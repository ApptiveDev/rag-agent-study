from pydantic import BaseModel, Field


class GradeDocuments(BaseModel):
    """검색된 문서가 질문과 관련 있는지 이진 평가."""

    binary_score: str = Field(
        description="문서가 질문과 관련 있으면 'yes', 없으면 'no'"
    )


class GradeHallucination(BaseModel):
    """생성 답변이 검색 문서에 근거하는지 이진 평가."""

    binary_score: str = Field(
        description="답변이 문서에 근거하면 'yes', 환각이면 'no'"
    )


class GradeAnswer(BaseModel):
    """생성 답변이 질문을 해결하는지 이진 평가."""

    binary_score: str = Field(
        description="질문을 해결하면 'yes', 아니면 'no'"
    )
