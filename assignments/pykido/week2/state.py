from typing import Optional

from langgraph.graph import MessagesState


class AgentState(MessagesState):
    final_answer: Optional[dict]
