"""Save each distinct chain-positive stage once and retain each occurrence."""

import argparse
import gzip
import json
import resource
import time
from pathlib import Path

from growth import load_census, stage_rows


HERE = Path(__file__).resolve().parent
ARMS = ("one_fewer", "arity_floor")


def write_line(handle, record):
    print(json.dumps(record, separators=(",", ":")), file=handle)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    start_time = time.perf_counter()
    suffix = "_pilot" if args.pilot else ""
    census = load_census()
    indices = range(0, len(census), 97 if args.pilot else 1)
    seen = {}
    occurrence_totals = {arm: {"stages": 0, "chains": 0, "prefix": 0} for arm in ARMS}
    incidence_path = HERE / f"step_incidence{suffix}.jsonl.gz"
    with gzip.open(HERE / f"step_stages{suffix}.jsonl.gz", "wt") as stages, gzip.open(incidence_path, "wt") as incidences:
        for start in indices:
            for arm in ARMS:
                for row in stage_rows(census[start], arm):
                    if not row.chains:
                        continue
                    if row.supports not in seen:
                        stage = len(seen)
                        seen[row.supports] = (stage, row.chains)
                        write_line(stages, {"id": stage, "supports": row.supports, "chains": row.chains})
                    else:
                        stage, first_chains = seen[row.supports]
                        assert first_chains == row.chains
                    write_line(incidences, {"start": start, "arm": arm, "round": row.round, "stage": stage})
                    counts = occurrence_totals[arm]
                    counts["stages"] += 1
                    counts["chains"] += len(row.chains)
                    counts["prefix"] += min(3, len(row.chains))
    summary = {"pilot": args.pilot, "census_start_count": len(indices), "stage_occurrences": occurrence_totals,
               "distinct_stages": len(seen), "distinct_stage_chain_checks": sum(len(s[1]) for s in seen.values()),
               "max_stage_laws": max(len(s) for s in seen),
               "max_stage_distinctions": max(len(set(x for law in s for x in law)) for s in seen),
               "wall_seconds": time.perf_counter() - start_time,
               "peak_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    (HERE / f"step_inventory{suffix}.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
