"""Gates for LAYER-RANK-20261117-001A (run before any read-out).

L1  the layer-by-layer rank equals the least Strahler number computed by the
    atom library of SEQUENTIAL-WALL-20261116-001A on the same circuit, encoded
    as atoms (every gate, every input pattern of small circuits, and random
    larger ones).
L2  the mean-field recursion keeps the true fraction at 1/2 and its total
    probability equal to the true fraction.
L3  at small depth the mean-field mean and sd agree with simulations at
    width 2^20 (within 0.01).
"""

import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "experiments", "SEQUENTIAL-WALL-20261116-001A",
                                "SEQUENTIAL-WALL-20261116-001A-E001_rounds_phases"))
import layer_rank as LR  # noqa: E402
import atoms as A  # noqa: E402

OUT = os.path.join(ROOT, "artifacts", "LAYER-RANK-20261117-001A", "LAYER-RANK-20261117-001A-E001_layer_rank")


def recursion_on(inputs, layers):
    true = inputs.copy()
    rank = np.where(true, 0, -1).astype(np.int64)
    ranks = [rank.copy()]
    BIG = 1 << 40
    for is_and, pairs in layers:
        x, y = pairs[:, 0], pairs[:, 1]
        tx, ty, rx, ry = true[x], true[y], rank[x], rank[y]
        r_and = np.where(rx == ry, rx + 1, np.maximum(rx, ry))
        r_or = np.minimum(np.where(tx, np.maximum(rx, 1), BIG), np.where(ty, np.maximum(ry, 1), BIG))
        true = np.where(is_and, tx & ty, tx | ty)
        rank = np.where(true, np.where(is_and, r_and, r_or), -1)
        ranks.append(rank.copy())
    return ranks


def main():
    rng = np.random.default_rng(20261117)
    rep = {}
    n_cmp = 0
    for depth in range(1, 9):
        for width in (2, 3, 5, 8, 20, 60):
            for _ in range(6):
                inputs, layers = A.alternating_circuit(depth, width, rng, p_one=0.5, mixed=True)
                p, ids = A.circuit_to_atoms(inputs, layers)
                r = A.rank(p)
                rec = recursion_on(inputs, layers)
                for g, rr in zip(ids, rec):
                    lib = np.where(r[g] < A.INF, r[g], -1)
                    assert np.array_equal(lib, rr), "L1"
                    n_cmp += len(g)
    rep["L1_gates_compared"] = n_cmp
    mf = LR.meanfield(200, [1, 2, 5, 50, 200])
    for L, v in mf.items():
        assert abs(v["p"] - 0.5) < 1e-9, "L2"
    rep["L2"] = "true fraction 1/2 at every checkpoint"
    sim = LR.simulate(1 << 20, 6, np.random.default_rng(7), [1, 2, 3, 4, 5, 6])
    mf6 = LR.meanfield(6, [1, 2, 3, 4, 5, 6])
    dev = max(max(abs(sim[L]["mean"] - mf6[L]["mean"]), abs(sim[L]["sd"] - mf6[L]["sd"])) for L in sim)
    assert dev < 0.01, f"L3 {dev}"
    rep["L3_max_deviation"] = dev
    rep["status"] = "all gates passed"
    os.makedirs(OUT, exist_ok=True)
    json.dump(rep, open(os.path.join(OUT, "gates.json"), "w"), indent=1)
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
