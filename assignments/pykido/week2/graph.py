import os
from typing import Literal

from dotenv import find_dotenv, load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.types import Command, interrupt

from schema import ReActAnswer
from state import AgentState
from tools import TOOLS

load_dotenv(find_dotenv(), override=True)
os.environ["LANGSMITH_TRACING"] = "false"
os.environ["LANGSMITH_TRACING_V2"] = "false"

SYSTEM_PROMPT = """당신은 알고리즘 코딩 테스트 준비를 돕는 학습 코치입니다.

도구:
- get_algorithm_pattern(name): 패턴 설명
- recommend_problems(topic, level, problem_id): 프로그래머스 문제 추천/조회
- review_solution(problem_id, user_code): 풀이 리뷰용 rubric (코드는 직접 채점하지 않으므로 rubric 받은 뒤 사용자 코드와 비교해 리뷰 작성)

원칙:
1. 개념/패턴 → get_algorithm_pattern
2. 문제 추천/검색 → recommend_problems
3. 풀이 리뷰 요청 → review_solution(problem_id, user_code) 호출 후 rubric 기반 비교
4. 도구 결과만 신뢰. mock DB miss 면 솔직히 말할 것
5. 이전 대화에서 다룬 문제·패턴을 기억하고 맥락에 맞게 이어서 답할 것
6. 한국어 답변, 코드/패턴 키는 영어 원형
"""

HINT_DIRECTIVE = (
    "학습자가 힌트만 요청했습니다. review_solution을 다시 호출하지 말고, "
    "레퍼런스 정답·접근을 그대로 공개하지 마세요. 막힌 지점을 스스로 찾도록 "
    "방향성 힌트 1~2개만 한국어로 제시하세요."
)

model = init_chat_model("openai:gpt-4.1-mini", temperature=0.1)
model_with_tools = model.bind_tools(TOOLS)
structured_model = model.with_structured_output(ReActAnswer)


def agent_node(state: AgentState) -> dict:
    messages = state["messages"]
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [SystemMessage(content=SYSTEM_PROMPT), *messages]
    return {"messages": [model_with_tools.invoke(messages)]}


def review_gate(state: AgentState) -> Command[Literal["tools", "agent"]]:
    last = state["messages"][-1]
    decision = interrupt(
        {
            "question": "풀이 리뷰를 어떻게 받을까요?",
            "options": {"hint": "막힌 부분 힌트만", "full": "레퍼런스 기반 전체 리뷰"},
        }
    )
    if str(decision) == "full":
        return Command(goto="tools")
    tool_messages = [
        ToolMessage(content=HINT_DIRECTIVE, tool_call_id=tc["id"], name=tc["name"])
        for tc in last.tool_calls
    ]
    return Command(goto="agent", update={"messages": tool_messages})


def format_answer_node(state: AgentState) -> dict:
    prompt = (
        "바로 앞 assistant 답변을 ReActAnswer 스키마로 정리하세요. "
        "answer에는 그 답변 내용을 담되 직전 질문과 무관한 이전 추천·설명까지 다시 끌어오지는 마세요. "
        "used_tools: 실제 호출한 도구만 / sources: 근거 ID·패턴 키 / "
        "confidence: 도구 직접 근거 0.85+, 추측이면 ≤0.7"
    )
    answer = structured_model.invoke([*state["messages"], HumanMessage(content=prompt)])
    return {"final_answer": answer.model_dump()}


def route_after_agent(state: AgentState) -> Literal["review_gate", "tools", "format_answer"]:
    last = state["messages"][-1]
    if not last.tool_calls:
        return "format_answer"
    if any(tc["name"] == "review_solution" for tc in last.tool_calls):
        return "review_gate"
    return "tools"


def build_graph():
    builder = StateGraph(AgentState)
    builder.add_node("agent", agent_node)
    builder.add_node("review_gate", review_gate)
    builder.add_node("tools", ToolNode(TOOLS))
    builder.add_node("format_answer", format_answer_node)

    builder.add_edge(START, "agent")
    builder.add_conditional_edges(
        "agent",
        route_after_agent,
        {"review_gate": "review_gate", "tools": "tools", "format_answer": "format_answer"},
    )
    builder.add_edge("tools", "agent")
    builder.add_edge("format_answer", END)

    return builder.compile(checkpointer=InMemorySaver())


graph = build_graph()
