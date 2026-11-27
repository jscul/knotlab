"""Count copies of the sufficient eight-law form on histories where the rival laws differ."""

import argparse
from collections import Counter
import json
from pathlib import Path
from resource import getrusage, RUSAGE_SELF
from time import perf_counter

from growth_replay import LAWS, census_starts, loose, stages
from open_four import paths


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-limit", type=int, default=7075)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    then = perf_counter()
    rows = []
    count = {law: Counter() for law in LAWS}
    qualifying = {law: [] for law in LAWS}
    for i, start in enumerate(census_starts()[:args.start_limit]):
        records = [dict(stages(start, law)) for law in LAWS]
        divergence = next((r for r in range(1, 7) if records[0].get(r) != records[1].get(r)), None)
        if divergence is None:
            continue
        rows.append({"entry": i, "first_different_round": divergence})
        for law, record in zip(LAWS, records):
            for r, stage in record.items():
                if r < divergence or not loose(stage):
                    continue
                count[law][r] += 1
                chain = next(paths(stage, set(range(len(stage)))), None)
                if chain:
                    qualifying[law].append({"entry": i, "round": r, "eight_laws": chain})
    positive = dict(stages(census_starts()[420], LAWS[0], through=2))[2]
    assert next(paths(positive, set(range(len(positive)))), None)
    result = {"starts_per_law": min(args.start_limit, len(census_starts())),
              "through_round": 6, "starts_with_different_support_histories": rows,
              "open_formed_stages_at_or_after_first_difference": count,
              "stages_with_eight_law_chain": qualifying,
              "positive_control_contains_eight_law_chain": True,
              "seconds": round(perf_counter() - then, 5), "peak_KiB": getrusage(RUSAGE_SELF).ru_maxrss}
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(len(rows), count, qualifying, result["seconds"])


if __name__ == "__main__":
    main()
