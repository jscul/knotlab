#!/usr/bin/env python3
"""One size past for GROWTH-LAW-20261107-001C's computed claims (research-next-steps, "Stress-Test Published Claims").

    python3 -B research/GROWTH-LAW-20261107-001/stress_test_c.py
Reuses ticket C's code unchanged (shared_coin.py, with ticket B's engine). Two tests:
- the stronger law in the order C did not run: forced-first growth, seeds 1..10, to 500 tiles (under the collar law alone,
  4 of these 10 reached 500 tiles of non-pinwheel patches);
- the oracle one size past 1,000 tiles: bfs, seeds 1..3, to 1,500 tiles.
Writes stress_test_c.json beside this file."""
import json
import multiprocessing as mp
import sys
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments/GROWTH-LAW-20261107-001C/GROWTH-LAW-20261107-001C-E001_shared_coin"))
import shared_coin as S  # noqa: E402

W = {}


def init():
    keys, _, by_h = S.E.law()
    W["by_h"] = by_h
    W["climber"] = S.L.Climber(keys)


def job(spec):
    t0 = time.time()
    kind, order, seed, size = spec
    if kind == "strong":
        row = S.strong_run(W["by_h"], order, seed, size, W["climber"])
    else:
        row = S.oracle_run(W["by_h"], order, seed, size, W["climber"])
    row["kind"] = kind
    row["seconds"] = round(time.time() - t0, 1)
    return row


def main():
    jobs = [("oracle", "bfs", s, 1500) for s in (1, 2, 3)] + [("strong", "forced", s, 500) for s in range(1, 11)]
    rows = []
    with mp.Pool(13, initializer=init) as pool:
        for row in pool.imap_unordered(job, jobs):
            rows.append(row)
            print(json.dumps({k: row.get(k) for k in ("kind", "order", "seed", "outcome", "tiles", "choices", "final_legal",
                                                      "atlas_bad", "bits_all_options", "bits_legal_options", "seconds")}),
                  flush=True)
    strong = [r for r in rows if r["kind"] == "strong"]
    oracle = [r for r in rows if r["kind"] == "oracle"]
    summary = {
        "stronger law, forced order": {"runs": len(strong), "outcomes": dict(Counter(r["outcome"] for r in strong)),
                                       "sizes": sorted(r["tiles"] for r in strong),
                                       "final legal": dict(Counter(str(r["final_legal"]) for r in strong))},
        "oracle to 1,500 tiles [seed, tiles, choices, bits all, bits legal, legal choices beyond the seed]":
            [[r["seed"], r["tiles"], r["choices"], r["bits_all_options"], r["bits_legal_options"],
              [x for x in r["choices_log"][1:] if x[2] > 1]] for r in oracle],
        "oracle outcomes": dict(Counter(r["outcome"] for r in oracle)),
        "oracle final legal": dict(Counter(str(r["final_legal"]) for r in oracle)),
    }
    (HERE / "stress_test_c.json").write_text(json.dumps({"summary": summary, "rows": rows}, indent=1) + "\n")
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
