import os

from dotenv import find_dotenv, load_dotenv
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

from rag.retriever import retrieve
from schema import RAGAnswer
from state import RAGState

load_dotenv(find_dotenv(), override=True)
os.environ["LANGSMITH_TRACING"] = "false"
os.environ["LANGSMITH_TRACING_V2"] = "false"

SYSTEM_PROMPT = """당신은 알고리즘 코딩 테스트를 돕는 학습 코치입니다.
아래 검색된 문서(context)만 근거로 한국어 마크다운으로 답하세요.

원칙:
1. context 에 있는 내용만 사용하고, 없으면 모른다고 말할 것
2. 패턴 이름·복잡도·코드는 context 에 적힌 표현을 따를 것
3. 답변에 어떤 패턴/문제 근거를 썼는지 자연스럽게 녹일 것
4. 패턴 키와 코드 식별자는 영어 원형 유지
"""

DEFAULT_STRATEGY = "markdown"
TOP_K = 4

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
structured_model = model.with_structured_output(RAGAnswer)


def format_docs(docs: list[Document]) -> str:
    blocks = []
    for i, doc in enumerate(docs, start=1):
        blocks.append(
            f"[문서 {i}] source={doc.metadata.get('source')} "
            f"chunk={doc.metadata.get('chunk_id')}\n{doc.page_content}"
        )
    return "\n\n".join(blocks)


def collect_sources(docs: list[Document]) -> list[str]:
    seen, sources = set(), []
    for doc in docs:
        source = doc.metadata.get("source")
        if source and source not in seen:
            seen.add(source)
            sources.append(source)
    return sources


def retrieve_node(state: RAGState) -> dict:
    strategy = state.get("strategy") or DEFAULT_STRATEGY
    docs = retrieve(state["question"], mode="vector", strategy=strategy, k=TOP_K)
    return {"strategy": strategy, "documents": docs, "context": format_docs(docs)}


def generate_node(state: RAGState) -> dict:
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=f"질문: {state['question']}\n\ncontext:\n{state['context']}"),
    ]
    answer = structured_model.invoke(messages)
    final = answer.model_dump()
    final["sources"] = collect_sources(state["documents"])
    return {"final_answer": final}


def build_graph():
    builder = StateGraph(RAGState)
    builder.add_node("retrieve", retrieve_node)
    builder.add_node("generate", generate_node)
    builder.add_edge(START, "retrieve")
    builder.add_edge("retrieve", "generate")
    builder.add_edge("generate", END)
    return builder.compile()


graph = build_graph()


def ask(question: str, strategy: str = DEFAULT_STRATEGY) -> dict:
    result = graph.invoke({"question": question, "strategy": strategy})
    return result["final_answer"]
