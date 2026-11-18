"""Referee R1 for KEEP-READ-20261118-001 (own code; the study's keeplib.py, run.py, readout.py and the pinned knotlib/picklib/melib
are not imported).

  ../../../.venv/bin/python -B referee_keep.py <part> > referee_keep_<part>.json      (from this directory)

SEEDK, written by the referee (KNOT-SWITCH-R1): knot-local KF3 options from MEET-ORDERS-R1 (`referee_meet.options`), any fill while
nothing crosses, then SEED's condition (`referee_switch.seed_ok`), else a knot-local subdivision.  After the switch every zero-cost
knot set is recorded with its extension, lambda after (KNOT-CAP-R1 `measure`), whether it keeps two orders, SEED's acceptance, how
many of its knots have the new distinction as middle, and its pictures:
  tier 0     the new distinction, the move's old distinctions and the move's knots, each distinction's role (middle or end) marked;
  closure    the same with every betweenness the states imply among the move's old distinctions (middle marked).
Picture classes are exact: Weisfeiler-Lehman buckets split by VF2 isomorphism, across all runs.

Parts:
  tier0     from every bracketing of 5, 6, 7 and every third of 8 (105 starts) to n = 24: the clean-witness fractions (R2) at tier 0
            and the closure tier, over exact classes, for "keeps two orders" and for SEED's acceptance; confirmed look-alikes.
  middles   the same starts to n = 40: does a knot set whose new distinction is the middle of two or more of its knots ever raise
            the orders, on these larger bases?
"""
import itertools
import json
import random
import sys
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/MEET-ORDERS-20261118-001/referee-R1"))
sys.path.insert(0, str(ROOT / "research/KNOT-CAP-20261117-001/referee-R1"))
sys.path.insert(0, str(ROOT / "research/KNOT-SWITCH-20261118-001/referee-R1"))
import referee_meet as RM  # noqa: E402
import referee_cap as KC  # noqa: E402
import referee_switch as RSW  # noqa: E402


def pic0(ks, n):
    G = nx.Graph()
    G.add_node(("d", n), kind="new")
    for j, k in enumerate(ks):
        G.add_node(("m", j), kind="move")
        for pos, v in enumerate(k):
            if ("d", v) not in G:
                G.add_node(("d", v), kind="start")
            G.add_edge(("m", j), ("d", v), role="mid" if pos == 1 else "end")
    return G


def picc(S, n, ks):
    G = pic0(ks, n)
    D = sorted({v for k in ks for v in k if v != n})
    c = 0
    for x, z in itertools.combinations(D, 2):
        for y in D:
            if y in (x, z):
                continue
            if all(RSW.ok(s, (x, y, z)) for s in S):
                G.add_node(("i", c), kind="implied")
                G.add_edge(("i", c), ("d", x), role="end")
                G.add_edge(("i", c), ("d", y), role="mid")
                G.add_edge(("i", c), ("d", z), role="end")
                c += 1
    return G


def serial(G):
    return ([(repr(v), d["kind"]) for v, d in G.nodes(data=True)], [(repr(a), repr(b), d["role"]) for a, b, d in G.edges(data=True)])


def unserial(x):
    G = nx.Graph()
    for v, kind in x[0]:
        G.add_node(v, kind=kind)
    for a, b, role in x[1]:
        G.add_edge(a, b, role=role)
    return G


def one_run(args):
    T, nmax, want_pics = args
    n0 = 1 + max(max(k) for k in T)
    S, n, G = RM.line_states(n0), n0, RM.pairs_of(T)
    rng = random.Random(f"referee-keep:{T}")
    exts = []
    while n < nmax and len(S) <= 60:
        cost, top = RM.options(S, n, G)
        switched = RSW.crosses(S, n)
        if switched and cost == 0:
            by_ext = defaultdict(list)
            for q0, q1, ks in top:
                by_ext[(q0, q1)].append(ks)
            for (q0, q1), kss in by_ext.items():
                S2 = RM.extend(S, n, q0, q1)
                lam = KC.measure(list(S2), n + 1)["lam"]
                row = {"n": n, "keep": lam == 2, "accepted": RSW.seed_ok(S, n, S2),
                       "max_middles": max(sum(1 for k in ks if k[1] == n) for ks in kss),
                       "two_middles_any": any(sum(1 for k in ks if k[1] == n) >= 2 for ks in kss)}
                if want_pics:
                    row["p0"] = [serial(pic0(ks, n)) for ks in kss]
                    row["pc"] = [serial(picc(S, n, ks)) for ks in kss]
                exts.append(row)
        move = None
        if cost == 0:
            good = top if not switched else [t for t in top if RSW.seed_ok(S, n, RM.extend(S, n, t[0], t[1]))]
            if good:
                move = rng.choice(good)
        if move is None:
            subs = [(u, v) for u, v in sorted(G) if sum(((s >> u) ^ (s >> v)) & 1 for s in S) == 2]
            if not subs:
                break
            u, v = rng.choice(subs)
            k = (u, n, v)
            S2 = tuple(sorted(x for s in S for x in (s, s | (1 << n)) if RSW.ok(x, k)))
            ks = (k,)
        else:
            S2, ks = RM.extend(S, n, move[0], move[1]), move[2]
        S, n = S2, n + 1
        G = G | RM.pairs_of(ks)
    return exts


def starts():
    Ts = []
    for n0 in (5, 6, 7):
        Ts += [tuple(T) for T in RM.bracketings(0, n0 - 1)]
    Ts += [tuple(T) for T in RM.bracketings(0, 7)][::3]
    return Ts


class Classes:
    """Exact isomorphism classes of marked pictures across all runs."""
    def __init__(self):
        self.b = defaultdict(list)

    def cid(self, G):
        h = nx.weisfeiler_lehman_graph_hash(G, node_attr="kind", edge_attr="role", iterations=4)
        for i, H in enumerate(self.b[h]):
            if nx.is_isomorphic(G, H, node_match=lambda a, b: a["kind"] == b["kind"], edge_match=lambda a, b: a["role"] == b["role"]):
                return (h, i)
        self.b[h].append(G)
        return (h, len(self.b[h]) - 1)


def clean_witness(E, key, label):
    dirty = set()
    for e in E:
        if label == "keep" and not e["keep"] or label == "accepted" and not e["accepted"]:
            dirty |= set(e[key])
    pos = [e for e in E if e[label]]
    clean = [e for e in pos if any(c not in dirty for c in e[key])]
    return {"positives": len(pos), "clean_witness": round(len(clean) / len(pos), 6) if pos else None,
            "classes": len({c for e in E for c in e[key]}), "dirty_classes": len(dirty)}


def part_tier0(workers=16):
    with Pool(workers) as P:
        runs = P.map(one_run, [(T, 24, True) for T in starts()], chunksize=1)
    E = []
    C0, Cc = Classes(), Classes()
    for r in runs:
        for e in r:
            e["c0"] = {C0.cid(unserial(x)) for x in e.pop("p0")}
            e["cc"] = {Cc.cid(unserial(x)) for x in e.pop("pc")}
            E.append(e)
    table = defaultdict(int)
    for e in E:
        table[f"keep={e['keep']} accepted={e['accepted']}"] += 1
    out = {"runs": len(runs), "extensions": len(E), "keep_vs_accepted": dict(table)}
    for key, name in (("c0", "tier 0"), ("cc", "closure")):
        out[name] = {"keep": clean_witness(E, key, "keep"), "accepted": clean_witness(E, key, "accepted")}
        mixed = 0
        for c in {c for e in E for c in e[key]}:
            outs = {e["keep"] for e in E if c in e[key]}
            mixed += len(outs) == 2
        out[name]["classes_with_both_outcomes"] = mixed
    tm = [e for e in E if e["two_middles_any"]]
    out["two_middles"] = {"extensions": len(tm), "raising": sum(1 for e in tm if not e["keep"]),
                          "accepted": sum(1 for e in tm if e["accepted"]),
                          "recall_of_accepted": round(sum(1 for e in tm if e["accepted"]) / max(1, sum(e["accepted"] for e in E)), 4)}
    return out


def part_middles(workers=16):
    with Pool(workers) as P:
        runs = P.map(one_run, [(T, 40, False) for T in starts()], chunksize=1)
    E = [e for r in runs for e in r]
    tm = [e for e in E if e["two_middles_any"]]
    by_n = defaultdict(lambda: [0, 0])
    for e in tm:
        by_n[e["n"] // 10 * 10][0] += 1
        by_n[e["n"] // 10 * 10][1] += not e["keep"]
    return {"runs": len(runs), "extensions": len(E), "two_middles_extensions": len(tm),
            "two_middles_raising": sum(1 for e in tm if not e["keep"]),
            "by_size_band": {f"n {k}-{k + 9}": {"two_middles": v[0], "raising": v[1]} for k, v in sorted(by_n.items())},
            "max_middles_seen_on_raising": max((e["max_middles"] for e in E if not e["keep"]), default=None)}


if __name__ == "__main__":
    part = sys.argv[1]
    f = {"tier0": part_tier0, "middles": part_middles}[part]
    print(json.dumps(f(), indent=1, default=str))
