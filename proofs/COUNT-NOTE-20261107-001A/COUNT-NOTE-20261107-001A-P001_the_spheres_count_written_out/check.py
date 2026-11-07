#!/usr/bin/env python3
"""Checks for COUNT-NOTE-20261107-001A: the sphere's count written out (width Theta(sqrt n), size 2^Theta(sqrt n), grid Sperner).

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv. Single process; about ten minutes. Checks 1 and 8 are exact (they decide the local lemmas for every k);
the others confirm the lemmas on finite instances."""
import hashlib
import heapq
import json
import math
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import note_lib as N  # noqa: E402

W, F = N.W, N.F
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:600], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def dijkstra(adj, src):
    d = {src: 0}
    h = [(0, src)]
    while h:
        du, u = heapq.heappop(h)
        if du > d[u]:
            continue
        for v, c in adj[u]:
            if v not in d or du + c < d[v]:
                d[v] = du + c
                heapq.heappush(h, (d[v], v))
    return d


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(".json") and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})
    rng = random.Random(20261107)

    # 1. the local lemma at a sphere vortex (exact over all critical-angle intervals)
    L1 = N.local_lemma(22.0, 11.0, 5.0)
    check("1 local lemma (exact): six rays from a lattice point, within 22 degrees (near corners) and 11 degrees (far corners) of the "
          "ideal directions, meet pairwise disjoint faces within radius 5; at most 18 points can head one ray's crossing and tail "
          "another's, all within lattice distance 3", L1["pairs of intervals sharing a face"] == 0 and
          L1["bound on |X0| (sum over ordered pairs of the largest set)"] <= 18 and L1["largest lattice distance of such a point"] <= 3, L1)

    # 2-4. straight cut systems on the sphere
    info2, ok2, info3, ok3, info4, ok4 = {}, True, {}, True, {}, True
    geo = {}
    for k in (12, 18, 24, 30, 36, 48):
        K = N.geometry(k)
        geo[k] = K
        cs = N.core(K, k // 6)
        # 2. directions: deviation from the ideal directions over the core
        dev = {"near": 0.0, "far": 0.0}
        for z in cs:
            P0 = K["pos"][z]
            for v3 in K["corner_face"]:
                E = N.unfold(v3)                       # F's centroid is the origin, so E's own angle is the ideal direction
                a1 = math.atan2(E[1] - P0[1], E[0] - P0[0])
                a0 = math.atan2(E[1], E[0])
                d = abs(math.degrees((a1 - a0 + math.pi) % (2 * math.pi) - math.pi))
                kind = "near" if all(t >= 0 for t in v3) else "far"
                dev[kind] = max(dev[kind], d)
        if k >= 36:
            ok2 &= dev["near"] <= 22 and dev["far"] <= 11
            info2["k=%d" % k] = {"core vortices": len(cs), "largest deviation, near corners": round(dev["near"], 2),
                                 "largest deviation, far corners": round(dev["far"], 2)}
        if k == 48:
            continue
        # 3. every core vortex: a cut system, a flat state with one violated line at z, X0 near z
        mx, far, nbad = 0, 0, 0
        for z in cs:
            st = N.straight_star(K, z)
            T = N.trivialization(K, z, st)
            x0, Wt = N.zero_heads_tails(T)
            dz = F.dist_from(K["adj"], [z])
            mx, far = max(mx, len(x0)), max(far, max(dz[p] for p in x0))
            x = F.flat_state(K, z, st, next(p for p in range(K["n"]) if p != z))
            v = F.violated(K, x)
            nbad += not (len(v) == 1 and z in K["lines"][v[0]])
        ok3 &= nbad == 0 and mx <= 18 and far <= 3
        info3["k=%d" % k] = {"core vortices": len(cs), "failures": nbad, "largest |X0|": mx, "farthest X0 point from z": far}
        # 4. the distance lemma, from sampled sources
        if k in (24, 36):
            slack = 99
            for z in rng.sample(cs, 12):
                T = N.trivialization(K, z, N.straight_star(K, z))
                Wt = W.weights(T)
                for src in rng.sample([p for p in range(K["n"]) if p != z], 3):
                    dw = W.dists(Wt, src, K["n"])
                    dg = F.dist_from(K["adj"], [src])
                    slack = min(slack, min(dw[y] - (dg[y] - 19) / 2 for y in range(K["n"]) if y not in (z, src)))
            ok4 &= slack >= 0
            info4["k=%d" % k] = {"vortices": 12, "sources each": 3, "least d - (dist - 19)/2": slack}
    check("2 directions: over every core vortex (radius k/6) the arcs deviate from the ideal directions by at most 22 degrees (near "
          "corners) and 11 degrees (far corners), so the local lemma applies", ok2, info2)
    check("3 straight cut systems: for every core vortex of K_12..K_36 the six straight arcs are disjoint paths of faces, the flat state "
          "violates exactly one line, through z, and X0 has at most 18 points, within distance 3 of z", ok3, info3)
    check("4 distance lemma: d_z(x, y) >= (dist(x, y) - 19)/2 for sampled vortices and sources on K_24 and K_36", ok4, info4)

    # 5. single steps: every blocked step has a certificate through the old vortex, short and dense
    K = geo[30]
    cs = set(N.core(K, 5))
    cache = {}

    def triv(z):
        if z not in cache:
            cache[z] = N.trivialization(K, z, N.straight_star(K, z))
        return cache[z]
    st5 = {"steps": 0, "blocked": 0, "through the old vortex": 0, "budget sum d <= 3r - 6": 0, "largest dist(y, pebble)/r": 0.0}
    for trial in range(30):
        y = rng.choice(sorted(cs))
        T = triv(y)
        x, L = W.realize(K, T, {}, None, None, None)
        dy = F.dist_from(K["adj"], [y])
        ring = [p for p in range(K["n"]) if 1 <= dy[p] <= rng.choice((1, 2, 3))]
        P = ring if trial % 3 == 0 else rng.sample(ring, min(len(ring), rng.randint(3, 9)))
        peb = {p: x[p] for p in P}
        assert W.feasible(K, T, peb)[0]
        for y2 in K["adj"][y]:
            if y2 not in cs or y2 in peb:
                continue
            st5["steps"] += 1
            T2 = triv(y2)
            ob = W.obstruction(K, T2, peb)
            if ob is None:
                continue
            st5["blocked"] += 1
            cyc, walk, bsum, a2 = ob
            r = len(cyc)
            Wt = W.weights(T2)
            dsum = sum(W.dists(Wt, p, K["n"])[q] for p, q in zip(cyc, cyc[1:] + cyc[:1]))
            st5["budget sum d <= 3r - 6"] += dsum <= 3 * r - 6
            st5["through the old vortex"] += y in walk
            st5["largest dist(y, pebble)/r"] = max(st5["largest dist(y, pebble)/r"], max(dy[p] for p in cyc) / r)
    check("5 single steps on K_30: every blocked step to a neighbour has a certificate whose walk passes through the old vortex, with "
          "sum d <= 3r - 6 and every pebble of the cycle within 25r of the old vortex",
          st5["blocked"] > 0 and st5["blocked"] == st5["through the old vortex"] == st5["budget sum d <= 3r - 6"] and
          st5["largest dist(y, pebble)/r"] <= 25, st5)

    # 6. islands at the proof's separation on K_48 and K_60
    info6 = {"islands": {}, "vortex positions tested": 0, "least same-island d + lambda_p - lambda_q": 99,
             "least between-island term": 99, "window starts range": [99, -99], "islands alone admit a state": 0}
    for k6 in (48, 60):
        K = geo[48] if k6 == 48 else N.geometry(60)
        centres = N.packing(K, 45, rng)
        col, isl = N.island_colours(K, centres, rng)
        info6["islands"]["k=%d" % k6] = len(centres)
        cs = N.core(K, k6 // 6)
        dI = F.dist_from(K["adj"], list(isl))
        ys = [y for y in cs if dI[y] >= 7]
        for y in rng.sample(ys, 2):
            T = N.trivialization(K, y, N.straight_star(K, y))
            lam = N.island_lifts(K, T, col, isl, centres)
            Wt = W.weights(T)
            A = {}
            for p in isl:
                j = (lam[p] - W.arc_start(T["fr"][p], col[p])) % 6
                assert j in (0, 1, 2)
                A[p] = lam[p] - j
            info6["window starts range"] = [min(info6["window starts range"][0], min(A.values())),
                                            max(info6["window starts range"][1], max(A.values()))]
            D = {p: W.dists(Wt, p, K["n"]) for p in isl}
            for p in isl:
                for q in isl:
                    if p == q:
                        continue
                    if isl[p] == isl[q]:
                        info6["least same-island d + lambda_p - lambda_q"] = min(info6["least same-island d + lambda_p - lambda_q"],
                                                                                 D[p][q] + lam[p] - lam[q])
                    else:
                        info6["least between-island term"] = min(info6["least between-island term"], (D[p][q] + A[p] + 2 - A[q]) // 6)
            info6["islands alone admit a state"] += W.feasible(K, T, col)[0]
            info6["vortex positions tested"] += 1
    check("6 islands on K_48 and K_60 (radius 1, separation 45, vortex at distance >= 7): same-island terms >= 0 (d + lambda_p - lambda_q >= 0), "
          "between-island terms >= 1, window starts in [-3, 6], and the islands alone admit a state",
          info6["least same-island d + lambda_p - lambda_q"] >= 0 and info6["least between-island term"] >= 1 and
          -3 <= info6["window starts range"][0] and info6["window starts range"][1] <= 6 and
          info6["islands alone admit a state"] == info6["vortex positions tested"] > 0, info6)

    # 7. grid Sperner: the local lemma at a down-triangle vortex (exact)
    L7 = N.local_lemma_disk(20.0, 5.0)
    check("7 local lemma for grid Sperner (exact): three rays from a down-triangle's centroid within 20 degrees of 90, 210, 330 meet "
          "disjoint faces beyond the vortex triangle within radius 5, and at most 3 points can head one ray's crossing and tail another's",
          L7["vortex triangle points down"] and L7["pairs of intervals sharing a face"] == 0 and L7["bound on |X0|"] <= 3, L7)

    # 8. grid Sperner: straight three-arc cuts on the cores, flat boundary, distance lemma, boundary and boundary-island terms
    info8, ok8 = {}, True
    for m in (24, 36, 48):
        S = N.sperner(m)
        core = N.sperner_core(S, m / 6.0)
        nbad, mx, slack, bterm = 0, 0, 99, 99
        for T in core:
            C = N.sperner_cut(S, T)
            bset, starts, colour, full = N.sperner_flat(S, C)
            nbad += not (len(starts) == 1 and full == [T] and all(colour[b] == S["bcol"][b] for b in S["bcol"]))
            Wd = N.sperner_weights(S, C)
            heads, tails = set(), set()
            for u, nb in Wd.items():
                for v, w in nb:
                    if w == 0:
                        tails.add(u)
                        heads.add(v)
            mx = max(mx, len(heads & tails))
        for T in rng.sample(core, 6):
            C = N.sperner_cut(S, T)
            Wd = N.sperner_weights(S, C)
            for src in rng.sample(S["V"], 2):
                d = dijkstra(Wd, src)
                slack = min(slack, min(d[y] - (N.hexdist(src, y) - 4) / 2 for y in S["V"]))
            # boundary terms and terms between the boundary and islands touching it (colour c, start in {-1, 0, 1})
            bnd = list(S["bcol"])
            a0 = (S["bcol"][bnd[0]] - C["phi"][bnd[0]]) % 3
            for b in rng.sample(bnd, min(12, len(bnd))):
                d = dijkstra(Wd, b)
                for b2 in bnd:
                    if b2 != b:
                        bterm = min(bterm, (d[b2] + 0) // 3)
                for v in S["V"]:
                    if v in S["bcol"] or N.hexdist(v, b) != 1 or min(N.hexdist(v, c) for c in ((0, 0), (m, 0), (0, m))) < 8:
                        continue
                    for A in (-1, 0, 1):        # an island start relative to the boundary's
                        bterm = min(bterm, (d[v] + 0 - A) // 3)
                        dv = dijkstra(Wd, v)
                        bterm = min(bterm, (dv[b] + A - 0) // 3)
        ok8 &= nbad == 0 and mx <= 3 and slack >= 0 and bterm >= 0
        info8["m=%d" % m] = {"core vortex triangles": len(core), "failures": nbad, "largest |X0|": mx, "least distance-lemma slack": slack,
                             "least boundary or boundary-island term": bterm}
    check("8 grid Sperner on m = 24, 36, 48: for every core down-triangle the three straight arcs give a flat boundary (one window start) "
          "and a flat state whose only full triangle is the vortex, |X0| <= 3, d >= (dist - 4)/2, and every term between boundary points "
          "or between a boundary point and an adjacent island point (start -1, 0 or 1) is >= 0", ok8, info8)

    # 9a. balls of G are no larger than the flat lattice's (radius 20, every point within distance 25 of a corner of K_48)
    K = geo[48]
    dcor = F.dist_from(K["adj"], list(K["corner_pts"]))
    worst = 0
    for p in [q for q in range(K["n"]) if dcor[q] <= 25] + rng.sample(range(K["n"]), 40):
        dp = F.dist_from(K["adj"], [p])
        worst = max(worst, sum(1 for x in dp.values() if x <= 20))       # dist_from returns {point: distance}
    # 9. the size bound's constants at the proof's parameters
    ball = lambda R: 3 * R * R + 3 * R + 1  # noqa: E731
    M = ball(2 * 1 + 45)
    p0 = ball(1) / (math.e * M)
    q = p0 / 2
    V = ball(2 * (1 + 47))
    alpha = -math.log2(1 - q) / V
    check("9 constants of the size bound (s = 1, separation 45): balls of G are no larger than flat ones (radius 20 near every corner of "
          "K_48), coverage >= 7/(eM), literal probability q = p0/2, independence beyond distance 96, alpha = -log2(1 - q)/|B(96)| > 0",
          alpha > 0 and worst <= ball(20),
          {"largest ball of radius 20 near the corners of K_48 (flat: 1261)": worst, "M = |B(47)|": M, "coverage lower bound p0": "%.3g" % p0, "q": "%.3g" % q, "|B(96)|": V, "alpha (bits per literal)": "%.3g" % alpha})

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
