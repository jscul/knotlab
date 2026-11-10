"""Stress test for TREE-XOR-20261110-001, one size past the tickets' checks, with their own code:
A: Lemma 1 on K_3 (36 points; checked exhaustively on K_2): complete parity decision trees under two strategies, every leaf's clause
falsified on its leaf (exact, by linear algebra), and the leaves partitioning F2^36 (their sizes 2^(36 - codim) summing to 2^36, exact),
which with the first gives the identity sum_leaves 1_V J_C = 1 everywhere;
B: the size-degree bound on random unsatisfiable 3-CNFs on 10 variables (checked on 8).

    .venv/bin/python3 -B stress_test.py    writes stress_test.json beside it
"""
import importlib.util
import json
import math
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


A = load("check_tx_a", ROOT / "proofs/TREE-XOR-20261110-001A/TREE-XOR-20261110-001A-P001_parity_trees_need_polynomial_depth/check.py")
B = load("check_tx_b", ROOT / "proofs/TREE-XOR-20261110-001B/TREE-XOR-20261110-001B-P001_size_from_pc_degree/check.py")

if __name__ == "__main__":
    t0 = time.time()
    out = {}
    cls, n = A.clauses(3)
    rng = random.Random(3)
    for name, strat in (("line by line", A.line_by_line), ("corner parities first", A.corner_pairs)):
        leaves = []
        A.build(A.Affine(), cls, n, strat, random.Random(7), 0, leaves)
        ok_leaf = all(all(V.fixed(p) == b for p, b in cls[c].items()) for V, c, d in leaves)
        measure = sum(1 << (n - len(V.rows)) for V, c, d in leaves)
        bad = 0 if measure == 1 << n else 1
        out["A: K_3, " + name] = {"leaves": len(leaves), "depth": max(d for _, _, d in leaves), "clause falsified on every leaf": ok_leaf,
                                  "leaves partition the space": bad == 0, "pass": ok_leaf and bad == 0}
    B.NV = 10
    rng = random.Random(20261111)
    rows, ok = 0, True
    while rows < 6:
        cl = [tuple((v, rng.randrange(2)) for v in rng.sample(range(10), 3)) for _ in range(rng.randint(80, 130))]
        if B.satisfiable(cl):
            continue
        D = B.pc_degree([B.falsifier(c) for c in cl], 6)
        s = B.tree_size(cl, rng, "variables")
        ok &= D is not None and D <= math.log2(s) + 3
        rows += 1
    out["B: random 3-CNFs on 10 variables"] = {"formulas": rows, "pass": ok}
    out["all pass"] = all(v["pass"] for v in out.values() if isinstance(v, dict))
    out["seconds"] = round(time.time() - t0, 1)
    (HERE / "stress_test.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))
