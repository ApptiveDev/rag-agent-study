from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from retriever import retrieve

load_dotenv()

def format_docs(docs):
    formatted = []
    
    for i, doc in enumerate(docs, start=1):
        source = doc.metadata.get("source", "unknown")
        chunk_id = doc.metadata.get("chunk_id", "unknown")
        
        formatted.append(
            f"[문서 {i}]\n"
            f"source: {source}\n"
            f"chunk_id: {chunk_id}\n"
            f"content:\n{doc.page_content}"
        )
        
    return "\n\n".join(formatted)

def answer_question(
    question: str,
    strategy: str = "markdown",
    k: int = 4,
) -> dict:
    docs = retrieve(query=question, strategy=strategy, k=k)
    context = format_docs(docs)
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature = 0)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
    """
    너는 사용자의 기술 트러블슈팅 기록을 기반으로 답변하는 RAG assistant 이다.
    
    규칙:
    - 제공된 context 안의 내용을 근거고 대답하되, 중간 단계가 비어있는 경우 적당히 추측해서 채워넣는다. 이때 추측한 내용은 [추측] 이라고 무조건 표시한다. 
    - 답변에는 문제 상황, 해결, 인사이트를 가능한 한 구분해서 정리한다.
    - 마지막에 참고 문서 source를 반드시 포함한다.
    
    """,
            ),
            (
                "human",
                """
                질문: {question}
                
                검색된 context: {context}
                """,
            ),
        ]
    )
    
    chain = prompt | llm
    response = chain.invoke(
        {
            "question": question,
            "context": context,
        }
    )
    
    sources = [
        {
            "source": doc.metadata.get("source"),
            "filename": doc.metadata.get("filename"),
            "chunk_id": doc.metadata.get("chunk_id"),
            "strategy": doc.metadata.get("chunk_strategy"),
        }
        for doc in docs
    ]
    
    return {
        "question": question,
        "strategy": strategy,
        "answer": response.content,
        "sources": sources,
    }
    
def print_qa_result(result: dict):
    print("=" * 100)
    print(f"Question: {result['question']}")
    print(f"Strategy: {result['strategy']}")
    print("-" * 100)
    print(result["answer"])
    print("-" * 100)
    print("Sources:")
    for source in result["sources"]:
        print(
            f"- {source['filename']} | "
            f"{source['chunk_id']} | "
            f"{source['strategy']}"
        )
        
if __name__ == "__main__":
    result = answer_question(
        question="외부 API 변경으로 장애가 발생한 사례를 원인과 해결 중심으로 정리해줘",
        strategy="markdown",
        k=4,
    )
    
    print_qa_result(result)