"""Checks for TREE-XOR-20261110-001A. Lemma 1 (a parity decision tree of depth d gives an F2 Nullstellensatz refutation of degree d + 3)
is checked on the sphere K_2 (16 points, 32 clauses) by building complete parity decision trees under four query strategies and
verifying the leaf identity sum_leaves 1_V * J_C = 1 under all 2^16 assignments. The sizes of the reduction chain (COUNT-TFNP-20261107-001A,
FLAT-STATES-20261107-001B) are tabulated.

    python3 -B check.py          verify against result.json
    python3 -B check.py --write  write result.json from a fresh run
"""
import hashlib
import importlib.util
import json
import random
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SA = next((ROOT / "proofs/COUNT-NOTE-20261107-001B").iterdir())
spec = importlib.util.spec_from_file_location("sa_lib", SA / "sa_lib.py")
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)
TUBE = ROOT / "proofs/COUNT-TFNP-20261107-001A/COUNT-TFNP-20261107-001A-P001_one_sided_grid_sperner_is_ppads_hard"
sys.path.insert(0, str(TUBE))
spec = importlib.util.spec_from_file_location("tube_lib", TUBE / "tube_lib.py")
TB = importlib.util.module_from_spec(spec)
sys.modules["tube_lib"] = TB
spec.loader.exec_module(TB)
OUT = {}
T0 = time.time()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print(("PASS " if ok else "FAIL ") + name, "(%.0fs)" % (time.time() - T0), flush=True)
    if not ok:
        print(json.dumps(info, indent=1, default=str)[:3000])


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def clauses(k):
    """falsifying conjunctions of NAE(K_k): {point: value} for every line's two clauses"""
    lines, signs, n = S.sphere(k)
    out = []
    for L, s in zip(lines, signs):
        out.append({p: sp for p, sp in zip(L, s)})          # every literal 0
        out.append({p: 1 - sp for p, sp in zip(L, s)})      # every literal 1
    return out, n


class Affine:
    """an affine subspace of F2^n as reduced rows (mask, value) with distinct pivots"""
    def __init__(self, rows=()):
        self.rows = list(rows)

    def reduce(self, mask, val):
        for m, v in self.rows:
            if mask >> (m.bit_length() - 1) & 1:
                mask ^= m
                val ^= v
        return mask, val

    def add(self, mask, val):
        mask, val = self.reduce(mask, val)
        if mask == 0:
            return None if val else self
        rows = []
        piv = mask.bit_length() - 1
        for m, v in self.rows:
            if m >> piv & 1:
                m, v = m ^ mask, v ^ val
            rows.append((m, v))
        return Affine(rows + [(mask, val)])

    def fixed(self, p):
        m, v = self.reduce(1 << p, 0)
        return None if m else v


def forced_clause(V, cls):
    for i, c in enumerate(cls):
        if all(V.fixed(p) == b for p, b in c.items()):
            return i
    return None


def build(V, cls, n, strategy, rng, depth, leaves):
    c = forced_clause(V, cls)
    if c is not None:
        leaves.append((V, c, depth))
        return
    while True:
        mask = strategy(V, cls, n, rng)
        m, _ = V.reduce(mask, 0)
        if m:
            break
    for b in (0, 1):
        W = V.add(mask, b)
        if W is not None:
            build(W, cls, n, strategy, rng, depth + 1, leaves)


def single_in_order(V, cls, n, rng):
    for p in range(n):
        if V.fixed(p) is None:
            return 1 << p


def line_by_line(V, cls, n, rng):
    for c in cls:
        for p in c:
            if V.fixed(p) is None:
                return 1 << p


def corner_pairs(V, cls, n, rng):
    for c in cls:
        ps = list(c)
        for a, b in ((ps[0], ps[1]), (ps[1], ps[2])):
            m, _ = V.reduce((1 << a) | (1 << b), 0)
            if m:
                return (1 << a) | (1 << b)
        for p in ps:
            if V.fixed(p) is None:
                return 1 << p


def random_parities(V, cls, n, rng):
    if rng.random() < 0.5:
        free = [p for p in range(n) if V.fixed(p) is None]
        return 1 << rng.choice(free)
    return rng.randrange(1, 1 << n)


def main():
    write = "--write" in sys.argv
    man = json.loads((HERE / "manifest.json").read_text())
    bound = man.get("parent_bindings", {})
    check("0_dependencies_bound", bool(bound) and all(sha(ROOT / p) == h for p, h in bound.items()), bound)

    cls, n = clauses(2)
    xs = np.arange(1 << n, dtype=np.int64)
    bits = [((xs >> p) & 1).astype(np.uint8) for p in range(n)]
    info, ok = {}, True
    for name, strat in (("single variables in order", single_in_order), ("line by line", line_by_line),
                        ("corner parities first", corner_pairs), ("random parities", random_parities)):
        leaves = []
        build(Affine(), cls, n, strat, random.Random(7), 0, leaves)
        total = np.zeros(1 << n, dtype=np.uint8)
        clause_false_on_leaf = True
        for V, c, d in leaves:
            ind = np.ones(1 << n, dtype=np.uint8)
            for m, v in V.rows:
                par = np.zeros(1 << n, dtype=np.uint8)
                x = m
                while x:
                    low = x & -x
                    par ^= bits[low.bit_length() - 1]
                    x ^= low
                ind &= (par == v).astype(np.uint8)
            J = np.ones(1 << n, dtype=np.uint8)
            for p, b in cls[c].items():
                J &= (bits[p] == b).astype(np.uint8)
            clause_false_on_leaf &= bool(np.all(J[ind == 1] == 1))
            total ^= ind & J
        identity = bool(np.all(total == 1))
        partition = True
        info[name] = {"leaves": len(leaves), "depth": max(d for _, _, d in leaves), "clause falsified on every leaf": clause_false_on_leaf,
                      "sum of 1_V J_C is 1 everywhere (F2)": identity}
        ok &= identity and clause_false_on_leaf
    check("1_parity_trees_give_nullstellensatz_refutations_on_K_2", ok, info)

    sizes = {}
    for N in (2, 4, 8, 16, 32):
        m = TB.layout(N)["m"] if N <= 8 else None
        if m is None:
            S4, X0, Y0 = 4, 4, 12
            m = X0 + 3 * S4 * (N * N + 1) + Y0 + 6 * S4 * N + 3 * S4 + 8
        k = 2 * m + 4
        sizes[N] = {"grid side m": m, "sphere k": k, "points n = 4k^2": 4 * k * k, "n / N^4": round(4 * k * k / N ** 4)}
    ratios = [sizes[N]["n / N^4"] for N in sorted(sizes)]
    check("2_sizes_of_the_chain", all(r <= 22000 for r in ratios) and ratios == sorted(ratios, reverse=True), sizes)

    allok = all(v["pass"] for v in OUT.values())
    result = {"ticket": "TREE-XOR-20261110-001A", "checks": OUT, "status": "passed" if allok else "failed",
              "seconds": round(time.time() - T0, 1)}
    path = HERE / "result.json"
    if write:
        path.write_text(json.dumps(result, indent=1, default=str) + "\n")
        print("wrote", path)
    else:
        old = json.loads(path.read_text())
        same = {k: v["pass"] for k, v in old["checks"].items()} == {k: v["pass"] for k, v in OUT.items()}
        print("matches result.json" if same else "DIFFERS from result.json")
        sys.exit(0 if same and allok else 1)


if __name__ == "__main__":
    main()
