#!/usr/bin/env python3
"""Checks for KNOT-COUPLING-20261031-001B: away from the knot's law, counting on the knot's spaces is #P-hard.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (sympy, networkx). The end-to-end sections use only hard_lib (its own counter, atom builder and
interpolation), not ticket A's library."""
import hashlib
import itertools
import json
import random
import sys
import time
from fractions import Fraction
from pathlib import Path

import networkx as nx
import sympy as sp

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import hard_lib as B  # noqa: E402

T0 = time.time()
OUT = {}
FANO = [(0, 1, 2), (0, 3, 4), (0, 5, 6), (1, 3, 5), (1, 4, 6), (2, 3, 6), (2, 4, 5)]
K4 = [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:600], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        print(json.dumps(info, default=str, indent=1))
        sys.exit(1)


def s(z):
    return str(z[0]) if z[1] == 0 else f"{z[0]} + {z[1]} i"


def prism_system(n):
    g = nx.circular_ladder_graph(n)
    col = nx.bipartite.color(g)
    return [tuple(sorted(g[v])) for v in sorted(g) if col[v] == 1]


def splice():
    out, k = [], 0
    for l in FANO:
        if 0 in l:
            out.append(tuple(('s', FANO[0][k]) if q == 0 else ('a', q) for q in l))
            k += 1
        else:
            out.append(tuple(('a', q) for q in l))
    return out + [tuple(('s', q) for q in l) for l in FANO if tuple(l) != tuple(FANO[0])]


def pfaffian_negation_set(G):
    incs = [(i, p) for i, l in enumerate(G) for p in l]
    for r in range(0, 6):
        for S in itertools.combinations(incs, r):
            if B.count(G, B.C(0), frozenset(S)) == B.ZERO:
                return set(S)


def connected(lines):
    g = nx.Graph()
    for i, l in enumerate(lines):
        for p in l:
            g.add_edge(('l', i), ('p', p))
    return nx.is_connected(g)


# ------------------------------------------------------------------------------------------------ 0. bindings
manifest = json.loads((HERE / "manifest.json").read_text())
bad = {p: d for p, d in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != d}
check("0 dependency artifacts bound by hash", not bad, {"parents": len(manifest["parent_bindings"]), "mismatched": bad})

P6 = prism_system(6)
SPLICE = splice()
NONPLANAR = B.with_chains(K4, {(0, 0): 1}, FANO, (0, 0))          # K4^(3) with one Fano atom: 11 points, Pfaffian, not planar, colourable
SOURCES = {"K4^(3)": K4, "6-prism system": P6, "K4^(3) with a Fano atom (non-planar)": NONPLANAR}
O = {k: pfaffian_negation_set(v) for k, v in SOURCES.items()}

# ------------------------------------------------------------------------------------------------ 1. the instances are knot's spaces
res = {}
for name in ("K4^(3)", "6-prism system"):
    G = SOURCES[name]
    incs = [(i, p) for i, l in enumerate(G) for p in l]
    for i, j in itertools.product((0, 1, 2), (0, 1)):
        inst = B.with_chains(G, {e: (2 * j + 1 if e in O[name] else 2 * i) for e in incs}, FANO, (0, 0))
        res[f"{name}, i = {i}, j = {j}"] = {"connected": connected(inst), "#col": s(B.count(inst, B.C(0))), "lines": len(inst),
                                           "cubic": all(sum(1 for l in inst if p in l) == 3 for p in {q for l in inst for q in l})}
    wrong = set(list(O[name])[1:])           # drop one incidence: not a Pfaffian negation set
    inst = B.with_chains(G, {e: (1 if e in wrong else 0) for e in incs}, FANO, (0, 0))
    res[f"{name}, control: odd chains on a non-Pfaffian set"] = {"#col": s(B.count(inst, B.C(0)))}
ok = all(v["connected"] and v["cubic"] and v["#col"] == "0" for k, v in res.items() if "control" not in k) and all(
    v["#col"] != "0" for k, v in res.items() if "control" in k)
check("1 the reduction's instances (even chains off a Pfaffian negation set O, odd chains on O) are connected cubic knot's spaces; odd "
      "chains on a non-Pfaffian set give colourable systems", ok, {"negation sets": {k: sorted(map(str, v)) for k, v in O.items()}, **res})

# ------------------------------------------------------------------------------------------------ 2. the oracle identity
def Q_direct(G, Oset, u0, rho, a, b):
    g = nx.Graph()
    for i, l in enumerate(G):
        for p in l:
            g.add_edge(('l', i), ('p', p))
    edges = [frozenset(e) for e in g.edges()]
    idx = {e: k for k, e in enumerate(edges)}
    span = [0]
    for cyc in nx.cycle_basis(g):
        m = 0
        for x, y in zip(cyc, cyc[1:] + cyc[:1]):
            m ^= 1 << idx[frozenset((x, y))]
        span += [z ^ m for z in span]
    om = sum(1 << idx[frozenset((('l', i), ('p', p)))] for i, p in Oset)
    tot = B.ZERO
    for chi in span:
        r, t = bin(chi & ~om).count("1"), bin(chi & om).count("1")
        tot = B.cadd(tot, B.cmul(B.cmul(B.cpow(u0, (r + t) // 2) if (r + t) % 2 == 0 else None, B.cpow(rho, t)),
                                  B.cmul(B.cpow(a, r), B.cpow(b, t))))
    return tot


res = {}
lam0 = B.C(2)
al = B.cdiv(B.count(FANO, lam0), B.C(2))
be = B.cdiv(B.count(FANO, lam0, frozenset({(0, 0)})), B.C(2))
sm, rho = B.cadd(al, be), B.cdiv(B.csub(al, be), B.cadd(al, be))
u0 = B.cdiv(B.csub(lam0, B.ONE), B.cadd(lam0, B.C(3)))
G = K4
incs = [(i, p) for i, l in enumerate(G) for p in l]
for i, j in itertools.product((0, 1, 2), (0, 1, 2)):
    lengths = {e: (2 * j + 1 if e in O["K4^(3)"] else 2 * i) for e in incs}
    inst = B.with_chains(G, lengths, FANO, (0, 0))
    lhs = B.count(inst, lam0)
    K = B.cmul(B.cmul(B.cpow(B.C(2), 4), B.cpow(B.cdiv(B.cadd(lam0, B.C(3)), B.C(4)), 4)), B.cpow(sm, sum(lengths.values())))
    rhs = B.cmul(K, Q_direct(G, O["K4^(3)"], u0, rho, B.cpow(rho, 2 * i), B.cpow(rho, 2 * j)))
    res[f"i = {i}, j = {j}"] = lhs == rhs
check("2 the oracle identity: M(G_ij; lam0) = 2^n ((lam0+3)/4)^n (alpha+beta)^(sum of chain lengths) Q(rho^2i, rho^2j), Q summed over the "
      "even subgraphs of G directly (K4^(3), lam0 = 2)", all(res.values()), {"cases": len(res), "rho(2)": s(rho), **res})

# ------------------------------------------------------------------------------------------------ 3. end to end
runs = [("K4^(3)", FANO, (0, 0), B.C(2)), ("K4^(3)", FANO, (0, 0), B.C(Fraction(-1, 2))), ("K4^(3)", FANO, (0, 0), B.C(1, 1)),
        ("K4^(3)", SPLICE, (0, ('a', 1)), B.C(2)), ("6-prism system", FANO, (0, 0), B.C(2)),
        ("K4^(3) with a Fano atom (non-planar)", FANO, (0, 0), B.C(2))]
res = {}
for name, Hat, e0, l0 in runs:
    G = SOURCES[name]
    Da, Db = B.even_subgraph_degrees(G, O[name])
    t = time.time()
    got, calls, biggest, rho_used, q = B.recover_colourings(G, O[name], Hat, e0, l0, Da, Db)
    true = B.count(G, B.C(0))
    res[f"{name}, atom {'Fano' if Hat is FANO else '13-point splice'}, lam0 = {s(l0)}"] = {
        "recovered #col": s(got), "true #col": s(true), "oracle calls": calls, "largest instance (lines)": biggest,
        "rho": s(rho_used), "seconds": round(time.time() - t, 1)}
check("3 end to end: the colouring counts of plain Pfaffian systems (two planar, one non-planar) are recovered exactly from the counts of "
      "knot's spaces at real, negative and complex couplings, with the Fano or the splice atom", all(
          v["recovered #col"] == v["true #col"] for v in res.values()), res)

# ------------------------------------------------------------------------------------------------ 4. real couplings
rng = random.Random(20261031)
atoms = [("Fano", FANO, (0, 0))] + [("splice", SPLICE, e) for e in ((0, ('a', 1)), (3, ('a', 3)), (7, ('s', 3)))]
worst = None
for t in range(150):
    l0 = Fraction(rng.randint(-400, 400), rng.randint(1, 37))
    if l0 in (0, 1, -1, -3):
        continue
    best = 0
    for nm, Hat, e0 in atoms:
        a_ = B.count(Hat, B.C(l0))[0] / 2
        b_ = B.count(Hat, B.C(l0), frozenset({e0}))[0] / 2
        if a_ + b_ != 0:
            r = (a_ - b_) / (a_ + b_)
            best = max(best, abs(abs(r) - 1) if r != 0 else 0)
    worst = best if worst is None else min(worst, best)
check("4 real couplings: at 150 random rational lam0 outside {0, 1, -1, -3} some atom has |rho| != 1 and rho != 0 (ticket A, Proposition 6 "
      "proves it for every real lam0)", worst is not None and worst > 0, {"smallest best distance of |rho| from 1": float(worst)})

# ------------------------------------------------------------------------------------------------ 5. the tractable couplings
res = {}
spaces = {"Fano": FANO, "13-point splice": SPLICE,
          "K4^(3) decorated on O (knot's space)": B.with_chains(K4, {e: (1 if e in O["K4^(3)"] else 0) for e in
                                                                     [(i, p) for i, l in enumerate(K4) for p in l]}, FANO, (0, 0))}
for name, H in spaces.items():
    n = len({p for l in H for p in l})
    res[name] = {
        "lam = 0: #col = 0": B.count(H, B.C(0)) == B.ZERO,
        "lam = 1: 2^n": B.count(H, B.C(1)) == B.C(2 ** n),
        "lam = -1: quadratic exponential sum = M": B.C(B.M_at_minus_one(H)) == B.count(H, B.C(-1)),
        "lam = oo: linear system = leading coefficient": B.M_at_infinity(H) == 2,
        "lam = -3: (-2)^n |det| = M": B.C(B.M_at_minus_three_knot(H)) == B.count(H, B.C(-3)),
    }
rng = random.Random(7)
qs_ok = 0
for H in (FANO, K4, P6):
    incs = [(i, p) for i, l in enumerate(H) for p in l]
    for t in range(10):
        neg = frozenset(rng.sample(incs, rng.randint(0, len(incs))))
        qs_ok += B.C(B.M_at_minus_one(H, neg)) == B.count(H, B.C(-1), neg)
res["quadratic sum against the counter on 30 random signed systems"] = qs_ok
check("5 the tractable couplings on knot's spaces: lam = 0 (zero), 1 (2^n), -1 (a quadratic exponential sum over GF(2)), oo (a linear "
      "system), -3 ((-2)^n |det|)", all(all(v.values()) for k, v in res.items() if isinstance(v, dict)) and qs_ok == 30, res)

# ------------------------------------------------------------------------------------------------ 6. deficiency one
res = {}
G = K4
Da, Db = B.even_subgraph_degrees(G, O["K4^(3)"])
estar = next(e for e in [(i, p) for i, l in enumerate(G) for p in l] if e not in O["K4^(3)"])
got, calls, biggest, rho2 = B.recover_deficiency_one(G, O["K4^(3)"], estar, FANO, (0, 0), 3, B.C(2), Da, Db)
res["K4^(3) from deficiency-one knot's spaces, lam0 = 2"] = {"recovered #col": s(got), "oracle calls": calls,
                                                               "largest instance (lines)": biggest, "rho of the line-deleted atom": s(rho2)}
# real points where every line-deleted Fano atom degenerates
lam = sp.Symbol('lam')
polys = []
for Ldel in range(1, 7):
    Hm = B.remove_line(FANO, Ldel)
    e0 = (0, 0)
    pts = list(range(8))
    vals_a = [B.count(Hm, B.C(t))[0] / 2 for t in pts]
    vals_b = [B.count(Hm, B.C(t), frozenset({e0}))[0] / 2 for t in pts]
    pa = sp.interpolate([(t, sp.Rational(v.numerator, v.denominator)) for t, v in zip(pts, vals_a)], lam)
    pb = sp.interpolate([(t, sp.Rational(v.numerator, v.denominator)) for t, v in zip(pts, vals_b)], lam)
    polys.append(sp.expand((pa + pb) * (pa - pb)))
common = sp.gcd_list(polys)
res["real roots common to every line-deleted Fano atom's degeneracy polynomial"] = [str(r) for r in sp.real_roots(sp.Poly(common, lam))]
# lam = -3: the structure and why the determinant argument does not apply
def pm_count(lines_sub, pts_sub):
    left = list(lines_sub)
    right = {p: k for k, p in enumerate(pts_sub)}
    nb = [[right[p] for p in l[1] if p in right] for l in left]
    memo = {}

    def rec(i, used):
        if i == len(left):
            return 1
        if (i, used) not in memo:
            memo[(i, used)] = sum(rec(i + 1, used | (1 << j)) for j in nb[i] if not used >> j & 1)
        return memo[(i, used)]
    return rec(0, 0)


dimer = {}
for name, H in (("Fano", FANO), ("13-point splice", SPLICE)):
    L = 0
    n = len(H)
    pts_all = sorted({p for l in H for p in l}, key=repr)
    total, unfaithful = 0, 0
    for p in pts_all:
        lines_p = {i for i, l in enumerate(H) if p in l}
        dl = {L} | lines_p
        dp = set(H[L]) | {p}
        rows = [(i, l) for i, l in enumerate(H) if i not in dl]
        cols = [q for q in pts_all if q not in dp]
        pm = pm_count(rows, cols) if len(rows) == len(cols) else 0
        mat = [[1 if q in l else 0 for q in cols] for i, l in rows]
        dt = abs(B.det_exact(mat)) if len(rows) == len(cols) else 0
        total += pm
        unfaithful += pm != dt
    val = B.count(B.remove_line(H, L), B.C(-3))
    dimer[name] = {"M(H - L; -3)": s(val), "2^n sum_p #PM(B - N[L] - N[p])": 2 ** n * total,
                   "points p with #PM != |det|": unfaithful}
res["deficiency one at lam = -3 (left open)"] = dimer
ok = (res["K4^(3) from deficiency-one knot's spaces, lam0 = 2"]["recovered #col"] == "6"
      and set(res["real roots common to every line-deleted Fano atom's degeneracy polynomial"]) <= {"-3", "-1", "0", "1"}
      and all(v["M(H - L; -3)"] == str(v["2^n sum_p #PM(B - N[L] - N[p])"]) and v["points p with #PM != |det|"] > 0 for v in dimer.values()))
check("6 deficiency one: #col(K4^(3)) recovered from counts of knot's spaces minus a line; the line-deleted atoms degenerate together only "
      "at special points; at lam = -3 the count is 2^n sum_p #PM(B - N[L] - N[p]), whose subgraphs are not Pfaffian-faithful (open)", ok, res)

# ------------------------------------------------------------------------------------------------ 7. controls
G = K4
incs = [(i, p) for i, l in enumerate(G) for p in l]
inst = B.with_chains(G, {e: (1 if e in O["K4^(3)"] else 2) for e in incs}, FANO, (0, 0))
controls = {"at lam0 = 0 every oracle value vanishes (no information)": B.count(inst, B.C(0)) == B.ZERO,
            "at lam0 = -3 the normalization (lam0 + 3)/4 vanishes": B.cadd(B.C(-3), B.C(3)) == B.ZERO,
            "at lam0 = 1 every atom has rho = 0": B.csub(B.count(FANO, B.C(1)), B.count(FANO, B.C(1), frozenset({(0, 0)}))) == B.ZERO}
check("7 controls: the reduction degenerates at the special couplings", all(controls.values()), controls)

OUT["seconds"] = round(time.time() - T0, 1)
print("ALL OK", OUT["seconds"], "s")
result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"], "proof": manifest["proof"],
          "status": "passed", "claim": manifest["claim"],
          "checks": {k: {"pass": v["pass"], "info": json.loads(json.dumps(v["info"], default=str))} for k, v in OUT.items() if k != "seconds"}}
for v in result["checks"].values():
    info = v["info"]
    if isinstance(info, dict):
        for k2, v2 in info.items():
            if isinstance(v2, dict):
                v2.pop("seconds", None)
text = json.dumps(result, indent=1, sort_keys=True, default=str) + "\n"
if "--write" in sys.argv:
    (HERE / "result.json").write_text(text)
elif not (HERE / "result.json").exists() or json.loads((HERE / "result.json").read_text()) != json.loads(text):
    print("result.json does not match a fresh run; rerun with --write after review")
    sys.exit(1)
