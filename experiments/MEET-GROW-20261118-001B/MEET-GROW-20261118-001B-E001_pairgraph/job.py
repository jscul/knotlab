"""MEET-GROW-20261118-001B frozen run, for the shared runner (docs/tooling/shared-runner.md).

melib.py is MEET-ORDERS-20261118-001B's engine, copied unchanged (same sha256).

Case P|n0|d|j: labelled KF3 from presentation j (one per mirror pair) of the line of n0, to n0 + d. Its meeting pattern (the
knots as sets of distinctions) is relabelled to a canonical form H* by a fixed bijection phi_P (the least relabelled knot list).
For every automorphism alpha of H*, and every level, the case reports a digest of the labelled distribution of the co-knotted
pairs G after relabelling the starting distinctions by alpha o phi_P (new distinctions keep their numbers). Two presentations
with the same H* have pair-graph distributions carried onto each other by a meeting-pattern isomorphism exactly when the
identity digests of one equal some alpha's digests of the other at every level.  It also reports, for levels up to n0 + 3, a
digest of the distribution of G up to renaming (all distinctions), and the labelled base counts; and, for levels up to n0 + 3
below the case's depth, per alpha a digest of the joint distribution of G with each state's option profile (the cost and the new
pairs of each of KF3's options), the advisor's test of a state-by-state correspondence (P4).
"""
import hashlib
import itertools
import json
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import melib as M

CASES = [(5, 5), (6, 4), (7, 4), (8, 4), (9, 3)]
RENAMING_LEVELS = 3
HEAVY = {5}          # the five-start cases to n0 + 5 need several GB each; run as their own launch (--param subset=heavy)
SUBSET = "all"


def setup(params):
    global SUBSET
    SUBSET = params.get("subset", "all")


def reps(n0):
    seen = set()
    out = []
    m = n0 - 1
    for T in M.bracketings(0, m):
        key = tuple(sorted(T))
        if tuple(M.mirror(T, m)) in seen or key in seen:
            continue
        seen.add(key)
        out.append(sorted(T))
    return out


def cases():
    for n0, d in CASES:
        if (SUBSET == "heavy" and n0 not in HEAVY) or (SUBSET == "light" and n0 in HEAVY):
            continue
        for j, T in enumerate(reps(n0)):
            yield f"P|{n0}|{d}|{j}", {"n0": n0, "depth": d, "knots": T}


def canonical_pattern(knots, n0):
    """The least relabelled sorted knot list over all bijections, the bijection reaching it first, and the automorphisms of the
    canonical form."""
    best, best_phi = None, None
    for perm in itertools.permutations(range(n0)):
        lab = tuple(sorted(tuple(sorted(perm[v] for v in k)) for k in knots))
        if best is None or lab < best:
            best, best_phi = lab, perm
    target = set(best)
    autos = [perm for perm in itertools.permutations(range(n0))
             if {tuple(sorted(perm[v] for v in k)) for k in best} == target]
    return best, best_phi, autos


def digest(items):
    h = hashlib.sha256()
    for x in sorted(items):
        h.update(repr(x).encode())
    return h.hexdigest()[:24]


def relabel(G, f, n0):
    g = lambda v: f[v] if v < n0 else v
    return tuple(sorted((min(g(u), g(v)), max(g(u), g(v))) for u, v in G))


def run(case_id, p):
    n0, d, T = p["n0"], p["depth"], [tuple(k) for k in p["knots"]]
    H, phi, autos = canonical_pattern(T, n0)
    lv = M.exact(n0, T, n0 + d, use_canon=False)
    levels = []
    for L in lv:
        dist = defaultdict(Fraction)
        for (S, G), q in L["dist"].items():
            dist[G] += q
        per_alpha = []
        for alpha in autos:
            f = [alpha[phi[v]] for v in range(n0)]
            per_alpha.append(digest((relabel(G, f, n0), str(q)) for G, q in dist.items()))
        row = {"n": L["n"], "labelled_bases": L["classes"], "pair_graphs": len(dist), "per_alpha": per_alpha,
               "two": str(L["two"])}
        if L["n"] - n0 <= RENAMING_LEVELS and L["n"] < n0 + d:
            prof = {}
            for (S, G), q in L["dist"].items():
                cost, top = M.zero_cost_top(S, L["n"], G)
                prof[(S, G)] = (cost, [tuple(sorted(M.pairs_of(ks) - G)) for _, _, ks in top])
            joint = []
            for alpha in autos:
                f = [alpha[phi[v]] for v in range(n0)]
                items = defaultdict(Fraction)
                for (S, G), q in L["dist"].items():
                    cost, effs = prof[(S, G)]
                    key = (relabel(G, f, n0), cost, tuple(sorted(relabel(e, f, n0) for e in effs)))
                    items[key] += q
                joint.append(digest((k, str(q)) for k, q in items.items()))
            row["per_alpha_profile"] = joint
        if L["n"] - n0 <= RENAMING_LEVELS:
            cls = defaultdict(Fraction)
            for G, q in dist.items():
                cls[M.canon((), L["n"], G)[1]] += q
            row["renaming_digest"] = digest((tuple(sorted(c)), str(q)) for c, q in cls.items())
            row["renaming_classes"] = len(cls)
        levels.append(row)
    return {"n0": n0, "depth": d, "knots": T, "pattern": H, "automorphisms": len(autos),
            "ordered": M.nesting(T, 0, n0 - 1, ordered=True), "bare": M.nesting(T, 0, n0 - 1), "levels": levels}


if __name__ == "__main__":
    print(sum(1 for _ in cases()), "cases")
