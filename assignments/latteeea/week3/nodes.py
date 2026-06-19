from langgraph.types import interrupt
from state import AgentState


HYPOTHESES_KEYWORDS = [
    "설계 문제",
    "구조 문제",
    "boundary 문제",
    "단순 버그가 아니다",
    "단순 버그",
    "경계",
    "원인"
]

def extract_hypotheses_nodes(state):
    last_messages = state["messages"][-1]
    content = getattr(last_messages, "content","")
    
    existing = state.get("hypotheses", [])
    
    matched_keywords = [
        keyword for keyword in HYPOTHESES_KEYWORDS
        if keyword.lower() in content.lower()
    ]
    
    if not matched_keywords:
        return {}
    
    new_hypothesis = {
        "claim": content,
        "type": "user_interpretation",
        "matched_keywords": matched_keywords,
        "status": "active",
    }
            
    return {
        "hypotheses": existing + [new_hypothesis]
    }
    
def narrative_interrupt_node(state: AgentState):
    last_message = state["messages"][-1]
    content = getattr(last_message, "content", "")
    
    if state.get("narrative_intent"):
        return {}
    
    should_interrupt = (
        "글" in content
        or "블로그" in content
        or "아웃라인" in content
    )
    
    if not should_interrupt:
        return {}
    
    choice = interrupt({
        "question": "어떤 narrative 방향으로 정리할까요?",
        "options": {
            "1": "디버깅 흐름 중심",
            "2": "구조적 설계 문제 중심",
            "3": "운영 장애 리뷰 중심",
        }
    })
    
    intent_map = {
        "1": "debugging_flow",
        "2": "architectural_problem",
        "3": "operation_error_review"
    }
    
    return {
        "narrative_intent": intent_map.get(str(choice), "debugging_flow")
    }