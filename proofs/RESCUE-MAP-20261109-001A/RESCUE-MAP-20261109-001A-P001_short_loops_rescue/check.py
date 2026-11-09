"""Checks for RESCUE-MAP-20261109-001A. Distances and route parities are exact: breadth-first search layer by layer, tube certificates
checked at every contact of a window and one period past it. The census (check 6) reads every lattice up to the index bounds of
Theorem 3 exactly.

    python3 -B check.py          verify against result.json
    python3 -B check.py --write  write result.json from a fresh run
"""
import hashlib
import json
import math
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "experiments/PLAIN-TIME-20261108-001A/PLAIN-TIME-20261108-001A-E001_map_census"))
import rescue_lib as R  # noqa: E402
import tube_cert as C  # noqa: E402
import plain_lib as PL  # noqa: E402

OUT = {}
T0 = time.time()
FAMILY = {"square": [(2, 0), (0, 2), (2, 1), (-1, 2)], "triangular": [(1, -1), (2, 1), (1, 2)], "honeycomb": []}
THETA = {"square": 12, "triangular": 18, "honeycomb": 13}           # 2 ell + m
BOUND = {"square": 50, "triangular": 93, "honeycomb": 48}           # Theorem 3's index bounds
TUBES = [("square", (2, 1)), ("triangular", (1, -1))]


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print(("PASS " if ok else "FAIL ") + name, "(%.0fs)" % (time.time() - T0), flush=True)
    if not ok:
        print(json.dumps(info, indent=1, default=str)[:3000])


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def hnf_lattices(N):
    for p in range(1, N + 1):
        if N % p == 0:
            for q in range(p):
                yield ((p, 0), (q, N // p))


def contains(B, v):
    (a, b), (c, d) = B
    det = a * d - b * c
    x, y = v
    return (x * d - y * c) % det == 0 and (y * a - x * b) % det == 0


def beta(kind, v):
    """the lower bound on the undirected arcs between a contact and its translate by v (check 2)"""
    a, b = v
    if kind == "square":
        return 2 * max(abs(a), abs(b))
    if kind == "triangular":
        return 2 * math.sqrt(a * a - a * b + b * b)
    return 2 * math.sqrt(a * a + a * b + b * b)


# ---------- tori, read by rescue_lib
def torus_points(Q, det):
    pts = {Q.red((i, j)) for i in range(-2 * det, 2 * det + 1) for j in range(-2 * det, 2 * det + 1)}
    assert len(pts) == det
    return pts


def on_time(args):
    """None if a contact joins a ring to itself, else whether every ring is on time for every contact it does not hold"""
    kind, B = args
    Q = R.Quotient(B)
    det = abs(B[0][0] * B[1][1] - B[0][1] * B[1][0])
    pts = torus_points(Q, det)
    if kind != "honeycomb":
        for p in pts:
            for d in R.DIRS[kind][:len(R.DIRS[kind]) // 2]:
                if Q.red(R.add(p, d)) == p:
                    return kind, B, None
    rad = 10 * det + 20
    for t in range(R.TYPES[kind]):
        dist, cnt = R.bfs_counts(kind, Q, (t, (0, 0)), rad)
        tg = (t, Q.red((0, 0)))
        for p in pts:
            for rk in R.rings_of(kind):
                sl = [(c[0], Q.red(c[1])) for c in R.slots(kind, rk, p)]
                if tg in sl:
                    continue
                v = R.ring_verdict(kind, Q, dist, cnt, rk, p, rad)
                if v is None or not v[2]:
                    return kind, B, False
    return kind, B, True


# ---------- the same tori through loopnet_lib (PLAIN-TIME-20261108-001A's plain_lib)
def lib_torus(kind, B):
    det = B[0][0] * B[1][1] - B[0][1] * B[1][0]
    red = lambda v: PL.reduce_mod(v, B)
    pts = sorted({red((i, j)) for i in range(-2 * det, 2 * det + 1) for j in range(-2 * det, 2 * det + 1)})
    if kind != "honeycomb":
        dirs = R.DIRS[kind]
        edges, eid = [], {}
        for v in pts:
            for d in dirs[:len(dirs) // 2]:
                w = red((v[0] + d[0], v[1] + d[1]))
                if w == v:
                    return None
                eid[(v, d)] = eid[(w, (-d[0], -d[1]))] = len(edges)
                edges.append((v, w))
        return {v: [eid[(v, d)] for d in dirs] for v in pts}, edges
    verts = [(p, s) for p in pts for s in (0, 1)]
    edges, rot = [], {v: [None] * 3 for v in verts}
    for p in pts:
        for k, q in enumerate((p, red((p[0] - 1, p[1])), red((p[0], p[1] - 1)))):
            rot[(p, 0)][k] = rot[(q, 1)][k] = len(edges)
            edges.append(((p, 0), (q, 1)))
    return rot, edges


def lib_on_time(args):
    kind, B = args
    t = lib_torus(kind, B)
    if t is None:
        return kind, B, None
    rot, edges = t
    sizes, contacts = PL.LN.network(rot, edges, 2)
    n, out, rc = PL.network_map(sizes, contacts)
    lst = rot[min(rot)]
    types = sorted(set(lst[:len(lst) // 2] if kind != "honeycomb" else lst))
    for tgt in types:
        v = PL.verdicts(n, out, rc, tgt)
        if v["rings late"] or v["rings never"]:
            return kind, B, False
    return kind, B, True


# ---------- check 2: what one arc moves
def arc_moves(kind):
    """the largest |du| + |dw| (square) or Euclidean displacement (others) of a contact's midpoint along one arc"""
    if kind == "square":
        mid = lambda c: (c[1][0] + (0.5 if c[0] == 0 else 0), c[1][1] + (0.5 if c[0] == 1 else 0))
        f = lambda a, b: abs((b[0] + b[1]) - (a[0] + a[1])) + abs((b[1] - b[0]) - (a[1] - a[0]))
    elif kind == "triangular":
        e = [(1, 0), (0.5, math.sqrt(3) / 2), (-0.5, math.sqrt(3) / 2)]   # (1,0), (1,1), (0,1) at 0, 60 and 120 degrees
        coord = lambda p: (p[0] * 1 + p[1] * -0.5, p[1] * math.sqrt(3) / 2)
        mid = lambda c: tuple(coord(c[1])[i] + e[c[0]][i] / 2 for i in range(2))
        f = lambda a, b: math.dist(a, b)
    else:
        s3 = math.sqrt(3)
        coord = lambda p: (s3 * (p[0] + p[1] * 0.5), s3 * p[1] * s3 / 2)   # A lattice, spacing sqrt 3, e1 and e2 at 60 degrees
        bpos = lambda p: (coord(p)[0] + s3 / 2, coord(p)[1] + 0.5)        # B(p) at the centre of A(p), A(p + e1), A(p + e2)
        def mid(c):
            t, p = c
            q = (p, (p[0] - 1, p[1]), (p[0], p[1] - 1))[t]
            a, b = coord(p), bpos(q)
            return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
        f = lambda a, b: math.dist(a, b)
    worst, lengths = 0, set()
    for t in range(R.TYPES[kind]):
        for p in [(i, j) for i in range(-2, 3) for j in range(-2, 3)]:
            for y in R.out_arcs(kind, (t, p)):
                x = f(mid((t, p)), mid(y))
                worst = max(worst, x)
                lengths.add(round(x, 9))
    return worst, sorted(lengths)


# ---------- check 5: late tubes
def tube_witness(args):
    kind, v = args
    Q = R.Quotient([v])
    if kind != "honeycomb" and any(Q.red(d) == Q.red((0, 0)) for d in R.DIRS[kind]):
        return kind, v, "joins a ring to itself"
    m = R.RING_SIZE[kind]
    rad = 3 * R.ELL[kind] + 3 * m
    best = None
    for t in range(R.TYPES[kind]):
        dist, cnt = R.bfs_counts(kind, Q, (t, (0, 0)), rad)
        tg = (t, Q.red((0, 0)))
        seen = set()
        for (tt, p), d in dist.items():
            if d > R.ELL[kind] + m:
                continue
            for rk, q, s in R.contact_rings(kind, (tt, p)):
                key = (rk, Q.red(q))
                if key in seen:
                    continue
                seen.add(key)
                sl = [(c[0], Q.red(c[1])) for c in R.slots(kind, rk, q)]
                if tg in sl:
                    continue
                vv = R.ring_verdict(kind, Q, dist, cnt, rk, q, rad)
                if vv and not vv[2] and vv[0] <= R.ELL[kind] and (best is None or vv[0] < best[0]):
                    best = (vv[0], t, rk, list(Q.red(q)))
    return kind, v, best


def short_vectors(kind):
    out = []
    for a in range(0, 12):
        for b in range(-12, 12):
            if (a == 0 and b <= 0) or beta(kind, (a, b)) >= THETA[kind]:
                continue
            out.append((a, b))
    return out


def is_family(kind, v):
    return tuple(v) in FAMILY[kind] or (-v[0], -v[1]) in FAMILY[kind]


# ---------- check 7: exact route counts at the closest contacts of the two tubes
def exact_closest(args):
    kind, v, t0, W = args
    tube = C.Tube(kind, v)
    dist, cnt = R.bfs_counts(kind, tube.Q, (t0, (0, 0)), 3 * W, modulus=10 ** 12)
    val = {}
    for (t, p), d in dist.items():
        val[(t, tube.pos(p))] = (d, cnt[(t, p)])
    counts = set()
    for j in range(-W, W + 1):
        for rk in R.rings_of(kind):
            sl = tube.ring_slots(rk, j)
            vals = [val[x] for x in sl]
            if any(d == 0 for d, _ in vals):
                continue
            d = min(x[0] for x in vals)
            for x in vals:
                if x[0] == d:
                    counts.add(x[1])
    return kind, v, t0, sorted(counts)


def main():
    write = "--write" in sys.argv
    man = json.loads((HERE / "manifest.json").read_text())
    bound = man.get("parent_bindings", {})
    check("0_dependencies_bound", bool(bound) and all(sha(ROOT / p) == h for p, h in bound.items()), {p: h for p, h in bound.items()})
    with Pool(20) as pool:
        # 1: the two readings agree
        jobs = [(k, B) for k in ("square", "triangular", "honeycomb") for N in range(1, 25) for B in hnf_lattices(N)]
        a = pool.map(on_time, jobs, chunksize=8)
        b = pool.map(lib_on_time, jobs, chunksize=8)
        dis = [x[:2] for x, y in zip(a, b) if x[2] != y[2]]
        check("1_rescue_lib_agrees_with_loopnet_lib", not dis, {"tori": len(jobs), "disagreements": dis})
        # 2: arc moves
        mv = {k: arc_moves(k) for k in ("square", "triangular", "honeycomb")}
        check("2_one_arc_moves_a_contact_by_at_most", abs(mv["square"][0] - 1) < 1e-9 and abs(mv["triangular"][0] - 0.5) < 1e-9
              and abs(mv["honeycomb"][0] - math.sqrt(3) / 2) < 1e-9,
              {k: {"largest": v[0], "lengths": v[1]} for k, v in mv.items()})
        # 3: tube certificates and the quotient conditions
        certs = {}
        for kind, v in TUBES:
            for t0 in range(R.TYPES[kind]):
                c = C.certificate(kind, v, t0)
                q = C.quotient_conditions(c)
                certs["%s %s target %d" % (kind, v, t0)] = {
                    "period": c["P"], "window": c["F"], "shift right": c["DR"], "shift left": c["DL"], "arc width": c["w"],
                    "local conditions failing": c["bad"], "agrees with the search": c["agree"],
                    "Q2 sides share no closest set": q["Q2"], "Q3 closest counts odd": q["Q3"], "grows right": q["grow right"],
                    "grows left": q["grow left"], "N1": q["N1"], "closest sets right": q["sets right"], "closest sets left": q["sets left"]}
        ok3 = all(not x["local conditions failing"] and x["agrees with the search"] and x["Q2 sides share no closest set"]
                  and x["Q3 closest counts odd"] and x["grows right"] and x["grows left"] for x in certs.values())
        check("3_tube_certificates_and_quotient_conditions", ok3, certs)
        # 4: the mirror tube of (1, 2) fails Q3 (it is late)
        mirror = {}
        for t0 in range(2):
            c = C.certificate("square", (1, 2), t0)
            q = C.quotient_conditions(c)
            mirror[t0] = {"certificate holds": not c["bad"] and c["agree"], "Q3": q["Q3"]}
        check("4_the_mirror_tube_is_late", all(x["certificate holds"] for x in mirror.values()) and not all(x["Q3"] for x in mirror.values()),
              mirror)
        # 5: every other short tube is late within the plane's first late distance
        wit = {}
        for kind in ("square", "triangular", "honeycomb"):
            S = short_vectors(kind)
            res = pool.map(tube_witness, [(kind, v) for v in S if not is_family(kind, v)])
            wit[kind] = {"short vectors": len(S), "family": [v for v in S if is_family(kind, v)],
                         "joining a ring to itself": [v for k, v, b in res if b == "joins a ring to itself"],
                         "late at": sorted({b[0] for k, v, b in res if isinstance(b, tuple)}),
                         "no witness": [v for k, v, b in res if b is None],
                         "witnesses": {str(v): b for k, v, b in res}}
        check("5_every_other_short_tube_is_late", all(not w["no witness"] for w in wit.values()), wit)
        # 6: the census
        cen = {}
        for kind in ("square", "triangular", "honeycomb"):
            jobs = [(kind, B) for N in range(1, BOUND[kind] + 1) for B in hnf_lattices(N)]
            res = pool.map(on_time, jobs, chunksize=8)
            idx = lambda B: abs(B[0][0] * B[1][1] - B[0][1] * B[1][0])
            fam = lambda B: any(contains(B, v) for v in FAMILY[kind])
            rot = {"square": lambda v: (-v[1], v[0]), "triangular": lambda v: (v[0] - v[1], v[0]),
                   "honeycomb": lambda v: (-v[0] - v[1], v[0])}[kind]
            invariant = lambda B: contains(B, rot(B[0])) and contains(B, rot(B[1]))
            cen[kind] = {"lattices": len(jobs), "valid": sum(1 for r in res if r[2] is not None),
                         "rotation-invariant on time": sum(1 for r in res if r[2] and invariant(r[1])),
                         "rotation-invariant on time, index": sorted(abs(r[1][0][0] * r[1][1][1] - r[1][0][1] * r[1][1][0])
                                                                     for r in res if r[2] and invariant(r[1])),
                         "on time": sum(1 for r in res if r[2]),
                         "family tori on time": sum(1 for r in res if r[2] and fam(r[1])),
                         "family tori late": [[list(map(list, r[1])), idx(r[1])] for r in res if r[2] is False and fam(r[1])],
                         "listed": sorted([[idx(r[1]), list(map(list, r[1]))] for r in res if r[2] and not fam(r[1])])}
        ok6 = (cen["square"]["family tori late"] == [[[[3, 0], [1, 1]], 3], [[[3, 0], [2, 1]], 3]] and not cen["triangular"]["family tori late"]
               and max(x[0] for x in cen["square"]["listed"]) == 17 and max(x[0] for x in cen["triangular"]["listed"]) == 21
               and max(x[0] for x in cen["honeycomb"]["listed"]) == 9
               and [cen[k]["rotation-invariant on time"] for k in ("square", "triangular", "honeycomb")] == [10, 11, 6])
        for kind in cen:
            cen[kind]["listed count"] = len(cen[kind]["listed"])
        check("6_census_every_lattice_to_the_bounds", ok6, cen)
        # 7: computed, exact counts at the closest contacts of the two tubes
        ex = pool.map(exact_closest, [(k, v, t0, 120) for k, v in TUBES for t0 in range(R.TYPES[k])])
        check("7_computed_every_closest_contact_of_the_tubes_has_one_route", all(c == [1] for k, v, t0, c in ex),
              {"%s %s target %d" % (k, v, t0): c for k, v, t0, c in ex})
    allok = all(v["pass"] for v in OUT.values())
    result = {"ticket": "RESCUE-MAP-20261109-001A", "checks": OUT, "status": "passed" if allok else "failed",
              "seconds": round(time.time() - T0, 1)}
    path = HERE / "result.json"
    if write:
        path.write_text(json.dumps(result, indent=1, default=str) + "\n")
        print("wrote", path)
    else:
        old = json.loads(path.read_text())
        same = {k: v["pass"] for k, v in old["checks"].items()} == {k: v["pass"] for k, v in OUT.items()}
        print("matches result.json" if same else "DIFFERS from result.json")
        sys.exit(0 if same and allok else 1)


if __name__ == "__main__":
    main()
