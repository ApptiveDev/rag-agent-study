from .loader import load_docs
from .splitter import split_docs
from .embeddings import get_embeddings
from .vectorstore import create_vectorstore, load_vectorstore


def build_index(data_path: str = "./data", persist_directory: str = "./chroma_db"):
    docs = load_docs(data_path)
    chunks = split_docs(docs)
    embeddings = get_embeddings()
    return create_vectorstore(chunks, embeddings, persist_directory)


def load_index(persist_directory: str = "./chroma_db"):
    embeddings = get_embeddings()
    return load_vectorstore(embeddings, persist_directory)
