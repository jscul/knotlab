"""Shared-runner job for the referee's check of GROW-SMALL-20261119-001 (own starts, own growth with the program's fresh rule, own
full tables, exact isometry and states searches; the pairs' starts read from the study's origin.json as data; no study code run).

For each of the 87 pairs (atlas index and loose counts of both starts, and the round):
- both starts rebuilt (each line of the atlas graph one shared distinction, then each junction's loose ones) and their full tables
  (the referee's shore enumeration) compared: isometric with other states (carried) or not isometric (created);
- both grown by the referee's engine (complete rounds, the program's fewest rule: an implied junction gets exactly d, any other
  max(d, 3 - p, 1)) to the recorded round; the two stages: meet once, not isomorphic (incidence graphs), full tables exactly (the
  shore enumeration up to 22 junctions; beyond, every bond by MEET-ONCE-R1's flow-bounded enumeration, the bound raised until every
  pair inside one block of the junction graph has its least bond), isometric (the referee's twin-quotient search, the renaming
  then checked entry by entry), states by GROWN-PAIR-R1's exact search over table isometries;
- one round further: full tables again, isometric or not.

  .venv/bin/python -B scripts/longrun.py launch research/GROW-SMALL-20261119-001/referee-R1/job_growsmall.py \\
      --out runs/referee-growsmall --unit referee-growsmall --workers 4 --case-timeout 3600 --case-mem 3G --mem-max 16G
"""
import itertools
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in ("research/VARIABLE-OUTPUT-READER-20261118-001F/referee-R1", "research/FIRST-KNOT-20261118-001/referee-R1",
          "research/CENSUS-READ-20261118-001/referee-R1", "research/GROWN-PAIR-20261119-001/referee-R1",
          "research/MEET-ONCE-20261119-001/referee-R1", "research/PARENT-RULE-20261119-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))
ORIGIN = ROOT / "artifacts/GROW-SMALL-20261119-001A/GROW-SMALL-20261119-001A-E001_grow/origin.json"


def floored(G, info, rng):
    return [i["d"] if i["implied"] else max(i["d"], 3 - i["p"], 1) for i in info]


def relabel(stars):
    labels = sorted({b for s in stars for b in s})
    idx = {b: i for i, b in enumerate(labels)}
    return [sorted(idx[b] for b in s) for s in stars], len(labels)


def full_table(stars):
    """K matrix of least bond sizes (F.INF where no bond holds both)."""
    import referee_census as RC
    import referee_f as F
    import referee_meet as RM
    import networkx as nx
    S, nb = relabel(stars)
    if len(S) <= 22:
        return np.array(RC.shore_table(S)[0]), S, nb, "shore enumeration"
    # blocks of the junction graph (with the outside vertex): two lines in different blocks lie in no common bond
    V, root, edges, adj = RM.graph(S)
    G = nx.MultiGraph()
    for b, (u, v) in enumerate(edges):
        G.add_edge(u, v, key=b)
    block = {}
    for i, comp in enumerate(nx.biconnected_component_edges(nx.Graph(G))):
        nodes = {x for e in comp for x in e}
        for b, (u, v) in enumerate(edges):
            if u in nodes and v in nodes:
                block.setdefault(b, i)
    need = {(a, b) for a, b in itertools.combinations(range(nb), 2) if block.get(a) == block.get(b)}
    L = 9
    while True:
        t = RM.table8(S, L)
        if need <= set(t) or L >= nb:
            break
        L += 4
    K = np.full((nb, nb), F.INF, dtype=np.int64)
    np.fill_diagonal(K, 0)
    for (a, b), s in t.items():
        K[a][b] = K[b][a] = s
    return K, S, nb, f"bonds of at most {L} distinctions (every pair of one block reached)"


def iso_arr(A, B):
    import networkx as nx

    def inc(stars):
        g = nx.Graph()
        for j, s in enumerate(stars):
            g.add_node(("j", j), k="j")
            for x in s:
                g.add_node(("b", x), k="b")
                g.add_edge(("j", j), ("b", x))
        return g
    return nx.is_isomorphic(inc(A), inc(B), node_match=nx.algorithms.isomorphism.categorical_node_match("k", None))


def meet_once(stars):
    own = defaultdict(list)
    for j, s in enumerate(stars):
        for x in s:
            own[x].append(j)
    c = Counter(tuple(v) for v in own.values() if len(v) == 2)
    return not c or max(c.values()) < 2


def compare(A, B):
    import referee_f as F
    from job_grown import same_states
    KA, SA, na, how_a = full_table(A)
    KB, SB, nb_, how_b = full_table(B)
    out = {"junctions": [len(SA), len(SB)], "distinctions": [na, nb_], "tables by": [how_a, how_b],
           "meet once": [meet_once(SA), meet_once(SB)], "isomorphic as arrangements": iso_arr(SA, SB)}
    if na != nb_:
        out["tables isometric"] = False
        return out
    perm = F.isometric(KA, KB)
    out["tables isometric"] = perm is not None
    if perm is not None:
        perm = list(perm)
        out["renaming checked entry by entry"] = all(KA[x][y] == KB[perm[x]][perm[y]] for x in range(na) for y in range(na))
        ss, steps = same_states(SA, SB, KA, KB, na, cap=5000000)
        out["same states (exact search)"] = ss
        out["search steps"] = steps
    return out


def run(case_id, p):
    import referee_first as RFK
    from job_parent_groups import stars_of
    starts = [stars_of(gi, ell) for _, gi, ell, _ in p["starts"]]
    rnd = p["rounds"][0]
    out = {"recorded kind": p["kind"], "round": rnd, "starts": [s[:3] for s in p["starts"]]}
    out["starts compared"] = compare(starts[0], starts[1])
    stages, nxt = [], []
    for S0 in starts:
        G = RFK.Start([list(s) for s in S0])
        ok = all(G.step(floored, None, None) == "ok" for _ in range(rnd))
        stages.append([sorted(b) for b in G.bits] if ok else None)
        ok2 = ok and G.step(floored, None, None) == "ok"
        nxt.append([sorted(b) for b in G.bits] if ok2 else None)
    if None in stages:
        out["stage"] = "growth ended early"
        return out
    out["stage compared"] = compare(stages[0], stages[1])
    if None not in nxt and max(len(nxt[0]), len(nxt[1])) <= 30:
        out["next round compared"] = compare(nxt[0], nxt[1])
    else:
        out["next round compared"] = "ended or over 30 junctions"
    return out


def cases():
    for i, p in enumerate(json.load(open(ORIGIN))["pairs"]):
        yield f"P-{i:03d}", p
