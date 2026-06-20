from typing import List
from langchain_core.documents import Document


class CrossEncoderReranker:
    """
    sentence-transformers Cross-Encoder 기반 재정렬기.

    기본 모델: cross-encoder/ms-marco-MiniLM-L-6-v2
      - 영어 MS-MARCO 데이터로 학습된 경량 모델.
      - 한국어 성능 향상을 원하면 BAAI/bge-reranker-v2-m3 권장.

    사용법:
        reranker = CrossEncoderReranker(top_k=4)
        reranked_docs = reranker.rerank(query, candidate_docs)
    """

    def __init__(
        self,
        model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        top_k: int = 4,
    ):
        from sentence_transformers import CrossEncoder  # lazy import

        self.model = CrossEncoder(model_name)
        self.top_k = top_k

    def rerank(self, query: str, docs: List[Document]) -> List[Document]:
        if not docs:
            return docs
        pairs = [(query, doc.page_content) for doc in docs]
        scores = self.model.predict(pairs)
        ranked = sorted(zip(scores, docs), key=lambda x: x[0], reverse=True)
        return [doc for _, doc in ranked[: self.top_k]]
