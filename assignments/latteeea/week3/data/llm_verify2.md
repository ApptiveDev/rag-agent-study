### llm 추출 프롬프트 수동 검증 테스트 

1. EVD-PAPER-ZN-080-005이나 EVD-PAPER-FE-008-004 같은 fact sheet들을 커버할 수 있는 study_type 필요 (fact_sheet) + confidence는 high로 고정
2. EVD-PAPER-PR-043-001 이 논문은 표본 크기가 24이므로 medium으로 낮추기 (지금은 high) -> 표본크기 기준은 30으로
3. EVD-PAPER-VIT2-054-004 이거는 동물실험(생쥐 대상)이기 때문에 RCT가 아니라 mechanistic으로 분류해야함 -> confidence는 medium으로(상한선 맞추기)
4. EVD-PAPER-BET-005-002는 논문 안에서 Our study integrated functional, metabolic, transcriptomic, and
epigenetic data to elucidate the molecular mechanisms underpinning
C1q-induced innate immune tolerance.

이렇게 되어있기 때문에 observational 보다는 mechanistic 인것같음. 다변량 보정 모델 있기 때문에 medium으로 유지

1. EVD-PAPER-CHR-009-001 같은 경우는 고강도 운동인에게 구리 농도가 떨어진다는것으로 negative로 갔는데
이 말은 고강도 운동인에게 구리가 안 좋게 작용한다는 말이 아님
그렇다고 구리가 고강도 운동인에게 좋게 반영된다는 것은(positive) 확신할 수 없으므로 direction은 null이 되어야 하고 고강도 운동이라는 행동을 함으로써 구리라는 성분이 줄어들었다는 것은 행동에 의한 상태 변화이기 때문에 behavior_exposure 이 되어야하고, 성분에 의한 상태변화가 아니라 생리적 매커니즘이기 때문에 evidence_type은 mechanism이 되어야 함 (association rule이 될 수 없음), observational 이고 다변량모델이 없기 때문에 low로 낮추기
2. EVD-PAPER-COE-002-004 다변량 보정 모델 없으므로 confidence는 low
3. EVD-PAPER-FOL-011-001 는 필드로만 보면 엽산이 과일섭취가 부족한 사람에게 추천될 수 있다 <- 라는 건데
내용은 "과일이 아닌 채소의 섭취 부족은 영양소 결핍으로 이어진다"
-> evidence_type = mechanism 으로 가야함. 다변량 보정 모델 있지만 상한선 안지켰으므로 medium이 되어야 하고 state_tag는 없는것으로 하는게 맞는것 같다.
4. EVD-PAPER-BCA-004-001 는 빈혈과 직접적 내용이 아니라 간접적 매핑이 된거기 때문에 state_tag 없는걸로 해야한다(BCAA가 조혈 작용에 중요한 역할을 해서 llm이 간접적 연결로 인식하고 태깅한듯함
실제 논문에서 헤모글로빈이나 줄기세포 기능에 대한 직접적 언급이 없으면 연결하지 않도록 방지 필요), 다변량 보정 모델 없으니까 low로
5. EVD-PAPER-POT-015-003은 다변량 보정 모델 없으므로 confidence=low
6. EVD-PAPER-CAL-028-001에서 상한선 medium 맞추기
7. EVD-PAPER-EL-014-004 에서 duration=unknown으로 들어가있는데 이는 kg/day 라는 단위가 없어서 -> 추가 필요
-> " 67.9 mg/kg 체중/일" 에서 체중/일에 해당되는 단위를 못찾아서 unknown으로 들어감. 그리고 리뷰 논문이므로 narrative 가 되어야 함 (study_type)
8. EVD-PAPER-PB-032-001 이것도 리뷰 논문임. (confidence는 medium으로)
9. EVD-PAPER-FE-004-004, EVD-PAPER-DIE-055-001 두개는 다변량 보정 모델 없으니까 low가 되어야 하고 EVD-PAPER-VIT-054-004 이건 선형 혼합 모델 사용되었으나 주 결과에 보정된 것 아님 -> low
4.2 Unfortunately, the sample size of this pilot study was too small to include CRP and the SOFA score in the mixed model analysis

[수동 검증 필요(llm추출_QA시나리오) - llm 추출 수동 검증표.csv](attachment:8b33e5b9-0efe-47c0-8dfc-b7d5e630145d:수동_검증_필요(llm추출_QA시나리오)_-_llm_추출_수동_검증표.csv)

### 프롬프트 수정 리스트업

현재 코드 상태와 대조한 결과입니다.

A. STEP 0 — study_type 판별 체크리스트 신설 [코드에 없음, 완전 신규]

현재: study_type 허용값 목록만 있고 판별 기준 없음 (line 280-288)

추가 위치: study_type 허용값 목록 바로 위

STEP 0 — study_type 판별 시 반드시 아래 순서를 먼저 확인하십시오:

① 논문 텍스트에서 제목 바로 앞/위에 "Review", "Review Article",
"Narrative Review", "Mini-Review"가 단독으로 있으면
→ Abstract 내용에 관계없이 study_type = Narrative Review로 즉시 분류하십시오.
(저자가 자신의 이전 실험 데이터를 인용하더라도, 저널 부여 article type이 우선합니다.)

② Methods 섹션이 존재하지 않으면 → Narrative Review 강력 의심.
Abstract에 "this work reviews", "we review", "we summarize", "this paper examines"
가 있으면 Narrative Review로 분류하십시오.

③ 실험 대상이 동물(mice, rat, rodent, in vitro, cell line)이면
→ "RCT"라는 단어가 있더라도 study_type = Mechanistic

④ 주목적이 분자 경로 규명이면 → Mechanistic
키워드: transcriptomic, epigenetic, proteomic, signaling pathway,
molecular mechanism, multi-omics, innate immune tolerance

⑤ ①~④ 해당 없으면 RCT / Observational / 기타로 판단하십시오.

---

B. study_type 허용값에 Fact_Sheet 신설 [코드에 없음]

현재: 8개 값 (line 281-288), Fact_Sheet 없음

추가:

- Fact_Sheet ← 국가 기관, WHO, 보건부 공식 영양 섭취 기준표·지침서
→ confidence는 반드시 high로 고정

---

C. confidence 규칙 강화 [기존 있으나 "권고" → "필수"로 격상]

현재 line 116: "낮출 수 있음", "권고" 표현 → LLM이 무시함

수정 1: line 128 "표본 수 < 30이면 medium 이하 권고"
→ "표본 수 < 30이면 high 불가, 반드시(must) medium 이하"

수정 2: line 125 "다변량 보정 모델이 명시된 경우에만 medium 허용"
→ "다변량 보정(adjusted model)이 논문에 명시되지 않으면
Observational은 반드시 low. 혼합 모델(linear mixed model)이 있어도
주 결과에 실제 적용되지 않았으면 low."

추가: "evidence_type=mechanism이고 claim_subject=behavior_exposure이면
confidence는 반드시 low (보충 효과 근거 아님)"

---

D. evidence_type=mechanism 판정 기준 신설 [정의가 현재 전혀 없음]

현재 line 431-439: 허용값 목록만 있음

추가 위치: evidence_type 허용값 위

[mechanism 판정 기준]
다음 경우 evidence_type = mechanism을 사용하십시오:

- 성분이 개입(독립변수)이 아닌 측정 결과(종속변수·바이오마커) 위치에 있을 때
- 행동·식이 패턴 → 성분 수준 변화를 설명하는 생리 경로일 때
(성분을 투여한 것이 아니라, 행동 결과로 성분 농도가 변한 것)
- 성분 투여 없이 결핍/유병률만 관찰한 역학 연구
(이것은 association이 아닙니다)
- 분자 경로 규명이 목적인 연구 (multi-omics, transcriptomic, epigenetic)

association과의 구분:

- association: 성분 투여·섭취 → 결과 변화가 중심
- mechanism: 왜 그런지 경로 설명, 또는 성분이 결과의 측정값

---

E. behavior_exposure 규칙 강화 [기존 있으나 direction=null 명시 없음]

현재 line 82-99: claim_subject 정의만 있고 direction=null 강제 없음

수정 1: "claim_subject=behavior_exposure 또는 covariate_pattern이면
direction은 반드시(must) null"
(통계 수치가 있어도 성분 보충 효과가 아니므로 direction 기록 금지)

수정 2: 정의 확장 — 현재 "운동·훈련·신체 부하"만 예시
→ "식이 행동(특정 식품군 섭취 부족, 식이 패턴 불균형)도 behavior_exposure"

수정 3: line 90 "target_effect_relation은 보통(usually) unrelated_to_target"
→ "반드시(must) unrelated_to_target"

추가: few-shot 예시 2개

- "고강도 운동 그룹에서 구리 농도 유의하게 감소"
→ claim_subject=behavior_exposure, direction=null,
evidence_type=mechanism, target_effect_relation=unrelated_to_target, confidence=low
- "채소 섭취 부족 인구에서 엽산 결핍 비율 높음"
→ claim_subject=behavior_exposure, direction=null, evidence_type=mechanism

---

F. state_tag 과태깅 방지 강화 [기존 규칙 보완]

현재 line 369-413: 간접 매핑 허용 기준이 있으나 2단계 추론 금지 명시 없음

추가: [매핑 금지 및 주의 사항] 항목에 추가

- 2단계 이상 추론으로 state_tag 부여 금지
(예: "BCAA → 조혈 기능 → 빈혈" 처럼 논문에 헤모글로빈·빈혈이
직접 언급되지 않으면 anemia_risk 태깅 금지)
- evidence_type=mechanism이면 state_tag 부여에 매우 신중할 것
(성분 보충 효과가 아닌 생리 관찰이므로 추천 엔진 연결 부적절)

---

G. dose_unit 허용값 확장 [현재 mg/kg만 있음]

현재 line 454-458: mg/kg, g/kg, IU/kg만 있고 /day 복합 단위 없음

추가:

- mg/kg/day ← "mg/kg 체중/일", "mg/kg BW/d", "mg/kg body weight/day" 모두 이걸로 파싱
- g/kg/day
- mcg/kg/day

그리고 _normalize_analysis_dict 함수의 allowed_dose_units set (line 1063-1077)에도 동일하게 추가 필요.

### 가치 평가

포트폴리오 가치 평가

결론부터: 헬스테크/AI 프로덕트 포지션에서는 상위 10% 수준의 포트폴리오 소재입니다. 단, 어떻게 포장하느냐에 따라 편차가 큽니다.

강점 — 진짜 차별점

1. End-to-End LLM 파이프라인 구축 경험
논문 PDF → LLM 추출 → evidence DB → atomic facts → 추천 규칙까지 직접 설계하고 구현한 사람은 드뭅니다. "LLM 써봤다" 수준이 아니라 LLM 출력의 신뢰도를 구조적으로 제어하는 수준.
2. 체계적 품질 관리 (QA 프레임워크)
- 2-pass 임상 검증 레이어 (approve/correct/reject)
- 팀원 수동 검증 → 13개 케이스 → 7개 카테고리 오류 분류
- confidence 기준, study_type 체계, state_tag 정밀도를 직접 설계

이게 포트폴리오에서 가장 강한 부분입니다. "LLM이 틀리는 걸 어떻게 잡아내고 개선했는가"를 데이터로 보여줄 수 있음.

1. 도메인 × 기술 동시 보유
영양학적 판단(mechanism vs association, behavior_exposure 구분)을 직접 해서 프롬프트 설계에 반영했다는 점. 대부분의 ML 엔지니어는 이 판단을 도메인 전문가에게 위임합니다.
2. Medallion 아키텍처
Bronze → Silver → Gold 레이어 설계는 데이터 엔지니어링 관점에서 명확한 설계 능력을 보여줌.

---

약점 — 솔직하게

1. 임팩트 수치가 없음
논문 몇 편 처리했는지, 성분 몇 개 커버하는지, 실제 사용자가 몇 명인지 없으면 채용 담당자가 규모를 가늠하기 어렵습니다.
2. 아직 제품 수준이 아님
QA 시나리오 116개, 검증 13개 케이스 — 이건 "개발 중인 시스템"의 규모입니다. 실제 배포·운영 경험이 없으면 ML 엔지니어링 포지션에서 가산점이 크지 않음.
3. 기술 스택 폭이 좁음
인프라(MLOps, 배포), 모니터링, A/B 테스트 경험이 드러나지 않습니다.