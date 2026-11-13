"""Describe the prescribed smoke run and compare its interrupted replay."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import statistics

from run_census import HERE, _atomic_json, build_draws, read_finished


def _stable(row):
    # Compare every requested non-timing field, plus worker assignment. Peak
    # RSS is an additional profiling extension, separate from scientific data.
    omit = {"total_wall_seconds", "peak_rss_mb", "wall_n", "level_wall_n"}
    return {k: v for k, v in row.items() if k not in omit}


def describe(baseline, resumed):
    rows = read_finished(baseline)
    replay = read_finished(resumed)
    mismatches = []
    for kid in sorted(set(rows) | set(replay)):
        if kid not in rows or kid not in replay:
            mismatches.append({"key_id": kid, "cause": "missing"})
        elif _stable(rows[kid]) != _stable(replay[kid]):
            a, b = _stable(rows[kid]), _stable(replay[kid])
            mismatches.append({"key_id": kid, "fields": [k for k in a.keys() | b.keys() if a.get(k) != b.get(k)]})
    resume = {"gate": "V-resume", "status": "passed" if not mismatches and len(rows) == 300 else "failed",
              "baseline_keys": len(rows), "replayed_keys": len(replay), "mismatches": mismatches,
              "ignored_execution_fields": sorted(set(next(iter(rows.values()), {})) - set(_stable(next(iter(rows.values()), {})))),
              "interruption": json.loads((HERE / "interruption.json").read_text()) if (HERE / "interruption.json").exists() else None}
    _atomic_json(HERE / "validation_parts" / "V-resume.json", resume)
    info = json.loads((Path(baseline) / "run_info.json").read_text())
    records = list(rows.values())
    totals = [r["total_wall_seconds"] for r in records]
    level_stats = []
    for i in range(12):
        values = [r["wall_n"][i] for r in records]
        full = [r["level_wall_n"][i] for r in records]
        level_stats.append({"n": i + 1, "mean_solver_wall_seconds": statistics.mean(values),
                            "max_solver_wall_seconds": max(values), "sum_solver_wall_seconds": sum(values),
                            "mean_level_wall_seconds": statistics.mean(full), "max_level_wall_seconds": max(full),
                            "undecided": sum(r["verdict_n"][i] is None for r in records)})
    draws, keys = build_draws()
    e_high = {d["key_id"] for d in draws if d["population"] == "E" and d["s"] == 3 and d["r"] >= 4}
    e_all = {d["key_id"] for d in draws if d["population"] == "E"}
    def group(kid):
        return "E_s3_r_ge4" if kid in e_high else "E_other" if kid in e_all else "W_only"
    populations = Counter(group(kid) for kid in keys)
    selection = json.loads((HERE / "prepared" / "smoke_keys.json").read_text())
    source_strata = {"E_s3_r_ge4": "E_s3_r_ge4", "E_other": "E_uniform", "W_only": "W_s_ge2"}
    samples = defaultdict(list)
    for label, source in source_strata.items():
        # Use the corresponding uniform stratum, not additional observations
        # from an overlapping source with a different inclusion probability.
        for kid in selection["strata"][source]:
            if group(kid) == label:
                samples[label].append(rows[kid]["total_wall_seconds"])
    groups = {}
    estimated_serial = 0.0
    for label, size in sorted(populations.items()):
        observed = samples[label]
        mean = statistics.mean(observed) if observed else None
        groups[label] = {"full_keys": size, "smoke_keys": len(observed), "mean_seconds": mean,
                         "max_seconds": max(observed) if observed else None}
        if mean is not None:
            estimated_serial += size * mean
    # This is a runtime extrapolation, not a confidence bound or run authorization.
    overhead_factor = info["elapsed_seconds"] / (sum(totals) / 4) if sum(totals) else None
    summary = {"keys": len(records), "workers": 4, "child_processes": 3,
               "elapsed_seconds": info["elapsed_seconds"],
               "mean_wall_seconds_per_key": statistics.mean(totals),
               "max_wall_seconds_per_key": max(totals), "sum_key_wall_seconds": sum(totals),
               "max_peak_rss_mb": max(r["peak_rss_mb"] for r in records),
               "fates": dict(Counter(r["fate"] for r in records)),
               "undecided_levels": sum(sum(v is None for v in r["verdict_n"]) for r in records),
               "undecided_keys": sum(any(v is None for v in r["verdict_n"]) for r in records),
               "returns": sum(r["return"] for r in records), "levels": level_stats,
               "full_run_projection": {"population_distinct_keys": len(keys), "poststrata": groups,
                   "estimated_serial_seconds": estimated_serial,
                   "ideal_8_worker_seconds": estimated_serial / 8,
                   "observed_4_worker_overhead_factor": overhead_factor,
                   "8_worker_seconds_using_observed_overhead": estimated_serial / 8 * overhead_factor if overhead_factor else None,
                   "estimator": "Poststratum means use only the corresponding uniform original selection stratum; overlapping-source observations are not pooled.",
                   "limitations": "Extrapolation from 300 deliberately stratified keys. Eight workers were not launched; contention, heavy solver tails, absent s=1 samples, and scaling overhead are unmeasured. The two unsampled s=1 keys are charged the W-only mean as part of this coarse runtime estimate."},
               "resume": resume}
    _atomic_json(HERE / "smoke_metrics.json", summary)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("baseline", type=Path)
    parser.add_argument("resumed", type=Path)
    args = parser.parse_args()
    result = describe(args.baseline, args.resumed)
    brief = {k: result[k] for k in ("keys", "elapsed_seconds", "fates", "undecided_levels")}
    brief["resume"] = {k: result["resume"][k] for k in ("status", "baseline_keys", "replayed_keys", "mismatches")}
    brief["projection_8_worker_seconds"] = result["full_run_projection"]["8_worker_seconds_using_observed_overhead"]
    print(json.dumps(brief, indent=2))


if __name__ == "__main__":
    main()
