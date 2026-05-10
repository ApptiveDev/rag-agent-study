from typing import Annotated, Literal, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field


class BaseballFinalAnswer(BaseModel):
    """Structured response returned by the baseball rules graph."""

    answer: str = Field(description="User-facing Korean answer.")
    ruling: str = Field(description="Short decision or rule summary.")
    used_tools: list[str] = Field(description="Domain tools used to answer.")
    confidence: Literal["low", "medium", "high"] = Field(
        description="Confidence level based on available mock rule data."
    )
    references: list[str] = Field(description="Rule or data references used.")
    next_steps: list[str] = Field(description="Helpful follow-up checks or actions.")


class BaseballAgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    final_response: BaseballFinalAnswer | None
