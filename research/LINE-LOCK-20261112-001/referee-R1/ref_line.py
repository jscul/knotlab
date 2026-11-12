#!/usr/bin/env python3
"""Referee LINE-LOCK-R1: the census of stitch pairs, rebuilt with the referee's own code (ref_lib.py of the BASES-WITHIN referee
folder for the harmonies of span at most 8, now with no period bound; no import of line_lib.py, nest_lib.py or check.py).

    python3 -B ref_line.py      (writes result_line.json)

For each harmony: its states W (n-periodic words as bit masks), its kinds; the one-order stitch R(u, v, w): for every kind (0, a, b)
and place i, not all of u(i), v(i + a), w(i + b) equal. For each orbit O of <shift, flip>: the group Q acting on O (Z_p, or Z_p x Z_2
when the flip is not a shift on O), the stitch pairs A = {(y, z) in Q^2 : R(u, y u, z u)}, every cyclic subgroup of Q^2 inside A, every
coset d + L inside A with d outside L (L cyclic, not trivial), each classified at every odd prime q of its order: degenerate when its
order-q part lies in {(a, 0)}, {(a, a)} or {(0, b)}, genuine (a ratio) otherwise; free pairs {0, h}^2 inside A; and for each harmony
whether some state has a free site (a place every knot through which has its other two members opposite).
The odd step sets are the 7 of ODD-FAMILY-20261112-001 (n, S): kinds (0, a, b), 0 < a < b < n, whose residues {0, a, b} are a translate
of {0, s, 2s} for some s in S; states enumerated by SAT on the cyclic block."""
import itertools
import json
import math
import sys
import time
from pathlib import Path

from pysat.solvers import Glucose4

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "BASES-WITHIN-20261112-001" / "referee-R1"))
import ref_lib as R  # noqa: E402

ODD_SETS = [(61, (1, 2, 11, 22, 39, 50, 59, 60)), (61, (1, 11, 25, 30, 31, 36, 50, 60)),
            (73, (1, 2, 19, 27, 46, 54, 71, 72)), (73, (1, 23, 27, 36, 37, 46, 50, 72)),
            (193, (1, 2, 31, 54, 65, 81, 112, 128, 139, 162, 191, 192)), (193, (1, 3, 25, 50, 81, 95, 98, 112, 143, 168, 190, 192)),
            (193, (1, 27, 56, 64, 81, 96, 97, 112, 129, 137, 166, 192))]


def rot(x, s, P):
    s %= P
    return x if s == 0 else ((x >> s) | (x << (P - s))) & ((1 << P) - 1)


def stitch(u, v, w, kinds, P):
    full = (1 << P) - 1
    for a, b in kinds:
        va, wb = rot(v, a, P), rot(w, b, P)
        if (u & va & wb) or ((u | va | wb) != full):
            return False
    return True


def odd_harmony(n, S):
    kinds = sorted({(a, b) for a in range(1, n) for b in range(a + 1, n) for s in S for t in range(n)
                    if sorted(((0 - t) % n, (a - t) % n, (b - t) % n)) == sorted((0, s % n, (2 * s) % n))})
    # states: words on Z_n non-constant on every {x, x + s, x + 2s}
    cl = []
    for s in S:
        for x in range(n):
            t = [x + 1, (x + s) % n + 1, (x + 2 * s) % n + 1]
            cl += [t, [-y for y in t]]
    W = []
    with Glucose4(bootstrap_with=cl) as so:
        while so.solve():
            m = so.get_model()
            W.append(sum(1 << i for i in range(n) if m[i] > 0))
            so.add_clause([-l for l in m[:n]])
    return {"name": f"odd {n} {list(S)}", "P": n, "kinds": kinds, "W": sorted(W)}


def span8_harmonies():
    out = []
    for h in R.harmonies(max_span=8, max_period=10 ** 6):
        W = sorted(sum(b << i for i, b in enumerate(w)) for w in R.states(h))
        out.append({"name": " + ".join(h["orbits"]), "P": h["P"], "kinds": [tuple(k) for k in h["kinds"]], "W": W})
    return out


def free_site(h):
    P, kinds = h["P"], h["kinds"]
    for w in h["W"]:
        bit = lambda i: (w >> (i % P)) & 1
        for i in range(P):
            ok = True
            for a, b in kinds:
                for others in ((i + a, i + b), (i - a, i - a + b), (i - b, i - b + a)):
                    if bit(others[0]) == bit(others[1]):
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                return [w, i]
    return None


def orbits(h):
    P = h["P"]
    full = (1 << P) - 1
    left = set(h["W"])
    out = []
    while left:
        u = min(left)
        orb = {rot(u, s, P) ^ (full if e else 0) for s in range(P) for e in (0, 1)}
        left -= orb
        out.append((u, orb))
    return out


def analyse_orbit(h, u, orb):
    P, kinds = h["P"], h["kinds"]
    full = (1 << P) - 1
    p = min(s for s in range(1, P + 1) if rot(u, s, P) == u)
    anti = any(rot(u, s, P) == u ^ full for s in range(P))
    # Q as Z_p (flip a shift on O) or Z_p x Z_2; act(g, x)
    if anti:
        Q = [(a, 0) for a in range(p)]
        act = lambda g, x: rot(x, g[0], P)
        add = lambda g, k: ((g[0] + k[0]) % p, 0)
        mul = lambda g, m: ((g[0] * m) % p, 0)
    else:
        Q = [(a, e) for a in range(p) for e in (0, 1)]
        act = lambda g, x: rot(x, g[0], P) ^ (full if g[1] else 0)
        add = lambda g, k: ((g[0] + k[0]) % p, (g[1] + k[1]) % 2)
        mul = lambda g, m: ((g[0] * m) % p, (g[1] * m) % 2)
    assert len({act(g, u) for g in Q}) == len(Q) == len(orb)
    A = {(y, z) for y in Q for z in Q if stitch(u, act(y, u), act(z, u), kinds, P)}
    zero = Q[0]

    def order(g):
        m, x = 1, g
        while x != (zero, zero):
            x = (add(x[0], g[0]), add(x[1], g[1]))
            m += 1
        return m

    def cyc(g):
        out, x = [(zero, zero)], g
        while x != (zero, zero):
            out.append(x)
            x = (add(x[0], g[0]), add(x[1], g[1]))
        return out

    def classify(g):
        m = order(g)
        res = []
        for q in range(3, m + 1, 2):
            if m % q or any(q % r == 0 for r in range(3, int(q ** 0.5) + 1, 2)):
                continue
            y, z = mul(g[0], m // q), mul(g[1], m // q)
            if y == zero or z == zero or y == z:
                res.append([q, "degenerate"])
            else:
                lam = next(l for l in range(2, q) if mul(y, l) == z) if any(mul(y, l) == z for l in range(2, q)) else None
                res.append([q, "genuine", lam])
        return res
    subs = {}
    for g in A:
        if g == (zero, zero):
            continue
        C = cyc(g)
        if all(x in A for x in C):
            subs[frozenset(C)] = g
    cosets = {}
    Al = list(A)
    for d in Al:
        for d2 in Al:
            g = ((d2[0][0] - d[0][0]) % p, (d2[0][1] - d[0][1]) % 2), ((d2[1][0] - d[1][0]) % p, (d2[1][1] - d[1][1]) % 2)
            if anti:
                g = ((g[0][0], 0), (g[1][0], 0))
            if g == (zero, zero):
                continue
            C = cyc(g)
            if (d[0], d[1]) in C:
                continue
            co = frozenset((add(d[0], x[0]), add(d[1], x[1])) for x in C)
            if co <= A:
                cosets[co] = (d, g)
    free_pairs = [h_ for h_ in Q if h_ != zero and order((h_, zero)) == 2 and
                  all((x, y) in A for x in (zero, h_) for y in (zero, h_))]
    genuine_sub = [[list(map(list, g)), classify(g)] for C, g in subs.items() if any(c[1] == "genuine" for c in classify(g))]
    genuine_cos = [[list(map(list, d)), list(map(list, g)), classify(g)] for co, (d, g) in cosets.items()
                   if any(c[1] == "genuine" for c in classify(g))]
    return {"orbit period": p, "antiperiodic": anti, "|Q|": len(Q), "|A|": len(A), "cyclic subgroups inside": len(subs),
            "subgroup classes": sorted({json.dumps(classify(g)) for g in subs.values()}),
            "cosets inside": len(cosets), "coset classes": sorted({json.dumps(classify(g)) for d, g in cosets.values()}),
            "genuine subgroups": genuine_sub, "genuine cosets": genuine_cos, "free pairs": [list(x) for x in free_pairs]}


def main():
    t0 = time.time()
    hs = span8_harmonies()
    print("span <= 8 harmonies:", len(hs), flush=True)
    hs += [odd_harmony(n, S) for n, S in ODD_SETS]
    rows = []
    for h in hs:
        t = time.time()
        orbs = orbits(h)
        rows.append({"harmony": h["name"], "P": h["P"], "states": len(h["W"]), "kinds": len(h["kinds"]), "free site": free_site(h),
                     "orbits": [analyse_orbit(h, u, o) for u, o in orbs], "seconds": round(time.time() - t, 1)})
        print(h["name"][:50], h["P"], len(h["W"]), len(orbs), rows[-1]["seconds"], flush=True)
    summ = {"harmonies": len(rows), "orbits": sum(len(r["orbits"]) for r in rows),
            "orbits with an odd prime in their period": sum(1 for r in rows for o in r["orbits"] if any(o["orbit period"] % q == 0 for q in range(3, o["orbit period"] + 1, 2))),
            "free sites": sum(1 for r in rows if r["free site"]),
            "cyclic subgroups inside": sum(o["cyclic subgroups inside"] for r in rows for o in r["orbits"]),
            "genuine subgroups": sum(len(o["genuine subgroups"]) for r in rows for o in r["orbits"]),
            "cosets inside": sum(o["cosets inside"] for r in rows for o in r["orbits"]),
            "genuine cosets": sum(len(o["genuine cosets"]) for r in rows for o in r["orbits"]),
            "free pairs": sum(len(o["free pairs"]) for r in rows for o in r["orbits"]),
            "odd harmonies: |A| per orbit": [[r["harmony"], [o["|A|"] for o in r["orbits"]]] for r in rows if r["harmony"].startswith("odd")]}
    (HERE / "result_line.json").write_text(json.dumps({"summary": summ, "rows": rows}, indent=1) + "\n")
    print(json.dumps(summ, indent=1))
    print("done", round(time.time() - t0, 1), "s")


if __name__ == "__main__":
    main()
