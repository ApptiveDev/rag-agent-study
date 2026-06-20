from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage
from langgraph.prebuilt import ToolNode

from schemas import AgentState, MinecraftRAGResponse
from tools import search_minecraft


TOOLS = [search_minecraft]

_llm = init_chat_model("gpt-4o-mini")
llm_with_tools = _llm.bind_tools(TOOLS)
llm_for_output = _llm.with_structured_output(MinecraftRAGResponse)

# 도구 실행 노드 — 오류 발생 시 에러 메시지를 ToolMessage로 전달하여 LLM이 재시도 가능
tool_node = ToolNode(TOOLS, handle_tool_errors=True)

SYSTEM_PROMPT = """당신은 마인크래프트 전문 지식 에이전트입니다.

사용자의 마인크래프트 관련 질문에 search_minecraft 도구를 활용하여 정확한 답변을 제공하세요.

사용 가능한 도구:
- search_minecraft: 마인크래프트 위키 문서 검색 (몹, 아이템, 레시피 등)

도구를 먼저 호출하여 문서를 검색한 뒤 답변하세요.
도구 결과를 그대로 복사하지 말고 자연스럽게 요약하여 답변하세요.
마크다운 문법은 사용하지 말고 일반 텍스트로만 답변하세요.
답변은 한국어로 하세요."""


def with_token_logging(node_fn):
    def wrapper(state):
        result = node_fn(state)
        last_msg = result["messages"][-1]
        if hasattr(last_msg, "usage_metadata") and last_msg.usage_metadata:
            usage = last_msg.usage_metadata
            print(f"[토큰] 입력: {usage['input_tokens']} | 출력: {usage['output_tokens']} | 합계: {usage['total_tokens']}")
        return result
    return wrapper


def agent_node(state: AgentState) -> dict:
    """LLM이 도구 호출 여부를 판단하고 응답을 생성하는 핵심 노드."""
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


def format_output_node(state: AgentState) -> dict:
    """대화 기록을 바탕으로 Pydantic 구조화 응답을 생성하는 노드."""
    messages = state["messages"]

    # 대화에서 사용된 도구·출처 추출
    tools_used: list[str] = []
    sources: list[str] = []
    for msg in messages:
        if isinstance(msg, AIMessage) and msg.tool_calls:
            for tc in msg.tool_calls:
                if tc["name"] not in tools_used:
                    tools_used.append(tc["name"])
        if isinstance(msg, ToolMessage):
            # 도구 결과에서 [출처: ...] 파싱
            for line in str(msg.content).split("\n"):
                if line.startswith("[출처:") and "]" in line:
                    src = line[len("[출처:"):line.index("]")].strip()
                    if src not in sources:
                        sources.append(src)

    # 최종 AI 메시지의 자연어 답변 추출
    last_ai_text = ""
    for msg in reversed(messages):
        if isinstance(msg, AIMessage):
            content = msg.content
            if isinstance(content, str) and content.strip():
                last_ai_text = content
                break
            elif isinstance(content, list):
                texts = [b["text"] for b in content if isinstance(b, dict) and b.get("type") == "text"]
                if texts:
                    last_ai_text = " ".join(texts)
                    break

    prompt = f"""다음 대화 기록을 바탕으로 마인크래프트 질문에 대한 구조화된 최종 응답을 생성하세요.

에이전트 최종 답변:
{last_ai_text}

위 내용을 바탕으로 아래 필드를 채워주세요:
- answer: 사용자 질문에 대한 완전하고 명확한 한국어 답변
- sources: 반드시 빈 리스트로 반환 ([]). 출처는 별도로 처리합니다.
- tools_used: 반드시 빈 리스트로 반환 ([]). 도구 목록은 별도로 처리합니다.
- confidence: 답변의 신뢰도 (문서 기반이면 0.9 이상, 일반 지식이면 0.7 정도)"""

    structured = llm_for_output.invoke(prompt)

    structured.sources = sources
    structured.tools_used = tools_used

    return {"structured_output": structured}
