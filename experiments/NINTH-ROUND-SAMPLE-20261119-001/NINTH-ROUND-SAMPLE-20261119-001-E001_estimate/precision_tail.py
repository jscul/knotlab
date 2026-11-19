"""Design-based lower-mean and upper-tail checks on named, complete BK streams."""

import argparse
import gzip
import hashlib
import json
import math
from decimal import Decimal, ROUND_CEILING
from pathlib import Path

from scipy.stats import beta


UNIFORM = range(20261119095, 20261119099)
RANKED = range(20261119100, 20261119104)
HELDOUT = 202611199795
HIGH = 1_479_137_034_240
MID = 200_620_800
STAGE = "049ad2aa85d55619a9e9c97dfd7ed33f6bb0d929d665af56f071b13f8fbd1102"


def read(path, expected_seed, count):
    digest = hashlib.sha256()
    weights = []
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rb") as stream:
        header = stream.readline()
        digest.update(header)
        attr = json.loads(header)
        assert attr["seed"] == expected_seed and attr["samples"] == count and attr["n"] == 28065
        for i, line in enumerate(stream):
            digest.update(line)
            row = json.loads(line)
            assert row["sample"] == i
            value = Decimal(row["weight"])
            assert value.is_finite() and value >= 0
            weights.append(value)
    assert len(weights) == count
    return weights, dict(seed=expected_seed, count=count, sha256=digest.hexdigest(),
                         mean=str(sum(weights) / count), parameters=attr)


def tail_order(n, rank, alpha):
    """Upper coverage on the strict survival probability at a sample order statistic."""
    return beta.isf(alpha, rank, n - rank + 1)


def binomial_upper(count, n, alpha):
    return 1.0 if count == n else beta.isf(alpha, count + 1, n - count)


def implications(lower, t, s, p_t, p_s, future_n=10_000):
    truncated_upper = s + (t - s) * p_s
    fraction = max(0.0, 1 - truncated_upper / lower)
    p_all_below = math.exp(future_n * math.log1p(-p_t))
    under = p_all_below * max(0.0, 1 - 10 * truncated_upper / (lower * (1 - p_t)))
    return dict(common_raw_mean_lower=lower, probability_above_high_upper=p_t,
                probability_above_mid_upper=p_s, truncated_raw_mean_upper=truncated_upper,
                mean_fraction_above_high_lower=fraction, future_independent_draws=future_n,
                probability_missing_tail_lower=p_all_below,
                probability_mean_below_one_tenth_lower=under)


def fixed_holdout(path, lower_record, parts_record):
    weights, info = read(path, HELDOUT, 100_000)
    parameters = info["parameters"]
    assert (parameters["pivot_limit"], parameters["exact_cutoff"], parameters["quotient_n"],
            parameters["rank_power"], parameters["local_order"], parameters["population_budget"],
            parameters["mass_power"], parameters["component_limit"]) == (64, 10, 25654, 0, 0, 0, 0, 0)
    hit_t, hit_s = (sum(w > threshold for w in weights) for threshold in (HIGH, MID))
    p_t = binomial_upper(hit_t, len(weights), .02)
    p_s = binomial_upper(hit_s, len(weights), .005)
    info.update(high=HIGH, mid=MID, high_strict_exceedances=hit_t, mid_strict_exceedances=hit_s,
                simultaneous_tail_confidence=.975, high_probability_upper=p_t, mid_probability_upper=p_s)
    separate = json.loads(lower_record.read_text())
    assert separate["blocks_sha256"] == STAGE
    assert separate["estimand"] == "All maximal cliques of the age-eight candidate graph"
    assert separate["seeds"] == list(range(202611199400, 202611199416))
    raw_limit = Decimal(str(separate["lower_limit_99pct"]))
    raw_integer_limit = int(raw_limit.to_integral_value(rounding=ROUND_CEILING))
    joint = implications(raw_integer_limit, HIGH, MID, p_t, p_s)
    parts = json.loads(parts_record.read_text())
    assert (parts["age"], parts["junctions"]) == (8, 28065)
    correction_upper = parts["residual_pairs_upper"] + parts["offshoots_upper"] - parts["held_maximal_blocks"]
    raw_threshold = (raw_integer_limit - 9 * correction_upper) / 10
    joint["birth_correction_upper"] = correction_upper
    joint["probability_exactly_corrected_mean_below_one_tenth_of_births_lower"] = (
        joint["probability_missing_tail_lower"]
        * max(0.0, 1 - joint["truncated_raw_mean_upper"] / ((1 - p_t) * raw_threshold))
    )
    joint.update(joint_confidence_at_least=.965, separate_lower_source=lower_record.name)
    return {"fixed_threshold_holdout": info, "heldout_tail_with_separately_frozen_lower": joint}


def run(folder, archive, lower_record, parts_record, heldout_only=False):
    assert hashlib.sha256((folder / "age8.txt").read_bytes()).hexdigest() == STAGE
    path = folder / f"precision_holdout_uniform_{HELDOUT}.jsonl"
    holdout = fixed_holdout(path if path.exists() else archive, lower_record, parts_record)
    if heldout_only:
        return dict(stage_sha256=STAGE, **holdout)
    decisions = []
    peaks = {}
    for method, seeds, n in (("uniform", UNIFORM, 100_000), ("rank", RANKED, 6000)):
        for seed in seeds:
            weights, info = read(folder / f"estimate_{method}_age8_{seed}.jsonl", seed, n)
            decisions.append(info)
            if method == "uniform":
                weights.sort(reverse=True)
                peaks[seed] = [int(weights[i]) for i in (0, 100)]
    assert peaks[20261119097] == [HIGH, MID]
    delta = .05 / 16
    max_mean = max(Decimal(row["mean"]) for row in decisions)
    lower = float(max_mean * Decimal("0.003125"))
    t_upper = tail_order(100_000, 1, delta)
    s_upper = tail_order(100_000, 101, delta)
    all_ranks_upper = tail_order(100_000, 101, delta * 2 / (101 * 102))
    report = dict(stage_sha256=STAGE, older_eight_streams=decisions,
                  thresholds_by_uniform_seed=peaks, selected_seed=20261119097,
                  exploratory_16_events=implications(lower, HIGH, MID, t_upper, s_upper),
                  exploratory_all_uniform_ranks=implications(lower, HIGH, MID, t_upper, all_ranks_upper))
    report.update(holdout)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    family = Path(__file__).resolve().parent
    artifacts = family.parents[2] / "artifacts" / family.parent.name / family.name
    parser.add_argument("--archive", type=Path, default=artifacts / "precision_holdout.jsonl.gz")
    parser.add_argument("--lower-record", type=Path, default=artifacts / "estimate_heldout.json")
    parser.add_argument("--parts", type=Path, default=artifacts / "parts8.json")
    parser.add_argument("--heldout-only", action="store_true",
                        help="Read the fixed confirmation without the older eight exploratory streams")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    report = run(args.folder, args.archive, args.lower_record, args.parts, args.heldout_only)
    if args.out:
        args.out.write_text(json.dumps(report, indent=2) + "\n")
    for name, result in report.items():
        if isinstance(result, dict) and "probability_mean_below_one_tenth_lower" in result:
            print(name, result)
