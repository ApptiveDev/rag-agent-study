import json
import os
from typing import Literal

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from schema import BaseballAgentState, BaseballFinalAnswer
from tools import BASEBALL_TOOLS


SYSTEM_PROMPT = """You are a Korean baseball rules assistant.
Use tools when the user asks about a specific rule, term, or game situation.
If the user asks a general advice question, answer without tools.
Keep answers concise and practical."""

DEFAULT_MODEL = "gpt-5-mini"


def _has_openai_key() -> bool:
    return bool(os.getenv("OPENAI_API_KEY"))


def _latest_human_text(state: BaseballAgentState) -> str:
    for message in reversed(state["messages"]):
        if isinstance(message, HumanMessage):
            return str(message.content)
    return ""


def _tool_messages(state: BaseballAgentState) -> list[ToolMessage]:
    return [message for message in state["messages"] if isinstance(message, ToolMessage)]


def _tool_names_from_state(state: BaseballAgentState) -> list[str]:
    return [message.name or "unknown_tool" for message in _tool_messages(state)]


def _select_demo_tool_call(question: str) -> AIMessage:
    lowered = question.lower()

    if any(keyword in question for keyword in ["좋은", "어떤 정보", "설명하려면", "기준"]):
        return AIMessage(content="도구 없이 답변할 수 있는 일반 질문입니다.")

    if any(keyword in question for keyword in ["상황", "판정", "주자", "아웃", "플라이", "투구 동작"]):
        return AIMessage(
            content="상황 판정을 위해 야구 상황 판정 도구를 확인하겠습니다.",
            tool_calls=[
                {
                    "name": "judge_game_situation",
                    "args": {"situation": question},
                    "id": "call_judge_situation",
                }
            ],
        )

    if any(keyword in question for keyword in ["뜻", "용어", "OPS", "WHIP", "보크", "태그업", "낫아웃"]):
        term = question
        for candidate in ["보크", "태그업", "낫아웃", "인필드 플라이"]:
            if candidate in question:
                term = candidate
                break
        if "ops" in lowered:
            term = "OPS"
        if "whip" in lowered:
            term = "WHIP"
        return AIMessage(
            content="용어 설명 도구를 확인하겠습니다.",
            tool_calls=[
                {
                    "name": "explain_baseball_term",
                    "args": {"term": term},
                    "id": "call_explain_term",
                }
            ],
        )

    if any(keyword in question for keyword in ["규칙", "룰", "인필드", "보크", "태그업", "낫아웃"]):
        topic = "infield_fly" if "인필드" in question else question
        return AIMessage(
            content="규칙 검색 도구를 확인하겠습니다.",
            tool_calls=[
                {
                    "name": "lookup_baseball_rule",
                    "args": {"topic": topic},
                    "id": "call_lookup_rule",
                }
            ],
        )

    return AIMessage(content="도구 없이 답변할 수 있는 일반 질문입니다.")


def call_model(state: BaseballAgentState) -> dict:
    """Agent node. Uses real tool-calling LLM when configured, otherwise demo routing."""
    if _tool_messages(state):
        return {"messages": [AIMessage(content="도구 결과를 바탕으로 최종 답변을 작성합니다.")]}

    if _has_openai_key():
        model_name = os.getenv("BASEBALL_MODEL", DEFAULT_MODEL)
        model = ChatOpenAI(model=model_name, temperature=0).bind_tools(BASEBALL_TOOLS)
        response = model.invoke([SystemMessage(content=SYSTEM_PROMPT), *state["messages"]])
        return {"messages": [response]}

    return {"messages": [_select_demo_tool_call(_latest_human_text(state))]}


def route_after_agent(state: BaseballAgentState) -> Literal["tools", "final"]:
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"
    return "final"


def _summarize_tool_payloads(state: BaseballAgentState) -> tuple[str, list[str]]:
    summaries: list[str] = []
    references: list[str] = []
    for message in _tool_messages(state):
        try:
            payload = json.loads(str(message.content))
        except json.JSONDecodeError:
            payload = {"raw": str(message.content)}

        if isinstance(payload, dict):
            if "ruling" in payload:
                summaries.append(f"{payload.get('ruling')} {payload.get('reason', '')}".strip())
            elif "summary" in payload:
                summaries.append(str(payload["summary"]))
            elif "explanation" in payload:
                summaries.append(str(payload["explanation"]))
            elif "message" in payload:
                summaries.append(str(payload["message"]))

            reference = payload.get("reference")
            if reference:
                references.append(str(reference))
        else:
            summaries.append(str(payload))

    return "\n".join(summaries), references


def make_structured_response(state: BaseballAgentState) -> dict:
    """Final node that enforces the Pydantic output schema."""
    question = _latest_human_text(state)
    used_tools = _tool_names_from_state(state)
    tool_summary, references = _summarize_tool_payloads(state)

    if tool_summary:
        answer = f"질문: {question}\n\n판정/설명: {tool_summary}"
        ruling = tool_summary.split("\n", maxsplit=1)[0]
        confidence = "high"
    else:
        answer = (
            "야구 규칙을 볼 때는 먼저 아웃카운트, 주자 위치, 타구 종류, 수비수의 실제 "
            "플레이 가능성을 순서대로 확인하면 됩니다."
        )
        ruling = "일반 설명"
        confidence = "medium"

    final_response = BaseballFinalAnswer(
        answer=answer,
        ruling=ruling,
        used_tools=used_tools,
        confidence=confidence,
        references=references or ["general baseball rules guidance"],
        next_steps=["아웃카운트와 주자 위치를 함께 적으면 더 정확히 판정할 수 있습니다."],
    )
    return {"final_response": final_response}


def build_graph():
    builder = StateGraph(BaseballAgentState)

    builder.add_node("agent", call_model)
    builder.add_node("tools", ToolNode(BASEBALL_TOOLS))
    builder.add_node("final", make_structured_response)

    builder.add_edge(START, "agent")
    builder.add_conditional_edges(
        "agent",
        route_after_agent,
        {
            "tools": "tools",
            "final": "final",
        },
    )
    builder.add_edge("tools", "agent")
    builder.add_edge("final", END)

    return builder.compile()


graph = build_graph()
