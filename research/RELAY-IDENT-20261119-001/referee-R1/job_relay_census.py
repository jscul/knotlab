"""Shared-runner job, a second pass for RELAY-IDENT-R1 (after job_relay.py):
- C2: the touch census's simple trees with the round-1 demand counted among live knots, as the growth counts it (a knot with no
  loose distinction joins no group): live knots, d_k, stall, (S3), pieces (live knots joined through common K-neighbours), each live
  knot's open_k - d_k pendant points with R(open_k) rays, and D against the census's measured dimension.  Also how many of these
  starts are not bare-plus-surplus: a non-live knot that has a common K-neighbour with a live knot.
- KINDS: the 218 starts of part K classified again with a finite piece meaning no ray and no cycle.

  .venv/bin/python -B scripts/longrun.py launch research/RELAY-IDENT-20261119-001/referee-R1/job_relay_census.py \\
      --out runs/referee-relay-census --unit referee-relay-census --workers 2 --case-timeout 3600 --case-mem 3G --mem-max 16G
"""
import itertools
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/CHAIN-IDENT-20261119-001/referee-R1"))
sys.path.insert(0, str(ROOT / "research/RING-IDENT-20261119-001/referee-R1"))
for p in ("research/FIRST-KNOT-20261118-001/referee-R1", "research/TOUCH-CENSUS-20261118-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))


def cases():
    yield "C2", {"part": "C2"}
    yield "KINDS", {"part": "KINDS"}


def census():
    import networkx as nx
    import referee_first as RFK
    import job_ring as JR
    rows = []
    for line in open(ROOT / "runs/touch-census/results.jsonl"):
        r = json.loads(line)
        if r.get("status") == "ok":
            rows += [(a["key"], a["dim"], a["outcome"]) for a in r["result"]["arrangements"]]
    cmp, bad = Counter(), []
    for key, dim, outcome in rows:
        sizes, flat = key
        n = len(sizes)
        if n < 2 or any(m > 1 for m in flat):
            continue
        pairs = [(i, j) for (i, j), m in zip(itertools.combinations(range(n), 2), flat) if m]
        G = nx.Graph()
        G.add_nodes_from(range(n))
        G.add_edges_from(pairs)
        if not nx.is_connected(G) or len(pairs) != n - 1:
            continue
        nb = defaultdict(set)
        for a, b in pairs:
            nb[a].add(b)
            nb[b].add(a)
        sh = [len(nb[k]) for k in range(n)]
        opn = [sizes[k] - sh[k] for k in range(n)]
        live = [k for k in range(n) if opn[k] >= 1]
        S = RFK.Start(JR.stars_of(n, pairs, list(sizes)))
        groups = S.groups(live, None) if live else []
        d = Counter(x for g in groups for x in g)
        if any(d[k] > opn[k] for k in live):
            cmp["stall"] += 1
            continue
        if any(len(g) > 2 for g in groups):
            cmp["out by (S3)"] += 1
            continue
        nonbare = any(opn[k] == 0 and any((nb[k] & nb[u]) for u in live if u != k) for k in range(n))
        parent = {k: k for k in live}

        def find(x):
            while parent[x] != x:
                x = parent[x]
            return x
        for w in range(n):
            L = sorted(nb[w] & set(live))
            for a, b in zip(L, L[1:]):
                parent[find(a)] = find(b)
        rays = Counter()
        for k in live:
            R = 0 if opn[k] >= 3 else (1 if opn[k] == 2 else 2)
            rays[find(k)] += (opn[k] - d[k]) * R
        pieces = {find(k) for k in live}
        q = len(pieces)
        fin = [p for p in pieces if rays[p] == 0]
        if q == 0 or (q == 1 and fin):
            D = 0
        else:
            D = max([rays[p] for p in pieces if rays[p] > 0] + ([2] if fin else []))
        meas = dim if dim is not None else (0 if outcome == "closed" else None)
        tag = "agree" if meas == D else "differ"
        cmp[tag] += 1
        cmp[f"{tag}, non-bare (a non-live knot with a candidate)"] += nonbare
        if tag == "differ" and len(bad) < 6:
            bad.append([key, dim, outcome, D])
    return {"simple trees": dict(cmp), "differences": bad}


def kinds():
    import job_chain as JC
    rows = []
    for line in open(ROOT / "runs/referee-relay/results.jsonl"):
        r = json.loads(line)
        if r["case"].startswith("K-"):
            rows += r["result"]["rows"]
    c = Counter()
    for x in rows:
        X = JC.plus(x["n"], [tuple(e) for e in x["edges"]], {int(k): v for k, v in x["surplus"].items()}, ray_len=2)
        pieces = [p for p in X["comps"].values() if p["knots"]]
        fin = [p for p in pieces if p["rays"] == 0 and p["inc"] <= len(p["points"] | p["knots"]) + p["blocks"] - 1]
        kind = "single finite piece" if len(pieces) == 1 and fin else ("relay" if fin else "chains only")
        c[(kind, x["agree"])] += 1
    return {"kinds": {f"{k}: {'agree' if a else 'differ'}": v for (k, a), v in sorted(c.items())}}


def run(case_id, p):
    return census() if p["part"] == "C2" else kinds()
