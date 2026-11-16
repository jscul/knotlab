"""Export the previously returned circuit and account for the work that produced it."""

import argparse
import hashlib
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STUDY = "FOLD-REUSE-20261115-001"
SOURCE = "ANSWER-COMPOSE-20261115-001"
PARSER = "BIT-DECODER-20261114-001"
SOURCE_FAMILY = SOURCE + "-E001_packet_nand"
PARSER_FAMILY = PARSER + "-E001_atomic_codec"
SOURCE_OUT = ROOT / "artifacts" / SOURCE / SOURCE_FAMILY
PARSER_OUT = ROOT / "artifacts" / PARSER / PARSER_FAMILY
WIRING_ID = "d406ab6ea3ee6c83"
DEFAULT_OUT = ROOT / "artifacts" / STUDY / (STUDY + "-E001_second_learner")

# These are the historical records that actually supply the fold and its training time.
PARENTS = {
    "parser_run": (PARSER_OUT / "results.jsonl", "ea7a47c5f4e119ef6947f217ff7f14457342e3ddec58646ca08ed7ef4b78f094"),
    "parser_checkpoint": (PARSER_OUT / "varied_checkpoint.json", "b328cd2bcd4aa95976fad2513252ad1c23e0e21fa337323b84919a8ea93db0cd"),
    "composition_run": (SOURCE_OUT / "results.jsonl", "3230673e610aad79c0cfdad349b30f96ffcddc270c0a42e14e7fd8273435979b"),
    "checkpoint": (SOURCE_OUT / "checkpoint.json", "e9a8045605315623cc0f3db055478c6ccca68401b28bccf2a11864e0bb604722"),
    "source_freeze": (SOURCE_OUT / "freeze.json", "5a8d688f36d3fbc12d42abd918965dafa124ce2a8ee1b66671aed8053123e31d"),
    "raw_plans": (SOURCE_OUT / "raw_proposals.json", "b230ee2c164426343a5ce7832949a06fbbe8700731c4712211375345eb0e0d19"),
    "checked_plans": (SOURCE_OUT / "plans.json", "32fdfc32b1c8030a6eeacec4cf05d521220418370ba615dea68163879a0784b8"),
}


def file_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def write_new(path, value):
    data = canonical(value)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError(f"Different record already exists at {path}")
        return
    with path.open("xb") as output:
        output.write(data)


def historical_case(path, name):
    rows = [json.loads(line) for line in path.read_bytes().splitlines()]
    found = [row for row in rows if row["case"] == name and row["status"] == "ok"]
    if len(found) != 1:
        raise ValueError(f"Expected a single successful historical {name} fit")
    return found[0]


def export(out):
    out.mkdir(parents=True, exist_ok=True)
    for path, digest in PARENTS.values():
        if file_sha(path) != digest:
            raise ValueError(f"Predecessor changed at {path}")
    for relative, digest in json.loads(PARENTS["source_freeze"][0].read_bytes())["files"].items():
        if file_sha(ROOT / relative) != digest:
            raise ValueError(f"Changed historical source file {relative}")
    old_raw = json.loads(PARENTS["raw_plans"][0].read_bytes())["plans"][WIRING_ID]["raw"]
    old_certified = json.loads(PARENTS["checked_plans"][0].read_bytes())["wirings"][WIRING_ID]
    old_parser = historical_case(PARENTS["parser_run"][0], "varied")
    old_composer = historical_case(PARENTS["composition_run"][0], "packet_nand")

    # A single later consumer needs one source plan and its certificate. The
    # original case timings already include fitting and generating training labels.
    clock = time.perf_counter()
    cpu = time.process_time()
    sys.path[:0] = [str(ROOT / "experiments" / SOURCE / SOURCE_FAMILY), str(ROOT / "research" / SOURCE)]
    import compiler
    import learner
    import panels

    checkpoint = json.loads(PARENTS["checkpoint"][0].read_bytes())
    wiring = next(w for key, w, _ in panels.held_panel() if key == WIRING_ID)
    proposed = learner.plan(checkpoint, wiring)
    accepted, certificate = compiler.certify(wiring, proposed)
    if certificate["status"] != "certified_three":
        raise ValueError("The source circuit failed its original exhaustive certificate")
    if proposed != old_raw or accepted != old_certified["sender"]["certified"]:
        raise ValueError("The reconstructed candidate differs from the saved source")
    dag = proposed["dag"]
    write_new(out / "fold.json", dag)
    export_wall = time.perf_counter() - clock
    export_cpu = time.process_time() - cpu
    parser_case_wall = old_parser["seconds"]
    composition_case_wall = old_composer["seconds"]
    record = {
        "ticket": STUDY, "source_wiring_id": WIRING_ID, "dag_sha256": file_sha(out / "fold.json"),
        "source_files": {name: sha for name, (_, sha) in PARENTS.items()},
        "parser_training_case_wall_s": parser_case_wall, "composition_training_case_wall_s": composition_case_wall,
        "composition_training_fit_cpu_s": old_composer["result"]["fit_cpu_seconds"],
        "export_and_recertification_wall_s": export_wall, "export_and_recertification_cpu_s": export_cpu,
        "original_acquisition_wall_s": parser_case_wall + composition_case_wall + export_wall,
        "serialized_fold_bytes": (out / "fold.json").stat().st_size,
        "source_certificate": certificate,
        "source_work": proposed["public_actions"],
        "source_accounting": "One required training run at each stage and one fresh materialization and certificate of the source plan. Historical scientific evaluation and unrelated control fits are excluded.",
    }
    write_new(out / "source_cost.json", record)
    return record


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--out", type=Path, default=DEFAULT_OUT)
    options = cli.parse_args()
    print(json.dumps(export(options.out), indent=2))
