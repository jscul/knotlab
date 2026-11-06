#!/usr/bin/env python3
"""Check of SURFACE-GLUING-20261024-001A-P001 (standard library only).

A hub-free network of K copies of a three-place relation is a connected multigraph whose nodes are the copies, every node of degree
three counting a loop twice and a boundary leg once; shared distinctions are the internal edges, open distinctions the legs. Its glued
result is the set of leg assignments that extend to the internal edges (with the number of extensions as witness count). Its surface
has Euler characteristic -K and b boundary circles, so genus g = (K - b + 2) / 2, which equals the cycle rank of the multigraph.

The check enumerates every such multigraph with K <= 6 up to isomorphism and, for each of the 16 symmetric three-place relations,
computes glued results and witness counts, groups them by (genus, legs) and decides whether gluing is topological (one profile per
group, symmetric in the legs), as a relation and with counts. It confirms:
- the criterion of Theorem 2: topological exactly when two copies glued along one distinction give a result symmetric in its four legs;
- the formulas of Theorem 3 for parity (total of the legs = K kappa, counts 2^g), for the 'no lone value' relations (on a sphere the
  legs' zero set, or one set, is not a single leg; with a handle everything is allowed; closed genus-g counts tr H^(g-1),
  H = [[3,1],[1,2]]), for the frozen relations, and for all-equal;
- the classification of the 34 knots (three-place relations with every pair of places free): 27 are not symmetric, and the seven
  symmetric ones split as stated.
Controls: a hub (one distinction in three parity copies) fits no surface; the one-copy criterion would wrongly accept not-all-equal;
two-place networks are paths and cycles, and among symmetric two-place relations only equality gives a length-independent result.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
"""

from __future__ import annotations

import itertools
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
KMAX = 6
H = ((3, 1), (1, 2))


# ------------------------------------------------------------------ hub-free networks

def shapes(K):
    """Connected multigraphs on K nodes, all of degree 3 (loops count twice, legs once), up to isomorphism.
    Returned as (multiplicity of each node pair (i, j), i <= j; legs per node)."""
    pairs = [(i, j) for i in range(K) for j in range(i, K)]
    seen, out = set(), []

    def canon(mult, legs):
        best = None
        for perm in itertools.permutations(range(K)):
            inv = [0] * K
            for i in range(K):
                inv[perm[i]] = i
            M = {}
            for (i, j), m in zip(pairs, mult):
                a, b = sorted((perm[i], perm[j]))
                M[(a, b)] = m
            key = (tuple(M.get(p, 0) for p in pairs), tuple(legs[inv[i]] for i in range(K)))
            if best is None or key < best:
                best = key
        return best

    def rec(idx, deg, mult):
        if idx == len(pairs):
            legs = tuple(3 - d for d in deg)
            parent = list(range(K))

            def find(a):
                while parent[a] != a:
                    a = parent[a]
                return a
            for (i, j), m in zip(pairs, mult):
                if m and i != j:
                    parent[find(i)] = find(j)
            if len({find(k) for k in range(K)}) == 1:
                key = canon(mult, legs)
                if key not in seen:
                    seen.add(key)
                    out.append(key)
            return
        i, j = pairs[idx]
        m = 0
        while (deg[i] + 2 * m <= 3) if i == j else (deg[i] + m <= 3 and deg[j] + m <= 3):
            d2 = list(deg)
            if i == j:
                d2[i] += 2 * m
            else:
                d2[i] += m
                d2[j] += m
            rec(idx + 1, d2, mult + [m])
            m += 1
    rec(0, [0] * K, [])
    return [(dict(zip(pairs, mult)), legs) for mult, legs in out]


def glue(allowed, K, shape):
    """allowed(t) for t a 3-tuple; returns Counter: leg assignment -> number of internal extensions."""
    mult, legs = shape
    slots = [[] for _ in range(K)]
    nv = 0
    for (i, j), m in sorted(mult.items()):
        for _ in range(m):
            slots[i].append(nv)
            slots[j].append(nv)
            nv += 1
    internal = nv
    for i in range(K):
        for _ in range(legs[i]):
            slots[i].append(nv)
            nv += 1
    out = Counter()
    for a in itertools.product((0, 1), repeat=nv):
        if all(allowed(tuple(a[v] for v in slots[i])) for i in range(K)):
            out[a[internal:]] += 1
    return out


def genus(K, b):
    return (K - b + 2) // 2


def weight_profile(c, b):
    """value by leg weight if the Counter is symmetric in the legs, else None"""
    by_w = defaultdict(set)
    for t in itertools.product((0, 1), repeat=b):
        by_w[sum(t)].add(c.get(t, 0))
    if any(len(v) > 1 for v in by_w.values()):
        return None
    return tuple(next(iter(by_w[w])) for w in range(b + 1))


def support(c):
    return Counter({t: 1 for t in c})


# ------------------------------------------------------------------ relations

def sym_rel(W):
    return lambda t: sum(t) in W


def pairs_free(R):
    return all(len({(t[i], t[j]) for t in R}) == 4 for i, j in ((0, 1), (0, 2), (1, 2)))


def symmetric_set(R):
    return all(tuple(t[i] for i in p) in R for t in R for p in itertools.permutations(range(3)))


def mat_pow_trace(M, n):
    P = ((1, 0), (0, 1))
    for _ in range(n):
        P = tuple(tuple(sum(P[i][k] * M[k][j] for k in range(2)) for j in range(2)) for i in range(2))
    return P[0][0] + P[1][1]


# ------------------------------------------------------------------ checks

def census(S):
    rows = {}
    for wmask in range(16):
        W = frozenset(w for w in range(4) if wmask >> w & 1)
        groups = defaultdict(set)
        nonsym_support = nonsym_counts = 0
        for K, sl in S.items():
            for sh in sl:
                b = sum(sh[1])
                c = glue(sym_rel(W), K, sh)
                ps, pc = weight_profile(support(c), b), weight_profile(c, b)
                nonsym_support += ps is None
                nonsym_counts += pc is None
                groups[(genus(K, b), b)].add((ps, pc))
        topo_rel = nonsym_support == 0 and all(len({s for s, _ in v}) == 1 for v in groups.values())
        topo_cnt = nonsym_counts == 0 and all(len(v) == 1 for v in groups.values())
        two = glue(sym_rel(W), 2, ({(0, 1): 1}, (2, 2)))
        crit_rel = weight_profile(support(two), 4) is not None
        crit_cnt = weight_profile(two, 4) is not None
        one = glue(sym_rel(W), 1, ({}, (3,)))
        rows[tuple(sorted(W))] = {"topological as a relation": topo_rel, "topological with counts": topo_cnt,
                                  "four-leg criterion (relation)": crit_rel, "four-leg criterion (counts)": crit_cnt,
                                  "one-copy criterion (relation)": weight_profile(support(one), 3) is not None,
                                  "_groups": groups}
    return rows


def parity_formula(S):
    ok = True
    for kappa, W in ((0, frozenset({0, 2})), (1, frozenset({1, 3}))):
        for K, sl in S.items():
            for sh in sl:
                b = sum(sh[1])
                c = glue(sym_rel(W), K, sh)
                g = genus(K, b)
                for t in itertools.product((0, 1), repeat=b):
                    want = 2 ** g if (sum(t) - K * kappa) % 2 == 0 else 0
                    ok &= c.get(t, 0) == want
    return ok


def no_lone_formula(S):
    ok = True
    closed = {}
    for flip, W in ((0, frozenset({0, 1, 3})), (1, frozenset({0, 2, 3}))):
        for K, sl in S.items():
            for sh in sl:
                b = sum(sh[1])
                c = glue(sym_rel(W), K, sh)
                g = genus(K, b)
                for t in itertools.product((0, 1), repeat=b):
                    lone = sum(1 for v in t if v == flip) == 1      # zero set (or one set) is a single leg
                    allowed = (not lone) if g == 0 else True
                    ok &= (c.get(t, 0) > 0) == allowed
                if b == 0:
                    closed.setdefault(g, set()).add(c.get((), 0))
                    ok &= c.get((), 0) == mat_pow_trace(H, g - 1)
    return ok, {g: sorted(v) for g, v in sorted(closed.items())}


def frozen_and_equal(S):
    frozen_ok = True
    witnesses = None
    for W in (frozenset({0, 1, 2}), frozenset({1, 2, 3})):
        seen = {}
        for K, sl in S.items():
            for sh in sl:
                b = sum(sh[1])
                c = glue(sym_rel(W), K, sh)
                if K >= 2:
                    frozen_ok &= len(c) == 2 ** b
                key = (genus(K, b), b)
                prof = weight_profile(c, b)
                if key in seen and seen[key][1] != prof and witnesses is None:
                    witnesses = {"relation": sorted(W), "genus": key[0], "legs": key[1],
                                 "count profiles": [seen[key][1], prof]}
                seen.setdefault(key, (sh, prof))
    eq_ok = True
    for K, sl in S.items():
        for sh in sl:
            b = sum(sh[1])
            c = glue(sym_rel({0, 3}), K, sh)
            want = {(0,) * b: 1 if b else 2, (1,) * b: 1} if b else {(): 2}
            eq_ok &= dict(c) == want
    return frozen_ok, witnesses, eq_ok


def knot_census():
    cube = list(itertools.product((0, 1), repeat=3))
    knots = [frozenset(cube[i] for i in range(8) if m >> i & 1) for m in range(256)]
    knots = [R for R in knots if 0 < len(R) < 8 and pairs_free(R)]
    sym = [R for R in knots if symmetric_set(R)]
    weights = sorted(tuple(sorted({sum(t) for t in R})) for R in sym)
    return len(knots), len(knots) - len(sym), weights


def nae_certificate():
    two = glue(sym_rel({1, 2}), 2, ({(0, 1): 1}, (2, 2)))
    allowed = sorted(t for t in itertools.product((0, 1), repeat=4) if t in two)
    excluded = sorted(t for t in itertools.product((0, 1), repeat=4) if t not in two)
    return {"excluded leg assignments (legs 1-2 on one copy, 3-4 on the other)": [''.join(map(str, t)) for t in excluded],
            "symmetric": weight_profile(support(two), 4) is not None, "allowed count": len(allowed)}


def hub_control():
    """three parity copies sharing one distinction e, each with two legs: not a surface (genus would be -1/2) and the glued
    result has two independent parity constraints, not one."""
    out = Counter()
    for a in itertools.product((0, 1), repeat=7):
        e, legs = a[0], a[1:]
        if all((legs[2 * i] + legs[2 * i + 1] + e) % 2 == 0 for i in range(3)):
            out[legs] += 1
    K, b = 3, 6
    allowed = len(out)
    surface_like = (K - b + 2) % 2 == 0 and allowed == 2 ** (b - 1)
    return {"allowed leg assignments": allowed, "a single parity constraint would allow": 2 ** (b - 1),
            "fits a surface": surface_like}


def two_place():
    """hub-free networks of two-place relations have maximum degree two: paths and cycles. Among symmetric two-place relations,
    the path result is independent of length only for equality (and the trivial relations)."""
    out = {}
    for wmask in range(1, 8):
        W = {w for w in range(3) if wmask >> w & 1}
        results = set()
        for n in range(1, 6):
            rel = set()
            for a in itertools.product((0, 1), repeat=n + 1):
                if all((a[i] + a[i + 1]) in W for i in range(n)):
                    rel.add((a[0], a[-1]))
            results.add(frozenset(rel))
        out[tuple(sorted(W))] = len(results) == 1
    return out


def main() -> int:
    manifest = json.loads((HERE / "manifest.json").read_text())
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "claim": manifest["claim"], "foundation_contract": manifest["foundation_contract"],
              "semantic_domains": manifest["semantic_domains"], "evidence_modes": manifest["evidence_modes"],
              "thesis_alignment": manifest["thesis_alignment"], "safe_conclusions": manifest["safe_to_conclude"]}
    S = {K: shapes(K) for K in range(1, KMAX + 1)}
    rows = census(S)
    criterion_matches = all(r["topological as a relation"] == r["four-leg criterion (relation)"] and
                            r["topological with counts"] == r["four-leg criterion (counts)"] for r in rows.values())
    topo_rel = [list(w) for w, r in rows.items() if r["topological as a relation"]]
    topo_cnt = [list(w) for w, r in rows.items() if r["topological with counts"]]
    par_ok = parity_formula(S)
    nl_ok, closed = no_lone_formula(S)
    frozen_ok, frozen_cert, eq_ok = frozen_and_equal(S)
    nk, nasym, symw = knot_census()
    nae = nae_certificate()
    hub = hub_control()
    tp = two_place()
    controls = {
        "a hub of three parity copies fits no surface": not hub["fits a surface"],
        "the one-copy criterion would accept not-all-equal": rows[(1, 2)]["one-copy criterion (relation)"]
        and not rows[(1, 2)]["topological as a relation"],
        "among symmetric two-place relations only equality and the trivial ones are length-independent":
            [list(w) for w, v in tp.items() if v] == [[0], [0, 1, 2], [0, 2], [2]] or
            sorted([list(w) for w, v in tp.items() if v]) == sorted([[0], [2], [0, 2], [0, 1, 2]]),
    }
    expected_cnt = sorted([[], [0], [0, 2], [1, 3], [0, 1, 3], [0, 2, 3], [0, 3], [3], [0, 1, 2, 3]])
    expected_rel = sorted(expected_cnt + [[0, 1, 2], [1, 2, 3]])
    ok = (criterion_matches and sorted(topo_cnt) == expected_cnt and sorted(topo_rel) == expected_rel and par_ok and nl_ok
          and frozen_ok and frozen_cert is not None and eq_ok and nk == 34 and nasym == 27
          and symw == sorted([(0, 2), (1, 3), (0, 1, 3), (0, 2, 3), (0, 1, 2), (1, 2, 3), (1, 2)])
          and not nae["symmetric"] and all(controls.values()))
    result["checks"] = {
        "shapes per number of copies": {K: len(v) for K, v in S.items()},
        "census by allowed weights": {str(list(w)): {k: v for k, v in r.items() if not k.startswith("_")} for w, r in rows.items()},
        "criterion matches census": criterion_matches,
        "topological as a relation": topo_rel, "topological with counts": topo_cnt,
        "parity formula (legs total = K kappa, counts 2^g)": par_ok,
        "no-lone formula (sphere: lone leg excluded; handle: all allowed; closed counts tr H^(g-1))": nl_ok,
        "no-lone closed-surface counts by genus": closed,
        "frozen relations full once two copies are glued": frozen_ok, "frozen counts certificate": frozen_cert,
        "all-equal glued result": eq_ok,
        "knots": {"total": nk, "not symmetric": nasym, "symmetric (allowed weights)": [list(w) for w in symw]},
        "not-all-equal certificate": nae, "hub control": hub, "two-place relations, length-independent": {str(list(w)): v for w, v in tp.items()},
    }
    result["controls"] = controls
    result["status"] = "passed" if ok else "failed"
    result["failures"] = [] if ok else ["a check or control did not come out as stated in proof.md"]
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(text)
    else:
        old = (HERE / "result.json").read_text() if (HERE / "result.json").exists() else None
        print("result.json matches" if old == text else "result.json differs from a fresh run")
        ok = ok and old == text
    print(json.dumps({"status": result["status"], "topological as a relation": topo_rel, "topological with counts": topo_cnt,
                      "criterion matches": criterion_matches, "closed no-lone counts": closed, "controls": controls,
                      "frozen certificate": frozen_cert, "nae": nae, "hub": hub, "two-place": {str(k): v for k, v in tp.items()}},
                     indent=1, default=str))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
