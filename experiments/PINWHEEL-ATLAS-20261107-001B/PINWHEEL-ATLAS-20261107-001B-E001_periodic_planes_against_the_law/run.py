"""PINWHEEL-ATLAS-20261107-001B-E001: does a periodic plane satisfy the pinwheel's radius-r law? (exploratory; see contract.json)

The law is ticket A's atlas: the radius-2 rooted codes of all pinwheel tilings (atlas.json), and its radius-1 truncation. A candidate
plane passes at radius r when every dart farther than r + 1 from its patch boundary has its radius-r code in the law. Candidates are
declared in contract.json. Writes artifacts/PINWHEEL-ATLAS-20261107-001B/PINWHEEL-ATLAS-20261107-001B-E001_periodic_planes_against_the_law/run/result.json."""
from __future__ import annotations
import itertools, json, math, sys, time
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import atlas_lib as A

ATLAS = ROOT / "proofs" / "PINWHEEL-ATLAS-20261107-001A" / "PINWHEEL-ATLAS-20261107-001A-P001_the_complete_radius_2_atlas" / "atlas.json"
OUT = ROOT / "artifacts" / "PINWHEEL-ATLAS-20261107-001B" / "PINWHEEL-ATLAS-20261107-001B-E001_periodic_planes_against_the_law" / "run"

def load_law():
    data = json.loads(ATLAS.read_text())
    c2 = {tuple((d, tuple(row)) for d, row in c) for c, _ in data["atlas"]}
    def trunc(c):
        deg0 = c[0][0]
        rows = [c[0]] + [(d, tuple(x if x <= deg0 else -1 for x in row)) for d, row in c[1:deg0 + 1]]
        return tuple(rows)
    c1 = {trunc(c) for c in c2}
    return {1: c1, 2: c2}

# ---- candidates ------------------------------------------------------------------------------------------------------------------
def rect_h(x, y, d):
    a, b, c, e = (x, y), (x + 2, y), (x + 2, y + 1), (x, y + 1)
    return [(a, b, e), (c, e, b)] if d == 0 else [(b, a, c), (e, c, a)]

def rect_v(x, y, d):
    a, b, c, e = (x, y), (x + 1, y), (x + 1, y + 2), (x, y + 2)
    return [(b, c, a), (e, a, c)] if d == 0 else [(a, e, b), (c, b, e)]

def rows_plane(pattern, n, brick):
    p, q = len(pattern), len(pattern[0])
    tiles = []
    for j in range(-n, n):
        for i in range(-n, n):
            tiles += rect_h(2 * i + (1 if brick and j % 2 else 0), j, pattern[i % p][j % q])
    return tiles

def torus_dominoes(m, n):
    out, cells = [], [(i, j) for j in range(n) for i in range(m)]
    def rec(used, acc):
        free = next((c for c in cells if c not in used), None)
        if free is None:
            out.append(list(acc)); return
        i, j = free
        # the domino covering the first free cell: it may start there or end there (on a torus it can wrap around)
        for kind, start, other in (("h", (i, j), ((i + 1) % m, j)), ("h", ((i - 1) % m, j), ((i - 1) % m, j)),
                                   ("v", (i, j), (i, (j + 1) % n)), ("v", (i, (j - 1) % n), (i, (j - 1) % n))):
            if other not in used and other != free:
                used |= {free, other}; acc.append((kind,) + start); rec(used, acc); acc.pop(); used -= {free, other}
    rec(set(), [])
    return out

def torus_plane(doms, diags, m, n, size=12):
    ra, rb = -(-size // m), -(-size // n)
    tiles = []
    for a in range(ra):
        for b in range(rb):
            for (kind, i, j), d in zip(doms, diags):
                x, y = i + a * m, j + b * n
                tiles += rect_h(x, y, d) if kind == "h" else rect_v(x, y, d)
    return tiles

def halfturn_plane(poly, pair, radius):
    """Tile the plane by half-turns of a convex polygon (triangle or quadrilateral) about its edge midpoints; each copy carries the
    two tiles `pair`. Coordinates are integers and 2 * midpoints are used throughout."""
    k = len(poly)
    mids2 = [(poly[i][0] + poly[(i + 1) % k][0], poly[i][1] + poly[(i + 1) % k][1]) for i in range(k)]
    seen = {(1, (0, 0))}; frontier = [(1, (0, 0))]
    while frontier:
        nxt = []
        for s, c in frontier:
            for mx, my in mids2:
                g = (-s, (c[0] + s * mx, c[1] + s * my))
                if g not in seen and abs(g[1][0]) <= radius and abs(g[1][1]) <= radius:
                    seen.add(g); nxt.append(g)
        frontier = nxt
    return [tuple((s * x + c[0], s * y + c[1]) for x, y in t) for s, c in seen for t in pair]

def two_tile_shapes():
    """The six shapes made of two tiles sharing a whole side, scaled by 5: O = (0, 0), Q = (5, 0), P = (0, 10)."""
    O, Q, P = (0, 0), (5, 0), (0, 10)
    T = (O, P, Q)
    rot = lambda t, m2: tuple((m2[0] - x, m2[1] - y) for x, y in t)        # half-turn about m (given as 2m)
    out = {}
    out["rectangle (half-turn across the hypotenuse)"] = ((O, Q, (5, 10), P), [T, rot(T, (5, 10))])
    out["kite (mirror across the hypotenuse)"] = ((O, Q, (8, 4), P), [T, ((8, 4), P, Q)])
    out["parallelogram (half-turn about the short leg's midpoint)"] = ((P, O, (5, -10), Q), [T, rot(T, (5, 0))])
    out["parallelogram (half-turn about the long leg's midpoint)"] = ((Q, P, (-5, 10), O), [T, rot(T, (0, 10))])
    out["isosceles triangle (mirror across the short leg)"] = ((P, Q, (0, -10)), [T, (O, (0, -10), Q)])
    out["isosceles triangle (mirror across the long leg)"] = ((Q, P, (-5, 0)), [T, (O, P, (-5, 0))])
    return out

def frame_consistent_patch(k):
    def split2(tile):
        O, P, Q = tile
        H = (Q[0] + (P[0] - Q[0]) // 5, Q[1] + (P[1] - Q[1]) // 5)
        out = [(H, O, Q)]
        ex = ((P[0] - H[0]) // 2, (P[1] - H[1]) // 2); ey = ((O[0] - H[0]) // 2, (O[1] - H[1]) // 2)
        V = lambda i, j: (H[0] + i * ex[0] + j * ey[0], H[1] + i * ex[1] + j * ey[1])
        for i in range(2):
            for j in range(2 - i):
                out.append((V(i, j), V(i + 1, j), V(i, j + 1)))
                if i + j <= 0:
                    out.append((V(i + 1, j + 1), V(i, j + 1), V(i + 1, j)))
        return out
    tiles = [((0, 0), (2, 0), (0, 1))]
    for _ in range(k):
        tiles = [tuple((x * 10, y * 10) for x, y in t) for t in tiles]
        tiles = [s for t in tiles for s in split2(t)]
    return tiles

def isosceles_patch(k):
    tiles = [((0, 0), (1, 0), (0, 1))]
    for _ in range(k):
        tiles = [tuple((x * 2, y * 2) for x, y in t) for t in tiles]
        nt = []
        for O, P, Q in tiles:
            H = ((P[0] + Q[0]) // 2, (P[1] + Q[1]) // 2)
            nt += [(H, O, P), (H, Q, O)]
        tiles = nt
    return tiles

# ---- evaluation ------------------------------------------------------------------------------------------------------------------
def is_tiling(tiles):
    """No two tiles overlap: distinct centroids and every edge piece is on at most two tiles (checked by the map builder)."""
    cen = [(O[0] + P[0] + Q[0], O[1] + P[1] + Q[1]) for O, P, Q in tiles]
    return len(set(cen)) == len(cen)

def evaluate(tiles, law, radii=(1, 2), stop_at_first=False):
    M = A.build_map(tiles, 1)
    db = A.bfs_dist(M["rot"], list(M["boundary"]))
    out = {}
    for r in radii:
        tested = bad = 0
        for (u, v) in M["dlab"]:
            if db.get(u, 0) <= r + 1 or db.get(v, 0) <= r + 1:
                continue
            tested += 1
            if A.code(M["rot"], u, v, r) not in law[r]:
                bad += 1
                if stop_at_first:
                    break
        out[r] = {"darts": tested, "outside_law": bad, "passes": tested > 0 and bad == 0}
        if not out[r]["passes"]:
            for r2 in radii:
                if r2 > r:
                    out[r2] = {"darts": None, "outside_law": None, "passes": False, "skipped": "fails at a smaller radius"}
            break
    return out

def main():
    t0 = time.time()
    law = load_law()
    res = {"law": {"radius_1_codes": len(law[1]), "radius_2_codes": len(law[2])}, "controls": {}, "families": {}}
    # controls
    res["controls"]["pinwheel level-5 patch"] = evaluate(A.pinwheel_patch(5), law)
    res["controls"]["isosceles right-triangle substitution, level 8"] = evaluate(isosceles_patch(8), law)
    print("controls", res["controls"], flush=True)
    # F1, F2: rows of rectangles, plain and brick
    for brick in (False, True):
        name = "brick rows of rectangles" if brick else "rectangle grid"
        rows = []
        for p, q in ((1, 1), (1, 2), (2, 1), (2, 2)):
            for bits in itertools.product((0, 1), repeat=p * q):
                pat = [list(bits[i * q:(i + 1) * q]) for i in range(p)]
                tiles = rows_plane(pat, 10, brick)
                ev = evaluate(tiles, law, stop_at_first=True)
                rows.append({"period": [p, q], "diagonals": pat, "tiling": is_tiling(tiles),
                             "passes_r1": ev[1]["passes"], "passes_r2": ev[2]["passes"]})
        res["families"][name] = {"tested": len(rows), "pass_r1": sum(r["passes_r1"] for r in rows),
                                 "pass_r2": sum(r["passes_r2"] for r in rows), "all_tilings": all(r["tiling"] for r in rows),
                                 "passing": [r for r in rows if r["passes_r1"]]}
        print(name, {k: v for k, v in res["families"][name].items() if k != "passing"}, flush=True)
    # F3: domino tilings of small tori with every diagonal choice
    for m, n in ((2, 2), (2, 4), (4, 2), (2, 6), (6, 2), (4, 4)):
        doms_all = torus_dominoes(m, n)
        tested = p1 = p2 = 0; passing = []
        for doms in doms_all:
            for diags in itertools.product((0, 1), repeat=len(doms)):
                tiles = torus_plane(doms, diags, m, n)
                ev = evaluate(tiles, law, stop_at_first=True)
                tested += 1
                p1 += ev[1]["passes"]; p2 += ev[2]["passes"]
                if ev[1]["passes"] and len(passing) < 20:
                    passing.append({"dominoes": doms, "diagonals": list(diags), "passes_r2": ev[2]["passes"]})
        res["families"][f"domino tilings of the {m}x{n} torus"] = {"domino_tilings": len(doms_all), "tested": tested,
                                                                   "pass_r1": p1, "pass_r2": p2, "passing_examples": passing}
        print(m, n, len(doms_all), tested, p1, p2, round(time.time() - t0, 1), "s", flush=True)
    # F4: the six two-tile shapes, tiled by half-turns
    for name, (poly, pair) in two_tile_shapes().items():
        tiles = halfturn_plane(poly, pair, 120)
        ev = evaluate(tiles, law)
        res["families"][f"half-turn tiling of the {name}"] = {"tiling": is_tiling(tiles), "evaluation": ev}
        print(name, ev, flush=True)
    # F5: the frame-consistent cut (not periodic; four tile directions; not round, PINWHEEL-ROUND-20261107-001B)
    res["families"]["frame-consistent cut, level 5"] = {"evaluation": evaluate(frame_consistent_patch(5), law)}
    print("frame-consistent", res["families"]["frame-consistent cut, level 5"], flush=True)
    periodic_pass = {r: [k for k, v in res["families"].items() if k != "frame-consistent cut, level 5" and
                         (v.get("pass_r%d" % r, 0) > 0 or v.get("evaluation", {}).get(r, {}).get("passes"))] for r in (1, 2)}
    res["periodic_families_passing"] = periodic_pass
    res["controls_ok"] = (res["controls"]["pinwheel level-5 patch"][2]["passes"]
                          and not res["controls"]["isosceles right-triangle substitution, level 8"][1]["passes"])
    res["runtime_seconds"] = round(time.time() - t0, 1)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(res, indent=1) + "\n")
    print("periodic families passing:", periodic_pass, "controls ok:", res["controls_ok"], "runtime", res["runtime_seconds"])

if __name__ == "__main__":
    main()
