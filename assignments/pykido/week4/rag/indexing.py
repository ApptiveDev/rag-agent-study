import os

from dotenv import find_dotenv, load_dotenv

from . import STRATEGIES
from .loader import load_documents

load_dotenv(find_dotenv(), override=True)
os.environ["LANGSMITH_TRACING"] = "false"
from .splitter import split_documents
from .vectorstore import build_vectorstore, save_vectorstore


def build_index(strategy: str) -> int:
    docs = load_documents()
    chunks = split_documents(docs, strategy)
    store = build_vectorstore(chunks)
    save_vectorstore(store, strategy)
    return len(chunks)


def build_all() -> dict[str, int]:
    counts = {}
    for strategy in STRATEGIES:
        counts[strategy] = build_index(strategy)
        print(f"[{strategy}] indexed {counts[strategy]} chunks")
    return counts


if __name__ == "__main__":
    build_all()
