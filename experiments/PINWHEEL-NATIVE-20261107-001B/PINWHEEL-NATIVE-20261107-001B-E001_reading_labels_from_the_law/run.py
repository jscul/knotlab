"""PINWHEEL-NATIVE-20261107-001B-E001: can the rule read its labels from the law? (exploratory; see contract.json)

Builds the level-k pinwheel patch (exact integer coordinates, used only as the reference), its planar map (vertices, darts,
counterclockwise rotation order) and each interior dart's oriented label; tests 3-connectivity of the vertex graph with a vertex at
infinity, and whether the label is a function of the unlabelled rooted neighbourhood of radius r.
Writes artifacts/PINWHEEL-NATIVE-20261107-001B/PINWHEEL-NATIVE-20261107-001B-E001_reading_labels_from_the_law/run/result.json."""
from __future__ import annotations
import json, math, random, time
from collections import defaultdict, Counter
from fractions import Fraction as Fr
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "artifacts" / "PINWHEEL-NATIVE-20261107-001B" / "PINWHEEL-NATIVE-20261107-001B-E001_reading_labels_from_the_law" / "run"

def split(tile, m):
    O, P, Q = tile
    d = 1 + m * m
    H = (Q[0] + (P[0] - Q[0]) // d, Q[1] + (P[1] - Q[1]) // d)
    out = [(H, O, Q)]                       # small copy: right angle at H, long leg to O, short leg to Q
    ex = ((P[0] - H[0]) // m, (P[1] - H[1]) // m)
    ey = ((O[0] - H[0]) // m, (O[1] - H[1]) // m)
    V = lambda i, j: (H[0] + i * ex[0] + j * ey[0], H[1] + i * ex[1] + j * ey[1])
    for i in range(m):
        for j in range(m - i):
            out.append((V(i, j), V(i + 1, j), V(i, j + 1)))
            if i + j <= m - 2:
                out.append((V(i + 1, j + 1), V(i, j + 1), V(i + 1, j)))
    return out

def split_pinwheel(tile):
    """Conway's pinwheel decomposition (legs 1:2): drop the altitude from the right angle; cut the larger piece along its median
    to the midpoint M of the long leg, and each of the two isosceles halves along its axis. Four copies meet at M; the two
    halves give mirror-image pairs. Needs coordinates divisible by 10."""
    O, P, Q = tile
    H = (Q[0] + (P[0] - Q[0]) // 5, Q[1] + (P[1] - Q[1]) // 5)
    M = ((O[0] + P[0]) // 2, (O[1] + P[1]) // 2)
    F1 = ((O[0] + H[0]) // 2, (O[1] + H[1]) // 2)
    F2 = ((H[0] + P[0]) // 2, (H[1] + P[1]) // 2)
    return [(H, O, Q), (F1, M, O), (F1, M, H), (F2, H, M), (F2, P, M)]

def tiling_rule(rule, k):
    """rule in {'pinwheel', 'consistent', 'isosceles'}: the pinwheel (Conway's cut), the same five copies cut frame-consistently
    (altitude, then midpoints), or the isosceles right triangle halved by its altitude."""
    if rule == "pinwheel":
        D, top, f = 10, ((0, 0), (2, 0), (0, 1)), split_pinwheel
    elif rule == "consistent":
        D, top, f = 10, ((0, 0), (2, 0), (0, 1)), lambda t: split(t, 2)
    elif rule == "isosceles":
        D, top, f = 2, ((0, 0), (1, 0), (0, 1)), lambda t: split(t, 1)
    else:
        raise ValueError(rule)
    tiles = [top]
    for _ in range(k):
        tiles = [tuple((x * D, y * D) for x, y in t) for t in tiles]
        tiles = [s for t in tiles for s in f(t)]
    ratio = math.sqrt(5) if rule != "isosceles" else math.sqrt(2)
    scale = D ** k / ratio ** k
    return tiles, scale


def build(k):
    tiles, scale = tiling_rule("pinwheel", k)
    vid = {}
    for t in tiles:
        for p in t:
            vid.setdefault(p, len(vid))
    pts = list(vid)
    side_len = max(abs(t[1][0] - t[0][0]) + abs(t[1][1] - t[0][1]) for t in tiles[:50])
    cell = max(1, side_len)
    buckets = defaultdict(list)
    for p in pts:
        buckets[(p[0] // cell, p[1] // cell)].append(p)
    seg = defaultdict(list)     # frozenset(p1, p2) -> [(tile, side, lo, hi, start point)]
    for ti, (O, P, Q) in enumerate(tiles):
        for s, (A, B) in (("S", (O, Q)), ("L", (O, P)), ("H", (Q, P))):
            dx, dy = B[0] - A[0], B[1] - A[1]
            L2 = dx * dx + dy * dy
            on = {A: Fr(0), B: Fr(1)}
            for cx in range(min(A[0], B[0]) // cell, max(A[0], B[0]) // cell + 1):
                for cy in range(min(A[1], B[1]) // cell, max(A[1], B[1]) // cell + 1):
                    for p in buckets.get((cx, cy), ()):
                        if (p[0] - A[0]) * dy - (p[1] - A[1]) * dx != 0:
                            continue
                        sc = (p[0] - A[0]) * dx + (p[1] - A[1]) * dy
                        if 0 < sc < L2:
                            on[p] = Fr(sc, L2)
            sq = sorted(on.items(), key=lambda kv: kv[1])
            for (p1, l1), (p2, l2) in zip(sq, sq[1:]):
                seg[frozenset((p1, p2))].append((ti, s, l1, l2, p1))
    cent = [((O[0] + P[0] + Q[0]) / 3, (O[1] + P[1] + Q[1]) / 3) for O, P, Q in tiles]
    adj = defaultdict(set)
    for key in seg:
        a, b = tuple(key)
        adj[vid[a]].add(vid[b]); adj[vid[b]].add(vid[a])
    rot = {}
    for v, nb in adj.items():
        x, y = pts[v]
        rot[v] = sorted(nb, key=lambda w: math.atan2(pts[w][1] - y, pts[w][0] - x))
    # oriented label of each dart (u -> v): (left tile's (side, lo, hi), right tile's (side, lo, hi), aligned)
    dlab = {}
    for key, inc in seg.items():
        a, b = tuple(key)
        for u, v in ((a, b), (b, a)):
            left = right = None
            for ti, s, lo, hi, st in inc:
                cx, cy = cent[ti]
                cr = (v[0] - u[0]) * (cy - u[1]) - (v[1] - u[1]) * (cx - u[0])
                if cr > 0:
                    left = (s, lo, hi)
                else:
                    right = (s, lo, hi)
            aligned = (inc[0][4] == inc[1][4]) if len(inc) == 2 else None
            dlab[(vid[u], vid[v])] = (left, right, aligned)
    boundary = {vid[p] for key, inc in seg.items() if len(inc) == 1 for p in key}
    return {"pts": pts, "rot": rot, "dlab": dlab, "boundary": boundary, "tiles": tiles, "scale": scale}

def bfs_dist(rot, sources):
    from collections import deque
    d = {s: 0 for s in sources}; q = deque(sources)
    while q:
        u = q.popleft()
        for w in rot[u]:
            if w not in d:
                d[w] = d[u] + 1; q.append(w)
    return d

def code(rot, u, v, r):
    num = {u: 0}; order = [u]; entry = {u: v}; dist = {u: 0}
    out = []
    i = 0
    while i < len(order):
        x = order[i]; i += 1
        nb = rot[x]
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

def readability(M, r, labeller=None, margin_extra=1):
    db = bfs_dist(M["rot"], list(M["boundary"]))
    groups = defaultdict(set)
    n = 0
    for (u, v), lab in M["dlab"].items():
        if db.get(u, 0) <= r + margin_extra or db.get(v, 0) <= r + margin_extra:
            continue
        lab = labeller((u, v), lab) if labeller else lab
        groups[code(M["rot"], u, v, r)].add(lab)
        n += 1
    conflicts = sum(1 for s in groups.values() if len(s) > 1)
    return {"r": r, "darts": n, "codes": len(groups), "conflicting_codes": conflicts}


def incentre(M):
    pts = M["pts"]
    xs = [p[0] for p in pts]
    return (min(xs) + max(xs)) / 2

def connectivity(k):
    import networkx as nx
    M = build(k)
    G = nx.Graph()
    for u, nb in M["rot"].items():
        for w in nb:
            G.add_edge(u, w)
    for b in M["boundary"]:
        G.add_edge(-1, b)
    return {"level": k, "vertices": G.number_of_nodes(), "connectivity": nx.node_connectivity(G)}

def main():
    t0 = time.time()
    res = {"whitney": [], "readability": {}, "controls": {}}
    for k in (2, 3, 4, 5):
        t = time.time()
        row = connectivity(k); row["seconds"] = round(time.time() - t, 1)
        res["whitney"].append(row)
        print("whitney", row, flush=True)
    maps = {}
    for k in (5, 6, 7):
        maps[k] = build(k)
        res["readability"][str(k)] = []
        for r in range(1, 9):
            t = time.time()
            row = readability(maps[k], r)
            row["seconds"] = round(time.time() - t, 1)
            res["readability"][str(k)].append(row)
            print("level", k, row, flush=True)
    free = [r for r in range(1, 9) if all(res["readability"][str(k)][r - 1]["conflicting_codes"] == 0 for k in (5, 6, 7))]
    rstar = min(free) if free else None
    res["least_conflict_free_radius"] = rstar
    if rstar is not None:
        rng = random.Random(20261107)
        for k in (5, 6, 7):
            M = maps[k]
            db = bfs_dist(M["rot"], list(M["boundary"]))
            tested = [d for d in M["dlab"] if db.get(d[0], 0) > rstar + 1 and db.get(d[1], 0) > rstar + 1]
            labs = [M["dlab"][d] for d in tested]
            rng.shuffle(labs)
            perm = dict(zip(tested, labs))
            xc = incentre(M)
            a = readability(M, rstar, labeller=lambda d, lab: perm[d])
            b = readability(M, rstar, labeller=lambda d, lab: (M["pts"][d[0]][0] + M["pts"][d[1]][0]) / 2 < xc)
            res["controls"][str(k)] = {"permuted_labels": a, "side_of_vertical_line": b}
            print("controls", k, a["conflicting_codes"], b["conflicting_codes"], flush=True)
    res["runtime_seconds"] = round(time.time() - t0, 1)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(res, indent=1) + "\n")
    print("least conflict-free radius", rstar, "runtime", res["runtime_seconds"])

if __name__ == "__main__":
    main()
