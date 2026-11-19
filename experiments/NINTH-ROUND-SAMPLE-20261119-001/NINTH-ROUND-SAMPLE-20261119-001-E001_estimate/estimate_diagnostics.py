"""Summarize complete exploratory streams and the held-out precision diagnostic."""

import argparse
import hashlib
import json
import math
import re
import statistics
from collections import Counter
from pathlib import Path


def quantile(sorted_values, fraction):
    position = fraction * (len(sorted_values) - 1)
    index = int(position)
    right = min(index + 1, len(sorted_values) - 1)
    return sorted_values[index] + (position - index) * (sorted_values[right] - sorted_values[index])


def dispersion(values):
    ordered = sorted(values)
    lower, upper = (quantile(ordered, fraction) for fraction in (.025, .975))
    return {
        "replicates": len(values),
        "mean": statistics.fmean(values),
        "median": statistics.median(values),
        "standard_deviation": statistics.stdev(values) if len(values) > 1 else None,
        "observed_min": ordered[0],
        "observed_max": ordered[-1],
        "empirical_central_95pct": [lower, upper],
        "central_ratio": upper / lower if lower else None,
    }


def summarize(log):
    raw = log.read_bytes()
    config, *rows = map(json.loads, raw.splitlines())
    match = re.fullmatch(r"estimate_([a-z]+)_age([5-8])_([0-9]+)(?:_([01]))?.jsonl", log.name)
    if match is None:
        raise ValueError(f"bad stream name {log.name}")
    phase, age, _, pilot_shuffled = match.groups()
    seed = config["seed"]
    is_shuffled = pilot_shuffled == "1" or (phase == "uniform" and seed == 20261119096)
    config.setdefault("shuffled", int(is_shuffled))
    config.setdefault("quotient", int(seed != 20261119098))
    for field in ("rank_power", "local_order", "population_budget", "mass_power", "component_limit"):
        config.setdefault(field, 0)
    if len(rows) != max(1, config["samples"]):
        raise ValueError(f"incomplete stream {log.name}")
    if any(row["sample"] != i for i, row in enumerate(rows)):
        raise ValueError(f"out-of-order stream {log.name}")
    weights = [float(row["weight"]) for row in rows]
    total = math.fsum(weights)
    total_squares = math.fsum(weight * weight for weight in weights)
    is_population = bool(config["population_budget"])
    group_count = 20 if len(weights) >= 20 and not is_population else len(weights)
    group_size, remainder = divmod(len(weights), group_count)
    if remainder:
        raise ValueError(f"stream cannot divide into equal-sized groups {log.name}")
    replicate_means = [
        statistics.fmean(weights[i:i + group_size]) for i in range(0, len(weights), group_size)
    ]
    maximum = max(rows, key=lambda row: float(row["weight"]))
    return {
        "stream": log.name,
        "sha256": hashlib.sha256(raw).hexdigest(),
        "phase": phase,
        "age": int(age),
        "configuration": config,
        "replicate_kind": "population run" if is_population else "mean of independent paths",
        "replicate_group_size": group_size,
        "replicate_means": replicate_means,
        "run_dispersion": dispersion(replicate_means),
        "largest_raw_weight": maximum,
        "largest_raw_weight_share_of_sum": float(maximum["weight"]) / total if total else None,
        "effective_weight_count": total * total / total_squares if total_squares else None,
        "zero_weight_count": weights.count(0.0),
        "base_10_weight_bins": dict(sorted(Counter(
            math.floor(math.log10(weight)) for weight in weights if weight
        ).items())),
        "visited_states": sum(row["nodes"] for row in rows),
        "generated": sum(row.get("generated", 0) for row in rows),
        "retained": sum(row.get("retained", 0) for row in rows),
        "factored_components": sum(row.get("component_count", 0) for row in rows),
        "summed_seconds": math.fsum(row["seconds"] for row in rows),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pilot_logs", type=Path)
    parser.add_argument("heldout", type=Path)
    args = parser.parse_args()
    log_patterns = ("pilot", "uniform", "rank", "population", "wide", "factored")
    logs = [path for phase in log_patterns for path in sorted(args.pilot_logs.glob(f"estimate_{phase}_age*.jsonl"))]
    heldout = json.loads(args.heldout.read_text())
    print(json.dumps({
        "pilot_streams": [summarize(log) for log in logs],
        "heldout_empirical_dispersion": dispersion(
            [float(item["result"]["weight"]) for item in heldout["replicates"]]
        ),
    }, indent=2))


if __name__ == "__main__":
    main()
