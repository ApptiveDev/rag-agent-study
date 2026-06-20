from langchain_chroma import Chroma


def create_vectorstore(chunks, embeddings, persist_directory: str = "./chroma_db"):
    return Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_directory,
    )


def load_vectorstore(embeddings, persist_directory: str = "./chroma_db"):
    return Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings,
    )
