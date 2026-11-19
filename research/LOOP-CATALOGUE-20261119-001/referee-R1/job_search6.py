"""Shared-runner job for the referee's independent eddy search of LOOP-CATALOGUE-20261119-001 up to six knots: every connected
simple knot graph on 2 to 6 knots (networkx's graph atlas), at bare sizes (max(3, shared + round-1 demand), the demand read from
the referee's engine's own round-1 groups) plus no spare, one spare at any knot, or two spares (at one knot or two); each grown by
the referee's own engine for up to 36 rounds, 30,000 junctions, or before a round with more than 6,000 live junctions.

  .venv/bin/python -B scripts/longrun.py launch research/LOOP-CATALOGUE-20261119-001/referee-R1/job_search6.py \\
      --out runs/referee-loop-search6 --unit referee-loop-search6 --workers 6 --case-timeout 300 --case-mem 2G --mem-max 16G
"""
import itertools
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in ("research/FIRST-KNOT-20261118-001/referee-R1", "research/TOUCH-CENSUS-20261118-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))
sys.path.insert(0, str(HERE))


def cases():
    import networkx as nx
    k = 0
    for gi, G in enumerate(nx.graph_atlas_g()):
        n = G.number_of_nodes()
        if n < 2 or n > 6 or not nx.is_connected(G):
            continue
        edges = sorted(tuple(sorted(e)) for e in G.edges())
        placements = [()] + [(v,) for v in range(n)] + list(itertools.combinations_with_replacement(range(n), 2))
        for pl in placements:
            yield f"g{gi:04d}-{'-'.join(map(str, pl)) or 'none'}", {"n": n, "edges": edges, "spares": list(pl), "atlas": gi}
            k += 1


def run(case_id, payload):
    import referee_first as RFK
    import referee_touch as RT
    import referee_loop as RL
    n, edges = payload["n"], [tuple(e) for e in payload["edges"]]
    spares = [0] * n
    for v in payload["spares"]:
        spares[v] += 1
    sizes = RL.bare(n, edges, spares)
    M = [[0] * n for _ in range(n)]
    for a, b in edges:
        M[a][b] += 1
        M[b][a] += 1
    G = RFK.Start(RT.stars(sizes, M))
    out = "alive"
    for _ in range(36):
        if len([j for j in G.live if G.loose(j)]) > 6000:
            out = "live cap"
            break
        r = G.step(RFK.fewest, None, None)
        if r != "ok":
            out = r
            break
        if len(G.bits) > 30000:
            out = "cap"
            break
    c = G.counts()
    ratios = [c[i] / c[i - 1] for i in range(max(1, len(c) - 4), len(c)) if c[i - 1]]
    if out in ("cap", "live cap") and ratios and min(ratios) >= 1.2:
        cls = "explosive"
    else:
        cls = RL.classify(c, out).split(" (")[0]
    return {"n": n, "edges": payload["edges"], "spares": payload["spares"], "sizes": sizes, "class": cls, "outcome": out,
            "counts": c[:40]}
