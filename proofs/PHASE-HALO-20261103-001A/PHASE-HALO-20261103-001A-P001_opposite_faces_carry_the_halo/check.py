#!/usr/bin/env python3
"""Checks for PHASE-HALO-20261103-001A: opposite faces carry the halo.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx). About ten minutes."""
import collections
import hashlib
import itertools
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
sys.path.insert(0, str(ROOT / "proofs/HALO-FORCING-20261103-001C/HALO-FORCING-20261103-001C-P001_the_reach_on_ladders_and_grids"))
import planar_lib as PL  # noqa: E402
import elim_lib as E  # noqa: E402
import halo_pipeline as HP  # noqa: E402
import families_lib as FL  # noqa: E402

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

# ------------------------------------------------------------------------------------------------ 1. the claiming lemma
info1 = collections.Counter()
ok1 = True
SMALL = [("census %d" % i,) + SP[i] for i in sorted(SP) if PL.incidence_planar(SP[i][0])]
for seed in (0, 1):
    SMALL.append(("grown 10 points, seed %d" % seed,) + PL.to_space(PL.grow(10, seed)))
for name, H, s, n in SMALL:
    for z in range(n):
        Q = TL.Split(H, [list(x) for x in s], n, z)
        pts = sorted(set(range(n + 3)) - {z})
        idx = {p: i for i, p in enumerate(pts)}
        A = G.states(len(pts))[G.sat_matrix([tuple(idx[q] for q in L) for L in Q.lines], [list(x) for x in s], len(pts)).all(axis=1)]
        through = [k for k, L in enumerate(Q.lines) if any(y in L for y in Q.ports)]
        for k in through:
            L = list(Q.lines[k])
            y = next(q for q in L if q in Q.ports)
            a, b = [q for q in L if q != y]
            opp = next(f for (kk, f, p, q) in Q.edges if kk == k and {p, q} == {a, b})
            others = [(kk, p, q) for (kk, f, p, q) in Q.edges if f == opp and kk != k]
            sg = dict(zip(L, s[k]))
            for r in A:
                v = {q: int(r[idx[q]]) ^ sg[q] for q in L}
                y_odd = v[y] != v[a] and v[y] != v[b]
                # the other lines of the opposite face that skip into it (their corner in it joins two agreeing points)
                skips = 0
                for (kk, p, q) in others:
                    sgk = dict(zip(Q.lines[kk], s[kk]))
                    skips += (int(r[idx[p]]) ^ sgk[p]) == (int(r[idx[q]]) ^ sgk[q])
                good = (skips == 0) if y_odd else (skips == 1)
                ok1 &= good
                info1["(split, port line, solution) triples"] += 1
                info1["triples obeying the claim (odd port: no other line skips into the opposite face; else exactly one)"] += good
check("1 the claiming lemma: on every point split of the planar census and two 10-point grown spaces, in every solution, a port is the odd "
      "point of its line exactly when no other line of the face opposite the port (across its line) skips into that face, and otherwise "
      "exactly one other line does", ok1 and info1["(split, port line, solution) triples"] > 0, dict(info1))


# ------------------------------------------------------------------------------------------------ 2-3. the opposite-face law
def opposite_law(HF, sF, H2, s2, n2, zs, tag, info, opposite_only=True):
    """for each attachment point z: the halo beyond distance 3, against the lines of the faces opposite z (faces holding a corner of a
    line through z but not z itself)"""
    nFh = len({q for L in HF for q in L})
    faces, corners = TL.faces_with_corners(H2)
    size = collections.Counter(fi for (k, fi, p, q) in corners)
    fpts = {fi: {v[1] for v in faces[fi] if v[0] == "p"} for fi in size}
    flines = {fi: {k for (k, f, p, q) in corners if f == fi} for fi in size}
    ok = True
    for z in zs:
        hs = HP.HaloSpace(HF, sF, 0, H2, s2, n2, z, G)
        g = nx.Graph()
        g.add_edges_from((("p", q), ("l", k)) for k, L in enumerate(hs.lines) for q in L)
        dist = nx.multi_source_dijkstra_path_length(g, [("p", q) for q in range(nFh)] + [("l", k) for k in range(hs.nh)])
        R = {L: hs.transfer(L) for L in range(hs.nh, len(hs.lines))}
        halo = set()
        for M in range(hs.nh):
            Hand = hs.handle(M)
            for L in R:
                for fname, F in FARS:
                    if L not in halo and HP.creates(hs, M, L, F, Hand, R[L]):
                        halo.add(L)
        through = [k for k, Lp in enumerate(H2) if z in Lp]
        far = {L for L in R if dist[("l", L)] > 3}
        actual = {hs.qline[L] for L in halo & far}
        opp = {fi for fi in size if z not in fpts[fi] and any(k in flines[fi] for k in through)}
        own = {fi for fi in size if z in fpts[fi]}
        farlines = {hs.qline[L] for L in far}
        pred = (set().union(*[flines[fi] for fi in opp]) if opp else set()) & farlines
        pred2 = set().union(*[flines[fi] for fi in opp | own]) & farlines
        contained = actual <= pred
        ok &= contained if opposite_only else actual <= pred2
        info["%s: attachment points" % tag] += 1
        info["%s: far halo inside the opposite faces' lines" % tag] += contained
        info["%s: far halo inside the lines of the point's own and opposite faces" % tag] += actual <= pred2
        info["%s: far halo equal to the opposite faces' far lines" % tag] += actual == pred
        info["%s: largest opposite face %s corners" % (tag, ">= 4" if max(size[f] for f in opp) >= 4 else "<= 3")] += 1
        if actual:
            info["%s: attachment points with a far halo" % tag] += 1
    return ok


HF, sF, nF = SP[21]
info2 = collections.Counter()
ok2 = True
FAMILIES = [("ladders", [PL.to_space(PL.prism(k)) for k in (6, 10, 15)], lambda n: [0, 1]),
            ("thick tubes", [PL.to_space(FL.tube(k, l)) for (k, l) in ((6, 1), (8, 1), (6, 2))], lambda n: range(0, n, max(1, n // 10))),
            ("grids", [PL.to_space(FL.octahedral(2))], lambda n: [0, 5, 17, 40]),
            ("random grown spaces", [PL.to_space(PL.grow(m, s)) for (m, s) in ((20, 0), (20, 1), (30, 0), (30, 1), (40, 0))],
             lambda n: range(0, n, max(1, n // 10)))]
gg, gp = FL.octahedral(2), PL.prism(16)
cg, cp = nx.bipartite.color(gg), nx.bipartite.color(gp)
v1 = next(v for v in gg.nodes if cg[v] == 1)
v2 = next(v for v in gp.nodes if cp[v] != cg[v1])
MIXED = PL.to_space(FL.graph_splice(gg, v1, gp, v2))
FAMILIES.append(("a ladder arm spliced onto a grid", [MIXED], lambda n: range(0, n, 3)))
for tag, spaces, zsf in FAMILIES:
    for (H2, s2, n2) in spaces:
        ok2 &= opposite_law(HF, sF, H2, s2, n2, zsf(n2), tag, info2)
check("2 the opposite-face law (Fano plane as handle): on ladders, thick tubes, a grid, random grown spaces and a ladder arm spliced onto a "
      "grid, at every attachment point tested, every halo line beyond distance 3 lies on a face opposite the attachment point (a face holding "
      "a corner of a line through the point but not the point itself)", ok2, dict(info2))

# ------------------------------------------------------------------------------------------------ 3. census 58 as handle
H58, s58, n58 = SP[58]
info3 = collections.Counter()
ok3 = True
for seed in (0, 1):
    H2, s2, n2 = PL.to_space(PL.grow(10, seed))
    for z in (0, 3):
        hs = HP.HaloSpace(H58, s58, 0, H2, s2, n2, z, G)
        ls, ss, n, side, ports = G.splice(H58, s58, n58, 0, H2, s2, n2, z)
        ok3 &= [tuple(x) for x in ls] == [tuple(x) for x in hs.lines] and [list(x) for x in ss] == [list(x) for x in hs.signs]
        for M in range(hs.nh):
            AN = np.array(G.removal(hs.lines, hs.signs, hs.n, M), dtype=np.int8)
            Hand = hs.handle(M)
            for L in range(hs.nh, len(hs.lines)):
                if len({tuple(int(b) for b in r) for r in AN[:, list(hs.lines[L])]}) != 6:
                    continue
                for fname, F in FARS:
                    exact = bool(J.new_knots(E, G, AN, hs.lines, hs.signs, hs.n, L, F, 3)[0])
                    pred = HP.creates(hs, M, L, F, Hand)
                    ok3 &= pred == exact
                    info3["census 58 handle: cases"] += 1
                    info3["census 58 handle: pipeline cases equal to exact creation (%s)" % ("creates" if exact else "none")] += pred == exact
for tag, spaces, zsf in FAMILIES[:1] + [("grids", [PL.to_space(FL.octahedral(2))], lambda n: [0, 5]),
                                         ("a ladder arm spliced onto a grid", [MIXED], lambda n: range(0, n, 6))]:
    for (H2, s2, n2) in spaces:
        ok3 &= opposite_law(H58, s58, H2, s2, n2, zsf(n2), "census 58 handle, " + tag, info3, opposite_only=False)
check("3 census 58 as handle: the pipeline equals exact creation in every case on two 10-point grown spaces at two attachment points each; "
      "on ladders, the grid and the mixed space, the halo beyond distance 3 lies on the faces around the attachment point (its own three "
      "faces and the three opposite it); on the ladder arm of the mixed space it uses the point's own big face as well as the opposite one",
      ok3 and info3["census 58 handle: cases"] == sum(v for k, v in info3.items() if k.startswith("census 58 handle: pipeline cases equal")),
      dict(info3))

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
