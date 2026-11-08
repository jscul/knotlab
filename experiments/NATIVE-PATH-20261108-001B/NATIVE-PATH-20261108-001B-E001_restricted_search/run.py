"""NATIVE-PATH-20261108-001B-E001: restricted searches for native paths across time (exploratory; see contract.json).

    .venv/bin/python3 -B run.py           both families; writes artifacts/NATIVE-PATH-20261108-001B/
                                          NATIVE-PATH-20261108-001B-E001_restricted_search/run/result.json and paths.json
    .venv/bin/python3 -B run.py --pilot   times 500 paths of each family and prints no verdicts
Every verdict is exact by ticket A's row-sequence reduction. Only paths whose three contacts all persist are written out."""
from __future__ import annotations

import hashlib
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
sys.path.insert(0, str(ROOT / "proofs/NATIVE-PATH-20261108-001A/NATIVE-PATH-20261108-001A-P001_paths_reduce_to_row_sequences"))
import path_lib as PL  # noqa: E402

C = PL.C
OUT = ROOT / "artifacts" / "NATIVE-PATH-20261108-001B" / "NATIVE-PATH-20261108-001B-E001_restricted_search" / "run"
CARRIERS = ROOT / "artifacts/AFFINE-WIRE-20261108-001B/AFFINE-WIRE-20261108-001B-E001_affine_search/run/positives.json"
LAWS = [("proposals",)] + [("self-blind", x, y) for x in sorted(PL.ULIN) for y in sorted(PL.ULIN)]
ENDS = (3, 4, 5)
MIDDLE = [(m, k) for m in (4, 5, 6, 7) for k in range(2, m - 1)]           # contacts at least two apart
D_RULES = (90, 150, 60, 102, 170, 240)


def family_one():
    """rule 150 on all four rings"""
    for m0 in ENDS:
        for m3 in ENDS:
            for (m1, k1) in MIDDLE:
                for (m2, k2) in MIDDLE:
                    yield ("150 everywhere", (150, 150, 150, 150), (m0, m1, m2, m3), [k1, k2])


def family_two():
    """each carrying chain of AFFINE-WIRE-20261108-001B extended by one end ring after its last ring"""
    rows = json.loads(CARRIERS.read_text())["rows"]
    carriers = [r for r in rows if r[5] and r[8] >= 2]
    for r in carriers:
        (rA, rB, rC), (mA, mB, mC), k, law1, law2 = r[0], r[1], r[2], tuple(r[3]), tuple(r[4])
        for kC in range(2, mC - 1):
            for rD in D_RULES:
                for mD in ENDS:
                    yield ("carrier extended", (rA, rB, rC, rD), (mA, mB, mC, mD), [k, kC], (law1, law2))


def job(item):
    name, rules, sizes, ks, fixed = item
    counts = Counter()
    keep = []
    law_sets = [fixed + (l3,) for l3 in LAWS] if fixed else [(a, b, c) for a in LAWS for b in LAWS for c in LAWS]
    for laws in law_sets:
        a = PL.analyze(rules, sizes, ks, laws)
        counts["paths"] += 1
        if not a["all persist"]:
            continue
        counts["all three contacts persist"] += 1
        counts["native (ends bound at the last contact from the light cone)"] += a["ends at the last contact"]
        counts["ends bound at both end contacts"] += a["ends at the last contact"] and a["ends at the first contact"]
        counts["last contact binds every ring"] += a["last contact binds every ring"]
        keep.append([name, list(rules), list(sizes), ks, [list(l) for l in laws], a["ends at the last contact"],
                     a["ends at the first contact"], a["last contact binds every ring"], a["light cone"], a["periods"]])
    return name, counts, keep


def items():
    one = [(n, r, s, k, None) for (n, r, s, k) in family_one()]
    two = [(n, r, s, k, f) for (n, r, s, k, f) in family_two()]
    return one, two


def brute(rules, sizes, ks, laws, cap=8192):
    nxt, N, blocks = PL.mixed_state_map(rules, sizes, ks, tuple(tuple(l) for l in laws))
    n = len(sizes)
    L = PL.light_cone(sizes, ks)
    names = [f"R{i}" for i in range(n)]
    binds = lambda F, ns: F.min() != F.max() and not any(C.decides_outside(F, *blocks[x], N) for x in ns)
    cur = np.arange(len(nxt), dtype=np.int64)
    seen, per = {}, {"p0": [], "p1": [], "p2": [], "ends": []}
    for T in range(1, cap + 1):
        cur = nxt[cur]
        key = hashlib.blake2b(cur.tobytes(), digest_size=16).digest()
        if key in seen:
            T1, period = seen[key], T - seen[key]
            hold = lambda seq, start: all(seq[min(start, T1) - 1:T1 + period - 1]) and all(seq[start - 1:])
            return [hold(per["p0"], 1), hold(per["p1"], 1), hold(per["p2"], 1), hold(per["ends"], L)]
        seen[key] = T
        Fs = [((cur >> c) & 1).astype(np.uint8) for c in range(3)]
        per["p0"].append(binds(Fs[0], (names[0], names[1])))
        per["p1"].append(binds(Fs[1], (names[1], names[2])))
        per["p2"].append(binds(Fs[2], (names[2], names[3])))
        per["ends"].append(binds(Fs[2], (names[0], names[3])))
    return None


def main():
    t0 = time.time()
    one, two = items()
    if "--pilot" in sys.argv:
        rng = random.Random(1)
        for fam in (one, two):
            s = time.time()
            for it in rng.sample(fam, 5):
                name, rules, sizes, ks, fixed = it
                for _ in range(100):
                    laws = fixed + (rng.choice(LAWS),) if fixed else tuple(rng.choice(LAWS) for _ in range(3))
                    PL.analyze(rules, sizes, ks, laws)
            print("pilot: 500 paths of", fam[0][0], "in", round(time.time() - s, 1), "s; items", len(fam))
        return
    OUT.mkdir(parents=True, exist_ok=True)
    with Pool(16) as pool:
        res = pool.map(job, one + two, chunksize=1)
    totals = {"150 everywhere": Counter(), "carrier extended": Counter()}
    keep = []
    for name, counts, kp in res:
        totals[name].update(counts)
        keep.extend(kp)
    native = [x for x in keep if x[5]]
    native.sort(key=lambda x: (sum(x[2]), x[2], x[3], x[1]))
    small = [x for x in native if sum(x[2]) - 3 <= 15][:10]
    verified = []
    for x in small:
        b = brute(tuple(x[1]), tuple(x[2]), x[3], x[4])
        verified.append({"path": x[:5], "full state space (c1, c2, c3 persist; ends at c3)": b,
                         "agrees": b is not None and all(b)})
    result = {"experiment": "NATIVE-PATH-20261108-001B-E001", "families": {k: dict(v) for k, v in totals.items()},
              "native paths": len(native),
              "H1 (some native path exists in the restricted families)": len(native) > 0,
              "native paths by family": dict(Counter(x[0] for x in native)),
              "native paths by rules (top 15)": [[k_, v] for k_, v in Counter(tuple(x[1]) for x in native).most_common(15)],
              "native paths by sizes and positions (top 10)": [[list(k_[0]), list(k_[1]), v] for k_, v in Counter((tuple(x[2]), tuple(x[3])) for x in native).most_common(10)],
              "smallest native paths": native[:10],
              "verified on the full state space": verified,
              "all verified": all(v["agrees"] for v in verified) if verified else None,
              "seconds": round(time.time() - t0, 1)}
    (OUT / "paths.json").write_text(json.dumps({"columns": ["family", "rules", "sizes", "positions", "laws", "native",
                                                            "ends at the first contact", "last contact binds every ring",
                                                            "light cone", "row periods"], "rows": keep}) + "\n")
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("smallest native paths",)}, indent=1)[:6000])


if __name__ == "__main__":
    main()
