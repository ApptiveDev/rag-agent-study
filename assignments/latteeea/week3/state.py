from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    
    active_note_id: str | None 
    current_topic: str | None
    
    hypotheses: list[dict]
    
    narrative_intent: str | None
    evidence_plan: dict | None 