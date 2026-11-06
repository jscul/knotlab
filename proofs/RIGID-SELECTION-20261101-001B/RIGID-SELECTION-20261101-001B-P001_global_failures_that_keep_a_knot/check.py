#!/usr/bin/env python3
"""Checks for RIGID-SELECTION-20261101-001B: global failures that keep a knot.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx)."""
import collections
import hashlib
import itertools
import json
import math
import random
import sys
import time
from pathlib import Path

import networkx as nx
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/RIGID-SELECTION-20261101-001A/RIGID-SELECTION-20261101-001A-P001_where_selection_is_rigid"))
import zlocal as Z  # noqa: E402

T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:600], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        print(json.dumps(info, default=str, indent=1))
        sys.exit(1)


# ------------------------------------------------------------------------------------------------ 0. bindings
manifest = json.loads((HERE / "manifest.json").read_text())
bad = {p: d for p, d in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != d}
status = {p: json.loads((ROOT / p).read_text()).get("status") for p in manifest["parent_bindings"]
          if p.endswith(".json") and p.startswith("proofs/")}
check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
      {"mismatched": bad, "statuses": status})


def brute(A, c, q, skip=None):
    n = len(A[0])
    X = np.array(list(itertools.product(range(q), repeat=n)), dtype=np.int64)
    ok = np.ones(len(X), dtype=bool)
    for i, (row, b) in enumerate(zip(A, c)):
        if i != skip:
            ok &= (X @ np.array(row) - b) % q == 0
    return [tuple(int(v) for v in x) for x in X[ok]]


def is_cyclic(K, q):
    if len(K) <= 1:
        return True
    return max(math.lcm(*[q // math.gcd(x, q) for x in v]) for v in K) == len(K)


def substrate_ok(lines, n, k):
    g = nx.Graph([(("l", i), ("p", p)) for i, L in enumerate(lines) for p in L])
    return (len(lines) == n and all(len(set(L)) == k for L in lines) and all(sum(p in L for L in lines) == k for p in range(n))
            and len({frozenset(L) for L in lines}) == n and nx.is_connected(g))


def example_report(lines, A, c, q, k):
    n = len(A)
    signs_ok = all((A[i][p] in (1, q - 1)) == (p in L) or (A[i][p] == 0 and p not in L) for i, L in enumerate(lines) for p in range(n))
    rep = {"substrate: connected, %d-regular, %d-uniform, simple" % (k, k): substrate_ok(lines, n, k),
           "coefficients are signs (+1 or -1 on incidences, 0 elsewhere)": signs_ok,
           "fails (brute force)": not brute(A, c, q), "removals": []}
    glob, kept = True, 0
    for i in range(n):
        sol = brute(A, c, q, skip=i)
        K = brute(A, [0] * n, q, skip=i)
        knots = sorted(sorted(C) for C in Z.circuits(sol, n) if len(C) >= 3)
        glob &= bool(sol)
        kept += bool(knots)
        rep["removals"].append({"line": i, "solutions": len(sol), "solution group cyclic": is_cyclic(K, q), "knots": knots[:3]})
    rep["global"] = glob
    rep["lines whose removal keeps a knot"] = kept
    return rep


# ------------------------------------------------------------------------------------------------ 1. signed Z4 at four places
L4 = [[5, 2, 1, 3], [0, 4, 1, 5], [0, 2, 4, 1], [0, 4, 3, 2], [3, 5, 1, 0], [5, 2, 4, 3]]
A4 = [[0, 3, 3, 3, 0, 3], [1, 3, 0, 0, 1, 3], [3, 1, 1, 0, 1, 0], [3, 0, 1, 3, 3, 0], [3, 1, 0, 3, 0, 1], [0, 0, 1, 1, 1, 1]]
c4 = [2, 0, 0, 0, 0, 0]
rep1 = example_report(L4, A4, c4, 4, 4)
ok1 = (rep1["substrate: connected, 4-regular, 4-uniform, simple"] and rep1["coefficients are signs (+1 or -1 on incidences, 0 elsewhere)"]
       and rep1["fails (brute force)"] and rep1["global"] and rep1["lines whose removal keeps a knot"] == 6
       and all(r["solutions"] == 8 and not r["solution group cyclic"] for r in rep1["removals"]))
check("1 signed Z4 at four places fails globally on a 6-point 4-regular substrate, and removing any of its 6 lines leaves 8 solutions, "
      "a non-cyclic group, and a knot of three variables (brute force over Z4^6)", ok1, rep1)

# ------------------------------------------------------------------------------------------------ 2. signed Z4 at three places
L3 = [[1, 8, 2], [8, 1, 5], [8, 0, 7], [6, 3, 0], [3, 4, 2], [5, 4, 2], [3, 5, 7], [1, 7, 6], [4, 6, 0]]
A3 = [[0, 1, 1, 0, 0, 0, 0, 0, 3], [0, 3, 0, 0, 0, 1, 0, 0, 1], [1, 0, 0, 0, 0, 0, 0, 1, 1], [3, 0, 0, 1, 0, 0, 3, 0, 0],
      [0, 0, 1, 3, 3, 0, 0, 0, 0], [0, 0, 3, 0, 1, 3, 0, 0, 0], [0, 0, 0, 3, 0, 1, 0, 3, 0], [0, 3, 0, 0, 0, 0, 1, 1, 0],
      [1, 0, 0, 0, 1, 0, 3, 0, 0]]
c3 = [1, 0, 0, 0, 0, 0, 0, 0, 0]
rep2 = example_report(L3, A3, c3, 4, 3)
ok2 = (rep2["substrate: connected, 3-regular, 3-uniform, simple"] and rep2["coefficients are signs (+1 or -1 on incidences, 0 elsewhere)"]
       and rep2["fails (brute force)"] and rep2["global"] and rep2["lines whose removal keeps a knot"] >= 1
       and all(not r["solution group cyclic"] for r in rep2["removals"] if r["knots"]))
check("2 signed Z4 at three places fails globally on a 9-point cubic substrate, and removing a line leaves 8 solutions with a knot "
      "(brute force over Z4^9)", ok2, rep2)

# ------------------------------------------------------------------------------------------------ 3-4. the cubic census
CENSUS = json.loads((ROOT / "research/MUTUAL-SELECTION-20261031-001C/census.json").read_text())
GRAPHS = [(int(n), [tuple(L) for L in row["lines"]]) for n, v in sorted(CENSUS.items(), key=lambda kv: int(kv[0])) for row in v["rows"]]


def dual(lines, n):
    return [tuple(i for i, L in enumerate(lines) if p in L) for p in range(n)]


def canon(lines, n):
    return min(tuple(sorted(tuple(sorted(perm[p] for p in L)) for L in lines)) for perm in itertools.permutations(range(n)))


# the census lists incidence graphs (all 60 connected cubic bipartite graphs on at most 16 vertices); a substrate is a graph with
# one side read as lines, so each graph gives itself and its dual, which coincide up to isomorphism for 47 of the 60
SUBS = []
for n, lines in GRAPHS:
    SUBS.append((n, lines))
    if canon(lines, n) != canon(dual(lines, n), n):
        SUBS.append((n, dual(lines, n)))
check("3a the census read both ways: 60 incidence graphs give 73 connected cubic substrates with at most 8 points up to isomorphism",
      len(GRAPHS) == 60 and len({canon(L, n) for n, L in SUBS}) == len(SUBS) == 73, {"graphs": len(GRAPHS), "substrates": len(SUBS)})


def signing_classes(lines, n, units):
    edges = [(i, p) for i, L in enumerate(lines) for p in L]
    adj = collections.defaultdict(list)
    for i, p in edges:
        adj[("l", i)].append((("p", p), (i, p)))
        adj[("p", p)].append((("l", i), (i, p)))
    seen, tree, stack = {("l", 0)}, set(), [("l", 0)]
    while stack:
        u = stack.pop()
        for v, e in adj[u]:
            if v not in seen:
                seen.add(v)
                tree.add(e)
                stack.append(v)
    others = [e for e in edges if e not in tree]
    for choice in itertools.product(units, repeat=len(others)):
        s = {e: 1 for e in edges}
        s.update(dict(zip(others, choice)))
        yield s


def analyse(A, p, kk):
    """for one global class (if any): (global?, lines keeping a knot, non-rigid removals all with non-cyclic groups?)"""
    n = len(A)
    q = p ** kk
    g, gens, glob = Z.global_classes(A, p, kk)
    if not glob:
        return None
    _, cls = Z.coker(A, p, kk)
    orders = [Z.order_of(x, g) for x in gens]
    L0 = min(range(n), key=lambda L: orders[L])
    t = next(t for t in range(1, q) if cls([t if j == L0 else 0 for j in range(n)]) == glob[0])
    c = [t if j == L0 else 0 for j in range(n)]
    kept, consistent = 0, True
    for i in range(n):
        rows = [r for j, r in enumerate(A) if j != i]
        rhs = [b for j, b in enumerate(c) if j != i]
        sol = Z.solutions(rows, rhs, p, kk, n)
        if any(len(C) >= 3 for C in Z.circuits(sol, n)):
            kept += 1
            consistent &= not is_cyclic(Z.solutions(rows, [0] * len(rhs), p, kk, n), q)
    return kept, consistent


tally3 = collections.Counter()
for n, lines in SUBS:
    with_glob = with_knot = 0
    for s in signing_classes(lines, n, [1, 3]):
        A = [[s[(i, p)] if p in L else 0 for p in range(n)] for i, L in enumerate(lines)]
        r = analyse(A, 2, 2)
        if r is None:
            continue
        with_glob += 1
        with_knot += r[0] > 0
    tally3["substrates"] += 1
    tally3["substrates where signed Z4 fails globally"] += with_glob > 0
    tally3["signing classes failing globally"] += with_glob
    tally3["signing classes failing globally and keeping a knot"] += with_knot
check("3 signed Z4 at three places on all 73 connected cubic substrates with at most 8 points, every signing class: its global "
      "failures are all rigid, so a cubic signed Z4 space that keeps a knot needs at least 9 points (check 2 has 9)",
      tally3["signing classes failing globally and keeping a knot"] == 0 and tally3["substrates where signed Z4 fails globally"] >= 1,
      dict(tally3))

rng = random.Random(20261101)
info4, ok4 = {}, True
for p, kk in ((2, 3), (3, 2), (5, 2), (3, 3)):
    q = p ** kk
    units = [u for u in range(1, q) if math.gcd(u, q) == 1]
    hosts, glob_n, nonrigid_n = set(), 0, 0
    for idx, (n, lines) in enumerate(SUBS):
        if len({frozenset(L) for L in lines}) < len(lines):
            continue
        for _ in range(30):
            A = [[(rng.choice(units) if pt in L else 0) for pt in range(n)] for L in lines]
            r = analyse(A, p, kk)
            if r is None:
                continue
            glob_n += 1
            if r[0]:
                nonrigid_n += 1
                hosts.add(idx)
                ok4 &= r[1]
    info4["Z_%d" % q] = {"unit-weighted global failures sampled": glob_n, "keeping a knot": nonrigid_n,
                         "simple substrates hosting one (of 72)": len(hosts)}
    ok4 &= nonrigid_n > 0
check("4 unit-weighted Z8, Z9, Z25 and Z27 laws (30 random weightings on each of the 72 simple substrates of check 3a): global "
      "failures that keep a knot "
      "occur on many substrates, and every removal that keeps a knot leaves a non-cyclic solution group", ok4, info4)

OUT["seconds"] = round(time.time() - T0, 1)
print("ALL OK", OUT["seconds"], "s")
result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"], "proof": manifest["proof"],
          "status": "passed", "claim": manifest["claim"], "checks": {k: v for k, v in OUT.items() if k != "seconds"}}
text = json.dumps(result, indent=1, sort_keys=True, default=str) + "\n"
if "--write" in sys.argv:
    (HERE / "result.json").write_text(text)
elif not (HERE / "result.json").exists() or json.loads((HERE / "result.json").read_text()) != json.loads(text):
    print("result.json does not match a fresh run; rerun with --write after review")
    sys.exit(1)
