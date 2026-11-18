"""Continue the width-20 state-ambiguous sources on permanent bit names."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter
from dataclasses import dataclass
from functools import cache, lru_cache
from hashlib import sha256
from itertools import combinations, product
from math import comb
from pathlib import Path
from time import perf_counter


HERE = Path(__file__).resolve().parent
SPAN_SHA = "ece53f8c0aa3f71c6be5984de374992d11c15bd3f4a20e9ff979d4c57e7cd6a2"
ARCHIVE_SHA = "f6bf1f48a6c59d9062277257e1f727bc458f1441770373e4da6ee5062af5c027"
EXCLUDED = "width_20_type_12350"


@cache
def inherited():
    path = HERE / "check_span_controls.py"
    assert sha256(path.read_bytes()).hexdigest() == SPAN_SHA
    spec = importlib.util.spec_from_file_location("live_twin_predecessor", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@cache
def source_apis():
    archive = inherited()
    scout, rules = archive.scout_and_rules()
    controls = archive.controls()
    return archive, scout, rules, controls, controls.inherited()


def scopes(supports):
    return dict(enumerate(supports))


@dataclass(frozen=True)
class Seed:
    label: str
    history: tuple
    supports: tuple
    loose: int
    shared: int


@dataclass(frozen=True)
class Step:
    parents: tuple
    used: tuple
    fresh: tuple

    def record(self):
        return {"parents": self.parents, "consumed": self.used, "fresh": self.fresh}


@dataclass(frozen=True)
class State:
    width: int
    supports: tuple
    tail: tuple[Step, ...] = ()


def twin_swap(rows, first, second):
    return all(rows[first][j] == rows[second][j] for j in range(len(rows)) if j not in (first, second))


def span_moves(supports, truth, first, second):
    _, scout, _, _, _ = source_apis()
    pair = (1 << first) | (1 << second)
    for support in supports:
        word = scout.mask(support)
        if (word & pair) not in (0, pair) and word ^ pair not in truth:
            return True
    return False


def width_twenty_seeds():
    archive, scout, rules, _, trim = source_apis()
    raw = (HERE / "span_controls.json").read_bytes()
    assert sha256(raw).hexdigest() == ARCHIVE_SHA
    records = json.loads(raw)["full_table_rank_one_extension_controls"]["individual_cases"]
    all_seeds = []
    for record in records:
        if record["reachable_labeled_states"] == 1:
            continue
        fixture = scout.Fixture((), (3,), ())
        ordered_history = tuple((tuple(parents), fresh) for parents, fresh in record["source_history"])
        for parents, fresh in ordered_history:
            assert parents in {candidate for candidate, _ in scout.legal_parent_sets(rules, fixture.checks())}
            fixture = fixture.successor(parents, fresh)
        supports = tuple(fixture.checks().values())
        observed = scout.measure(rules, fixture)
        owners, ordinary = rules.incidence(fixture.checks())
        assert not any(len(choice) == 3 for choice in observed.menu)
        rows = trim.matrix_from_pairs(observed.table, 20)
        assert archive.measure_every_pair(observed.span, 20) == rows
        for a, b in combinations(range(20), 2):
            if not twin_swap(rows, a, b) or not span_moves(supports, observed.span, a, b):
                continue
            assert {len(owners[a]), len(owners[b])} == {1, 2}
            loose, shared = (a, b) if len(owners[a]) == 1 else (b, a)
            holder, = owners[loose]
            assert holder in owners[shared]
            assert rules.loose_ports(owners)[holder] == [loose]
            assert len(ordinary[holder]) == 3
            all_seeds.append(Seed(record["case_id"], ordered_history, supports, loose, shared))
    assert len(all_seeds) == 32 and len({seed.label for seed in all_seeds}) == 24
    assert sum(seed.label == EXCLUDED for seed in all_seeds) == 1
    return tuple(seed for seed in all_seeds if seed.label != EXCLUDED)


def next_moves(current, protected, preserve=False):
    """One literal move per in-holder orbit fixing both tracked names."""
    _, scout, rules, _, _ = source_apis()
    checks = scopes(current.supports)
    for parents, ports in scout.legal_parent_sets(rules, checks):
        options = []
        for available in ports:
            ordinary = tuple(bit for bit in available if bit not in protected)[:1]
            marked = tuple(bit for bit in available if bit in protected)
            options.append(ordinary if preserve else ordinary + marked)
        for used in product(*options):
            assert rules.legal_local_move(checks, used, scout.FRESH_FOR_PARENT_TEST)
            for count in (2, 3):
                fresh = tuple(range(current.width, current.width + count))
                added = tuple(sorted((*used, *fresh)))
                yield State(current.width + count, (*current.supports, added),
                            (*current.tail, Step(parents, used, fresh)))


def actual_menu(current, required=None):
    """Read named triples directly from the physical holders and witnesses."""
    _, _, rules, _, _ = source_apis()
    owners, adjacent = rules.incidence(scopes(current.supports))
    loose = rules.loose_ports(owners)
    if required is not None:
        ends = owners[required]
        if len(ends) != 1:
            return frozenset()
        holder, = ends
        mates = sorted(parent for parent in loose if parent != holder and adjacent[parent] & adjacent[holder])
        candidates = ((holder, b, c) for b, c in combinations(mates, 2))
    else:
        candidates = combinations(sorted(loose), 3)
    menu = set()
    for a, b, c in candidates:
        first, second, third = adjacent[a], adjacent[b], adjacent[c]
        if first & second and first & third and second & third and not first & second & third:
            first_ports = (required,) if required is not None else loose[a]
            menu.update(tuple(sorted(mark)) for mark in product(first_ports, loose[b], loose[c]))
    return frozenset(menu)


@lru_cache(maxsize=256)
def measure(supports, width):
    archive, scout, _, _, _ = source_apis()
    truth = scout.parity_span(scopes(supports))
    return archive.measure_every_pair(truth, width), truth


def retains_tracked(state, seed):
    return all(seed.loose not in step.used for step in state.tail)


def frozen_common_witness(seed):
    """Identify the cases where a fixed common witness forbids every later triple."""
    _, _, rules, _, _ = source_apis()
    owners, ordinary = rules.incidence(scopes(seed.supports))
    live = rules.loose_ports(owners)
    holder, = owners[seed.loose]
    cap, = set(owners[seed.shared]) - {holder}
    # Retaining the sole port of holder freezes all three of its neighbors.
    # An exhausted neighbor can never gain a new neighbor. An old neighbor
    # of it can serve as a future holder only if it has a loose bit now.
    # If every such holder already meets cap, any future pair of mates of
    # holder still has the common witness cap, which forbids their triple.
    directions = {}
    forced = True
    for witness in sorted(ordinary[holder] - {cap}):
        possible_old = sorted((ordinary[witness] - {holder}) & live.keys())
        outside = sorted(set(possible_old) - ordinary[cap])
        directions[witness] = {"loose_bits_on_witness": len(live.get(witness, ())),
                               "other_possible_old_holders": possible_old, "not_adjacent_to_cap": outside}
        if witness in live or outside:
            forced = False
    return {"holder": holder, "common_witness": cap, "other_directions": directions,
            "forbidden_for_every_continuation_retaining_the_bit": forced}


def source_record(state, seed):
    return {
        "source": seed.label, "tracked_loose": seed.loose, "tracked_shared": seed.shared,
        "source_history": seed.history, "continuation": tuple(step.record() for step in state.tail),
        "junction_supports": state.supports, "width": state.width,
    }


def swap_failure(rows, a, b):
    for i in range(len(rows)):
        if i not in (a, b) and rows[a][i] != rows[b][i]:
            return [i, rows[a][i], rows[b][i]]
    return None


def remember(groups, rows, active, old_names, legal, case):
    _, _, _, controls, _ = source_apis()
    index = {i: j for j, i in enumerate(old_names)}
    active = tuple(index[i] for i in active)
    marks = frozenset(tuple(index[i] for i in mark) for mark in legal)
    key = rows, active
    if key not in groups:
        groups[key] = controls.Group(rows, active)
    group = groups[key]
    group.occurrences.append(controls.Occurrence(case, old_names, marks))
    group.legal_counts.update(marks)


def add_readings(state, seed, legal, rows, full, retained):
    _, _, _, controls, trim = source_apis()
    label = seed.label + "/" + str(tuple((step.used, len(step.fresh)) for step in state.tail))
    history = (*seed.history, *(step.record() for step in state.tail))
    case = controls.PhysicalCase(state.width, label, state.supports, history)
    names = tuple(range(state.width))
    remember(full, rows, names, names, legal, case)
    adjacency = controls.incidence_graph(state.supports, state.width)
    physical, actual = controls.incidence_deletions(adjacency, state.width)
    finite, cuts = trim.scalar_cuts(rows)
    assert tuple(sorted(finite)) == physical and cuts == actual, (source_record(state, seed), cuts, actual)
    eligible = set()
    for kept, active in trim.active_groups(finite, cuts):
        valid = frozenset(mark for mark in legal if set(mark) <= set(active))
        eligible.update(valid)
        remember(retained, trim.restrict(rows, kept), active, kept, valid, case)
    assert eligible == legal


def record_measurement(state, seed, by_step, examples, seen, full, retained):
    _, _, _, controls, _ = source_apis()
    stats = by_step[len(state.tail)]
    live = retains_tracked(state, seed)
    legal = actual_menu(state)
    marked = frozenset(mark for mark in legal if seed.loose in mark)
    assert marked == actual_menu(state, seed.loose)
    assert legal == controls.actual_triples(state.supports)
    rows, truth = measure(state.supports, state.width)
    difference = swap_failure(rows, seed.loose, seed.shared)
    moves_state = span_moves(state.supports, truth, seed.loose, seed.shared)
    stats["measured_seed_path_occurrences"] += 1
    stats["measured_unordered_scalar_pairs"] += comb(state.width, 2)
    stats["kept_original_loose_bit"] += live
    stats["with_any_legal_triple"] += bool(legal)
    stats["with_a_legal_triple_using_tracked_bit"] += bool(marked)
    stats["original_swap_still_scalar"] += difference is None
    stats["original_swap_still_scalar_and_moves_state"] += difference is None and moves_state
    stats["original_swap_still_scalar_and_some_triple_legal"] += difference is None and bool(legal)
    stats["original_swap_still_scalar_and_some_triple_legal_and_moves_state"] += (
        difference is None and bool(legal) and moves_state
    )
    if difference is not None and live and "first_live_swap_failure" not in examples:
        examples["first_live_swap_failure"] = {
            **source_record(state, seed), "distinguishing_bit_and_two_entries": difference,
        }
    if difference is None and moves_state and legal and "first_inert_state_moving_swap" not in examples:
        examples["first_inert_state_moving_swap"] = {
            **source_record(state, seed), "legal_triples": sorted(legal),
            "full_rows_hex": tuple(row.hex() for row in rows),
        }
    if difference is None and marked and "exact_old_swap_collision" not in examples:
        mark = min(marked)
        target = tuple(sorted(seed.shared if bit == seed.loose else bit for bit in mark))
        assert target not in legal
        permutation = list(range(state.width))
        permutation[seed.loose], permutation[seed.shared] = seed.shared, seed.loose
        controls.verify_map(rows, rows, mark, target, permutation)
        witness = {**source_record(state, seed), "legal_mark": mark, "forbidden_mark": target,
                   "permutation": permutation, "full_rows_hex": tuple(row.hex() for row in rows)}
        print(json.dumps({"exact_old_swap_collision": witness}), flush=True)
        examples.setdefault("exact_old_swap_collision", witness)
    key = state.supports
    if key not in seen:
        seen.add(key)
        stats["distinct_literal_supports_first_seen"] += 1
        add_readings(state, seed, legal, rows, full, retained)


def summarize_comparisons(groups):
    _, _, _, controls, _ = source_apis()
    result = controls.compare_survivors(groups)
    return {key: result.get(key, 0) for key in (
        "grouped_numbered_tables_and_active_sets", "numbered_group_triples",
        "positive_group_input_maps_verified_entry_by_entry", "forbidden_group_inputs_canonicalized",
        "forbidden_named_occurrences_passing_necessary_filter", "exact_legal_classes",
        "classes_shared_between_physical_types", "opposite_color_exact_classes",
        "opposite_color_named_forbidden_occurrences", "opposite_color_occurrence_pairs",
        "opposite_color_pairs_also_matching_before_pruning", "opposite_color_witnesses",
    )}


def menu_control():
    archive, scout, rules, _, _ = source_apis()
    control = archive.literal_twenty_two()
    fixture = scout.Fixture((), (3,), ())
    for parents, count in control["history"]:
        fixture = fixture.successor(parents, count)
    state = State(22, tuple(fixture.checks().values()))
    good, bad = (entry["mark"] for entry in control["designated_marks_and_true_verdicts"])
    assert good in actual_menu(state, good[-1])
    assert bad not in actual_menu(state, bad[-1])
    assert rules.legal_local_move(fixture.checks(), good, scout.FRESH_FOR_PARENT_TEST)
    assert not rules.legal_local_move(fixture.checks(), bad, scout.FRESH_FOR_PARENT_TEST)
    return {"source": control["case_id"], "accepted_mark": good, "rejected_mark": bad}


def run(timing=False):
    seeds = width_twenty_seeds()
    by_step = {step: Counter() for step in (1, 2, 3)}
    cases, examples, seen, full, retained = [], {}, set(), {}, {}
    third_prefixes = []
    for seed in seeds:
        report = {"source": seed.label, "tracked_loose": seed.loose, "tracked_shared": seed.shared,
                  "initial_common_witness_control": frozen_common_witness(seed)}
        counts = Counter()
        protected = (seed.loose, seed.shared)
        original = State(20, seed.supports)
        for first in next_moves(original, protected):
            counts["one_step"] += 1
            record_measurement(first, seed, by_step, examples, seen, full, retained)
            for second in next_moves(first, protected):
                counts["two_steps"] += 1
                record_measurement(second, seed, by_step, examples, seen, full, retained)
                if retains_tracked(second, seed):
                    third_prefixes.append((seed, second, counts))
        report["paths_by_depth"] = counts
        cases.append(report)

    if timing:
        print("Full tables measured at depths one and two.", file=sys.stderr)
    full_comparison = summarize_comparisons(full)
    retained_comparison = summarize_comparisons(retained)
    two_step_collision = (full_comparison["opposite_color_exact_classes"]
                          or retained_comparison["opposite_color_exact_classes"])
    if two_step_collision:
        witness = (full_comparison["opposite_color_witnesses"] or retained_comparison["opposite_color_witnesses"])[0]
        print(json.dumps({"exact_depth_at_most_two_collision": witness}), flush=True)
    else:
        for seed, state, counts in third_prefixes:
            for third in next_moves(state, (seed.loose, seed.shared), preserve=True):
                assert retains_tracked(third, seed)
                counts["third_moves_preserving_tracked_loose"] += 1
                by_step[3]["third_moves_preserving_tracked_loose"] += 1
                if actual_menu(third, seed.loose):
                    record_measurement(third, seed, by_step, examples, seen, full, retained)
        if by_step[3]["measured_seed_path_occurrences"]:
            full_comparison = summarize_comparisons(full)
            retained_comparison = summarize_comparisons(retained)
    for field in ("measured_seed_path_occurrences", "with_a_legal_triple_using_tracked_bit"):
        by_step[3][field] += 0

    assert sum(case["paths_by_depth"]["one_step"] for case in cases) == by_step[1]["measured_seed_path_occurrences"]
    assert sum(case["paths_by_depth"]["two_steps"] for case in cases) == by_step[2]["measured_seed_path_occurrences"]
    assert sum(case["paths_by_depth"]["third_moves_preserving_tracked_loose"] for case in cases) == (
        by_step[3]["third_moves_preserving_tracked_loose"]
    )
    return {
        "span_archive_sha256": ARCHIVE_SHA, "span_checker_sha256": SPAN_SHA,
        "other_source_examined_separately": EXCLUDED,
        "source_types": len({seed.label for seed in seeds}), "tracked_source_transpositions": len(seeds),
        "scope": (
            "All one- and two-move continuations up to loose-port permutations fixing the two tracked "
            "bits, and every third move preserving the loose bit after these prefixes. "
            "All depth-one and depth-two tables were measured in full. A depth-three table is measured "
            "only if one of its legal triples uses the tracked loose bit."
        ),
        "number_with_persistent_common_witness_proof": sum(
            case["initial_common_witness_control"]["forbidden_for_every_continuation_retaining_the_bit"]
            for case in cases
        ),
        "by_step": by_step, "per_source_transposition": cases,
        "target_triple_menu_control": menu_control(),
        "independent_numeric_support_states_measured": len(seen),
        "example_continuations": examples,
        "full_marked_table_comparison_across_measured_states": full_comparison,
        "retained_marked_table_comparison_across_measured_states": retained_comparison,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write the checked live_twins.json")
    parser.add_argument("--timing", action="store_true", help="Report elapsed time on stderr")
    args = parser.parse_args()
    start = perf_counter()
    report = json.dumps(run(args.timing), sort_keys=True, indent=2) + "\n"
    if args.timing:
        print(f"Tracked twin continuation controls: {perf_counter() - start:.1f}s", file=sys.stderr)
    if args.write:
        (HERE / "live_twins.json").write_text(report)
    else:
        assert (HERE / "live_twins.json").read_text() == report
        print("Tracked twin continuation controls reproduced.")
