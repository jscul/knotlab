#!/usr/bin/env python3
"""Checks for STRIP-RELAY-20261103-001B: pendant rings.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx). Uses up to 22 processes. About ten minutes."""
import collections
import hashlib
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import networkx as nx

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/STRIP-RELAY-20261103-001A/STRIP-RELAY-20261103-001A-P001_heights_and_reduction"))
import strip_lib as SL  # noqa: E402

PL, FL, HP, CL, G = SL.PL, SL.FL, SL.HP, SL.CL, SL.G
T0 = time.time()
OUT = {}
KS = (8, 12, 16, 24, 32)


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        print(json.dumps(info, default=str, indent=1))
        sys.exit(1)


def task_halo(args):
    """the far halo from point z of the ring of length k on the 64-point grid, by where its lines lie"""
    k, z = args
    gg, gp, v1, v2, h = SL.arm_on_grid(2, k)
    (H2, s2, n2), pts, lns = SL.labelled(h)
    org = nx.get_node_attributes(h, "origin")
    hs = SL.halo_space(H2, s2, n2, z, (0, 1, 2))
    gm = nx.Graph()
    gm.add_edges_from((("p", q), ("l", kk)) for kk, L in enumerate(hs.lines) for q in L)
    dist = nx.multi_source_dijkstra_path_length(gm, [("p", q) for q in range(hs.nF)] + [("l", kk) for kk in range(hs.nh)])
    g = CL.Geometry(H2, s2, n2, z)
    around = set().union(*[g.barred(c) for c in range(3)])
    Hands = [hs.handle(M) for M in range(hs.nh)]
    off = []
    for L in range(hs.nh, len(hs.lines)):
        if dist[("l", L)] <= 3:
            continue
        j = hs.qline[L]
        if g.lfaces[j] & around:
            continue
        R = hs.transfer(L)
        if any(HP.creates(hs, M, L, F, Hands[M], R) for M in range(hs.nh) for fname, F in SL.FARS):
            off.append(org[lns[j]])
    cut = org[pts[z]][0] == 1 and org[pts[z]][1] in set(gp[v2])
    return k, z, org[pts[z]], cut, off


def task_prism(args):
    """in the closed prism over a 2k-cycle, attached at point zp (port order as given): the far halo and the far lines of each long face,
    and whether the removed line v2 runs through the point with its far corner on a long face"""
    k, zn, order, v2 = args
    gp = PL.prism(k)
    swap = zn not in SL.labelled(gp)[1]
    (H, s, n), pts, lns = SL.labelled(gp, swap=swap)
    z = pts.index(zn)
    hs = SL.halo_space(H, s, n, z, order)
    gm = nx.Graph()
    gm.add_edges_from((("p", q), ("l", kk)) for kk, L in enumerate(hs.lines) for q in L)
    dist = nx.multi_source_dijkstra_path_length(gm, [("p", q) for q in range(hs.nF)] + [("l", kk) for kk in range(hs.nh)])
    g = CL.Geometry(H, s, n, z)
    Hands = [hs.handle(M) for M in range(hs.nh)]
    fsize = collections.Counter(fi for (kk, fi, p, q) in g.corners)
    halo = set()
    far = {}
    for L in range(hs.nh, len(hs.lines)):
        if dist[("l", L)] <= 3:
            continue
        j = hs.qline[L]
        far[lns[j]] = {fi for fi in g.lfaces[j] if fsize[fi] == k}
        R = hs.transfer(L)
        if any(HP.creates(hs, M, L, F, Hands[M], R) for M in range(hs.nh) for fname, F in SL.FARS):
            halo.add(lns[j])
    opp_long = {g.opp[c] for c in range(3) if fsize[g.opp[c]] == k}
    on_opp = {v for v, fs in far.items() if fs & opp_long}
    c2 = [lns[kk] for kk in g.through].index(v2) if v2 in [lns[kk] for kk in g.through] else None
    removed_far_long = c2 is not None and fsize[g.opp[c2]] == k
    return k, zn, sorted(halo), sorted(on_opp), removed_far_long


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {p: d for p, d in manifest["parent_bindings"].items() if __import__("hashlib").sha256((ROOT / p).read_bytes()).hexdigest() != d}
    status = {p: json.loads((ROOT / p).read_text()).get("status") for p in manifest["parent_bindings"]
              if p.endswith(".json") and p.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})

    # -------------------------------------------------------------------------------------------- 1. the rings
    tasks = [(k, z) for k in KS for z in range(SL.labelled(SL.arm_on_grid(2, k)[4])[0][2])]
    with Pool(22) as pool:
        res = pool.map(task_halo, tasks)
    info1 = {}
    ok1 = True
    hits = {}
    for k in KS:
        rk = [r for r in res if r[0] == k]
        h_ = [(z, orig, cut, off) for (kk, z, orig, cut, off) in rk if off]
        ok1 &= len(h_) == 1 and h_[0][2] and len(h_[0][3]) == k - 3 and all(o[0] == 1 for o in h_[0][3])
        hits[k] = h_[0] if h_ else None
        info1["ring over a %d-cycle" % (2 * k)] = {"points": len(rk), "points creating off the faces around them": len(h_),
                                                   "that point is a cut point": bool(h_ and h_[0][2]),
                                                   "far lines it creates at off those faces": len(h_[0][3]) if h_ else 0, "k - 3": k - 3}
    check("1 the rings: on rings over 16- to 64-cycles spliced onto the 64-point grid, exactly one attachment point creates beyond distance 3 "
          "off the faces around it; it is one of the ring's three cut points, and it creates at k - 3 ring lines", ok1, info1)

    # -------------------------------------------------------------------------------------------- 2. the closed prism from that point
    ptasks = []
    for k in KS:
        z, orig, cut, off = hits[k]
        gg, gp, v1, v2, h = SL.arm_on_grid(2, k)
        (H2, s2, n2), pts, lns = SL.labelled(h)
        org = nx.get_node_attributes(h, "origin")
        swap = orig[1] not in SL.labelled(gp)[1]
        (Hr, sr, nr), rpts, rlns = SL.labelled(gp, swap=swap)
        zr = rpts.index(orig[1])
        rline = {v: j for j, v in enumerate(rlns)}
        through = [kk for kk, L in enumerate(H2) if z in L]
        mates = [rline[org[lns[kk]][1]] if org[lns[kk]][0] == 1 else rline[v2] for kk in through]
        rthrough = [kk for kk, L in enumerate(Hr) if zr in L]
        ptasks.append((k, orig[1], tuple(mates.index(rthrough[j]) for j in range(3)), v2))
    with Pool(len(ptasks)) as pool:
        pres = pool.map(task_prism, ptasks)
    info2 = {}
    ok2 = True
    for (k, zn, halo, on_opp, removed_far_long) in pres:
        z, orig, cut, off = hits[k]
        offn = sorted(o[1] for o in off)
        ok2 &= set(offn) <= set(halo) and set(halo) == set(on_opp) and len(on_opp) == k - 3 and removed_far_long
        info2["prism over a %d-cycle" % (2 * k)] = {"far halo lines from the corresponding point": len(halo),
                                                    "far lines on the opposite long face": len(on_opp),
                                                    "the ring's off-face creating lines inside the prism's halo": set(offn) <= set(halo),
                                                    "the removed line runs through the point with its far corner on the opposite long face": removed_far_long}
    check("2 the closed prism: the creating point is the one whose removed line, in the closed prism, has its far corner on the long face "
          "opposite it; attached there (ports on corresponding lines), the closed prism's far halo is exactly the far lines of that face (k - 3) "
          "and contains the ring's creating lines; so from the cut point the ring shows the ladder's halo", ok2, info2)

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
