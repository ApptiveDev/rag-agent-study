def recall_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    if not relevant:
        return 0.0
    return len(set(retrieved[:k]) & relevant) / len(relevant)


def precision_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    topk = retrieved[:k]
    if not topk:
        return 0.0
    hits = sum(1 for src in topk if src in relevant)
    return hits / min(k, len(topk))


def reciprocal_rank(retrieved: list[str], relevant: set[str]) -> float:
    for rank, src in enumerate(retrieved, start=1):
        if src in relevant:
            return 1.0 / rank
    return 0.0


def hit_rate_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    return 1.0 if any(src in relevant for src in retrieved[:k]) else 0.0


def evaluate_query(retrieved: list[str], relevant: set[str], ks: tuple[int, ...]) -> dict:
    result: dict[str, float] = {"mrr": reciprocal_rank(retrieved, relevant)}
    for k in ks:
        result[f"recall@{k}"] = recall_at_k(retrieved, relevant, k)
        result[f"precision@{k}"] = precision_at_k(retrieved, relevant, k)
        result[f"hit@{k}"] = hit_rate_at_k(retrieved, relevant, k)
    return result


def mean_metrics(rows: list[dict]) -> dict:
    if not rows:
        return {}
    keys = rows[0].keys()
    return {key: sum(row[key] for row in rows) / len(rows) for key in keys}
