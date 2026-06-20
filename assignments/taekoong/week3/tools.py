from langchain_core.tools import tool
from rag import get_retriever, load_index

## RAG 검색기 초기화 (chroma_db에서 불러옴)
_vectorstore = load_index()
_retriever = get_retriever(_vectorstore)


@tool
def search_minecraft(query: str) -> str:
    """마인크래프트 관련 정보를 위키 문서에서 검색합니다.
    몹, 아이템, 레시피, 전투 팁 등을 질문하면 관련 문서를 반환합니다.

    Args:
        query: 검색할 내용 (영어로 입력하면 검색 정확도가 높아집니다)
    """
    docs = _retriever.invoke(query)
    if not docs:
        return "관련 문서를 찾지 못했습니다."

    results = []
    for doc in docs:
        source = doc.metadata.get("source", "알 수 없음")
        results.append(f"[출처: {source}]\n{doc.page_content}")

    return "\n\n".join(results)
