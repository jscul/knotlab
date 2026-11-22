"""Reissue one saved position-tree decision on its raw bitmap and exchange only memory."""

import argparse
import json
from pathlib import Path
import sys

from custody import ARCHIVE, RECORD

FAMILY = RECORD.parents[1] / "experiments" / RECORD.name / ARCHIVE.name
sys.path.insert(0, str(FAMILY))
import study


def replay(prefix, law):
    if not (ARCHIVE / "scored/release.json").is_file():
        raise ValueError("This explanatory replay requires the released blind score")
    contract, authority = study.preflight()
    study.check_upstream(ARCHIVE, "scored", contract, authority)
    study.check_anchors(ARCHIVE, "scored", RECORD / "phase_anchors.jsonl")
    choices = [(stage, row) for stage, stream in (("pair", "diagnostic"), ("blind", "queries"))
               for row in study.public(contract, stream) if row["id"].startswith(prefix)]
    if len(choices) != 1:
        raise ValueError(f"Expected a unique bitmap prefix, found {len(choices)}")
    stage, row = choices[0]
    predicted = next(item for item in study.io.json_lines((ARCHIVE / stage / "predictions.jsonl").read_bytes())
                     if item["id"] == row["id"])
    name = "position-" + law
    saved = {s: study.io.load(ARCHIVE / "fit" / f"{name}-{s}.json") for s in study.SCHEDULES}
    model = study.implementations(contract)[0].KnotTree.from_memory(saved["ordinary"])
    pixels = study.bits(row)
    reads = {}
    for mode in ("ordinary", "swapped-ordinary", "clear", "restored"):
        if mode == "swapped-ordinary":
            model.restore_memory(saved["opposite"])
        elif mode == "clear":
            model.clear_memory()
        elif mode == "restored":
            model.restore_memory(saved["ordinary"])
        reading = model.explain(pixels)
        if reading["guess"] != predicted["actions"][f"{name}-{mode}"]:
            raise ValueError("Action differs from the sealed decision")
        reads[mode] = {"called": "LT"[reading["guess"]], "path": reading["path"],
                       "physical_state": study.io.memory_digest(model.export_memory())}
    return {"id": row["id"], "stage": stage, "law": law, "raw_rows":
            [row["pixels"][r:r + 8] for r in range(0, 64, 8)], "reads": reads}


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("prefix")
    cli.add_argument("--law", choices=study.LAWS, default="parity")
    args = cli.parse_args()
    print(json.dumps(replay(args.prefix, args.law), indent=2))
