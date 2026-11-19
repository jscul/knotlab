"""Shared-runner job for the referee's check of PARENT-RULE-20261119-001 (own growth, own properties, own tables; no study code
imported or run).

Parts (case prefixes):
- C-*: every census start (runs/census-exact5 keys, all 26,441, the study's pending shard included), grown in complete rounds by
  the referee's engine (fewest counts, GF(2) implication) to round 8 or 40 junctions.  At every stage of round >= 1: live junctions
  (holders of a loose distinction) pairwise apart (P2); for every live junction and any two junctions it meets, a third junction
  meeting both that holds no loose distinction (P1+); removing the live junctions gives the previous stage exactly (an open
  stage), or removing the last junction does (a closed one); the static peel depth at least the round.  On open stages of at
  most 12 junctions, Theorem 3: for every two distinctions of the previous stage, the least bond through both in this stage
  against the previous one (the referee's shore enumeration).
- S-*: every connected graph of the networkx atlas on 2 to 7 points as the junctions (each line one shared distinction), with
  a loose count per junction (0..3; 0..2 at 7 points).  Legal: every junction of three places or more, no cut point but the
  outside.  The number of legal orbits under the graph's automorphisms by Burnside's lemma (fixed legal vectors per
  automorphism), and one representative per orbit (the least image), each with its exact table's invariant (the referee's shore
  enumeration and refinement) and the properties P1, P1+, P2, the stratum and the peel depth.

  .venv/bin/python -B scripts/longrun.py launch research/PARENT-RULE-20261119-001/referee-R1/job_parent.py \\
      --out runs/referee-parent --unit referee-parent --workers 6 --case-timeout 3600 --case-mem 2G --mem-max 16G
"""
import itertools
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in ("research/VARIABLE-OUTPUT-READER-20261118-001F/referee-R1", "research/FIRST-KNOT-20261118-001/referee-R1",
          "research/CENSUS-READ-20261118-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))
SHARD = 500


# ---------------------------------------------------------------- properties (the referee's own)

def owners(stars):
    own = defaultdict(list)
    for j, s in enumerate(stars):
        for b in s:
            own[b].append(j)
    return own


def props(stars):
    own = owners(stars)
    nb = [set() for _ in stars]
    for js in own.values():
        if len(js) == 2:
            nb[js[0]].add(js[1])
            nb[js[1]].add(js[0])
    live = {js[0] for js in own.values() if len(js) == 1}
    p1 = p1p = p2 = 0
    for j in live:
        for u, v in itertools.combinations(sorted(nb[j]), 2):
            third = (nb[u] & nb[v]) - {j}
            p1 += not third
            p1p += not (third - live)
    p2 = sum(1 for u, v in itertools.combinations(sorted(live), 2) if v in nb[u])
    stratum = "closed" if not live else ("pendant-only" if all(len(nb[j]) <= 1 for j in live) else "backed")
    return {"P1": p1, "P1+": p1p, "P2": p2, "stratum": stratum, "live": live}


def peel(stars):
    live = props(stars)["live"]
    return [s for j, s in enumerate(stars) if j not in live]


def depth(stars, cap=64):
    d, cur = 0, stars
    while d < cap and cur:
        p = props(cur)
        if not p["live"] or p["P1+"] or p["P2"]:
            return d
        d += 1
        cur = peel(cur)
    return d


# ---------------------------------------------------------------- part C

def part_c(keys):
    import referee_first as RFK
    import referee_census as RC
    import referee_f as F
    viol = defaultdict(int)
    tally = defaultdict(int)
    for ix, key in keys:
        G = RFK.Start(RC.stars_of(tuple(map(tuple, key))))
        prev = [frozenset(s) for s in G.bits]
        for rnd in range(1, 9):
            if len(G.bits) > 40:
                break
            r = G.step(RFK.fewest, None, None)
            if r != "ok":
                break
            if len(G.bits) > 40:
                break
            stars = [frozenset(s) for s in G.bits]
            p = props(stars)
            tally["stages"] += 1
            tally["meet once"] += max((v for v in __import__("collections").Counter(
                tuple(js) for js in owners(stars).values() if len(js) == 2).values()), default=0) < 2
            viol["P2"] += p["P2"] > 0
            viol["P1+"] += p["P1+"] > 0
            if p["live"]:
                tally["open"] += 1
                back = [s for j, s in enumerate(stars) if j not in p["live"]]
                viol["peel"] += sorted(map(sorted, back)) != sorted(map(sorted, prev))
            else:
                tally["closed"] += 1
                viol["peel"] += sorted(map(sorted, stars[:-1])) != sorted(map(sorted, prev))
            d = depth(stars)
            viol["depth < round"] += p["live"] != set() and d < rnd
            if p["live"] and len(stars) <= 12 and len(prev) >= 2:
                Kn, ln = RC.shore_table([sorted(s) for s in stars])
                Ko, lo = RC.shore_table([sorted(s) for s in prev])
                inn = {b: i for i, b in enumerate(ln)}
                for a, b in itertools.combinations(range(len(lo)), 2):
                    o, n = Ko[a][b], Kn[inn[lo[a]]][inn[lo[b]]]
                    o, n = (99 if o >= F.INF else int(o)), (99 if n >= F.INF else int(n))
                    tally["T3 equal" if n == o else ("T3 shorter" if n < o else "T3 farther")] += 1
                tally["T3 stages"] += 1
            prev = stars
    return {"violations": dict(viol), "tally": dict(tally)}


# ---------------------------------------------------------------- part S

def legal_supports(g, n):
    """For each set of junctions holding a loose distinction (bitmask), is there no cut point but the outside?"""
    import networkx as nx
    ok = {}
    for m in range(1 << n):
        h = nx.Graph(g)
        for j in range(n):
            if m >> j & 1:
                h.add_edge(j, "o")
        ok[m] = not (set(nx.articulation_points(h)) - {"o"})
    return ok


def part_s(graphs):
    import networkx as nx
    from networkx.algorithms import isomorphism
    import referee_census as RC
    import referee_f as F
    atlas = nx.graph_atlas_g()
    rows, burnside = [], {}
    for gi in graphs:
        g = nx.convert_node_labels_to_integers(atlas[gi])
        n = g.number_of_nodes()
        lmax = 3 if n <= 6 else 2
        auts = [tuple(m[i] for i in range(n)) for m in isomorphism.GraphMatcher(g, g).isomorphisms_iter()]
        sup = legal_supports(g, n)
        deg = [g.degree(j) for j in range(n)]

        def legal(ell):
            return all(deg[j] + ell[j] >= 3 for j in range(n)) and sup[sum(1 << j for j in range(n) if ell[j])]
        fixed = 0
        vecs = list(itertools.product(range(lmax + 1), repeat=n))
        L = [ell for ell in vecs if legal(ell)]
        for s in auts:
            fixed += sum(1 for ell in L if all(ell[s[i]] == ell[i] for i in range(n)))
        assert fixed % len(auts) == 0
        burnside[gi] = [n, fixed // len(auts)]
        edges = sorted(tuple(sorted(e)) for e in g.edges())
        for ell in L:
            if min(tuple(ell[s[i]] for i in range(n)) for s in auts) != ell:
                continue
            stars = [set() for _ in range(n)]
            b = 0
            for u, v in edges:
                stars[u].add(b)
                stars[v].add(b)
                b += 1
            for j in range(n):
                for _ in range(ell[j]):
                    stars[j].add(b)
                    b += 1
            K, labels = RC.shore_table([sorted(s) for s in stars])
            p = props([frozenset(s) for s in stars])
            rows.append([n, gi, "".join(map(str, ell)), F.invariant(K), len(labels), p["P1"], p["P1+"], p["P2"], p["stratum"][0],
                         depth([frozenset(s) for s in stars])])
    return {"burnside": burnside, "rows": rows}


def cases():
    import networkx as nx
    keys = []
    for line in open(ROOT / "runs/census-exact5/results.jsonl"):
        r = json.loads(line)
        if r.get("status") == "ok" and r["case"].startswith("census"):
            keys += [[a["index"], a["key"]] for a in r["result"]["arrangements"]]
    keys.sort()
    for a in range(0, len(keys), SHARD):
        yield f"C-{a // SHARD:03d}", {"part": "C", "keys": keys[a:a + SHARD]}
    by_n = defaultdict(list)
    for i, g in enumerate(nx.graph_atlas_g()):
        if 2 <= g.number_of_nodes() <= 7 and nx.is_connected(g):
            by_n[g.number_of_nodes()].append(i)
    for n, idx in sorted(by_n.items()):
        step = 8 if n == 7 else (12 if n == 6 else len(idx))
        for k in range(0, len(idx), step):
            yield f"S-{n}-{k // step:03d}", {"part": "S", "graphs": idx[k:k + step]}


def run(case_id, p):
    return part_c(p["keys"]) if p["part"] == "C" else part_s(p["graphs"])
