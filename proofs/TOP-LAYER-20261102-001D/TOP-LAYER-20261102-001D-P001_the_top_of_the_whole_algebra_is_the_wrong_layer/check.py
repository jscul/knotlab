#!/usr/bin/env python3
"""Checks for TOP-LAYER-20261102-001D: the top of the whole algebra is the wrong layer.

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


def circuits(sol, n):
    ranges = [len({t[v] for t in sol}) for v in range(n)]
    cons = [frozenset(Y) for r in range(1, n + 1) for Y in itertools.combinations(range(n), r)
            if len({tuple(t[v] for v in Y) for t in sol}) < math.prod(ranges[v] for v in Y)]
    return [C for C in cons if not any(D < C for D in cons)]


def partitions(s):
    s = list(s)
    if not s:
        yield []
        return
    first, rest = s[0], s[1:]
    for p in partitions(rest):
        for i in range(len(p)):
            yield p[:i] + [[first] + p[i]] + p[i + 1:]
        yield [[first]] + p


# ------------------------------------------------------------------------------------------------ 1. a five-value law that composes like cycles, with top = everything
E = 4                                                   # the fifth value
FREE = {(0, 1, 4): 1, (0, 2, 4): 4, (0, 3, 4): 0, (0, 4, 0): 2, (0, 4, 1): 0, (0, 4, 2): 3, (0, 4, 3): 3, (1, 0, 4): 3, (1, 2, 4): 3,
        (1, 3, 4): 1, (1, 4, 0): 0, (1, 4, 1): 3, (1, 4, 2): 0, (1, 4, 3): 3, (2, 0, 4): 3, (2, 1, 4): 4, (2, 3, 4): 0, (2, 4, 0): 3,
        (2, 4, 1): 2, (2, 4, 2): 1, (2, 4, 3): 4, (3, 0, 4): 0, (3, 1, 4): 2, (3, 2, 4): 0, (3, 4, 0): 0, (3, 4, 1): 0, (3, 4, 2): 4,
        (3, 4, 3): 0, (4, 0, 1): 3, (4, 0, 2): 1, (4, 0, 3): 3, (4, 0, 4): 0, (4, 1, 0): 4, (4, 1, 2): 1, (4, 1, 3): 3, (4, 1, 4): 3,
        (4, 2, 0): 4, (4, 2, 1): 1, (4, 2, 3): 2, (4, 2, 4): 1, (4, 3, 0): 1, (4, 3, 1): 3, (4, 3, 2): 2, (4, 3, 4): 0}
M5 = {}
for x, y, z in itertools.product(range(5), repeat=3):
    if x < 4 and y < 4 and z < 4:
        M5[(x, y, z)] = (x - y + z) % 4
    elif x == y:
        M5[(x, y, z)] = z
    elif y == z:
        M5[(x, y, z)] = x
    else:
        M5[(x, y, z)] = FREE[(x, y, z)]
maltsev = all(M5[(x, x, y)] == y and M5[(y, x, x)] == y for x in range(5) for y in range(5))


def closure(S):
    S = set(S)
    while True:
        new = {M5[(x, y, z)] for x in S for y in S for z in S} - S
        if not new:
            return frozenset(S)
        S |= new


SUBS = sorted({closure(S) for r in range(1, 6) for S in itertools.combinations(range(5), r)}, key=lambda S: (len(S), sorted(S)))


def congruences(S):
    out = []
    for p in partitions(sorted(S)):
        cls = {x: i for i, b in enumerate(p) for x in b}
        if all(cls[M5[(a, y, z)]] == cls[M5[(b, y, z)]] and cls[M5[(y, a, z)]] == cls[M5[(y, b, z)]] and cls[M5[(y, z, a)]] == cls[M5[(y, z, b)]]
               for a in S for b in S if cls[a] == cls[b] and a != b for y in S for z in S):
            out.append(frozenset(frozenset(b) for b in p))
    return out


def unique_max(S):
    if len(S) == 1:
        return True
    top = frozenset([frozenset(S)])
    proper = [c for c in congruences(S) if c != top]
    finer = lambda c, d: all(any(b <= e for e in d) for b in c)
    return len([c for c in proper if not any(c != d and finer(c, d) for d in proper)]) == 1


info1 = {"Mal'tsev, extending x - y + z on Z4": maltsev, "subalgebras": [sorted(S) for S in SUBS],
         "each has a unique maximal congruence": all(unique_max(S) for S in SUBS),
         "congruences of the whole algebra": len(congruences(range(5)))}
check("1 a Mal'tsev operation on five values extending Z4's x - y + z: its subalgebras are the five points, {0,2}, {1,3}, Z4 and the "
      "whole set, each with a unique maximal congruence, and the whole algebra is simple; so its law composes like cycles (KNOT-CIRCUITS "
      "Theorem 1) and its top is the whole algebra",
      maltsev and info1["each has a unique maximal congruence"] and info1["congruences of the whole algebra"] == 2 and
      [sorted(S) for S in SUBS] == [[0], [1], [2], [3], [4], [0, 2], [1, 3], [0, 1, 2, 3], [0, 1, 2, 3, 4]], info1)

# ------------------------------------------------------------------------------------------------ 2. RIGID-SELECTION B's examples inside it
L4 = [[5, 2, 1, 3], [0, 4, 1, 5], [0, 2, 4, 1], [0, 4, 3, 2], [3, 5, 1, 0], [5, 2, 4, 3]]
A4 = [[0, 3, 3, 3, 0, 3], [1, 3, 0, 0, 1, 3], [3, 1, 1, 0, 1, 0], [3, 0, 1, 3, 3, 0], [3, 1, 0, 3, 0, 1], [0, 0, 1, 1, 1, 1]]
L3 = [[1, 8, 2], [8, 1, 5], [8, 0, 7], [6, 3, 0], [3, 4, 2], [5, 4, 2], [3, 5, 7], [1, 7, 6], [4, 6, 0]]
A3 = [[0, 1, 1, 0, 0, 0, 0, 0, 3], [0, 3, 0, 0, 0, 1, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 1, 1], [3, 0, 0, 1, 0, 0, 3, 0, 0],
      [0, 0, 1, 3, 3, 0, 0, 0, 0], [0, 0, 3, 0, 1, 3, 0, 0, 0], [0, 0, 0, 3, 0, 1, 0, 3, 0], [0, 3, 0, 0, 0, 0, 1, 1, 0],
      [1, 0, 0, 0, 1, 0, 3, 0, 0]]


def inside(lines, A, c):
    n = len(A)
    rels = []
    for i, L in enumerate(lines):
        R = {t for t in itertools.product(range(5), repeat=len(L))
             if all(v < 4 for v in t) and sum(A[i][p] * v for p, v in zip(L, t)) % 4 == c[i]}
        rels.append(R)
    closed = all(tuple(M5[(a[j], b[j], d[j])] for j in range(len(L))) in R
                 for R, L in zip(rels, lines) for a in R for b in R for d in R)
    X = np.array(list(itertools.product(range(5), repeat=n)), dtype=np.int8)
    sat = np.zeros((len(X), n), dtype=bool)
    for i, (L, R) in enumerate(zip(lines, rels)):
        tab = np.zeros((5,) * len(L), dtype=bool)
        for t in R:
            tab[t] = True
        sat[:, i] = tab[tuple(X[:, p] for p in L)]
    rep = {"relations are subuniverses of A5^k": closed, "fails": not sat.all(axis=1).any(), "global": True, "removals keeping a knot": []}
    for L in range(n):
        keep = np.delete(sat, L, axis=1).all(axis=1)
        rep["global"] &= bool(keep.any())
        S = [tuple(int(v) for v in x) for x in X[keep]]
        if any(len(C) >= 3 for C in circuits(S, n)):        # the top map is the identity: the top image is S itself
            rep["removals keeping a knot"].append(L)
    return rep


r1 = inside(L4, A4, [2, 0, 0, 0, 0, 0])
r2 = inside(L3, A3, [1, 0, 0, 0, 0, 0, 0, 0, 0])
check("2 RIGID-SELECTION B's two signed Z4 systems, as systems of the five-value law (brute force over 5^6 and 5^9): both fail globally "
      "and keep knots after removals; the top is the whole algebra, so the top image keeps knots and the top-layer statement fails",
      all(r["relations are subuniverses of A5^k"] and r["fails"] and r["global"] for r in (r1, r2)) and len(r1["removals keeping a knot"]) == 6
      and len(r2["removals keeping a knot"]) >= 1, {"6-point four-place example": r1, "9-point cubic example": r2})

# ------------------------------------------------------------------------------------------------ 3. the layer that is rigid: leading digits of each point's own section
rng = random.Random(20261102)
SECTIONS = {"Z4": ([0, 1, 2, 3], lambda x: x, 4), "{0,2}": ([0, 2], lambda x: x // 2, 2), "{1,3}": ([1, 3], lambda x: (x - 1) // 2, 2)}


def lead(dom, x):
    vals, f, size = SECTIONS[dom]
    return f(x) % 2                                      # the leading digit of x in its section


def random_regular(n, k, tries=4000):
    for _ in range(tries):
        pts = [p for p in range(n) for _ in range(k)]
        rng.shuffle(pts)
        lines = [tuple(pts[i * k:(i + 1) * k]) for i in range(n)]
        if all(len(set(L)) == k for L in lines) and len({frozenset(L) for L in lines}) == n:
            return lines
    return None


XS = {n: np.array(list(itertools.product(range(4), repeat=n)), dtype=np.int64) for n in range(4, 8)}
info3, ok3 = collections.Counter(), True


def leading_digits_report(n, dom, X, sat):
    """for a global failure: (leading digits form at most one line after every removal, every kept knot has one varying digit at most,
    number of removals keeping a knot)"""
    keep = [np.delete(sat, L, axis=1).all(axis=1) for L in range(n)]
    good, kept = True, 0
    for L in range(n):
        S = [tuple(int(v) for v in x) for x in X[keep[L]]]
        leads = sorted({tuple(lead(dom[v], x[v]) for v in range(n)) for x in S})
        knots = [C for C in circuits(S, n) if len(C) >= 3]
        moving = {v for v in range(n) if len({t[v] for t in leads}) > 1}
        good &= len(leads) <= 2 and all(len(set(C) & moving) <= 1 for C in knots)
        kept += bool(knots)
    return good, kept


X6 = XS[6]
sat_ex = (X6 @ np.array(A4).T - np.array([2, 0, 0, 0, 0, 0])) % 4 == 0
good_ex, kept_ex = leading_digits_report(6, ["Z4"] * 6, X6, sat_ex)
ok3 &= good_ex
info3["RIGID-SELECTION B's example: removals keeping a knot"] = kept_ex
for trial in range(2500):
    k = rng.choice((3, 4))
    n = rng.randint(k + 1, 7)
    lines = random_regular(n, k)
    if not lines:
        continue
    dom = [rng.choice(["Z4", "Z4", "{0,2}", "{1,3}"]) for _ in range(n)]
    X = XS[n]
    ok_dom = np.ones(len(X), dtype=bool)
    for v in range(n):
        ok_dom &= np.isin(X[:, v], SECTIONS[dom[v]][0])
    sat = np.zeros((len(X), n), dtype=bool)
    for i, L in enumerate(lines):
        if all(dom[v] == "Z4" for v in L) and rng.random() < 0.6:      # a Z4 knot: signed sum mod 4
            s = [rng.choice((1, 3)) for _ in L]
            sat[:, i] = (sum(si * X[:, v] for si, v in zip(s, L)) - rng.randrange(4)) % 4 == 0
        else:                                                            # a knot of the common quotient Z2: leading digits
            acc = sum(np.vectorize(lambda x, d=dom[v]: lead(d, x) if x in SECTIONS[d][0] else 0)(X[:, v]) for v in L)
            sat[:, i] = (acc - rng.randrange(2)) % 2 == 0
    sat &= ok_dom[:, None]
    if sat.all(axis=1).any():
        continue
    keep = [np.delete(sat, L, axis=1).all(axis=1) for L in range(n)]
    if not all(kk.any() for kk in keep):
        continue
    info3["global failures"] += 1
    good, kept = leading_digits_report(n, dom, X, sat)
    info3["random systems: removals keeping a knot"] += kept
    ok3 &= good
check("3 systems of the five-value law with declared domains Z4, {0,2} or {1,3}: RIGID-SELECTION B's example (domains Z4) and random "
      "systems on cubic and 4-regular substrates up to 7 points. After every removal from a global failure the leading digits (each read "
      "in its own section) form at most one line, and every kept knot has at most one variable whose leading digit varies",
      ok3 and kept_ex == 6 and info3["global failures"] > 0, dict(info3))

# ------------------------------------------------------------------------------------------------ 4. two chain rings joined through tops (not proved)
MULT = np.array([[(v & 1) | ((((v >> 1) ^ ((v & 1) if u == 3 else 0)) & 1) << 1) for v in range(4)] for u in range(4)])
info4 = collections.Counter()
for trial in range(3000):
    k = rng.choice((3, 4))
    n = rng.randint(k + 1, 7)
    lines = random_regular(n, k)
    if not lines:
        continue
    kind = [rng.random() < 0.5 for _ in range(n)]          # True: a Z4 point; False: an F2[s]/(s^2) point (a + 2b means a + b s)
    X = XS[n]
    sat = np.zeros((len(X), n), dtype=bool)
    for i, L in enumerate(lines):
        L = list(L)
        c = rng.randrange(4)
        if all(kind[p] for p in L) and rng.random() < 0.8:
            sat[:, i] = (sum(rng.choice((1, 3)) * X[:, p] for p in L) - c) % 4 == 0
        elif not any(kind[p] for p in L) and rng.random() < 0.8:
            acc = np.zeros(len(X), dtype=np.int64)
            for p in L:
                acc ^= MULT[rng.choice((1, 3))][X[:, p]]
            sat[:, i] = acc == c
        else:
            sat[:, i] = (sum(X[:, p] & 1 for p in L) - c) % 2 == 0
    if sat.all(axis=1).any():
        continue
    keep = [np.delete(sat, L, axis=1).all(axis=1) for L in range(n)]
    if not all(kk.any() for kk in keep):
        continue
    info4["global failures"] += 1
    info4["with both kinds of point"] += len(set(kind)) == 2
    for L in range(n):
        tops = sorted({tuple(int(v) for v in x) for x in (X[keep[L]] & 1)})
        if any(len(C) >= 3 for C in circuits(tops, n)):
            info4["leading digits keep a knot"] += 1
check("4 points of two kinds, Z4 and F2[s]/(s^2), joined only through their leading digits, on random regular substrates up to 7 "
      "points: no global failure leaves a knot among the leading digits (evidence, not a proof)",
      info4["leading digits keep a knot"] == 0 and info4["with both kinds of point"] > 0, dict(info4))

# ------------------------------------------------------------------------------------------------ 5. the knot keeps its emergence in its only layer
CENSUS = json.loads((ROOT / "research/MUTUAL-SELECTION-20261031-001C/census.json").read_text())
FANO = next([tuple(L) for L in row["lines"]] for n, v in CENSUS.items() if int(n) == 7 for row in v["rows"]
            if all(len(set(a) & set(b)) == 1 for a, b in itertools.combinations(row["lines"], 2)))
X7 = np.array(list(itertools.product(range(2), repeat=7)), dtype=np.int64)
nae = np.stack([~((X7[:, L[0]] == X7[:, L[1]]) & (X7[:, L[1]] == X7[:, L[2]])) for L in FANO], axis=1)
kept5 = [L for L in range(7) if any(len(C) >= 3 for C in circuits([tuple(int(v) for v in x) for x in X7[np.delete(nae, L, axis=1).all(axis=1)]], 7))]
check("5 the knot (not-all-equal on two values) on the Fano plane fails globally and keeps a knot after every removal: three-place "
      "emergence in its only layer", not nae.all(axis=1).any() and all(np.delete(nae, L, axis=1).all(axis=1).any() for L in range(7))
      and len(kept5) == 7, {"Fano lines": FANO, "removals keeping a knot": kept5})

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
