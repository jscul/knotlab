"""RETURN-LAW-20261110-001C checks (one process, about ten seconds; --write rewrites result.json).

0 the dependencies bound by hash; 1 Theorem 7 (the two-sided column decomposition) against the walk; 2 Proposition 8 (the
first-passage series at a power of two); 3 Proposition 9 (the looped path); 4 computed: C1 exactly at 4 to 256, C2's failures,
C3 at 3 to 64, the four-corner formula at 4 to 64, the corner orbit's period at 4 to 128; 5 Corollary 10 (interior targets)
against the walk, with the two targets of the count of REACH-HALVES-20261110-001A (B137) at 8 and 16."""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/RETURN-LAW-20261110-001A/RETURN-LAW-20261110-001A-P001_the_quadrant_law"))
from return_lib import (FastRect as Rect, Ring, arch_two_sided, box_law_sequence, catalan2, corner_returns, det_looped_path, det_path,  # noqa: E402
                        first_passage, lower, path, pinv, pmul, spread, trace_poly, truncated_catalan)

DEPS = ["proofs/REACH-HALVES-20261110-001A/REACH-HALVES-20261110-001A-P001_the_failure_at_every_power_of_two/manifest.json",
        "proofs/FULL-REACH-PROOF-20261108-001A/FULL-REACH-PROOF-20261108-001A-P001_symmetries_the_torus_and_powers_of_two/manifest.json"]
WANT = {DEPS[0]: "1fa0ec2aeb379ac83ad178e1d66ea8f4d86b1934544edb2b0e1c5ef925b9b3d5",
        DEPS[1]: "affc32533a4d960bd72b879ef5870513fe8ffaad5614bf296900aa27d5d618d0"}
checks = {}


def rec(name, ok, info=None):
    checks[name] = {"pass": bool(ok), "info": info}
    print(("PASS " if ok else "FAIL ") + name, flush=True)


def check0():
    got = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in DEPS}
    rec("0 dependencies bound by hash (REACH-HALVES-20261110-001A, FULL-REACH-PROOF-20261108-001A manifests)", got == WANT, got)


def halve(d, T):
    return sum(((d >> (2 * k)) & 1) << k for k in range(T))


def check1():
    ok, info = True, {}
    T = 60
    R = Ring(T)
    for n in range(2, 13):
        E, _ = arch_two_sided(R, n)
        d = corner_returns(2 * n - 2, 2 * n - 2, 2 * T)
        good = E[0][0] == halve(d, T)
        info[n] = good
        ok &= good
    # over the integers, with signs, at n = 3, 4, 5 to s^18
    T = 18

    def zmul(a, b):
        out = [0] * T
        for i, x in enumerate(a):
            if x:
                for j in range(T - i):
                    out[i + j] += x * b[j]
        return out

    def zmm(A, B):
        n, m, k = len(A), len(B[0]), len(B)
        C = [[[0] * T for _ in range(m)] for _ in range(n)]
        for i in range(n):
            for l in range(k):
                if any(A[i][l]):
                    for j in range(m):
                        if any(B[l][j]):
                            C[i][j] = [x + y for x, y in zip(C[i][j], zmul(A[i][l], B[l][j]))]
        return C

    def zeye(n):
        return [[[1 if i == j and t == 0 else 0 for t in range(T)] for j in range(n)] for i in range(n)]

    def zadd(A, B, c=1):
        return [[[x + c * y for x, y in zip(A[i][j], B[i][j])] for j in range(len(A[0]))] for i in range(len(A))]

    def zinv(N):  # (I - N)^-1, N = O(s)
        n = len(N)
        R, P = zeye(n), zeye(n)
        for _ in range(T):
            P = zmm(P, N)
            if not any(any(any(c) for c in r) for r in P):
                break
            R = zadd(R, P)
        return R

    def smat(M, k):
        return [[[M[i][j] if t == k else 0 for t in range(T)] for j in range(len(M[0]))] for i in range(len(M))]

    for n in (3, 4, 5):
        L = n - 1
        # N_XY(h) over Z by direct count on the column path [0, n - 1]
        NLL, NLR = [0] * T, [0] * T
        for start, store in ((0, None),):
            cur = {start: 1}
            for h in range(1, T):
                nxt = {}
                for a, c in cur.items():
                    for b2 in (a - 1, a + 1):
                        if 0 <= b2 <= n - 1:
                            nxt[b2] = nxt.get(b2, 0) + c
                NLL[h] = nxt.get(0, 0)
                NLR[h] = nxt.get(n - 1, 0)
                cur = {a: c for a, c in nxt.items() if 1 <= a <= n - 2}
        Q = zinv(smat(path(L), 1))                       # (I - sP)^-1
        def S(Nh):
            tot = [[[0] * T for _ in range(L)] for _ in range(L)]
            Pw = zeye(L)                                 # (I - sP)^-(h - 1), h = 1, 2, ...
            for h in range(1, T):
                if Nh[h]:
                    sh = [[[0] * h + Pw[i][j][:T - h] for j in range(L)] for i in range(L)]
                    tot = zadd(tot, sh, Nh[h])
                Pw = zmm(Pw, Q)
            return tot
        SLL, SLR = S(NLL), S(NLR)
        top = zadd(smat(lower(L), 1), SLL)
        bot = zadd(smat([[1 if j == i + 1 else 0 for j in range(L)] for i in range(L)], 1), SLL)
        N = [top[i] + SLR[i] for i in range(L)] + [SLR[i] + bot[i] for i in range(L)]
        E = zinv(N)
        # the walk A itself on the box [0, 2n - 2]^2, over the integers: returns of c = (0, 1) at the even times 2k
        Nb = 2 * n - 2
        cur = {(0, 1): 1}
        direct = []
        for k in range(2 * T):
            if k % 2 == 0:
                direct.append(cur.get((0, 1), 0))
            nxt = {}
            for (X, Y), c in cur.items():
                for q in ([(X - 1, Y - 1), (X + 1, Y + 1)] if X % 2 else [(X + 1, Y - 1), (X - 1, Y + 1)]):
                    if 0 <= q[0] <= Nb and 0 <= q[1] <= Nb:
                        nxt[q] = nxt.get(q, 0) + c
            cur = nxt
        good = E[0][0] == direct
        info[f"integers {n}"] = good
        ok &= good
    rec("1 Theorem 7: the box's corner series is the (L, 0) entry of K_n^-1 (over GF(2) to s^60 at the sides 2 to 12; over the "
        "integers, with signs, against the walk A itself, to s^18 at 3, 4, 5)", ok, info)


def check2():
    ok, info = True, {}
    for m in range(2, 11):
        n = 2 ** m
        a = det_path(n - 2) == spread(truncated_catalan(m - 1), 2, 4 * n)
        b = det_path(n - 3) == spread(truncated_catalan(m - 2), 4, 4 * n)
        c = det_path(n - 1) == 1
        info[n] = (a, b, c)
        ok &= a and b and c
    # nilpotency of the row path P_(2^m - 1): P^(2^m - 1) = 0 over GF(2), m <= 5
    for m in range(2, 6):
        k = 2 ** m - 1
        P = [[1 if abs(i - j) == 1 else 0 for j in range(k)] for i in range(k)]
        Q = [[1 if i == j else 0 for j in range(k)] for i in range(k)]
        for _ in range(k):
            Q = [[sum(Q[i][l] & P[l][j] for l in range(k)) % 2 for j in range(k)] for i in range(k)]
        ok &= not any(any(r) for r in Q)
    # the first-passage series equal x^2 C_(m-2)(x^4) / C_(m-1)(x^2) and x^(n-1) / C_(m-1)(x^2) (below x^T)
    T = 80
    R = Ring(T)
    for m in range(2, 6):
        n = 2 ** m
        NLL, NLR = first_passage(R, n)
        den = pinv(spread(truncated_catalan(m - 1), 2, T), T)
        wLL = pmul(spread(truncated_catalan(m - 2), 4, T) << 2, den, T)
        wLR = pmul(1 << (n - 1), den, T)
        good = NLL == wLL and NLR == wLR
        info[f"first passage {n}"] = good
        ok &= good
    rec("2 Proposition 8: det(I + xP_(2^m - 2)) = C_(m-1)(x^2), det(I + xP_(2^m - 3)) = C_(m-2)(x^4), det(I + xP_(2^m - 1)) = 1 "
        "(m = 2..10), P_(2^m - 1) nilpotent (m <= 5), and the first-passage series in closed form (n = 4..32, below x^80)", ok, info)


def check3():
    ok, info = True, {}
    for m in range(1, 13):
        n = 2 ** m
        a = det_looped_path(n) == 1 ^ trace_poly(n)
        b = det_path(n - 1) == 1
        info[n] = (a, b)
        ok &= a and b
    rec("3 Proposition 9: det(I + zP_n^o) = 1 + L(z) and det(I + zP_(n-1)) = 1 at n = 2^m, m = 1..12", ok, info)


def check4():
    ok, info = True, {}
    # C1 exactly: agreement below 2n(n - 1) + 4n terms (both sides obey linear recurrences of orders <= 2n(n - 1) and 4n)
    for m in range(2, 9):
        n = 2 ** m
        K = 2 * n * (n - 1) + 4 * n
        d = corner_returns(2 * n - 2, 2 * n - 2, K)
        good = d == box_law_sequence(n, K)
        info[f"C1 exact {n}"] = good
        ok &= good
    # C2: 1/r_2n(w) = 1/r_n(w^2) + w^4 fails from 2 to 4, 3 to 6, 5 to 10 and 6 to 12, first at w^16, w^64, w^96, w^128
    K = 160
    c2 = {}
    for n, first in ((2, 16), (3, 64), (5, 96), (6, 128)):
        rn = corner_returns(2 * n - 2, 2 * n - 2, K)
        r2n = corner_returns(4 * n - 2, 4 * n - 2, K)
        d = pinv(r2n, K) ^ (spread(pinv(rn, K), 2, K) ^ (1 << 4))
        f = (d & -d).bit_length() - 1 if d else None
        c2[n] = f
        ok &= f == first
    info["C2 first failures"] = c2
    # C3: the box's corner series first differs from the quadrant's C(w^4) at time 8n (n = 3..64)
    c3 = True
    for n in range(3, 65):
        H = 8 * n + 8
        d = corner_returns(2 * n - 2, 2 * n - 2, H) ^ spread(catalan2(H), 4, H)
        f = (d & -d).bit_length() - 1 if d else None
        c3 &= f == 8 * n
    info["C3 at 3..64"] = c3
    ok &= c3
    # the four-corner formula below w^1200 at 4..64
    fc = True
    for m in range(2, 7):
        n = 2 ** m
        N = 2 * n - 2
        K = 1200
        B = Rect(N, N)
        cs = [(0, 1)]
        for _ in range(3):
            X, Y = cs[-1]
            cs.append((Y, N - X))
        got = [B.series((0, 1), q, K) for q in cs]
        Cm = sum(1 << (4 * (2 ** j - 1)) for j in range(m + 1))
        pred = [0, 0, 0, 0]
        k = 0
        while k * (2 * n - 1) < K:
            pred[k % 4] ^= (Cm << (k * (2 * n - 1))) & ((1 << K) - 1)
            k += 1
        pred[3] ^= 1 << (2 * n - 3)
        fc &= got == pred
    info["four corners 4..64"] = fc
    ok &= fc
    # the period of the corner's whole orbit: e_c A^P = e_c first at P = 2^(floor(m/2) + 1) (2n - 1), n = 2^m = 4..128
    per = {}
    for m in range(2, 8):
        n = 2 ** m
        B = Rect(2 * n - 2, 2 * n - 2)
        x0 = 1 << B.idx(0, 1)
        x, k = B.step(x0), 1
        while x != x0:
            x, k = B.step(x), k + 1
        per[n] = k
    pok = all(per[2 ** m] == 2 ** (m // 2 + 1) * (2 ** (m + 1) - 1) for m in range(2, 8))
    info["orbit periods"] = per
    ok &= pok
    rec("4 computed: C1 exactly at 4 to 256 (agreement below 2n(n - 1) + 4n terms), C2's first failures at 2, 3, 5, 6, C3 (first "
        "deviation from the quadrant at time 8n) at every side 3 to 64, the four-corner formula below w^1200 at 4 to 64, the corner orbit's period 2^(floor(m/2) + 1)(2n - 1) at 4 to 128", ok, info)


def check5():
    """Corollary 10: walks from c to an inner v contact v(a, b) = (2a, 2b + 1) are sum over the last end-column visit of
    [K_n^-1]_((L,0),(X,b')) times the final free segment N_(X->a)(Pi) from row b' to b; each target compared on its own."""
    ok, info = True, {}
    T = 40
    R = Ring(T)

    def formula(n):
        L = n - 1
        E, _ = arch_two_sided(R, n)
        IsP = R.add(R.eye(L), R.scal(2, path(L)))
        Pi = R.scal(2, R.inv_unip(IsP))
        m = n - 2
        G = R.inv_unip(R.add(R.eye(m), R.scal(2, path(m))))
        F = {}
        for a in range(1, n - 1):
            for X in (0, 1):
                ser = ((G[0][a - 1] if X == 0 else G[m - 1][a - 1]) << 1) & R.MASK
                F[(X, a)] = R.evaluate(ser, Pi)

        def target(a, b):
            tot = 0
            for X in (0, 1):
                for bp in range(L):
                    tot ^= R.pm(E[0][X * L + bp], F[(X, a)][bp][b])
            return tot
        return target

    for n in (4, 5, 6):
        tg = formula(n)
        B = Rect(2 * n - 2, 2 * n - 2)
        good = all(tg(a, b) == halve(B.series((0, 1), (2 * a, 2 * b + 1), 2 * T), T) for a in range(1, n - 1) for b in range(n - 1))
        info[f"every inner target at {n}"] = good
        ok &= good
    for n in (8, 16):
        tg = formula(n)
        B = Rect(2 * n - 2, 2 * n - 2)
        t1 = tg(n // 2 + 1, n // 2 + 1) == halve(B.series((0, 1), (n + 2, n + 3), 2 * T), T)       # c* = (n + 2, n + 3)
        t2 = tg(n // 2 + 2, n // 2) == halve(B.series((0, 1), (n + 4, n + 1), 2 * T), T)           # (n + 4, n + 1)
        zero = tg(n // 2 + 1, n // 2 + 1) ^ tg(n // 2 + 2, n // 2) == 0
        info[f"B137 targets at {n}"] = (t1, t2, zero)
        ok &= t1 and t2 and zero
    rec("5 Corollary 10 against the walk, each target separately: every inner target at 4, 5, 6, and at 8 and 16 the two targets of "
        "the count of REACH-HALVES-20261110-001A (B137), c* and (n + 4, n + 1), whose sum vanishes (below s^40)", ok, info)

if __name__ == "__main__":
    for c in (check0, check1, check2, check3, check4, check5):
        c()
    allok = all(v["pass"] for v in checks.values())
    print("ALL PASS" if allok else "SOME FAIL")
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps({"schema_version": 1, "artifact": "RETURN-LAW-20261110-001C-P001", "checks": checks,
                                                      "status": "passed" if allok else "failed"}, indent=2, default=str) + "\n")
