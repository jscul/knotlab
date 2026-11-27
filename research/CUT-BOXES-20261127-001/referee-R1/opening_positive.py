"""Audit new boxes with direct projections and source-law deletions."""

from argparse import ArgumentParser
from collections import Counter
from fractions import Fraction
from itertools import product
import json
from math import prod
import os
from pathlib import Path
import subprocess
import sys
from time import perf_counter

from opening_witness import HERE, split_source
from upper_check import TruthTable, as_box


def direct_record(closed, search):
    cuts = search["equivalent_labelled_cuts"][0]
    opened = split_source(closed["closed_supports"], cuts)
    truth = TruthTable(opened)
    all_loose = search["loose_distinctions"]
    shadow_cache = {}
    summaries = []
    for index, candidate in enumerate(search["boxes"]):
        box = as_box(candidate)
        places = {x for pair in box for c, _ in pair for x in c}
        assert len(places) == sum(len(c) for pair in box for c, _ in pair)
        for triple in product(*box):
            index_ordered = tuple(sorted(triple))
            if index_ordered in shadow_cache:
                continue
            readings = [truth.equal(c) for c, _ in index_ordered]
            signs = tuple(sign for _, sign in index_ordered)
            absent = []
            for word in product((0, 1), repeat=3):
                cell = truth.allowed
                for value, sign in zip(readings, word):
                    cell &= value if sign else ~value
                if not cell:
                    absent.append(word)
            assert absent == [signs]
            shadow_cache[index_ordered] = True
        missing, needed = truth.upper(box)
        disjoint_loose = [[u for u, pair in enumerate(box) for c, _ in pair if x in c] for x in all_loose]
        direct_lower_ids = [[i for i, (c, _) in enumerate(v for pair in box for v in pair) if x in c]
                            for x in all_loose]
        assert len(missing) > 0
        summaries.append({"box_index": index, "number_of_carrier_distinctions": len(places),
                          "upper_missing_words": missing, "needed_source_laws": needed,
                          "upper_pairs_reading_each_loose": disjoint_loose,
                          "lower_readings_of_each_loose": direct_lower_ids})
    truth.equal.cache_clear()
    return {"source_position": closed["position"], "cut_representative": cuts,
            "equivalent_labelled_cuts": len(search["equivalent_labelled_cuts"]),
            "distinct_lower_triples_checked_in_full": len(shadow_cache), "boxes": summaries}


def weighted_summary(records, number):
    fields = ["by_number_of_carrier_distinctions", "by_number_of_needed_source_laws",
              "by_upper_missing_words", "by_loose_distinctions_read",
              "by_distinct_lower_readings_of_loose_distinctions", "by_distinct_upper_pairs_of_loose_distinctions"]
    counts = {k: Counter() for k in fields}
    for row in records:
        if len(row["cut_representative"]) != number:
            continue
        weight = row["equivalent_labelled_cuts"]
        for box in row["boxes"]:
            loose_readings = box["lower_readings_of_each_loose"]
            loose_pairs = box["upper_pairs_reading_each_loose"]
            keys = (box["number_of_carrier_distinctions"], len(box["needed_source_laws"]),
                    ",".join(box["upper_missing_words"]), sum(bool(x) for x in loose_readings),
                    len({a for entry in loose_readings for a in entry}),
                    len({a for entry in loose_pairs for a in entry}))
            for name, key in zip(fields, keys):
                counts[name][key] += weight
    return counts


def canonical_seven():
    out = []
    env = dict(os.environ, PYTHONPATH=str(HERE.parents[2] / "tools"))
    for contact in "ABC":
        loops = [c for c in "ABC" if c != contact]
        result = subprocess.run([sys.executable, "-B", "-m", "knotlab", "check", "--cnf", "~A ~B ~C",
                                 "--loops", *loops, "--contact", contact, "--json"],
                                capture_output=True, text=True, check=True, env=env)
        verdict = json.loads(result.stdout)
        assert verdict["is_knot"] and len(verdict["allowed"]) == 7
        out.append({"variables": verdict["variables"], "allowed": verdict["allowed"], "is_knot": verdict["is_knot"]})
    return out


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--census", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    start = perf_counter()
    archive = json.loads((HERE / "archive_counts.json").read_text())
    rows = {r["position"]: r for r in archive["rows"]}
    census = json.loads(args.census.read_text())
    checked = [direct_record(rows[r["source_position"]], r) for r in census["records"] if r["boxes"]]
    summary = {n: weighted_summary(checked, n) for n in (1, 2)}
    no_hits = None
    complete_singles = sum(len(r["equivalent_labelled_cuts"]) for r in census["records"]
                           if len(r["equivalent_labelled_cuts"][0]) == 1)
    h = Counter()
    if complete_singles == 18 * len(rows):
        for r in checked:
            if len(r["cut_representative"]) == 1:
                h[r["source_position"]] += r["equivalent_labelled_cuts"]
        chance = prod(Fraction(18 - h[pos], 18) for pos in rows)
        no_hits = {"numerator": chance.numerator, "denominator": chance.denominator,
                   "decimal": float(chance), "weighting": "independent uniform single cut on each of the 49 sources"}
    out = {"source": args.census.name, "counts_across_labelled_cuts": summary,
           "positive_single_cuts_by_source_position": dict(sorted(h.items())),
           "no_single_hits_chance_under_stated_weighting": no_hits,
           "canonical_check_of_image_missing_only_111_in_each_contact_role": canonical_seven(),
           "records": checked, "elapsed_seconds": round(perf_counter() - start, 4)}
    args.out.write_text(json.dumps(out, separators=(",", ":")) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k not in ("records", "canonical_check_of_image_missing_only_111_in_each_contact_role")}))


if __name__ == "__main__":
    main()
