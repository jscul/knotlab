"""CORNER-ROW-20261110-001A checks (one process, under a minute; run with the workspace's .venv, which has sympy; --write rewrites
result.json).

0 the dependencies bound by hash; 1 Proposition 1 (the row is the walk to the side walls) against ticket C's block inverse; 2 the exact
rows: every recovered rational function reproduces all the walk terms computed, at 4 to 64; 3 the training rows equal the file
committed in 128b2e30d, and the held-out file equals a fresh computation; 4 the held-out predictions P1 to P5 of 128b2e30d (K1 to K3,
K4 at random points, the corner relations) at 4 to 32 and at the held-out side 64; 5 the protocol: commit 128b2e30d holds the verdict
and the predictions and not the side-64 rows; 6 the six entries next to the corners at 4 to 64, and the failure of the two
power-of-two relations at the sides 3, 5 to 7 and 9 to 12; 7 K4 exactly: each wall's Hankel determinant is nonzero at points of
GF(2^31); 8 the spectrum: the reversed minimal polynomial of A^2 on the v contacts at 4 to 32, its factors and exponents against the
row's."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "research/CORNER-ROW-20261110-001"
sys.path.insert(0, str(RES))
sys.path.insert(0, str(ROOT / "proofs/RETURN-LAW-20261110-001A/RETURN-LAW-20261110-001A-P001_the_quadrant_law"))
from heldout64 import bm_fast, exact_row  # noqa: E402
from test64 import Field, tests  # noqa: E402
from return_lib import FastRect, Ring, arch_two_sided  # noqa: E402

DEPS = ["proofs/RETURN-LAW-20261110-001C/RETURN-LAW-20261110-001C-P001_the_box_law_at_every_power_of_two/manifest.json",
        "proofs/REACH-HALVES-20261110-001A/REACH-HALVES-20261110-001A-P001_the_failure_at_every_power_of_two/manifest.json"]
WANT = {DEPS[0]: "c61ddd96ca03326f445645883f786751392a9c0e755dcc7a058cc26d4823e55c",
        DEPS[1]: "1fa0ec2aeb379ac83ad178e1d66ea8f4d86b1934544edb2b0e1c5ef925b9b3d5"}
SIDES = (4, 8, 16, 32, 64)
checks = {}


def rec(name, ok, info=None):
    checks[name] = {"pass": bool(ok), "info": info}
    print(("PASS " if ok else "FAIL ") + name, flush=True)


def pmul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1
        b >>= 1
    return r


def pdivmod(a, b):
    q, db = 0, b.bit_length() - 1
    while a and a.bit_length() - 1 >= db:
        sh = a.bit_length() - 1 - db
        q |= 1 << sh
        a ^= b << sh
    return q, a


def pgcd(a, b):
    while b:
        a, b = b, pdivmod(a, b)[1]
    return a


def reverse(p):
    """s^deg p(1/s), after dividing out the powers of s"""
    while p and not p & 1:
        p >>= 1
    d = p.bit_length() - 1
    return sum(((p >> k) & 1) << (d - k) for k in range(d + 1))


def series(num, den, K):
    """coefficients below s^K of num/den over GF(2), den(0) = 1"""
    out, rem = 0, num
    for k in range(K):
        if (rem >> k) & 1:
            out |= 1 << k
            rem ^= den << k
    return out


def rows():
    train = json.loads((RES / "rows_training.json").read_text())
    held = json.loads((RES / "rows_heldout64.json").read_text())
    return {n: (train[str(n)] if n != 64 else held["64"]) for n in SIDES}


def frac(row, key):
    return int(row[key]["num"], 16), int(row[key]["den"], 16)


def same(f, g):
    return pmul(f[0], g[1]) == pmul(g[0], f[1])


def one_plus_L(n):
    """1 + L(s^2) = 1 + s^2 + s^4 + s^8 + ... + s^(2n)"""
    p, j = 1, 1
    while j <= n:
        p |= 1 << (2 * j)
        j *= 2
    return p


def check0():
    got = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in DEPS}
    rec("0 dependencies bound by hash (RETURN-LAW-20261110-001C, REACH-HALVES-20261110-001A manifests)", got == WANT, got)


def check1():
    ok, info = True, {}
    T = 40
    R = Ring(T)
    for n in (4, 8, 16):
        E, _ = arch_two_sided(R, n)
        N = 2 * n - 2
        B = FastRect(N, N)
        L = n - 1
        good = True
        for X, col in (("L", 0), ("R", N)):
            for b in range(L):
                d = B.series((0, 1), (col, 2 * b + 1), 2 * T)
                good &= sum(((d >> (2 * k)) & 1) << k for k in range(T)) == E[0][(0 if X == "L" else L) + b]
        info[n] = good
        ok &= good
    rec("1 Proposition 1: the corner row of K_n^-1 is the walk series from c to the v contacts of the two side walls (to s^40 at 4, 8, 16)",
        ok, info)


def check2():
    ok, info = True, {}
    for n in SIDES:
        row = exact_row(n)
        N = 2 * n - 2
        B = FastRect(N, N)
        K = 8 * n * (n - 1) + 8 * n
        good = all(v["L"] <= n * (n - 1) for v in row.values())
        for key, v in row.items():
            X, b = key[0], int(key[1:])
            d = B.series((0, 1), (0 if X == "L" else N, 2 * b + 1), K)
            even = sum(((d >> (2 * k)) & 1) << k for k in range(K // 2))
            good &= series(int(v["num"], 16), int(v["den"], 16), K // 2) == even
        info[n] = {"exact": good, "largest complexity": max(v["L"] for v in row.values()), "bound": n * (n - 1)}
        ok &= good
    rec("2 the exact rows: every recovered rational function reproduces all 4n^2 walk terms computed in s (more than four times the "
        "complexity bound n(n - 1), the number of v contacts), at 4, 8, 16, 32 and 64", ok, info)


def check3():
    try:
        blob = subprocess.run(["git", "show", "128b2e30d:research/CORNER-ROW-20261110-001/rows_training.json"], cwd=ROOT,
                              capture_output=True, text=True, check=True).stdout
    except subprocess.CalledProcessError as e:
        rec("3 the training rows (commit 128b2e30d)", False, str(e))
        return
    train = json.loads(blob)
    held = json.loads((RES / "rows_heldout64.json").read_text())
    ok = all(exact_row(int(n)) == train[n] for n in ("4", "8", "16", "32")) and exact_row(64) == held["64"]
    rec("3 the training rows equal rows_training.json as committed in 128b2e30d, and rows_heldout64.json equals a fresh computation", ok)


def check4():
    ok, info = True, {}
    for n, row in rows().items():
        res = tests(n, row)
        good = all(res[p] for p in ("P1", "P2", "P3", "P4", "P5"))
        info[n] = res
        ok &= good
    rec("4 the predictions of 128b2e30d: K1 (the denominators' factors are exactly the classes K(a) != 0 of GF(2n)), K2 (perfect "
        "squares), K3 (largest exponent 2 ceil(|K|/8)), K4 at random points of GF(2^31) (recurrence order n/2 along each wall) and P5 "
        "(the relations next to the corners), at 4 to 32 and at the held-out side 64", ok, info)


def check5():
    try:
        names = subprocess.run(["git", "show", "--name-only", "--format=", "128b2e30d"], cwd=ROOT, capture_output=True, text=True,
                               check=True).stdout.split()
        text = subprocess.run(["git", "show", "128b2e30d:proofs/CORNER-ROW-20261110-001A/CORNER-ROW-20261110-001A-P001_the_corner_row/proof.md"],
                              cwd=ROOT, capture_output=True, text=True, check=True).stdout
    except subprocess.CalledProcessError as e:
        rec("5 the protocol (commit 128b2e30d)", False, str(e))
        return
    ok = ("research/CORNER-ROW-20261110-001/rows_heldout64.json" not in names and "Held-out predictions for side 64" in text
          and all(f"**P{i}.**" in text for i in range(1, 6)) and "no pattern" in text)
    rec("5 the protocol: commit 128b2e30d records the verdict and P1 to P5 and does not contain the side-64 rows", ok,
        {"files": names})


def check6():
    ok, info = True, {}
    for n, row in rows().items():
        D = one_plus_L(n)
        near = (pmul(1 << (n - 1), D) ^ (1 << (3 * n - 1)), D)          # s^(n-1) + s^(3n-1)/(1 + L(s^2))
        want = {"L0": (1, D), f"R{n - 2}": (1 << (2 * n - 1), D), f"L{n - 2}": (1 << n, D), "R0": near,
                "R1": frac(row, f"L{n - 2}"), f"L{n - 3}": frac(row, "R0")}
        good = all(same(frac(row, k), v) for k, v in want.items())
        info[n] = {"rules": good, "entries": len(row), "with a rule": len(want)}
        ok &= good
    other = {}
    for n in (3, 5, 6, 7, 9, 10, 11, 12):
        row = exact_row(n)
        other[n] = {"rho_(R,1) = rho_(L,n-2)": same(frac(row, "R1"), frac(row, f"L{n - 2}")),
                    "rho_(L,n-3) = rho_(R,0)": same(frac(row, f"L{n - 3}"), frac(row, "R0"))}
        ok &= not any(other[n].values())
    info["other sides"] = other
    rec("6 the six entries next to the corners: rho_(L,0) = 1/(1 + L(s^2)), rho_(R,n-2) = s^(2n-1) rho_(L,0), rho_(L,n-2) = s^n rho_(L,0), "
        "rho_(R,0) = s^(n-1) + s^(3n-1) rho_(L,0), rho_(R,1) = rho_(L,n-2), rho_(L,n-3) = rho_(R,0), exactly at 4 to 64; the last two "
        "relations fail at every side 3, 5 to 7 and 9 to 12", ok, info)


# GF(2^31) = GF(2)[x]/(x^31 + x^3 + 1); it meets GF(2^r), r <= 7, only in GF(2), so no denominator vanishes at a point outside GF(2)
MOD31 = (1 << 31) | (1 << 3) | 1


def m31(a, b):
    x = 0
    while b:
        if b & 1:
            x ^= a
        b >>= 1
        a <<= 1
        if a >> 31:
            a ^= MOD31
    return x


def inv31(a):
    x, e = 1, (1 << 31) - 2
    while e:
        if e & 1:
            x = m31(x, a)
        a = m31(a, a)
        e >>= 1
    return x


def ev31(poly, a):
    v, p = 0, 1
    for k in range(poly.bit_length()):
        if (poly >> k) & 1:
            v ^= p
        p = m31(p, a)
    return v


def rank31(M):
    M = [r[:] for r in M]
    rank, cols = 0, len(M[0])
    for c in range(cols):
        piv = next((i for i in range(rank, len(M)) if M[i][c]), None)
        if piv is None:
            continue
        M[rank], M[piv] = M[piv], M[rank]
        iv = inv31(M[rank][c])
        M[rank] = [m31(iv, x) for x in M[rank]]
        for i in range(len(M)):
            if i != rank and M[i][c]:
                f = M[i][c]
                M[i] = [x ^ m31(f, y) for x, y in zip(M[i], M[rank])]
        rank += 1
    return rank


def check7():
    """A sequence u_0..u_(2k-2) over a field has linear complexity exactly k when its k x k Hankel matrix [u_(i+j)] is nonsingular: no
    recurrence of length k - 1 (its k x k system has no left kernel), hence none shorter, and one of length k (k - 1 equations in k
    unknowns, of full rank). Over GF(2)(s) the determinant is a rational function; it is nonzero if it is nonzero at one point where
    every entry is defined."""
    ok, info = True, {}
    for n, row in rows().items():
        k = n // 2
        got = {}
        for X in "LR":
            for s0 in (2, 3, 0x2545F491):
                vals = []
                for b in range(n - 1):
                    num, den = frac(row, f"{X}{b}")
                    dv = ev31(den, s0)
                    assert dv, "a denominator vanished in GF(2^31)"
                    vals.append(m31(ev31(num, s0), inv31(dv)))
                got[f"{X} at {hex(s0)}"] = rank31([[vals[i + j] for j in range(k)] for i in range(k)])
        good = any(v == k for key, v in got.items() if key.startswith("L")) and any(v == k for key, v in got.items() if key.startswith("R"))
        info[n] = {"n/2": k, "Hankel ranks": got}
        ok &= good
    rec("7 K4 exactly: along each wall the n - 1 entries have linear complexity exactly n/2 over GF(2)(s) (their n/2 x n/2 Hankel "
        "determinant is nonzero at a point of GF(2^31)), at 4 to 64", ok, info)


def class_polys(F):
    """each class of GF(2^r)* (keyed by its least element) and its minimal polynomial over GF(2)"""
    out, seen = {}, set()
    for a in range(1, F.q):
        if a in seen:
            continue
        orb, x = [], a
        while x not in orb:
            orb.append(x)
            x = F.mul(x, x)
        seen |= set(orb)
        poly = [1]
        for r in orb:
            new = [0] * (len(poly) + 1)
            for i, c in enumerate(poly):
                new[i + 1] ^= c
                new[i] ^= F.mul(c, r)
            poly = new
        out[a] = sum(c << i for i, c in enumerate(poly))
    return out


def exponent(p, f):
    e = 0
    while True:
        q, r = pdivmod(p, f)
        if r:
            return e
        p, e = q, e + 1


def check8():
    """the minimal polynomial mu of A^2 on the v contacts: the lcm of the minimal polynomials of scalar sequences u A^(2k) x (each a
    divisor of mu, by Berlekamp-Massey on 2d + 4 terms), then mu(A^2) = 0 checked on every v contact, so the lcm is mu itself"""
    import random
    ok, info = True, {}
    allrows = rows()
    for n in (4, 8, 16, 32):
        N = 2 * n - 2
        B = FastRect(N, N)
        vs = [B.idx(2 * a, 2 * b + 1) for a in range(n) for b in range(n - 1)]
        vmask = sum(1 << i for i in vs)
        d = len(vs)
        random.seed(n)
        mu = 1
        for _ in range(24):
            x = random.getrandbits(B.W * (N + 1)) & vmask
            u = random.getrandbits(B.W * (N + 1)) & vmask
            seq = []
            for _ in range(2 * d + 4):
                seq.append(bin(x & u).count("1") & 1)
                x = B.step(B.step(x))
            C, L = bm_fast(seq)
            m = reverse(C) << (L - (reverse(C).bit_length() - 1))      # the recurrence's characteristic polynomial, degree L
            g = pgcd(mu, m)
            mu = pmul(pdivmod(mu, g)[0], m)
        deg = mu.bit_length() - 1
        zero = True
        for i in vs:
            y = 0
            for k in range(deg, -1, -1):
                y = B.step(B.step(y))
                if (mu >> k) & 1:
                    y ^= 1 << i
            zero &= y == 0
        F = Field(n.bit_length())
        K = F.kloosterman()
        cls = class_polys(F)
        rv, left = reverse(mu), reverse(mu)
        spec, rowexp = {}, {}
        for a, f in cls.items():
            e = exponent(rv, f)
            for _ in range(e):
                left = pdivmod(left, f)[0]
            spec[a] = e
            rowexp[a] = max(exponent(int(v["den"], 16), f) for v in allrows[n].values())
        good = (zero and left == 1
                and all(spec[a] == (abs(K[a]) // 2 if K[a] else 0) for a in cls)
                and all(pdivmod(rv, int(v["den"], 16))[1] == 0 for v in allrows[n].values())
                and all(rowexp[a] == 2 * (-(-abs(K[a]) // 8)) for a in cls))
        # the corner entry 1/(1 + L(s^2)) = 1/(1 + L(s))^2 sees exactly the classes with Tr(a) = 1
        good &= all((exponent(one_plus_L(n), f) > 0) == (F.tr(a) == 1) for a, f in cls.items())
        info[n] = {"mu(A^2) = 0": zero, "deg mu": deg, "d": d,
                   "classes (K, exponent in mu, largest exponent in the row)": {a: (K[a], spec[a], rowexp[a]) for a in cls}}
        ok &= good
    rec("8 the spectrum: the reversed minimal polynomial of A^2 on the v contacts is the product of m_a^(|K(a)|/2) over the classes with "
        "K(a) != 0, every reduced denominator of the row divides it, the row's largest exponent 2 ceil(|K|/8) is below |K|/2 from |K| = 8, "
        "and the corner entry sees exactly the classes with Tr(a) = 1 (4 to 32)", ok, info)


if __name__ == "__main__":
    for c in (check0, check1, check2, check3, check4, check5, check6, check7, check8):
        c()
    allok = all(v["pass"] for v in checks.values())
    print("ALL PASS" if allok else "SOME FAIL")
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps({"schema_version": 1, "artifact": "CORNER-ROW-20261110-001A-P001", "checks": checks,
                                                      "status": "passed" if allok else "failed"}, indent=2, default=str) + "\n")
