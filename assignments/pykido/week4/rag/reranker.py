import os
from functools import lru_cache

from langchain_core.documents import Document

LOCAL_MODEL = "BAAI/bge-reranker-v2-m3"
COHERE_MODEL = "rerank-multilingual-v3.0"


@lru_cache(maxsize=None)
def _local_model(model_name: str):
    from sentence_transformers import CrossEncoder

    return CrossEncoder(model_name)


def _rerank_local(query: str, docs: list[Document], top_k: int, model_name: str) -> list[Document]:
    if not docs:
        return []
    scores = _local_model(model_name).predict([(query, doc.page_content) for doc in docs])
    ranked = sorted(zip(docs, scores), key=lambda pair: pair[1], reverse=True)
    return [doc for doc, _ in ranked[:top_k]]


@lru_cache(maxsize=None)
def _cohere_client():
    import cohere

    return cohere.Client(os.environ["COHERE_API_KEY"])


def _rerank_cohere(query: str, docs: list[Document], top_k: int, model_name: str) -> list[Document]:
    if not docs:
        return []
    result = _cohere_client().rerank(
        model=model_name,
        query=query,
        documents=[doc.page_content for doc in docs],
        top_n=top_k,
    )
    return [docs[r.index] for r in result.results]


def rerank(
    query: str,
    docs: list[Document],
    top_k: int = 5,
    backend: str = "local",
    model_name: str | None = None,
) -> list[Document]:
    if backend == "local":
        return _rerank_local(query, docs, top_k, model_name or LOCAL_MODEL)
    if backend == "cohere":
        return _rerank_cohere(query, docs, top_k, model_name or COHERE_MODEL)
    raise ValueError(f"unknown rerank backend: {backend}")
