#!/usr/bin/env python3
"""Checks for GROWN-DISTANCE-20261109-001A: the grown torus reads distance by freezing at every stage, and plainly only as a ladder.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
One process, a few minutes. Every verdict is exact: breadth-first route counts and the least odd walk length by the span of rows mod 2
(plain_lib.verdicts), and cell-level rows of M^T (distance_lib.first_need). Check 5 is a computation, not a theorem."""
import collections
import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import grown_lib as GL  # noqa: E402

P, G, LN, D = GL.P, GL.G, GL.LN, GL.D
T0 = time.time()
OUT = {}
DEPS = {
    "proofs/DISTANCE-20261108-001B/DISTANCE-20261108-001B-P001_distance_across_time_is_native_as_a_cone/manifest.json":
        "cfa8fa26d7df3f5e629fb573d241bac4589e378535bd24aee4d061df6406c45d",
    "proofs/PLAIN-TIME-20261108-001B/PLAIN-TIME-20261108-001B-P001_only_the_sphere_reads_distance_plainly/manifest.json":
        "603257295514c890d7114b2b0866127cb84b1efcee560a64d987b1173a173936",
    "experiments/PLAIN-TIME-20261108-001A/PLAIN-TIME-20261108-001A-E001_map_census/plain_lib.py":
        "bb6dc72ac1267b8139483d95bcbedddd9f55919481f27f8f8f6c040c605f3e30",
    "proofs/GROW-NET-20261108-001A/GROW-NET-20261108-001A-P001_bands_grow_single_rings_do_not/grow_lib.py":
        "7dcd377da641727744cb00956f40c88f5614ae2e4fd6908d5d790117d7be1f78",
    "proofs/BAND-SURFACE-20261108-001A/BAND-SURFACE-20261108-001A-P001_one_band_makes_the_torus/manifest.json":
        "e2631ce24057d884ac630262b921c82b9919c46b38a733fc8939c93038c1be2a",
}
R1 = {(2, 1), (-1, 2), (-2, -1), (1, -2)}
REGULAR = {"square": [4, 5, 5, 8, 9, 10, 10, 13, 17], "triangular": [3, 4, 7, 7, 9, 12, 13, 13, 16, 19, 21],
           "honeycomb": [1, 3, 4, 7, 7, 9]}
CENSUS_MAX = {"square": 100, "triangular": 80, "honeycomb": 50}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:400], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def stage(n, m):
    """a band stage: the loop of n rings (m = 1), the n x 2 ladder, or the n x m torus"""
    return LN.dihedron(n) if m == 1 else G.rect_torus(n, m)


# ---------- check 1: every stage reads both freeze lengths
def freeze_lengths():
    twins = []
    for n in range(3, 13):
        for m in range(1, 21):
            rot, edges = stage(n, m)
            sizes, contacts = LN.network(rot, edges, 2)
            out, inn, rc = D.graph(sizes, contacts)
            if D.parallel_arcs(out):
                twins.append((n, m))
    for n in range(2, 41):
        rot, edges = stage(n, 2)
        sizes, contacts = LN.network(rot, edges, 2)
        out, inn, rc = D.graph(sizes, contacts)
        if D.parallel_arcs(out):
            twins.append((n, 2))
    flights, bad = 0, []
    for n, m in ((3, 1), (3, 2), (4, 2), (5, 2), (3, 3), (4, 5), (5, 3), (6, 4)):
        for g in (2, 3):
            rot, edges = stage(n, m)
            sizes, contacts = LN.network(rot, edges, g)
            out, inn, rc = D.graph(sizes, contacts)
            nc = len(contacts)
            for c in (0, 1):
                for X in sorted(rc):
                    if c in rc[X]:
                        continue
                    dist = D.dist_from(out, rc[X], nc)
                    route = [c]
                    while dist[route[-1]] > 0:   # a fixed shortest route, traced back through the least predecessor
                        route.append(min(d for d, ring, l in inn[route[-1]] if dist[d] == dist[route[-1]] - 1))
                    route = route[::-1]
                    t = D.isolated_first_need(sizes, contacts, route, X, g * dist[c] + 1)
                    flights += 1
                    if t != g * dist[c] + 1:
                        bad.append((n, m, g, c, X, t))
    return twins, flights, bad


# ---------- check 2: the ladders
def ladder_forms():
    """the cover tables of Theorem 2 against breadth-first counts on the 60 x 2 ladder, ring lifts |i| <= 25"""
    n = 60
    rot, edges = G.rect_torus(n, 2)
    sizes, contacts = LN.network(rot, edges, 2)
    nc, out, rc = P.network_map(sizes, contacts)
    verts = sorted(rot, key=repr)
    role = {}
    for v in verts:
        for k, e in enumerate(rot[v]):
            role[(v, e)] = "ENWS"[k]
    bad, read = [], 0
    for target, t in (("h", 0), ("v", 1)):
        dist, cnt = GL.routes_to(out, nc, t)
        for i in range(-25, 26):
            for level in (0, 1):
                form = GL.ladder_cover_forms(target, i, level)
                v = (i % n, level)
                es = rot[v]
                if form is None:
                    if t not in es:
                        bad.append((target, i, level, "should hold the target"))
                    continue
                dr = min(dist[e] for e in es)
                at = [e for e in es if dist[e] == dr]
                read += 1
                if (dr, role[(v, at[0])]) != form or len(at) != 1 or cnt[at[0]] != 1:
                    bad.append((target, i, level, dr, [role[(v, e)] for e in at], [cnt[e] for e in at], form))
    return read, bad


def ladders():
    bad, read = [], 0
    for a in range(2, 201):
        for t in (0, 1):
            T = GL.torus("square", ((a, t), (0, 2)))
            ok, v = GL.on_time(*T, "square")
            read += 1
            if not ok:
                bad.append((a, t))
    cells, late = 0, []
    for n in range(2, 13):
        for g in (2, 3):
            rot, edges = G.rect_torus(n, 2)
            sizes, contacts = LN.network(rot, edges, g)
            out, inn, rc = D.graph(sizes, contacts)
            nc = len(contacts)
            for c in range(nc):
                for X in sorted(rc):
                    if c in rc[X]:
                        continue
                    d = D.dist_from(out, rc[X], nc)[c]
                    cells += 1
                    if D.first_need(sizes, contacts, c, X, g * d + 1) != g * d + 1:
                        late.append((n, g, c, X))
    return read, bad, cells, late


# ---------- check 3: the thick stages
def thick():
    cyl = {n: GL.cylinder_first_late(n, 40) for n in (3, 4, 5)}
    small = {}
    for n in range(3, 6):
        for m in range(n, 6):
            rot, edges = G.rect_torus(n, m)
            small["%dx%d" % (n, m)] = GL.on_time(rot, edges, "square")[0]
    wide = []
    for n in range(2, 11):
        for m in range(n, 41):
            rot, edges = G.rect_torus(n, m)
            if GL.on_time(rot, edges, "square")[0]:
                wide.append((n, m))
    cell = {}
    for n, m in ((3, 4), (4, 6), (5, 7), (3, 9)):
        rot, edges = G.rect_torus(n, m)
        sizes, contacts = LN.network(rot, edges, 2)
        out, inn, rc = D.graph(sizes, contacts)
        nc = len(contacts)
        late = 0
        for c in (0, 1):
            for X in sorted(rc):
                if c not in rc[X]:
                    d = D.dist_from(out, rc[X], nc)[c]
                    late += D.first_need(sizes, contacts, c, X, 2 * d + 1) != 2 * d + 1
        cell["%dx%d" % (n, m)] = late
    return cyl, small, wide, cell


# ---------- check 4: balls
def balls():
    bad = []
    for n in range(2, 11):
        for m in range(2, 15):
            R = n // 2 + m // 2 + 1
            if GL.ring_ball_sizes(n, m, R) != GL.ring_ball_bfs(n, m, R):
                bad.append(("torus", n, m))
    for n in range(2, 11):
        R = 14
        if GL.ring_ball_sizes(n, None, R) != GL.ring_ball_bfs(n, 2 * R + 3, R):
            bad.append(("cylinder", n))
    slopes = {}
    for n in range(2, 11):
        s = GL.ring_ball_sizes(n, None, 3 * n)
        steps = [s[r + 1] - s[r] for r in range(3 * n)]
        if steps != [min(n, 2 * r + 1) + min(n, 2 * r + 3) for r in range(3 * n)]:
            bad.append(("steps", n, steps))
        slopes[n] = sorted(set(steps[r] for r in range(3 * n) if 2 * r + 1 >= n))
        if slopes[n] != [2 * n]:
            bad.append(("slope", n, slopes[n]))
        head = [s[r] for r in range(0, (n - 1) // 2 + 1)]
        if head != [2 * r * r + 2 * r + 1 for r in range(0, (n - 1) // 2 + 1)]:
            bad.append(("head", n, head))
    # the time ball at even radius 2r is the ball of ring distance r about the target's two rings (D = ceil(delta / 2))
    tb = 0
    for n in range(2, 9):
        for m in range(2, 12):
            rot, edges = G.rect_torus(n, m)
            nb = collections.defaultdict(set)
            for u, v in edges:
                nb[u].add(v)
                nb[v].add(u)
            for t in (0, 1):
                rings = edges[t]
                dist = {r: 0 for r in rings}
                q = collections.deque(rings)
                while q:
                    a = q.popleft()
                    for b in nb[a]:
                        if b not in dist:
                            dist[b] = dist[a] + 1
                            q.append(b)
                R = n // 2 + m // 2 + 1
                two = [sum(1 for d in dist.values() if d <= r) for r in range(R + 1)]
                tball = GL.time_ball_sizes(n, m, t, 2 * R)
                tb += 1
                if [tball[2 * r] for r in range(R + 1)] != two:
                    bad.append(("time ball", n, m, t))
    return slopes, tb, bad


# ---------- check 5: every torus of the three lattices (computed)
ROTATE = {"square": lambda v: (-v[1], v[0]), "triangular": lambda v: (v[0] - v[1], v[0]), "honeycomb": lambda v: (-v[0] - v[1], v[0])}


def rotation_invariant(kind, B):
    """the sublattice is invariant under the rotation plain_lib.lattice_torus uses (PLAIN-TIME-20261108-001B's regular tori)"""
    red = lambda v: P.reduce_mod(v, B)
    return all(red(ROTATE[kind](row)) == (0, 0) for row in B)


def census():
    out = {}
    for kind, imax in CENSUS_MAX.items():
        cls = collections.defaultdict(lambda: [0, 0])
        on_list, regular = [], []
        for B in GL.hermite_bases(imax, 1 if kind == "honeycomb" else 3):
            T = GL.torus(kind, B)
            if T is None:
                continue
            ok, v = GL.on_time(*T, kind)
            n2, s = GL.shortest(kind, B)
            key = str(n2)
            if kind == "square" and n2 == 5:
                key = "5 R1" if (s in R1) else "5 R2"
            cls[key][1] += 1
            if ok:
                cls[key][0] += 1
                on_list.append((key, B[0][0] * B[1][1], B))
                if rotation_invariant(kind, B):
                    regular.append(B[0][0] * B[1][1])
        out[kind] = {"classes": {k: v for k, v in sorted(cls.items())}, "regular on time": sorted(regular),
                     "on time outside the families": sorted((idx, key, B) for key, idx, B in on_list
                                                            if not ((kind == "square" and key in ("4", "5 R1"))
                                                                    or (kind == "triangular" and key == "3")))}
    return out


def cells_families():
    res = {}
    for name, kind, B in (("square twisted ladder (0,2), (21,1)", "square", ((21, 1), (0, 2))),
                          ("square (2,1) tube, index 41", "square", ((41, 0), (2, 1))),
                          ("triangular sqrt 3 tube, index 40", "triangular", ((40, 0), (2, 1)))):
        rot, edges = GL.torus(kind, B)
        sizes, contacts = LN.network(rot, edges, 2)
        out, inn, rc = D.graph(sizes, contacts)
        nc = len(contacts)
        late = pairs = 0
        for c in GL.targets(kind):
            for X in sorted(rc):
                if c in rc[X]:
                    continue
                d = D.dist_from(out, rc[X], nc)[c]
                pairs += 1
                late += D.first_need(sizes, contacts, c, X, 2 * d + 1) != 2 * d + 1
        res[name] = (pairs, late)
    return res


def main():
    deps = {p: sha(p) for p in DEPS}
    check("0 dependencies bound by hash", all(DEPS[p] == deps[p] for p in DEPS), deps)
    twins, flights, bad = freeze_lengths()
    check("1 Theorem 1: no twin corners at any stage (loops 3-12, ladders 2-40, tori to 12 x 20); isolated shortest routes arrive at "
          "g delta + 1 at the cell level", not twins and not bad, {"twins": twins, "flights read": flights, "bad": bad})
    read, badf = ladder_forms()
    check("2a Theorem 2: the ladder cover's tables (least distance, its unique contact, one route) for both targets", not badf,
          {"ring lifts read": read, "bad": badf[:5]})
    read, bad, cells, late = ladders()
    check("2b Theorem 2: every square torus holding (0, 2), twisted or not, n = 2 to 200, on time; n x 2 at the cell level, g = 2, 3",
          not bad and not late, {"tori": read, "late": bad, "cell pairs": cells, "cell late": late})
    cyl, small, wide, cell = thick()
    check("3 Theorem 3: cylinders of width 3, 4, 5 late at 4; the n x m tori with 3 <= n <= m <= 5 late but 3 x 3; computed to "
          "10 x 40: on time only n = 2 and 3 x 3",
          all(min(x for x in c.values() if x is not None) == 4 for c in cyl.values())
          and small == {k: k == "3x3" for k in small}
          and wide == [(2, m) for m in range(2, 41)] + [(3, 3)]
          and all(v > 0 for v in cell.values()),
          {"cylinders": cyl, "small": small, "on time": wide, "cell-level late pairs": cell})
    slopes, tb, badb = balls()
    check("4 Theorem 4: ring balls in closed form (tori to 10 x 14, cylinders); 2r^2 + 2r + 1 below radius n/2, steps f(r) + f(r + 1), "
          "2n once 2r + 1 >= n; "
          "time balls at radius 2r = ring balls of radius r about the target's rings", not badb,
          {"cylinder slopes": slopes, "time balls compared": tb, "bad": badb})
    cen = census()
    sq, tri, hc = cen["square"]["classes"], cen["triangular"]["classes"], cen["honeycomb"]["classes"]
    ok = (sq["4"][0] == sq["4"][1] and sq["5 R1"][0] == sq["5 R1"][1] and tri["3"][0] == tri["3"][1]
          and all(idx <= 21 for idx, key, B in cen["square"]["on time outside the families"] + cen["triangular"]["on time outside the families"])
          and all(idx <= 9 for idx, key, B in cen["honeycomb"]["on time outside the families"])
          and all(cen[k]["regular on time"] == REGULAR[k] for k in cen))
    check("5 Computed: every torus of the square (index <= 100), triangular (<= 80) and honeycomb (<= 50) lattices; the ladders, the "
          "square (2, 1) tubes of one chirality and the triangular sqrt 3 tubes all on time, every other on-time torus of small index",
          ok, {k: {"classes": cen[k]["classes"], "others": len(cen[k]["on time outside the families"]),
                   "regular": cen[k]["regular on time"]} for k in cen})
    OUT["5 census detail"] = cen
    fam = cells_families()
    check("6 The computed families at the cell level, g = 2", all(v[1] == 0 for v in fam.values()), fam)
    result = {"ticket": "GROWN-DISTANCE-20261109-001A", "artifact_id": "GROWN-DISTANCE-20261109-001A-P001", "checks": OUT, "status": "passed"}
    path = HERE / "result.json"
    if "--write" in sys.argv:
        path.write_text(json.dumps(result, indent=1, default=str) + "\n")
    else:
        old = json.loads(path.read_text())
        same = json.dumps(old["checks"], sort_keys=True, default=str) == json.dumps(json.loads(json.dumps(OUT, default=str)), sort_keys=True)
        print("result.json matches" if same else "result.json differs")
        return 0 if same else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
