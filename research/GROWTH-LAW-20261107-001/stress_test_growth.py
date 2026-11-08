#!/usr/bin/env python3
"""One size past for GROWTH-LAW-20261107-001B's computed claims (research-next-steps, "Stress-Test Published Claims").

    python3 -B research/GROWTH-LAW-20261107-001/stress_test_growth.py
Reuses ticket B's engine unchanged. Three tests, with 20 workers:
- the mirror seed (handedness -1), which the contract says gives mirror runs: bfs and random, seeds 1..10, to 500 tiles;
- more seeds: bfs, seeds 21..40, to 500 tiles;
- the four forced runs that reached 500 tiles, continued to 1,000 tiles (same seeds): do they dead-end or stay collar-legal?
Writes stress_test_growth.json beside this file."""
import json
import multiprocessing as mp
import random
import sys
import time
from collections import Counter
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
B = ROOT / "experiments/GROWTH-LAW-20261107-001B/GROWTH-LAW-20261107-001B-E001_pinwheel_grown_outward"
sys.path.insert(0, str(B))
import growth_engine as E  # noqa: E402
import legality as L  # noqa: E402

W = {}
MIRROR = ((Fr(0), Fr(0)), (Fr(1), Fr(0)), (Fr(0), Fr(1)))      # O at 0, P at (1, 0), Q at (0, 1): handedness -1


def init():
    keys, _, by_h = E.law()
    W["by_h"] = by_h
    W["climber"] = L.Climber(keys)


def job(spec):
    t0 = time.time()
    kind, order, seed, size = spec
    if kind == "mirror":
        assert E.A.orient(MIRROR) == -1
        P, rec = E.grow(W["by_h"], order, random.Random(seed), size, seed=MIRROR)
    else:
        P, rec = E.grow(W["by_h"], order, random.Random(seed), size)
    out = {"kind": kind, "order": order, "seed": seed, "size": size, "outcome": rec["outcome"], "tiles": rec["tiles"],
           "moves": rec["moves"], "forced": rec["forced"], "choices": rec["choices"]}
    if kind == "forced long":
        out["tiles_list"] = [[[str(c) for c in pt] for pt in t] for t in P.tiles]
    if kind != "mirror":
        tested, bad = L.atlas_check(list(P.tiles))
        out.update(atlas_darts=tested, atlas_bad=bad)
        if P.is_complete(0):
            out["embeds"] = W["climber"].embed(list(P.tiles), (P.handed(0), P.collar(0)))[0]
    out["seconds"] = round(time.time() - t0, 1)
    return out


def main():
    jobs = [("forced long", "forced", s, 1000) for s in (5, 7, 9, 10)]
    jobs += [("mirror", o, s, 500) for o in ("bfs", "random") for s in range(1, 11)]
    jobs += [("more seeds", "bfs", s, 500) for s in range(21, 41)]
    rows = []
    with mp.Pool(8, initializer=init) as pool:
        for row in pool.imap_unordered(job, jobs):
            rows.append(row)
            print(json.dumps({k: v for k, v in row.items() if k != "tiles_list"}), flush=True)
    summary = {}
    for kind in ("mirror", "more seeds", "forced long"):
        rs = [r for r in rows if r["kind"] == kind]
        summary[kind] = {"runs": len(rs), "outcomes": dict(Counter(r["outcome"] for r in rs)),
                         "sizes": sorted(r["tiles"] for r in rs), "embeds": dict(Counter(str(r.get("embeds")) for r in rs)),
                         "atlas bad": sorted(r["atlas_bad"] for r in rs if "atlas_bad" in r)}
    (HERE / "stress_test_growth.json").write_text(json.dumps({"summary": summary, "rows": rows}, indent=1) + "\n")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
