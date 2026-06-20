from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from langchain_core.documents import Document

def split_recursive(
    docs: list[Document],
    chunk_size: int = 700,
    chunk_overlap: int = 100,
) -> list[Document]:
    """
    일반적인 문자 기반 chunking으로, 문맥이 길게 이어진 문서를 일정 길이로 자르기 
    """
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = chunk_size,
        chunk_overlap = chunk_overlap,
        separators=["\n\n", "\n", " ", ""],
    )
    
    chunks = splitter.split_documents(docs)
    
    for i, chunk in enumerate(chunks):
        chunk.metadata.update(
            {
                "chunk_strategy": "recursive",
                "chunk_id": f"recursive-{i}",
            }
        )
        
    return chunks

def split_md_header(docs: list[Document]) -> list[Document]:
    """
    md header 기준 chunking. 해결하려는 문제를 적은 경우가 있어서 구조 보존용.
    """
    
    headers_to_split_on = [
        ("#", "h1"),
        ("##", "h2"),
        ("###", "h3"),
    ]
    
    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on,
        strip_headers=False,
    )
    
    chunks: list[Document] = []
    
    for doc in docs:
        split_docs = splitter.split_text(doc.page_content)
        
        for idx, split_doc in enumerate(split_docs):
            split_doc.metadata.update(doc.metadata)
            split_doc.metadata.update(
                {
                    "chunk_strategy": "md_header",
                    "chunk_id": f"{doc.metadata.get('stem', 'doc')}-header-{idx}",
                }
            )
            chunks.append(split_doc)
            
    return chunks

def preview_chunks(chunks: list[Document], limit: int = 5) -> None:
    print(f"Total chunk: {len(chunks)}")
    
    for chunk in chunks[:limit]:
        print("=" * 80)
        print(chunk.metadata)
        print(chunk.page_content[:500])
        
if __name__ == "__main__":
    from loader import load_md_documents
    
    docs = load_md_documents("data")
    
    recursive_chunks = split_recursive(docs)
    md_chunks = split_md_header(docs)
    
    print("\n[Recursive chunking]")
    preview_chunks(recursive_chunks, limit=3)
    
    print("\n[Markdown Header chunking]")
    preview_chunks(md_chunks, limit=3)