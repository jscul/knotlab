"""Recount the marked-loose parity presentations and widen their scope."""

import argparse
from collections import Counter
from itertools import combinations
import json
from pathlib import Path

from census_tools import connected, roster, tree


HERE = Path(__file__).resolve().parent
FROZEN = HERE.parent / "frozen_parity.jsonl"
EXTENSIONS = ("two_place", "disconnected", "different_knot_count")


def pieces(mask):
    while mask:
        bit = mask & -mask
        yield bit
        mask ^= bit


def parity_span(rows):
    implied = {0}
    for mask in rows:
        implied |= {prev ^ mask for prev in implied}
    return implied


def multiplicities(rows):
    once = twice = 0
    for mask in rows:
        assert not mask & twice
        twice |= mask & once
        once |= mask
    return once ^ twice, twice


def exact_covers(choices, single, double, target_size):
    """Consume every named distinction's remaining multiplicity exactly."""
    def visit(available, once, twice, selected):
        remaining = once | twice
        if not remaining:
            if len(parity_span(selected)) == target_size:
                yield tuple(sorted(selected))
            return

        available = [row for row in available if row & remaining == row]
        fewest_branches = None
        for bit in pieces(remaining):
            holders = [row for row in available if row & bit]
            needed = 2 if bit & twice else 1
            count = len(holders)
            if count < needed:
                return
            branches = count * (count - 1) // 2 if needed == 2 else count
            if fewest_branches is None or branches < fewest_branches:
                chosen_bit, chosen_holders, needed_here = bit, holders, needed
                fewest_branches = branches

        others = [row for row in available if not row & chosen_bit]
        for chosen in combinations(chosen_holders, needed_here):
            first = chosen[0]
            second = chosen[1] if needed_here == 2 else 0
            if once & first & second:
                continue
            used_once = first ^ second
            next_once = (once & ~used_once) | (twice & used_once)
            next_twice = twice & ~(first | second)
            yield from visit(others, next_once, next_twice, selected + chosen)

    return visit(choices, single, double, ())


def allowed_states(rows, width):
    return {state for state in range(1 << width)
            if all((state & row).bit_count() % 2 == 0 for row in rows)}


def direct_covers(choices, single, double, target):
    """Small control using subsets, column counts and literal truth tables."""
    width = (single | double).bit_length()
    columns = [1 << i for i in range(width)]
    counts = [int(bool((single | double) & b)) + int(bool(double & b)) for b in columns]
    return {
        group
        for size in range(1, len(choices) + 1)
        for group in combinations(choices, size)
        if [sum(bool(b & row) for row in group) for b in columns] == counts
        and allowed_states(group, width) == target
    }


def named(mask):
    return [bit.bit_length() - 1 for bit in pieces(mask)]


def read_start(index, rows, recorded, witnesses):
    rows = tuple(sorted(rows))
    loose, shared = multiplicities(rows)
    width = (loose | shared).bit_length()
    span = parity_span(rows)
    choices = sorted(row for row in span if row.bit_count() >= 2)
    broader = list(exact_covers(choices, loose, shared, len(span)))
    assert len(broader) == len(set(broader))
    assert rows in broader
    brute_subset_control = len(choices) <= 7
    if brute_subset_control:
        actual = allowed_states(rows, width)
        assert set(broader) == direct_covers(choices, loose, shared, actual)

    source_reading = tree(rows)
    source_families, source_levels = source_reading
    source_holders = sum(bool(row & loose) for row in rows)
    intermediate = sum(1 < len(groups) < len(source_families) for _, groups in source_levels)
    frozen_readings, broad_readings = set(), set()
    frozen_holdings, broad_holdings = set(), set()
    frozen_total = 0
    by_extensions = Counter()
    witness_rows = {}
    for alternative in broader:
        reading = tree(alternative)
        holdings = tuple(row for row in alternative if row & loose)
        names = tuple(name for name, condition in zip(EXTENSIONS, (
            any(row.bit_count() == 2 for row in alternative),
            not connected(alternative),
            len(alternative) != len(rows),
        )) if condition)
        broad_readings.add(reading)
        broad_holdings.add(holdings)
        if not names:
            frozen_total += 1
            frozen_readings.add(reading)
            frozen_holdings.add(holdings)
        else:
            group = "+".join(names)
            by_extensions[group] += 1
            witness_rows.setdefault(group, alternative)
        if reading != source_reading:
            witness_rows.setdefault("changed_tree", alternative)
        if reading[0] != source_families:
            witness_rows.setdefault("changed_families", alternative)

    if frozen_total == 1 and witness_rows:
        key = next(iter(witness_rows))
        witness_rows["frozen_unique_with_broader_alternative"] = witness_rows[key]
    if frozen_total > 1 and intermediate:
        witness_rows["frozen_alternative_with_intermediate_merge"] = next(
            alt for alt in broader if alt != rows and connected(alt)
            and len(alt) == len(rows) and all(r.bit_count() >= 3 for r in alt)
        )
    for label, alternative in witness_rows.items():
        if label in witnesses:
            continue
        actual = allowed_states(rows, width)
        assert actual == allowed_states(alternative, width)
        witnesses[label] = {
            "census_index": index,
            "source_supports": [named(row) for row in rows],
            "alternative_supports": [named(row) for row in alternative],
            "marked_loose": named(loose),
            "literal_allowed_state_count": len(actual),
            "source_family_and_tree_masks": source_reading,
            "alternative_family_and_tree_masks": tree(alternative),
        }

    expected = {
        "start": f"census {index}",
        "presentations": frozen_total,
        "capped": False,
        "family partitions": len({fam for fam, _ in frozen_readings}),
        "trees": len(frozen_readings),
        "own tree among them": source_reading in frozen_readings,
    }
    mismatch = None
    if expected != recorded:
        mismatch = {"index": index, "independent": expected, "archived": recorded}
    return {
        "index": index,
        "source_knots": len(rows),
        "distinctions": width,
        "loose": loose.bit_count(),
        "loose_holders": source_holders,
        "families": len(source_families),
        "intermediate_merge_tiers": intermediate,
        "brute_subset_control": brute_subset_control,
        "frozen_presentations": frozen_total,
        "broader_presentations": len(broader),
        "frozen_families": expected["family partitions"],
        "broader_families": len({fam for fam, _ in broad_readings}),
        "frozen_trees": len(frozen_readings),
        "broader_trees": len(broad_readings),
        "frozen_loose_holding_support_sets": len(frozen_holdings),
        "broader_loose_holding_support_sets": len(broad_holdings),
        "added_presentations_by_relaxation": dict(sorted(by_extensions.items())),
    }, mismatch


def summary(rows, scope):
    counts = Counter(r[f"{scope}_presentations"] for r in rows)
    alternatives = [r for r in rows if r[f"{scope}_presentations"] > 1]
    return {
        "presentations": sum(k * v for k, v in counts.items()),
        "presentation_histogram": dict(sorted(counts.items())),
        "one_presentation": counts[1],
        "multiple_presentations": len(alternatives),
        "multiple_family_partitions": sum(r[f"{scope}_families"] > 1 for r in rows),
        "multiple_tree_readings": sum(r[f"{scope}_trees"] > 1 for r in rows),
        "multiple_loose_holding_support_sets": sum(
            r[f"{scope}_loose_holding_support_sets"] > 1 for r in rows
        ),
        "multiple_presentations_with_two_or_more_loose": sum(r["loose"] >= 2 for r in alternatives),
        "multiple_presentations_with_two_or_more_loose_holders": sum(
            r["loose_holders"] >= 2 for r in alternatives
        ),
        "multiple_presentations_with_two_or_more_families": sum(
            r["families"] >= 2 for r in alternatives
        ),
        "multiple_presentations_with_three_or_more_families": sum(
            r["families"] >= 3 for r in alternatives
        ),
        "multiple_presentations_with_intermediate_merge": sum(
            r["intermediate_merge_tiers"] > 0 for r in alternatives
        ),
    }


def run(pilot):
    cases = roster()
    recorded = [json.loads(line) for line in FROZEN.read_text().splitlines()]
    archived_tally = recorded.pop()["tally"]
    assert len(cases) == len(recorded) == 7075
    size = len(cases) if pilot is None else pilot
    indexes = [i * len(cases) // size for i in range(size)]
    rows, mismatches, witnesses = [], [], {}
    extension_starts, extension_presentations = Counter(), Counter()
    for index in indexes:
        row, mismatch = read_start(index, cases[index], recorded[index], witnesses)
        rows.append(row)
        if mismatch is not None:
            mismatches.append(mismatch)
        extensions = row["added_presentations_by_relaxation"]
        extension_starts.update(extensions.keys())
        extension_presentations.update(extensions)

    aggregate = {
        "census_starts_read": len(rows),
        "literal_subset_controls": sum(r["brute_subset_control"] for r in rows),
        "source_knot_count_histogram": dict(sorted(Counter(r["source_knots"] for r in rows).items())),
        "source_loose_count_histogram": dict(sorted(Counter(r["loose"] for r in rows).items())),
        "source_family_count_histogram": dict(sorted(Counter(r["families"] for r in rows).items())),
        "source_starts_with_intermediate_merge": sum(
            r["intermediate_merge_tiers"] > 0 for r in rows
        ),
        "frozen": summary(rows, "frozen"),
        "broader": summary(rows, "broader"),
        "frozen_unique_with_broader_alternative": sum(
            r["frozen_presentations"] == 1 < r["broader_presentations"] for r in rows
        ),
        "added_presentations_by_relaxation": dict(sorted(extension_presentations.items())),
        "starts_with_added_presentations_by_relaxation": dict(sorted(extension_starts.items())),
        "frozen_archive_mismatch_count": len(mismatches),
    }
    if pilot is None:
        frozen = aggregate["frozen"]
        tally = {
            "starts": len(rows),
            "one presentation": frozen["one_presentation"],
            "partition not fixed": frozen["multiple_family_partitions"],
            "tree not fixed": frozen["multiple_tree_readings"],
            "capped": 0,
            "own presentation missing": 0,
        }
        aggregate["archived_frozen_tally"] = archived_tally
        aggregate["archived_frozen_tally_matches"] = tally == archived_tally
        aggregate["parity_prefix_of_1194_with_one_frozen_presentation"] = sum(
            r["frozen_presentations"] == 1 for r in rows[:1194]
        )
    return aggregate, mismatches, witnesses, rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", type=int, help="evenly spaced starts in the archive's order")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.pilot is not None and not 1 <= args.pilot <= 7075:
        parser.error("--pilot must be between 1 and 7075")
    aggregate, mismatches, witnesses, rows = run(args.pilot)
    print(json.dumps(aggregate, indent=2))
    if args.output is not None:
        fields = list(rows[0])
        result = {
            "input": "FORBID-EDITS-20261126-001/starts.json, archive order",
            "comparison": "ONE-STATEMENT-20261127-001/frozen_parity.jsonl",
            "weighting": "One per archived census start up to renaming. Each presentation is a set of named supports.",
            "frozen_scope": "Same even-parity allowed states, distinctions and loose marks. One holder per marked distinction and two per other distinction. Connected, source number of supports, all of size three or more.",
            "broader_scope": "Same states, distinctions and multiplicities. Distinct supports of at least two places, any number, connected or disconnected. No new distinctions.",
            "tree_reading": "Start families join loose holders with a common neighbor. Thresholds use least shared-distinction route lengths between families. The value 1000000000 represents no route.",
            "summary": aggregate,
            "frozen_archive_mismatches": mismatches,
            "witnesses": witnesses,
            "per_start_columns": fields,
        }
        head = json.dumps(result, indent=2)
        lines = [json.dumps([row[key] for key in fields], separators=(",", ":")) for row in rows]
        args.output.write_text(head[:-2] + ',\n  "per_start": [\n    '
                               + ",\n    ".join(lines) + "\n  ]\n}\n")


if __name__ == "__main__":
    main()
