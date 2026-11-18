"""Referee R1 for MEET-GROW-20261118-001 (own code; the study's job.py and melib.py are not imported).

  ../../../.venv/bin/python -B referee_grow.py run <n0> <depth> <j>      one presentation (j-th up to mirror) -> grow_<n0>_<depth>_<j>.json
  ../../../.venv/bin/python -B referee_grow.py merge <n0> <depth>          compare within meeting patterns -> referee_grow_<n0>_<depth>.json

The engine is the referee's MEET-ORDERS-R1 KF3 (`referee_meet.run`, labelled (S, G) bases, exact fractions).

- run: the labelled distribution of the co-knotted pairs G at every level; and, at every level below the last, whether each
  base's option profile (the cost and, per cheapest knot set, the pairs it adds) is a function of G alone (if it is, the pair graph
  grows as a Markov chain of its own, whatever the states); and the weaker test, whether each base's law of the next pair graph
  depends only on its pair graph.
- merge: for every two presentations whose knots form the same meeting pattern, every isomorphism of the patterns (brute force over
  renamings of the line's distinctions, new distinctions fixed), and whether one carries the exact distribution of G onto the
  other's at every level (exact equality of fractions, no digests).
"""
import itertools
import json
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/MEET-ORDERS-20261118-001/referee-R1"))
import referee_meet as RM  # noqa: E402


def reps(n0):
    m = n0 - 1
    seen, out = set(), []
    for T in RM.bracketings(0, m):
        key = tuple(sorted(T))
        mir = tuple(sorted((m - k[2], m - k[1], m - k[0]) for k in T))
        if key in seen or mir in seen:
            continue
        seen.add(key)
        out.append(key)
    return out


def run_one(n0, depth, j):
    T = reps(n0)[j]
    lv = RM.run(n0, T, depth, keep_levels=True)
    levels = []
    for i, L in enumerate(lv):
        dist = defaultdict(Fraction)
        for (S, G), q in L["dist"].items():
            dist[G] += q
        row = {"n": L["n"], "labelled": L["labelled"], "pair_graphs": len(dist), "two": str(L["two"]),
               "G": [[sorted(map(list, G)), str(q)] for G, q in sorted(dist.items(), key=lambda x: sorted(x[0]))]}
        if i < len(lv) - 1:
            prof = defaultdict(set)
            for (S, G), q in L["dist"].items():
                cost, top = RM.options(S, L["n"], G)
                prof[G].add((cost, tuple(sorted(tuple(sorted(RM.pairs_of(ks) - G)) for _, _, ks in top))))
            row["pair_graphs_whose_bases_have_different_option_profiles"] = sum(1 for v in prof.values() if len(v) > 1)
            # the weaker test: does each base's law of the next pair graph depend only on its pair graph?
            nxt = defaultdict(set)
            for (S, G), q in L["dist"].items():
                cost, top = RM.options(S, L["n"], G)
                law = defaultdict(Fraction)
                for _, _, ks in top:
                    law[G | RM.pairs_of(ks)] += Fraction(1, len(top))
                nxt[G].add(tuple(sorted((tuple(sorted(g)), str(w)) for g, w in law.items())))
            row["pair_graphs_whose_bases_give_different_next_pair_laws"] = sum(1 for v in nxt.values() if len(v) > 1)
        levels.append(row)
        print("run", n0, depth, j, L["n"], L["labelled"], len(dist), row.get("pair_graphs_whose_bases_have_different_option_profiles"),
              row.get("pair_graphs_whose_bases_give_different_next_pair_laws"), file=sys.stderr, flush=True)
    out = {"n0": n0, "depth": depth, "j": j, "knots": [list(k) for k in T], "levels": levels}
    (HERE / f"grow_{n0}_{depth}_{j}.json").write_text(json.dumps(out))
    return {k: v for k, v in out.items() if k != "levels"}


def merge(n0, depth):
    R = [json.loads((HERE / f"grow_{n0}_{depth}_{j}.json").read_text()) for j in range(len(reps(n0)))]

    def pattern_isos(A, B):
        KA = [frozenset(k) for k in A]
        KB = {frozenset(k) for k in B}
        return [p for p in itertools.permutations(range(n0)) if {frozenset(p[v] for v in k) for k in KA} == KB]

    def dists(r):
        return [{frozenset(tuple(e) for e in G): Fraction(q) for G, q in L["G"]} for L in r["levels"]]
    D = [dists(r) for r in R]
    groups = []
    for j, r in enumerate(R):
        for g in groups:
            if pattern_isos(R[g[0]]["knots"], r["knots"]):
                g.append(j)
                break
        else:
            groups.append([j])
    pairs = []
    for g in groups:
        for a, b in itertools.combinations(g, 2):
            isos = pattern_isos(R[a]["knots"], R[b]["knots"])
            carried_by = 0
            for p in isos:
                f = lambda x, p=p: p[x] if x < n0 else x
                ok = all({frozenset((min(f(u), f(v)), max(f(u), f(v))) for u, v in G): q for G, q in Da.items()} == Db
                         for Da, Db in zip(D[a], D[b]))
                carried_by += ok
            two = [(La["two"], Lb["two"]) for La, Lb in zip(R[a]["levels"], R[b]["levels"])]
            pairs.append({"a": a, "b": b, "isomorphisms": len(isos), "isomorphisms_carrying_every_level": carried_by,
                          "two_orders_differ_at_some_level": any(x != y for x, y in two)})
    prof = {j: [L.get("pair_graphs_whose_bases_have_different_option_profiles") for L in r["levels"]] for j, r in enumerate(R)}
    nxt = {j: [L.get("pair_graphs_whose_bases_give_different_next_pair_laws") for L in r["levels"]] for j, r in enumerate(R)}
    return {"n0": n0, "depth": depth, "presentations_up_to_mirror": len(R), "meeting_patterns": len(groups),
            "group_sizes": [len(g) for g in groups], "pairs": pairs,
            "pairs_carried": sum(1 for p in pairs if p["isomorphisms_carrying_every_level"] > 0),
            "labelled_counts": {j: [L["labelled"] for L in r["levels"]] for j, r in enumerate(R)},
            "pair_graphs_with_state_dependent_profiles_by_level": prof,
            "pair_graphs_with_state_dependent_next_pair_laws_by_level": nxt,
            "pair_graphs_by_level": {j: [L["pair_graphs"] for L in r["levels"]] for j, r in enumerate(R)}}


if __name__ == "__main__":
    if sys.argv[1] == "run":
        print(json.dumps(run_one(int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))))
    else:
        print(json.dumps(merge(int(sys.argv[2]), int(sys.argv[3])), indent=1))
