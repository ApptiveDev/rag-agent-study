from langchain_core.tools import tool
"""스타듀밸리 도메인 도구 정의.

각 도구는 mock 데이터를 사용. 추후 위키 스크래퍼로 교체 가능한 구조.
"""


# ─── Mock 데이터 ───────────────────────────────────────────────
# 실제 프로젝트에서는 data/ 폴더에 JSON으로 분리하는 게 좋지만
# 1주차에선 도구 자체가 작동하는지가 중요하므로 인라인 처리.

_NPC_DATABASE = {
    "Abigail": {
        "birthday": "Fall 13",
        "loved_gifts": ["Amethyst", "Banana Pudding", "Blackberry Cobbler",
                        "Chocolate Cake", "Pufferfish", "Pumpkin",
                        "Spicy Eel"],
        "location_default": "Pierre's General Store",
        "heart_events": {2: "방에서 일어나는 이벤트", 4: "묘지 이벤트",
                         6: "기타 연주 이벤트", 8: "동굴 탐험 이벤트",
                         10: "결혼 가능"},
    },
    "Sebastian": {
        "birthday": "Winter 10",
        "loved_gifts": ["Frozen Tear", "Obsidian", "Pumpkin Soup",
                        "Sashimi", "Void Egg"],
        "location_default": "지하 방 (산속 집)",
        "heart_events": {2: "방에서 작업 중", 4: "오토바이 이벤트",
                         8: "비 오는 날 호수 이벤트", 10: "결혼 가능"},
    },
    "Emily": {
        "birthday": "Spring 27",
        "loved_gifts": ["Amethyst", "Aquamarine", "Cloth", "Emerald",
                        "Jade", "Ruby", "Survival Burger", "Topaz", "Wool"],
        "location_default": "Stardrop Saloon (오후 근무)",
        "heart_events": {2: "옷 만들기 이벤트", 4: "꿈 이벤트",
                         6: "춤 이벤트", 14: "결혼 가능"},
    },
    # 실제 구현에서는 30명 전부, 지금은 3명만으로 충분.
}

_FISH_DATABASE = [
    {"name": "Sardine", "season": ["Spring", "Fall", "Winter"],
     "weather": "any", "time": "06:00-19:00",
     "location": "Ocean", "difficulty": 30},
    {"name": "Pufferfish", "season": ["Summer"],
     "weather": "sunny", "time": "12:00-16:00",
     "location": "Ocean", "difficulty": 80},
    {"name": "Catfish", "season": ["Spring", "Fall"],
     "weather": "rainy", "time": "06:00-24:00",
     "location": "River", "difficulty": 75},
    {"name": "Legend", "season": ["Spring"],
     "weather": "rainy", "time": "06:00-23:00",
     "location": "Mountain Lake", "difficulty": 110},
    # ...
]

_CROP_DATABASE = {
    "Spring": [
        {"name": "Strawberry", "seed_cost": 100, "sell_price": 120,
         "grow_days": 8, "regrowth": 4,
         "note": "Egg Festival에서만 씨앗 구매 가능"},
        {"name": "Cauliflower", "seed_cost": 80, "sell_price": 175,
         "grow_days": 12, "regrowth": None},
        {"name": "Potato", "seed_cost": 50, "sell_price": 80,
         "grow_days": 6, "regrowth": None},
    ],
    "Summer": [
        {"name": "Blueberry", "seed_cost": 80, "sell_price": 50,
         "grow_days": 13, "regrowth": 4,
         "note": "수확 시 3개씩 — 실수익 최강"},
        {"name": "Starfruit", "seed_cost": 400, "sell_price": 750,
         "grow_days": 13, "regrowth": None},
    ],
    # ...
}


# ─── 도구 1: NPC 정보 ─────────────────────────────────────────
@tool
def get_npc_info(npc_name: str) -> str:
    """스타듀밸리 NPC의 기본 정보를 반환합니다.

    생일, 좋아하는 선물, 기본 위치, 하트 이벤트 정보를 포함합니다.
    플레이어가 특정 NPC와 친해지고 싶거나, 생일 선물을 고민할 때 사용하세요.

    Args:
        npc_name: NPC 이름 (예: 'Abigail', 'Sebastian', 'Emily'). 영문 표기.
    """
    # docstring을 정성껏 — LLM이 이 설명만 보고 도구 선택 여부를 결정해요.
    info = _NPC_DATABASE.get(npc_name)
    if not info:
        return f"'{npc_name}' NPC 정보를 찾을 수 없습니다. 영문 이름으로 다시 시도해주세요."

    return (
        f"=== {npc_name} ===\n"
        f"생일: {info['birthday']}\n"
        f"좋아하는 선물: {', '.join(info['loved_gifts'])}\n"
        f"기본 위치: {info['location_default']}\n"
        f"하트 이벤트: {info['heart_events']}"
    )


# ─── 도구 2: 물고기 찾기 ───────────────────────────────────────
@tool
def find_fish(season: str, weather: str = "any", location: str = "any") -> str:
    """조건에 맞는 스타듀밸리 물고기를 찾아 반환합니다.

    계절, 날씨, 장소를 기준으로 잡을 수 있는 물고기 목록을 줍니다.
    "지금 잡을 수 있는 물고기" 같은 질문에 사용하세요.

    Args:
        season: 계절. 'Spring', 'Summer', 'Fall', 'Winter' 중 하나.
        weather: 날씨. 'sunny', 'rainy', 'any' 중 하나. 기본값 'any'.
        location: 장소. 'Ocean', 'River', 'Mountain Lake', 'any' 중 하나.
    """
    matched = []
    for fish in _FISH_DATABASE:
        if season not in fish["season"]:
            continue
        if weather != "any" and fish["weather"] != "any" and fish["weather"] != weather:
            continue
        if location != "any" and fish["location"] != location:
            continue
        matched.append(fish)

    if not matched:
        return f"{season}/{weather}/{location} 조건에 맞는 물고기가 없습니다."

    lines = [f"=== {season} / {weather} / {location} 에서 잡을 수 있는 물고기 ==="]
    for f in matched:
        lines.append(
            f"- {f['name']} (난이도 {f['difficulty']}, "
            f"시간 {f['time']}, {f['location']})"
        )
    return "\n".join(lines)


# ─── 도구 3: 작물 수익 최적화 ───────────────────────────────────
@tool
def optimize_crop_profit(season: str, budget_g: int = 1000) -> str:
    """주어진 예산과 계절에서 가장 수익이 좋은 작물을 추천합니다.

    씨앗 가격, 판매가, 성장 기간, 재성장 여부를 고려해 일당 수익을 계산합니다.
    "이번 시즌 뭐 심을지" 고민할 때 사용하세요.

    Args:
        season: 계절. 'Spring', 'Summer', 'Fall', 'Winter' 중 하나.
        budget_g: 씨앗 구매 예산 (gold). 기본값 1000.
    """
    crops = _CROP_DATABASE.get(season, [])
    if not crops:
        return f"{season} 작물 정보가 없습니다."

    analyzed = []
    for c in crops:
        if c["seed_cost"] > budget_g:
            continue
        max_seeds = budget_g // c["seed_cost"]
        if c["regrowth"]:
            # 재성장: 첫 수확 후 regrowth마다 반복 (28일 시즌 기준)
            harvests = 1 + max(0, (28 - c["grow_days"]) // c["regrowth"])
        else:
            harvests = 28 // c["grow_days"]
        gross = max_seeds * harvests * c["sell_price"]
        net = gross - (max_seeds * c["seed_cost"])
        analyzed.append((c["name"], net, max_seeds, harvests, c.get("note", "")))

    analyzed.sort(key=lambda x: x[1], reverse=True)

    lines = [f"=== {season} 예산 {budget_g}g 작물 수익 분석 ==="]
    for name, net, seeds, harvests, note in analyzed:
        line = f"- {name}: 순이익 {net:,}g (씨앗 {seeds}개 × {harvests}회 수확)"
        if note:
            line += f" — {note}"
        lines.append(line)
    return "\n".join(lines)


# ─── export ───────────────────────────────────────────────────
ALL_TOOLS = [get_npc_info, find_fish, optimize_crop_profit]