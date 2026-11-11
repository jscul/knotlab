"""RETURN-LAW-20261110-001A checks (one process, about ten seconds; --write rewrites result.json).

0 the dependencies bound by hash; 1 Lemma 1 (the v-grid); 2 Theorem 2 (the reflection through the corner); 3 Theorem 3 (the
column decomposition) over GF(2) and over the integers; 4 Lemma 4 (the plain quadrant is even); 5 Proposition 5 (the looped
half-line); 6 computed: A1 below w^4000, A2 for k <= 24, and the pairing of the corner's row and column; 7 computed: the
structure of M^2 on the v-grid and the doubled identity on the half-line; 8 the kernel equation of the corner's column."""
import hashlib
import json
import random
import sys
from collections import defaultdict
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
from return_lib import (FastRect, Rect, Ring, arch_one_sided, catalan2, corner_returns, lower, path, pmul, spread)  # noqa: E402

DEPS = ["proofs/REACH-HALVES-20261110-001A/REACH-HALVES-20261110-001A-P001_the_failure_at_every_power_of_two/manifest.json",
        "proofs/FULL-REACH-PROOF-20261108-001A/FULL-REACH-PROOF-20261108-001A-P001_symmetries_the_torus_and_powers_of_two/manifest.json"]
WANT = {DEPS[0]: "1fa0ec2aeb379ac83ad178e1d66ea8f4d86b1934544edb2b0e1c5ef925b9b3d5",
        DEPS[1]: "affc32533a4d960bd72b879ef5870513fe8ffaad5614bf296900aa27d5d618d0"}
checks = {}


def rec(name, ok, info=None):
    checks[name] = {"pass": bool(ok), "info": info}
    print(("PASS " if ok else "FAIL ") + name, flush=True)


def reads(X, Y):
    return [(X - 1, Y - 1), (X + 1, Y + 1)] if X % 2 else [(X + 1, Y - 1), (X - 1, Y + 1)]


def check0():
    got = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in DEPS}
    rec("0 dependencies bound by hash (REACH-HALVES-20261110-001A, FULL-REACH-PROOF-20261108-001A manifests)", got == WANT, got)


def vgrid_moves(a, b, A, B):
    """Lemma 1: the v-grid moves from (a, b); A, B = number of columns, rows (None = unbounded)"""
    out = []
    lastcol = A is not None and a == A - 1
    if not lastcol:
        out.append((a + 1, b))                                  # E
        if b >= 1:
            out.append((a, b - 1))                              # S
    if a >= 1:
        out.append((a - 1, b))                                  # W
        if B is None or b + 1 <= B - 1:
            out.append((a, b + 1))                              # N
    return out


def check1():
    ok, info = True, {}
    cases = [("box", n, 2 * n - 2, 2 * n - 2, n, n - 1) for n in range(2, 13)]
    cases += [("half-strip Y", n, 60, 2 * n - 2, None, n - 1) for n in (2, 3, 4, 7)]
    cases += [("half-strip X", n, 2 * n - 2, 60, n, None) for n in (2, 3, 4, 7)]
    cases += [("quadrant", 0, 60, 60, None, None)]
    for kind, n, NX, NY, A, B in cases:
        R = Rect(NX, NY)
        bad = 0
        for a in range(NX // 2 + 1):
            for b in range((NY - 1) // 2 + 1):
                X, Y = 2 * a, 2 * b + 1
                if not R.inside(X, Y):
                    continue
                x = R.step(R.step(1 << R.idx(X, Y)))
                got = {(Xq // 2, (Yq - 1) // 2) for (Xq, Yq) in R.contacts if (x >> R.idx(Xq, Yq)) & 1}
                if (A is None and 2 * a + 3 > NX) or (B is None and 2 * b + 4 > NY):
                    continue                                    # the far edge of a finite stand-in for an unbounded side
                want = set(vgrid_moves(a, b, A, B))
                if got != want:
                    bad += 1
        info[f"{kind} {n}"] = bad
        ok &= bad == 0
    # the library's fast rectangle builds the same four masks as REACH-HALVES-20261110-001A's Rect
    fast = all((Rect(a, b).hm, Rect(a, b).hp, Rect(a, b).vp, Rect(a, b).vm) ==
               (FastRect(a, b).hm, FastRect(a, b).hp, FastRect(a, b).vp, FastRect(a, b).vm)
               for a, b in [(2, 2), (6, 6), (10, 3), (3, 10), (14, 14), (21, 8), (8, 21), (40, 40), (61, 30)])
    info["FastRect = Rect"] = fast
    ok &= fast
    rec("1 Lemma 1: on the v contacts A^2 is the v-grid walk (E, W, N, S; no N from column 0, no S from column n - 1) "
        "in boxes 2 to 12, both half-strips and the quadrant; the library's fast rectangle has the same masks", ok, info)


def survivors(NX, NY, K):
    """integer counts of all returns and of the walks left by the reflection through the corner (Theorem 2)"""
    inside = lambda q: 0 <= q[0] <= NX and 0 <= q[1] <= NY
    tot = {(0, 1): 1}
    sur = {((0, 1), True): 1}
    out = []
    for k in range(1, K + 1):
        nt = defaultdict(int)
        for p, c in tot.items():
            for q in reads(*p):
                if inside(q):
                    nt[q] += c
        ns = defaultdict(int)
        for (p, t), c in sur.items():
            for q in reads(*p):
                if not inside(q):
                    continue
                d = q[0] - q[1]
                if d < -1:
                    continue
                if d == -1:
                    if p[0] - p[1] == -1 or t:
                        ns[(q, True)] += c
                    continue
                tq = (t if p[0] - p[1] != -1 else False) or q[1] == 0 or q[0] == NX
                ns[(q, tq)] += c
        tot, sur = nt, ns
        out.append((k, tot.get((0, 1), 0), sur.get(((0, 1), True), 0)))
    return out


def check2():
    ok, info = True, {}
    # (a) the reflection through the corner is a symmetry of the walk in the plane
    sig = lambda p: (p[1] - 1, p[0] + 1)
    random.seed(1)
    for _ in range(4000):
        X = random.randint(-50, 50)
        Y = random.randint(-50, 50)
        if (X + Y) % 2 == 0:
            Y += 1
        if sorted(reads(*sig((X, Y)))) != sorted(sig(q) for q in reads(X, Y)):
            ok = False
    info["symmetry"] = ok
    # (b) the walks left over have the parity of all returns
    for name, NX, NY, K in [("quadrant", 200, 200, 48), ("box 4", 6, 6, 60), ("box 6", 10, 10, 60), ("box 8", 14, 14, 64)]:
        res = survivors(NX, NY, K)
        good = all((T - S) % 2 == 0 for k, T, S in res)
        info[name] = [(k, T, S) for k, T, S in res if k % 4 == 0][:8]
        ok &= good
        if name == "quadrant":
            counts = [S for k, T, S in res if k % 4 == 0][:6]
            info["quadrant survivors k = 1..6"] = counts
            ok &= counts == [1, 2, 7, 34, 206, 1458]
    rec("2 Theorem 2: the reflection through the corner is a symmetry; the walks whose every excursion lies below the line and "
        "touches Y = 0 (or X = N) have the parity of all returns (quadrant to 48, boxes 4, 6, 8); the quadrant's survivors at "
        "k = 1..6 are 1, 2, 7, 34, 206, 1458", ok, info)


def check3():
    ok, info = True, {}
    # over GF(2): Theorem 3 against the direct walk, the half-strip with Y bounded at every n = 2..12, and the quadrant
    T = 60
    R = Ring(T)
    for n in range(2, 13):
        E = arch_one_sided(R, n - 1)
        d = corner_returns(T + 6, 2 * n - 2, 2 * T)
        dd = sum(((d >> (2 * k)) & 1) << k for k in range(T))
        good = E[0][0] == dd and all(((d >> (2 * k + 1)) & 1) == 0 for k in range(T))
        info[f"half-strip {n}"] = good
        ok &= good
    T = 48
    R = Ring(T)
    E = arch_one_sided(R, T // 2 + 2)
    d = corner_returns(T + 6, T + 6, 2 * T)
    dd = sum(((d >> (2 * k)) & 1) << k for k in range(T))
    info["quadrant"] = E[0][0] == dd
    ok &= E[0][0] == dd
    # over the integers, with signs: R(s) = [(I - sD - s^2 f(P))^-1]_00, f(P) = sum_h C_h s^2h (I - sP)^-(2h+1), T = 22
    T = 22

    def zmul(a, b):
        out = [0] * T
        for i, x in enumerate(a):
            if x:
                for j in range(T - i):
                    out[i + j] += x * b[j]
        return out

    def zmm(A, B):
        n = len(A)
        C = [[[0] * T for _ in range(n)] for _ in range(n)]
        for i in range(n):
            for l in range(n):
                if any(A[i][l]):
                    for j in range(n):
                        if any(B[l][j]):
                            p = zmul(A[i][l], B[l][j])
                            C[i][j] = [x + y for x, y in zip(C[i][j], p)]
        return C

    def zeye(n):
        return [[[1 if i == j and k == 0 else 0 for k in range(T)] for j in range(n)] for i in range(n)]

    def zadd(A, B, c=1):
        return [[[x + c * y for x, y in zip(A[i][j], B[i][j])] for j in range(len(A))] for i in range(len(A))]

    def zinv(N):  # (I - N)^-1 = sum N^k, N = O(s)
        n = len(N)
        R, P = zeye(n), zeye(n)
        for _ in range(T):
            P = zmm(P, N)
            if not any(any(any(c) for c in r) for r in P):
                break
            R = zadd(R, P)
        return R

    def smat(M, k):  # s^k M for an integer matrix M
        n = len(M)
        return [[[M[i][j] if t == k else 0 for t in range(T)] for j in range(n)] for i in range(n)]

    def direct_int(n, K):
        """the walk A itself on [0, oo) x [0, 2n - 2], over the integers: returns of c = (0, 1) at the even times 2k, k < K"""
        Nb = 2 * n - 2
        cur = {(0, 1): 1}
        out = []
        for k in range(2 * K):
            if k % 2 == 0:
                out.append(cur.get((0, 1), 0))
            nxt = defaultdict(int)
            for p, c in cur.items():
                for q in reads(*p):
                    if q[0] >= 0 and 0 <= q[1] <= Nb:
                        nxt[q] += c
            cur = nxt
        return out

    for n in (2, 3, 4, 5, 6):
        L = n - 1
        Pm, Dm = path(L), lower(L)
        Q = zinv(smat(Pm, 1))                     # (I - sP)^-1
        Q2 = zmm(Q, Q)
        f = [[[0] * T for _ in range(L)] for _ in range(L)]
        h, Ph = 0, Q
        while 2 * h < T:
            cat = comb(2 * h, h) // (h + 1)
            sh = [[[0] * (2 * h) + Ph[i][j][:T - 2 * h] for j in range(L)] for i in range(L)]
            f = zadd(f, sh, cat)
            Ph = zmm(Ph, Q2)
            h += 1
        N = zadd(smat(Dm, 1), [[[0, 0] + f[i][j][:T - 2] for j in range(L)] for i in range(L)])
        E = zinv(N)
        good = E[0][0] == direct_int(n, T)
        info[f"integers, half-strip {n}"] = good
        ok &= good
    rec("3 Theorem 3: the corner's return series is the (0, 0) entry of (I - sD - s^2 f(P))^-1 (over GF(2) to s^60 at the "
        "half-strips 2 to 12, to s^48 in the quadrant; over the integers, against the walk A itself, to s^22 at 2 to 6)", ok, info)


def check4():
    ok, info = True, {}
    T = 60
    R = Ring(T)
    from return_lib import f_of
    f = f_of(R, path(T // 2 + 2))
    ok &= f[0][0] == 1
    info["f(P)_00 mod 2 below s^60"] = f[0][0]
    for t in range(1, 201):
        sw = sum(comb(2 * t, 2 * h) * (comb(2 * h, h) // (h + 1)) * (comb(2 * (t - h), t - h) // (t - h + 1)) for h in range(t + 1))
        ct = comb(2 * t, t) // (t + 1)
        cn = comb(2 * t + 2, t + 1) // (t + 2)
        if sw != ct * cn or sw % 2:
            ok = False
            info["bad t"] = t
            break
    rec("4 Lemma 4: f(P)_00 = 1 mod 2 for the half-line; the shuffle sum is C_t C_(t+1) and even for t = 1..200", ok, info)


def check5():
    K = 4000
    C = catalan2(K)
    # 1/(1 + z + z^2 C(z^2)) = C(z)  <=>  C(z) (1 + z + z^2 C(z^2)) = 1
    rhs = 1 ^ 0b10 ^ (spread(C, 2, K) << 2) & ((1 << K) - 1)
    ok = pmul(C, rhs, K) == 1
    rec("5 Proposition 5: the loop end of the looped half-line returns by C(z) mod 2 (below z^4000)", ok)


def check6():
    ok, info = True, {}
    H = 4000
    d = corner_returns(H // 2 + 4, H // 2 + 4, H)
    C = catalan2(H)
    want = spread(C, 4, H)
    info["A1 below w^4000"] = d == want
    ok &= d == want
    # A2: integer counts C_k^2, k <= 24
    K = 4 * 24
    cur = {(0, 1): 1}
    good = True
    for k in range(1, K + 1):
        nxt = defaultdict(int)
        for p, c in cur.items():
            for q in reads(*p):
                if q[0] >= 0 and q[1] >= 0:
                    nxt[q] += c
        cur = nxt
        if k % 4 == 0:
            j = k // 4
            good &= cur.get((0, 1), 0) == (comb(2 * j, j) // (j + 1)) ** 2
    info["A2 for k <= 24"] = good
    ok &= good
    # the pairing of the corner's column and row of the column resolvent: entry 2k = t0 * entry 2k - 1, k = 1, 2, 3
    T = 56
    R = Ring(T)
    E = arch_one_sided(R, T // 2 + 2)
    t0 = R.pm(2, E[0][0])
    m = (1 << (T - 12)) - 1
    pair = all(((E[2 * k][0] ^ R.pm(t0, E[2 * k - 1][0])) & m) == 0 and ((E[0][2 * k] ^ R.pm(t0, E[0][2 * k - 1])) & m) == 0
               for k in range(1, 9))
    info["pairing below s^44, k <= 8"] = pair
    ok &= pair
    # the same relation fails in column 1, and the shifted relation fails in column 0
    other = all(((E[2 * k][1] ^ R.pm(t0, E[2 * k - 1][1])) & m) != 0 and ((E[2 * k + 1][0] ^ R.pm(t0, E[2 * k][0])) & m) != 0
                for k in (1, 2, 3))
    info["no pairing in column 1, none shifted"] = other
    ok &= other
    rec("6 computed: A1 below w^4000, A2 (C_k^2 returns of length 4k) for k <= 24, and the pairing of the corner's row and "
        "column (entry 2k = t0 entry 2k - 1, t0 = s C(s^2)) for k <= 8 below s^44, failing in column 1 and when shifted", ok, info)


def check7():
    ok, info = True, {}
    # (a) M^2 on the quadrant's v-grid, mod 2: the doubled walk with these boundary terms
    def m2(a, b):
        cnt = defaultdict(int)
        for p in vgrid_moves(a, b, None, None):
            for q in vgrid_moves(*p, None, None):
                cnt[q] ^= 1
        return {q for q, c in cnt.items() if c}
    for a in range(12):
        for b in range(12):
            want = {(a + 2, b), (a, b - 2) if b >= 2 else None, (a - 2, b) if a >= 2 else None, (a, b + 2) if a >= 1 else None,
                    (a, b) if (a == 0 or b == 0) else None, (a + 1, b + 1) if a == 0 else None, (a - 1, b + 1) if a == 1 else None}
            want.discard(None)
            if m2(a, b) != want:
                ok = False
                info[(a, b)] = "differs"
    # (b) the doubled identity [(I + uD + uI + u^2 f(P + E0) + u^2 f(P) D^T)^-1]_00 = 1 + u C(u^2) on the half-line, below u^40
    from return_lib import f_of, raise_
    T = 40
    R = Ring(T)
    rows = T // 2 + 2
    P, D, Dt = path(rows), lower(rows), raise_(rows)
    Po = [r[:] for r in P]
    Po[0][0] = 1
    K = R.add(R.eye(rows), R.scal(2, D), R.scal(2, R.eye(rows)), R.scal(4, f_of(R, Po)), R.scal(4, R.mm(f_of(R, P), Dt)))
    E = R.inv_unip(K)
    want = (1 ^ (spread(catalan2(T), 2, T) << 1)) & R.MASK
    info["doubled identity below u^40"] = E[0][0] == want
    ok &= E[0][0] == want
    rec("7 computed: M^2 on the quadrant's v-grid is the half-scale walk plus loops on the axes plus the couplings (0, b) -> (1, b + 1) "
        "and (1, b) -> (0, b + 1) (sites up to 11); the doubled identity on the half-line below u^40", ok, info)


def check8():
    """the kernel equation of Theorem 3's column, over GF(2): with Y the small root of Y + 1/Y = 1/s + z + 1/z and
    a(z) = sum_b E[b, 0] z^b, s(z + Y) a(z) + s(1/z + Y) a(1/z) = (z + 1/z) Y; z a(z)/(1 + zY) + z is symmetric in z <-> 1/z;
    and E[b, 0] is the series of the walks from (1, 0) to (2b + 1, 0) at even times (the diagonal reflection D)."""
    ok, info = True, {}
    T = 48
    K = 24                          # compare below s^K
    OFF = 96                        # z^e is bit e + OFF of a coefficient
    R = Ring(T)
    E = arch_one_sided(R, T // 2 + 2)

    def lmul(x, y):                 # Laurent polynomials in z with offset OFF
        r = 0
        while y:
            low = y & -y
            r ^= x << (low.bit_length() - 1)
            y ^= low
        return r >> OFF

    def smul(A, B):                 # series in s (lists of K Laurent coefficients)
        out = [0] * K
        for i, x in enumerate(A):
            if x:
                for j in range(K - i):
                    if B[j]:
                        out[i + j] ^= lmul(x, B[j])
        return out

    def sadd(*Ss):
        out = [0] * K
        for S in Ss:
            for i in range(K):
                out[i] ^= S[i]
        return out

    def reflect(S):                 # z -> 1/z
        out = []
        for x in S:
            r = 0
            while x:
                low = x & -x
                e = low.bit_length() - 1 - OFF
                r |= 1 << (-e + OFF)
                x ^= low
            out.append(r)
        return out

    def sinv(S):                    # 1/S for S = 1 + O(s)
        assert S[0] == 1 << OFF
        out = [0] * K
        out[0] = 1 << OFF
        for k in range(1, K):
            acc = 0
            for j in range(1, k + 1):
                if S[j] and out[k - j]:
                    acc ^= lmul(S[j], out[k - j])
            out[k] = acc
        return out

    one = [1 << OFF] + [0] * (K - 1)
    z = [1 << (OFF + 1)] + [0] * (K - 1)
    zi = [1 << (OFF - 1)] + [0] * (K - 1)
    s1 = [0, 1 << OFF] + [0] * (K - 2)
    q = sadd(z, zi)
    inv1sq = sinv(sadd(one, smul(s1, q)))
    Y = [0] * K
    for _ in range(K):
        Y = smul(smul(s1, sadd(one, smul(Y, Y))), inv1sq)       # s Y^2 + (1 + sq) Y + s = 0
    a = [0] * K
    for b in range(T // 2 + 2):
        for k in range(K):
            if (E[b][0] >> k) & 1:
                a[k] ^= 1 << (b + OFF)
    lhs = sadd(smul(s1, smul(sadd(z, Y), a)), smul(s1, smul(sadd(zi, Y), reflect(a))))
    good = lhs[:K - 1] == smul(q, Y)[:K - 1]
    info["kernel equation below s^23"] = good
    ok &= good
    Sig = sadd(smul(smul(z, a), sinv(sadd(one, smul(z, Y)))), z)
    sym = Sig[:K - 1] == reflect(Sig)[:K - 1]
    info["z a/(1 + zY) + z symmetric below s^23"] = sym
    ok &= sym
    # E[b, 0] = walks from (1, 0) to (2b + 1, 0) at the even times
    Q = FastRect(2 * T + 6, 2 * T + 6)
    dd = all(sum(((Q.series((1, 0), (2 * b + 1, 0), 2 * T) >> (2 * k)) & 1) << k for k in range(T)) == E[b][0] for b in range(6))
    info["D identification, b < 6"] = dd
    ok &= dd
    rec("8 the kernel equation s(z + Y)a(z) + s(1/z + Y)a(1/z) = (z + 1/z)Y for the corner's column (below s^23), the symmetry that "
        "forces a(z) = (1 + zY)(1 + Sigma/z), and the column as the walks from (1, 0) along the bottom row (b < 6, below s^48)", ok, info)


if __name__ == "__main__":
    for c in (check0, check1, check2, check3, check4, check5, check6, check7, check8):
        c()
    allok = all(v["pass"] for v in checks.values())
    print("ALL PASS" if allok else "SOME FAIL")
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps({"schema_version": 1, "artifact": "RETURN-LAW-20261110-001A-P001", "checks": checks,
                                                      "status": "passed" if allok else "failed"}, indent=2, default=str) + "\n")
