"""RETURN-LAW-20261110-001B checks (one process, a few seconds; --write rewrites result.json).

0 the dependencies bound by hash; 1 Proposition 6(a) (the two half-strips have one corner series); 2 Proposition 6(b), (c) (the four-periodic
branch); 3 computed: B1 at the even sides 2 to 64 below w^2400, B2 at the odd sides 3 to 63; 4 computed: without the bottom wall
the far wall is seen at time 4n at every side."""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/RETURN-LAW-20261110-001A/RETURN-LAW-20261110-001A-P001_the_quadrant_law"))
from return_lib import FastRect as Rect, catalan2, corner_returns, spread  # noqa: E402

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


def check1():
    ok, info = True, {}
    H = 1600
    for n in range(2, 31):
        N = 2 * n - 2
        a = corner_returns(N, H // 2 + 4, H)
        b = corner_returns(H // 2 + 4, N, H)
        ok &= a == b
        if a != b:
            info[n] = "differ"
    rec("1 Proposition 6(a): the two half-strips have the same corner return series below w^1600 at the sides 2 to 30", ok, info)


# Laurent polynomials in t over GF(2): frozensets of exponents
def L(*e):
    out = set()
    for x in e:
        out ^= {x}
    return frozenset(out)


def ladd(*ps):
    out = set()
    for p in ps:
        out ^= set(p)
    return frozenset(out)


def lmul(p, q):
    out = set()
    for a in p:
        for b in q:
            out ^= {a + b}
    return frozenset(out)


def check2():
    ok, info = True, {}
    lam = L(1, -1)
    pat = [L(1), L(1, -1), L(-1), L()]
    for n in range(2, 41):
        N = 2 * n - 2
        psi = [pat[X % 4] for X in range(N + 1)]
        get = lambda X: psi[X] if 0 <= X <= N else L()
        eig = True
        for X in range(N + 1):
            if X % 2:
                rhs = ladd(lmul(L(1), get(X - 1)), lmul(L(-1), get(X + 1)))
            else:
                rhs = ladd(lmul(L(-1), get(X - 1)), lmul(L(1), get(X + 1)))
            if rhs != lmul(lam, psi[X]):
                eig = False
                break
        info[n] = eig
        ok &= eig == (n % 2 == 0)
    # the two-site transfer matrix of REACH-HALVES Theorem 3 squares to I on the branch
    t2, tm2 = L(2), L(-2)
    M = [[t2, lam], [lmul(lam, t2), ladd(lmul(lam, lam), tm2)]]
    M2 = [[ladd(lmul(M[i][0], M[0][j]), lmul(M[i][1], M[1][j])) for j in range(2)] for i in range(2)]
    sq = M2 == [[L(0), L()], [L(), L(0)]]
    info["M^2 = I at lambda = t + 1/t"] = sq
    ok &= sq
    rec("2 Proposition 6(b), (c): the four-periodic vector (t, t + 1/t, 1/t, 0, ...) is an eigenvector of the strip [0, N] x Z with "
        "eigenvalue t + 1/t exactly at the even sides (2 to 40), and the two-site transfer matrix squares to I on that branch", ok,
        {k: v for k, v in info.items() if not isinstance(k, int) or k <= 8})


def check3():
    ok, info = True, {}
    H = 2400
    q = spread(catalan2(H), 4, H)
    first = {}
    for n in range(2, 65):
        N = 2 * n - 2
        a = corner_returns(N, H // 2 + 4, H)
        if n % 2 == 0:
            ok &= a == q
            if a != q:
                info[n] = "even side differs"
        else:
            d = a ^ q
            f = (d & -d).bit_length() - 1 if d else None
            first[n] = f
            ok &= f == 4 * n
    info["odd sides: first difference at 4n"] = all(first[n] == 4 * n for n in first)
    rec("3 computed: B1 (the half-strip's corner series is C(w^4)) at every even side 2 to 64 below w^2400; B2 (first "
        "difference at time 4n) at every odd side 3 to 63", ok, info)


def check4():
    ok, info = True, {}
    H = 400
    BIG = H + 4
    Y0 = BIG + 1 if (BIG + 1) % 2 else BIG          # a contact (0, Y0) far from both ends of a tall rectangle
    def ret(NX):
        R = Rect(NX, 2 * BIG)
        i0 = R.idx(0, Y0)
        x, out = 1 << i0, 0
        for k in range(H):
            if (x >> i0) & 1:
                out |= 1 << k
            x = R.step(x)
        return out
    hp = ret(BIG)
    for n in range(2, 41):
        d = ret(2 * n - 2) ^ hp
        f = (d & -d).bit_length() - 1 if d else None
        info[n] = f
        ok &= f == 4 * n
    rec("4 computed: with no bottom wall (the strip [0, N] x Z against the half-plane) the returns of a contact (0, Y0) on the left wall, far from the other walls, differ first at "
        "time 4n at every side 2 to 40, even or odd", ok, {k: v for k, v in info.items() if k <= 8})


if __name__ == "__main__":
    for c in (check0, check1, check2, check3, check4):
        c()
    allok = all(v["pass"] for v in checks.values())
    print("ALL PASS" if allok else "SOME FAIL")
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps({"schema_version": 1, "artifact": "RETURN-LAW-20261110-001B-P001", "checks": checks,
                                                      "status": "passed" if allok else "failed"}, indent=2, default=str) + "\n")
