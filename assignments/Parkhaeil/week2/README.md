# Week 2 — 체크포인터 + Interrupt 기반 스킬 트리 선택 시스템

1주차 스타듀밸리 ReAct Agent에 (1) PostgresSaver 체크포인터와 (2) interrupt 기반 사용자 입력 흐름을 추가.

## 로컬 Postgres 세팅

```bash
# Postgres 설치 & 시작
brew install postgresql@16
brew services start postgresql@16

# 과제용 데이터베이스 생성
createdb stardew_agent
```

> **인증 에러 시** `postgresql://USER@localhost:5432/stardew_agent` 형식으로 시도 (USER는 `whoami` 결과)

`.env` 파일에 연결 정보를 관리합니다:
```
POSTGRES_URI=postgresql://localhost:5432/stardew_agent
```

## 그래프 구조

```
START → agent ─[should_continue]─┬→ tools → agent (루프)
                                  ├→ commit_choice → format → END
                                  └→ format → END
```

`interrupt_before=["commit_choice"]`로 사용자 선택 대기 포인트를 명시.

## 주요 변경 사항

### 커스텀 reducer `upsert_skill_choices`

스타듀밸리는 하수구에서 10,000g을 내고 직업을 재선택할 수 있음.  
같은 레벨에 대해 나중에 다른 선택이 들어오면 덮어써야 하기 때문에,  
기본 `add` reducer(항상 추가)나 덮어쓰기(이전 기록 소실) 모두 맞지 않아 upsert를 직접 구현했음.

```python
def upsert_skill_choices(current, new):
    # 같은 level 있으면 교체, 없으면 추가
```

### interrupt 패턴 선택 이유

스킬 트리 선택은 게임 내 비용이 큰 결정(5레벨은 이후 10레벨 선택지 자체가 달라짐).  
LLM이 정보를 제공한 뒤 **사용자가 직접 확인**하도록 "추천 → interrupt → 컨펌" 패턴이 적합함.  
강의에서 든 "보고서 outline 생성 후 사용자 승인" 예시와 같은 구조.

### `[AWAITING_SKILL_CHOICE]` 시그널

`should_continue` 라우터가 LLM 응답에서 이 문자열을 감지해 `commit_choice` 노드로 분기.  
format 노드에서 최종 출력 시 이 문자열을 제거해 사용자에게는 노출하지 않음.

## 시나리오 결과 요약

### 시나리오 1: thread_id 분리

| 호출 | thread_id | 결과 |
|------|-----------|------|
| 1차 | thread-A | "민준이야 기억해줘" 저장 |
| 2차 | thread-A | 이전 대화 이어받아 이름 기억 |
| 3차 | thread-B | 새 세션, 이름 모름 |

Postgres에 thread별로 체크포인트가 저장되므로 `thread_id`가 곧 세션 키.

### 시나리오 2: interrupt 흐름

```
사용자: "농사 5렙인데 뭐 찍을지 고민이야"
봇: "목축업자(+20%) vs 경작인(+10%). 뭐할래?"  ← [AWAITING_SKILL_CHOICE] 포함
--- interrupt ---
사용자: "목축업자 할래"
봇: "저장했어요!"
skill_choices: [{"level": 5, "choice": "목축업자"}]
```

### 시나리오 3: 하수구 직업 변경

```
사용자: "사실 경작인으로 바꿨어"
→ upsert: level 5를 경작인으로 교체
skill_choices: [{"level": 5, "choice": "경작인"}]  ← 리스트 길이 1 유지
```
