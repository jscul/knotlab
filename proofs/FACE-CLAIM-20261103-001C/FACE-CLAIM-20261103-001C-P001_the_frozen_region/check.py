#!/usr/bin/env python3
"""Checks for FACE-CLAIM-20261103-001C: the frozen region.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx). Uses up to 22 processes. About fifteen minutes."""
import collections
import hashlib
import itertools
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import networkx as nx
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "proofs/HANDLE-EMERGENCE-20261102-001A/HANDLE-EMERGENCE-20261102-001A-P001_a_planar_removed_side_creates_nothing"))
sys.path.insert(0, str(ROOT / "proofs/SPLICE-TREE-20261102-001C/SPLICE-TREE-20261102-001C-P001_opened_cuts_interact"))
sys.path.insert(0, str(ROOT / "proofs/HALO-FORCING-20261103-001C/HALO-FORCING-20261103-001C-P001_the_reach_on_ladders_and_grids"))
sys.path.insert(0, str(ROOT / "proofs/PHASE-HALO-20261103-001A/PHASE-HALO-20261103-001A-P001_opposite_faces_carry_the_halo"))
import planar_lib as PL  # noqa: E402
import elim_lib as E  # noqa: E402
import halo_pipeline as HP  # noqa: E402
import families_lib as FL  # noqa: E402
import frozen_lib as FZ  # noqa: E402

CL, J, TL = FZ.CL, HP.J, HP.TL
G = PL.G
SP = {idx: (H, s, n) for idx, n, H, s in G.census_spaces(ROOT)}
FARS = [("K4^(3)", SP[1]), ("census 6", SP[6]), ("the Fano plane", SP[21]), ("census 58", SP[58])]
HANDLES = {"the Fano plane": (SP[21], 0), "census 58 minus line 0": (SP[58], 0), "census 58 minus line 6": (SP[58], 6)}
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        print(json.dumps(info, default=str, indent=1))
        sys.exit(1)


def arm_on_grid(level, k, choice=0):
    gg, gp = FL.octahedral(level), PL.prism(k)
    cg, cp = nx.bipartite.color(gg), nx.bipartite.color(gp)
    v1 = [v for v in gg.nodes if cg[v] == 1][choice]
    v2 = next(v for v in gp.nodes if cp[v] != cg[v1])
    return PL.to_space(FL.graph_splice(gg, v1, gp, v2))


MIX = arm_on_grid(2, 16)
SMALL = arm_on_grid(1, 3, 1)
GENERIC = [("ladder", PL.to_space(PL.prism(10)), [0, 1]), ("grid", PL.to_space(FL.octahedral(2)), [0, 5, 17, 40]),
           ("thick tube", PL.to_space(FL.tube(6, 2)), None), ("grown 30", PL.to_space(PL.grow(30, 0)), None),
           ("grown 40", PL.to_space(PL.grow(40, 0)), None)]


def task_frozen(args):
    """per (piece, attachment point): barred faces frozen; unit propagation sound; frozen lines it misses; claim types by face kind"""
    tag, (H, s, n), z = args
    g = CL.Geometry(H, s, n, z)
    around = set().union(*[g.barred(k) for k in range(3)])
    out = collections.Counter()
    det = {k: FZ.propagate(g, k) for k in range(3)}
    for j in g.beyond:
        fr, R, img = FZ.frozen_lines(g, j)
        for w in img:
            k = g.port_class(w)
            on = bool(g.lfaces[j] & g.barred(k))
            frozen = w in fr
            prop = det[k] is not None and len(set(g.Q.lines[j]) & det[k]) >= 2
            if on:
                out["lines on a face barred by the class: frozen %s" % frozen] += 1
            out["unit propagation fixes two points: %s, frozen: %s" % (prop, frozen)] += 1
            if frozen and not prop:
                out["missed at point %d" % z] += 1
            if frozen:
                kind = "opposite face" if g.opp[k] in g.lfaces[j] else ("own arc" if g.lfaces[j] & g.own[k] else
                                                                       ("off the faces around the point" if not (g.lfaces[j] & around) else "another face around the point"))
                ct = FZ.claim_type(img, fr[w])
                out["claim type %s on %s" % (ct, kind)] += 1
                if kind.startswith("off"):
                    out["off-face frozen lines at point %d with claim type %s" % (z, ct)] += 1
    return tag, out


def task_halo(args):
    """per (handle, attachment point of the mixed space): far halo lines off the faces around the point"""
    hname, z = args
    (HF, sF, nF), li = HANDLES[hname]
    H2, s2, n2 = MIX
    hs = HP.HaloSpace(HF, sF, li, H2, s2, n2, z, G)
    gr = nx.Graph()
    gr.add_edges_from((("p", q), ("l", k)) for k, L in enumerate(hs.lines) for q in L)
    dist = nx.multi_source_dijkstra_path_length(gr, [("p", q) for q in range(hs.nF)] + [("l", k) for k in range(hs.nh)])
    g = CL.Geometry(H2, s2, n2, z)
    around = set().union(*[g.barred(k) for k in range(3)])
    Hands = [hs.handle(M) for M in range(hs.nh)]
    off = []
    for L in range(hs.nh, len(hs.lines)):
        if dist[("l", L)] <= 3 or g.lfaces[hs.qline[L]] & around:
            continue
        R = hs.transfer(L)
        if any(HP.creates(hs, M, L, F, Hands[M], R) for M in range(hs.nh) for fname, F in FARS):
            off.append(hs.qline[L])
    return hname, z, off


def task_exact(args):
    """the small arm-on-grid piece with the Fano plane at point z, removal M: exact creation against the pipeline at every line"""
    z, M = args
    H2, s2, n2 = SMALL
    HF, sF, nF = SP[21]
    hs = HP.HaloSpace(HF, sF, 0, H2, s2, n2, z, G)
    gr = nx.Graph()
    gr.add_edges_from((("p", q), ("l", k)) for k, L in enumerate(hs.lines) for q in L)
    dist = nx.multi_source_dijkstra_path_length(gr, [("p", q) for q in range(hs.nF)] + [("l", k) for k in range(hs.nh)])
    g = CL.Geometry(H2, s2, n2, z)
    around = set().union(*[g.barred(k) for k in range(3)])
    AN = CL.solutions(hs.lines, hs.signs, hs.n, skip=M)
    Hand = hs.handle(M)
    out = collections.Counter()
    offs = []
    for L in range(hs.nh, len(hs.lines)):
        if len({tuple(int(b) for b in r) for r in AN[:, list(hs.lines[L])]}) != 6:
            continue
        where = "off the faces around the point" if not (g.lfaces[hs.qline[L]] & around) else "on a face around the point"
        band = "far" if dist[("l", L)] > 3 else "near"
        for fname, F in FARS:
            exact = bool(J.new_knots(E, G, AN, hs.lines, hs.signs, hs.n, L, F, 3)[0])
            pipe = HP.creates(hs, M, L, F, Hand)
            out["%s, %s: exact %s, pipeline %s" % (band, where, exact, pipe)] += 1
            if exact and band == "far" and where.startswith("off"):
                offs.append((z, M, hs.qline[L], fname))
    return out, offs


if __name__ == "__main__":
    # -------------------------------------------------------------------------------------------- 0. bindings
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {p: d for p, d in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != d}
    status = {p: json.loads((ROOT / p).read_text()).get("status") for p in manifest["parent_bindings"]
              if p.endswith(".json") and p.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})

    # -------------------------------------------------------------------------------------------- 1-2. frozen lines, propagation, claims
    tasks = []
    for tag, X, zs in GENERIC:
        for z in (zs if zs is not None else range(0, X[2], max(1, X[2] // 8))):
            tasks.append(("generic: " + tag, X, z))
    for z in range(MIX[2]):
        tasks.append(("ladder arm on a grid", MIX, z))
    with Pool(22) as pool:
        res = pool.map(task_frozen, tasks)
    info = collections.defaultdict(collections.Counter)
    for tag, out in res:
        info[tag.split(":")[0]].update(out)
    gen, mix = info["generic"], info["ladder arm on a grid"]
    ok1 = all(v == 0 for k, v in list(gen.items()) + list(mix.items()) if k == "lines on a face barred by the class: frozen False") and \
        gen["unit propagation fixes two points: True, frozen: False"] == 0 and mix["unit propagation fixes two points: True, frozen: False"] == 0 and \
        gen["unit propagation fixes two points: False, frozen: True"] == 0 and mix["unit propagation fixes two points: False, frozen: True"] > 0
    missed = sorted(int(k.split()[-1]) for k in mix if k.startswith("missed at point"))
    check("1 frozen lines: on ladders, a grid, a thick tube, two grown spaces and every point of a ladder arm spliced onto a grid, every "
          "line beyond distance 3 with a corner on a face barred by the class is frozen; unit propagation from the class's seeds never fixes "
          "two points of an unfrozen line, finds every frozen line on the generic pieces, and misses frozen lines on the arm-on-grid piece "
          "at the points listed", ok1,
          {"generic pieces": {k: v for k, v in gen.items() if not k.startswith(("claim", "off", "missed"))},
           "arm on grid": {k: v for k, v in mix.items() if not k.startswith(("claim", "off", "missed"))},
           "arm on grid: points where propagation misses frozen lines": missed})
    ok2 = all(("(1, 1)" in k) if "own arc" in k else True for k in gen if k.startswith("claim type")) and \
        all(("(2, 2)" in k) if "opposite face" in k else True for k in gen if k.startswith("claim type")) and \
        not any("off the faces" in k for k in gen if k.startswith("claim type"))
    offtypes = {k: v for k, v in mix.items() if k.startswith("off-face frozen lines")}
    check("2 claim types: on the generic pieces every frozen own-arc line claims from one port pattern per value and every frozen opposite-"
          "face line from two, and no frozen line lies off the faces around the point; on the arm-on-grid piece the frozen lines off those "
          "faces are rigid (no claim) except at one point, where they claim from two port patterns per value",
          ok2 and any("(2, 2)" in k for k in offtypes),
          {"generic": {k: v for k, v in gen.items() if k.startswith("claim")}, "arm on grid": {k: v for k, v in mix.items() if k.startswith("claim")},
           "arm on grid, off the faces around the point, by point and claim type": offtypes})

    # -------------------------------------------------------------------------------------------- 3. creation off the faces around the point
    with Pool(22) as pool:
        res3 = pool.map(task_halo, [(h, z) for h in HANDLES for z in range(MIX[2])])
    info3 = collections.Counter()
    where = collections.defaultdict(list)
    for h, z, off in res3:
        info3[h + ": attachment points"] += 1
        if off:
            info3[h + ": points with far creation off the faces around the point"] += 1
            where[h].append((z, off))
    pts = {h: [z for z, off in v] for h, v in where.items()}
    two2 = sorted(int(k.split()[5]) for k in offtypes if "(2, 2)" in k)
    ok3 = all(pts.get(h) == two2 for h in HANDLES) and len(two2) == 1
    check("3 creation off the faces around the point: on the arm-on-grid piece (95 points), each of the three handles creates beyond distance "
          "3 off the faces around the attachment point at exactly one point, the one whose off-face frozen lines claim from two port "
          "patterns per value; there the halo runs along the arm's far long face", ok3,
          dict(info3, **{"points and lines": {h: v for h, v in where.items()}}))

    # -------------------------------------------------------------------------------------------- 4. exact creation on a small junction
    with Pool(18) as pool:
        res4 = pool.map(task_exact, [(z, M) for z in (1, 3, 4) for M in range(6)])
    info4 = collections.Counter()
    offs = []
    for out, o in res4:
        info4.update(out)
        offs += o
    ok4 = all(v == 0 for k, v in info4.items() if ("exact True, pipeline False" in k or "exact False, pipeline True" in k)) and len(offs) > 0
    check("4 exact creation on a small junction: on a 21-point ladder arm spliced onto a 16-point grid, with the Fano plane attached at three "
          "points, exact creation agrees with the pipeline at every removal, gluing line and far side, and creates beyond distance 3 off "
          "the faces around the attachment point", ok4, dict(info4, **{"exact far creation off the faces around the point": sorted(set(offs))[:20],
                                                                       "count": len(offs)}))

    OUT["seconds"] = round(time.time() - T0, 1)
    print("ALL OK", OUT["seconds"], "s")
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "status": "passed", "claim": manifest["claim"],
              "checks": {k: v for k, v in OUT.items() if k != "seconds"}}
    text = json.dumps(result, indent=1, sort_keys=True, default=str) + "\n"
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(text)
    elif not (HERE / "result.json").exists() or json.loads((HERE / "result.json").read_text()) != json.loads(text):
        print("result.json does not match a fresh run; rerun with --write after review")
        sys.exit(1)
