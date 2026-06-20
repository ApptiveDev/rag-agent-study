from langchain_core.documents import Document
from typing import List


def format_docs(docs: List[Document]) -> str:
    """
    검색된 위키 문서 리스트를 LLM 프롬프트 입력용 문자열로 포맷.
    위키 문서에는 page 가 없으므로 source/category/section 기반으로 출처 표시.
    """
    parts = []
    for doc in docs:
        source = doc.metadata.get("source", "unknown")
        category = doc.metadata.get("category", "")
        # MarkdownHeaderTextSplitter가 부착하는 헤더 메타데이터 처리
        header1 = doc.metadata.get("Header 1", "")
        header2 = doc.metadata.get("Header 2", "")
        header3 = doc.metadata.get("Header 3", "")
        section = " > ".join(h for h in [header1, header2, header3] if h)

        meta_parts = [f"<source>{source}</source>"]
        if category:
            meta_parts.append(f"<category>{category}</category>")
        if section:
            meta_parts.append(f"<section>{section}</section>")

        parts.append(
            f"<document>"
            f"<content>{doc.page_content}</content>"
            f"{''.join(meta_parts)}"
            f"</document>"
        )
    return "\n".join(parts)


def format_docs_simple(docs: List[Document]) -> str:
    """청킹 비교용 단순 포맷 (내용만)."""
    return "\n\n".join(doc.page_content for doc in docs)


def format_source_list(docs: List[Document]) -> str:
    """출처 목록 문자열 반환 (답변 하단 출력용)."""
    seen = set()
    lines = []
    for doc in docs:
        source = doc.metadata.get("source", "unknown")
        category = doc.metadata.get("category", "")
        key = f"{source}|{category}"
        if key not in seen:
            seen.add(key)
            cat_str = f" [{category}]" if category else ""
            lines.append(f"- {source}{cat_str}")
    return "\n".join(lines) if lines else "- (출처 없음)"
