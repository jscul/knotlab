#!/usr/bin/env python3
"""Checks for COUNT-TFNP-20261107-001A: SINK reduces to one-sided grid Sperner by shallow decision trees.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv. Single process; a few minutes."""
import hashlib
import itertools
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import tube_lib as T  # noqa: E402

T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:500], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def random_instance(N, rng):
    """random disjoint paths and cycles with node 0 starting a path, plus occasional inconsistent pointers and edges into 0"""
    perm = list(range(1, N))
    rng.shuffle(perm)
    succ, pred = [None] * N, [None] * N
    order = [0] + perm
    i = 0
    while i < len(order):
        L = rng.randint(1, 4)
        seg = order[i:i + L]
        for u, v in zip(seg, seg[1:]):
            succ[u], pred[v] = v, u
        if len(seg) >= 3 and seg[0] != 0 and rng.random() < 0.3:
            succ[seg[-1]], pred[seg[0]] = seg[0], seg[-1]
        i += L
    if rng.random() < 0.3:
        succ[rng.randrange(N)] = rng.randrange(N)
    if rng.random() < 0.2:
        u = rng.randrange(1, N)
        if succ[u] is None:
            succ[u], pred[0] = 0, u          # an edge into the standard source
    return succ, pred


def verify(L, succ, pred, **kw):
    """the theorem's claims on one instance: (full triangles at ports with the right orientations, no boundary clash, back-map valid)"""
    col, route, clash, cr = T.colouring(L, succ, pred, **kw)
    full = T.full_triangles(col, L["m"])
    sinks, sources = T.leaves(L["N"], succ, pred)
    at = {}
    for t, o in full:
        at.setdefault(T.triangle_node(L, t), []).append(o)
    expect = {j: [1] for j in sinks}
    expect.update({j: [-1] for j in sources})
    back = all(T.is_sink_solution(succ, pred, T.back_map(succ, pred, j)) for j in sinks)
    return (not clash) and at == expect and back, col, cr, at, expect


def crossing_types(L, succ, pred):
    """(horizontal direction, vertical direction) at each crossing of two present runs"""
    route, crossings = T.draw(L, succ, pred, uncross=False)
    runs = {}
    for (i, j) in T.present_edges(succ, pred):
        pts = T.steps(T.polyline(L, i, j))
        for k in range(1, len(pts) - 1):
            d = (pts[k + 1][0] - pts[k][0], pts[k + 1][1] - pts[k][1])
            runs.setdefault(pts[k], []).append(d)
    kinds = set()
    for X in crossings:
        ds = runs.get(X, [])
        dh = [d for d in ds if d[1] == 0]
        dv = [d for d in ds if d[0] == 0]
        if dh and dv:
            kinds.add((dh[0], dv[0]))
    return kinds


def port_types(L, succ, pred):
    """for each node: (has an in-edge, has an out-edge) in the drawn graph (node 0 is fed by the door)"""
    edges = T.present_edges(succ, pred)
    return {(j == 0 or any(e[1] == j for e in edges), any(e[0] == j for e in edges)) for j in range(L["N"])}


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(".json") and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})
    rng = random.Random(20261107)

    # 1. every consistent pointer structure on 3 nodes, plus all single inconsistent pointers from them
    L3 = T.layout(3)
    n1, fails1, cross1 = 0, [], 0
    for succ in itertools.product([None, 0, 1, 2], repeat=3):
        succ = [None if (s == u) else s for u, s in enumerate(succ)]
        if len({s for s in succ if s is not None}) < sum(s is not None for s in succ):
            continue                                   # two nodes pointing to one: not in- and out-degree <= 1
        pred = [None] * 3
        for u, v in enumerate(succ):
            if v is not None:
                pred[v] = u
        for extra in [None] + [(u, v) for u in range(3) for v in range(3)]:
            s2 = list(succ)
            if extra is not None:
                s2[extra[0]] = extra[1]
            ok, col, cr, at, expect = verify(L3, s2, pred)
            n1 += 1
            cross1 += len(cr)
            if not ok:
                fails1.append((s2, pred, at, expect))
    check("1 every pointer structure on 3 nodes (consistent ones and each with one pointer changed): fully labelled triangles occur "
          "exactly at the ports of the drawn graph's sinks (positive) and non-standard sources (negative), never on the fixed boundary's "
          "wrong colour, and every positive one maps back to a SINK solution", not fails1,
          {"instances": n1, "crossings resolved": cross1, "failures": fails1[:2]})

    # 2. random instances on 4..7 nodes
    n2, fails2, cross2, kinds, ports = 0, [], 0, set(), set()
    sizes = {}
    for trial in range(36):
        N = rng.randint(4, 7)
        succ, pred = random_instance(N, rng)
        L = T.layout(N)
        sizes[N] = L["m"]
        ok, col, cr, at, expect = verify(L, succ, pred)
        n2 += 1
        cross2 += len(cr)
        kinds |= crossing_types(L, succ, pred)
        ports |= port_types(L, succ, pred)
        if not ok:
            fails2.append((N, succ, pred, at, expect))
    possible = {((1, 0), (0, 1)), ((-1, 0), (0, 1)), ((-1, 0), (0, -1))}   # an eastward out-run never meets a southward column
    check("2 random instances on 4..7 nodes (paths, cycles, inconsistent pointers, edges into the standard source): the same; every "
          "local picture of the layout occurs: the three possible crossing types (horizontal east against vertical north, horizontal "
          "west against vertical north or south; east against south cannot occur) and every port type (isolated, sink, source, through)",
          not fails2 and kinds == possible and len(ports) == 4,
          {"instances": n2, "crossings resolved": cross2, "crossing types (horizontal, vertical)": sorted(kinds),
           "port types (in, out)": sorted(ports),
           "grid side m by number of nodes": sizes, "m / N^2": {N: round(m / N ** 2, 1) for N, m in sizes.items()}, "failures": fails2[:2]})

    # 3. locality: changing one pointer changes colours only near the drawings of edges whose presence changed
    far, n3 = 0, 0
    for trial in range(10):
        N = rng.randint(4, 6)
        succ, pred = random_instance(N, rng)
        L = T.layout(N)
        col1 = T.colouring(L, succ, pred)[0]
        s2 = list(succ)
        s2[rng.randrange(N)] = rng.choice([None] + list(range(N)))
        col2 = T.colouring(L, s2, pred)[0]
        changed = [v for v in col1 if col1[v] != col2[v]]
        e1, e2 = T.present_edges(succ, pred), T.present_edges(s2, pred)
        near = set()
        for (i, j) in e1 ^ e2:
            for p in T.steps(T.polyline(L, i, j)):
                for dx in range(-L["r"] - 2, L["r"] + 3):
                    for dy in range(-L["r"] - 2, L["r"] + 3):
                        near.add((p[0] + dx, p[1] + dy))
        far += sum(1 for v in changed if v not in near)
        n3 += 1
    check("3 locality: when one pointer changes, every vertex whose colour changes lies within distance r + 2 of the drawing of an edge "
          "whose presence changed (so each colour is a function of O(1) pointers: decision trees of depth O(log N))", far == 0,
          {"instance pairs": n3, "changed vertices far from the changed edges": far})

    # 4. negative controls: each mutation must make the claim fail
    ctl = {}
    succ, pred = [1, 2, None, None, None], [None, 0, 1, None, None]
    succ[3], pred[4] = 4, 3                       # 0 -> 1 -> 2 and 3 -> 4: a sink at 2 and at 4, a source at 3, with crossings
    L = T.layout(5)
    base_ok = verify(L, succ, pred)[0]
    ctl["base instance passes"] = base_ok
    ctl["no uncrossing: rejected"] = not verify(L, succ, pred, uncross=False)[0]
    L2 = dict(L, r=2)
    ctl["turn radius 2: rejected"] = not verify(L2, succ, pred)[0]
    orig_right = T.right
    T.right = T.left                               # lane 2 on the left: orientations flip
    ctl["lane 2 on the left: rejected"] = not verify(L, succ, pred)[0]
    T.right = orig_right
    check("4 controls: the instance passes, and dropping the uncrossing, shrinking the turn radius to 2, or putting lane 2 on the left "
          "each make the check fail", all(ctl.values()), ctl)

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
