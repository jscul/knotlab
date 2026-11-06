#!/usr/bin/env python3
"""Checks for RIGID-SELECTION-20261101-001D: selection spends the top layer.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy)."""
import collections
import hashlib
import itertools
import json
import math
import random
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/RIGID-SELECTION-20261101-001A/RIGID-SELECTION-20261101-001A-P001_where_selection_is_rigid"))
import zlocal as Z  # noqa: E402

T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:600], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        print(json.dumps(info, default=str, indent=1))
        sys.exit(1)


# ------------------------------------------------------------------------------------------------ 0. bindings
manifest = json.loads((HERE / "manifest.json").read_text())
bad = {p: d for p, d in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != d}
status = {p: json.loads((ROOT / p).read_text()).get("status") for p in manifest["parent_bindings"]
          if p.endswith(".json") and p.startswith("proofs/")}
check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
      {"mismatched": bad, "statuses": status})


def knot_report(K, n, top_of, full_size, lower_size):
    """circuits of three or more variables of the group K: (number, most full-range variables in one, largest index)"""
    ranges = [len({x[i] for x in K}) for i in range(n)]
    most_full, worst, count = 0, 1, 0
    for C in Z.circuits(K, n):
        if len(C) < 3:
            continue
        count += 1
        proj = {tuple(x[i] for i in sorted(C)) for x in K}
        worst = max(worst, math.prod(ranges[i] for i in C) // len(proj))
        most_full = max(most_full, sum(ranges[i] == full_size for i in C))
    return count, most_full, worst


def top_dim(K, top_of, f):
    """dimension over the residue field (of size f) of the top layer {x mod pi : x in K}"""
    T = {tuple(top_of(v) for v in x) for x in K}
    d = round(math.log(len(T), f))
    assert f ** d == len(T)
    return d


# ------------------------------------------------------------------------------------------------ 1. Z_(p^k), random systems
rng = random.Random(20261101)


def random_regular(n, k, tries=4000):
    for _ in range(tries):
        pts = [p for p in range(n) for _ in range(k)]
        rng.shuffle(pts)
        lines = [tuple(pts[i * k:(i + 1) * k]) for i in range(n)]
        if all(len(set(L)) == k for L in lines) and len({frozenset(L) for L in lines}) == n:
            return lines
    return None


def global_rhs(A, p, kk, n):
    """a right-hand side failing globally, or None. Every global class lies in R g_0, so c = t e_0 covers them all."""
    q = p ** kk
    m = len(A)
    for t in range(1, q):
        c = [t] + [0] * (m - 1)
        if Z.solutions(A, c, p, kk, n):
            continue
        if all(Z.solutions([r for j, r in enumerate(A) if j != L], [b for j, b in enumerate(c) if j != L], p, kk, n) for L in range(m)):
            return c
    return None


tally = collections.Counter()
viol = []
RINGS = ((2, 1), (3, 1), (5, 1), (2, 2), (2, 3), (2, 4), (3, 2), (3, 3), (5, 2))
for p, kk in RINGS:
    q = p ** kk
    units = [u for u in range(1, q) if u % p]
    for trial in range(1000):
        kind = trial % 4
        if kind == 0:                                   # a knot system on a random regular substrate
            k = rng.choice((3, 4))
            n = rng.randint(k + 2, 7 if q <= 9 else 6)
            lines = random_regular(n, k)
            if not lines:
                continue
            m = n
            A = [[(rng.choice(units) if pt in L else 0) for pt in range(n)] for L in lines]
        else:                                           # arbitrary entries; square, one short, one long, two long
            n = rng.randint(3, 6 if q <= 9 else 5)
            m = n + (0, -1, 1, 2)[kind]
            A = [[rng.choice(range(q)) if rng.random() < 0.6 else 0 for _ in range(n)] for _ in range(m)]
        c = global_rhs(A, p, kk, n)
        if c is None:
            continue
        tally[("global", m - n)] += 1
        if m > n + 1:
            viol.append(("global with m > n + 1", q, A))
            continue
        for L in range(m):
            K = Z.solutions([r for j, r in enumerate(A) if j != L], [0] * (m - 1), p, kk, n)
            d = top_dim(K, lambda v: v % p, p)
            tally["removals"] += 1
            if d != n - m + 1:
                viol.append(("top layer", q, A, L, d))
            if m == n:
                cnt, most_full, worst = knot_report(K, n, lambda v: v % p, q, q // p)
                tally["kept knots"] += cnt
                tally[("largest index", q)] = max(tally[("largest index", q)], worst)
                if cnt and (most_full > 1 or worst > q // p):
                    viol.append(("knot", q, A, L, most_full, worst))
info1 = {"global failures by m - n": {str(k[1]): v for k, v in tally.items() if k[0] == "global"}, "removals": tally["removals"],
         "kept knots (square)": tally["kept knots"],
         "largest kept index by ring": {str(k[1]): v for k, v in tally.items() if k[0] == "largest index"}, "violations": viol[:3]}
check("1 over Z_(p^k) for p^k in 2, 3, 5, 4, 8, 16, 9, 27, 25 (knot systems on random regular substrates, and arbitrary m x n systems "
      "with m = n - 1, n, n + 1, n + 2): every global failure has m <= n + 1, every removal leaves a top layer of dimension n - m + 1, "
      "and in square systems every kept knot has at most one full-range variable and index at most p^(k-1)",
      not viol and tally[("global", 2)] == 0 and tally["kept knots"] > 0 and all(tally[("global", s)] for s in (-1, 0, 1)), info1)

# ------------------------------------------------------------------------------------------------ 2. brute force over F2[t]/(t^2)
# elements a + b t are coded 0..3 as a + 2b; addition is XOR, multiplication (a + bt)(c + dt) = ac + (ad + bc) t
MUL = np.array([[(x & 1 & y) | ((((x & 1) & (y >> 1)) ^ ((y & 1) & (x >> 1))) << 1) for y in range(4)] for x in range(4)])
UNITS2 = [1, 3]


def images(A, X):
    """the vector A x over F2[t]/(t^2) for every x in X, as an array of row values"""
    out = np.zeros((len(X), len(A)), dtype=np.int64)
    for i, row in enumerate(A):
        acc = np.zeros(len(X), dtype=np.int64)
        for j, a in enumerate(row):
            acc ^= MUL[a][X[:, j]]
        out[:, i] = acc
    return out


def codes(V):
    return (V * (4 ** np.arange(V.shape[1]))).sum(axis=1) if V.shape[1] else np.zeros(len(V), dtype=np.int64)


XS = {n: np.array(list(itertools.product(range(4), repeat=n)), dtype=np.int64) for n in range(2, 9)}
tally2 = collections.Counter()
viol2 = []
examples2 = []
for trial in range(1600):
    kind = trial % 4
    if kind == 0:                                       # a knot system on a random regular substrate, units 1 and 1 + t
        n = rng.choice((5, 6))
        lines = random_regular(n, rng.choice((3, 4)))
        if not lines:
            continue
        m = n
        A = [[(rng.choice(UNITS2) if pt in L else 0) for pt in range(n)] for L in lines]
    else:                                               # arbitrary entries; square, one short, one long, two long
        n = rng.randint(3, 6) if kind == 1 else rng.randint(3, 5)
        m = n + (0, 0, -1, 1, 2)[kind if rng.random() < 0.75 else 4]
        A = [[rng.choice(range(4)) if rng.random() < 0.6 else 0 for _ in range(n)] for _ in range(m)]
    X = XS[n]
    IM = images(A, X)
    C = XS[m]
    glob = ~np.isin(codes(C), np.unique(codes(IM)))
    for L in range(m):
        glob &= np.isin(codes(np.delete(C, L, axis=1)), np.unique(codes(np.delete(IM, L, axis=1))))
    if not glob.any():
        continue
    tally2[("global", m - n)] += 1
    if m > n + 1:
        viol2.append(("global with m > n + 1", A))
        continue
    for L in range(m):
        K = [tuple(int(v) for v in x) for x in X[(np.delete(IM, L, axis=1) == 0).all(axis=1)]]
        d = top_dim(K, lambda v: v & 1, 2)
        tally2["removals"] += 1
        if d != n - m + 1:
            viol2.append(("top layer", A, L, d))
        if m == n:
            cnt, most_full, worst = knot_report(K, n, lambda v: v & 1, 4, 2)
            tally2["kept knots"] += cnt
            tally2["removals keeping a knot"] += cnt > 0
            if cnt and len(examples2) < 1:
                examples2.append({"A (a + bt coded a + 2b)": A, "removed": L, "knots": cnt})
            if cnt and (most_full > 1 or worst > 2):
                viol2.append(("knot", A, L, most_full, worst))
info2 = {"global failures by m - n": {str(k[1]): v for k, v in tally2.items() if k[0] == "global"}, "removals": tally2["removals"],
         "kept knots (square)": tally2["kept knots"], "removals keeping a knot": tally2["removals keeping a knot"], "an example keeping a knot": examples2, "violations": viol2[:3]}
check("2 brute force over F2[t]/(t^2), a chain ring of characteristic 2 that is not Z4, with no Smith form: every removal from a global "
      "failure leaves a top layer of dimension n - m + 1, square global failures do keep knots, and each has at most one full-range "
      "variable and index at most 2; no global failure has m > n + 1",
      not viol2 and tally2["kept knots"] > 0 and tally2[("global", 2)] == 0 and all(tally2[("global", s)] for s in (-1, 0, 1)), info2)

# ------------------------------------------------------------------------------------------------ 3. the bound is attained
A8 = [[1, 0, 0, 0, 3, 1], [0, 1, 0, 7, 5, 0], [3, 0, 7, 7, 0, 0], [7, 0, 7, 0, 0, 5], [0, 5, 1, 3, 0, 0], [0, 3, 0, 0, 7, 7]]
A27 = [[25, 0, 22, 22, 0, 0], [0, 20, 0, 0, 19, 13], [0, 0, 22, 23, 19, 0], [0, 7, 22, 0, 20, 0], [7, 16, 0, 0, 0, 7], [19, 0, 0, 22, 0, 26]]


def cubic(A):
    return all(sum(1 for x in r if x) == 3 for r in A) and all(sum(1 for r in A if r[j]) == 3 for j in range(len(A)))


rep3 = {}
X8 = np.array(list(itertools.product(range(8), repeat=6)), dtype=np.int64)
c8 = global_rhs(A8, 2, 3, 6)
sol8 = X8[((X8 @ np.array(A8[1:]).T) % 8 == 0).all(axis=1)]
K8 = [tuple(int(v) for v in x) for x in sol8]
proj8 = {(x[0], x[1], x[2]) for x in K8}
r8 = [len({x[i] for x in K8}) for i in (0, 1, 2)]
rep3["Z8"] = {"cubic with unit coefficients": cubic(A8) and all(v % 2 for r in A8 for v in r if v), "global right-hand side": c8,
              "removed line": 0, "knot": [0, 1, 2], "ranges": r8, "projection": len(proj8),
              "is a circuit": frozenset({0, 1, 2}) in Z.circuits(K8, 6), "index": math.prod(r8) // len(proj8)}
c27 = global_rhs(A27, 3, 3, 6)
K27 = Z.solutions([r for j, r in enumerate(A27) if j != 4], [0] * 5, 3, 3, 6)
proj27 = {(x[0], x[2], x[5]) for x in K27}
r27 = [len({x[i] for x in K27}) for i in (0, 2, 5)]
rep3["Z27"] = {"cubic with unit coefficients": cubic(A27) and all(v % 3 for r in A27 for v in r if v), "global right-hand side": c27,
               "removed line": 4, "knot": [0, 2, 5], "ranges": r27, "projection": len(proj27),
               "is a circuit": frozenset({0, 2, 5}) in Z.circuits(K27, 6), "index": math.prod(r27) // len(proj27)}
check("3 the bound p^(k-1) is attained at k = 3: a cubic knot system over Z8 (brute force over Z8^6) and one over Z27 fail globally "
      "and keep knots of index 4 and 9",
      all(v["cubic with unit coefficients"] and v["global right-hand side"] and v["is a circuit"] for v in rep3.values())
      and rep3["Z8"]["index"] == 4 and rep3["Z27"]["index"] == 9, rep3)

OUT["seconds"] = round(time.time() - T0, 1)
print("ALL OK", OUT["seconds"], "s")
result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"], "proof": manifest["proof"],
          "status": "passed", "claim": manifest["claim"], "checks": {k: v for k, v in OUT.items() if k != "seconds"}}
text = json.dumps(result, indent=1, sort_keys=True, default=str) + "\n"
if "--write" in sys.argv:
    (HERE / "result.json").write_text(text)
elif not (HERE / "result.json").exists() or json.loads((HERE / "result.json").read_text()) != json.loads(text):
    print("result.json does not match a fresh run; rerun with --write after review")
    sys.exit(1)
