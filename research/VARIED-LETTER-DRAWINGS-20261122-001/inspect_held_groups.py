"""Run the sealed diagnostic on its registered population of 180° and 270° queries."""

from hashlib import sha256
import json

from inspect_groups import ARCHIVE, PANEL, PRIOR, analyze, maximal_groups, rows, training_from_receipts


def held_analysis():
    release = json.loads((ARCHIVE / "scored/release.json").read_bytes())
    for path, checksum in ((ARCHIVE / "scored/scores.json", release["files"]["scores.json"]),
                           (PANEL / "scorer_key.jsonl", release["parents"]["scorer_key"])):
        if sha256(path.read_bytes()).hexdigest() != checksum:
            raise ValueError(f"File differs from the score release: {path}")

    receipts = rows(ARCHIVE / "fit/receipts.jsonl")
    training = {arm: training_from_receipts(rows(PANEL / f"train_{arm}.jsonl"), receipts, arm)
                for arm in ("narrow", "varied")}
    labels = {row["id"]: int(row["label"] == "T") for row in rows(PRIOR / "training_key.jsonl")}
    reference = maximal_groups([{**row, "slot": slot, "action": labels[row["id"]]}
                                for slot, row in enumerate(rows(PRIOR / "train.jsonl"))])
    key = {row["id"]: row for row in rows(PANEL / "scorer_key.jsonl") if row["q"] in (2, 3)}
    held = [{**row, "q": key[row["id"]]["q"], "label": key[row["id"]]["label"]}
            for row in rows(PANEL / "queries.jsonl") if row["id"] in key]
    if len(held) != 512 or {r["id"] for r in held} != set(key):
        raise ValueError("Missing or duplicate held-orientation decisions")
    fitted = json.loads((ARCHIVE / "fit/diagnostics.json").read_bytes())
    analysis = analyze(training, held, fitted, prior_maximal_masks=reference)
    if len(reference) != 240 or not analysis["prior_reference"]["matches_narrow"]:
        raise ValueError("Narrow reference differs from predecessor")
    if not all(all(checks.values()) for checks in analysis["checkpoint_checks"].values()):
        raise ValueError("Group census differs from the fitted checkpoints")
    return analysis


if __name__ == "__main__":
    print(json.dumps(held_analysis(), sort_keys=True, indent=2))
