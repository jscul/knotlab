"""Stress-test the tower result on all previously recorded held-out draws."""

import argparse
from collections import Counter
import json
from pathlib import Path

from growth import heldout
from tower_recount import DISTINCTION_LIMIT, LAYERS, READINGS, ROUND_LIMIT, STUDY, counts_for_round, json_lines, replay


PILOT_DRAWS = {(6, 2), (6, 105), (6, 228), (7, 37), (7, 236), (7, 239), (8, 191)}


def summarize(records):
    result = {}
    for number in range(1, ROUND_LIMIT + 1):
        row = counts_for_round(records, number)
        row.pop("two independent individually unreadable labels")
        row["opportunities for two whole-held labels"] = {
            key: tally["count"] for key, tally in row["opportunities for two whole-held labels"].items()
        }
        result[number] = row
    return result


def run(pilot):
    source = heldout()
    old_first = {row["index"]: row for row in json_lines(LAYERS / "frozen_heldout.jsonl")}
    original_subset = {row["start"]: row["rounds"] for row in json_lines(STUDY / "tower_multi.jsonl")
                       if row["start"].startswith("held out ")}
    records = {}
    source_sizes = Counter()
    disagreements = []
    comparisons = Counter()
    multiple = []
    capped = []
    for (knots, index), stage in source.items():
        if pilot and (knots, index) not in PILOT_DRAWS:
            continue
        name = f"{knots}-{index}"
        source_sizes[knots] += 1
        rounds, details = replay(stage, report_individual=False)
        records[name] = rounds, details
        first = old_first[name]
        comparisons["first round in predecessor archive"] += 1
        if first["grows"]:
            match = rounds[0].get("SHORT", {}).get("classes") == first["classes"]
        else:
            match = rounds[0].get("end") == first["end"]
        if not match:
            disagreements.append({"draw": name, "rebuilt": rounds[0], "predecessor archive": first})
        original = original_subset.get(f"held out {name}")
        if original is not None:
            comparisons["all recorded rounds in original tower subset"] += 1
            if original != rounds:
                disagreements.append({"draw": name, "rebuilt": rounds, "tower archive": original})
        for row in rounds:
            if row.get("end", "").startswith("not read"):
                capped.append({"draw": name, **row})
        for row, detail in zip(rounds, details):
            if any(row[key]["whole-held"] >= 2 for key in READINGS):
                multiple.append({"draw": name, "knots": detail["knots"], "distinctions": detail["distinctions"], **row})
    sizes = {knots: summarize({name: record for name, record in records.items() if name.startswith(f"{knots}-")})
             for knots in source_sizes}
    return {
        "scope": "Stress test outside T1 selection, ordinary parity with loose distinctions free. Draws are labelled by knot count and zero-based accepted index.",
        "weighting": "Equal per accepted labelled draw within size, with replacement. Seed 20261206 plus the knot count.",
        "pilot": pilot,
        "round limit": ROUND_LIMIT,
        "distinction limit": DISTINCTION_LIMIT,
        "draws by knot count": dict(source_sizes),
        "archive comparisons": dict(comparisons),
        "archive differences": disagreements,
        "all draws by round": summarize(records),
        "by source knot count and round": sizes,
        "rounds with at least two whole-held quotient bits in either reading": multiple,
        "first round above distinction cap": capped,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run(args.pilot)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print({"draws": sum(result["draws by knot count"].values()),
           "archive differences": len(result["archive differences"]),
           "stages with two whole-held quotient bits": len(result["rounds with at least two whole-held quotient bits in either reading"])})
    return bool(result["archive differences"])


if __name__ == "__main__":
    raise SystemExit(main())
