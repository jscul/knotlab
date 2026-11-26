"""Read the unlinked and start-membership controls directly from the run shards."""

import argparse
from collections import Counter, defaultdict
import gzip
from itertools import islice
import json
from pathlib import Path
import time


HERE = Path(__file__).resolve().parent
TICKET = "FOLLOWS-THE-FORM-20261125-001A"
ARCHIVE = HERE.parents[2] / "artifacts" / TICKET


def rows(runset, limit):
    for path in sorted(ARCHIVE.glob(f"*/runs_{runset}_*.jsonl.gz")):
        with gzip.open(path, "rt") as f:
            for line in islice(f, limit):
                row = json.loads(line)
                assert row["runset"] == runset
                yield row
        if limit is not None:
            break


def collect(limit):
    controls = defaultdict(list)
    for r in rows("R2u", limit):
        assert r["knot_law"] == "nae" and not r["linked"]
        assert r["rounds_read"] == len(r["make"])
        key = (r["first"], r["take"], r["treatment"], r["ration"])
        controls[key].append((r["second"], r["rounds_read"], r["make"], r["stop"]))
    observations = Counter()
    stop_reasons = Counter()
    common_rounds = Counter()
    for runs in controls.values():
        if limit is not None:
            continue
        assert len(runs) == len({x[0] for x in runs}) == 61
        bare, = [r for r in runs if r[0] is None]
        common_rounds[min(r[1] for r in runs)] += 1
        study_agrees = True
        for name, horizon, make, stop in runs:
            if name is None:
                continue
            lesser = min(horizon, bare[1])
            agrees = make[:lesser] == bare[2][:lesser]
            study_agrees = study_agrees and agrees
            observations["same_through_both_read"] += agrees
            observations["comparisons"] += 1
            if horizon != bare[1]:
                direction = "shorter" if horizon < bare[1] else "longer"
                observations[f"unlinked_run_{direction}_than_bare"] += 1
                stop_reasons[f"{direction}, unlinked={stop}, bare={bare[3]}"] += 1
            else:
                observations["same_number_of_rounds"] += 1
        observations["studies_equal_through_pairwise_prefixes"] += study_agrees
    membership = defaultdict(Counter)
    for runset in ("R1", "R2"):
        for r in rows(runset, limit):
            if r["family"] not in {"mixed", "second", "fresh"}:
                continue
            tab = membership[r["treatment"]]
            tab["runs"] += 1
            tab["member_in_later_round"] += r["last_member_round"] > 1
            tab["member_in_final_roster"] += r["start_member_final"]
    return {
        "unlinked_prefix_comparisons": dict(observations),
        "unlinked_different_lengths_by_stop": dict(stop_reasons),
        "unlinked_studies_by_common_round": dict(sorted(common_rounds.items())),
        "start_membership": {k: dict(v) for k, v in membership.items()},
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--time-first", action="store_true")
    args = parser.parse_args()
    t0 = time.perf_counter()
    result = collect(50 if args.time_first else None)
    if args.time_first:
        print(f"50 records from each of three run sets: {time.perf_counter()-t0:.4f} seconds")
    else:
        (HERE / "trace_controls.json").write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2))
