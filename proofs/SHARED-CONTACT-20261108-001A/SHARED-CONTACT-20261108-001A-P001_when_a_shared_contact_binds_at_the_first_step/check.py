#!/usr/bin/env python3
"""Checks for SHARED-CONTACT-20261108-001A: when a shared contact binds at the first step.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
Needs numpy (the repository's .venv). Single process, about a minute. References: PROCESS-CONTACT-20261108-001A's binds and its
minimally decisive sets (TIME-KNOTS-20261107-001A's machinery), and two implementations of the shared dynamics."""
import hashlib
import json
import random
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "proofs/TIME-KNOTS-20261107-001A/TIME-KNOTS-20261107-001A-P001_knots_across_time_are_minimal_decisive_sets"))
import shared_contact_lib as S  # noqa: E402
import time_knots_lib as K  # noqa: E402

P = S.P
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:600], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"] if q.endswith(".json")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})

    reps = K.classes()
    # 1 Theorem 1: proposals bind at lag 1 exactly for a parity combiner with neither rule canalizing at its centre
    tested = mism = 0
    for (m, n) in ((3, 3), (3, 4), (4, 5)):
        sa, sb, own = P.shared_sides(m, n)
        for ra in reps:
            for rb in reps:
                for g2 in range(16):
                    F = P.shared_maps(ra, m, rb, n, g2, 1)[0]
                    b = P.binds(F, sa, sb, own, m + n - 1)
                    tested += 1
                    mism += b != S.proposals_bind_at_lag1(ra, rb, g2) or b != S.fast_binds(F, m, n)
    nc = sum(not S.centre_canalizing(r) for r in reps)
    check("1 Theorem 1: a contact combining the rings' proposals binds at lag 1 exactly when its combiner is XOR or XNOR and "
          "neither rule is canalizing at its centre (all 7,744 ordered pairs of rule classes, all 16 combiners, rings of 3 + 3, "
          "3 + 4 and 4 + 5 cells); the reshaping test agrees with process_contact_lib.binds", mism == 0,
          {"maps": tested, "mismatches": mism, "rule classes not canalizing at their centre": nc})

    # 2 Theorem 2: a self-blind contact binds at lag 1 exactly when h has no constant row or column; parities u + v exactly when
    # u and v are nonconstant
    tested = mism = 0
    count = 0
    m, n = 3, 4
    sa, sb, own = P.shared_sides(m, n)
    for h in range(1 << 16):
        F = S.selfblind_maps(204, m, 204, n, h, 1)[0]
        b = S.fast_binds(F, m, n)
        tested += 1
        mism += b != S.selfblind_binds_at_lag1(h)
        count += b
    par = sum(S.selfblind_binds_at_lag1(S.parity_table(u, v)) for u in range(16) for v in range(16))
    par_ok = all(S.selfblind_binds_at_lag1(S.parity_table(u, v)) == (u not in (0, 15) and v not in (0, 15))
                 for u in range(16) for v in range(16))
    # the lag-1 verdict does not depend on the ring rules: a sample of rules and the slow test
    rng = random.Random(20261108)
    sample_ok = True
    for _ in range(300):
        h, ra, rb = rng.randrange(1 << 16), rng.choice(reps), rng.choice(reps)
        F = S.selfblind_maps(ra, m, rb, n, h, 1)[0]
        sample_ok &= P.binds(F, sa, sb, own, m + n - 1) == S.selfblind_binds_at_lag1(h)
    check("2 Theorem 2: of all 65,536 self-blind contact laws (rings of 3 + 4 cells), exactly those with no constant row and no "
          "constant column bind at lag 1; the parities u + v bind exactly when u and v are nonconstant (196 of 256); the verdict "
          "is the same under 300 random ring-rule pairs", mism == 0 and par_ok and par == 196 and sample_ok,
          {"laws": tested, "mismatches": mism, "binding at lag 1": count, "parities binding": par, "random rules agree": sample_ok})

    # 3 Theorem 3: linear and affine rings with an affine contact: binding at lag T = the contact's row of M^T meets both rings
    lin_rules = sorted(set(P.LINEAR) | set(P.AFFINE))
    tested = mism = affine_fail = 0
    for (m, n) in ((3, 4), (4, 5)):
        N = m + n - 1
        sa, sb, own = P.shared_sides(m, n)
        for r in lin_rules:
            for rb in (r, 150, 90):
                for kind, law in [("proposals", g2) for g2 in P.PARITIES] + [("self-blind", S.parity_table(u, v))
                                                                                 for u in S.AFFINE_TWO for v in S.AFFINE_TWO]:
                    if kind == "proposals":
                        nxt = P.shared_state_maps(r, m, rb, n, law)
                        maps = P.shared_maps(r, m, rb, n, law, 12)
                    else:
                        nxt = S.selfblind_state_map(r, m, rb, n, law)
                        maps = S.selfblind_maps(r, m, rb, n, law, 12)
                    rows = S.affine_contact_row(nxt, N, 12)
                    if rows is None:
                        affine_fail += 1
                        continue
                    for F, row in zip(maps, rows):
                        tested += 1
                        mism += S.fast_binds(F, m, n) != (bool(row & sa) and bool(row & sb))
    check("3 Theorem 3: for the 16 linear and affine rules (with partners 150 and 90), both contact families with affine laws, "
          "rings of 3 + 4 and 4 + 5 cells and T = 1..12, the shared system is affine and the contact binds at lag T exactly when "
          "its row of M^T meets both rings", mism == 0 and affine_fail == 0 and tested > 0,
          {"maps": tested, "mismatches": mism, "systems not affine": affine_fail})

    # 4 the two implementations of the self-blind dynamics agree, and the reshaping test agrees with the minimally decisive sets
    agree = knots_agree = 0
    trials = 400
    for _ in range(trials):
        m, n = rng.choice(((3, 3), (3, 4), (4, 4)))
        ra, rb = rng.choice(reps), rng.choice(reps)
        u, v = rng.choice(S.NONCONSTANT_TWO), rng.choice(S.NONCONSTANT_TWO)
        h = S.parity_table(u, v)
        nxt = S.selfblind_state_map(ra, m, rb, n, h)
        maps = S.selfblind_maps(ra, m, rb, n, h, 6)
        cur = np.arange(len(nxt), dtype=np.int64)
        same = True
        for F in maps:
            cur = nxt[cur]
            same &= bool(((cur & 1).astype(np.uint8) == F).all())
        agree += same
        sa, sb, own = P.shared_sides(m, n)
        F = maps[rng.randrange(6)]
        knots_agree += S.fast_binds(F, m, n) == P.binds_by_knots(F, sa, sb, m + n - 1, K.knots_across_time)
    check("4 the state map and the direct simulation of the self-blind contact agree for 6 lags, and the reshaping test agrees "
          "with the minimally decisive sets, on 400 random configurations", agree == trials and knots_agree == trials,
          {"trials": trials, "dynamics agree": agree, "binding agrees with the decisive sets": knots_agree})

    res = {"status": "passed", "checks": OUT, "seconds": round(time.time() - T0, 1)}
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
        print("wrote result.json")
    else:
        old = json.loads((HERE / "result.json").read_text())
        same = {k: v["info"] for k, v in old["checks"].items()} == json.loads(json.dumps({k: v["info"] for k, v in OUT.items()}, default=str))
        print("result.json reproduced" if same else "result.json DIFFERS")
        sys.exit(0 if same else 1)
