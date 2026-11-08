#!/usr/bin/env python3
"""Checks for PROCESS-CHAIN-20261108-001A: what a chain of contacts can carry.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
Needs numpy (the repository's .venv). Single process, a few minutes. References: two implementations of the chain dynamics, the
blockwise decisiveness test against process_contact_lib's grouping test, and the linear algebra of affine chains."""
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
import chain_lib as C  # noqa: E402
import time_knots_lib as K  # noqa: E402

S, P = C.S, C.P
T0 = time.time()
OUT = {}
SIZES = ((3, 4, 3), (4, 6, 4), (5, 6, 5))


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:600], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def affine_rows(nxt, N, bitpos, lags):
    """the support of row `bitpos` of M^T for T = 1..lags, for an affine state map (None if not affine)"""
    base = int(nxt[0])
    cols = [int(nxt[1 << j]) ^ base for j in range(N)]
    u = np.arange(1 << N, dtype=np.int64)
    lin = np.zeros(1 << N, dtype=np.int64)
    for j in range(N):
        lin ^= np.where((u >> j) & 1, cols[j], 0)
    if not ((lin ^ base) == nxt).all():
        return None
    def apply(c):
        v, j = 0, 0
        while c:
            if c & 1:
                v ^= cols[j]
            c >>= 1
            j += 1
        return v
    Mt, rows = [1 << j for j in range(N)], []
    for _ in range(lags):
        Mt = [apply(c) for c in Mt]
        rows.append(sum(((Mt[j] >> bitpos) & 1) << j for j in range(N)))
    return rows


def block_mask(blocks, name):
    s, n = blocks[name]
    return ((1 << n) - 1) << s


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"] if q.endswith(".json")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})
    reps = K.classes()
    rng = random.Random(20261108)

    # 1 Theorem 1: listening contacts never carry one ring's past to another contact
    tested = leak = 0
    for r in reps:
        for g in rng.sample(range(256), 12) + [150, 90]:
            maps, N = C.listening_chain_maps(r, 3, 4, 3, 2, g, 6)
            for c1, c2 in maps:
                tested += 1
                leak += C.depends_on_block(c2, 2, 3, N) or C.depends_on_block(c1, 2 + 3 + 4, 3, N)
    check("1 Theorem 1: in chains of listening contacts (rings of 3, 4 and 3 cells, all 88 rule classes, 14 contact laws each, "
          "T = 1..6) the far contact never depends on the far ring, so the chain never binds its ends", leak == 0,
          {"maps": tested, "far-ring dependences": leak})

    # 2 Theorem 2: in a shared chain the far ring reaches the far contact only from lag d + 1
    tested = early = tight = 0
    for (mA, mB, mC) in SIZES:
        k = mB // 2
        d = C.ring_distance(k, mB)
        a, b, c, N, blocks = C.layout(mA, mB, mC, k)
        for r in reps:
            for family, law in (("proposals", 0b0110), ("self-blind", 0b0110), ("self-blind", 0b1000)):
                maps = C.chain_maps(r, mA, mB, mC, k, family, law, d + 1)
                for T, (c1, c2) in enumerate(maps, start=1):
                    dep = C.depends_on_block(c2, *blocks["A"], N) or C.depends_on_block(c1, *blocks["C"], N)
                    if T <= d:
                        tested += 1
                        early += dep
                    else:
                        tight += C.depends_on_block(c2, *blocks["A"], N)
    check("2 Theorem 2: in shared chains (rings of 3/4/3, 4/6/4 and 5/6/5 cells, contacts opposite on ring B, all 88 classes, "
          "three laws), c2 never depends on ring A, nor c1 on ring C, at lags T <= d, d the distance between the contacts on ring B; "
          "how often c2 depends on ring A already at lag d + 1 is reported", early == 0 and tested > 0,
          {"maps at T <= d": tested, "dependences before the light cone": early,
           "configurations whose c2 depends on ring A at lag d + 1": tight, "of": len(SIZES) * len(reps) * 3})

    # 3 Theorem 3: affine chains bind two rings at lag T exactly when the contact's row of M^T meets both
    lin = sorted(set(P.LINEAR) | set(P.AFFINE))
    tested = mism = nonaffine = 0
    for (mA, mB, mC) in SIZES[:2]:
        k = mB // 2
        a, b, c, N, blocks = C.layout(mA, mB, mC, k)
        masks = {x: block_mask(blocks, x) for x in "ABC"}
        for r in lin:
            for family, law in [("proposals", g2) for g2 in P.PARITIES] + [("self-blind", u) for u in S.AFFINE_TWO]:
                nxt = C.chain_state_map(r, mA, mB, mC, k, family, law)
                maps = C.chain_maps(r, mA, mB, mC, k, family, law, 10)
                for bitpos, idx in ((0, 0), (1, 1)):
                    rows = affine_rows(nxt, N, bitpos, 10)
                    if rows is None:
                        nonaffine += 1
                        continue
                    for T, row in enumerate(rows):
                        F = maps[T][idx]
                        for pair in (("A", "B"), ("B", "C"), ("A", "C")):
                            tested += 1
                            pred = all(row & masks[x] for x in pair)
                            mism += C.binds(F, blocks, pair, N) != pred
    check("3 Theorem 3: for the 16 linear and affine rules with affine contact laws (both families), chains of 3/4/3 and 4/6/4 "
          "cells and T = 1..10, each contact binds each pair of rings exactly when the support of its row of M^T meets both",
          mism == 0 and nonaffine == 0 and tested > 0, {"verdicts": tested, "mismatches": mism, "systems not affine": nonaffine})

    # 4 the two implementations agree, and the blockwise test agrees with process_contact_lib's grouping test
    trials, agree, tests_agree = 300, 0, 0
    for _ in range(trials):
        (mA, mB, mC) = rng.choice(SIZES)
        k = mB // 2
        a, b, c, N, blocks = C.layout(mA, mB, mC, k)
        r = rng.choice(reps)
        family = rng.choice(("proposals", "self-blind"))
        law = rng.choice(P.PARITIES) if family == "proposals" else rng.choice(S.NONCONSTANT_TWO)
        nxt = C.chain_state_map(r, mA, mB, mC, k, family, law)
        maps = C.chain_maps(r, mA, mB, mC, k, family, law, 6)
        cur = np.arange(len(nxt), dtype=np.int64)
        same = True
        for c1, c2 in maps:
            cur = nxt[cur]
            same &= bool((((cur >> 0) & 1).astype(np.uint8) == c1).all() and (((cur >> 1) & 1).astype(np.uint8) == c2).all())
        agree += same
        F = maps[rng.randrange(6)][1]
        x = rng.choice("ABC")
        s0, n0 = blocks[x]
        outside = ((1 << N) - 1) & ~(((1 << n0) - 1) << s0)
        tests_agree += C.decides_outside(F, s0, n0, N) == P.side_decides(F, outside, N)
    check("4 the state map and the direct simulation agree for 6 lags, and the blockwise decisiveness test agrees with "
          "process_contact_lib's grouping test, on 300 random chains", agree == trials and tests_agree == trials,
          {"trials": trials, "dynamics agree": agree, "tests agree": tests_agree})

    res = {"status": "passed", "checks": OUT, "seconds": round(time.time() - T0, 1)}
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
        print("wrote result.json")
    else:
        old = json.loads((HERE / "result.json").read_text())
        same = {k: v["info"] for k, v in old["checks"].items()} == json.loads(json.dumps({k: v["info"] for k, v in OUT.items()}, default=str))
        print("result.json reproduced" if same else "result.json DIFFERS")
        sys.exit(0 if same else 1)
