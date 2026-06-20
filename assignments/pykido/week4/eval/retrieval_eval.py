import json
import os
import sys

from dotenv import find_dotenv, load_dotenv

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.dirname(_HERE))

load_dotenv(find_dotenv(), override=True)
os.environ["LANGSMITH_TRACING"] = "false"

from metrics import evaluate_query, mean_metrics

from rag.retriever import retrieve

DATASET = os.path.join(_HERE, "dataset.json")
KS = (1, 3, 5, 10)
TOP_K = 10
FIRST_STAGE_N = 50

MODES = {
    "vector": {"mode": "vector"},
    "+hybrid": {"mode": "hybrid"},
    "+rerank": {"mode": "rerank", "first_stage_n": FIRST_STAGE_N},
}


def load_dataset(path: str = DATASET) -> list[dict]:
    return json.load(open(path, encoding="utf-8"))["items"]


def retrieved_sources(query: str, mode_kwargs: dict, k: int) -> list[str]:
    return [doc.metadata.get("source") for doc in retrieve(query, k=k, **mode_kwargs)]


def run_retrieval_eval(ks: tuple[int, ...] = KS, top_k: int = TOP_K) -> dict:
    items = [it for it in load_dataset() if it.get("answerable", True) and it["relevant"]]
    result: dict[str, dict] = {}
    for mode_name, mode_kwargs in MODES.items():
        per_query = []
        for it in items:
            sources = retrieved_sources(it["question"], mode_kwargs, top_k)
            row = evaluate_query(sources, set(it["relevant"]), ks)
            row["_hop"] = it["hop"]
            per_query.append(row)
        result[mode_name] = _aggregate_by_hop(per_query)
    return result


def _aggregate_by_hop(per_query: list[dict]) -> dict:
    groups = {"all": per_query}
    for hop in ("single", "multi"):
        groups[hop] = [r for r in per_query if r["_hop"] == hop]
    out = {}
    for name, rows in groups.items():
        clean = [{k: v for k, v in r.items() if k != "_hop"} for r in rows]
        out[name] = {"n": len(clean), **mean_metrics(clean)}
    return out


def to_dataframe(result: dict, hop: str = "all"):
    import pandas as pd

    rows = {}
    for mode_name, by_hop in result.items():
        rows[mode_name] = {k: round(v, 3) for k, v in by_hop[hop].items() if k != "n"}
    return pd.DataFrame(rows).T


if __name__ == "__main__":
    print(json.dumps(run_retrieval_eval(), ensure_ascii=False, indent=2))
