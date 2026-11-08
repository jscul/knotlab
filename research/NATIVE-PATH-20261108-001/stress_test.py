#!/usr/bin/env python3
"""One size past for NATIVE-PATH-20261108-001 (research-next-steps, "Stress-Test Published Claims").

    .venv/bin/python3 -B research/NATIVE-PATH-20261108-001/stress_test.py quick   the light cone on five-ring paths with arbitrary
                                                                              rules, full state spaces (stress_quick.json)
    .venv/bin/python3 -B research/NATIVE-PATH-20261108-001/stress_test.py wide    ticket B's first family one size past: rule 150
                                                                              on all four rings, end rings of 3 to 6 cells, middle
                                                                              rings of 4 to 8 (stress_wide.json; long-running,
                                                                              NATIVE-PATH-S1 in docs/LONG_RUNNING.md)
Reuses ticket A's library and ticket B's run.py (job, LAWS) with 16 worker processes."""
import json
import random
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "proofs/NATIVE-PATH-20261108-001A/NATIVE-PATH-20261108-001A-P001_paths_reduce_to_row_sequences"))
sys.path.insert(0, str(ROOT / "experiments/NATIVE-PATH-20261108-001B/NATIVE-PATH-20261108-001B-E001_restricted_search"))
import path_lib as PL  # noqa: E402
import run as B  # noqa: E402

T0 = time.time()


def cone_job(args):
    rules, sizes, ks, laws = args
    nxt, N, blocks = PL.mixed_state_map(rules, sizes, ks, laws)
    L = PL.light_cone(sizes, ks)
    cur = np.arange(len(nxt), dtype=np.int64)
    early = 0
    for T in range(1, L):
        cur = nxt[cur]
        F = ((cur >> (len(sizes) - 2)) & 1).astype(np.uint8)
        early += PL.C.depends_on_block(F, *blocks["R0"], N)
    return early


def quick():
    rng = random.Random(20261108)
    jobs = []
    for _ in range(300):
        sizes = (3, rng.choice((3, 4)), rng.choice((3, 4)), rng.choice((3, 4)), 3)
        ks = [rng.randint(1, sizes[i] - 1) for i in range(1, 4)]
        jobs.append((tuple(rng.randrange(256) for _ in range(5)), sizes, ks, tuple(rng.choice(B.LAWS) for _ in range(4))))
    with Pool(16) as pool:
        res = pool.map(cone_job, jobs, chunksize=4)
    out = {"five-ring paths with arbitrary rules": len(jobs), "dependences on the first ring before the light cone": sum(res),
           "seconds": round(time.time() - T0, 1)}
    (HERE / "stress_quick.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


def wide():
    middle = [(m, k) for m in (4, 5, 6, 7, 8) for k in range(2, m - 1)]
    items = [("150 everywhere", (150, 150, 150, 150), (m0, m1, m2, m3), [k1, k2], None)
             for m0 in (3, 4, 5, 6) for m3 in (3, 4, 5, 6) for (m1, k1) in middle for (m2, k2) in middle
             if max(m0, m1, m2, m3) > 5 or m1 == 8 or m2 == 8 or m0 == 6 or m3 == 6]
    with Pool(16) as pool:
        res = pool.map(B.job, items, chunksize=1)
    total, native = Counter(), []
    for name, counts, keep in res:
        total.update(counts)
        native.extend(x for x in keep if x[5])
    out = {"family": "rule 150 on all four rings, one size past ticket B (end rings to 6 cells, middle rings to 8)",
           "size-position items (new only)": len(items), "counts": dict(total), "native paths": len(native),
           "smallest native paths": sorted(native, key=lambda x: (sum(x[2]), x[2], x[3]))[:10], "seconds": round(time.time() - T0, 1)}
    (HERE / "stress_wide.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "smallest native paths"}, indent=1))


if __name__ == "__main__":
    {"quick": quick, "wide": wide}[sys.argv[1]]()
