"""Exact reconstruction of the finite seeded two-reader sample."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import product
from random import Random


SETTINGS = tuple(product((0, 1), repeat=2))
PARTS = ("DD'", "DN'", "ND'", "NN'")


def sampled_models(trials, seed, impose_h5):
    rng = Random(seed)
    for draw in range(1, trials + 1):
        width = rng.choice((2, 3))
        old = [[rng.randrange(3) for _ in range(width)] for _ in range(width)]
        fresh = [
            [[tuple(rng.randrange(3) for _ in range(2)) for _ in range(width)] for _ in range(2)]
            for _ in range(2)
        ]
        totals = tuple(tuple(tuple(map(sum, setting)) for setting in reader) for reader in fresh)
        h5 = all(bool(first) == bool(second) for reader in totals for first, second in zip(*reader))
        # The imposed run discards failing draws before consuming the outcome bits.
        if impose_h5 and not h5:
            continue
        outcomes = [
            [[tuple(rng.randrange(2) for _ in range(2)) for _ in range(width)] for _ in range(2)]
            for _ in range(2)
        ]
        yield draw, old, fresh, totals, outcomes, h5


def setting_data(old, fresh, totals, outcomes):
    """Return each correlation numerator and the four finished weights in PARTS order."""
    signed = [
        [
            [sum(weight * (1 - 2 * bit) for weight, bit in zip(pair, bits))
             for pair, bits in zip(weights, reading)]
            for weights, reading in zip(reader_weights, reader_outcomes)
        ]
        for reader_weights, reader_outcomes in zip(fresh, outcomes)
    ]
    changing = [tuple(first != second for first, second in zip(*reader)) for reader in totals]
    entries = [
        (v, u, weight, PARTS.index(("D" if changing[0][v] else "N") +
                                  ("D'" if changing[1][u] else "N'")))
        for v, row in enumerate(old) for u, weight in enumerate(row) if weight
    ]
    old_parts = [0] * len(PARTS)
    for _, _, weight, part in entries:
        old_parts[part] += weight

    fixed_parts, correlators = [], []
    for a, b in SETTINGS:
        weights = [0] * len(PARTS)
        numerator = 0
        for v, u, weight, part in entries:
            weights[part] += weight * totals[0][a][v] * totals[1][b][u]
            numerator += weight * signed[0][a][v] * signed[1][b][u]
        denominator = sum(weights)
        if denominator == 0:
            return None
        fixed_parts.append(tuple(weights))
        correlators.append(Fraction(numerator, denominator))
    score = max(abs(sum(correlators) - 2 * special) for special in correlators)
    return score, tuple(old_parts), tuple(fixed_parts)


def policy_quiet(old, sender_totals, receiver_fresh):
    """Compare complete-record probability vectors by integer cross-products."""
    for receiver in receiver_fresh:
        baseline = None
        for policy in product(*zip(*sender_totals)):
            counts = tuple(
                sum(row[u] * count for row, count in zip(old, policy)) * fresh_weight
                for u, fresh_pair in enumerate(receiver) for fresh_weight in fresh_pair
            )
            total = sum(counts)
            if total == 0:
                continue
            if baseline is None:
                baseline = counts, total
                continue
            reference, reference_total = baseline
            if any(x * reference_total != y * total for x, y in zip(counts, reference)):
                return False
    return True


def quiet_both(old, fresh, totals):
    return policy_quiet(old, totals[0], fresh[1]) and policy_quiet(list(zip(*old)), totals[1], fresh[0])


def reported_flag(parts):
    dd, dn, nd, nn = parts
    return bool((dd + dn) and (dd + nd) and nn)


def record(stats, score, quiet, old_parts, fixed_parts):
    counts, maxima = stats
    counts["valid"] += 1
    combined = tuple(map(sum, zip(*fixed_parts)))
    flags = {
        "above_2": score > 2,
        "quiet_above_2": quiet and score > 2,
        "quiet": quiet,
        "quiet_reported_flag": quiet and reported_flag(old_parts),
        "quiet_positive_D_Dprime_NN": quiet and reported_flag(combined),
        "quiet_each_part_positive_somewhere": quiet and all(combined),
        "quiet_four_parts_same_pair": quiet and any(all(parts) for parts in fixed_parts),
        "quiet_four_parts_every_pair": quiet and all(all(parts) for parts in fixed_parts),
    }
    for label, flag in flags.items():
        counts[label] += flag
        if flag:
            maxima[label] = max(maxima.get(label, score), score)


def verify_controls():
    old = [[1, 1], [1, 1]]
    outcomes = [[[(0, 0), (0, 0)]] * 2] * 2
    first = [[(1, 0), (1, 0)], [(2, 0), (1, 0)]]
    for second_value in (0, 1):
        second = [[(1, 0), (second_value, 0)], [(2, 0), (second_value, 0)]]
        fresh = [first, second]
        totals = [[list(map(sum, setting)) for setting in reader] for reader in fresh]
        score, old_parts, fixed_parts = setting_data(old, fresh, totals, outcomes)
        assert reported_flag(old_parts) and quiet_both(old, fresh, totals) and score == 2
        assert all(all(parts) for parts in fixed_parts) == bool(second_value)
        print(f"Control {second_value} (quiet, H5, CHSH {score})")
        print(f"  mu={old}, t1={totals[0]}, t2={totals[1]}")
        print(f"  old weights={old_parts}, finished weights={fixed_parts}")


def run(trials, seed, impose_h5):
    grouped = defaultdict(lambda: (Counter(), {}))
    first_false_positive = None
    for draw, old, fresh, totals, outcomes, h5 in sampled_models(trials, seed, impose_h5):
        categories = ["all"] if impose_h5 else ["all", "H5 holds" if h5 else "H5 fails"]
        result = setting_data(old, fresh, totals, outcomes)
        for label in categories:
            grouped[label][0]["passed_filter"] += 1
        if result is None:
            continue
        score, old_parts, fixed_parts = result
        quiet = quiet_both(old, fresh, totals)
        for label in categories:
            record(grouped[label], score, quiet, old_parts, fixed_parts)
        if (first_false_positive is None and quiet and reported_flag(old_parts)
                and not all(map(sum, zip(*fixed_parts)))):
            first_false_positive = (draw, h5, score, old, totals, fixed_parts)

    print(f"\nSeed {seed}, {trials} draws, H5 {'imposed' if impose_h5 else 'filter disabled'}")
    for label, (counts, maxima) in grouped.items():
        print(f"  {label} | passed_filter={counts['passed_filter']}, valid={counts['valid']}")
        for metric in counts:
            if metric in {"passed_filter", "valid"}:
                continue
            print(f"    {metric}={counts[metric]}, max_CHSH={maxima.get(metric, '-')}")
    if first_false_positive:
        draw, h5, score, old, totals, fixed_parts = first_false_positive
        print(f"  First flagged draw with a missing finished part: {draw}, H5={h5}, CHSH={score}")
        print(f"    mu={old}, t1={totals[0]}, t2={totals[1]}, finished weights={fixed_parts}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=20_000)
    parser.add_argument("--seed", type=int, default=20_261_126)
    options = parser.parse_args()
    print(f"Part order: {PARTS}. Setting-pair order: {SETTINGS}.")
    verify_controls()
    for impose in (True, False):
        run(options.trials, options.seed, impose)
