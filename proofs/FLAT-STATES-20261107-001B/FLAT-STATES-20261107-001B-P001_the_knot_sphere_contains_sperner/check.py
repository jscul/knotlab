#!/usr/bin/env python3
"""Checks for FLAT-STATES-20261107-001B: the knot sphere contains Sperner's lemma.

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (networkx, python-sat). Single process; several minutes."""
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
import sperner_lib as S  # noqa: E402
import window_lib as W  # noqa: E402

F = S.F
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str), round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def orientation(col, t):
    """+1 when the colours increase along the listed (counterclockwise) order of t, -1 when they decrease, 0 if t is not full"""
    c = [col[v] for v in t]
    if len(set(c)) < 3:
        return 0
    return 1 if (c[1] - c[0]) % 3 == 1 and (c[2] - c[1]) % 3 == 1 else -1


def ccw(m):
    up = [((a, b), (a + 1, b), (a, b + 1)) for a in range(m) for b in range(m - a)]
    dn = [((a + 1, b), (a + 1, b + 1), (a, b + 1)) for a in range(m) for b in range(m - a - 1)]
    return {tuple(sorted(t)): t for t in up + dn}


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(".json") and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})

    # 1. the local lemma in the bulk: inside one coarse triangle, which fine lines are violated
    SUB = lambda p: (p[0] - p[1]) % 3  # noqa: E731
    U = lambda x, y: ((x, y), (x + 1, y), (x, y + 1))  # noqa: E731
    info1, ok1 = {}, True
    for kind in ("up", "down"):
        for phase in range(3):
            o = (phase, 0)
            if kind == "up":
                verts = [(0, 0), (1, 0), (0, 1)]
                lines = [U(0, 0), U(1, 0), U(0, 1)]
            else:
                verts = [(1, 0), (1, 1), (0, 1)]
                lines = [U(1, 1)]
            tally = {}
            for cs in itertools.product(range(3), repeat=3):
                col = dict(zip(verts, cs))
                lab = {}
                for X in range(4):
                    for Y in range(4):
                        cv = S.coarse_of((X, Y))
                        if all(v in col for v in cv):
                            lab[(X, Y)] = S.label_from([col[v] for v in cv])
                viol = 0
                for L in lines:
                    pts = [(p[0] + o[0], p[1] + o[1]) for p in L]
                    cols = {F.PATTERNS[lab[p]][SUB(q)] for p, q in zip(L, pts)}
                    viol += len(cols) == 1
                key = {1: "positive full", -1: "negative full", 0: "not full"}[orientation(col, verts)]
                tally.setdefault(key, set()).add(viol)
            info1["%s, phase %d" % (kind, phase)] = {kk: sorted(v) for kk, v in sorted(tally.items())}
            ok1 &= tally["not full"] == {0} and tally["negative full"] == {0} and 0 not in tally["positive full"]
    check("1 local lemma (bulk lattice, exhaustive): inside a coarse triangle of the doubled grid, with labels 2c at Sperner vertices and "
          "midpoint labels between, no fine line is violated unless the triangle is fully labelled counterclockwise, and then at least one "
          "is; a clockwise full triangle holds none (it holds a full face instead)", ok1, info1)

    # 2. the reduction on the knot sphere
    info2, ok2 = {}, True
    rng = random.Random(2026)
    for m in (3, 4, 5, 6):
        k = 2 * m + 4
        red = S.build_reduction(k, m)
        iv = S.interior_vertices(m)
        tri = ccw(m)
        reads = max(len(S.coarse_of(XY)) for XY in red["R"].values())
        combos = list(itertools.product(range(3), repeat=len(iv))) if 3 ** len(iv) <= 3000 else \
            [tuple(rng.randrange(3) for _ in iv) for _ in range(3000)]
        n_ok = n_pos = n_neg = 0
        nets = set()
        for cs in combos:
            x, col = S.image(red, dict(zip(iv, cs)))
            fulls = {key: orientation(col, t) for key, t in tri.items() if orientation(col, t)}
            net = sum(fulls.values())
            hit = {}
            for l in F.violated(red["K"], x):
                ct = S.coarse_triangle_of_line(red, l)
                hit[ct] = hit.get(ct, 0) + 1
            good = abs(net) == 1 and set(hit) == {key for key, sg in fulls.items() if sg == net}
            nets.add(net)
            n_ok += good
            n_pos += sum(1 for sg in fulls.values() if sg == net)
            n_neg += sum(1 for sg in fulls.values() if sg == -net)
        ok2 &= n_ok == len(combos) and reads <= 2
        info2["m=%d, k=%d" % (m, k)] = {"Sperner colourings (exhaustive if <= 3000)": len(combos), "colourings whose violated lines lie "
                                         "exactly inside the full triangles oriented like the boundary": n_ok,
                                         "full triangles oriented like the boundary": n_pos,
                                         "oppositely oriented full triangles (no violated line)": n_neg,
                                         "net orientation in the listing used": sorted(nets),
                                         "Sperner colours read per point (at most)": reads,
                                         "boundary corner colours": [red["bcol"][(0, 0)], red["bcol"][(m, 0)], red["bcol"][(0, m)]]}
    check("2 the reduction (m = 3..6, k = 2m + 4): for every tested Sperner colouring of the side-m grid with the fixed boundary, the image "
          "assignment of K_k violates lines exactly inside the fully labelled triangles oriented like the boundary (every such triangle "
          "holds one or more, the opposite ones none; the net count is 1), and each point's colour reads at most two Sperner colours", ok2, info2)

    # 3. the window criterion against a solver
    info3, ok3 = {}, True
    rng = random.Random(11)
    for m in (5, 6, 7):
        V, tris, _ = W.grid(m)
        bc = W.boundary_colours(m)
        agree = dis = infeas = 0
        for trial in range(25):
            T0_, col = W.random_state(m, rng)
            inner = [v for v in V if v not in bc]
            P = set(rng.sample(inner, rng.randint(2, len(inner) // 2)))
            peb = {v: col[v] for v in P}
            peb.update(bc)
            for T in tris:
                if any(v in P for v in T):
                    continue
                a, b = W.feasible_by_window(m, T, peb), W.feasible_by_solver(m, T, peb)
                agree += a == b
                dis += a != b
                infeas += not b
        ok3 &= dis == 0 and infeas > 0 and agree > infeas
        info3["m=%d" % m] = {"(pebble set, triangle) pairs": agree + dis, "criterion agrees with the solver": agree,
                             "infeasible (solver)": infeas}
    check("3 the window criterion: for random pebbled colourings (taken from random one-full-triangle states, boundary pebbled) and every "
          "triangle T avoiding the pebbles, the integer difference system on pebble sheets has no negative cycle exactly when a solver finds "
          "a state with T as the only full triangle, counterclockwise", ok3, info3)

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
