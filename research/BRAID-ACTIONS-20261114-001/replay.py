"""Independently check every transmitted packet and repeat both fixed fits."""

from hashlib import sha256
import json
from pathlib import Path
import runpy
import sys

import independent


ROOT = Path(__file__).resolve().parents[2]
TICKET = "BRAID-ACTIONS-20261114-001"
ARTIFACTS = ROOT / "artifacts" / TICKET


def raw(folder):
    record = json.loads((folder / "results.jsonl").read_text())
    if record["status"] != "ok":
        raise ValueError(record["error"])
    return record["result"]


def check():
    e1 = TICKET + "-E001_atomic_policy"
    e2 = TICKET + "-E002_rewarded_actions"
    directory = ROOT / "experiments" / TICKET
    sys.path.insert(0, str(directory / e1))
    source = raw(ARTIFACTS / e1)
    refit = runpy.run_path(str(directory / e1 / "job.py"))["run"]("fit-one-policy", {})
    # JSON normalizes tuples in a fresh fit to the arrays on disk.
    refit = json.loads(json.dumps(refit))
    assert source["checkpoint"] == refit["checkpoint"]
    assert source["checkpoint_sha256"] == refit["checkpoint_sha256"]
    assert source["reader_training"] == refit["reader_training"]
    assert source["move_training"]["training"] == refit["move_training"]["training"]
    replay2 = runpy.run_path(str(directory / e2 / "job.py"))["run"]("guided-and-neutral-27183", {})
    assert json.loads(json.dumps(replay2)) == raw(ARTIFACTS / e2)
    frozen = independent.compile_checkpoint(source["checkpoint"])
    scores = json.loads((ARTIFACTS / e1 / "assessment.json").read_text())["wiring"]
    for row in scores["rows"]:
        tally = sha256()
        for state in range(512):
            literal = independent.packet(frozen, state, row["wiring"])
            tally.update(bytes(literal))
        if tally.hexdigest() != row["packet_stream_sha256"]:
            raise AssertionError(f"Different emitted bits on {row['tags']}")
    return {"primary_checkpoint_identical": True, "primary_training_identical": True,
            "guided_and_neutral_training_and_assessment_identical": True,
            "independent_literal_packet_streams_matching": scores["menus"],
            "independent_physical_packets_matching": scores["menus"] * 512,
            "primary_checkpoint_sha256": source["checkpoint_sha256"]}


if __name__ == "__main__":
    print(json.dumps(check(), indent=2))
