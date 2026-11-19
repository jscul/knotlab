"""Apply the fixed empirical spread rule and the independent-product confidence inequality."""

import argparse
from fractions import Fraction
import json
from math import prod
from pathlib import Path

from anneal_panel import distribution


def floor_root(q, exponent):
    lo, hi = 0, 1
    def admissible(x):
        return x ** exponent * q.denominator <= q.numerator
    while admissible(hi):
        lo, hi = hi, 2 * hi
    while hi - lo > 1:
        point = (lo + hi) // 2
        if admissible(point):
            lo = point
        else:
            hi = point
    return lo


def quantile(xs, p):
    z = p * (len(xs) - 1)
    i = int(z)
    return xs[i] + (z - i) * (xs[min(i + 1, len(xs) - 1)] - xs[i])


def main():
    parse = argparse.ArgumentParser(description=__doc__)
    parse.add_argument("artifact_directory", type=Path)
    parse.add_argument("correction_directory", type=Path)
    parse.add_argument("output", type=Path)
    args = parse.parse_args()
    residual_source = args.artifact_directory / "literal_residual03.json"
    exact = json.loads(residual_source.read_text())
    if not (exact["candidate_pairs"] - exact["covered_pairs"] ==
            exact["residual_count"] == len(exact["residual_pairs"]) == 1241):
        raise ValueError("inconsistent literal residual correction")
    results = {}
    c_means = {}
    for arm in ("primary", "sensitivity"):
        data = json.loads((args.artifact_directory / f"anneal_{arm}.json").read_text())
        correction = json.loads((args.correction_directory / f"anneal_residual_{arm}.json").read_text())
        cliques = [Fraction(*map(int, row["value"])) for row in data["exact_batch_means"]]
        residuals = [correction["easy_residual_pairs"] +
                     Fraction(hit * correction["nontrivial_candidate_pairs"], correction["samples_per_replicate"])
                     for hit in correction["hits"]]
        assert len(cliques) == len(residuals) == 24
        sampled_births = sorted(c + p + correction["raw_maximum_to_birth_term"] for c, p in zip(cliques, residuals))
        drift = correction["raw_maximum_to_birth_term"] + exact["residual_count"]
        births = sorted(c + drift for c in cliques)
        upper, lower = quantile(births, Fraction(39, 40)), quantile(births, Fraction(1, 40))
        c_means[arm] = sum(cliques) / len(cliques)
        results[arm] = dict(maximal_sets=data["batches"], individual_islands=data["islands"],
                            marked_counts=data["marked"], birth_summary=distribution(births), exact_birth_drift=drift,
                            residual_certificate=residual_source.name, sampled_birth_summary=distribution(sampled_births),
                            sampled_correction=correction,
                            span_lt_ten=bool(upper < 10 * lower))
        if arm == "primary":
            c_lower = floor_root(Fraction(prod(cliques), 100), len(cliques))
            results[arm].update(one_sided_99_percent_lower_C=c_lower, one_sided_99_percent_lower_J=c_lower+drift)
    results["primary_to_sensitivity_C_mean"] = float(c_means["primary"] / c_means["sensitivity"])
    with args.output.open("x") as stream:
        json.dump(results, stream, indent=2)
        stream.write("\n")
    for arm in ("primary", "sensitivity"):
        a = results[arm]
        print(arm, json.dumps(a["birth_summary"], separators=(",", ":")), "gate", a["span_lt_ten"])
    print("mean ratio", results["primary_to_sensitivity_C_mean"], "lower J", results["primary"]["one_sided_99_percent_lower_J"])


if __name__ == "__main__":
    main()
