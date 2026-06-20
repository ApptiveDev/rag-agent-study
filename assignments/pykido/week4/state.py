from typing import Optional, TypedDict

from langchain_core.documents import Document


class RAGState(TypedDict):
    question: str
    strategy: str
    documents: list[Document]
    context: str
    final_answer: Optional[dict]


class AgenticRAGState(TypedDict, total=False):
    question: str
    query: str
    strategy: str
    documents: list[Document]
    context: str
    doc_grade: str
    hallucination_grade: str
    rewrite_count: int
    regen_count: int
    final_answer: Optional[dict]
