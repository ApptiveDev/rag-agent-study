from pydantic import BaseModel, Field


class RAGAnswer(BaseModel):
    """검색된 문서에 근거한 RAG 답변 형식."""

    answer: str = Field(description="한국어 마크다운 답변. context 근거만 사용하고 모르면 모른다고 한다.")
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="context 가 질문을 직접 뒷받침하면 0.85+, 부분적 근거면 ≤0.7.",
    )
