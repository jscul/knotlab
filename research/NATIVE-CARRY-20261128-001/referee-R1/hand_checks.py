"""Check sign by cancelling a word, and audit the interpretation of the published rows."""

import gzip
import json
import subprocess
from collections import Counter, defaultdict
from itertools import combinations, permutations
from pathlib import Path

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parents[1]
FREEZE = "76187954b"
CLOSE = "9a462d2563"
FOUR = "four mutually meeting knots"
TWO_THREE = "K_{2,3}"


def check_orders(holders, exhaustive=True, *, whole_only=False, knots=None):
    if knots is None:
        knots = sorted({k for pair in holders for k in pair})
    cells = [(i, j) for i, j in combinations(range(len(holders)), 2)
             if set(holders[i]).isdisjoint(holders[j])]
    blocks = {k: [i for i, p in enumerate(holders) if k in p] for k in knots}
    orders = list(permutations(knots)) if exhaustive else [tuple(knots)]
    masks = range(1 << len(cells)) if exhaustive and not whole_only else [(1 << len(cells)) - 1]
    # On each cancellation, move the mate left and remove the resulting equal pair.
    # An interchange with a failing pair changes the sign once.
    def cancellation(order, fails):
        word = [x for k in order for x in blocks[k]]
        count = 0
        while word:
            x = word.pop(0)
            mate = word.index(x)
            for y in word[:mate]:
                count += tuple(sorted((x, y))) in fails
            word.pop(mate)
        return count % 2

    def interleavings(order, fails):
        pos = {k: i for i, k in enumerate(order)}
        total = 0
        for x, y in fails:
            a, b = sorted(pos[k] for k in holders[x])
            c, d = (pos[k] for k in holders[y])
            total += (a < c < b) != (a < d < b)
        return total

    orders_tested = exchanges = discrepancies = stable = 0
    base_counts = []
    for mask in masks:
        fails = {cell for j, cell in enumerate(cells) if mask >> j & 1}
        parities = set()
        for order in orders:
            count = interleavings(order, fails)
            parities.add(count % 2)
            if mask == (1 << len(cells)) - 1:
                base_counts.append(count)
            discrepancies += (count % 2 != cancellation(order, fails))
            orders_tested += 1
            for i in range(len(order) - 1):
                u, v = order[i:i + 2]
                at_pair = sum((u in holders[x] and v in holders[y]) or
                              (v in holders[x] and u in holders[y]) for x, y in fails)
                swapped = order[:i] + (v, u) + order[i + 2:]
                discrepancies += (count + interleavings(swapped, fails) - at_pair) % 2
                exchanges += 1
        stable += len(parities) == 1
    # Every failing pair forces its two distinctions into the same reader.
    groups = [{i} for i in {x for cell in cells for x in cell}]
    for x, y in cells:
        joined = set.union(*(g for g in groups if x in g or y in g))
        groups = [g for g in groups if not (joined & g)] + [joined]
    split = all(len(set(blocks[k]) & g) <= 1 for g in groups for k in knots)
    return {"cells": len(cells), "choices": len(masks), "orders_per_choice": len(orders),
            "product_tests": orders_tested, "exchanges": exchanges,
            "mismatches": discrepancies, "choices_constant_over_checked_orders": stable,
            "whole_interleavings_first_order": base_counts[0],
            "whole_interleavings_range_checked": [min(base_counts), max(base_counts)],
            "whole_reader_group_sizes": sorted(map(len, groups)), "whole_failing_groups_meet_each_knot_at_most_once": split}


def record_audit():
    book = {"census": {}, "by_population": {}, "freeze": {}}
    by_pop = defaultdict(Counter)
    by_kind = defaultdict(Counter)
    readers = {r["start"]: r for line in
               (STUDY.parent / "READER-SPLIT-20261127-001/results.jsonl").open()
               if (r := json.loads(line))}
    cross = Counter()
    prior_types = {r["type"]: r for line in
                   (STUDY.parent / "NO-WHOLE-STATE-20261126-001/rule_census.jsonl").open()
                   if (r := json.loads(line))}
    type_counts = defaultdict(Counter)
    with gzip.open(STUDY / "rows.jsonl.gz", "rt") as rows:
        for line in rows:
            r = json.loads(line)
            pop = r["population"]
            mins = r["minimal carriers"]
            kinds = {c["kind"] for c in mins if c["sign"]}
            tag = " and ".join(sorted(kinds)) or "none"
            by_kind[pop][tag] += 1
            by_pop[pop]["rows"] += 1
            by_pop[pop]["has_even_minimal"] += any(not c["sign"] for c in mins)
            by_pop[pop]["qualifying_nonminimal_entire_row"] += r["whole closure a carrier"] and not any(
                c["knots"] == r["knots"] for c in mins)
            if pop == "census types":
                prior = prior_types[r["type"]]
                assert prior["R1 knots commute under R"] == r["whole closure a carrier"]
                assert prior["R2 sum forced under R"] == {1: "odd", 0: "even", None: None}[r["whole closure sign"]]
                type_counts[r["knots"]]["types"] += 1
                type_counts[r["knots"]]["has_odd_minimal"] += bool(kinds)
            if pop == "census starts" and r["birth choices attain odd"]:
                rec = readers[r["start index"]]
                cross[tag, rec["general"]] += 1
    book["by_population"] = {p: {**c, "odd_minimal_kinds_per_row": by_kind[p]} for p, c in by_pop.items()}
    book["census"]["any_separated_reader_choice_against_reported_minimal_kinds"] = [
        {"odd_minimal": k, "some_birth_choice_splits": s, "closures": n}
        for (k, s), n in sorted(cross.items())]
    book["prior_whole_rule_type_rows_matched_by_size"] = dict(sorted(type_counts.items()))
    for path in ["README.md", "nativecarry.py"]:
        source = str(STUDY.relative_to(ROOT) / path)
        before, after = [subprocess.check_output(["git", "show", f"{rev}:{source}"], cwd=ROOT)
                         for rev in (FREEZE, CLOSE)]
        book["freeze"][path] = {
            "identical": before == after, "frozen_bytes_are_prefix": after.startswith(before),
            "appended_lines": len(after.splitlines()) - len(before.splitlines()),
            "first_nonblank_appended_line": next((line.decode() for line in after[len(before):].splitlines()
                                                  if line.strip()), None)}
    return book


def main():
    petersen = ([(i, (i + 1) % 5) for i in range(5)] +
                [(i, 5 + i) for i in range(5)] +
                [(5 + i, 5 + (i + 2) % 5) for i in range(5)])
    k4 = list(combinations(range(4), 2))
    fixtures = {
        FOUR: (k4, True), TWO_THREE: ([(a, b) for a in (0, 1) for b in (2, 3, 4)], True),
        "ring of four": ([(0, 1), (1, 2), (2, 3), (3, 0)], True),
        "ring of three with a separate meeting": ([(0, 1), (1, 2), (2, 0), (3, 4)], True),
        "doubled and separate": ([(0, 1), (0, 1), (2, 3)], True),
        "four mutually meeting, tripling one meeting": (k4 + [(0, 1), (0, 1)], True),
        "Petersen": (petersen, False)}
    data = {"fixtures": {k: check_orders(*v) for k, v in fixtures.items()}, "records": record_audit()}
    data["fixtures"]["same multiplicities modulo two, with no cell"] = check_orders([(2, 3)], knots=range(4))
    # Five-knot round-one closure. Check every order of the complete choice on
    # each subset, including subsets pruned from the original classification.
    supports = [[0, 1, 2, 7], [0, 3, 4, 5, 6, 8], [1, 3, 4, 9], [2, 5, 6, 10], [7, 8, 9, 10]]
    holders = [tuple(k for k, s in enumerate(supports) if x in s) for x in range(11)]
    witness = {}
    for size in (4, 5):
        for subset in combinations(range(5), size):
            inside = [p for p in holders if set(p).issubset(subset)]
            result = check_orders(inside, whole_only=True, knots=subset)
            assert result["mismatches"] == 0
            witness[",".join(map(str, subset))] = result
    data["five-knot census closure, start index 643"] = {"supports": supports, "sets_checked": witness}
    assert not any(row["mismatches"] for row in data["fixtures"].values())
    (HERE / "hand_counts.json").write_text(json.dumps(data, indent=2) + "\n")


if __name__ == "__main__":
    main()
