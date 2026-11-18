"""Reverse reachability and marked triple comparison at width twenty."""

import importlib.util
import json
from collections import Counter
from hashlib import sha256
from itertools import combinations, permutations
from pathlib import Path


WIDTH = 20
PAIRS = tuple(combinations(range(WIDTH), 2))
EARLIER = (
    Path(__file__).resolve().parents[2] / "VARIABLE-OUTPUT-READER-20261118-001B"
    / "VARIABLE-OUTPUT-READER-20261118-001B-P001_width_nineteen" / "check_reverse.py"
)
# Configure an isolated instance of the committed checker. Only its
# width-parameterized reverse, table and marked-orbit functions are used.
spec = importlib.util.spec_from_file_location("width_twenty_engine", EARLIER)
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)
assert (engine.WIDTH, engine.INFINITY, len(engine.PAIRS)) == (19, 19, 171)
engine.WIDTH, engine.INFINITY, engine.PAIRS = WIDTH, WIDTH, PAIRS


def table_classes():
    stages = {}
    classes = {}
    fixtures = []
    coverage = Counter(dict.fromkeys(("legal_marked_orbits", "partial_legal_orbits",
                                      "same_table_alternate_presentations", "alternate_matches_touching_triples",
                                      "alternate_matches_changing_triples"), 0))
    first_conflict = None
    for size in (7, 8, 9):
        counts = Counter()
        for checks, history in engine.presentations(size, counts):
            counts["presentations"] += 1
            legal = engine.triple_menu(checks)
            counts["triple_bearing_presentations"] += bool(legal)
            counts["legal_triples"] += len(legal)
            table, _, _ = engine.bond_table(checks)
            fixtures.append((checks, history, table, legal))

            twins = engine.interchangeable(table)
            key, group, order = engine.canonical(table, twins)
            marks, partial = engine.marked_orbits(table, twins, legal, group)
            coverage["legal_marked_orbits"] += len(marks)
            coverage["partial_legal_orbits"] += len(partial)
            if partial and first_conflict is None:
                first_conflict = {"checks": checks, "history": history,
                                  **engine.partial_orbit_witness(table, twins, legal, marks, partial)}
            if key not in classes:
                classes[key] = (fixtures[-1], order, marks.keys())
                continue
            other, other_order, other_marks = classes[key]
            coverage["same_table_alternate_presentations"] += 1
            coverage["alternate_matches_touching_triples"] += bool(legal or other[-1])
            if marks.keys() == other_marks:
                continue
            coverage["alternate_matches_changing_triples"] += 1
            if first_conflict is None:
                other_checks, other_history, other_table, other_legal = other
                mapping = engine.table_map(table, other_table, order, other_order)
                renamed = {tuple(sorted(mapping[i] for i in triple)): triple for triple in legal}
                target_triple = min(renamed.keys() ^ other_legal)
                if target_triple in renamed:
                    source = (checks, history)
                    target = (other_checks, other_history)
                    source_triple = renamed[target_triple]
                else:
                    source = (other_checks, other_history)
                    target = (checks, history)
                    mapping = {new: old for old, new in mapping.items()}
                    source_triple = target_triple
                    target_triple = tuple(sorted(mapping[i] for i in source_triple))
                first_conflict = {"source": source, "target": target, "from": source_triple,
                                  "to": target_triple, "permutation": sorted(mapping.items())}
        stages[size] = counts
    return fixtures, {
        "junction_counts": stages, "full_table_classes": len(classes), "coverage": coverage,
        "class_count_with_legal_triple": sum(bool(details[0][-1]) for details in classes.values()),
        "first_triple_conflict": first_conflict,
    }


def reduced_rows(table, triple):
    """Encode the three full rows by trying every order of the three marks."""
    outside = tuple(i for i in range(WIDTH) if i not in triple)
    return min(
        (table[a][b], table[a][c], table[b][c],
         tuple(sorted((table[a][i] << 10) | (table[b][i] << 5) | table[c][i] for i in outside)))
        for a, b, c in permutations(triple)
    )


def profile_key(table, profiles, triple):
    a, b, c = triple
    return tuple(sorted(((profiles[a], table[b][c]), (profiles[b], table[a][c]), (profiles[c], table[a][b]))))


def distance_four_count(table):
    return sum(row[i+1:].count(4) for i, row in enumerate(table))


def describe(fixture, triple, count):
    checks, history, _, _ = fixture
    return {"checks": checks, "history": history, "triple": triple, "distance_four_pairs": count}


def reduced_reader(fixtures):
    # Any full-row match has matching row histograms and opposite entries.
    # This necessary condition screens candidates before the six-order check.
    accepted = {}
    exact_counts = {}
    positive_labels = set()
    profile_keys = set()
    prepared = []
    for fixture in fixtures:
        _, _, table, legal = fixture
        profiles = tuple(bytes(sorted(row)) for row in table)
        count = distance_four_count(table)
        prepared.append((fixture, profiles, count))
        for triple in sorted(legal):
            positive_labels.update(profiles[i] for i in triple)
            profile_keys.add(profile_key(table, profiles, triple))
            key = reduced_rows(table, triple)
            accepted.setdefault(key, {}).setdefault(count % 2, (fixture, triple, count))
            exact_counts.setdefault(key, set()).add(count)

    totals = Counter(dict.fromkeys(("profile_candidates", "legal_candidates", "false_matches_rows_only",
                                    "false_matches_rows_and_distance_four_parity",
                                    "false_matches_rows_and_exact_distance_four_count"), 0))
    first_reduced_collision = None
    first_parity_collision = None
    for fixture, profiles, count in prepared:
        _, _, table, legal = fixture
        labels = [i for i, profile in enumerate(profiles) if profile in positive_labels]
        legal_hits = 0
        for triple in combinations(labels, 3):
            if profile_key(table, profiles, triple) not in profile_keys:
                continue
            totals["profile_candidates"] += 1
            key = reduced_rows(table, triple)
            if triple in legal:
                legal_hits += 1
                assert count % 2 in accepted[key]
                continue
            if key not in accepted:
                continue
            totals["false_matches_rows_only"] += 1
            totals["false_matches_rows_and_exact_distance_four_count"] += count in exact_counts[key]
            if first_reduced_collision is None:
                first_reduced_collision = {"legal": describe(*next(iter(accepted[key].values()))),
                                           "forbidden": describe(fixture, triple, count)}
            if count % 2 in accepted[key]:
                totals["false_matches_rows_and_distance_four_parity"] += 1
                if first_parity_collision is None:
                    first_parity_collision = {"legal": describe(*accepted[key][count % 2]),
                                              "forbidden": describe(fixture, triple, count)}
        assert legal_hits == len(legal)
        totals["legal_candidates"] += legal_hits
    totals["candidates_covered"] = len(fixtures) * len(tuple(combinations(range(WIDTH), 3)))
    return {
        "counts": totals, "accepted_three_row_keys": len(accepted),
        "accepted_three_row_and_parity_keys": sum(map(len, accepted.values())),
        "accepted_three_row_and_exact_count_keys": sum(map(len, exact_counts.values())),
        "first_rows_only_collision": first_reduced_collision, "first_parity_collision": first_parity_collision,
    }


def verify_literal_fixture(description, eligible):
    checks, history, triple = (description[key] for key in ("checks", "history", "triple"))
    users = {}
    neighborhoods = [set() for _ in checks]
    widths = []
    for earlier, joint in enumerate(history):
        parents = []
        fresh = []
        for name in checks[joint]:
            if name in users:
                assert len(users[name]) == 1
                parents.extend(users[name])
            else:
                fresh.append(name)
        if earlier:
            assert len(parents) == len(set(parents)) and 1 <= len(parents) <= 3
            assert len(fresh) in (2, 3)
            assert all(neighborhoods[a] & neighborhoods[b] for a, b in combinations(parents, 2))
            if len(parents) == 3:
                assert not set.intersection(*(neighborhoods[parent] for parent in parents))
        else:
            assert not parents and len(fresh) == 3
        for parent in parents:
            neighborhoods[parent].add(joint)
            neighborhoods[joint].add(parent)
        for name in checks[joint]:
            users.setdefault(name, []).append(joint)
        widths.append(len(users))

    owners = tuple(tuple(users[name]) for name in triple)
    if all(len(group) == 1 for group in owners):
        parents = tuple(group[0] for group in owners)
        common = set.intersection(*(neighborhoods[parent] for parent in parents))
        permitted = (len(set(parents)) == 3 and not common
                     and all(neighborhoods[a] & neighborhoods[b] for a, b in combinations(parents, 2)))
    else:
        common = set()
        permitted = False
    assert permitted == eligible
    expected, bonds, dual = engine.bond_table(checks)
    equations = tuple(engine.reverse.mask_of(check) for check in checks)
    entries = [int(not any((row & equation).bit_count() % 2 for equation in equations))
               for row in range(1 << WIDTH)]
    rows = [row for row, value in enumerate(entries) if value]
    assert len(rows) == 1 << (WIDTH - len(checks))
    stride = 1
    while stride < len(entries):
        for block in range(0, len(entries), 2 * stride):
            for i in range(block, block + stride):
                left, right = entries[i], entries[i + stride]
                entries[i], entries[i + stride] = left + right, left - right
        stride *= 2
    assert {word for word, value in enumerate(entries) if value == len(rows)} == set(dual)
    engine.reverse.direct_bond_check(rows, bonds)
    assert distance_four_count(expected) == description["distance_four_pairs"]
    return expected, {"allowed_rows": len(rows), "minimal_bonds_checked": len(bonds), "owners": owners,
                      "common_neighbor_for_all_parents": sorted(common), "widths": widths}


def replay_reduced_witness(witness):
    legal, forbidden = witness["legal"], witness["forbidden"]
    first, legal_physical = verify_literal_fixture(legal, eligible=True)
    second, forbidden_physical = verify_literal_fixture(forbidden, eligible=False)
    marked = legal["triple"]
    other = forbidden["triple"]
    for target in permutations(other):
        left = sorted((tuple(first[i][j] for j in marked), i) for i in range(WIDTH) if i not in marked)
        right = sorted((tuple(second[i][j] for j in target), i) for i in range(WIDTH) if i not in other)
        if [profile for profile, _ in left] != [profile for profile, _ in right]:
            continue
        if any(first[marked[i]][marked[j]] != second[target[i]][target[j]]
               for i, j in combinations(range(3), 2)):
            continue
        mapping = dict(zip(marked, target))
        mapping.update((old, new) for (_, old), (_, new) in zip(left, right, strict=True))
        assert set(mapping) == set(mapping.values()) == set(range(WIDTH))
        retained = [(i, j) for i, j in PAIRS if i in marked or j in marked]
        assert len(retained) == 54
        assert all(first[i][j] == second[mapping[i]][mapping[j]] for i, j in retained)
        changed = [(i, j) for i, j in PAIRS if first[i][j] != second[mapping[i]][mapping[j]]]
        assert changed
        a, b = changed[0]
        return {"legal_physical": legal_physical, "forbidden_physical": forbidden_physical,
                "map_legal_to_forbidden": tuple(mapping[i] for i in range(WIDTH)),
                "matching_marked_pairs": len(retained), "changed_unmarked_pairs": len(changed),
                "one_outside_difference": {"legal_pair": (a, b), "forbidden_pair": (mapping[a], mapping[b]),
                                           "values": (first[a][b], second[mapping[a]][mapping[b]])}}
    raise AssertionError("No common marked table")


def run():
    fixtures, exact = table_classes()
    reduced = reduced_reader(fixtures)
    return {
        "width": WIDTH,
        "independent_width_nineteen_engine_sha256": sha256(EARLIER.read_bytes()).hexdigest(),
        "full_table": exact,
        "reduced_reader": reduced,
        "literal_replay_of_rows_only_collision": replay_reduced_witness(reduced["first_rows_only_collision"]),
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
