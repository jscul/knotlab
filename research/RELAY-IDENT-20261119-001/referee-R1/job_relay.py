"""Shared-runner job for the referee's check of RELAY-IDENT-20261119-001 (own relayed model, own growth with the program's fresh
rule, own Theorem 5 check and census tally; built on CHAIN-IDENT-R1's job_chain.py and RING-IDENT-R1's job_ring.py; no study code
imported or run).

The growth: the referee's engine (complete rounds, GF(2) implication) with the program's fewest rule as FRESH-COUNT's
freelib.floored has it: an implied junction gets exactly d, any other max(d, 3 - p, 1).
Parts:
- K-*: every connected knot graph on 2 to 7 knots with (S3) and (S4), no surplus or one surplus at one knot; keys per round to 9
  (parents, fresh, the parents' keys) against the relayed model: every piece's clusters (the referee's lazy cover); a finite
  piece's top with boundary 1 when there are two or more pieces, 0 when it is the only one; and, after a top, the junctions J(i, l)
  of the relay (keys (1, 2) for J(0, 0) and the chain ends, (2, 2) for the others, with their parents' keys).
- D: Theorem 5 on every tree on 2 to 9 knots (networkx's trees), no surplus: the growth's counts to round 24 against D (largest ray
  count of an infinite piece, or 2 if a piece is finite and there are two or more pieces; 0 if one finite piece), the (D - 1)-th
  differences against the stated leading coefficient times (D - 1)!, from the last top or core size on.
- N: the path of seven knots and the spider with four legs of two, counts to round 16.
- C: the touch census (runs/touch-census, as data): every tree-shaped arrangement's measured dimension, and for the simple ones
  that do not stall, the referee's own D read from the census's sizes.

  .venv/bin/python -B scripts/longrun.py launch research/RELAY-IDENT-20261119-001/referee-R1/job_relay.py \\
      --out runs/referee-relay --unit referee-relay --workers 6 --case-timeout 3600 --case-mem 3G --mem-max 16G
"""
import itertools
import json
import math
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/CHAIN-IDENT-20261119-001/referee-R1"))
sys.path.insert(0, str(ROOT / "research/RING-IDENT-20261119-001/referee-R1"))
for p in ("research/FIRST-KNOT-20261118-001/referee-R1", "research/TOUCH-CENSUS-20261118-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))
T = 9


def floored(G, info, rng):
    return [i["d"] if i["implied"] else max(i["d"], 3 - i["p"], 1) for i in info]


def grow_keys(n, edges, sizes, rounds, maxj=50000):
    import job_ring as JR
    import referee_first as RFK
    G = RFK.Start(JR.stars_of(n, edges, sizes))
    inv = defaultdict(Counter)
    base = {}
    for j in range(n):
        base[j] = (0, len(G.loose(j)))
        inv[0][(0, len(G.loose(j)), ())] += 1
    counts = [n]
    for t in range(1, rounds + 1):
        r = G.step(floored, None, None)
        if r != "ok":
            counts.append(r)
            break
        new = [j for j in range(len(G.bits)) if G.round[j] == t]
        counts.append(len(new))
        for j in new:
            base[j] = (len(G.parents[j]), G.fresh[j])
        for j in new:
            inv[t][(base[j][0], base[j][1], tuple(sorted(base[q] for q in G.parents[j])))] += 1
        if len(G.bits) > maxj:
            break
    return inv, counts


def relayed_keys(n, X, m):
    import job_ring as JR
    cov = JR.Cover(X["npts"], X["blocks"])
    live = set(X["live"])
    pieces = [c for c in X["comps"].values() if c["knots"]]
    q = len(pieces)
    finite = [frozenset(c["points"] | c["knots"]) for c in pieces if c["rays"] == 0 and
              c["inc"] <= len(c["points"] | c["knots"]) + c["blocks"] - 1]
    inv = defaultdict(Counter)

    def knot(v):
        return cov.proj(v) < n

    def connected(R):
        R = set(R)
        if not R:
            return False
        st = [next(iter(R))]
        seen = {st[0]}
        while st:
            a = st.pop()
            for b in cov.nbrs(a):
                if b in R and b not in seen:
                    seen.add(b)
                    st.append(b)
        return len(seen) == len(R)

    def rstar(S):
        return [v for v in S if any(knot(x) for x in S - {v}) and connected(S - {v})]

    def bd(S):
        b = len({y for v in S for y in cov.nbrs(v)} - S)
        if b == 0 and q >= 2 and frozenset(cov.proj(v) for v in S) in finite and len({cov.proj(v) for v in S}) == len(S):
            return 1                                     # a finished piece's top, relayed
        return b
    roots = [x for x in range(X["npts"]) if x >= n or x in live]
    for x in roots:
        for S in JR.clusters(cov, (x,), m):
            if not any(knot(v) for v in S):
                continue
            R = rstar(S)
            inv[len(S) - 1][(len(R), bd(S), tuple(sorted((len(rstar(S - {v})), bd(S - {v})) for v in R)))] += Fraction(1, len(S))
    if q >= 2:
        for Y in finite:
            top_round = len(Y) - 1
            # R*(Y): from the enumeration's own top
            topkeys = [k for k in inv[top_round] if k[1] == 1]
            rY = None
            for k in range(n):
                if k in live and k in Y:
                    for S in JR.clusters(cov, (k,), len(Y)):
                        if frozenset(cov.proj(v) for v in S) == Y and len(S) == len(Y):
                            rY = len(rstar(S))
                            break
                    break

            def basek(i, l):
                return (1, 2) if i == 0 or l == 0 else (2, 2)
            for k in range(1, m - len(Y) + 1):
                t = top_round + k
                for i in range(k):
                    l = k - 1 - i
                    if i == 0 and l == 0:
                        key = (1, 2, ((rY, 1),))
                    elif i == 0 or l == 0:
                        key = (1, 2, ((1, 2),))
                    else:
                        key = (2, 2, tuple(sorted([basek(i - 1, l), basek(i, l - 1)])))
                    inv[t][key] += 1
    for k in range(n):
        if k not in live:
            inv[0][(0, 0, ())] += 1
    return inv


def D_of(n, X):
    pieces = [c for c in X["comps"].values() if c["knots"]]
    q = len(pieces)
    fin = [c for c in pieces if c["rays"] == 0]
    if q == 1 and fin:
        return 0, 0, 0
    D = max([c["rays"] for c in pieces if c["rays"] > 0] + ([2] if fin else []))
    return D, q, len(fin)


def part_k(graphs):
    import job_chain as JC
    rows = []
    for n, edges in graphs:
        edges = [tuple(e) for e in edges]
        for surplus in [{}] + [{k: 1} for k in range(n)]:
            X = JC.plus(n, edges, surplus, ray_len=T + 3)
            if not (X["S3"] and X["S4"]):
                continue
            a, counts = grow_keys(n, edges, X["sizes"], T)
            b = relayed_keys(n, X, T + 1)
            bad = [t for t in range(T + 1) if {k: Fraction(v) for k, v in a.get(t, {}).items()} != {k: v for k, v in b.get(t, {}).items() if v}]
            pieces = [c for c in X["comps"].values() if c["knots"]]
            fin = sum(1 for c in pieces if c["rays"] == 0)
            kind = "single finite piece" if len(pieces) == 1 and fin else ("relay" if fin else "chains only")
            rows.append({"n": n, "edges": edges, "surplus": {str(k): v for k, v in surplus.items()}, "kind": kind, "agree": not bad,
                         "rounds that differ": bad, "counts": counts})
    return {"rows": rows}


def part_d():
    import networkx as nx
    import job_chain as JC
    rows = []
    for nn in range(2, 10):
        for tr in nx.nonisomorphic_trees(nn):
            edges = sorted(tuple(sorted(e)) for e in tr.edges())
            X = JC.plus(nn, edges, {}, ray_len=4)
            D, q, nfin = D_of(nn, X)
            _, counts = grow_keys(nn, edges, X["sizes"], 24)
            seq = [c for c in counts if isinstance(c, int)]
            pieces = [c for c in X["comps"].values() if c["knots"]]
            row = {"n": nn, "edges": edges, "D": D, "q": q, "finite pieces": nfin, "counts": seq}
            if D == 0:
                row["ok"] = isinstance(counts[-1], str) and counts[-1] == "closed"
            else:
                _, claim = JC.theorem2(nn, X, 2)
                N = sum(c["N"] for c in claim if c["rays"] == D)
                lead = N + (nfin if D == 2 else 0)
                start = max([len(c["points"] | c["knots"]) for c in pieces] + [0]) + 1
                tail = seq[start:]
                diffs = tail
                for _ in range(D - 1):
                    diffs = [diffs[i + 1] - diffs[i] for i in range(len(diffs) - 1)]
                row["expected (D-1)-th difference"] = lead
                row["(D-1)-th differences"] = diffs[-6:]
                row["ok"] = len(diffs) >= 3 and all(x == lead for x in diffs)
            rows.append(row)
    return {"rows": rows}


def part_n():
    import job_chain as JC
    out = {}
    for name, n, edges in (("path of seven", 7, [(i, i + 1) for i in range(6)]),
                           ("spider with four legs of two", 9, [(0, 1), (1, 2), (0, 3), (3, 4), (0, 5), (5, 6), (0, 7), (7, 8)])):
        X = JC.plus(n, edges, {}, ray_len=4)
        _, counts = grow_keys(n, edges, X["sizes"], 16)
        out[name] = {"counts": counts, "D, q, finite pieces": D_of(n, X), "sizes": X["sizes"]}
    c = out["spider with four legs of two"]["counts"]
    out["spider: c(t) = C(t + 3, 3) + t + 1"] = [[t, c[t], math.comb(t + 3, 3) + t + 1] for t in range(len(c)) if isinstance(c[t], int)]
    return out


def part_c():
    import job_chain as JC
    import job_ring as JR
    import networkx as nx
    rows = []
    for line in open(ROOT / "runs/touch-census/results.jsonl"):
        r = json.loads(line)
        if r.get("status") != "ok":
            continue
        for a in r["result"]["arrangements"]:
            rows.append((a["key"], a["dim"], a["outcome"]))
    tally = Counter()
    cmp = Counter()
    bad = []
    for key, dim, outcome in rows:
        sizes, flat = key
        n = len(sizes)
        if n < 2:
            continue
        pairs = [(i, j) for (i, j), m in zip(itertools.combinations(range(n), 2), flat) if m]
        G = nx.Graph()
        G.add_nodes_from(range(n))
        G.add_edges_from(pairs)
        if not nx.is_connected(G) or len(pairs) != n - 1:
            continue
        simple = all(m <= 1 for m in flat)
        tally[f"{'simple' if simple else 'double touches'}, measured dimension {dim}, {outcome}"] += 1
        if not simple:
            continue
        # the referee's D from the census's own sizes
        sh, d, groups = JR.round1(n, pairs)
        opn = [sizes[k] - sh[k] for k in range(n)]
        if any(d[k] > opn[k] for k in range(n)):
            cmp["stall at round 1"] += 1
            continue
        surplus = {k: opn[k] - max(3 - sh[k], d[k]) for k in range(n) if opn[k] - max(3 - sh[k], d[k]) > 0}
        X = JC.plus(n, pairs, surplus, ray_len=3)
        assert X["sizes"] == list(sizes), (sizes, X["sizes"])
        if not X["S3"]:
            cmp["out by (S3)"] += 1
            continue
        D, q, nfin = D_of(n, X)
        meas = dim if dim is not None else (0 if outcome == "closed" else None)
        cmp["agree" if meas == D else "differ"] += 1
        if meas != D and len(bad) < 6:
            bad.append([key, dim, outcome, D])
    return {"tree-shaped arrangements": dict(sorted(tally.items())), "simple trees: the referee's D against the census": dict(cmp),
            "differences": bad}


def cases():
    import networkx as nx
    items = []
    for G in nx.graph_atlas_g():
        if 2 <= G.number_of_nodes() <= 7 and nx.is_connected(G):
            items.append([G.number_of_nodes(), sorted(tuple(sorted(e)) for e in G.edges())])
    for a in range(0, len(items), 40):
        yield f"K-{a // 40:03d}", {"part": "K", "graphs": items[a:a + 40]}
    yield "D", {"part": "D"}
    yield "N", {"part": "N"}
    yield "C", {"part": "C"}


def run(case_id, p):
    return {"K": lambda: part_k(p["graphs"]), "D": part_d, "N": part_n, "C": part_c}[p["part"]]()
