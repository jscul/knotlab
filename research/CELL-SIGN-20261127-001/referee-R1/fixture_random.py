"""Rebuild the recorded random-pattern sample and score every nonempty commuting choice."""

import argparse
from collections import Counter
from itertools import combinations, product
import json
from random import Random

from pysat.card import CardEnc, EncType
from pysat.solvers import Solver

from fixture_audit import HERE, interleaving, order_parities
from fixture_audit import paired_reading, parity_balance, two_colourable, unordered, walk_data


def pattern(generator):
    knots = generator.randrange(4, 8)
    ends = [(generator.randrange(knot), knot) for knot in range(1, knots)]
    extra = generator.randint(knots, 2 * knots)
    ends.extend(tuple(sorted(generator.sample(range(knots), 2))) for _ in range(extra))
    return knots, ends


def opportunities(ends):
    terms = []
    for left, right in combinations(ends, 2):
        if len(set(left + right)) == 4:
            terms.append((left, right))
    return terms


def commuting_basis(terms, knot_count):
    check = {pair: 1 << index for index, pair in enumerate(combinations(range(knot_count), 2))}
    augmented = []
    candidate_bits = len(terms)
    stored = {}
    for j, (left, right) in enumerate(terms):
        column = sum(check[unordered(a, b)] for a, b in product(left, right))
        augmented.append((column << candidate_bits) | (1 << j))
    # Any elimination row with a zero check part represents a dependency.
    for column in augmented:
        while column >> candidate_bits:
            lead = column.bit_length()
            if lead not in stored:
                stored[lead] = column
                break
            column ^= stored[lead]
        else:
            yield column


def selected(mask, objects):
    while mask:
        first = mask & -mask
        yield objects[first.bit_length() - 1]
        mask ^= first


def orientable(incidence, orientability_methods):
    if not parity_balance(incidence.values()):
        orientability_methods["inconsistent necessary parity equations"] += 1
        return False
    if all(len(visits) == 2 for visits in incidence.values()):
        orientability_methods["solved by parity under twofold coverage"] += 1
        return True
    if all(sum(direction for _, _, direction in visits) * 2 == len(visits) for visits in incidence.values()):
        orientability_methods["as-listed directions already balance"] += 1
        return True
    top = 1 + max(index for visits in incidence.values() for index, _, _ in visits)
    equations = []
    for visits in incidence.values():
        variables = [-(index + 1) if direction else index + 1 for index, _, direction in visits]
        encoding = CardEnc.equals(lits=variables, bound=len(visits) // 2, top_id=top, encoding=EncType.seqcounter)
        equations.extend(encoding.clauses)
        top = max(top, encoding.nv)
    with Solver(name="g3", bootstrap_with=equations) as solver:
        orientability_methods["exact signed cardinality search"] += 1
        return solver.solve()


def orientation_control():
    # Three selected binary variables cannot each be opposite to both others.
    impossible = {
        (0, 1): [(0, 0, True), (1, 0, True)],
        (1, 2): [(0, 0, True), (2, 0, True)],
        (2, 3): [(1, 0, True), (2, 0, True)],
    }
    balanced = walk_data([(0, 1, 2, 3)] * 4)
    assert orientable(balanced, Counter()) and not orientable(impossible, Counter())


def main(limit):
    orientation_control()
    generator = Random(4040)
    order_generator = Random(50191)
    reasons = Counter()
    histogram = Counter()
    counts = Counter()
    euler_counts = Counter()
    separated_counts = Counter()
    largest_cover = Counter()
    methods = Counter()
    trial_count = 450
    checked = []
    for trial in range(trial_count if limit is None else limit):
        knot_count, ends = pattern(generator)
        knot_degrees = Counter(knot for pair in ends for knot in pair)
        if min(knot_degrees.values()) < 2:
            reasons["some knot holds fewer than two distinctions"] += 1
            continue
        terms = opportunities(ends)
        basis = list(commuting_basis(terms, knot_count))
        if len(basis) > 12:
            reasons["above twelve free choices"] += 1
            continue
        reasons["within the rank cap"] += 1
        histogram[len(basis)] += 1
        checked.append([trial, knot_count, len(ends), len(terms), len(basis), (1 << len(basis)) - 1])
        word = 0
        for i in range(1, 1 << len(basis)):
            word ^= basis[(i & -i).bit_length() - 1]
            chosen = list(selected(word, terms))
            cycles = [(a, c, b, d) for (a, b), (c, d) in chosen]
            visits = walk_data(cycles)
            assert all(len(values) % 2 == 0 for values in visits.values())
            sign = interleaving(chosen, range(knot_count))
            double = all(len(values) == 2 for values in visits.values())
            for _ in range(2):
                reverse_cycles = order_generator.getrandbits(len(cycles))
                reverse_references = order_generator.getrandbits(len(visits))
                order, same = order_parities(visits, reverse_cycles, reverse_references)
                assert order == sign and (not double or same == sign)
            # Match the archived sample's generator state between patterns.
            # Each order check consumed one coin per cycle and per distinct
            # cross pair regardless of the visit order and coin values.
            for _ in range(2 * (len(cycles) + len(visits))):
                generator.random()
            two_colour = two_colourable(visits)
            weak = parity_balance(visits.values())
            exact = orientable(visits, methods)
            assert not sign or not (weak or exact or two_colour)
            counts["choices"] += 1
            counts["theorem holds"] += 1
            counts["exactly two"] += double
            counts["orientable"] += exact
            counts["weak even condition"] += weak
            counts["two-colourable"] += two_colour
            active = len({knot for pair in visits for knot in pair})
            euler_counts[active - len(visits) + len(cycles)] += 1
            largest_cover[max(map(len, visits.values()))] += 1
            if double:
                reading = paired_reading(cycles, list(visits.values()))
                assert reading["sign"] == sign and reading["orientable"] == exact
                counts["one cycle at every knot"] += reading["pinched knots"] == 0
                separated_counts[reading["Euler count"]] += 1
    results = dict(counts)
    results.update({
        "Euler counts": dict(euler_counts),
        "separated Euler counts": dict(separated_counts),
        "most at a cross pair": dict(largest_cover),
    })
    if limit is not None:
        print(json.dumps({"pilot trial count": limit, "counts": counts, "orientability methods": methods}))
        return
    archive = json.loads((HERE.parent / "summary.json").read_text())["random patterns (theorem gate)"]
    results = json.loads(json.dumps(results))
    differences = {key: [results.get(key), archive.get(key)] for key in results.keys() | archive.keys()
                   if results.get(key) != archive.get(key)}
    data = {
        "weighting": "One per nonempty commuting choice at each seed-4040 pattern passing the two filters.",
        "bounds": "450 generated trials, 4–7 knots, at least two distinctions at each knot, at most 12 free choices.",
        "order checks": "Two independently seeded order settings per choice. The pattern generator advances by the archived check's coin count.",
        "trial disposition": reasons,
        "free-choice histogram": histogram,
        "accepted trials with index, knots, distinctions, eligible pairs, free choices, choices": checked,
        "results": results,
        "exact orientation methods": methods,
        "differences from archived random-pattern metrics": differences,
    }
    (HERE / "fixture_random.json").write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"trial disposition": reasons, "choices": counts["choices"], "orientability methods": methods,
                      "differences": differences}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, help="Run a pilot on this prefix of trials without writing evidence.")
    main(parser.parse_args().limit)
