"""Reproduce the registered group and ambiguity analysis after the blind score release."""

from hashlib import sha256
import json
from pathlib import Path
import sys

RECORD = Path(__file__).resolve().parent
ROOT = RECORD.parents[1]
FAMILY = RECORD.name + "-E001_drawings"
EXPERIMENT = ROOT / "experiments" / RECORD.name / FAMILY
ARCHIVE = ROOT / "artifacts" / RECORD.name / FAMILY
PANEL = EXPERIMENT / "panel"
PRIOR = ROOT / "experiments/LEARNED-PATCH-GROUPS-20261122-001/LEARNED-PATCH-GROUPS-20261122-001-E001_groups" / "panel"
sys.path.insert(0, str(EXPERIMENT))
from diagnostics import analyze, maximal_groups, training_from_receipts


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def run():
    scored = json.loads((ARCHIVE / "scored/release.json").read_bytes())
    score_bytes = (ARCHIVE / "scored/scores.json").read_bytes()
    assert sha256(score_bytes).hexdigest() == scored["files"]["scores.json"]
    receipts = rows(ARCHIVE / "fit/receipts.jsonl")
    training = {arm: training_from_receipts(rows(PANEL / f"train_{arm}.jsonl"), receipts, arm)
                for arm in ("narrow", "varied")}
    prior_targets = {r["id"]: int(r["label"] == "T") for r in rows(PRIOR / "training_key.jsonl")}
    reference = maximal_groups([{**r, "slot": i, "action": prior_targets[r["id"]]}
                                for i,r in enumerate(rows(PRIOR / "train.jsonl"))])
    key = {r["id"]: r for r in rows(PANEL / "scorer_key.jsonl")}
    assert sha256((PANEL / "scorer_key.jsonl").read_bytes()).hexdigest() == scored["parents"]["scorer_key"]
    held = [{**r, "q": key[r["id"]]["q"], "label": key[r["id"]]["label"]}
            for r in rows(PANEL / "queries.jsonl")]
    fitted = json.loads((ARCHIVE / "fit/diagnostics.json").read_bytes())
    result = analyze(training, held, fitted, prior_maximal_masks=reference)
    if not all(all(checks.values()) for checks in result["checkpoint_checks"].values()):
        raise ValueError("Independent group census disagrees with fitted snapshots")
    assert result["prior_reference"]["matches_narrow"] and len(reference) == 240
    return result


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
