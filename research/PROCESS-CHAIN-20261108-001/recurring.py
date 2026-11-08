#!/usr/bin/env python3
"""Post hoc, exploratory (not part of ticket B's frozen contract): in the census's chains, at how many lags of the eventual cycle
does c2 bind the end rings A and C? The frozen verdict asked for every lag from d + 1 on; this asks for recurring lags.

    .venv/bin/python3 -B research/PROCESS-CHAIN-20261108-001/recurring.py   writes recurring.json
Reuses ticket A's library and ticket B's run.py layout with 16 worker processes."""
import hashlib
import json
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments/PROCESS-CHAIN-20261108-001B/PROCESS-CHAIN-20261108-001B-E001_chain_census"))
import run as B  # noqa: E402

C, P, S, K = B.C, B.P, B.S, B.K
T0 = time.time()


def job(args):
    r, mA, mB, mC, family, law = args
    k = mB // 2
    a, b, c, N, blocks = C.layout(mA, mB, mC, k)
    nxt = C.chain_state_map(r, mA, mB, mC, k, family, law)
    cur = np.arange(len(nxt), dtype=np.int64)
    seen, e2, v1, v2 = {}, [], [], []
    for T in range(1, B.CAP + 1):
        cur = nxt[cur]
        key = hashlib.blake2b(cur.tobytes(), digest_size=16).digest()
        if key in seen:
            T1, period = seen[key], T - seen[key]
            cyc = slice(T1 - 1, T1 + period - 1)
            frac = sum(e2[cyc]) / period
            both_cyc = sum(1 for x, y, z in zip(e2[cyc], v1[cyc], v2[cyc]) if x and y and z) / period
            return [r, mA, mB, mC, family, law, period, round(frac, 4), round(both_cyc, 4), all(v1) and all(v2)]
        seen[key] = T
        F1, F2 = (cur & 1).astype(np.uint8), ((cur >> 1) & 1).astype(np.uint8)
        e2.append(C.binds(F2, blocks, ("A", "C"), N))
        v1.append(C.binds(F1, blocks, ("A", "B"), N))
        v2.append(C.binds(F2, blocks, ("B", "C"), N))
    return [r, mA, mB, mC, family, law, None, None, None, None]


def main():
    reps = K.classes()
    laws = [("proposals", g2) for g2 in P.PARITIES] + [("self-blind", u) for u in S.NONCONSTANT_TWO]
    jobs = [(r, *size, fam, law) for size in B.SIZES for r in reps for fam, law in laws]
    with Pool(16) as pool:
        rows = pool.map(job, jobs, chunksize=8)
    dec = [x for x in rows if x[6] is not None]
    rec = [x for x in dec if x[7] > 0]
    out = {"chains": len(rows), "decided": len(dec),
           "c2 binds the ends at some lag of the cycle": len(rec),
           "of those, at every lag of the cycle": sum(1 for x in rec if x[7] == 1),
           "share of cycle lags with the ends bound (among chains that have some)": dict(sorted(Counter(round(x[7], 1) for x in rec).items())),
           "chains whose cycle has lags with the ends bound and both contacts binding": sum(1 for x in dec if x[8] > 0),
           "chains with both contacts persistent and the ends bound at some cycle lag": sum(1 for x in dec if x[9] and x[7] > 0),
           "rules with recurring composition (top 15)": dict(Counter(x[0] for x in rec).most_common(15)),
           "examples (rule, sizes, family, law, period, share)": [[x[0], f"{x[1]}/{x[2]}/{x[3]}", x[4], x[5], x[6], x[7]] for x in rec[:20]],
           "seconds": round(time.time() - T0, 1)}
    (HERE / "recurring.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
