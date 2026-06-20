from typing import List
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever


class HybridRetriever:
    """
    BM25(희소 검색) + FAISS(밀집 검색)를 RRF(Reciprocal Rank Fusion)로 결합.

    RRF 공식:  score(d) = Σ  1 / (k + rank_i(d))
    기본 k=60 은 Cormack et al. 2009 논문 권장값.
    """

    def __init__(
        self,
        vectorstore,
        split_docs: List[Document],
        k: int = 6,
        rrf_k: int = 60,
        fetch_k_multiplier: int = 3,
    ):
        self.k = k
        self.rrf_k = rrf_k
        # 최종 k 개보다 더 많이 가져와서 RRF 재정렬 후 상위 k 반환
        fetch_k = k * fetch_k_multiplier
        self.dense_retriever = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": fetch_k},
        )
        self.sparse_retriever = BM25Retriever.from_documents(split_docs, k=fetch_k)

    def _rrf_score(self, rank: int) -> float:
        return 1.0 / (self.rrf_k + rank + 1)

    def invoke(self, query: str) -> List[Document]:
        dense_docs = self.dense_retriever.invoke(query)
        sparse_docs = self.sparse_retriever.invoke(query)

        scores: dict[str, float] = {}
        doc_map: dict[str, Document] = {}

        for rank, doc in enumerate(dense_docs):
            key = doc.page_content
            scores[key] = scores.get(key, 0.0) + self._rrf_score(rank)
            doc_map[key] = doc

        for rank, doc in enumerate(sparse_docs):
            key = doc.page_content
            scores[key] = scores.get(key, 0.0) + self._rrf_score(rank)
            doc_map[key] = doc

        ranked_keys = sorted(scores, key=lambda k: scores[k], reverse=True)
        return [doc_map[k] for k in ranked_keys[: self.k]]
