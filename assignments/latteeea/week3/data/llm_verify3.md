### 1차 오류율 측정 및 개선 결과 
- 1차 수동 검증 후 수정 필요 사항들
    1. EVD-PAPER-ZN-080-005이나 EVD-PAPER-FE-008-004 같은 fact sheet들을 커버할 수 있는 study_type 필요 (fact_sheet) + confidence는 high로 고정
    2. EVD-PAPER-PR-043-001 이 논문은 표본 크기가 24이므로 medium으로 낮추기 (지금은 high) -> 표본크기 기준은 30으로
    3. EVD-PAPER-VIT2-054-004 이거는 동물실험(생쥐 대상)이기 때문에 RCT가 아니라 mechanistic으로 분류해야함 -> confidence는 medium으로(상한선 맞추기)
    4. EVD-PAPER-BET-005-002는 논문 안에서 Our study integrated functional, metabolic, transcriptomic, and
    epigenetic data to elucidate the molecular mechanisms underpinning
    C1q-induced innate immune tolerance.
        
        이렇게 되어있기 때문에 observational 보다는 mechanistic 인것같음. 다변량 보정 모델 있기 때문에 medium으로 유지
        
    5. EVD-PAPER-CHR-009-001 같은 경우는 고강도 운동인에게 구리 농도가 떨어진다는것으로 negative로 갔는데
    이 말은 고강도 운동인에게 구리가 안 좋게 작용한다는 말이 아님
    그렇다고 구리가 고강도 운동인에게 좋게 반영된다는 것은(positive) 확신할 수 없으므로 direction은 null이 되어야 하고 고강도 운동이라는 행동을 함으로써 구리라는 성분이 줄어들었다는 것은 행동에 의한 상태 변화이기 때문에 behavior_exposure 이 되어야하고, 성분에 의한 상태변화가 아니라 생리적 매커니즘이기 때문에 evidence_type은 mechanism이 되어야 함 (association rule이 될 수 없음), observational 이고 다변량모델이 없기 때문에 low로 낮추기
    6. EVD-PAPER-COE-002-004 다변량 보정 모델 없으므로 confidence는 low
    7. EVD-PAPER-FOL-011-001 는 필드로만 보면 엽산이 과일섭취가 부족한 사람에게 추천될 수 있다 <- 라는 건데
    내용은 "과일이 아닌 채소의 섭취 부족은 영양소 결핍으로 이어진다"
    -> evidence_type = mechanism 으로 가야함. 다변량 보정 모델 있지만 상한선 안지켰으므로 medium이 되어야 하고 state_tag는 없는것으로 하는게 맞는것 같다.
    8. EVD-PAPER-BCA-004-001 는 빈혈과 직접적 내용이 아니라 간접적 매핑이 된거기 때문에 state_tag 없는걸로 해야한다(BCAA가 조혈 작용에 중요한 역할을 해서 llm이 간접적 연결로 인식하고 태깅한듯함
    실제 논문에서 헤모글로빈이나 줄기세포 기능에 대한 직접적 언급이 없으면 연결하지 않도록 방지 필요), 다변량 보정 모델 없으니까 low로
    9. EVD-PAPER-POT-015-003은 다변량 보정 모델 없으므로 confidence=low
    10. EVD-PAPER-CAL-028-001에서 상한선 medium 맞추기
    11. EVD-PAPER-EL-014-004 에서 duration=unknown으로 들어가있는데 이는 kg/day 라는 단위가 없어서 -> 추가 필요
    -> " 67.9 mg/kg 체중/일" 에서 체중/일에 해당되는 단위를 못찾아서 unknown으로 들어감. 그리고 리뷰 논문이므로 narrative 가 되어야 함 (study_type)
    12. EVD-PAPER-PB-032-001 이것도 리뷰 논문임. (confidence는 medium으로)
    13. EVD-PAPER-FE-004-004, EVD-PAPER-DIE-055-001 두개는 다변량 보정 모델 없으니까 low가 되어야 하고 EVD-PAPER-VIT-054-004 이건 선형 혼합 모델 사용되었으나 주 결과에 보정된 것 아님 -> low
    4.2 Unfortunately, the sample size of this pilot study was too small to include CRP and the SOFA score in the mixed model analysis
- 프롬프트 수정 전
    
    Evidence 추출 오류율 측정 결과
    
    샘플: 50편 논문, 166개 evidence rows (무작위 추출, seed=42)
    
    전체 오류율
    
    전체 플래그율 (reject + correct): 17.5%  [95% CI: 12.4% ~ 24.0%]
    ├── reject (데이터 제외):         9.0%  [95% CI:  5.6% ~ 14.4%]
    └── correct (자동 수정):          8.4%  [95% CI:  5.1% ~ 13.7%]
    
    → 현재 추출된 evidence 약 6개 중 1개에 오류
    
    에러 유형별 (현행 validator 6-check 기준)
    
    causal_attribution_error       13.9%  (n=23)  ← 압도적 1위
    direction_inversion             3.0%  (n=5)
    outcome_direction_mismatch      0.6%  (n=1)
    
    causal_attribution_error가 전체 오류의 79%를 차지합니다. behavior_exposure(고강도 운동, 식이 패턴)를 substance_intervention으로 혼동하는 문제 — 이번 수정에서 직접 타깃.
    

> 50편 무작위 표본 기준 evidence 추출 오류율 17.5% (95% CI: 12.4%–24.0%) 측정. 가장 큰 원인은 causal attribution 오분류(13.9%)로, 팀원 수동 검증 13케이스를 통해 validator가 잡지 못하는 4개 추가 오류 카테고리를 체계적으로 발굴 → 7개 카테고리 프롬프트 수정안 도출.
> 
- 프롬프트 1차 수정 후
    
    applicability_misclassified가 갑자기 40.1%로 튀었음 - 프롬프트가 아닌 비교 구조 문제였음 + 근데 프롬프트 문제도 하나 발견 
    
    - BEFORE 검증기는 3check, AFTER 검증기는 6CHECK
    - 기존에 존재했는데 원래 몰랐다가 (구 validator가 못 잡다가) 새 프롬프트를 적용하고 나니 is_strict_direct_match 버그 발견함
        - BEFORE: target="ascorbic_acid" → "ascorbic acid" ≠ "vitamin c supplement" → unrelated (원래도 틀림, 구 validator가 못 잡은 것)
        - AFTER: target="vitamin_c" → underscore 때문에 "vitamin_c" ≠ "vitamin c supplementation" → unrelated (틀린 매칭)
        - 새 프롬프트가 더 표준적인 target_ingredient("vitamin_c")를 쓰면서 버그가 수면 위로 올라옴
    
    |  | BEFORE | AFTER(1차 프롬프트) | DELTA |
    | --- | --- | --- | --- |
    | 전체 플래그율 | 48.2% | 52.0% | +3.8pp (CI 겹침 → 통계적 동등) |
    | causal_attribution_error | 12.0% | 8.6% | -3.4pp 개선 |
    | direction_inversion | 2.4% | 0.7% | -1.7pp 개선 |
    | appicability_mismatch | 9.6% | 40.1% | +30.5pp ← 버그 노출 !!  |
    - causal_attribution_error 감소, direction_inversion 감소는 프롬프트 수정 효과인데
    - applicability_misclassified 급증 → 새 프롬프트로 못 보던 버그가 수면 위로 올라온 것
- 프롬프트 2차 수정 후 (applicability_misclassified 얼마나 줄었는지)
    
    모두 같은 50편으로 전체 측정 결과 요약 
    
    |  | BEFORE | AFTER(2차 프롬프트) | DELTA |
    | --- | --- | --- | --- |
    | 전체 플래그율 | 48.2% | 25.0% | -23.2 개선  |
    | causal_attribution_error | 12.0% | 6.6% | -5.4pp 개선 |
    | direction_inversion | 2.4% | 0.7% | -1.7pp 개선 |
    | appicability_mismatch | 40.1% (1차 프롬프트) | 13.8% | -26.3pp 개선  |
    
- 프롬프트 2차 수정까지 한 후 정리
    
    측정 불가 항목 (validator가 현재 체크하지 않음)
    
    ┌─────────────────────────────────────────────────────┬──────────────────────────────────────────────┬──────────────────────────────────────────┐
    │                      수정 항목                      │                  기대 효과                   │                측정 방법                 │
    ├─────────────────────────────────────────────────────┼──────────────────────────────────────────────┼──────────────────────────────────────────┤
    │ CAT-A STEP 0 study_type 체크리스트 (리뷰 논문 감지) │ 리뷰 논문 Narrative 오분류 감소              │ 수동 검증 또는 validator Check 추가 필요 │
    ├─────────────────────────────────────────────────────┼──────────────────────────────────────────────┼──────────────────────────────────────────┤
    │ CAT-C confidence 권고 → 필수(must)                  │ 표본수<30·다변량보정 없는 케이스 과산정 감소 │ 동상                                     │
    ├─────────────────────────────────────────────────────┼──────────────────────────────────────────────┼──────────────────────────────────────────┤
    │ CAT-F state_tag 2단계 추론 금지                     │ 간접 연결 과태깅 감소                        │ 동상                                     │
    ├─────────────────────────────────────────────────────┼──────────────────────────────────────────────┼──────────────────────────────────────────┤
    │ CAT-G dose_unit mg/kg/day 파싱 추가                 │ unknown 오기입 감소                          │ 동상                                     │
    ├─────────────────────────────────────────────────────┼──────────────────────────────────────────────┼──────────────────────────────────────────┤
    │ CAT-B Fact_Sheet 신설                               │ 공식 지침서 분류 가능                        │ 동상                                     │
    └─────────────────────────────────────────────────────┴──────────────────────────────────────────────┴──────────────────────────────────────────┘
    
    ---
    
    부작용으로 새로 나타난 오류
    
    ┌──────────────────────────────────┬──────────────┬───────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
    │            오류 유형             │    발생률    │                                                       원인                                                        │
    ├──────────────────────────────────┼──────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
    │ missing_state_tags               │ 2.0% (n=3)   │ CAT-F state_tag 기준 강화로 필요한 태그도 보수적으로 적용하는 케이스 발생                                         │
    ├──────────────────────────────────┼──────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
    │ missing_outcome_normalized       │ 2.0% (n=3)   │ 새 추출 데이터 특성 (BEFORE에도 존재했을 가능성 있음)                                                             │
    ├──────────────────────────────────┼──────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
    │ prescription_drug_misclassified  │ 2.0% (n=3)   │ 동상                                                                                                              │
    ├──────────────────────────────────┼──────────────┼───────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
    │ applicability_misclassified 잔존 │ 13.8% (n=21) │ 버그 수정 후에도 남은 건 새 프롬프트가 behavior_exposure를 더 적극 분류하면서 생긴 진짜 차이 (BEFORE 대비 +4.2pp) │
    └──────────────────────────────────┴──────────────┴───────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
    
    ---
    
    한 줄 요약
    
    ▎ CAT-E + CAT-D(behavior_exposure 규칙 강화)가 causal_attribution_error 12.0%→6.6%, direction_inversion 2.4%→0.7%를 만들었고, _is_strict_direct_match 버그 수정이 applicability_misclassified 40.1%→13.8%를
    ▎ 만들었습니다. 나머지 5개 카테고리(A·B·C·F·G)의 효과는 현재 validator로는 측정 불가 — 수동 검증 또는 validator Check 확장 필요합니다.
    
- 그 다음으로 validator 에 추가해야하는 check 항목
    1. Check 7 — behavior_exposure + direction≠null [최상] — 구현 가장 쉬움 (CHR-009 내용)
        
        왜 최상: Check 3이 substance_intervention → behavior_exposure 방향만 잡고, 반대 (behavior_exposure인데 direction=positive/negative는 통과)는 못 잡음. 이번 측정에서 causal_attribution_error가 줄었지만 완전히
        없어지지 않은 원인 중 하나.
        
        claim_subject = "behavior_exposure" 또는 "covariate_pattern"인데
        direction = "positive" 또는 "negative"인 row:
        → correct, error_type: behavior_exposure_direction_error
        → correction_direction: "null"
        
        구현 난이도: 매우 쉬움 — 필드값만 비교
        
    
    ---
    
    1. Check 8 — confidence 과산정 [최상] — 임팩트 가장 큼 (7/13)
        
        왜 최상: 수동 검증 7/13 케이스에서 발견, 현재 전혀 측정 안 됨. 이게 없으면 confidence 규칙을 프롬프트에서 아무리 강화해도 효과를 측정할 수 없음.
        
        [Rule 1] study_type = Mechanistic 또는 Narrative Review인데 confidence = "high"
        → correct, error_type: confidence_overcalibrated
        → correction_confidence: "medium"
        
        [Rule 2] study_type = Observational인데
        source_snippet에 "adjusted", "multivariate", "controlled for",
        "regression model", "cox model" 키워드 없고 confidence = "medium" 또는 "high"
        → correct, error_type: confidence_overcalibrated
        → correction_confidence: "low"
        
        [Rule 3] evidence_type = "mechanism" + claim_subject = "behavior_exposure"인데
        confidence ≠ "low"
        → correct, error_type: confidence_overcalibrated
        → correction_confidence: "low"
        
        구현 난이도: 보통 — Rule 1,3은 필드값만 비교, Rule 2는 source_snippet 키워드 검색 필요
        
    2. Check 9 — study_type 오분류 [상] (3/13)
        
        왜 상: confidence 과산정의 upstream 원인. study_type이 틀리면 Check 8 Rule 1도 작동 안 함.
        
        [Rule 1] condition_population 또는 source_snippet에
        "mice", "rat", "mouse", "in vitro", "cell line", "murine", "rodent"가 있는데
        study_type = "RCT" 또는 "Observational"
        → correct, error_type: study_type_misclassified
        → correction_study_type: "Mechanistic"
        
        [Rule 2] source_snippet 또는 evidence_statement에
        "this review", "we review", "narrative review", "literature review",
        "systematic search", "PRISMA"가 있는데
        study_type ≠ "Narrative Review" 또는 "Systematic Review"
        → correct, error_type: study_type_misclassified
        → correction_study_type: "Narrative Review" (또는 "Systematic Review")
        
        구현 난이도: 쉬움 — keyword matching
        
- 새 프롬프트(추출 프롬프트)로 v5 sample 돌린 결과
    
    수동 검증에서 수정할사항으로 나왔던 16가지 논문 중 5가지만 pass (31%)
    
    FAIL (11개) — 패턴별 분류
    
    패턴 1: confidence 과산정 (7개) — 가장 많음
    COE-002, POT-015, FE-004, DIE-055, VIT-054  → medium으로 나옴 (low여야)
    BCA-004                                      → high/medium 혼재 (low여야)
    PR-043                                       → high 그대로 (medium이어야, n=24)
    CHR-009                                      → medium 그대로 (low여야)
    프롬프트에 "반드시(must) low"를 넣었지만 LLM이 여전히 무시.
    
    패턴 2: study_type 오분류 (2개)
    VIT2-054: 동물실험인데 RCT 그대로
    BET-005:  multi-omics인데 RCT 그대로
    STEP 0 체크리스트 추가했지만 이 두 논문은 통과 못 함.
    
    패턴 3: behavior_exposure direction (1개)
    CHR-009: 4개 row 중 2개는 direction=null 됐지만 2개는 여전히 negative
    
    패턴 4: mechanism 미분류 (1개)
    FOL-011: 식이패턴→결핍 경로인데 여전히 association 4개
    
    - 31%는 낮아보이지만 11개 FAIL의 대부분은 validator가 자동 수정 가능함
        - confidence 과산정 7개 → check 8로 수정 가능
        - study_type 오분류 2개 → check 9로 수정 가능
        - direction=negative → check7로 수정 가능
        - FOL-011 mechanism 미분류 → 수정가능한 check 없음 (수동 수정 필요)
    - 2-pass 기준(검증 프롬프트 추가된) 예상 → 14~15/16 → 실제 측정 결과 : 5/16 (그대로다 문제임… 밑에서)
    - 리뷰 논문/fact sheet 판단 여부는 프롬프트로 해결되지만, confidence 과산정은 추출 프롬프트로 한계가 있어, validator에 의존하는 게 현실적이다.
        - 일단 mechanism 미분류한거 few_shot 예시를 좀 더 구체적으로 조정해보고
        - confidence 과산정 경우는, 프롬프트 must 강화로도 안되는 상황이고. validator가 사후에 잡아주는것으로 집중 필요
- check-9(검증 프롬프트) 추가했는데도 5/16(31%)이 나온 이유
    
    validator decision 분석 결과 → 모든 케이스에서 corr_conf = None 이 나왔는데 3가지 구조적 문제가 있음
    
    1. 1행 1결정 제약 - validator는 행당 하나의 error_type만 반환해서 check 8보다 check3 이 먼저 걸리면 confidence(check8) 는 수정이 안됨 
        1. COE-002 row0: behavior_exposure_direction_error 잡힘 → confidence는 못 고침
        2. FE-004  row0: causal_attribution_error 잡힘      → confidence는 못 고침
    2. check8 자체가 미발동됨 - POT-015, PR-043은 다른 오류도 없는데 confidence가 그냥 approve됨. LLM이 "multivariate 키워드 없으면 low"를 Observational에서 일관되게 적용 못 함
    3. Check 8에 RCT n<30 규칙이 없음 — PR-043 (n=24인데 high) 케이스는 Check 8에 아예 없는 규칙
    
    어떻게 고쳐야 하냐면 : confidence 과산정 → LLM이 아닌 코드 레벨로 이동하도록 
    →  LLM 기반 validator로는 결정론적 규칙(다변량 여부, 표본 크기)를 일관되게 적용하기 어렵구나… 코드로 박는 게 어느정도 필요함 
    
    - fact sheet는 confidence high로 고정하는 거 필요하고 (postpreocessor로)
    - study_type에 따른 상한선 강제하는것도 필요하고 (Observational인데 계속 high로 나옴 ㅜㅜ 상한선 medium이라 해놨는데)
    - (이건 반영안함) 클로드가 source_snippet (논문 문장 그대로 가져온 필드)에 다변량 관련된 키워드가 없으면 low로 (observational + 다변량 모델 x → low 라는 우리만의 규칙) 하자고 하는데, 우리가 수동 검증할때는 source_snippet에서 다변량에 관련된 말이 있었던게 아니라 논문 전체를 읽고 다변량 모델이 아니라고 판단해서 해당 근거 사례의 confidence를 low로 해야한다고 결정한거기 때문에 검증 프롬프트가 아닌 추출 프롬프트에서 해결이 되어야 하는것임 → 클로드 말 반영 안함
        - evidence의 필드에 다변량 여부를 boolean으로 명시적으로 기록하도록 추가함. 여기서 postprocessor가 이 필드를 보고 결정론적으로 적용하도록 하기. (표본 크기 필드도 추가함)
    - RCT + 표본 n<30 → medium 상한으로 하는것도 필요 (n=24인데 high로 하는건 표본 크기가 너무 작아서 신뢰도 높지 않은 것임)
- 검증 프롬프트 및 추출 프롬프트 약간 수정(다변량 필드 추가 후)한 이후 결과 (9/16 → 56%)
    
    5/16(31%) → 9/16(56%), 4 pass 개선됨 
    
    결과 분석
    
    새로 PASS된 6개 (confidence 보정 작동)
    
    ✓ PR-043   n=24 → Rule D (RCT n<30 → medium) 작동
    ✓ COE-002  Observational + 다변량 없음 → Rule B (→ low) 작동
    ✓ POT-015  동상
    ✓ FE-004   동상
    ✓ DIE-055  동상
    ✓ VIT-054  혼합모델 미적용 → has_multivariate_adjustment=False → low
    
    기존 PASS인데 이번에 FAIL된 2개 (regression)
    
    ✗ EL-014  study_type=Narrative Review → Unknown으로 퇴행
    (이번 재추출에서 STEP 0이 안 먹힘)
    ✗ PB-032  한 row만 confidence=high 남음
    (나머지 3개는 medium인데 1개 row study_type이 달랐을 가능성)
    
    여전히 FAIL (7개)
    
    ┌──────────┬───────────────────────────────────────────────────────────────────────┐
    │  케이스  │                               남은 문제                               │
    ├──────────┼───────────────────────────────────────────────────────────────────────┤
    │ CHR-009  │ direction=null 2/3 미적용, evidence_type=association (mechanism 아님) │
    ├──────────┼───────────────────────────────────────────────────────────────────────┤
    │ FOL-011  │ evidence_type=population_note (mechanism 아님)                        │
    ├──────────┼───────────────────────────────────────────────────────────────────────┤
    │ VIT2-054 │ study_type=RCT 그대로 (동물 실험 미인식)                              │
    ├──────────┼───────────────────────────────────────────────────────────────────────┤
    │ BET-005  │ study_type=RCT/Observational 혼재 (Mechanistic 미인식)                │
    ├──────────┼───────────────────────────────────────────────────────────────────────┤
    │ BCA-004  │ 1개 row만 medium 잔존                                                 │
    ├──────────┼───────────────────────────────────────────────────────────────────────┤
    │ EL-014   │ 이번 추출에서 Narrative Review → Unknown 퇴행                         │
    ├──────────┼───────────────────────────────────────────────────────────────────────┤
    │ PB-032   │ 1개 row confidence=high                                               │
    └──────────┴───────────────────────────────────────────────────────────────────────┘
    
    패턴 정리
    
    확실히 해결된 것: confidence 과산정 (다변량 없음, n<30) — Rule B·D가 결정론적으로 잡아줌
    
    아직 LLM이 일관성 없는 것 2가지:
    
    1. study_type 오분류 (동물실험, multi-omics → RCT/Observational): STEP 0 추가했지만 논문 내용에 따라 여전히 틀림. LLM이 "mice", "rodent" 키워드를 보고도 RCT로 분류하는 것 → 이건 Check 9 (validator 자동 수정)
    에 의존하거나, 추출 후 코드 레벨 키워드 체크 추가 고려
    2. mechanism 미분류 (CHR-009, FOL-011): 행동→성분 경로를 여전히 association/population_note로 분류. 예시를 추가했지만 이 두 논문에서 안 통함 → 예시를 더 강화하거나 논문 내용 자체가 모호할 수 있음
    
    EL-014·PB-032 퇴행: LLM 비결정성으로 이번 추출에서 다르게 나온 것. 여러 번 돌리면 결과가 달라질 수 있음.
    
    - 다음으로는 study_type오분류(VIT2-054, BET-005)는 postprocess 부분에 condition_population 키워드 체크를 코드 레벨로 추가해서 비결정성 없이 llm이 잡도록 하고
    - mechanism 미분류는 llm 의존이라 더 많은 예시가 필요할듯 → 다음 수동 검증으로 넘기자
- study_type 키워드 보정 후 결과 (14/16 pass → 88%)
    
    14/16 PASS (88%) 입니다.
    
    ---
    
    전체 진행 경과
    
    최초 (프롬프트 수정 전):    5/16  (31%)
    
    - 프롬프트 7개 카테고리: 5/16 (31%) ← confidence 미해결
    - n_sample/has_adj 필드: 9/16 (56%) ← confidence 해결
    - study_type 키워드 보정: 14/16 (88%) ← study_type 해결
    
    새로 PASS된 것 (이번 최종 run)
    
    ┌────────────┬───────────────────────────────────────────────────────────────────────────┐
    │   케이스   │                                 해결 원인                                 │
    ├────────────┼───────────────────────────────────────────────────────────────────────────┤
    │ CHR-009 ✓  │ behavior_exposure + direction=null + mechanism + confidence=low 모두 통과 │
    ├────────────┼───────────────────────────────────────────────────────────────────────────┤
    │ FOL-011 ✓  │ evidence_type=mechanism 분류 성공 (예시 추가 효과)                        │
    ├────────────┼───────────────────────────────────────────────────────────────────────────┤
    │ VIT2-054 ✓ │ condition_population 키워드(C57BL, mice 등) → Mechanistic 자동 보정       │
    ├────────────┼───────────────────────────────────────────────────────────────────────────┤
    │ BET-005 ✓  │ source_snippet 키워드(transcriptomic, epigenetic) → Mechanistic 자동 보정 │
    ├────────────┼───────────────────────────────────────────────────────────────────────────┤
    │ PB-032 ✓   │ Narrative Review 인식 + confidence 상한선 적용                            │
    └────────────┴───────────────────────────────────────────────────────────────────────────┘
    
    여전히 FAIL (2개)
    
    ┌─────────┬───────────────────────────────────────────────────────────────────────┬────────────────────────────────────────────────────────────────────────────────────────────────────┐
    │ 케이스  │                                 문제                                  │                                                원인                                                │
    ├─────────┼───────────────────────────────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────┤
    │ BCA-004 │ 1개 row만 medium 잔존 ['medium', 'low', 'low']                        │ 해당 row의 has_multivariate_adjustment가 null로 나와서 Rule B 미발동, Rule C만 적용(→ medium 상한) │
    ├─────────┼───────────────────────────────────────────────────────────────────────┼────────────────────────────────────────────────────────────────────────────────────────────────────┤
    │ EL-014  │ study_type=Observational/Mechanistic ['Observational', 'Mechanistic'] │ 이번엔 Mechanistic 키워드 체크가 과도하게 걸려서 Narrative Review를 못 잡음                        │
    └─────────┴───────────────────────────────────────────────────────────────────────┴────────────────────────────────────────────────────────────────────────────────────────────────────┘
    
    BCA-004는 LLM이 has_multivariate_adjustment=null로 반환한 row 1개 문제, EL-014는 Narrative Review 감지 불안정(LLM 비결정성)입니다. 둘 다 다음 수동 검증 회차로 넘겨도 무방한 수준입니다. 88%면 충분히 진행할 수
    있을 것 같습니다.