from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from tools import TOOLS

class AgentState(TypedDict):
  messages: Annotated[list[BaseMessage], add_messages]

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools(TOOLS)

def agent_node(state: AgentState):
  response = llm_with_tools.invoke(state["messages"])
  return {"messages": [response]}

def build_graph():
  graph = StateGraph(AgentState)
  graph.add_node("agent", agent_node)
  graph.add_node("tools", ToolNode(TOOLS))
  graph.add_edge(START,"agent")
  graph.add_conditional_edges("agent", tools_condition)
  graph.add_edge("tools", "agent")

  return graph.compile()