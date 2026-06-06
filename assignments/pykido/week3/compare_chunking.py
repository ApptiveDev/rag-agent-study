import os

from dotenv import find_dotenv, load_dotenv

from rag import STRATEGIES
from rag.retriever import retrieve

load_dotenv(find_dotenv(), override=True)
os.environ["LANGSMITH_TRACING"] = "false"

COMPARE_QUERIES = [
    "답이 단조성을 가질 때 답 자체를 이분 탐색하는 최적화 문제",
    "연속 구간에서 모든 종류를 포함하는 가장 짧은 구간 찾기",
    "작업을 소요 시간이 짧은 것부터 처리해 평균 대기를 줄이는 스케줄링",
    "최소 비용으로 모든 노드를 연결하는 최소 신장 트리",
]


def compare(query: str, k: int = 3) -> None:
    print("=" * 90)
    print(f"QUERY: {query}")
    for strategy in STRATEGIES:
        print(f"\n[{strategy}]")
        for i, doc in enumerate(retrieve(query, strategy=strategy, k=k), start=1):
            preview = doc.page_content[:80].replace("\n", " ")
            print(f"  {i}. {doc.metadata['chunk_id']:<28} | {preview}")


if __name__ == "__main__":
    for query in COMPARE_QUERIES:
        compare(query)
        print()
