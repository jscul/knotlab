#!/usr/bin/env python3
"""Checks for INTERMITTENT-NET-20261108-001A: when intermittent composition is a law.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
Needs numpy (the repository's .venv). 16 worker processes, a few minutes. References: PROCESS-CHAIN-20261108-001A's chain
library, and direct recomputation of the T-step maps at strobed lags."""
import hashlib
import json
import random
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "proofs/TIME-KNOTS-20261107-001A/TIME-KNOTS-20261107-001A-P001_knots_across_time_are_minimal_decisive_sets"))
import intermittent_lib as I  # noqa: E402
import time_knots_lib as K  # noqa: E402

C, S, P = I.C, I.S, I.P
T0 = time.time()
OUT = {}
SIZES = ((3, 4, 3), (4, 4, 4), (4, 6, 4), (5, 6, 5))


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:600], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def linear_job(args):
    r, size, family, law = args
    rows, T1, period = I.profile(r, *size, family, law)
    if T1 is None:
        return None
    return [int(x[0] == (x[1] and x[2])) for x in rows]


def implication_job(args):
    r, size, family, law = args
    rows, T1, period = I.profile(r, *size, family, law)
    return [int((not x[0]) or (x[1] and x[2])) for x in rows], T1 is not None


def strobe_job(args):
    r, size, family, law, seed = args
    rows, T1, period = I.profile(r, *size, family, law)
    if T1 is None:
        return None
    mA, mB, mC = size
    k = mB // 2
    a, b, c, N, blocks = C.layout(mA, mB, mC, k)
    nxt = C.chain_state_map(r, mA, mB, mC, k, family, law)
    rng = random.Random(seed)
    T = rng.randrange(T1, T1 + period)
    ok = True
    for j in (1, 2, 3):
        cur = np.arange(len(nxt), dtype=np.int64)
        for _ in range(T + j * period):
            cur = nxt[cur]
        ok &= I.verdicts_at(cur, blocks, N) == rows[T - 1]
    return ok


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"] if q.endswith(".json")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})
    reps = K.classes()
    rng = random.Random(20261108)
    laws = [("proposals", g2) for g2 in P.PARITIES] + [("self-blind", u) for u in S.NONCONSTANT_TWO]

    # 1 Theorem 1: verdicts repeat with the period of the T-step maps; a strobed chain composes at all observed lags or none
    jobs = [(r, rng.choice(SIZES), *rng.choice(laws), rng.randrange(10 ** 9)) for r in reps for _ in range(3)]
    with Pool(16) as pool:
        res = pool.map(strobe_job, jobs, chunksize=4)
    done = [x for x in res if x is not None]
    check("1 Theorem 1: on 264 random chains (every rule class three times), the verdicts at a random cycle lag T recur at T + P, "
          "T + 2P and T + 3P when the T-step maps are recomputed from scratch, so a strobed chain composes at every observed lag or "
          "at none", all(done) and len(done) > 200, {"chains": len(jobs), "decided": len(done), "agree": sum(done)})

    # 2 Theorem 2: linear and affine chains compose exactly where the far contact depends on both end rings
    lin = sorted(set(P.LINEAR) | set(P.AFFINE))
    jobs = [(r, size, fam, law) for r in lin for size in SIZES for fam, law in [("proposals", g2) for g2 in P.PARITIES]
            + [("self-blind", u) for u in S.AFFINE_TWO]]
    with Pool(16) as pool:
        res = pool.map(linear_job, jobs, chunksize=4)
    done = [x for x in res if x is not None]
    lags = sum(len(x) for x in done)
    agree = sum(sum(x) for x in done)
    check("2 Theorem 2: for the 16 linear and affine rules with affine contact laws (both families) at the four census sizes, at "
          "every lag up to the repeat, composition holds exactly when c2 depends on both end rings", agree == lags and lags > 0,
          {"chains": len(jobs), "decided": len(done), "lags": lags, "agree": agree})

    # 3 Theorem 3: in every chain, composition implies that c2 depends on both end rings
    jobs = [(r, size, fam, law) for size in SIZES[:2] for r in reps for fam, law in laws]
    with Pool(16) as pool:
        res = pool.map(implication_job, jobs, chunksize=8)
    lags = sum(len(x) for x, _ in res)
    ok = sum(sum(x) for x, _ in res)
    check("3 Theorem 3: in all 2,816 chains of 3/4/3 and 4/4/4 cells, at every lag computed, composition implies that c2 depends "
          "on both end rings", ok == lags, {"chains": len(jobs), "lags": lags, "holding": ok})

    res = {"status": "passed", "checks": OUT, "seconds": round(time.time() - T0, 1)}
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
        print("wrote result.json")
    else:
        old = json.loads((HERE / "result.json").read_text())
        same = {k: v["info"] for k, v in old["checks"].items()} == json.loads(json.dumps({k: v["info"] for k, v in OUT.items()}, default=str))
        print("result.json reproduced" if same else "result.json DIFFERS")
        sys.exit(0 if same else 1)
