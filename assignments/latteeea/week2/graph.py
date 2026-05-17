from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from state import AgentState
from tools import TOOLS
from memory import checkpointer
from nodes import extract_hypotheses_nodes


llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools(TOOLS)

def agent_node(state: AgentState):
  response = llm_with_tools.invoke(state["messages"])
  return {"messages": [response]}

def build_graph():
  graph = StateGraph(AgentState)
  
  graph.add_node("extract_hypothesis", extract_hypotheses_nodes)
  graph.add_node("agent", agent_node)
  graph.add_node("tools", ToolNode(TOOLS))
  
  graph.add_edge(START,"extract_hypothesis")
  graph.add_edge("extract_hypothesis", "agent")
  
  graph.add_conditional_edges("agent", tools_condition)
  graph.add_edge("tools", "agent")

  return graph.compile(
    checkpointer=checkpointer
  )