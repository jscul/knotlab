#!/usr/bin/env python3
"""Checks for LOOP-ANY-20261108-001A: balance cancels the feedback in loops of any length.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
Needs numpy (the repository's .venv). 16 worker processes, a few minutes."""
import hashlib
import json
import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "experiments/LOOP-RINGS-20261108-001A/LOOP-RINGS-20261108-001A-E001_closed_loops"))
sys.path.insert(0, str(ROOT / "proofs/SEPARATE-20261108-001A/SEPARATE-20261108-001A-P001_a_cut_separates_a_cycle_needs_two"))
import run as LR  # noqa: E402
import net_lib as N  # noqa: E402

T0 = time.time()
OUT = {}
H = 300


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:400], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def step(rows, r):
    v = 0
    while r:
        low = r & -r
        v ^= rows[low.bit_length() - 1]
        r ^= low
    return v


def witnesses(args):
    """every contact's chain-end witnesses keep coefficient 1 at every lag to H, and every contact binds both rings"""
    s, ks = args
    r = len(ks)
    net = LR.loop_net(s, ks, [(12, 12)] * r)
    rings, Nn, blocks = N.layout(net[0], net[2])
    rows, _, _ = N.matrix(*net)
    for c in range(r):
        wA, wB = rings[c][ks[c] - 1], rings[(c + 1) % r][s - 1]
        ma, mb = N.mask(blocks, c), N.mask(blocks, (c + 1) % r)
        row = 1 << c
        for T in range(1, H + 1):
            row = step(rows, row)
            if not (row >> wA & 1 and row >> wB & 1 and row & ma and row & mb):
                return False
    return True


def balanced_positions(rng, r, s, tries=2000):
    for _ in range(tries):
        ks = [rng.randint(2, s - 2) for _ in range(r)]
        if 2 * sum(ks) == r * s:
            return tuple(ks)
    return None


# exact rational functions over GF(2): polynomials as Python ints (bit i = coefficient of z^i)
def pmul(a, b):
    out = 0
    while b:
        if b & 1:
            out ^= a
        a <<= 1
        b >>= 1
    return out


def pdivmod(a, b):
    q = 0
    db = b.bit_length()
    while a and a.bit_length() >= db:
        sh = a.bit_length() - db
        q ^= 1 << sh
        a ^= b << sh
    return q, a


def pgcd(a, b):
    while b:
        a, b = b, pdivmod(a, b)[1]
    return a


def rnorm(n, d):
    if n == 0:
        return (0, 1)
    g = pgcd(n, d)
    return (pdivmod(n, g)[0], pdivmod(d, g)[0])


def radd(x, y):
    return rnorm(pmul(x[0], y[1]) ^ pmul(y[0], x[1]), pmul(x[1], y[1]))


def rmul(x, y):
    return rnorm(pmul(x[0], y[0]), pmul(x[1], y[1]))


def ppow(p, e):
    out = 1
    for _ in range(e):
        out = pmul(out, p)
    return out


Z, ONE_Z = 0b10, 0b11          # z and 1 + z


def apow(e):
    """a^e = z^e / (1 + z)^e for any integer e"""
    return rnorm(ppow(Z, e), ppow(ONE_Z, e)) if e >= 0 else rnorm(ppow(ONE_Z, -e), ppow(Z, -e))


def m_matrix(s, ks):
    r = len(ks)
    f = [k - 1 for k in ks]
    c = apow(s - 2)
    M = [[(0, 1)] * r for _ in range(r)]
    for i in range(r):
        M[i][(i - 1) % r] = radd(M[i][(i - 1) % r], apow(f[i]))                       # A
        M[(i - 1) % r][i] = radd(M[(i - 1) % r][i], rmul(c, apow(-f[i])))              # c A^-1
    return M


def mmul(X, Y):
    r = len(X)
    out = [[(0, 1)] * r for _ in range(r)]
    for i in range(r):
        for j in range(r):
            acc = (0, 1)
            for k in range(r):
                if X[i][k][0] and Y[k][j][0]:
                    acc = radd(acc, rmul(X[i][k], Y[k][j]))
            out[i][j] = acc
    return out


def is_zero(X):
    return all(e[0] == 0 for row in X for e in row)


def nilpotent_by(s, ks, n):
    M = m_matrix(s, ks)
    P = M
    for m in range(1, n + 1):
        if is_zero(P):
            return m
        P = mmul(P, M)
    return None


def full_persists(args):
    s, ks = args
    r = len(ks)
    net = LR.loop_net(s, ks, [(12, 12)] * r)
    nxt, Nn, blocks = N.state_map(*net)
    cur = np.arange(len(nxt), dtype=np.int64)
    seen = set()
    for T in range(1, 4097):
        cur = nxt[cur]
        key = cur.tobytes()
        if key in seen:
            return True
        seen.add(key)
        for c, (ra, pa, rb, pb, law) in enumerate(net[2]):
            F = ((cur >> c) & 1).astype(np.uint8)
            if F.min() == F.max() or any(N.PL.C.decides_outside(F, *blocks[x], Nn) for x in (ra, rb)):
                return False
    return None


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"] if q.endswith("manifest.json")}
    check("0 dependency artifacts bound by hash; upstream statuses", not bad and all(s_ == "Proved" for s_ in status.values()),
          {"mismatched": bad, "statuses": status})
    rng = random.Random(20261108)
    jobs = []
    for r in range(2, 9):
        for s in range(4, 21):
            for _ in range(12):
                ks = balanced_positions(rng, r, s)
                if ks is not None:
                    jobs.append((s, ks))
            if s % 2 == 0:
                jobs.append((s, (s // 2,) * r))
    with Pool(16) as pool:
        res = pool.map(witnesses, jobs, chunksize=4)
    check("1 Theorem 3's witnesses at every lag to 300, balanced loops of 2 to 8 rings at sizes 4 to 20 (random balanced and antipodal positions)",
          all(res), {"loops": len(jobs), "failures": sum(1 for x in res if not x)})
    jobs = [(s, (s // 2,) * r) for r in range(2, 11) for s in range(4, 17, 2)]
    with Pool(16) as pool:
        res = pool.map(witnesses, jobs, chunksize=2)
    check("2 the antipodal loops of 2 to 10 rings at every even size from 4 to 16", all(res), {"loops": len(jobs), "failures": sum(1 for x in res if not x)})
    cases = {"balanced, 2 rings": (8, (3, 5)), "balanced, 4 rings": (8, (2, 6, 2, 6)), "balanced, 8 rings": (8, (2, 6, 2, 6, 3, 5, 4, 4)),
             "balanced, 3 rings": (8, (4, 4, 4)), "balanced, 5 rings": (8, (2, 6, 4, 4, 4)), "balanced, 6 rings": (6, (2, 4, 3, 3, 2, 4)),
             "balanced, 7 rings": (8, (2, 6, 2, 6, 4, 4, 4)), "unbalanced, 4 rings": (8, (2, 2, 6, 3))}
    found = {}
    for name, (s, ks) in cases.items():
        assert (2 * sum(ks) == len(ks) * s) == name.startswith("balanced")
        found[name] = nilpotent_by(s, ks, 2 * len(ks))
    ok = (found["balanced, 2 rings"] == 1 and found["balanced, 4 rings"] == 2 and found["balanced, 8 rings"] == 4
          and all(found[k] is None for k in ("balanced, 3 rings", "balanced, 5 rings", "balanced, 6 rings", "balanced, 7 rings", "unbalanced, 4 rings")))
    check("3 Theorem 4 by exact rational functions over GF(2): M^(r/2) = 0 for balanced loops of 2, 4 and 8 rings; M^n != 0 up to n = 2r for "
          "balanced loops of 3, 5, 6 and 7 rings and an unbalanced one of 4", ok, {"first power that vanishes (None: none up to 2r)": found})
    with Pool(8) as pool:
        fs = pool.map(full_persists, [(4, (2,) * r) for r in (2, 3, 4, 5)])
    check("4 full state spaces: balanced loops of 2, 3, 4 and 5 rings at size 4 keep every contact persistent", all(x is True for x in fs),
          {"loops": 4, "persistent": sum(1 for x in fs if x is True)})
    out = {"status": "passed", "checks": OUT, "seconds": round(time.time() - T0, 1)}
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
        print("wrote result.json")
    else:
        old = json.loads((HERE / "result.json").read_text())
        same = {k: v["info"] for k, v in old["checks"].items()} == json.loads(json.dumps({k: v["info"] for k, v in OUT.items()}, default=str))
        print("result.json reproduced" if same else "result.json DIFFERS")
        sys.exit(0 if same else 1)
