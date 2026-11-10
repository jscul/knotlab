"""KERNEL-FRAC-20261110-001B-E001: conjecture C, K_k = I_k ∩ L_k, on small instances (exploratory; see contract.json).

    .venv/bin/python3 -B run.py    writes artifacts/KERNEL-FRAC-20261110-001B/KERNEL-FRAC-20261110-001B-E001_conjecture_c/run/result.json

I_k: the span of kappa_{a,j} * M over multilinear monomials M in the pigeon and hole bits of degree <= k - 1 (multilinearized), as
vectors over the multilinear monomials of degree <= k. dim(I_k ∩ L_k) = dim I_k - dim(projection of I_k onto the monomials that are not
row-linear). dim K_k is HOLE-SEP-20261110-001B-E001's computation (its run.py, imported), rerun here for every entry."""
import importlib.util
import itertools
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
HX = ROOT / "experiments/HOLE-SEP-20261110-001B/HOLE-SEP-20261110-001B-E001_decoder_kernel"
spec = importlib.util.spec_from_file_location("hole_sep_run", HX / "run.py")
R = importlib.util.module_from_spec(spec)
sys.modules["hole_sep_run"] = R
spec.loader.exec_module(R)
OUT = ROOT / "artifacts" / "KERNEL-FRAC-20261110-001B" / "KERNEL-FRAC-20261110-001B-E001_conjecture_c" / "run"
ROSTER = [(4, 2), (8, 2), (16, 2), (32, 2), (4, 3), (8, 3), (4, 4)]
PREDICTED = {(4, 2): 173, (8, 2): 839, (16, 2): 3423, (32, 2): 12287, (4, 3): 1389, (8, 3): 20378}


def bits(n):
    l = n.bit_length() - 1
    m = n + 1
    lg = (m - 1).bit_length()
    f = [("f", x, t) for x in range(m) for t in range(l)]
    g = [("g", h, j) for h in range(n) for j in range(lg)]
    return l, m, lg, f + g


def kappas(n):
    l, m, lg, _ = bits(n)
    out = []
    for j in range(lg):
        for a in [None] + list(range(l)):
            p = set()
            for h in range(n):
                if a is None or (h >> a) & 1:
                    p ^= {frozenset({("g", h, j)})}
            for x in range(m):
                if (x >> j) & 1:
                    p ^= {frozenset() if a is None else frozenset({("f", x, a)})}
            out.append(p)
    return out


def row_linear(mono):
    rows = [(k, r) for k, r, _ in mono]
    return len(set(rows)) == len(rows)


def ideal_dims(n, k):
    l, m, lg, allbits = bits(n)
    ks = kappas(n)
    idx = {}
    rl_basis, nrl_basis = {}, {}
    full_basis = {}
    rank_full = rank_nrl = 0
    for d in range(k):
        for M in itertools.combinations(allbits, d):
            Ms = frozenset(M)
            for kap in ks:
                prod = set()
                for mono in kap:
                    prod ^= {mono | Ms}
                v_full = 0
                v_nrl = 0
                for mono in prod:
                    i = idx.setdefault(mono, len(idx))
                    v_full ^= 1 << i
                    if not row_linear(mono):
                        v_nrl ^= 1 << i
                rank_full += R.insert(full_basis, v_full)
                rank_nrl += R.insert(nrl_basis, v_nrl)
    return rank_full, rank_nrl, rank_full - rank_nrl


def main():
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    log = open(OUT / "progress.txt", "w")
    rows = []
    for n, k in ROSTER:
        dI, dN, dIL = ideal_dims(n, k)
        kd = R.kernel_dim(n, k)[0]
        row = {"n": n, "k": k, "dim L_k": kd["dim L_k"], "dim K_k": kd["dim K_k"], "dim I_k": dI, "dim of its non-row-linear part": dN,
               "dim I_k ∩ L_k": dIL, "predicted": PREDICTED.get((n, k)), "C holds": dIL == kd["dim K_k"],
               "seconds": round(time.time() - t0, 1)}
        rows.append(row)
        print(json.dumps(row), file=log, flush=True)
    c = all(r["C holds"] for r in rows)
    pred = all(r["predicted"] is None or r["dim I_k ∩ L_k"] == r["predicted"] for r in rows)
    k4 = [r for r in rows if (r["n"], r["k"]) == (4, 4)][0]
    result = {"experiment": "KERNEL-FRAC-20261110-001B-E001", "readings": rows, "conjecture C at every entry": c,
              "predicted dimensions met": pred,
              "(4, 4) within the expected 5,700 to 5,806": 5700 <= k4["dim K_k"] <= 5806,
              "stop (c): a kernel element outside I_k ∩ L_k": not c, "seconds": round(time.time() - t0, 1)}
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "readings"}, indent=1))
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
