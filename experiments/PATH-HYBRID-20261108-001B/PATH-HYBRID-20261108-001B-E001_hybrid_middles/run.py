"""PATH-HYBRID-20261108-001B-E001: hybrid second middle rings (exploratory; see contract.json).

    .venv/bin/python3 -B run.py           the search; writes artifacts/PATH-HYBRID-20261108-001B/
                                          PATH-HYBRID-20261108-001B-E001_hybrid_middles/run/result.json and paths.json
    .venv/bin/python3 -B run.py --pilot   times 2,000 random paths and prints no verdicts
The first part of each path is one of the 20 smallest carrying chains of AFFINE-WIRE-20261108-001B with self-blind laws; its old end
ring C becomes a hybrid middle ring, each non-contact cell with its own rule. Every verdict is exact by the row-sequence reduction."""
from __future__ import annotations

import hashlib
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
sys.path.insert(0, str(HERE))
import hybrid_lib as H  # noqa: E402

PL, C = H.PL, H.C
OUT = ROOT / "artifacts" / "PATH-HYBRID-20261108-001B" / "PATH-HYBRID-20261108-001B-E001_hybrid_middles" / "run"
CARRIERS = ROOT / "artifacts/AFFINE-WIRE-20261108-001B/AFFINE-WIRE-20261108-001B-E001_affine_search/run/positives.json"
CELL_RULES = (170, 240, 204, 150, 90, 60, 102)
C_SHAPES = [(4, 2), (5, 2), (5, 3)]
D_RULES = (90, 150, 60, 204)
D_SIZES = (3, 4)
U = sorted(H.ULIN)
SELF_BLIND = [("self-blind", x, y) for x in U for y in U]


def carriers():
    rows = json.loads(CARRIERS.read_text())["rows"]
    out, seen = [], set()
    for r in sorted([r for r in rows if r[5] and r[8] >= 2 and r[3][0] == "self-blind" and r[4][0] == "self-blind"],
                    key=lambda r: (sum(r[1]), r[1], r[2], r[0], r[3], r[4])):
        key = (tuple(r[0]), tuple(r[1]), r[2], tuple(r[3]), tuple(r[4]))
        if key not in seen:
            seen.add(key)
            out.append(r)
        if len(out) == 20:
            break
    return out


def items():
    out = []
    for r in carriers():
        (rA, rB, _), (mA, mB, _), k, law1, law2 = r[0], r[1], r[2], tuple(r[3]), tuple(r[4])
        for (mC, kC) in C_SHAPES:
            free = [j for j in range(mC) if j not in (0, kC)]
            for assign in itertools.product(CELL_RULES, repeat=len(free)):
                rC = [204] * mC
                for j, rule in zip(free, assign):
                    rC[j] = rule
                for uC in U:
                    out.append(((rA, rB, tuple(rC)), (mA, mB, mC), [k, kC], (law1, ("self-blind", law2[1], uC))))
    return out


def job(item):
    (rA, rB, rC), (mA, mB, mC), ks, (law1, law2) = item
    counts, keep = Counter(), []
    for rD in D_RULES:
        for mD in D_SIZES:
            for law3 in SELF_BLIND:
                rules, sizes, laws = (rA, rB, list(rC), rD), (mA, mB, mC, mD), (law1, law2, law3)
                a = H.analyze(rules, sizes, ks, laws)
                counts["paths"] += 1
                if not a["all persist"]:
                    continue
                counts["all three contacts persist"] += 1
                counts["native"] += a["ends at the last contact"]
                counts["last contact binds every ring"] += a["last contact binds every ring"]
                keep.append([[rA, rB, list(rC), rD], list(sizes), ks, [list(l) for l in laws], a["ends at the last contact"],
                             a["ends at the first contact"], a["last contact binds every ring"], a["light cone"], a["periods"]])
    return counts, keep


def brute(rules, sizes, ks, laws, cap=8192):
    nxt, N, blocks = H.mixed_state_map(rules, sizes, ks, laws)
    L = PL.light_cone(sizes, ks)
    names = [f"R{i}" for i in range(4)]
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
    its = items()
    if "--pilot" in sys.argv:
        rng = random.Random(1)
        for _ in range(2000):
            (rA, rB, rC), sizes3, ks, (l1, l2) = rng.choice(its)
            H.analyze((rA, rB, list(rC), rng.choice(D_RULES)), sizes3 + (rng.choice(D_SIZES),), ks, (l1, l2, rng.choice(SELF_BLIND)))
        print("pilot: 2,000 paths in", round(time.time() - t0, 1), "s; items", len(its), "paths", len(its) * len(D_RULES) * len(D_SIZES) * len(SELF_BLIND))
        return
    OUT.mkdir(parents=True, exist_ok=True)
    with Pool(16) as pool:
        res = pool.map(job, its, chunksize=8)
    total, keep = Counter(), []
    for counts, kp in res:
        total.update(counts)
        keep.extend(kp)
    native = sorted([x for x in keep if x[4]], key=lambda x: (sum(x[1]), x[1], x[2], json.dumps(x[0])))
    verified = []
    for x in native[:10]:
        rules = (x[0][0], x[0][1], x[0][2], x[0][3])
        b = brute(rules, tuple(x[1]), x[2], tuple(tuple(l) for l in x[3]))
        verified.append({"path": x[:4], "full state space (c1, c2, c3 persist; ends at c3)": b, "agrees": b is not None and all(b)})
    roles = Counter()
    for x in native:
        rC = x[0][2]
        kinds = tuple(sorted({"shift" if r in (170, 240) else ("buffer" if r == 204 else "additive") for j, r in enumerate(rC) if j not in (0, x[2][1])}))
        roles[kinds] += 1
    result = {"experiment": "PATH-HYBRID-20261108-001B-E001", "carriers used": 20, "counts": dict(total), "native paths": len(native),
              "H1 (some hybrid second middle ring gives a native path)": len(native) > 0,
              "kinds of cells in the hybrid ring among native paths": [[list(k_), v] for k_, v in roles.most_common()],
              "smallest native paths": native[:10], "verified on the full state space": verified,
              "all verified": all(v["agrees"] for v in verified) if verified else None, "seconds": round(time.time() - t0, 1)}
    (OUT / "paths.json").write_text(json.dumps({"columns": ["rules (A, B, C per cell, D)", "sizes", "positions", "laws", "native",
                                                            "ends at the first contact", "last contact binds every ring", "light cone",
                                                            "row periods"], "rows": keep}) + "\n")
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "smallest native paths"}, indent=1)[:5000])


if __name__ == "__main__":
    main()
