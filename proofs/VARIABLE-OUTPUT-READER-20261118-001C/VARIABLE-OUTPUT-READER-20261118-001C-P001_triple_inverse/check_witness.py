"""Replay the failures of three rows with distance-four parity or exact count."""

import json
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations, permutations
from pathlib import Path


HOST_PATH = (
    Path(__file__).resolve().parents[2] / "VARIABLE-OUTPUT-READER-20261118-001B"
    / "VARIABLE-OUTPUT-READER-20261118-001B-P001_width_nineteen" / "near_witness.json"
)
ANCHOR = 16
LEGAL_GRAFT = ((0, 1, 3), (0, 2, 4), (1, 5, 6), (2, 7, 8))
FORBIDDEN_GRAFT = ((0, 1, 4), (0, 2, 5), (1, 3, 6), (2, 3, 7, 8))
EXACT_LEGAL_GRAFT = ((0, 1, 2), (1, 3, 4), (2, 5, 6, 7), (5, 8, 9))
EXACT_FORBIDDEN_GRAFT = ((0, 1, 2), (1, 3, 4), (2, 5, 6, 7), (3, 5, 8, 9))


def mask(names):
    return sum(1 << name for name in names)


def bits(word):
    while word:
        first = word & -word
        yield first.bit_length() - 1
        word ^= first


def append_graft(checks, graft, local_anchor):
    new_base = len(set().union(*checks))
    fresh = sorted(set().union(*graft) - {local_anchor})
    names = dict(zip(fresh, range(new_base, new_base + len(fresh)), strict=True))
    names[local_anchor] = ANCHOR
    return (*checks, *(tuple(sorted(names[name] for name in check)) for check in graft))


def options(owners, neighbors, triple):
    uses = tuple(tuple(owners[name]) for name in triple)
    assert all(len(users) == 1 for users in uses)
    parents = tuple(users[0] for users in uses)
    assert len(set(parents)) == 3
    common = [sorted(neighbors[a] & neighbors[b]) for a, b in combinations(parents, 2)]
    all_common = sorted(set.intersection(*(neighbors[parent] for parent in parents)))
    return {"parents": parents, "pairwise_common_neighbors": common,
            "common_neighbor_for_all_three": all_common, "legal": all(common) and not all_common}


def replay(checks, host_history, triple):
    owners = defaultdict(list)
    neighbors = [set() for _ in checks]
    rows = {0}
    history = []
    for joint, check in enumerate(checks):
        assert len(set(check)) == len(check)
        consumed = tuple(name for name in check if name in owners)
        fresh = tuple(name for name in check if name not in owners)
        assert all(len(owners[name]) == 1 for name in consumed)
        parents = tuple(sorted(owners[name][0] for name in consumed))
        if joint < len(host_history):
            assert [list(parents), len(fresh)] == host_history[joint]
        if joint:
            assert len(set(parents)) == len(parents) and 1 <= len(parents) <= 3
            assert len(fresh) in (2, 3)
            assert all(neighbors[a] & neighbors[b] for a, b in combinations(parents, 2))
            if len(parents) == 3:
                assert not set.intersection(*(neighbors[parent] for parent in parents))
        else:
            assert not parents and len(fresh) == 3
        equation = mask(check)
        old_mask = mask(owners)
        choices = tuple(mask(fresh[i] for i in bits(word)) for word in range(1 << len(fresh)))
        extended = {row | fresh_row for row in rows for fresh_row in choices
                    if ((row | fresh_row) & equation).bit_count() % 2 == 0}
        assert {row & old_mask for row in extended} == rows
        rows = extended
        for parent in parents:
            neighbors[parent].add(joint)
            neighbors[joint].add(parent)
        for name in check:
            owners[name].append(joint)
        history.append({"junction": joint, "parents": parents, "fresh": fresh, "consumed": consumed})
    return rows, history, options(owners, neighbors, triple)


def independent_rows(rows):
    basis = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot not in basis:
                basis[pivot] = row
                break
            row ^= basis[pivot]
    return tuple(basis.values())


def scalar_table(checks, width):
    """Enumerate sums by separating the ownership of each distinction."""
    columns = tuple(mask(joint for joint, check in enumerate(checks) if name in check) for name in range(width))
    span = {mask(i for i, column in enumerate(columns) if (selected & column).bit_count() % 2)
            for selected in range(1 << len(checks))}
    assert len(span) == 1 << len(checks)
    bonds = []
    table = [[0 if i == j else None for j in range(width)] for i in range(width)]
    for word in sorted(span - {0}, key=lambda word: (word.bit_count(), word)):
        if any(known & word == known for known in bonds):
            continue
        bonds.append(word)
        value = word.bit_count() - 1
        assert value >= 2
        for a, b in combinations(bits(word), 2):
            if table[a][b] is None:
                table[a][b] = table[b][a] = value
    return tuple(tuple(row) for row in table), bonds, span


def check_bonds(rows, checks, bonds, span, width):
    witness = independent_rows(rows)
    assert len(witness) == width - len(checks)
    assert len(rows) == 1 << len(witness)
    assert all(not (row & word).bit_count() % 2 for row in witness for word in span)
    for bond in bonds:
        rank = bond.bit_count() - 1
        assert len(independent_rows(row & bond for row in witness)) == rank
        for i in bits(bond):
            erased = bond ^ (1 << i)
            assert len(independent_rows(row & erased for row in witness)) == rank


def marked_map(first, second, selected, target):
    width = len(first)

    def reordering(table, marked):
        return sorted((tuple(table[outer][i] for i in marked), outer)
                      for outer in range(width) if outer not in marked)

    left = reordering(first, selected)
    for order in permutations(target):
        if any(first[selected[a]][selected[b]] != second[order[a]][order[b]]
               for a, b in combinations(range(3), 2)):
            continue
        right = reordering(second, order)
        if [profile for profile, _ in left] != [profile for profile, _ in right]:
            continue
        mapping = dict(zip(selected, order, strict=True))
        mapping.update((old, new) for (_, old), (_, new) in zip(left, right, strict=True))
        assert set(mapping) == set(mapping.values()) == set(range(width))
        return tuple(mapping[i] for i in range(width))
    raise AssertionError("Marked entries of the two tables do not match")


def histogram(table):
    return Counter(table[i][j] for i, j in combinations(range(len(table)), 2))


def padded_witness(host, grafts, fresh_counts, expected_distance_four):
    sides = []
    tables = []
    marked = []
    for name, (graft, anchor) in zip(("legal_side", "forbidden_side"), grafts, strict=True):
        datum = host[name]
        current = tuple(tuple(check) for check in datum["junction_supports"])
        checks = append_graft(current, graft, anchor)
        width = len(set().union(*checks))
        triple = tuple(datum["marked"])
        rows, history, permission = replay(checks, datum["history"], triple)
        assert permission["legal"] == (name == "legal_side")
        assert history[8]["consumed"] == (ANCHOR,)
        assert tuple(len(step["fresh"]) for step in history[8:]) == fresh_counts
        table, bonds, span = scalar_table(checks, width)
        check_bonds(rows, checks, bonds, span, width)
        counts = histogram(table)
        sides.append({"checks": checks, "history": history, "marked": triple, "allowed_rows": len(rows),
                      "minimal_bonds_checked": len(bonds), "distance_four_pairs": counts[4],
                      "local_graft_checks": graft, "local_anchor_name": anchor,
                      "full_bond_distance_histogram": counts, "triple_permission": permission})
        tables.append(table)
        marked.append(triple)

    left, right = tables
    assert len(left) == len(right) == width
    selected, target = marked
    mapping = marked_map(left, right, selected, target)
    assert tuple(sorted(mapping[i] for i in selected)) == target
    marked_pairs = [(i, j) for i, j in combinations(range(width), 2) if i in selected or j in selected]
    assert len(marked_pairs) == 3 * (width - 3) + 3
    assert all(left[i][j] == right[mapping[i]][mapping[j]] for i, j in marked_pairs)
    outside = [(i, j) for i, j in combinations(range(width), 2) if left[i][j] != right[mapping[i]][mapping[j]]]
    assert outside
    i, j = outside[0]
    assert tuple(side["distance_four_pairs"] for side in sides) == expected_distance_four
    assert all(side["distance_four_pairs"] % 2 == 0 for side in sides)
    return {"width": width, "legal_side": sides[0], "forbidden_side": sides[1],
            "label_map": mapping, "marked_pairs_checked": len(marked_pairs),
            "different_outside_pairs": len(outside),
            "one_outside_difference": {"legal_pair": (i, j), "forbidden_pair": (mapping[i], mapping[j]),
                                       "distances": (left[i][j], right[mapping[i]][mapping[j]])}}


def run():
    host_bytes = HOST_PATH.read_bytes()
    host = json.loads(host_bytes)
    parity = padded_witness(host, ((LEGAL_GRAFT, 3), (FORBIDDEN_GRAFT, 4)), (2, 2, 2, 2), (46, 52))
    exact = padded_witness(host, ((EXACT_LEGAL_GRAFT, 0), (EXACT_FORBIDDEN_GRAFT, 0)),
                           (2, 2, 3, 2), (50, 50))
    return {"width_nineteen_source_sha256": sha256(host_bytes).hexdigest(),
            "padded_witness": parity, "exact_count_witness": exact}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
