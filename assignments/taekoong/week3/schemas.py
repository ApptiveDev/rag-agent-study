from typing import Annotated, Optional
from pydantic import BaseModel, Field
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class MinecraftRAGResponse(BaseModel):
    answer: str = Field(description="사용자 질문에 대한 최종 답변")
    sources: list[str] = Field(
        default_factory=list,
        description="답변에 사용된 문서 출처 목록",
    )
    tools_used: list[str] = Field(
        default_factory=list,
        description="호출된 도구 이름 목록",
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="답변 신뢰도 (0.0 ~ 1.0)",
    )


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    # add_messages는 리스트를 덮어쓰지 않고 뒤에 추가하는 리듀서
    structured_output: Optional[MinecraftRAGResponse]
