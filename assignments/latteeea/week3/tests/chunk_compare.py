# tests/chunk_compare.py

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
RAG_DIR = ROOT_DIR / "rag"
sys.path.append(str(RAG_DIR))

from retriever import retrieve


COMPARE_QUERIES = [
    "외부 API 변경으로 장애가 발생한 사례",
    "사용자 인증 정보 불일치로 문제가 발생한 사례",
    "수동 검토와 자동 검증을 함께 사용한 사례",
    "안드로이드 빌드 시 배포 에러가 발생한 사례",
    "long polling 으로 인한 서버 다운 사례"
]


def summarize_doc(doc):
    return {
        "source": doc.metadata.get("source"),
        "filename": doc.metadata.get("filename"),
        "chunk_id": doc.metadata.get("chunk_id"),
        "preview": doc.page_content[:120].replace("\n", " "),
    }


def compare_query(query: str, k: int = 3):
    recursive_docs = retrieve(query=query, strategy="recursive", k=k)
    markdown_docs = retrieve(query=query, strategy="markdown", k=k)

    print("=" * 120)
    print(f"QUERY: {query}")
    print("=" * 120)

    print("\n[Recursive Chunking Results]")
    for i, doc in enumerate(recursive_docs, start=1):
        item = summarize_doc(doc)
        print(f"{i}. {item['filename']} | {item['chunk_id']}")
        print(f"   {item['preview']}")

    print("\n[Markdown Header Chunking Results]")
    for i, doc in enumerate(markdown_docs, start=1):
        item = summarize_doc(doc)
        print(f"{i}. {item['filename']} | {item['chunk_id']}")
        print(f"   {item['preview']}")


if __name__ == "__main__":
    for query in COMPARE_QUERIES:
        compare_query(query, k=3)