#!/usr/bin/env python3
"""Stress test for CONE-COLLAPSE-20261109-001, one size past what ticket A checked: side 128 (the cone has 8128 states).

Stage 1 (exact): the collapse on the cone (A_cone^(255 e) = I for the least power of two e); the traces tr(A_cone^j) for
j = 1 to 255 against the powers of two mod 255; the cone polynomial at 128, to degree 128, against the one at 64 (both from
det(I + C_s(w)) modulo w^129); the return map's trace at 128; the return map's characteristic polynomial at 64.
Stage 2 (exact): for every class of 255-th roots of unity, its generalized eigenspace ker m_s(A_cone^256) (a GF(2) null space),
whose dimension gives the multiplicity (against the triangular numbers and the parity law), and the restriction of A_cone to it, whose
kernel dimensions of m_s(.)^j give the Jordan blocks (against 2k - 1, 2k - 5, ...).
Each stage rewrites stress_test.json when it ends; STRESS_FROM_STAGE=2 reuses a saved stage 1. Run under a memory cap
(CONE-COLLAPSE-S1 in docs/LONG_RUNNING.md)."""
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("OPENBLAS_NUM_THREADS", "12")
os.environ.setdefault("OMP_NUM_THREADS", "12")
import numpy as np  # noqa: E402
import scipy.sparse as sps  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LIB = ROOT / "proofs/CONE-COLLAPSE-20261109-001A/CONE-COLLAPSE-20261109-001A-P001_the_cone_and_its_return_map"
sys.path.insert(0, str(LIB))
import collapse_lib as L  # noqa: E402

T0 = time.time()
OUT_DIR = Path(os.environ.get("STRESS_OUT", str(HERE)))
OUT_PATH = OUT_DIR / "stress_test.json"
LOG = OUT_DIR / "stress_test_log.txt"
N = int(os.environ.get("STRESS_N", "128"))   # a smaller side only to test the script
Q = 2 * N - 1
RES = {"side": N, "stages": {}}


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    with open(LOG, "a") as f:
        f.write("[%6.0fs] %s\n" % (time.time() - T0, s))


def save(final=False):
    st = RES["stages"]
    RES["pass"] = all(v.get("pass") for v in st.values()) if final else None
    RES["seconds"] = round(time.time() - T0)
    OUT_PATH.write_text(json.dumps(RES, indent=1, default=str) + "\n")


def dmm(A, B):
    return np.mod(A @ B, np.float32(2))


def det_mod(M, prec):
    """det of a polynomial matrix with M = I mod w, modulo w^prec, by elimination with unit pivots"""
    mask = (1 << prec) - 1
    A = [[x & mask for x in r] for r in M]
    n = len(A)

    def inv(f):
        g, rem = 0, 1
        for i in range(prec):
            if (rem >> i) & 1:
                g |= 1 << i
                rem ^= f << i
            rem &= mask
        return g
    d = 1
    for k in range(n):
        p = A[k][k]
        assert p & 1
        d = L.pmul(d, p) & mask
        ip = inv(p)
        for i in range(k + 1, n):
            if A[i][k]:
                f = L.pmul(A[i][k], ip) & mask
                A[i] = [(x ^ L.pmul(f, y)) & mask for x, y in zip(A[i], A[k])]
    return d


def stage1(Ac, As):
    rec = {}
    m = Ac.shape[0]
    pw2 = {pow(2, i, Q) for i in range(Q)}
    Pw = np.eye(m, dtype=np.float32)
    bad = []
    AsT = As.T.tocsr()
    for j in range(1, Q + 1):
        Pw = np.mod((AsT @ Pw.T).T, np.float32(2))
        if (int(np.trace(Pw)) % 2) != (1 if j % Q in pw2 else 0):
            bad.append(j)
    rec["traces: j checked"] = Q
    rec["traces: mismatches"] = bad
    log("traces done, mismatches", bad)
    Aq = Pw  # A^255
    I = np.eye(m, dtype=np.float32)
    e, X = 1, Aq
    while not np.array_equal(X, I) and e <= 512:
        X = dmm(X, X)
        e *= 2
    rec["least e (power of two) with A_cone^(255 e) = I"] = e if e <= 512 else None
    log("collapse: e =", e)
    # stability and the return map at 128 and 64
    prec = N + 1
    polys = {}
    for n in (N // 2, N):
        rm = L.return_map(n)
        polys[n] = det_mod(L.pmat_plus_identity(rm["Cs"]), prec)
        tr = 0
        for i in range(n // 2):
            tr ^= rm["Cs"][i][i]
        rec["tr C_s = w + w^3 at %d" % n] = tr == 0b1010
        log("return map at", n, "done")
    x = polys[N // 2] ^ polys[N]
    rec["cone polynomials at %d and %d first differ at degree" % (N // 2, N)] = L.val(x) if x else None
    rec["cone polynomial at %d below degree %d" % (N, prec)] = [i for i in range(prec) if (polys[N] >> i) & 1]
    # the return map's characteristic polynomial at 64
    rm = L.return_map(N // 2)
    ech = L.charpoly_berkowitz(rm["Cs"])
    h, mm = N // 4, (N // 2).bit_length() - 1
    rec["e_j at 64: e_1 = w + w^3"] = ech[1] == 0b1010
    rec["e_j at 64: valuations j(2j - 1)"] = all(L.val(ech[j]) == j * (2 * j - 1) for j in range(1, h + 1))
    rec["e_j at 64: e_(h-1) formula"] = ech[h - 1] == L.pmul(1 << ((h - 1) * (2 * h - 3)),
                                                             L.psquare(sum(1 << ((1 << i) - 1) for i in range(mm))))
    log("return map characteristic polynomial at", N // 2, "done")
    rec["pass"] = (not bad and rec["least e (power of two) with A_cone^(255 e) = I"] is not None
                   and rec["cone polynomials at %d and %d first differ at degree" % (N // 2, N)] == N
                   and rec["tr C_s = w + w^3 at %d" % (N // 2)] and rec["tr C_s = w + w^3 at %d" % N]
                   and rec["e_j at 64: e_1 = w + w^3"] and rec["e_j at 64: valuations j(2j - 1)"]
                   and rec["e_j at 64: e_(h-1) formula"])
    return rec


def poly_at(A, f, As=None):
    m = A.shape[0]
    R = np.zeros((m, m), dtype=np.float32)
    for i in range(L.pdeg(f), -1, -1):
        R = dmm(R, A) if As is None else np.mod((As.T.tocsr() @ R.T).T, np.float32(2))
        if (f >> i) & 1:
            R = R + np.eye(m, dtype=np.float32)
        R = np.mod(R, np.float32(2))
    return R


def classes():
    k = (2 * N).bit_length() - 1
    f, mul = L.field(k)
    out = []
    for c in L.cosets(Q):
        out.append({"coset": c[0], "size": len(c), "minpoly": L.minpoly_of_coset(c, mul, k),
                    "Tr(1/lambda)": L.trace_of_power((-c[0]) % Q, mul, k)})
    return f, out


def nullspace2(M):
    """basis of {v : M v = 0} over GF(2) as a 0/1 array (columns), with the free coordinates that index it"""
    rows, cols = M.shape
    A = np.packbits(np.asarray(M, dtype=np.uint8) & 1, axis=1)
    piv, r = [], 0
    for c in range(cols):
        if r == rows:
            break
        byte, mask = c // 8, np.uint8(1 << (7 - c % 8))
        hit = np.nonzero(A[r:, byte] & mask)[0]
        if hit.size == 0:
            continue
        p = r + hit[0]
        if p != r:
            A[[r, p]] = A[[p, r]]
        others = np.nonzero(A[:, byte] & mask)[0]
        others = others[others != r]
        if others.size:
            A[others, byte:] ^= A[r, byte:]
        piv.append(c)
        r += 1
    R = np.unpackbits(A[:r], axis=1)[:, :cols]
    pivset = set(piv)
    free = [c for c in range(cols) if c not in pivset]
    K = np.zeros((cols, len(free)), dtype=np.float32)
    for t, f in enumerate(free):
        K[f, t] = 1
    if r:
        K[piv, :] = R[:, free]
    return K, free


def stage2(Ac, As, cls):
    m = Ac.shape[0]
    A256 = Ac.astype(np.float32)
    for _ in range(8):
        A256 = dmm(A256, A256)
    total, rows = 0, []
    for r in cls:
        K, free = nullspace2(poly_at(A256, r["minpoly"]))
        D = K.shape[1]
        alg = D // r["size"]
        k = L.triangular_index(alg)
        dims = [0]
        if D:
            X = np.mod((As @ K)[free, :], np.float32(2))
            assert np.array_equal(np.mod(K @ X, 2), np.mod(As @ K, 2)), "kernel not invariant"
            Mp = poly_at(X, r["minpoly"])
            Pw, dims = np.eye(D, dtype=np.float32), []
            while True:
                Pw = dmm(Pw, Mp)
                kd = (D - L.rank2(Pw)) // r["size"]
                if dims and kd == dims[-1]:
                    break
                dims.append(kd)
        want = (L.clebsch_gordan_dims(k) or [0]) if k is not None else None
        rows.append({"coset": r["coset"], "size": r["size"], "alg": alg, "k": k, "kernel dims": dims,
                     "Jordan blocks 2k - 1, 2k - 5, ...": dims == want,
                     "parity = Tr(1/lambda)": (alg % 2) == r["Tr(1/lambda)"]})
        total += alg * r["size"]
        log("class", r["coset"], "alg", alg, "k", k, "dims", dims, "CG", dims == want)
    return {"classes": rows, "accounted": total, "cone dimension": m,
            "pass": total == m and all(x["k"] is not None and x["parity = Tr(1/lambda)"]
                                       and x["Jordan blocks 2k - 1, 2k - 5, ..."] for x in rows)}


def main():
    start = int(os.environ.get("STRESS_FROM_STAGE", "1"))
    if start == 1:
        open(LOG, "w").close()
    reps, orb, Ac = L.cone(N)
    Ac = Ac.astype(np.float32)
    As = sps.csr_matrix(Ac)
    log("cone at", N, "states", Ac.shape[0], "from stage", start)
    if start == 1:
        RES["stages"]["1 collapse, traces, stability, return map"] = stage1(Ac, As)
        save()
    else:
        RES["stages"]["1 collapse, traces, stability, return map"] = json.loads(OUT_PATH.read_text())["stages"][
            "1 collapse, traces, stability, return map"]
    f, cls = classes()
    RES["field polynomial"] = f
    RES["stages"]["2 multiplicities, parity and Jordan blocks"] = stage2(Ac, As, cls)
    save(final=True)
    log("done, pass", RES["pass"])


if __name__ == "__main__":
    main()
