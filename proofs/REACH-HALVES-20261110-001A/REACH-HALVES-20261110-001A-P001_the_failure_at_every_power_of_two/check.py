"""REACH-HALVES-20261110-001A checks (one process, about a minute; --write rewrites result.json).

0 the dependencies bound by hash; 1 Theorem 1 (the reduction to one walk count, the conveyor grid); 2 Theorem 2 (the reflection
about the near diagonal and its excursion form); 3 Theorem 3 (the strip); 4 Lemma 4 (anti-diagonal sums on the conveyor grid);
5 computed at 4 to 64: the targets A1 and A3's corner half, the return law A2 and the far-corner delay."""
import hashlib
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
from halves_lib import Rect, box, reads, Conveyor, GF, det  # noqa: E402

DEPS = ["proofs/FULL-REACH-PROOF-20261108-001A/FULL-REACH-PROOF-20261108-001A-P001_symmetries_the_torus_and_powers_of_two/manifest.json",
        "proofs/CONE-COLLAPSE-20261109-001A/CONE-COLLAPSE-20261109-001A-P001_the_cone_and_its_return_map/manifest.json"]
WANT = {DEPS[0]: "affc32533a4d960bd72b879ef5870513fe8ffaad5614bf296900aa27d5d618d0",
        DEPS[1]: "220ceb6c18c74cf54ff51f53bca81468bd38d0512836a37a34e63d06f621d273"}
checks = {}


def rec(name, ok, info=None):
    checks[name] = {"pass": bool(ok), "info": info}
    print(("PASS " if ok else "FAIL ") + name, flush=True)


def check0():
    got = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in DEPS}
    rec("0 dependencies bound by hash (FULL-REACH-PROOF-20261108-001A, CONE-COLLAPSE-20261109-001A manifests)", got == WANT, got)


def check1():
    ok, info = True, {}
    for n in range(3, 17):
        B = box(n)
        N = B.NX
        # (a) the funnel at the corner
        rd = lambda c: [d for d in reads(*c) if B.inside(*d)]
        readers = lambda c: [p for p in B.contacts if c in rd(p)]
        ok &= rd((0, 1)) == [(1, 0)] and readers((1, 0)) == [(0, 1)] and readers((0, 1)) == [(1, 2)] and rd((1, 0)) == [(2, 1)]
        if n >= 5:
            ds, cs = (n + 3, n + 2), (n + 2, n + 3)
            K = 40 * n
            # (d) A^k[c*, (0,1)] = A^k[(1,0), d*] and A^k[c*, (1,0)] = A^k[(0,1), d*]
            ok &= B.series(cs, (0, 1), K) == B.series((1, 0), ds, K) and B.series(cs, (1, 0), K) == B.series((0, 1), ds, K)
            # (c) A^(k+1)[(0,1), d*] = A^k[(1,0), d*]
            ok &= B.series((0, 1), ds, K) == B.series((1, 0), ds, K) << 1
        # (e) A^2 on the h's is the conveyor grid walk, h(i, j) = (2i + 1, 2j)
        C = Conveyor(n)
        for i in range(n - 1):
            for j in range(n):
                x = 1 << B.idx(2 * i + 1, 2 * j)
                y = B.step(B.step(x))
                got = sorted(((X - 1) // 2, Y // 2) for (X, Y) in B.contacts if (y >> B.idx(X, Y)) & 1)
                ok &= got == sorted(C.nbrs(i, j))
    rec("1 Theorem 1: the corner funnel, the D-identities A^k[c*,(0,1)] = A^k[(1,0),d*], A^k[c*,(1,0)] = A^k[(0,1),d*], and A^2 on h = the conveyor grid, sides 3 to 16", ok)


def check2():
    ok = True
    info2 = {}
    # (a) sigma_0(X, Y) = (Y + 1, X - 1) is a symmetry of the free walk
    for X in range(-6, 7):
        for Y in range(-6, 7):
            if (X + Y) % 2:
                s = lambda p: (p[1] + 1, p[0] - 1)
                ok &= sorted(s(d) for d in reads(X, Y)) == sorted(reads(*s((X, Y))))
    # (b) G^B = G^(sigma_0 B) for endpoints on the line X - Y = 1, inside B and sigma_0 B
    for n in range(3, 11):
        N = 2 * n - 2
        B = box(n)
        K = 30 * n
        line = [(Y + 1, Y) for Y in range(0, N)]       # X - Y = 1, X in [1, N]
        # sigma_0 B = [1, N + 1] x [-1, N - 1]: shift coordinates by (-1, +1) to a box [0, N] x [0, N] with the shifted walk
        # the walk is translation-covariant only for even shifts, so compare by brute integer-free series on explicit sets
        def series_on(points_ok, start, target):
            cur, out = {start: 1}, 0
            for k in range(K):
                if cur.get(target, 0):
                    out |= 1 << k
                nxt = defaultdict(int)
                for p, c in cur.items():
                    for q in reads(*p):
                        if points_ok(q):
                            nxt[q] ^= c
                cur = {p: c for p, c in nxt.items() if c}
            return out
        inB = lambda p: 0 <= p[0] <= N and 0 <= p[1] <= N
        inS = lambda p: 1 <= p[0] <= N + 1 and -1 <= p[1] <= N - 1
        for a in line[:4] + line[-3:]:
            for b in line[1::3]:
                ok &= series_on(inB, a, b) == series_on(inS, a, b)
    # (c) the excursion form: walks (1,0) -> d* = walks whose every excursion off X - Y = 1 lies above it and touches X = 0 or Y = N
    def excursion_check(n, K, start, target):
        N = 2 * n - 2
        inbox = lambda u, v: 0 <= u + v + 1 <= N and 0 <= u - v <= N
        mv = lambda u, v: [(u - 1, v), (u + 1, v)] if (u + v) % 2 == 0 else [(u, v - 1), (u, v + 1)]
        wall = lambda u, v: u + v + 1 == 0 or u - v == N
        cur, full = {start: 1}, []
        for k in range(K):
            full.append(cur.get(target, 0))
            nxt = defaultdict(int)
            for p, c in cur.items():
                for q in mv(*p):
                    if inbox(*q):
                        nxt[q] ^= c
            cur = {p: c for p, c in nxt.items() if c}
        cur, fix = {(start, 0): 1}, []
        for k in range(K):
            fix.append(cur.get((target, 0), 0))
            nxt = defaultdict(int)
            for (p, f), c in cur.items():
                for q in mv(*p):
                    if not inbox(*q) or q[1] > 0:
                        continue
                    if q[1] == 0:
                        if f != 1:
                            nxt[(q, 0)] ^= c
                    else:
                        nxt[(q, 2 if (f == 2 or wall(*q)) else 1)] ^= c
            cur = {s: c for s, c in nxt.items() if c}
        return full == fix
    pairs = 0
    for n in range(5, 17):
        ok &= excursion_check(n, 25 * n, (0, 0), (n + 2, 0))
    for n in range(5, 10):
        line = [u for u in range(0, 2 * n - 2) if 0 <= u + 1 <= 2 * n - 2 and 0 <= u <= 2 * n - 2]
        for a in line:
            for b in line:
                ok &= excursion_check(n, 12 * n, (a, 0), (b, 0))
                pairs += 1
    info2 = {"all line pairs checked (sides 5 to 9, 12n steps)": pairs}
    rec("2 Theorem 2: sigma_0 is a symmetry of the free walk; G^B = G^(sigma_0 B) on the line X - Y = 1 (sides 3 to 10); the excursion form for (1,0) -> d* (sides 5 to 16, 25n steps) and for every pair of line points, h and v ends (sides 5 to 9, 12n steps)", ok, info2)


def check3():
    F = GF(10)
    rng = random.Random(5)
    ok = True

    def U(k, tau):
        a, b = 0, 1
        for _ in range(k):
            a, b = b, F.mul(tau, b) ^ a
        return b
    for n in range(2, 17):
        N = 2 * n - 2
        for _ in range(6):
            t, lam = rng.randrange(1, F.q), rng.randrange(1, F.q)
            ti = F.inv(t)
            M = [[0] * (N + 1) for _ in range(N + 1)]
            for X in range(N + 1):
                M[X][X] = lam
                if X + 1 <= N:
                    w = t if X % 2 == 0 else ti
                    M[X][X + 1] ^= w
                    M[X + 1][X] ^= w
            s = t ^ ti ^ lam
            ok &= det(F, M) == F.mul(lam, U(n - 1, F.mul(s, s)))
            if n in (2, 4, 8, 16):
                # at powers of two: lam U_(n-1)(tau) = lam tau^(n-1), and psi = (t, t + 1/t, 1/t, 0, ...) solves psi A(t) = (t + 1/t) psi
                ok &= U(n - 1, F.mul(s, s)) == F.exp[(F.log[F.mul(s, s)] * (n - 1)) % (F.q - 1)] if s else U(n - 1, 0) == 0
                lam0 = t ^ ti
                psi = [[t, lam0, ti, 0][X % 4] for X in range(N + 1)]
                row = [0] * (N + 1)
                for X in range(N + 1):
                    for Y in range(N + 1):
                        a = (t if min(X, Y) % 2 == 0 else ti) if abs(X - Y) == 1 else 0
                        row[Y] ^= F.mul(psi[X], a)
                ok &= row == [F.mul(lam0, p) for p in psi]
    # one Jordan block: dim ker (A(t) - (t + 1/t))^j = j for j = 1 .. 2n - 2, and rank A(t) = 2n - 2 (the flat band lambda = 0)
    def rank(M):
        M = [r[:] for r in M]; rk = 0; cols = len(M[0])
        for c in range(cols):
            p = next((r for r in range(rk, len(M)) if M[r][c]), None)
            if p is None:
                continue
            M[rk], M[p] = M[p], M[rk]
            inv = F.inv(M[rk][c])
            for r in range(len(M)):
                if r != rk and M[r][c]:
                    f = F.mul(M[r][c], inv)
                    M[r] = [a ^ F.mul(f, b) for a, b in zip(M[r], M[rk])]
            rk += 1
        return rk
    def mm(P, Q):
        d = len(P)
        out = [[0] * d for _ in range(d)]
        for i in range(d):
            for k in range(d):
                if P[i][k]:
                    a = P[i][k]
                    for j in range(d):
                        if Q[k][j]:
                            out[i][j] ^= F.mul(a, Q[k][j])
        return out
    for n in (4, 8):
        N = 2 * n - 2
        t = rng.randrange(2, F.q)
        ti = F.inv(t)
        lam0 = t ^ ti
        A = [[0] * (N + 1) for _ in range(N + 1)]
        for X in range(N):
            w = t if X % 2 == 0 else ti
            A[X][X + 1] = w
            A[X + 1][X] = w
        ok &= rank(A) == N
        B1 = [[A[i][j] ^ (lam0 if i == j else 0) for j in range(N + 1)] for i in range(N + 1)]
        P = [[1 if i == j else 0 for j in range(N + 1)] for i in range(N + 1)]
        for j in range(1, 2 * n - 1):
            P = mm(P, B1)
            ok &= (N + 1) - rank(P) == j
    # the decaying root s_- of s + 1/s = w^-2 is w^2 C(w^4), C the Catalan series mod 2 (sum_j z^(2^j - 1)): s = w^2 (1 + s^2)
    K = 400
    C = sum(1 << (4 * (2 ** j - 1)) for j in range(10) if 4 * (2 ** j - 1) < K)
    s = C << 2
    sq = 0
    for k in range(K):
        if (s >> k) & 1 and 2 * k < K:
            sq |= 1 << (2 * k)
    ok &= (s & ((1 << K) - 1)) == (((1 ^ sq) << 2) & ((1 << K) - 1))
    rec("3 Theorem 3: det(lam - A(t)) = lam U_(n-1)((lam + t + 1/t)^2) at random points of GF(2^10), sides 2 to 16; the period-4 eigenvector at 2, 4, 8, 16; rank A(t) = 2n - 2 and dim ker (A(t) - (t + 1/t))^j = j for j <= 2n - 2 at 4 and 8 (one Jordan block); s_- = w^2 C(w^4)", ok)


def check4():
    rng = random.Random(3)
    ok = True
    for n in range(3, 21):
        C = Conveyor(n)
        for _ in range(10):
            x = rng.getrandbits(C.I * C.J)
            y = C.step(x)
            val = lambda v, i, j: (v >> C.idx(i, j)) & 1 if 0 <= i < C.I and 0 <= j < C.J else 0
            for s in range(C.I + C.J - 1):
                lhs = 0
                for i in range(C.I):
                    if 0 <= s - i < C.J:
                        lhs ^= val(y, i, s - i)
                ok &= lhs == val(x, 0, s + 1) ^ val(x, n - 2, s + 1 - n)
    rec("4 Lemma 4: anti-diagonal sums of x M are x(0, s + 1) + x(n - 2, s + 1 - n) for 0 <= s <= 2n - 3, sides 3 to 20, ten random vectors each", ok)


def check5():
    E = {4: 4, 8: 8, 16: 16, 32: 16, 64: 32}
    info, ok = {}, True
    for n in (4, 8, 16, 32, 64):
        B = box(n)
        N = B.NX
        P = E[n] * (2 * n - 1)
        e = 1 << B.idx(0, 1)
        q = 2 * n - 1
        pw = {pow(2, i, q) for i in range(64)}
        x, union, ret, far = e, 0, [], []
        for k in range(P):
            union |= x
            ret.append((x >> B.idx(0, 1)) & 1)
            far.append((x >> B.idx(N, N - 1)) & 1)
            x = B.step(x)
        per = x == e
        law = ret == [1 if (k % 4 == 0 and (k // 4 + 1) % q in pw) else 0 for k in range(P)]
        missed = sorted(c for c in B.contacts if not (union >> B.idx(*c)) & 1)
        want = sorted((X + 1, X) for X in range(n + 2, 2 * n - 5, 4))
        delay = all(far[k] == ret[(k - 4 * n + 2) % P] for k in range(P))
        # A1 at this side: c* misses the corner ring, through the D-identity
        a1 = True
        if n >= 8:
            cs = (n + 2, n + 3)
            y0 = 1 << B.idx(*cs)
            y, seen = y0, 0
            for k in range(P):
                seen |= y
                y = B.step(y)
            a1 = y == y0 and not (seen >> B.idx(0, 1)) & 1 and not (seen >> B.idx(1, 0)) & 1
        info[str(n)] = {"A^P fixes the orbits": per, "return law": law, "never read = predicted d*'s": missed == want, "far delay 4n - 2": delay, "A1": a1}
        ok &= per and law and missed == want and delay and a1
    rec("5 computed at 4 to 64: A^P, P = e(2n - 1), fixes the corner's orbit and c*'s (so the unions over k < P are exact); A1 (c* misses the corner ring); the corner reads every contact but the d*'s; the return law A2; the far corner delayed by 4n - 2", ok, info)


def main():
    for f in (check0, check1, check2, check3, check4, check5):
        f()
    allpass = all(c["pass"] for c in checks.values())
    print("ALL PASS" if allpass else "SOME FAIL")
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps({"schema_version": 1, "artifact": "REACH-HALVES-20261110-001A-P001", "checks": checks,
                                                     "status": "passed" if allpass else "failed"}, indent=1) + "\n")


if __name__ == "__main__":
    main()
