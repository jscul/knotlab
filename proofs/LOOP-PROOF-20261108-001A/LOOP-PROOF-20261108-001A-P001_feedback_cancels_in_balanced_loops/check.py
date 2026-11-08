#!/usr/bin/env python3
"""Checks for LOOP-PROOF-20261108-001A: feedback cancels in balanced loops.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
Needs numpy (the repository's .venv). 16 worker processes, a few minutes."""
import hashlib
import itertools
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "experiments/LOOP-RINGS-20261108-001A/LOOP-RINGS-20261108-001A-E001_closed_loops"))
sys.path.insert(0, str(ROOT / "proofs/SEPARATE-20261108-001A/SEPARATE-20261108-001A-P001_a_cut_separates_a_cycle_needs_two"))
sys.path.insert(0, str(ROOT / "research/LOOP-RINGS-20261108-001"))
import run as LR  # noqa: E402
import net_lib as N  # noqa: E402

T0 = time.time()
OUT = {}
H = 300
LAWS = ((12, 12), (6, 6))


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:400], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def odd(n, k):
    return n >= 0 and (n & k) == k


def step(rows, r):
    v = 0
    while r:
        low = r & -r
        v ^= rows[low.bit_length() - 1]
        r ^= low
    return v


def W(ks, laws, s):
    return all(not (laws[j] == (6, 6) and (ks[j] == s - 2 or ks[(j + 1) % 4] == 2)) for j in range(4))


def witness_job(s):
    bad = lags = 0
    for v in itertools.product((0, 1), repeat=4):
        ks = tuple(2 if x == 0 else s - 2 for x in v)
        if sum(ks) != 2 * s:
            continue
        for laws in itertools.product(LAWS, repeat=4):
            if not W(ks, laws, s) and not (s == 4 and laws == ((12, 12),) * 4):
                continue
            if s == 4 and laws != ((12, 12),) * 4:
                continue
            net = LR.loop_net(s, ks, list(laws))
            rings, Nn, blocks = N.layout(net[0], net[2])
            rows, _, _ = N.matrix(*net)
            for i in range(4):
                wA, wB = rings[i][ks[i] - 1], rings[(i + 1) % 4][s - 1]
                r = 1 << i
                for T in range(1, H):
                    r = step(rows, r)
                    lags += 1
                    bad += not (r >> wA & 1 and r >> wB & 1)
    return bad, lags


def far_job(s):
    bad = lags = 0
    for v in itertools.product((0, 1), repeat=4):
        ks = tuple(2 if x == 0 else s - 2 for x in v)
        if sum(ks) != 2 * s:
            continue
        net = LR.loop_net(s, ks, [(12, 12)] * 4)
        rows, Nn, blocks = N.matrix(*net)
        f, b = [k - 1 for k in ks], [s - k - 1 for k in ks]
        for i in range(4):
            mA, mB = N.mask(blocks, (i - 1) % 4), N.mask(blocks, (i + 2) % 4)
            r = 1 << i
            for T in range(1, H):
                r = step(rows, r)
                lags += 1
                pA = any(odd(T - 2, m) for m in range(f[i], f[i] + f[(i - 1) % 4]))
                pB = any(odd(T - 2, m) for m in range(b[(i + 1) % 4], b[(i + 1) % 4] + b[(i + 2) % 4]))
                bad += (bool(r & mA) != pA) or (bool(r & mB) != pB)
    return bad, lags


def unbalanced_job(s):
    verdicts = []
    for v in itertools.product((0, 1), repeat=4):
        ks = tuple(2 if x == 0 else s - 2 for x in v)
        if sum(ks) == 2 * s:
            continue
        verdicts.append(LR.verdict(s, ks, [(12, 12)] * 4)[0])
    return verdicts


def full_job(args):
    s, ks = args
    net = LR.loop_net(s, ks, [(12, 12)] * 4)
    nxt, Nn, blocks = N.state_map(*net)
    cur = np.arange(len(nxt), dtype=np.int64)
    seen = set()
    for T in range(1, 4097):
        cur = nxt[cur]
        key = cur.tobytes()
        if key in seen:
            return True
        seen.add(key)
        for c, (ra, pa, rb, pb, law) in enumerate(net[2]):
            F = ((cur >> c) & 1).astype(np.uint8)
            if F.min() == F.max() or any(N.PL.C.decides_outside(F, *blocks[x], Nn) for x in (ra, rb)):
                return False
    return None


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"] if q.endswith(("manifest.json", "contract.json"))}
    check("0 dependency artifacts bound by hash; upstream statuses", not bad and all(s_ in ("Proved", "Frozen") for s_ in status.values()),
          {"mismatched": bad, "statuses": status})
    with Pool(16) as pool:
        w = pool.map(witness_job, range(4, 31))
        fa = pool.map(far_job, range(5, 31))
        ub = pool.map(unbalanced_job, range(5, 31))
        fs = pool.map(full_job, [(4, (2, 2, 2, 2))] + [(5, tuple(2 if x == 0 else 3 for x in v)) for v in itertools.product((0, 1), repeat=4) if sum(v) == 2])
    check("1 Theorem 2's witnesses at every lag to 300 (balanced loops, laws (12,12) or (6,6) under condition W, sizes 5 to 30; laws (12,12) from 4)",
          sum(b for b, l in w) == 0, {"lags": sum(l for b, l in w), "failures": sum(b for b, l in w)})
    check("2 Theorem 3's lags for every contact and far ring, laws (12,12), balanced loops, sizes 5 to 30",
          sum(b for b, l in fa) == 0, {"lags": sum(l for b, l in fa), "mismatches": sum(b for b, l in fa)})
    flat = [x for vs in ub for x in vs]
    check("3 no unbalanced loop with law (12,12) is persistent, sizes 5 to 30 (each loses persistence or stays undecided within 10^6 lags)",
          "persistent" not in flat, {"loops": len(flat), "losing persistence": flat.count("not persistent"), "undecided": flat.count("undecided"),
                                     "persistent": flat.count("persistent")})
    check("4 full state spaces: balanced loops with law (12,12) at sizes 4 and 5 keep every contact persistent", all(x is True for x in fs),
          {"loops": len(fs), "persistent": sum(1 for x in fs if x is True)})
    import characterise as CH
    rows_ = json.loads((ROOT / "artifacts/LOOP-RINGS-20261108-001A/LOOP-RINGS-20261108-001A-E001_closed_loops/run/loops.json").read_text())["rows"]
    pers = [r for r in rows_ if r[3] == "persistent"]
    fams = sorted({CH.family_key(r[0], r[1], r[2]) for r in pers if all(k in (2, r[0] - 2) for k in r[1])})
    every = [f for f in fams if all(CH.family_sizes(f)[s] == "persistent" for s in range(4, 17))]
    covered = [f for f in every if all(tuple(l) in LAWS for l in f[1]) and W(tuple(2 if x == 0 else 7 for x in f[0]), tuple(tuple(l) for l in f[1]), 9)]
    check("5 of LOOP-RINGS-20261108-001's 54 families persisting at sizes 4 to 16, 16 satisfy Theorem 2's hypotheses at size 9",
          len(every) == 54 and len(covered) == 16, {"families": len(every), "covered": len(covered)})
    out = {"status": "passed", "checks": OUT, "seconds": round(time.time() - T0, 1)}
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
        print("wrote result.json")
    else:
        old = json.loads((HERE / "result.json").read_text())
        same = {k: v["info"] for k, v in old["checks"].items()} == json.loads(json.dumps({k: v["info"] for k, v in OUT.items()}, default=str))
        print("result.json reproduced" if same else "result.json DIFFERS")
        sys.exit(0 if same else 1)
