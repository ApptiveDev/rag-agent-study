### Adversarial Injection : 의도적으로 오류 케이스를 넣어서 검증 에이전트가 이를 잡아내는지 확인하는 방법

Evidence 추출 오류율 추정 결과 (50편, 166행 표본 결과) : 95% 신뢰구간에서 16.3% 정도 (최대 22.6%)
하지만 validator가 체크하는 영역 (direction, 처방약 잘못 classify, causal attribution)에서는 100% 잡아내는데 validator가 모르는 오류 유형 (미묘한 수치 과장이나 맥락 오독 등)은 측정 불가능함. 이 유형 기준 약 16% (95% CI:11~23%)를 자동으로 플래그하고 해당 오류 유형에 대한 캐치율은 100%(n=15)

fn_review_sample_v2.csv 수동 검토가 필요하긴 함. 해당 방식은 우리가 이미 아는 오류를 자동 테스트하는 것이기에 우리가 아직 정의하지 못한 패턴이 항상 존재한다는 것이 문제이다. 수동 검토는 그걸 발견하는 유일한 방법임. 

수동 검토 → 미지의 오류 발견 → adversarial 케이스 추가 → 자동화 범위 확대 → 다음 수동 검토로 미지의 오류 발견 의 반복 (수동 검토를 없애는 게 목표가 아니라 수동 검토의 빈도와 범위를 줄이는 게 목표)

### 수동 검토를 없애는 건 불가능 + Adversarial Injection 자동화로 오류 범위 늘려가기

### 레전드레전드!!

50편 샘플 + 기존 체크 3가지는 16.3% 였는데 새로 추가한 체크 3가지 (outcome_normalized 누락, state_tags 누락, applicability 오분류) 에다가 1175편을 했더니 → 48.9%로 올랐다

reject 5%, correct 44% 인데 대부분은 데이터 제외가 아니라 자동 수정 (outcome_normalized 채움, state_tags 추가) 인것임. 실제 오염 제거보다 누락 필드 보완이 훨씬 많았음. 

5%는 실제 근본적으로 정보를 추출한것에 오류가 있었던 것이고 (잘못된 인과 귀속, 방향 반전 등)
44%는 누락 필드를 자동으로 보완한 것들임. → 잘못 나온게아닌것 

![{6A543A56-CA8D-440F-A102-2FB6D20B182A}.png](attachment:ccf1a1f1-6aa6-4cfe-9493-7ced346bfcf0:6A543A56-CA8D-440F-A102-2FB6D20B182A.png)

전체 evidence 중에서 rule로 만들어지는 게 34% 정도밖에 없었고, 66%가 안쓰이는 이유는 target_effect_Relation = unrelated_to_target인게 전체의 68%이고 rule 생성에 들어가는건 supports_target인것만 쓰이기 때문. 

direct이면서 unrelated_to_target인 행이 1400개인것은 논리적으로 모순이다라고 하는데, rule 생성되는 범위를 supports_to_taget으로 좁혔던건 interacts까지 포함하니 rule 이 이상하게 나오는것을 발견했기 때문임. 지금 상황에서 범위를 늘리는게 얼마나 유의미할지 확인하기 

⇒ 핵심 패턴이 뭐였냐면 interacts_partners가 비어있어도 llm이 논문 내 복합 맥락이 있다는 이유로 interacts로 붙이는 경우가 235개였고, 진짜 성분간 상호작용이어서 interacts로 나온게 19개였음. 235개는 처리해야 rule 품질이 올라감. 즉, interaction_partners가 비어있고 interacts-to-target인 경우는 association rule과 동일하다는 것임. → 이거 보정하는 로직 추가 

### 품질 개선 이유

![{7D7F955E-E93D-47E3-9D45-0A6301ED4D98}.png](attachment:4b0d2c3f-cbca-423c-a996-23909aa5858b:7D7F955E-E93D-47E3-9D45-0A6301ED4D98.png)

수정 전 : 7/36 = 19% 이고 수정 후 : 31/36 = 86% → +67%p (4.4배 향상)

 CKD(6/8)은 처음부터 잘 동작 → 이거 포함하면 전체 수치가 눌리고 CKD 제외하고 “수정 전에 깨져 있던 항목”만 보면 → 1/28=4% ⇒ 25/29=89% 로 22배 개선됨

버그 3개가 독립적인 문제였고 이걸 다 고쳐서 개선함 

- BMI 주입 + 가중치 상향 같이 묶어야 효과가 남 : needs_vector 에 BMI 신호 추가, 그 신호가 guarantee 임계값에 도달해서 가중치 상향했더니 이게 효과가 있었고
- 오타 수정 (pregnant → pregnancy). 임상 로직은 처음부터 있었는데 임신 태그 자체가 아예 생성됨