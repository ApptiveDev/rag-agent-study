from langchain_core.documents import Document
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

HEADERS = [("#", "h1"), ("##", "h2"), ("###", "h3")]


def split_recursive(
    docs: list[Document],
    chunk_size: int = 700,
    chunk_overlap: int = 100,
) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = splitter.split_documents(docs)
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_strategy"] = "recursive"
        chunk.metadata["chunk_id"] = f"{chunk.metadata.get('stem', 'doc')}-rec-{i}"
    return chunks


def split_markdown(docs: list[Document]) -> list[Document]:
    splitter = MarkdownHeaderTextSplitter(headers_to_split_on=HEADERS, strip_headers=False)
    chunks: list[Document] = []
    for doc in docs:
        for i, section in enumerate(splitter.split_text(doc.page_content)):
            section.metadata = {**doc.metadata, **section.metadata}
            section.metadata["chunk_strategy"] = "markdown"
            section.metadata["chunk_id"] = f"{doc.metadata.get('stem', 'doc')}-md-{i}"
            chunks.append(section)
    return chunks


def split_documents(docs: list[Document], strategy: str) -> list[Document]:
    if strategy == "recursive":
        return split_recursive(docs)
    if strategy == "markdown":
        return split_markdown(docs)
    raise ValueError(f"unknown strategy: {strategy}")


if __name__ == "__main__":
    from .loader import load_documents

    docs = load_documents()
    for strategy in ("recursive", "markdown"):
        chunks = split_documents(docs, strategy)
        print(f"[{strategy}] {len(docs)} docs -> {len(chunks)} chunks")
