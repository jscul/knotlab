"""Reweight the four-knot census for a specified, state-compatible growth rule."""

import argparse
import json
from fractions import Fraction
from itertools import combinations, permutations, product
from math import comb
from pathlib import Path


PORTS = "abcxyz"
READ_ROLES = "axby"
TRIPLES = list(combinations(PORTS, 3))


def passing_patterns(census):
    """Give every labeled pattern that works at the fixed ports its read convention."""
    passing = {}
    for orbit in census["orbits"]:
        roles = {row["ports"]: row["inverted"] for row in orbit["successful_roles"]}
        for labels in permutations(PORTS):
            forward = dict(zip(PORTS, labels))
            backward = dict(zip(labels, PORTS))
            source_ports = "".join(backward[name] for name in READ_ROLES)
            if source_ports not in roles:
                continue
            pattern = frozenset(
                tuple(sorted(forward[port] for port in rule)) for rule in orbit["rules"]
            )
            inverted = roles[source_ports]
            if pattern in passing and passing[pattern] != inverted:
                raise ValueError("A relabeling changed the same fixed-port reading")
            passing[pattern] = inverted
    if len(passing) != census["passing_fixed_roles"]:
        raise ValueError("Fixed-port patterns did not reproduce the census")
    return passing


def growth(census):
    passing = passing_patterns(census)
    seeds = [
        dict(zip(PORTS, bits)) for bits in product((0, 1), repeat=6)
        if bits[0] == 0 and bits[3] == 1
    ]
    probability = {False: Fraction(), True: Fraction()}
    per_seed = {}
    for seed in seeds:
        # Seed is held during assembly. Eligible knots stay eligible, so drawing
        # four in succession uniformly without replacement gives a uniform subset.
        eligible = [triple for triple in TRIPLES if len({seed[p] for p in triple}) == 2]
        total = comb(len(eligible), 4)
        counts = {False: 0, True: 0}
        for rules in combinations(eligible, 4):
            candidate = frozenset(rules)
            if candidate in passing:
                counts[passing[candidate]] += 1
        for inverted, count in counts.items():
            probability[inverted] += Fraction(count, total * len(seeds))
        per_seed["".join(str(seed[p]) for p in PORTS)] = {
            "final_patterns": total, "same_reading": counts[False], "inverted_reading": counts[True]
        }
    return {
        "roles": READ_ROLES, "fixed_neutral": {"a": 0, "x": 1},
        "seeds": per_seed,
        "labeled_same_reading": sum(not inverted for inverted in passing.values()),
        "labeled_inverted_reading": sum(passing.values()),
        "probability_same_reading": str(probability[False]),
        "probability_inverted_reading": str(probability[True]),
        "probability_either_reading": str(sum(probability.values())),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("census_result", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    raw = json.loads(args.census_result.read_text(encoding="utf-8"))
    encoded = json.dumps(growth(raw["census"]), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    else:
        print(encoded, end="")
