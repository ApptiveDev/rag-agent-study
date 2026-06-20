import os
from pathlib import Path
from typing import Annotated, Optional

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, SystemMessage
from langgraph.graph import START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

from schema import PrepAnswer
from tools import ALL_TOOLS


def load_project_env() -> None:
    """Load only the repository-root .env file."""
    env_path = Path(__file__).resolve().parents[3] / ".env"
    load_dotenv(env_path, override=True)


load_project_env()

os.environ.setdefault("LANGSMITH_TRACING", "false")
os.environ.setdefault("LANGSMITH_TRACING_V2", "false")


SYSTEM_PROMPT = """
당신은 클래식 공연 예습을 돕는 RAG 에이전트입니다.

[역할]
- 사용자가 공연 링크를 보내면 공연 상세 페이지를 읽고, 공연명/일시/장소/연주자/프로그램을 파악합니다.
- 사용자가 작품명이나 작곡가만 말하면 해당 작품을 중심으로 예습 자료를 찾습니다.
- 초보자가 공연 전에 궁금해할 내용을 중심으로 설명합니다.
- 너무 음악학적으로 깊게 들어가기보다, "이 곡이 뭔지", "왜 유명한지", "어떤 배경에서 만들어졌는지", "공연장에서 무엇을 들으면 좋은지"를 알려줍니다.

[공연 링크가 있는 경우]
도구 호출은 가능한 한 다음 순서를 따르세요.
1) fetch_concert_page(url)
   - 공연 상세 페이지의 텍스트를 가져옵니다.
2) extract_concert_program(page_text)
   - 공연명, 날짜, 장소, 연주자, 프로그램 후보를 추출합니다.
3) retrieve_work_overview(query)
   - 각 작품이 어떤 곡인지 초보자용 개요를 검색합니다.
4) retrieve_creation_background(query)
   - 작품의 작곡 배경과 맥락을 검색합니다.
5) retrieve_concert_listening_points(query)
   - 공연장에서 들을 감상 포인트를 검색합니다.
6) retrieve_preview_keywords(query)
   - 공연 전에 들어볼 만한 유튜브 검색어 또는 예습 키워드를 가져옵니다.

[공연 링크가 없는 경우]
- 사용자의 질문에서 작품명, 작곡가, 악장, 공연 맥락을 파악하세요.
- 특정 작품/작곡가/악장에 대한 질문이면 필요한 도구를 선택적으로 호출하세요.
  - retrieve_work_overview
  - retrieve_creation_background
  - retrieve_concert_listening_points
  - retrieve_preview_keywords
- 일반적인 공연 예습 방법을 묻는 질문이면 도구를 호출하지 않아도 됩니다.

[도구를 호출하지 않아도 되는 경우]
- 사용자가 일반 인사나 간단한 사용법을 묻는 경우.
- 특정 작품/공연 정보 검색이 필요 없는 일반 조언인 경우.
- 직전 메시지에 이미 충분한 예습 결과가 있고 재활용할 수 있는 경우.

[응답 형식]
- 도구를 사용한 경우, 도구 결과를 근거로 한국어로 정리하세요.
- 초보자 친화적으로 답하세요.
- 확실하지 않은 정보는 추측하지 말고 불확실하다고 말하세요.
- 최종 답변에는 가능하면 다음을 포함하세요.
  · 공연 정보 또는 작품명
  · 한 줄 요약
  · 작곡/역사적 배경
  · 공연장에서 들을 포인트
  · 공연 전 예습 추천
  · 유튜브 또는 웹 검색 키워드
  · 참고한 출처 또는 도구 결과
"""


MODEL_NAME = os.getenv("CLASSICAL_AGENT_MODEL", "openai:gpt-5.4-mini")

model_with_tools = init_chat_model(MODEL_NAME).bind_tools(ALL_TOOLS)
structured_model = init_chat_model(MODEL_NAME).with_structured_output(PrepAnswer)


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    used_tools: list[str]
    final_answer: Optional[PrepAnswer]


def _collect_used_tools(messages: list) -> list[str]:
    used_tools = []

    for message in messages:
        for tool_call in getattr(message, "tool_calls", []) or []:
            tool_name = tool_call.get("name")
            if tool_name and tool_name not in used_tools:
                used_tools.append(tool_name)

    return used_tools


def agent_node(state: AgentState):
    messages = [SystemMessage(content=SYSTEM_PROMPT), *state["messages"]]
    response = model_with_tools.invoke(messages)

    if response.tool_calls:
        return {
            "messages": [response],
            "used_tools": _collect_used_tools([*state["messages"], response]),
        }

    final = structured_model.invoke(messages)
    used_tools = _collect_used_tools(state["messages"])
    final.used_tools = used_tools

    return {
        "messages": [AIMessage(content=final.model_dump_json(indent=2))],
        "used_tools": used_tools,
        "final_answer": final,
    }


builder = StateGraph(AgentState)
builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(ALL_TOOLS))

builder.add_edge(START, "agent")
builder.add_conditional_edges("agent", tools_condition)
builder.add_edge("tools", "agent")

graph = builder.compile()
