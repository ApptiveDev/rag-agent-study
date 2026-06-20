from langchain.chat_models import init_chat_model
from langchain_core.tools import tool

from schema import CoverageSummary, ProductInfo, RiderInfo

_product_lookup = init_chat_model("gpt-5.4-mini").with_structured_output(ProductInfo)
_rider_lookup = init_chat_model("gpt-5.4-mini").with_structured_output(RiderInfo)
_coverage_summarizer = init_chat_model("gpt-5.4-mini").with_structured_output(CoverageSummary)


@tool
def lookup_product(name: str) -> dict:
    """보험 상품명을 받아 상품 개요와 주요 보장 항목을 반환합니다.

    사용자가 특정 상품(예: '건강보험', '암보험', '종신보험')에 대해 물어보면
    가장 먼저 호출해 상품의 윤곽을 파악하세요.
    """
    prompt = (
        "당신은 국내 보험 상품을 잘 아는 컨설턴트입니다. "
        "아래 상품에 대해 한국어로 정확히 답하세요.\n\n"
        f"[상품명]\n{name}\n\n"
        "- overview: 이 상품이 어떤 위험을 보장하는지 1~2문장으로\n"
        "- main_coverage: 주요 보장 항목 3~5개 (짧은 문장)"
    )
    result: ProductInfo = _product_lookup.invoke(prompt)
    return result.model_dump()


@tool
def lookup_rider(name: str) -> dict:
    """보험 특약명을 받아 보장 내용, 면책 사항, 갱신 여부를 반환합니다.

    사용자가 특정 특약(예: '암 진단비 특약', '실손 특약')에 대해 물어보면 호출하세요.
    """
    prompt = (
        "당신은 국내 보험 특약·약관을 잘 아는 컨설턴트입니다. "
        "아래 특약에 대해 한국어로 정확히 답하세요.\n\n"
        f"[특약명]\n{name}\n\n"
        "- coverage: 특약이 보장하는 내용을 2~3문장으로\n"
        "- exclusions: 면책 사항 또는 주의해야 할 점 (짧은 문장 리스트)\n"
        "- renewable: 갱신형 특약이면 True, 비갱신형이면 False"
    )
    result: RiderInfo = _rider_lookup.invoke(prompt)
    return result.model_dump()


@tool
def summarize_coverage(product_name: str, user_interests: list[str]) -> dict:
    """상품명과 사용자 관심사를 받아 사용자 관점에서 보장을 다시 정리해 반환합니다.

    `lookup_product`로 상품을 먼저 조회한 뒤, 사용자가 관심 있는 보장
    (예: '암', '수술', '입원')에 맞춰 다시 요약할 때 호출하세요.
    """
    interests = ", ".join(user_interests) if user_interests else "전반"
    prompt = (
        "당신은 보험 컨설턴트입니다. 아래 상품의 보장을 사용자의 관심사에 맞춰 "
        "한국어로 다시 정리하세요.\n\n"
        f"[상품명]\n{product_name}\n\n"
        f"[사용자 관심사]\n{interests}\n\n"
        "- summary: 사용자 관심사에 맞춰 어떻게 보장되는지 2~3문장으로\n"
        "- relevant_riders: 관심사와 관련된 특약 이름 (없으면 빈 리스트)"
    )
    result: CoverageSummary = _coverage_summarizer.invoke(prompt)
    return result.model_dump()


ALL_TOOLS = [lookup_product, lookup_rider, summarize_coverage]
