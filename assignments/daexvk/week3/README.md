# Week 3 RAG Assignment

클래식 공연 예습 도메인의 원문 RAG 파이프라인입니다.

## 요구사항 반영

- Loader: `assignments/daexvk/data/raw/*.txt` 원문 로드
- Splitter: 2개 전략 비교
  - `recursive_character`
  - `token` whitespace token splitter
- Embedding: HuggingFace `sentence-transformers/all-MiniLM-L6-v2` 우선 사용
  - 로컬에 `sentence_transformers`가 없으면 같은 인터페이스의 `sklearn` TF-IDF fallback 사용
- Store: FAISS
- Retrieve: `similarity_search`
- 2-step RAG: `retrieve` 후 `generate_answer`
- 답변에는 근거 문서 파일명과 chunk 정보를 포함

## 실행

```bash
source /Users/nozerose/Documents/GitHub/rag-agent-study/.venv/bin/activate
python -m py_compile rag_pipeline.py
```

노트북은 `week3_mission.ipynb`입니다.
