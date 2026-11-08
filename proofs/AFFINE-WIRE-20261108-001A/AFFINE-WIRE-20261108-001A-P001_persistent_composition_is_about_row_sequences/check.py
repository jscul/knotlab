#!/usr/bin/env python3
"""Checks for AFFINE-WIRE-20261108-001A: persistent composition in affine chains is a question about row sequences.

    .venv/bin/python3 -B check.py          verify result.json against a fresh run
    .venv/bin/python3 -B check.py --write  write result.json from a fresh run
Needs numpy (the repository's .venv). 16 worker processes, a few minutes. References: the full state space of each chain, iterated
until its T-step map repeats, with PROCESS-CHAIN-20261108-001A's blockwise decisiveness test."""
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
import wire_lib as W  # noqa: E402

C, P = W.C, W.P
T0 = time.time()
OUT = {}
LAWS = [("proposals",)] + [("self-blind", x, y) for x in W.ULIN for y in W.ULIN]


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:600], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def brute(rules, sizes, k, law1, law2, cap=4096):
    """the verdicts from the full state space: (c1 persists, c2 persists, c2 composes from d + 1), or None if no repeat"""
    nxt, N, blocks = W.mixed_state_map(rules, sizes, k, law1, law2)
    d = C.ring_distance(k, sizes[1])
    cur = np.arange(len(nxt), dtype=np.int64)
    seen, v1, v2, e2 = {}, [], [], []
    for T in range(1, cap + 1):
        cur = nxt[cur]
        key = hashlib.blake2b(cur.tobytes(), digest_size=16).digest()
        if key in seen:
            T1, period = seen[key], T - seen[key]
            hold = lambda seq, start: all(seq[min(start, T1) - 1:T1 + period - 1]) and all(seq[start - 1:])
            return hold(v1, 1), hold(v2, 1), hold(e2, d + 1)
        seen[key] = T
        F1, F2 = (cur & 1).astype(np.uint8), ((cur >> 1) & 1).astype(np.uint8)
        v1.append(C.binds(F1, blocks, ("A", "B"), N))
        v2.append(C.binds(F2, blocks, ("B", "C"), N))
        e2.append(C.binds(F2, blocks, ("A", "C"), N))
    return None


def job(args):
    rules, sizes, k, law1, law2 = args
    a = W.analyze(rules, sizes, k, law1, law2)
    b = brute(rules, sizes, k, law1, law2)
    if b is None:
        return None
    return (a["c1 persists"], a["c2 persists"], a["c2 composes"]) == b, b


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"] if q.endswith(".json")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})
    rng = random.Random(20261108)
    lin = sorted(W.LIN)

    # 1 the linear matrix is the chain's own linear map
    tested = mism = 0
    for _ in range(400):
        sizes = (rng.randint(3, 5), rng.randint(3, 6), rng.randint(3, 5))
        k = rng.randint(1, sizes[1] - 1)
        rules = tuple(rng.choice(lin) for _ in range(3))
        law1, law2 = rng.choice(LAWS), rng.choice(LAWS)
        rows, N, blocks = W.linear_matrix(rules, sizes, k, law1, law2)
        nxt, N2, _ = W.mixed_state_map(rules, sizes, k, law1, law2)
        base = int(nxt[0])
        cols = [int(nxt[1 << j]) ^ base for j in range(N)]
        mrows = [sum(((cols[j] >> i) & 1) << j for j in range(N)) for i in range(N)]
        tested += 1
        mism += mrows != rows or base != 0 or N != N2
    check("1 for 400 random chains with linear rules on the three rings and linear laws (both families, chosen independently at each "
          "contact), sizes 3-5/3-6/3-5 and every contact position, the matrix rows equal the chain's own linear map read off its full "
          "state space", mism == 0, {"chains": tested, "mismatches": mism})

    # 2 the row-sequence verdicts equal the full-state-space verdicts
    jobs = []
    for _ in range(1200):
        sizes = (rng.randint(3, 4), rng.randint(3, 5), rng.randint(3, 4))
        k = rng.randint(1, sizes[1] - 1)
        rules = tuple(rng.choice(lin) for _ in range(3))
        jobs.append((rules, sizes, k, rng.choice(LAWS), rng.choice(LAWS)))
    with Pool(16) as pool:
        res = pool.map(job, jobs, chunksize=8)
    done = [x for x in res if x is not None]
    agree = sum(x[0] for x in done)
    positives = {"c1 persists": sum(x[1][0] for x in done), "c2 persists": sum(x[1][1] for x in done),
                 "c2 composes": sum(x[1][2] for x in done)}
    check("2 on 1,200 random affine chains (sizes 3-4/3-5/3-4), the verdicts read from the row sequences of M^T (c1 persists, c2 "
          "persists, c2 composes from d + 1) equal the verdicts from the full state space", agree == len(done) and len(done) > 1000,
          {"chains": len(jobs), "decided": len(done), "agree": agree, "positives in the full-state verdicts": positives})

    res = {"status": "passed", "checks": OUT, "seconds": round(time.time() - T0, 1)}
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
        print("wrote result.json")
    else:
        old = json.loads((HERE / "result.json").read_text())
        same = {k: v["info"] for k, v in old["checks"].items()} == json.loads(json.dumps({k: v["info"] for k, v in OUT.items()}, default=str))
        print("result.json reproduced" if same else "result.json DIFFERS")
        sys.exit(0 if same else 1)
