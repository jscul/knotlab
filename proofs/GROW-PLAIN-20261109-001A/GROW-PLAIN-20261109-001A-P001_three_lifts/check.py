"""Checks for GROW-PLAIN-20261109-001A: the one map of RESCUE-GENUS-20261109-001A-E001 rescued by an odd count of several routes. Exact
reading: breadth-first search from the target contact, every shortest route enumerated, and the homology class mod 2 of the loop two
routes with common ends make, against the span of the map's face boundaries.

    python3 -B check.py          verify against result.json
    python3 -B check.py --write  write result.json from a fresh run
"""
import collections
import hashlib
import itertools
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PLAIN = ROOT / "experiments/PLAIN-TIME-20261108-001A/PLAIN-TIME-20261108-001A-E001_map_census"
CENSUS = ROOT / "experiments/RESCUE-GENUS-20261109-001A/RESCUE-GENUS-20261109-001A-E001_closest_routes"
sys.path.insert(0, str(PLAIN))
import plain_lib as P  # noqa: E402

OUT = {}
T0 = time.time()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print(("PASS " if ok else "FAIL ") + name, "(%.0fs)" % (time.time() - T0), flush=True)
    if not ok:
        print(json.dumps(info, indent=1, default=str)[:3000])


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def reading(n, out, target):
    inn = [[] for _ in range(n)]
    for d in range(n):
        for e in out[d]:
            inn[e].append(d)
    dist, cnt = [None] * n, [0] * n
    dist[target], cnt[target] = 0, 1
    order, q = [target], collections.deque([target])
    while q:
        a = q.popleft()
        for b in inn[a]:
            if dist[b] is None:
                dist[b] = dist[a] + 1
                q.append(b)
                order.append(b)
    for b in order[1:]:
        cnt[b] = sum(cnt[e] for e in out[b] if dist[e] == dist[b] - 1)
    return dist, cnt


def main():
    write = "--write" in sys.argv
    man = json.loads((HERE / "manifest.json").read_text())
    bound = man.get("parent_bindings", {})
    check("0_dependencies_bound", bool(bound) and all(sha(ROOT / p) == h for p, h in bound.items()), bound)
    G, gens = P.group("S 6")
    hits = []
    for x, y in P.generating_pairs(G, gens):
        n, out, rc, target, m, f = P.group_map(G, x, y)
        if (m, f) != (6, 6) or (2 - (len(rc) - n + len(G) // f)) // 2 != 61:
            continue
        dist, cnt = reading(n, out, target)
        odd = []
        for ri, cs in enumerate(rc):
            if target in cs:
                continue
            dr = min(dist[e] for e in cs)
            cl = [e for e in cs if dist[e] == dr]
            if all(cnt[e] > 1 for e in cl) and any(cnt[e] % 2 for e in cl):
                odd.append((ri, dr, cl))
        v = P.verdicts(n, out, rc, target)
        hits.append((x, y, n, out, rc, target, dist, cnt, odd, v))
    maps_with_odd = [h for h in hits if h[8]]
    same = len({json.dumps(h[9], sort_keys=True) for h in maps_with_odd}) == 1
    check("1_the_map_and_its_two_rings", len(maps_with_odd) >= 1 and same and all(len(h[8]) == 2 for h in maps_with_odd)
          and maps_with_odd[0][9]["rings late"] == 0 and maps_with_odd[0][9]["rings never"] == 0,
          {"generating pairs of S6 of type (6, 6) and genus 61 read": len(hits),
           "with a ring rescued only by an odd count of several routes": len(maps_with_odd),
           "those pairs give identical readings (one map in the census)": same,
           "rings": [[ri, dr, [[e, maps_with_odd[0][7][e]] for e in cl]] for ri, dr, cl in maps_with_odd[0][8]]})
    x, y, n, out, rc, target, dist, cnt, odd, v = maps_with_odd[0]
    # darts, rings, faces
    cid, rid = {}, {}
    k = 0
    for g in G:
        if g not in cid:
            cid[g] = cid[P.mul(g, y)] = k
            k += 1
    k = 0
    for g in G:
        if g not in rid:
            h = g
            while True:
                rid[h] = k
                h = P.mul(h, x)
                if h == g:
                    break
            k += 1
    rings_of = collections.defaultdict(set)
    for g in G:
        rings_of[cid[g]].add(rid[g])
    xy, seen, basis = P.mul(x, y), set(), {}

    def reduce(vec):
        while vec:
            t = vec.bit_length() - 1
            if t not in basis:
                return vec
            vec ^= basis[t]
        return 0
    nfaces = 0
    for g in G:
        if g in seen:
            continue
        h, fb = g, 0
        while True:
            seen.add(h)
            fb ^= 1 << cid[h]
            h = P.mul(h, xy)
            if h == g:
                break
        nfaces += 1
        r = reduce(fb)
        if r:
            basis[r.bit_length() - 1] = r
    genus = (n - len(basis) - (len(rc) - 1)) // 2
    check("2_faces_span_and_genus", len(basis) == nfaces - 1 and genus == 61, {"faces": nfaces, "rank": len(basis), "genus": genus})

    def routes_from(e):
        res = []

        def walk(u, path):
            if u == target:
                res.append(path + [u])
                return
            for w in out[u]:
                if dist[w] == dist[u] - 1:
                    walk(w, path + [u])
        walk(e, [])
        return res

    def ring_seq(route):
        seq = []
        for a, b in zip(route, route[1:]):
            common = rings_of[a] & rings_of[b]
            assert len(common) == 1
            seq.append(next(iter(common)))
        return seq

    def loop(A, B):
        ra, rb = ring_seq(A), ring_seq(B)
        vec = 0
        for route, rs in ((A, ra), (B, rb)):
            for i in range(1, len(route) - 1):
                if rs[i - 1] != rs[i]:
                    vec ^= 1 << route[i]
        if ra[0] != rb[0]:
            vec ^= 1 << A[0]
        if ra[-1] != rb[-1]:
            vec ^= 1 << A[-1]
        deg = collections.Counter()
        for e in range(n):
            if vec >> e & 1:
                for rr in rings_of[e]:
                    deg[rr] += 1
        assert all(d % 2 == 0 for d in deg.values())
        return vec
    info, ok = {}, True
    for ri, dr, cl in odd:
        for e in cl:
            rs = routes_from(e)
            pairs = [reduce(loop(rs[i], rs[j])) != 0 for i, j in itertools.combinations(range(len(rs)), 2)]
            info["ring %d contact %d" % (ri, e)] = {"distance": dr, "routes": len(rs), "every pair round a handle": all(pairs),
                                                    "routes listed": rs}
            ok &= len(rs) == cnt[e] and all(pairs)
    check("3_every_pair_of_routes_runs_round_a_handle", ok, info)
    # the half-turn about the target (left multiplication by y) exchanges the two rings
    ring_of_dart = rid
    image = {}
    for g in G:
        image[ring_of_dart[g]] = ring_of_dart[P.mul(y, g)]
    r0, r1 = odd[0][0], odd[1][0]
    check("4_the_half_turn_about_the_target_exchanges_the_two_rings", image[r0] == r1 and image[r1] == r0, {"rings": [r0, r1]})
    allok = all(v["pass"] for v in OUT.values())
    result = {"ticket": "GROW-PLAIN-20261109-001A", "checks": OUT, "status": "passed" if allok else "failed",
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
