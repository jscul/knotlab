"""Replay the small sharing-pattern and exact change-answer controls."""

import argparse
from collections import Counter
from functools import cache
from itertools import combinations, product
import json
from random import Random
from time import process_time

import networkx as nx

from growth_readings import ARCHIVE, HERE, INPUT, grow, holdings, reconstruct_draws


def adjacency(n, links):
    result = [0] * n
    for a, b in links:
        result[a] |= 1 << b
        result[b] |= 1 << a
    return tuple(result)


def members(bits):
    while bits:
        first = bits & -bits
        yield first.bit_length() - 1
        bits ^= first


def contract(rows, a, b):
    below = (1 << b) - 1
    result = []
    for knot, older in enumerate(rows):
        if knot != b:
            if knot == a:
                older = (older | rows[b]) & ~(1 << a)
            elif older & (1 << b):
                older |= 1 << a
            result.append((older & below) | ((older >> (b + 1)) << b))
    return tuple(result)


@cache
def contains_forbidden_minor(rows):
    """Find either excluded classical subgraph after zero or more contractions."""
    n = len(rows)
    if n < 5 or sum(row.bit_count() for row in rows) < 18:
        return False
    # Target minima are at least three. A degree-two intermediate can
    # be suppressed without losing a possible subdivision.
    for i, row in enumerate(rows):
        if row.bit_count() <= 2:
            neighbors = list(members(row))
            if neighbors:
                return contains_forbidden_minor(contract(rows, *sorted((i, neighbors[0]))))
            below = (1 << i) - 1
            return contains_forbidden_minor(tuple(
                (other & below) | ((other >> (i + 1)) << i)
                for j, other in enumerate(rows) if j != i
            ))
    for group in combinations((i for i, row in enumerate(rows) if row.bit_count() >= 4), 5):
        if all(rows[a] & (1 << b) for a, b in combinations(group, 2)):
            return True
    for a, b, c in combinations(range(n), 3):
        if ((rows[a] & rows[b] & rows[c]) & ~((1 << a) | (1 << b) | (1 << c))).bit_count() >= 3:
            return True
    if n <= 5:
        return False
    return any(
        contains_forbidden_minor(contract(rows, a, b))
        for a, row in enumerate(rows)
        for b in members(row)
        if a < b
    )


def controls(pilot):
    stored_file = next((ARCHIVE / "FOUR-READINGS-20261120-001A").glob("*/census.json"))
    stored = json.loads(stored_file.read_text())
    if pilot:
        stored = [row for i, row in enumerate(stored) if i % 7 == 0]
    counts = Counter()
    for row in stored:
        found = contains_forbidden_minor(adjacency(row["n"], row["sharing"]))
        assert found == row["operator"], row["atlas"]
        counts["patterns"] += 1
        counts["nonplanar_equals_admitting"] += found
        counts["planar_equals_not_admitting"] += not found
        counts["with_at_most_six_knots"] += row["n"] <= 6
    simple = Counter()
    for index, graph in enumerate(nx.graph_atlas_g()):
        if len(graph) == 0 or (pilot and index % 19 != 0):
            continue
        n = len(graph)
        found = contains_forbidden_minor(adjacency(n, graph.edges))
        # Compare the independent contraction decision with a direct
        # planarity call on the full incidence graph.
        incidence = nx.Graph()
        incidence.add_nodes_from(range(n))
        incidence.add_edges_from(
            (knot, n + distinction)
            for distinction, pair in enumerate(graph.edges)
            for knot in pair
        )
        assert found == (not nx.check_planarity(incidence)[0]), index
        simple[f"{n}_knots"] += 1
        simple["nonplanar"] += found
    multi_holder = Counter()
    rng = Random(20261123)
    panels = []
    while len(panels) < (12 if pilot else 60):
        n = rng.randint(3, 6)
        m = rng.randint(3, 4)
        groups = [sorted(rng.sample(range(n), rng.randint(2, min(n, 5)))) for _ in range(m)]
        if any(len(group) > 2 for group in groups):
            panels.append((n, groups))
    panels.append((3, [[0, 1, 2]] * 3))
    for n, groups in panels:
        links = [(knot, n + d) for d, group in enumerate(groups) for knot in group]
        found = contains_forbidden_minor(adjacency(n + len(groups), links))
        incidence = nx.Graph()
        incidence.add_nodes_from(range(n + len(groups)))
        incidence.add_edges_from(links)
        assert found == (not nx.check_planarity(incidence)[0]), (n, groups)
        multi_holder["patterns"] += 1
        multi_holder["nonplanar"] += found
    return {"recorded": counts, "simple_atlas": simple, "multi_holder": multi_holder}


def typed_incidence(rows):
    graph = nx.Graph()
    graph.add_nodes_from((("knot", k) for k in range(len(rows))), kind="knot")
    owners = holdings(rows)
    graph.add_nodes_from((("distinction", d) for d in owners), kind="distinction")
    graph.add_edges_from(
        (("knot", k), ("distinction", d)) for d, knots in owners.items() for k in knots
    )
    return graph


def select_fresh():
    selected = []
    for label, (initial, _, _, _) in reconstruct_draws():
        rows, ends, _, outcome = grow(initial, "parity", 12, 5000)
        if outcome != "closed":
            continue
        owners = holdings(rows)
        if len(owners) > 14 or any(len(part) != 2 for part in owners.values()):
            continue
        graph = typed_incidence(rows)
        assert nx.is_connected(graph)
        if any(nx.is_isomorphic(graph, old, node_match=lambda a, b: a["kind"] == b["kind"])
               for _, _, _, old in selected):
            continue
        selected.append((*label, len(ends) - 1, graph))
        yield (*label, len(ends) - 1), rows
        if len(selected) == 3:
            return
    raise AssertionError("Fewer than three qualifying parts")


def exact_answers(rows):
    names = sorted(holdings(rows))
    bit = {distinction: 1 << i for i, distinction in enumerate(names)}
    masks = [sum(bit[d] for d in knot) for knot in rows]
    answers = 1 << len(names)
    allowed = [
        word for word in range(answers)
        if all((word & mask).bit_count() % 2 == 0 for mask in masks)
    ]
    # Every ordered allowed pair contributes exactly once to its change
    # mask. Invert the defined moments directly as a signed integer sum.
    pair_counts = Counter(a ^ b for a, b in product(allowed, repeat=2))
    knot_word_counts = Counter()
    owner_masks = [sum(1 << k for k in group) for _, group in sorted(holdings(rows).items())]
    for subset in range(1 << len(rows)):
        answer = sum(1 << i for i, group in enumerate(owner_masks) if (subset & group).bit_count() % 2)
        knot_word_counts[answer] += 1

    inverse_denom = answers * len(allowed)
    draw_denom = 1 << len(rows)
    numerator_support = 0
    max_difference = 0
    for answer in range(answers):
        numerator = sum(
            -count if (answer & mask).bit_count() % 2 else count for mask, count in pair_counts.items()
        )
        numerator_support += numerator != 0
        cross_difference = abs(numerator * draw_denom - knot_word_counts[answer] * inverse_denom)
        max_difference = max(max_difference, cross_difference)
    return {
        "knots": len(rows), "distinctions": len(names), "allowed_words": len(allowed),
        "answer_words": answers, "support_of_counted": numerator_support,
        "largest_difference": "0" if not max_difference else f"{max_difference}/{inverse_denom * draw_denom}",
        "agree": max_difference == 0,
    }


def answer_controls(pilot):
    examples = {
        "five_knot_closure": [(1, 6, 7, 8), (2, 3, 4, 8), (0, 3, 6, 9), (4, 5, 7, 9), (0, 1, 2, 5)],
        "two_split_three_place_knots": [(0, 1, 2), (0, 1, 3)],
    }
    old_gates = json.loads((INPUT / "gates.json").read_text())["G4_first_two"]
    old_fresh = json.loads((INPUT / "knotside.json").read_text())["structures"]
    output = {}
    for label, rows in examples.items():
        result = exact_answers(rows)
        assert all(value == old_gates[label][field] for field, value in result.items()), label
        output[label] = result
    for ((arm, draw, t), rows), old in zip(select_fresh(), old_fresh, strict=True):
        assert (arm, draw, t) == (old["arm"], old["draw"], old["t"])
        if pilot and old["distinctions"] != 14:
            continue
        result = exact_answers(rows)
        assert all(value == old[field] for field, value in result.items()), (arm, draw, t)
        label = f"fresh_arm_{arm}_draw_{draw}_step_{t}"
        output[label] = result
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    started = process_time()
    sharing = controls(args.pilot)
    after_sharing = process_time()
    answers = answer_controls(args.pilot)
    result = {
        "sharing": sharing, "answer_tables": answers,
        "answer_words_checked": sum(row["answer_words"] for row in answers.values()),
        "cpu_s": {"sharing": after_sharing - started, "answer": process_time() - after_sharing},
    }
    filename = "gate_checks_pilot.json" if args.pilot else "gate_checks_full.json"
    (HERE / filename).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
