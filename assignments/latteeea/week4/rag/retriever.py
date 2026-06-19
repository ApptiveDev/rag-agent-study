from pathlib import Path

from vectorstore import load_faiss_vectorstore

WEEK4_ROOT = Path(__file__).resolve().parent.parent
CACHE_ROOT = WEEK4_ROOT / "cache"
if not (CACHE_ROOT / "faiss_markdown").exists():
    CACHE_ROOT = WEEK4_ROOT.parent / "week3" / "cache"

RECURSIVE_INDEX_DIR = str(CACHE_ROOT / "faiss_recursive")
MARKDOWN_INDEX_DIR = str(CACHE_ROOT / "faiss_markdown")

def get_retriever(strategy: str = "recursive", k: int = 4):
    if strategy == "recursive":
        vectorstore = load_faiss_vectorstore(RECURSIVE_INDEX_DIR)
    elif strategy == "markdown":
        vectorstore = load_faiss_vectorstore(MARKDOWN_INDEX_DIR)
    else:
        raise ValueError("strategy must be either 'recursive" or 'markdown')
    
    return vectorstore.as_retriever(
        search_kwargs={"k": k}
    )
    
def retrieve(query: str, strategy: str = "recursive", k: int = 4):
    retriever = get_retriever(strategy=strategy, k=k)
    return retriever.invoke(query)

def print_results(query: str, strategy: str = "recursive", k: int = 4):
    docs = retrieve(query = query, strategy=strategy, k=k)
    
    print(f"\nQuery: {query}")
    print(f"Strategy: {strategy}")
    print(f"Result count: {len(docs)}")
    
    for i, doc in enumerate(docs, start=1):
        print("=" * 80)
        print(f"[{i}] source={doc.metadata.get('source')}")
        print(f"filename={doc.metadata.get('filename')}")
        print(f"chunk_id={doc.metadata.get('chunk_id')}")
        print(doc.page_content[:1000])
        
if __name__ == "__main__":
    test_query = "외부 API 변경으로 장애가 발생한 사례"
    
    print_results(test_query, strategy="recursive", k=3)
    print_results(test_query, strategy="markdown",k=3)