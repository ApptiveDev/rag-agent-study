import os
from typing import Literal

from dotenv import load_dotenv, find_dotenv
from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from schemas import AgentState
from nodes import agent_node, format_output_node, tool_node, with_token_logging

load_dotenv(find_dotenv())
os.environ["LANGSMITH_TRACING"] = "false"
os.environ["LANGSMITH_TRACING_V2"] = "false"


### 1. 조건부 엣지 함수 ###

def should_continue(state: AgentState) -> Literal["tools", "format_output"]:
    """마지막 AI 메시지에 tool_calls가 있으면 도구 실행, 없으면 응답 포맷팅으로 분기."""
    messages = state["messages"]
    last = messages[-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    return "format_output"


### 2. 그래프 조립 ###

def build_graph():
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
