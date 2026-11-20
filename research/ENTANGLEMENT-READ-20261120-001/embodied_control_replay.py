"""Replay the frozen two-register control by factoring its two four-knot groups."""

import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from math import lcm, prod
from pathlib import Path


BITS = (0, 1)
REGISTER_NAMES = ("X", "A0", "A1", "P", "Y", "B0", "B1")
REGISTER_WORDS = tuple(product(BITS, repeat=len(REGISTER_NAMES)))
CONTEXTS = tuple(product(BITS, repeat=2))
# The two terminal distinctions come first, followed by 02, 03, 12, 13, 23.
GROUP_SUPPORTS = ((0, 2, 3), (1, 4, 5), (2, 4, 6), (3, 5, 6))


def even(word):
    return sum(word) % 2 == 0


def not_all_equal(word):
    return 0 < sum(word) < len(word)


def group_counts(allowed):
    """Count the 32 possible internal assignments for each terminal pair."""
    counts = {}
    for terminals in CONTEXTS:
        count = 0
        for internal in product(BITS, repeat=5):
            values = terminals + internal
            if all(allowed(tuple(values[i] for i in support)) for support in GROUP_SUPPORTS):
                count += 1
        counts[terminals] = count
    return counts


def registers(allowed, terminal_counts):
    # Alice's X and P produce unary births that share their parent and have
    # next demand one. Bob's Y produces a unary birth with demand zero.
    # The ternary floor gives all three offshoots two fresh distinctions.
    fresh_counts = {bit: sum(allowed((bit, *pair)) for pair in CONTEXTS) for bit in BITS}
    start, extensions = [], []
    for x, a0, a1, p, y, b0, b1 in REGISTER_WORDS:
        count = 0
        if allowed((x, a0, a1, p)) and allowed((y, b0, b1)):
            count = terminal_counts[a0, b1] * terminal_counts[a1, b0]
        start.append(count)
        extensions.append(prod(fresh_counts[bit] for bit in (x, p, y)) if count else 0)
    return start, extensions


def histogram(weighted_rows, project):
    counts = Counter()
    total = 0
    for word, weight in weighted_rows:
        if weight:
            counts[project(word)] += weight
            total += weight
    return {cell: Fraction(weight, total) for cell, weight in counts.items()}


def tv(left, right):
    if not left or not right:
        return None
    return sum(abs(left.get(key, 0) - right.get(key, 0)) for key in left.keys() | right.keys()) / 2


def score(register_counts, protocol, endogenous):
    common = tuple(zip(REGISTER_WORDS, register_counts, strict=True))
    total = sum(register_counts)

    def respond(pair, setting):
        if protocol == "I":
            return pair[setting]
        return int(pair == (setting, setting))

    def four_marks(word):
        return word[1:3] + word[5:7]

    def six_marks(word):
        return word[:3] + word[4:]

    def potential_outputs(word):
        return tuple(respond(word[positions], setting)
                     for positions in (slice(1, 3), slice(5, 7)) for setting in BITS)

    joint_projections = {"four_marks": four_marks, "six_marks": six_marks,
                         "four_potential_outputs": potential_outputs}
    common_projections = {label: histogram(common, project) for label, project in joint_projections.items()}
    joint_tv = {label: [] for label in joint_projections}
    context_masses, settings, correlations, outcomes = [], [], [], []
    marginal_kinds = ("selected_bit", "marked_pair", "whole_bond")
    marginals = {side: {kind: [] for kind in marginal_kinds} for side in ("Alice", "Bob")}
    for x, y in CONTEXTS:
        rows = common
        if endogenous:
            rows = tuple((word, weight) for word, weight in common if (word[0], word[4]) == (x, y))
        mass = sum(weight for _, weight in rows)
        context_masses.append(mass)
        settings.append(Fraction(mass, total) if endogenous else Fraction(1, 4))
        outcome = histogram(rows, lambda word: (respond(word[1:3], x), respond(word[5:7], y)))
        outcomes.append([outcome.get(pair, Fraction(0)) for pair in CONTEXTS] if outcome else None)
        correlation = sum((-1) ** (a + b) * weight for (a, b), weight in outcome.items())
        correlations.append(correlation if outcome else None)
        for label, project in joint_projections.items():
            joint_tv[label].append(tv(histogram(rows, project), common_projections[label]))
        for side, pair, bond, setting in (("Alice", slice(1, 3), slice(0, 4), x),
                                          ("Bob", slice(5, 7), slice(4, 7), y)):
            marginals[side]["selected_bit"].append(histogram(rows, lambda word: respond(word[pair], setting)))
            marginals[side]["marked_pair"].append(histogram(rows, lambda word: word[pair]))
            marginals[side]["whole_bond"].append(histogram(rows, lambda word: word[bond]))

    signed, maximum = None, None
    if all(correlation is not None for correlation in correlations):
        signed = sum(correlations[:3]) - correlations[3]
        maximum = max(sum(s * e for s, e in zip(signs, correlations, strict=True))
                      for signs in product((-1, 1), repeat=4) if prod(signs) == -1)
    marginal_tv = {}
    for side, comparisons in (("Alice", ((0, 1), (2, 3))), ("Bob", ((0, 2), (1, 3)))):
        marginal_tv[side] = {kind: [tv(rows[i], rows[j]) for i, j in comparisons]
                             for kind, rows in marginals[side].items()}
    return {"context_mass_numerators": context_masses, "setting_probabilities": settings,
            "outcome_probabilities": outcomes, "correlations": correlations,
            "signed_S": signed, "max_eight_signs": maximum, "joint_tv_vs_common": joint_tv,
            "marginal_tv_by_own_setting": marginal_tv}


def replay():
    binary_pair_order = tuple(f"{a}{b}" for a, b in CONTEXTS)
    result = {"register_order": REGISTER_NAMES, "context_order": binary_pair_order, "output_order": binary_pair_order,
              "internal_assignments_per_terminal_pair": 32, "terminal_pair_counts": {}, "stages": {}}
    for law, allowed in (("parity", even), ("nae", not_all_equal)):
        terminal_counts = group_counts(allowed)
        result["terminal_pair_counts"][law] = [terminal_counts[terminals] for terminals in CONTEXTS]
        start, extensions = registers(allowed, terminal_counts)
        stages = {}
        result["stages"][law] = stages
        for stage in (0, 1):
            fibers = [extension if stage else 1 for extension in extensions]
            unit = [count * fiber for count, fiber in zip(start, fibers, strict=True)]
            lifted_divisor = lcm(*(fiber for fiber in fibers if fiber))
            lifted = [count * (lifted_divisor // fiber) if fiber else 0
                      for count, fiber in zip(unit, fibers, strict=True)]
            tilted = [count * (1 + word[1]) for count, word in zip(unit, REGISTER_WORDS, strict=True)]
            weights = {}
            stages[str(stage)] = {"allowed_assignments": sum(unit), "start_extension_counts": sorted(set(fibers) - {0}),
                                  "weights": weights}
            for label, counts, divisor in (("U", unit, 1), ("L", lifted, lifted_divisor), ("T", tilted, 1)):
                weights[label] = {"register_counts": counts, "assignment_mass_divisor": divisor,
                                  "protocols": {protocol: {arm: score(counts, protocol, arm == "endogenous")
                                                            for arm in ("external", "endogenous")}
                                                for protocol in ("I", "II")}}
    return result


def compare_reading(independent, upstream, label, independent_divisor, upstream_divisor):
    def require(actual, expected, field):
        if actual != expected:
            raise ValueError(f"Reading disagreement for {label}, {field}: {actual} != {expected}")

    for field, upstream_field in (("signed_S", "signed_S"), ("max_eight_signs", "max_CHSH")):
        require(str(independent[field]), upstream[upstream_field], field)
    require(list(map(str, independent["correlations"])), upstream["correlations"], "correlations")
    masses = upstream["context_masses"]
    require([Fraction(mass, independent_divisor) for mass in independent["context_mass_numerators"]],
            [Fraction(mass, upstream_divisor) for mass in masses], "exact context masses")
    output_probabilities = [[Fraction(count, mass) for count in counts]
                            for counts, mass in zip(upstream["output_counts"], masses, strict=True)]
    require(independent["outcome_probabilities"], output_probabilities, "outcomes")
    for kind, values in independent["joint_tv_vs_common"].items():
        require(list(map(str, values)), upstream[f"TV_{kind}_from_common"], f"{kind} joint TV")
    for side, kinds in independent["marginal_tv_by_own_setting"].items():
        for kind, values in kinds.items():
            upstream_kind = "selected" if kind == "selected_bit" else kind
            require(list(map(str, values)), upstream["marginal_TV_fixed_own"][side.lower()][upstream_kind],
                    f"{side} {kind} marginal TV")


def compare_receipt(replayed, path):
    data = path.read_bytes()
    primary = json.loads(data)
    for order in ("register_order", "context_order", "output_order"):
        if tuple(primary[order]) != replayed[order]:
            raise ValueError(f"Unexpected primary {order}")
    register_cells = reading_tables = 0
    for law, stages in replayed["stages"].items():
        for stage, record in stages.items():
            for weighting, independent in record["weights"].items():
                upstream = primary["stages"][law][stage]["weights"][weighting]
                upstream_divisor = upstream["assignment_mass_divisor"]
                independent_divisor = independent["assignment_mass_divisor"]
                if type(upstream_divisor) is not int or upstream_divisor <= 0:
                    raise ValueError(f"Invalid primary divisor for {law} {stage} {weighting}")
                pairs = zip(independent["register_counts"], upstream["register_counts"], strict=True)
                for i, (a, b) in enumerate(pairs):
                    if type(b) is not int or b < 0 or a * upstream_divisor != b * independent_divisor:
                        raise ValueError(f"Register mass disagreement for {law} {stage} {weighting}, word {i:07b}")
                    register_cells += 1
                for protocol, arms in independent["protocols"].items():
                    for arm, reading in arms.items():
                        compare_reading(reading, upstream["readings"][protocol][arm],
                                        f"{law} {stage} {weighting} {protocol} {arm}",
                                        independent_divisor, upstream_divisor)
                        reading_tables += 1
    return {"file": path.name, "sha256": sha256(data).hexdigest(), "exact_register_masses_matched": register_cells,
            "exact_reading_tables_matched": reading_tables}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compare", type=Path,
                        help="Compare exact register masses and readings with the primary receipt.")
    args = parser.parse_args()
    result = replay()
    if args.compare is not None:
        result["comparison"] = compare_receipt(result, args.compare)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
