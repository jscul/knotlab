#!/usr/bin/env python3
"""Checks for BASE-CRITICALITY-20261022-001A-P001. The statements are in proof.md.

A world: a finite multigraph, a not-all-equal relation NAE(h_u, x_e, h_v) on every edge, hidden joints h, visible
spokes x drawn uniformly. tau = h xor g recolours it for any two-colouring g of the vertices.

Checks:
- Theorem 1 (recolouring). On an odd cycle, K4, the prism, the 3 x 3 torus and a 3 x 2 torus with a double edge, for
  several colourings g and every spoke pattern: the world is consistent exactly when its recoloured instance is, and the
  recoloured instance has an implication on every bichromatic edge whose direction is set by the spoke and a monotone
  two-literal clause on every monochromatic edge, each spoke value giving each form once.
- Theorem 2 (exploration coupling). On the 2 x 3 grid, K4 and the 3 x 2 cylinder, the reach set of a vertex set over all
  uniform orientations has exactly the distribution of its bond-percolation cluster at 1/2 over all edge subsets. With
  gadgets on a triangle and a 4-cycle (parallel pairs, triples, series of three edges, series of three parallel pairs),
  the reach set within the base graph has exactly, in rational arithmetic, the distribution of percolation at the
  gadget's traversal probability; the traversal and two-way probabilities of each gadget match their formulas.
- Theorem 3 (blocking). On the cut-open 3 x 2, 5 x 2 and 3 x 4 tori with one odd side (every spoke pattern on the
  first two, 200,000 sampled on the third): whenever no directed path joins the bottom side to the top side in one of
  the two directions, the world is consistent; worlds with directed paths both ways can be consistent or not, and both
  occur.

Controls, each of which must be rejected:
- 'the reach set has the law of percolation at 2/5' (a wrong parameter);
- 'the recolouring orients each edge from the endpoint whose colour equals the spoke' (a wrong rule);
- 'a world with directed paths both ways is never consistent' (the converse of Theorem 3);
- 'the consistency test accepts a world with an unsatisfiable seam' (the solver on a wrong input).

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json
"""

from __future__ import annotations

import json
import random
import sys
from collections import Counter, deque
from fractions import Fraction as F
from itertools import product
from pathlib import Path

HERE = Path(__file__).resolve().parent

NAE = [((0, 1), (1, 1)), ((1, 1), (1, 0))]     # spoke 0 forbids (0, 0); spoke 1 forbids (1, 1)


# ------------------------------------------------------------------ consistency of binary relations on bits

def consistent(nv, edges, mats):
    """Limited backtracking (Even, Itai and Shamir): exact for binary relations on bits."""
    adj = [[] for _ in range(nv)]
    for k, (u, v) in enumerate(edges):
        adj[u].append((v, k, 0))
        adj[v].append((u, k, 1))
    val = [None] * nv

    def propagate(start, a, changed):
        val[start] = a
        changed.append(start)
        stack = [start]
        while stack:
            u = stack.pop()
            for w, k, side in adj[u]:
                M = mats[k]
                allowed = [c for c in (0, 1) if (M[val[u]][c] if side == 0 else M[c][val[u]])]
                if val[w] is None:
                    if not allowed:
                        return False
                    if len(allowed) == 1:
                        val[w] = allowed[0]
                        changed.append(w)
                        stack.append(w)
                elif val[w] not in allowed:
                    return False
        return True

    for v in range(nv):
        if val[v] is not None:
            continue
        for a in (0, 1):
            changed = []
            if propagate(v, a, changed):
                break
            for w in changed:
                val[w] = None
        else:
            return False
    return True


def recoloured(edges, g, x, rule="correct"):
    """The recoloured instance as tables on (tau_u, tau_v), and the form of each edge."""
    mats, forms = [], []
    for (u, v), xe in zip(edges, x):
        if g[u] != g[v]:
            tail_is_u = (g[u] == 1 - xe) if rule == "correct" else (g[u] == xe)
            # arc u -> v: tau_u = 1 forces tau_v = 1, so (1, 0) is forbidden; arc v -> u forbids (0, 1)
            M = ((1, 1), (0, 1)) if tail_is_u else ((1, 0), (1, 1))
            forms.append("arc u->v" if tail_is_u else "arc v->u")
        else:
            c = xe ^ g[u]
            M = ((0, 1), (1, 1)) if c == 0 else ((1, 1), (1, 0))
            forms.append("clause both-not-0" if c == 0 else "clause both-not-1")
        mats.append(M)
    return mats, forms


def torus(a, b):
    idx = lambda i, j: (i % a) * b + (j % b)
    edges = [(idx(i, j), idx(i + 1, j)) for i in range(a) for j in range(b)]
    edges += [(idx(i, j), idx(i, j + 1)) for i in range(a) for j in range(b)]
    return a * b, edges


# ------------------------------------------------------------------ reach and percolation

def reach(nv, arcs, sources):
    out = [[] for _ in range(nv)]
    for u, v in arcs:
        out[u].append(v)
    seen = set(sources)
    dq = deque(sources)
    while dq:
        w = dq.popleft()
        for z in out[w]:
            if z not in seen:
                seen.add(z)
                dq.append(z)
    return frozenset(seen)


def cluster(nv, open_edges, sources):
    return reach(nv, [(u, v) for u, v in open_edges] + [(v, u) for u, v in open_edges], sources)


def decorate(nv, edges, blocks):
    """Replace every edge by a series of blocks, a block being a number of parallel edges. Returns the decorated graph
    and, for each base edge, its terminal pair."""
    out, n = [], nv
    for (u, v) in edges:
        chain = [u] + list(range(n, n + len(blocks) - 1)) + [v]
        n += len(blocks) - 1
        for k, par in enumerate(blocks):
            out += [(chain[k], chain[k + 1])] * par
    return n, out


def gadget_probabilities(blocks):
    n, es = decorate(2, [(0, 1)], blocks)
    fwd = both = 0
    for bits in product((0, 1), repeat=len(es)):
        arcs = [(u, v) if b else (v, u) for (u, v), b in zip(es, bits)]
        f = 1 in reach(n, arcs, [0])
        r = 0 in reach(n, arcs, [1])
        fwd += f
        both += f and r
    total = 2 ** len(es)
    return F(fwd, total), F(both, total)


# ------------------------------------------------------------------ the checks

def run():
    checks, controls, failures = {}, {}, []
    rng = random.Random("base-criticality-reduction")

    # Theorem 1: recolouring on several graphs and colourings
    graphs = {
        "C5": (5, [(i, (i + 1) % 5) for i in range(5)]),
        "K4": (4, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]),
        "prism": (6, [(0, 1), (1, 2), (0, 2), (3, 4), (4, 5), (3, 5), (0, 3), (1, 4), (2, 5)]),
        "torus 3x3": torus(3, 3),
        "torus 3x2 with a double edge": (lambda t: (t[0], t[1] + [t[1][0]]))(torus(3, 2)),
    }
    recol = {}
    for name, (nv, edges) in graphs.items():
        colourings = [[0] * nv, [v % 2 for v in range(nv)], [rng.randrange(2) for _ in range(nv)]]
        agree = forms_ok = cases = 0
        patterns = list(product((0, 1), repeat=len(edges))) if len(edges) <= 18 else \
            [tuple(rng.randrange(2) for _ in edges) for _ in range(40000)]
        for g in colourings:
            for x in patterns:
                cases += 1
                direct = consistent(nv, edges, [NAE[xe] for xe in x])
                mats, forms = recoloured(edges, g, x)
                agree += direct == consistent(nv, edges, mats)
            # each spoke value gives each form once on every edge
            for (u, v) in edges:
                f0 = recoloured([(u, v)], g, (0,))[1][0]
                f1 = recoloured([(u, v)], g, (1,))[1][0]
                forms_ok += f0 != f1
        recol[name] = {"cases": cases, "agree": agree, "edge_form_pairs_distinct": forms_ok,
                       "edge_colourings": len(edges) * len(colourings)}
    checks["theorem_1_recolouring"] = recol
    if not all(v["agree"] == v["cases"] and v["edge_form_pairs_distinct"] == v["edge_colourings"] for v in recol.values()):
        failures.append("Theorem 1")

    # Theorem 2: exploration coupling, plain edges (exact counts) and gadgets (exact rationals)
    plain = {}
    for name, (nv, edges, src) in {"grid 2x3": (6, [(0, 1), (1, 2), (3, 4), (4, 5), (0, 3), (1, 4), (2, 5)], [0]),
                                   "K4": (4, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)], [0]),
                                   "cylinder 3x2 from the bottom": (6, [(0, 2), (1, 3), (2, 4), (3, 5), (0, 1), (1, 0), (2, 3), (3, 2), (4, 5), (5, 4)], [0, 1])}.items():
        orient = Counter()
        perc = Counter()
        for bits in product((0, 1), repeat=len(edges)):
            orient[reach(nv, [(u, v) if b else (v, u) for (u, v), b in zip(edges, bits)], src)] += 1
            perc[cluster(nv, [e for e, b in zip(edges, bits) if b], src)] += 1
        plain[name] = {"configurations": 2 ** len(edges), "distinct_sets": len(orient), "laws_equal": orient == perc}
    gadgets = {}
    for blocks in ([2], [3], [1, 1, 1], [2, 2, 2]):
        p, pb = gadget_probabilities(blocks)
        formula = F(1)
        for k in blocks:
            formula *= 1 - F(1, 2 ** k)
        both_formula = (1 - F(2, 2 ** blocks[0])) if len(blocks) == 1 else None
        gadgets[str(blocks)] = {"traversal": str(p), "formula": str(formula), "two_way": str(pb),
                                "traversal_matches": p == formula,
                                "two_way_matches": both_formula is None or pb == both_formula}
    deco = {}
    for name, (nv, edges, src, blocks) in {"triangle, parallel pairs": (3, [(0, 1), (1, 2), (0, 2)], [0], [2]),
                                           "4-cycle, parallel triples": (4, [(0, 1), (1, 2), (2, 3), (3, 0)], [0], [3]),
                                           "triangle, series of three": (3, [(0, 1), (1, 2), (0, 2)], [0], [1, 1, 1]),
                                           "triangle, series of three pairs": (3, [(0, 1), (1, 2), (0, 2)], [0], [2, 2, 2])}.items():
        n, es = decorate(nv, edges, blocks)
        law = Counter()
        for bits in product((0, 1), repeat=len(es)):
            arcs = [(u, v) if b else (v, u) for (u, v), b in zip(es, bits)]
            law[frozenset(w for w in reach(n, arcs, src) if w < nv)] += 1
        total = 2 ** len(es)
        p, _ = gadget_probabilities(blocks)
        target = Counter()
        for bits in product((0, 1), repeat=len(edges)):
            weight = F(1)
            for b in bits:
                weight *= p if b else 1 - p
            target[cluster(nv, [e for e, b in zip(edges, bits) if b], src)] += weight
        deco[name] = {"oriented_edges": len(es), "laws_equal": all(F(law[s], total) == target[s] for s in set(law) | set(target))}
    checks["theorem_2_exploration_coupling"] = {"plain": plain, "gadgets": gadgets, "decorated": deco}
    if not (all(v["laws_equal"] for v in plain.values()) and all(v["traversal_matches"] and v["two_way_matches"] for v in gadgets.values())
            and all(v["laws_equal"] for v in deco.values())):
        failures.append("Theorem 2")

    # Theorem 3: blocking on cut-open tori with one odd side
    block = {}
    for a, b, sample in ((3, 2, None), (5, 2, None), (3, 4, 200000)):
        nv, edges = torus(a, b)
        g = [((v // b) + (v % b)) % 2 for v in range(nv)]
        seam = [g[u] == g[v] for u, v in edges]
        bottom = [v for v in range(nv) if v // b == 0]
        top = [v for v in range(nv) if v // b == a - 1]
        stats = Counter()
        patterns = product((0, 1), repeat=len(edges)) if sample is None else \
            (tuple(rng.randrange(2) for _ in edges) for _ in range(sample))
        for x in patterns:
            ok = consistent(nv, edges, [NAE[xe] for xe in x])
            arcs = []
            for (u, v), s, xe in zip(edges, seam, x):
                if s:
                    continue
                arcs.append((u, v) if g[u] == 1 - xe else (v, u))
            up = bool(reach(nv, arcs, bottom) & set(top))
            down = bool(reach(nv, arcs, top) & set(bottom))
            stats["patterns"] += 1
            stats["blocked one way"] += not (up and down)
            stats["blocked and consistent"] += (not (up and down)) and ok
            stats["two-way"] += up and down
            stats["two-way consistent"] += up and down and ok
            stats["inconsistent"] += not ok
        block[f"{a}x{b}"] = dict(stats)
    checks["theorem_3_blocking"] = block
    if not all(v["blocked one way"] == v["blocked and consistent"] and v["two-way consistent"] > 0
               and v["inconsistent"] > 0 for v in block.values()):
        failures.append("Theorem 3")

    checks["theorem_4_regimes"] = ("argued-in-prose from cited percolation theorems (exponential decay below threshold, "
                                   "Russo-Seymour-Welsh at 1/2, supercritical arms and merging); not computed here; the "
                                   "experiment BASE-CRITICALITY-20261022-001B-E001 tests the regimes empirically")

    # Controls
    nv, edges, src = 4, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)], [0]
    orient = Counter()
    for bits in product((0, 1), repeat=len(edges)):
        orient[reach(nv, [(u, v) if b else (v, u) for (u, v), b in zip(edges, bits)], src)] += 1
    wrong = Counter()
    for bits in product((0, 1), repeat=len(edges)):
        weight = F(1)
        for bb in bits:
            weight *= F(2, 5) if bb else F(3, 5)
        wrong[cluster(nv, [e for e, bb in zip(edges, bits) if bb], src)] += weight
    same = all(F(orient[s], 2 ** len(edges)) == wrong[s] for s in set(orient) | set(wrong))
    controls["reach_set_has_the_law_of_percolation_at_two_fifths"] = "accepted" if same else "rejected"
    nv3, e3 = torus(3, 3)
    g3 = [v % 2 for v in range(nv3)]
    mismatch = 0
    for _ in range(3000):
        x = [rng.randrange(2) for _ in e3]
        mismatch += consistent(nv3, e3, [NAE[xe] for xe in x]) != consistent(nv3, e3, recoloured(e3, g3, x, rule="wrong")[0])
    controls["recolouring_with_the_spoke_coloured_tail"] = "accepted" if mismatch == 0 else "rejected"
    controls["two_way_crossing_never_consistent"] = (
        "accepted" if all(v["two-way consistent"] == 0 for v in block.values()) else "rejected")
    # both monotone clauses plus an equality on one pair: (0,0), (1,1), (0,1), (1,0) all forbidden
    unsat_seam = consistent(2, [(0, 1), (0, 1), (0, 1)], [((0, 1), (1, 1)), ((1, 1), (1, 0)), ((1, 0), (0, 1))])
    controls["consistency_test_accepts_an_unsatisfiable_seam"] = "accepted" if unsat_seam else "rejected"
    if any(v != "rejected" for v in controls.values()):
        failures.append("controls")
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
