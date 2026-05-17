from typing import Annotated, TypedDict

from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, SystemMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from schema import ConsultationResponse
from tools import ALL_TOOLS

SYSTEM_PROMPT = """
당신은 사용자의 보험 상담을 돕는 에이전트입니다.

[역할]
- 사용자가 보험 상품·특약·보장에 대해 물어보면 도구를 활용해 답하세요.
- 도구 사용 가이드:
  1) lookup_product(name): 상품 윤곽 파악
  2) lookup_rider(name): 특정 특약 상세
  3) summarize_coverage(product_name, user_interests): 사용자 관심사에 맞춰 보장 정리
- 사용자 대화 맥락(이전 발화의 관심사·가입 현황·연령대 등)을 적극적으로 참고해 답변하세요.

[도구를 호출하지 않아도 되는 경우]
- 사용자가 일반 인사·앱 사용법 질문을 한 경우.
- 직전 메시지에 이미 결과가 있어 재활용으로 충분한 경우.

[중요 - 맥락 참조 규칙]
- 사용자가 "방금 말한 조건", "내 또래", "그 상품"처럼 직전 발화를 명시적으로 가리키는데
  대화 메시지 히스토리에서 해당 맥락(나이대·가입 현황·관심 보장 등)을 찾을 수 없다면,
  임의로 추정하지 말고 사용자에게 어떤 조건인지 먼저 되묻고 답변을 보류하세요.
  이때는 도구를 호출하지 말고, 짧은 chat 응답으로 어떤 정보가 필요한지 명확히 물어보세요.

[응답 형식]
- 도구 결과를 활용한 답변은 한국어로 보기 좋게 정리해서 보여주세요.
  · 참조한 상품/특약을 referenced_products / referenced_riders 에 명시.
- 일반 대화는 짧고 친근하게 답하세요.
"""

model_with_tools = init_chat_model("gpt-5.4-mini").bind_tools(ALL_TOOLS)
structured_model = init_chat_model("gpt-5.4-mini").with_structured_output(
    ConsultationResponse, method="json_schema", strict=True
)


# 공유되는 데이터의 형태 선언
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]  # 리듀서 추가


# ReAct 루프의 Thought 단계 (노드 실행마다 호출됨)
def agent_node(state: AgentState):
    messages = [SystemMessage(SYSTEM_PROMPT), *state["messages"]]  # LLM에게 보낼 메시지 리스트
    response = model_with_tools.invoke(messages)
    if response.tool_calls:  # 도구 호출이 필요하면
        return {"messages": [response]}  # response를 그대로 state에 추가 (tools 노드로 라우팅)

    final = structured_model.invoke(messages)  # 스키마에 맞춰서 응답
    return {"messages": [AIMessage(content=final.model_dump_json(indent=2))]}


builder = StateGraph(AgentState)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(ALL_TOOLS))
builder.add_edge(START, "agent")
# tool_calls가 있으면 tools, 없으면 END 노드로 이동 (기본 함수 로직)
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")

# Week 2 추가분: InMemorySaver로 thread별 대화 상태를 분리·복원하고,
# interrupt_before=["tools"]로 보험 정보 조회 직전 사용자 검토 단계를 끼워 넣는다.
checkpointer = InMemorySaver()
graph = builder.compile(
    checkpointer=checkpointer,
    interrupt_before=["tools"],
)
