#!/usr/bin/env python3
"""Checks for STRIP-RELAY-20261103-001A: heights and reduction.

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
sys.path.insert(0, str(ROOT / "proofs/SPLICE-TREE-20261102-001C/SPLICE-TREE-20261102-001C-P001_opened_cuts_interact"))
import strip_lib as SL  # noqa: E402
import elim_lib as E  # noqa: E402

PL, FL, HP, CL, G, TL, J = SL.PL, SL.FL, SL.HP, SL.CL, SL.G, SL.TL, SL.HP.J
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        print(json.dumps(info, default=str, indent=1))
        sys.exit(1)


def mixed(level, k, choice=0):
    gg, gp, v1, v2, h = SL.arm_on_grid(level, k, choice)
    return ({0: gg, 1: gp}, {0: v1, 1: v2}, h)


FAMILIES = [("ladder", PL.to_space(PL.prism(10)), [0, 1]), ("grid", PL.to_space(FL.octahedral(2)), [0, 5, 17]),
            ("grown 30", PL.to_space(PL.grow(30, 0)), [0, 7, 14, 21]), ("thick tube", PL.to_space(FL.tube(6, 1)), [0, 9, 18])]


def task_heights(args):
    tag, (H, s, n), z = args
    g = CL.Geometry(H, s, n, z)
    Q = g.Q
    out = collections.Counter()
    near = {q for k in g.through for q in H[k]}
    fr = {p: SL.frozen_by_heights(g, p) for p in Q.points if p not in Q.ports and p not in near}
    for p, d in fr.items():
        for w, (frozen, fixed) in d.items():
            out["(point, port pattern) pairs"] += 1
            out["frozen"] += frozen
            out["frozen with a fixed height difference"] += frozen and fixed
            out["frozen with a varying height difference"] += frozen and not fixed
    # consistency with the transfer: a line shows two patterns with two points fixed exactly when two of its points are frozen
    for j in g.beyond:
        img = collections.defaultdict(set)
        for w, t in Q.transfer(j):
            img[w].add(t)
        for w, T in img.items():
            ff = CL.frozen_form(T)
            nfz = sum(1 for q in Q.lines[j] if q in fr and fr[q][w][0])
            out["(line, port pattern) pairs"] += 1
            out["pairs where the transfer's two fixed points are the heights' frozen points"] += (len(T) <= 2) == (nfz >= 2) and \
                (ff is None or all(fr[Q.lines[j][i]][w][0] for i in ff[:2]))
            out["(line, port pattern) pairs with at most two patterns"] += len(T) <= 2
    # the class fixes the ports' heights
    D = TL.shortest(Q.graph(), Q.ports)
    for w in itertools.product((0, 1), repeat=3):
        if g.port_class(w) is None:
            continue
        par = {Q.ports[i]: (w[i] ^ w[0] ^ Q.x0[Q.ports[i]] ^ Q.x0[Q.ports[0]]) for i in range(3)}
        ok, dist = SL._halved(D, Q.ports, par)
        out["port patterns"] += 1
        out["port patterns fixing every port height difference"] += ok and all(dist[a][b] + dist[b][a] == 0 for a in Q.ports for b in Q.ports)
    return tag, out


def task_reduce(args):
    key, z = args
    level, k, choice = key
    pieces = mixed(level, k, choice)
    return key, SL.compare(pieces, z)


def task_faces(args):
    """creating far lines on z's side, against the faces around z in the reduced space, and across the cut against the spliced space"""
    key, z = args
    level, k, choice = key
    origs, removed, h = mixed(level, k, choice)
    (H2, s2, n2), pts, lns = SL.labelled(h)
    org = nx.get_node_attributes(h, "origin")
    side, zn = org[pts[z]]
    swap = zn not in SL.labelled(origs[side])[1]
    (Hr, sr, nr), rpts, rlns = SL.labelled(origs[side], swap=swap)
    gr_ = CL.Geometry(Hr, sr, nr, rpts.index(zn))
    around_r = set().union(*[gr_.barred(c) for c in range(3)])
    gm_ = CL.Geometry(H2, s2, n2, z)
    around_m = set().union(*[gm_.barred(c) for c in range(3)])
    hs = SL.halo_space(H2, s2, n2, z, (0, 1, 2))
    gm = nx.Graph()
    gm.add_edges_from((("p", q), ("l", kk)) for kk, L in enumerate(hs.lines) for q in L)
    dist = nx.multi_source_dijkstra_path_length(gm, [("p", q) for q in range(hs.nF)] + [("l", kk) for kk in range(hs.nh)])
    Hands = [hs.handle(M) for M in range(hs.nh)]
    rl = {v: j for j, v in enumerate(rlns)}
    out = collections.Counter()
    for L in range(hs.nh, len(hs.lines)):
        if dist[("l", L)] <= 3:
            continue
        R = hs.transfer(L)
        if not any(HP.creates(hs, M, L, F, Hands[M], R) for M in range(hs.nh) for fname, F in SL.FARS):
            continue
        j = hs.qline[L]
        s_, node = org[lns[j]]
        on_m = bool(gm_.lfaces[j] & around_m)
        if s_ != side:
            out["across the cut: on the faces around z in the spliced space %s" % on_m] += 1
        else:
            on_r = bool(gr_.lfaces[rl[node]] & around_r)
            out["same side: spliced %s, reduced %s" % ("on" if on_m else "off", "on" if on_r else "off")] += 1
    return key, out


def task_exact(args):
    """exact creation (join method) on z's side of the small junction, in the spliced and in the reduced space"""
    z, M = args
    origs, removed, h = mixed(1, 3, 1)
    (H2, s2, n2), pts, lns = SL.labelled(h)
    org = nx.get_node_attributes(h, "origin")
    side, zn = org[pts[z]]
    swap = zn not in SL.labelled(origs[side])[1]
    (Hr, sr, nr), rpts, rlns = SL.labelled(origs[side], swap=swap)
    zr = rpts.index(zn)
    rline = {v: j for j, v in enumerate(rlns)}
    through = [k for k, L in enumerate(H2) if z in L]
    mates = [rline[org[lns[k]][1]] if org[lns[k]][0] == side else rline[removed[side]] for k in through]
    rthrough = [k for k, L in enumerate(Hr) if zr in L]
    order = [mates.index(rthrough[j]) for j in range(3)]
    hs = SL.halo_space(H2, s2, n2, z, (0, 1, 2))
    hr = SL.halo_space(Hr, sr, nr, zr, order)
    rq = {j: L for L, j in hr.qline.items()}
    AN = CL.solutions(hs.lines, hs.signs, hs.n, skip=M)
    AR = CL.solutions(hr.lines, hr.signs, hr.n, skip=M)
    out = collections.Counter()
    for L in range(hs.nh, len(hs.lines)):
        s_, node = org[lns[hs.qline[L]]]
        if s_ != side:
            continue
        Lr = rq[rline[node]]
        if len({tuple(int(b) for b in r) for r in AN[:, list(hs.lines[L])]}) != 6:
            continue
        for fname, F in SL.FARS:
            a = bool(J.new_knots(E, G, AN, hs.lines, hs.signs, hs.n, L, F, 3)[0])
            b = bool(J.new_knots(E, G, AR, hr.lines, hr.signs, hr.n, Lr, F, 3)[0])
            out["spliced %s, reduced %s" % (a, b)] += 1
    return out


if __name__ == "__main__":
    # -------------------------------------------------------------------------------------------- 0. bindings
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {p: d for p, d in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != d}
    status = {p: json.loads((ROOT / p).read_text()).get("status") for p in manifest["parent_bindings"]
              if p.endswith(".json") and p.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})

    # -------------------------------------------------------------------------------------------- 1. the heights lemma
    MIX = SL.labelled(mixed(2, 16)[2])[0]
    tasks = [(tag, X, z) for tag, X, zs in FAMILIES for z in zs] + [("ladder arm on a grid", MIX, z) for z in (94, 4, 9, 30, 70)]
    with Pool(22) as pool:
        res = pool.map(task_heights, tasks)
    info1 = collections.Counter()
    for tag, out in res:
        info1.update(out)
    ok1 = info1["frozen with a varying height difference"] == 0 and info1["frozen"] > 0 and \
        info1["pairs where the transfer's two fixed points are the heights' frozen points"] == info1["(line, port pattern) pairs"] and \
        info1["port patterns fixing every port height difference"] == info1["port patterns"]
    check("1 the heights lemma: on a ladder, a grid, a grown space, a thick tube and a ladder arm spliced onto a grid, every port pattern fixes "
          "the ports' height differences, every point it freezes has a fixed height difference to the ports, and the transfer's frozen lines "
          "are exactly the lines with two frozen points", ok1, dict(info1))

    # -------------------------------------------------------------------------------------------- 2-3. reduction across a 3-edge cut
    KEYS = [(2, 8, 0), (2, 16, 0), (1, 3, 1), (1, 4, 0), (1, 5, 1), (1, 6, 0)]
    tasks = [(key, z) for key in KEYS for z in range(SL.labelled(mixed(*key)[2])[0][2])]
    with Pool(22) as pool:
        res2 = pool.map(task_reduce, tasks)
        res3 = pool.map(task_faces, tasks)
    info2 = collections.Counter()
    for key, out in res2:
        info2.update(out)
    ok2 = all(v == 0 for k, v in info2.items() if ("True, reduced False" in k or "False, reduced True" in k)) and info2["far: spliced True, reduced True"] > 0
    check("2 reduction: on two rings spliced onto the 64-point grid and four small junction pieces, at every attachment point, creation "
          "(pipeline) at every gluing line on the point's side of the cut, every removal and far side, is the same in the spliced space and in "
          "the side's own closed space with the handle's ports on corresponding lines", ok2, dict(info2))
    info3 = collections.Counter()
    for key, out in res3:
        info3.update(out)
    ok3 = all(v == 0 for k, v in info3.items() if "reduced off" in k) and \
        all(v == 0 for k, v in info3.items() if k.startswith("across") and k.endswith("False")) and info3["same side: spliced off, reduced on"] > 0
    check("3 the reduced-faces law: every creating far line on the point's side lies on a face around the point in the reduced space, "
          "including every line off those faces in the spliced space; creating far lines across the cut lie on faces around the point",
          ok3, dict(info3))

    # -------------------------------------------------------------------------------------------- 4. exact reduction on a small junction
    with Pool(18) as pool:
        res4 = pool.map(task_exact, [(z, M) for z in (1, 3, 4) for M in range(6)])
    info4 = collections.Counter()
    for out in res4:
        info4.update(out)
    ok4 = info4["spliced True, reduced False"] == 0 and info4["spliced False, reduced True"] == 0 and info4["spliced True, reduced True"] > 0
    check("4 exact reduction: on the 21-point junction with the Fano plane at three points, exact creation (join method) at every gluing line "
          "on the point's side agrees between the spliced space and the reduced 16-point grid", ok4, dict(info4))

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
