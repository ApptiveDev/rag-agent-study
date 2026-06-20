import shutil

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

from . import INDEX_DIR

EMBEDDING_MODEL = "text-embedding-3-small"


def get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(model=EMBEDDING_MODEL)


def build_vectorstore(chunks: list[Document]) -> FAISS:
    return FAISS.from_documents(chunks, get_embeddings())


def save_vectorstore(store: FAISS, strategy: str) -> None:
    path = INDEX_DIR / strategy
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)
    store.save_local(str(path))


def load_vectorstore(strategy: str) -> FAISS:
    path = INDEX_DIR / strategy
    if not path.exists():
        raise FileNotFoundError(f"index not found: {path}. run indexing.py first.")
    return FAISS.load_local(
        str(path),
        get_embeddings(),
        allow_dangerous_deserialization=True,
    )
