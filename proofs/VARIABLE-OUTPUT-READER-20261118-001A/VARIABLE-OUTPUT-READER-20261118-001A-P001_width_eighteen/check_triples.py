"""Read the target's legal operand sets from scalar distances on the current bits."""

import json
from itertools import combinations, product
from random import Random

import check_reference as reference


def triples_by_distance(table):
    """This rule is specific to the target's complete distance-table class."""
    return {triple for triple in combinations(range(len(table)), 3)
            if sorted(table[a][b] for a, b in combinations(triple, 2)) == [6, 8, 8]}


def exchangeable_groups(table):
    """Group bits whose transposition leaves the entire observed table fixed."""
    remaining = set(range(len(table)))
    groups = []
    while remaining:
        first = min(remaining)
        group = {other for other in remaining
                 if all(table[first][j] == table[other][j] for j in range(len(table))
                        if j not in (first, other))}
        groups.append(tuple(sorted(group)))
        remaining -= group
    return groups


def menu_through_four(table):
    short = reference.pool(table, 4)
    groups = exchangeable_groups(short)
    multiple = [g for g in groups if len(g) > 1]
    assert sorted(map(len, multiple)) == [2, 2, 3]
    # The two other loose distinctions share a row histogram with the
    # outside pairs. Each is distinguishable from every other single bit.
    other = tuple(g[0] for g in groups if len(g) == 1 and short[g[0]].count(3) == 3
                  and short[g[0]].count(4) == 2 and 2 not in short[g[0]])
    assert len(other) == 2
    singles = {(bit,) for group in [*multiple, other] for bit in group}
    pairs = {tuple(sorted(pair)) for left, right in combinations(multiple, 2)
             for pair in product(left, right)}
    triples = {tuple(sorted(bits)) for bits in product(*multiple)}
    return singles | pairs | {tuple(sorted(other))} | triples


def change_names(group, mapping):
    return tuple(sorted(mapping[i] for i in group))


def run():
    rows, supports = reference.literal_relation(reference.TARGET)
    table, _ = reference.table_from_supports(supports, ignored=reference.WIDTH)
    menu = reference.named_menu(reference.TARGET)
    triples = {choice for choice in menu if len(choice) == 3}
    assert triples_by_distance(table) == triples
    assert menu_through_four(table) == menu

    names = list(range(len(table)))
    Random(831).shuffle(names)
    renamed = tuple(tuple(table[a][b] for b in names) for a in names)
    assert {change_names(t, names) for t in triples_by_distance(renamed)} == triples
    assert {change_names(t, names) for t in menu_through_four(renamed)} == menu

    # This permutation fixes all observations through three and violates the menu.
    swaps = ((0, 6), (2, 7), (4, 11), (5, 12), (8, 16), (10, 17))
    mapping = list(range(len(table)))
    for a, b in swaps:
        mapping[a], mapping[b] = mapping[b], mapping[a]
    differences = {}
    for cutoff in (3, 4):
        short = reference.pool(table, cutoff)
        differences[cutoff] = sum(short[i][j] != short[mapping[i]][mapping[j]]
                                  for i, j in combinations(range(len(table)), 2))
    good = (12, 13, 17)
    bad = change_names(good, mapping)
    assert good in triples and bad not in menu
    assert differences[3] == 0 and differences[4] > 0
    return {"all_old_triples_checked": len(tuple(combinations(range(len(table)), 3))),
            "legal_triples_with_pair_distances_6_8_8": sorted(triples),
            "nontrivial_exchangeable_groups_through_four": [
                g for g in exchangeable_groups(reference.pool(table, 4)) if len(g) > 1],
            "legal_choices_by_input_count": {n: sum(len(x) == n for x in menu) for n in (1, 2, 3)},
            "literal_rows": len(rows), "cutoff_three_witness": {
                "swaps": swaps, "legal_before": good, "illegal_after": bad,
                "changed_unordered_pairs_by_cutoff": differences}}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
