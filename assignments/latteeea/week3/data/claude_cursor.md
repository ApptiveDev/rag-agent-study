이 프로젝트의 전체 구조를 분석해줘. 특히 논문 데이터를 Atomic Facts로 추출해서 최종 Rule을 생성하는 'split-mapping-reduce' 파이프라인의 핵심 파일들과 로직이 어떻게 연결되어 있는지 요약해줘. 해당 파이프라인이 아닌 다른 구조라면 뭐라고 명명할 수 있는지도 알려주고.

- cursor
    
    프로젝트를 보면 큰 흐름이 **`수집/추출 → 정규화/저장 → 룰 생성 → 추천/검증 → 외부 동기화`**로 나뉩니다.
    
    질문하신 “논문 데이터 → Atomic Facts → 최종 Rule” 경로는 실제로 존재하고, 핵심은 `pipeline/generate_rules.py`를 중심으로 연결되어 있습니다.
    
    ## **전체 구조 (상위 관점)**
    
    - **논문 처리(ingest)**
        - `pipeline/process_drive_sample_batch.py`: 구글 드라이브에서 PDF 샘플 배치 처리
        - `pipeline/process_one_paper.py`: 단일 PDF 처리 오케스트레이션
        - `services/pdf_service.py`: PDF 텍스트 추출
        - `services/llm_service.py`: 논문 텍스트를 구조화된 `evidence_rows`로 변환
        - `services/csv_service.py`: `paper_registry.csv`, `evidence_db.csv` 저장
    - **룰 엔진(rule engine)**
        - `pipeline/generate_rules.py`: 전체 룰 생성 파이프라인 엔트리
        - `pipeline/rule_engine/*`: 점수화, 세그먼트화, 충돌감지, atomic fact 생성, 정책 문장 생성
        - 산출: `evidence_with_scores.csv`, `conflicts_report.csv`, `atomic_facts.csv`, `final_guidelines.csv`, 그리고 유형별 룰 CSV들
    - **추천/QA**
        - `services/recommendation_service.py`, `pipeline/recommend.py`: state tag 기반 기본 추천
        - `services/recommendation_mvp.py`, `pipeline/recommend_mvp.py`: 설문 기반 니즈 벡터 + 안전/상호작용 정책 반영
        - `pipeline/run_qa_scenarios.py`: QA 시나리오 일괄 실행
    - **외부 연동**
        - `pipeline/sync_rules_to_notion.py`, `services/notion_rules_service.py`: 룰 CSV를 노션으로 업서트
        - `services/notion_service.py`: 논문/근거 페이지 저장
    
    ---
    
    ## **split-mapping-reduce 파이프라인 연결 (핵심)**
    
    질문하신 흐름을 파일 기준으로 연결하면:
    
    1. **Split (논문을 근거 단위로 분해)**
        - `process_one_paper.py`가 `llm_service.analyze_paper_with_llm()` 호출
        - `llm_service.py`에서 논문 1편을 최대 6개 `evidence_rows`로 분해/정제
        - 결과를 `csv_service.append_evidence_rows()`로 `evidence_db.csv`에 적재
    2. **Mapping/Normalization (근거를 분석 가능한 축으로 매핑)**
        - `generate_rules.py`에서 순차 실행:
            - `evidence_scoring.enrich_evidence_with_scores()`→ `study_type × confidence` 기반 `evidence_score`
            - `population_segment.enrich_evidence_with_population_segments()`→ `condition_population` 텍스트를 세그먼트 태그로 매핑
            - `dosage_normalize.enrich_evidence_with_dosage_normalization()`→ 투여경로(IV/Oral) 및 용량 단위 정규화
        - 그리고 `conflicts.identify_conflicts()`로 동일 축 내 상충 근거 탐지
    3. **Reduce (집계/합성)**
        - `atomic_facts.generate_atomic_facts()`에서
            - 그룹 키: `rule_ingredient + outcome_normalized + population_segment + dose_route + claim_subject`
            - 집계값: 근거 수, 점수 합, 방향별 점수, 지배 방향
        - 이 단계가 사실상 질문하신 “Atomic Facts 생성”의 핵심 reduce
    4. **Final Rule/Guideline 생성**
        - `policy_language.build_final_guidelines(atomic_facts, conflicts)`에서
            - conflict verdict 조인
            - recommendation tier 계산
            - 최종 한국어 policy statement 생성
        - 별도로 `generate_rules.py` 내 `generate_association_rules / generate_dose_rules / generate_safety_rules / generate_interaction_rules`
            - 실서비스용 구조화 룰 CSV 생성
    
    ---
    
    ## **이걸 꼭 split-mapping-reduce라고 부를 수 있나?**
    
    가능은 하지만, 코드 구조상 더 정확한 명명은 아래가 맞습니다.
    
    - **Evidence-to-Policy Aggregation Pipeline** (가장 정확)
    - **Extract-Normalize-Aggregate-Compose (ENAC) Pipeline**
    - **Rule Synthesis Pipeline from Evidence Graph**
    - 한국어로는 **“근거 집계 기반 규칙 합성 파이프라인”**
    
    이유:
    
    - 단순 split-map-reduce보다, 실제로는
        - 상충 탐지(conflict mediation),
        - 신뢰도 가중치(scoring),
        - 정책 문장 합성(policy language generation) 이 포함된 **다단계 합성 파이프라인**이기 때문입니다.
    
    원하시면 다음 답변에서 이 구조를 **한 장짜리 아키텍처 다이어그램 형태**(입력/출력 CSV와 함수 호출 순서 포함)로 정리해드릴게요.
    
- claude code
    
    ```markdown
      1. 프로젝트 전체 구조
    
      health_algorithm/
      ├── main.py                              (빈 엔트리 — 실제 진입점은 pipeline/*)
      ├── config.py, create_notion_schema.py
      ├── models/evidence_models.py            (Pydantic: EvidenceRow / PaperAnalysisResult)
      ├── services/                            (외부 시스템 + 비즈니스 로직)
      │   ├── drive_service.py                 (Google Drive 목록·다운로드)
      │   ├── pdf_service.py                   (PDF → 텍스트)
      │   ├── llm_service.py                   (OpenAI 호출 + 프롬프트)
      │   ├── normalization_service.py
      │   ├── csv_service.py                   (paper_registry / evidence_db I/O)
      │   ├── notion_service.py, notion_rules_service.py
      │   ├── recommendation_service.py / recommendation_mvp.py
      │   ├── survey_needs.py, policy_config.py
      ├── pipeline/                            (배치 오케스트레이션)
      │   ├── process_drive_sample_batch.py    (성분 폴더 루프)
      │   ├── process_one_paper.py             (1논문 → Evidence rows 저장)
      │   ├── generate_rules.py                (⭐ Rule 생성 엔트리)
      │   ├── recommend.py / recommend_mvp.py
      │   ├── run_qa_scenarios.py, summary_report.py, sync_rules_to_notion.py
      │   └── rule_engine/                     (순수 함수 변환 모듈)
      │       ├── common.py                    (claim_subject, rule_ingredient 추론)
      │       ├── evidence_scoring.py          (study_type × confidence → evidence_score)
      │       ├── population_segment.py, dosage_normalize.py
      │       ├── conflicts.py                 (동일 성분·결과 positive/negative 충돌)
      │       ├── atomic_facts.py              (⭐ 중간 레이어: 그룹 집계)
      │       └── policy_language.py           (Atomic Fact → 한국어 가이드라인)
      └── data/
          ├── paper_registry.csv, evidence_db.csv         (1차 산출)
          ├── evidence_with_scores.csv, conflicts_report.csv   (파생)
          ├── atomic_facts.csv                             (중간 레이어)
          ├── final_guidelines.csv                         (정책 문장)
          └── association_rules.csv, dose_rules.csv, safety_rules.csv, interaction_rules.csv
    
      2. 파이프라인 연결 흐름 (논문 → Rule)
    
      [Drive PDF]
         │  process_drive_sample_batch.py  (성분별 루프, N개 샘플링)
         ▼
      process_one_paper.py
         │  pdf_service.extract_full_text
         │  llm_service.analyze_paper_with_llm   → PaperAnalysisResult (evidence_rows: List[EvidenceRow])
         │  csv_service.append_evidence_rows     → evidence_db.csv
         │  notion_service.save_analysis_to_notion
         ▼
      [evidence_db.csv]   ← 행 단위 원자 근거 (논문 × 클레임)
         │
         │  generate_rules.main()                (pipeline/generate_rules.py)
         │
         ├─ enrich_evidence_with_scores         (rule_engine/evidence_scoring.py)
         │     study_type·confidence → evidence_score
         ├─ enrich_evidence_with_population_segments
         ├─ enrich_evidence_with_dosage_normalization
         │     → evidence_with_scores.csv
         │
         ├─ identify_conflicts                   (rule_engine/conflicts.py)
         │     (rule_ingredient, outcome_normalized, claim_subject) 그룹의
         │     positive vs negative 가중합 비교 → conflicts_report.csv
         │
         ├─ generate_atomic_facts                (rule_engine/atomic_facts.py)  ⭐ 중간 레이어
         │     그룹키: (rule_ingredient, outcome_normalized, population_segment,
         │              dose_route, claim_subject)
         │     집계: n_evidence, score_sum, 방향별 점수, dominant_direction
         │     → atomic_facts.csv
         │
         ├─ build_final_guidelines               (rule_engine/policy_language.py)
         │     atomic_facts ⋈ conflicts → recommendation_tier + 한국어 policy_statement
         │     → final_guidelines.csv
         │
         └─ generate_{association|dose|safety|interaction}_rules  (generate_rules.py)
              evidence_with_scores 에서 각 evidence_type별 재그룹 → 4종 rules CSV
    
      [final_guidelines.csv + *_rules.csv]
         │  recommendation_service / recommend.py
         ▼
      state_tags 쿼리 → 추천 JSON
    
      핵심 중간 레이어 도입 이유 (commit c13510f): Evidence(서술형 LLM 추출) ↔ Rule(의사결정용 집계) 사이 간극이 커서 atomic_facts 레이어를 추가, 토큰화·집계·방향 결정을 여기로 모음.
    
      3. "Split–Map–Reduce"로 부를 수 있는가
    
      형태적으로는 MapReduce와 부분적으로 일치합니다 — (a) 논문을 Evidence 행으로 쪼개기(Split/Flat-Map by LLM), (b) 각 행에 점수·세그먼트·claim_subject enrichment(Map), (c) 그룹바이 집계(Reduce) 구조를 갖습니다.
      다만 atomic_facts → final_guidelines는 조인 + 자연어 템플릿 합성이라 순수 Reduce는 아닙니다.
    
      더 정확한 명명 후보
      - Evidence Synthesis Pipeline (체계적 고찰 용어로 가장 자연스러움)
      - Medallion / Bronze→Silver→Gold 아키텍처 — paper_registry · evidence_db(Bronze) → evidence_with_scores · atomic_facts(Silver) → final_guidelines · *_rules(Gold)
      - Extract → Normalize → Aggregate → Publish (ENAP) — LLM 기반 논문 추출 파이프라인의 일반 패턴
      - Claim Distillation Pipeline — 개별 클레임(Evidence)을 신뢰도 가중으로 증류해 Rule/가이드라인으로 승격시키는 관점 강조
    
      현재 코드베이스가 가장 가까운 건 "LLM-Extracted Evidence → Atomic Fact Aggregation → Policy/Rule Synthesis" 형태의 단계적 증거 증류 파이프라인이며, 구현 실체는 pandas 기반 groupby 파이프라인이라 엄밀한 분산
      MapReduce라기보단 ELT 스타일 Medallion 아키텍처로 부르는 편이 가장 맞습니다.
    ```
    
- 차이
    
    커서는 해당 파이프라인을 근거 집계 기반 규칙 합성 파이프라인이라고 했고, 클로드는 Medallion 아키텍처 (bronze → silver → gole) : 데이터 엔지니어링 용어를 사용함 (지능이 다르다…) → 철학이 담긴다. 데이터의 증류를 아키텍처 관점에서 봄 + claim distillation (증류 파이프라인 : 파편화된 주장을 순도 높은 규칙으로 도출)
    

현재 pipeline/rule_engine/atomic_facts.py와 generate_rules.py에서 가중치(Scoring)를 부여하고 근거 간의 충돌을 해결하는 로직을 집중적으로 봐줘. 지금 방식에서 논리적으로 보완이 필요하거나, 영양소 조합 레시피를 산출할 때 정확도를 떨어뜨릴 만한 위험 요소가 있다면 우선순위 순으로 찾아줘. 최대 10가지, 10개를 다 채울 필요는 없음.

- cursor
    
    우선순위 높은 순으로, **정확도/레시피 품질 저하 가능성**만 추렸습니다.
    
    - **[높음] 충돌 판정이 레시피 산출 경로에 반영되지 않음**
        - `generate_rules.py`에서 충돌 리포트를 만들지만, 추천 엔진은 `association/dose/safety` CSV만 사용해 충돌 정보를 직접 소비하지 않습니다. 결과적으로 상충 근거가 있는 성분도 조합 추천에 그대로 들어갈 수 있습니다.
    
    generate_rules.pyLines 872-893
    
    df_scored = enrich_evidence_with_scores(df)
    
    ...
    
    conflicts_df = identify_conflicts(df_scored)
    
    ...
    
    association_df = generate_association_rules(df_scored)
    
    dose_df = generate_dose_rules(df_scored)
    
    safety_df = generate_safety_rules(df_scored)
    
    interaction_df = generate_interaction_rules(df_scored)
    
    - **[높음] `atomic_facts` 집계에 paper 단위 cap이 없어 단일 논문 과대표 가능**
        - `association_rules`는 논문별 기여도 cap(`_capped_signed_score_by_paper`)을 쓰는데, `atomic_facts`/`conflicts`는 단순 합산이라 같은 논문 다건이 방향을 밀어버릴 수 있습니다.
    
    generate_rules.pyLines 108-127
    
    def _capped_signed_score_by_paper(...):
    
    ...
    
    by_paper = by_paper.clip(lower=-per_paper_cap, upper=per_paper_cap)
    
    atomic_facts.pyLines 149-166
    
    n = len(g)
    
    total = float(g["_w"].sum())
    
    ...
    
    dom = _weighted_dominant_direction(g)
    
    - **[높음] 충돌 판단이 `positive/negative`만 사용해 `mixed/null` 근거를 버림**
        - 실제로는 혼합/무효 근거가 많은데도 충돌 비율 계산에서 제외되어, 양/음의 점수 분율이 과장될 수 있습니다.
    
    conflicts.pyLines 82-95
    
    pos = g[g["_dir"] == "positive"]
    
    neg = g[g["_dir"] == "negative"]
    
    mixed = g[g["_dir"] == "mixed"]
    
    ...
    
    total = s_pos + s_neg
    
    share = s_pos / total
    
    - **[중간] `dominant_direction`이 건수 기반(count), 점수 기반(weight)과 불일치**
        - `association_rules`의 대표 방향은 가중치가 아니라 건수로 결정됩니다. 저품질 다건이 고품질 소수보다 방향 판정에 더 큰 영향 줄 수 있습니다.
    
    generate_rules.pyLines 311-324
    
    positive_count = int(...)
    
    negative_count = int(...)
    
    ...
    
    dominant_direction = compute_dominant_direction(
    
    positive_count, negative_count, mixed_count, null_count
    
    )
    
    - **[중간] `atomic_facts` 대표 방향 tie-break가 `positive` 편향**
        - 가중치 합이 동률일 때 `max()`가 dict 순서상 먼저 나온 `positive`를 선택할 수 있어, 경계 케이스에서 체계적 편향이 생깁니다.
    
    atomic_facts.pyLines 41-55
    
    for d in ["positive", "negative", "mixed", "null", "unclear"]:
    
    sums[d] = ...
    
    best = max(sums, key=lambda k: sums[k])
    
    ...
    
    return best
    
    - **[중간] `atomic_facts`가 evidence type을 분리하지 않아 이질 근거가 같은 fact로 합쳐질 수 있음**
        - 그룹 키에 `evidence_type`이 없어, 동일 `outcome_normalized`를 쓰는 관찰/기전/안전 문맥이 합쳐질 여지가 있습니다(특히 데이터 품질이 흔들릴 때).
    
    atomic_facts.pyLines 65-66
    
    그룹 키: rule_ingredient, outcome_normalized, population_segment, dose_route, claim_subject
    
    - **[중간] 스코어 체계가 이원화되어 파이프라인 해석 일관성 저하**
        - 충돌/atomic은 `evidence_score`(0~1 스케일), association는 `confidence_weight*direction_sign`(정수 스케일)이라 동일 데이터에 대해 중요도 판단 기준이 달라질 수 있습니다.
    
    evidence_scoring.pyLines 14-42
    
    study_type_weight * confidence_weight -> evidence_score
    
    generate_rules.pyLines 86-101
    
    def confidence_weight(...) -> int
    
    def direction_sign(...) -> int
    
    - **[낮음~중간] 음수 근거 정보가 `weighted_score` floor 처리로 일부 손실**
        - `weighted_score_raw`가 음수여도 `weighted_score = max(0, raw)`로 잘려 support 계산에 반영력이 줄고, 이후 규칙 소비자가 raw 대신 floor 값을 보면 리스크 신호가 약해집니다.
    
    generate_rules.pyLines 317-319
    
    weighted_score_raw = _capped_signed_score_by_paper(group)
    
    weighted_score = max(EFFICACY_WEIGHTED_SCORE_FLOOR, weighted_score_raw)
    
    ---
    
    확인하고 싶은 가정 2가지:
    
    - 레시피 추천이 현재 `final_guidelines`나 `conflicts_report`를 전혀 읽지 않는 구조가 맞는지
    - `atomic_facts`를 실제 추천/랭킹 입력으로도 쓸 계획인지(현재는 주로 guideline 생성용으로 보임)
- claude
    
    ```tsx
    ● 전체 파이프라인을 파악했습니다. 우선순위 순으로 정리합니다.
    
    ---
    
    스코어링·충돌 로직 위험 요소 (우선순위 순)
    
    ---
    
    1. confidence_weight 함수가 두 곳에 따로 존재하는 이중 스케일 문제 — 최우선
    
    evidence_scoring.py와 generate_rules.py에 같은 이름의 함수가 별도로 있는데 반환 타입과 스케일이 다릅니다.
    
    # evidence_scoring.py (float, 0~1 범위)
    
    def confidence_weight(confidence: str) -> float:
    high=1.0, medium=0.7, low=0.4, default=0.6
    
    # generate_rules.py (int, 1~3 범위)
    
    def confidence_weight(confidence: str) -> int:
    high=3, medium=2, low=1
    
    atomic_facts·conflicts는 float 기반 evidence_score를 쓰고, association_rules·dose_rules·safety_rules는 integer 기반 weighted_score를 씁니다. 두 파이프라인이 같은 데이터에서 출발해도 수치 체계가 달라
    "final_guidelines가 권장, association_rule은 weak" 같은 모순이 구조적으로 발생할 수 있습니다.
    
    ---
    
    1. 충돌(conflict) 탐지 키가 atomic_facts 집계 키보다 거칠어서 오염되는 문제 — 최우선
    
    # [conflicts.py](http://conflicts.py/): 3-tuple
    
    for (ri, out, cs), g in d.groupby(["_ri", "_out", "_cs"], ...)
    
    # atomic_facts.py: 5-tuple
    
    for (ri, out, pop, route, cs), g in d.groupby(["_ri", "_out", "_pop", "_route", "_cs"], ...)
    
    final_guidelines 빌드 시 (ri, ou, cs) 키로 conflict lookup을 합니다. 즉, "고령자"에서 발견된 positive↔negative 충돌이 "건강 성인" atomic fact에도 그대로 적용됩니다. 인구 집단별로 효과 방향이 다를 수 있는
    영양소(예: 철분, 비타민 D)에서 잘못된 tier_mixed_review 판정을 유발합니다.
    
    ---
    
    1. _weighted_dominant_direction에 최소 우세 마진 기준이 없는 문제
    
    best = max(sums, key=lambda k: sums[k])
    if sums[best] <= 0:
    return "unclear"
    return best
    
    positive=0.41, negative=0.40이어도 "positive" dominant를 반환합니다. 이 값이 compute_recommendation_tier에 들어가 tier_strong_positive까지 도달할 수 있습니다. 레시피에서 거의 상충되는 근거를 강한 권장으로
    오분류하는 가장 직접적인 위험입니다. 최소한 (sp - sn) / (sp + sn) > 0.15 같은 최소 마진 기준이 필요합니다.
    
    ---
    
    1. dose 규칙과 safety 규칙에 논문(paper) 단위 상한이 없는 문제
    
    association_rules와 interaction_rules에는 _capped_signed_score_by_paper(cap=2)가 있지만:
    
    # dose_rules (generate_rules.py:461)
    
    weighted_score = sum(confidence_weight(str(c)) for c in group["confidence"].tolist())
    
    # safety_rules (generate_rules.py:811)
    
    weighted_score = sum(confidence_weight(str(c)) for c in group["confidence"].tolist())
    
    한 논문이 여러 용량 또는 부작용 항목을 보고하면 그 논문의 기여가 무제한으로 축적됩니다. 논문 1편이 3개 dose entry를 내면 weighted_score=9 → strong으로 판정될 수 있습니다.
    
    ---
    
    1. compute_recommendation_tier에서 share 분기가 누락된 케이스
    
    if share >= 0.65 and dom == "positive":   # ✅
    ...
    if share >= 0.55 and dom == "positive":   # ✅
    ...
    if share <= 0.35 and dom == "negative":   # ✅
    ...
    if share <= 0.35 and dom == "positive":   # ✅
    ...
    
    # share >= 0.65인데 dom == "mixed"나 "unclear"이면? → 아무 분기도 안 걸림
    
    share >= 0.65이지만 dominant_direction이 "mixed"인 경우 어떤 분기도 통과하지 못하고 하단의 score 기반 로직(s >= 1.5 → moderate)으로 낙하합니다. share 정보가 완전히 무시됩니다. policy_language.py:166 참조.
    
    ---
    
    1. atomic_facts와 association_rules가 같은 데이터를 병렬로 집계하지만 조율 없이 독립 출력되는 구조
    
    main()에서:
    atomic_facts_df = generate_atomic_facts(df_scored)   # → final_guidelines
    association_df = generate_association_rules(df_scored)   # → association_rules.csv
    
    같은 데이터에서 final_guidelines와 association_rules가 별개로 만들어지는데 그룹 키가 다릅니다 (outcome vs state_tag). 레시피 로직이 두 파일을 모두 참조할 때 **성분 A가 final_guidelines에서는 "강력 권장",
    association_rules에서는 "weak"**으로 나오는 모순을 reconcile하는 코드가 없습니다.
    
    ---
    
    1. choose_representative_text가 품질이 아닌 길이 기준으로 대표 문장을 선택
    
    def choose_representative_text(series: pd.Series) -> str:
    values.sort(key=len, reverse=True)
    return values[0]
    
    가장 긴 문장 = 가장 verbose한 문장이지, 가장 high-confidence나 high-score인 문장이 아닙니다. 레시피 출력에 표시되는 representative_statement가 case report 수준의 장황한 서술에서 왔을 가능성이 있습니다.
    
    ---
    
    1. LLM이 출력한 direction="mixed"와 내부 집계로 산출한 "mixed" 개념이 구분되지 않음
    
    compute_recommendation_tier에서 tier_mixed_review는 0.35 < share < 0.65 조건에서만 발동합니다. 그런데 LLM이 단일 논문 결과 자체를 "mixed"라 표기한 경우, share 계산에 분자(positive)도 분모(negative)도 없어
    share=None이 됩니다. 결과적으로 "mixed" 방향의 논문 3편이 있어도 tier_mixed_review가 아닌 tier_reference나 tier_limited로 분류됩니다.
    
    ---
    
    1. evidence_score_sum에 null/unclear 근거가 포함되지만 weighted_positive_share 분모에는 제외되는 분모 불일치
    
    atomic_facts.evidence_score_sum은 모든 방향의 score 합입니다. 그러나:
    
    # policy_language.py:122
    
    share = sp / (sp + sn)  # null, unclear 무시
    
    null/unclear evidence가 많을수록 evidence_score_sum은 크지만 share 계산에는 반영되지 않아, score_sum이 높게 나오지만 실제 유효 방향 비율은 낮은 음영 구간이 생깁니다.
    
    ---
    
    1. dose 규칙에서 신뢰도 낮은 논문이 min/max 용량을 결정할 수 있는 문제
    
    "dose_min": float(group["dose_value"].min()),
    "dose_max": float(group["dose_value"].max()),
    
    집계 전에 confidence 기준 필터링이 없습니다. low-confidence case report 1건의 극단 용량이 dose_min 또는 dose_max로 노출됩니다. 레시피에서 최소/최대 용량 범위 표시에 직접 영향을 줍니다.
    ```
    
- claude 충돌 브리핑 내용 확인
    1. confidence weight 스케일 통일 안됨 (evidence_scoring과 generate_rules 다름) → float로 채택 
        
        ![{2A5378E3-786B-4CFE-A97B-08E3B9F29A60}.png](attachment:7dd6160d-3964-40bd-a08d-56bcc5badcfb:2A5378E3-786B-4CFE-A97B-08E3B9F29A60.png)
        
        ![{571C6A33-F0C4-4514-BF28-01B994160345}.png](attachment:e8b011e0-234a-4df6-b2be-03fd194cd598:571C6A33-F0C4-4514-BF28-01B994160345.png)
        
    2. 우리가 원하는 방향성과 코드의 방향성의 일치성 점검 및 보완점 확인 
        1. 좋은 구조
            1. LLM 출력 행 제한 준수 (evidence 개수 초과한 것 없음)
            2. dose 수치 필드 완결성 (dose_value/unit 채워짐)
            3. 핵심 설문 state_tag 커버 (14개 중 9개 커버함) - 좋은 게 아닌데??
            4. 파이프라인 아키텍처 (Bronze → Silver → Gold 단계 분리 명확)
            5. conflict 탐지 및 tier 산출 (claude 수정으로 구조적 차단 완료)
        2. 보완 필요
            1. target_ingredient 정규화 없음
            : magnesium이 17가지가 나와서 atomic_facts가 636개 있으면 evidence 567개가 나와서 거의 모든 게 잠재적 유익성(근거 부족 tier)로 강등됨. 
            → target_ingredient→canonical ingredient 매핑 테이블을 config에 추가하고 enrich_evidence_with_scores 단계에서 rule_ingredient를 canonical form으로 정규화 
            2. state_tags 미입력된 것들 (햇빛 노출, 유제품, 생선, 당류, 신경계 없음)
            3. confidence를 llm에게 과대하게 부여하는 것 → bias 유도 
            evidence scoring에서 RCT = 1.0이 atomic_facts weight에 들어가는데 llm이 rct 처리할때 기계적으로 high를 부여하면 근거 강도가 훨씬 빡세짐 (과평가), 다변량 보정 여부, 표본 수, 선택 평향을 confidence 판정 기준으로 넣었지만 실제 반영 안되고 있는 문제
            4. dose_route = unknown 이 너무 많음 (똑같은 oral 복용인데 dose_route가 달라서 다른 그룹이 되는 것, n_evidence = 1 fragmentation 의 원인. unknown 추론 로직이나 병합하는 전처리 필요 (groupby 단에서)
            5. dose_unit이 known이면 dose_rules 제외되는 거 아까움. 단위 추론 로직 보완이 필요 
            6. 
- 차이
    
    커서는 이 파일은 이걸 쓰고, 저 파일은 이걸 안 쓰고의 가시적인 surface 차이점 위주, 구조적인 불일치를 찾는 데에서 그침 
    
    클로드는 1번 (이중 스케일 문제)에서 같은 함수이름인데 타입과 범위가 달라서 발생하는 모순을 찾아냄 로직의 충돌… 시한폭탄 같은 것
    2번 (충돌 탐지 키 오염) : 고령자가데이터가 성인 데이터에 영향을 줄 수 있다는 것을 파악한것. 코드를 단순히 읽는 게 아니라 데이터의 흐름과 비지니스 로직을 이해하고 있는 것. 
    
    → 이게 왜 레시피에서 문제가 되는지, 비지니스 임팩트를 연결해서 설명함 
    

같은 질문을 던졌을 때, 단순 코드 불일치를 찾는 Cursor와 **데이터 스케일의 모순과 도메인 지식(영양소 충돌)의 허점**을 찾아낸 Claude Code의 차이.

지적해준 10가지 포인트가 정말 날카로워. 특히 1번(이중 스케일)과 2번(충돌 키 오염)은 지금 당장 해결해야겠어.

1. `evidence_scoring.py`와 `generate_rules.py`의 `confidence_weight` 스케일을 하나로 통일하는 리팩토링을 진행해줘. 어떤 스케일이 더 합리적일지 먼저 제안해줘.
2. 충돌 탐지 키를 `atomic_facts`와 동일하게 5-tuple로 맞춰서 인구 집단별 데이터 오염을 막는 코드를 수정해줘.

이 작업을 마친 뒤에, 전체 파이프라인을 다시 돌려서 `conflicts_report.csv`에 어떤 변화가 생기는지 확인해보고 싶어.

![{46FBCF66-9539-4EA9-A5A7-4B372B9D50FC}.png](attachment:358720f5-135d-45d2-876a-54def5087408:46FBCF66-9539-4EA9-A5A7-4B372B9D50FC.png)

클로드가 있더라도 판단하고 실행하는 건 우리의 몫… 무작정 실행하는것보다 실행의 이유를 따지는 게 중요함 

- DRI 테이블 생성하기 (베이스 레시피 도출용)

![{7B81DE38-6EFE-433B-B057-72C34DE40F52}.png](attachment:c058d7be-0ff0-4cc6-b428-ca7a48aa4511:7B81DE38-6EFE-433B-B057-72C34DE40F52.png)

- Dose 와 관련된 UL 넘지 않도록 클램핑 하고 BMI 계산하는 것도 설문에 추가
- 13개 시나리오 업데이트 및 실행 완료 → 정확히 동작함
    - S11 노인 여성 68세 57kg: 단백질 1.0g/kg (노인 보정) × 57kg = 57g, 마그네슘 228mg
    - S12 비만 남성 BMI 33.7: 비타민D BMI 2.0x 계수 → 20μg (표준 10μg의 2배)
    - S13 고강도 운동 80kg: 단백질 1.6g/kg × 80kg = 128g, 마그네슘 cap 350mg

![{7A427CD8-8C69-447D-8FA9-51D28F76A6BA}.png](attachment:e9ad87c5-8c95-4715-a6c7-01f372fe1b81:7A427CD8-8C69-447D-8FA9-51D28F76A6BA.png)

![{8B2E1E2C-BE45-4935-86D4-ED88C1F67947}.png](attachment:6587c599-edc2-4405-8606-b89ab8b41212:8B2E1E2C-BE45-4935-86D4-ED88C1F67947.png)

아까 전에는 논문 다시 돌릴 필요 없다고 했는데 안 돌렸더니 누락된 필드 → 이게 하필 품질 테스트 측면에서 중요한 거였고 (canonical 반영) 이걸 모르고 코드를 수정할뻔했는데 중간에 작업을 막아서 괜찮았음 

![{F8951F17-ADFD-4CD6-BA07-67C5AA0F84C2}.png](attachment:ba5a33b3-5e97-463b-a5bc-b2534ebfbdd6:F8951F17-ADFD-4CD6-BA07-67C5AA0F84C2.png)

![{CD9C8E1C-E2F7-4298-A64B-532209217806}.png](attachment:e68a7fd7-7e3b-48c4-ae90-2c2f2108de52:CD9C8E1C-E2F7-4298-A64B-532209217806.png)

품질 테스트를 진행하면서 잘못 나온 게 있으면 역추적 할 수 있어야 함 
빈혈 경험이 있다고 입력했는데 iron 의 추천 점수가 0.52 (논문 간 상충이 있었음)

빈혈 경험과 iron은 필연적이고 상충되면 안되는 기본적인 지식인데 상충이 됐다는 건 논문에서 evidence를 추출하는 과정에서 에러가 있다는 것 → 확인해봤더니 ‘철분 보충이 혈색소에 부정적’이 아니라 ‘운동 강도가 높으면 철이 소모됨’을 관찰한 연구인데 ‘철 농도가 낮아졌다’는 결과를 보고 direction=negative로 추출한 것. 

![{27B74567-77F1-4353-BB6D-955B454B1EEE}.png](attachment:c874dd9a-aa22-4258-b3f3-cce55ebefdfe:27B74567-77F1-4353-BB6D-955B454B1EEE.png)

- 역상관관계에 대한 내용을 direction = negative로 추출하는 llm 추출 로직
    - 엽산 상태와 호모시스테인이 역상관관계라는 내용인데 이를 direction = negative로 추출해서 빈혈 경험이 있음에도 불구하고 엽산이 제외된 성분으로 나옴. 
    → 실제 의미 : 엽산을 많이 먹으면 호모시스테인이 낮아져서 빈혈 위험이 감소하는것 = positive 임
    - 이 구조 (역상관관계를 negative로 잘못 해석)가 전체를 뒤집고 있음 → 음수 룰을 처리하는 로직 수정 필요
    - 문제가 두 층으로 겹쳐 있음
        - 1층 (데이터) : 엽산-호모시스테인 역상관관계를 direction=negative로 해서 folatexanemia_risk 룰이 음수로 나옴
        - 2층 (로직) : score ≤0 (음수)이면 hard exclude → prior_knowledge를 추가해도 negative(-1.3) + prior_knowledge(1.3) = 0.0 여전히 excluded 인것
        
        ⇒ prior_knowledge weight를 weak보다 높게 설정해서 llm 단일 오류를 이길 수 있도록 
        

![{6E9CB3DD-3926-43C3-8389-147DC41F88A8}.png](attachment:bad633e0-6e5b-47ad-a590-901ec48038de:6E9CB3DD-3926-43C3-8389-147DC41F88A8.png)

### 파이프라인 칭찬

![{F6EBED4E-903B-4281-9024-BC14125BF0AA}.png](attachment:a045e127-c2d5-498f-89ab-51e9888806f7:F6EBED4E-903B-4281-9024-BC14125BF0AA.png)

![{42100BB8-6F72-4435-9EE2-0F1389ABF598}.png](attachment:041b2df1-be34-415f-8f5f-0d9063f721e2:42100BB8-6F72-4435-9EE2-0F1389ABF598.png)

![{BD4556D3-0233-4C1D-8983-642141E5A765}.png](attachment:bbb5b3e6-c8f7-4089-ac79-de1cd93a5608:BD4556D3-0233-4C1D-8983-642141E5A765.png)

![{B0892FAE-CEEC-476E-BD35-9104CC2B5903}.png](attachment:e4d0b695-c580-4ad1-ab21-25949d526329:B0892FAE-CEEC-476E-BD35-9104CC2B5903.png)

![{9378BAF9-19F5-4DD9-87E2-3D5C50190CE3}.png](attachment:f275c5b7-b334-4867-ba47-f8bda0db3cee:9378BAF9-19F5-4DD9-87E2-3D5C50190CE3.png)

| **평가 차원** | **항목** | **등급** | **상세 평가 및 상용화 관점의 분석** |
| --- | --- | --- | --- |
| **영양학적 정밀도** | **개인화 분석력** | **S+** | 사용자의 BMI, 식습관(고당 식이), 증상(피로, 빈혈)을 벡터화하여 1~8위까지 정교하게 도출함. |
|  | **시너지 배합** | **S** | 비타민 C와 철분의 3배 흡수 로직 등 영양소 간의 상호작용을 계산에 반영함. |
| **임상적 안전성** | **고위험군 배제** | **S+** | **칼륨(Potassium)** 등 심장/신장에 민감한 성분을 'Hard Safety' 로직으로 자동 차단하여 법적 리스크 관리. |
|  | **제형 최적화** | **A+** | 저체중 사용자를 위해 위장 부담이 적은 **Bisglycinate** 형태의 미네랄을 우선 매칭함. |
| **H/W 연동 적합성** | **투입량 변환** | **B+** | **순도/벌크 밀도** 개념이 도입되었으나, 실제 하드웨어의 오거(Auger) 제어값으로의 최종 매핑은 미팅 후 보완 필요. |
|  | **용해 환경 제어** | **A** | 포화용해도에 따른 물 양 산출 로직이 설계되어 물리적 '떡짐'이나 미용해 현상을 예방 가능함. |
| **상업적 신뢰도** | **복약 지도력** | **S** | LLM 기반의 전문가 페르소나 총평이 도입되어, 단순 자판기를 넘어 '디지털 약사'의 경험을 제공함. |
|  | **데이터 투명성** | **A** | DRI(권장량), UL(상한량), 논문 근거 용량을 모두 표기하여 전문가용 신뢰도 확보. |

## 파이프라인 최종 구조

### LLM 기반 임상 근거 증류 파이프라인 (LLM-Augmented Clinical Evidence Distillation Pipeline)

- LLM-Augmented : AI가 추천 주체가 아닌 근거 도출 도구로 사용 → 과장 없음
- Clinical Evidence : 논문 근거 기반 → 규제 대응 근거 가능
- Distillation : 수백 편 논문 → 단일 방향성 규칙으로 증류 - 정보 손실 없이 압축

### 아키텍처 구조 : Medallion Evidence Architecture (3-tier)

1. Bronze : 논문 원자 근거 
    1. pdf → LLM 추출 → 행 단위 저장
2. Silver : 정규화/점수화 근거
    1. study_type 가중, confidence 보정, 결과 표준화 (atomic facts + evidence with scores)
3. gold : 의사결정 룰
    1. association, dose, safety, interaction ruels 
    2. 성분 x state_tag 집계 x 방향성/신뢰도 확정 

⇒ Databricks가 정의한 Medallion Architecture와 동일한 계층 논리이며, 의약 데이터 파이프라인(FDA Sentinel, EMA 약물 감시)에서도 채택하는 표준 방식임 

### 5가지 핵심 구조적 특징

① Claim Distillation (클레임 증류)

논문 A: "마그네슘 → 수면 개선 (positive, RCT, high)"
논문 B: "마그네슘 → 수면 개선 (positive, RCT, medium)"
논문 C: "마그네슘 → 수면 개선 (mixed, Observational)"
↓
association_rule: sleep_problem, dominant=positive,
positive_count=5, weighted_score=6.2, support=strong

경쟁 차별점: 단순 논문 수 집계가 아닌 study_type × confidence × direction 가중 합산. 저신뢰 연구가 고신뢰 RCT를 이길 수 없습니다.

---

② Dual-Source Knowledge Injection (이중 지식 주입)

논문 근거 (Bottom-up)          임상 지식 (Top-down)
↓                               ↓
association_rules           clinical_guarantees.yaml
prior_facts.yaml
↘         ↙
추천 엔진 (병합)

- Bottom-up: 논문에서 귀납적으로 추출된 규칙
- Top-down: WHO·KDRIs·생리학 교과서 수준의 연역적 임상 지식
- 두 레이어가 충돌하지 않고 보완: 논문 근거 부족 시 임상 지식이 fallback

의미: 근거 공백(Evidence Gap)을 임상 지식으로 메우면서도 두 근거 출처를 혼합하지 않고 추적 가능하게 분리 관리.

---

③ Multi-Signal Needs Vector (다중 신호 니즈 벡터)

needs_vector = {
"fatigue_state":        1.63,  # q_fatigue(direct) + q_anemia(supporting)
"anemia_risk":          1.50,  # q_anemia(direct) + q_fatigue(supporting)
"glucose_variability":  1.10,  # q_sugar(direct)
...
}

설문 응답 → 단순 카테고리 매칭이 아닌 가중 연속값 벡터로 변환. 동일한 q_anemia=diagnosed 응답도 q_fatigue=high가 동반되면 anemia_risk 점수가 더 높아집니다.

의미: 추천 결과가 설문의 조합에 반응 — 단일 응답이 아닌 사용자 전체 상태를 반영.

---

④ Layered Safety Architecture (계층적 안전 필터링)

Layer 1 — LLM 추출 Safety Rules
논문에서 추출된 contraindication/AE → hard/soft 분류

Layer 2 — 상호작용 검사
추천 성분 간 cross-interaction pair 검사

Layer 3 — DRI UL Clamping
한국인 섭취기준 상한선 자동 조정

Layer 4 — Constraint Tags
흡연·음주·카페인 → 니즈벡터 아닌 별도 constraint 채널

의미: 일반 앱의 블랙리스트 방식과 달리 논문 근거가 있는 안전 필터 — 규제 대응 시 각 필터의 근거를 제시 가능.

---

⑤ Self-Updating Rule Generation (자기갱신 룰 엔진)

새 논문 추가
↓
process_one_paper (LLM 분석)
↓ evidence_db 자동 추가
generate_rules (파이프라인 재실행)
↓
새 association_rule 자동 생성 or 기존 룰 강화

논문 30편 추가 → 배치 실행 → 규칙 자동 갱신. 수작업 룰 편집 없음.

의미: 논문 DB가 곧 경쟁 해자(Moat). 데이터가 쌓일수록 정밀도가 올라가는 플라이휠 구조.

![{7B228EC3-A1C8-4DEC-AF20-B01B8092195F}.png](attachment:7dde4630-2372-4b0e-964f-9c8d08aca6cd:7B228EC3-A1C8-4DEC-AF20-B01B8092195F.png)

### RAG의 구조를 정형 데이터 파이프라인으로 치환 (AI의 불안정성 제거)

- 구조도 Mermaid 코드
    
    ```tsx
     flowchart TB
          classDef input   fill:#dbeafe,stroke:#3b82f6,color:#1e40af
          classDef process fill:#d1fae5,stroke:#10b981,color:#065f46
          classDef store   fill:#fef3c7,stroke:#f59e0b,color:#78350f
          classDef config  fill:#f3e8ff,stroke:#8b5cf6,color:#5b21b6
          classDef output  fill:#fce7f3,stroke:#ec4899,color:#9d174d
    
          PDF["☁️ Google Drive\nPDF 논문 (성분별 폴더)"]:::input
          USER["👤 사용자\n설문 응답 19개 + 신체정보"]:::input
    
          subgraph BATCH["🔄  배치 파이프라인  (오프라인 · 논문 → 규칙)"]
              direction TB
              A["pdf_service\nPDF → 텍스트"]:::process
              B["llm_service · GPT-4.1-mini\n논문 → evidence rows (최대 6개/편)\nclaim_subject · direction
       · confidence 추출"]:::process
              C[("evidence_db.csv\n원자 근거 행")]:::store
              D["evidence_scoring\npopulation_segment · dosage_normalize\nstudy_type × confidence →
      evidence_score"]:::process
              E[("evidence_with_scores.csv")]:::store
              F["atomic_facts.py\n5-tuple 그룹 집계\ndominant_direction ·
      weighted_positive_share"]:::process
              G["conflicts.py\n긍·부 충돌 감지\nconflict_verdict 판정"]:::process
              H["policy_language.py\n추천 등급 8단계 판정\n한국어 가이드라인 생성"]:::process
              I["generate_rules.py\n4종 규칙 CSV 생성"]:::process
    
              A --> B --> C --> D --> E
              E --> F
              E --> G
              F --> H
              G --> H
              H --> I
          end
    
          RULES[("association_rules.csv\ndose_rules.csv  ·  safety_rules.csv\ninteraction_rules.csv  ·
      final_guidelines.csv")]:::store
    
          subgraph CONFIG["⚙️  설정 레이어  (data/config/)"]
              direction LR
              C1["algorithm_params.yaml\n점수·등급 임계값 18개"]:::config
              C2["prior_facts.yaml\n임상 사전 지식\n(논문 없는 조합 fallback)"]:::config
              C3["clinical_guarantees.yaml\n임상 보장 규칙 25개"]:::config
              C4["ingredient_canonical_groups.yaml\n16개 성분 그룹·형태"]:::config
              C5["dri_korean.csv\n한국인 영양소 섭취기준"]:::config
              C6["constraint_warnings.yaml\n제약 조건 경고 매핑"]:::config
          end
    
          subgraph ONLINE["⚡  온라인 추천 엔진  (실시간)"]
              direction TB
              P1["survey_needs.py\n설문 → needs_vector + constraint_tags\nstate_weight ×
      question_importance"]:::process
              P2["성분 점수 계산\nassociation_rules × needs_vector\nTop-5 rule 합산 +
      dose_bonus"]:::process
              P3["임상 보장 규칙 적용\nclinical_guarantees.yaml\nforce_core 성분 강제 포함"]:::process
              P4["안전성 필터\nhard_exclude · soft_warning · soft_penalty\nconstraint_tag 경고 문구
      추가"]:::process
              P5["canonical 중복 제거\nform_selection 자동 선택\n소화 불편 → bisglycinate 등"]:::process
              P6["DRI 용량 산출\n성별 × 연령 × 체중 기반\nUL 초과 시 자동 보정"]:::process
    
              P1 --> P2 --> P3 --> P4 --> P5 --> P6
          end
    
          OUT["📋 최종 추천 결과\ncore 성분 + supporting 성분\n권장 용량 · 추천 등급 · 안전
      경고"]:::output
    
          %% ── 주요 데이터 흐름 ──
          PDF --> A
          USER --> P1
          I --> RULES
          RULES --> P2
          RULES --> P4
    
          %% ── 설정 레이어 → 파이프라인 ──
          C1 --> F
          C1 --> G
          C1 --> H
          C2 --> I
    
          %% ── 설정 레이어 → 추천 엔진 ──
          C3 --> P3
          C4 --> P5
          C5 --> P6
          C6 --> P4
    
          %% ── 출력 ──
          P6 --> OUT
    ```