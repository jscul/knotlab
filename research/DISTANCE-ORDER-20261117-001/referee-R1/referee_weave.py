"""Referee R1 for DISTANCE-ORDER-20261117-001: the weave's counts, exactly, by the referee's own transfer matrix.

  .venv/bin/python -B referee_weave.py > referee_weave.json

W(L): distinctions v(i, j) = i + L j, knots (v(i,j), v(i+1,j), v(i,j+1)) and (v(i+1,j), v(i,j+1), v(i+1,j+1)), not all equal.
A row is an L-bit state; T[a][b] = 1 when rows a (row j) and b (row j + 1) satisfy every knot between them. Then
  N = trace(T^L), and for two distinctions in one row, d(v(0,0), v(c,0)) = sum over rows a with a_0 != a_c of (T^L)[a][a].
T^h is computed exactly in int64 for h <= L/2 (its entries stay far below 2^63, checked), and the diagonal of T^L as exact
Python integers. Compared with the study's results.json (N and the rates along a row).
Also: zero betweenness on W(L), checked exactly through statement 1 (c lies between a and b iff no allowed state has
a = b != c), by SAT for every pair (b, c) with a = v(0, 0) (the weave's translations make a's position arbitrary).
"""
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "artifacts/DISTANCE-ORDER-20261117-001B/DISTANCE-ORDER-20261117-001B-E001_order/results.json"


def transfer(L):
    R = 1 << L
    a = np.arange(R)
    bit = lambda x, i: (x >> (i % L)) & 1
    T = np.ones((R, R), dtype=np.int64)
    for i in range(L):
        ai, ai1 = bit(a, i)[:, None], bit(a, i + 1)[:, None]
        bi, bi1 = bit(a, i)[None, :], bit(a, i + 1)[None, :]
        T &= ~((ai == ai1) & (ai1 == bi)).astype(np.int64) & 1
        T &= ~((ai1 == bi) & (bi == bi1)).astype(np.int64) & 1
    return T


def exact_diag_power(T, L):
    """The diagonal of T^L as Python ints, via T^h with h = L // 2 (int64) and T^(L - h)."""
    h = L // 2
    P = np.eye(len(T), dtype=np.int64)
    for _ in range(h):
        P = P @ T
        assert P.max() < (1 << 62) // len(T), "int64 margin"
    Q = P if L - h == h else P @ T
    assert Q.max() < (1 << 62) // len(T)
    Pl, Ql = P.astype(object), Q.astype(object)
    return [int(sum(Pl[x, :] * Ql[:, x])) for x in range(len(T))]


PRIMES = (1000003, 1000033, 1000037, 1000039, 1000081, 1000099)  # the referee's own moduli, all prime, below 2^20


def modular_diag_power(T, L):
    """The diagonal of T^L as exact integers, from float64 products modulo primes below 2^20 (every product and partial sum
    stays below 2^53, so each is exact), joined by the Chinese remainder theorem (the referee's own implementation)."""
    Tf = T.astype(np.float64)
    h = L // 2
    residues = []
    for p in PRIMES:
        P = np.eye(len(T))
        for _ in range(h):
            P = np.mod(P @ Tf, p)
        Q = P if L - h == h else np.mod(P @ Tf, p)
        residues.append(np.mod((P * Q.T).sum(axis=1), p).astype(np.int64))
    M = 1
    for p in PRIMES:
        M *= p
    out = []
    for x in range(len(T)):
        v = 0
        for r, p in zip(residues, PRIMES):
            q = M // p
            v += int(r[x]) * q * pow(q, -1, p)
        out.append(v % M)
    return out


def weave_rows(L):
    T = transfer(L)
    diag = exact_diag_power(T, L) if L <= 9 else modular_diag_power(T, L)
    N = sum(diag)
    R = 1 << L
    d = {}
    for c in range(1, L):
        d[c] = sum(diag[x] for x in range(R) if ((x >> 0) & 1) != ((x >> c) & 1))
    return N, d


def no_betweenness(L):
    from pysat.solvers import Cadical195
    n = L * L
    v = lambda i, j: (i % L) + L * (j % L)
    cl = []
    for j in range(L):
        for i in range(L):
            for t in ((v(i, j), v(i + 1, j), v(i, j + 1)), (v(i + 1, j), v(i, j + 1), v(i + 1, j + 1))):
                cl.append([x + 1 for x in t])
                cl.append([-(x + 1) for x in t])
    between = 0
    with Cadical195(bootstrap_with=cl) as S:
        for b in range(1, n):
            for c in range(1, n):
                if c == b:
                    continue
                # c between a = 0 and b iff no state has x_0 = x_b != x_c; by flipping every value, test x_0 = x_b = 0, x_c = 1
                if not S.solve(assumptions=[-1, -(b + 1), c + 1]):
                    between += 1
    return between


def main():
    study = {w["name"]: w for w in json.load(open(RES))["b3_weave"]}
    out = {}
    for L in (6, 9, 12):
        N, d = weave_rows(L)
        s = study[f"weave L={L}"]
        row = {"N_referee": str(N), "N_study": s["N"], "N_agree": str(N) == s["N"],
               "rate_along_row_referee": {c: str(Fraction(d[c], N)) for c in d},
               "rate_along_row_study": {r[0]: r[1] for r in (s["rate_along_line"] if isinstance(s["rate_along_line"], list)
                                                          else [])},
               "rate_along_row_float": {c: float(Fraction(d[c], N)) for c in d},
               "below_half_exactly_at_multiples_of_3": all((Fraction(d[c], N) < Fraction(1, 2)) == (c % 3 == 0) for c in d),
               "one_step_rate": str(Fraction(d[1], N))}
        if L <= 9:
            row["betweenness_triples_through_a_fixed_a"] = no_betweenness(L)
        out[L] = row
        print(L, row["N_referee"], row["N_study"], row["N_agree"], row["below_half_exactly_at_multiples_of_3"], flush=True)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
