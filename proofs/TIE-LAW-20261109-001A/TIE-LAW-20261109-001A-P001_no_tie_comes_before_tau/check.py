#!/usr/bin/env python3
"""Checks for TIE-LAW-20261109-001A: no two shortest routes of the directed medial graph of {f, m} share an endpoint before
tau = L - L/m - L/f + 1 (L = lcm(m, f)); the tie at tau when m = f.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
One process, a few minutes. Check 1 is exact rational arithmetic over every type with m, f <= 40 (the proof's case analysis); checks
2 to 6 read balls of the tessellations in PSL(2, p) for two primes each (computations, not theorems)."""
import hashlib
import json
import math
import sys
import time
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import tie_lib as T  # noqa: E402

T0 = time.time()
OUT, FAILED = {}, []
DEPS = {"proofs/PLAIN-TIME-20261108-001B/PLAIN-TIME-20261108-001B-P001_only_the_sphere_reads_distance_plainly/manifest.json":
        "603257295514c890d7114b2b0866127cb84b1efcee560a64d987b1173a173936"}


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info=None):
    OUT[name] = {"pass": bool(ok), "info": info}
    if not ok:
        FAILED.append(name)
    print(("PASS " if ok else "FAIL ") + name, "(%.0fs)" % (time.time() - T0), flush=True)


def types(limit, euclid=False):
    out = []
    for m in range(3, limit + 1):
        for f in range(3, limit + 1):
            if 2 * (m + f) < m * f or (euclid and 2 * (m + f) == m * f):
                out.append((m, f))
    return out


# 1. the proof's arithmetic (Theorem 2, steps 5 to 7): for every type and every K = cL, one of the four cases applies
def lower_bound_cases(limit=40):
    bad, why = [], {}
    for m, f in types(limit, euclid=True):
        g = math.gcd(m, f)
        L = m * f // g
        tau = T.tau_formula(m, f)
        h = Fr(1) - Fr(2, m) - Fr(2, f)
        rR, rF = (m * (f - 1)) // f, (f * (m - 1)) // m
        den = Fr(1) - Fr(1, rR) - Fr(1, rF)
        used = set()
        for c in range(1, 200):
            K = c * L
            if c < g:
                used.add("thin by counting")
            elif c == 1 and g == 1:
                used.add("thin, coprime argument")
            elif K * h + 3 >= tau:
                used.add("simple bound")
            elif den > 0 and math.ceil((K * h + 1) / den) >= tau:
                used.add("refined bound")
            else:
                bad.append((m, f, c))
                break
            if h > 0 and K * h + 3 >= tau and (den > 0 and (K * h + 1) / den >= tau):
                break
            if h == 0 and c >= max(g, 2) and den > 0 and Fr(1) / den >= tau:
                break
        why[f"{m},{f}"] = sorted(used)
    return bad, why


# 2. the first tie on every readable type, two primes (later distances with a count >= 2 include contacts downstream of a tie)
def first_ties(ts, R_extra=2, limit=4_000_000):
    res, bad = {}, []
    for m, f in ts:
        tau = T.tau_formula(m, f)
        per = []
        for start in (10 ** 6, 10 ** 7):
            p = T.prime_for(m, f, start)
            ties, reached = T.first_tie(m, f, p, tau + R_extra, limit)
            first = min(ties) if ties else None
            per.append({"p": p, "first tie": first, "at first": ties.get(first), "radius read": reached,
                        "tie distances": sorted(ties)})
        ok = all(x["first tie"] == tau and x["at first"] == (2, [2, 2]) for x in per) and per[0]["tie distances"] == per[1]["tie distances"]
        res[f"{m},{f}"] = {"tau": tau, "reads": per, "ok": ok}
        if not ok:
            bad.append((m, f))
    return res, bad


# 4. every pair of internally disjoint shortest routes is thin, and the run bounds are attained
def bigons(ts, R_extra=2):
    res, bad = {}, []
    for m, f in ts:
        tau = T.tau_formula(m, f)
        p = T.prime_for(m, f, 10 ** 6)
        G, dist, paths = T.shortest_routes(m, f, p, tau + R_extra)
        h = Fr(1) - Fr(2, m) - Fr(2, f)
        L = m * f // math.gcd(m, f)
        pairs, readings = 0, set()
        longest_ring = longest_face = 0
        for c, lst in paths.items():
            for _, w in lst:
                rr, fr = T.runs(w)
                longest_ring, longest_face = max(longest_ring, max(rr)), max(longest_face, max(fr))
            if len(lst) < 2:
                continue
            d = dist[c]
            for i in range(len(lst)):
                for j in range(i + 1, len(lst)):
                    (da, wa), (db, wb) = lst[i], lst[j]
                    sb = set(G.contact(g) for g in db[1:-1])
                    if any(G.contact(g) in sb for g in da[1:-1]):
                        continue
                    pairs += 1
                    got = None
                    for (P, Q) in ((wa, wb), (wb, wa)):
                        pF, qV = P[1:].count("F"), Q[1:].count("V")
                        if h > 0:
                            K = Fr(d - 3 - pF - qV) / h
                            nint = K / m + K / f - 2 - pF - qV
                            if K > 0 and K.denominator == 1 and K % L == 0 and nint.denominator == 1 and nint >= 0:
                                got = (int(K // L), int(nint))
                    readings.add((d, got))
        rR, rF = (m * (f - 1)) // f, (f * (m - 1)) // m
        thin = all(g is not None and g[1] == 0 and d == g[0] * (tau - 1) + 1 for d, g in readings) if h > 0 else True
        ok = thin and longest_ring == rR and longest_face == rF and pairs > 0
        res[f"{m},{f}"] = {"radius": tau + R_extra, "contacts": len(dist), "disjoint shortest pairs": pairs,
                           "(distance, (K/L, interior vertices))": sorted(readings, key=str), "longest ring run": longest_ring,
                           "bound": rR, "longest face run": longest_face, "face bound": rF, "ok": ok}
        if not ok:
            bad.append((m, f))
    return res, bad


# 5. directed girth min(m, f) and, for m = f, the tie at m - 1 between the long way round a ring and round a face
def girth_and_equal(ts):
    res, bad = {}, []
    for m, f in ts:
        p = T.prime_for(m, f, 10 ** 6)
        G = T.Group(m, f, p)
        R = max(m, f) + 1
        ties, _ = T.first_tie(m, f, p, R)
        # shortest closed route through the start contact: distance to an in-neighbour + 1
        G2, dist, paths = T.shortest_routes(m, f, p, R, cap=2)
        c0 = G.contact(G.e)
        # in-neighbours of c0: contacts whose out-arcs reach c0
        ins = [c for c in dist if any(G.contact(G.mul(paths[c][0][0][-1], s)) == c0 for s in (G.x, G.yx))]
        girth = min(dist[c] for c in ins) + 1 if ins else None
        ok = girth == min(m, f)
        if m == f:
            ok &= min(ties) == m - 1
        res[f"{m},{f}"] = {"directed girth": girth, "first tie": min(ties) if ties else None, "ok": ok}
        if not ok:
            bad.append((m, f))
    return res, bad


def main():
    deps = {p: sha(p) for p in DEPS}
    check("0 dependency bound by hash (PLAIN-TIME-20261108-001B's manifest)", all(DEPS[p] == deps[p] for p in DEPS), deps)
    bad, why = lower_bound_cases(40)
    check("1 Theorem 2's case analysis closes for every type with m, f <= 40 (the 1/m + 1/f <= 1/3 and (3, f) cases are general; "
          "exact rational arithmetic)", not bad, {"uncovered": bad, "cases used (sample)": {k: why[k] for k in list(why)[:12]}})
    readable = [(5, 5), (6, 6), (3, 9), (4, 8), (7, 7), (8, 4), (9, 3), (8, 8), (3, 12), (4, 6), (5, 10), (6, 4), (9, 9), (10, 5),
                (12, 3), (4, 12), (10, 10), (12, 4), (6, 12), (11, 11), (12, 6), (12, 12), (3, 7), (4, 5), (5, 4), (7, 3), (3, 8),
                (4, 10), (6, 9), (8, 3), (9, 6), (10, 4), (3, 10), (4, 7), (7, 4), (10, 3), (3, 11), (11, 3), (6, 8), (8, 6),
                (5, 6), (6, 5)]
    ft, bad = first_ties(readable)
    check("2 Computed: on all 42 readable hyperbolic types (balls to tau + 2, two primes each) the first tie is at tau, two contacts "
          "of two routes each, and the two primes agree", not bad, {"bad": bad, "detail": ft})
    small = [t for t in readable if T.tau_formula(*t) <= 14 and t not in ((6, 9), (9, 6), (4, 10), (10, 4))]
    bg, bad = bigons(small, R_extra=2)
    check("3 Computed: every pair of internally disjoint shortest routes read is thin (no interior vertex, K = cL, distance "
          "c(tau - 1) + 1), and the longest ring and face runs are floor(m(f - 1)/f) and floor(f(m - 1)/m)", not bad,
          {"bad": bad, "detail": bg})
    gq, bad = girth_and_equal([(5, 5), (6, 6), (7, 7), (8, 8), (4, 5), (3, 7), (4, 6), (5, 6), (3, 9), (4, 8)])
    check("4 Theorem 3: the shortest closed route has length min(m, f); for m = f the first tie is at m - 1", not bad,
          {"bad": bad, "detail": gq})
    result = {"ticket": "TIE-LAW-20261109-001A", "artifact_id": "TIE-LAW-20261109-001A-P001", "checks": OUT,
              "status": "passed" if not FAILED else "failed"}
    path = HERE / "result.json"
    if "--write" in sys.argv:
        path.write_text(json.dumps(result, indent=1, default=str) + "\n")
    elif path.is_file():
        old = json.loads(path.read_text())
        print("result.json matches a fresh run:", json.dumps(old["checks"], sort_keys=True, default=str)
              == json.dumps(json.loads(json.dumps(OUT, default=str)), sort_keys=True))
    print("failed:", FAILED)
    return 0 if not FAILED else 1


if __name__ == "__main__":
    sys.exit(main())
