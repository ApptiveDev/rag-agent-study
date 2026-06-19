from langgraph.graph import END, START, StateGraph

from nodes import (
    decide_to_generate,
    generate_node,
    grade_documents_node,
    grade_generation,
    retrieve_node,
    transform_query_node,
)
from state import GraphState


def build_graph():
    workflow = StateGraph(GraphState)

    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("grade_documents", grade_documents_node)
    workflow.add_node("generate", generate_node)
    workflow.add_node("transform_query", transform_query_node)

    workflow.add_edge(START, "retrieve")
    workflow.add_edge("retrieve", "grade_documents")
    workflow.add_conditional_edges(
        "grade_documents",
        decide_to_generate,
        {
            "transform_query": "transform_query",
            "generate": "generate",
        },
    )
    workflow.add_edge("transform_query", "retrieve")
    workflow.add_conditional_edges(
        "generate",
        grade_generation,
        {
            "hallucination": "generate",
            "relevant": END,
            "not relevant": "transform_query",
        },
    )

    return workflow.compile()


def run_agentic_rag(
    question: str,
    strategy: str = "markdown",
) -> dict:
    app = build_graph()
    result = app.invoke(
        {
            "question": question,
            "original_question": question,
            "generation": "",
            "documents": [],
            "strategy": strategy,
            "rewrite_count": 0,
            "generation_attempts": 0,
        }
    )

    sources = [
        {
            "source": doc.metadata.get("source"),
            "filename": doc.metadata.get("filename"),
            "chunk_id": doc.metadata.get("chunk_id"),
            "strategy": doc.metadata.get("chunk_strategy"),
        }
        for doc in result.get("documents", [])
    ]

    return {
        "question": result.get("original_question", question),
        "rewritten_question": result.get("question", question),
        "rewrite_count": result.get("rewrite_count", 0),
        "strategy": strategy,
        "answer": result.get("generation", ""),
        "sources": sources,
    }
