from metrics import hit_rate_at_k, precision_at_k, recall_at_k, reciprocal_rank


def test_recall_collapses_topk_to_source_file_set():
    retrieved = ["A", "A", "B", "C"]
    relevant = {"A", "B"}
    assert recall_at_k(retrieved, relevant, 3) == 1.0
    assert recall_at_k(retrieved, relevant, 1) == 0.5


def test_recall_multihop_partial():
    assert recall_at_k(["A", "X", "Y"], {"A", "B"}, 3) == 0.5


def test_precision_counts_chunks_not_fileset():
    retrieved = ["A", "A", "B", "B", "C", "D", "E", "F", "G", "H"]
    assert precision_at_k(retrieved, {"A", "B"}, 10) == 0.4


def test_precision_at_1():
    assert precision_at_k(["A", "B"], {"A"}, 1) == 1.0
    assert precision_at_k(["C", "A"], {"A"}, 1) == 0.0


def test_precision_denominator_min_k_len():
    assert precision_at_k(["A"], {"A"}, 5) == 1.0


def test_reciprocal_rank():
    assert reciprocal_rank(["X", "A", "B"], {"A"}) == 0.5
    assert reciprocal_rank(["A"], {"A"}) == 1.0
    assert reciprocal_rank(["X", "Y"], {"A"}) == 0.0


def test_hit_rate():
    assert hit_rate_at_k(["X", "A"], {"A"}, 2) == 1.0
    assert hit_rate_at_k(["X", "A"], {"A"}, 1) == 0.0
    assert hit_rate_at_k(["X", "Y"], {"A"}, 5) == 0.0


def test_empty_retrieved():
    assert recall_at_k([], {"A"}, 5) == 0.0
    assert precision_at_k([], {"A"}, 5) == 0.0
    assert reciprocal_rank([], {"A"}) == 0.0
    assert hit_rate_at_k([], {"A"}, 5) == 0.0


if __name__ == "__main__":
    import sys

    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {fn.__name__}: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    sys.exit(1 if failed else 0)
