# RAG Agent Study

LangGraph, RAG, Agent를 6주 동안 실습 중심으로 학습하는 스터디 레포입니다.

이 스터디의 목표는 노트북을 읽고 끝내는 것이 아니라, 각자 고른 도메인에 LangGraph 기반 LLM 시스템을 6주 동안 누적해서 키워가는 것입니다. 1-2주차에는 LangGraph의 상태, 그래프, 메모리, 분기 같은 실행 모델을 익히고, 3-4주차에는 도메인 문서를 이용한 RAG와 평가 루프를 다룹니다. 5-6주차에는 RAG를 도구로 쓰는 agent와 supervisor multi-agent 구조까지 확장합니다.

## 진행 방식

- 스터디 시작 전에 각자 6주 동안 다룰 도메인 1개를 고릅니다.
- 매주 지정된 노트북을 학습하고, 같은 도메인 시스템을 한 단계씩 확장합니다.
- 과제는 개인 브랜치에서 작업한 뒤 Pull Request로 제출합니다.
- 브랜치 이름은 `{깃헙아이디}/{과제명}` 형식을 사용합니다.
- 제출물은 `assignments/{깃헙아이디}/week{n}/` 아래에 둡니다.
- PR에는 구현 내용, 실행 방법, 확인한 결과, 어려웠던 점을 적습니다.
- 다른 사람의 PR을 읽고 질문하거나 개선 의견을 남기는 것도 스터디의 일부입니다.

브랜치 예시:

```bash
git checkout -b your-github-id/week1-react-graph
```

제출 위치 예시:

```text
assignments/your-github-id/week1/
```

## 시작하기

이 레포는 Python 3.12와 uv를 기준으로 구성했습니다.

```bash
uv python pin 3.12
uv sync
cp .env.example .env
uv run jupyter lab
```

`.env`에는 실습에 필요한 API 키를 설정합니다. RAG와 Agent 실습 일부는 `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `TAVILY_API_KEY`, `LANGSMITH_API_KEY`가 필요합니다.

RAG 노트북은 `data/`, `rag/` 상대 경로를 사용합니다. 경로 문제가 생기면 해당 주차 폴더에서 `uv run --project .. jupyter lab`로 실행하세요.

## 주차별 학습 내용

- [1주차: LangGraph 기초 문법](./week1-langgraph-basics)  
  모델과 메시지, `StateGraph`, State/Reducer, 챗봇 그래프, `ToolNode`

- [2주차: LangGraph 심화 문법](./week2-langgraph-advanced)  
  Graph API, checkpointer memory, streaming, human-in-the-loop, branching, subgraph

- [3주차: RAG 기초](./week3-rag-basics)  
  Retrieval, vector store, naive RAG, groundedness check, web search, query rewrite

- [4주차: RAG 심화 및 평가](./week4-rag-advanced-evaluation)  
  Agentic RAG, CRAG, Self-RAG, Adaptive RAG, hallucination/answer grading, GraphRAG 선택 실습

- [5주차: Agent 기초](./week5-agent-basics)  
  `create_agent`, tool schema, structured output, streaming, runtime, context engineering

- [6주차: Agent 심화 및 평가](./week6-agent-advanced-evaluation)  
  middleware, HITL, guardrail, supervisor, multi-agent, plan-and-execute, SQL agent evaluation

과제의 상세 요구사항은 [ASSIGNMENT.md](./ASSIGNMENT.md)에 정리되어 있습니다.

## 과제 제출 규칙

각 주차 과제는 다음 흐름으로 제출합니다.

1. 최신 `main` 기준으로 브랜치를 만듭니다.
2. 브랜치 이름은 `{깃헙아이디}/{과제명}`으로 작성합니다.
3. 제출물은 `assignments/{깃헙아이디}/week{n}/` 아래에 추가합니다.
4. PR을 열고 실행 방법과 결과를 적습니다.
5. 리뷰를 반영한 뒤 merge합니다.

브랜치 이름 예시:

- [1주차 과제](./ASSIGNMENT.md#1주차-stategraph-react-loop): `your-id/week1-react-graph`
- [2주차 과제](./ASSIGNMENT.md#2주차-state-memory-control): `your-id/week2-state-memory`
- [3주차 과제](./ASSIGNMENT.md#3주차-domain-rag): `your-id/week3-domain-rag`
- [4주차 과제](./ASSIGNMENT.md#4주차-agentic-rag-evaluation): `your-id/week4-agentic-rag`
- [5주차 과제](./ASSIGNMENT.md#5주차-tool-using-agent): `your-id/week5-tool-agent`
- [6주차 과제](./ASSIGNMENT.md#6주차-supervisor-multi-agent): `your-id/week6-supervisor-agent`

## 1주차: LangGraph 기초 문법

목표는 LangGraph의 가장 작은 실행 단위를 이해하는 것입니다. 모델 호출, 메시지 객체, State, reducer, node, edge를 익히고 마지막에는 도구를 호출하는 그래프를 만듭니다.

1. [LangGraph Models](./week1-langgraph-basics/01-LangGraph-Models.ipynb): LangChain/LangGraph에서 모델 초기화, invoke/stream, 응답 메타데이터
2. [LangGraph Messages](./week1-langgraph-basics/02-LangGraph-Messages.ipynb): `HumanMessage`, `AIMessage`, `SystemMessage`, `ToolMessage` 구조
3. [Building Graphs](./week1-langgraph-basics/03-LangGraph-Building-Graphs.ipynb): `StateGraph`, node, edge, reducer, `MessagesState` 기본 문법
4. [LangGraph State](./week1-langgraph-basics/04-LangGraph-State.ipynb): `TypedDict`, `Annotated`, reducer를 이용한 State 설계
5. [ChatBot](./week1-langgraph-basics/05-LangGraph-ChatBot.ipynb): 가장 작은 챗봇 그래프를 단계별로 구성하고 실행
6. [ToolNode](./week1-langgraph-basics/06-LangGraph-ToolNode.ipynb): 도구 호출 메시지와 `ToolNode`를 그래프에 연결하는 방식

과제 요약: LangChain의 `create_agent` 같은 고수준 agent helper 없이 `StateGraph`로 도메인용 ReAct 루프를 직접 구현합니다. 상세 요구사항은 [1주차 과제](./ASSIGNMENT.md#1주차-stategraph-react-loop)를 확인하세요.

## 2주차: LangGraph 심화 문법

목표는 그래프가 한 번 실행되고 끝나는 함수가 아니라, 상태를 저장하고 중단/재개하며 분기할 수 있는 workflow라는 점을 익히는 것입니다.

1. [Graph API](./week2-langgraph-advanced/01-LangGraph-Graph-API.ipynb): State schema, reducer, config, checkpoint, interrupt 등 Graph API 전반
2. [Add Memory](./week2-langgraph-advanced/02-LangGraph-Add-Memory.ipynb): `InMemorySaver`, `thread_id`, 상태 스냅샷과 히스토리
3. [Streaming Outputs](./week2-langgraph-advanced/03-LangGraph-Streaming-Outputs.ipynb): `stream_mode`, `output_keys`, 단계별 실행 출력
4. [Human In The Loop](./week2-langgraph-advanced/04-LangGraph-Human-In-the-Loop.ipynb): interrupt, resume, state history 기반 사람 개입 패턴
5. [Branching](./week2-langgraph-advanced/05-LangGraph-Branching.ipynb): fan-out/fan-in, 병렬 노드, 조건부 경로 설계
6. [Subgraph](./week2-langgraph-advanced/06-LangGraph-Subgraph.ipynb): 부모 그래프와 하위 그래프 조합
7. [Subgraph Transform State](./week2-langgraph-advanced/07-LangGraph-Subgraph-Transform-State.ipynb): subgraph 입출력 State 변환 패턴

과제 요약: 1주차 그래프에 `thread_id` 기반 short-term memory와 실행 제어를 추가합니다. 상세 요구사항은 [2주차 과제](./ASSIGNMENT.md#2주차-state-memory-control)를 확인하세요.

## 3주차: RAG 기초

목표는 문서를 잘라 embedding하고, retriever로 찾은 근거를 LLM 응답에 연결하는 기본 RAG 흐름을 직접 실행하는 것입니다.

1. [Retrieval](./week3-rag-basics/01-LangGraph-Retrieval.ipynb): 문서 분할, embedding, FAISS, retriever, 2-step RAG와 Agentic RAG 개념
2. [RAG Building Graphs](./week3-rag-basics/02-LangGraph-RAG-Building-Graphs.ipynb): RAG workflow에 맞는 State와 노드 설계
3. [Naive RAG](./week3-rag-basics/03-LangGraph-Naive-RAG.ipynb): PDF 기반 retrieval chain과 기본 RAG 그래프
4. [Groundedness Check](./week3-rag-basics/04-LangGraph-Groundedness-Check.ipynb): 생성 답변의 근거성 검사와 재귀 상태 처리
5. [Add Web Search](./week3-rag-basics/05-LangGraph-Add-Web-Search.ipynb): 검색 실패 시 Tavily web search를 결합하는 패턴
6. [Add Query Rewrite](./week3-rag-basics/06-LangGraph-Add-Query-Rewrite.ipynb): 검색 품질 개선을 위한 query rewrite 노드

과제 요약: 자기 도메인 문서 또는 코드 파일로 2-step RAG를 만들고 청킹 전략을 비교합니다. 상세 요구사항은 [3주차 과제](./ASSIGNMENT.md#3주차-domain-rag)를 확인하세요.

## 4주차: RAG 심화 및 평가

목표는 retrieval 실패, hallucination, 답변 부적합 같은 RAG의 실패 모드를 그래프 안에서 감지하고 보정하는 것입니다.

1. [Agentic RAG](./week4-rag-advanced-evaluation/01-LangGraph-Agentic-RAG.ipynb): retriever tool, tool routing, document grader를 결합한 RAG agent
2. [CRAG](./week4-rag-advanced-evaluation/02-LangGraph-CRAG.ipynb): retrieval grader, corrective web search, query rewrite
3. [Self-RAG](./week4-rag-advanced-evaluation/03-LangGraph-Self-RAG.ipynb): retrieval grading, hallucination grading, answer grading loop
4. [Adaptive RAG](./week4-rag-advanced-evaluation/04-LangGraph-Adaptive-RAG.ipynb): query routing, document grading, hallucination/answer 평가를 통합한 adaptive workflow
5. [Text2Cypher Neo4j](./week4-rag-advanced-evaluation/05-LangGraph-Text2Cypher-Neo4j.ipynb): GraphRAG/Text2Cypher 선택 실습. Neo4j 환경이 필요합니다.

과제 요약: 3주차 RAG를 Agentic RAG 또는 reranker 기반 구조로 개선하고 자기 도메인 쿼리로 비교합니다. 상세 요구사항은 [4주차 과제](./ASSIGNMENT.md#4주차-agentic-rag-evaluation)를 확인하세요.

## 5주차: Agent 기초

목표는 agent의 구성 요소를 익히고, tool schema와 structured output으로 예측 가능한 agent 인터페이스를 만드는 것입니다.

1. [Agents](./week5-agent-basics/01-LangGraph-Agents.ipynb): `create_agent`, 모델 선택, 정적/동적 시스템 프롬프트
2. [Tools](./week5-agent-basics/02-LangGraph-Tools.ipynb): tool 정의, Pydantic schema, `ToolRuntime`, store/context 접근
3. [Structured Output](./week5-agent-basics/03-LangGraph-Structured-Output.ipynb): provider strategy, tool calling strategy, Pydantic/TypedDict 출력
4. [Streaming](./week5-agent-basics/04-LangGraph-Streaming.ipynb): agent updates, token streaming, custom stream writer
5. [Runtime](./week5-agent-basics/05-LangGraph-Runtime.ipynb): runtime context, store, stream writer를 tool/middleware에서 사용하는 방식
6. [Context Engineering](./week5-agent-basics/06-LangGraph-Context-Engineering.ipynb): model/tool/lifecycle context와 동적 prompt, tool filtering

과제 요약: 4주차 RAG를 하나의 도구로 감싸고, 추가 도구를 붙여 단일 ReAct agent를 구성합니다. 상세 요구사항은 [5주차 과제](./ASSIGNMENT.md#5주차-tool-using-agent)를 확인하세요.

## 6주차: Agent 심화 및 평가

목표는 단일 agent를 역할 분리된 multi-agent workflow로 확장하는 것입니다. supervisor, handoff, guardrail, HITL 같은 패턴을 상황에 맞게 선택합니다.

1. [Middleware](./week6-agent-advanced-evaluation/01-LangGraph-Middleware.ipynb): summarization, call limit, fallback, PII, retry, custom middleware
2. [Human In The Loop](./week6-agent-advanced-evaluation/02-LangGraph-Human-In-The-Loop.ipynb): `HumanInTheLoopMiddleware`, approve/edit/reject 흐름
3. [Guardrail](./week6-agent-advanced-evaluation/03-LangGraph-Guardrail.ipynb): deterministic/model-based guardrail, PII 보호, custom guardrail
4. [Supervisor](./week6-agent-advanced-evaluation/04-LangGraph-Supervisor.ipynb): supervisor pattern, 역할 분리, subagent routing
5. [Multi-Agent Supervisor](./week6-agent-advanced-evaluation/05-LangGraph-Multi-Agent-Supervisor.ipynb): 여러 agent를 supervisor가 조율하는 구조
6. [Plan and Execute](./week6-agent-advanced-evaluation/06-LangGraph-Plan-and-Execute.ipynb): planning, execution, replanning을 분리한 agent workflow
7. [SQL Agent](./week6-agent-advanced-evaluation/07-LangGraph-SQL-Agent.ipynb): SQL tool graph와 LangSmith evaluator 기반 agent 평가

과제 요약: 5주차 단일 agent를 Supervisor multi-agent 시스템으로 확장하고 최종 데모를 준비합니다. 상세 요구사항은 [6주차 과제](./ASSIGNMENT.md#6주차-supervisor-multi-agent)를 확인하세요.

## 보조 파일

- `week3-rag-basics/rag`, `week3-rag-basics/data`: 3주차 RAG 노트북 실행용 PDF loader/helper와 실습 PDF입니다.
- `week4-rag-advanced-evaluation/rag`, `week4-rag-advanced-evaluation/data`: 4주차 RAG 심화 노트북 실행용 helper와 PDF입니다.
- `week6-agent-advanced-evaluation/Chinook.db`: SQL Agent 실습용 SQLite 데이터베이스입니다.
- 각 주차의 `assets/`: 노트북 내 이미지 링크가 깨지지 않도록 관련 이미지를 함께 둡니다.
