from functools import lru_cache

from langchain_core.documents import Document

from .vectorstore import load_vectorstore


@lru_cache(maxsize=None)
def _store(strategy: str):
    return load_vectorstore(strategy)


def retrieve(query: str, strategy: str = "markdown", k: int = 4) -> list[Document]:
    return _store(strategy).as_retriever(search_kwargs={"k": k}).invoke(query)


if __name__ == "__main__":
    for strategy in ("recursive", "markdown"):
        print(f"\n[{strategy}]")
        for doc in retrieve("이분 탐색으로 답을 찾는 최적화 문제", strategy=strategy, k=3):
            print(f"- {doc.metadata['chunk_id']} ({doc.metadata['source']})")
