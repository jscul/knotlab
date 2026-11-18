"""Exploratory comparison of scalar separators and trimmed triple observations."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import cache
from itertools import combinations, permutations
from math import comb
from pathlib import Path


HERE = Path(__file__).resolve().parent
PARITY_CHECK = HERE / "check_parity.py"
PARITY_SHA = "49020cc4c6f6f1fdd723a777495fc7a3711c4eae90dc8a05b39778bf6b734342"
GRAFT_SHA = "7685dbb6636b3611a6e8a1f090bba446365feeaad00f22437594bfa3b6fd93ca"
WIDTHS = (19, 20)
INFINITY = 255
ROWS, PARITY, COUNT = "three_rows", "three_rows_and_d4_parity", "three_rows_and_d4_count"
MODES = (ROWS, PARITY, COUNT)


@cache
def inherited():
    assert hashlib.sha256(PARITY_CHECK.read_bytes()).hexdigest() == PARITY_SHA
    spec = importlib.util.spec_from_file_location("exploratory_core_populations", PARITY_CHECK)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def bits(mask):
    while mask:
        least = mask & -mask
        yield least.bit_length() - 1
        mask ^= least


def bitmask(indices):
    return sum(1 << i for i in indices)


def matrix_from_pairs(table, width):
    assert len(table) == comb(width, 2)
    rows = [bytearray(width) for _ in range(width)]
    for (i, j), value in table.items():
        assert value is None or 2 <= value < width
        rows[i][j] = rows[j][i] = INFINITY if value is None else value
    return tuple(map(bytes, rows))


def finite_components(rows):
    """Group mutually reachable bits before any arithmetic on bond values."""
    unseen = (1 << len(rows)) - 1
    components = []
    while unseen:
        root = (unseen & -unseen).bit_length() - 1
        group = bitmask(i for i, value in enumerate(rows[root]) if value != INFINITY)
        assert group & ~unseen == 0
        # In these examples finite reachability is already an equivalence relation.
        assert all(bitmask(j for j, value in enumerate(rows[i]) if value != INFINITY) == group
                   for i in bits(group))
        unseen ^= group
        components.append(group)
    return tuple(components)


def mismatch_components(rows, group, cut):
    """Compute connected components of the nonadditivity graph without materializing it."""
    along = rows[cut]
    unseen = group ^ (1 << cut)
    groups = []
    while unseen:
        root = (unseen & -unseen).bit_length() - 1
        reached = 1 << root
        unseen ^= reached
        frontier = [root]
        while unseen and frontier:
            i = frontier.pop()
            source = rows[i]
            offset = along[i] - 1
            following = [j for j in bits(unseen) if source[j] != offset + along[j]]
            added = bitmask(following)
            unseen ^= added
            reached |= added
            frontier.extend(following)
        groups.append(reached)
    return tuple(sorted(groups))


def scalar_cuts(rows):
    """Retain cuts inside a finite reachability component."""
    if any(INFINITY in row for row in rows):
        finite = finite_components(rows)
    else:
        finite = ((1 << len(rows)) - 1,)
    cuts = {}
    for group in finite:
        for t in bits(group):
            parts = mismatch_components(rows, group, t)
            if len(parts) > 1:
                cuts[t] = parts
    return finite, cuts


def ordinary_deletion(checks, width):
    """Compute actual bit partitions by deleting a proposed shared identity."""
    owners = [[] for _ in range(width)]
    ordinary = {i: [] for i in checks}
    for vertex, support in checks.items():
        for bit in support:
            owners[bit].append(vertex)
    for bit, ends in enumerate(owners):
        assert len(ends) in (1, 2)
        if len(ends) == 2:
            u, v = ends
            ordinary[u].append((v, bit))
            ordinary[v].append((u, bit))

    def vertices_from(root, erased):
        reached, pending = {root}, [root]
        while pending:
            for neighbor, bit in ordinary[pending.pop()]:
                if bit != erased and neighbor not in reached:
                    reached.add(neighbor)
                    pending.append(neighbor)
        return reached

    remaining = set(checks)
    baseline = []
    cuts = {}
    while remaining:
        vertices = vertices_from(min(remaining), None)
        remaining -= vertices
        group = bitmask(bit for bit, ends in enumerate(owners) if ends[0] in vertices)
        baseline.append(group)
        for t in bits(group):
            if len(owners[t]) == 1:
                continue
            left, right = owners[t]
            side = vertices_from(left, t)
            if right in side:
                continue
            first = bitmask(bit for bit in bits(group) if bit != t and owners[bit][0] in side)
            second = group ^ first ^ (1 << t)
            assert first and second
            cuts[t] = tuple(sorted((first, second)))
    return tuple(sorted(baseline)), cuts


def active_groups(finite, cuts):
    """Group eligible nonseparator bits with the same side of every cut."""
    separator_bits = bitmask(cuts)
    for full in finite:
        local_cuts = {t: parts for t, parts in cuts.items() if full >> t & 1}
        by_sides = defaultdict(list)
        for bit in bits(full & ~separator_bits):
            side_signature = tuple(
                next(part | (1 << t) for part in parts if part >> bit & 1)
                for t, parts in local_cuts.items()
            )
            by_sides[side_signature].append(bit)
        for sides, choices in by_sides.items():
            kept = full
            for side in sides:
                kept &= side
            assert set(bits(kept & ~separator_bits)) == set(choices)
            if len(choices) >= 3:
                yield tuple(bits(kept)), tuple(choices)


def restrict(rows, kept):
    return tuple(bytes(rows[i][j] for j in kept) for i in kept)


@dataclass(frozen=True)
class Occurrence:
    width: int
    index: int
    fixture: object
    names: tuple[int, ...]
    legal: frozenset


@dataclass
class Part:
    rows: tuple[bytes, ...]
    active: tuple[int, ...]
    occurrences: list
    legal_multiplicity: Counter


def format_parts(parts):
    return tuple(tuple(bits(part)) for part in parts)


def diagnostic(fixture, rows, bit, actual, observed, category):
    others = ((1 << len(rows)) - 1) ^ (1 << bit)
    physical = actual.get(bit, (others,))
    inferred = observed.get(bit, (others,))
    crossings = []
    for i, j in combinations(bits(others), 2):
        physically_separate = not any(part >> i & 1 and part >> j & 1 for part in physical)
        numerically_separate = not any(part >> i & 1 and part >> j & 1 for part in inferred)
        if physically_separate != numerically_separate:
            crossings.append({
                "pair": (i, j), "scalar": rows[i][j],
                "scalar_via_cut_minus_one": rows[i][bit] + rows[bit][j] - 1,
            })
    assert crossings
    return {
        "category": category, "history": fixture.history,
        "junction_supports": tuple(fixture.checks().values()), "cut_identity": bit,
        "physical_parts": format_parts(physical), "scalar_parts": format_parts(inferred),
        "pairs_with_disagreed_separation": crossings,
        "full_scalar_rows_hex": [row.hex() for row in rows],
    }


def compare_cuts(fixture, rows, physical, observed, stats, bad_examples):
    stats["physical_separators"] += len(physical)
    stats["scalar_separators"] += len(observed)
    if physical != observed:
        stats["types_with_partition_disagreement"] += 1
    for bit in sorted(physical.keys() | observed.keys()):
        if physical.get(bit) == observed.get(bit):
            continue
        if bit not in physical:
            category = "artificial"
        elif bit not in observed:
            category = "missing"
        else:
            category = "wrong_partition_at_common_cut"
        stats[category] += 1
        if category not in bad_examples:
            bad_examples[category] = diagnostic(fixture, rows, bit, physical, observed, category)


def register_part(parts, fixture, width, case_index, rows, legal, kept, names):
    lookup = {old: i for i, old in enumerate(kept)}
    active_names = set(names)
    choices = frozenset(tuple(lookup[i] for i in triple) for triple in legal if set(triple) <= active_names)
    table = restrict(rows, kept)
    active = tuple(lookup[i] for i in names)
    key = table, active
    part = parts.get(key)
    if part is None:
        part = Part(table, active, [], Counter())
        parts[key] = part
    part.occurrences.append(Occurrence(width, case_index, fixture, kept, choices))
    part.legal_multiplicity.update(choices)
    return len(choices)


def populations():
    all_parts = {}
    by_width = {}
    examples = {}
    transfer = inherited()
    for width in WIDTHS:
        stats, bad_examples = Counter(), {}
        records = transfer.width_records() if width == 20 else transfer.producer(19).width_records()
        for index, measured in enumerate(records):
            fixture = measured.fixture
            checks = fixture.checks()
            rows = matrix_from_pairs(measured.table, width)
            finite, inferred = scalar_cuts(rows)
            baseline, actual = ordinary_deletion(checks, width)
            if tuple(sorted(finite)) != baseline:
                stats["types_with_reachability_disagreement"] += 1
            assert tuple(sorted(finite)) == baseline == ((1 << width) - 1,)
            compare_cuts(fixture, rows, actual, inferred, stats, bad_examples)
            legal = tuple(sorted(tuple(sorted(choice)) for choice in measured.menu if len(choice) == 3))
            stats["types"] += 1
            stats["bit_deletions_checked"] += width
            stats["all_triples"] += comb(width, 3)
            stats["legal_triples"] += len(legal)
            cuts_mask = bitmask(inferred)
            stats["all_triples_containing_scalar_separator"] += comb(width, 3) - comb(width - len(inferred), 3)
            for choice in legal:
                word = bitmask(choice)
                touches = bool(word & cuts_mask)
                straddles = any(t not in choice and all(word & part != word for part in split)
                                for t, split in inferred.items())
                stats["legal_triples_containing_scalar_separator"] += touches
                stats["legal_triples_straddling_scalar_separator"] += straddles
                if touches or straddles:
                    stats["legal_triples_rejected_by_scalar_cuts"] += 1
                    if "rejected_legal_triple" not in bad_examples:
                        bad_examples["rejected_legal_triple"] = {
                            "history": fixture.history, "operands": choice,
                            "cut_identities": sorted(inferred),
                            "scalar_parts_by_cut": {t: format_parts(split) for t, split in inferred.items()},
                            "junction_supports": tuple(checks.values()),
                        }
            recovered = 0
            for kept, active in active_groups(finite, inferred):
                stats["core_occurrences"] += 1
                stats["triples_surviving_scalar_cuts"] += comb(len(active), 3)
                recovered += register_part(all_parts, fixture, width, index, rows, legal, kept, active)
            stats["legal_triples_surviving_scalar_cuts"] += recovered
        assert stats["legal_triples_surviving_scalar_cuts"] + stats["legal_triples_rejected_by_scalar_cuts"] == stats["legal_triples"]
        stats["triples_straddling_without_a_separator_operand"] = (
            stats["all_triples"] - stats["all_triples_containing_scalar_separator"]
            - stats["triples_surviving_scalar_cuts"]
        )
        for key in ("artificial", "missing", "wrong_partition_at_common_cut", "types_with_partition_disagreement"):
            stats[key] += 0
        by_width[str(width)] = dict(stats)
        examples[str(width)] = bad_examples
    return all_parts, by_width, examples


def count_four(rows):
    return sum(row.count(4) for row in rows) // 2


def keys_for_rows(raw, four):
    return raw, (raw, four % 2), (raw, four)


def internals(rows, triple):
    a, b, c = triple
    return rows[b][c], rows[a][c], rows[a][b]


def row_decoration(histograms, triple, opposite):
    return tuple(sorted((distance, histograms[i]) for i, distance in zip(triple, opposite, strict=True)))


def occurrence_record(part, item, local):
    old = tuple(item.names[i] for i in local)
    return {
        "source_width": item.width, "physical_index": item.index,
        "junction_count": len(item.fixture.loose_counts),
        "history": item.fixture.history, "junction_supports": tuple(item.fixture.checks().values()),
        "retained_original_identified_bits": item.names, "marked_triple_on_original_names": old,
        "marked_triple_on_retained_names": local, "legal": local in item.legal,
        "restricted_rows_hex": [row.hex() for row in part.rows],
        "restricted_distance_four_count": count_four(part.rows),
    }


def occurrence_conflict(mode, key, good, bad):
    left_part, left_item, left_triple = good
    right_part, right_item, right_triple = bad
    assert left_triple in left_item.legal and right_triple not in right_item.legal
    mapping = inherited().incident_map(left_part.rows, left_triple, right_part.rows, right_triple)
    return {
        "mode": mode, "canonical_profile": key,
        "legal_side": occurrence_record(left_part, left_item, left_triple),
        "forbidden_side": occurrence_record(right_part, right_item, right_triple),
        "incident_map_on_retained_names": mapping,
    }


def analyze_parts(parts):
    """Evaluate every surviving named choice, grouping only identical numbered data."""
    raw_key = inherited().raw_canonical_rows
    legal_examples = {mode: {} for mode in MODES}
    legal_counts_at_four = defaultdict(Counter)
    filters = defaultdict(set)
    receipts = []
    for part in parts.values():
        four = count_four(part.rows)
        histograms = tuple(bytes(sorted(row)) for row in part.rows)
        receipts.append((part, four, histograms))
        for triple in sorted(part.legal_multiplicity):
            example = next(item for item in part.occurrences if triple in item.legal)
            opp = internals(part.rows, triple)
            filters[tuple(sorted(opp))].add(row_decoration(histograms, triple, opp))
            raw = raw_key(part.rows, triple)
            legal_counts_at_four[raw][four] += part.legal_multiplicity[triple]
            for mode, key in zip(MODES, keys_for_rows(raw, four), strict=True):
                legal_examples[mode].setdefault(key, (part, example, triple))

    stats = Counter()
    bads = {mode: Counter() for mode in MODES}
    bad_counts_at_four = defaultdict(Counter)
    first = {}
    for part, four, histograms in receipts:
        site_count = len(part.occurrences)
        for triple in combinations(part.active, 3):
            stats["unique_numbered_table_and_triple_candidates"] += 1
            stats["named_triple_occurrences_tested"] += site_count
            truth = part.legal_multiplicity[triple]
            stats["legal_occurrences"] += truth
            false_weight = site_count - truth
            stats["forbidden_occurrences"] += false_weight
            if not false_weight:
                continue
            opp = internals(part.rows, triple)
            allowed_hist = filters.get(tuple(sorted(opp)))
            if allowed_hist is None or row_decoration(histograms, triple, opp) not in allowed_hist:
                continue
            stats["after_necessary_row_histogram_filter"] += false_weight
            raw = raw_key(part.rows, triple)
            if raw in legal_examples[ROWS]:
                bad_counts_at_four[raw][four] += false_weight
            for mode, key in zip(MODES, keys_for_rows(raw, four), strict=True):
                if key in legal_examples[mode]:
                    bads[mode][key] += false_weight
                    if mode not in first:
                        bad = next(item for item in part.occurrences if triple not in item.legal)
                        first[mode] = occurrence_conflict(
                            mode, key, legal_examples[mode][key], (part, bad, triple)
                        )
    return {
        "grouped_numbered_tables_with_eligible_subsets": len(parts),
        **stats,
        "observations": {
            mode: {
                "distinct_legal_profiles": len(legal_examples[mode]),
                "conflicting_profiles": len(bads[mode]),
                "forbidden_occurrences_matching_a_legal_profile": sum(bads[mode].values()),
                "first_counterexample": first.get(mode),
            }
            for mode in MODES
        },
        "row_only_conflicting_profiles_at_four": [
            {
                "profile": raw,
                "legal_occurrences_by_count": dict(legal_counts_at_four[raw]),
                "forbidden_occurrences_by_count": dict(bad_counts_at_four[raw]),
            }
            for raw in sorted(bads[ROWS])
        ],
    }


def retained_part(rows, triple):
    finite, cuts = scalar_cuts(rows)
    targets = set(triple)
    options = [keep for keep, eligible in active_groups(finite, cuts) if targets <= set(eligible)]
    if not options:
        return None
    kept, = options
    return kept


def actual_scalar_table(checks):
    scout, _, _ = inherited().inherited()
    width = len(set().union(*checks.values()))
    return matrix_from_pairs(scout.full_table(scout.parity_span(checks), width), width)


def literal_history(side):
    scout, _, rules = inherited().inherited()
    checks = {}
    for move in side["history"]:
        junction = move["junction"]
        consumed, fresh = tuple(move["consumed"]), tuple(move["fresh"])
        users, _ = rules.incidence(checks)
        assert junction == len(checks) and not set(fresh) & users.keys()
        if junction:
            assert len(fresh) in (2, 3)
            assert rules.legal_local_move(checks, consumed, scout.FRESH_FOR_PARENT_TEST)
            assert sorted(users[bit][0] for bit in consumed) == move["parents"]
        else:
            assert len(fresh) == 3 and not consumed
        checks[junction] = tuple(sorted((*consumed, *fresh)))
    assert [sorted(values) for values in side["checks"]] == list(map(list, checks.values()))
    return checks


def exact_graft_controls():
    transfer = inherited()
    witness_path = HERE / "witness.json"
    assert hashlib.sha256(witness_path.read_bytes()).hexdigest() == GRAFT_SHA
    data = json.loads(witness_path.read_text())
    host_path = transfer.FAMILY19 / "near_witness.json"
    assert hashlib.sha256(host_path.read_bytes()).hexdigest() == transfer.NEAR_WITNESS_SHA
    hosts = json.loads(host_path.read_text())
    scout, _, rules = transfer.inherited()
    result = {}
    for name in ("padded_witness", "exact_count_witness"):
        cases = data[name]
        raws, small_raws, counts, small_counts = [], [], [], []
        steps = {}
        for side_name in ("legal_side", "forbidden_side"):
            side = cases[side_name]
            checks = literal_history(side)
            marked = tuple(side["marked"])
            good = frozenset(marked) in scout.actual_menu(rules, checks)
            assert good == (side_name == "legal_side")
            rows = actual_scalar_table(checks)
            assert len(rows) == cases["width"]
            _, numerical = scalar_cuts(rows)
            _, physical = ordinary_deletion(checks, len(rows))
            kept = retained_part(rows, marked)
            raw = transfer.raw_canonical_rows(rows, marked)
            four = count_four(rows)
            assert four == side["distance_four_pairs"]
            details = {
                "marks": marked, "legal": good, "whole_distance_four_count": four,
                "scalar_cuts_agree_with_physical": numerical == physical,
                "scalar_cuts": {i: format_parts(parts) for i, parts in numerical.items()},
            }
            raw_host = hosts[side_name]
            host_checks = dict(enumerate(map(tuple, raw_host["junction_supports"])))
            assert tuple(marked) == tuple(raw_host["marked"])
            host = actual_scalar_table(host_checks)
            assert len(host) == 19 and restrict(rows, tuple(range(19))) == host
            details["all_width_nineteen_host_entries_preserved"] = True
            host_kept = retained_part(host, marked)
            details["same_scalar_retained_part_as_width_nineteen_host"] = kept == host_kept
            details["retained_bits"] = kept
            details["width_nineteen_host_retained_bits"] = host_kept
            details["host_distance_four_count"] = count_four(host)
            if kept is not None:
                cut = restrict(rows, kept)
                reduced = tuple(kept.index(bit) for bit in marked)
                small_raws.append(transfer.raw_canonical_rows(cut, reduced))
                small_counts.append(count_four(cut))
                details["retained_distance_four_count"] = small_counts[-1]
            raws.append(raw)
            counts.append(four)
            steps[side_name] = details
        assert raws[0] == raws[1] and counts[0] % 2 == counts[1] % 2
        assert (counts[0] == counts[1]) == (name == "exact_count_witness")
        result[name] = {
            "width": cases["width"], **steps,
            "whole_profiles_match_even_with_parity": True,
            "restricted_rows_match": len(small_raws) == 2 and small_raws[0] == small_raws[1],
            "restricted_rows_and_parity_match": (
                len(small_raws) == 2 and small_raws[0] == small_raws[1]
                and small_counts[0] % 2 == small_counts[1] % 2
            ),
        }
    return result


def disconnected_control():
    checks = {0: (0, 1, 2), 1: (3, 4, 5)}
    rows = actual_scalar_table(checks)
    observed, cuts = scalar_cuts(rows)
    physical, actual_cuts = ordinary_deletion(checks, 6)
    assert tuple(sorted(observed)) == physical and not cuts and not actual_cuts
    assert rows[0][3] == INFINITY
    assert retained_part(rows, (0, 1, 3)) is None
    assert retained_part(rows, (0, 1, 2)) == (0, 1, 2)
    return {"reachability_components": format_parts(observed), "cross_component_triple_rejected": True}


def planted_cut_controls():
    scout, _, _ = inherited().inherited()
    fixture = scout.Fixture((), (3,), ()).successor((0,), 2)
    checks = fixture.checks()
    rows = actual_scalar_table(checks)
    _, physical = ordinary_deletion(checks, 5)
    assert set(physical) == {0} and scalar_cuts(rows)[1] == physical
    # The first mutation links the true sides by a nonadditive pair. The
    # second forces all pairs across one apparent separation to be additive.
    mutations = (
        ("missing", 0, ((1, 3, 2),)),
        ("artificial", 1, ((2, 0, 3), (2, 3, 4), (2, 4, 4))),
    )
    checked = {}
    for category, t, substitutions in mutations:
        edited = [bytearray(row) for row in rows]
        for i, j, value in substitutions:
            assert rows[i][j] != value
            edited[i][j] = edited[j][i] = value
        table = tuple(map(bytes, edited))
        _, observed = scalar_cuts(table)
        stats, examples = Counter(), {}
        compare_cuts(fixture, table, physical, observed, stats, examples)
        assert stats[category] > 0
        assert (t in physical and t not in observed) if category == "missing" else (
            t in observed and t not in physical
        )
        checked[category] = {
            "expected_cut_identity": t, "altered_pair_entries": substitutions,
            "diagnosis": diagnostic(fixture, table, t, physical, observed, category),
        }
    return checked


def result_record(by_width, examples, result):
    assert result["named_triple_occurrences_tested"] == sum(
        row["triples_surviving_scalar_cuts"] for row in by_width.values()
    )
    assert result["legal_occurrences"] == sum(
        row["legal_triples_surviving_scalar_cuts"] for row in by_width.values()
    )
    return {
        "status": "exploratory",
        "complete_populations": WIDTHS,
        "population_cut_checks": by_width,
        "first_examples_of_false_diagnoses": examples,
        "pooled_surviving_triple_checks": result,
        "known_graft_controls": exact_graft_controls(),
        "unreachable_control": disconnected_control(),
        "planted_incorrect_scalar_table_controls": planted_cut_controls(),
        "width_twenty_predecessor_sha256": PARITY_SHA,
        "graft_source_sha256": GRAFT_SHA,
    }


def run():
    parts, by_width, examples = populations()
    return result_record(by_width, examples, analyze_parts(parts))


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, sort_keys=True))
