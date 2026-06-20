import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.dirname(_HERE))

import graph_agentic
import graph_baseline
from judge import judge_answer

DATASET = os.path.join(_HERE, "dataset.json")

SYSTEMS = {
    "baseline": graph_baseline.graph,
    "agentic": graph_agentic.graph,
}


def load_dataset(path: str = DATASET) -> list[dict]:
    return json.load(open(path, encoding="utf-8"))["items"]


def _run_graph(graph, item: dict) -> dict:
    state = graph.invoke({"question": item["question"], "strategy": "markdown"})
    return {
        "answer": (state.get("final_answer") or {}).get("answer", ""),
        "context": state.get("context", ""),
        "sources": (state.get("final_answer") or {}).get("sources", []),
    }


def run_answer_eval(limit: int | None = None) -> dict:
    items = load_dataset()
    if limit:
        items = items[:limit]
    records: list[dict] = []
    for it in items:
        rec = {"id": it["id"], "hop": it["hop"], "failure_mode": it["failure_mode"]}
        for sys_name, graph in SYSTEMS.items():
            run = _run_graph(graph, it)
            score = judge_answer(
                it["question"], it["reference_answer"], run["answer"], run["context"]
            )
            rec[sys_name] = {
                "correctness": score.correctness,
                "groundedness": score.groundedness,
                "reason": score.reason,
                "answer": run["answer"],
                "sources": run["sources"],
            }
        records.append(rec)
    return {"records": records, "summary": _summarize(records)}


def _summarize(records: list[dict]) -> dict:
    groups = {"all": records}
    for hop in ("single", "multi", "none"):
        groups[hop] = [r for r in records if r["hop"] == hop]
    out: dict[str, dict] = {}
    for sys_name in SYSTEMS:
        out[sys_name] = {}
        for gname, rows in groups.items():
            if not rows:
                continue
            n = len(rows)
            out[sys_name][gname] = {
                "n": n,
                "correctness": round(sum(r[sys_name]["correctness"] for r in rows) / n, 3),
                "groundedness": round(sum(r[sys_name]["groundedness"] for r in rows) / n, 3),
            }
    return out


def to_dataframe(summary: dict, hop: str = "all"):
    import pandas as pd

    rows = {}
    for sys_name, by_hop in summary.items():
        if hop in by_hop:
            rows[sys_name] = by_hop[hop]
    return pd.DataFrame(rows).T


if __name__ == "__main__":
    res = run_answer_eval(limit=3)
    print(json.dumps(res["summary"], ensure_ascii=False, indent=2))
