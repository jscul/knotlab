#!/usr/bin/env python3
"""One size past for AFFINE-WIRE-20261108-001B (research-next-steps, "Stress-Test Published Claims"): transport of persistent
composition to larger rings, and a canonical check of one knot.

    .venv/bin/python3 -B research/AFFINE-WIRE-20261108-001/stress_test.py   writes stress_test.json
- Transport: for every rule triple and law pair that composes persistently with contacts at least two cells apart in the search,
  the same chain one size past it, at mB = 8 with mA and mC in 3..6 and every position with d >= 2 (the search went to 5, 7 and
  5), by ticket A's exact row-sequence reduction, each row iterated up to 20,000 lags (beyond that undecided).
- Canonical check: for the smallest such chain, the knots of c2's two-time law at lags up to the repeat, by GROWTH-LAW-20261107-001A's
  generic enumerator, and the parity relation of its eventual support by knotlab check."""
import json
import subprocess
import sys
import time
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments/AFFINE-WIRE-20261108-001B/AFFINE-WIRE-20261108-001B-E001_affine_search"))
sys.path.insert(0, str(ROOT / "proofs/GROWTH-LAW-20261107-001A/GROWTH-LAW-20261107-001A-P001_a_beginning_is_a_knot"))
import run as B  # noqa: E402
import growth_law_lib as G  # noqa: E402

W, C = B.W, B.C
T0 = time.time()
BIG = [(mA, 8, mC, k) for mA in range(3, 7) for mC in range(3, 7) for k in range(1, 8)]
CAP = 20000


def capped_orbit(rows, start):
    seen, out, r, T = {}, [], start, 0
    while T < CAP:
        v, x = 0, r
        while x:
            low = x & -x
            v ^= rows[low.bit_length() - 1]
            x ^= low
        r, T = v, T + 1
        if r in seen:
            return out, seen[r], T - seen[r]
        seen[r] = T
        out.append(r)
    return out, None, None


def transport(group):
    rules, law1, law2 = group
    hits = undecided = tested = 0
    for (mA, mB, mC, k) in BIG:
        d = C.ring_distance(k, mB)
        if d < 2:
            continue
        rows, N, blocks = W.linear_matrix(rules, (mA, mB, mC), k, law1, law2)
        mA_, mB_, mC_ = (W.block_mask(blocks, x) for x in "ABC")
        s1, T1a, p1 = capped_orbit(rows, 1 << 0)
        s2, T1b, p2 = capped_orbit(rows, 1 << 1)
        tested += 1
        if T1a is None or T1b is None:
            undecided += 1
            continue
        ok = (W.holds_from(s1, T1a, p1, 1, lambda r: bool(r & mA_) and bool(r & mB_))
              and W.holds_from(s2, T1b, p2, 1, lambda r: bool(r & mB_) and bool(r & mC_))
              and W.holds_from(s2, T1b, p2, d + 1, lambda r: bool(r & mA_) and bool(r & mC_)))
        hits += ok
    return [list(rules), list(law1), list(law2), tested, hits, undecided]


def main():
    rows = json.loads((ROOT / "artifacts/AFFINE-WIRE-20261108-001B/AFFINE-WIRE-20261108-001B-E001_affine_search/run/positives.json").read_text())["rows"]
    far = [r for r in rows if r[5] and r[8] >= 2]
    groups = sorted({(tuple(r[0]), tuple(r[3]), tuple(r[4])) for r in far})
    with Pool(16) as pool:
        res = pool.map(transport, groups, chunksize=1)
    out = {"rule-law groups composing persistently with d >= 2 in the search": len(groups),
           "sizes one past the search": "mB = 8, mA and mC in 3..6, every position with d >= 2",
           "chains tested": sum(x[3] for x in res), "undecided within the cap": sum(x[5] for x in res),
           "groups that compose persistently at some size one past the search": sum(1 for x in res if x[4] > 0),
           "persistently composing chains one past the search": sum(x[4] for x in res),
           "largest counts (rules, law at c1, law at c2, tested, composing, undecided)": sorted(res, key=lambda x: -x[4])[:12]}
    # canonical check on the smallest chain
    far.sort(key=lambda r: (sum(r[1]), r[1], r[2], r[0]))
    r = far[0]
    rules, sizes, k, law1, law2 = tuple(r[0]), tuple(r[1]), r[2], tuple(r[3]), tuple(r[4])
    nxt, N, blocks = W.mixed_state_map(rules, sizes, k, law1, law2)
    import numpy as np
    cur = np.arange(len(nxt), dtype=np.int64)
    knots_ok = []
    masks = {x: W.block_mask(blocks, x) for x in "ABC"}
    for T in range(1, 9):
        cur = nxt[cur]
        F = ((cur >> 1) & 1).astype(np.uint8)
        R = G.Rel([f"v{j}" for j in range(N)] + ["c2"], [u | (int(F[u]) << N) for u in range(1 << N)])
        kn = G.knots(R)
        through = [S for S in kn if S >> N & 1]
        if T >= C.ring_distance(k, sizes[1]) + 1:
            knots_ok.append(bool(through) and all(S & masks["A"] and S & masks["C"] for S in through))
    mrows, N, blocks = W.linear_matrix(rules, sizes, k, law1, law2)
    s2, T1, p2 = W.row_orbit(mrows, 1 << 1)
    support = [j for j in range(N) if s2[-1] >> j & 1]
    names = [f"x{j}" for j in support]
    cnf = []
    import itertools
    for vals in itertools.product((0, 1), repeat=len(names) + 1):
        if sum(vals) % 2 == 1:                          # forbid odd assignments: contact = parity of the support
            cnf.append(" ".join((f"~{n}" if v else n) for n, v in zip(names + ["c"], vals)))
    env = {"PYTHONPATH": str(ROOT / "tools"), "PATH": "/usr/bin:/bin"}
    kl = json.loads(subprocess.run([sys.executable, "-B", "-m", "knotlab", "check", "--cnf", ";".join(cnf), "--loops", *names,
                                    "--contact", "c", "--json"], capture_output=True, text=True, env=env, cwd=ROOT, check=True).stdout)
    out["canonical check"] = {"chain": r, "generic enumerator: every knot through c2(T) meets A and C, T = d + 1..8": all(knots_ok),
                              "eventual support of c2": {x: sum(1 for j in support if masks[x] >> j & 1) for x in "ABC"},
                              "knotlab check of the parity relation on that support": {k_: kl[k_] for k_ in ("is_knot", "binding", "loss_on_erasure", "invisible_in_parts")}}
    out["seconds"] = round(time.time() - T0, 1)
    (HERE / "stress_test.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
