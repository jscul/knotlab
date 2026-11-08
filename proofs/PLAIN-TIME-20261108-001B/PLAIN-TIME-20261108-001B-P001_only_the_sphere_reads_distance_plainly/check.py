#!/usr/bin/env python3
"""Checks for PLAIN-TIME-20261108-001B: only the sphere reads distance plainly at every size.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
16 worker processes, about two minutes. Every verdict is exact (breadth-first route counts and rows mod 2 to their span, plain_lib);
cover balls are read in PSL(2, p) for two primes, which must agree. Checks 3 and 5 are computations, not theorems."""
import collections
import hashlib
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import cover_lib as C  # noqa: E402

P = C.P
T0 = time.time()
OUT = {}
DEPS = {
    "experiments/PLAIN-TIME-20261108-001A/PLAIN-TIME-20261108-001A-E001_map_census/contract.json":
        "df868cf441b9df94ab09ae37fae0463ca6525590dbb5741ab504e41dbdb085c1",
    "experiments/PLAIN-TIME-20261108-001A/PLAIN-TIME-20261108-001A-E001_map_census/run.py":
        "12e29ced1dd83607598bae32b077d1cfa22a70737e2f97ef9498672bd2f562c5",
    "experiments/PLAIN-TIME-20261108-001A/PLAIN-TIME-20261108-001A-E001_map_census/plain_lib.py":
        "bb6dc72ac1267b8139483d95bcbedddd9f55919481f27f8f8f6c040c605f3e30",
    "proofs/DISTANCE-20261108-001B/DISTANCE-20261108-001B-P001_distance_across_time_is_native_as_a_cone/manifest.json":
        "cfa8fa26d7df3f5e629fb573d241bac4589e378535bd24aee4d061df6406c45d",
}
KIND = {"square": (4, 4), "triangular": (6, 3), "honeycomb": (3, 6)}
FIRST_LATE_FLAT = {"square": 4, "triangular": 6, "honeycomb": 5}
# the least index from which the systole lemma makes every torus late: systole >= 2 l + m, with the medial systole at least
# sqrt(2) |v| (square), 2 |v| (triangular, unit spacing) and 2 sqrt(N) (honeycomb, translations of length sqrt(3 N))
LEMMA_INDEX = {"square": 72, "triangular": 81, "honeycomb": 43}
NMAX = {"square": 400, "triangular": 300, "honeycomb": 200}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:400], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def on_time_row(rot, edges, target=0):
    sizes, contacts = P.LN.network(rot, edges, 2)
    n, out, rc = P.network_map(sizes, contacts)
    v = P.verdicts(n, out, rc, target)
    return v["rings late"] == 0 and v["rings never"] == 0, v, len(rc)


# ---------- check 1: the sphere
def sphere():
    bad = []
    for k in range(2, 201):
        for name, (rot, edges) in (("loop", P.LN.dihedron(k)), ("pair", P.LN.hosohedron(k))):
            ok, v, r = on_time_row(rot, edges)
            if not ok:
                bad.append((name, k))
    plat = {}
    for g in ("A 4", "S 4", "PSL(2,p) 5"):
        G, gens = P.group(g)
        for x, y in P.generating_pairs(G, gens):
            n, out, rc, t, m, f = P.group_map(G, x, y)
            if len(G) // m - len(G) // 2 + len(G) // f != 2:
                continue
            v = P.verdicts(n, out, rc, t)
            plat["%s (%d,%d)" % (g, m, f)] = v["rings late"] == 0 and v["rings never"] == 0
    return bad, plat


# ---------- check 2: the flat planes' first late rings
def plane(kind, n):
    rot, edges = P.lattice_torus(kind, n, 0)
    sizes, contacts = P.LN.network(rot, edges, 2)
    N, out, rc = P.network_map(sizes, contacts)
    inn = [[] for _ in range(N)]
    for d in range(N):
        for e in out[d]:
            inn[e].append(d)
    dist, cnt = [None] * N, [0] * N
    dist[0], cnt[0] = 0, 1
    order, q = [0], collections.deque([0])
    while q:
        a = q.popleft()
        for b in inn[a]:
            if dist[b] is None:
                dist[b] = dist[a] + 1
                q.append(b)
                order.append(b)
    for b in order[1:]:
        cnt[b] = sum(cnt[e] for e in out[b] if dist[e] == dist[b] - 1)
    verts = sorted(rot, key=repr)
    late = []
    for i, cs in enumerate(rc):
        D = min(dist[e] for e in cs)
        if D < n // 3 and not any(dist[e] == D and cnt[e] % 2 for e in cs):
            late.append((D, sorted((dist[e], cnt[e]) for e in cs), verts[i]))
    return sorted(late)


# ---------- check 3: covers
def cover_task(args):
    m, f, R = args
    p1, p2 = C.prime_for(m, f, 10 ** 7), C.prime_for(m, f, 3 * 10 ** 7)
    a, b = C.cover_ball(m, f, p1, R), C.cover_ball(m, f, p2, R)
    return m, f, R, a == b, a[2], sum(a[0])


COVERS = [(3, 3, 8), (3, 4, 8), (4, 3, 8), (3, 5, 10), (5, 3, 10), (4, 4, 12), (6, 3, 12), (3, 6, 12),
          (3, 7, 16), (7, 3, 17), (3, 8, 18), (8, 3, 19), (3, 9, 12), (9, 3, 12), (3, 10, 21), (10, 3, 22), (3, 11, 23), (11, 3, 24),
          (3, 12, 12), (12, 3, 13), (4, 5, 16), (5, 4, 16), (4, 6, 12), (6, 4, 12), (4, 7, 21), (7, 4, 21), (4, 8, 10), (8, 4, 11),
          (5, 5, 9), (6, 6, 9), (8, 8, 10), (4, 10, 14), (10, 4, 14), (6, 8, 12), (8, 6, 12), (6, 9, 12),
          (9, 6, 12), (5, 6, 22), (6, 5, 22)]


# ---------- check 4: every torus
def torus_task(args):
    kind, key, b, c, N = args
    rot, edges = P.lattice_torus(kind, b, c)
    ok, v, rings = on_time_row(rot, edges)
    return kind, key, b, c, N, ok, rings, v["rings late"], v["rings never"]


def main():
    write = "--write" in sys.argv
    got = {p: sha(p) for p in DEPS}
    check("0 dependencies bound by hash", all(h is None or got[p] == h for p, h in DEPS.items()), got)
    bad, plat = sphere()
    check("1 the sphere: loops of 2 to 200 rings and two rings sharing 2 to 200 contacts, and every spherical map of A4, S4 and A5, are on time",
          not bad and all(plat.values()), {"loops and pairs late": bad, "spherical group maps": plat})
    sq = plane("square", 41)
    first = sq[0]
    check("2 the square plane: the first late ring is at distance 4, its only closest contact reached by 2 shortest routes",
          first[0] == 4 and first[1][0] == (4, 2) and all(d > 4 for d, cnt in first[1][1:]),
          {"first late rings (distance, contacts (distance, routes), ring)": sq[:4],
           "triangular plane first late": plane("triangular", 31)[:2], "honeycomb plane first late": plane("honeycomb", 31)[:2]})
    with Pool(16) as pool:
        cov = pool.map(cover_task, COVERS, chunksize=1)
        cover_table = {"(%d,%d)" % (m, f): {"radius": R, "primes agree": agree, "first late": min(late) if late else None,
                                             "ball contacts": size} for m, f, R, agree, late, size in cov}
        flat_ok = all(cover_table["(%d,%d)" % KIND[k]]["first late"] == FIRST_LATE_FLAT[k] for k in KIND)
        sph_ok = all(cover_table[k]["first late"] is None for k in ("(3,3)", "(3,4)", "(4,3)", "(3,5)", "(5,3)"))
        check("3 computed: first late distance of the covers, two primes each; the flat covers repeat check 2, spherical ones have none",
              all(v["primes agree"] for v in cover_table.values()) and flat_ok and sph_ok, cover_table)
        tasks = []
        for kind in KIND:
            for key, (b, c, N) in sorted(C.lattices(kind, NMAX[kind]).items(), key=lambda kv: kv[1][2]):
                if N >= 3 or (kind == "honeycomb" and N >= 1):
                    tasks.append((kind, key, b, c, N))
        res = pool.map(torus_task, tasks, chunksize=4)
    on = collections.defaultdict(list)
    lemma_bad = []
    for kind, key, b, c, N, ok, rings, late, never in res:
        if ok:
            on[kind].append({"lattice": list(key), "vector": [b, c], "index": N, "rings": rings})
        if N >= LEMMA_INDEX[kind] and ok:
            lemma_bad.append((kind, b, c, N))
    counts = {k: sum(1 for r in res if r[0] == k) for k in KIND}
    check("4 every torus: the systole lemma's tori (index at least 72, 81 and 43) are all late; the on-time tori, both chiralities",
          not lemma_bad, {"tori read": counts, "on time": dict(on), "lemma tori on time": lemma_bad})
    # check 5: the first late distance against the law of first ties (computed)
    import math
    pat = {}
    for key, v in cover_table.items():
        m, f = map(int, key.strip("()").split(","))
        if 1 / m + 1 / f > 0.5:
            continue
        L = m * f // math.gcd(m, f)
        tau = L - L // m - L // f + 1
        law = tau + 1 + (1 if f == 3 and m > 3 else 0)
        pat[key] = {"first late": v["first late"], "radius": v["radius"], "tau": tau, "law": law,
                    "agrees": v["first late"] == law if v["first late"] is not None else law >= v["radius"]}
    check("5 computed: the cover's first late ring comes at tau + 1 (tau + 2 when faces are triangles and rings larger), "
          "tau = L - L/m - L/f + 1 with L = lcm(m, f); a cover with none to its radius has law at least the radius",
          all(v["agrees"] for v in pat.values()), pat)
    # check 6: the smallest late torus, the twisted square torus of index 13, against its mirror image, at the cell level
    tw = {}
    for (b, c) in ((2, 3), (3, 2)):
        rot, edges = P.lattice_torus("square", b, c)
        for g in (2, 3):
            sizes, contacts = P.LN.network(rot, edges, g)
            n, out, rc = P.network_map(sizes, contacts)
            ins = [0] * n
            for d in range(n):
                for e in out[d]:
                    ins[e] ^= 1 << d
            outa = {x: [(y, 0, 0) for y in out[x]] for x in range(n)}
            dist_from = {e: P.D.dist_from(outa, [e], n) for e in range(n)}
            late, bad, lags = 0, 0, collections.Counter()
            for t in range(n):
                first = P.T.reach(ins, t)[1]
                for r, cs in enumerate(rc):
                    delta = min(dist_from[e][t] for e in cs)
                    kap = min(first[e] for e in cs if e in first)
                    cell = P.D.first_need(sizes, contacts, t, r, g * kap + 1)
                    bad += cell != g * kap + 1
                    if kap > delta:
                        late += 1
                        lags["delta %d, kappa %d, lag %s" % (delta, kap, cell)] += 1
            tw["(%d,%d), g = %d" % (b, c, g)] = {"rings": len(rc), "contacts": n, "late pairs": late, "cell mismatches": bad,
                                                 "late": dict(lags)}
    check("6 the twisted square torus {4,4}_(2,3), 13 rings, has one late ring per contact at delta 4 (first need at kappa 5, lag 5g + 1, "
          "cell level); its mirror image {4,4}_(3,2) is on time",
          all(v["cell mismatches"] == 0 for v in tw.values()) and tw["(2,3), g = 2"]["late pairs"] == 26 and tw["(3,2), g = 2"]["late pairs"] == 0,
          tw)
    # check 7: the contact-level horizon, the first tie of two shortest routes, against tau (computed, two primes)
    import math
    ties = {}
    for (m, f) in ((4, 4), (6, 3), (3, 6), (7, 3), (3, 7), (6, 4), (4, 6), (5, 5), (8, 4), (4, 5)):
        L = m * f // math.gcd(m, f)
        tau = L - L // m - L // f + 1
        got = [C.first_tie(m, f, C.prime_for(m, f, s), tau + 2) for s in (10 ** 7, 3 * 10 ** 7)]
        ties["(%d,%d)" % (m, f)] = {"tau": tau, "first tie (two primes)": got, "agrees": all(t is not None and t[0] == tau for t in got)}
    check("7 computed: in the cover the first contact with two shortest routes comes at tau = L - L/m - L/f + 1", all(v["agrees"] for v in ties.values()), ties)
    result = {"ticket": "PLAIN-TIME-20261108-001B", "checks": OUT, "status": "passed"}
    path = HERE / "result.json"
    if write:
        path.write_text(json.dumps(result, indent=1, default=str) + "\n")
        print("wrote", path.relative_to(ROOT))
    else:
        old = json.loads(path.read_text())
        same = json.dumps(old, sort_keys=True, default=str) == json.dumps(json.loads(json.dumps(result, default=str)), sort_keys=True)
        print("result.json", "matches" if same else "DIFFERS")
        sys.exit(0 if same else 1)


if __name__ == "__main__":
    main()
