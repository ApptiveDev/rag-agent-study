"""ReAct loop StateGraph 구성.

구조:
  START → agent ─[should_continue]─┬→ tools → agent (루프)
                                    └→ format → END
"""
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from schema import AgentState, FinalAnswer
from tools import ALL_TOOLS


# ─── 모델 준비 ───────────────────────────────────────────────
# 도구 호출용과 최종 포맷팅용을 분리. bind_tools와 with_structured_output을
# 같은 인스턴스에 동시 적용하면 provider에 따라 불안정함.
_base_model = init_chat_model("openai:gpt-4.1-mini", temperature=0)
_model_with_tools = _base_model.bind_tools(ALL_TOOLS)
_model_for_format = _base_model.with_structured_output(FinalAnswer)

SYSTEM_PROMPT = """당신은 스타듀밸리 게임 가이드 어시스턴트입니다.
플레이어 질문에 답할 때 필요하면 제공된 도구를 사용해 정확한 정보를 가져오세요.
일반적인 질문(인사, 게임 소개 등)에는 도구 없이 답하세요.
답변은 한국어로 친근하게 작성하세요."""


# ─── 노드 함수 정의 ──────────────────────────────────────────
def call_agent(state: AgentState) -> dict:
    """LLM이 도구 호출 여부를 판단하는 노드.

    응답 메시지를 add_messages reducer로 누적시키기 위해
    {"messages": [response]} 형태로 반환 (단일 메시지여도 리스트!).
    """
    messages = state["messages"]

    # 첫 호출 시 시스템 프롬프트 삽입
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)

    response = _model_with_tools.invoke(messages)

    # 심화: tool call trace 기록
    trace = []
    if isinstance(response, AIMessage) and response.tool_calls:
        trace = [
            {"tool": tc["name"], "args": tc["args"], "id": tc.get("id")}
            for tc in response.tool_calls
        ]

    return {"messages": [response], "tool_call_trace": trace}


def _on_tool_error(error: Exception) -> str:
    """심화: 도구 실패 시 LLM이 받을 fallback 메시지."""
    return (
        f"도구 실행 중 오류 발생: {error}. "
        "다른 도구를 시도하거나 도구 없이 답해주세요."
    )

# tools 노드: ToolNode 인스턴스가 그 자체로 노드
tool_node = ToolNode(ALL_TOOLS, handle_tool_errors=_on_tool_error)


def format_final_answer(state: AgentState) -> dict:
    """지금까지의 대화를 FinalAnswer 스키마로 정리하는 노드."""
    used_tools = list({t["tool"] for t in state.get("tool_call_trace", [])})

    prompt_messages = [
        SystemMessage(content=(
            "지금까지의 대화와 도구 사용 내역을 바탕으로 "
            "최종 응답을 FinalAnswer 형식으로 정리해주세요. "
            f"사용된 도구: {used_tools if used_tools else '없음'}"
        )),
        *state["messages"],
        HumanMessage(content="위 대화를 바탕으로 FinalAnswer를 작성해주세요."),
    ]

    final: FinalAnswer = _model_for_format.invoke(prompt_messages)

    # 사람이 읽기 좋은 텍스트로 변환해 messages에 추가
    formatted = (
        f"{final.answer}\n\n"
        f"---\n"
        f"📊 사용 도구: {', '.join(final.sources_used) or '없음'}\n"
        f"🧠 추론: {final.reasoning}\n"
        f"✅ 확신도: {final.confidence:.0%}"
    )
    return {"messages": [AIMessage(content=formatted)]}


# ─── 라우팅 함수 (직접 구현 — 과제 명세!) ────────────────────
def should_continue(state: AgentState) -> str:
    """agent 다음 분기 결정.

    - 마지막 AIMessage에 tool_calls 있음 → tools (루프 계속)
    - tool_calls 없음 → format (루프 탈출)
    """
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"
    return "format"


# ─── 빌더에 노드 추가 ────────────────────────────────────────
builder = StateGraph(AgentState)
builder.add_node("agent", call_agent)
builder.add_node("tools", tool_node)
builder.add_node("format", format_final_answer)


# ─── 엣지 연결 ───────────────────────────────────────────────
builder.add_edge(START, "agent")
builder.add_conditional_edges(
    "agent",
    should_continue,
    {"tools": "tools", "format": "format"},
)
builder.add_edge("tools", "agent")   # ReAct 루프의 핵심
builder.add_edge("format", END)


# ─── 컴파일 ──────────────────────────────────────────────────
graph = builder.compile()


# ─── 단독 실행 테스트 ────────────────────────────────────────
if __name__ == "__main__":
    result = graph.invoke(
        {
            "messages": [HumanMessage(content="Abigail 생일이 언제야?")],
            "tool_call_trace": [],
        },
        config={"recursion_limit": 25},  # 안전장치
    )
    print(result["messages"][-1].content)
    print("\n📋 Tool call trace:")
    for entry in result["tool_call_trace"]:
        print(f"  - {entry}")