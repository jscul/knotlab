#!/usr/bin/env python3
"""Referee (even_referee.py) for EVEN-PERIOD-20261112-001A, fresh code: it imports nothing from even_lib and reads only
result_census.json and result_control.json.

R1. Periods 3 to 19 recomputed in full by brute force: every word of minimal period p that is its own least rotation; its residue
    pairs, its flippable residues, and, if it has none, a compatible flippable word searched among all 2^p words (numpy). The counts
    of each class must equal the census's, and no word may lack a certificate.
R2. Every certificate the census reports at periods 21 to 29 checked directly: compatible with the word's pairs, flippable at its
    residue.
R3. A random sample of 300 words at each period 21 to 29 recomputed with its own SAT encoding (minisat22): each must have a
    certificate.
R4. Lemma 3 on actual bases: for every word of odd period up to 11 with some pair, and every span 3 to 14, the base of all kinds of
    that span the word allows also allows its certificate with one value flipped (every knot checked on a window around the flip)."""
import itertools
import json
import random
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent


def min_rot(t):
    return min(t[r:] + t[:r] for r in range(len(t)))


def lyndon_brute(p):
    out = []
    for n in range(1 << p):
        t = tuple((n >> (p - 1 - i)) & 1 for i in range(p))
        if any(t == t[d:] + t[:d] for d in range(1, p)):
            continue
        if min_rot(t) == t:
            out.append(t)
    return out


def pairs_of(u):
    p = len(u)
    return [(al, be) for al in range(p) for be in range(p)
            if all(not (u[r] == u[(r + al) % p] == u[(r + be) % p]) for r in range(p))]


def blocked(c, G, r0):
    p = len(c)
    for al, be in G:
        for x, y in (((r0 + al) % p, (r0 + be) % p), ((r0 - al) % p, (r0 - al + be) % p), ((r0 - be) % p, (r0 - be + al) % p)):
            if c[x] == c[y] and c[x] != c[r0]:
                return True
    return False


def fits(c, G):
    p = len(c)
    return all(not (c[r] == c[(r + al) % p] == c[(r + be) % p]) for r in range(p) for al, be in G)


def brute_certificate(u, G):
    p = len(u)
    allw = ((np.arange(1 << p)[:, None] >> np.arange(p)[None, :]) & 1).astype(np.int8)
    ok = np.ones(len(allw), dtype=bool)
    for al, be in G:
        for r in range(p):
            a, b = allw[:, r], allw[:, (r + al) % p]
            ok &= ~((a == b) & (b == allw[:, (r + be) % p]))
    for idx in np.nonzero(ok)[0]:
        c = tuple(int(x) for x in allw[idx])
        for r0 in range(p):
            if not blocked(c, G, r0):
                return c, r0
    return None


def sat_certificate(u, G):
    from pysat.solvers import Minisat22
    p = len(u)
    for r0 in range(p):
        with Minisat22() as s:
            for al, be in G:
                for r in range(p):
                    t = sorted({r, (r + al) % p, (r + be) % p})
                    s.add_clause([i + 1 for i in t])
                    s.add_clause([-(i + 1) for i in t])
                for x, y in (((r0 + al) % p, (r0 + be) % p), ((r0 - al) % p, (r0 - al + be) % p), ((r0 - be) % p, (r0 - be + al) % p)):
                    s.add_clause(sorted({-(x + 1), -(y + 1), r0 + 1}))
                    s.add_clause(sorted({x + 1, y + 1, -(r0 + 1)}))
            if s.solve():
                m = s.get_model()
                return tuple(int(m[i] > 0) for i in range(p)), r0
    return None


def r1(census):
    out, bad = {}, []
    for p in range(3, 20, 2):
        tally = Counter()
        for u in lyndon_brute(p):
            G = pairs_of(u)
            if not G:
                tally["no kind"] += 1
                continue
            if any(not blocked(u, G, r) for r in range(p)):
                tally["self"] += 1
                continue
            cert = brute_certificate(u, G)
            tally["other" if cert else "none"] += 1
        theirs = census[p]["tally"]
        if dict(tally) != theirs:
            bad.append((p, dict(tally), theirs))
        out[str(p)] = dict(tally)
    return {"counts": out, "disagreements": bad}


def r2(census):
    bad, n = [], 0
    for p in range(21, 30, 2):
        for row in census[p]["certified by another word"]:
            u = tuple(int(x) for x in row["u"]); c = tuple(int(x) for x in row["c"]); r0 = row["residue"]
            G = pairs_of(u)
            n += 1
            if not (fits(c, G) and not blocked(c, G, r0)):
                bad.append(row)
    return {"certificates checked": n, "bad": bad}


def r3():
    rng = random.Random(20261112)
    out, bad = {}, []
    for p in range(21, 30, 2):
        tally = Counter()
        for _ in range(300):
            while True:
                t = tuple(rng.randint(0, 1) for _ in range(p))
                if not any(t == t[d:] + t[:d] for d in range(1, p)):
                    break
            u = min_rot(t)
            G = pairs_of(u)
            if not G:
                tally["no kind"] += 1
            elif any(not blocked(u, G, r) for r in range(p)):
                tally["self"] += 1
            else:
                cert = sat_certificate(u, G)
                tally["other" if cert else "none"] += 1
                if not cert:
                    bad.append("".join(map(str, u)))
        out[str(p)] = dict(tally)
    return {"sample": out, "without certificate": bad}


def r4():
    bad, n = [], 0
    for p in range(3, 12, 2):
        for u in lyndon_brute(p):
            G = pairs_of(u)
            if not G:
                continue
            cert = None
            for r0 in range(p):
                if not blocked(u, G, r0):
                    cert = (u, r0)
                    break
            if cert is None:
                cert = brute_certificate(u, G)
            c, r0 = cert
            for W in range(3, 15):
                K = [(a, b) for a in range(1, W + 1) for b in range(a + 1, W + 1) if (a % p, b % p) in set(G)]
                if not K:
                    continue
                n += 1
                z = lambda i: c[i % p] ^ (1 if i == r0 else 0)
                for a, b in K:
                    for i in range(r0 - 2 * W, r0 + 2 * W):
                        if z(i) == z(i + a) == z(i + b):
                            bad.append(("".join(map(str, u)), W, a, b, i))
                            break
    return {"bases checked": n, "violations": bad[:10], "number": len(bad)}


def main():
    census = {r["p"]: r for r in json.loads((HERE / "result_census.json").read_text())["checks"]["result"]["rows"]}
    out = {"R1": r1(census), "R2": r2(census), "R3": r3(), "R4": r4()}
    out["passed"] = (not out["R1"]["disagreements"] and all("none" not in v for v in out["R1"]["counts"].values())
                     and not out["R2"]["bad"] and not out["R3"]["without certificate"] and out["R4"]["number"] == 0)
    (HERE / "referee.json").write_text(json.dumps(out, indent=1) + "\n")
    print("referee passed" if out["passed"] else "referee FAILED")
    sys.exit(0 if out["passed"] else 1)


if __name__ == "__main__":
    main()
