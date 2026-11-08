#!/usr/bin/env python3
"""Checks for TIME-KNOTS-20261107-001A: knots across time are minimal decisive sets.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
Needs numpy (the repository's .venv). Single process, about a minute. The generic K1-K3 enumerator of GROWTH-LAW-20261107-001A
(minimal constrained sets on allowed states) is the independent reference."""
import collections
import hashlib
import itertools
import json
import random
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "proofs/GROWTH-LAW-20261107-001A/GROWTH-LAW-20261107-001A-P001_a_beginning_is_a_knot"))
import time_knots_lib as K  # noqa: E402
import growth_law_lib as G  # noqa: E402

T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:500], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def generic_knots(F, n):
    R = G.Rel([f"x{j}" for j in range(n)] + ["y"], K.relation_of_map(F, n))
    return set(G.knots(R))


def is_term_or_clause(F, n):
    dep = K.depends(F, n)
    vs = [j for j in range(n) if dep >> j & 1]
    u = np.arange(1 << n)
    for signs in itertools.product((0, 1), repeat=len(vs)):
        lits = [((u >> j) & 1) == s for j, s in zip(vs, signs)]
        a = np.logical_and.reduce(lits).astype(np.uint8)
        o = np.logical_or.reduce(lits).astype(np.uint8)
        if (a == F).all() or (o == F).all():
            return True
    return False


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"] if q.endswith(".json")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})

    # 1 Theorem 1: the knots of the graph of F_T are the minimally decisive sets of size >= 2, plus the output
    reps = K.classes()
    mism = 0
    tested = 0
    for r in reps:
        for T in (1, 2):
            n = 2 * T + 1
            F = K.t_step_map(r, T)
            kn, _, _ = K.knots_across_time(F, n)
            tested += 1
            mism += generic_knots(F, n) != {S | (1 << n) for S in kn}
    rng = np.random.default_rng(20261108)
    rand = 0
    for n in (5, 6):
        for _ in range(150):
            F = rng.integers(0, 2, size=1 << n).astype(np.uint8)
            kn, _, _ = K.knots_across_time(F, n)
            rand += 1
            mism += generic_knots(F, n) != {S | (1 << n) for S in kn}
    # control: every prime-implicant support (not only the minimal ones) as knots, which overcounts
    F = K.t_step_map(30, 2)
    dec = K.decisive_table(F, 5)
    allsupp = {S for S in range(32) if dec[S] and bin(S).count("1") >= 2}
    control = generic_knots(F, 5) != {S | (1 << 5) for S in allsupp}
    check("1 Theorem 1: on all 88 elementary rules at T = 1, 2 and on 300 random functions of 5 and 6 inputs, the knots of the graph "
          "of the map are exactly the minimally decisive sets with two or more cells, plus the output; control: all decisive sets "
          "overcount", mism == 0 and control, {"maps tested": tested + rand, "mismatches": mism, "control differs": control})

    # 2 Theorem 2: a nonconstant function has no knot exactly when it is a single AND or OR of literals
    rows = []
    ok = True
    for n in (2, 3, 4):
        agree = noknot = 0
        for code in range(1, (1 << (1 << n)) - 1):
            F = np.array([(code >> u) & 1 for u in range(1 << n)], dtype=np.uint8)
            a = not K.knots_across_time(F, n)[0]
            agree += a == is_term_or_clause(F, n)
            noknot += a
        rows.append([n, (1 << (1 << n)) - 2, noknot, agree])
        ok &= agree == (1 << (1 << n)) - 2
    n = 5
    u = np.arange(1 << n)
    terms = 0
    for k in range(1, 6):
        for vs in itertools.combinations(range(n), k):
            for signs in itertools.product((0, 1), repeat=k):
                lits = [((u >> j) & 1) == s for j, s in zip(vs, signs)]
                for F in (np.logical_and.reduce(lits).astype(np.uint8), np.logical_or.reduce(lits).astype(np.uint8)):
                    terms += 1
                    ok &= not K.knots_across_time(F, n)[0]
    rnd = 0
    for _ in range(300):
        F = rng.integers(0, 2, size=1 << n).astype(np.uint8)
        if F.min() == F.max():
            continue
        rnd += 1
        ok &= (not K.knots_across_time(F, n)[0]) == is_term_or_clause(F, n)
    check("2 Theorem 2: every nonconstant Boolean function of 2, 3 and 4 inputs has no knot exactly when it is a single AND or OR "
          "of literals; every term and clause of 5 inputs is knot-free; 300 random 5-input functions agree", ok,
          {"[n, nonconstant functions, knot-free, agreeing]": rows, "5-input terms and clauses": terms, "random 5-input": rnd})

    # 3 linear rules: one two-time knot per lag, the support of p^T plus the cell
    linear = {60: {-1, 0}, 102: {0, 1}, 90: {-1, 1}, 150: {-1, 0, 1}, 105: {-1, 0, 1}, 195: {-1, 0}}
    rows = []
    ok = True
    for r, p in linear.items():
        for T in range(1, 7):
            n = 2 * T + 1
            F = K.t_step_map(r, T)
            kn, ties, _ = K.knots_across_time(F, n)
            supp = K.poly_power_support(p, T)
            expect = sum(1 << (e + T) for e in supp)
            good = kn == [expect] and not ties
            if T in (1, 2, 4):
                good &= len(supp) == len(p)
            ok &= good
            rows.append([r, T, [bin(S).count("1") + 1 for S in kn], good])
    lucas = all(len(K.poly_power_support({-1, 0}, T)) == 2 ** bin(T).count("1") for T in range(1, 33))
    ok &= lucas
    check("3 Theorem 3: linear and affine rules (60, 102, 90, 150 and the complements 105, 195), T = 1..6: exactly one two-time knot "
          "per lag, the support of p^T plus the cell, with |supp p| + 1 places at T = 1, 2, 4; Lucas: rule 60's support at lag T has "
          "2^popcount(T) cells (T <= 32)", ok, {"[rule, T, knot sizes, ok]": rows, "lucas": lucas})

    # 4 intermediate rows: rule 102 (Ledrappier's orientation), the least knot through (0, 0) and (T, 0) in the light cone
    rows = []
    ok = True
    for T in range(1, 7):
        cone = [(t, i) for t in range(T + 1) for i in range(T - t + 1)]
        idx = {c: k for k, c in enumerate(cone)}
        rows_ = []
        for u in range(1 << (T + 1)):
            vals = {(0, i): (u >> i) & 1 for i in range(T + 1)}
            for t in range(1, T + 1):
                for i in range(T - t + 1):
                    vals[(t, i)] = vals[(t - 1, i)] ^ vals[(t - 1, i + 1)]
            rows_.append(sum(vals[c] << idx[c] for c in cone))
        R = G.Rel([f"c{t}_{i}" for (t, i) in cone], rows_)
        a, b = f"c0_0", f"c{T}_0"
        others = [v for v in R.names if v not in (a, b)]
        least = None
        for k in range(1, 6):
            for S in itertools.combinations(others, k):
                if G.is_knot_set(R, [a, b] + list(S)):
                    least = k + 2
                    break
            if least:
                break
        naf = 0
        m = T
        while m:
            if m & 1:
                naf += 1
                m -= 2 - (m & 3) if (m & 3) == 3 else 1
            m >>= 1
        two_time = 2 ** bin(T).count("1") + 1
        rows.append([T, least, 2 + naf, two_time])
        ok &= least == 2 + naf
    check("4 intermediate rows (rule 102, Ledrappier's law): within the past light cone, the least knot through a cell and its "
          "value T steps on has 2 + w(T) places for T = 1..6, w the non-adjacent-form weight; the two-time knot alone has "
          "2^popcount(T) + 1", ok, {"[T, least knot in the light cone, 2 + w(T), two-time knot]": rows})

    # 5 Life at T = 1
    F = K.life_map()
    kn, ties, _ = K.knots_across_time(F, 9)
    sizes = collections.Counter(bin(S).count("1") + 1 for S in kn)
    centre = any(S >> 4 & 1 for S in kn)
    four = all(bin(S).count("1") == 4 and not S >> 4 & 1 for S in kn)
    check("5 Conway's Life, one step: the knots across time are the 70 sets of four neighbours with the cell's next value (four live "
          "neighbours decide by overcrowding); no ties; the cell's own present value lies in no knot",
          len(kn) == 70 and four and not ties and not centre, {"knots": len(kn), "sizes": dict(sizes), "ties": len(ties),
                                                           "centre in a knot": centre})

    res = {"status": "passed", "checks": OUT, "seconds": round(time.time() - T0, 1)}
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
        print("wrote result.json")
    else:
        old = json.loads((HERE / "result.json").read_text())
        same = {k: v["info"] for k, v in old["checks"].items()} == json.loads(json.dumps({k: v["info"] for k, v in OUT.items()}, default=str))
        print("result.json reproduced" if same else "result.json DIFFERS")
        sys.exit(0 if same else 1)
