"""Referee R1 for WEAVE-MIX-20261117-001 (own code; the study's mixlib is not imported; its stored results are only compared).

  ../../../.venv/bin/python -B referee_weavemix.py <part> > referee_weavemix_<part>.json      (from this directory)

Knot codes 0..3 exclude {000,111}, {100,011}, {010,101}, {001,110} in place order (the study's P).  An arrangement is a dict
(i % pc, j % pr, 'U' | 'D') -> code; up knot (v(i,j), v(i+1,j), v(i,j+1)), down knot (v(i+1,j), v(i,j+1), v(i+1,j+1)).
The row transfer is built with the referee's strip() from WEAVE-LAWS-R1, multiplied over one row period, and split by the global
flip (every knot here is closed under it): flip-even and flip-odd parts give the spin gap (top even against top odd) and the
energy gap (top even against second even), per row in log base 3.  Widths above 12 use the same product applied one distinction
at a time (front of w + 1 bits), with Arnoldi on flip-symmetrised and antisymmetrised vectors.

Parts:
  twist     the gauge groups whose width-6 spectra differ (2 x 1 and 3 x 1): do their members agree at every width that holds
            an even number of column periods, and differ only at the others?
  gaps      the four post hoc survivors and the referee's 2 x 2 law, at widths to 18 (column period 3) or 16 (column period 2):
            states per distinction, spin and energy gaps, by width
  around    the two 3 x 1 survivors' correlations around the cylinder at widths 6, 9 and 12
  corr      for the same five at width 12: correlations along the transfer axis (r rows) and around the cylinder (c columns),
            from the leading eigenvectors; and whether the width-independent 2 x 2 survivor factors into independent strips
"""
from __future__ import annotations

import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import LinearOperator, eigs

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/WEAVE-LAWS-20261117-001/referee-R1"))
from referee_scope import strip  # noqa: E402  (the referee's own strip transfer, WEAVE-LAWS-R1)

EXCL = [frozenset({(0, 0, 0), (1, 1, 1)}), frozenset({(1, 0, 0), (0, 1, 1)}), frozenset({(0, 1, 0), (1, 0, 1)}),
        frozenset({(0, 0, 1), (1, 1, 0)})]
ART = ROOT / "artifacts/WEAVE-MIX-20261117-001B/WEAVE-MIX-20261117-001B-E001_mixes"


def parse(a):
    return {(int(k.split(",")[0]), int(k.split(",")[1]), k.split(",")[2]): v for k, v in a.items()}


def dims(arr):
    return max(i for i, _, _ in arr) + 1, max(j for _, j, _ in arr) + 1


def row_product(w, arr):
    pc, pr = dims(arr)
    M = None
    for j in range(pr):
        T = strip(w, [EXCL[arr[(i % pc, j, "U")]] for i in range(w)], [EXCL[arr[(i % pc, j, "D")]] for i in range(w)])
        T = T.astype(np.float64)
        M = T if M is None else M @ T
    return M


def sectors_dense(M, w):
    R = 1 << w
    full = R - 1
    reps = [a for a in range(R) if a < (a ^ full)]
    comp = [a ^ full for a in reps]
    A, B = M[np.ix_(reps, reps)], M[np.ix_(reps, comp)]
    ev_e = np.sort(np.abs(np.linalg.eigvals(A + B)))[::-1]
    ev_o = np.sort(np.abs(np.linalg.eigvals(A - B)))[::-1]
    return ev_e, ev_o


def site_operator(w, arr):
    """v -> v T (one row period), applied one distinction at a time on fronts of w + 1 bits."""
    pc, pr = dims(arr)
    N = 1 << (w + 1)
    s = np.arange(N)
    bit = [(s >> t) & 1 for t in range(w + 1)]

    def bad(code, a, b, c):
        m = np.zeros(N, bool)
        for p in EXCL[code]:
            m |= (a == p[0]) & (b == p[1]) & (c == p[2])
        return m
    plan = []
    for j in range(pr):
        for i in range(w):
            masks, idxs = [], []
            for x in (0, 1):
                xs = np.full(N, x)
                old_next = bit[i + 1] if i + 1 < w else bit[w]
                m = bad(arr[(i % pc, j, "U")], bit[i], old_next, xs)
                if i >= 1:
                    m |= bad(arr[((i - 1) % pc, j, "D")], bit[i], bit[i - 1], xs)
                if i == w - 1:
                    m |= bad(arr[((w - 1) % pc, j, "D")], bit[w], xs, bit[0])
                idx = (s & ~(1 << i)) | (x << i)
                if i == 0:
                    idx = (idx & ~(1 << w)) | (bit[0] << w)
                masks.append(~m)
                idxs.append(idx)
            plan.append((masks, idxs))

    def apply(v):
        V = np.zeros(N)
        V[: 1 << w] = v
        for k, (masks, idxs) in enumerate(plan):
            new = np.zeros(N)
            for ok, idx in zip(masks, idxs):
                new += np.bincount(idx[ok], weights=V[ok], minlength=N)
            V = new
            if (k + 1) % w == 0:
                V[: 1 << w] += V[1 << w:]
                V[1 << w:] = 0
        return V[: 1 << w]
    return apply


def sectors_large(w, arr, k=4):
    op = site_operator(w, arr)
    R = 1 << w
    flip = np.arange(R) ^ (R - 1)
    out = []
    for sgn in (1, -1):
        def mv(v, sgn=sgn):
            u = op(v)
            return 0.5 * (u + sgn * u[flip])
        L = LinearOperator((R, R), matvec=mv, dtype=np.float64)
        v0 = np.ones(R) if sgn == 1 else (np.arange(R) & 1) * 2.0 - 1.0
        v0 = 0.5 * (v0 + sgn * v0[flip]) + 1e-3 * np.random.default_rng(1).random(R)
        ev = eigs(L, k=k, which="LM", return_eigenvectors=False, tol=1e-10, maxiter=5000, v0=v0)
        out.append(np.sort(np.abs(ev))[::-1])
    return out


def readings(w, arr, dense_max=12):
    pc, pr = dims(arr)
    if w <= dense_max:
        ev_e, ev_o = sectors_dense(row_product(w, arr), w)
    else:
        ev_e, ev_o = sectors_large(w, arr)
    lam0 = ev_e[0]
    if lam0 < 1e-12:
        return {"width": w, "empty": True}
    sec = next((x for x in ev_e[1:] if x < lam0 * (1 - 1e-9)), 0.0)
    lo = ev_o[0]
    return {"width": w, "per_site": float(lam0 ** (1 / (pr * w))),
            "spin_gap": float(math.log(lam0 / lo, 3) / pr) if lo > 1e-12 else float("inf"),
            "energy_gap": float(math.log(lam0 / sec, 3) / pr) if sec > 1e-12 else float("inf")}


def part_twist():
    R = json.load(open(ART / "results.json"))
    out = {}
    for fam, widths in (("2x1", (4, 6, 8, 10)), ("3x1", (6, 9, 12))):      # dense spectra throughout
        pc = int(fam[0])
        rows = R["families"][fam]["rows"]
        g = defaultdict(list)
        for x in rows:
            g[str(x["inconsistent_set"])].append(parse(x["arrangement"]))
        res = {"groups": 0, "agree_at_even_period_counts": 0, "differ_somewhere_at_odd": 0, "examples": [], "not_explained": []}
        for key, arrs in g.items():
            if len(arrs) < 2:                         # a group of one cannot differ
                continue
            vals = {w: [readings(w, a) for a in arrs] for w in widths}
            def same(lst):
                f = lambda r: ("empty",) if r.get("empty") else (round(r["per_site"], 9),
                                                                    round(r["spin_gap"], 7) if math.isfinite(r["spin_gap"]) else "inf")
                return len({f(r) for r in lst}) == 1
            if all(same(vals[w]) for w in widths):
                continue
            res["groups"] += 1
            even = [w for w in widths if (w // pc) % 2 == 0]
            odd = [w for w in widths if (w // pc) % 2 == 1]
            if all(same(vals[w]) for w in even):
                res["agree_at_even_period_counts"] += 1
            else:
                res["not_explained"].append({"inconsistent_set": key, "members": len(arrs),
                                             "per_site_by_width": {w: [None if r.get("empty") else round(r["per_site"], 6)
                                                                       for r in vals[w]] for w in widths},
                                             "spin_gap_by_width": {w: [None if r.get("empty") else round(r["spin_gap"], 4)
                                                                       for r in vals[w]] for w in widths}})
            if any(not same(vals[w]) for w in odd):
                res["differ_somewhere_at_odd"] += 1
            if len(res["examples"]) < 3:
                res["examples"].append({"inconsistent_set": key, "members": len(arrs),
                                        "spin_gap_by_width": {w: [None if r.get("empty") else round(r["spin_gap"], 4)
                                                                  for r in vals[w]] for w in widths}})
        out[fam] = res
        print(fam, json.dumps({k: v for k, v in res.items() if k != "examples"}), file=sys.stderr, flush=True)
    return out


def candidates():
    rd = json.load(open(ART / "readout.json"))
    c = [(f"survivor {k} ({s['family']})", parse(s["arrangement"])) for k, s in enumerate(rd["post_hoc"]["survivors"])]
    law = {(i, j, t): 0 for i in range(2) for j in range(2) for t in "UD"}
    law[(0, 0, "U")] = 3
    c.append(("referee's 2 x 2 law (code 3 on one up knot per 2 x 2 block)", law))
    return c


def part_gaps():
    out = []
    for name, arr in candidates():
        pc, _ = dims(arr)
        widths = (6, 9, 12, 15, 18) if pc == 3 else (4, 6, 8, 10, 12, 14, 16)
        row = {"candidate": name, "readings": []}
        for w in widths:
            r = readings(w, arr)
            row["readings"].append(r)
            print(name, json.dumps(r), file=sys.stderr, flush=True)
        out.append(row)
    return out


def part_corr(w=12, which=None):
    out = []
    for name, arr in (candidates() if which is None else which):
        pc, pr = dims(arr)
        M = row_product(w, arr)
        ev, Rv = np.linalg.eig(M)
        evL, Lv = np.linalg.eig(M.T)
        i0, j0 = np.argmax(np.abs(ev)), np.argmax(np.abs(evL))
        lam = ev[i0].real
        r = np.abs(Rv[:, i0].real)
        l = np.abs(Lv[:, j0].real)
        pi = l * r / (l @ r)                                  # distribution of a row at a period boundary
        X = ((np.arange(1 << w)[:, None] >> np.arange(w)[None, :]) & 1).astype(float)
        m = pi @ X
        around = []
        for c in range(1, w // 2 + 1):
            both = pi @ (X[:, 0] * X[:, c])
            around.append(float((both - m[0] * m[c]) / math.sqrt(m[0] * (1 - m[0]) * m[c] * (1 - m[c]))))
        along = []
        v = X[:, 0] * r
        for k in range(1, 8):
            v = M @ v / lam
            both = (l * X[:, 0]) @ v / (l @ r)
            along.append((k * pr, float((both - m[0] ** 2) / (m[0] * (1 - m[0])))))
        row = {"candidate": name, "width": w, "correlation_around_cylinder_by_columns": around,
               "correlation_along_transfer_by_rows": along,
               "per_site_by_width_equal": None}
        out.append(row)
        print(name, json.dumps({k: row[k] for k in ("correlation_around_cylinder_by_columns", "correlation_along_transfer_by_rows")}),
              file=sys.stderr, flush=True)
    return out


def part_around():
    """For the two 3 x 1 survivors: the correlation around the cylinder at widths 6, 9 and 12 (does it fall with width?)."""
    two = candidates()[:2]
    return {w: part_corr(w, two) for w in (6, 9, 12)}


if __name__ == "__main__":
    res = {"twist": part_twist, "gaps": part_gaps, "corr": part_corr, "around": part_around}[sys.argv[1]]()
    print(json.dumps(res, indent=1, default=str))
