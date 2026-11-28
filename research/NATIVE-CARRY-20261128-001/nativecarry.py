"""nativecarry.py: whole-choice sets (NATIVE-CARRY-20261128-001; README.md, frozen predictions G, P1-P3).

The candidate cells of a set S of knots are every unheld pair of distinctions (x, y) whose four holders are distinct
and all in S; together they are S's whole choice. S is a whole-choice set (provisional word) when it has a cell and
every pair of knots is a cross pair of an even number of its cells: then its whole choice commutes, with nothing
selected. It is minimal when no proper subset of its knots is one. In the code "carrier" names the same object.
This script
  A  classifies the minimal sets abstractly: every graph on four to seven knots (the literature's atlas, at most one
     distinction per pair of knots), and every pattern on four or five knots with zero, one or two distinctions on each
     pair, at least one pair holding two, and every knot holding one;
  P  lists the minimal sets at the census-start closures, the census types and the closures of the sampled larger
     starts, with each set's sign, cells and kind.
    nativecarry.py [--out DIR] [--probe]
"""
import argparse
import collections
import itertools
import json
import random
import resource
import sys
import time
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "research" / "EVEN-ORIENT-20261127-001"))
import evenorient as EO  # noqa: E402  (history, census_starts, forbid, SECOND_SEED: growth and starts only)

CENSUS = ROOT / "artifacts/FOUR-READINGS-20261120-001A/FOUR-READINGS-20261120-001A-E001_signed_rules/census.json"
FULL_LIMIT = 12        # closures with at most this many knots: every subset; larger ones: subsets of at most SUB_LIMIT
SUB_LIMIT = 8


# ---------------------------------------------------------------- the carrier test

def pattern(values, n):
    """values: list of (u, v) holder pairs, one per distinction; returns the multiplicity matrix"""
    m = [[0] * n for _ in range(n)]
    for u, v in values:
        m[u][v] += 1
        m[v][u] += 1
    return m


def coverage_formula(S, m):
    """the number of cells of S at each pair of its knots, by the formula of item 2"""
    out = {}
    for u, v in itertools.combinations(S, 2):
        mu = sum(m[u][w] for w in S if w != u)
        mv = sum(m[v][w] for w in S if w != v)
        out[(u, v)] = (mu - m[u][v]) * (mv - m[u][v]) - sum(m[u][w] * m[v][w] for w in S if w not in (u, v))
    return out


def cells_of(S, values):
    """the candidate cells of S: pairs of distinctions with four distinct holders, all in S"""
    inside = [(i, p) for i, p in enumerate(values) if p[0] in S and p[1] in S]
    return [(i, j) for (i, p), (j, q) in itertools.combinations(inside, 2) if len({*p, *q}) == 4]


def coverage_direct(S, values, cells):
    cov = collections.Counter()
    for i, j in cells:
        for u in values[i]:
            for v in values[j]:
                cov[tuple(sorted((u, v)))] += 1
    return {pr: cov[pr] for pr in itertools.combinations(sorted(S), 2)}


def sign(cells, values, order):
    """the closing sign: crossing pairs of chords with the knots placed on a circle in this order, mod 2"""
    pos = {k: i for i, k in enumerate(order)}
    s = 0
    for i, j in cells:
        x1, x2 = sorted(pos[k] for k in values[i])
        y1, y2 = sorted(pos[k] for k in values[j])
        s ^= int(x1 < y1 < x2 < y2 or y1 < x1 < y2 < x2)
    return s


def formula_check(n, values):
    """item 2's formula against a direct count, at every pair of the whole pattern"""
    S = list(range(n))
    cells = cells_of(set(S), values)
    direct = coverage_direct(S, values, cells)
    formula = coverage_formula(S, pattern(values, n))
    return all(direct[pr] == formula[pr] for pr in direct)


def is_carrier(S, m):
    if len(S) < 4:
        return False
    cov = coverage_formula(S, m)
    return all(c % 2 == 0 for c in cov.values()) and any(c for c in cov.values())


def minimal_carriers(n, values, limit=None):
    """every minimal carrier among subsets of the n knots (of at most `limit` knots, if given)"""
    m = pattern(values, n)
    found = []
    top = n if limit is None else min(n, limit)
    for size in range(4, top + 1):
        for S in itertools.combinations(range(n), size):
            mask = sum(1 << k for k in S)
            if any(f & mask == f for f in found):
                continue
            if is_carrier(S, m):
                found.append(mask)
    return [[k for k in range(n) if f >> k & 1] for f in found]


FORMULA_FAIL = [0]


def kind(S, values, cells):
    """the cells' meeting pattern with inert distinctions removed: four mutually meeting knots, K_{2,3}, or other"""
    used = collections.Counter(tuple(sorted(values[i])) for i in {i for c in cells for i in c})
    G = nx.Graph()
    G.add_nodes_from(S)
    G.add_edges_from(used)
    if all(k == 1 for k in used.values()):
        if nx.is_isomorphic(G, nx.complete_graph(4)):
            return "four mutually meeting knots"
        if nx.is_isomorphic(G, nx.complete_bipartite_graph(2, 3)):
            return "K_{2,3}"
    return "other"


def swaps(S):
    """the order of S, every order one neighbouring exchange away from it, and two seeded random orders"""
    base = list(S)
    out = [base]
    for i in range(len(base) - 1):
        o = base[:]
        o[i], o[i + 1] = o[i + 1], o[i]
        out.append(o)
    return out


def describe(S, values, rng):
    cells = cells_of(set(S), values)
    orders = swaps(S) + [rng.sample(list(S), len(S)) for _ in range(2)]
    signs = [sign(cells, values, o) for o in orders]
    direct = coverage_direct(S, values, cells)
    m = pattern(values, max(max(p) for p in values) + 1)
    formula = coverage_formula(S, m)
    pair_counts = collections.Counter(tuple(sorted(values[i])) for i in {i for c in cells for i in c})
    return {"knots": len(S), "cells": len(cells), "sign": signs[0], "order independent": len(set(signs)) == 1,
            "formula agrees": all(direct[pr] == formula[pr] for pr in direct),
            "max coverage": max(direct.values()), "covered twice": all(v in (0, 2) for v in direct.values()),
            "doubled": any(k >= 2 for k in pair_counts.values()), "kind": kind(S, values, cells),
            "inert distinctions": sum(1 for i, p in enumerate(values) if p[0] in S and p[1] in S
                                      and not any(i in c for c in cells))}


# ---------------------------------------------------------------- A: abstract classification

def abstract(rng):
    rows = []
    for G in nx.graph_atlas_g():
        n = G.number_of_nodes()
        if n < 4 or min(d for _, d in G.degree()) == 0:
            continue
        values = [tuple(e) for e in G.edges()]
        FORMULA_FAIL[0] += not formula_check(n, values)
        mins = minimal_carriers(n, values)
        if mins == [list(range(n))]:
            d = describe(list(range(n)), values, rng)
            rows.append({"source": "atlas", "graph": nx.to_graph6_bytes(G, header=False).decode().strip(),
                         "edges": len(values), **d})
    seen = set()
    n = 5
    pairs = list(itertools.combinations(range(n), 2))
    for mult in itertools.product((0, 1, 2), repeat=len(pairs)):
        if 2 not in mult:
            continue                      # simple patterns are in the atlas
        values = [p for p, k in zip(pairs, mult) for _ in range(k)]
        G = nx.Graph([p for p, k in zip(pairs, mult) if k])
        if G.number_of_nodes() < n:
            continue
        key = min(tuple(sorted((min(s[a], s[b]), max(s[a], s[b]), k) for (a, b), k in zip(pairs, mult) if k))
                  for s in itertools.permutations(range(n)))
        if key in seen:
            continue
        seen.add(key)
        FORMULA_FAIL[0] += not formula_check(n, values)
        if minimal_carriers(n, values) == [list(range(n))]:
            rows.append({"source": "five knots, doubled", "pattern": key, "edges": len(values),
                         **describe(list(range(n)), values, rng)})
    # four knots with doubled meetings
    n = 4
    pairs = list(itertools.combinations(range(n), 2))
    seen = set()
    for mult in itertools.product((0, 1, 2), repeat=len(pairs)):
        if 2 not in mult:
            continue
        values = [p for p, k in zip(pairs, mult) for _ in range(k)]
        key = min(tuple(sorted((min(s[a], s[b]), max(s[a], s[b]), k) for (a, b), k in zip(pairs, mult) if k))
                  for s in itertools.permutations(range(n)))
        if key in seen:
            continue
        seen.add(key)
        if min(sum(1 for p, k in zip(pairs, mult) if k and v in p) for v in range(n)) == 0:
            continue
        FORMULA_FAIL[0] += not formula_check(n, values)
        if minimal_carriers(n, values) == [list(range(n))]:
            rows.append({"source": "four knots, doubled", "pattern": key, "edges": len(values),
                         **describe(list(range(n)), values, rng)})
    return rows


# ---------------------------------------------------------------- P: populations

def closure_values(supports):
    hold = collections.defaultdict(list)
    for k, row in enumerate(supports):
        for d in row:
            hold[d].append(k)
    return [tuple(h) for _, h in sorted(hold.items())]


ORDER_FAIL = [0]


def read_population(name, items, rng, probe):
    rows = []
    t = time.time()
    for idx, (n, values, extra) in enumerate(items):
        limit = None if n <= FULL_LIMIT else SUB_LIMIT
        mins = minimal_carriers(n, values, limit)
        found = [{"set": S, **describe(S, values, rng)} for S in mins]
        whole = is_carrier(list(range(n)), pattern(values, n))
        FORMULA_FAIL[0] += not formula_check(n, values)
        wcells = cells_of(set(range(n)), values) if whole else []
        wsigns = {sign(wcells, values, o) for o in swaps(range(n))} if whole else set()
        wsign = min(wsigns) if whole else None
        if len(wsigns) > 1:
            ORDER_FAIL[0] += 1
        rows.append({"population": name, "index": idx, "knots": n, "distinctions": len(values),
                     "subsets up to": limit or n, "whole closure a carrier": whole, "whole closure sign": wsign,
                     "minimal carriers": found, **extra})
        if probe and idx >= 150:
            break
    print(f"{name}: {len(rows)} read, {time.time() - t:.1f}s", flush=True)
    return rows


def grown_items(starts, rounds, cap, prior=None):
    out = []
    for i, s in enumerate(starts):
        outcome, stages = EO.history(s, rounds, cap)
        if outcome != "grown closed":
            continue
        extra = {"start index": i, "rounds": len(stages) - 1, "start knots": s[0]}
        if prior is not None:
            assert i in prior, f"census start {i} closes but has no recorded birth verdict"
            extra["birth choices attain odd"] = prior[i]
        out.append((len(stages[-1]), closure_values(stages[-1]), extra))
    return out


def census_odd():
    """from the commutation-at-birth study's rows: does some birth choice close odd, per census start (any choice)"""
    out = {}
    for line in open(ROOT / "research/LOCAL-COMMUTE-20261127-001/results.jsonl"):
        r = json.loads(line)
        if "closing round" in r and r["rounds"] > 0:
            out[r["start"]] = r["birth choices attain odd"]
    return out


def ckeys(c):
    return {str(k): v for k, v in sorted(c.items(), key=lambda kv: str(kv[0]))}


PETERSEN = [(i, (i + 1) % 5) for i in range(5)] + [(i, i + 5) for i in range(5)] + \
           [(5 + i, 5 + (i + 2) % 5) for i in range(5)]


def fixture(vals):
    n = 1 + max(max(p) for p in vals)
    whole = is_carrier(list(range(n)), pattern(vals, n))
    cells = cells_of(set(range(n)), vals)
    mins = minimal_carriers(n, vals)
    return {"whole set closes": whole, "sign": sign(cells, vals, list(range(n))) if whole else None,
            "cells": len(cells), "minimal sets": len(mins),
            "whole set minimal": mins == [list(range(n))]}


def grown_fixture(index):
    outcome, stages = EO.history(EO.census_starts()[index], EO.CENSUS_ROUNDS, EO.CENSUS_CAP)
    vals = closure_values(stages[-1])
    n = len(stages[-1])
    mins = minimal_carriers(n, vals)
    rng = random.Random(index)
    found = [describe(S, vals, rng) for S in mins]
    return {"outcome": outcome, "knots": n, "minimal sets": len(mins),
            "odd kinds": sorted(f["kind"] for f in found if f["sign"])}


def summarise(A, P):
    g, s = {}, {}
    fixtures = {"four mutually meeting knots": [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)],
                "K_{2,3}": [(a, b) for a in (0, 1) for b in (2, 3, 4)],
                "the ring of five with a knot meeting all five": [(0, i) for i in range(1, 6)] +
                                                                  [(i, i % 5 + 1) for i in range(1, 6)],
                "a ring of four": [(0, 1), (1, 2), (2, 3), (0, 3)],
                "a ring of three and a separate meeting": [(0, 1), (1, 2), (0, 2), (3, 4)],
                "a doubled meeting and a separate meeting": [(0, 1), (0, 1), (2, 3)],
                "the literature's Petersen graph": PETERSEN}
    fx = {name: fixture(vals) for name, vals in fixtures.items()}
    fx["census start 17's closure"] = grown_fixture(17)
    fx["census start 5088's closure"] = grown_fixture(5088)
    g["fixtures"] = (fx["four mutually meeting knots"]["sign"] == 1 and fx["four mutually meeting knots"]["whole set minimal"]
                     and fx["K_{2,3}"]["sign"] == 1 and fx["K_{2,3}"]["whole set minimal"]
                     and not fx["the ring of five with a knot meeting all five"]["whole set closes"]
                     and not fx["a ring of four"]["whole set closes"]
                     and fx["a ring of three and a separate meeting"]["sign"] == 0
                     and fx["a doubled meeting and a separate meeting"]["sign"] == 0
                     and fx["the literature's Petersen graph"]["sign"] == 1
                     and fx["the literature's Petersen graph"]["whole set minimal"]
                     and fx["the literature's Petersen graph"]["cells"] == 75
                     and fx["census start 17's closure"]["odd kinds"][:1] == ["four mutually meeting knots"]
                     and fx["census start 5088's closure"]["minimal sets"] == 0)
    allc = list(A) + [c for r in P for c in r["minimal carriers"]]
    g["the formula equals a direct count at every pair of every whole pattern examined"] = FORMULA_FAIL[0] == 0
    g["every set's sign is the same under every neighbouring exchange and two random orders"] = (
        all(c["order independent"] for c in allc) and ORDER_FAIL[0] == 0)
    g["every minimal set on an outerplanar graph of the atlas closes even"] = all(
        c["sign"] == 0 for c in A if c.get("source") == "atlas"
        and nx.check_planarity(outer(nx.from_graph6_bytes(c["graph"].encode())))[0])
    r1 = [r for r in P if r["population"] == "census starts" and r.get("rounds") == 1]
    g["round-1 census closures: the whole closure a set at 145 of 1,713, odd at 53 (rule R at birth)"] = (
        len(r1), sum(r["whole closure a carrier"] for r in r1), sum(r["whole closure sign"] == 1 for r in r1)) == (
        1713, 145, 53)
    g["all gates"] = all(g.values())
    s["fixtures"] = fx
    odd_atlas = [c for c in A if c["sign"] == 1 and c["source"] == "atlas"]
    odd_doubled = [c for c in A if c["sign"] == 1 and c["source"] != "atlas"]
    s["P1"] = {"holds": all(c["kind"] != "other" for c in odd_atlas + odd_doubled),
               "minimal odd sets, atlas": ckeys(collections.Counter(c["kind"] for c in odd_atlas)),
               "minimal odd sets, with a doubled meeting": ckeys(collections.Counter(c["kind"] for c in odd_doubled)),
               "minimal even sets (source, knots, cells)": ckeys(collections.Counter(
                   (c["source"], c["knots"], c["cells"]) for c in A if c["sign"] == 0))}
    pops = sorted({r["population"] for r in P})
    pop_odd = [c for r in P for c in r["minimal carriers"] if c["sign"]]
    s["P2"] = {"holds": all(c["kind"] != "other" for c in pop_odd),
               "odd minimal sets in the populations": len(pop_odd),
               "of another kind": [dict(population=r["population"], index=r["index"], set=c["set"], cells=c["cells"])
                                   for r in P for c in r["minimal carriers"] if c["sign"] and c["kind"] == "other"]}
    by_pop = {}
    for name in pops:
        rows = [r for r in P if r["population"] == name]
        odd_ix = {r["index"] for r in rows if any(c["sign"] for c in r["minimal carriers"])}
        entry = {"closures or types": len(rows),
                 "with a minimal set": sum(bool(r["minimal carriers"]) for r in rows),
                 "with an odd minimal set": len(odd_ix),
                 "odd set kinds": ckeys(collections.Counter(c["kind"] for r in rows for c in r["minimal carriers"]
                                                            if c["sign"])),
                 "even set kinds (kind, knots, cells)": ckeys(collections.Counter(
                     (c["kind"], c["knots"], c["cells"]) for r in rows for c in r["minimal carriers"] if not c["sign"])),
                 "whole closure a set": sum(r["whole closure a carrier"] for r in rows),
                 "whole closure a set, odd": sum(r["whole closure sign"] == 1 for r in rows),
                 "read with subsets of at most eight knots only": sum(r["subsets up to"] < r["knots"] for r in rows)}
        if any("birth choices attain odd" in r for r in rows):
            att = {r["index"] for r in rows if r.get("birth choices attain odd")}
            later = {r["index"] for r in rows if r.get("rounds", 0) > 1}
            entry["attaining odd under birth choices"] = len(att)
            entry["of those, with an odd minimal set"] = len(att & odd_ix)
            entry["odd minimal set but birth choices never odd (later rounds only)"] = len((odd_ix - att) & later)
            entry["odd minimal set but birth choices never odd, round 1 (0 by construction)"] = len((odd_ix - att) - later)
        by_pop[name] = entry
    s["P3"] = by_pop
    return g, s


def outer(G):
    """the literature's test of outerplanarity: planar after adding one knot meeting every knot"""
    H = nx.Graph(G)
    H.add_edges_from(("apex", v) for v in G.nodes())
    return H


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(HERE))
    ap.add_argument("--probe", action="store_true")
    a = ap.parse_args()
    out = Path(a.out)
    rng = random.Random(20261128)
    t0 = time.time()
    A = abstract(rng)
    print(f"A: {len(A)} minimal carriers, {time.time() - t0:.1f}s", flush=True)
    census = json.loads(CENSUS.read_text())
    types = []
    for i, row in enumerate(census):
        ends = [tuple(p) for p in row["sharing"]]
        types.append((1 + max(max(p) for p in ends), ends, {"type": i}))
    odd = census_odd()
    P = []
    P += read_population("census starts", grown_items(EO.census_starts(), EO.CENSUS_ROUNDS, EO.CENSUS_CAP, odd),
                         rng, a.probe)
    P += read_population("census types", types, rng, a.probe)
    P += read_population("extension", grown_items(EO.forbid.extension(), EO.ROUNDS, EO.CAP), rng, a.probe)
    second = [s for n in EO.forbid.SAMPLE_SIZES for s in EO.forbid.sampled(n, 10000, EO.SECOND_SEED + n)]
    P += read_population("second sample", grown_items(second, EO.ROUNDS, EO.CAP), rng, a.probe)
    secs = round(time.time() - t0, 1)
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024
    if a.probe:
        print(f"probe done in {secs}s, peak {peak} MiB; nothing written", flush=True)
        return
    g, s = summarise(A, P)
    s["seconds"], s["peak MiB"] = secs, peak
    (out / "gates.json").write_text(json.dumps(g, indent=1) + "\n")
    (out / "summary.json").write_text(json.dumps(s, indent=1, default=list) + "\n")
    (out / "abstract.json").write_text(json.dumps(A, indent=1, default=list) + "\n")
    with open(out / "rows.jsonl", "w") as fh:
        for r in P:
            fh.write(json.dumps(r, default=list) + "\n")
    print(f"done in {secs}s, peak {peak} MiB", flush=True)


if __name__ == "__main__":
    main()
