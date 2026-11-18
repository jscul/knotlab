"""Check the reachable eight-junction witness using literal allowed states."""

import json
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations
from pathlib import Path

import check_reference as reference


CHECKS = (
    (0, 1, 2),
    (0, 3, 5),
    (1, 4, 7),
    (2, 6, 8),
    (3, 4, 9, 12),
    (5, 6, 10, 13),
    (7, 8, 11, 14),
    (9, 10, 11, 15, 16, 17),
)
EXPECTED_HISTORY = (
    ((), 3),
    ((0,), 2),
    ((0,), 2),
    ((0,), 2),
    ((1, 2), 2),
    ((1, 3), 2),
    ((2, 3), 2),
    ((4, 5, 6), 3),
)


def replay_history(checks):
    owners = defaultdict(list)
    allowed = {0}
    report = []
    for joint, check in enumerate(checks):
        assert len(check) == len(set(check))
        old = tuple(name for name in check if name in owners)
        fresh = tuple(name for name in check if name not in owners)
        assert all(len(owners[name]) == 1 for name in old)
        parents = tuple(sorted(owners[name][0] for name in old))
        assert len(parents) == len(set(parents))
        assert (parents, len(fresh)) == EXPECTED_HISTORY[joint]
        neighbors = [set() for _ in range(joint)]
        for attached in owners.values():
            if len(attached) == 2:
                first, second = attached
                neighbors[first].add(second)
                neighbors[second].add(first)
        assert all(neighbors[a] & neighbors[b] for a, b in combinations(parents, 2))
        if len(parents) == 3:
            assert not set.intersection(*(neighbors[parent] for parent in parents))

        prior = set(allowed)
        equation = reference.mask_of(check)
        loose_words = tuple(reference.mask_of(fresh[i] for i in reference.bits(word))
                            for word in range(1 << len(fresh)))
        allowed = {row | choice for row in prior for choice in loose_words
                   if ((row | choice) & equation).bit_count() % 2 == 0}
        old_names = reference.mask_of(owners)
        assert {row & old_names for row in allowed} == prior
        for name in check:
            owners[name].append(joint)
        report.append({"junction": joint, "parents": parents, "consumed": old,
                       "fresh": fresh, "allowed_rows": len(allowed)})
    return report, allowed


def relation_preserving_witness(rows, table, pairs, original_history):
    swaps = ((9, 12), (10, 13), (11, 14))
    mapping = list(range(reference.WIDTH))
    for a, b in swaps:
        mapping[a], mapping[b] = mapping[b], mapping[a]
    alternate_last, = reference.image((CHECKS[-1],), mapping)
    alternate_checks = (*CHECKS[:-1], alternate_last)
    alternate_history, second_rows = replay_history(alternate_checks)
    assert original_history[:-1] == alternate_history[:-1]
    assert original_history[-1]["parents"] == alternate_history[-1]["parents"] == (4, 5, 6)
    assert original_history[-1]["consumed"] == (9, 10, 11)
    assert alternate_history[-1]["consumed"] == (12, 13, 14)
    assert original_history[-1]["fresh"] == alternate_history[-1]["fresh"] == (15, 16, 17)

    older_xor = 0
    for older in CHECKS[:-1]:
        assert reference.image((older,), mapping) == {older}
        older_xor ^= reference.mask_of(older)
    assert tuple(reference.bits(older_xor)) == (9, 10, 11, 12, 13, 14)
    # Exchanging the eighth equation for its XOR with the seven retained
    # equations keeps both systems equivalent in the same names.
    assert reference.mask_of(CHECKS[-1]) ^ older_xor == reference.mask_of(alternate_last)
    literal_alternate, alternate_supports = reference.literal_relation(alternate_checks)
    assert rows == second_rows == literal_alternate
    assert reference.transport_rows(rows, mapping) == rows
    alternate_table, _ = reference.table_from_supports(alternate_supports, ignored=reference.WIDTH)
    assert alternate_table == table
    assert all(table[i][j] == table[mapping[i]][mapping[j]] for i, j in pairs)

    legal = reference.named_menu(CHECKS)
    alternate_menu = reference.named_menu(alternate_checks)
    witness_owners = {stage: {name: tuple(i for i, check in enumerate(checks) if name in check)
                              for name in (9, 12)}
                      for stage, checks in (("first", CHECKS), ("alternate", alternate_checks))}
    assert witness_owners == {"first": {9: (4, 7), 12: (4,)}, "alternate": {9: (4,), 12: (4, 7)}}
    assert reference.image(legal, mapping) == alternate_menu
    assert (12,) in legal - alternate_menu and (9,) in alternate_menu - legal
    assert (12, 13) in legal - alternate_menu and (9, 10) in alternate_menu - legal
    assert all(len(use) != 3 for use in legal | alternate_menu)
    assert set(legal & alternate_menu) == {(15,), (16,), (17,)}

    return {
        "transpositions": swaps,
        "alternate_eighth_check": alternate_last,
        "xor_of_seven_older_checks": tuple(reference.bits(older_xor)),
        "first_eighth_junction": original_history[-1],
        "alternate_eighth_junction": alternate_history[-1],
        "allowed_rows_in_common_prefix": original_history[-2]["allowed_rows"],
        "same_named_allowed_rows": len(rows),
        "allowed_rows_moved_outside_relation": 0,
        "bond_distance_pairs_checked": len(pairs),
        "witness_owners": witness_owners,
        "first_only_ninth_inputs": sorted(legal - alternate_menu),
        "alternate_only_ninth_inputs": sorted(alternate_menu - legal),
        "common_ninth_inputs": sorted(legal & alternate_menu),
    }


def verify():
    history, generated = replay_history(CHECKS)
    rows, supports = reference.literal_relation(CHECKS)
    assert rows == generated
    table, bonds = reference.table_from_supports(supports, ignored=reference.WIDTH)
    reference.direct_bond_check(rows, bonds)

    mapping = list(range(reference.WIDTH))
    mapping[9], mapping[12] = mapping[12], mapping[9]
    pairs = tuple(combinations(range(reference.WIDTH), 2))
    assert len(pairs) == 153
    assert all(table[i][j] == table[mapping[i]][mapping[j]] for i, j in pairs)
    assert all(table[i][j] < reference.WIDTH for i, j in pairs)

    legal = reference.named_menu(CHECKS)
    assert legal == ({(name,) for name in range(12, 18)}
                     | {(12, 13), (12, 14), (13, 14)})
    moved_menu = reference.image(legal, mapping)
    removed = legal - moved_menu
    added = moved_menu - legal
    assert removed == {(12,), (12, 13), (12, 14)}
    assert added == {(9,), (9, 13), (9, 14)}
    assert (13, 14) in legal & moved_menu

    moved_rows = reference.transport_rows(rows, mapping)
    escaped = sorted(moved_rows - rows)
    assert len(escaped) == 512
    to_row = escaped[0]
    from_row, = reference.transport_rows((to_row,), mapping)
    assert from_row in rows
    violates = [i for i, check in enumerate(CHECKS)
                if (to_row & reference.mask_of(check)).bit_count() % 2]
    assert violates == [7]

    return {
        "literal_checker_sha256": sha256(Path(reference.__file__).read_bytes()).hexdigest(),
        "checks": CHECKS,
        "history": history,
        "bond_distance_pairs_checked": len(pairs),
        "bond_distance_histogram": dict(sorted(Counter(table[i][j] for i, j in pairs).items())),
        "transposition": [9, 12],
        "menu_by_arity": {
            arity: {"legal": sorted(use for use in legal if len(use) == arity),
                    "missing_after_transport": sorted(use for use in removed if len(use) == arity),
                    "illegal_after_transport": sorted(use for use in added if len(use) == arity)}
            for arity in (1, 2, 3)
        },
        "row_count": len(rows),
        "allowed_rows_moved_outside_relation": len(escaped),
        "allowed_row_witness": {"before": from_row, "after": to_row,
                                "ones_before": tuple(reference.bits(from_row)),
                                "ones_after": tuple(reference.bits(to_row)),
                                "violated_junctions_after": violates},
        "relation_preserving_witness": relation_preserving_witness(rows, table, pairs, history),
    }


if __name__ == "__main__":
    print(json.dumps(verify(), indent=2, sort_keys=True))
