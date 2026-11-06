#!/usr/bin/env python3
"""Checks for HALO-FORCING-20261103-001C: the reach on ladders and grids.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx)."""
import collections
import hashlib
import json
import sys
import time
from pathlib import Path

import networkx as nx
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "proofs/HANDLE-EMERGENCE-20261102-001A/HANDLE-EMERGENCE-20261102-001A-P001_a_planar_removed_side_creates_nothing"))
sys.path.insert(0, str(ROOT / "proofs/SPLICE-TREE-20261102-001C/SPLICE-TREE-20261102-001C-P001_opened_cuts_interact"))
import planar_lib as PL  # noqa: E402
import elim_lib as E  # noqa: E402
import halo_pipeline as HP  # noqa: E402

J, TL = HP.J, HP.TL
G = PL.G
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)
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

SP = {idx: (H, s, n) for idx, n, H, s in G.census_spaces(ROOT)}
FARS = [("K4^(3)", SP[1]), ("census 6", SP[6]), ("the Fano plane", SP[21]), ("census 58", SP[58])]
HF, sF, nF = SP[21]


def octahedral(level):
    """the dual of the octahedron subdivided level times (each triangle into four): plane, cubic and bipartite"""
    verts = {(1, 0, 0): 0, (-1, 0, 0): 1, (0, 1, 0): 2, (0, -1, 0): 3, (0, 0, 1): 4, (0, 0, -1): 5}
    tris = [(a, b, c) for a in (0, 1) for b in (2, 3) for c in (4, 5)]
    coords = {v: k for k, v in verts.items()}
    for _ in range(level):
        mid = {}

        def m(u, v):
            key = (min(u, v), max(u, v))
            if key not in mid:
                mid[key] = len(coords)
                coords[mid[key]] = tuple((a + b) for a, b in zip(coords[u], coords[v]))
            return mid[key]
        new = []
        for (a, b, c) in tris:
            ab, bc, ca = m(a, b), m(b, c), m(c, a)
            new += [(a, ab, ca), (ab, b, bc), (ca, bc, c), (ab, bc, ca)]
        tris = new
    edge_tris = collections.defaultdict(list)
    for i, t in enumerate(tris):
        for u, v in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
            edge_tris[(min(u, v), max(u, v))].append(i)
    g = nx.Graph()
    for e, ts in edge_tris.items():
        g.add_edge(*ts)
    return g


def halo_map(H2, s2, n2, z):
    """creating plane gluing lines for every removal inside the handle and far side; distances from the handle"""
    hs = HP.HaloSpace(HF, sF, 0, H2, s2, n2, z, G)
    g = nx.Graph()
    g.add_edges_from((("p", q), ("l", k)) for k, L in enumerate(hs.lines) for q in L)
    dist = nx.multi_source_dijkstra_path_length(g, [("p", q) for q in range(nF)] + [("l", k) for k in range(hs.nh)])
    R = {L: hs.transfer(L) for L in range(hs.nh, len(hs.lines))}
    halo = collections.defaultdict(set)
    for M in range(hs.nh):
        Hand = hs.handle(M)
        for L in R:
            for fname, F in FARS:
                if HP.creates(hs, M, L, F, Hand, R[L]):
                    halo[fname].add(L)
    d = {L: dist[("l", L)] for L in R}
    return hs, R, halo, d


# ------------------------------------------------------------------------------------------------ 1. the pipeline equals exact creation
info1 = collections.Counter()
ok1 = True
for size, seed in ((10, 0), (10, 1), (12, 0), (12, 1), (14, 0)):
    H2, s2, n2 = PL.to_space(PL.grow(size, seed))
    for z in (0, 3):
        ls, ss, n, side, ports = G.splice(HF, sF, nF, 0, H2, s2, n2, z)
        hs = HP.HaloSpace(HF, sF, 0, H2, s2, n2, z, G)
        same = [tuple(x) for x in ls] == [tuple(x) for x in hs.lines] and [list(x) for x in ss] == [list(x) for x in hs.signs]
        ok1 &= same
        info1["spaces whose fast splice equals glue_lib.splice"] += same
        for M in range(hs.nh):
            AN = np.array(G.removal(hs.lines, hs.signs, hs.n, M), dtype=np.int8)
            Hand = hs.handle(M)
            for L in range(hs.nh, len(hs.lines)):
                X = list(hs.lines[L])
                if len({tuple(int(b) for b in r) for r in AN[:, X]}) != 6:
                    continue
                for fname, F in FARS:
                    exact = bool(J.new_knots(E, G, AN, hs.lines, hs.signs, hs.n, L, F, 3)[0])
                    pred = HP.creates(hs, M, L, F, Hand)
                    ok1 &= pred == exact
                    info1["cases (removal, gluing line, far side)"] += 1
                    info1["cases where the pipeline equals exact creation: %s" % ("creates" if exact else "no new knot")] += pred == exact
check("1 the pipeline: on the Fano plane spliced into two points of each of five grown plane spaces (10 to 14 points), the splice built "
      "with the twist chosen by theory equals glue_lib.splice, and creation decided by the route criterion over handle pairs, with every "
      "transfer computed by heights, equals exact creation (new crossing knots up to three points, join method) in every case",
      ok1 and info1["cases (removal, gluing line, far side)"] > 0, dict(info1))

# ------------------------------------------------------------------------------------------------ 2. ladders
info2 = collections.Counter()
ok2 = True
for k in (5, 8, 12, 16, 20, 25, 30, 40):
    H2, s2, n2 = PL.to_space(PL.prism(k))
    hs, R, halo, d = halo_map(H2, s2, n2, 0)
    allh = set().union(*halo.values())
    dmax = max(d.values())
    reach = max(d[L] for L in allh)
    per_d = collections.Counter(d.values())
    byd = collections.Counter(d[L] for L in allh)
    two_of_four = all(byd[x] == 2 for x in per_d if per_d[x] == 4)
    cut_only = all(d[L] == 1 for f in ("the Fano plane", "census 58") for L in halo[f])
    ok2 &= reach == dmax and two_of_four and cut_only
    info2["ladder of %d points: reach %d of maximal distance %d; creating lines %d of %d" % (n2, reach, dmax, len(allh), len(R))] += 1
check("2 ladders: with the Fano plane attached at a point of the prism over a 2k-cycle (k = 5 to 40, up to 80 points) and the removal "
      "inside it, the halo reaches the farthest gluing line of the ladder; at every distance with four gluing lines exactly two create; "
      "the far sides the Fano plane and census 58 create only at the three lines through the cut", ok2, dict(info2))

# ------------------------------------------------------------------------------------------------ 3-4. grids and the forcing profile
info3, info4 = collections.Counter(), collections.Counter()
ok3 = ok4 = True
for level, zs in ((1, (0,)), (2, (0, 5, 17, 40)), (3, (0,))):
    H2, s2, n2 = PL.to_space(octahedral(level))
    for z in zs:
        hs, R, halo, d = halo_map(H2, s2, n2, z)
        allh = set().union(*halo.values())
        reach = max(d[L] for L in allh)
        ok3 &= reach == 3
        info3["grid of %d points, attached at %d: reach %d of maximal distance %d; creating lines %d of %d" % (
            n2, z, reach, max(d.values()), len(allh), len(R))] += 1
        if level >= 2 and z == 0:
            for L, Rl in R.items():
                full = len(Rl) == 36
                if d[L] >= 7:
                    ok4 &= full
                info4["grid of %d points: gluing lines at distance %s with %s" % (
                    n2, d[L] if d[L] < 7 else ">= 7", "the full transfer (independent of the split point)" if full else "a restricted transfer")] += 1
check("3 grids: with the Fano plane attached at a point of the duals of the octahedron subdivided once, twice and three times (16, 64 and "
      "256 points; four attachment points on the 64-point grid) and the removal inside it, the halo reaches exactly distance 3",
      ok3, dict(info3))
H2, s2, n2 = PL.to_space(PL.prism(20))
Q = TL.Split(H2, [list(x) for x in s2], n2, 0)
g = nx.Graph()
g.add_edges_from((("p", q), ("l", k)) for k, L in enumerate(Q.lines) for q in L)
dq = nx.multi_source_dijkstra_path_length(g, [("p", y) for y in Q.ports])
for L in range(len(Q.lines)):
    per_w = collections.defaultdict(set)
    for w, t in Q.transfer(L):
        per_w[w].add(t)
    mn = min(len(v) for v in per_w.values())
    if dq[("l", L)] >= 3:
        ok4 &= mn == 2
    info4["ladder of 40 points: gluing lines whose patterns, with the split point's copies fixed, are at least %d" % mn] += 1
check("4 the forcing profile: on the 40-point ladder, fixing the split point's three copies leaves every gluing line at distance 3 or more "
      "with exactly two patterns (an edge), however far; on the 64- and 256-point grids, every gluing line at distance 7 or more has the "
      "full transfer (all 36 pairs), so it is independent of the split point", ok4, dict(info4))

# ------------------------------------------------------------------------------------------------ 5. random grown spaces (record)
info5 = {}
for size in (20, 30, 40):
    H2, s2, n2 = PL.to_space(PL.grow(size, 0))
    hs, R, halo, d = halo_map(H2, s2, n2, 0)
    allh = set().union(*halo.values())
    info5["grown %d points: reach" % size] = max(d[L] for L in allh)
    info5["grown %d points: maximal distance" % size] = max(d.values())
check("5 random grown plane spaces (20, 30 and 40 points; recorded): reaches between the ladder and the grid", True, info5)

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
