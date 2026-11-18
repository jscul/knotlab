"""Replay the two width-19 histories with matching marked bond-distance rows."""

import json
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations, permutations
from pathlib import Path

import check_reverse as audit


LEGAL_HISTORY = (
    ((), 3),
    ((0,), 2),
    ((0,), 2),
    ((1,), 2),
    ((0, 3), 2),
    ((1, 2), 3),
    ((3, 5), 2),
    ((6,), 3),
)
FORBIDDEN_HISTORY = (*LEGAL_HISTORY[:5], ((2, 4), 3), *LEGAL_HISTORY[6:])
LEGAL_MARK = (10, 11, 15)
FORBIDDEN_MARK = (11, 12, 15)


def grow(history):
    junctions = []
    loose = []
    neighbors = []
    shared = []
    next_name = 0
    for joint, (parents, fresh_count) in enumerate(history):
        if joint == 0:
            assert not parents and fresh_count == 3
        else:
            assert 1 <= len(parents) <= 3 and fresh_count in (2, 3)
        assert len(parents) == len(set(parents))
        assert all(parent < joint and loose[parent] for parent in parents)
        assert all(neighbors[a] & neighbors[b] for a, b in combinations(parents, 2))
        if len(parents) == 3:
            assert not set.intersection(*(neighbors[parent] for parent in parents))

        consumed = tuple(loose[parent].pop(0) for parent in parents)
        fresh = list(range(next_name, next_name + fresh_count))
        next_name += fresh_count
        shared.extend(consumed)
        for parent in parents:
            neighbors[parent].add(joint)
        neighbors.append(set(parents))
        loose.append(fresh)
        junctions.append((*consumed, *fresh))
    names = (*shared, *(name for group in loose for name in group))
    assert len(names) == len(set(names)) == audit.WIDTH
    order = {old: new for new, old in enumerate(names)}
    return tuple(tuple(sorted(order[name] for name in junction)) for junction in junctions)


def literal_table(checks):
    table, bonds, span = audit.bond_table(checks)
    equations = tuple(audit.reverse.mask_of(check) for check in checks)
    indicator = [int(not any((row & equation).bit_count() % 2 for equation in equations))
                 for row in range(1 << audit.WIDTH)]
    rows = [row for row, allowed in enumerate(indicator) if allowed]
    assert len(rows) == 1 << (audit.WIDTH - len(checks))
    stride = 1
    while stride < len(indicator):
        for block in range(0, len(indicator), 2 * stride):
            for i in range(block, block + stride):
                left, right = indicator[i], indicator[i + stride]
                indicator[i], indicator[i + stride] = left + right, left - right
        stride *= 2
    assert {mask for mask, coefficient in enumerate(indicator) if coefficient == len(rows)} == set(span)
    audit.reverse.direct_bond_check(rows, bonds)
    return table, rows, bonds


def permissions(checks, marked):
    owners = tuple(tuple(joint for joint, check in enumerate(checks) if name in check) for name in marked)
    menu = audit.triple_menu(checks)
    report = {"owners": owners, "legal_marked_input": marked in menu, "legal_triples": sorted(menu)}
    if all(len(users) == 1 for users in owners):
        parents = tuple(users[0] for users in owners)
        neighborhoods = tuple({joint for joint, check in enumerate(checks)
                               if joint != parent and set(checks[parent]).intersection(check)}
                              for parent in parents)
        report["pairwise_parent_common_neighbors"] = [sorted(a & b) for a, b in combinations(neighborhoods, 2)]
        report["neighbor_common_to_all_parents"] = sorted(set.intersection(*neighborhoods))
    return report


def mark_isometries(left, right):
    outside_left = tuple(i for i in range(audit.WIDTH) if i not in LEGAL_MARK)
    outside_right = tuple(i for i in range(audit.WIDTH) if i not in FORBIDDEN_MARK)

    def bucket(table, marked, choices):
        result = defaultdict(list)
        for i in choices:
            result[tuple(table[i][j] for j in marked)].append(i)
        return result

    buckets = bucket(left, LEGAL_MARK, outside_left)
    for target in permutations(FORBIDDEN_MARK):
        matched_buckets = bucket(right, target, outside_right)
        if {key: len(group) for key, group in buckets.items()} != {
            key: len(group) for key, group in matched_buckets.items()
        }:
            continue
        if any(left[LEGAL_MARK[i]][LEGAL_MARK[j]] != right[target[i]][target[j]]
               for i, j in combinations(range(3), 2)):
            continue
        mapping = dict(zip(LEGAL_MARK, target, strict=True))
        for key, group in buckets.items():
            mapping.update(zip(group, matched_buckets[key], strict=True))
        yield mapping, buckets


def run():
    left_checks, right_checks = grow(LEGAL_HISTORY), grow(FORBIDDEN_HISTORY)
    left_report = permissions(left_checks, LEGAL_MARK)
    right_report = permissions(right_checks, FORBIDDEN_MARK)
    assert left_report["legal_marked_input"] and not right_report["legal_marked_input"]
    left, left_rows, left_bonds = literal_table(left_checks)
    right, right_rows, right_bonds = literal_table(right_checks)
    mapping, buckets = next(mark_isometries(left, right))
    assert set(mapping) == set(mapping.values()) == set(range(audit.WIDTH))
    assert tuple(sorted(mapping[i] for i in LEGAL_MARK)) == FORBIDDEN_MARK

    marked_pairs = []
    outside_differences = []
    for i, j in audit.PAIRS:
        original = left[i][j]
        mapped = right[mapping[i]][mapping[j]]
        if i in LEGAL_MARK or j in LEGAL_MARK:
            assert original == mapped
            marked_pairs.append((i, j))
        elif original != mapped:
            outside_differences.append({"legal_side": (i, j), "forbidden_side": (mapping[i], mapping[j]),
                                        "legal_side_bond_distance": original, "forbidden_side_bond_distance": mapped})
    assert len(marked_pairs) == 51 and outside_differences
    histogram_left = Counter(left[i][j] for i, j in audit.PAIRS)
    histogram_right = Counter(right[i][j] for i, j in audit.PAIRS)
    assert histogram_left != histogram_right

    return {
        "independent_implementation_sha256": sha256(Path(audit.__file__).read_bytes()).hexdigest(),
        "legal_side": {"history": LEGAL_HISTORY, "junction_supports": left_checks, "marked": LEGAL_MARK,
                       "allowed_rows": len(left_rows), "bonds": len(left_bonds),
                       "bond_distance_histogram": dict(sorted(histogram_left.items())), **left_report},
        "forbidden_side": {"history": FORBIDDEN_HISTORY, "junction_supports": right_checks,
                           "marked": FORBIDDEN_MARK, "allowed_rows": len(right_rows), "bonds": len(right_bonds),
                           "bond_distance_histogram": dict(sorted(histogram_right.items())), **right_report},
        "map_legal_to_forbidden": tuple(mapping[i] for i in range(audit.WIDTH)),
        "matching_pairs_with_a_marked_endpoint": len(marked_pairs),
        "internal_marked_bond_distances": sorted(left[i][j] for i, j in combinations(LEGAL_MARK, 2)),
        "outside_profiles_to_the_marked_triple": {str(key): len(group) for key, group in sorted(buckets.items())},
        "outside_pairs_that_differ": len(outside_differences),
        "one_outside_difference": outside_differences[0],
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
