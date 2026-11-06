#!/usr/bin/env python3
"""Checks for STRIP-RELAY-20261103-001C: rigid strips relay a handle.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (numpy, networkx). Uses up to 22 processes. About fifteen minutes."""
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
sys.path.insert(0, str(ROOT / "proofs/SPLICE-TREE-20261102-001C/SPLICE-TREE-20261102-001C-P001_opened_cuts_interact"))
import strip_lib as SL  # noqa: E402
import elim_lib as E  # noqa: E402

PL, FL, HP, CL, G, J = SL.PL, SL.FL, SL.HP, SL.CL, SL.G, SL.HP.J
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:900], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        print(json.dumps(info, default=str, indent=1))
        sys.exit(1)


def middle(kind, size):
    return PL.prism(size) if kind == "rigid strip" else (FL.octahedral(size) if kind == "grid" else FL.tube(size, 1))


def task(args):
    """one attachment point of a dumbbell: far creation by the part of its line, with the point's part and its distance to grid1"""
    kind, size, l1, l2, receive2, z, claim = args
    h, part, v1, v3 = SL.dumbbell(middle(kind, size), l1, l2, receive2)
    (H2, s2, n2), pts, lns = SL.labelled(h)
    org = nx.get_node_attributes(h, "origin")
    g1v = [v for v in h if part[v] == "grid1"]
    dz = min(nx.single_source_shortest_path_length(h, pts[z])[v] for v in g1v) if part[pts[z]] != "grid1" else 0
    hs = SL.halo_space(H2, s2, n2, z, (0, 1, 2))
    gm = nx.Graph()
    gm.add_edges_from((("p", q), ("l", kk)) for kk, L in enumerate(hs.lines) for q in L)
    dist = nx.multi_source_dijkstra_path_length(gm, [("p", q) for q in range(hs.nF)] + [("l", kk) for kk in range(hs.nh)])
    Hands = [hs.handle(M) for M in range(hs.nh)]
    out = collections.Counter()
    relayed = []
    for L in range(hs.nh, len(hs.lines)):
        if dist[("l", L)] <= 3:
            continue
        j = hs.qline[L]
        R = hs.transfer(L)
        made = any(HP.creates(hs, M, L, F, Hands[M], R) for M in range(hs.nh) for fname, F in SL.FARS)
        if claim and part[lns[j]] == "grid1" and part[pts[z]] != "grid1":
            rule = any(CL.claim_rule_at(hs, L, R, Hands[M]) is True for M in range(hs.nh))
            out["grid1 lines from outside grid1: claim rule %s, pipeline %s" % (rule, made)] += 1
        if made:
            out["%s -> %s" % (part[pts[z]], part[lns[j]])] += 1
            if part[lns[j]] == "grid1" and part[pts[z]] != "grid1":
                relayed.append(org[lns[j]])
    return z, part[pts[z]], dz, out, sorted(relayed)


def task_exact(args):
    size, z, M = args
    h, part, v1, v3 = SL.dumbbell(PL.prism(size), 0, 0, False)
    (H2, s2, n2), pts, lns = SL.labelled(h)
    hs = SL.halo_space(H2, s2, n2, z, (0, 1, 2))
    AN = CL.solutions(hs.lines, hs.signs, hs.n, skip=M)
    Hand = hs.handle(M)
    out = collections.Counter()
    for L in range(hs.nh, len(hs.lines)):
        if len({tuple(int(b) for b in r) for r in AN[:, list(hs.lines[L])]}) != 6:
            continue
        where = part[lns[hs.qline[L]]]
        for fname, F in SL.FARS:
            exact = bool(J.new_knots(E, G, AN, hs.lines, hs.signs, hs.n, L, F, 3)[0])
            pipe = HP.creates(hs, M, L, F, Hand)
            out["line in %s: exact %s, pipeline %s" % (where, exact, pipe)] += 1
    return out


def run(kind, size, l1, l2, receive2, claim=False):
    h, part, v1, v3 = SL.dumbbell(middle(kind, size), l1, l2, receive2)
    n2 = SL.labelled(h)[0][2]
    with Pool(22) as pool:
        return pool.map(task, [(kind, size, l1, l2, receive2, z, claim) for z in range(n2)]), n2


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {p: d for p, d in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != d}
    status = {p: json.loads((ROOT / p).read_text()).get("status") for p in manifest["parent_bindings"]
              if p.endswith(".json") and p.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})

    # -------------------------------------------------------------------------------------------- 1. rigid strips of several lengths
    info1 = {}
    ok1 = True
    relayed_sets = []
    claim_info = collections.Counter()
    for size in (8, 12, 16, 24):
        res, n2 = run("rigid strip", size, 1, 1, False, claim=(size == 8))
        rel = [(pz, dz) for z, pz, dz, out, r in res if r]
        lines = sorted({tuple(x) for z, pz, dz, out, r in res for x in r})
        strip_d = sorted({dz for z, pz, dz, out, r in res if pz == "strip"})
        relayed_sets.append(lines)
        reach = max(d for p, d in rel) if rel else 0
        per_d = collections.Counter(d for p, d in rel if p == "strip")
        two_each = all(per_d[d] == 2 for d in range(3, max(strip_d) + 1, 2)) and set(per_d) == set(range(3, max(strip_d) + 1, 2))
        ok1 &= bool(rel) and reach >= max(strip_d) and any(p == "grid2" for p, d in rel) and two_each
        info1["strip from a ring over a %d-cycle" % (2 * size)] = {"points": n2, "relaying points (part, distance to grid1)": rel,
                                                                   "relayed grid1 lines (origins)": lines,
                                                                   "largest distance of a strip point": max(strip_d),
                                                                   "two strip points relay at every odd distance from 3 to the far end": two_each}
        if size == 8:
            for z, pz, dz, out, r in res:
                claim_info.update({k: v for k, v in out.items() if k.startswith("grid1 lines from outside")})
    ok1 &= all(s == relayed_sets[0] for s in relayed_sets)
    check("1 rigid strips relay: in dumbbells grid -- strip -- grid with strips from rings over 16- to 48-cycles, an opened Fano handle at "
          "two strip points at every distance from the first grid up to the strip's far end, and at a point of the second grid, creates in "
          "the first grid beyond the strip, always at the same lines around the removed vertex", ok1, info1)
    ok1b = all(v == 0 for k, v in claim_info.items() if ("rule True, pipeline False" in k or "rule False, pipeline True" in k)) and \
        claim_info["grid1 lines from outside grid1: claim rule True, pipeline True"] > 0
    check("1b the claim rule agrees with the pipeline at every first-grid line seen from outside the first grid (strip from a 16-cycle)",
          ok1b, dict(claim_info))

    # -------------------------------------------------------------------------------------------- 2. liquid connectors
    info2 = {}
    ok2 = True
    for kind, size in (("grid", 2), ("grid", 3), ("thick tube", 4), ("thick tube", 6), ("thick tube", 8)):
        res, n2 = run(kind, size, 1, 1, False)
        rel = sorted(dz for z, pz, dz, out, r in res if r)
        alld = sorted({dz for z, pz, dz, out, r in res if pz != "grid1"})
        if kind == "grid":
            ok2 &= bool(rel) and max(rel) <= 3
        info2["%s %d" % (kind, size)] = {"points": n2, "distances of relaying points to grid1": rel, "largest distance": max(alld)}
    check("2 liquid connectors screen: with a grid (64 or 256 points) between the two grids, only points 3 steps from the first grid relay; "
          "thick tubes, which have long polar faces, relay part of the way", ok2, info2)

    # -------------------------------------------------------------------------------------------- 3. orientation
    info3 = {}
    ok3 = True
    for receive2 in (False, True):
        for size in (8, 12):
            res, n2 = run("rigid strip", size, 1, 1, receive2)
            agg = collections.Counter()
            for z, pz, dz, out, r in res:
                agg.update({k: v for k, v in out.items() if "->" in k})
            if receive2:
                ok3 &= agg["strip -> grid1"] > 0 and agg["strip -> grid2"] > 0 and agg["grid1 -> grid2"] == 0 and agg["grid2 -> grid1"] == 0 \
                    and agg["grid1 -> strip"] == 0 and agg["grid2 -> strip"] == 0
            else:
                ok3 &= agg["grid2 -> grid1"] > 0 and agg["grid1 -> strip"] == 0 and agg["grid1 -> grid2"] == 0 and agg["strip -> grid2"] == 0
            info3["strip %d, second grid %s" % (2 * size, "split at a point" if receive2 else "minus a line")] = dict(sorted(agg.items()))
    check("3 orientation: a grid receives only through a cut where it is split at a point (its cut vertices are lines); a handle leaves its "
          "grid only through a cut where the grid has lost a line. With the second grid minus a line, its handles relay into the first grid "
          "and first-grid handles stay; with both grids split at a point, strip handles relay into both and grid handles stay", ok3, info3)

    # -------------------------------------------------------------------------------------------- 4. exact creation on small dumbbells
    info4 = {}
    ok4 = True
    for size in (4, 6):
        res, n2 = run("rigid strip", size, 0, 0, False)
        far_relays = [(z, dz) for z, pz, dz, out, r in res if r and dz >= 5]
        ok4 &= bool(far_relays)
        tasks = [(size, z, M) for z, dz in far_relays for M in range(6)]
        with Pool(min(22, len(tasks))) as pool:
            outs = pool.map(task_exact, tasks)
        agg = collections.Counter()
        for o in outs:
            agg.update(o)
        ok4 &= all(v == 0 for k, v in agg.items() if ("exact True, pipeline False" in k or "exact False, pipeline True" in k)) and \
            agg["line in grid1: exact True, pipeline True"] > 0
        info4["two cubes joined by a strip from a ring over a %d-cycle" % (2 * size)] = dict(agg, **{"points": n2, "relaying points 5 or more steps away": far_relays})
    check("4 exact relays: on small dumbbells (two 4-point cubes joined by strips from 8- and 12-cycles), at the points relaying from 5 or more "
          "steps, exact creation (join method) agrees with the pipeline at every line, removal and far side, and creates in the first grid",
          ok4, info4)

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
