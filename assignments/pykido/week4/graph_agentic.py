import os

from dotenv import find_dotenv, load_dotenv
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph

from rag.retriever import retrieve
from schema import DocGrade, HallucinationGrade, RAGAnswer
from state import AgenticRAGState

load_dotenv(find_dotenv(), override=True)
os.environ["LANGSMITH_TRACING"] = "false"
os.environ["LANGSMITH_TRACING_V2"] = "false"

DEFAULT_STRATEGY = "markdown"
RETRIEVE_MODE = "rerank"
FIRST_STAGE_N = 50
TOP_K = 5
MAX_REWRITE = 2
MAX_REGEN = 2

GENERATE_SYSTEM = """당신은 알고리즘 코딩 테스트를 돕는 학습 코치입니다.
아래 검색된 문서(context)만 근거로 한국어 마크다운으로 답하세요.

원칙:
1. context 에 있는 내용만 사용하고, 없으면 모른다고 말할 것
2. 패턴 이름·복잡도·코드는 context 에 적힌 표현을 따를 것
3. 답변에 어떤 패턴/문제 근거를 썼는지 자연스럽게 녹일 것
4. 패턴 키와 코드 식별자는 영어 원형 유지
"""

GRADE_DOCS_SYSTEM = """당신은 검색 품질 평가자입니다.
검색된 문서 묶음이 사용자 질문에 답할 근거를 담고 있는지 binary 로 판정하세요.
관련 키워드나 의미가 일부라도 답에 쓸 수 있으면 'yes', 전혀 무관하면 'no'.
지나치게 엄격하지 말고, 답의 근거가 될 수 있으면 yes 로 판정합니다."""

HALLUCINATION_SYSTEM = """당신은 환각 검사자입니다.
생성된 답변의 핵심 주장이 모두 검색된 문서(context)로 뒷받침되는지 binary 로 판정하세요.
context 에 없는 사실을 지어냈으면 'no'(환각), 전부 근거가 있으면 'yes'.
답변이 '근거가 없어 모른다'고 정직하게 말한 경우는 환각이 아니므로 'yes' 로 봅니다."""

REWRITE_SYSTEM = """당신은 검색 질의 재작성기입니다.
원래 질문의 의도는 유지하되, 알고리즘 학습 문서 검색이 잘 되도록
핵심 개념어·자료구조·기법 이름을 드러내 한국어 한 문장으로 다시 쓰세요.
질문만 출력하고 다른 설명은 붙이지 마세요."""

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
gen_model = model.with_structured_output(RAGAnswer)
doc_grader = model.with_structured_output(DocGrade)
hallucination_grader = model.with_structured_output(HallucinationGrade)


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


def retrieve_node(state: AgenticRAGState) -> dict:
    strategy = state.get("strategy") or DEFAULT_STRATEGY
    query = state.get("query") or state["question"]
    docs = retrieve(
        query,
        mode=RETRIEVE_MODE,
        strategy=strategy,
        k=TOP_K,
        first_stage_n=FIRST_STAGE_N,
    )
    return {"strategy": strategy, "query": query, "documents": docs, "context": format_docs(docs)}


def grade_docs_node(state: AgenticRAGState) -> dict:
    messages = [
        SystemMessage(content=GRADE_DOCS_SYSTEM),
        HumanMessage(content=f"질문: {state['question']}\n\n검색된 문서:\n{state['context']}"),
    ]
    grade = doc_grader.invoke(messages)
    return {"doc_grade": grade.relevant}


def rewrite_node(state: AgenticRAGState) -> dict:
    base = state.get("query") or state["question"]
    messages = [
        SystemMessage(content=REWRITE_SYSTEM),
        HumanMessage(content=f"원래 질문: {state['question']}\n직전 질의: {base}"),
    ]
    rewritten = model.invoke(messages).content.strip()
    return {"query": rewritten, "rewrite_count": state.get("rewrite_count", 0) + 1}


def _generate(state: AgenticRAGState, feedback: str | None = None) -> dict:
    human = f"질문: {state['question']}\n\ncontext:\n{state['context']}"
    if feedback:
        human += f"\n\n{feedback}"
    messages = [SystemMessage(content=GENERATE_SYSTEM), HumanMessage(content=human)]
    answer = gen_model.invoke(messages)
    final = answer.model_dump()
    final["sources"] = collect_sources(state["documents"])
    return {"final_answer": final}


def generate_node(state: AgenticRAGState) -> dict:
    return _generate(state)


def check_hallucination_node(state: AgenticRAGState) -> dict:
    answer_text = (state.get("final_answer") or {}).get("answer", "")
    messages = [
        SystemMessage(content=HALLUCINATION_SYSTEM),
        HumanMessage(content=f"context:\n{state['context']}\n\n생성된 답변:\n{answer_text}"),
    ]
    grade = hallucination_grader.invoke(messages)
    return {"hallucination_grade": grade.grounded}


def regenerate_node(state: AgenticRAGState) -> dict:
    prior = (state.get("final_answer") or {}).get("answer", "")
    feedback = (
        "이전 답변에 context 로 뒷받침되지 않는 내용이 있었습니다.\n"
        f"이전 답변: {prior}\n"
        "context 에 실제로 적힌 내용만으로 다시 작성하고, 근거가 없는 부분은 '모른다'고 하세요."
    )
    out = _generate(state, feedback=feedback)
    out["regen_count"] = state.get("regen_count", 0) + 1
    return out


def route_after_grade(state: AgenticRAGState) -> str:
    if state.get("doc_grade") == "yes":
        return "generate"
    if state.get("rewrite_count", 0) < MAX_REWRITE:
        return "rewrite"
    return "generate"


def route_after_hallucination(state: AgenticRAGState) -> str:
    if state.get("hallucination_grade") == "yes":
        return END
    if state.get("regen_count", 0) < MAX_REGEN:
        return "regenerate"
    return END


def build_graph():
    builder = StateGraph(AgenticRAGState)
    builder.add_node("retrieve", retrieve_node)
    builder.add_node("grade_docs", grade_docs_node)
    builder.add_node("rewrite", rewrite_node)
    builder.add_node("generate", generate_node)
    builder.add_node("regenerate", regenerate_node)
    builder.add_node("check_hallucination", check_hallucination_node)

    builder.add_edge(START, "retrieve")
    builder.add_edge("retrieve", "grade_docs")
    builder.add_conditional_edges(
        "grade_docs",
        route_after_grade,
        {"generate": "generate", "rewrite": "rewrite"},
    )
    builder.add_edge("rewrite", "retrieve")
    builder.add_edge("generate", "check_hallucination")
    builder.add_conditional_edges(
        "check_hallucination",
        route_after_hallucination,
        {"regenerate": "regenerate", END: END},
    )
    builder.add_edge("regenerate", "check_hallucination")
    return builder.compile()


graph = build_graph()


def ask(question: str, strategy: str = DEFAULT_STRATEGY) -> dict:
    result = graph.invoke(
        {"question": question, "strategy": strategy, "rewrite_count": 0, "regen_count": 0}
    )
    return result["final_answer"]
