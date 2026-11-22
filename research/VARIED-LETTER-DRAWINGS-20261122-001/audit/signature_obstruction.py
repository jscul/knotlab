#!/usr/bin/env python3
"""Find exact label collisions in the released sensor signatures without fitting."""

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

from reference import counts, read_jsonl, require


def sensor_census(panel):
    queries = read_jsonl(panel / "queries.jsonl")
    scoring = {row["id"]: row for row in read_jsonl(panel / "scorer_key.jsonl")}
    training = {}
    for arm in ("narrow", "varied"):
        observed = read_jsonl(panel / f"train_{arm}.jsonl")
        labels = {row["id"]: row["label"] for row in read_jsonl(panel / f"training_key_{arm}.jsonl")}
        seen = defaultdict(set)
        for row in observed:
            seen[counts(row["pixels"])].add(labels[row["id"]])
        training[arm] = seen

    released = {"held": defaultdict(list), "all": defaultdict(list)}
    overlaps = defaultdict(Counter)
    for row in queries:
        key = scoring[row["id"]]
        signal = counts(row["pixels"])
        fields = ("id", "style", "label", "q", "row", "col")
        received = ({name: key[name] for name in fields}, row["pixels"])
        released["all"][signal].append(received)
        if key["q"] in (2, 3):
            released["held"][signal].append(received)

        for arm, examples in training.items():
            labels = examples.get(signal)
            event = "new" if not labels else "same_label" if labels == {key["label"]} else "different_or_mixed_label"
            overlaps[f"{arm}/{key['condition']}"][event] += 1

    results = {}
    for bank, signatures in released.items():
        upper = 0
        units = set()
        conflicting = []
        for signal, observations in signatures.items():
            votes = Counter(row["label"] for row, _ in observations)
            upper += max(votes.values())
            cases = defaultdict(list)
            for key, pixels in observations:
                label_drawing = key["style"], key["label"], key["q"]
                cases[label_drawing].append((key, pixels))
            units.update(cases)
            if len(votes) > 1:
                images = []
                for key, choices in sorted(cases.items()):
                    witness, pixels = min(choices, key=lambda choice: choice[0]["id"])
                    images.append({"count": len(choices), **witness,
                                   "bitmap_rows": [pixels[i:i+8] for i in range(0, 64, 8)]})
                conflicting.append({"histogram": signal, "labels": votes, "drawings": images})
        require(sum(len(rows) for rows in signatures.values()) == len(units) * 16, "Expected equal translation multiplicity")
        results[bank] = {
            "distinct_signatures": len(signatures), "units": len(units),
            "bitmap_count": len(units) * 16, "deterministic_correct_upper_bound": upper,
            "drawing_turn_correct_upper_bound": upper // 16, "exact_opposite_label_collisions": conflicting,
        }

    return {"classification_executed": False,
            "method": "Count-equivalence classes and their largest true-label multiplicities, using released data only.",
            "counts": results, "novelty_by_fit_and_condition": overlaps}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("panel", type=Path)
    args = parser.parse_args()
    print(json.dumps(sensor_census(args.panel), indent=2, sort_keys=True))
