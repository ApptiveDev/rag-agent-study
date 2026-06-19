from loader import load_md_documents
from splitter import split_recursive, split_md_header

from vectorstore import (
    build_faiss_vectorstore,
    save_faiss_vectorstore,
    reset_faiss_index,
)

RECURSIVE_INDEX_DIR = "./cache/faiss_recursive"
MARKDOWN_INDEX_DIR = "./cache/faiss_markdown"

def build_recursive_index():
    docs = load_md_documents("data")
    
    chunks = split_recursive(docs)
    
    print(f"[Recursive] chunk count: {len(chunks)}")
    
    vectorstore = build_faiss_vectorstore(chunks)
    
    reset_faiss_index(RECURSIVE_INDEX_DIR)
    
    save_faiss_vectorstore(
        vectorstore,
        RECURSIVE_INDEX_DIR,
    )
    
    print(f"Saved recursive index -> {RECURSIVE_INDEX_DIR}")
    
def build_markdown_index():
    docs = load_md_documents("data")
    
    chunks = split_md_header(docs)
    
    print(f"[Markdown Header] chunk count: {len(chunks)}")
    
    vectorstore = build_faiss_vectorstore(chunks)
    
    reset_faiss_index(MARKDOWN_INDEX_DIR)
    
    save_faiss_vectorstore(
        vectorstore,
        MARKDOWN_INDEX_DIR,
    )
    
    print(f"Saved markdown index -> {MARKDOWN_INDEX_DIR}")
    
if __name__ == "__main__":
    build_recursive_index()
    build_markdown_index()