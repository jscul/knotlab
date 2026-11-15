#!/usr/bin/env python3
"""Compare raw truth tables, labelled preorders, closures and future pin answers."""

import argparse
import json
import random
from functools import cache
from itertools import combinations, product
from math import comb
from pathlib import Path


def require(test, message):
    if not test:
        raise ValueError(message)


def members(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def pin_menu(w):
    # Each question has the indices of its positive and negative pin, if present.
    if not w:
        return [(None, None)]
    return ([(i, None) for i in range(w)] + [(None, i) for i in range(w)]
            + [(i, j) for i in range(w) for j in range(w) if i != j])


def answers_mask(w, positive, negative):
    return sum(1 << x for x in range(1 << w)
               if (positive is None or x & (1 << positive))
               and (negative is None or not x & (1 << negative)))


def report(table, queries):
    return sum(1 << k for k, question in enumerate(queries) if table & question)


def literal_profiles(w):
    # Form the truth table of every possible conjunction by successive intersections.
    world = (1 << (1 << w)) - 1
    tables = {0, world}  # A direct source-to-sink implication realizes 0.
    for yes, no in pin_menu(w):
        literal = answers_mask(w, yes, no)
        if yes is not None and no is not None:
            literal = world ^ literal  # The clause forbids exactly x_yes=1, x_no=0.
        tables.update([old & literal for old in tables])
    return tables


@cache
def preorders(n):
    """Insert a new labelled name into every smaller reflexive transitive relation."""
    if not n:
        return ((),)
    new = 1 << (n - 1)
    result = []
    for rows in preorders(n - 1):
        lower = [p for p in range(new) if all(p & (1 << i) or not (row & p)
                                              for i, row in enumerate(rows))]
        upper = [s for s in range(new) if all(not s & (1 << i) or not (row & ~s)
                                              for i, row in enumerate(rows))]
        for p in lower:
            for s in upper:
                if all(not (s & ~rows[i]) for i in members(p)):
                    result.append(tuple(row | (new if p & (1 << i) else 0)
                                        for i, row in enumerate(rows)) + (new | s,))
    return tuple(result)


def lift(mask, labels):
    return sum(1 << labels[i] for i in members(mask))


def structural_profiles(w):
    # Canonical realization of a feasible table: true pins, false pins, neutral arcs.
    profiles = {0: None}
    for roles in product((0, 1, 2), repeat=w):
        positives = sum(1 << i for i, role in enumerate(roles) if role == 1)
        negatives = sum(1 << i for i, role in enumerate(roles) if role == 0)
        neutral = [i for i, role in enumerate(roles) if role == 2]
        expansions = [lift(x, neutral) for x in range(1 << len(neutral))]
        for order in preorders(len(neutral)):
            table = sum(1 << (positives | x) for u, x in enumerate(expansions)
                        if all(not (row & ~u) for i, row in enumerate(order) if u & (1 << i)))
            arcs = [0] * w
            for i, row in zip(neutral, order):
                arcs[i] = expansions[row]
            require(table not in profiles, "two distinct canonical profiles have the same truth table")
            profiles[table] = (positives, negatives, tuple(arcs))
    return profiles


def closed_tables(w):
    # Independent enumeration of arbitrary families of subsets, including empty.
    rows = range(1 << w)
    obligations = [((1 << a) | (1 << b), (1 << (a & b)) | (1 << (a | b)))
                   for a, b in combinations(rows, 2) if a & b != a and a & b != b]
    return {t for t in range(1 << len(rows))
            if all(t & given != given or t & needed == needed for given, needed in obligations)}


def joined_feasible(prefix, future):
    if prefix is None or future is None:
        return False
    p, n, a = prefix
    q, m, b = future
    forbidden = n | m
    reached = p | q
    pending = reached
    while pending:
        if reached & forbidden:
            return False
        todo = pending & -pending
        i = todo.bit_length() - 1
        fresh = (a[i] | b[i]) & ~reached
        pending = (pending ^ todo) | fresh
        reached |= fresh
    return True


def menu_checks(w, profiles):
    menu = pin_menu(w)
    tests = [answers_mask(w, p, n) for p, n in menu]
    reports = {table: report(table, tests) for table in profiles}
    require(len(set(reports.values())) == len(profiles), "pin reports failed to separate prefixes")
    classes = {}
    for k, (p, n) in enumerate(menu):
        world = (1 << (1 << w)) - 1
        if p is None and n is None:
            left, right = world, 0
            kind = "no_pins"
        elif n is None:
            top = (1 << w) - 1
            left, right = (1 << top) | (1 << (top ^ (1 << p))), 1 << (top ^ (1 << p))
            kind = "single_pin"
        elif p is None:
            left, right = 1 | (1 << (1 << n)), 1 << (1 << n)
            kind = "single_pin"
        else:
            left, right = world, world ^ tests[k]
            kind = "mixed_pair"
        require(left in profiles and right in profiles and (reports[left] ^ reports[right]) == 1 << k,
                "deleting a menu question did not produce its claimed indistinguishable prefixes")
        remaining = len({s & ~(1 << k) for s in reports.values()})
        require(remaining < len(reports), "an essential question was redundant")
        require(classes.setdefault(kind, remaining) == remaining, "renaming or complementing changed a count")
    if w:
        plus, minus = tests[0], tests[w]
        require(all(bool(t) == (bool(t & plus) or bool(t & minus)) for t in profiles),
                "the no-pin answer was not obtained from the two unary questions")
        require(all(not answers_mask(w, i, i) for i in range(w)), "opposite pins on one name agreed")
    return {"questions": len(menu), "separate_reports": len(reports),
            "verified_indispensable_questions": len(menu), "reports_after_one_deletion": classes}


def compatibility_checks(w, profiles):
    profiles = sorted(profiles.items())
    if w <= 4:
        pairs = product(profiles, repeat=2)
    else:
        rng = random.Random(1701)
        pairs = ((rng.choice(profiles), rng.choice(profiles)) for _ in range(8192))
    comparisons = disagreements = feasible = 0
    for (x, first), (y, second) in pairs:
        by_assignment = bool(x & y)
        disagreements += by_assignment != joined_feasible(first, second)
        feasible += by_assignment
        comparisons += 1
    require(not disagreements, "future feasibility under reachability differs from a shared assignment")
    return {"ordered_prefix_continuation_tests": comparisons, "compatible": feasible,
            "exhaustive": w <= 4}


def graph_profile(w, private, edges):
    source, sink = w + private, w + private + 1
    closure = [1 << i for i in range(sink + 1)]
    for i, j in edges:
        closure[i] |= 1 << j
    for k, row in enumerate(closure):
        for i in range(len(closure)):
            if closure[i] & (1 << k):
                closure[i] |= row
    if closure[source] & (1 << sink):
        return 0
    table = 0
    for x in range(1 << w):
        reached = closure[source]
        for i in members(x):
            reached |= closure[i]
        if not (reached & (1 << sink)) and reached & ((1 << w) - 1) == x:
            table |= 1 << x
    return table


def direct_projection(w, private, edges):
    source = w + private
    table = 0
    for x in range(1 << source):
        bits = x | (1 << source)
        if all(not bits & (1 << i) or bits & (1 << j) for i, j in edges):
            table |= 1 << (x & ((1 << w) - 1))
    return table


def hidden_checks():
    small = set()
    w, private = 2, 1
    source, sink = w + private, w + private + 1
    arcs = [(i, j) for i in range(source + 1) for j in (*range(source), sink) if i != j]
    for mask in range(1 << len(arcs)):
        edges = [arcs[i] for i in members(mask)]
        actual = direct_projection(w, private, edges)
        require(actual == graph_profile(w, private, edges), "exhaustive hidden-variable projection failed")
        small.add(actual)
    require(small == literal_profiles(w), "the hidden-vertex graphs missed a boundary profile")

    rng = random.Random(605421)
    w, private = 5, 3
    size = w + private + 2
    arcs_large = [(i, j) for i in range(size) for j in range(size) if i != j]
    count = 240
    several = set()
    for i in range(count):
        edges = rng.sample(arcs_large, (i % 5 + 1) * 3)
        table = direct_projection(w, private, edges)
        require(table == graph_profile(w, private, edges), "larger hidden-variable projection failed")
        several.add(table)
    return {"exhaustive_2_boundary_1_private_graphs": 1 << len(arcs),
            "distinct_small_tables": len(small), "sampled_5_boundary_3_private_graphs": count,
            "distinct_sampled_tables": len(several)}


def outside_family_control():
    # At width 1 every possible truth table is already an implication profile.
    require(literal_profiles(1) == set(range(4)), "width one omitted a Boolean relation")
    two = (1 << 4) - 1
    disjunction = two ^ 1
    tests = [answers_mask(2, p, n) for p, n in pin_menu(2)]
    require(disjunction not in literal_profiles(2) and report(two, tests) == report(disjunction, tests)
            and two & 1 and not (disjunction & 1), "smallest outside-family separation failed")
    w = 3
    world = (1 << (1 << w)) - 1
    even = sum(1 << x for x in range(1 << w) if x.bit_count() % 2 == 0)
    tests = [answers_mask(w, p, n) for p, n in pin_menu(w)]
    require(even not in literal_profiles(w) and report(even, tests) == report(world, tests),
            "even parity should evade the elementary tests outside the implication family")
    all_ones = 1 << ((1 << w) - 1)
    require(world & all_ones and not (even & all_ones), "pinning all three names failed to distinguish")
    return {"first_width": 2, "disjunction_vs_free": {"agreed_elementary_answers": len(pin_menu(2)),
            "all_zero_feasible": [False, True]}, "three_name_parity_vs_free": {
            "agreed_elementary_answers": len(tests), "states": [even.bit_count(), world.bit_count()],
            "all_ones_feasible": [False, True]}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit", action="store_true", help="print the reference data without comparing it")
    parser.add_argument("--expected", type=Path, default=Path(__file__).with_name("checks.json"))
    args = parser.parse_args()
    widths = {}
    for w in range(6):
        profiles = structural_profiles(w)
        require(profiles.keys() == literal_profiles(w), "preorders and literal conjunctions disagree")
        if w <= 4:
            require(profiles.keys() == closed_tables(w), "arbitrary union/intersection tables disagree")
        expected = 1 + sum(comb(w, n) * 2**(w - n) * len(preorders(n)) for n in range(w + 1))
        require(len(profiles) == expected, "the combinatorial count disagrees with the table identities")
        widths[str(w)] = {"profiles": len(profiles), "neutral_preorders": len(preorders(w)),
                          "arbitrary_truth_tables_exhausted": 1 << (1 << w) if w <= 4 else None,
                          "menu": menu_checks(w, profiles), "compatibility": compatibility_checks(w, profiles)}
    result = {"widths": widths, "hidden_variable_checks": hidden_checks(),
              "outside_family_control": outside_family_control()}
    if args.emit:
        print(json.dumps(result, indent=2))
    else:
        require(json.loads(args.expected.read_text()) == result, "reference data and recalculation disagree")
        print(json.dumps({"status": "passed", **result}, sort_keys=True))


if __name__ == "__main__":
    main()
