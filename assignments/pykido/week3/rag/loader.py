from pathlib import Path

from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document

from . import DATA_DIR


def load_documents(data_dir: Path = DATA_DIR) -> list[Document]:
    docs: list[Document] = []
    for path in sorted(data_dir.rglob("*.md")):
        loaded = TextLoader(str(path), encoding="utf-8").load()
        category = path.parent.name
        for doc in loaded:
            doc.metadata.update(
                {
                    "source": str(path.relative_to(data_dir)),
                    "filename": path.name,
                    "stem": path.stem,
                    "category": category,
                }
            )
            docs.append(doc)
    return docs


if __name__ == "__main__":
    documents = load_documents()
    print(f"loaded {len(documents)} documents")
    for doc in documents[:3]:
        print("-" * 60)
        print(doc.metadata)
        print(doc.page_content[:200])
