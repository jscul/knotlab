"""Referee R1 for MEET-HIST-20261118-001 (own code; the study's job.py, merge.py and melib.py are not imported).

  ../../../.venv/bin/python -B referee_hist.py <n0> <depth> > referee_hist_<n0>_<depth>.json      (from this directory)

Engine: the referee's MEET-ORDERS-R1 KF3 (`referee_meet.run`, labelled (S, G)); readings of each grown base by the referee's
MEET-DIST-R1 tools (tables of disagreement counts, which by DISTANCE-ORDER 3(a) are the states):
  U    the table up to renaming (WL hash, then VF2);
  NL   the line's distinctions named by place, the new ones anonymous, up to the line's reversal;
  NO   the new ones named by order of growth, the line's anonymous (VF2 with node colours);
  N    all named, up to the line's reversal;
  ADD  a preview of B199: the co-knotted pairs that hold a new distinction, as a graph up to renaming (no states, no names).
Shares I(bare bracketing; reading) / H(bare) under the prior uniform over labelled presentations; H(N | NL) = H(N) - H(NL) (N
refines NL, checked); the part of it that bears on the nesting, I(bare; N | NL) = H(bare) (share_N - share_NL); and whether NO and N
give the same partition of the grown bases (the study's sanity row).
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


class ColouredRegistry:
    """Complete graphs with edge weights (the table) and node colours, up to colour-keeping renaming."""

    def __init__(self):
        self.buckets = defaultdict(list)

    def cls(self, S, n, colours, extra=()):
        D = RD.table(S, n)
        G = nx.Graph()
        for u in range(n):
            G.add_node(u, c=str(colours[u]))
        for u, v in itertools.combinations(range(n), 2):
            G.add_edge(u, v, d=str(D[u][v]))
        h = (len(S), n, extra, nx.weisfeiler_lehman_graph_hash(G, node_attr="c", edge_attr="d", iterations=3))
        for i, H in enumerate(self.buckets[h]):
            if nx.is_isomorphic(G, H, node_match=lambda a, b: a["c"] == b["c"], edge_match=lambda a, b: a["d"] == b["d"]):
                return (h, i)
        self.buckets[h].append(G)
        return (h, len(self.buckets[h]) - 1)


def mirror_states(S, n, n0):
    m = n0 - 1
    perm = [m - u if u < n0 else u for u in range(n)]
    return tuple(sorted(sum(1 << perm[u] for u in range(n) if (s >> u) & 1) for s in S))


def nl_key(S, n, n0):
    """Line named by place up to reversal, new ones anonymous: the least form over orders of the new ones, and over reversal."""
    return min(RD.old_labelled(S, n, n0), RD.old_labelled(mirror_states(S, n, n0), n, n0))


def n_key(S, n, n0):
    return min(S, mirror_states(S, n, n0))


def added_graph_key(reg, G, n, n0):
    H = nx.Graph()
    H.add_nodes_from(range(n))
    for a, b in G:
        if a >= n0 or b >= n0:
            H.add_edge(a, b)
    h = nx.weisfeiler_lehman_graph_hash(H, iterations=4)
    for i, X in enumerate(reg[h]):
        if nx.is_isomorphic(H, X):
            return (h, i)
    reg[h].append(H)
    return (h, len(reg[h]) - 1)


def entropy(law):
    return -sum(float(p) * math.log2(float(p)) for p in law.values() if p > 0)


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
    return I / H if H else None, H


def main(n0, depth):
    Ts = [tuple(T) for T in RM.bracketings(0, n0 - 1)]
    regU, regNO = RD.Registry(), ColouredRegistry()
    regADD = defaultdict(list)
    per = []
    for T in Ts:
        lv = RM.run(n0, T, depth, keep_levels=True)
        rows = []
        for k, L in enumerate(lv):
            n = L["n"]
            laws = {r: defaultdict(Fraction) for r in ("U", "NL", "NO", "N", "ADD", "NL|N", "NO|N")}
            for (S, G), q in L["dist"].items():
                u = regU.cls(S, n)
                nl = nl_key(S, n, n0)
                no = regNO.cls(S, n, ["line" if v < n0 else f"new{v}" for v in range(n)])
                nn = n_key(S, n, n0)
                ad = added_graph_key(regADD, G, n, n0)
                for r, x in (("U", u), ("NL", nl), ("NO", no), ("N", nn), ("ADD", ad), ("NL|N", (nl, nn)), ("NO|N", (no, nn))):
                    laws[r][x] += q
            rows.append(laws)
        per.append({"bare": RD.bare(T, 0, n0 - 1), "levels": rows})
        print("done", T, file=sys.stderr, flush=True)
    out = {"n0": n0, "depth": depth, "bracketings": len(Ts), "levels": []}
    for k in range(depth + 1):
        row = {"k": k}
        for r in ("U", "NL", "N", "ADD"):
            s, Hb = share([(p["bare"], p["levels"][k][r]) for p in per])
            row[f"share_{r}"] = round(s, 4) if s is not None else None
        row["H_bare_bits"] = round(Hb, 4)
        pooled = {r: defaultdict(float) for r in ("NL", "N", "NL|N", "NO", "NO|N")}
        for p in per:
            for r in pooled:
                for x, q in p["levels"][k][r].items():
                    pooled[r][x] += float(q) / len(per)
        row["N_refines_NL"] = abs(entropy(pooled["NL|N"]) - entropy(pooled["N"])) < 1e-9
        row["NO_and_N_same_partition"] = abs(entropy(pooled["NO|N"]) - entropy(pooled["N"])) < 1e-9 and \
            abs(entropy(pooled["NO|N"]) - entropy(pooled["NO"])) < 1e-9
        hNgNL = entropy(pooled["N"]) - entropy(pooled["NL"])
        row["H_order_given_NL_bits"] = round(hNgNL, 4)
        row["log2_k_factorial"] = round(math.log2(math.factorial(k)), 4) if k else 0
        if row["share_N"] is not None and row["share_NL"] is not None:
            row["I_bare_order_given_NL_bits"] = round(Hb * (row["share_N"] - row["share_NL"]), 4)
        out["levels"].append(row)
        print("level", json.dumps(row), file=sys.stderr, flush=True)
    return out


if __name__ == "__main__":
    print(json.dumps(main(int(sys.argv[1]), int(sys.argv[2])), indent=1))
