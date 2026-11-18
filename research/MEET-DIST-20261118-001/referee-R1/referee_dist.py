"""Referee R1 for MEET-DIST-20261118-001 (own code; the study's job.py, merge.py and melib.py are not imported).

  ../../../.venv/bin/python -B referee_dist.py <n0> <depth> > referee_dist_<n0>_<depth>.json      (from this directory)

Engine: the referee's MEET-ORDERS-R1 KF3 (`referee_meet.run`, labelled (S, G), exact fractions).  For every bracketing of the line
(all of them, so the prior "uniform over labelled presentations" needs no mirror bookkeeping), at every level k = 0..depth:
- the law of the grown base's table of disagreement counts with N, up to renaming.  Classes are kept in one registry for all
  presentations: a WL hash of the complete graph whose edges carry the counts, then VF2 with exact edge matching;
- the bag-of-knots null: k distinct knots of the presentation chosen uniformly and revealed as fill points (the parity of each
  knot's three distinctions), no growth;
- the multiset ablation: N with the sorted multiset of the table's entries;
- the labelled table: the same table with its labels kept (the line's distinctions 0..m, new ones in order), which by DISTANCE-ORDER
  3(a) is the labelled base itself; and the line-labelled table: the line's distinctions labelled, the new ones anonymous (which
  separates the line's labels, readable from distances up to mirror, from the order in which the new distinctions came).
Then the share I(bare bracketing; class) / H(bare bracketing) under two priors: uniform over labelled presentations (the study's)
and uniform over bare bracketings (each bare bracketing equal, its presentations uniform within it); and whether the laws of the
table classes differ between every two bare bracketings.
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
import referee_meet as RM  # noqa: E402


def table(S, n):
    return [[sum(((s >> u) ^ (s >> v)) & 1 for s in S) for v in range(n)] for u in range(n)]


class Registry:
    def __init__(self):
        self.buckets = defaultdict(list)

    def cls(self, S, n):
        D = table(S, n)
        G = nx.Graph()
        G.add_nodes_from(range(n))
        for u, v in itertools.combinations(range(n), 2):
            G.add_edge(u, v, d=str(D[u][v]))
        h = (len(S), n, nx.weisfeiler_lehman_graph_hash(G, edge_attr="d", iterations=3))
        for i, H in enumerate(self.buckets[h]):
            if nx.is_isomorphic(G, H, edge_match=lambda a, b: a["d"] == b["d"]):
                return (h, i)
        self.buckets[h].append(G)
        return (h, len(self.buckets[h]) - 1)


def old_labelled(S, n, n0):
    """The table with the line's distinctions labelled and the new ones anonymous (least form over orders of the new ones)."""
    D = table(S, n)
    best = None
    for perm in itertools.permutations(range(n0, n)):
        order = list(range(n0)) + list(perm)
        t = tuple(D[order[i]][order[j]] for i in range(n) for j in range(i + 1, n))
        if best is None or t < best:
            best = t
    return (len(S), best)


def multiset(S, n):
    D = table(S, n)
    return (len(S), tuple(sorted(D[u][v] for u, v in itertools.combinations(range(n), 2))))


def bare(T, a, b):
    span = {(k[0], k[2]): k for k in T}
    if (a, b) not in span:
        return "x"
    c = span[(a, b)][1]
    return "(" + ",".join(sorted([bare(T, a, c), bare(T, c, b)])) + ")"


def fills_base(n0, T, chosen):
    out = []
    for s in RM.line_states(n0):
        x = s
        for i, k in enumerate(chosen):
            x |= (sum((s >> v) & 1 for v in k) & 1) << (n0 + i)
        out.append(x)
    return tuple(sorted(out))


def share(rows, key, prior):
    """I(bare; class) / H(bare): rows are (bare, weight, law over classes)."""
    tot = sum(w for _, w, _ in rows)
    pk, pc, joint = defaultdict(float), defaultdict(float), defaultdict(float)
    for b, w, law in rows:
        for c, q in law.items():
            x = float(Fraction(w, 1) / tot * q)
            pk[b] += x
            pc[c] += x
            joint[(b, c)] += x
    H = -sum(p * math.log2(p) for p in pk.values() if p > 0)
    I = sum(q * math.log2(q / (pk[b] * pc[c])) for (b, c), q in joint.items() if q > 0)
    return I / H if H else None


def main(n0, depth):
    Ts = [tuple(T) for T in RM.bracketings(0, n0 - 1)]
    reg = Registry()
    per = []
    for T in Ts:
        lv = RM.run(n0, T, depth, keep_levels=True)
        tl, ml, nl, ll, ol = [], [], [], [], []
        for k, L in enumerate(lv):
            law, mlaw, llaw, olaw = defaultdict(Fraction), defaultdict(Fraction), defaultdict(Fraction), defaultdict(Fraction)
            for (S, G), q in L["dist"].items():
                law[reg.cls(S, L["n"])] += q
                mlaw[multiset(S, L["n"])] += q
                llaw[(len(S), tuple(map(tuple, table(S, L["n"]))))] += q      # the table with its labels kept
                olaw[old_labelled(S, L["n"], n0)] += q
            tl.append(dict(law))
            ml.append(dict(mlaw))
            ll.append(dict(llaw))
            ol.append(dict(olaw))
            if k == 0:
                nl.append(None)
            elif k <= len(T):
                subs = list(itertools.combinations(T, k))
                nlaw = defaultdict(Fraction)
                for c in subs:
                    nlaw[reg.cls(fills_base(n0, T, c), n0 + k)] += Fraction(1, len(subs))
                nl.append(dict(nlaw))
            else:
                nl.append(None)
        per.append({"T": T, "bare": bare(T, 0, n0 - 1), "table": tl, "multiset": ml, "null": nl, "labelled_table": ll, "line_labelled_table": ol})
        print("done", T, file=sys.stderr, flush=True)
    bares = sorted({p["bare"] for p in per})
    size = {b: sum(1 for p in per if p["bare"] == b) for b in bares}
    out = {"n0": n0, "depth": depth, "bracketings": len(Ts), "bare_bracketings": {b: size[b] for b in bares}, "levels": []}
    for k in range(depth + 1):
        row = {"k": k}
        for name in ("table", "multiset", "null", "labelled_table", "line_labelled_table"):
            if per[0][name][k] is None:
                continue
            labelled = [(p["bare"], 1, p[name][k]) for p in per]
            even = [(p["bare"], Fraction(1, size[p["bare"]]), p[name][k]) for p in per]
            row[f"{name}_share_uniform_over_presentations"] = round(share(labelled, None, None), 4)
            row[f"{name}_share_uniform_over_bare_bracketings"] = round(share(even, None, None), 4)
        # the law: do every two bare bracketings have different laws of table classes (mixing their presentations uniformly)?
        mix = {}
        for b in bares:
            law = defaultdict(Fraction)
            for p in per:
                if p["bare"] == b:
                    for c, q in p["table"][k].items():
                        law[c] += q / size[b]
            mix[b] = dict(law)
        row["bare_bracketing_pairs_with_equal_table_laws"] = sum(1 for a, b in itertools.combinations(bares, 2) if mix[a] == mix[b])
        row["presentation_pairs_with_equal_table_laws"] = sum(1 for a, b in itertools.combinations(per, 2) if a["table"][k] == b["table"][k])
        row["table_classes"] = len({c for p in per for c in p["table"][k]})
        out["levels"].append(row)
        print("level", json.dumps(row), file=sys.stderr, flush=True)
    return out


if __name__ == "__main__":
    print(json.dumps(main(int(sys.argv[1]), int(sys.argv[2])), indent=1))
