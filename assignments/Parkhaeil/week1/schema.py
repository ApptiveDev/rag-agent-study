"""State 및 최종 응답 스키마 정의."""
from typing import Annotated, TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from operator import add

class AgentState(TypedDict):
    """ReAct loop가 공유하는 그래프 상태
    - messages: agent <-> tool 사이를 오가며 누적되는 대화 기록.
      add_messages reducer 덕분에 노드가 새 메세지만 반환해도 자동 append
    - tool_call_trace: 심화 - 어떤 도구를 어떤 인자로 호출했는지 기록.
    """
    messages: Annotated[list[AnyMessage], add_messages]
    tool_call_trace: Annotated[list[dict], add]

class FinalAnswer(BaseModel):
    """사용자에게 전달되는 최종 응답 형식.
    
    1주차 과제 필수 사항: structured output 강제
    1주차 과제 심화 사항: 근거 / 사용한 도구 / Confidence 필드 포함
    """
    answer: str = Field(description="사용자 질문에 대한 최종 답변 (한국어)")
    sources_used: list[str] = Field(description="답변 생성에 사용한 도구 이름 목록", default_factory=list,)
    reasoning: str = Field(description="이 답변에 도달한 추론 과정 요약")
    confidence: float = Field(description="답변에 대한 확신도 (0.0~1.0)", ge=0.0, le=1.0)