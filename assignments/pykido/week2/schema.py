from pydantic import BaseModel, Field


class ReActAnswer(BaseModel):
    """ReAct agent의 최종 답변 형식."""

    answer: str = Field(description="한국어 마크다운 답변. 코드/패턴 키는 영어 원형.")
    used_tools: list[str] = Field(default_factory=list, description="실제 호출된 도구 이름들.")
    sources: list[str] = Field(default_factory=list, description="근거 식별자 (예: 'pgs-43238', 'binary-search').")
    confidence: float = Field(ge=0.0, le=1.0, description="도구 결과 직접 근거면 0.85+, 추측 섞이면 ≤0.7.")
