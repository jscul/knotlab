"""Referee R1 for MEET-ADDED-20261118-001 (own code; the study's job.py, merge.py and melib.py are not imported).

  ../../../.venv/bin/python -B referee_added.py <n0> <depth> > referee_added_<n0>_<depth>.json      (from this directory)

Engine: the referee's MEET-ORDERS-R1 KF3 options (`referee_meet.options`), run here keyed by (states, added knots), so that every
knot a step adds is kept with its middle.  Each grown base is read up to renaming as one coloured graph: the distinctions joined by
their disagreement counts (the states, by DISTANCE-ORDER 3(a)), and one node per knot joined to its two ends and its middle.  Arms:
  U      the states alone;
  K1     the states with the added knots (middles marked) -- the study's arm;
  T1     the same without middles;
  ALL    the states with every knot, the starting ones and the added ones, not told apart (the coordinator's arm);
  ALLK   every knot, not told apart, without the states;
  ADDK   the added knots alone (middles marked), without the states;
  N      all named (the line's distinctions by place up to reversal, the new ones by order of growth).
Shares I(bare; arm) / H(bare), prior uniform over labelled presentations.  For seven at k = 3, a search for two grown bases that K1
cannot tell apart but N can, from different bare bracketings, checked by VF2: is the study's shortfall real?
"""
import itertools
import json
import math
import sys
from collections import defaultdict
from fractions import Fraction
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/MEET-ORDERS-20261118-001/referee-R1"))
sys.path.insert(0, str(ROOT / "research/MEET-DIST-20261118-001/referee-R1"))
import referee_meet as RM  # noqa: E402
import referee_dist as RD  # noqa: E402


def norm(k):
    x, y, z = k
    return (min(x, z), y, max(x, z))


def run_with_knots(n0, T, depth):
    S0 = RM.line_states(n0)
    G0 = RM.pairs_of(T)
    dist = {(S0, frozenset()): Fraction(1)}
    levels = [dist]
    n = n0
    for _ in range(depth):
        new = defaultdict(Fraction)
        for (S, K), p in dist.items():
            cost, top = RM.options(S, n, G0 | RM.pairs_of(list(K)))
            for q0, q1, ks in top:
                new[(RM.extend(S, n, q0, q1), K | frozenset(norm(k) for k in ks))] += p / len(top)
        dist = dict(new)
        n += 1
        levels.append(dist)
    return levels


def structure(S, n, knots, mids=True, states=True):
    G = nx.Graph()
    for u in range(n):
        G.add_node(("d", u), t="d")
    if states:
        D = RD.table(S, n)
        for u, v in itertools.combinations(range(n), 2):
            G.add_edge(("d", u), ("d", v), r=f"d{D[u][v]}")
    for i, (a, c, b) in enumerate(sorted(knots)):
        G.add_node(("k", i), t="k")
        G.add_edge(("k", i), ("d", a), r="end")
        G.add_edge(("k", i), ("d", b), r="end")
        G.add_edge(("k", i), ("d", c), r="mid" if mids else "end")
    return G


class Reg:
    def __init__(self):
        self.b = defaultdict(list)

    def key(self, G, extra):
        h = (extra, nx.weisfeiler_lehman_graph_hash(G, node_attr="t", edge_attr="r", iterations=4))
        for i, H in enumerate(self.b[h]):
            if nx.is_isomorphic(G, H, node_match=lambda x, y: x["t"] == y["t"], edge_match=lambda x, y: x["r"] == y["r"]):
                return (h, i)
        self.b[h].append(G)
        return (h, len(self.b[h]) - 1)


def mirror_states(S, n, n0):
    m = n0 - 1
    perm = [m - u if u < n0 else u for u in range(n)]
    return tuple(sorted(sum(1 << perm[u] for u in range(n) if (s >> u) & 1) for s in S))


def share(rows):
    tot = len(rows)
    pk, pc, joint = defaultdict(float), defaultdict(float), defaultdict(float)
    for b, law in rows:
        for c, q in law.items():
            x = float(q) / tot
            pk[b] += x
            pc[c] += x
            joint[(b, c)] += x
    H = -sum(p * math.log2(p) for p in pk.values() if p > 0)
    I = sum(q * math.log2(q / (pk[b] * pc[c])) for (b, c), q in joint.items() if q > 0)
    return I / H if H else None


def main(n0, depth, arms=("U", "K1", "T1", "ALL", "ALLK", "ADDK", "N")):
    Ts = [tuple(T) for T in RM.bracketings(0, n0 - 1)]
    regs = {a: Reg() for a in arms}
    per = []
    keep = defaultdict(list)                  # last level: K1 class -> list of (bare, N key, S, K)
    for T in Ts:
        lv = run_with_knots(n0, T, depth)
        rows = []
        for k, dist in enumerate(lv):
            n = n0 + k
            laws = {a: defaultdict(Fraction) for a in arms}
            for (S, K), q in dist.items():
                allk = set(K) | {norm(t) for t in T}
                for a in arms:
                    if a == "N":
                        x = min(S, mirror_states(S, n, n0))
                    elif a == "U":
                        x = regs[a].key(structure(S, n, ()), len(S))
                    elif a == "K1":
                        x = regs[a].key(structure(S, n, K), len(S))
                    elif a == "T1":
                        x = regs[a].key(structure(S, n, K, mids=False), len(S))
                    elif a == "ALL":
                        x = regs[a].key(structure(S, n, allk), len(S))
                    elif a == "ALLK":
                        x = regs[a].key(structure(S, n, allk, states=False), n)
                    elif a == "ADDK":
                        x = regs[a].key(structure(S, n, K, states=False), n)
                    laws[a][x] += q
                    if a == "K1" and k == depth:
                        keep[x].append((RD.bare(T, 0, n0 - 1), min(S, mirror_states(S, n, n0)), S, K))
            rows.append(laws)
        per.append({"bare": RD.bare(T, 0, n0 - 1), "levels": rows})
        print("done", T, file=sys.stderr, flush=True)
    out = {"n0": n0, "depth": depth, "bracketings": len(Ts), "levels": []}
    for k in range(depth + 1):
        row = {"k": k}
        for a in arms:
            s = share([(p["bare"], p["levels"][k][a]) for p in per])
            row[a] = round(s, 6) if s is not None else None
        out["levels"].append(row)
        print("level", json.dumps(row), file=sys.stderr, flush=True)
    # witnesses for a shortfall of K1 against N: one K1 class holding two named bases (different N keys) whose laws over bare
    # bracketings differ (in support or in weight), so that K1 merges what the names keep apart; checked again by VF2
    lawN = defaultdict(lambda: defaultdict(Fraction))
    for p in per:
        for nk, q in p["levels"][depth]["N"].items():
            lawN[nk][p["bare"]] += q
    def normed(d):
        t = sum(d.values())
        return {k: v / t for k, v in d.items()}
    wit, multi = [], 0
    n = n0 + depth
    for x, members in keep.items():
        reps = {}
        for b, nk, S, K in members:
            reps.setdefault(nk, (S, K))
        if len(reps) < 2:
            continue
        multi += 1
        keysN = list(reps)
        for i, j in itertools.combinations(range(len(keysN)), 2):
            la, lb = normed(lawN[keysN[i]]), normed(lawN[keysN[j]])
            if la != lb:
                a, b = reps[keysN[i]], reps[keysN[j]]
                iso = nx.is_isomorphic(structure(a[0], n, a[1]), structure(b[0], n, b[1]),
                                       node_match=lambda p, q: p["t"] == q["t"], edge_match=lambda p, q: p["r"] == q["r"])
                wit.append({"vf2_isomorphic": iso, "law_a": {k: str(v) for k, v in la.items()}, "law_b": {k: str(v) for k, v in lb.items()},
                            "added_knots_a": sorted(a[1]), "added_knots_b": sorted(b[1])})
                break
    out["K1_classes_holding_several_named_bases"] = multi
    out["K1_classes_merging_named_bases_with_different_bare_laws"] = len(wit)
    out["witnesses"] = wit[:3]
    return out


if __name__ == "__main__":
    n0, d = int(sys.argv[1]), int(sys.argv[2])
    arms = tuple(sys.argv[3].split(",")) if len(sys.argv) > 3 else ("U", "K1", "T1", "ALL", "ALLK", "ADDK", "N")
    print(json.dumps(main(n0, d, arms), indent=1, default=str))
