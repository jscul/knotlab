"""Recount forced splits for the archived parity stages using exact binary arithmetic.

Every distinction is held once or twice on these stages. In the classical
multigraph reading, join the two holders of a distinction, supplying a single
extra holder for all loose distinctions. Even incidence at each actual knot
implies even incidence at the extra holder. A shortest allowed change through
a distinction consists of just a shortest simple cycle through it.

The split count treats the same unordered partition as one split and exhausts
each nonzero forced sum. Local readability is equality modulo the parity laws.
No study reading or split code is imported.
"""

import argparse
from collections import Counter, defaultdict, deque
from functools import cache, cached_property
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import time


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parents[1]
ORIGINAL_JUDGE = "fd6b445e0f"
SETS = ("census", "heldout", "witnesses")
FIRST_REPORTED_ROWS = 7713


def one_bits(mask):
    while mask:
        bit = mask & -mask
        yield bit
        mask ^= bit


def sum_selected(vectors, selection):
    total = 0
    for bit in one_bits(selection):
        total ^= vectors[bit.bit_length() - 1]
    return total


class BinarySpan:
    def __init__(self, vectors=()):
        self.pivots = {}
        for vector in vectors:
            self.add(vector)

    def __len__(self):
        return len(self.pivots)

    def __iter__(self):
        return iter(self.pivots.values())

    def add(self, vector):
        while vector:
            pivot = 1 << (vector.bit_length() - 1)
            if pivot not in self.pivots:
                self.pivots[pivot] = vector
                return
            vector ^= self.pivots[pivot]

    def __contains__(self, vector):
        while vector:
            pivot = 1 << (vector.bit_length() - 1)
            if pivot not in self.pivots:
                return False
            vector ^= self.pivots[pivot]
        return True

    def residue(self, vector):
        remainder = 0
        while vector:
            pivot = 1 << (vector.bit_length() - 1)
            if pivot in self.pivots:
                vector ^= self.pivots[pivot]
            else:
                remainder |= pivot
                vector ^= pivot
        return remainder

    def elements(self):
        elements = [0]
        for vector in self:
            elements += [vector ^ older for older in elements]
        return elements


def kernel_combinations(images):
    """A basis of the selections of images whose binary sum is zero."""
    pivots = {}
    for index, image in enumerate(images):
        tag = 1 << index
        while image:
            pivot = image.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = (image, tag)
                break
            other, selection = pivots[pivot]
            image ^= other
            tag ^= selection
        if not image:
            yield tag


def signature(vector, checks):
    value = 0
    for index, check in enumerate(checks):
        value |= ((vector & check).bit_count() & 1) << index
    return value


class Stage:
    def __init__(self, supports, *, max_move=None):
        self.names = tuple(sorted({name for knot in supports for name in knot}))
        bits = {name: 1 << index for index, name in enumerate(self.names)}
        holders = defaultdict(list)
        rows = []
        for index, knot in enumerate(supports):
            assert len(knot) == len(set(knot))
            row = 0
            for name in knot:
                row |= bits[name]
                holders[bits[name]].append(index)
            rows.append(row)
        self.rows = rows
        self.laws = BinarySpan(rows)
        self.allowed_dimension = len(self.names) - len(self.laws)
        self.max_move = max_move
        loose_holder = len(rows)
        self.loose = 0
        self.endpoints = {}
        self.links = [[] for _ in range(loose_holder + 1)]
        for bit, knots in holders.items():
            if len(knots) == 1:
                self.loose |= bit
                knots.append(loose_holder)
            first, second = knots
            self.endpoints[bit] = (first, second)
            self.links[first].append((second, bit))
            self.links[second].append((first, bit))

    @cached_property
    def law_change_images(self):
        return tuple(signature(vector, self.rows) for vector in self.laws)

    @cached_property
    def forced(self):
        """Restrict the law sum to even incidence and zero on loose distinctions."""
        basis = tuple(self.laws)
        images = [value | ((row & self.loose) << len(self.rows))
                  for value, row in zip(self.law_change_images, basis, strict=True)]
        return BinarySpan(sum_selected(basis, selection)
                          for selection in kernel_combinations(images))

    @cached_property
    def law_change_dimension(self):
        return len(self.laws) - len(BinarySpan(self.law_change_images))

    @cached_property
    def moves(self):
        if self.max_move is None:
            return self.shortest_span()
        all_distinctions = (1 << len(self.names)) - 1
        return BinarySpan(self.simple_cycles(all_distinctions, self.max_move))

    def shortest_span(self):
        span = BinarySpan()
        groups = defaultdict(list)
        for bit, pair in self.endpoints.items():
            groups[pair].append(bit)
        for (first, last), parallel in groups.items():
            if len(parallel) > 1:
                for bit in parallel[1:]:
                    span.add(parallel[0] ^ bit)
            else:
                self.add_shortest_through(first, last, parallel[0], span)
            if len(span) == self.allowed_dimension:
                break
        return span

    def add_shortest_through(self, first, last, excluded, span):
        """Span the shortest-path differences instead of listing tied paths.

        Each reference path to a holder in the shortest-path DAG can be
        completed by the same suffix as any other path to that holder. Thus
        replacing its final step yields a difference of two shortest changes.
        Those differences telescope along any shortest path.
        """
        depths = {first: 0}
        reference = {first: 0}
        queue = deque([first])
        while queue:
            current = queue.popleft()
            if last in depths and depths[current] >= depths[last]:
                break
            for neighbor, bit in self.links[current]:
                if bit != excluded and neighbor not in depths:
                    depths[neighbor] = depths[current] + 1
                    reference[neighbor] = reference[current] ^ bit
                    queue.append(neighbor)
        if last not in depths:
            return
        span.add(excluded ^ reference[last])
        active = {last}
        queue = deque([last])
        while queue:
            current = queue.popleft()
            if current == first:
                continue
            for parent, bit in self.links[current]:
                if bit == excluded or depths.get(parent) != depths[current] - 1:
                    continue
                span.add(reference[current] ^ bit ^ reference[parent])
                if parent not in active:
                    active.add(parent)
                    queue.append(parent)

    @cached_property
    def class_dimension(self):
        return self.allowed_dimension - len(self.moves)

    @cached_property
    def local_labels(self):
        if not self.class_dimension:
            return set()
        moves = tuple(self.moves)
        distinct_images = {bit: signature(bit, moves) for bit in self.endpoints}
        labels = set()
        for row in self.rows:
            units = tuple(one_bits(row))
            invariants = kernel_combinations(distinct_images[bit] for bit in units)
            local = BinarySpan(self.laws.residue(sum_selected(units, selection))
                               for selection in invariants)
            labels.update(local.elements())
        labels.discard(0)
        return labels

    def read_cycle(self, mask):
        label = self.laws.residue(mask)
        if not label:
            return 3, 0  # constant
        if not self.class_dimension or signature(label, self.moves):
            return 0, 0  # varies along an admitted change
        if label in self.local_labels:
            return 2, label  # readable by a single knot
        return 1, label  # invariant and unreadable by every single knot

    def simple_cycles(self, support, length_limit=None):
        """List a support cycle by its least distinction and the complementary path."""
        for least in one_bits(support):
            first, last = self.endpoints[least]
            available = support & - (least << 1)
            todo = [(first, 1 << first, least)]
            while todo:
                holder, visited, mask = todo.pop()
                if length_limit is not None and mask.bit_count() >= length_limit:
                    continue
                for neighbor, bit in self.links[holder]:
                    if not available & bit:
                        continue
                    if neighbor == last:
                        yield mask | bit
                    elif not (visited >> neighbor) & 1:
                        todo.append((neighbor, visited | 1 << neighbor, mask | bit))

    def names_of(self, mask):
        return [self.names[bit.bit_length() - 1] for bit in one_bits(mask)]


SPLIT_COUNTS = (
    "elements", "elements_with_three_cycles", "elements_with_alternative_splits",
    "elements_where_an_alternative_changes_part_count", "elements_with_an_unread_cycle",
    "elements_with_three_cycles_and_an_unread_part", "elements_with_three_cycles_and_two_unread_parts",
    "splits", "splits_with_three_cycles", "splits_with_three_cycles_and_an_unread_part",
    "splits_with_three_cycles_and_two_unread_parts", "splits_with_three_eligible_parts",
    "splits_with_all_parts_eligible", "elements_reaching_judge_split_break",
    "elements_with_splits_omitted_by_cap", "splits_omitted_by_split_cap",
    "moves_varying_split_parts", "nonconstant_local_split_parts", "constant_split_parts",
    "eligible_split_parts",
)


def cover_counts(support, cycle_catalog, by_bit):
    """Count splits by cycle count and the counts of the three non-varying part types."""
    @cache
    def count(rest):
        if not rest:
            return Counter({(0, 0, 0, 0): 1})
        result = Counter()
        for cycle in by_bit[rest & -rest]:
            if cycle & rest != cycle:
                continue
            category, _ = cycle_catalog[cycle]
            for subtotals, ways in count(rest ^ cycle).items():
                totals = list(subtotals)
                totals[0] += 1
                if category:
                    totals[category] += 1
                result[tuple(totals)] += ways
        return result

    return count(support)


def partitions(support, by_bit):
    if not support:
        yield ()
        return
    for cycle in by_bit[support & -support]:
        if cycle & support == cycle:
            for rest in partitions(support ^ cycle, by_bit):
                yield (cycle, *rest)


def read_splits(stage, *, preserve_examples=False):
    counts = {name: 0 for name in SPLIT_COUNTS}
    known_cycles = {}
    most_cycles = 0
    max_splits_per_element = 0
    first_binding_by_size = []
    certificates = []
    stage_eligible_labels = set()
    largest_unread_part_count = 0
    examples = []
    for relation in stage.forced.elements()[1:]:
        cycles = sorted(stage.simple_cycles(relation))
        by_bit = defaultdict(list)
        for cycle in cycles:
            if cycle not in known_cycles:
                known_cycles[cycle] = stage.read_cycle(cycle)
            kind, label = known_cycles[cycle]
            if kind == 1:
                stage_eligible_labels.add(label)
            for bit in one_bits(cycle):
                by_bit[bit].append(cycle)

        tally = cover_counts(relation, known_cycles, by_bit)
        assert tally, "Every nonzero even-incidence support should partition into simple cycles"
        split_count = sum(tally.values())
        max_splits_per_element = max(max_splits_per_element, split_count)
        part_sizes = {sizes[0] for sizes in tally}
        most_cycles = max(most_cycles, max(part_sizes))
        largest_unread_part_count = max(largest_unread_part_count, max(sizes[1] for sizes in tally))
        counts["elements"] += 1
        counts["elements_with_three_cycles"] += max(part_sizes) >= 3
        counts["elements_with_alternative_splits"] += split_count > 1
        counts["elements_where_an_alternative_changes_part_count"] += len(part_sizes) > 1
        counts["elements_with_an_unread_cycle"] += any(sizes[1] for sizes in tally)
        counts["elements_with_three_cycles_and_an_unread_part"] += any(
            sizes[0] >= 3 and sizes[1] >= 1 for sizes in tally)
        counts["elements_with_three_cycles_and_two_unread_parts"] += any(
            sizes[0] >= 3 and sizes[1] >= 2 for sizes in tally)
        counts["splits"] += split_count
        counts["elements_reaching_judge_split_break"] += split_count >= 5001
        counts["elements_with_splits_omitted_by_cap"] += split_count > 5001
        counts["splits_omitted_by_split_cap"] += max(0, split_count - 5001)

        for (parts, unread, local, constant), ways in tally.items():
            counts["moves_varying_split_parts"] += (parts - unread - local - constant) * ways
            counts["nonconstant_local_split_parts"] += local * ways
            counts["constant_split_parts"] += constant * ways
            counts["eligible_split_parts"] += unread * ways
            counts["splits_with_three_cycles"] += ways if parts >= 3 else 0
            counts["splits_with_three_cycles_and_an_unread_part"] += ways if parts >= 3 and unread >= 1 else 0
            counts["splits_with_three_cycles_and_two_unread_parts"] += ways if parts >= 3 and unread >= 2 else 0
            counts["splits_with_three_eligible_parts"] += ways if unread >= 3 else 0
            counts["splits_with_all_parts_eligible"] += ways if parts >= 3 and unread == parts else 0

        if preserve_examples:
            split = next(candidate for candidate in partitions(relation, by_bit)
                         if len(candidate) == max(part_sizes))
            examples.append({"forced_sum": stage.names_of(relation), "number_of_splits": split_count,
                             "longest_split": [{"distinctions": stage.names_of(part),
                                                "reading": ("varies along a move", "unread label",
                                                            "local label", "constant")[known_cycles[part][0]]}
                                               for part in split]})

        if any(parts >= 3 and unread == parts for parts, unread, _, _ in tally):
            first = None
            for number, split in enumerate(partitions(relation, by_bit), 1):
                labels = [known_cycles[part][1] for part in split if known_cycles[part][0] == 1]
                if len(split) < 3 or len(labels) != len(split):
                    continue
                if first is None:
                    first = number
                    first_binding_by_size.append({"size": relation.bit_count(), "parts": len(split),
                                                  "split_number": number})
                certificates.append({"forced_sum": stage.names_of(relation),
                                     "cycles": [stage.names_of(part) for part in split],
                                     "proper_values_free": len(BinarySpan(labels)) == len(split) - 1,
                                     "split_number": number})
    unique_counts = Counter(kind for kind, label in known_cycles.values())
    result = {
        **counts,
        "most_cycles": most_cycles,
        "max_splits_per_element": max_splits_per_element,
        "max_unread_parts_in_one_split": largest_unread_part_count,
        "distinct_cycles_in_forced_sums": len(known_cycles),
        "distinct_unread_cycles_in_forced_sums": unique_counts[1],
        "distinct_constant_cycles_in_forced_sums": unique_counts[3],
        "distinct_local_cycles_in_forced_sums": unique_counts[2],
        "distinct_move_varying_cycles_in_forced_sums": unique_counts[0],
        "distinct_unread_labels_in_forced_sums": len(stage_eligible_labels),
        "first_binding_by_size": first_binding_by_size,
        "binding_certificates": certificates,
    }
    if preserve_examples:
        result["forced_sum_examples"] = examples
    return result


def read_stage(supports, *, max_move=None):
    stage = Stage(supports, max_move=max_move)
    return summarize_stage(stage)


def summarize_stage(stage, *, preserve_examples=False):
    return {
        "distinctions": len(stage.names), "allowed_dimension": stage.allowed_dimension,
        "law_change_dimension": stage.law_change_dimension, "forced_dimension": len(stage.forced),
        "class_dimension": stage.class_dimension, "local_labels": len(stage.local_labels),
        "unread_labels": 2 ** stage.class_dimension - 1 - len(stage.local_labels),
        **read_splits(stage, preserve_examples=preserve_examples),
    }


def check_literal(stage):
    """Independent literal check on tiny stages, including local readability and tied shortest changes."""
    allowed = [value for value in range(1 << len(stage.names)) if not signature(value, stage.rows)]
    assert len(allowed) == 2 ** stage.allowed_dimension
    for value in range(1 << len(stage.names)):
        expected = value in allowed and not value & stage.loose and not any(
            (value & state).bit_count() & 1 for state in allowed)
        assert (value in stage.forced) == expected
    literal_moves = BinarySpan()
    for bit in stage.endpoints:
        through = [value for value in allowed if value & bit]
        if through:
            minimum = min(map(int.bit_count, through)) if stage.max_move is None else stage.max_move
            for value in through:
                if value.bit_count() <= minimum:
                    literal_moves.add(value)
    assert len(literal_moves) == len(stage.moves) and all(move in stage.moves for move in literal_moves)
    literal_labels = set()
    for row in stage.rows:
        units = tuple(one_bits(row))
        for code in range(1 << len(units)):
            candidate = sum_selected(units, code)
            if not signature(candidate, literal_moves):
                literal_labels.add(stage.laws.residue(candidate))
    literal_labels.discard(0)
    assert literal_labels == stage.local_labels


def check_controls():
    six_parallel = Stage((tuple(range(6)), tuple(range(6))))
    check_literal(six_parallel)
    result = summarize_stage(six_parallel)
    assert result["forced_dimension"] == 1 and result["splits"] == 15
    assert result["most_cycles"] == 3 and result["constant_split_parts"] == 0
    assert result["moves_varying_split_parts"] == 45 and not result["binding_certificates"]
    two_loose = Stage(((0, 1, 2), (0, 1, 3)))
    check_literal(two_loose)
    assert not len(two_loose.forced) and len(two_loose.moves) == 2

    # Three four-knot rings with a pairwise connector joining distinct
    # even-indexed knots. The three connector values are free. Each ring
    # parity is the sum of the two connectors it meets. No knot reads two.
    supports = [[] for _ in range(12)]
    for ring_start in (0, 4, 8):
        for offset in range(4):
            distinction = ring_start + offset
            supports[distinction].append(distinction)
            supports[ring_start + (offset + 1) % 4].append(distinction)
    for name, holder in enumerate(range(1, 12, 2), 12):
        supports[holder].append(name)
    for name, (first, last) in enumerate(((0, 4), (6, 8), (10, 2)), 18):
        supports[first].append(name)
        supports[last].append(name)
    positive = read_stage(supports, max_move=1)
    assert positive["forced_dimension"] == 1 and positive["distinct_unread_cycles_in_forced_sums"] == 3
    assert len(positive["binding_certificates"]) == 1
    assert positive["binding_certificates"][0]["proper_values_free"]
    negative = read_stage(supports)
    assert negative["forced_dimension"] == 1 and not negative["class_dimension"]
    assert not negative["binding_certificates"]
    return {
        "six_distinctions_shared_by_two_knots": {"splits": result["splits"], "admitted_parts": 0},
        "two_shared_and_one_loose_at_each_of_two_knots": {"forced_dimension": 0, "move_dimension": 2},
        "three_joined_four_knot_rings": {
            "supports": supports,
            "move_bound_one": positive["binding_certificates"],
            "shortest_moves": negative["binding_certificates"],
            "scope": "A positive control for the split test, with a move bound that admits no nonzero changes. "
                     "The forced sum is already present at the source. The control is outside the study census."
        },
    }


def read_json_lines(raw):
    return [json.loads(line) for line in raw.splitlines()]


def read_archives():
    committed = subprocess.check_output(
        ["git", "show", f"{ORIGINAL_JUDGE}:{(STUDY / 'judge.jsonl').relative_to(ROOT)}"], cwd=ROOT)
    working = (STUDY / "judge.jsonl").read_bytes()
    committed_prefix = b"".join(committed.splitlines(keepends=True)[:FIRST_REPORTED_ROWS])
    judges = {"reported_prefix": committed_prefix, "committed": committed, "working": working}
    forced = {}
    hashes = {}
    for group in SETS[:2]:
        raw = (STUDY / f"forced_{group}.jsonl").read_bytes()
        records = read_json_lines(raw)
        forced[group] = {row["start"]: {record["round"]: record for record in row["rounds"]}
                         for row in records}
        assert len(records) == len(forced[group])
        hashes[f"forced_{group}.jsonl"] = sha256(raw).hexdigest()
    return forced, judges, hashes, working.startswith(committed)


def count_cell(cell, result):
    cell["stages"] += 1
    cell["stages_with_labels"] += result["class_dimension"] > 0
    cell["stages_with_unread_labels"] += result["unread_labels"] > 0
    cell["stages_with_at_least_two_unread_labels"] += result["unread_labels"] >= 2
    cell["stages_with_at_least_three_unread_labels"] += result["unread_labels"] >= 3
    cell["stages_with_forced_sums"] += result["forced_dimension"] > 0
    cell["stages_with_forced_sums_and_at_least_three_unread_labels"] += (
        result["forced_dimension"] > 0 and result["unread_labels"] >= 3)
    cell["stages_with_three_cycles"] += result["most_cycles"] >= 3
    cell["stages_with_three_cycles_and_at_least_three_unread_labels"] += (
        result["most_cycles"] >= 3 and result["unread_labels"] >= 3)
    cell["stages_with_alternative_splits"] += result["elements_with_alternative_splits"] > 0
    cell["stages_where_an_alternative_changes_part_count"] += (
        result["elements_where_an_alternative_changes_part_count"] > 0)
    cell["stages_with_an_unread_cycle_in_forced_sums"] += result["distinct_unread_cycles_in_forced_sums"] > 0
    cell["stages_with_three_unread_labels_on_cycles_in_forced_sums"] += (
        result["distinct_unread_labels_in_forced_sums"] >= 3)
    cell["stages_with_three_cycles_and_an_unread_part"] += result["splits_with_three_cycles_and_an_unread_part"] > 0
    cell["stages_with_three_cycles_and_two_unread_parts"] += result["splits_with_three_cycles_and_two_unread_parts"] > 0
    cell["stages_with_three_eligible_parts_in_one_split"] += result["max_unread_parts_in_one_split"] >= 3
    cell["stages_with_bindings"] += bool(result["binding_certificates"])
    cell["max_forced_dimension"] = max(cell["max_forced_dimension"], result["forced_dimension"])
    cell["max_class_dimension"] = max(cell["max_class_dimension"], result["class_dimension"])
    cell["max_unread_labels"] = max(cell["max_unread_labels"], result["unread_labels"])
    cell["max_splits_per_element"] = max(cell["max_splits_per_element"], result["max_splits_per_element"])
    cell["max_cycles_per_split"] = max(cell["max_cycles_per_split"], result["most_cycles"])
    cell["max_unread_parts_in_one_split"] = max(cell["max_unread_parts_in_one_split"], result["max_unread_parts_in_one_split"])
    cell["elements_omitted_by_element_cap"] += max(0, (2 ** result["forced_dimension"]) - 2 ** 10)
    for metric in SPLIT_COUNTS:
        cell[metric] += result[metric]
    for suffix in ("", "unread_", "local_", "constant_", "move_varying_"):
        metric = f"distinct_{suffix}cycles_in_forced_sums"
        cell[metric] += result[metric]


def check_forced_record(expected, stage, result):
    errors = []
    for key, actual in [("distinctions", result["distinctions"]), ("dim Z", result["allowed_dimension"]),
                        ("dim of laws ∩ changes", result["law_change_dimension"]),
                        ("dim B", result["forced_dimension"])]:
        if expected.get(key) != actual:
            errors.append([key, expected.get(key), actual])
    listed = BinarySpan()
    for entry in expected.get("elements", []):
        value = 0
        for knot in entry["knots summing to it"]:
            value ^= stage.rows[knot]
        if value.bit_count() != entry["size"] or not value or value not in stage.forced:
            errors.append(["invalid forced certificate", entry])
        listed.add(value)
    if len(listed) != min(len(stage.forced), 6):
        errors.append(["rank of listed forced certificates", len(listed), min(len(stage.forced), 6)])
    return errors


def judge_summary(raw, expected, *, truncated_replay=False):
    rows = read_json_lines(raw)
    keys = Counter((row["start"], row["round"]) for row in rows)
    comparison_cells = defaultdict(Counter)
    disagreements = []
    for row in rows:
        key = (row["start"], row["round"])
        if key not in expected:
            continue
        exact = expected[key]
        cell = comparison_cells[exact["group"], key[1]]
        cell["rows_matched_to_case"] += 1
        cell["rows_with_three_or_more_cycles"] += row["most cycles in a split"] >= 3
        checks = {"dim B": exact["forced_dimension"], "elements read": exact["elements"],
                  "most cycles in a split": exact["most_cycles"],
                  "bindings": sorted((r["size"], r["parts"]) for r in exact["first_binding_by_size"])}
        normalized = dict(row, bindings=sorted((b["size"], b["parts"]) for b in row["bindings"]))
        for field, value in checks.items():
            if normalized.get(field) != value:
                disagreements.append([*key, field, normalized.get(field), value])
    return {
        "sha256": sha256(raw).hexdigest(), "rows": len(rows), "unique_keys": len(keys),
        "rows_with_bindings": sum(bool(row["bindings"]) for row in rows),
        "rows_with_three_or_more_cycles": sum(row["most cycles in a split"] >= 3 for row in rows),
        "unique_keys_with_three_or_more_cycles": len({(row["start"], row["round"]) for row in rows
                                                       if row["most cycles in a split"] >= 3}),
        "last_key": [rows[-1]["start"], rows[-1]["round"]],
        "duplicate_keys": [[*key, count] for key, count in sorted(keys.items()) if count > 1],
        "missing_replayed_keys": sorted(key for key in expected if key not in keys),
        "unmatched_archive_key_count": sum(key not in expected for key in keys),
        "unmatched_archive_keys": [] if truncated_replay else sorted(key for key in keys if key not in expected),
        "comparison_by_set_and_round": group_cells(comparison_cells), "field_disagreements": disagreements,
    }


def group_cells(cells):
    output = defaultdict(dict)
    for (group, round_number), cell in sorted(cells.items()):
        output[group][round_number] = dict(cell)
    return dict(output)


def round_census(start_items, grow, forced_archives, limit=None):
    cells = defaultdict(Counter)
    totals = Counter()
    expected_judged = {}
    archived_disagreements = []
    archived_forced_checked = 0
    literal_checked = 0
    ends = defaultdict(Counter)
    witness_rounds = {}
    narrow_denominators = []
    duplicate_replays = []
    proved_keys = {}
    replayed_names = defaultdict(set)
    for group in SETS:
        started = time.monotonic()
        for index, (name, supports) in enumerate(start_items(group)):
            if limit is not None and index >= limit:
                break
            assert name not in replayed_names[group]
            replayed_names[group].add(name)
            archived = forced_archives[group][name] if group in forced_archives else {}
            for round_number in range((3 if group == "witnesses" else 2) + 1):
                key = (name, round_number)
                archived_round = archived.get(round_number, {})
                if round_number:
                    supports, status = grow(supports)
                    if status != "funded":
                        ends[group, round_number][status] += 1
                        if group in forced_archives and archived_round.get("end") != status:
                            archived_disagreements.append([*key, "end", archived_round.get("end"), status])
                        break
                stage = Stage(supports)
                if len(stage.names) > 600:
                    ends[group, round_number]["not read"] += 1
                    if group in forced_archives and archived_round.get("end") != "not read":
                        archived_disagreements.append([*key, "end", archived_round.get("end"), "not read"])
                    break
                if len(stage.names) <= 10 and index % 59 == 0:
                    check_literal(stage)
                    literal_checked += 1
                result = summarize_stage(stage, preserve_examples=group == "witnesses")
                if group in forced_archives:
                    archived_forced_checked += 1
                    errors = check_forced_record(archived_round, stage, result)
                    if errors:
                        archived_disagreements.append([*key, *errors])
                count_cell(cells[group, round_number], result)
                if key in proved_keys:
                    assert proved_keys[key] == supports and key in expected_judged
                    assert result["forced_dimension"] == expected_judged[key]["forced_dimension"]
                    duplicate_replays.append(key)
                else:
                    count_cell(totals, result)
                    if name == "held out 7-239":
                        proved_keys[key] = supports
                if result["forced_dimension"] > 0 and key not in expected_judged:
                    expected_judged[key] = dict(result, group=group)
                if group == "witnesses":
                    witness_rounds.setdefault(name, {})[round_number] = result
                if (result["most_cycles"] >= 3 and result["unread_labels"] >= 3
                        or result["splits_with_three_cycles_and_an_unread_part"]):
                    narrow_denominators.append({"start": name, "round": round_number, "group": group,
                                                **{key: result[key] for key in (
                                                    "class_dimension", "unread_labels", "forced_dimension",
                                                    "most_cycles", "distinct_unread_cycles_in_forced_sums",
                                                    "distinct_unread_labels_in_forced_sums",
                                                    "max_unread_parts_in_one_split",
                                                    "splits_with_three_cycles_and_an_unread_part",
                                                    "splits_with_three_cycles_and_two_unread_parts",
                                                    "binding_certificates")}})
        print(f"{group} done in {time.monotonic() - started:.2f} s", flush=True)
    return {
        "totals_unique_stage_keys": dict(totals), "by_set_and_round": group_cells(cells),
        "stopped_by_set_and_round": group_cells(ends), "witness_rounds": witness_rounds,
        "literal_stage_checks": literal_checked,
        "forced_archive_records_checked": archived_forced_checked,
        "forced_archive_disagreements": archived_disagreements,
        "replayed_start_counts": {group: len(names) for group, names in replayed_names.items()},
        "archive_starts_not_replayed": {
            group: len(archives.keys() - replayed_names[group]) for group, archives in forced_archives.items()},
        "duplicate_replayed_keys": duplicate_replays, "narrow_denominator_cases": narrow_denominators,
    }, expected_judged


def main():
    from replay_growth import grow, start_items

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--limit-per-set", type=int)
    options = parser.parse_args()
    started = time.monotonic()
    controls = check_controls()
    forced, judge_versions, hashes, working_extends_committed = read_archives()
    summary, expected_judged = round_census(start_items, grow, forced, options.limit_per_set)
    summary.update({
        "limit_per_set": options.limit_per_set,
        "controls": controls,
        "elapsed_seconds": time.monotonic() - started,
        "source_file_hashes": hashes, "judge_original_commit": ORIGINAL_JUDGE,
        "working_judge_extends_committed_byte_for_byte": working_extends_committed,
        "judge_comparison": {name: judge_summary(raw, expected_judged, truncated_replay=options.limit_per_set is not None)
                             for name, raw in judge_versions.items()},
        "most_splits_examples": [{"start": key[0], "round": key[1],
                                  "max_splits_per_element": value["max_splits_per_element"]}
                                 for key, value in sorted(expected_judged.items(),
                                                          key=lambda item: -item[1]["max_splits_per_element"])[:5]],
        "method_note": (
            "A class label is any nonconstant binary linear invariant modulo the laws. Unread counts exclude the "
            "union of the individual knots' readable subspaces. Cycles in forced sums are simple, distinction-" 
            "disjoint when split, and use only twice-held distinctions. Class label denominators alone neither "
            "require nor imply a cycle carrier. A distinction can contribute repeatedly across different splits "
            "and sums, while the distinct-cycle counts are summed over stages after deduplication within each stage. "
            "The witness row for the 240th accepted seven-knot draw repeats the held-out row through round two."
        ),
    })
    options.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
