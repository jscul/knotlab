"""Audit the width-18 target against a reverse enumeration of legal histories.

No producer checker is imported. The target and the shortlisted candidates
are read from literal allowed states. A cheap filter measures only bond
distances 2 and 3 using junction subsets and incidence.

The junction graph stays connected and bipartite because every new junction
uses parents on one side. Each shared distinction belongs to two junctions;
every other distinction is loose. This makes the graph and its loose counts
a complete description up to names. Reverse deletion checks reachability.
"""

import json
from collections import Counter
from functools import cache
from itertools import combinations, combinations_with_replacement, permutations, product


WIDTH = 18
TARGET = (
    (0, 1, 2),
    (0, 3, 4, 5),
    (1, 6, 7),
    (2, 8, 9, 10),
    (3, 6, 11, 12),
    (4, 8, 13, 14, 15),
    (7, 9, 16, 17),
)


def bits(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def mask_of(indices):
    return sum(1 << index for index in indices)


def parents_agree(parents, neighbors, earlier):
    reachable = [neighbors[parent] & earlier for parent in parents]
    return (all(first & second for first, second in combinations(reachable, 2))
            and (len(reachable) < 3 or not (reachable[0] & reachable[1] & reachable[2])))


def named_menu(checks):
    owners = [tuple(i for i, check in enumerate(checks) if name in check)
              for name in range(WIDTH)]
    assert all(1 <= len(parents) <= 2 for parents in owners)
    held = [set() for _ in checks]
    for parents in owners:
        if len(parents) == 2:
            left, right = parents
            held[left].add(right)
            held[right].add(left)
    neighbors = tuple(mask_of(partners) for partners in held)
    loose = [name for name, parents in enumerate(owners) if len(parents) == 1]
    menu = set()
    for size in (1, 2, 3):
        for use in combinations(loose, size):
            parents = tuple(owners[name][0] for name in use)
            if len(set(parents)) == size and parents_agree(parents, neighbors, (1 << len(checks)) - 1):
                menu.add(use)
    return menu


def literal_relation(checks):
    equations = tuple(mask_of(check) for check in checks)
    values = [int(not any((row & eq).bit_count() % 2 for eq in equations))
              for row in range(1 << WIDTH)]
    allowed = frozenset(row for row, accepts in enumerate(values) if accepts)
    assert len(allowed) == (1 << (WIDTH - len(checks)))

    # The Walsh coefficient at a mask sums its parity character over the
    # allowed rows. It equals their count precisely for identically even masks.
    stride = 1
    while stride < len(values):
        for block in range(0, len(values), 2 * stride):
            for i in range(block, block + stride):
                left, right = values[i], values[i + stride]
                values[i], values[i + stride] = left + right, left - right
        stride *= 2
    supports = [i for i, coefficient in enumerate(values) if i and coefficient == len(allowed)]
    return allowed, supports


def table_from_supports(supports, ignored):
    table = [[0 if i == j else ignored for j in range(WIDTH)] for i in range(WIDTH)]
    bonds = []
    for support in sorted(supports, key=int.bit_count):
        if any(prior & support == prior for prior in bonds):
            continue
        bonds.append(support)
        distance = support.bit_count() - 1
        assert distance >= 2
        for i, j in combinations(bits(support), 2):
            if distance < table[i][j]:
                table[i][j] = table[j][i] = distance
    return tuple(tuple(row) for row in table), bonds


def direct_bond_check(rows, bonds):
    for support in bonds:
        width = support.bit_count()
        assert 0 < len({row & support for row in rows}) < 1 << width
        for name in bits(support):
            erased = support ^ (1 << name)
            assert len({row & erased for row in rows}) == 1 << (width - 1)


def pool(table, cutoff):
    return tuple(tuple(min(value, cutoff + 1) for value in row) for row in table)


def profile(table):
    return sorted(tuple(sorted(row)) for row in table)


def histogram(table):
    return Counter(table[i][j] for i, j in combinations(range(WIDTH), 2))


def isometries(first, second):
    profiles = [tuple(sorted(row)) for row in second]
    domains = [tuple(i for i, current in enumerate(profiles) if current == tuple(sorted(row)))
               for row in first]
    labels = sorted(range(WIDTH), key=lambda i: len(domains[i]))
    assigned = {}
    used = set()

    def extend(offset):
        if offset == WIDTH:
            yield tuple(assigned[i] for i in range(WIDTH))
            return
        source = labels[offset]
        for name in domains[source]:
            if name in used or any(first[source][prior] != second[name][target]
                                   for prior, target in assigned.items()):
                continue
            assigned[source] = name
            used.add(name)
            yield from extend(offset + 1)
            used.remove(name)
            del assigned[source]

    yield from extend(0)


def image(groups, mapping):
    return {tuple(sorted(mapping[name] for name in group)) for group in groups}


def transport_rows(rows, mapping):
    tables = tuple(1 << name for name in mapping)
    return {sum(tables[i] for i in bits(row)) for row in rows}


@cache
def row_permutations(count):
    return tuple((order, tuple(mask_of(j for j, old in enumerate(order) if word & (1 << old))
                               for word in range(1 << count)))
                 for order in permutations(range(count)))


def transpose(columns, row_count):
    return tuple(mask_of(j for j, column in enumerate(columns) if column & (1 << i))
                 for i in range(row_count))


def frames(columns, row_count):
    row_ids = tuple(range(row_count))
    column_ids = tuple(range(row_count, row_count + len(columns)))
    orientations = [(columns, row_ids, column_ids)]
    if row_count == len(columns):
        orientations.append((transpose(columns, row_count), column_ids, row_ids))
    for incidence, rows, labels in orientations:
        for order, relabel in row_permutations(row_count):
            moved = tuple((relabel[entry], label) for entry, label in zip(incidence, labels))
            ordered = tuple(sorted(value for value, _ in moved))
            yield ordered, tuple(rows[i] for i in order), moved


def shape_neighbors(columns, left_count):
    return (*tuple(word << left_count for word in transpose(columns, left_count)), *columns)


def connected(neighbors):
    reached = 1
    while True:
        extended = reached
        for i in bits(reached):
            extended |= neighbors[i]
        if reached == extended:
            return reached == (1 << len(neighbors)) - 1
        reached = extended


def shapes(size):
    for left_count in range(1, size // 2 + 1):
        for columns in combinations_with_replacement(range(1, 1 << left_count), size - left_count):
            neighbors = shape_neighbors(columns, left_count)
            if not connected(neighbors) or any(group.bit_count() > 6 for group in neighbors):
                continue
            equivalent = []
            for ordered, sources, moved in frames(columns, left_count):
                if ordered < columns:
                    break
                if ordered == columns:
                    equivalent.append((sources, moved))
            else:
                yield columns, neighbors, equivalent


def canonical_counts(counts, columns, equivalents):
    key = (counts[:len(counts) - len(columns)], tuple(zip(columns, counts[-len(columns):])))
    return all(key <= (tuple(counts[i] for i in sources),
                       tuple(sorted((column, counts[i]) for column, i in moved)))
               for sources, moved in equivalents)


def legal_history(neighbors, support_sizes):
    @cache
    def peel(active):
        if active.bit_count() == 1:
            root, = bits(active)
            return (root,) if support_sizes[root] == 3 else ()
        for joint in bits(active):
            earlier = active ^ (1 << joint)
            parents = tuple(bits(neighbors[joint] & earlier))
            fresh = support_sizes[joint] - len(parents)
            if not 1 <= len(parents) <= 3 or fresh not in (2, 3):
                continue
            if not parents_agree(parents, neighbors, earlier):
                continue
            # In reverse, a shared distinction with the removed junction
            # becomes loose at its earlier parent.
            if any(support_sizes[parent] - (neighbors[parent] & earlier).bit_count() > 3
                   for parent in parents):
                continue
            prefix = peel(earlier)
            if prefix:
                return (*prefix, joint)
        return ()

    return peel((1 << len(neighbors)) - 1)


def named_checks(neighbors, loose):
    checks = [[] for _ in loose]
    name = 0
    for left, group in enumerate(neighbors):
        for right in bits(group):
            if left < right:
                checks[left].append(name)
                checks[right].append(name)
                name += 1
    for joint, count in enumerate(loose):
        checks[joint].extend(range(name, name + count))
        name += count
    assert name == WIDTH
    return tuple(tuple(check) for check in checks)


def short_table(checks):
    owners = tuple(mask_of(i for i, check in enumerate(checks) if name in check)
                   for name in range(WIDTH))
    supports = []
    for subset in range(1, 1 << len(checks)):
        # A name survives the junction sum when its owners meet the subset oddly.
        support = mask_of(i for i, owner in enumerate(owners) if (owner & subset).bit_count() % 2)
        if support.bit_count() <= 4:
            supports.append(support)
    return table_from_supports(supports, ignored=4)[0]


def reference():
    rows, supports = literal_relation(TARGET)
    target, bonds = table_from_supports(supports, ignored=WIDTH)
    direct_bond_check(rows, bonds)
    target_menu = named_menu(TARGET)
    target_short = pool(target, 3)
    assert short_table(TARGET) == target_short
    target_profiles = profile(target_short)
    target_short_histogram = histogram(target_short)
    self_maps = {
        mode: tuple(isometries(table, table))
        for mode, table in (("full", target), ("cutoff_five", pool(target, 5)))
    }
    assert {mode: len(maps) for mode, maps in self_maps.items()} == {"full": 48, "cutoff_five": 48}
    assert set(self_maps["full"]) == set(self_maps["cutoff_five"])
    expected_pairs = {(5, 10)} | {pair for left, right in (((11, 12), (13, 14, 15)),
                                                          ((11, 12), (16, 17)),
                                                          ((13, 14, 15), (16, 17)))
                                      for pair in product(left, right)}
    expected_menu = ({(i,) for i in (5, 10, *range(11, 18))} | expected_pairs
                     | set(product((11, 12), (13, 14, 15), (16, 17))))
    assert target_menu == expected_menu

    swaps = {13: 5, 5: 13}
    false_map = tuple(swaps.get(name, name) for name in range(WIDTH))
    assert (11, 13, 16) in target_menu and (5, 11, 16) not in target_menu
    assert any(target_short[i][j] != target_short[false_map[i]][false_map[j]]
               for i, j in combinations(range(WIDTH), 2))

    stages = {}
    matches = []
    histogram_control = None
    for size in (6, 7, 8):
        counts = dict.fromkeys(("connected_bipartite_shapes_of_maximum_degree_at_most_six",
                                "reachable_shapes", "reachable_presentations",
                                "short_histogram_matches", "short_profile_matches",
                                "cutoff_five_presentations", "full_presentations",
                                "cutoff_five_isometries", "full_isometries"), 0)
        for columns, neighbors, equivalents in shapes(size):
            counts["connected_bipartite_shapes_of_maximum_degree_at_most_six"] += 1
            reachable_shape = False
            degrees = tuple(group.bit_count() for group in neighbors)
            loose_total = WIDTH - sum(degrees) // 2
            ranges = [range(max(0, 3 - degree), min(3, 6 - degree) + 1) for degree in degrees]
            for loose in product(*ranges):
                if sum(loose) != loose_total or not canonical_counts(loose, columns, equivalents):
                    continue
                history = legal_history(neighbors, tuple(a + b for a, b in zip(degrees, loose)))
                if not history:
                    continue
                reachable_shape = True
                counts["reachable_presentations"] += 1
                checks = named_checks(neighbors, loose)
                short = short_table(checks)
                if histogram(short) != target_short_histogram:
                    continue
                counts["short_histogram_matches"] += 1
                if profile(short) != target_profiles:
                    if histogram_control is None:
                        histogram_control = {"junction_checks": checks, "legal_history": history,
                                             "why_rejected": "Different per-distinction profiles through three."}
                    continue
                counts["short_profile_matches"] += 1
                candidate_rows, candidate_supports = literal_relation(checks)
                candidate, _ = table_from_supports(candidate_supports, ignored=WIDTH)
                assert short == pool(candidate, 3)
                candidate_menu = named_menu(checks)
                candidate_report = {"junction_checks": checks, "legal_history": history,
                                    "allowed_rows": len(candidate_rows),
                                    "cutoff_five_histogram_matches": histogram(pool(candidate, 5)) == histogram(pool(target, 5)),
                                    "isometries": {}, "disagreements": []}
                for mode, first, second in (("cutoff_five", pool(target, 5), pool(candidate, 5)),
                                            ("full", target, candidate)):
                    maps = tuple(isometries(first, second))
                    candidate_report["isometries"][mode] = len(maps)
                    counts[f"{mode}_presentations"] += bool(maps)
                    counts[f"{mode}_isometries"] += len(maps)
                    for mapping in maps:
                        unexpected = image(target_menu, mapping) ^ candidate_menu
                        checks_match = image(TARGET, mapping) == set(checks)
                        relation_matches = transport_rows(rows, mapping) == candidate_rows
                        if unexpected or not checks_match or not relation_matches:
                            candidate_report["disagreements"].append({
                                "mode": mode, "label_map": mapping,
                                "incorrect_menu_sets": sorted(unexpected),
                                "checks_match": checks_match,
                                "relation_matches": relation_matches,
                            })
                matches.append(candidate_report)
            counts["reachable_shapes"] += reachable_shape
        stages[size] = counts

    assert sum(count["full_isometries"] for count in stages.values()) >= 48
    assert sum(count["full_presentations"] for count in stages.values()) >= 1
    return {
        "target": {"checks": TARGET, "literal_rows": len(rows), "bond_count": len(bonds),
                   "bond_distance_histogram": sorted(histogram(target).items()),
                   "automorphisms": {mode: len(maps) for mode, maps in self_maps.items()},
                   "legal_inputs_by_count": {i: sorted(group for group in target_menu if len(group) == i)
                                             for i in (1, 2, 3)}},
        "width": WIDTH,
        "width_18_junction_counts": stages,
        "short_profile_matches": matches,
        "histogram_negative_control": histogram_control,
        "failed_renaming": {"swapped": [5, 13], "legal_before": [11, 13, 16],
                            "illegal_after": [5, 11, 16], "fails_through_three": True},
    }


if __name__ == "__main__":
    print(json.dumps(reference(), indent=2, sort_keys=True))
