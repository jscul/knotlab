"""Tiny deterministic controls; no census, multiprocessing, or output files."""
import importlib.util
import json
from pathlib import Path
import time

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("reach_brute_controls", HERE / "brute_check.py")
B = importlib.util.module_from_spec(spec)
spec.loader.exec_module(B)


def run():
    start = time.perf_counter()
    positive = [(3, 1, [("K", (0, 1, 3)), ("SELF", (0, 1, 3))])]
    negative = [(3, 1, [("K", (0, 1, 2)), ("SELF", (0, 1, 2))])]
    assert B.brute(positive, 1)["least_size"] == 3
    assert B.brute(negative, 1)["status"] == "none up to 7"
    # Full truth-table comparison exercises prefix partitions, unused gaps,
    # all-free distinctions, and unsatisfiability independently of the DP.
    truth_cases = [([], 5), ([[1], [-1]], 3), ([[1, 4], [-1, -4], [2, -6]], 7)]
    for clauses, n in truth_cases:
        got, _ = B._enumerate_models(clauses, n, "cadical153", partition_variables=2)
        expected = {a for a in range(1 << n)
                    if all(any(bool((a >> (abs(lit) - 1)) & 1) == (lit > 0)
                               for lit in clause) for clause in clauses)}
        assert set(map(int, got)) == expected, (clauses, n)
        assert len(got) == len(expected), "duplicate full assignment"
    inlined = [(3, 2, [("K", (0, 1, 3))]),
               (3, 1, [(0, (0, 1, 3)), ("SELF", (0, 1, 3))])]
    body = B.flat_body(inlined)
    assert body.own == 3
    assert [(c.target, c.args) for c in body.calls] == [("K", (0, 1, 4)), (1, (0, 1, 3))]
    cnf, n, top, created = B.ray_cnf(inlined, 1)
    assert n == 9 and top == [0, 1, 2] and created == [[0, 1, 2, 3, 4, 5], [6, 7, 8]]
    assert B.brute(inlined, 1)["least_size"] == 3
    alternatives = [
        (3, 1, [("K", (0, 1, 3)), ("SELF", (0, 1, 3)), ("SELF", (1, 2, 3))]),
        (3, 0, [("SELF", (0, 1, 2))]),
        (3, 1, [(0, (0, 1, 3)), (1, (0, 1, 2)), (0, (1, 2, 3)), (1, (0, 2, 3))]),
    ]
    first, last = B.ray_metadata(alternatives), B.ray_metadata(alternatives, "last")
    assert first["S_index"] == last["S_index"] == 0
    assert (first["entry_call"], last["entry_call"]) == (0, 2)
    assert (first["ray_call"], last["ray_call"]) == (1, 2)
    bd_path = B._ROOT / "experiments/BOND-DEPTH-20261112-001A/BOND-DEPTH-20261112-001A-E001_spine_bonds/census.py"
    bd_spec = importlib.util.spec_from_file_location("reach_brute_bd_control", bd_path)
    bd = importlib.util.module_from_spec(bd_spec)
    bd_spec.loader.exec_module(bd)
    usual = B.LS.usual(positive)[0]
    assert B.ray_cnf(positive, 1) == bd.ray_cnf(usual, 1)
    assert B.brute(positive, 1)["least_size"] == bd.brute(usual, 1)
    return dict(status="passed", truth_tables=len(truth_cases),
                positive_and_negative=True, inlining_and_unused=True,
                last_ray_selection=True, BD_control=True,
                seconds=time.perf_counter() - start)


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True))
