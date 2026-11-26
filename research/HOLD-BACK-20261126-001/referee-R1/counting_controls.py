"""Fixed follow-up to the trace check: all four cap-positive census pairs.

These are selected controls. Compare all additions after rounds 1, 2 and 3
under a demand-dependent ceiling, with the original 12-round and 1,500-knot
limits. Count differing allocations and later births on each hearing.
"""
import argparse
import json
from archive import records, STUDY
from counting_ceiling import fresh
from minimum_places import check
from growth import Law

def run(skip, count):
    positive = [r for r in records(STUDY / "hold_runs.jsonl.gz")
                if r["law"][0] == "CAP-3" and any(e["heard"] for e in r["changes"])]
    assert len(positive) == 4
    law = Law(lambda b: fresh(len(b.inputs), b.demand))
    for row in positive[skip:skip+count]:
        result = check(row, law=law, ceiling=lambda p,d: 1 + (max(1,d)-1).bit_length(),
                       rounds=12, bound=1500, edits_after=(1,2,3))
        print(json.dumps(result), flush=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip", type=int, default=0)
    parser.add_argument("--limit", type=int, default=4)
    args = parser.parse_args()
    run(args.skip, args.limit)
