#!/usr/bin/env python3
"""Checks for PROCESS-CONTACT-20261108-001A: which listening contacts bind two processes.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
Needs numpy (the repository's .venv). Single process, a few minutes. Independent references: GROWTH-LAW-20261107-001A's generic
K1-K3 enumerator (erasure as forgetting on allowed states) and knotlab check (tools/knotlab) on the space-time law's CNF."""
import hashlib
import json
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "proofs/TIME-KNOTS-20261107-001A/TIME-KNOTS-20261107-001A-P001_knots_across_time_are_minimal_decisive_sets"))
sys.path.insert(0, str(ROOT / "proofs/GROWTH-LAW-20261107-001A/GROWTH-LAW-20261107-001A-P001_a_beginning_is_a_knot"))
import process_contact_lib as P  # noqa: E402
import time_knots_lib as K  # noqa: E402
import growth_law_lib as G  # noqa: E402

T0 = time.time()
OUT = {}
SAMPLE_RULES = (0, 30, 51, 60, 90, 110, 128, 150, 184, 204)


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:600], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def erasure_loses(F, side_a, side_b, own, n):
    """generic: forgetting either ring leaves the rest free (GROWTH-LAW's Rel on the graph of F, output as bit n)"""
    R = G.Rel([f"v{j}" for j in range(n)] + ["c"], [u | (int(F[u]) << n) for u in range(1 << n)])
    out = 1 << n
    return R.is_free(side_b | own | out) and R.is_free(side_a | own | out) and F.min() != F.max()


def histories(rule, m, T):
    return {tuple(int(v) for v in row) for row in P.ring_contact_history(rule, m, T)}


def knotlab(cnf, loops, contact, witnesses):
    env = {"PYTHONPATH": str(ROOT / "tools"), "PATH": "/usr/bin:/bin"}
    res = subprocess.run([sys.executable, "-B", "-m", "knotlab", "check", "--cnf", ";".join(cnf), "--loops", *loops, "--contact",
                          contact, "--witnesses", *witnesses, "--json"], capture_output=True, text=True, env=env, cwd=ROOT,
                         check=True)
    return json.loads(res.stdout)


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"] if q.endswith(".json")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})

    # 1 Theorem 1: binding = no side decides = every minimally decisive set meets both rings = erasure of either ring frees c(T)
    tested = mism = binding = 0
    for r in SAMPLE_RULES:
        for (m, n) in ((3, 3), (3, 4)):
            N = m + n + 1
            sa, sb, own = P.listening_sides(m, n)
            for g in range(256):
                for T, F in enumerate(P.listening_maps(r, m, r, n, g, 3), start=1):
                    b1 = P.binds(F, sa, sb, own, N)
                    b2 = P.binds_by_knots(F, sa, sb, N, K.knots_across_time)
                    b3 = erasure_loses(F, sa, sb, own, N)
                    tested += 1
                    mism += not (b1 == b2 == b3)
                    binding += b1
    check("1 Theorem 1: on 10 ring rules (both rings alike), rings of 3 + 3 and 3 + 4 cells, all 256 contact laws, T = 1..3, "
          "the three readings agree: no ring's first row with c(0) decides c(T); every minimally decisive set meets both rings; "
          "forgetting either ring leaves c(T) free over the rest (generic enumerator)", mism == 0 and binding > 0,
          {"maps": tested, "mismatches": mism, "binding maps": binding})

    # 2 Theorem 2: the contact sees each ring only through its contact histories
    tested = mism = 0
    m, n = 3, 4
    sa, sb, own = P.listening_sides(m, n)
    for r in K.classes():
        HA = {T: histories(r, m, T) for T in range(1, 7)}
        HB = {T: histories(r, n, T) for T in range(1, 7)}
        for g in range(256):
            for T, F in enumerate(P.listening_maps(r, m, r, n, g, 6), start=1):
                G_T = lambda c0, h, k, g=g: P.contact_value(g, c0, h, k)
                tested += 1
                mism += P.binds(F, sa, sb, own, m + n + 1) != P.binds_by_histories(G_T, HA[T], HB[T])
    # two different rule pairs with the same history sets are bound by the same laws
    same = defaultdict(set)
    for r in K.classes():
        key = tuple(sorted(histories(r, 3, 4))), tuple(sorted(histories(r, 4, 4)))
        same[key].add(r)
    groups = [sorted(v) for v in same.values() if len(v) > 1]
    agree = True
    for grp in groups:
        verdicts = {r: tuple(P.binds(P.listening_maps(r, 3, r, 4, g, 4)[3], sa, sb, own, 8) for g in range(256)) for r in grp}
        agree &= len(set(verdicts.values())) == 1
    check("2 Theorem 2: on all 88 rule classes (both rings alike, 3 + 4 cells), all 256 laws and T = 1..6, binding read from the "
          "first rows equals binding read from the two rings' sets of contact histories; rule classes with equal history sets at "
          "T = 4 are bound by exactly the same laws", mism == 0 and agree,
          {"maps": tested, "mismatches": mism, "rule groups with equal histories at T = 4": len(groups), "groups agree": agree})

    # 3 Theorem 3: memoryless two-input contacts bind exactly when they are parities of two nonconstant contact cells
    assert all(P.canalizing_two_input(g2) for g2 in range(16) if g2 not in P.PARITIES)
    assert not any(P.canalizing_two_input(g2) for g2 in P.PARITIES)
    tested = mism = binding = 0
    for (m, n) in ((3, 4), (4, 5), (5, 5)):
        sa, sb, own = P.listening_sides(m, n)
        for r in K.classes():
            HA, HB = P.ring_contact_history(r, m, 8), P.ring_contact_history(r, n, 8)
            for g2 in range(16):
                for T, F in enumerate(P.listening_maps(r, m, r, n, P.memoryless(g2), 8), start=1):
                    nonconst = bool(HA[:, T - 1].min() != HA[:, T - 1].max() and HB[:, T - 1].min() != HB[:, T - 1].max())
                    b = P.binds(F, sa, sb, own, m + n + 1)
                    tested += 1
                    mism += b != ((g2 in P.PARITIES) and nonconst)
                    binding += b
    # mixed rule pairs, 3 + 4 cells, T = 1..6
    mixed = 0
    sa, sb, own = P.listening_sides(3, 4)
    reps = K.classes()
    for ra in reps:
        HA = P.ring_contact_history(ra, 3, 6)
        for rb in reps:
            HB = P.ring_contact_history(rb, 4, 6)
            for g2 in (0b0110, 0b1000, 0b1110, 0b1100, 0b0100):
                for T, F in enumerate(P.listening_maps(ra, 3, rb, 4, P.memoryless(g2), 6), start=1):
                    nonconst = bool(HA[:, T - 1].min() != HA[:, T - 1].max() and HB[:, T - 1].min() != HB[:, T - 1].max())
                    mixed += 1
                    mism += P.binds(F, sa, sb, own, 8) != ((g2 in P.PARITIES) and nonconst)
    # composition: under a parity contact, the minimally decisive sets of c(T) are the unions of the rings' own
    comp_tested = comp_bad = 0
    m, n = 3, 4
    for r in reps:
        HA, HB = P.ring_contact_history(r, m, 4), P.ring_contact_history(r, n, 4)
        for T, F in enumerate(P.listening_maps(r, m, r, n, P.memoryless(0b0110), 4), start=1):
            a, b = HA[:, T - 1].copy(), HB[:, T - 1].copy()
            if a.min() == a.max() or b.min() == b.max():
                continue
            kn, ties, _ = K.knots_across_time(F, m + n + 1)
            ka, ta, _ = K.knots_across_time(a, m)
            kb, tb, _ = K.knots_across_time(b, n)
            comp_tested += 1
            comp_bad += set(kn + ties) != {sA | (sB << m) for sA in ka + ta for sB in kb + tb} or bool(ties)
    check("3 Theorem 3: a memoryless two-input contact binds both rings at lag T exactly when it is XOR or XNOR and both rings' "
          "contact cells at lag T - 1 are nonconstant (all 16 laws, all 88 classes with both rings alike, 3 + 4, 4 + 5 and 5 + 5 "
          "cells, T = 1..8; all 7,744 mixed pairs of classes with 5 laws, 3 + 4 cells, T = 1..6); the 14 other laws are "
          "canalizing; under XOR the minimally decisive sets are exactly the unions of the rings' own, so no tie",
          mism == 0 and comp_bad == 0 and comp_tested > 0,
          {"maps (alike)": tested, "maps (mixed)": mixed, "mismatches": mism, "binding maps (alike)": binding,
           "composition maps": comp_tested, "composition mismatches": comp_bad})

    # 4 Theorem 4: binding at lag 1 means one of the four parity laws; later binding from restricted histories (computed)
    sa, sb, own = P.listening_sides(3, 4)
    lag1 = sorted(g for g in range(256) if P.binds(P.listening_maps(204, 3, 204, 4, g, 1)[0], sa, sb, own, 8))
    later = defaultdict(list)
    for g in range(256):
        for r in reps:
            nxt = P.listening_state_map(r, 3, r, 4, g)
            verdicts, T1, period = P.lags_exactly(nxt, 7, lambda F: P.binds(F, sa, sb, own, 8))
            if not verdicts[0] and P.at_every_lag(verdicts, T1, period, 2):
                later[g].append(r)
    with51 = sorted(g for g, rs in later.items() if 51 in rs)
    check("4 Theorem 4: the contact laws that bind both rings at lag 1 are exactly the four parities a + b, a + b + 1, "
          "a + b + c, a + b + c + 1 (laws 90, 165, 150, 105); computed, exact at every lag by iterating the 2^8-state dynamics "
          "until its maps repeat (3 + 4 cells, both rings alike): non-parity laws that bind at every lag from 2 on",
          lag1 == [90, 105, 150, 165] and all(g not in (90, 105, 150, 165) for g in later),
          {"lag-1 binding laws": lag1, "laws binding at every lag >= 2 only, for some rule": len(later),
           "rules per such law": {g: len(rs) for g, rs in sorted(later.items())},
           "laws doing so between negation rings (rule 51)": with51})

    # 5 Theorem 5: linear rings; nilpotency and persistence of the memoryless parity contact
    rows = []
    ok = True
    for r, off in sorted(P.LINEAR.items()):
        for m in range(3, 17):
            idx = P.nilpotency_index(off, m)
            pow2 = m & (m - 1) == 0
            expect = 1 if r == 0 else (m if r in (60, 102) and pow2 else (m // 2 if r == 90 and pow2 else None))
            ok &= idx == expect and (idx is not None) == P.nilpotent_by_radical(off, m)
        rows.append([r, [m for m in range(3, 17) if P.nilpotency_index(off, m)]])
    big = all(P.nilpotent_by_radical(off, m) == (r == 0 or (r in (60, 102, 90) and m & (m - 1) == 0))
              for r, off in P.LINEAR.items() for m in range(3, 129))
    # the polynomial of each linear and affine rule is its one-step action on a ring
    poly_ok = True
    for r, off in list(P.LINEAR.items()) + [(a, P.LINEAR[l]) for a, l in P.AFFINE.items()]:
        s = P.bits_of(5)
        nxt = P.ring_step(s, r)
        pr = P.ring_poly(off, 5)
        lin = np.zeros_like(s)
        for j in range(5):
            if pr >> j & 1:
                lin ^= np.roll(s, j, axis=1)
        poly_ok &= bool(((lin ^ (1 if r in P.AFFINE else 0)) == nxt).all())
    # binding of the memoryless parity contact between linear or affine rings, simulated
    sim = sim_bad = 0
    for r in list(P.LINEAR) + list(P.AFFINE):
        off = P.LINEAR[P.AFFINE.get(r, r)]
        for m in range(3, 9):
            for n in range(m, 9):
                sa, sb, own = P.listening_sides(m, n)
                for T, F in enumerate(P.listening_maps(r, m, r, n, P.memoryless(0b0110), 2 * n + 2), start=1):
                    pred = P.poly_ring_power(off, T - 1, m) != 0 and P.poly_ring_power(off, T - 1, n) != 0
                    sim += 1
                    sim_bad += P.binds(F, sa, sb, own, m + n + 1) != pred
    check("5 Theorem 5: for the 16 linear and affine rules, p is nilpotent modulo X^m - 1 exactly for rules 0 and 255 (index 1) "
          "and for 60, 102 (index m) and 90 (index m / 2), with their negations, on rings of 2^k cells (m = 3..16 exactly; the "
          "radical criterion to m = 128); the memoryless parity contact between two such rings binds at lag T exactly when "
          "neither p^(T - 1) vanishes (simulated, rings of 3 to 8 cells)",
          ok and big and poly_ok and sim_bad == 0,
          {"[rule, ring sizes 3..16 where p is nilpotent]": rows, "radical criterion to 128": big, "polynomials": poly_ok,
           "simulated maps": sim, "mismatches": sim_bad})

    # 6 knotlab check on the space-time law's CNF: a parity contact between two rule-128 rings is a knot across time
    cnf = P.cnf_listening(128, 3, 128, 3, P.memoryless(0b0110), 2)
    allv = sorted({tok.lstrip("~") for cl in cnf for tok in cl.split()})
    loops, contact = ["a0_0", "b0_1"], "c2"
    wit = [v for v in allv if v not in loops + [contact]]
    xor = knotlab(cnf, loops, contact, wit)
    cnf_and = P.cnf_listening(128, 3, 128, 3, P.memoryless(0b1000), 2)
    wit_and = [v for v in sorted({tok.lstrip("~") for cl in cnf_and for tok in cl.split()}) if v not in loops + [contact]]
    andc = knotlab(cnf_and, loops, contact, wit_and)
    # the generic enumerator agrees on the same two-time law: 9 knots {a_i, b_j, c(2)}, each excluding only (0, 0, 1)
    F = P.listening_maps(128, 3, 128, 3, P.memoryless(0b0110), 2)[1]
    R = G.Rel([f"a{j}" for j in range(3)] + [f"b{j}" for j in range(3)] + ["c0", "c"], [u | (int(F[u]) << 7) for u in range(128)])
    kn = sorted(G.knots(R))
    shapes = all(bin(S).count("1") == 3 and S >> 7 & 1 and S & 0b111 and S & 0b111000 for S in kn)
    check("6 knotlab check, rule-128 rings of 3 cells, T = 2: under the XOR contact {a_0(0), b_1(0), c(2)} is a knot (K1-K3, "
          "erasure as forgetting, every other cell a witness), and under the AND contact it is not; the generic enumerator finds "
          "exactly 9 knots, each one cell of each ring with c(2)",
          xor["is_knot"] and not andc["is_knot"] and len(kn) == 9 and shapes,
          {"xor": {k: xor[k] for k in ("allowed", "is_knot", "binding", "loss_on_erasure", "pairwise_definable")},
           "and": {k: andc[k] for k in ("allowed", "is_knot", "binding", "loss_on_erasure")}, "generic knots": len(kn)})

    res = {"status": "passed", "checks": OUT, "seconds": round(time.time() - T0, 1)}
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
        print("wrote result.json")
    else:
        old = json.loads((HERE / "result.json").read_text())
        same = {k: v["info"] for k, v in old["checks"].items()} == json.loads(json.dumps({k: v["info"] for k, v in OUT.items()}, default=str))
        print("result.json reproduced" if same else "result.json DIFFERS")
        sys.exit(0 if same else 1)
