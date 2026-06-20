from typing import Annotated, Optional

from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


class PrepAnswer(BaseModel):
    """클래식 공연 예습 에이전트의 최종 응답 스키마"""

    concert_title: Optional[str] = Field(default=None, description="Concert title, if known")
    concert_date: Optional[str] = Field(default=None, description="Concert date, if known")
    venue: Optional[str] = Field(default=None, description="Concert venue, if known")
    performers: list[str] = Field(default_factory=list, description="Conductors, orchestras, soloists, etc.")
    work_title: str = Field(description="Main classical work being discussed")
    program_works: list[str] = Field(default_factory=list, description="Works found in the concert program")
    composer: Optional[str] = Field(default=None, description="Composer, if identified")
    difficulty: str = Field(description="beginner, intermediate, or advanced")
    summary: str = Field(description="Beginner-friendly concert-prep summary")
    background: list[str] = Field(description="Historical, composer, or creation background")
    listening_points: list[str] = Field(description="What to listen for during the performance")
    recommended_before_concert: list[str] = Field(description="Concrete prep actions before attending")
    preview_keywords: list[str] = Field(
        default_factory=list,
        description="YouTube or web search keywords for preview listening",
    )
    used_tools: list[str] = Field(description="Tool names used by the graph")
    sources: list[str] = Field(description="Source URLs or source labels")


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    used_tools: list[str]
    final_answer: Optional[dict]
