#!/usr/bin/env python3
"""Exact checks for FOLD-20261112-001A-P001: on base 16, the travelling triple is a bond of four with the origin at every distance.

Base 16 (BOND-BALLS-20261111-001A-E001's index 16) has knot kinds {0, (0,1), (1,-1)} and {0, (0,2), (1,1)}. In the sheared frame
(x, y) -> (x, y + x) they become {0, (0,1), (1,0)} and {0, (0,2), (1,2)}: every knot is a pair in column x with a distinction in
column x + 1, and the triple T_x = {(x,0), (x,1), (x,2)} travels straight along x. All checks are in the sheared frame.

  C1. The column rule: a pair of columns (c, d) satisfies every knot between them exactly when, for every y, c(y) = c(y+1) implies
      d(y) != c(y) and c(y) = c(y+2) implies d(y+2) != c(y) (checked on every pair of columns of period 3 to 8).
  C2. Every k >= 3: each three-element part of {(-k,0), (-k,1), (-k,2), (0,0)} (a translate of C3's set at j = 0; the proof's B_k is
      the translate of C3's set at j = 2) is free, by states periodic in y with period 3 to 8 (exact transfer graphs; their Boolean
      powers are eventually periodic, so finitely many k cover every k).
  C3. Forward bonds, every k >= 3: each three-element part of {(0,0), (0,1), (0,2), (k,j)} is free, for j = 0, 1, 2, likewise.
  C4. Pairs: {(0,0), (-k,i)} and {(0,0), (k,j)} take all four patterns for every k >= 3 (the faithful reading keeps them apart).
  C5. Mutation: without the second knot kind the triple does not travel: the set is not refuted in a window (by SAT), so the forcing
      that refutes it with both kinds is gone.

Usage: check.py [--write]   (the workspace .venv)
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
from pysat.solvers import Minisat22

HERE = Path(__file__).resolve().parent
MS = range(3, 9)


def bit(c, y, m):
    return (c >> (y % m)) & 1


def transition(m):
    n = 1 << m
    A = np.zeros((n, n), dtype=bool)
    for c in range(n):
        for d in range(n):
            ok = True
            for y in range(m):
                if bit(c, y, m) == bit(c, y + 1, m) and bit(d, y, m) == bit(c, y, m):
                    ok = False
                    break
                if bit(c, y, m) == bit(c, y + 2, m) and bit(d, y + 2, m) == bit(c, y, m):
                    ok = False
                    break
            A[c, d] = ok
    return A


def knots_between(c, d, m):
    """The knots between columns c and d of a strip of period m, as triples of (column, row) values."""
    out = []
    for y in range(m):
        out.append((bit(c, y, m), bit(c, y + 1, m), bit(d, y, m)))          # {(x,y), (x,y+1), (x+1,y)}
        out.append((bit(c, y, m), bit(c, y + 2, m), bit(d, y + 2, m)))      # {(x,y), (x,y+2), (x+1,y+2)}
    return out


def c1():
    bad = 0
    for m in MS:
        A = transition(m)
        for c in range(1 << m):
            for d in range(1 << m):
                nae = all(not (a == b == e) for a, b, e in knots_between(c, d, m))
                bad += nae != A[c, d]
    return {"violations": bad, "holds": bad == 0}


def recurrent(A):
    fut = np.ones(len(A), bool)
    while True:
        new = fut & A[:, fut].any(axis=1)
        if (new == fut).all():
            break
        fut = new
    past = np.ones(len(A), bool)
    while True:
        new = past & A[past, :].any(axis=0)
        if (new == past).all():
            break
        past = new
    return past, fut


def coverage_sequence(m):
    """For k = 1, 2, ...: the patterns realized on the backward and forward parts by bi-infinite paths, until A^k repeats.
    Returns (covs, k0, p): covs[k] for k = 1 .. k0 + p - 1, and A^(k0 + p) = A^k0."""
    A = transition(m)
    past, fut = recurrent(A)
    Ai = A.astype(np.int64)
    M = np.eye(len(A), dtype=bool)
    seen = {}
    covs = {}
    k = 0
    while True:
        k += 1
        M = (M.astype(np.int64) @ Ai) > 0
        key = M.tobytes()
        if key in seen:
            return covs, seen[key], k - seen[key], A, past, fut
        seen[key] = k
        R = M & past[:, None] & fut[None, :]
        ci, di = np.nonzero(R)
        cov = {}
        # backward: column -k holds the triple (rows 0, 1, 2), column 0 holds the target (row 0)
        for i, j in ((0, 1), (0, 2), (1, 2)):
            cov[f"back T{i}T{j} o"] = {(bit(c, i, m), bit(c, j, m), bit(d, 0, m)) for c, d in zip(ci, di)}
        for i in range(3):
            cov[f"back pair T{i} o"] = {(bit(c, i, m), bit(d, 0, m)) for c, d in zip(ci, di)}
        # forward: column 0 holds the triple, column k holds the target at row j
        for j in range(3):
            for a, b in ((0, 1), (0, 2), (1, 2)):
                cov[f"fwd O{a}O{b} t{j}"] = {(bit(c, a, m), bit(c, b, m), bit(d, j, m)) for c, d in zip(ci, di)}
            cov[f"fwd pair o t{j}"] = {(bit(c, 0, m), bit(d, j, m)) for c, d in zip(ci, di)}
        covs[k] = cov


def c2_c4():
    seqs = {m: coverage_sequence(m) for m in MS}
    K0 = max(s[1] for s in seqs.values())
    L = 1
    for s in seqs.values():
        L = L * s[2] // math.gcd(L, s[2])
    triple_free = set()
    for m, (covs, k0, p, A, past, fut) in seqs.items():
        triple_free |= {(bit(c, 0, m), bit(c, 1, m), bit(c, 2, m)) for c in np.nonzero(past & fut)[0]}

    def cov_at(m, k):
        covs, k0, p = seqs[m][0], seqs[m][1], seqs[m][2]
        return covs[k] if k < k0 + p else covs[k0 + (k - k0) % p]
    bad = []
    for k in range(3, K0 + L + 1):
        union = {}
        for m in MS:
            for name, s in cov_at(m, k).items():
                union.setdefault(name, set()).update(s)
        for name, s in union.items():
            need = 4 if "pair" in name else 8
            if len(s) < need:
                bad.append((k, name, need - len(s)))
    return {"periods": {m: [seqs[m][1], seqs[m][2]] for m in MS}, "k checked": [3, K0 + L], "triple free": len(triple_free) == 8,
            "uncovered": bad[:10], "holds": not bad and len(triple_free) == 8}


def c5():
    """Without the second knot kind: is {(-3,0), (-3,1), (-3,2), (0,0)} constrained? Brute force on the window |x| <= 6, |y| <= 8
    by SAT (with only the first kind the triple does not travel)."""
    def constrained(kinds):
        cells = [(x, y) for x in range(-6, 3) for y in range(-6, 10)]
        idx = {c: i + 1 for i, c in enumerate(cells)}
        cl = []
        for (x, y) in cells:
            for kind in kinds:
                pts = [(x + a, y + b) for a, b in kind]
                if all(p in idx for p in pts):
                    cl.append([idx[p] for p in pts])
                    cl.append([-idx[p] for p in pts])
        S = [(-3, 0), (-3, 1), (-3, 2), (0, 0)]
        with Minisat22(bootstrap_with=cl) as s:
            return any(not s.solve(assumptions=[idx[p] * (1 if (b >> i) & 1 else -1) for i, p in enumerate(S)]) for b in range(16))
    full = constrained([((0, 0), (0, 1), (1, 0)), ((0, 0), (0, 2), (1, 2))])
    mutant = constrained([((0, 0), (0, 1), (1, 0))])
    return {"constrained with both kinds": full, "constrained with the first kind only": mutant, "holds": full and not mutant}


def main():
    out = {"C1": c1(), "C2-C4": c2_c4(), "C5": c5()}
    out["failures"] = [k for k in ("C1", "C2-C4", "C5") if not out[k]["holds"]]
    print(json.dumps(out, indent=1, default=str))
    if "--write" in sys.argv:
        manifest = json.loads((HERE / "manifest.json").read_text())
        result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
                  "proof": manifest["proof"], "status": "passed" if not out["failures"] else "failed", "claim": manifest["claim"], **out}
        (HERE / "result.json").write_text(json.dumps(result, indent=1, default=str) + "\n")
    return 0 if not out["failures"] else 1


if __name__ == "__main__":
    sys.exit(main())
