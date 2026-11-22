"""Witness that fitted state or blind decisions exist before their successor."""

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path

RECORD = Path(__file__).resolve().parent
ARCHIVE = RECORD.parents[1] / "artifacts" / RECORD.name / (RECORD.name + "-E001_relative")


def witness(out, anchors, stage):
    next_stage = {"fit": "pair", "blind": "scored"}[stage]
    if (out / next_stage).exists():
        raise ValueError(f"{next_stage} already exists")
    prior = [json.loads(line) for line in anchors.read_bytes().splitlines()] if anchors.exists() else []
    if [row["stage"] for row in prior] != (["fit"] if stage == "blind" else []):
        raise ValueError("Missing or duplicate external commitment")
    release = (out / stage / "release.json").read_bytes()
    row = {"stage": stage, "sha256": sha256(release).hexdigest(), "next_stage_absent": next_stage,
           "utc": datetime.now(timezone.utc).isoformat()}
    with anchors.open("x" if stage == "fit" else "a") as stream:
        stream.write(json.dumps(row, sort_keys=True) + "\n")
    return row


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("stage", choices=("fit", "blind"))
    cli.add_argument("--out", type=Path, default=ARCHIVE)
    cli.add_argument("--anchors", type=Path, default=RECORD / "phase_anchors.jsonl")
    args = cli.parse_args()
    print(json.dumps(witness(args.out, args.anchors, args.stage)))
