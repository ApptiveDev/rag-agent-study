import re
from functools import lru_cache

from langchain_core.documents import Document
from rank_bm25 import BM25Okapi

from .loader import load_documents
from .splitter import split_documents
from .vectorstore import load_vectorstore

RRF_K = 60


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[가-힣]+|[a-zA-Z0-9]+", text.lower())


@lru_cache(maxsize=None)
def _chunks(strategy: str) -> tuple[Document, ...]:
    return tuple(split_documents(load_documents(), strategy))


@lru_cache(maxsize=None)
def _bm25(strategy: str) -> BM25Okapi:
    return BM25Okapi([_tokenize(c.page_content) for c in _chunks(strategy)])


@lru_cache(maxsize=None)
def _store(strategy: str):
    return load_vectorstore(strategy)


@lru_cache(maxsize=None)
def vector_search(query: str, strategy: str, top_n: int) -> list[Document]:
    return _store(strategy).as_retriever(search_kwargs={"k": top_n}).invoke(query)


def bm25_search(query: str, strategy: str, top_n: int) -> list[Document]:
    chunks = _chunks(strategy)
    scores = _bm25(strategy).get_scores(_tokenize(query))
    ranked = sorted(range(len(chunks)), key=lambda i: scores[i], reverse=True)
    return [chunks[i] for i in ranked[:top_n]]


def rrf_fuse(rankings: list[list[Document]], top_n: int, k: int = RRF_K) -> list[Document]:
    scores: dict[str, float] = {}
    by_id: dict[str, Document] = {}
    for ranking in rankings:
        for rank, doc in enumerate(ranking, start=1):
            cid = doc.metadata.get("chunk_id") or doc.page_content
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (k + rank)
            by_id.setdefault(cid, doc)
    fused = sorted(scores, key=lambda cid: scores[cid], reverse=True)
    return [by_id[cid] for cid in fused[:top_n]]


def hybrid_search(
    query: str,
    strategy: str = "markdown",
    top_n: int = 50,
    rrf_k: int = RRF_K,
) -> list[Document]:
    vector = vector_search(query, strategy, top_n)
    keyword = bm25_search(query, strategy, top_n)
    return rrf_fuse([vector, keyword], top_n=top_n, k=rrf_k)
