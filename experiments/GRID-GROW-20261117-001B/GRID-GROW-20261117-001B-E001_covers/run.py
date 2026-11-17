"""Read-out for GRID-GROW-20261117-001B-E001 (frozen before running).

C1 every nonempty Young diagram inside a 4 x 4 box (69 shapes): the box-betweenness base equals the cut system, and the
   disagreement count is twice the L1 distance.
C2 every step (shape, outer corner inside the box): minimum number of three-place knots, minimum within each L1 radius of p, the
   smallest radius reaching the minimum, one such cover, and whether the unit-square four-place parity alone covers.
C3 growth runs from the three-cell L (0,0), (1,0), (0,1), whose cut system is the single knot B((1,0), (0,0), (0,1)):
   arms then fill, and raster, to the 4 x 4 square.  At each step the most local minimum cover is added; the base is then
   recomputed from all knots by brute force and compared with the target cut system.
    python3 -B run.py      (writes artifacts/.../results.json)
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import gridgrow as G  # noqa: E402

OUT = os.path.join(ROOT, "artifacts", "GRID-GROW-20261117-001B", "GRID-GROW-20261117-001B-E001_covers")


def c1():
    rows = []
    for S in G.young_diagrams(4, 4):
        cells = sorted(S)
        n = len(cells)
        sts = G.cut_states(cells)
        d_ok = all(sum(((s >> i) ^ (s >> j)) & 1 for s in sts) == 2 * G.l1(cells[i], cells[j]) for i in range(n) for j in range(n))
        rows.append({"cells": n, "box_base_is_cut_system": G.box_base_equals_cuts(cells), "d_is_2L1": d_ok})
    return rows


def c2():
    out = []
    for S in G.young_diagrams(4, 4):
        for p in G.outer_corners(S, 4, 4):
            out.append(G.step_covers(S, p))
    return out


def grow(order):
    S = {(0, 0), (1, 0), (0, 1)}
    knots = [((1, 0), (0, 0), (0, 1), G.BTW)]
    steps = []
    for p in order:
        r = G.step_covers(frozenset(S), p)
        chosen = r["example_cover"]["knots"]
        S2 = S | {p}
        cells = sorted(S2)
        idx = {c: i for i, c in enumerate(cells)}
        knots_new = knots + [tuple(k["cells"]) + (k["excluded"],) for k in r["example_cover"]["knots_full"]]
        n = len(cells)
        sts = {s for s in range(1 << n) if all(tuple((s >> idx[c]) & 1 for c in kn[:3]) not in kn[3] for kn in knots_new)}
        exact = sts == G.cut_states(cells)
        steps.append({"p": p, "kind": r["kind"], "knots_added": len(chosen), "max_l1_from_p": r["example_cover"]["max_l1_from_p"],
                      "exact": exact})
        S, knots = S2, knots_new
    deg = {}
    for kn in knots:
        for c in kn[:3]:
            deg[c] = deg.get(c, 0) + 1
    return {"steps": steps, "total_knots": len(knots), "max_knots_per_distinction": max(deg.values()),
            "busiest": sorted(deg.items(), key=lambda kv: -kv[1])[:3]}


def main():
    os.makedirs(OUT, exist_ok=True)
    res = {"started": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    res["C1"] = c1()
    res["C2"] = c2()
    arms_fill = [(2, 0), (3, 0), (0, 2), (0, 3), (1, 1), (2, 1), (1, 2), (3, 1), (2, 2), (1, 3), (3, 2), (2, 3), (3, 3)]
    raster = [(2, 0), (3, 0), (1, 1), (2, 1), (3, 1), (0, 2), (1, 2), (2, 2), (3, 2), (0, 3), (1, 3), (2, 3), (3, 3)]
    res["C3"] = {"arms then fill": grow(arms_fill), "raster": grow(raster)}
    res["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    with open(os.path.join(OUT, "results.json"), "w") as f:
        json.dump(res, f, indent=1, default=str)
    print("wrote", os.path.join(OUT, "results.json"), res["started"], res["finished"])


if __name__ == "__main__":
    main()
