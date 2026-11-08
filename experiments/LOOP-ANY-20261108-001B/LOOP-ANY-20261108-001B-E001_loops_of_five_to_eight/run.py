"""LOOP-ANY-20261108-001B-E001: a census of loops of five to eight rings (exploratory; see contract.json).

    .venv/bin/python3 -B run.py           the census; writes artifacts/LOOP-ANY-20261108-001B/LOOP-ANY-20261108-001B-E001_loops_of_five_to_eight/
                                          run/result.json and loops.json
    .venv/bin/python3 -B run.py --pilot   times random loops and prints no verdicts
Loops of r = 5 to 8 rule-60 rings of s = 4 to 16 cells (LOOP-RINGS-20261108-001A's construction), every contact with law (12, 12), the
contacts' positions k_i drawn from {2, floor(s/2), ceil(s/2), s - 2}, one loop per rotation class. For each loop: whether it is
balanced (k_1 + ... + k_r = rs/2); the first lag up to 400 at which some contact's row misses one of its two rings, if any; and, for
balanced loops, whether the chain-end witnesses of LOOP-ANY-20261108-001A keep coefficient 1 at every lag to 400. Rows by
SEPARATE-20261108-001A's net_lib."""
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
sys.path.insert(0, str(ROOT / "experiments/LOOP-RINGS-20261108-001A/LOOP-RINGS-20261108-001A-E001_closed_loops"))
sys.path.insert(0, str(ROOT / "proofs/SEPARATE-20261108-001A/SEPARATE-20261108-001A-P001_a_cut_separates_a_cycle_needs_two"))
import run as LR  # noqa: E402
import net_lib as N  # noqa: E402

OUT = ROOT / "artifacts" / "LOOP-ANY-20261108-001B" / "LOOP-ANY-20261108-001B-E001_loops_of_five_to_eight" / "run"
H = 400


def positions(s):
    return sorted({2, s // 2, (s + 1) // 2, s - 2})


def necklaces(r, s):
    seen, out = set(), []
    for ks in itertools.product(positions(s), repeat=r):
        canon = min(ks[i:] + ks[:i] for i in range(r))
        if canon not in seen:
            seen.add(canon)
            out.append(canon)
    return out


def step(rows, r):
    v = 0
    while r:
        low = r & -r
        v ^= rows[low.bit_length() - 1]
        r ^= low
    return v


def judge(r, s, ks):
    net = LR.loop_net(s, ks, [(12, 12)] * r)
    rings, Nn, blocks = N.layout(net[0], net[2])
    rows, _, _ = N.matrix(*net)
    balanced = 2 * sum(ks) == r * s
    first, witness = None, True
    for c in range(r):
        ma, mb = N.mask(blocks, c), N.mask(blocks, (c + 1) % r)
        wA, wB = rings[c][ks[c] - 1], rings[(c + 1) % r][s - 1]
        row = 1 << c
        for T in range(1, H + 1):
            row = step(rows, row)
            if balanced and not (row >> wA & 1 and row >> wB & 1):
                witness = False
            if not (row & ma and row & mb):
                first = T if first is None else min(first, T)
                break
    return balanced, first, (witness if balanced else None)


def job(item):
    r, s = item
    counts, keep = Counter(), []
    for ks in necklaces(r, s):
        balanced, first, witness = judge(r, s, ks)
        persist = first is None
        counts[("balanced" if balanced else "unbalanced", "persistent to 400" if persist else "misses a ring")] += 1
        if balanced:
            counts[("balanced", "witnesses hold" if witness else "witnesses fail")] += 1
        if balanced or persist:
            keep.append([r, s, list(ks), balanced, first, witness])
    return r, s, counts, keep


def main():
    t0 = time.time()
    items = [(r, s) for r in range(5, 9) for s in range(4, 17)]
    if "--pilot" in sys.argv:
        rng = random.Random(3)
        n = 0
        for _ in range(300):
            r, s = rng.choice(items)
            judge(r, s, tuple(rng.choice(positions(s)) for _ in range(r)))
            n += 1
        print("pilot:", n, "loops in", round(time.time() - t0, 1), "s; rotation classes:", sum(len(necklaces(r, s)) for r, s in items))
        return
    OUT.mkdir(parents=True, exist_ok=True)
    with Pool(16) as pool:
        res = pool.map(job, sorted(items, key=lambda x: -x[0] * x[1]), chunksize=1)
    total, by, keep = Counter(), {}, []
    for r, s, counts, kp in res:
        total.update(counts)
        by[f"{r} rings, {s} cells"] = {" / ".join(k): v for k, v in counts.items()}
        keep.extend(kp)
    result = {"experiment": "LOOP-ANY-20261108-001B-E001", "loops (rotation classes)": sum(total[k] for k in total if k[1] in ("persistent to 400", "misses a ring")),
              "totals": {" / ".join(k): v for k, v in sorted(total.items())},
              "H1 (every balanced loop persists, through the chain-end witnesses)": total[("balanced", "misses a ring")] == 0 and total[("balanced", "witnesses fail")] == 0,
              "by rings and size": by, "seconds": round(time.time() - t0, 1)}
    (OUT / "loops.json").write_text(json.dumps({"columns": ["rings", "size", "positions", "balanced", "first miss", "witnesses hold"], "rows": keep}) + "\n")
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "by rings and size"}, indent=1))


if __name__ == "__main__":
    main()
