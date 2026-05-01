# Assignment Guide

과제는 매주 새로운 프로젝트를 만드는 방식이 아닙니다. 각자 고른 도메인을 바탕으로 하나의 LangGraph 기반 시스템을 6주 동안 조금씩 키워가는 방식으로 진행합니다.

노트북은 패턴을 익히기 위한 자료이고, 과제의 핵심은 그 패턴을 자기 도메인에 적용해 보는 것입니다. 6주가 끝났을 때 각자 도메인에 특화된 RAG/Agent 시스템 하나가 남는 것을 목표로 합니다.

## 공통 전제

스터디 시작 전에 6주 동안 다룰 도메인 1개를 정합니다. 너무 거창할 필요는 없지만, 질문을 만들 수 있을 만큼 문서나 데이터가 충분해야 합니다.

예시는 다음과 같습니다.

- 자기 GitHub 레포의 코드베이스
- 즐겨 읽는 논문 모음
- 사이드프로젝트 문서
- 제품 매뉴얼 또는 운영 문서
- 게임 위키, 기술 블로그, 튜토리얼 모음

도메인은 6주 동안 유지합니다. 매주 과제는 같은 도메인 시스템을 한 단계씩 확장하는 방식으로 진행합니다.

## 제출 위치

학생 제출물은 `assignments/` 아래에 둡니다.

```text
assignments/
└── {github-id}/
    ├── week1/
    ├── week2/
    ├── week3/
    ├── week4/
    ├── week5/
    └── week6/
```

각 주차 폴더 안에는 코드, 노트북, 데이터 샘플, 실행 스크립트 등 필요한 파일을 자유롭게 둘 수 있습니다. 별도 마크다운 제출 파일은 필수가 아닙니다. 구현 요약과 실행 결과는 PR 본문에 적어 주세요.

## PR 작성 규칙

브랜치는 `{깃헙아이디}/{과제명}` 형식으로 만듭니다.

- 1주차: `your-id/week1-react-graph` -> `assignments/your-id/week1/`
- 2주차: `your-id/week2-state-memory` -> `assignments/your-id/week2/`
- 3주차: `your-id/week3-domain-rag` -> `assignments/your-id/week3/`
- 4주차: `your-id/week4-agentic-rag` -> `assignments/your-id/week4/`
- 5주차: `your-id/week5-tool-agent` -> `assignments/your-id/week5/`
- 6주차: `your-id/week6-supervisor-agent` -> `assignments/your-id/week6/`

PR 본문에는 아래 내용을 포함합니다.

- 선택한 도메인과 이번 주 구현 목표
- 구현 요약
- 실행 방법
- 테스트 입력 또는 데모 시나리오
- 실행 결과 요약
- 막힌 점 또는 다음 주에 개선할 점

## 1주차: StateGraph ReAct Loop

1주차 목표는 helper agent 뒤에 숨어 있는 LangGraph의 기본 실행 모델을 직접 이해하는 것입니다.

LangChain의 `create_agent` 같은 고수준 agent helper는 사용하지 않습니다. `StateGraph`로 직접 ReAct loop를 구성해 보세요. 자기 도메인에 맞는 도구를 2-3개 만들고, 모델이 도구 사용 여부를 판단한 뒤 최종 답변을 생성하는 흐름을 그래프로 표현합니다.

도구가 반드시 실제 API일 필요는 없습니다. 초반에는 mock 데이터나 간단한 로컬 함수만으로도 충분합니다.

필수 요구사항:

- `StateGraph`로 직접 그래프 구성
- 도메인용 tool 2-3개 구현
- 조건부 엣지로 tool 호출 여부 제어
- 최종 응답을 Pydantic 또는 TypedDict 기반 structured output으로 강제
- 그래프 시각화 결과 포함
- 테스트 질문 3개 이상 실행

심화:

- 도구 실패 시 retry 또는 fallback 분기 추가
- tool call trace를 보기 좋게 출력
- 응답 스키마에 근거, 사용한 도구, confidence 같은 필드 추가

제출 기준:

- `assignments/{github-id}/week1/` 아래에 구현 파일 제출
- PR에 그래프 노드/엣지 흐름 설명 포함
- PR에 테스트 질문과 응답 결과 요약 포함

## 2주차: State, Memory, Control

2주차 목표는 1주차 그래프를 상태가 유지되는 workflow로 확장하는 것입니다.

1주차 그래프에 `thread_id` 기반 short-term memory를 붙입니다. 같은 사용자 대화가 이어지는 경우와 새 thread로 시작하는 경우가 어떻게 달라지는지 확인해 보세요. 여기에 streaming, interrupt, branching, subgraph 중 최소 1개를 추가해 그래프 실행을 제어합니다.

필수 요구사항:

- 1주차 그래프 또는 같은 도메인의 새 그래프 재사용
- `InMemorySaver` 또는 동등한 checkpointer 적용
- `thread_id`에 따라 대화 상태가 분리되는 예시 포함
- streaming, interrupt, branching, subgraph 중 최소 1개 적용
- 이전 대화 맥락을 활용하는 테스트 질문 3개 이상 실행

심화:

- long-term memory `Store`로 사용자별 선호 또는 이력 저장
- 입력 PII 마스킹, 토큰 사용량 로깅, dynamic prompt 변경 중 하나를 별도 노드 또는 래퍼 함수로 구현
- interrupt 이후 상태 수정 또는 resume 흐름 추가

제출 기준:

- `assignments/{github-id}/week2/` 아래에 구현 파일 제출
- PR에 같은 `thread_id`와 다른 `thread_id`의 실행 차이 설명 포함
- PR에 추가한 실행 제어 패턴의 이유 포함

## 3주차: Domain RAG

3주차 목표는 자기 도메인 문서를 기반으로 기본 RAG 파이프라인을 구축하는 것입니다.

도메인 문서 또는 코드 파일을 최소 20개 이상 수집합니다. 문서를 로드하고, 청킹하고, embedding하고, vector store를 구축한 뒤 2-step RAG Q&A를 구현합니다. 청킹 전략을 2개 이상 비교하면서 어떤 질문에서 결과가 달라지는지도 확인합니다.

필수 요구사항:

- 도메인 문서 또는 코드 파일 20개 이상 사용
- loader, splitter, embedding, vector store, retriever 구성
- 2-step RAG Q&A 구현
- 청킹 전략 2개 이상 비교
- 비교 쿼리 3개 이상 정리
- 최종 테스트 질문 5개 이상 실행
- 답변에 근거 문서 또는 파일 정보를 함께 출력

심화:

- BM25와 vector search를 결합한 hybrid retrieval
- metadata filtering 추가
- query rewrite 또는 groundedness check 추가
- 검색 결과를 표 형태로 비교

제출 기준:

- `assignments/{github-id}/week3/` 아래에 구현 파일 제출
- 큰 원본 데이터는 필요한 경우 제외하고 샘플 또는 수집 방법만 남김
- PR에 청킹 전략 비교 결과와 선택 이유 포함

## 4주차: Agentic RAG Evaluation

4주차 목표는 3주차 RAG의 실패 모드를 줄이는 것입니다.

3주차 RAG를 Agentic RAG로 리팩터링합니다. 검색 결과가 부족하거나 부적절할 때 LLM이 재검색, query rewrite, web search, reranking 중 하나 이상의 보정 행동을 하도록 구성합니다. 같은 질문에 대해 기초 RAG와 개선된 RAG의 차이를 비교해 보세요.

필수 요구사항:

- 3주차 RAG 재사용
- Agentic RAG, query rewrite, reranker 중 최소 1개 적용
- retrieval grader, hallucination checker, answer grader 중 최소 1개 적용
- 기초 RAG와 개선 RAG를 같은 질문 5개 이상으로 비교
- 각 질문에 대해 개선 여부와 이유 기록

심화:

- Cohere rerank 또는 cross-encoder reranker 적용
- CRAG, Self-RAG, Adaptive RAG 중 하나를 자기 도메인에 맞게 구현
- GraphRAG 실험: 엔티티-관계 추출 후 그래프 검색
- LangSmith trace 또는 evaluator 사용

제출 기준:

- `assignments/{github-id}/week4/` 아래에 구현 파일 제출
- PR에 비교 표 포함
- PR에 어떤 실패 모드를 줄이려고 했는지 설명 포함

## 5주차: Tool-Using Agent

5주차 목표는 RAG 시스템을 agent가 사용할 수 있는 하나의 도구로 감싸고, 다른 도구들과 함께 선택적으로 사용하게 만드는 것입니다.

4주차 RAG를 하나의 tool로 제공합니다. 여기에 웹 검색, 계산기, 코드 실행, 도메인 API, 파일 조회 등 도구 2개 이상을 추가합니다. Agent가 내부 지식 검색과 외부 도구 중 무엇을 쓸지 판단할 수 있도록 시스템 프롬프트와 tool description을 설계합니다.

필수 요구사항:

- 4주차 RAG를 tool로 래핑
- RAG tool 외 추가 tool 2개 이상 구현
- tool input schema 정의
- structured output으로 최종 응답 형식 강제
- 내부 RAG를 써야 하는 질문과 외부 도구를 써야 하는 질문을 각각 2개 이상 테스트
- agent가 어떤 도구를 선택했는지 확인 가능한 로그 또는 streaming 출력 포함

심화:

- FastMCP로 도구 1개를 MCP 서버로 분리 후 연결
- `ToolRuntime`으로 context 또는 store 접근
- tool 실패 시 fallback tool 선택
- 도구별 비용 또는 latency 기록

제출 기준:

- `assignments/{github-id}/week5/` 아래에 구현 파일 제출
- PR에 tool 목록과 각 tool의 역할 설명 포함
- PR에 agent가 도구를 적절히 선택한 사례와 실패 사례 포함

## 6주차: Supervisor Multi-Agent

6주차 목표는 5주차 단일 agent를 역할이 분리된 multi-agent system으로 확장하는 것입니다.

Supervisor agent를 두고, 도메인에 맞는 서브에이전트 2-3개를 구성합니다. 예를 들어 researcher, analyzer, writer처럼 역할을 나눌 수 있습니다. Handoff 패턴 또는 tool-calling supervisor 패턴 중 하나를 선택하고, 왜 그 패턴을 골랐는지 정리합니다.

필수 요구사항:

- supervisor agent 구성
- 서브에이전트 2-3개 구성
- handoff 또는 tool-calling supervisor 패턴 중 하나 선택
- 5주차 tool agent 또는 RAG tool 재사용
- 최종 데모 시나리오 1개 이상 구성
- 테스트 입력 5개 이상으로 성공/실패 정리
- 선택한 multi-agent 패턴의 장단점 설명

심화:

- 민감 작업에 HITL interrupt 추가
- guardrail 추가
- DeepAgents 스타일로 planning과 execution 분리
- LangSmith evaluator로 최종 결과 평가

제출 기준:

- `assignments/{github-id}/week6/` 아래에 구현 파일 제출
- PR에 최종 시스템 구조 설명 포함
- PR에 데모 시나리오와 실행 결과 포함
- 6주 동안 만든 시스템의 한계와 다음 개선 방향 포함

## 운영 가이드

- 기본 과제 예상 시간은 주당 4-6시간입니다.
- 심화 과제는 선택입니다. 필수 과제를 먼저 끝내고 여유가 있을 때 진행합니다.
- 매주 시작 30분은 지난 주 과제 데모 시간으로 사용합니다.
- 데모는 1인당 5분 내외로 짧게 진행합니다.
- 막히면 코드 일부와 에러 메시지를 함께 공유합니다.
- 6주차 마지막에는 각자 만든 도메인 특화 시스템을 데모합니다.
