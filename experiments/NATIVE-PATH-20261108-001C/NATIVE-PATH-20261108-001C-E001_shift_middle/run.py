"""NATIVE-PATH-20261108-001C-E001: a shift as the second middle ring (exploratory; see contract.json).

    .venv/bin/python3 -B run.py           the search; writes artifacts/NATIVE-PATH-20261108-001C/
                                          NATIVE-PATH-20261108-001C-E001_shift_middle/run/result.json and paths.json
    .venv/bin/python3 -B run.py --pilot   times 2,000 random paths of the family and prints no verdicts
Every verdict is exact by ticket A's row-sequence reduction. Only paths whose three contacts all persist are written out."""
from __future__ import annotations

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
import run as B  # noqa: E402

OUT = ROOT / "artifacts" / "NATIVE-PATH-20261108-001C" / "NATIVE-PATH-20261108-001C-E001_shift_middle" / "run"
SHIFTS = (170, 240)
C_SIZES = [(m, k) for m in (4, 5, 6) for k in range(2, m - 1)]
D_RULES = (90, 150, 60, 102, 204, 170, 240)
D_SIZES = (3, 4, 5)
U = sorted(PL.ULIN)


def items():
    rows = json.loads(B.CARRIERS.read_text())["rows"]
    carriers = [r for r in rows if r[5] and r[8] >= 2]
    out = []
    for r in carriers:
        (rA, rB, _), (mA, mB, _), k, law1, law2 = r[0], r[1], r[2], tuple(r[3]), tuple(r[4])
        c2_laws = [law2] if law2[0] == "proposals" else [("self-blind", law2[1], u) for u in U]
        for rC in SHIFTS:
            for (mC, kC) in C_SIZES:
                for l2 in c2_laws:
                    out.append(((rA, rB, rC), (mA, mB, mC), [k, kC], (law1, l2)))
    return out


def job(item):
    (rA, rB, rC), (mA, mB, mC), ks, (law1, law2) = item
    counts, keep = Counter(), []
    for rD in D_RULES:
        for mD in D_SIZES:
            for law3 in B.LAWS:
                rules, sizes, laws = (rA, rB, rC, rD), (mA, mB, mC, mD), (law1, law2, law3)
                a = PL.analyze(rules, sizes, ks, laws)
                counts["paths"] += 1
                if not a["all persist"]:
                    continue
                counts["all three contacts persist"] += 1
                counts["native"] += a["ends at the last contact"]
                counts["ends bound at both end contacts"] += a["ends at the last contact"] and a["ends at the first contact"]
                counts["last contact binds every ring"] += a["last contact binds every ring"]
                keep.append(["shift middle", list(rules), list(sizes), ks, [list(l) for l in laws], a["ends at the last contact"],
                             a["ends at the first contact"], a["last contact binds every ring"], a["light cone"], a["periods"]])
    return counts, keep


def main():
    t0 = time.time()
    its = items()
    if "--pilot" in sys.argv:
        rng = random.Random(1)
        for it in rng.sample(its, 10):
            (rA, rB, rC), (mA, mB, mC), ks, (l1, l2) = it
            for _ in range(200):
                PL.analyze((rA, rB, rC, rng.choice(D_RULES)), (mA, mB, mC, rng.choice(D_SIZES)), ks, (l1, l2, rng.choice(B.LAWS)))
        print("pilot: 2,000 paths in", round(time.time() - t0, 1), "s; items", len(its), "paths", len(its) * len(D_RULES) * len(D_SIZES) * len(B.LAWS))
        return
    OUT.mkdir(parents=True, exist_ok=True)
    with Pool(16) as pool:
        res = pool.map(job, its, chunksize=4)
    total, keep = Counter(), []
    for counts, kp in res:
        total.update(counts)
        keep.extend(kp)
    native = sorted([x for x in keep if x[5]], key=lambda x: (sum(x[2]), x[2], x[3], x[1]))
    verified = []
    for x in [x for x in native if sum(x[2]) - 3 <= 15][:10]:
        b = B.brute(tuple(x[1]), tuple(x[2]), x[3], x[4])
        verified.append({"path": x[:5], "full state space (c1, c2, c3 persist; ends at c3)": b, "agrees": b is not None and all(b)})
    result = {"experiment": "NATIVE-PATH-20261108-001C-E001", "counts": dict(total), "native paths": len(native),
              "H1 (some native path exists with a shift as the second middle ring)": len(native) > 0,
              "native paths by rules (top 15)": [[list(k_), v] for k_, v in Counter(tuple(x[1]) for x in native).most_common(15)],
              "native paths by laws (top 10)": [[k_, v] for k_, v in Counter(json.dumps(x[4]) for x in native).most_common(10)],
              "smallest native paths": native[:10], "verified on the full state space": verified,
              "all verified": all(v["agrees"] for v in verified) if verified else None, "seconds": round(time.time() - t0, 1)}
    (OUT / "paths.json").write_text(json.dumps({"columns": ["family", "rules", "sizes", "positions", "laws", "native",
                                                            "ends at the first contact", "last contact binds every ring",
                                                            "light cone", "row periods"], "rows": keep}) + "\n")
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("smallest native paths",)}, indent=1)[:6000])


if __name__ == "__main__":
    main()
