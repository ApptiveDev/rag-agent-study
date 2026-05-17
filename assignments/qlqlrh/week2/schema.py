from typing import Literal

from pydantic import BaseModel, Field


class ProductInfo(BaseModel):
    """`lookup_product` 도구 반환 형태."""

    name: str
    overview: str = Field(description="상품 한 줄 개요")
    main_coverage: list[str] = Field(description="주요 보장 항목")


class RiderInfo(BaseModel):
    """`lookup_rider` 도구 반환 형태."""

    name: str
    coverage: str = Field(description="특약이 보장하는 내용")
    exclusions: list[str] = Field(description="면책 사항 또는 주의점")
    renewable: bool = Field(description="갱신형 여부")


class CoverageSummary(BaseModel):
    """`summarize_coverage` 도구 반환 형태."""

    summary: str = Field(description="사용자 관심사에 맞춘 보장 요약")
    relevant_riders: list[str] = Field(description="관련 특약 이름")


class ConsultationResponse(BaseModel):
    """에이전트의 최종 응답 스키마.

    ReAct 루프가 종료될 때 LLM이 이 스키마에 맞춰 응답한다.
    `kind`로 응답 유형을 구분해, 도구가 돌지 않은 일반 대화도 같은 스키마로 처리한다.
    """

    kind: Literal["answer", "chat"]
    message: str = Field(description="사용자에게 보여줄 메인 메시지")
    referenced_products: list[str] = Field(default_factory=list)
    referenced_riders: list[str] = Field(default_factory=list)
