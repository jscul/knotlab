"""Transfer the unchanged reader to the second learner's frozen Boolean instructions."""

from argparse import ArgumentParser
from itertools import permutations
import json
from pathlib import Path

import assessment
import unguided


BASE = assessment.ROOT / "artifacts" / assessment.TICKET
PRIMARY = BASE / assessment.FAMILY / "checkpoint.json"
SEQUENCES = BASE / (assessment.TICKET + "-E002_rewarded_actions")
BUNDLE = SEQUENCES / "sequence_checkpoint.json"


def extract():
    learned = json.loads((SEQUENCES / "results.jsonl").read_text())["result"]["fit"]["stages"]
    main = json.loads(PRIMARY.read_text())
    return {"schema_version": 1, "encoding": "guarded-bit-flips-00-01-10",
            "forward": learned["guided_forward"]["actions"], "undo": learned["guided_undo"]["actions"],
            "reader": main["reader"]}


def run(bundle):
    points = assessment.reader.POINTS
    images = tuple(tuple(unguided.elementary_execution(bundle[key], p) for p in points)
                   for key in ("forward", "undo"))
    score = assessment.results_by_menu(bundle, executed_moves=images)
    original = json.loads(PRIMARY.read_text())
    original_images = assessment.reader.frame_values(original["moves"])
    equivalent = []
    for relabel in permutations(range(3)):
        all_agree = True
        for a, b in zip(original_images, images):
            for (x, y), (u, v) in zip(points, a):
                if b[3 * relabel[x] + relabel[y]] != (relabel[u], relabel[v]):
                    all_agree = False
        if all_agree:
            equivalent.append(relabel)
    return {"checkpoint_sha256": assessment.actions.canonical_sha256(bundle),
            "identical_reader_parameters": original["reader"] == bundle["reader"],
            "simultaneous_relabelings_matching_both_actions": equivalent, "wiring": score}


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--freeze", action="store_true")
    args = parser.parse_args()
    if args.freeze:
        data = json.dumps(extract(), sort_keys=True, separators=(",", ":")).encode()
        if BUNDLE.exists():
            if data != BUNDLE.read_bytes():
                raise ValueError("the frozen bundle differs")
        else:
            with BUNDLE.open("xb") as out:
                out.write(data)
        print(assessment.actions.canonical_sha256(json.loads(data)))
    else:
        print(json.dumps(run(json.loads(BUNDLE.read_text())), separators=(",", ":")))
