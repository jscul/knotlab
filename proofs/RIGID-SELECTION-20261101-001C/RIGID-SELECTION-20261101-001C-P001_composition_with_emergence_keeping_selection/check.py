#!/usr/bin/env python3
"""Checks for RIGID-SELECTION-20261101-001C: a law that composes like cycles and selects spaces that keep a knot.

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
from fractions import Fraction
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

# ------------------------------------------------------------------------------------------------ the law
PHI = [0, 0, 1, 2, 3]                    # blurred values 0 and 1 both map to 0 of Z4
DOM = range(5)
W = [PHI.count(a) for a in range(4)]     # preimage sizes 2, 1, 1, 1


def base_rel(signs, c):
    return {t for t in itertools.product(range(4), repeat=len(signs)) if sum(s * x for s, x in zip(signs, t)) % 4 == c}


def blur_rel(signs, c):
    return {t for t in itertools.product(DOM, repeat=len(signs)) if sum(s * PHI[x] for s, x in zip(signs, t)) % 4 == c}


SIGNS3 = list(itertools.product((1, -1), repeat=3))
SIGNS4 = list(itertools.product((1, -1), repeat=4))


def circuits(sol, n):
    ranges = [len({t[v] for t in sol}) for v in range(n)]

    def constrained(Y):
        return len({tuple(t[v] for v in Y) for t in sol}) < math.prod(ranges[v] for v in Y)
    cons = [frozenset(Y) for r in range(1, n + 1) for Y in itertools.combinations(range(n), r) if constrained(Y)]
    return set(cons), [C for C in cons if not any(D < C for D in cons)], constrained


# ------------------------------------------------------------------------------------------------ 1. a Mal'tsev lift preserves the law
def m_lift(x, y, z):
    if x == y:
        return z
    if y == z:
        return x
    return PHI.index((PHI[x] - PHI[y] + PHI[z]) % 4)


M = {(x, y, z): m_lift(x, y, z) for x in DOM for y in DOM for z in DOM}
maltsev = all(M[(x, x, y)] == y and M[(y, x, x)] == y for x in DOM for y in DOM)
lifts = all(PHI[M[(x, y, z)]] == (PHI[x] - PHI[y] + PHI[z]) % 4 for x in DOM for y in DOM for z in DOM)
pres = 0
for s in SIGNS3:
    for c in range(4):
        R = blur_rel(s, c)
        pres += all(tuple(M[(a[j], b[j], c_[j])] for j in range(3)) in R for a in R for b in R for c_ in R)
ppdef = 0
for s in SIGNS4:
    for c in range(4):
        left, right = blur_rel((s[0], s[1], -1), 0), blur_rel((1, s[2], s[3]), c)
        defined = {(x, y, z, w) for (x, y, u) in left for (u2, z, w) in right if u == u2}
        ppdef += defined == blur_rel(s, c)
check("1 the Mal'tsev lift of x - y + z (identities, and phi(m(x,y,z)) = phi(x) - phi(y) + phi(z)) preserves all 32 three-place relations "
      "of the blurred law; each of the 64 four-place relations is pp-defined from three-place ones, so it is preserved too",
      maltsev and lifts and pres == 32 and ppdef == 64,
      {"Mal'tsev identities": maltsev, "lifts x - y + z": lifts, "three-place relations preserved (of 32)": pres,
       "four-place relations pp-defined (of 64)": ppdef})

# ------------------------------------------------------------------------------------------------ 2-3. the two spaces of ticket B
A4 = [[0, 3, 3, 3, 0, 3], [1, 3, 0, 0, 1, 3], [3, 1, 1, 0, 1, 0], [3, 0, 1, 3, 3, 0], [3, 1, 0, 3, 0, 1], [0, 0, 1, 1, 1, 1]]
c4 = [2, 0, 0, 0, 0, 0]
A3 = [[0, 1, 1, 0, 0, 0, 0, 0, 3], [0, 3, 0, 0, 0, 1, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 1, 1], [3, 0, 0, 1, 0, 0, 3, 0, 0],
      [0, 0, 1, 3, 3, 0, 0, 0, 0], [0, 0, 3, 0, 1, 3, 0, 0, 0], [0, 0, 0, 3, 0, 1, 0, 3, 0], [0, 3, 0, 0, 0, 0, 1, 1, 0],
      [1, 0, 0, 0, 1, 0, 3, 0, 0]]
c3 = [1, 0, 0, 0, 0, 0, 0, 0, 0]
PHI_NP = np.array(PHI, dtype=np.int32)


def space_report(A, c, label):
    n = len(A)
    Xb = np.array(list(itertools.product(range(5), repeat=n)), dtype=np.int8)
    Y = PHI_NP[Xb]                                        # images in Z4
    sat = ((Y @ np.array(A, dtype=np.int32).T - np.array(c)) % 4 == 0)
    rep = {"blurred assignments": len(Xb), "fails": not sat.all(axis=1).any(), "removals": []}
    glob, kept, counts_ok, same_circ, top_ok = True, 0, True, True, True
    for L in range(n):
        keep = np.delete(sat, L, axis=1).all(axis=1)
        blur = [tuple(int(v) for v in x) for x in Xb[keep]]
        base = Z.solutions([r for j, r in enumerate(A) if j != L], [b for j, b in enumerate(c) if j != L], 2, 2, n)
        weighted = sum(math.prod(W[a] for a in x) for x in base)
        glob &= bool(blur)
        counts_ok &= weighted == len(blur)
        cb, circ_b, _ = circuits(base, n) if base else (set(), [], None)
        cl, circ_l, _ = circuits(blur, n) if blur else (set(), [], None)
        same_circ &= cb == cl
        knots = sorted(sorted(C) for C in circ_l if len(C) >= 3)
        kept += bool(knots)
        full = [i for i in range(n) if len({x[i] for x in base}) == 4]
        for C in knots:                                  # ticket D: at most one variable whose image takes all four values
            top_ok &= sum(i in full for i in C) <= 1
        rep["removals"].append({"line": L, "image solutions": len(base), "blurred solutions": len(blur),
                                "weighted image count": weighted, "knots": knots[:3], "number of knots": len(knots)})
    rep.update({"global": glob, "lines whose removal keeps a knot": kept,
                "count = sum over image solutions of 2^(number of zeros)": counts_ok,
                "constrained sets equal the image's": same_circ, "each kept knot has at most one full-range image variable": top_ok})
    return rep


rep2 = space_report(A4, c4, "four places")
check("2 on the 6-point four-place space of ticket B (brute force over 5^6): the blurred law fails globally, keeps knots after every "
      "line is removed, has the image's constrained sets, and counts as 8 weighted image solutions",
      rep2["fails"] and rep2["global"] and rep2["lines whose removal keeps a knot"] == 6 and rep2["count = sum over image solutions of 2^(number of zeros)"]
      and rep2["constrained sets equal the image's"] and rep2["each kept knot has at most one full-range image variable"]
      and all(r["image solutions"] == 8 for r in rep2["removals"]), rep2)
rep3 = space_report(A3, c3, "three places")
check("3 on the 9-point cubic space of ticket B (brute force over 5^9): the blurred law fails globally, keeps knots after line 0 is "
      "removed, has the image's constrained sets at every removal, and counts as the weighted image solutions",
      rep3["fails"] and rep3["global"] and rep3["removals"][0]["number of knots"] > 0 and rep3["removals"][0]["image solutions"] == 8
      and rep3["count = sum over image solutions of 2^(number of zeros)"] and rep3["constrained sets equal the image's"]
      and rep3["each kept knot has at most one full-range image variable"], rep3)


# ------------------------------------------------------------------------------------------------ 4. counting is hard
def rank(Mx):
    A = [[Fraction(v) for v in row] for row in Mx]
    r = 0
    for col in range(len(A[0])):
        pr = next((i for i in range(r, len(A)) if A[i][col] != 0), None)
        if pr is None:
            continue
        A[r], A[pr] = A[pr], A[r]
        for i in range(len(A)):
            if i != r and A[i][col] != 0:
                f = A[i][col] / A[r][col]
                A[i] = [a - f * b for a, b in zip(A[i], A[r])]
        r += 1
    return r


ranks_blur, ranks_base = collections.Counter(), collections.Counter()
for s in SIGNS3:
    for c in range(4):
        R, R0 = blur_rel(s, c), base_rel(s, c)
        ranks_blur[rank([[sum(1 for z in DOM if (x, y, z) in R) for y in DOM] for x in DOM])] += 1
        ranks_base[rank([[sum(1 for z in range(4) if (x, y, z) in R0) for y in range(4)] for x in range(4)])] += 1
check("4 every three-place relation of the blurred law has a count matrix (pairs against the number of completions) of rank 4, against "
      "rank 1 for signed Z4: the blurred law is not strongly balanced, so counting it is #P-complete (Dyer-Richerby)",
      set(ranks_blur) == {4} and set(ranks_base) == {1}, {"blurred ranks": dict(ranks_blur), "signed Z4 ranks": dict(ranks_base)})

# ------------------------------------------------------------------------------------------------ 5. recognition and circuit elimination
rng = random.Random(20261101)


def random_system(n):
    out = []
    for _ in range(rng.randint(2, 5)):
        k = rng.choice((3, 4))
        vs = rng.sample(range(n), k) if n >= k else [rng.randrange(n) for _ in range(k)]
        out.append((tuple(vs), tuple(rng.choice((1, -1)) for _ in range(k)), rng.randrange(4)))
    return out


def solve_blur(n, system):
    X = np.array(list(itertools.product(range(5), repeat=n)), dtype=np.int8)
    Y = PHI_NP[X]
    ok = np.ones(len(X), dtype=bool)
    for vs, s, c in system:
        ok &= (sum(si * Y[:, v] for si, v in zip(s, vs)) - c) % 4 == 0
    return [tuple(int(v) for v in x) for x in X[ok]]


agree = failing = tested = viol = 0
for trial in range(300):
    n = rng.choice((4, 5))
    system = random_system(n)
    sol = solve_blur(n, system)
    rows = []
    for vs, s, c in system:
        r = [0] * n
        for si, v in zip(s, vs):
            r[v] = (r[v] + si) % 4
        rows.append(r)
    image = Z.solutions(rows, [c for _, _, c in system], 2, 2, n)
    agree += bool(sol) == bool(image)
    failing += not sol
    if sol and trial < 200:
        _, circ, constrained = circuits(sol, n)
        for C1, C2 in itertools.combinations(circ, 2):
            for e in C1 & C2:
                tested += 1
                viol += not constrained(sorted((C1 | C2) - {e}))
check("5 on 300 random blurred systems: failure is decided by linear algebra over Z4 on the image (agrees with brute force), and circuit "
      "elimination holds (for circuits C1, C2 sharing e, (C1 u C2) - e is constrained)",
      agree == 300 and failing > 0 and tested > 0 and viol == 0,
      {"agree (of 300)": agree, "failing": failing, "circuit pairs tested": tested, "violations": viol})

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
