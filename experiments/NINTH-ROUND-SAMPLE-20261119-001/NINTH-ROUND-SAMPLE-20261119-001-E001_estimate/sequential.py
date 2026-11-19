"""Repeat the prefix estimator with independent, named resampling streams.

The output counts all maximal candidate sets. Held maximal sets, leftover
pairs, isolated names and offshoots have their own deterministic accounting.
Per-panel quantiles are empirical dispersion of independent estimates; the
reported relative standard error is descriptive and uses their arithmetic mean.

Each prefix set has one primary child. A second child adds the new name to
the parent's subset in its neighborhood, provided that subset is maximal there
and has this parent as its greedy completion. This assigns every child once.
Systematic resampling preserves expected child weight. Multiplying the mass
ratios and the final residual mass gives an unbiased count for each fixed order.
"""

from argparse import ArgumentParser, ArgumentTypeError
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal, localcontext
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from time import perf_counter


MASTER_SEED = 20261119094


def seed(tag):
    encoded = f"{MASTER_SEED}:sequential:{tag}".encode()
    return int.from_bytes(sha256(encoded).digest()[:8], "little") >> 1


def panel(text):
    try:
        age, order, particles, replicates, trigger, label = text.split(",")
        result = (int(age), order, int(particles), int(replicates), int(trigger), label)
    except ValueError as error:
        raise ArgumentTypeError("expected age,order,particles,replicates,trigger,label") from error
    if result[0] not in (6, 7, 8) or result[2] < 0 or result[3] < 1 or result[4] < 1:
        raise ArgumentTypeError("invalid panel limits")
    return result


def dispersion(records):
    estimates = sorted(Decimal(row["estimate"]) for row in records)
    count = len(estimates)
    with localcontext() as context:
        context.prec = 30

        def percentile(p):
            idx = p * (count - 1)
            i = int(idx)
            f = idx - i
            return estimates[i] * (1 - f) + estimates[min(i + 1, count - 1)] * f

        mean = sum(estimates) / count
        lower = percentile(Decimal("0.025"))
        upper = percentile(Decimal("0.975"))
        relatives = [z / mean - 1 for z in estimates]
        rel_se = (sum(z*z for z in relatives) / (count*(count-1))).sqrt() if count > 1 else None
        mass_of_biggest = estimates[-1] / (mean * count)
        checkpoints = [row["checkpoint_prefix_unique_ancestors_maxfamily_mass"][-1] for row in records]
        return {
            "minimum": str(estimates[0]),
            "maximum": str(estimates[-1]),
            "mean": str(mean),
            "median": str(percentile(Decimal("0.5"))),
            "empirical_central_95_percent": [str(lower), str(upper)],
            "empirical_central_ratio": float(upper / lower),
            "relative_standard_error_of_mean": float(rel_se) if rel_se is not None else None,
            "largest_replicate_share_of_sum": float(mass_of_biggest),
            "final_distinct_ancestor_range": [min(r[2] for r in checkpoints), max(r[2] for r in checkpoints)],
            "final_largest_ancestor_mass_fraction_range": [
                min(r[3] / r[4] for r in checkpoints), max(r[3] / r[4] for r in checkpoints)
            ],
        }


def ancestry(records, metadata):
    if any(row["exact"] for row in records):
        return None
    prefixes = {(row["exact_prefix"], row["exact_count_at_prefix"]) for row in records}
    assert len(prefixes) == 1, "fixed-order replicates need the same exact prefix"
    prefix, count = prefixes.pop()
    initial_lower = metadata["particles"] * metadata["resample_mass_multiple"] + 1
    surviving_sum = sum(row["checkpoint_prefix_unique_ancestors_maxfamily_mass"][-1][2] for row in records)
    return {
        "last_exact_prefix": prefix,
        "maximal_sets_at_last_exact_prefix": count,
        "initial_ancestor_count_lower_bound": initial_lower,
        "final_ancestors_across_replicates_sum": surviving_sum,
        "upper_bound_on_fraction_of_initial_ancestors_with_any_final_representation":
            min(1, surviving_sum / initial_lower),
    }


def measure(binary, root, settings):
    age, order, particles, replicates, trigger, label = settings
    order_seed, resampling_seed = seed(f"order:{label}"), seed(f"resampling:{label}")
    source = root / f"age{age}.txt"
    args = (order, order_seed, particles, resampling_seed, replicates, 0, 1, trigger)
    start = perf_counter()
    proc = subprocess.run([binary, source, *map(str, args)], capture_output=True, check=True, text=True)
    metadata, *records = map(json.loads, proc.stdout.splitlines())
    assert len(records) == replicates and all(row["seed"] == resampling_seed + i for i, row in enumerate(records))
    return {
        "age": age,
        "label": label,
        "input_sha256": sha256(source.read_bytes()).hexdigest(),
        "engine": metadata,
        "elapsed_seconds": round(perf_counter() - start, 3),
        "replicates": records,
        "dispersion": dispersion(records),
        "ancestry": ancestry(records, metadata),
    }


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("binary", type=Path)
    parser.add_argument("rosters", type=Path)
    parser.add_argument("--panel", action="append", type=panel, required=True)
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    assert len({setting[-1] for setting in args.panel}) == len(args.panel)
    control = json.loads(subprocess.check_output([args.binary.resolve(), "--self-test"], text=True))
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        cases = [pool.submit(measure, args.binary.resolve(), args.rosters, setting) for setting in args.panel]
        result = [case.result() for case in cases]
    exact = {r["age"]: int(Decimal(r["replicates"][0]["estimate"])) for r in result
             if r["engine"]["particles"] == 0}
    for summary in result:
        age = summary["age"]
        if age in exact:
            summary["exact_calibration"] = exact[age]
            summary["mean_over_exact"] = float(Decimal(summary["dispersion"]["mean"]) / exact[age])
    print(json.dumps({
        "freeze": "7a1b4cc94",
        "master_seed": MASTER_SEED,
        "observable": "all maximal candidate sets, including held maximal sets and small sets",
        "exact_synthetic_controls": control,
        "panels": result,
    }, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
