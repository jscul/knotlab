"""Checks for BEYOND-CLASS2-20261027-001C-P001 (the finite and exact facts the proof uses).

  1 the group G_p = U4(F_p) x| <D>: D normalizes U4 with characters (-1, -1, -1 | 1, 1 | -1); no graded hard pair
  2 J-invariance of the Fox-coloring transport, over Z, every letter, n <= 12; the bundle and constant identities
  3 the symmetric-power constructions of Lemma 3.1: eight support patterns, homomorphisms on Aff(F_p), values in G_p,
    superdiagonal constants, mu -> D
  4 the pure braid P4: purity, conjugators in the third lower central term (Magnus over Z), the 2-cable acts by bundle
    substitution (free-group identity), the cable's coloring transport is the identity (over Z), the degree-3 tensor
  5 the edge weight: #{(A, B) : Phi_0(A, B, .) = 0} = 2 p^4 - p^2 (p = 5, 7, 11, 13); f on every support pattern at p = 5
    (integer, rescaling-invariant); f(0) = p^12, f(d*) = p^6 (2 p^4 - p^2); the 2 x 2 minor of W = f^2
  6 the count identity #Lambda = p^(12 m - N) Z_f on a reduced K2 template at p = 5, by kernel ranks
  7 BEYOND-CLASS2-20261027-001B (realization experiment): verdict supported
Run: python3 -B check.py [--write]"""
import glob
import itertools
import json
import os
import sys
import time
import numpy as np

T_START = time.time()

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
EXP = glob.glob(os.path.join(ROOT, "experiments/BEYOND-CLASS2-20261027-001B/*E001_*"))[0]
sys.path.insert(0, EXP)
sys.path.insert(1, glob.glob(os.path.join(ROOT, "proofs/COPRIME-CLASS2-20261026-001B/*P001_*"))[0])
sys.path.insert(2, glob.glob(os.path.join(ROOT, "proofs/BEYOND-CLASS2-20261027-001A/*P001_*"))[0])
sys.path.insert(3, glob.glob(os.path.join(ROOT, "proofs/CLASSK-DICHOTOMY-20261026-001A/*P001_*"))[0])
import mlib  # noqa: E402  (experiment B's braid helpers, read-only)
import cp_lib as C  # noqa: E402
import bc_lib as Bc  # noqa: E402
import ck_lib as K  # noqa: E402

PRIMES = (5, 7, 11, 13)
BIG = (1 << 61) - 1          # Magnus coefficients over Z are read mod a large prime (all are tiny integers)
out = {}
ok_all = True


def report(key, ok, detail):
    global ok_all
    out[key] = {"ok": bool(ok), "detail": detail}
    ok_all &= bool(ok)
    print(("PASS " if ok else "FAIL ") + key + ": " + str(detail), flush=True)


def E(i, j):
    M = np.zeros((4, 4), dtype=np.int64)
    M[i, j] = 1
    return M


# ---------------------------------------------------------------- 1 group
ok = True
chars = {}
for p in PRIMES:
    D = np.diag([1, p - 1, 1, p - 1]).astype(np.int64)
    for (i, j) in [(0, 1), (1, 2), (2, 3), (0, 2), (1, 3), (0, 3)]:
        conj = D @ E(i, j) @ D % p
        sign = 1 if ((conj - E(i, j)) % p == 0).all() else (-1 if ((conj + E(i, j)) % p == 0).all() else 0)
        chars[(i + 1, j + 1)] = sign
        ok &= sign == (1 if (i, j) in [(0, 2), (1, 3)] else -1)
L4 = Bc.four_way_algebra(5, 2, 1)
hard = Bc.graded_hard_pairs(L4)
report("1 group", ok and not hard, {"characters of E12, E23, E34, E13, E24, E14": [chars[k] for k in
                                    [(1, 2), (2, 3), (3, 4), (1, 3), (2, 4), (1, 4)]], "graded hard pairs (r = 2)": hard})


# ---------------------------------------------------------------- 2 J-invariance over Z
def J_int(n):
    M = np.zeros((n, n), dtype=np.int64)
    for q in range(n):
        M[q, q] = 1
        for q2 in range(q):
            M[q, q2] = 2 * (-1) ** (q - q2)
    return M


def bur_letter(n, g):
    B = np.eye(n, dtype=np.int64)
    i = abs(g) - 1
    if g > 0:
        B[i, i], B[i, i + 1], B[i + 1, i], B[i + 1, i + 1] = 2, -1, 1, 0
    else:
        B[i, i], B[i, i + 1], B[i + 1, i], B[i + 1, i + 1] = 0, 1, -1, 2
    return B


ok = True
cases = 0
for n in range(2, 13):
    J = J_int(n)
    for i in range(1, n):
        for g in (i, -i):
            B = bur_letter(n, g)
            ok &= (B.T @ J @ B == J).all() and (B.T @ J.T @ B == J.T).all()
            cases += 1
    for q in range(n - 1):        # (J^T s)_q + (J^T s)_{q+1} = -(s_{q+1} - s_q) as integer row identities
        row = J.T[q] + J.T[q + 1]
        target = np.zeros(n, dtype=np.int64)
        target[q], target[q + 1] = 1, -1
        ok &= (row == target).all()
    alt = J.T @ np.ones(n, dtype=np.int64)
    ok &= (alt == np.array([(-1) ** (n - 1 - q) for q in range(n)])).all()
report("2 J-invariance", ok, {"letters checked over Z": cases, "n": "2..12",
                              "bundle identity": "(J^T s)_q + (J^T s)_{q+1} = s_q - s_{q+1}",
                              "J^T 1": "((-1)^(n-1-q))_q, the Artin identity vector up to sign"})


# ---------------------------------------------------------------- 3 symmetric-power constructions
def aff(a, e, p):
    return np.array([[1, a % p], [0, e % p]], dtype=np.int64)


def sym3(M, p):
    a, e = int(M[0, 1]), int(M[1, 1])
    return np.array([[1, a, a * a, a ** 3], [0, e, 2 * a * e, 3 * a * a * e], [0, 0, e * e, 3 * a * e * e],
                     [0, 0, 0, e ** 3]], dtype=np.int64) % p


def sym2(M, p):
    a, e = int(M[0, 1]), int(M[1, 1])
    return np.array([[1, a, a * a], [0, e, 2 * a * e], [0, 0, e * e]], dtype=np.int64) % p


def blocks(*bs):
    n = sum(b.shape[0] for b in bs)
    M = np.zeros((n, n), dtype=np.int64)
    k = 0
    for b in bs:
        M[k:k + b.shape[0], k:k + b.shape[0]] = b
        k += b.shape[0]
    return M


def construction(pattern, M, p):
    e = int(M[1, 1])
    one = np.array([[1]], dtype=np.int64)
    chi = np.array([[e % p]], dtype=np.int64)
    return {(1, 1, 1): lambda: sym3(M, p),
            (1, 1, 0): lambda: blocks(sym2(M, p), chi),
            (0, 1, 1): lambda: blocks(one, e * sym2(M, p) % p),
            (1, 0, 1): lambda: blocks(M, M),
            (1, 0, 0): lambda: blocks(M, one, chi),
            (0, 1, 0): lambda: blocks(one, e * M % p, chi),
            (0, 0, 1): lambda: blocks(one, chi, M),
            (0, 0, 0): lambda: blocks(one, chi, one, chi)}[pattern]() % p


ok = True
consts = {}
for p in PRIMES:
    D = np.diag([1, p - 1, 1, p - 1]).astype(np.int64)
    group = [aff(a, e, p) for a in range(p) for e in (1, -1)]
    for pattern in itertools.product((0, 1), repeat=3):
        R = {(int(M[0, 1]), int(M[1, 1])): construction(pattern, M, p) for M in group}
        for M1, M2 in itertools.product(group, repeat=2):
            prod = M1 @ M2 % p
            ok &= ((R[(int(M1[0, 1]), int(M1[1, 1]))] @ R[(int(M2[0, 1]), int(M2[1, 1]))] - R[(int(prod[0, 1]),
                    int(prod[1, 1]))]) % p == 0).all()
        ks = set()
        for M in group:
            X = R[(int(M[0, 1]), int(M[1, 1]))]
            e = int(M[1, 1])
            Dk = D if e == p - 1 else np.eye(4, dtype=np.int64)
            U = X @ Dk % p
            ok &= (np.tril(U, -1) % p == 0).all() and (np.diag(U) % p == 1).all()
            c = (e * int(M[0, 1])) % p            # left-cocycle value: a = chi(g) c(g)
            sup = [int(U[0, 1]), int(U[1, 2]), int(U[2, 3])]
            if c:
                ks.add(tuple(s * pow(c, p - 2, p) % p for s in sup))
            else:
                ok &= sup == [0, 0, 0]
        ok &= len(ks) == 1
        k = ks.pop()
        ok &= all((k[t] != 0) == bool(pattern[t]) for t in range(3))
        ok &= (R[(0, p - 1)] % p == D).all()
        consts[(p, pattern)] = k
report("3 constructions", ok, {"superdiagonal constants at p = 5": {str(pt): consts[(5, pt)] for pt in
                                itertools.product((0, 1), repeat=3)},
                               "checked": "homomorphism on all of Aff(F_p), values in G_p, constants g-independent and "
                                          "nonzero exactly on the pattern, reflection fixing 0 -> D; p = 5, 7, 11, 13"})


# ---------------------------------------------------------------- 4 the pure braid P4
st = mlib.artin_conj(mlib.P4, 4)
ok = all(g == j for j, (W, g) in enumerate(st))
M3 = []
for j, (W, g) in enumerate(st):
    mg = mlib.magnus(W, 3, BIG)
    ok &= all(len(k) in (0, 3) for k in mg)
    M3.append({k: (v if v < BIG // 2 else v - BIG) for k, v in mg.items() if len(k) == 3})
ok &= all(len(m) == 4 and all(len(set(k) | {j}) == 4 and abs(v) == 1 for k, v in m.items()) for j, m in enumerate(M3))
imgC = mlib.artin(C.cable(mlib.P4, 2), 8)
for j in range(4):
    Wsub = mlib.subst(st[j][0], lambda k: [(2 * k + 1, 1), (2 * k, 1)])
    for t in range(2):
        ok &= mlib.red(Wsub + [(2 * j + t, 1)] + mlib.inv(Wsub)) == imgC[2 * j + t]
for g1 in (1, -1, 2, -2, 3, -3):     # base case of the induction in Lemma 4.1: one cabled letter acts by bundle substitution
    stg = mlib.artin_conj([g1], 4)
    imgg = mlib.artin(C.cable([g1], 2), 8)
    for j in range(4):
        Wsub = mlib.subst(stg[j][0], lambda k: [(2 * k + 1, 1), (2 * k, 1)])
        tgt = stg[j][1]
        for t in range(2):
            ok &= mlib.red(Wsub + [(2 * tgt + t, 1)] + mlib.inv(Wsub)) == imgg[2 * j + t]
Bcab = np.eye(8, dtype=np.int64)
for g in C.cable(mlib.P4, 2):
    Bcab = bur_letter(8, g) @ Bcab
ok &= (Bcab == np.eye(8, dtype=np.int64)).all()
report("4 pure braid P4", ok, {"degree-3 tensor M_j (i1 i2 i3)": {str(j): {str(k): v for k, v in M3[j].items()} for j in
                                                                   range(4)},
                               "cable": "2-cable acts by substituting x_{2k+1} x_{2k}; its coloring transport is I over Z",
                               "conjugator lengths": [len(W) for W, g in st]})


# ---------------------------------------------------------------- 5 the edge weight
def phi0_count(p):
    """#{(A, B) in (F_p^3)^2 : Phi_0(A, B, .) = 0}, Phi_0 = sum M_0(i1 i2 i3) A_i1 B_i2 C_i3 (leaves 1..3)"""
    AB = K.all_vectors(p, 6)
    coef = np.zeros((len(AB), 3), dtype=np.int64)
    for (i1, i2, i3), v in M3[0].items():
        coef[:, i3 - 1] = (coef[:, i3 - 1] + v * AB[:, i1 - 1] * AB[:, 3 + i2 - 1]) % p
    return int((coef == 0).all(axis=1).sum())


counts = {p: phi0_count(p) for p in PRIMES}
ok = all(counts[p] == 2 * p ** 4 - p ** 2 for p in PRIMES)


def f_of(d, p):
    """f(d) = sum over private leaf values of omega^(2 T(d, pi)); sum over the s-slot privates done exactly"""
    w = np.exp(2j * np.pi * np.arange(p) / p)
    CAB = K.all_vectors(p, 9)
    Y = [np.full(len(CAB), d[0])] + [CAB[:, k] for k in range(3)]
    X = [np.full(len(CAB), d[1])] + [CAB[:, 3 + k] for k in range(3)]
    Wv = [np.full(len(CAB), d[2])] + [CAB[:, 6 + k] for k in range(3)]
    Phi = [np.zeros(len(CAB), dtype=np.int64) for _ in range(4)]
    for j in range(4):
        for (i1, i2, i3), v in M3[j].items():
            Phi[j] = (Phi[j] + v * Y[i1] * X[i2] * Wv[i3]) % p
    mask = (Phi[1] == 0) & (Phi[2] == 0) & (Phi[3] == 0)
    hist = np.bincount((2 * d[3] * Phi[0][mask]) % p, minlength=p)
    val = p ** 3 * np.dot(hist, w)
    return val


p = 5
fpat = {}
for pat in itertools.product((0, 1), repeat=4):
    v = f_of(pat, p)
    v2 = f_of(tuple((x * 2) % p for x in pat), p) if any(pat) else v
    integral = abs(v.imag) < 1e-6 and abs(v.real - round(v.real)) < 1e-6
    fpat[pat] = int(round(v.real))
    ok &= integral and abs(v2 - v) < 1e-6
ok &= fpat[(0, 0, 0, 0)] == p ** 12 and fpat[(0, 0, 0, 1)] == p ** 6 * (2 * p ** 4 - p ** 2)
minors = {q: (q ** 12) ** 4 - (q ** 6 * (2 * q ** 4 - q ** 2)) ** 4 for q in PRIMES}
ok &= all(m != 0 for m in minors.values())
report("5 edge weight", ok, {"count 2p^4 - p^2": counts, "f on support patterns (y, x, w, s) at p = 5":
                             {str(k): v for k, v in fpat.items()}, "minor f(0)^4 - f(d*)^4 nonzero": True})


# ---------------------------------------------------------------- 6 count identity on a reduced K2 template
p = 5
nV = 5                              # coordinates X_u, X_v, z1, z2, z3; leaves: X_v - X_u, z1, z2, z3 (no unused coordinates)
leafmat = np.array([[-1, 1, 0, 0, 0], [0, 0, 1, 0, 0], [0, 0, 0, 1, 0], [0, 0, 0, 0, 1]], dtype=np.int64)
YX = K.all_vectors(p, 2 * nV)
measured = 0
for s0 in range(0, len(YX), 1 << 20):
    ch = YX[s0:s0 + (1 << 20)]
    ly = (ch[:, :nV] @ leafmat.T) % p
    lx = (ch[:, nV:] @ leafmat.T) % p
    Mleaf = np.zeros((len(ch), 4, 4), dtype=np.int64)          # bilinear form in the (c_w, s) leaf values
    for j in range(4):
        for (i1, i2, i3), v in M3[j].items():
            Mleaf[:, i3, j] = (Mleaf[:, i3, j] + 2 * v * ly[:, i1] * lx[:, i2]) % p
    Mfull = np.einsum("ia,Pij,jb->Pab", leafmat, Mleaf, leafmat) % p
    measured += int(sum(p ** (nV - int(r)) for r in K.batch_rank(Mfull, p)))
Zf = p ** 4 * sum(fpat[tuple(int(x != 0) for x in d)] for d in itertools.product(range(p), repeat=4))
assert Zf % p ** nV == 0
report("6 count identity", measured == Zf // p ** nV,
       {"#Lambda by kernel ranks": measured, "p^(-N) Z_f(K2) (N = 5, no unused coordinates)": Zf // p ** nV})


# ---------------------------------------------------------------- 7 experiment B
res = os.path.join(ROOT, "artifacts/BEYOND-CLASS2-20261027-001B/BEYOND-CLASS2-20261027-001B-E001_four_way_massey_form_on_gadget_surgeries/result.json")
verdict = json.load(open(res))["verdict"] if os.path.exists(res) else "missing"
report("7 realization experiment", verdict == "supported", {"verdict": verdict})

out["all_ok"] = ok_all
if "--write" in sys.argv:
    with open(os.path.join(HERE, "result.json"), "w") as fh:
        json.dump({"schema_version": 1, "artifact_id": "BEYOND-CLASS2-20261027-001C-P001",
                   "status": "Proved" if ok_all else "Failed", "checks": out,
                   "seconds": round(time.time() - T_START, 1)}, fh, indent=1)
        fh.write("\n")
print("ALL OK" if ok_all else "SOME CHECK FAILED")
