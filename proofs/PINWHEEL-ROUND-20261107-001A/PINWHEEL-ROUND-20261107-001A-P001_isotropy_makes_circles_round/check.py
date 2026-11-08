"""Checker for PINWHEEL-ROUND-20261107-001A-P001 (isotropy makes logical circles round: the pinwheel law).

Finite validation of proof.md. It does not prove the cited theorems (Radin's unique ergodicity and rotational symmetry of the
pinwheel space); it checks the substitutions, the frame mechanism, the 1:1 pattern, the vertex-cycle lemma and the bounds used in
the proof. Writes result.json next to this file. Run: python3 -B check.py   (needs numpy)"""
from __future__ import annotations
import json, math, random, sys, time
from collections import Counter, defaultdict
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import sub_lib as sl

TOPS = {"pinwheel": ((0, 0), (2, 0), (0, 1)), "consistent": ((0, 0), (2, 0), (0, 1)), "isosceles": ((0, 0), (1, 0), (0, 1))}

def exact_ok(tiles, m):
    """Every tile is a right triangle with legs in ratio m:1 (integer arithmetic)."""
    for O, P, Q in tiles:
        a = (P[0] - O[0], P[1] - O[1]); b = (Q[0] - O[0], Q[1] - O[1])
        if a[0] * b[0] + a[1] * b[1] != 0 or a[0] ** 2 + a[1] ** 2 != m * m * (b[0] ** 2 + b[1] ** 2):
            return False
    return True

def area2(t):
    (ox, oy), (px, py), (qx, qy) = t
    return abs((px - ox) * (qy - oy) - (py - oy) * (qx - ox))

def check_substitutions():
    rows, ok = [], True
    for rule, m, levels in (("pinwheel", 2, range(1, 7)), ("consistent", 2, range(1, 7)), ("isosceles", 1, range(2, 15, 2))):
        for k in levels:
            tiles, _ = sl.tiling_rule(rule, k)
            D = (10 if rule != "isosceles" else 2) ** k
            top = [(x * D, y * D) for x, y in TOPS[rule]]
            covers = sum(area2(t) for t in tiles) == area2(top)
            good = exact_ok(tiles, m) and covers and len(set(tiles)) == len(tiles)
            ok &= good
        rows.append({"rule": rule, "levels": [levels.start, levels.stop - 1], "congruent_and_cover_area": bool(good)})
    return ok, rows

def check_orientations():
    counts = {}
    for rule, levels in (("pinwheel", range(1, 8)), ("consistent", range(1, 8)), ("isosceles", range(2, 15, 2))):
        counts[rule] = {k: sl.orientation_count(sl.tiling_rule(rule, k)[0]) for k in levels}
    pin = counts["pinwheel"]
    ok = all(pin[k] == 4 * k for k in range(2, 8)) and pin[1] == 3
    ok &= all(v == 4 for k, v in counts["consistent"].items() if k >= 2)
    ok &= all(v == 4 for k, v in counts["isosceles"].items() if k >= 4)
    return ok, {r: {str(k): v for k, v in c.items()} for r, c in counts.items()}

def check_handedness():
    top = tuple((x * 10, y * 10) for x, y in TOPS["pinwheel"])
    pin = Counter(sl.handedness(t) for t in sl.split_pinwheel(top))
    con = Counter(sl.handedness(t) for t in sl.split(top, 2))
    parent = sl.handedness(top)
    ok = pin[parent] == 2 and pin[-parent] == 3 and con[-parent] == 5
    return ok, {"parent": parent, "pinwheel_children": dict(pin), "consistent_children": dict(con)}

def isosceles_pattern_ok(tiles, k, flip=False):
    """At even level k = 2j: every tile is half of a grid square of side D^k / 2^j, and the square (a, b) is cut by its NE diagonal
    exactly when a + b is even (the checkerboard-diagonal, tetrakis, triangulation)."""
    j = k // 2
    side = 2 ** k // 2 ** j
    for O, P, Q in tiles:
        xs = [O[0], P[0], Q[0]]; ys = [O[1], P[1], Q[1]]
        a, b = min(xs) // side, min(ys) // side
        if max(xs) - min(xs) != side or max(ys) - min(ys) != side:
            return False
        # hypotenuse P-Q: NE if it joins (a, b) and (a+1, b+1)
        ne = {P, Q} == {(a * side, b * side), ((a + 1) * side, (b + 1) * side)}
        nw = {P, Q} == {((a + 1) * side, b * side), (a * side, (b + 1) * side)}
        if not (ne or nw):
            return False
        want_ne = ((a + b) % 2 == 0) != flip
        if ne != want_ne:
            return False
    return True

def check_isosceles():
    res = {k: isosceles_pattern_ok(sl.tiling_rule("isosceles", k)[0], k) for k in range(2, 15, 2)}
    return all(res.values()), {str(k): v for k, v in res.items()}

def vertex_cycles_ok(G, skip_tile=None):
    """Around every interior vertex the tiles meeting it form a cycle of the tile adjacency graph through exactly the dual edges of
    the segments at that vertex (so any two segments at a vertex lie on a common bond of size deg(v))."""
    at = defaultdict(list)
    for k, (a, b) in enumerate(G["segs"]):
        at[a].append(k); at[b].append(k)
    checked = bad = 0
    maxdeg = 0
    for v, ks in at.items():
        tiles_of = [G["seg_tiles"][k] for k in ks]
        if any(len(ts) != 2 for ts in tiles_of):
            continue                      # boundary vertex
        if skip_tile is not None and any(skip_tile in ts for ts in tiles_of):
            tiles_of = [[t for t in ts if t != skip_tile] for ts in tiles_of]
        checked += 1
        maxdeg = max(maxdeg, len(ks))
        deg = Counter(t for ts in tiles_of for t in ts)
        nodes = set(deg)
        if any(len(ts) != 2 for ts in tiles_of) or any(d != 2 for d in deg.values()) or len(nodes) != len(ks):
            bad += 1; continue
        # connected?
        adj = defaultdict(list)
        for x, y in tiles_of:
            adj[x].append(y); adj[y].append(x)
        start = next(iter(nodes)); seen = {start}; stack = [start]
        while stack:
            u = stack.pop()
            for w in adj[u]:
                if w not in seen:
                    seen.add(w); stack.append(w)
        if seen != nodes:
            bad += 1
    return bad == 0 and checked > 0, {"interior_vertices": checked, "failures": bad, "max_degree": maxdeg}

def incenter(top):
    (ax, ay), (bx, by), (cx, cy) = top
    a = math.dist((bx, by), (cx, cy)); b = math.dist((ax, ay), (cx, cy)); c = math.dist((ax, ay), (bx, by))
    s = a + b + c
    return ((a * ax + b * bx + c * cx) / s, (a * ay + b * by + c * cy) / s)

def check_bounds(rnd):
    """Corner law of the pinwheel at level 6: on sampled pairs, 2 d + 1 <= delta <= (Delta - 1)(h + 1), where d is the distance
    in the tile adjacency graph between the tiles of the two segments and h the number of segments on a shortest vertex path
    between them (the vertex-cycle lemma and the triangle inequality)."""
    tiles, scale = sl.tiling_rule("pinwheel", 6)
    G = sl.build_graph(tiles)
    L = sl.laws(G)
    tadj, telist, seg_of = L["corner"]
    vadj, _, _ = L["tile"]
    maxdeg = max(len(a) for a in vadj)
    coords = np.array(G["coords"], dtype=float) / scale
    D = 10 ** 6
    c = np.array(incenter([(x * D, y * D) for x, y in TOPS["pinwheel"]])) / scale
    segs = G["segs"]
    emid = np.array([(coords[a] + coords[b]) / 2 for a, b in (segs[s] for s in seg_of)])
    e0 = int(np.argmin(np.linalg.norm(emid - c, axis=1)))
    cand = [j for j in range(len(telist)) if np.linalg.norm(emid[j] - emid[e0]) < 25 and len(set(telist[j]) | set(telist[e0])) == 4]
    from collections import deque
    def bfs(adj, srcs):
        dist = [-1] * len(adj); q = deque()
        for s in srcs:
            dist[s] = 0; q.append(s)
        while q:
            u = q.popleft()
            for w, _ in adj[u]:
                if dist[w] < 0:
                    dist[w] = dist[u] + 1; q.append(w)
        return dist
    dt = bfs(tadj, list(telist[e0]))
    a0, b0 = segs[seg_of[e0]]
    dv = bfs(vadj, [a0, b0])
    ok, worst_low, worst_high = True, 0, 0
    for j in rnd.sample(cand, 40):
        cyc = sl.min_cycle_through(tadj, telist, e0, j)
        delta = cyc - 1
        lo = 2 * min(dt[t] for t in telist[j]) + 1
        a, b = segs[seg_of[j]]
        h = min(dv[a], dv[b]) + 1
        hi = (maxdeg - 1) * (h + 1)
        ok &= lo <= delta <= hi
        worst_low = min(worst_low, delta - lo) if worst_low else delta - lo
        worst_high = max(worst_high, delta - hi)
    return ok, {"pairs": 40, "max_degree": maxdeg, "min_delta_minus_lower": worst_low, "max_delta_minus_upper": worst_high}

def check_ball_orientations():
    """Orientations met by the tiles within radius R of the incentre, level 7: grows like log R; the consistent cut stays at 4."""
    out = {}
    for rule in ("pinwheel", "consistent"):
        tiles, scale = sl.tiling_rule(rule, 7)
        D = 10 ** 7
        c = np.array(incenter([(x * D, y * D) for x, y in TOPS[rule]])) / scale
        cent = np.array([((O[0] + P[0] + Q[0]) / 3, (O[1] + P[1] + Q[1]) / 3) for O, P, Q in tiles]) / scale
        ang = np.array([round(math.atan2(P[1] - O[1], P[0] - O[0]) % (2 * math.pi), 9) for O, P, Q in tiles])
        d = np.linalg.norm(cent - c, axis=1)
        out[rule] = {str(R): int(len(set(ang[d <= R].tolist()))) for R in (2, 4, 8, 16, 32, 64, 100)}
    pin = [out["pinwheel"][str(R)] for R in (2, 4, 8, 16, 32, 64, 100)]
    grows = all(x <= y for x, y in zip(pin, pin[1:])) and pin[-1] > pin[0]
    logbound = all(n <= 4 * (math.log(R, math.sqrt(5)) + 4) for n, R in zip(pin, (2, 4, 8, 16, 32, 64, 100)))
    ok = grows and logbound and all(v <= 4 for v in out["consistent"].values())
    return ok, out

# ---------------------------------------------------------------- controls (each must be rejected)

def control_consistent_has_no_growth():
    c = {k: sl.orientation_count(sl.tiling_rule("consistent", k)[0]) for k in range(2, 7)}
    return all(c[k] != 4 * k for k in range(3, 7)), c

def control_mutated_pinwheel():
    """Replace one mirror copy by its unmirrored labelling: the five pieces no longer form congruent 1:2 right triangles."""
    orig = sl.split_pinwheel
    def bad(tile):
        out = orig(tile)
        F1, M, H = out[2]
        out[2] = (F1, H, M)
        return out
    sl.split_pinwheel = bad
    try:
        tiles, _ = sl.tiling_rule("pinwheel", 3)
        ok = exact_ok(tiles, 2)
    finally:
        sl.split_pinwheel = orig
    return not ok, ok

def control_isosceles_parity():
    return not isosceles_pattern_ok(sl.tiling_rule("isosceles", 8)[0], 8, flip=True), "parity flipped"

def control_missing_tile():
    tiles, _ = sl.tiling_rule("pinwheel", 4)
    G = sl.build_graph(tiles)
    ok, info = vertex_cycles_ok(G, skip_tile=len(tiles) // 2)
    return not ok, info

def main():
    t0 = time.time()
    rnd = random.Random(20261107)
    res = {}
    checks = {}
    checks["substitutions"], res["substitutions"] = check_substitutions()
    checks["orientations_per_level"], res["orientations_per_level"] = check_orientations()
    checks["handedness"], res["handedness"] = check_handedness()
    checks["isosceles_is_tetrakis"], res["isosceles_is_tetrakis"] = check_isosceles()
    tiles, _ = sl.tiling_rule("pinwheel", 5)
    checks["vertex_cycle_lemma"], res["vertex_cycle_lemma"] = vertex_cycles_ok(sl.build_graph(tiles))
    checks["bond_distance_bounds"], res["bond_distance_bounds"] = check_bounds(rnd)
    checks["orientations_in_balls"], res["orientations_in_balls"] = check_ball_orientations()
    checks = {k: bool(v) for k, v in checks.items()}
    controls = {}
    for name, fn in (("consistent_cut_has_no_orientation_growth", control_consistent_has_no_growth),
                     ("mutated_pinwheel_cut", control_mutated_pinwheel), ("isosceles_parity_flipped", control_isosceles_parity),
                     ("vertex_cycles_with_a_missing_tile", control_missing_tile)):
        rejected, info = fn()
        controls[name] = {"rejected": bool(rejected), "detail": info}
    res["controls"] = controls
    res["theorem_flags"] = {"isotropy_principle": "argued-in-prose (Theorem 1)",
                            "pinwheel_round": "argued-in-prose (Corollary 2), conditional on Radin's cited theorems",
                            "isosceles_periodic": "argued-in-prose (Proposition 3) and checked at levels 2-14",
                            "log_orientations": "argued-in-prose (Proposition 4) and checked in balls up to radius 100"}
    res["runtime_seconds"] = round(time.time() - t0, 1)
    manifest = json.loads((HERE / "manifest.json").read_text())
    failures = [k for k, v in checks.items() if not v] + [f"control {k} not rejected" for k, v in controls.items() if not v["rejected"]]
    out = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
           "proof": manifest["proof"], "status": "passed" if not failures else "failed", "claim": manifest["claim"],
           "checks": checks, "failures": failures, "details": res}
    (HERE / "result.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    print(json.dumps({"checks": checks, "controls": {k: v["rejected"] for k, v in controls.items()}, "runtime": res["runtime_seconds"]}, indent=1))
    return 0 if not failures else 1

if __name__ == "__main__":
    sys.exit(main())
