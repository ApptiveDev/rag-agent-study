"""ReAct loop StateGraph 구성.

구조:
  START → agent ─[should_continue]─┬→ tools → agent (루프)
                                    ├→ commit_choice → format → END
                                    └→ format → END
"""
from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode

from schema import AgentState, FinalAnswer, SkillChoiceCommit
from tools import ALL_TOOLS


# ─── 모델 준비 ───────────────────────────────────────────────
# 도구 호출용과 최종 포맷팅용을 분리. bind_tools와 with_structured_output을
# 같은 인스턴스에 동시 적용하면 provider에 따라 불안정함.
_base_model = init_chat_model("openai:gpt-4.1-mini", temperature=0)
_model_with_tools = _base_model.bind_tools(ALL_TOOLS)
_model_for_format = _base_model.with_structured_output(FinalAnswer)
_model_for_commit = _base_model.with_structured_output(SkillChoiceCommit)

SYSTEM_PROMPT = """당신은 스타듀밸리 게임 가이드 어시스턴트입니다.
플레이어 질문에 답할 때 필요하면 제공된 도구를 사용해 정확한 정보를 가져오세요.
일반적인 질문(인사, 게임 소개, NPC 생일 등)에는 도구 없이 답하세요.
답변은 한국어로 친근하게 작성하세요.

## 스킬 트리 안내
스킬 선택 질문에는 아래 정보를 참고해 정확하게 안내해주세요:
- 농사 5레벨: 목축업자(동물 생산물 가치 +20%) vs 경작인(작물 가치 +10%)
- 농사 10레벨 (목축업자 선택 시): 닭장의달인(계란·우유 품질 업) vs 양치기(양털·토끼발 획득률 증가)
- 농사 10레벨 (경작인 선택 시): 장인(가공품 가치 +40%) vs 농업전문가(곡물류 가치 +50%)

## 중요: 스킬 선택 시그널
다음 두 경우 모두 응답 맨 마지막에 반드시 `[AWAITING_SKILL_CHOICE]`를 붙이세요:
1. 사용자가 직업 선택을 **고민 중**일 때 (어떤 직업을 고를지 물을 때): 두 선택지를 비교 안내 후 붙이세요.
2. 사용자가 직업 선택을 **직접 밝히거나 변경**할 때 (예: "목축업자 할래", "경작인으로 바꿨어"): 선택 확인 메시지 후 붙이세요.
단, NPC 정보/낚시/작물 수익 같은 일반 질문에는 절대 붙이지 마세요."""




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

    trace = []
    if isinstance(response, AIMessage) and response.tool_calls:
        trace = [
            {"tool": tc["name"], "args": tc["args"], "id": tc.get("id")}
            for tc in response.tool_calls
        ]

    return {"messages": [response], "tool_call_trace": trace}


def _on_tool_error(error: Exception) -> str:
    """도구 실패 시 LLM이 받을 fallback 메시지."""
    return (
        f"도구 실행 중 오류 발생: {error}. "
        "다른 도구를 시도하거나 도구 없이 답해주세요."
    )

tool_node = ToolNode(ALL_TOOLS, handle_tool_errors=_on_tool_error)


def commit_choice(state: AgentState) -> dict:
    """사용자의 자연어 답변에서 스킬 선택을 추출해 state에 저장하는 노드.

    interrupt_before=["commit_choice"]로 그래프가 여기서 멈추고,
    사용자 답변이 추가된 후 resume되면 이 노드가 실행됨.
    """
    # 최근 메시지만 파싱 — 긴 히스토리에서 이전 선택과 혼동하는 현상 방지
    recent = state["messages"][-3:]
    current_choices = state.get("skill_choices", [])
    parse_prompt = [
        SystemMessage(content=(
            "대화를 읽고 사용자가 가장 마지막에 선택하거나 변경한 "
            "스타듀밸리 농사 스킬 직업을 파악해주세요. "
            "이전에 다른 선택이 있더라도 가장 최근 선택을 기준으로 추출하세요. "
            f"현재 저장된 스킬: {current_choices}. "
            "같은 레벨의 기존 선택이 있으면 is_change=true로 표시하세요."
        )),
        *recent,
    ]
    parsed: SkillChoiceCommit = _model_for_commit.invoke(parse_prompt)

    if parsed.is_change:
        reply = f"알겠어요! 농사 {parsed.level}레벨 직업을 **{parsed.choice}**으로 변경해서 저장했어요. 하수구 갔다 오셨군요 😄"
    else:
        reply = f"좋아요! 농사 {parsed.level}레벨 직업 **{parsed.choice}** 선택을 저장했어요!"

    print(f"[DEBUG commit_choice] level={parsed.level}, choice={parsed.choice}")
    
    return {
        "messages": [AIMessage(content=reply)],
        "skill_choices": [{"level": parsed.level, "choice": parsed.choice}],
    }


def format_final_answer(state: AgentState) -> dict:
    """지금까지의 대화를 FinalAnswer 스키마로 정리하는 노드.

    [AWAITING_SKILL_CHOICE] 시그널은 사용자에게 노출하지 않도록 제거.
    """
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

    # [AWAITING_SKILL_CHOICE]는 내부 시그널 — 최종 출력에 노출하지 않음
    clean_answer = final.answer.replace("[AWAITING_SKILL_CHOICE]", "").strip()

    formatted = (
        f"{clean_answer}\n\n"
        f"---\n"
        f"📊 사용 도구: {', '.join(final.sources_used) or '없음'}\n"
        f"🧠 추론: {final.reasoning}\n"
        f"✅ 확신도: {final.confidence:.0%}"
    )
    return {"messages": [AIMessage(content=formatted)]}


# ─── 라우팅 함수 ─────────────────────────────────────────────
def should_continue(state: AgentState) -> str:
    """agent 다음 3-way 분기.

    - tool_calls 있음 → tools (ReAct 루프)
    - [AWAITING_SKILL_CHOICE] 포함 → commit_choice (interrupt 후 선택 저장)
    - 그 외 → format
    """
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    if isinstance(last, AIMessage) and "[AWAITING_SKILL_CHOICE]" in last.content:
        return "commit_choice"
    return "format"


# ─── 빌더에 노드 추가 ────────────────────────────────────────
builder = StateGraph(AgentState)
builder.add_node("agent", call_agent)
builder.add_node("tools", tool_node)
builder.add_node("commit_choice", commit_choice)
builder.add_node("format", format_final_answer)


# ─── 엣지 연결 ───────────────────────────────────────────────
builder.add_edge(START, "agent")
builder.add_conditional_edges(
    "agent",
    should_continue,
    {"tools": "tools", "commit_choice": "commit_choice", "format": "format"},
)
builder.add_edge("tools", "agent")
builder.add_edge("commit_choice", "format")
builder.add_edge("format", END)


# ─── 컴파일 (체크포인터는 run.ipynb에서 주입) ────────────────
# 직접 실행할 때는 MemorySaver로 폴백
def build_graph(checkpointer=None):
    if checkpointer is None:
        from langgraph.checkpoint.memory import MemorySaver
        checkpointer = MemorySaver()
    return builder.compile(
        checkpointer=checkpointer,
        interrupt_before=["commit_choice"],
    )

graph = build_graph()


# ─── 단독 실행 테스트 ────────────────────────────────────────
if __name__ == "__main__":
    result = graph.invoke(
        {
            "messages": [HumanMessage(content="Abigail 생일이 언제야?")],
            "tool_call_trace": [],
            "skill_choices": [],
        },
        config={"configurable": {"thread_id": "test"}, "recursion_limit": 25},
    )
    print(result["messages"][-1].content)