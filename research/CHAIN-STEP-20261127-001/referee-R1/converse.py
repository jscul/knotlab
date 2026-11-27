"""Recount the bounded converse and audit the bare chains by state enumeration.

The state screen can only discard triples with all eight words witnessed.
Every surviving triple is evaluated on all allowed words. Global complement
preserves every source law and each agreement, including after deletions.
"""

import argparse
from collections import Counter, defaultdict
from functools import cache
from itertools import combinations
import json
import os
from pathlib import Path
import resource
import sys
from tempfile import NamedTemporaryFile
from time import perf_counter

import numpy as np


HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parents[1]
sys.path.insert(0, str(RESEARCH / "NAE-LAYER-20261127-001/referee-R1"))
from growth_rule import advance, supports_of


CENSUS = RESEARCH / "FORBID-EDITS-20261126-001/starts.json"
CLOSED_CONTROL = RESEARCH / "UPPER-GROWN-20261127-001/referee-R1/upper_four_closed.json"
BARE_ARCHIVE = RESEARCH / "FOUR-CLAUSE-20261127-001/post/chain_replay.json"
PAIR_PROJECTIONS = tuple(
    frozenset(w & (7 ^ (1 << bit)) for w in range(8)) for bit in range(3)
)


def words(cells):
    return tuple(i for i, cell in enumerate(cells) if cell)


def pairs_free(image):
    return all(
        {w & (7 ^ (1 << bit)) for w in image} == projection
        for bit, projection in enumerate(PAIR_PROJECTIONS)
    )


def split(cells, zero, one):
    return tuple(cell & value for cell in cells for value in (zero, one))


def read_bits(values):
    packed = np.packbits(values, bitorder="little")
    return int.from_bytes(packed, byteorder="little")


def agree(states, mask):
    on = states & mask
    return (on == 0) | (on == mask)


def get_masks(supports):
    names = sorted(set().union(*map(set, supports)))
    positions = {name: i for i, name in enumerate(names)}
    masks = tuple(sum(1 << positions[x] for x in support) for support in supports)
    return names, masks


def chain_count_of_eight(supports):
    triples = tuple(frozenset(support) for support in supports if len(support) == 3)
    if len(triples) < 8:
        return 0
    overlaps = [0] * len(triples)
    joins = [[] for _ in triples]
    for (i, left), (j, right) in combinations(enumerate(triples), 2):
        shared = len(left & right)
        if shared:
            overlaps[i] |= 1 << j
            overlaps[j] |= 1 << i
        if shared == 1:
            joins[i].append(j)
            joins[j].append(i)

    def extend(first, last, length, unavailable):
        if length == 8:
            return int(first < last)
        return sum(
            extend(first, nxt, length + 1, unavailable | (1 << nxt) | overlaps[last])
            for nxt in joins[last] if not unavailable & (1 << nxt)
        )

    return sum(extend(i, i, 1, 1 << i) for i in range(len(triples)))


class Stage:
    def __init__(self, supports, *, full_complements=False):
        self.names, self.source_masks = get_masks(supports)
        self.width = len(self.names)
        self.assignment_count = 1 << (self.width if full_complements else self.width - 1)
        self.orbit_size = 1 if full_complements else 2
        raw = np.arange(self.assignment_count, dtype=np.uint32)
        self.allowed = np.logical_and.reduce([~agree(raw, law) for law in self.source_masks])
        self.states = raw[self.allowed]
        self.full = (1 << len(self.states)) - 1

        rules = []
        for mask in self.source_masks:
            on = self.states & mask
            keys = np.minimum(on, on ^ mask)
            rules.append(tuple(read_bits(keys == v) for v in np.unique(keys)))

        self.carriers = []
        self.truth = []
        tables = []
        for width in (2, 3):
            for indices in combinations(range(self.width), width):
                mask = sum(1 << index for index in indices)
                table = agree(self.states, mask)
                one = read_bits(table)
                zero = self.full ^ one
                if not (zero and one):
                    continue
                if not all(any((zero & cell) and (one & cell) for cell in rule) for rule in rules):
                    continue
                self.carriers.append(mask)
                self.truth.append((zero, one))
                tables.append(table)
        self.tables = np.array(tables, dtype=bool)

    def lower_bonds(self, sample_limit):
        """Every disjoint triple with free pairs and at least one missing word."""
        bonds = {}
        starts_with = len(self.carriers)
        total_disjoint = 0
        total_exact = 0
        if starts_with < 3:
            return bonds, total_disjoint, total_exact

        masks = np.array(self.carriers, dtype=np.uint32)
        disjoint = np.triu((masks[:, None] & masks) == 0)
        rng = np.random.default_rng(0)
        order = rng.permutation(len(self.states))
        for first in range(starts_with - 2):
            later = np.flatnonzero(disjoint[first])
            if len(later) < 2:
                continue
            eligible = disjoint[np.ix_(later, later)]
            total_disjoint += int(eligible.sum())
            candidates = eligible.copy()

            if sample_limit:
                missing = np.zeros_like(eligible)
                for value in (False, True):
                    sample = order[self.tables[first, order] == value][:sample_limit]
                    view = self.tables[later[:, None], sample].astype(np.float32)
                    both = view @ view.T
                    one = view.sum(axis=1)
                    # These are the four exact pair counts in the finite screen.
                    # A zero is checked again against all allowed states below.
                    missing |= (
                        (both == 0) | (both == one[:, None]) | (both == one)
                        | (both == one[:, None] + one - len(sample))
                    )
                candidates &= missing

            js, ks = np.nonzero(candidates)
            total_exact += len(js)
            prev = -1
            for j, k in zip(later[js].tolist(), later[ks].tolist(), strict=True):
                if j != prev:
                    two = split(self.truth[first], *self.truth[j])
                    prev = j
                image = words(split(two, *self.truth[k]))
                if len(image) < 8 and pairs_free(image):
                    bonds[(first, j, k)] = tuple(w for w in range(8) if w not in image)

        return bonds, total_disjoint, total_exact

    def six_eligible_carriers(self):
        @cache
        def pack(choices, remaining, count):
            if count == 0:
                return True
            if remaining.bit_count() < 2 * count:
                return False
            for index, mask in enumerate(choices):
                if mask & remaining == mask and pack(choices[index + 1:], remaining ^ mask, count - 1):
                    return True
            return False

        return pack(tuple(self.carriers), (1 << self.width) - 1, 6)

    def find_patterns(self, bonds):
        """Join clauses on a shared signed reading and check the two completions."""
        by_single = defaultdict(list)
        by_pair = defaultdict(set)
        counts = Counter()
        masks = self.carriers
        for triple, missing in bonds.items():
            if len(missing) != 1:
                continue
            w = missing[0]
            lits = tuple(2 * i + ((w >> (2 - j)) & 1) for j, i in enumerate(triple))
            counts["single_word_lower_bonds"] += 1
            if self.width - sum(masks[i].bit_count() for i in triple) >= 6:
                counts["single_word_lower_bonds_with_space_for_three_carriers"] += 1
            for j, pivot in enumerate(lits):
                other = lits[:j] + lits[j + 1:]
                used = masks[other[0] // 2] | masks[other[1] // 2]
                by_single[pivot].append((other, used))
                by_pair[other].add(pivot)

        if self.width < 12 or len(bonds) < 2:
            return {}, counts

        @cache
        def can_add_carrier(used):
            spare = tuple(i for i in range(self.width) if not used >> i & 1)
            return any(
                sum(1 << i for i in trial) in eligible_masks
                for size in (2, 3) for trial in combinations(spare, size)
            )

        eligible_masks = set(masks)
        patterns = {}
        for pivot, entries in by_single.items():
            pivot_mask = masks[pivot // 2]
            for ((a, b), first_mask), ((c, d), second_mask) in combinations(entries, 2):
                if first_mask & second_mask:
                    continue
                counts["two_clauses_with_only_one_shared_signed_reading"] += 1
                used = first_mask | second_mask | pivot_mask
                if not can_add_carrier(used):
                    continue
                counts["two_clauses_with_an_eligible_sixth_carrier"] += 1
                for u, v in ((c, d), (d, c)):
                    first_join = tuple(sorted((a, u)))
                    second_join = tuple(sorted((b, v)))
                    for sixth in by_pair.get(first_join, set()) & by_pair.get(second_join, set()):
                        if used & masks[sixth // 2]:
                            continue
                        # The repeated descriptions of the four clauses give the same key.
                        clauses = tuple(sorted(tuple(sorted(clause)) for clause in (
                            (pivot, a, b), (pivot, u, v), (sixth, a, u), (sixth, b, v)
                        )))
                        pairs = tuple(sorted(tuple(sorted(pair)) for pair in ((pivot, sixth), (a, v), (b, u))))
                        patterns[clauses] = pairs

        return patterns, counts

    def report_patterns(self, bonds, patterns, start_laws):
        if not patterns:
            return []

        def literal_values(lit):
            return self.truth[lit // 2][lit & 1]

        def show(lit):
            mask = self.carriers[lit // 2]
            return {
                "carrier": [x for i, x in enumerate(self.names) if mask >> i & 1],
                "excluded_agreement_value": lit & 1,
            }

        raw = np.arange(self.assignment_count, dtype=np.uint32)
        failed = [agree(raw, source) for source in self.source_masks]
        singly_failed = np.sum(failed, axis=0) == 1
        result = []
        for clauses, pairs in sorted(patterns.items()):
            lower_known = {tuple(lit // 2 for lit in clause) for clause in clauses}
            raw_truth = {}
            for pair in pairs:
                for lit in pair:
                    raw_truth[lit] = agree(raw, self.carriers[lit // 2]) == bool(lit & 1)
            for both in range(3):
                upper = tuple(
                    literal_values(a) & literal_values(b) if i == both else literal_values(a) | literal_values(b)
                    for i, (a, b) in enumerate(pairs)
                )
                raw_upper = tuple(
                    raw_truth[a] & raw_truth[b] if i == both else raw_truth[a] | raw_truth[b]
                    for i, (a, b) in enumerate(pairs)
                )
                cells = (self.full,)
                for one in upper:
                    cells = split(cells, self.full ^ one, one)
                image = words(cells)
                fixed_by_selected = []
                fixed_by_any = [0, 0, 0]
                for triple in bonds:
                    first, second, third = (self.truth[i] for i in triple)
                    lower_cells = split(split(first, *second), *third)
                    for index, one in enumerate(upper):
                        zero = self.full ^ one
                        if not any((zero & cell) and (one & cell) for cell in lower_cells):
                            fixed_by_any[index] += 1
                            if triple in lower_known:
                                fixed_by_selected.append([index, [show(2 * i)["carrier"] for i in triple]])
                upper111 = singly_failed & np.logical_and.reduce(raw_upper)
                restored = [self.orbit_size * int(np.count_nonzero(upper111 & failure)) for failure in failed]
                result.append({
                    "clauses": [[show(lit) for lit in clause] for clause in clauses],
                    "pairs": [[show(lit) for lit in pair] for pair in pairs],
                    "both_pair_index": both,
                    "upper_words": list(image),
                    "upper_word_assignment_counts": [self.orbit_size * cell.bit_count() for cell in cells],
                    "pairs_free": pairs_free(image),
                    "upper_determinations_by_selected_bonds": fixed_by_selected,
                    "lower_bonds_determining_each_upper_reading": fixed_by_any,
                    "restorations_after_each_source_law_deletion": restored,
                    "a_birth_law_needed": any(restored[start_laws:]),
                })
        return result


def examine(supports, start_laws, sample_limit):
    start = perf_counter()
    stage = Stage(supports)
    bonds, disjoint, exact = stage.lower_bonds(sample_limit)
    patterns, candidates = stage.find_patterns(bonds)
    roles = stage.report_patterns(bonds, patterns, start_laws)

    # The archive counts each signed pairing once. Preserve distinct clause
    # families as well, and test every role without its 60-pattern cap.
    signed_pairings = set(patterns.values())
    archive_steps = set()
    strict_steps = 0
    for row in roles:
        if 0 < len(row["upper_words"]) < 8 and row["pairs_free"] and not row["upper_determinations_by_selected_bonds"]:
            archive_steps.add((json.dumps(row["pairs"], sort_keys=True), row["both_pair_index"]))
            strict_steps += int(len(row["upper_words"]) == 7 and not any(row["lower_bonds_determining_each_upper_reading"]))

    return {
        "knots": len(supports),
        "distinctions": stage.width,
        "eight_knot_chains": chain_count_of_eight(supports),
        "allowed_assignments": len(stage.states) * stage.orbit_size,
        "eligible_agreements": len(stage.carriers),
        "six_disjoint_eligible_carriers": stage.six_eligible_carriers(),
        "disjoint_eligible_triples": disjoint,
        "triples_checked_on_all_allowed_states": exact,
        "lower_bonds": len(bonds),
        "single_word_lower_bonds": candidates["single_word_lower_bonds"],
        "single_word_lower_bonds_with_space_for_three_carriers": candidates["single_word_lower_bonds_with_space_for_three_carriers"],
        "two_clauses_with_only_one_shared_signed_reading": candidates["two_clauses_with_only_one_shared_signed_reading"],
        "two_clauses_with_an_eligible_sixth_carrier": candidates["two_clauses_with_an_eligible_sixth_carrier"],
        "signed_pairings": len(signed_pairings),
        "four_clause_patterns": len(patterns),
        "upper_readings": len(roles),
        "archive_step_definition": len(archive_steps),
        "seven_word_steps_with_all_bond_locality_check": strict_steps,
        "seconds": round(perf_counter() - start, 6),
        **({"upper": roles, "source_supports": supports} if roles else {}),
    }


def raw_records():
    records = {}
    for path in sorted((HERE.parent / "out").glob("cs_*.jsonl")):
        with path.open() as source:
            for line in source:
                record = json.loads(line)
                start = int(record["start"].removeprefix("census "))
                if start in records:
                    raise ValueError(f"duplicate census entry {start}")
                records[start] = {row["round"]: row for row in record["rounds"]}
    return records


def archive_comparison(census, records):
    included = []
    omitted = []
    differences = []
    for index, raw in sorted(records.items()):
        supports = supports_of(census[index])
        starting_laws = len(supports)
        for count in (1, 2):
            result = advance(supports)
            if result.status != "funded":
                if count in raw:
                    differences.append([index, count, "round funded only in archive"])
                break
            supports = result.supports
            names = set().union(*map(set, supports))
            chains = chain_count_of_eight(supports)
            covered = len(names) <= 19
            actual = [len(supports), len(names), min(1000, chains), covered]
            original = raw.get(count)
            archived = None if original is None else [
                original["knots"], original["distinctions"], original["chains"], "converse" in original
            ]
            if actual != archived:
                differences.append([index, count, actual, archived])
            if covered:
                included.append((index, count, supports, starting_laws, original["converse"]))
            else:
                omitted.append({
                    "census_entry": index, "round": count, "distinctions": len(names),
                    "eight_knot_chains": chains,
                    "carried_steps_in_archive": sum(record["a step"] for record in original.get("mapped", ())),
                })
    return included, omitted, differences


def aggregate(rows):
    fields = (
        "eligible_agreements", "disjoint_eligible_triples", "lower_bonds", "single_word_lower_bonds",
        "single_word_lower_bonds_with_space_for_three_carriers",
        "two_clauses_with_only_one_shared_signed_reading", "two_clauses_with_an_eligible_sixth_carrier",
        "four_clause_patterns", "upper_readings", "archive_step_definition",
        "seven_word_steps_with_all_bond_locality_check", "eight_knot_chains",
    )
    return {
        "stages": len(rows),
        "stages_at_least_12_distinctions": sum(row["distinctions"] >= 12 for row in rows),
        "stages_at_least_17_distinctions": sum(row["distinctions"] >= 17 for row in rows),
        "stages_with_six_disjoint_eligible_carriers": sum(row["six_disjoint_eligible_carriers"] for row in rows),
        "stages_with_at_least_four_single_word_lower_bonds": sum(row["single_word_lower_bonds"] >= 4 for row in rows),
        "stages_with_at_least_four_size_eligible_single_word_lower_bonds": sum(
            row["single_word_lower_bonds_with_space_for_three_carriers"] >= 4 for row in rows
        ),
        "stages_with_nonzero": {key: sum(row[key] > 0 for row in rows) for key in fields},
        "totals": {key: sum(row[key] for row in rows) for key in fields},
        "seconds": round(sum(row["seconds"] for row in rows), 6),
    }


def bare_chain(count):
    return tuple((2 * i, 2 * i + 1, 2 * i + 2) for i in range(count))


def controls(census, sample_limit):
    cases = {
        "bare_chain_seven": (bare_chain(7), 7),
        "bare_chain_eight": (bare_chain(8), 8),
    }
    supports = supports_of(census[5260])
    start_laws = len(supports)
    for _ in range(2):
        result = advance(supports)
        if result.status != "funded":
            raise ValueError("earlier five-knot positive control did not fund two rounds")
        supports = result.supports
    cases["earlier_positive_second_round_census_5260"] = supports, start_laws
    closed = next(row["witness"] for row in json.loads(CLOSED_CONTROL.read_text()) if "witness" in row)
    cases["earlier_closed_ten_knot_positive"] = closed["knots"], len(closed["knots"])
    result = {name: examine(supports, start_laws, sample_limit) for name, (supports, start_laws) in cases.items()}

    # On small controls check the screen against an unscreened replay with
    # both representatives kept, as well as a literal projection oracle.
    small = []
    for index in (0, 2, 420):
        supports = supports_of(census[index])
        direct = Stage(supports, full_complements=True)
        screened = Stage(supports)
        bonds, _, _ = screened.lower_bonds(sample_limit)
        expected, _, _ = direct.lower_bonds(0)
        literal = {}
        for triple in combinations(range(len(direct.carriers)), 3):
            a, b, c = (direct.carriers[i] for i in triple)
            if a & b or a & c or b & c:
                continue
            image = set(
                4 * direct.tables[triple[0]].astype(np.uint8)
                + 2 * direct.tables[triple[1]].astype(np.uint8)
                + direct.tables[triple[2]]
            )
            if len(image) < 8 and pairs_free(image):
                literal[triple] = tuple(w for w in range(8) if w not in image)
        if screened.carriers != direct.carriers or bonds != expected or expected != literal:
            raise ValueError(f"full-state bond control differs on census entry {index}")
        small.append({"census_entry": index, "round": 0, "lower_bonds": len(bonds), "distinctions": direct.width})
    result["literal_state_controls"] = small
    return result


def bare_replay(lengths, sample_limit):
    start = perf_counter()
    archive = json.loads(BARE_ARCHIVE.read_text())
    rows = {}
    summary = {}
    differences = []
    for length in lengths:
        label = f"chain of {length}"
        record = examine(bare_chain(length), length, sample_limit)
        rows[label] = record
        roles = record.get("upper", [])
        pairings = {}
        for role in roles:
            pairing = frozenset(
                frozenset((tuple(member["carrier"]), member["excluded_agreement_value"]) for member in pair)
                for pair in role["pairs"]
            )
            pairings[(pairing, role["both_pair_index"])] = role
        compared = {
            "bonds": record["lower_bonds"],
            "patterns": record["signed_pairings"],
            "steps": record["archive_step_definition"],
            "every law needed": sum(all(role["restorations_after_each_source_law_deletion"]) for role in pairings.values()),
        }
        expected = archive[label]
        for key, value in compared.items():
            if value != expected[key]:
                differences.append([label, key, value, expected[key]])
        example = expected["example"]
        example_matches = not pairings if example is None else frozenset(
            frozenset((tuple(carrier), sign) for carrier, sign in example[i:i + 2])
            for i in (0, 2, 4)
        ) in {pairing for pairing, _ in pairings}
        if not example_matches:
            differences.append([label, "archived example missing from recount"])
        summary[label] = {
            **compared,
            "seven_word_steps_with_all_bond_locality_check": record["seven_word_steps_with_all_bond_locality_check"],
            "roles_by_number_of_necessary_source_laws": dict(sorted(Counter(
                sum(count > 0 for count in role["restorations_after_each_source_law_deletion"])
                for role in pairings.values()
            ).items())),
            "archived_example_reproduced": example_matches,
            "seconds": record["seconds"],
        }
    return {
        "mode": "bare chain replay",
        "sample_screen_max_states_per_first_reading_value": sample_limit,
        "sample_screen_seed": 0,
        "stage_summary": summary,
        "converse_differences": differences,
        "rows": rows,
        "seconds": round(perf_counter() - start, 6),
        "peak_rss_KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }


def merge_partition_results(paths):
    parts = sorted((json.loads(path.read_text()) for path in paths), key=lambda part: part["part"])
    part_ids = {part["part"] for part in parts}
    if part_ids != {f"{i}/{len(parts)}" for i in range(len(parts))}:
        raise ValueError("partition results do not cover the declared partition exactly once")

    common_fields = (
        "sample_screen_max_states_per_first_reading_value", "sample_screen_seed", "census_starts_in_archive",
        "eligible_stages_by_round", "eligible_stages_by_distinctions", "omitted_stages_by_round",
        "omitted_stages_with_eight_knot_chains", "coverage_differences",
    )
    first = parts[0]
    if any(part[key] != first[key] for part in parts for key in common_fields):
        raise ValueError("partitions disagree on the configuration or roster")

    rows = sorted((row for part in parts for row in part["rows"]), key=lambda row: (row["census_entry"], row["round"]))
    keys = [(row["census_entry"], row["round"]) for row in rows]
    archive_keys = sorted(
        (start, t) for start, times in raw_records().items() for t, row in times.items() if "converse" in row
    )
    if keys != archive_keys:
        raise ValueError("merged stage rows do not exactly match the archive converse roster")

    def controls_without_timing(part):
        return {
            key: value if isinstance(value, list) else {k: v for k, v in value.items() if k != "seconds"}
            for key, value in part["controls"].items()
        }

    if any(controls_without_timing(part) != controls_without_timing(first) for part in parts):
        raise ValueError("partition controls disagree")

    return {
        "mode": "all stages in merged partitions",
        **{key: first[key] for key in common_fields},
        "not_run_eligible_stages": 0,
        "converse_differences": [diff for part in parts for diff in part["converse_differences"]],
        "stage_summary": aggregate(rows),
        "by_round": {t: aggregate([row for row in rows if row["round"] == t]) for t in (1, 2)},
        "controls": first["controls"],
        "rows": rows,
        "parts": [
            {"part": part["part"], "seconds": part["seconds"], "peak_rss_KiB": part["peak_rss_KiB"],
             "stages": len(part["rows"])}
            for part in parts
        ],
    }


def write_result(output, destination, *, replace):
    target = NamedTemporaryFile(mode="w", prefix="converse_tmp_", suffix=".json", dir=HERE, delete=False)
    scratch = Path(target.name)
    try:
        with target:
            json.dump(output, target, indent=2)
            target.write("\n")
        if replace:
            scratch.replace(destination)
        else:
            os.link(scratch, destination)
    finally:
        scratch.unlink(missing_ok=True)
    print(json.dumps({
        "stage_summary": output["stage_summary"],
        "converse_differences": len(output["converse_differences"]),
        "resources": output.get("parts", {k: output[k] for k in ("seconds", "peak_rss_KiB") if k in output}),
    }))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="one representative eligible stage of each size")
    parser.add_argument("--prefix", type=int, help="limit to the first indicated number of stages by census entry and round")
    parser.add_argument("--part", help="one part I/N of a size-balanced partition, with I starting from zero")
    parser.add_argument("--merge", type=Path, nargs="+", help="check coverage and merge the completed partitions")
    parser.add_argument("--bare-lengths", type=int, choices=(6, 7, 8, 9), nargs="+", help="replay selected bare chain lengths")
    parser.add_argument("--sample-screen", type=int, default=96, help="states per first-reading value used to safely reject full triples")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--replace", action="store_true", help="atomically replace an existing generated output")
    args = parser.parse_args()
    t0 = perf_counter()
    if args.output.parent.resolve() != HERE or not args.output.name.startswith("converse") or args.output.suffix != ".json":
        parser.error("output must be a converse*.json file beside this script")
    if args.output.exists() and not args.replace:
        parser.error("output exists; --replace allows replay over a generated result")
    if sum((args.pilot, args.prefix is not None, args.part is not None, args.merge is not None, args.bare_lengths is not None)) > 1:
        parser.error("choose one of a size pilot, a deterministic prefix, a partition, a merge or bare lengths")
    if args.sample_screen < 0 or (args.prefix is not None and args.prefix < 0):
        parser.error("the state screen and prefix must be nonnegative")
    if args.bare_lengths:
        if len(args.bare_lengths) != len(set(args.bare_lengths)):
            parser.error("bare chain lengths must be distinct")
        write_result(bare_replay(args.bare_lengths, args.sample_screen), args.output, replace=args.replace)
        return
    if args.merge:
        if args.output.resolve() in {path.resolve() for path in args.merge}:
            parser.error("merged output must be separate from partition inputs")
        write_result(merge_partition_results(args.merge), args.output, replace=args.replace)
        return
    census = json.loads(CENSUS.read_text())
    records = raw_records()
    eligible, omitted, coverage_differences = archive_comparison(census, records)
    if args.pilot:
        by_size = {}
        for case in eligible:
            n = len(set().union(*map(set, case[2])))
            by_size.setdefault(n, case)
        selected = list(by_size.values())
    elif args.part:
        index, total = map(int, args.part.split("/"))
        if not 0 <= index < total:
            parser.error("partition index must be from zero to one less than the number of parts")
        size_order = sorted(eligible, key=lambda case: len(set().union(*map(set, case[2]))))
        selected = sorted(size_order[index::total], key=lambda case: case[:2])
    else:
        selected = eligible[:args.prefix]

    check = controls(census, args.sample_screen)
    rows = []
    differences = []
    for i, (index, count, supports, starting_laws, archived) in enumerate(selected, 1):
        row = examine(supports, starting_laws, args.sample_screen)
        row.update({"census_entry": index, "round": count})
        rows.append(row)
        new = {"patterns": row["signed_pairings"], "steps": row["archive_step_definition"]}
        if new != archived:
            differences.append({"census_entry": index, "round": count, "recount": new, "archive": archived})
        if i % 100 == 0:
            print(f"Recounted {i}/{len(selected)} stages in {perf_counter() - t0:.1f} seconds", file=sys.stderr, flush=True)

    output = {
        "mode": "size pilot" if args.pilot else "partition" if args.part else "complete" if args.prefix is None else "deterministic prefix",
        "part": args.part,
        "sample_screen_max_states_per_first_reading_value": args.sample_screen,
        "sample_screen_seed": 0,
        "census_starts_in_archive": len(records),
        "eligible_stages_by_round": dict(Counter(row[1] for row in eligible)),
        "eligible_stages_by_distinctions": dict(sorted(Counter(len(set().union(*map(set, row[2]))) for row in eligible).items())),
        "omitted_stages_by_round": dict(Counter(row["round"] for row in omitted)),
        "omitted_stages_with_eight_knot_chains": [row for row in omitted if row["eight_knot_chains"]],
        "not_run_eligible_stages": len(eligible) - len(rows),
        "coverage_differences": coverage_differences,
        "converse_differences": differences,
        "stage_summary": aggregate(rows),
        "by_round": {t: aggregate([row for row in rows if row["round"] == t]) for t in (1, 2)},
        "controls": check,
        "rows": rows,
        "seconds": round(perf_counter() - t0, 6),
        "peak_rss_KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    write_result(output, args.output, replace=args.replace)


if __name__ == "__main__":
    main()
