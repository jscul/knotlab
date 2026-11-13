"""Run a prefix of the frozen 1,000-family selection; never the full job."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import random
import statistics

from paths_dp import HERE, load_census_records, eligible_keys
from run_paths import run_tasks, dump, read_rows


def timings(rows):
    values = [r["seconds"] for r in rows if isinstance(r.get("seconds"), (int, float))]
    return {"families": len(rows), "timed_families": len(values), "total_seconds": sum(values),
            "mean_seconds": statistics.mean(values) if values else None,
            "median_seconds": statistics.median(values) if values else None,
            "max_seconds": max(values, default=None)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=3, choices=(1, 2, 3))
    parser.add_argument("--count", type=int, default=300)
    args = parser.parse_args()
    census = load_census_records()
    population = eligible_keys(census)
    frozen = random.Random(1113).sample(population, 1000)
    selection = {"seed": 1113, "population_families": len(population), "sample_size": 1000,
                 "population_sorted_keys_sha256": hashlib.sha256("\n".join(population).encode()).hexdigest(),
                 "keys": frozen}
    if not 1 <= args.count <= 1000:
        parser.error("count must be 1..1000")
    selected = frozen[:args.count]
    selection_path = HERE / "smoke_selection.json"
    if selection_path.exists():
        if json.loads(selection_path.read_text()) != selection:
            raise ValueError("Existing smoke sample differs; no overwrite or reselection")
    else:
        dump(selection_path, selection)
    summary_path = HERE / "smoke_summary.json"
    previous = json.loads(summary_path.read_text()) if summary_path.exists() else {}
    old_rows = read_rows(HERE / "smoke_families.jsonl", recover=True)
    if set(r["key"] for r in old_rows) - set(selected):
        raise ValueError("Existing smoke output contains keys outside the frozen sample")
    info = run_tasks(selected, HERE / "smoke_families.jsonl", workers=args.workers,
                     census_records=census, progress=True)
    rows = read_rows(HERE / "smoke_families.jsonl")
    if len(rows) != args.count or {r["key"] for r in rows} != set(selected):
        raise ValueError("Smoke completion does not match the requested frozen selection prefix")
    by_class, by_c = defaultdict(list), defaultdict(list)
    for row in rows:
        by_class[row["class"]].append(row)
        by_c[row["c"]].append(row)
    elapsed = sum(r.get("seconds") or 0 for r in rows)
    sessions = list(previous.get("sessions", []))
    if info.get("written") or not sessions:
        sessions.append(info)
    aggregate_peak = max((s.get("aggregate_peak_rss_bytes", 0) for s in sessions), default=0)
    interrupted_path = HERE / "smoke_attempt_1.json"
    interrupted = json.loads(interrupted_path.read_text()) if interrupted_path.exists() else None
    missing_times = sum(r.get("seconds") is None for r in rows)
    projection = elapsed / len(rows) * len(population) / 3
    summary = {"families": len(rows), "eligible_population_families": len(population), "seed": 1113,
        "timings": timings(rows),
        "timings_by_class": {name: timings(group) for name, group in sorted(by_class.items())},
        "timings_by_c": {str(c): timings(group) for c, group in sorted(by_c.items())},
        "class_counts": dict(sorted(Counter(row["class"] for row in rows).items())),
        "class_shares": {name: len(group) / len(rows) for name, group in sorted(by_class.items())},
        "sessions": sessions, "wall_seconds": sum(s.get("wall_seconds", 0) for s in sessions),
        "aggregate_peak_rss_bytes": None if interrupted else aggregate_peak,
        "maximum_observed_aggregate_peak_rss_bytes": aggregate_peak,
        "aggregate_peak_complete": interrupted is None,
        "interrupted_attempt": interrupted,
        "overall_wall_seconds_complete": interrupted is None,
        "overall_wall_seconds_known_lower_bound": sum(s.get("wall_seconds", 0) for s in sessions)
            + (interrupted.get("last_reported_runner_wall_seconds", 0) if interrupted else 0),
        "maximum_family_peak_rss_bytes": max((r.get("peak_rss_bytes") or 0 for r in rows), default=0),
        "projected_full_seconds_on_3_workers": None if missing_times else projection,
        "projection_scenarios_seconds_on_3_workers": {
            "unmeasured_family_times_set_to_zero": projection,
            "unmeasured_family_times_set_to_nominal_300_second_cap":
                (elapsed + missing_times * 300) / len(rows) * len(population) / 3},
        "projection_method": f"sample total per-family seconds / {len(rows)} * eligible population / 3; includes fixed-ray and uncarried diagnostics; excludes carry-only I/O and summary; missing times are not imputed in the point estimate",
        "projection_incomplete_timing_rows": missing_times,
        "selection_file": str(selection_path), "selection_prefix_size":args.count, "full_run_launched": False,
    }
    dump(summary_path, summary)
    # Class counts and shares stay in the file, as required.
    print(json.dumps({"smoke_families": len(rows), "wall_seconds": summary["wall_seconds"],
                      "aggregate_peak_rss_bytes": aggregate_peak,
                      "projected_full_seconds_on_3_workers": summary["projected_full_seconds_on_3_workers"],
                      "full_run_launched": False}), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
