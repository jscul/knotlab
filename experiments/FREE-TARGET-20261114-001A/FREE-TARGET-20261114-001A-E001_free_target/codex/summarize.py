"""Summarize a shared-runner output directory, keeping unrun keys separate."""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import json
import math
from pathlib import Path

import gates
import inputs


def wilson(successes, total=66):
    z = 1.959963984540054
    p = successes / total
    scale = 1 + z * z / total
    center = (p + z * z / (2 * total)) / scale
    half = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / scale
    return [max(0.0, center - half), min(1.0, center + half)]


def summarize(directory):
    directory = Path(directory).resolve()
    if not directory.is_relative_to(inputs.HERE):
        raise ValueError("the summary output must stay inside CODEX")
    population = inputs.load_population()
    records = gates.latest_records(directory)
    outside = set(records) - set(population["keys"])
    if outside:
        raise ValueError(f"runner has keys outside the frozen population: {sorted(outside)}")
    results = {key: row["result"] for key, row in records.items() if row["status"] == "ok"}
    counts = Counter(row["verdict"] for row in results.values())
    by_verdict = {name: dict(count=counts[name], denominator=66,
                             share=counts[name] / 66, wilson_95=wilson(counts[name]))
                  for name in ("grows", "bounded", "unresolved")}
    growers, bounded, unresolved = [], [], []
    for key, row in results.items():
        if row["verdict"] == "grows":
            r = row["r"]
            growers.append(dict(key=key, r=r, lambda_path=row["lambda_path"],
                                reciprocal_r=str(Fraction(1, r)),
                                L_path=row["L_path"]))
        elif row["verdict"] == "bounded":
            cert = row["bounded_certificate"]
            features = row.get("gate_b", {}).get("features", {})
            bounded.append(dict(key=key, k=cert.get("k"), onset=cert.get("onset"),
                                path=cert.get("path"),
                                carried=features.get("all_depths_use_carried_top"),
                                side=features.get("uses_side_member"),
                                carried_top_ports_on_path=cert.get("carried_top_ports"),
                                witnesses=cert.get("witnesses", []),
                                certificate=cert))
        else:
            unresolved.append(dict(key=key, reason=row.get("reason"),
                                   bounded_search=row.get("bounded_search"),
                                   limit_detail=row.get("limit_detail")))
    gate_result = gates.collect(directory)
    summary = dict(population_count=66, finished_cases=len(records),
                   successful_runner_cases=len(results), pending_cases=66 - len(records),
                   pending_keys=[key for key in population["keys"] if key not in records],
                   runner_statuses=dict(Counter(row["status"] for row in records.values())),
                   verdicts=by_verdict, r_against_lambda_path=growers,
                   bounded=bounded, unresolved=unresolved,
                   unresolved_by_reason=dict(Counter(row["reason"] for row in unresolved)),
                   gates=gate_result,
                   invalid=any(row.get("invalid", False) for row in results.values()) or
                           not gate_result["all_applicable_passed"],
                   seconds=sum(row.get("seconds", 0) for row in results.values()),
                   peak_case_memory_bytes=max((row.get("peak_memory_bytes", 0) for row in results.values()), default=0))
    (directory / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_directory", type=Path)
    args = parser.parse_args()
    result = summarize(args.run_directory)
    print(json.dumps({key: result[key] for key in ("population_count", "finished_cases", "pending_cases", "verdicts", "unresolved_by_reason", "invalid", "seconds", "peak_case_memory_bytes")}, sort_keys=True))
