"""Exhaust the specified controls using exact, candidate-marked retained tables."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from functools import cache
from itertools import combinations
from math import comb
from pathlib import Path
from random import Random

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CHECK_CORE = (
    ROOT / "proofs/VARIABLE-OUTPUT-READER-20261118-001C"
    / "VARIABLE-OUTPUT-READER-20261118-001C-P001_triple_inverse/check_core.py"
)
CORE_SHA = "2499b1bd43e3af655a599e3216ae42a138b1c1e0e501afb9ed70c4f9c7ed5750"


@cache
def inherited():
    assert hashlib.sha256(CHECK_CORE.read_bytes()).hexdigest() == CORE_SHA
    spec = importlib.util.spec_from_file_location("separator_inverse_source", CHECK_CORE)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def scopes(supports):
    return dict(enumerate(supports))


def actual_triples(supports):
    scout, _, rules = inherited().inherited().inherited()
    return frozenset(tuple(sorted(choice)) for choice in scout.actual_menu(rules, scopes(supports))
                     if len(choice) == 3)


def incidence_graph(supports, width):
    """Encode the physical bipartite incidence graph, including loose bits."""
    adjacency = [0] * (width + len(supports))
    for junction, support in enumerate(supports, start=width):
        for bit in support:
            adjacency[junction] |= 1 << bit
            adjacency[bit] |= 1 << junction
    assert all(adjacency) and all(1 <= row.bit_count() <= 2 for row in adjacency[:width])
    return tuple(adjacency)


def graph_components(adjacency, erased=0):
    unseen = ((1 << len(adjacency)) - 1) ^ erased
    while unseen:
        frontier = unseen & -unseen
        unseen ^= frontier
        component = frontier
        while frontier:
            first = frontier & -frontier
            frontier ^= first
            next_nodes = adjacency[first.bit_length() - 1] & unseen
            unseen ^= next_nodes
            component |= next_nodes
            frontier |= next_nodes
        yield component


def incidence_deletions(adjacency, width):
    mask = (1 << width) - 1
    baseline = tuple(sorted(group & mask for group in graph_components(adjacency)))
    partitions = {}
    for bit in range(width):
        if adjacency[bit].bit_count() == 1:
            continue  # Deleting a leaf cannot split its connected component.
        bit_word = 1 << bit
        original = next(group for group in baseline if group & bit_word)
        parts = tuple(sorted(group & original for group in graph_components(adjacency, bit_word)
                             if group & original))
        if len(parts) > 1:
            partitions[bit] = parts
    return baseline, partitions


def physical_parts(supports, width, adjacency, separators):
    core = inherited()
    erased = core.bitmask(separators)
    mask = (1 << width) - 1
    result = {}
    for component in graph_components(adjacency, erased):
        active = tuple(core.bits(component & mask))
        if len(active) < 3:
            continue
        junctions = tuple(core.bits(component >> width))
        selected = tuple(supports[j] for j in junctions)
        kept = tuple(sorted({bit for support in selected for bit in support}))
        result[kept, active] = selected
    return result


@cache
def remeasure_pruned(supports):
    core = inherited()
    return core.actual_scalar_table(scopes(supports)), actual_triples(supports)


@dataclass(frozen=True)
class PhysicalCase:
    width: int
    label: str
    supports: tuple
    history: tuple


@dataclass(frozen=True)
class Occurrence:
    source: PhysicalCase
    kept: tuple
    legal: frozenset


@dataclass
class Group:
    rows: tuple
    active: tuple
    occurrences: list = field(default_factory=list)
    legal_counts: Counter = field(default_factory=Counter)


def check_source(case, rows, menu, groups, stats, boundary_controls):
    core = inherited()
    width, supports = case.width, case.supports
    adjacency = incidence_graph(supports, width)
    physical, true_cuts = incidence_deletions(adjacency, width)
    finite, cuts = core.scalar_cuts(rows)
    assert tuple(sorted(finite)) == physical and cuts == true_cuts, (case, cuts, true_cuts)
    scalar_blocks = tuple(core.active_groups(finite, cuts))
    real_blocks = physical_parts(supports, width, adjacency, true_cuts)
    assert set(scalar_blocks) == real_blocks.keys(), (case, scalar_blocks, real_blocks)

    stats["physical_types"] += 1
    stats["single_bit_deletions"] += width
    stats["physical_and_scalar_separators"] += len(cuts)
    stats["all_named_triples"] += comb(width, 3)
    stats["marked_separator_rejections"] += comb(width, 3) - comb(width - len(cuts), 3)
    survivors = 0
    found_legal = 0
    for kept, active in scalar_blocks:
        selected = real_blocks[kept, active]
        lookup = {bit: i for i, bit in enumerate(kept)}
        new_active = tuple(lookup[bit] for bit in active)
        local_allowed = frozenset(new_active)
        original_allowed = frozenset(active)
        legal = frozenset(tuple(lookup[bit] for bit in mark) for mark in menu if set(mark) <= original_allowed)
        reduced = core.restrict(rows, kept)
        if selected == supports:
            assert kept == tuple(range(width)) and reduced == rows
            local_menu = menu
        else:
            stats["genuinely_pruned_blocks"] += 1
            local_scopes = tuple(sorted(tuple(sorted(lookup[bit] for bit in support)) for support in selected))
            local_rows, local_menu = remeasure_pruned(local_scopes)
            assert local_rows == reduced, (case, kept)
            stats["retained_unordered_entries_verified_against_remeasuring"] += comb(len(kept), 2)
            uses = Counter(bit for support in local_scopes for bit in support)
            boundary = frozenset(range(len(kept))) - local_allowed
            assert all(uses[i] == 1 and adjacency[kept[i]].bit_count() == 2 for i in boundary)
            assert all(uses[i] == adjacency[kept[i]].bit_count() for i in local_allowed)
            now_loose = set(local_menu) - legal
            assert all(set(mark) & boundary and tuple(kept[i] for i in mark) not in menu
                       for mark in now_loose)
            stats["locally_allowed_but_screened_out_boundary_marks"] += len(now_loose)
            if now_loose and width not in boundary_controls:
                planted = min(now_loose)
                boundary_controls[width] = {
                    "source": case.label,
                    "history": case.history,
                    "junction_supports": supports,
                    "boundary_bits_in_original_names": tuple(kept[i] for i in sorted(boundary)),
                    "mark_in_original_names": tuple(kept[i] for i in planted),
                    "mark_in_local_names": planted,
                    "kept_bits": kept,
                    "local_supports": local_scopes,
                    "local_rows_hex": tuple(row.hex() for row in local_rows),
                    "originally_legal": False,
                    "legal_after_pruning": True,
                }
        assert legal == {mark for mark in local_menu if set(mark) <= local_allowed}, (case, kept)
        occurrence = Occurrence(case, kept, legal)
        key = reduced, new_active
        if key not in groups:
            groups[key] = Group(reduced, new_active)
        group = groups[key]
        group.occurrences.append(occurrence)
        group.legal_counts.update(legal)
        stats["retained_block_occurrences"] += 1
        survivors += comb(len(active), 3)
        found_legal += len(legal)
    assert found_legal == len(menu), case
    stats["surviving_triples"] += survivors
    stats["legal_of_surviving_triples"] += found_legal
    stats["forbidden_of_surviving_triples"] += survivors - found_legal
    stats["mixed_side_rejections_without_marked_separator"] = (
        stats["all_named_triples"] - stats["marked_separator_rejections"] - stats["surviving_triples"]
    )


def archived_sources():
    core = inherited()
    transfer = core.inherited()
    for width in (19, 20):
        producer = transfer.producer(19) if width == 19 else transfer
        for index, measured in enumerate(producer.width_records()):
            supports = tuple(measured.fixture.checks().values())
            case = PhysicalCase(width, f"width_{width}_type_{index}", supports, measured.fixture.history)
            rows = core.matrix_from_pairs(measured.table, width)
            menu = frozenset(tuple(sorted(choice)) for choice in measured.menu if len(choice) == 3)
            yield case, rows, menu, None

    data = (CHECK_CORE.parent / "witness.json").read_bytes()
    assert hashlib.sha256(data).hexdigest() == core.GRAFT_SHA
    witnesses = json.loads(data)
    for name in ("padded_witness", "exact_count_witness"):
        witness = witnesses[name]
        for side_name, expected in (("legal_side", True), ("forbidden_side", False)):
            side = witness[side_name]
            checks = core.literal_history(side)
            supports = tuple(checks.values())
            case = PhysicalCase(witness["width"], f"{name}/{side_name}", supports, tuple(side["history"]))
            rows = core.actual_scalar_table(checks)
            menu = actual_triples(supports)
            marked = tuple(sorted(side["marked"]))
            assert (marked in menu) == expected
            assert len(rows) == witness["width"]
            yield case, rows, menu, marked


@cache
def twin_labels(rows):
    """Any two members of a class can be transposed while fixing other bits."""
    labels = []
    for i in range(len(rows)):
        for j, root in enumerate(labels):
            if root == j and rows[i][:j] + rows[i][j + 1:i] + rows[i][i + 1:] == (
                rows[j][:j] + rows[j][j + 1:i] + rows[j][i + 1:]
            ):
                labels.append(j)
                break
        else:
            labels.append(i)
    return tuple(labels)


def refine(rows, cells):
    while True:
        blocks = []
        for cell in cells:
            signatures = defaultdict(list)
            if len(cell) == 1:
                blocks.append(cell)
                continue
            for i in cell:
                key = tuple(bytes(sorted(rows[i][j] for j in other)) for other in cells)
                signatures[key].append(i)
            blocks.extend(tuple(signatures[key]) for key in sorted(signatures))
        if len(blocks) == len(cells):
            return blocks
        cells = blocks


@cache
def exact_form(rows, marked):
    """Canonicalize all pair entries with only mark membership as a color.

    Refinement uses multisets and therefore commutes with every table relabeling.
    The remaining branches try all distinct first choices in a pivot cell.
    Only transpositions of genuine twins within that cell are omitted.
    """
    twins = twin_labels(rows)
    outside = tuple(i for i in range(len(rows)) if i not in marked)
    start = [outside, marked] if outside else [marked]

    def search(cells):
        frozen, pivots = [], []
        for cell in refine(rows, cells):
            if all(twins[i] == twins[cell[0]] for i in cell):
                frozen.extend((i,) for i in cell)
            else:
                pivots.append(len(frozen))
                frozen.append(cell)
        if not pivots:
            order = tuple(cell[0] for cell in frozen)
            return bytes(rows[i][j] for i, j in combinations(order, 2)), order
        pivot = min(pivots, key=lambda i: len(frozen[i]))
        cell = frozen[pivot]
        seen, options = set(), []
        for lead in cell:
            if twins[lead] in seen:
                continue
            seen.add(twins[lead])
            remaining = tuple(i for i in cell if i != lead)
            options.append(search(frozen[:pivot] + [(lead,), remaining] + frozen[pivot + 1:]))
        return min(options)

    return search(start)


def verify_map(first, second, marks_from, marks_to, mapping):
    assert sorted(mapping) == list(range(len(first))) and len(first) == len(second)
    assert {mapping[i] for i in marks_from} == set(marks_to)
    assert all(first[i][j] == second[mapping[i]][mapping[j]]
               for i in range(len(first)) for j in range(len(first)))


def exact_map(first, second, marks_from, marks_to):
    if len(first) != len(second):
        return None
    left, left_order = exact_form(first, marks_from)
    right, right_order = exact_form(second, marks_to)
    if left != right:
        return None
    by_left = dict(zip(left_order, right_order, strict=True))
    mapping = tuple(by_left[i] for i in range(len(first)))
    verify_map(first, second, marks_from, marks_to, mapping)
    return mapping


def mark_stamp(rows, histograms, marked):
    a, b, c = marked
    opposite = rows[b][c], rows[a][c], rows[a][b]
    size_and_distances = len(rows), tuple(sorted(opposite))
    histograms_aligned_to_distances = tuple(sorted(zip(opposite, (histograms[a], histograms[b], histograms[c]))))
    return size_and_distances, histograms_aligned_to_distances


def example(group, occurrence, mark):
    case = occurrence.source
    return {
        "source": case.label, "width": case.width, "history": case.history,
        "junction_supports": case.supports, "retained_original_names": occurrence.kept,
        "marked_original_names": tuple(occurrence.kept[i] for i in mark),
        "marked_local_names": mark, "legal": mark in occurrence.legal,
        "unmarked_boundary_local_names_for_grading_only": tuple(i for i in range(len(group.rows))
                                                               if i not in group.active),
        "all_retained_rows_hex": tuple(row.hex() for row in group.rows),
    }


@dataclass
class MarkedClass:
    representative: tuple
    members: list = field(default_factory=list)
    widths: set = field(default_factory=set)


def compare_survivors(groups):
    """Only reject a comparison early with a necessary invariant of a full map."""
    positive_classes = defaultdict(dict)
    receipts = []
    stats = Counter()
    by_width = defaultdict(Counter)
    examples = {}
    for group in groups.values():
        histograms = tuple(bytes(sorted(row)) for row in group.rows)
        receipts.append((group, histograms))
        for mark, weight in sorted(group.legal_counts.items()):
            items = [item for item in group.occurrences if mark in item.legal]
            assert weight == len(items)
            stamp, encoding = mark_stamp(group.rows, histograms, mark), exact_form(group.rows, mark)[0]
            classes = positive_classes[stamp]
            stats["positive_group_inputs_canonicalized"] += 1
            if encoding not in classes:
                classes[encoding] = MarkedClass((group, items[0], mark))
            marked_class = classes[encoding]
            left, representative, first_mark = marked_class.representative
            mapping = exact_map(left.rows, group.rows, first_mark, mark)
            assert mapping is not None
            stats["positive_group_input_maps_verified_entry_by_entry"] += 1
            for item in items:
                width = item.source.width
                marked_class.members.append((group, item, mark))
                marked_class.widths.add(width)
                by_width[width]["legal_occurrences"] += 1
                if width != representative.source.width and "between_source_widths" not in examples:
                    examples["between_source_widths"] = {
                        "left": example(left, representative, first_mark), "right": example(group, item, mark),
                        "exact_retained_bijection": mapping, "whole_input_equal_up_to_relabeling": False,
                    }
                if (left is group and item == representative and first_mark != mark
                        and "different_marks_in_one_source" not in examples):
                    examples["different_marks_in_one_source"] = {
                        "left": example(left, representative, first_mark), "right": example(group, item, mark),
                        "exact_retained_automorphism": mapping,
                    }
                if {mapping[i] for i in left.active} != set(group.active):
                    stats["legal_occurrences_with_chosen_map_moving_a_boundary_role"] += 1
                    if "boundary_role_moves" not in examples:
                        examples["boundary_role_moves"] = {
                            "left": example(left, representative, first_mark), "right": example(group, item, mark),
                            "exact_retained_bijection": mapping,
                        }

    first_stage = defaultdict(set)
    for distances, histograms in positive_classes:
        first_stage[distances].add(histograms)

    stats["opposite_color_exact_classes"] = 0
    stats["opposite_color_named_forbidden_occurrences"] = 0
    stats["forbidden_group_inputs_canonicalized"] = 0
    stats["opposite_color_occurrence_pairs"] = 0
    stats["opposite_color_pairs_also_matching_before_pruning"] = 0
    counterexamples = {}
    opposite_classes = set()
    possible_width_pairs = Counter()
    widths_by_stamp = {
        stamp: set().union(*(item.widths for item in classes.values()))
        for stamp, classes in positive_classes.items()
    }
    for group, histograms in receipts:
        for item in group.occurrences:
            by_width[item.source.width]["forbidden_passed_necessary_filter"] += 0
            by_width[item.source.width]["opposite_color_named_forbidden_occurrences"] += 0
        named_count = len(group.occurrences)
        table = group.rows
        for a, b, c in combinations(group.active, 3):
            stats["numbered_group_triples"] += 1
            forbidden = named_count - group.legal_counts[a, b, c]
            if not forbidden:
                continue
            opposite = table[b][c], table[a][c], table[a][b]
            distances = len(table), tuple(sorted(opposite))
            allowed = first_stage.get(distances)
            if not allowed:
                continue
            key = tuple(sorted(zip(opposite, (histograms[a], histograms[b], histograms[c]))))
            if key not in allowed:
                continue
            mark = a, b, c
            stats["forbidden_group_inputs_canonicalized"] += 1
            stats["forbidden_named_occurrences_passing_necessary_filter"] += forbidden
            bad_items = [item for item in group.occurrences if mark not in item.legal]
            assert len(bad_items) == forbidden
            absent = Counter(item.source.width for item in bad_items)
            for width, count in absent.items():
                by_width[width]["forbidden_passed_necessary_filter"] += count
                for positive_width in widths_by_stamp[distances, key]:
                    possible_width_pairs[width, positive_width] += count
            encoding = exact_form(table, mark)[0]
            matched = positive_classes[distances, key].get(encoding)
            if matched is None:
                continue
            class_key = distances, key, encoding
            opposite_classes.add(class_key)
            stats["opposite_color_named_forbidden_occurrences"] += forbidden
            for width, count in absent.items():
                by_width[width]["opposite_color_named_forbidden_occurrences"] += count
            for first_group, good, first_mark in matched.members:
                mapping = exact_map(first_group.rows, table, first_mark, mark)
                assert mapping is not None
                first_table = remeasure_pruned(good.source.supports)[0]
                for bad in bad_items:
                    second_table = remeasure_pruned(bad.source.supports)[0]
                    full = exact_map(first_table, second_table, tuple(good.kept[i] for i in first_mark),
                                     tuple(bad.kept[i] for i in mark))
                    stats["opposite_color_occurrence_pairs"] += 1
                    stats["opposite_color_pairs_also_matching_before_pruning"] += full is not None
                    if class_key not in counterexamples:
                        counterexamples[class_key] = {
                            "legal": example(first_group, good, first_mark), "forbidden": example(group, bad, mark),
                            "retained_bijection": mapping, "whole_input_bijection": full,
                        }
    stats["opposite_color_exact_classes"] = len(opposite_classes)
    all_positive_classes = [item for classes in positive_classes.values() for item in classes.values()]
    stats["exact_legal_classes"] = len(all_positive_classes)
    stats["classes_shared_between_physical_types"] = sum(len({x.source.label for _, x, _ in item.members}) > 1
                                                        for item in all_positive_classes)
    stats["classes_shared_between_source_widths"] = sum(len(item.widths) > 1 for item in all_positive_classes)
    stats["legal_classes_per_width"] = dict(Counter(width for item in all_positive_classes for width in item.widths))
    width_pairs = Counter((left, right) for item in all_positive_classes for left, right in combinations(sorted(item.widths), 2))
    return {
        "grouped_numbered_tables_and_active_sets": len(groups), **stats,
        "by_width": {width: dict(values) for width, values in by_width.items()},
        "exact_legal_classes_shared_per_width_pair": {f"{a}/{b}": k for (a, b), k in width_pairs.items()},
        "filter_hits_by_forbidden_then_legal_source_width": {f"{a}/{b}": k for (a, b), k in possible_width_pairs.items()},
        "opposite_color_witnesses": list(counterexamples.values()),
        "positive_map_examples": examples,
    }


def nx_map(first, second, marks_from, marks_to):
    def graph(rows, marked):
        result = nx.Graph()
        result.add_nodes_from((i, {"marked": i in marked}) for i in range(len(rows)))
        result.add_edges_from((i, j, {"value": rows[i][j]}) for i, j in combinations(range(len(rows)), 2))
        return result

    matcher = nx.algorithms.isomorphism.GraphMatcher(
        graph(first, marks_from), graph(second, marks_to),
        node_match=lambda a, b: a["marked"] == b["marked"],
        edge_match=lambda a, b: a["value"] == b["value"],
    )
    if matcher.is_isomorphic():
        mapping = tuple(matcher.mapping[i] for i in range(len(first)))
        verify_map(first, second, marks_from, marks_to, mapping)
        return mapping
    return None


def synthetic_controls(witness):
    core = inherited()
    small = ((0, 1, 2), (0, 3, 4))
    rows = core.actual_scalar_table(scopes(small))
    physical, true_cuts = incidence_deletions(incidence_graph(small, 5), 5)
    assert core.scalar_cuts(rows) == (physical, true_cuts) and set(true_cuts) == {0}
    assert rows[1][3] == rows[1][0] + rows[0][3] - 1 == 3
    assert core.retained_part(rows, (0, 1, 2)) is None
    assert core.retained_part(rows, (1, 2, 3)) is None
    planted = {}
    for category, bit, edits in (
        ("missing", 0, ((1, 3, 2),)),
        ("artificial", 1, ((2, 0, 3), (2, 3, 4), (2, 4, 4))),
    ):
        changed = list(map(bytearray, rows))
        for i, j, new in edits:
            assert rows[i][j] != new
            changed[i][j] = changed[j][i] = new
        scalar = core.scalar_cuts(tuple(map(bytes, changed)))[1]
        assert scalar != true_cuts
        assert (bit in true_cuts and bit not in scalar) if category == "missing" else (
            bit in scalar and bit not in true_cuts
        )
        planted[category] = {"cut_bit": bit, "changed_entries": edits, "disagreement_detected": True}
    disconnected = ((0, 1, 2), (3, 4, 5))
    data = core.actual_scalar_table(scopes(disconnected))
    assert core.scalar_cuts(data) == incidence_deletions(incidence_graph(disconnected, 6), 6)
    assert data[0][3] == core.INFINITY and core.retained_part(data, (0, 1, 3)) is None
    assert core.retained_part(data, (0, 1, 2)) == (0, 1, 2)

    case, original, original_menu, mark = witness
    permutation = list(range(case.width))
    Random(13513).shuffle(permutation)
    changed_supports = tuple(tuple(sorted(permutation[i] for i in support)) for support in case.supports)
    renamed = core.actual_scalar_table(scopes(changed_supports))
    renamed_mark = tuple(sorted(permutation[i] for i in mark))
    renamed_menu = actual_triples(changed_supports)
    assert renamed_menu == {tuple(sorted(permutation[i] for i in old)) for old in original_menu}
    verify_map(original, renamed, mark, renamed_mark, permutation)
    true_blocks, renamed_blocks = (core.scalar_cuts(table)[1] for table in (original, renamed))
    permute_mask = lambda mask: core.bitmask(permutation[i] for i in core.bits(mask))
    assert renamed_blocks == {permutation[i]: tuple(sorted(permute_mask(side) for side in sides))
                              for i, sides in true_blocks.items()}
    first_keep, second_keep = (core.retained_part(original, mark), core.retained_part(renamed, renamed_mark))
    assert set(second_keep) == {permutation[i] for i in first_keep}
    first = core.restrict(original, first_keep)
    second = core.restrict(renamed, second_keep)
    first_mark = tuple(first_keep.index(i) for i in mark)
    second_mark = tuple(second_keep.index(i) for i in renamed_mark)
    found = exact_map(first, second, first_mark, second_mark)
    direct = nx_map(first, second, first_mark, second_mark)
    assert found is not None and direct is not None and first != second
    assert exact_form(first, first_mark)[0] == exact_form(first, tuple(reversed(first_mark)))[0]
    i, j = next(combinations((k for k in range(len(first)) if k not in first_mark), 2))
    edited = list(map(bytearray, first))
    edited[i][j] = edited[j][i] = 3 if first[i][j] == 2 else 2
    edited = tuple(map(bytes, edited))
    assert all(first[k] == edited[k] for k in first_mark)
    assert exact_map(first, edited, first_mark, first_mark) is None
    assert nx_map(first, edited, first_mark, first_mark) is None

    wrong_mark = next(mark for mark in combinations(range(len(first)), 3)
                      if exact_map(first, first, first_mark, mark) is None)
    assert nx_map(first, first, first_mark, wrong_mark) is None

    renamed_history = tuple({
        **move, "consumed": sorted(permutation[i] for i in move["consumed"]),
        "fresh": sorted(permutation[i] for i in move["fresh"]),
    } for move in case.history)
    planted_case = PhysicalCase(case.width, "literal_relabel_with_intentionally_wrong_grade",
                                changed_supports, renamed_history)
    positive = Group(first, first_mark, [Occurrence(case, first_keep, frozenset({first_mark}))],
                     Counter({first_mark: 1}))
    error = Group(second, second_mark, [Occurrence(planted_case, second_keep, frozenset())])
    planted_conflict = compare_survivors({0: positive, 1: error})
    assert planted_conflict["opposite_color_exact_classes"] == 1
    assert planted_conflict["opposite_color_occurrence_pairs"] == 1
    assert planted_conflict["opposite_color_pairs_also_matching_before_pruning"] == 1
    planted_map = planted_conflict["opposite_color_witnesses"][0]
    assert mark in original_menu and renamed_mark in renamed_menu
    return {
        "two_stars": {"physical_and_scalar_separator": 0, "cross_distance_via_separator": 3,
                      "marked_separator_rejected": True, "mixed_side_mark_rejected": True},
        "planted_scalar_cut_errors": planted,
        "disconnected_infinite_pairs": {"cross_component_mark_rejected": True, "within_component_mark_kept": True},
        "literal_relabel": {
            "source": case.label, "permutation_of_original_bits": permutation,
            "transported_every_cut_and_legal_choice": True,
            "mark_order_independent": True,
            "first_kept": first_keep, "second_kept": second_keep,
            "canonical_map": found, "independent_weighted_graph_map": direct,
        },
        "off_mark_entry_change": {
            "pair": (i, j), "original": first[i][j], "edited": edited[i][j],
            "all_three_marked_rows_unchanged": True, "both_exact_matchers_rejected": True,
        },
        "different_mark_on_same_table": {
            "original_mark": first_mark, "substituted_mark": wrong_mark,
            "both_exact_matchers_rejected": True,
        },
        "planted_opposite_grade_on_true_relabel": {
            "actual_eligibility_in_both_sources": True, "intentionally_reported_eligibility": (True, False),
            "exact_matcher_detected_conflict": True, "retained_match": planted_map["retained_bijection"],
            "whole_input_match": planted_map["whole_input_bijection"],
        },
    }


def run():
    assert (ROOT / "research/VARIABLE-OUTPUT-READER-20261118-001D/preregistration.md").is_file()
    groups, by_width, boundary_examples = {}, defaultdict(Counter), {}
    grafts = defaultdict(list)
    core = inherited()
    for case, rows, menu, mark in archived_sources():
        stats = by_width[case.width]
        check_source(case, rows, menu, groups, stats, boundary_examples)
        if mark is not None:
            kept = core.retained_part(rows, mark)
            local = tuple(kept.index(i) for i in mark)
            grafts[case.width].append((case, rows, menu, mark, kept, core.restrict(rows, kept), local))
    result = compare_survivors(groups)
    assert {width: by_width[width]["physical_types"] for width in by_width} == {19: 8191, 20: 19414, 27: 2, 28: 2}
    assert (by_width[19]["surviving_triples"], by_width[20]["surviving_triples"]) == (3416901, 9671289)
    assert (by_width[19]["legal_of_surviving_triples"], by_width[20]["legal_of_surviving_triples"]) == (2381, 6358)
    assert sum(stats["surviving_triples"] for stats in by_width.values()) == sum(
        comb(len(group.active), 3) * len(group.occurrences) for group in groups.values()
    )
    for width, stats in by_width.items():
        assert stats["legal_of_surviving_triples"] == result["by_width"][width]["legal_occurrences"]

    designated = {}
    for width, (left, right) in grafts.items():
        left_case, left_rows, left_menu, left_mark, left_kept, left_data, left_local = left
        right_case, right_rows, right_menu, right_mark, right_kept, right_data, right_local = right
        assert left_mark in left_menu and right_mark not in right_menu
        retained_map = exact_map(left_data, right_data, left_local, right_local)
        full_map = exact_map(left_rows, right_rows, left_mark, right_mark)
        assert (retained_map is not None) == (nx_map(left_data, right_data, left_local, right_local) is not None)
        designated[width] = {
            "legal_source": left_case.label, "forbidden_source": right_case.label,
            "legal_kept_bits": left_kept, "forbidden_kept_bits": right_kept,
            "legal_marked_bits": left_mark, "forbidden_marked_bits": right_mark,
            "retained_bijection": retained_map, "whole_input_bijection": full_map,
        }
    assert boundary_examples
    return {
        "scope": "Archived complete width-19 and width-20 rosters and all triples of four literal branch fixtures",
        "source_core_sha256": CORE_SHA,
        "marking": "Only unordered membership in the three chosen bits. Boundary roles are excluded from isomorphism.",
        "comparison": "A necessary marked-row histogram filter precedes canonical comparison of every retained pair entry.",
        "source_eligibility": "Eligibility in original incidence. Pruned incidence is graded separately after the cut screen.",
        "coverage_by_original_width": {width: dict(values) for width, values in by_width.items()},
        "full_marked_comparison": result,
        "designated_branch_pairs": designated,
        "pruning_can_make_screened_boundary_marks_legal": boundary_examples,
        "independent_and_synthetic_controls": synthetic_controls(grafts[27][0][:4]),
        "scope_limit": "This finite check leaves unrestricted reachable widths open.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Replace controls.json with the checked result")
    args = parser.parse_args()
    record = json.dumps(run(), sort_keys=True, indent=2) + "\n"
    if args.write:
        (HERE / "controls.json").write_text(record)
    else:
        assert (HERE / "controls.json").read_text() == record
        print("Exact retained-table controls reproduced.")
