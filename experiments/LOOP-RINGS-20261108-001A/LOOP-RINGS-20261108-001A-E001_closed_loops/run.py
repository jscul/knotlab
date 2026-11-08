"""LOOP-RINGS-20261108-001A-E001: a census of closed loops of rings (exploratory; see contract.json).

    .venv/bin/python3 -B run.py           the census; writes artifacts/LOOP-RINGS-20261108-001A/LOOP-RINGS-20261108-001A-E001_closed_loops/
                                          run/result.json and loops.json
    .venv/bin/python3 -B run.py --pilot   times random loops and prints no verdicts
A loop of r rings R_0 .. R_(r-1), each of s cells on rule 60: contact c_i is cell k_i of R_i and cell 0 of R_(i+1 mod r), so every ring
holds two contacts and influence can travel round. Each contact reads, on its first ring R_i, its left neighbour (the end of the chain
arriving from the contact at cell 0, law 12) or both neighbours (6), and on its second ring its left, right or both neighbours.
Persistence is exact by row sequences (net_lib of SEPARATE-20261108-001A): every contact binds both of its rings at every lag; a row
sequence that does not repeat within 1,000,000 lags is undecided."""
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
sys.path.insert(0, str(ROOT / "proofs/SEPARATE-20261108-001A/SEPARATE-20261108-001A-P001_a_cut_separates_a_cycle_needs_two"))
import net_lib as N  # noqa: E402

OUT = ROOT / "artifacts" / "LOOP-RINGS-20261108-001A" / "LOOP-RINGS-20261108-001A-E001_closed_loops" / "run"
FIRST, SECOND = (12, 6), (12, 10, 6)
CAP = 10 ** 6


def loop_net(s, ks, laws):
    r = len(ks)
    contacts = [(i, ks[i], (i + 1) % r, 0, laws[i]) for i in range(r)]
    return (s,) * r, (60,) * r, contacts


def step(rows, r):
    v = 0
    while r:
        low = r & -r
        v ^= rows[low.bit_length() - 1]
        r ^= low
    return v


def contact_persists(rows, blocks, contact):
    """True / False (with the first lag that misses) / None, exact: binds both rings at every lag up to the repeat of its row"""
    ra, rb = contact[1]
    ma, mb = N.mask(blocks, ra), N.mask(blocks, rb)
    seen, r, T = set(), 1 << contact[0], 0
    while T < CAP:
        r = step(rows, r)
        T += 1
        if r in seen:
            return True, None
        seen.add(r)
        if not (r & ma and r & mb):
            return False, T
    return None, None


def verdict(s, ks, laws):
    net = loop_net(s, ks, laws)
    rows, Nn, blocks = N.matrix(*net)
    first, undecided = None, False
    for c, (ra, pa, rb, pb, law) in enumerate(net[2]):
        ok, T = contact_persists(rows, blocks, (c, (ra, rb)))
        if ok is False:
            first = T if first is None else min(first, T)
            return "not persistent", first
        undecided |= ok is None
    return ("undecided" if undecided else "persistent"), None


def job(item):
    s, ks = item
    r = len(ks)
    counts, keep, misses = Counter(), [], Counter()
    for laws in itertools.product(itertools.product(FIRST, SECOND), repeat=r):
        v, T = verdict(s, ks, laws)
        counts[v] += 1
        if v == "not persistent":
            misses[T] += 1
        else:
            keep.append([s, list(ks), [list(l) for l in laws], v])
    return r, s, counts, keep, misses


def items():
    out = [(s, ks) for s in range(4, 11) for ks in itertools.product(range(2, s - 1), repeat=3)]      # three rings, every position
    out += [(s, ks) for s in range(4, 11) for ks in itertools.product(sorted({2, s - 2}), repeat=4)]  # four rings, two apart
    return out


def main():
    t0 = time.time()
    its = items()
    if "--pilot" in sys.argv:
        rng = random.Random(5)
        for _ in range(2000):
            s, ks = rng.choice(its)
            verdict(s, ks, tuple((rng.choice(FIRST), rng.choice(SECOND)) for _ in ks))
        print("pilot: 2,000 loops in", round(time.time() - t0, 1), "s; items", len(its),
              "loops", sum(36 ** len(ks) if len(ks) == 2 else 6 ** len(ks) for s, ks in its))
        return
    OUT.mkdir(parents=True, exist_ok=True)
    with Pool(16) as pool:
        res = pool.map(job, its, chunksize=1)
    total, by, keep, misses = Counter(), Counter(), [], Counter()
    for r, s, counts, kp, ms in res:
        total.update(counts)
        for k, v in counts.items():
            by[f"{r} rings, {s} cells: {k}"] += v
        keep.extend(kp)
        misses.update(ms)
    result = {"experiment": "LOOP-RINGS-20261108-001A-E001", "loops": sum(total.values()), "verdicts": dict(total),
              "by rings and size": dict(sorted(by.items())),
              "H1 (some closed loop keeps every contact persistent)": total.get("persistent", 0) > 0,
              "first lag at which some contact misses one of its rings (lag: loops), the 20 commonest": [[k, v] for k, v in misses.most_common(20)],
              "persistent or undecided loops (first 40)": keep[:40], "seconds": round(time.time() - t0, 1)}
    (OUT / "loops.json").write_text(json.dumps({"columns": ["size", "positions", "laws", "verdict"], "rows": keep}) + "\n")
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("by rings and size", "persistent or undecided loops (first 40)")}, indent=1))


if __name__ == "__main__":
    main()
