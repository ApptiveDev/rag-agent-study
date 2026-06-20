"""
테스트 질문 풀 — 수집한 위키 문서와 대조 후 A/B 그룹 분류.

분류 기준:
  Group A: 수집한 위키 문서 안에 직접적인 답이 있는 질문 (RAG 성능 측정)
  Group B: 문서에 답이 없거나, 모호하거나, 여러 문서를 거쳐야 하는 질문
            -> "모른다고 하는지 / 헛소리하는지" 관찰 (다음 주 Agentic RAG 빌드업)

분류 기준: crawl_wiki.py 실행 후 실제 24개 문서 직접 확인 완료 (2026-06-07).
"""

# -------------------------------------------------------
# Group A: 문서에 직접적인 답이 있는 질문 (verified=True 는 실제 문서 확인)
# -------------------------------------------------------
GROUP_A_QUESTIONS = [
    {
        "id": "A1",
        "question": "양조통(술통)에 넣을 수 있는 재료와 각각 만들어지는 제품은?",
        "expected_doc": "farming_keg.md",
        "verified": True,
        "note": "farming_keg.md 확인: 과일->와인, 채소->주스, 꽃->식물성 음료 등 표 있음.",
    },
    {
        "id": "A2",
        "question": "절임통에 넣을 수 있는 작물 종류와 산출 가공품은?",
        "expected_doc": "farming_preserves_jar.md",
        "verified": True,
        "note": "farming_preserves_jar.md에 재료 목록 확인.",
    },
    {
        "id": "A3",
        "question": "고대씨앗은 어떻게 얻고, 어디에 심을 수 있나?",
        "expected_doc": "farming_ancient_seed.md",
        "verified": True,
        "note": "farming_ancient_seed.md 확인: 유물 발굴->씨앗 복원, 봄~가을 재배, 온실 연중 가능.",
    },
    {
        "id": "A4",
        "question": "온실에 심은 작물은 계절 제한이 있나?",
        "expected_doc": "farming_greenhouse.md",
        "verified": True,
        "note": "farming_greenhouse.md 확인: 계절 무관 재배 가능 명시.",
    },
    {
        "id": "A5",
        "question": "피뢰침은 어떤 효과가 있고, 번개로부터 작물을 보호하려면 몇 개나 필요한가?",
        "expected_doc": "farming_lightning_rod.md",
        "verified": True,
        "note": "farming_lightning_rod.md 확인: 피뢰침 보호 메커니즘과 개당 보호 확률 설명.",
    },
    {
        "id": "A6",
        "question": "낚싯대에 미끼를 끼우는 방법은?",
        "expected_doc": "fishing_tackle.md",
        "verified": True,
        "note": "fishing_tackle.md 확인: 장착 방법(인벤에서 낚싯대에 우클릭) 설명.",
    },
    {
        "id": "A7",
        "question": "일반 달걀과 큰 달걀을 마요네즈 기계에 넣으면 품질이 다르게 나오나?",
        "expected_doc": "livestock_mayonnaise.md",
        "verified": True,
        "note": "livestock_mayonnaise.md 확인: 일반->기본 품질, 큰 달걀->금별. 달걀 별 등급은 영향 없음.",
    },
    {
        "id": "A8",
        "question": "스타듀밸리에서 결혼 조건과 절차는?",
        "expected_doc": "villagers_marriage.md",
        "verified": True,
        "note": "villagers_marriage.md 확인: 10하트 + 부케 -> 인어의 펜던트(5000골드) + 농가 업그레이드 1회.",
    },
    {
        "id": "A9",
        "question": "선물 등급(사랑/좋아함/평범/싫어함)에 따라 주민 호감도 포인트가 얼마나 오르나?",
        "expected_doc": "villagers_hearts.md",
        "verified": True,
        "note": "villagers_hearts.md 확인: 공식 = 이벤트 배수 x 선호도(사랑=80/좋아함=45) x 품질 배수.",
    },
    {
        "id": "A10",
        "question": "드워프 두루마리 I은 어디서 얻을 수 있나?",
        "expected_doc": "mining_dwarf_scroll1.md",
        "verified": True,
        "note": "mining_dwarf_scroll1.md 확인: 광산 몬스터 드롭 위치 설명.",
    },
]

# -------------------------------------------------------
# Group B: 문서 부재 / 모호 / 멀티홉 질문 (다음 주 Agentic RAG 빌드업 소재)
# -------------------------------------------------------
GROUP_B_QUESTIONS = [
    {
        "id": "B1",
        "question": "농작물 상자에 넣는 것과 피에르에게 파는 것의 차이가 있나?",
        "reason": "상자 판매 vs 피에르 판매 가격 차이는 수집된 24개 문서 어디에도 직접 설명 없음. "
                  "경제 시스템/판매처 비교 문서가 없어 RAG 실패 예상.",
    },
    {
        "id": "B2",
        "question": "외양간과 닭장 가축이 밖으로 안 나오는 이유와 해결 방법은?",
        "reason": "livestock_barn.md/livestock_coop.md에 건물 설명은 있지만, "
                  "'밖에 안 나오는 조건'(날씨, 문 열기, 에너지 등) 은 livestock_animals.md와 "
                  "여러 문서 참조 필요. 멀티홉 질문.",
    },
    {
        "id": "B3",
        "question": "용광로 앞에서 광물을 클릭해도 작동 안 할 때 어떻게 해야 하나?",
        "reason": "광산(mining_overview.md)에 용광로 사용법 일부 있을 수 있지만, "
                  "'클릭 방식'(우클릭 vs 인벤 드래그) 같은 게임 UI 문제는 수집 문서에 없음. "
                  "RAG 실패 또는 잘못된 답 출력 예상.",
    },
    {
        "id": "B4",
        "question": "마을에 설치한 상자가 자꾸 사라지는 이유는?",
        "reason": "상자 분실 원인(NPC 충돌, 업그레이드 이벤트, 마을 회관 복원 등) 은 "
                  "수집된 문서에 없음. RAG가 모른다고 답해야 정답.",
    },
    {
        "id": "B5",
        "question": "가축 먹이는 어떻게 주나, 겨울에는 자동으로 먹이가 공급되나?",
        "reason": "livestock_animals.md에 먹이 시스템 일부 있을 수 있지만, "
                  "겨울 건초 자동 공급 조건(사일로 유무, 자동 먹이 통)은 "
                  "여러 문서 연결 필요. 멀티홉 후보.",
    },
]

# -------------------------------------------------------
# 최종 테스트 실행 질문 (run.ipynb에서 사용)
# Group A에서 위키 문서 확인된 것으로 선정 (verified=True)
# -------------------------------------------------------
FINAL_TEST_QUESTIONS = [
    "양조통(술통)에 넣을 수 있는 재료와 각각 만들어지는 제품은?",          # A1
    "고대씨앗은 어떻게 얻고, 어디에 심을 수 있나?",                        # A3
    "온실에 심은 작물은 계절 제한이 있나?",                                # A4
    "낚싯대에 미끼를 끼우는 방법은?",                                     # A6
    "일반 달걀과 큰 달걀을 마요네즈 기계에 넣으면 품질이 다르게 나오나?",    # A7
    "스타듀밸리에서 결혼 조건과 절차는?",                                  # A8
]

if __name__ == "__main__":
    print("=== Group A (문서에 답 있음) ===")
    for q in GROUP_A_QUESTIONS:
        verified = "[문서 확인]" if q.get("verified") else "[미확인]"
        print(f"[{q['id']}] {verified} {q['question']}")
        print(f"     -> {q['expected_doc']}: {q['note'][:60]}...")
    print()
    print("=== Group B (문서 부재 / 멀티홉) ===")
    for q in GROUP_B_QUESTIONS:
        print(f"[{q['id']}] {q['question']}")
        print(f"     -> reason: {q['reason'][:70]}...")
    print()
    print("=== 최종 테스트 질문 ===")
    for i, q in enumerate(FINAL_TEST_QUESTIONS, 1):
        print(f"{i}. {q}")
