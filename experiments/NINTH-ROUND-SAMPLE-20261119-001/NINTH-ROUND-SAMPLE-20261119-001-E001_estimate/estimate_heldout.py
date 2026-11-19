"""Run and summarize the frozen independent lower-limit batch."""

import argparse
import hashlib
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal, localcontext
from pathlib import Path
from time import monotonic


SEEDS = tuple(range(202611199400, 202611199416))
OPTIONS = ("32", "24", "1", "0", "1", "0", "512", "0.5", "8192")


def run(executable, blocks, seed):
    command = (str(executable), str(blocks), "1", str(seed), *OPTIONS)
    output = subprocess.run(command, check=True, capture_output=True, text=True)
    config, replicate = map(json.loads, output.stdout.splitlines())
    expected = (28065, 365, seed, 1, 32, 24, 1, 0, 1, 0, 512, 0.5, 8192)
    fields = ("n", "blocks", "seed", "samples", "pivot_limit", "exact_cutoff",
              "quotient", "shuffled", "rank_power", "local_order", "population_budget",
              "mass_power", "component_limit")
    if tuple(config[field] for field in fields) != expected:
        raise RuntimeError(f"unexpected run configuration for seed {seed}")
    weight = Decimal(replicate["weight"])
    if weight < 0 or not weight.is_finite() or replicate["sample"] != 0:
        raise RuntimeError(f"invalid replicate for seed {seed}")
    return {"configuration": config, "result": replicate}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("executable", type=Path)
    parser.add_argument("blocks", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    executable = args.executable.resolve()
    blocks = args.blocks.resolve()
    executable_hash = digest(executable)
    blocks_hash = digest(blocks)
    if args.output.exists():
        raise FileExistsError(args.output)
    start = monotonic()
    with ThreadPoolExecutor(max_workers=4) as pool:
        replicates = list(pool.map(lambda seed: run(executable, blocks, seed), SEEDS))
    if digest(executable) != executable_hash or digest(blocks) != blocks_hash:
        raise RuntimeError("a batch input changed")
    with localcontext() as context:
        context.prec = 50
        weights = [Decimal(item["result"]["weight"]) for item in replicates]
        groups = [weights[i:i + 4] for i in range(0, len(weights), 4)]
        group_means = [sum(group) / len(group) for group in groups]
        mean = sum(weights) / len(weights)
        group_product = Decimal(1)
        for value in group_means:
            group_product *= value
        lower_mean = Decimal("0.005") * mean
        lower_product = (Decimal("0.005") * group_product).sqrt().sqrt()
        report = {
            "estimand": "All maximal cliques of the age-eight candidate graph",
            "executable_sha256": executable_hash,
            "blocks_sha256": blocks_hash,
            "arguments_after_seed": OPTIONS,
            "seeds": SEEDS,
            "groups": [SEEDS[i:i + 4] for i in range(0, len(SEEDS), 4)],
            "estimate_sample_mean": str(mean),
            "min_replicate": str(min(weights)),
            "max_replicate": str(max(weights)),
            "max_over_min": str(max(weights) / min(weights)) if min(weights) else None,
            "largest_replicate_share_of_sum": str(max(weights) / sum(weights)) if sum(weights) else None,
            "replicate_standard_deviation": str((sum((w - mean) ** 2 for w in weights) / (len(weights) - 1)).sqrt()),
            "group_means": [str(value) for value in group_means],
            "lower_limit_from_mean": str(lower_mean),
            "lower_limit_from_group_product": str(lower_product),
            "lower_limit_99pct": str(max(lower_mean, lower_product)),
            "wall_seconds": monotonic() - start,
            "replicates": replicates,
        }
    with args.output.open("x") as file:
        json.dump(report, file, indent=2)
        file.write("\n")


if __name__ == "__main__":
    main()
