from pathlib import Path
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document

def load_md_documents(data_dir: str = "data") -> list[Document]:
    """
    week3/data 폴더 아래의 모든 .md 파일을 로드합니다.
    """
    base_path = Path(data_dir)
    
    if not base_path.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")
    
    docs: list[Document] = []
    
    for file_path in base_path.rglob("*.md"):
        loader = TextLoader(str(file_path), encoding="utf-8")
        loaded_docs = loader.load()
        
        for doc in loaded_docs:
            doc.metadata.update(
                {
                    "source": str(file_path),
                    "filename": file_path.name,
                    "stem": file_path.stem,
                }
            )
            docs.append(doc)
            
    return docs

if __name__ == "__main__":
    documents = load_md_documents()
    print(f"Loaded {len(documents)} documents")
    
    for doc in documents[:3]:
        print("-" * 50)
        print(doc.metadata)
        print(doc.page_content[:400])