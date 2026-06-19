from typing import Literal

from pydantic import BaseModel, Field


class TranscriptResult(BaseModel):
    """`fetch_video_transcript` 도구 반환 형태."""

    video_id: str
    video_title: str
    transcript: str
    language: str


class SummaryResult(BaseModel):
    """`summarize_video` 도구 반환 형태."""

    summary: str = Field(description="3~5문장 분량의 핵심 요약")
    key_points: list[str] = Field(description="핵심 포인트 5개 이내")


class QuizItem(BaseModel):
    question: str
    answer: str
    explanation: str


class QuizResult(BaseModel):
    """`generate_quiz` 도구 반환 형태."""

    quiz: list[QuizItem]


class VideoLearningResult(BaseModel):
    """에이전트의 최종 응답 스키마.

    ReAct 루프가 종료될 때 LLM이 이 스키마에 맞춰 응답한다.
    `kind`로 응답 유형을 구분해, 도구가 돌지 않은 일반 대화도 같은 스키마로 처리한다.
    """

    kind: Literal["learning", "chat"]
    message: str = Field(description="사용자에게 보여줄 메인 메시지")
    video_title: str | None = None
    summary: str | None = None
    key_points: list[str] = Field(default_factory=list)
    quiz: list[QuizItem] = Field(default_factory=list)
