"""
Week 4 — 검색 지표 모듈 (순수 코드, LLM 불필요)
================================================

지표 정의
---------
  Recall@K     : 상위 K 결과 안에서 relevant 문서 집합 중 몇 개를 찾았는지 (커버리지)
  Precision@K  : 상위 K 결과 중 실제 relevant 문서가 차지하는 비율 (정확도)
  MRR          : Mean Reciprocal Rank — 첫 번째 relevant 문서가 몇 위에 있는지
  Hit@K        : 상위 K 안에 relevant 문서가 하나라도 있으면 1, 없으면 0

relevant 판단 기준
------------------
  golden_set 의 `relevant_chunk_ids` 는 파일 스텀(stem) 목록.
  검색된 문서의 metadata["filename"] 에서 확장자를 제거한 스텀과 비교한다.
  예) "farming_keg.md" → "farming_keg"
"""

from pathlib import Path
from typing import List
from langchain_core.documents import Document


# ──────────────────────────────────────────────
# 헬퍼
# ──────────────────────────────────────────────

def _source_stem(doc: Document) -> str:
    filename = doc.metadata.get("filename", "")
    if filename:
        return Path(filename).stem
    source = doc.metadata.get("source", "")
    return Path(source).stem if source else "unknown"


# ──────────────────────────────────────────────
# 개별 지표
# ──────────────────────────────────────────────

def recall_at_k(retrieved: List[Document], relevant_ids: List[str], k: int) -> float:
    """상위 K 중 relevant 파일 집합이 몇 개나 커버됐는지."""
    if not relevant_ids:
        return 0.0
    retrieved_stems = {_source_stem(d) for d in retrieved[:k]}
    return len(retrieved_stems & set(relevant_ids)) / len(set(relevant_ids))


def precision_at_k(retrieved: List[Document], relevant_ids: List[str], k: int) -> float:
    """상위 K 중 relevant 문서 비율."""
    if not retrieved or k == 0:
        return 0.0
    relevant_set = set(relevant_ids)
    hits = sum(1 for d in retrieved[:k] if _source_stem(d) in relevant_set)
    return hits / k


def mrr(retrieved: List[Document], relevant_ids: List[str]) -> float:
    """첫 번째 relevant 문서의 역수 순위."""
    relevant_set = set(relevant_ids)
    for rank, doc in enumerate(retrieved, start=1):
        if _source_stem(doc) in relevant_set:
            return 1.0 / rank
    return 0.0


def hit_at_k(retrieved: List[Document], relevant_ids: List[str], k: int) -> float:
    """상위 K 안에 relevant 문서가 하나라도 있으면 1."""
    relevant_set = set(relevant_ids)
    return float(any(_source_stem(d) in relevant_set for d in retrieved[:k]))


# ──────────────────────────────────────────────
# 배치 평가
# ──────────────────────────────────────────────

def evaluate_retrieval(retriever, golden_set, k: int = 6) -> List[dict]:
    """
    golden_set 전체(out_of_domain 제외)에 대해 검색 지표를 계산.

    Args:
        retriever  : .invoke(query) → List[Document] 인터페이스를 가진 검색기
        golden_set : List[QAPair]
        k          : 상위 K 개수
    Returns:
        per-question 결과 딕셔너리 리스트
    """
    results = []
    for qa in golden_set:
        if qa.question_type == "out_of_domain":
            continue
        retrieved = retriever.invoke(qa.question)
        relevant = qa.relevant_chunk_ids
        results.append({
            "question": qa.question,
            "question_type": qa.question_type,
            f"recall@{k}": recall_at_k(retrieved, relevant, k),
            f"precision@{k}": precision_at_k(retrieved, relevant, k),
            "mrr": mrr(retrieved, relevant),
            f"hit@{k}": hit_at_k(retrieved, relevant, k),
        })
    return results


def aggregate_metrics(results: List[dict]) -> dict:
    """per-question 결과를 평균 집계."""
    if not results:
        return {}
    numeric_keys = [k for k in results[0] if isinstance(results[0][k], float)]
    return {k: round(sum(r[k] for r in results) / len(results), 4) for k in numeric_keys}


def print_metrics_table(label: str, agg: dict) -> None:
    print(f"\n{'─'*40}")
    print(f"  {label}")
    print(f"{'─'*40}")
    for k, v in agg.items():
        print(f"  {k:<16} {v:.4f}")
