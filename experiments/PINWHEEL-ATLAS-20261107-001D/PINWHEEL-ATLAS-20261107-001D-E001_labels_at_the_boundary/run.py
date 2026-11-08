"""PINWHEEL-ATLAS-20261107-001D-E001: regrowth with the labels dropped (exploratory; see contract.json).

The growing patch is T_k, one triangle cut k times. Its unlabelled planar map gets one outside vertex joined to every boundary vertex,
placed in the outer face of each boundary vertex's rotation. A rooted code records the outside vertex as a marked leaf (degree -1, not
expanded), so codes see the boundary's shape but nothing global. For each level k and radius r, every dart of T_k (boundary darts
and their neighbours included) is grouped by its code; a code carrying two oriented labels is a conflict.
Writes artifacts/PINWHEEL-ATLAS-20261107-001D/PINWHEEL-ATLAS-20261107-001D-E001_labels_at_the_boundary/run/result.json."""
from __future__ import annotations
import json, math, random, sys, time
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import atlas_lib as A

OUT = ROOT / "artifacts" / "PINWHEEL-ATLAS-20261107-001D" / "PINWHEEL-ATLAS-20261107-001D-E001_labels_at_the_boundary" / "run"
INF = -1

def with_outside(M, k):
    """Insert the outside vertex into each boundary vertex's rotation, in the sector that lies outside the patch."""
    pts, rot = M["pts"], M["rot"]
    S = 10 ** k
    big = ((0, 0), (2 * S, 0), (0, S))            # the patch is this triangle (O, P, Q)
    def inside(x, y):
        (ax, ay), (bx, by), (cx, cy) = big
        def side(px, py, qx, qy):
            return (qx - px) * (y - py) - (qy - py) * (x - px)
        s1, s2, s3 = side(ax, ay, bx, by), side(bx, by, cx, cy), side(cx, cy, ax, ay)
        return (s1 > 0 and s2 > 0 and s3 > 0) or (s1 < 0 and s2 < 0 and s3 < 0)
    rot2 = {v: list(nb) for v, nb in rot.items()}
    for b in M["boundary"]:
        x, y = pts[b]
        nb = rot[b]
        ang = [math.atan2(pts[w][1] - y, pts[w][0] - x) for w in nb]
        minlen = min(math.hypot(pts[w][0] - x, pts[w][1] - y) for w in nb)
        placed = False
        for i in range(len(nb)):
            a0, a1 = ang[i], ang[(i + 1) % len(nb)]
            gap = (a1 - a0) % (2 * math.pi) or 2 * math.pi
            mid = a0 + gap / 2
            px, py = x + 1e-3 * minlen * math.cos(mid), y + 1e-3 * minlen * math.sin(mid)
            if not inside(px, py):
                rot2[b] = nb[:i + 1] + [INF] + nb[i + 1:]
                placed = True
                break
        assert placed
    rot2[INF] = []
    return rot2

def code_out(rot, u, v, r, mark=True):
    """The rooted code of PINWHEEL-NATIVE-20261107-001B, with the outside vertex recorded as a leaf of degree -1."""
    num = {u: 0}; order = [u]; entry = {u: v}; dist = {u: 0}
    out = []
    i = 0
    while i < len(order):
        x = order[i]; i += 1
        if x == INF:
            out.append((-1, ()))
            continue
        nb = [y for y in rot[x] if mark or y != INF]
        k = nb.index(entry[x])
        row = []
        for y in nb[k:] + nb[:k]:
            if dist[x] < r:
                if y not in num:
                    num[y] = len(order); order.append(y); entry[y] = x; dist[y] = dist[x] + 1
                row.append(num[y])
            else:
                row.append(num.get(y, -1))
        out.append((len(nb), tuple(row)))
    return tuple(out)

def main():
    t0 = time.time()
    levels, radii = (4, 5, 6, 7), (1, 2, 3, 4, 5, 6)
    groups = {r: defaultdict(set) for r in radii}            # over all levels
    blind = {r: defaultdict(set) for r in radii}
    per_level = {}
    maps = {}
    for k in levels:
        M = A.build_map(A.pinwheel_patch(k), 1)
        rot = with_outside(M, k)
        maps[k] = (M, rot)
        db = A.bfs_dist(M["rot"], list(M["boundary"]))
        per_level[k] = {}
        for r in radii:
            g = defaultdict(set)
            near = defaultdict(set)
            for (u, v), lab in M["dlab"].items():
                c = code_out(rot, u, v, r)
                g[c].add(lab); groups[r][c].add(lab)
                blind[r][code_out(rot, u, v, r, mark=False)].add(lab)
                if db.get(u, 0) <= r + 1:
                    near[c].add(lab)
            conf = [c for c, s in g.items() if len(s) > 1]
            per_level[k][r] = {"darts": len(M["dlab"]), "codes": len(g), "conflicting_codes": len(conf),
                               "conflicting_codes_near_boundary": sum(1 for c in conf if c in near)}
            print("level", k, "r", r, per_level[k][r], round(time.time() - t0, 1), "s", flush=True)
    across = {r: {"codes": len(groups[r]), "conflicting_codes": sum(1 for s in groups[r].values() if len(s) > 1)} for r in radii}
    blind_s = {r: {"codes": len(blind[r]), "conflicting_codes": sum(1 for s in blind[r].values() if len(s) > 1)} for r in radii}
    free = [r for r in radii if across[r]["conflicting_codes"] == 0]
    rstar = min(free) if free else None
    controls = {}
    if rstar is not None:
        rng = random.Random(20261107)
        M, rot = maps[6]
        darts = list(M["dlab"]); labs = [M["dlab"][d] for d in darts]; rng.shuffle(labs)
        g = defaultdict(set)
        for d, lab in zip(darts, labs):
            g[code_out(rot, d[0], d[1], rstar)].add(lab)
        controls["shuffled labels, level 6, r*"] = sum(1 for s in g.values() if len(s) > 1)
    res = {"levels": list(levels), "radii": list(radii), "per_level": per_level, "across_levels": across,
           "outside_not_marked": blind_s, "least_conflict_free_radius": rstar, "controls": controls,
           "runtime_seconds": round(time.time() - t0, 1)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(res, indent=1) + "\n")
    print("least conflict-free radius", rstar, "controls", controls, "runtime", res["runtime_seconds"])

if __name__ == "__main__":
    main()
