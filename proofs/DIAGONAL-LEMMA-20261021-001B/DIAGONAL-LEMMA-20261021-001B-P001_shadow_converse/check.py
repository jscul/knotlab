#!/usr/bin/env python3
"""Checks for DIAGONAL-LEMMA-20261021-001B-P001. The statements are in proof.md.

Circuits are relative to each variable's range, as in KNOT-CIRCUITS-20261020-001B-P001. Systems are conjunctions
of copies with any identification of variables (single-sorted) unless stated.

Checks:
- Theorem 1 (shadows). For the named products K6 = (x+y+z=0 over Z3) x (not exactly two ones) on 6 values and
  K4x4 = (x+y+z+w=0 over Z2) x (the same plus 1000) on 4 values, and for 9 random shadows over Z3, GF(4) and
  4-ary Z2: in random systems the product's constrained sets equal M's and no two circuits fail elimination.
- Theorem 2 (lifts). For K4 = (x+y+z=0 over Z3 with the value 2 doubled) minus (2,2,2), and the same lift of
  z = wx + w^2 y over GF(4): in random systems the constrained sets equal M's, ranges lose the doubled value
  exactly at pinned variables, and no two circuits fail elimination.
- Corollary 3. K6, K4 and K4x4 are non-rectangular knots with no direct case and no fibre-distance case; no
  diagonal derivation of K6 or K4 has a direct case.
- Theorem 4 (fibre distance). On random sparse knots where it applies, the composed relation is a knot whose
  fibres pairwise meet, and two copies sharing the variable fail elimination.
- Remark 5. Without full ranges the product of parity with the Boolean neither-knot fails (single-sorted); in
  positional systems it has parity's constrained sets.
- Remark 6. Without the identification hypothesis, the lift of 4-ary parity fails between ties.
- Census candidates: recorded failures for four lifted knots with other blocks, the fibre-distance failure of
  the inner factor x+y+z=0 plus {001, 010}, and a failure of the dihedral action with shared point variables.
- Census agreement with DIAGONAL-LEMMA-20261021-001A-E001.

Controls, each of which must be rejected:
- 'composing knots like cycles forces rectangular knots' (K4);
- 'the diagonal derivation resolves every knot with neither direct case' (K4);
- 'the full-range hypothesis of Theorem 1 can be dropped' (single-sorted parity x neither-knot);
- 'the identification hypothesis of Theorem 2 can be dropped' (lifted 4-ary parity);
- 'a shadow composes like cycles because its inner factor does' (not exactly two ones fails alone).

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json
"""

from __future__ import annotations

import json
import random
import sys
from itertools import combinations, permutations, product
from math import prod
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CENSUS = ROOT / "artifacts" / "DIAGONAL-LEMMA-20261021-001A" / "DIAGONAL-LEMMA-20261021-001A-E001_diagonal_census"

GF4_MUL = [[0, 0, 0, 0], [0, 1, 2, 3], [0, 2, 3, 1], [0, 3, 1, 2]]
M3 = {t for t in product(range(3), repeat=3) if sum(t) % 3 == 0}
M4 = {t for t in product(range(2), repeat=4) if sum(t) % 2 == 0}
MGF4 = {(x, y, GF4_MUL[2][x] ^ GF4_MUL[3][y]) for x in range(4) for y in range(4)}
PARITY = {t for t in product(range(2), repeat=3) if sum(t) % 2 == 0}
NEITHER = {(0, 0, 0), (0, 1, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)}
NOT_TWO = {t for t in product(range(2), repeat=3) if sum(t) != 2}


# ------------------------------------------------------------------ relations and systems

def proj(S, Y):
    return {tuple(t[i] for i in Y) for t in S}


def solve(R, doms, cons):
    n = len(doms)
    order = []
    for c in cons:
        for v in c:
            if v not in order:
                order.append(v)
    order += [v for v in range(n) if v not in order]
    pos = {v: i for i, v in enumerate(order)}
    check_at = {}
    for c in cons:
        check_at.setdefault(max(pos[v] for v in c), []).append(c)
    out, a = [], [None] * n

    def go(i):
        if i == n:
            out.append(tuple(a))
            return
        v = order[i]
        for x in doms[v]:
            a[v] = x
            if all(tuple(a[w] for w in c) in R for c in check_at.get(i, ())):
                go(i + 1)
        a[v] = None

    go(0)
    return out


def constrained_fn(S, n):
    rg = [len({t[i] for t in S}) for i in range(n)]
    memo = {}

    def f(Y):
        Y = tuple(sorted(Y))
        if Y not in memo:
            memo[Y] = len(proj(S, Y)) < prod(rg[i] for i in Y)
        return memo[Y]

    return f


def all_subsets(n):
    return [Y for size in range(1, n + 1) for Y in combinations(range(n), size)]


def failure(S, n, knots_only):
    if not S:
        return None
    f = constrained_fn(S, n)
    found = []
    for Y in all_subsets(n):
        if not any(set(C) <= set(Y) for C in found) and f(Y):
            found.append(Y)
    for C1, C2 in combinations(found, 2):
        if knots_only and min(len(C1), len(C2)) < 3:
            continue
        for e in sorted(set(C1) & set(C2)):
            if not f(tuple(sorted((set(C1) | set(C2)) - {e}))):
                return {"C1": list(C1), "C2": list(C2), "e": e}
    return None


def verify_failure(R, doms, cons, w):
    S = solve(R, doms, [tuple(c) for c in cons])
    n = len(doms)
    f = constrained_fn(S, n)

    def circuit(C):
        return f(C) and all(not f(tuple(x for x in C if x != v)) for v in C)

    return bool(S) and circuit(tuple(w["C1"])) and circuit(tuple(w["C2"])) and \
        not f(tuple(sorted((set(w["C1"]) | set(w["C2"])) - {w["e"]})))


def same_constrained_sets(SA, SB, n):
    fa, fb = constrained_fn(SA, n), constrained_fn(SB, n)
    return all(fa(Y) == fb(Y) for Y in all_subsets(n))


def random_system(rng, k, nmax, cmax=5):
    while True:
        n = rng.randint(k, nmax)
        cons = [tuple(rng.randrange(n) for _ in range(k)) for _ in range(rng.randint(1, cmax))]
        if len({v for c in cons for v in c}) == n:
            return n, cons


def is_knot(K, k):
    rg = [len({t[i] for t in K}) for i in range(k)]
    if k < 3 or min(rg) < 2:
        return False
    return all(len(proj(K, Y)) == prod(rg[i] for i in Y) for Y in combinations(range(k), k - 1)) and len(K) < prod(rg)


def fibres(K, e):
    g = {}
    for t in K:
        g.setdefault(t[:e] + t[e + 1:], set()).add(t[e])
    return {key: frozenset(v) for key, v in g.items()}


def rectangular(K, k):
    for e in range(k):
        fs = set(fibres(K, e).values())
        if any(a != b and a & b for a in fs for b in fs):
            return False
    return True


def direct_case(K, k):
    for e in range(k):
        g = fibres(K, e)
        others = [i for i in range(k) if i != e]
        for size in range(k - 1):
            for T in combinations(range(k - 1), size):
                groups = {}
                for rest, f in g.items():
                    groups.setdefault(tuple(rest[p] for p in T), []).append(f)
                if all(all(a & b for a in grp for b in grp) for grp in groups.values()):
                    return {"e": e, "T": [others[p] for p in T]}
    return None


def composed(K, k, e, steps):
    """K_steps(y, e) = exists h: K(y, h) and R^steps(h, e), R(h, h') = exists y': K(y', h) and K(y', h')."""
    fib = fibres(K, e)
    share = {(a, b) for f in fib.values() for a in f for b in f}
    rel = {(a, a) for f in fib.values() for a in f}
    for _ in range(steps):
        rel = {(a, c) for (a, b) in rel for (b2, c) in share if b == b2}
    return {rest[:e] + (c,) + rest[e:] for rest, f in fib.items() for c in {c for (a, c) in rel if a in f}}


def fibre_distance(K, k):
    for e in range(k):
        dom = {t[e] for t in K}
        for steps in range(1, len(dom) + 1):
            C = composed(K, k, e, steps)
            fs = list(set(fibres(C, e).values()))
            if all(a & b for a in fs for b in fs):
                if any(len(f) < len(dom) for f in fs):
                    return {"e": e, "steps": steps}
                break
    return None


def two_copies_fail(K, k, shared, e):
    rg = [sorted({t[i] for t in K}) for i in range(k)]
    second, nxt = [], k
    for p in range(k):
        if p in shared:
            second.append(p)
        else:
            second.append(nxt)
            nxt += 1
    doms = rg + [rg[p] for p in range(k) if p not in shared]
    return verify_failure(K, doms, [tuple(range(k)), tuple(second)], {"C1": list(range(k)), "C2": sorted(second), "e": e})


def diagonal(K, q):
    return {(a, b, c) for a in range(q) for b in range(q) for c in range(q)
            if any((a, a, h) in K and (b, c, h) in K for h in range(q))}


def diagonal_case(K, q):
    for pm in permutations(range(3)):
        D = diagonal({tuple(t[pm[i]] for i in range(3)) for t in K}, q)
        if is_knot(D, 3) and direct_case(D, 3):
            return list(pm)
    return None


def product_relation(M, K, qb):
    return {tuple(a * qb + b for a, b in zip(s, t)) for s in M for t in K}


def lift(M, qm, a):
    """Double the value a (its copy is qm), then remove the constant tuple (a, ..., a)."""
    g = list(range(qm)) + [a]
    k = len(next(iter(M)))
    K = {t for t in product(range(qm + 1), repeat=k) if tuple(g[x] for x in t) in M}
    return K - {(a,) * k}, g


def profile(K, k, q):
    return {"knot": is_knot(K, k), "rectangular": rectangular(K, k), "direct_case": direct_case(K, k) is not None,
            "fibre_distance": fibre_distance(K, k) is not None,
            "diagonal_resolves": (diagonal_case(K, q) is not None) if k == 3 else None}


# ------------------------------------------------------------------ the checks

def run():
    checks, controls, failures = {}, {}, []
    rng = random.Random(20261021)

    # Theorem 1: products
    named = {"K6": (M3, 3, NOT_TWO, 2, 3), "K4x4": (M4, 2, M4 | {(1, 0, 0, 0)}, 2, 4)}
    thm1 = {}
    for name, (M, qm, inner, qb, k) in named.items():
        K = product_relation(M, inner, qb)
        q = qm * qb
        row = {"values": q, "variables": k, **profile(K, k, q), "systems": 0, "equal_to_M": 0, "failures": 0}
        nmax = 5 if k == 3 else 6
        while row["systems"] < 400:
            n, cons = random_system(rng, k, nmax)
            SK = solve(K, [list(range(q))] * n, cons)
            SM = solve(M, [list(range(qm))] * n, cons)
            row["systems"] += 1
            row["equal_to_M"] += same_constrained_sets(SK, SM, n)
            row["failures"] += failure(SK, n, knots_only=False) is not None
        thm1[name] = row
    random_shadows = {"shadows": 0, "systems": 0, "equal_to_M": 0, "failures": 0}
    for M, qm, k in ((M3, 3, 3), (MGF4, 4, 3), (M4, 2, 4)):
        for _ in range(3):
            while True:
                if qm == 2:
                    h = [0, 1]
                else:
                    h = [rng.randrange(2) for _ in range(qm)]
                    if len(set(h)) < 2:
                        continue
                inner = {tuple(h[x] for x in t) for t in M}
                pool = [t for t in product(range(2), repeat=k) if t not in inner]
                inner |= set(rng.sample(pool, min(rng.randint(0, 2), len(pool))))
                K = product_relation(M, inner, 2)
                if len(inner) < 2 ** k and is_knot(K, k) and not rectangular(K, k):
                    break
            random_shadows["shadows"] += 1
            q = 2 * qm
            for _ in range(100):
                n, cons = random_system(rng, k, 5 if q <= 6 else 4)
                SK = solve(K, [list(range(q))] * n, cons)
                SM = solve(M, [list(range(qm))] * n, cons)
                random_shadows["systems"] += 1
                random_shadows["equal_to_M"] += same_constrained_sets(SK, SM, n)
                random_shadows["failures"] += failure(SK, n, knots_only=False) is not None
    thm1["random_shadows"] = random_shadows
    checks["theorem_1_shadows"] = thm1
    if any(r["equal_to_M"] != r["systems"] or r["failures"] for r in thm1.values()):
        failures.append("Theorem 1")

    # Theorem 2: lifts
    thm2 = {}
    for name, (M, qm, a) in {"K4 (Z3, 2 doubled)": (M3, 3, 2), "GF(4), 1 doubled": (MGF4, 4, 1)}.items():
        K, g = lift(M, qm, a)
        q = qm + 1
        row = {"values": q, **profile(K, 3, q), "systems": 0, "equal_to_M": 0, "pinned_ranges_ok": 0, "failures": 0}
        nmax = 6 if q == 4 else 5
        while row["systems"] < 500:
            n, cons = random_system(rng, 3, nmax, 6)
            SK = solve(K, [list(range(q))] * n, cons)
            SM = solve(M, [list(range(qm))] * n, cons)
            row["systems"] += 1
            row["equal_to_M"] += same_constrained_sets(SK, SM, n)
            pinned = {c[0] for c in cons if c[0] == c[1] == c[2]}
            row["pinned_ranges_ok"] += all({t[v] for t in SK} == (set(range(q)) - {a} if v in pinned else set(range(q)))
                                           for v in range(n))
            row["failures"] += failure(SK, n, knots_only=False) is not None
        thm2[name] = row
    checks["theorem_2_lifts"] = thm2
    if any(r["equal_to_M"] != r["systems"] or r["pinned_ranges_ok"] != r["systems"] or r["failures"] for r in thm2.values()):
        failures.append("Theorem 2")

    # Corollary 3: the counterexamples
    cor3 = {"K6": {k2: thm1["K6"][k2] for k2 in ("knot", "rectangular", "direct_case", "fibre_distance", "diagonal_resolves")},
            "K4": {k2: thm2["K4 (Z3, 2 doubled)"][k2] for k2 in ("knot", "rectangular", "direct_case", "fibre_distance", "diagonal_resolves")},
            "K4x4": {k2: thm1["K4x4"][k2] for k2 in ("knot", "rectangular", "direct_case", "fibre_distance")}}
    checks["corollary_3_counterexamples"] = cor3
    if not all(v["knot"] and not v["rectangular"] and not v["direct_case"] and not v["fibre_distance"]
               and not v.get("diagonal_resolves") for v in cor3.values()):
        failures.append("Corollary 3")

    # Theorem 4: fibre distance
    thm4 = {"knots": 0, "composed_knot_with_meeting_fibres": 0, "two_copies_fail": 0, "steps": {}}
    tries = 0
    while thm4["knots"] < 30 and tries < 200000:
        tries += 1
        q = rng.choice((5, 6))
        p = rng.uniform(0.15, 0.5)
        K = {t for t in product(range(q), repeat=3) if rng.random() < p}
        if not is_knot(K, 3) or rectangular(K, 3):
            continue
        fd = fibre_distance(K, 3)
        if not fd:
            continue
        thm4["knots"] += 1
        thm4["steps"][str(fd["steps"])] = thm4["steps"].get(str(fd["steps"]), 0) + 1
        C = composed(K, 3, fd["e"], fd["steps"])
        fs = list(set(fibres(C, fd["e"]).values()))
        thm4["composed_knot_with_meeting_fibres"] += is_knot(C, 3) and all(a & b for a in fs for b in fs)
        thm4["two_copies_fail"] += two_copies_fail(C, 3, {fd["e"]}, fd["e"])
    thm4["neither_knot_not_covered"] = fibre_distance(NEITHER, 3) is None
    checks["theorem_4_fibre_distance"] = thm4
    if not thm4["knots"] or thm4["two_copies_fail"] != thm4["knots"] or \
            thm4["composed_knot_with_meeting_fibres"] != thm4["knots"] or not thm4["neither_knot_not_covered"]:
        failures.append("Theorem 4")

    # Remark 5: full ranges
    PKB = product_relation(PARITY, NEITHER, 2)
    single = verify_failure(PKB, [list(range(4))] * 6, [(1, 1, 4), (1, 0, 5), (1, 3, 2), (2, 5, 0)],
                            {"C1": [0, 1, 3], "C2": [0, 1, 5], "e": 1})
    positional = {"systems": 0, "no_constant_parity_variable": 0, "equal_to_parity": 0, "failures": 0}
    while positional["systems"] < 300:
        m = rng.randint(2, 3)
        cons = [tuple(p * m + rng.randrange(m) for p in range(3)) for _ in range(rng.randint(1, 6))]
        used = sorted({v for c in cons for v in c})
        idx = {v: i for i, v in enumerate(used)}
        cons = [tuple(idx[v] for v in c) for c in cons]
        n = len(used)
        SP = solve(PARITY, [[0, 1]] * n, cons)
        SK = solve(PKB, [list(range(4))] * n, cons)
        positional["systems"] += 1
        positional["no_constant_parity_variable"] += all(len({t[v] for t in SP}) == 2 for v in range(n))
        positional["equal_to_parity"] += same_constrained_sets(SK, SP, n)
        positional["failures"] += failure(SK, n, knots_only=False) is not None
    checks["remark_5_full_ranges"] = {"single_sorted_failure_between_knots": single, "positional": positional}
    if not single or positional["no_constant_parity_variable"] != positional["systems"] or \
            positional["equal_to_parity"] != positional["systems"] or positional["failures"]:
        failures.append("Remark 5")

    # Remark 6: the identification hypothesis
    L4p, _ = lift(M4, 2, 1)
    tie_failure = verify_failure(L4p, [list(range(3))] * 3, [(1, 0, 0, 1), (0, 1, 1, 2), (2, 0, 2, 2)], {"C1": [0, 1], "C2": [0, 2], "e": 0})
    knot_failures = 0
    for _ in range(1500):
        n, cons = random_system(rng, 4, 5)
        knot_failures += failure(solve(L4p, [list(range(3))] * n, cons), n, knots_only=True) is not None
    checks["remark_6_identifications"] = {"lifted_4ary_parity_knot": is_knot(L4p, 4) and not rectangular(L4p, 4),
                                          "failure_between_ties": tie_failure, "sampled_systems": 1500,
                                          "failures_between_knots_observed": knot_failures}
    if not tie_failure:
        failures.append("Remark 6")

    # census candidates resolved
    def lifted_block(Rbits):
        g = (0, 1, 2, 2)
        return {t for t in product(range(4), repeat=3) if tuple(g[x] for x in t) in M3 and
                (tuple(g[x] for x in t) != (2, 2, 2) or tuple(int(x == 3) for x in t) in Rbits)}

    witnesses = {
        "odd parity block": ({(0, 0, 1), (0, 1, 0), (1, 0, 0), (1, 1, 1)}, [(4, 3, 0), (4, 1, 2), (1, 1, 1), (2, 5, 3)], {"C1": [0, 1, 5], "C2": [0, 2, 5], "e": 0}),
        "neither-knot block": (NEITHER, [(3, 2, 1), (0, 5, 4), (2, 1, 3), (4, 3, 3), (0, 5, 3)], {"C1": [0, 1, 2], "C2": [1, 2, 4], "e": 1}),
        "NAE block": ({t for t in product(range(2), repeat=3) if len(set(t)) > 1}, [(4, 3, 0), (5, 1, 2), (5, 2, 3), (3, 0, 4), (4, 4, 4), (2, 2, 2)], {"C1": [0, 2, 5], "C2": [0, 4, 5], "e": 0}),
        "even parity block": (PARITY, [(4, 4, 4), (1, 0, 0), (4, 1, 2), (3, 5, 2)], {"C1": [0, 3, 5], "C2": [3, 4, 5], "e": 3}),
    }
    cand = {name: verify_failure(lifted_block(Rb), [list(range(4))] * 6, cons, w) for name, (Rb, cons, w) in witnesses.items()}
    cand["all-but-000 block equals K4"] = lifted_block(set(product(range(2), repeat=3)) - {(0, 0, 0)}) == lift(M3, 3, 2)[0]
    inner = M3 | {(0, 0, 1), (0, 1, 0)}
    fd = fibre_distance(inner, 3)
    cand["inner factor x+y+z=0 plus {001, 010}: fibre distance fails"] = bool(fd) and \
        two_copies_fail(composed(inner, 3, fd["e"], fd["steps"]), 3, {fd["e"]}, fd["e"])
    gens = [(1, 2, 3, 0), (0, 3, 2, 1)]
    G = {tuple(range(4))}
    frontier = list(G)
    while frontier:
        x = frontier.pop()
        for s in gens:
            y = tuple(s[x[i]] for i in range(4))
            if y not in G:
                G.add(y)
                frontier.append(y)
    D4 = sorted(G)
    KD4 = {(u, gi, p[u]) for gi, p in enumerate(D4) for u in range(4)}
    cand["dihedral action with shared point variables fails"] = verify_failure(
        KD4, [list(range(4))] * 4 + [list(range(8))] * 2, [(2, 4, 0), (1, 5, 2), (1, 4, 3), (0, 5, 3), (1, 5, 2)],
        {"C1": [0, 1, 4], "C2": [0, 2, 4], "e": 4})
    checks["census_candidates"] = cand
    if not all(cand.values()):
        failures.append("census candidates")

    census = {}
    if (CENSUS / "result.json").exists():
        a = json.loads((CENSUS / "result.json").read_text())
        census = {"predictions": a["predictions"],
                  "shadows_equal_and_failure_free": all(s["equal_to_M"] == s["systems"] and s["product_failures"] == 0
                                                        for s in a["summary"]["shadows"])}
        if not (a["predictions"]["L1"] and a["predictions"]["L2"] and a["predictions"]["L3"] and census["shadows_equal_and_failure_free"]):
            failures.append("census agreement")
    checks["census_agreement"] = census

    K4 = lift(M3, 3, 2)[0]
    controls["composing_knots_like_cycles_forces_rectangular_knots"] = {
        "K4_rectangular": rectangular(K4, 3), "K4_failures_in_sampled_systems": thm2["K4 (Z3, 2 doubled)"]["failures"],
        "rejected": not rectangular(K4, 3) and thm2["K4 (Z3, 2 doubled)"]["failures"] == 0}
    controls["diagonal_derivation_resolves_every_neither_knot"] = {
        "K4_direct_case": thm2["K4 (Z3, 2 doubled)"]["direct_case"], "K4_diagonal": thm2["K4 (Z3, 2 doubled)"]["diagonal_resolves"],
        "rejected": not thm2["K4 (Z3, 2 doubled)"]["direct_case"] and not thm2["K4 (Z3, 2 doubled)"]["diagonal_resolves"]}
    controls["full_range_hypothesis_can_be_dropped"] = {"rejected": single}
    controls["identification_hypothesis_can_be_dropped"] = {"rejected": tie_failure}
    inner_fail = None
    for _ in range(3000):
        n, cons = random_system(rng, 3, 5)
        inner_fail = failure(solve(NOT_TWO, [[0, 1]] * n, cons), n, knots_only=False)
        if inner_fail:
            break
    controls["shadow_composes_because_its_inner_factor_does"] = {"inner_failure": inner_fail, "rejected": inner_fail is not None}
    for name, control in controls.items():
        if not control["rejected"]:
            failures.append(f"control not rejected: {name}")
    return checks, controls, failures


def main() -> int:
    write = "--write" in sys.argv[1:]
    checks, controls, failures = run()
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {
        "schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
        "proof": manifest["proof"], "status": "passed" if not failures else "failed", "claim": manifest["claim"],
        "foundation_contract": manifest["foundation_contract"], "semantic_domains": manifest["semantic_domains"],
        "evidence_modes": manifest["evidence_modes"], "thesis_alignment": manifest["thesis_alignment"],
        "safe_conclusions": manifest["safe_to_conclude"], "checks": checks, "controls": controls, "failures": failures,
    }
    path = HERE / "result.json"
    text = json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n"
    if write:
        path.write_text(text)
    elif not path.exists() or json.loads(path.read_text()) != json.loads(text):
        print("result.json does not match a fresh run; rerun with --write after review")
        return 1
    print(f"{result['status']}: failures {failures}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
