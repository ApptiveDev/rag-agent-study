from langchain_core.tools import tool


BASEBALL_RULES = {
    "infield_fly": {
        "title": "Infield Fly",
        "summary": (
            "무사 또는 1사, 주자 1-2루 또는 만루에서 내야수가 보통 수비로 잡을 수 "
            "있는 페어 플라이가 뜨면 타자는 자동 아웃될 수 있습니다."
        ),
        "reference": "Official Baseball Rules 5.09(a)(5)",
    },
    "balk": {
        "title": "Balk",
        "summary": (
            "주자가 있을 때 투수가 투구 동작을 중단하거나 규정에 어긋나는 견제/동작을 "
            "하면 보크가 선언되고 주자는 한 베이스씩 진루합니다."
        ),
        "reference": "Official Baseball Rules 6.02(a)",
    },
    "tag_up": {
        "title": "Tag Up",
        "summary": (
            "플라이 타구가 잡힌 뒤 주자는 원래 베이스를 다시 밟은 다음 진루해야 합니다. "
            "잡히기 전에 출발했다면 어필 아웃 대상입니다."
        ),
        "reference": "Official Baseball Rules 5.09(b)(5)",
    },
    "dropped_third_strike": {
        "title": "Dropped Third Strike",
        "summary": (
            "포수가 세 번째 스트라이크를 잡지 못했고 1루가 비어 있거나 2사라면 타자는 "
            "1루로 뛸 수 있습니다."
        ),
        "reference": "Official Baseball Rules 5.05(a)(2)",
    },
}


BASEBALL_TERMS = {
    "ops": "출루율(OBP)과 장타율(SLG)을 더한 공격 지표입니다.",
    "whip": "투수가 이닝당 허용한 볼넷과 안타 수를 합친 지표입니다.",
    "보크": BASEBALL_RULES["balk"]["summary"],
    "인필드 플라이": BASEBALL_RULES["infield_fly"]["summary"],
    "태그업": BASEBALL_RULES["tag_up"]["summary"],
    "낫아웃": BASEBALL_RULES["dropped_third_strike"]["summary"],
}


@tool
def lookup_baseball_rule(topic: str) -> dict:
    """Look up a baseball rule by topic, such as balk, infield fly, or tag up."""
    normalized = topic.lower().replace(" ", "_")
    aliases = {
        "인필드_플라이": "infield_fly",
        "인필드플라이": "infield_fly",
        "보크": "balk",
        "태그업": "tag_up",
        "낫아웃": "dropped_third_strike",
        "스트라이크_낫아웃": "dropped_third_strike",
    }
    key = aliases.get(normalized, normalized)
    rule = BASEBALL_RULES.get(key)
    if not rule:
        return {
            "found": False,
            "topic": topic,
            "message": "Mock rule book does not contain this topic.",
        }
    return {"found": True, "topic": topic, **rule}


@tool
def judge_game_situation(situation: str) -> dict:
    """Judge a baseball game situation using mock rule data."""
    text = situation.lower()

    if "무사" in text or "1사" in text:
        early_outs = True
    else:
        early_outs = False

    if ("1,2루" in text or "1-2루" in text or "만루" in text) and (
        "뜬공" in text or "플라이" in text
    ):
        rule = BASEBALL_RULES["infield_fly"]
        return {
            "ruling": "인필드 플라이 가능성이 높습니다.",
            "reason": rule["summary"] if early_outs else "아웃카운트 조건을 추가 확인해야 합니다.",
            "reference": rule["reference"],
        }

    if "투구 동작" in text and ("멈" in text or "중단" in text):
        rule = BASEBALL_RULES["balk"]
        return {
            "ruling": "보크 가능성이 높습니다.",
            "reason": rule["summary"],
            "reference": rule["reference"],
        }

    if "플라이" in text and ("먼저 출발" in text or "일찍 출발" in text):
        rule = BASEBALL_RULES["tag_up"]
        return {
            "ruling": "어필 아웃 대상일 수 있습니다.",
            "reason": rule["summary"],
            "reference": rule["reference"],
        }

    return {
        "ruling": "추가 정보가 필요합니다.",
        "reason": "현재 mock 판정기는 인필드 플라이, 보크, 태그업 상황을 중심으로 판단합니다.",
        "reference": "local mock situation rules",
    }


@tool
def explain_baseball_term(term: str) -> dict:
    """Explain a baseball term in Korean."""
    normalized = term.lower().strip()
    explanation = BASEBALL_TERMS.get(normalized) or BASEBALL_TERMS.get(term.strip())
    if not explanation:
        return {
            "found": False,
            "term": term,
            "explanation": "Mock glossary does not contain this term.",
        }
    return {"found": True, "term": term, "explanation": explanation}


BASEBALL_TOOLS = [lookup_baseball_rule, judge_game_situation, explain_baseball_term]
