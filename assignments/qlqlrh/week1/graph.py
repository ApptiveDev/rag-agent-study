from typing import Annotated, TypedDict

from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, SystemMessage
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from schema import VideoLearningResult
from tools import ALL_TOOLS

SYSTEM_PROMPT = """
당신은 사용자의 YouTube 학습을 돕는 에이전트입니다.

[역할]
- 사용자가 YouTube URL을 보내면 영상을 학습 모드로 처리합니다.
- 학습 흐름은 반드시 이 순서로 도구를 호출하세요.
  1) fetch_video_transcript(url)
  2) summarize_video(transcript, video_title)
  3) generate_quiz(summary, key_points)
- 각 단계의 결과(Observation)를 보고 다음 단계 도구를 호출할지, 또는 종료할지 판단하세요.

[도구를 호출하지 않아도 되는 경우]
- 사용자가 일반 인사·질문(앱 설명, 사용법 안내 등)을 한 경우.
- 직전 메시지에 이미 학습 결과가 있어 재활용으로 충분한 경우.

[응답 형식]
- 도구를 모두 사용한 학습 결과는 한국어로 보기 좋게 정리해서 보여주세요.
  · 영상 제목, 요약, 핵심 포인트, 퀴즈(문제·정답·해설)를 모두 포함.
- 일반 대화는 짧고 친근하게 답하세요.
"""

model_with_tools = init_chat_model("gpt-5.4-mini").bind_tools(ALL_TOOLS)
structured_model = init_chat_model("gpt-5.4-mini").with_structured_output(VideoLearningResult)


# 공유되는 데이터의 형태 선언
class AgentState(TypedDict):
    messages: Annotated[list, add_messages] # 리듀서 추가

# ReAct 루프의 Thought 단계 (노드 실행마다 호출됨)
def agent_node(state: AgentState):
    messages = [SystemMessage(SYSTEM_PROMPT), *state["messages"]] # LLM에게 보낼 메시지 리스트
    response = model_with_tools.invoke(messages)
    if response.tool_calls: # 도구 호출이 필요하면
        return {"messages": [response]} # response를 그대로 state에 추가 (tools 노드로 라우팅)

    final = structured_model.invoke(messages) # 스키마에 맞춰서 응답
    return {"messages": [AIMessage(content=final.model_dump_json(indent=2))]}


builder = StateGraph(AgentState)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(ALL_TOOLS))
builder.add_edge(START, "agent")
# tool_calls가 있으면 tools, 없으면 END 노드로 이동 (기본 함수 로직)
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")
graph = builder.compile()