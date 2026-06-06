from typing import Optional, TypedDict

from langchain_core.documents import Document


class RAGState(TypedDict):
    question: str
    strategy: str
    documents: list[Document]
    context: str
    final_answer: Optional[dict]
