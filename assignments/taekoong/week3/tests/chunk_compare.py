from rag.loader import load_docs
from rag.splitter import split_docs


def compare_chunks():
    docs = load_docs("../data")

    chunks_A = split_docs(docs, chunk_size=500, chunk_overlap=50)
    chunks_B = split_docs(docs, chunk_size=1000, chunk_overlap=100)

    print("원본 문서 수:", len(docs))
    print("\n[A] chunk_size=500, chunk_overlap=50")
    print("청크 수:", len(chunks_A))
    print(chunks_A[0].page_content[:300])

    print("\n[B] chunk_size=1000, chunk_overlap=100")
    print("청크 수:", len(chunks_B))
    print(chunks_B[0].page_content[:300])


if __name__ == "__main__":
    compare_chunks()
