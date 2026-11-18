"""Grade table-only short-support inference on the archived control populations."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from functools import cache, lru_cache
from hashlib import sha256
from itertools import combinations
from math import comb
from pathlib import Path
from random import Random
from time import perf_counter


HERE = Path(__file__).resolve().parent
OLDER = HERE.parents[1]
CLASS_API = (
    OLDER / "VARIABLE-OUTPUT-READER-20261118-001A"
    / "VARIABLE-OUTPUT-READER-20261118-001A-P001_width_eighteen/check_classes.py"
)
WIDTH_20_CLASS_RESULT = (
    OLDER / "VARIABLE-OUTPUT-READER-20261118-001C"
    / "VARIABLE-OUTPUT-READER-20261118-001C-P001_triple_inverse/full.json"
)
DEPENDENCIES = {
    "check_controls.py": "631634d3b8efb94c84199ce78edb48b45090f8429c1a01e15864331bb7965c86",
    "check_scalar_span.py": "19d293fe62d76eb910ebe606ed3afda97b69ff0b700eb7beab433c0cbb47c05c",
    "check_classes.py": "8dd0ddaa58aa6e6f8ba1ec20fbe87b0b1c31cb090e93849fb271c8243dcb2472",
    "full.json": "fe8942c22071b913e6362e95012a2ac7e6dd63a12c8bdb2b257cfca04953adcc",
}
EXPECTED_WIDTHS = {19: (8191, 582), 20: (19414, 1585)}
FIRST = "original_with_legal_triples"
OTHER = "original_without_legal_triples"
RETAINED = "retained_part_with_legal_triples"


@cache
def load(filename):
    path = CLASS_API if filename == CLASS_API.name else HERE / filename
    assert sha256(path.read_bytes()).hexdigest() == DEPENDENCIES[filename]
    spec = importlib.util.spec_from_file_location(f"span_audit_{path.stem}", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def controls():
    return load("check_controls.py")


def certificate():
    return load("check_scalar_span.py")


def scout_and_rules():
    scout, _, rules = controls().inherited().inherited().inherited()
    return scout, rules


@lru_cache(maxsize=512)
def infer_short_table(short_rows):
    width = len(short_rows)
    table = {(a, b): short_rows[a][b] or None for a, b in combinations(range(width), 2)}
    known, unresolved, passes = certificate().infer(table, width)
    return frozenset(known), frozenset(unresolved), tuple(passes)


def short_observation(rows):
    """Zero off the diagonal denotes an entry beyond five, including infinity."""
    return tuple(bytes(value if value <= 5 else 0 for value in row) for row in rows)


def rank_cap(width):
    # A whole source starts with three labels. A genuinely retained part starts
    # with the root or with a child keeping its incoming separator label and
    # its two or three fresh labels. Every further junction keeps its outputs.
    return (width - 1) // 2


@dataclass(frozen=True)
class Grade:
    truth: frozenset
    forced: frozenset
    undecided: frozenset
    passes: tuple

    def forced_rank(self):
        return len(self.forced).bit_length() - 1

    def true_rank(self):
        return len(self.truth).bit_length() - 1

    def status(self):
        if not self.undecided:
            return "closed"
        if self.forced == self.truth:
            return "all_actual_equations_forced_uniqueness_unproved"
        return "proper_forced_subspace_uniqueness_unproved"

    def law_status(self, width):
        if not self.undecided:
            return "pinned_by_short_support_closure"
        if self.forced_rank() == rank_cap(width):
            return "pinned_by_rank_cap"
        return "unresolved_by_these_two_tests"

    def summary(self, width):
        return {
            "certificate": self.status(),
            "actual_dual_rank": self.true_rank(),
            "forced_dual_rank": self.forced_rank(),
            "source_law_rank_cap": rank_cap(width),
            "source_law_certificate": self.law_status(width),
            "undecided_short_supports": len(self.undecided),
            "undecided_in_actual_dual": len(self.undecided & self.truth),
            "undecided_outside_actual_dual": len(self.undecided - self.truth),
            "passes": self.passes,
        }


def grade(rows, supports):
    scout, _ = scout_and_rules()
    known, undecided, passes = infer_short_table(short_observation(rows))
    assert all(3 <= len(support) <= 6 for support in supports)
    truth = scout.parity_span(controls().scopes(supports))
    assert all(word.bit_count() >= 3 for word in truth if word)
    assert known <= truth and not (known & undecided)
    # Every actual generating word is a short bond in these sources.
    assert all(scout.mask(support) in known | undecided for support in supports)
    if not undecided:
        assert known == truth
    result = Grade(truth, known, undecided, passes)
    assert result.true_rank() <= rank_cap(len(rows))
    if result.law_status(len(rows)) == "pinned_by_rank_cap":
        assert known == truth
    return result


def shortest_word(words):
    if not words:
        return None
    word = min(words, key=lambda mask: (mask.bit_count(), mask))
    return tuple(controls().inherited().bits(word))


def failure_example(case, kept, rows, supports, actual, original_legal):
    return {
        "case_id": case.label,
        "source_width": case.width,
        "retained_original_names": kept,
        "known_from_full_supports_for_grading": supports,
        "source_history": case.history,
        "full_scalar_rows_hex": tuple(row.hex() for row in rows),
        "sample_original_legal_triple": min(original_legal, default=None),
        "first_actual_word_outside_forced_span": shortest_word(actual.truth - actual.forced),
        "first_viable_candidate_outside_actual_span": shortest_word(actual.undecided - actual.truth),
        **actual.summary(len(rows)),
    }


@dataclass
class Ledger:
    counts: Counter = field(default_factory=Counter)
    source_law: Counter = field(default_factory=Counter)
    choices_by_source_law_status: Counter = field(default_factory=Counter)
    deficits: Counter = field(default_factory=Counter)
    dimensions: Counter = field(default_factory=Counter)
    failures: dict = field(default_factory=dict)

    def add(self, case, kept, rows, supports, actual, original_legal):
        verdict = actual.status()
        self.counts[verdict] += 1
        source_law_status = actual.law_status(len(rows))
        self.source_law[source_law_status] += 1
        self.choices_by_source_law_status[source_law_status] += len(original_legal)
        gap = actual.true_rank() - actual.forced_rank()
        self.deficits[gap] += 1
        self.dimensions[len(rows)] += 1
        if verdict != "closed":
            if "first_unclosed" not in self.failures:
                self.failures["first_unclosed"] = failure_example(case, kept, rows, supports, actual, original_legal)
            if gap and "first_proper_forced_subspace" not in self.failures:
                self.failures["first_proper_forced_subspace"] = failure_example(
                    case, kept, rows, supports, actual, original_legal
                )

    def report(self):
        cases = sum(self.counts.values())
        return {
            "cases": cases,
            "closed": self.counts["closed"],
            "unclosed": cases - self.counts["closed"],
            "all_actual_equations_forced_uniqueness_unproved": self.counts[
                "all_actual_equations_forced_uniqueness_unproved"],
            "proper_forced_subspace_uniqueness_unproved": self.counts[
                "proper_forced_subspace_uniqueness_unproved"],
            "with_source_law_rank_bound": {
                status: self.source_law[status] for status in (
                    "pinned_by_short_support_closure", "pinned_by_rank_cap", "unresolved_by_these_two_tests"
                )
            },
            "legal_triples_by_source_law_certificate": dict(self.choices_by_source_law_status),
            "by_actual_minus_forced_dual_rank": dict(self.deficits),
            "by_table_width": dict(self.dimensions),
            **self.failures,
        }


def retained(case, rows, legal, designated=()):
    """Grade each physical part hosting a legal or designated marked triple once."""
    api = controls()
    trim = api.inherited()
    finite, separators = trim.scalar_cuts(rows)
    physical = api.incidence_graph(case.supports, case.width)
    baseline, actual_separators = api.incidence_deletions(physical, case.width)
    assert tuple(sorted(finite)) == baseline and separators == actual_separators
    physical_blocks = api.physical_parts(case.supports, case.width, physical, actual_separators)
    covered = set()
    for kept, active in trim.active_groups(finite, separators):
        wanted = {mark for mark in legal | set(designated) if set(mark) <= set(active)}
        if not wanted:
            continue
        index = {old: i for i, old in enumerate(kept)}
        supports = tuple(tuple(sorted(index[bit] for bit in support)) for support in physical_blocks[kept, active])
        reduced = trim.restrict(rows, kept)
        if kept != tuple(range(case.width)):
            measured, _ = api.remeasure_pruned(supports)
            assert measured == reduced
        covered.update(wanted)
        yield kept, reduced, supports, frozenset(wanted & legal), tuple(sorted(wanted & set(designated)))
    assert covered == legal | set(designated)


def grade_literal(case, rows, legal, marks, original=None):
    if original is None:
        original = grade(rows, case.supports)
    return {
        "case_id": case.label,
        "source_width": case.width,
        "original": original.summary(len(rows)),
        "designated_marks_and_true_verdicts": [{"mark": mark, "legal": mark in legal} for mark in marks],
        "retained": [
            {
                "original_names": kept, "designated_marks_in_original_names": picked,
                "number_of_legal_marks": len(chosen), **grade(reduced, supports).summary(len(reduced)),
            }
            for kept, reduced, supports, chosen, picked in retained(case, rows, legal, marks)
        ],
    }


def literal_twenty_two():
    """Replay the literal shared source of the two weaker-observation marks."""
    api = controls()
    scout, rules = scout_and_rules()
    history = (
        ((0,), 2), ((0,), 3), ((0,), 3), ((1, 2), 2),
        ((1, 3), 2), ((2, 3), 2), ((4, 5, 6), 3), ((2, 3), 2),
    )
    fixture = scout.Fixture((), (3,), ())
    for parents, count in history:
        assert parents in {option for option, _ in scout.legal_parent_sets(rules, fixture.checks())}
        fixture = fixture.successor(parents, count)
    measured = scout.measure(rules, fixture)
    supports = tuple(fixture.checks().values())
    case = api.PhysicalCase(22, "continuation.json#matched_retained_rows_control", supports, history)
    rows = api.inherited().matrix_from_pairs(measured.table, 22)
    marks = (14, 15, 20), (14, 15, 16)
    legal = frozenset(tuple(sorted(choice)) for choice in measured.menu if len(choice) == 3)
    assert marks[0] in legal and marks[1] not in legal
    result = grade_literal(case, rows, legal, marks)
    assert len(result["retained"]) == 1
    assert result["retained"][0]["original_names"] == tuple(range(22))
    result["history"] = history
    result["context"] = (
        "One arrangement with two marks that agree on the weaker retained three-row observation. "
        "The continuation control distinguishes their full marked tables."
    )
    return result


def relabel_control(case, rows, actual):
    api = controls()
    trim = api.inherited()
    labels = list(range(case.width))
    Random(24109).shuffle(labels)
    renamed_supports = tuple(tuple(sorted(labels[i] for i in support)) for support in case.supports)
    renamed_rows = trim.actual_scalar_table(api.scopes(renamed_supports))
    api.verify_map(rows, renamed_rows, (), (), labels)
    target = grade(renamed_rows, renamed_supports)

    def transport(words):
        return {trim.bitmask(labels[i] for i in trim.bits(word)) for word in words}

    assert target.truth == transport(actual.truth)
    assert target.forced == transport(actual.forced)
    assert target.undecided == transport(actual.undecided)
    assert actual.status() == target.status()
    return {
        "case_id": case.label, "coordinate_permutation": labels,
        "forced_span_and_candidate_set_transport_exactly": True,
        "certificate": actual.status(),
    }


def measure_every_pair(dual, width):
    """Measure bonds by shortening the entire dual to each proposed support."""
    trim = controls().inherited()
    words = tuple(sorted(dual))
    all_words = (1 << len(words)) - 1
    all_bits = (1 << width) - 1
    zeros_in_coordinate = [
        trim.bitmask(i for i, word in enumerate(words) if not word >> bit & 1)
        for bit in range(width)
    ]
    rows = [bytearray([trim.INFINITY] * width) for _ in range(width)]
    for i in range(width):
        rows[i][i] = 0
    for word in words[1:]:
        assert 3 <= word.bit_count() and word & all_bits == word
        shortened = all_words
        for bit in trim.bits(all_bits ^ word):
            shortened &= zeros_in_coordinate[bit]
            if shortened.bit_count() == 2:
                break
        # Zero and the word itself remain. Exactly two rows means that
        # no different nonzero dual row has strictly smaller support.
        if shortened.bit_count() != 2:
            continue
        value = word.bit_count() - 1
        for a, b in combinations(trim.bits(word), 2):
            rows[a][b] = rows[b][a] = min(rows[a][b], value)
    return tuple(map(bytes, rows))


def one_coset_models(actual):
    """Every generated alternative either equals the forced span or adds one coset."""
    models = {actual.forced: None}
    seen = set()
    for support in sorted(actual.undecided, key=lambda word: (word.bit_count(), word)):
        signature = min(support ^ word for word in actual.forced)
        if signature not in seen:
            seen.add(signature)
            models[actual.forced | {support ^ word for word in actual.forced}] = support
    return models


@cache
def frozen_width_twenty_classes():
    raw = WIDTH_20_CLASS_RESULT.read_bytes()
    assert sha256(raw).hexdigest() == DEPENDENCIES[WIDTH_20_CLASS_RESULT.name]
    result = json.loads(raw)
    assert result["width"] == 20 and result["checked_full_distances"]
    assert result["producer_fixture_count"] == result["full_table_classes"] == EXPECTED_WIDTHS[20][0]
    assert result["classes_with_distinct_fixture_coincidences"] == 0
    return result["full_table_classes"]


def exact_width_twenty_extension(case, rows, actual):
    """Classify every full-table compatible binary code, then its source-law status."""
    width = len(rows)
    assert case.width == width == 20 and actual.forced_rank() == rank_cap(width) - 1
    assert frozen_width_twenty_classes() == EXPECTED_WIDTHS[width][0]
    api = controls()
    trim = api.inherited()
    variants = one_coset_models(actual)
    assert actual.truth in variants
    pairs = tuple(combinations(range(width), 2))
    compatible = {}
    rejected_by_number_of_disagreed_pairs = Counter()
    for dual, added in variants.items():
        measured = measure_every_pair(dual, width)
        disagreed = sum(measured[a][b] != rows[a][b] for a, b in pairs)
        if disagreed:
            rejected_by_number_of_disagreed_pairs[disagreed] += 1
        else:
            compatible[dual] = added
    assert actual.truth in compatible

    # The exhaustive archived class comparison found one physical type per
    # table. The possible reachable labeled states are exactly the orbit of
    # this fixture's dual under the observed table's full symmetry group.
    quotient = load(CLASS_API.name).Quotient.make(rows)
    group_order, quotient_order, generators = quotient.automorphisms()
    for permutation in generators:
        api.verify_map(rows, rows, (), (), permutation)

    def move_word(word, permutation):
        return trim.bitmask(permutation[i] for i in trim.bits(word))

    def image(dual, permutation):
        return frozenset(move_word(word, permutation) for word in dual)

    symmetry_moves = 0
    first_moving_generator = None
    for permutation in generators:
        assert image(actual.forced, permutation) == actual.forced
        if image(actual.truth, permutation) != actual.truth:
            symmetry_moves += 1
            if first_moving_generator is None:
                lost = shortest_word({word for word in actual.truth
                                      if move_word(word, permutation) not in actual.truth})
                first_moving_generator = {
                    "permutation": permutation, "actual_dual_support": lost,
                    "image_outside_actual_dual": tuple(sorted(permutation[i] for i in lost)),
                }
    reachable_maps = {actual.truth: ()}
    queue = deque([actual.truth])
    while queue:
        start = queue.popleft()
        for index, permutation in enumerate(generators):
            end = image(start, permutation)
            assert end in compatible
            if end not in reachable_maps:
                reachable_maps[end] = (*reachable_maps[start], index)
                queue.append(end)
    assert group_order % len(reachable_maps) == 0

    def show_code(dual, added):
        path = reachable_maps.get(dual)
        return {
            "rank": len(dual).bit_length() - 1,
            "is_actual_span": dual == actual.truth,
            "added_viable_support": tuple(trim.bits(added)) if added is not None else None,
            "reachable": path is not None,
            "generating_scalar_permutations_applied": [generators[i] for i in path] if path is not None else None,
        }

    return {
        "case_id": case.label,
        "source_history": case.history,
        "candidate_codes_including_forced_span_alone": len(variants),
        "pair_entries_recomputed": len(variants) * len(pairs),
        "rejected_codes_by_number_of_disagreed_pairs": dict(rejected_by_number_of_disagreed_pairs),
        "abstract_compatible_codes": len(compatible),
        "reachable_labeled_states": len(reachable_maps),
        "only_code_compatible_alternatives": len(compatible) - len(reachable_maps),
        "full_scalar_symmetry_group_order": group_order,
        "quotient_scalar_symmetry_group_order": quotient_order,
        "symmetry_generators_checked": len(generators),
        "symmetry_generators_moving_actual_dual": symmetry_moves,
        "first_moving_generator": first_moving_generator,
        "compatible_models": [show_code(dual, added) for dual, added in compatible.items()],
    }


def extension_report(tests):
    counts = ("candidate_codes_including_forced_span_alone", "pair_entries_recomputed",
              "abstract_compatible_codes", "reachable_labeled_states", "only_code_compatible_alternatives",
              "symmetry_generators_checked", "symmetry_generators_moving_actual_dual")
    return {
        "cases": len(tests),
        "all_190_pair_entries_checked_per_candidate_code": True,
        "same_numbered_table_and_same_source_path": (
            "The archived width-20 census has one physical type per full table. "
            "Compatible duals are reachable exactly when in the actual dual's scalar automorphism orbit."
        ),
        "cases_with_unique_compatible_code": sum(row["abstract_compatible_codes"] == 1 for row in tests),
        "cases_with_unique_reachable_labeled_state": sum(row["reachable_labeled_states"] == 1 for row in tests),
        **{key: sum(row[key] for row in tests) for key in counts},
        "individual_cases": tests,
    }


def run(report_timing):
    started = perf_counter()
    current_width = None
    ledgers = defaultdict(lambda: defaultdict(Ledger))
    larger, one_coset_checks, positive_control = [], [], None
    for case, rows, legal, mark in controls().archived_sources():
        if current_width != case.width:
            if report_timing and current_width is not None:
                print(f"Through source width {current_width}: {perf_counter() - started:.1f}s", file=sys.stderr)
            current_width = case.width
        actual = grade(rows, case.supports)
        if case.width in EXPECTED_WIDTHS:
            status = FIRST if legal else OTHER
            full = tuple(range(case.width))
            ledgers[case.width][status].add(case, full, rows, case.supports, actual, legal)
            if actual.law_status(case.width) == "unresolved_by_these_two_tests":
                one_coset_checks.append(exact_width_twenty_extension(case, rows, actual))
            if legal and positive_control is None and not actual.undecided:
                positive_control = relabel_control(case, rows, actual)
            if legal:
                for kept, reduced, supports, chosen, _ in retained(case, rows, legal):
                    trimmed = actual if kept == full else grade(reduced, supports)
                    assert trimmed.law_status(len(reduced)) != "unresolved_by_these_two_tests"
                    ledgers[case.width][RETAINED].add(case, kept, reduced, supports, trimmed, chosen)
        else:
            larger.append(grade_literal(case, rows, legal, (mark,), actual))

    results = {width: {name: ledger.report() for name, ledger in sorted(domains.items())}
               for width, domains in ledgers.items()}
    for width, (total, positive) in EXPECTED_WIDTHS.items():
        assert results[width][FIRST]["cases"] == positive
        assert results[width][OTHER]["cases"] == total - positive
    original_unresolved = sum(results[width][domain]["with_source_law_rank_bound"]["unresolved_by_these_two_tests"]
                              for width in EXPECTED_WIDTHS for domain in (FIRST, OTHER))
    assert original_unresolved == len(one_coset_checks)
    assert positive_control is not None
    assert [result["source_width"] for result in larger] == [27, 27, 28, 28]
    width22 = literal_twenty_two()
    if report_timing:
        print(f"All span controls: {perf_counter() - started:.1f}s", file=sys.stderr)
    extension = extension_report(one_coset_checks)
    ambiguous_twenty = extension["cases"] - extension["cases_with_unique_reachable_labeled_state"]
    return {
        "inputs": DEPENDENCIES,
        "criterion": (
            "Infer a forced dual span using only distances through five. If no viable short support "
            "remains outside it, every binary dual space with nonzero minimum weight at least three "
            "and generated by supports of size at most six is the forced span whenever it yields "
            "the same observation."
        ),
        "interpretation": (
            "An unclosed certificate supplies no second allowed-state realization. A closed "
            "certificate determines the labeled allowed states by taking the orthogonal complement."
        ),
        "source_law_rank_bound": (
            "The original initial junction contributes three bits and every later junction at least two. "
            "A genuine retained component contains the root or keeps the incoming shared bit at its "
            "first junction along with that junction's at least two fresh bits. All later fresh bits "
            "of its junctions are retained. A width w source in either domain has dual rank at most "
            "floor((w-1)/2). Saturation establishes equality for every allowed realization."
        ),
        "archived_populations": results,
        "full_table_rank_one_extension_controls": extension,
        "archived_originals_with_nonunique_reachable_dual_under_full_table": {19: 0, 20: ambiguous_twenty},
        "archived_originals_with_unique_reachable_dual_under_full_table": {
            19: EXPECTED_WIDTHS[19][0], 20: EXPECTED_WIDTHS[20][0] - ambiguous_twenty,
        },
        "literal_twenty_two": width22,
        "literal_branch_fixtures": larger,
        "literal_relabel_control": positive_control,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write the checked span_controls.json")
    parser.add_argument("--timing", action="store_true", help="Report cumulative elapsed time on stderr")
    args = parser.parse_args()
    report = json.dumps(run(args.timing), indent=2, sort_keys=True) + "\n"
    record = HERE / "span_controls.json"
    if args.write:
        record.write_text(report)
    else:
        assert record.read_text() == report
        print("Scalar-span population controls reproduced.")
