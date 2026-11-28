"""Check the full abstract census and classify the relabelling classes."""

import argparse
import itertools
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent


def pairs_in_cycle(cycle):
    return zip(cycle, cycle[1:] + cycle[:1])


def unordered(pair):
    return tuple(sorted(pair))


def cross_occurrences(cycles):
    occurrences = defaultdict(list)
    for i, cycle in enumerate(cycles):
        for u, v in pairs_in_cycle(cycle):
            occurrences[unordered((u, v))].append((i, u < v))
    return occurrences


def sign_of(cycles):
    total = 0
    for cycle in cycles:
        holders = {cycle[0], cycle[2]}
        order = sorted(cycle)
        total ^= (order[0] in holders) == (order[2] in holders)
    return int(total)


def balanced(occurrences, size):
    for flips in itertools.product((False, True), repeat=size - 1):
        flips = (False, *flips)
        if all(sum(forward ^ flips[i] for i, forward in group) * 2 == len(group)
               for group in occurrences.values()):
            return True
    return False


def check_minimal(occurrences, size):
    choice_set = set(range(size))
    for selected_size in range(1, size):
        for selected in itertools.combinations(choice_set, selected_size):
            assert any(sum(i in selected for i, _ in group) % 2
                       for group in occurrences.values())


def two_colourable(cross_pairs):
    return any(all((assignment >> u ^ assignment >> v) & 1 for u, v in cross_pairs)
               for assignment in range(1 << (1 + max(max(pair) for pair in cross_pairs))))


def separated_orders(cycles):
    """Relabel every local component, trying each choice of which keeps the old label."""
    local = defaultdict(lambda: defaultdict(set))
    for cycle in cycles:
        for i, knot in enumerate(cycle):
            prev, after = cycle[i - 1], cycle[(i + 1) % 4]
            local[knot][prev].add(after)
            local[knot][after].add(prev)
    next_label = max(local) + 1
    alternatives = []
    for knot, neighbors in sorted(local.items()):
        components = []
        remaining = set(neighbors)
        while remaining:
            todo = {min(remaining)}
            component = set()
            while todo:
                near = todo.pop()
                component.add(near)
                todo.update(neighbors[near] - component)
            components.append(component)
            remaining -= component
        labels = (knot, *range(next_label, next_label + len(components) - 1))
        next_label += len(components) - 1
        alternatives.append([
            {(knot, near): label for component, label in zip(components, perm) for near in component}
            for perm in itertools.permutations(labels)
        ])
    for assignments in itertools.product(*alternatives):
        rewrite = {key: value for assignment in assignments for key, value in assignment.items()}
        separated = []
        for cycle in cycles:
            next_cycle = []
            for i, knot in enumerate(cycle):
                prev, after = cycle[i - 1], cycle[(i + 1) % 4]
                assert rewrite[knot, prev] == rewrite[knot, after]
                next_cycle.append(rewrite[knot, after])
            separated.append(next_cycle)
        yield separated, rewrite, next_label


def holding_counts(cycles):
    return Counter(unordered((a, b)) for cycle in cycles
                   for a, b in [(cycle[0], cycle[2]), (cycle[1], cycle[3])])


def canonical(cycles, knots):
    cross = [list(pairs_in_cycle(cycle)) for cycle in cycles]
    return min(tuple(sorted(tuple(sorted(unordered((permutation[u], permutation[v])) for u, v in edges))
                            for edges in cross))
               for permutation in itertools.permutations(range(knots)))


def archived_comparison(census, nonorientable_even):
    archived = json.loads((HERE.parent / "abstract.json").read_text())
    tally_match = {
        row["knots"]: {tuple(key) for key in census[row["knots"]]["tally"]}
        == {tuple(key) for key in row["tally"]}
        for row in archived["rows"]
    }
    expected = {
        canonical(row["cycles"], row["knots"]): row
        for row in archived["non-orientable even classes"]
    }
    fields = {
        "labelled_copies": "labelled copies",
        "doubled_pairs": "doubled pairs",
        "original_two_colourable": "two-colourable",
        "orientable": "orientable",
        "sign": "sign",
        "pairs": "pairs",
        "knots": "knots",
    }
    for row in nonorientable_even:
        match = expected.pop(canonical(row["cycles"], row["knots"]))
        row["six_pair_kind"] = match["kind"]
        assert row["separated_euler_count"] == match["separated Euler count"]
        assert all(row[key] == match[old] for key, old in fields.items())
    assert not expected
    assert all(tally_match.values())
    return tally_match


def check_class(row):
    knots, cycles = row["knots"], row["cycles"]
    size = len(cycles)
    occurrences = cross_occurrences(cycles)
    assert sorted({knot for cycle in cycles for knot in cycle}) == list(range(knots))
    assert all(len(set(cycle)) == 4 for cycle in cycles)
    assert {len(group) for group in occurrences.values()} == {2}
    assert size == row["pairs"]
    original_sign = sign_of(cycles)
    same_order = sum(group[0][1] == group[1][1] for group in occurrences.values()) % 2
    assert original_sign == same_order == row["sign"]
    orientable = balanced(occurrences, size)
    assert orientable == row["orientable"]
    check_minimal(occurrences, size)
    assert two_colourable(occurrences) == row["original_two_colourable"]
    doubled = [pair for pair, count in holding_counts(cycles).items() if count > 1]
    assert len(doubled) == row["doubled_pairs"]
    separated_checks = 0
    for separated, rewrite, separated_knots in separated_orders(cycles):
        after = cross_occurrences(separated)
        cross_map = {unordered((rewrite[u, v], rewrite[v, u])) for u, v in occurrences}
        assert cross_map == after.keys() and len(after) == len(occurrences)
        assert {len(group) for group in after.values()} == {2}
        assert sign_of(separated) == original_sign
        assert balanced(after, size) == orientable
        assert two_colourable(after) == row["separated_two_colourable"]
        assert separated_knots == row["separated_knots"]
        separated_checks += 1
    row["separated_euler_count"] = row["separated_knots"] - size
    row["separation_labellings_checked"] = separated_checks
    row["doubled_pairs_of_knots"] = sorted(doubled)
    row["cross_pairs_of_knots"] = sorted(occurrences)
    return row


def check_higher_coverage_witness(row):
    cycles = row["cycles"]
    occurrences = cross_occurrences(cycles)
    assert all(len(group) % 2 == 0 for group in occurrences.values())
    assert max(map(len, occurrences.values())) == row["coverage"]
    assert not sign_of(cycles) and balanced(occurrences, len(cycles)) == row["orientable"]
    assert row["doubled_pairs"] == sum(count > 1 for count in holding_counts(cycles).values())
    check_minimal(occurrences, len(cycles))
    return row


def matchings(group):
    if not group:
        yield ()
        return
    for j in range(1, len(group)):
        for matches in matchings(group[1:j] + group[j + 1:]):
            yield ((group[0], group[j]), *matches)


def paired_separation(row):
    """Keep each paired occurrence group distinct, even if its endpoints coincide."""
    cycles = row["cycles"]
    occurrences = cross_occurrences(cycles)
    tally = Counter()
    for arrangement in itertools.product(*(matchings(group) for group in occurrences.values())):
        labels = {(i, knot): (i, knot) for i, cycle in enumerate(cycles) for knot in cycle}
        paired_cross_pairs = {}
        for (u, v), groups in zip(occurrences, arrangement):
            for group in groups:
                (i, _), (j, _) = group
                for endpoint in (u, v):
                    old, new = labels[j, endpoint], labels[i, endpoint]
                    for corner, label in labels.items():
                        if label == old:
                            labels[corner] = new
                paired_cross_pairs[len(paired_cross_pairs)] = group
        n_separated = len(set(labels.values()))
        euler = n_separated - len(paired_cross_pairs) + len(cycles)
        orientable = balanced(paired_cross_pairs, len(cycles))
        tally[(euler, orientable)] += 1
    return table(tally, ("separated_euler_count", "orientable_after_pairing", "pairing_count"))


def table(counts, columns):
    return [dict(zip(columns, (*key, count))) for key, count in sorted(counts.items())]


def check_repeated_cycles():
    orders = [(0, 1, 2, 3), (0, 1, 3, 2), (0, 2, 1, 3)]
    for cycle in orders:
        cycles = [cycle, cycle]
        occurrences = cross_occurrences(cycles)
        assert {len(group) for group in occurrences.values()} == {2}
        assert not sign_of(cycles) and balanced(occurrences, 2)
        check_minimal(occurrences, 2)
    return {"knots": 4, "pairs": 2, "labelled": len(orders), "classes": 1}


def run(raw):
    census = {}
    classes = []
    higher_coverage_witnesses = []
    for line in raw:
        row = json.loads(line)
        kind = row.pop("kind", None)
        if kind == "class":
            classes.append(check_class(row))
        elif kind == "higher_coverage_witness":
            higher_coverage_witnesses.append(check_higher_coverage_witness(row))
        else:
            census[row["knots"]] = row
    assert set(census) == {4, 5, 6, 7}
    for knots, row in census.items():
        labelled_count = sum(line[-1] for line in row["tally"])
        assert labelled_count == row["labels_in_orbits"]
        assert labelled_count == sum(c["labelled_copies"] for c in classes if c["knots"] == knots)
        assert not row["sign_disagreements"]
        row["labelled_structures"] = labelled_count
        row["classes"] = sum(c["knots"] == knots for c in classes)
        row["two_colourability_changes_after_separation"] = sum(
            line[-1] for line in row["separation"] if line[4] != line[5]
        )
    nonorientable_even = [row for row in classes if not row["orientable"] and not row["sign"]]
    assert all(row["pairs"] >= 6 for row in nonorientable_even)
    assert sum(row["pairs"] == 6 for row in nonorientable_even) == 3
    p1 = [row for row in nonorientable_even if row["knots"] <= 6 or row["pairs"] <= 6]
    assert len(p1) == 5
    assert all(row["doubled_pairs"] for row in p1)
    two_colourability_changes_by_class = sum(
        row["original_two_colourable"] != row["separated_two_colourable"] for row in classes
    )
    tally_match = archived_comparison(census, nonorientable_even)
    class_columns = ("knots", "pairs", "separated_euler_count", "orientable", "sign",
                     "original_two_colourable", "separated_two_colourable", "doubled_pairs",
                     "six_pair_kind")
    class_counts = Counter(
        tuple(row.get(name) if name != "six_pair_kind" else row.get(name) or "" for name in class_columns)
        for row in classes
    )
    control = next(row for row in higher_coverage_witnesses if row["orientable"])
    control["pairing_tally"] = paired_separation(control)
    assert {r["orientable_after_pairing"] for r in control["pairing_tally"]} == {True, False}
    return {
        "labelled_structure_count": sum(row["labelled_structures"] for row in census.values()),
        "class_count": len(classes),
        "nonorientable_even_class_count": len(nonorientable_even),
        "p1_class_count": len(p1),
        "classes_with_changed_two_colourability_after_separation": two_colourability_changes_by_class,
        "separation_labellings_checked": sum(row["separation_labellings_checked"] for row in classes),
        "repeated_cycles_outside_archived_count": check_repeated_cycles(),
        "labelled_tally_matches_archived": tally_match,
        "nonorientable_even_classes_match_archived": len(nonorientable_even),
        "labelled_tally_columns": ["knots", "pairs", "separated_euler_count", "orientable", "sign",
                                   "has_doubled_pair", "every_knot_on_doubled_pair",
                                   "original_two_colourable", "labelled_count"],
        "separation_tally_columns": ["pairs", "separated_knots", "orientable", "sign",
                                     "original_two_colourable", "separated_two_colourable",
                                     "doubled_pairs", "labelled_count"],
        "higher_coverage_tally_columns": ["pairs", "maximum_coverage", "orientable", "sign",
                                          "doubled_pairs", "labelled_count"],
        "class_tally_by_knots_and_pairs": table(Counter((row["knots"], row["pairs"]) for row in classes),
                                               ("knots", "pairs", "count")),
        "class_tally": table(class_counts, (*class_columns, "class_count")),
        "other_class_representatives": [row for row in classes if row["orientable"] or row["sign"]],
        "labelled_tallies": list(census.values()),
        "nonorientable_even_classes": nonorientable_even,
        "higher_coverage_witnesses": higher_coverage_witnesses,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("raw", type=Path)
    parser.add_argument("out", type=Path)
    args = parser.parse_args()
    with args.raw.open() as raw:
        result = run(raw)
    args.out.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
