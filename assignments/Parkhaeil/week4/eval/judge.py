"""
Week 4 — LLM-as-Judge 채점 모듈
================================

평가 축 3개:
  correctness   RAG 답변 vs 참조 답변 (의미 일치 여부)
  groundedness  RAG 답변 vs 검색 문서 (환각 여부)
  relevance     RAG 답변 vs 질문 (질문 응답 여부)

채점은 'reasoning → verdict' 순서를 강제하여 사후 합리화를 방지.
judge_llm 은 temperature=0, seed=42 으로 일관성을 확보.
생성 모델과 다른 회사 모델을 쓰면 편향이 줄어듦 (선택 사항).
"""

from typing import Literal
from pydantic import BaseModel, Field
from langchain.chat_models import init_chat_model


JUDGE_SYSTEM_PROMPT = """당신은 RAG 시스템의 답변을 평가하는 엄격하고 공정한 심판입니다.
아래 세 가지 축으로 판정하되, 각 축마다 '이유'를 먼저 쓰고 그 다음 yes/no를 정하세요.

[평가 축]
1. correctness   (RAG 답변 vs 참조 답변)
   참조 답변과 '의미적으로' 일치하면 yes. 표현·문장이 달라도 같은 사실을 다루면 yes.
   사실이 틀리거나 참조 답변의 핵심 정보가 빠지면 no.
2. groundedness  (RAG 답변 vs 검색 문서)
   답변의 모든 주장이 검색 문서로 뒷받침되면 yes.
   검색 문서에 없는 사실을 하나라도 끌어다 쓰면(환각) no.
3. relevance     (RAG 답변 vs 질문)
   답변이 질문이 묻는 것을 실제로 다루면 yes.
   질문과 동떨어지거나 회피·딴소리면 no.

[주의]
- 세 축은 독립적으로 판정하세요.
- 반드시 '이유 → 판정' 순서. 판정부터 정하고 이유를 끼워맞추지 마세요."""

JUDGE_USER_TEMPLATE = """[질문]
{question}

[참조 답변]
{reference}

[검색 문서]
{context}

[RAG 답변]
{answer}"""


class AxisVerdict(BaseModel):
    reasoning: str = Field(description="판정 이유를 먼저 작성")
    verdict: Literal["yes", "no"]


class JudgeResult(BaseModel):
    correctness: AxisVerdict
    groundedness: AxisVerdict
    relevance: AxisVerdict


def get_judge_llm(model_name: str = "gpt-4o-mini"):
    """채점용 LLM — temperature=0 + seed로 일관성 확보."""
    return init_chat_model(model_name, temperature=0, seed=42)


def judge_answer(
    question: str,
    reference: str,
    context: str,
    answer: str,
    llm=None,
) -> JudgeResult:
    """
    단일 답변 채점.

    Args:
        question:  사용자 질문
        reference: 정답셋의 reference_answer
        context:   검색된 청크를 이어붙인 문자열
        answer:    RAG 시스템이 생성한 답변
        llm:       judge LLM (None이면 기본 모델 사용)
    """
    if llm is None:
        llm = get_judge_llm()
    user = JUDGE_USER_TEMPLATE.format(
        question=question,
        reference=reference,
        context=context,
        answer=answer,
    )
    return llm.with_structured_output(JudgeResult).invoke(
        [("system", JUDGE_SYSTEM_PROMPT), ("human", user)]
    )


def verdict_to_score(verdict: Literal["yes", "no"]) -> int:
    return 1 if verdict == "yes" else 0


def aggregate_judge_results(results: list[JudgeResult]) -> dict:
    """JudgeResult 리스트를 집계하여 correctness/groundedness/relevance 평균 반환."""
    if not results:
        return {}
    n = len(results)
    return {
        "correctness": sum(verdict_to_score(r.correctness.verdict) for r in results) / n,
        "groundedness": sum(verdict_to_score(r.groundedness.verdict) for r in results) / n,
        "relevance": sum(verdict_to_score(r.relevance.verdict) for r in results) / n,
    }
