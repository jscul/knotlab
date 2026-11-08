"""AFFINE-WIRE-20261108-001B-E001: searching affine chains for persistent composition (exploratory; see contract.json).

    .venv/bin/python3 -B run.py           the search; writes artifacts/AFFINE-WIRE-20261108-001B/
                                          AFFINE-WIRE-20261108-001B-E001_affine_search/run/positives.json and result.json
    .venv/bin/python3 -B run.py --pilot   times 2,000 random chains and prints no verdicts (the contract's feasibility check)
Every verdict is exact (ticket A's row-sequence reduction). Only chains with both contacts persistent are written out."""
from __future__ import annotations

import itertools
import json
import random
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LIB = ROOT / "proofs/AFFINE-WIRE-20261108-001A/AFFINE-WIRE-20261108-001A-P001_persistent_composition_is_about_row_sequences"
sys.path.insert(0, str(LIB))
import wire_lib as W  # noqa: E402

C, P = W.C, W.P
OUT = ROOT / "artifacts" / "AFFINE-WIRE-20261108-001B" / "AFFINE-WIRE-20261108-001B-E001_affine_search" / "run"
RULES = sorted(W.LIN)
LAWS = [("proposals",)] + [("self-blind", x, y) for x in sorted(W.ULIN) for y in sorted(W.ULIN)]
SIZES = [(mA, mB, mC, k) for mA in (3, 4, 5) for mB in range(3, 8) for mC in (3, 4, 5) for k in range(1, mB)]


def job(rules):
    counts = Counter()
    keep = []
    for (mA, mB, mC, k) in SIZES:
        for law1 in LAWS:
            for law2 in LAWS:
                a = W.analyze(rules, (mA, mB, mC), k, law1, law2)
                counts["chains"] += 1
                both = a["c1 persists"] and a["c2 persists"]
                counts["c1 persists"] += a["c1 persists"]
                counts["c2 persists"] += a["c2 persists"]
                counts["both contacts persist"] += both
                counts["c2 composes from d + 1"] += a["c2 composes"]
                counts["both persist and c2 composes"] += both and a["c2 composes"]
                counts["both persist and both contacts compose"] += both and a["c2 composes"] and a["c1 composes"]
                if both:
                    keep.append([list(rules), [mA, mB, mC], k, list(law1), list(law2), a["c2 composes"], a["c1 composes"],
                                 list(a["periods"]), a["d"]])
    return counts, keep


def brute(rules, sizes, k, law1, law2, cap=8192):
    """full-state-space verdicts (c1 persists, c2 persists, c2 composes from d + 1), for verification"""
    import hashlib
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
            return hold(v1, 1), hold(v2, 1), hold(e2, d + 1), T1, period
        seen[key] = T
        F1, F2 = (cur & 1).astype(np.uint8), ((cur >> 1) & 1).astype(np.uint8)
        v1.append(C.binds(F1, blocks, ("A", "B"), N))
        v2.append(C.binds(F2, blocks, ("B", "C"), N))
        e2.append(C.binds(F2, blocks, ("A", "C"), N))
    return None


def main():
    t0 = time.time()
    if "--pilot" in sys.argv:
        rng = random.Random(1)
        for _ in range(2000):
            mA, mB, mC, k = rng.choice(SIZES)
            W.analyze(tuple(rng.choice(RULES) for _ in range(3)), (mA, mB, mC), k, rng.choice(LAWS), rng.choice(LAWS))
        print("pilot: 2,000 chains in", round(time.time() - t0, 1), "s")
        return
    OUT.mkdir(parents=True, exist_ok=True)
    triples = list(itertools.product(RULES, repeat=3))
    with Pool(16) as pool:
        res = pool.map(job, triples, chunksize=1)
    total = Counter()
    keep = []
    for counts, kp in res:
        total.update(counts)
        keep.extend(kp)
    found = [x for x in keep if x[5]]
    found.sort(key=lambda x: (sum(x[1]), x[1], x[2], x[0]))
    # verification of the smallest constructions on the full state space
    verified = []
    for x in found[:12]:
        rules, sizes, k = tuple(x[0]), tuple(x[1]), x[2]
        law1, law2 = tuple(x[3]), tuple(x[4])
        b = brute(rules, sizes, k, law1, law2)
        verified.append({"chain": x, "full state space (c1 persists, c2 persists, c2 composes, T1, period)": b,
                         "agrees": b is not None and b[:3] == (True, True, True)})
    by_rules = Counter(tuple(x[0]) for x in found)
    by_middle = Counter(x[0][1] for x in found)
    by_laws = Counter((tuple(x[3]), tuple(x[4])) for x in found)
    result = {"experiment": "AFFINE-WIRE-20261108-001B-E001", "rules": RULES, "laws": [list(l) for l in LAWS],
              "sizes and positions": len(SIZES), "counts": dict(total),
              "H1 (no chain keeps both contacts and composes from d + 1)": total["both persist and c2 composes"] == 0,
              "persistently composing chains": len(found),
              "middle-ring rules among them": dict(by_middle.most_common()),
              "rule triples among them (top 20)": [[list(k_), v] for k_, v in by_rules.most_common(20)],
              "law pairs among them (top 10)": [[[list(a), list(b)], v] for (a, b), v in by_laws.most_common(10)],
              "smallest constructions, verified on the full state space": verified,
              "all verified": all(v["agrees"] for v in verified) if verified else None,
              "seconds": round(time.time() - t0, 1)}
    (OUT / "positives.json").write_text(json.dumps({"columns": ["rules (A, B, C)", "sizes (mA, mB, mC)", "k", "law at c1", "law at c2",
                                                                "c2 composes from d + 1", "c1 composes from d + 1", "row periods", "d"],
                                                    "rows": keep}) + "\n")
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("laws",)}, indent=1)[:8000])


if __name__ == "__main__":
    main()
