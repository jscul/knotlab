"""PATH-HYBRID-20261108-001A-E001: a broad sweep of mixed four-ring paths (exploratory; see contract.json).

    .venv/bin/python3 -B run.py           the sweep (long-running); writes artifacts/PATH-HYBRID-20261108-001A/
                                          PATH-HYBRID-20261108-001A-E001_broad_sweep/run/result.json and paths.json
    .venv/bin/python3 -B run.py --pilot   times 2,000 random paths and prints no verdicts
Every verdict is exact by NATIVE-PATH-20261108-001A's row-sequence reduction. Paths whose contacts all persist are written out."""
from __future__ import annotations

import itertools
import json
import random
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/NATIVE-PATH-20261108-001A/NATIVE-PATH-20261108-001A-P001_paths_reduce_to_row_sequences"))
sys.path.insert(0, str(ROOT / "experiments/NATIVE-PATH-20261108-001B/NATIVE-PATH-20261108-001B-E001_restricted_search"))
import path_lib as PL  # noqa: E402
import run as NB  # noqa: E402

OUT = ROOT / "artifacts" / "PATH-HYBRID-20261108-001A" / "PATH-HYBRID-20261108-001A-E001_broad_sweep" / "run"
RULES = sorted(PL.LIN)
SHAPES = [((3, 4, 4, 3), [2, 2])] + [((3, 5, 5, 3), [k1, k2]) for k1 in (2, 3) for k2 in (2, 3)]
LAWS = NB.LAWS


def job(item):
    rules, sizes, ks = item
    counts, keep = Counter(), []
    for laws in itertools.product(LAWS, repeat=3):
        a = PL.analyze(rules, sizes, ks, laws)
        counts["paths"] += 1
        if not a["all persist"]:
            continue
        counts["all three contacts persist"] += 1
        counts["native"] += a["ends at the last contact"]
        counts["last contact binds every ring"] += a["last contact binds every ring"]
        keep.append([list(rules), list(sizes), ks, [list(l) for l in laws], a["ends at the last contact"],
                     a["ends at the first contact"], a["last contact binds every ring"], a["light cone"], a["periods"]])
    return counts, keep


def main():
    t0 = time.time()
    items = [(r, s, k) for r in itertools.product(RULES, repeat=4) for (s, k) in SHAPES]
    if "--pilot" in sys.argv:
        rng = random.Random(1)
        for _ in range(2000):
            r, s, k = rng.choice(items)
            PL.analyze(r, s, k, tuple(rng.choice(LAWS) for _ in range(3)))
        print("pilot: 2,000 paths in", round(time.time() - t0, 1), "s; items", len(items), "paths", len(items) * len(LAWS) ** 3)
        return
    OUT.mkdir(parents=True, exist_ok=True)
    with Pool(16) as pool:
        res = pool.map(job, items, chunksize=2)
    total, keep = Counter(), []
    for counts, kp in res:
        total.update(counts)
        keep.extend(kp)
    native = sorted([x for x in keep if x[4]], key=lambda x: (sum(x[1]), x[1], x[2], x[0]))
    verified = []
    for x in native[:10]:
        b = NB.brute(tuple(x[0]), tuple(x[1]), x[2], x[3])
        verified.append({"path": x[:4], "full state space (c1, c2, c3 persist; ends at c3)": b, "agrees": b is not None and all(b)})
    result = {"experiment": "PATH-HYBRID-20261108-001A-E001", "counts": dict(total), "native paths": len(native),
              "H1 (some native path exists in the sweep)": len(native) > 0,
              "native paths by rules (top 15)": [[list(k_), v] for k_, v in Counter(tuple(x[0]) for x in native).most_common(15)],
              "smallest native paths": native[:10], "verified on the full state space": verified,
              "all verified": all(v["agrees"] for v in verified) if verified else None, "seconds": round(time.time() - t0, 1)}
    (OUT / "paths.json").write_text(json.dumps({"columns": ["rules", "sizes", "positions", "laws", "native", "ends at the first contact",
                                                            "last contact binds every ring", "light cone", "row periods"], "rows": keep}) + "\n")
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "smallest native paths"}, indent=1)[:5000])


if __name__ == "__main__":
    main()
