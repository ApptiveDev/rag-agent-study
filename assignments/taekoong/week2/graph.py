import os
from typing import Literal

from dotenv import load_dotenv, find_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from schema import AgentState, MinecraftAgentResponse
from tools import get_item_info, get_crafting_recipe, get_mob_info


load_dotenv(find_dotenv())
os.environ["LANGSMITH_TRACING"] = "false"
os.environ["LANGSMITH_TRACING_V2"] = "false"

### 1. 모델, 도구 준비 ### 

TOOLS = [get_item_info, get_crafting_recipe, get_mob_info]

# 도구 호출용 LLM
_llm = init_chat_model("gpt-4o-mini")
# bind_tools 코드로 LLM이 사용할 도구 목록을 판단할 수 있음 
llm_with_tools = _llm.bind_tools(TOOLS)

# 구조화 출력용 LLM
llm_for_output = _llm.with_structured_output(MinecraftAgentResponse)


### 2. 도구 실행 ###

# 도구 실행 노드 — 오류 발생 시 에러 메시지를 ToolMessage로 전달하여 LLM이 재시도 가능
tool_node = ToolNode(TOOLS, handle_tool_errors=True)

SYSTEM_PROMPT = """당신은 마인크래프트 전문 지식 에이전트입니다.

사용자의 마인크래프트 관련 질문에 제공된 도구를 활용하여 정확하고 유용한 답변을 제공하세요. 

사용 가능한 도구:
- get_item_info: 아이템·블록 정보 조회 (종류, 획득 방법, 용도)
- get_crafting_recipe: 제작 레시피 조회 (재료, 패턴, 생산량)
- get_mob_info: 몹 정보 조회 (체력, 공격력, 약점, 전투 팁)

필요한 도구를 먼저 호출하여 정확한 정보를 수집한 뒤 답변하세요.
도구 결과를 그대로 복사하지 말고 자연스럽게 요약하여 답변하세요.
도구 결과가 없거나 오류가 발생하면 알고 있는 지식으로 최선을 다해 답변하세요.
마크다운 문법(**굵게**, ```코드블록```, # 제목 등)은 사용하지 말고 일반 텍스트로만 답변하세요."""

def with_token_logging(node_fn):
    def wrapper(state):
        result = node_fn(state)
        last_msg = result["messages"][-1]
        if hasattr(last_msg, "usage_metadata") and last_msg.usage_metadata:
            usage = last_msg.usage_metadata
            print(f"[토큰] 입력: {usage['input_tokens']} | 출력: {usage['output_tokens']} | 합계: {usage['total_tokens']}")
        return result
    return wrapper

### 3. 노드 정의 ###

def agent_node(state: AgentState) -> dict:
    """LLM이 도구 호출 여부를 판단하고 응답을 생성하는 핵심 노드."""
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def format_output_node(state: AgentState) -> dict:
    """대화 기록을 바탕으로 Pydantic 구조화 응답을 생성하는 노드."""
    messages = state["messages"]

    # 대화에서 사용된 도구·근거 추출
    tools_used: list[str] = []
    evidence: list[str] = []
    for msg in messages:
        if isinstance(msg, AIMessage) and msg.tool_calls:
            for tc in msg.tool_calls:
                if tc["name"] not in tools_used:
                    tools_used.append(tc["name"])
        if isinstance(msg, ToolMessage):
            evidence.append(f"[{msg.name}] {str(msg.content)}")

    # 최종 AI 메시지의 자연어 답변 추출
    last_ai_text = ""
    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            content = msg.content
            if isinstance(content, str) and content.strip():
                last_ai_text = content
                break
            elif isinstance(content, list):
                texts = [b["text"] for b in content if isinstance(b, dict) and b.get("type") == "text"]
                if texts:
                    last_ai_text = " ".join(texts)
                    break

    prompt = f"""다음 대화 기록을 바탕으로 마인크래프트 질문에 대한 구조화된 최종 응답을 생성하세요.

에이전트 최종 답변:
{last_ai_text}

사용된 도구: {tools_used if tools_used else "없음 (도구 없이 답변)"}
수집된 근거:
{chr(10).join(evidence) if evidence else "없음"}

위 내용을 바탕으로 아래 필드를 채워주세요:
- answer: 사용자 질문에 대한 완전하고 명확한 한국어 답변
- evidence: 수집된 근거 목록 (없으면 빈 리스트)
- tools_used: 사용된 도구 이름 목록 (없으면 빈 리스트)
- confidence: 답변의 신뢰도 (도구 결과 기반이면 0.9 이상, 일반 지식이면 0.7 정도)"""

    structured = llm_for_output.invoke(prompt)
    return {"structured_output": structured}


### 4. 조건부 엣지 함수 ###

def should_continue(state: AgentState) -> Literal["tools", "format_output"]:
    """마지막 AI 메시지에 tool_calls가 있으면 도구 실행, 없으면 응답 포맷팅으로 분기."""
    messages = state["messages"]
    last = messages[-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    return "format_output"


### 5. 그래프 조립 ###

def build_graph() -> StateGraph:
    builder = StateGraph(AgentState)

    builder.add_node("agent", with_token_logging(agent_node))
    builder.add_node("tools", tool_node)
    builder.add_node("format_output", format_output_node)

    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", should_continue)
    builder.add_edge("tools", "agent")
    builder.add_edge("format_output", END)

    memory = MemorySaver()
    return builder.compile(checkpointer=memory)


graph = build_graph()
