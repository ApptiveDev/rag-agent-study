from langchain_core.documents import Document

from .hybrid import hybrid_search, vector_search
from .reranker import rerank

DEFAULT_STRATEGY = "markdown"


def retrieve(
    query: str,
    mode: str = "vector",
    strategy: str = DEFAULT_STRATEGY,
    k: int = 4,
    first_stage_n: int = 50,
    rerank_backend: str = "local",
) -> list[Document]:
    if mode == "vector":
        return vector_search(query, strategy, k)
    if mode == "hybrid":
        return hybrid_search(query, strategy, top_n=k)
    if mode == "rerank":
        candidates = hybrid_search(query, strategy, top_n=first_stage_n)
        return rerank(query, candidates, top_k=k, backend=rerank_backend)
    raise ValueError(f"unknown retrieve mode: {mode}")
