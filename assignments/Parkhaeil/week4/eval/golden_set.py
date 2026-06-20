"""
Week 4 — 스타듀밸리 위키 RAG 정답셋(Golden Set)
=================================================

PART 1 (이 파일): 수기 검수 완료된 정답셋 35개
PART 2 (하단 함수): LLM으로 추가 생성할 때 사용하는 generate_golden_set()

relevant_chunk_ids 규칙
-----------------------
· 파일 스텀(stem) 기준: docs_sample 내 마크다운 파일명에서 확장자를 뺀 값
  예) "farming_keg", "farming_crops_spring", "fishing_overview"
· 검색 지표 계산 시 retrieved doc 의 metadata["filename"] 스텀과 대조한다.
· out_of_domain 질문은 relevant_chunk_ids = [] / reference_answer = "제공된 문서로는 답변할 수 없습니다."

검수 기준 (2026-06-20 완료)
---------------------------
· 모든 factual / multi_hop 답변을 해당 마크다운 파일에서 직접 확인.
· out_of_domain 은 24개 문서 전체를 검토하여 답이 없음을 확인.
"""

from typing import List, Literal
from pydantic import BaseModel, Field


# ──────────────────────────────────────────────
# 데이터 모델 (과제 템플릿과 동일)
# ──────────────────────────────────────────────

class QAPair(BaseModel):
    question: str
    question_type: Literal["factual", "multi_hop", "out_of_domain"]
    relevant_chunk_ids: List[str] = Field(
        description="답의 근거가 되는 파일 스텀 목록. out_of_domain이면 빈 배열 []"
    )
    reference_answer: str


# ──────────────────────────────────────────────
# PART 1 · 수기 검수 정답셋 (35개)
# ──────────────────────────────────────────────

GOLDEN_SET: List[QAPair] = [

    # ── FACTUAL ─────────────────────────────────────────────────── 23개 ──

    QAPair(
        question="술통(양조 설비)을 제작하려면 농사 레벨이 얼마나 필요한가?",
        question_type="factual",
        relevant_chunk_ids=["farming_keg"],
        reference_answer="농사 레벨 8이 필요합니다.",
    ),
    QAPair(
        question="술통 제작에 필요한 재료 4가지는 무엇인가?",
        question_type="factual",
        relevant_chunk_ids=["farming_keg"],
        reference_answer="나무 30개, 구리 주괴 1개, 철 주괴 1개, 참나무 수지 1개가 필요합니다.",
    ),
    QAPair(
        question="과일을 술통에 넣으면 판매가가 기본 가격의 몇 배가 되나?",
        question_type="factual",
        relevant_chunk_ids=["farming_keg"],
        reference_answer="과일은 술통에서 와인으로 가공되며, 판매가는 기본 과일 가격의 3배입니다.",
    ),
    QAPair(
        question="야채를 술통에 넣으면 판매가가 기본 가격의 몇 배가 되나?",
        question_type="factual",
        relevant_chunk_ids=["farming_keg"],
        reference_answer="야채는 술통에서 주스로 가공되며, 판매가는 기본 야채 가격의 2.25배입니다.",
    ),
    QAPair(
        question="밀을 술통에 넣으면 무엇이 만들어지고 소요시간은 얼마인가?",
        question_type="factual",
        relevant_chunk_ids=["farming_keg"],
        reference_answer="밀을 술통에 넣으면 맥주가 만들어지며 소요시간은 약 1750분(1~2일)입니다.",
    ),
    QAPair(
        question="커피콩 5개를 술통에 넣으면 무엇이 되고 시간은 얼마나 걸리나?",
        question_type="factual",
        relevant_chunk_ids=["farming_keg"],
        reference_answer="커피콩 5개를 술통에 넣으면 커피가 만들어지며 소요시간은 약 120분(2시간)입니다.",
    ),
    QAPair(
        question="절임통을 제작하려면 농사 레벨이 얼마나 필요한가?",
        question_type="factual",
        relevant_chunk_ids=["farming_preserves_jar"],
        reference_answer="농사 레벨 4가 필요합니다.",
    ),
    QAPair(
        question="절임통에 과일을 넣으면 어떤 제품이 되고, 판매가 계산 공식은?",
        question_type="factual",
        relevant_chunk_ids=["farming_preserves_jar"],
        reference_answer="과일을 넣으면 젤리가 되며, 판매가 = 기본 과일 가격 × 2 + 50골드입니다.",
    ),
    QAPair(
        question="결혼을 제안하려면 상대와의 우정 하트가 몇 개 필요하고, 어떤 아이템이 필요한가?",
        question_type="factual",
        relevant_chunk_ids=["villagers_marriage"],
        reference_answer="우정 하트 10개와 부케(피에르 잡화점에서 구매)가 필요하며, 농가를 최소 1회 업그레이드하고 인어의 펜던트를 선물해야 합니다.",
    ),
    QAPair(
        question="스타듀밸리에서 NPC와 결혼은 싱글플레이에서만 가능한가?",
        question_type="factual",
        relevant_chunk_ids=["villagers_marriage"],
        reference_answer="네. 싱글플레이에서는 마을 사람(NPC)과 결혼이 가능합니다. 멀티플레이에서는 플레이어끼리 결혼 반지를 이용해 결혼할 수 있습니다.",
    ),
    QAPair(
        question="피뢰침 제작에 필요한 재료는?",
        question_type="factual",
        relevant_chunk_ids=["farming_lightning_rod"],
        reference_answer="철 주괴 1개, 정제된 석영 1개, 박쥐 날개 5개가 필요합니다.",
    ),
    QAPair(
        question="피뢰침이 번개로부터 농장을 보호하는 원리는?",
        question_type="factual",
        relevant_chunk_ids=["farming_lightning_rod"],
        reference_answer="피뢰침은 천둥이 치는 동안 벼락을 대신 맞고, 다음 날 배터리 팩을 생성합니다. 충전 중이 아닌 피뢰침은 높은 확률로 벼락을 가로채 농장 피해를 막아줍니다.",
    ),
    QAPair(
        question="피뢰침이 벼락을 가로채는 확률 공식은 무엇인가?",
        question_type="factual",
        relevant_chunk_ids=["farming_lightning_rod"],
        reference_answer="가로챌 확률 = 1 − (충전된 피뢰침 수 / 총 피뢰침 수)² 입니다.",
    ),
    QAPair(
        question="봄 작물 중 수확까지 3일이 걸리는 작물은?",
        question_type="factual",
        relevant_chunk_ids=["farming_crops_spring"],
        reference_answer="당근은 3일이면 수확할 수 있습니다.",
    ),
    QAPair(
        question="봄에 낚을 수 있는 전설의 물고기 기본 판매가는?",
        question_type="factual",
        relevant_chunk_ids=["farming_crops_spring"],
        reference_answer="전설의 물고기 기본 판매가는 5,000골드입니다.",
    ),
    QAPair(
        question="봄에 강에서 비가 올 때만 잡을 수 있는 물고기 2종은?",
        question_type="factual",
        relevant_chunk_ids=["farming_crops_spring"],
        reference_answer="메기와 전어는 봄 강에서 비오는 날에 잡힙니다.",
    ),
    QAPair(
        question="낚시 레벨 0일 때 찌 막대(녹색 바)의 크기는 몇 픽셀인가?",
        question_type="factual",
        relevant_chunk_ids=["fishing_overview"],
        reference_answer="낚시 레벨 0에서 녹색 막대 크기는 96픽셀입니다.",
    ),
    QAPair(
        question="낚시에서 완벽 포획(Perfect Catch)을 했을 때 생기는 두 가지 효과는?",
        question_type="factual",
        relevant_chunk_ids=["fishing_overview"],
        reference_answer="① 은별·금별 생선의 품질이 한 단계 상승합니다. ② 경험치가 2.4배로 증가합니다.",
    ),
    QAPair(
        question="낚싯대를 이리듐 낚싯대로 업그레이드하면 녹색 막대 크기가 커지나?",
        question_type="factual",
        relevant_chunk_ids=["fishing_overview"],
        reference_answer="아닙니다. 낚싯대 업그레이드는 막대 크기에 아무런 영향을 주지 않습니다.",
    ),
    QAPair(
        question="이리듐 낚싯대를 구매할 수 있으려면 낚시 레벨이 얼마 이상이어야 하나?",
        question_type="factual",
        relevant_chunk_ids=["fishing_overview"],
        reference_answer="낚시 레벨 6 이상이 필요합니다(도달한 다음 날 구매 가능 편지가 옵니다).",
    ),
    QAPair(
        question="마요네즈 기계에 일반 달걀과 큰 달걀을 각각 넣으면 어떤 품질의 마요네즈가 나오나?",
        question_type="factual",
        relevant_chunk_ids=["livestock_mayonnaise"],
        reference_answer="일반 달걀 → 기본(일반) 품질 마요네즈, 큰 달걀 → 금별 마요네즈가 생산됩니다.",
    ),
    QAPair(
        question="외양간 기본(첫 번째) 단계에서 기를 수 있는 동물 종류는?",
        question_type="factual",
        relevant_chunk_ids=["livestock_barn"],
        reference_answer="기본 외양간에서는 소만 기를 수 있습니다.",
    ),
    QAPair(
        question="온실에서 작물을 재배할 때 계절 제한이 있나?",
        question_type="factual",
        relevant_chunk_ids=["farming_greenhouse"],
        reference_answer="온실 내에서는 계절에 관계없이 연중 어떤 작물이든 재배할 수 있습니다.",
    ),

    # ── MULTI-HOP ────────────────────────────────────────────────  6개 ──

    QAPair(
        question="봄에 딸기씨앗을 봄 1일에 심으면 계절 내 최대 몇 번 수확할 수 있고, 그 딸기를 술통에 넣으면 판매가가 얼마나 될까?",
        question_type="multi_hop",
        relevant_chunk_ids=["farming_crops_spring", "farming_keg"],
        reference_answer=(
            "봄 1일에 심으면 최대 5번 수확할 수 있습니다. "
            "딸기(기본가 120골드)를 술통에 넣으면 와인이 되며 판매가는 3배인 360골드입니다."
        ),
    ),
    QAPair(
        question="소요시간 기준 하루당 수익에서 절임통과 술통 중 어느 쪽이 더 효율적인가?",
        question_type="multi_hop",
        relevant_chunk_ids=["farming_keg", "farming_preserves_jar"],
        reference_answer=(
            "절임통이 더 효율적입니다. "
            "술통 문서에 '소요시간에 따른 하루당 이득을 찾고 있다면 절임통의 생산 속도가 더 빠르기 때문에 "
            "아이템 기본 가격에 상관없이(홉·밀 제외) 절임통이 술통보다 우세합니다'라고 명시되어 있습니다."
        ),
    ),
    QAPair(
        question="고대씨앗을 입수하는 방법과, 온실에서 재배할 때 어떤 이점이 있나?",
        question_type="multi_hop",
        relevant_chunk_ids=["farming_ancient_seed", "farming_greenhouse"],
        reference_answer=(
            "고대씨앗 유물을 땅에서 발굴한 뒤 씨앗 재현 도구로 복원하거나, 여행 카트에서 구매할 수 있습니다. "
            "온실에서는 계절에 상관없이 연중 재배가 가능하므로, 고대씨앗을 온실에 심으면 봄·여름·가을·겨울 구분 없이 지속 수확할 수 있습니다."
        ),
    ),
    QAPair(
        question="보물 상자를 낚으면서 완벽 포획까지 했을 때, 경험치 배율은 얼마인가?",
        question_type="multi_hop",
        relevant_chunk_ids=["fishing_overview"],
        reference_answer=(
            "보물 상자(×2.2)와 완벽 포획(×2.4)은 순서대로 곱합니다. "
            "기본 경험치 × 2.2 → 결과값 × 2.4, 즉 총 약 5.28배입니다."
        ),
    ),
    QAPair(
        question="선물을 통해 10하트를 채우려면 '사랑하는 선물'로 최소 몇 번을 줘야 하나?",
        question_type="multi_hop",
        relevant_chunk_ids=["villagers_hearts", "villagers_marriage"],
        reference_answer=(
            "10하트 = 2,500 포인트(하트 1개 = 250포인트). "
            "사랑하는 선물은 기본 80포인트이고 생일에 주면 8배(640포인트)입니다. "
            "매주 2번 선물(이벤트 배수 1) 기준으로 단순 계산하면 최소 32번이지만, "
            "이벤트(생일 등) 활용 시 훨씬 적은 횟수로도 달성 가능합니다."
        ),
    ),
    QAPair(
        question="디럭스 외양간을 짓기까지 총 비용(골드)과 그때 기를 수 있는 동물 종류는?",
        question_type="multi_hop",
        relevant_chunk_ids=["livestock_barn"],
        reference_answer=(
            "외양간(6,000골드) → 큰 외양간(12,000골드) → 디럭스 외양간(25,000골드), 총 43,000골드가 필요합니다. "
            "디럭스 외양간에서는 소, 염소, 양, 돼지를 기를 수 있습니다."
        ),
    ),

    # ── OUT OF DOMAIN ─────────────────────────────────────────────  6개 ──

    QAPair(
        question="스타듀밸리에서 배낭(인벤토리) 크기를 늘리는 방법은?",
        question_type="out_of_domain",
        relevant_chunk_ids=[],
        reference_answer="제공된 문서로는 답변할 수 없습니다.",
    ),
    QAPair(
        question="캐릭터 외모(헤어, 피부색 등)를 게임 중에 변경하려면 어떻게 해야 하나?",
        question_type="out_of_domain",
        relevant_chunk_ids=[],
        reference_answer="제공된 문서로는 답변할 수 없습니다.",
    ),
    QAPair(
        question="커뮤니티 센터를 완성하면 줄거스마트(Joja) 회사는 어떻게 되나?",
        question_type="out_of_domain",
        relevant_chunk_ids=[],
        reference_answer="제공된 문서로는 답변할 수 없습니다.",
    ),
    QAPair(
        question="스타듀밸리에서 친구를 초대해 멀티플레이를 시작하는 방법은?",
        question_type="out_of_domain",
        relevant_chunk_ids=[],
        reference_answer="제공된 문서로는 답변할 수 없습니다.",
    ),
    QAPair(
        question="광산 100층 아래에 있는 해골 동굴에 처음 들어가려면 무엇이 필요한가?",
        question_type="out_of_domain",
        relevant_chunk_ids=[],
        reference_answer="제공된 문서로는 답변할 수 없습니다.",
    ),
    QAPair(
        question="스타듀밸리에서 빠른 이동(워프)을 하려면 어떤 아이템이나 방법이 필요한가?",
        question_type="out_of_domain",
        relevant_chunk_ids=[],
        reference_answer="제공된 문서로는 답변할 수 없습니다.",
    ),
]


# ──────────────────────────────────────────────
# PART 2 · LLM 자동 생성 함수 (선택 사항)
# ──────────────────────────────────────────────

GEN_SYSTEM_PROMPT = """당신은 RAG 평가용 정답셋(golden set)을 만드는 데이터셋 생성기입니다.
주어진 문서 청크를 읽고, 이 문서로 평가할 수 있는 질문-정답 쌍을 생성하세요.

[규칙]
1. 누수 금지 — 질문에 문서 문장을 그대로 복사하지 마세요. 같은 내용을 묻되 표현을 바꾸세요.
2. 근거 필수 — 답은 반드시 제공된 청크 안에 실제로 존재해야 합니다. 추측·환각 금지.
3. 청크 id 정확히 — relevant_chunk_ids 에는 답의 근거가 되는 청크 id만 정확히 넣으세요.
4. 질문 유형을 의도적으로 섞으세요:
   · factual        한 청크 안에서 답이 나오는 단순 사실 질문
   · multi_hop      여러 청크를 종합/비교해야 답하는 질문 (relevant_chunk_ids 2개 이상)
   · out_of_domain  같은 도메인처럼 보이지만 '제공된 청크'로는 답할 수 없는 질문
                    → relevant_chunk_ids = [],
                      reference_answer = "제공된 문서로는 답변할 수 없습니다."
5. reference_answer 는 군더더기 없이 사실 위주로 간결하게.
6. 답이 청크에 또렷이 없으면 그 질문은 만들지 마세요. 양보다 질."""

GEN_USER_TEMPLATE = """[도메인 힌트]
{domain_hint}

[생성 요청 — 유형별 개수]
- factual: {n_factual}개
- multi_hop: {n_multi_hop}개
- out_of_domain: {n_ood}개

[문서 청크]
{chunks}"""


class GoldenSetSchema(BaseModel):
    items: List[QAPair]


def format_chunks(chunks: List[dict]) -> str:
    """chunks 예: [{"id": "farming_keg", "text": "..."}]"""
    return "\n\n".join(f"[id: {c['id']}]\n{c['text']}" for c in chunks)


def generate_golden_set(
    chunks: List[dict],
    domain_hint: str = "스타듀밸리 게임 위키 문서",
    n_factual: int = 4,
    n_multi_hop: int = 2,
    n_ood: int = 1,
    model_name: str = "gpt-4o-mini",
) -> List[QAPair]:
    """
    청크 배치로 추가 정답셋을 LLM 생성.
    생성 후 반드시 사람이 검수할 것.
    """
    from langchain.chat_models import init_chat_model

    gen_llm = init_chat_model(model_name, temperature=0.7)
    user = GEN_USER_TEMPLATE.format(
        domain_hint=domain_hint,
        n_factual=n_factual,
        n_multi_hop=n_multi_hop,
        n_ood=n_ood,
        chunks=format_chunks(chunks),
    )
    result = gen_llm.with_structured_output(GoldenSetSchema).invoke(
        [("system", GEN_SYSTEM_PROMPT), ("human", user)]
    )
    return result.items


if __name__ == "__main__":
    by_type = {}
    for qa in GOLDEN_SET:
        by_type.setdefault(qa.question_type, []).append(qa)

    print(f"총 {len(GOLDEN_SET)}개 QA 쌍")
    for t, items in by_type.items():
        print(f"  {t}: {len(items)}개")
    print()
    for qa in GOLDEN_SET[:3]:
        print(f"[{qa.question_type}] {qa.question}")
        print(f"  → {qa.reference_answer[:60]}...")
