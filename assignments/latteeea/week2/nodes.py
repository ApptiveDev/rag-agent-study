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