"""Test the fixed three-row description and distance-four parity at width 20."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import cache
from itertools import combinations, permutations
from pathlib import Path
from random import Random


ROOT = Path(__file__).resolve().parents[3]
PREREGISTRATION = ROOT / "research/VARIABLE-OUTPUT-READER-20261118-001C/preregistration.md"
FAMILY18 = (
    ROOT / "proofs/VARIABLE-OUTPUT-READER-20261118-001A"
    / "VARIABLE-OUTPUT-READER-20261118-001A-P001_width_eighteen"
)
FAMILY19 = (
    ROOT / "proofs/VARIABLE-OUTPUT-READER-20261118-001B"
    / "VARIABLE-OUTPUT-READER-20261118-001B-P001_width_nineteen"
)
PRODUCER_SHA = "dc1bdeaea873653d027b07dcad78f0735716bce7604f2bb62a179da1bbd6d163"
READER_SHA = "9a2f2236265fe5e63efc7312f4c7e6c2577f864280a4d6d68e878dac7d6ebd65"
NEAR_WITNESS_SHA = "960ec63a1a23da44e6c70a489fd8bd27f6ab6152efe8a7599c47a72b2adb42da"
WIDTH = 20
TRIPLES = tuple(combinations(range(WIDTH), 3))
QUOTAS = {7: {2: 1, 3: 5}, 8: {2: 4, 3: 3}, 9: {2: 7, 3: 1}}
ROWS = "to_other_distinctions"
PARITY = "three_rows_and_parity_at_four"
COUNT = "three_rows_and_count_at_four"
MODES = (ROWS, PARITY, COUNT)


def load_frozen(path, digest, module_name):
    assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@cache
def configured_producer(width):
    """Use a private instance of the verified population producer."""
    assert width in (19, WIDTH)
    module = load_frozen(
        FAMILY18 / "check_width.py", PRODUCER_SHA, f"parity_transfer_population_{width}"
    )
    assert module.WIDTH == 18 and module.FRESH_COUNTS == (2, 3)
    module.WIDTH = width
    module.MAX_JUNCTIONS = 1 + (width - 3) // 2
    module.PAIRS = tuple(combinations(range(width), 2))
    return module


def producer(width=WIDTH):
    return configured_producer(width)


def inherited():
    return producer().inherited()


def width_fixtures():
    """Return width-20 physical representatives ordered by junction count and history."""
    assert PREREGISTRATION.is_file()
    return producer().width_fixtures()


def width_records():
    """Yield archived Measured objects with 190 sorted pair entries and actual menus."""
    assert PREREGISTRATION.is_file()
    yield from producer().width_records()


@cache
def frozen_reader(width=WIDTH):
    """Retain the exact canonical descriptor while allowing one more outside identity."""
    assert width in (19, WIDTH)
    module = load_frozen(
        FAMILY19 / "check_reader.py", READER_SHA, f"parity_transfer_description_{width}"
    )
    assert module.WIDTH == 19
    module.WIDTH = width
    module.CUTOFFS = (width,)
    return module


@dataclass(frozen=True)
class Case:
    fixture: object
    table: tuple[bytes, ...]
    legal: frozenset[tuple[int, int, int]]

    @property
    def depth(self):
        return len(self.fixture.loose_counts)


def cases():
    reader = frozen_reader()
    for record in width_records():
        legal = frozenset(tuple(sorted(choice)) for choice in record.menu if len(choice) == 3)
        case = Case(record.fixture, reader.matrix_from_pairs(record.table), legal)
        assert Counter(fresh for _, fresh in case.fixture.history) == Counter(QUOTAS[case.depth])
        yield case


def descriptions(case, reader):
    desc = reader.Descriptions(case.table)
    assert desc.pairs_at_four == sum(
        case.table[i][j] == 4 for i, j in combinations(range(len(case.table)), 2)
    )
    return desc


def profile_keys(rows, pairs_at_four):
    return rows, (rows, (pairs_at_four % 2,)), (rows, (pairs_at_four,))


def raw_canonical_rows(table, triple):
    """Classify the marked rows independently by trying all six marked orders."""
    outside = tuple(i for i in range(len(table)) if i not in triple)
    return min(
        (
            (table[b][c], table[a][c], table[a][b]),
            tuple(sorted((table[a][i], table[b][i], table[c][i]) for i in outside)),
        )
        for a, b, c in permutations(triple)
    )


def compile_legal(census, reader):
    """Index only legal occurrences. The cheaper keys are determined by the retained rows."""
    earliest = {mode: {} for mode in MODES}
    multiplicity = {mode: Counter() for mode in MODES}
    prefilter = defaultdict(set)
    raw_to_frozen, frozen_to_raw = {}, {}
    for case_id, case in enumerate(census):
        if not case.legal:
            continue
        desc = descriptions(case, reader)
        for triple in sorted(case.legal):
            opposite = desc.opposite(triple)
            rows = desc.other_key(triple, opposite)
            raw = raw_canonical_rows(case.table, triple)
            assert raw_to_frozen.setdefault(raw, rows) == rows
            assert frozen_to_raw.setdefault(rows, raw) == raw
            internal = tuple(sorted(opposite))
            histogram = desc.row_key(triple, opposite, WIDTH)
            assert rows[0] == histogram
            prefilter[internal].add(histogram)
            for mode, key in zip(MODES, profile_keys(rows, desc.pairs_at_four), strict=True):
                earliest[mode].setdefault(key, (case_id, triple))
                multiplicity[mode][key] += 1
    return prefilter, earliest, multiplicity, raw_to_frozen


def preference(census, good, bad):
    a, b = census[good[0]].depth, census[bad[0]].depth
    return max(a, b), a + b, good, bad


def check_every_triple(census, reader, prefilter, earliest, raw_to_frozen):
    false_profiles = {mode: Counter() for mode in MODES}
    false_types = {mode: set() for mode in MODES}
    smallest = {mode: None for mode in MODES}
    wrong_counts_at_four = defaultdict(Counter)
    by_depth = defaultdict(Counter)
    for case_id, case in enumerate(census):
        counts = by_depth[case.depth]
        desc = descriptions(case, reader)
        table = case.table
        counts["types"] += 1
        counts["types_with_legal_triples"] += bool(case.legal)
        for triple in TRIPLES:
            counts["checked"] += 1
            if triple in case.legal:
                counts["legal"] += 1
                # The compilation pass formed all three exact profiles here.
                continue
            a, b, c = triple
            opposite = table[b][c], table[a][c], table[a][b]
            allowed_histograms = prefilter.get(tuple(sorted(opposite)))
            if allowed_histograms is None:
                continue
            counts["forbidden_passing_internal_prefilter"] += 1
            if desc.row_key(triple, opposite, WIDTH) not in allowed_histograms:
                continue
            counts["forbidden_passing_row_histogram_prefilter"] += 1
            rows = desc.other_key(triple, opposite)
            alternative = raw_to_frozen.get(raw_canonical_rows(table, triple))
            assert alternative == (rows if rows in earliest[ROWS] else None)
            if rows not in earliest[ROWS]:
                continue
            wrong_counts_at_four[rows][desc.pairs_at_four] += 1
            for mode, key in zip(MODES, profile_keys(rows, desc.pairs_at_four), strict=True):
                good = earliest[mode].get(key)
                if good is None:
                    continue
                bad = (case_id, triple)
                false_profiles[mode][key] += 1
                false_types[mode].add(case_id)
                counts[f"forbidden_matching_{mode}"] += 1
                rank = preference(census, good, bad)
                if smallest[mode] is None or rank < smallest[mode][0]:
                    smallest[mode] = (rank, good, bad, key)
    return by_depth, false_profiles, false_types, smallest, wrong_counts_at_four


def columns_by_values(table, triple):
    grouped = defaultdict(list)
    for target in range(len(table)):
        if target not in triple:
            grouped[tuple(table[mark][target] for mark in triple)].append(target)
    return grouped


def incident_map(left, left_triple, right, right_triple):
    """Reconstruct one simultaneous renaming on the actual identities."""
    assert len(left) == len(right)
    old_columns = columns_by_values(left, left_triple)
    for ordered in permutations(right_triple):
        if any(left[left_triple[i]][left_triple[j]] != right[ordered[i]][ordered[j]]
               for i, j in combinations(range(3), 2)):
            continue
        new_columns = columns_by_values(right, ordered)
        if {key: len(ids) for key, ids in old_columns.items()} != {
            key: len(ids) for key, ids in new_columns.items()
        }:
            continue
        mapping = dict(zip(left_triple, ordered, strict=True))
        for key in sorted(old_columns):
            mapping.update(zip(old_columns[key], new_columns[key], strict=True))
        renamed = tuple(mapping[i] for i in range(len(left)))
        assert sorted(renamed) == list(range(len(left)))
        assert all(left[i][j] == right[renamed[i]][renamed[j]]
                   for i, j in combinations(range(len(left)), 2)
                   if i in left_triple or j in left_triple)
        return renamed
    raise AssertionError("A common canonical row profile must supply an incident bijection")


def parity_case_record(case, triple, desc, index):
    _, _, rules = inherited()
    checks = case.fixture.checks()
    users, neighbors = rules.incidence(checks)
    owners = tuple(tuple(users[bit]) for bit in triple)
    parents = sorted({owner for support in owners for owner in support})
    loose = all(len(uses) == 1 for uses in owners)
    pairwise = {}
    common = []
    if loose and len(parents) == 3:
        pairwise = {
            f"{i},{j}": sorted(neighbors[i] & neighbors[j])
            for i, j in combinations(parents, 2)
        }
        common = sorted(set.intersection(*(neighbors[i] for i in parents)))
    direct = rules.legal_local_move(checks, triple, (20, 21, 22))
    assert direct == (triple in case.legal)
    return {
        "physical_index": index, "junction_count": case.depth, "history": case.fixture.history,
        "junction_supports": tuple(checks.values()), "operands": triple, "legal": direct,
        "operand_owners": owners, "pairwise_parent_common_neighbors": pairwise,
        "common_neighbor_of_all_three": common, "total_unordered_pairs_at_four": desc.pairs_at_four,
        "parity": desc.pairs_at_four % 2,
        "full_scalar_rows_hex": [row.hex() for row in case.table],
    }


def witness(census, reader, mode, selected):
    if selected is None:
        return None
    _, (i, a), (j, b), key = selected
    left, right = census[i], census[j]
    d_left, d_right = descriptions(left, reader), descriptions(right, reader)
    assert a in left.legal and b not in right.legal
    k = MODES.index(mode)
    r_left = d_left.other_key(a, d_left.opposite(a))
    r_right = d_right.other_key(b, d_right.opposite(b))
    assert profile_keys(r_left, d_left.pairs_at_four)[k] == profile_keys(r_right, d_right.pairs_at_four)[k] == key
    mapping = incident_map(left.table, a, right.table, b)
    outside_differences = [
        (i, j, left.table[i][j], right.table[mapping[i]][mapping[j]])
        for i, j in combinations(range(WIDTH), 2)
        if i not in a and j not in a and left.table[i][j] != right.table[mapping[i]][mapping[j]]
    ]
    return {
        "canonical_profile_hex": reader.encode(mode, key),
        "legal_side": parity_case_record(left, a, d_left, i),
        "forbidden_side": parity_case_record(right, b, d_right, j),
        "map_legal_to_forbidden": mapping,
        "incident_pairs_verified": 3 + 3 * (WIDTH - 3),
        "outside_pairs_that_differ_under_this_map": len(outside_differences),
        "outside_differences_in_legal_names": outside_differences,
    }


def archived_negative_control():
    path = FAMILY19 / "near_witness.json"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == NEAR_WITNESS_SHA
    frozen = json.loads(path.read_text())
    scout, _, rules = inherited()
    reader = frozen_reader(19)
    values = []
    for name in ("legal_side", "forbidden_side"):
        side = frozen[name]
        checks = dict(enumerate(map(tuple, side["junction_supports"])))
        pairs = scout.full_table(scout.parity_span(checks), 19)
        table = reader.matrix_from_pairs(pairs)
        marked = tuple(side["marked"])
        desc = reader.Descriptions(table)
        assert (frozenset(marked) in scout.actual_menu(rules, checks)) == side["legal_marked_input"]
        values.append((table, marked, desc.other_key(marked, desc.opposite(marked)), desc.pairs_at_four))
    left, right = values
    assert left[2] == right[2] and (left[3], right[3]) == (32, 33)
    assert raw_canonical_rows(left[0], left[1]) == raw_canonical_rows(right[0], right[1])
    mapping = frozen["map_legal_to_forbidden"]
    assert tuple(sorted(mapping[i] for i in left[1])) == right[1]
    assert all(left[0][i][j] == right[0][mapping[i]][mapping[j]]
               for i, j in combinations(range(19), 2) if i in left[1] or j in left[1])
    return {
        "marked_pairs_verified": 51, "three_rows_match": True,
        "unordered_pairs_at_four": (left[3], right[3]), "parity_separates": True,
    }


def relabel_control(census, reader):
    source = next(case for case in census if case.legal)
    scout, _, rules = inherited()
    names = list(range(WIDTH))
    Random(20020).shuffle(names)
    inverse = {old: new for new, old in enumerate(names)}
    checks = {i: tuple(inverse[bit] for bit in support) for i, support in source.fixture.checks().items()}
    matrix = tuple(bytes(source.table[i][j] for j in names) for i in names)
    assert reader.matrix_from_pairs(scout.full_table(scout.parity_span(checks), WIDTH)) == matrix
    menu = {
        tuple(sorted(choice)) for choice in scout.actual_menu(rules, checks) if len(choice) == 3
    }
    original, renamed = reader.Descriptions(source.table), reader.Descriptions(matrix)
    assert original.pairs_at_four == renamed.pairs_at_four
    for proposed in TRIPLES:
        old = tuple(sorted(names[i] for i in proposed))
        assert (proposed in menu) == (old in source.legal)
        assert original.other_key(old, original.opposite(old)) == renamed.other_key(
            proposed, renamed.opposite(proposed)
        )
    return {
        "new_names_to_original": names, "triples_checked": len(TRIPLES),
        "legal_triples": len(menu), "pairs_at_four": original.pairs_at_four,
    }


def run():
    assert PREREGISTRATION.is_file()
    assert len(TRIPLES) == 1140
    reader = frozen_reader()
    width19 = archived_negative_control()
    census = tuple(cases())
    assert {case.depth for case in census} == set(QUOTAS)
    relabeled = relabel_control(census, reader)
    prefilter, earliest, positives, raw_to_frozen = compile_legal(census, reader)
    by_depth, collisions, false_types, smallest, wrong_counts_at_four = check_every_triple(
        census, reader, prefilter, earliest, raw_to_frozen
    )
    legal_counts_at_four = defaultdict(Counter)
    for (rows, (count,)), multiplicity in positives[COUNT].items():
        legal_counts_at_four[rows][count] = multiplicity
    total = Counter()
    for counts in by_depth.values():
        assert counts["checked"] == counts["types"] * len(TRIPLES)
        counts["legal"] += 0
        counts["forbidden"] = counts["checked"] - counts["legal"]
        for mode in MODES:
            counts[f"forbidden_matching_{mode}"] += 0
        total.update(counts)
    results = {}
    for mode in MODES:
        assert sum(positives[mode].values()) == total["legal"]
        assert sum(collisions[mode].values()) == total[f"forbidden_matching_{mode}"]
        results[mode] = {
            "distinct_legal_profiles": len(earliest[mode]),
            "conflicting_profiles": len(collisions[mode]),
            "forbidden_triples_matching_legal_profile": sum(collisions[mode].values()),
            "physical_types_with_false_matches": len(false_types[mode]),
            "sufficient_at_width_twenty": not collisions[mode],
            "all_conflicting_profiles": [
                {"profile_hex": reader.encode(mode, key), "legal_occurrences": positives[mode][key],
                 "forbidden_occurrences": occurrences}
                for key, occurrences in sorted(collisions[mode].items())
            ],
            "smallest_witness": witness(census, reader, mode, smallest[mode]),
        }
    for record, rows in zip(
        results[ROWS]["all_conflicting_profiles"], sorted(collisions[ROWS]), strict=True
    ):
        record["legal_occurrences_by_d4_count"] = dict(sorted(legal_counts_at_four[rows].items()))
        record["forbidden_occurrences_by_d4_count"] = dict(sorted(wrong_counts_at_four[rows].items()))
    return {
        "width": WIDTH, "triples_per_type": len(TRIPLES), "primary_description": PARITY,
        "preregistration_sha256": hashlib.sha256(PREREGISTRATION.read_bytes()).hexdigest(),
        "population_producer_sha256": PRODUCER_SHA, "frozen_reader_sha256": READER_SHA,
        "witness_order": "minimum maximum junction count, then sum, then physical indices and operands",
        "joint_rows_code": "three opposite entries then the jointly ordered exterior columns",
        "direct_six_order_cross_checks": total["legal"] + total["forbidden_passing_row_histogram_prefilter"],
        "total": dict(total),
        "by_junction_count": {str(depth): dict(counts) for depth, counts in sorted(by_depth.items())},
        "results": results,
        "controls": {"known_width_nineteen_negative": width19, "width_twenty_relabeling": relabeled},
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
