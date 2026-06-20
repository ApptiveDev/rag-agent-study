import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

WEEK4_DIR = Path(__file__).resolve().parent
RAG_DIR = WEEK4_DIR / "rag"
sys.path.insert(0, str(RAG_DIR))

from graph import run_agentic_rag  # noqa: E402
from qa import answer_question  # noqa: E402

COMPARE_QUERIES = [
    "Cursor가 왜 멍청해 보였는지 인과적으로 설명해줘",
    "X-Username 인증 문제와 surface-level fix의 관계를 설명해줘",
    "long polling으로 서버 다운된 사례를 원인과 해결 중심으로 정리해줘",
    "canonical mapping이나 fragmentation 문제가 뭐였는지 설명해줘",
    "외부 API 변경으로 장애가 발생한 사례를 원인과 해결 중심으로 정리해줘",
    "안드로이드 빌드 시 배포 에러가 발생한 사례를 정리해줘",
]

STRATEGY = "markdown"


def run_comparison(queries: list[str] | None = None) -> list[dict]:
    queries = queries or COMPARE_QUERIES
    results = []

    for question in queries:
        print(f"\n{'=' * 100}")
        print(f"COMPARING: {question}")
        print("=" * 100)

        baseline = answer_question(question=question, strategy=STRATEGY, k=4)
        agentic = run_agentic_rag(question=question, strategy=STRATEGY)

        row = {
            "question": question,
            "baseline_answer": baseline["answer"],
            "baseline_sources": [s["filename"] for s in baseline["sources"]],
            "agentic_answer": agentic["answer"],
            "agentic_sources": [s["filename"] for s in agentic["sources"]],
            "rewritten_question": agentic["rewritten_question"],
            "rewrite_count": agentic["rewrite_count"],
        }
        results.append(row)

        print("\n--- Baseline RAG ---")
        print(baseline["answer"][:500])
        print("Sources:", row["baseline_sources"])

        print("\n--- Agentic RAG ---")
        print(f"Rewritten: {row['rewritten_question']} (count={row['rewrite_count']})")
        print(agentic["answer"][:500])
        print("Sources:", row["agentic_sources"])

    return results


def print_summary_table(results: list[dict]) -> None:
    print("\n" + "=" * 120)
    print("COMPARISON SUMMARY (PR 표에 복사)")
    print("=" * 120)
    print(f"{'#':<3} {'질문':<40} {'baseline src':<20} {'agentic src':<20} {'rewrite':<5}")
    print("-" * 120)
    for i, row in enumerate(results, start=1):
        q = row["question"][:38] + ".." if len(row["question"]) > 40 else row["question"]
        b_src = ", ".join(row["baseline_sources"][:2]) or "-"
        a_src = ", ".join(row["agentic_sources"][:2]) or "-"
        print(
            f"{i:<3} {q:<40} {b_src:<20} {a_src:<20} {row['rewrite_count']:<5}"
        )


if __name__ == "__main__":
    results = run_comparison()
    print_summary_table(results)
