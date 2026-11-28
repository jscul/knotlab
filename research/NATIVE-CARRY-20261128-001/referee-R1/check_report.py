"""Reconcile the independent population, birth, abstract and hand checks used in the report."""

import gzip
import json
from collections import Counter, defaultdict
from math import comb
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    return json.loads((HERE / name).read_text())


def main():
    with gzip.open(HERE / "population_rows.jsonl.gz", "rt") as file:
        rows = [json.loads(line) for line in file]
    replay = read("population_counts.json")
    assert replay["published population comparison"]["differences"] == []
    assert replay["published birth comparison"]["differences"] == []
    birth = read("birth.json")
    hand = read("hand_counts.json")
    abstract = read("abstract_counts.json")
    assert abstract["archive comparison"]["archived minimal patterns matched individually"] == 36
    eligible_minima = defaultdict(Counter)
    large = Counter()
    sizes = Counter()
    weighted = defaultdict(Counter)
    by_round = defaultdict(Counter)
    census_partition = Counter()
    for row in rows:
        pop = row["population"]
        n = row["knots"]
        totals = weighted[pop]
        totals["rows"] += 1
        totals["subsets"] += row["subsets checked"]
        totals["integer_formula_pairs_at_full_patterns"] += comb(n, 2)
        odd = sum(row["whole-choice sets by sign and size"]["odd"].values())
        minima = [s for s in row["minimal sets"] if s["sign"]]
        minimum = bool(minima)
        if n > 12:
            large["rows"] += 1
            sizes[n] += 1
            large["subsets"] += row["subsets checked"]
            large["subsets_above_old_cut"] += sum(comb(n, k) for k in range(9, n + 1))
            large["minimal_sets_above_old_cut"] += sum(s["knots"] > 8 for s in row["minimal sets"])
            for sign, size_counts in row["whole-choice sets by sign and size"].items():
                large[sign + "_sets_above_old_cut"] += sum(c for k, c in size_counts.items() if int(k) > 8)
        if "rounds" in row:
            eligible = eligible_minima[pop]
            eligible["odd_minimal_sets"] += len(minima)
            eligible["odd_minimal_sets_eligible"] += sum(s["birth-forbidden cells"] == 0 for s in minima)
            eligible["rows_with_any_eligible_odd_set"] += odd > row["odd whole-choice sets including a birth-forbidden cell"]
        if pop == "census starts":
            round_count = by_round[str(row["rounds"])]
            round_count["closures"] += 1
            round_count["odd minimal whole-choice sets"] += len(minima)
            round_count["closures with an odd whole-choice set of any size"] += bool(odd)
            round_count["closures with an odd minimal whole-choice set"] += minimum
            round_count["odd whole-choice sets of any size"] += odd
            round_count["an arbitrary birth choice can close odd"] += row["birth choices attain odd"]
            if row["birth choices attain odd"] and not minimum:
                if row["whole closure sign"] == 1:
                    census_partition["entire closure odd"] += 1
                elif odd:
                    census_partition["proper odd subset only"] += 1
                else:
                    census_partition["no odd whole-choice subset"] += 1
    for rnd, counts in by_round.items():
        for key, count in counts.items():
            assert birth["counts by closing round"][rnd][key] == count, (rnd, key)
    proof = hand["five-knot census closure, start index 643"]["sets_checked"]
    assert {k: row["whole_interleavings_first_order"] % 2 for k, row in proof.items()
            if row["choices_constant_over_checked_orders"]} == {"0,1,2,3,4": 1, "0,1,2,3": 0, "1,2,3,4": 0}
    assert census_partition == {"entire closure odd": 14, "proper odd subset only": 25, "no odd whole-choice subset": 986}
    result = {
        "weighting": "One vote per start reaching closure or per finished type for rows. One per actual knot subset in each row for sets.",
        "row_checks": weighted, "two independent census replays agree by round": by_round,
        "among 1025 birth-odd closures with no odd minimal set": census_partition,
        "all subsets at the formerly cut closures": {**large, "sizes of closures": sizes},
        "birth eligibility on grown population rows": eligible_minima}
    (HERE / "reconciliation.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
