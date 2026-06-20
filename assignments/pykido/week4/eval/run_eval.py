import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.dirname(_HERE))


def _fmt_retrieval(res: dict) -> str:
    lines = []
    metrics = ["recall@1", "recall@3", "recall@5", "precision@5", "mrr", "hit@1", "hit@3"]
    for hop in ("all", "single", "multi"):
        lines.append(f"\n[{hop}]")
        header = "  " + f"{'mode':9s} " + " ".join(f"{m:>11s}" for m in metrics)
        lines.append(header)
        for mode, by_hop in res.items():
            m = by_hop[hop]
            row = "  " + f"{mode:9s} " + " ".join(f"{m.get(k, 0):11.3f}" for k in metrics)
            lines.append(row)
    return "\n".join(lines)


def _fmt_answer(summary: dict) -> str:
    lines = []
    for hop in ("all", "single", "multi", "none"):
        lines.append(f"\n[{hop}]")
        lines.append(f"  {'system':9s} {'n':>3s} {'correctness':>12s} {'groundedness':>13s}")
        for sys_name, by_hop in summary.items():
            if hop not in by_hop:
                continue
            m = by_hop[hop]
            lines.append(
                f"  {sys_name:9s} {m['n']:>3d} {m['correctness']:>12.2f} {m['groundedness']:>13.2f}"
            )
    return "\n".join(lines)


def run_retrieval():
    from retrieval_eval import run_retrieval_eval

    print("=== Harness 1: retrieval_eval (vector / +hybrid / +rerank) ===")
    res = run_retrieval_eval()
    out = os.path.join(_HERE, "results_retrieval.json")
    json.dump(res, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(_fmt_retrieval(res))
    print(f"\nsaved -> {out}")
    return res


def run_answer():
    from answer_eval import run_answer_eval

    print("\n=== Harness 2: answer_eval (baseline vs agentic, LLM-as-Judge) ===")
    res = run_answer_eval()
    out = os.path.join(_HERE, "results_answer.json")
    json.dump(res, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(_fmt_answer(res["summary"]))
    print("\n--- baseline -> agentic 점수 변화 (문항별) ---")
    for r in res["records"]:
        b, a = r["baseline"], r["agentic"]
        print(
            f"  [{r['id']}|{r['hop']:6s}|{r['failure_mode']:14s}] "
            f"correct {b['correctness']}->{a['correctness']}  "
            f"ground {b['groundedness']}->{a['groundedness']}"
        )
    print(f"\nsaved -> {out}")
    return res


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "both"
    if which in ("both", "retrieval"):
        run_retrieval()
    if which in ("both", "answer"):
        run_answer()
