from typing import Literal

from pydantic import BaseModel, Field


class RAGAnswer(BaseModel):
    answer: str = Field(description="한국어 마크다운 답변. context 근거만 사용하고 모르면 모른다고 한다.")
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="context 가 질문을 직접 뒷받침하면 0.85+, 부분적 근거면 ≤0.7.",
    )


class DocGrade(BaseModel):
    relevant: Literal["yes", "no"] = Field(
        description="문서 묶음이 질문에 답할 근거를 담고 있으면 'yes', 아니면 'no'."
    )


class HallucinationGrade(BaseModel):
    grounded: Literal["yes", "no"] = Field(
        description="답의 모든 핵심 주장이 context 문서로 뒷받침되면 'yes', 환각이 있으면 'no'."
    )


class JudgeScore(BaseModel):
    correctness: int = Field(
        ge=1,
        le=5,
        description="답이 reference answer 와 의미적으로 일치하는 정도. 1=완전히 틀림, 5=완전히 일치.",
    )
    groundedness: int = Field(
        ge=1,
        le=5,
        description="답이 검색된 context 문서에 근거하는 정도. 1=환각, 5=전부 근거.",
    )
    reason: str = Field(description="두 점수에 대한 한 줄 근거 (한국어).")
