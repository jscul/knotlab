#!/usr/bin/env python3
"""Checks for FACE-CLAIM-20261103-001A: the reading lemma and the claim rule.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx). Uses up to 22 processes. About ten minutes."""
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
import claim_lib as CL  # noqa: E402

J, TL = HP.J, HP.TL
G = PL.G
SP = {idx: (H, s, n) for idx, n, H, s in G.census_spaces(ROOT)}
FARS = [("K4^(3)", SP[1]), ("census 6", SP[6]), ("the Fano plane", SP[21]), ("census 58", SP[58])]
HANDLES = [("the Fano plane", SP[21], 0), ("census 58 minus line 0", SP[58], 0), ("census 58 minus line 6", SP[58], 6)]
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        print(json.dumps(info, default=str, indent=1))
        sys.exit(1)


def mixed_space():
    gg, gp = FL.octahedral(2), PL.prism(16)
    cg, cp = nx.bipartite.color(gg), nx.bipartite.color(gp)
    v1 = next(v for v in gg.nodes if cg[v] == 1)
    v2 = next(v for v in gp.nodes if cp[v] != cg[v1])
    return PL.to_space(FL.graph_splice(gg, v1, gp, v2))


def task4(args):
    """per (piece, handle, attachment point): the claim rule against the pipeline at every gluing line"""
    tag, hname, (HF, sF, nF), li, (H2, s2, n2), z = args
    hs = HP.HaloSpace(HF, sF, li, H2, s2, n2, z, G)
    g = nx.Graph()
    g.add_edges_from((("p", q), ("l", k)) for k, L in enumerate(hs.lines) for q in L)
    dist = nx.multi_source_dijkstra_path_length(g, [("p", q) for q in range(hs.nF)] + [("l", k) for k in range(hs.nh)])
    Hands = [hs.handle(M) for M in range(hs.nh)]
    out = collections.Counter()
    for L in range(hs.nh, len(hs.lines)):
        R = hs.transfer(L)
        pipe = any(HP.creates(hs, M, L, F, Hands[M], R) for M in range(hs.nh) for fname, F in FARS)
        rules = [CL.claim_rule_at(hs, L, R, Hands[M]) for M in range(hs.nh)]
        rule = True if True in rules else ("other" if "other" in rules else False)
        band = "far" if dist[("l", L)] > 3 else "near"
        if rule == "other":
            out["%s: rule other, pipeline %s" % (band, pipe)] += 1
        elif rule == pipe:
            out["%s: rule %s, pipeline %s" % (band, rule, pipe)] += 1
        else:
            out["%s: disagree (rule %s, pipeline %s)" % (band, rule, pipe)] += 1
    return out


def split_solutions(g):
    """solutions of the split as {point label: value} columns, with each line's skipped corner (index into Q.edges)"""
    Q = g.Q
    pts = Q.points
    idx = {p: i for i, p in enumerate(pts)}
    A = CL.solutions([tuple(idx[q] for q in L) for L in Q.lines], [list(x) for x in g.s], len(pts))
    skip = np.zeros((len(A), len(Q.lines)), dtype=np.int64)
    for k, L in enumerate(Q.lines):
        sg = dict(zip(L, g.s[k]))
        v = {q: A[:, idx[q]] ^ sg[q] for q in L}
        for ci, (kk, f, p, q) in enumerate(Q.edges):
            if kk == k:
                skip[v[p] == v[q], k] = ci
    return A, idx, skip


if __name__ == "__main__":
    # -------------------------------------------------------------------------------------------- 0. bindings
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {p: d for p, d in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != d}
    status = {p: json.loads((ROOT / p).read_text()).get("status") for p in manifest["parent_bindings"]
              if p.endswith(".json") and p.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})

    # -------------------------------------------------------------------------------------------- 1-2. reading and claim lemmas
    SMALL = [("census %d" % i,) + SP[i] for i in sorted(SP) if PL.incidence_planar(SP[i][0])]
    for seed in (0, 1):
        SMALL.append(("grown 10 points, seed %d" % seed,) + PL.to_space(PL.grow(10, seed)))
    SMALL.append(("ladder, prism over a 10-cycle",) + PL.to_space(PL.prism(5)))
    info1, info2 = collections.Counter(), collections.Counter()
    ok1 = ok2 = True
    for name, H, s, n in SMALL:
        for z in range(n):
            g = CL.Geometry(H, s, n, z)
            Q = g.Q
            A, idx, skip = split_solutions(g)
            ofi = [fi for (k, fi, p, q) in g.corners]                     # original face of each corner of the split
            assert [e[0] for e in Q.edges] == [c[0] for c in g.corners]
            W = [tuple(int(v) for v in r) for r in A[:, [idx[y] for y in Q.ports]]]
            pl = {i: g.through[i] for i in range(3)}
            for r in range(len(A)):
                info1["(split, solution) pairs"] += 1
                k = g.port_class(W[r])
                good = k is not None
                # every face receives exactly one skip
                rec = collections.Counter(Q.edges[skip[r, kk]][1] for kk in range(len(Q.lines)))
                good &= all(v == 1 for v in rec.values()) and len(rec) == len(Q.facelist)
                if k is not None:
                    f0 = [skip[r, kk] for kk in range(len(Q.lines)) if Q.edges[skip[r, kk]][1] == "F0"]
                    good &= len(f0) == 1 and g.arc[ofi[f0[0]]] == tuple(sorted({0, 1, 2} - {k}))
                    # port k's line takes its far corner (the one without its port)
                    p2, q2 = Q.edges[skip[r, pl[k]]][2:]
                    good &= Q.ports[k] not in (p2, q2)
                    # the arc identity
                    for (i, j), fi in g.face_of_arc.items():
                        nsk = sum(1 for kk in range(len(Q.lines)) if ofi[skip[r, kk]] == fi and Q.edges[skip[r, kk]][1] == "F0")
                        good &= (W[r][i] ^ W[r][j]) == (g.kappa[(i, j)] ^ (nsk % 2))
                ok1 &= good
                info1["pairs obeying the lemma (one skip per face, the merged face's skip on the arc opposite the odd port, that port's "
                      "line on its far corner, the arc identity)"] += good
            # barred faces are frozen: for each port pattern of class k, every line other than port k's line with a corner on a face
            # barred by k has the two points of that corner fixed
            byw = collections.defaultdict(list)
            for r in range(len(A)):
                byw[W[r]].append(r)
            for w, rs in byw.items():
                k = g.port_class(w)
                for ci, (kk, f, p, q) in enumerate(Q.edges):
                    if kk == pl[k] or ofi[ci] not in g.barred(k):
                        continue
                    vals = {(int(A[r, idx[p]]), int(A[r, idx[q]])) for r in rs}
                    info1["(port pattern, corner on a barred face) pairs"] += 1
                    info1["pairs whose two corner points are fixed by the port pattern"] += len(vals) == 1
                    ok1 &= len(vals) == 1
            # the claim lemma
            for ci, (kk, f, p, q) in enumerate(Q.edges):
                if kk in g.through:
                    continue
                fi = ofi[ci]
                rs = [r for r in range(len(A)) if skip[r, kk] == ci]
                if not rs:
                    continue
                byval = collections.defaultdict(set)
                for r in rs:
                    byval[(int(A[r, idx[p]]), int(A[r, idx[q]]))].add(W[r])
                if fi in g.arc:                                            # a corner on an own arc A(i, j): the claim needs class k
                    kk3 = ({0, 1, 2} - set(g.arc[fi])).pop()
                    good = all(g.port_class(W[r]) == kk3 for r in rs) and all(len(v) == 1 for v in byval.values())
                    info2["own-arc corners claimed in some solution"] += 1
                    info2["own-arc corners whose claim needs the third port's class and one port pattern per value"] += good
                    ok2 &= good
                for k in range(3):
                    if fi == g.opp[k] and fi not in g.arc:                   # a corner on the face opposite port k
                        i, j = sorted({0, 1, 2} - {k})
                        good = all(g.port_class(W[r]) != k for r in rs)
                        for v in byval.values():
                            good &= len(v) <= 2
                            if len(v) == 2:
                                a, b = sorted(v)
                                good &= (a[i], a[j]) == (b[i], b[j]) and a[k] != b[k]
                        info2["opposite-face corners claimed in some solution"] += 1
                        info2["opposite-face corners whose claim avoids the class of the port and comes from at most two port patterns per "
                              "value, sharing the other two ports"] += good
                        info2["opposite-face corners with a value claimed from two port patterns"] += any(len(v) == 2 for v in byval.values())
                        ok2 &= good
    check("1 the reading lemma: in every solution of every point split of the planar census, two 10-point grown spaces and a ladder, every "
          "face receives one skip, the port pattern is never the all-agree pattern given by the arc constants or its complement, the merged "
          "face's skip lies on the arc opposite the odd port, that port's line takes its far corner, and the arc identity holds; for each "
          "port pattern, every line other than the odd port's own line has the two points of its corner on a barred face fixed",
          ok1 and info1["(split, solution) pairs"] > 0, dict(info1))
    check("2 the claim lemma: a line claims an own arc only in the class of the third port, from one port pattern per claimed value; it "
          "claims the face opposite a port only outside that port's class, from at most two port patterns per value, which then agree on "
          "the other two ports and differ at that port", ok2 and info2["opposite-face corners with a value claimed from two port patterns"] > 0,
          dict(info2))

    # -------------------------------------------------------------------------------------------- 3. the claim rule against exact creation
    info3 = collections.Counter()
    ok3 = True
    for seed in (0, 1):
        H2, s2, n2 = PL.to_space(PL.grow(10, seed))
        for hname, (HF, sF, nF), li in HANDLES:
            for z in (0, 3):
                hs = HP.HaloSpace(HF, sF, li, H2, s2, n2, z, G)
                for M in range(hs.nh):
                    AN = np.array(G.removal(hs.lines, hs.signs, hs.n, M), dtype=np.int8)
                    Hand = hs.handle(M)
                    for L in range(hs.nh, len(hs.lines)):
                        if len({tuple(int(b) for b in r) for r in AN[:, list(hs.lines[L])]}) != 6:
                            continue
                        exact = any(bool(J.new_knots(E, G, AN, hs.lines, hs.signs, hs.n, L, F, 3)[0]) for fname, F in FARS)
                        rule = CL.claim_rule_at(hs, L, hs.transfer(L), Hand)
                        info3["(handle, attachment point, removal, gluing line) cases"] += 1
                        info3["cases: rule %s, exact creation %s" % (rule, exact)] += 1
                        if rule in (True, False):
                            ok3 &= rule == exact
    check("3 the claim rule against exact creation: on two 10-point grown spaces with the Fano plane and census 58 (two removed lines) "
          "attached at two points, at every removal and gluing line, the rule agrees with exact creation (some far side) whenever it "
          "applies; where a pair squeezes the line in another form, the cases are listed", ok3 and info3["cases: rule True, exact creation True"] > 0,
          dict(info3))

    # -------------------------------------------------------------------------------------------- 4. the claim rule against the pipeline
    MIX = mixed_space()
    PIECES = [("tube 6,1", PL.to_space(FL.tube(6, 1)), 4), ("tube 8,1", PL.to_space(FL.tube(8, 1)), 4),
              ("grid 64", PL.to_space(FL.octahedral(2)), 4), ("grown 30/0", PL.to_space(PL.grow(30, 0)), 5),
              ("grown 40/0", PL.to_space(PL.grow(40, 0)), 5), ("mixed 95", MIX, MIX[2])]
    tasks = []
    for hname, (HF, sF, nF), li in HANDLES:
        for tag, (H2, s2, n2), k in PIECES:
            for z in range(0, n2, max(1, n2 // k)):
                tasks.append((tag, hname, (HF, [list(x) for x in sF], nF), li, (H2, [list(x) for x in s2], n2), z))
    with Pool(22) as pool:
        res = pool.map(task4, tasks)
    info4 = collections.Counter()
    for d in res:
        for k, v in d.items():
            info4[k] += v
    ok4 = all(v == 0 for k, v in info4.items() if k.startswith("far") and "disagree" in k) and \
        all(v == 0 for k, v in info4.items() if k.startswith("near") and "disagree" in k)
    check("4 the claim rule against the pipeline: with the same three handles on thick tubes, a grid, two random grown spaces and a ladder "
          "arm spliced onto a grid (every attachment point of the last), the rule agrees with the pipeline at every gluing line beyond "
          "distance 3, and at every nearer line where it applies; the nearer lines squeezed in another form are counted",
          ok4 and info4["far: rule True, pipeline True"] > 0, dict(info4))

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
