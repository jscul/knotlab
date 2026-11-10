#!/usr/bin/env python3
"""Checks for INVERT-STEP-20261110-001A: persistence needs forgetting.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
On SEPARATE-20261108-001A's net_lib (layout and rule-60 matrices). A substrate is a linear ring rule (one of the eight of LIN) on every
own cell and a linear contact law reading any subset of (itself, its left and right neighbours on ring a, on ring b): 256 substrates,
first order (x <- M x) and second order (x(t + 1) = M x(t) + x(t - 1), invertible by construction). Every first row is open: the state
is tracked as one bit vector per cell over the born cells (one row, or two for second order). A contact binds ring X at a lag when its
value depends on one of X's own born cells (A32); it persists when it binds both rings at every lag, read through a full cycle of the
state (Brent). The theorem is proved by hand; checks 1 and 2 verify it on the family, check 3 is a computation, check 4 reconciles it
with DOUBLE-BALANCE-20261109-001A."""
import hashlib
import itertools
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/SEPARATE-20261108-001A/SEPARATE-20261108-001A-P001_a_cut_separates_a_cycle_needs_two"))
import net_lib as N  # noqa: E402

T0 = time.time()
OUT = {}
DEPS = {
    "proofs/SEPARATE-20261108-001A/SEPARATE-20261108-001A-P001_a_cut_separates_a_cycle_needs_two/net_lib.py":
        "e75467f9d6df5f0fe7c8311e4801fabfaa8b4a4a74b3a4e2ff26c1cab9d26351",
    "proofs/REBASE-KNOTS-20261109-001A/REBASE-KNOTS-20261109-001A-P001_no_row_after_the_first_is_open/manifest.json":
        "ea0dce653eb06438a7cdfebfc6c467e88cb4826d6005e386da7ed48f522aa464",
    "proofs/DOUBLE-BALANCE-20261109-001A/DOUBLE-BALANCE-20261109-001A-P001_doubling_every_lag_keeps_every_stage_balanced/manifest.json":
        "cc40bc02687e69af79c7c71b66feebc5df67ca24616a4ceb60aa76325860a082",
}
CENSUS = ((3, 3, 2), (3, 4, 2), (4, 4, 3))
PAST = ((5, 4, 2), (3, 4, 3))           # one size past
CAP = 20000
LAWS = list(itertools.product((0, 1), repeat=5))   # (self, a left, a right, b left, b right)


def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:400], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def tube(n, m, g):
    """square tube of n x m rings of 4g cells, contacts at positions 0 and g (to the next ring along) and 2g and 3g (from the previous)"""
    rings = [(i, r) for r in range(m) for i in range(n)]
    idx = {R: k for k, R in enumerate(rings)}
    con = []
    for r in range(m):
        for i in range(n):
            con.append((idx[(i, r)], 0, idx[((i + 1) % n, r)], 2 * g))
            con.append((idx[(i, r)], g, idx[(i, (r + 1) % m)], 3 * g))
    return [4 * g] * len(rings), con


def build(sizes, con, rule, law):
    fake = [(a, pa, b, pb, (12, 12)) for a, pa, b, pb in con]
    rings, nb, blocks = N.layout(sizes, fake)
    rows, _, _ = N.matrix(sizes, (rule,) * len(sizes), fake)
    for c, (a, pa, b, pb) in enumerate(con):
        A, B = rings[a], rings[b]
        v = 0
        for bit, cell in zip(law, (c, A[pa - 1], A[(pa + 1) % len(A)], B[pb - 1], B[(pb + 1) % len(B)])):
            if bit:
                v ^= 1 << cell
        rows[c] = v
    masks = [((1 << ln) - 1) << st for st, ln in (blocks[i] for i in range(len(sizes)))]
    return rows, nb, masks


def rank(rows):
    piv, r = {}, 0
    for v in rows:
        while v:
            h = v.bit_length() - 1
            if h in piv:
                v ^= piv[h]
            else:
                piv[h] = v
                r += 1
                break
    return r


def step(rows, s):
    out = []
    for row in rows:
        v, x = 0, row
        while x:
            low = x & -x
            v ^= s[low.bit_length() - 1]
            x ^= low
        out.append(v)
    return out


def run(rows, nb, masks, con, second, full):
    """(first lag at which some contact fails to bind one of its rings or None, order of the step or None, period found or None)"""
    if second:
        prev, s = [1 << b for b in range(nb)], [1 << (b + nb) for b in range(nb)]
        masks = [mk | (mk << nb) for mk in masks]
    else:
        prev, s = None, [1 << b for b in range(nb)]
    start = (prev, s)
    first_fail, order = None, None
    saved, power, lam = (prev, s), 1, 0
    for t in range(1, CAP + 1):
        new = step(rows, s)
        if second:
            new = [x ^ y for x, y in zip(new, prev)]
            prev = s
        s = new
        if first_fail is None:
            for c, (a, pa, b, pb) in enumerate(con):
                if not (s[c] & masks[a]) or not (s[c] & masks[b]):
                    first_fail = t
                    break
            if first_fail is not None and not full:
                return first_fail, None, None
        if (prev, s) == start:
            order = t
            if second or first_fail is not None:
                return first_fail, order, t
        if (prev, s) == saved:
            return first_fail, order, lam + 1     # cycle closed: every later state repeats one already read
        lam += 1
        if lam == power:
            saved, power, lam = (prev, s), power * 2, 0
    return first_fail, order, None


def census(tubes, second):
    rows_out = {}
    for n, m, g in tubes:
        sizes, con = tube(n, m, g)
        inv, inv_fail, inv_order, persist, undecided, deficits = 0, [], [], [], 0, []
        for rule in N.LIN:
            for law in LAWS:
                rows, nb, masks = build(sizes, con, rule, law)
                full = second or rank(rows) == nb
                ff, order, per = run(rows, nb, masks, con, second, full)
                if full:
                    inv += 1
                    inv_fail.append(ff)
                    inv_order.append(order)
                elif ff is None and per is not None:
                    persist.append("%d/%s" % (rule, "".join(map(str, law))))
                    deficits.append(nb - rank(rows))
                elif ff is None:
                    undecided += 1
        rows_out["%d x %d, g = %d" % (n, m, g)] = {
            "invertible": inv,
            "invertible that persist": sum(1 for f in inv_fail if f is None),
            "orders found": sum(1 for o in inv_order if o is not None),
            "largest order": max((o for o in inv_order if o is not None), default=None),
            "latest first failure": max((f for f in inv_fail if f is not None), default=None),
            "persistent (non-invertible)": len(persist),
            "persistent by ring rule": {str(r): sum(1 for q in persist if q.split("/")[0] == str(r)) for r in N.LIN},
            "rule 60 with law (12, 12) persists": "60/01010" in persist,
            "smallest rank deficit of a persistent one": min(deficits, default=None),
            "undecided within the cap": undecided,
        }
    return rows_out


def main():
    deps = {p: sha(p) for p in DEPS}
    check("0 dependencies bound by hash", all(DEPS[p] == deps[p] for p in DEPS), deps)
    first = census(CENSUS + PAST, False)
    ok1 = all(r["invertible that persist"] == 0 and r["orders found"] == r["invertible"] for r in first.values())
    check("1 The theorem, first order: every invertible substrate has a finite order, at which every contact is its own first-row value, "
          "and none persists (census tubes and one size past)", ok1, first)
    second = census(CENSUS + PAST, True)
    ok2 = all(r["invertible"] == 256 and r["invertible that persist"] == 0 and r["orders found"] == 256 for r in second.values())
    check("2 The theorem, second order (reversible by construction): every one of the 256 has a finite order and none persists", ok2,
          second)
    ok3 = all(r["smallest rank deficit of a persistent one"] is None or r["smallest rank deficit of a persistent one"] >= 1
              for r in first.values()) and all(r["rule 60 with law (12, 12) persists"] for r in first.values())
    check("3 Computed: the persistent first-order substrates, all forgetting (rank deficit at least 1), rule 60 with law (12, 12) "
          "among them", ok3, {k: [r["persistent (non-invertible)"], r["smallest rank deficit of a persistent one"], r["persistent by ring rule"]]
                     for k, r in first.items()})
    rec = {}
    for n, m, g in CENSUS + PAST:
        sizes, con = tube(n, m, g)
        rows, nb, masks = build(sizes, con, 60, (0, 1, 0, 1, 0))
        own = [b for b in range(len(con), nb)]
        block = [sum(((rows[b] >> j) & 1) << i for i, j in enumerate(own)) for b in own]
        rec["%d x %d, g = %d" % (n, m, g)] = {"cells": nb, "rank of the step": rank(rows), "own cells": len(own),
                                              "rank of the own-cell block": rank(block)}
    ok4 = all(r["rank of the step"] < r["cells"] and r["rank of the own-cell block"] == r["own cells"] for r in rec.values())
    check("4 Reconciliation with DOUBLE-BALANCE-20261109-001A: on rule 60 with law (12, 12) the step forgets (rank below the number of "
          "cells) while the own cells' evolution with contacts read as zero is invertible", ok4, rec)
    result = {"ticket": "INVERT-STEP-20261110-001A", "artifact_id": "INVERT-STEP-20261110-001A-P001", "checks": OUT, "status": "passed"}
    path = HERE / "result.json"
    if "--write" in sys.argv:
        path.write_text(json.dumps(result, indent=1, default=str) + "\n")
        return 0
    old = json.loads(path.read_text())
    same = json.dumps(old["checks"], sort_keys=True, default=str) == json.dumps(json.loads(json.dumps(OUT, default=str)), sort_keys=True)
    print("result.json matches" if same else "result.json differs")
    return 0 if same else 1


if __name__ == "__main__":
    sys.exit(main())
