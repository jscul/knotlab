"""Shared-runner adapter for the complete certificate of each produced history."""

from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "scripts"))

import hashlib
import json

from certify import certify_history, read_history
from longrun import load_results


def setup(params):
    global FROZEN, FROZEN_DIGEST, PRODUCED, SUPPORTS_ROOT
    for filename in ("certify.py", "projection.py"):
        source_digest = hashlib.sha256((HERE / filename).read_bytes()).hexdigest()
        if params[f"{Path(filename).stem}_sha256"] != source_digest:
            raise ValueError(f"certificate source digest mismatch for {filename}")
    path = HERE.parent / "cases.json"
    contract = json.loads((HERE.parent / "contract.json").read_bytes())
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if contract["inputs"][str(path.relative_to(ROOT))] != digest:
        raise ValueError("frozen case digest mismatch")
    FROZEN = json.loads(path.read_bytes())
    FROZEN_DIGEST = digest
    PRODUCED = load_results(Path(params["producer"]))
    SUPPORTS_ROOT = Path(params["producer_artifacts"]).resolve(strict=True)


def cases():
    for config in FROZEN:
        case_id = config["id"]
        record = PRODUCED.get(case_id)
        if record is None or record["status"] != "ok":
            continue
        result = record["result"]
        if result["cases_sha256"] != FROZEN_DIGEST:
            raise ValueError(f"{case_id} was not grown from the frozen cases")
        for field in ("start", "law", "rounds", "r_max", "knot_bound"):
            if result[field] != config[field]:
                raise ValueError(f"{case_id} differs from the frozen configuration at {field}")
        if [entry["kl"] for entry in result["laws"]] != ["nae", "parity"]:
            raise ValueError(f"{case_id} lacks either actual knot-law trajectory")
        for entry in result["laws"]:
            yield f"{case_id}/{entry['kl']}", (config, entry)


def run(case_id, payload):
    config, entry = payload
    law = entry["kl"]
    digest = entry["support_sha256"]
    if entry["support_file"] != f"raw/supports/{digest}.jsonl.gz":
        raise ValueError(f"{case_id}: support file is not bound to its digest")
    history = read_history(SUPPORTS_ROOT / entry["support_file"], digest)
    final_round = len(history.stages) - 1
    if final_round != entry["rounds_done"] or final_round > config["rounds"][-1]:
        raise ValueError(f"{case_id}: terminal round mismatch")
    last = history.stages[-1]
    if (last.knots, last.distinctions) != (entry["knots"], entry["distinctions"]):
        raise ValueError(f"{case_id}: support history and producer disagree on the final totals")
    if any(stage.knots > config["knot_bound"] for stage in history.stages[:-1]):
        raise ValueError(f"{case_id}: history continued after exceeding the post-round knot bound")
    scheduled = [t for t in config["rounds"] if t <= final_round]
    if scheduled != [stage["round"] for stage in entry["stages"]]:
        raise ValueError(f"{case_id}: roster stages and the frozen schedule disagree")
    if any(stage["knots"] != history.stages[stage["round"]].knots for stage in entry["stages"]):
        raise ValueError(f"{case_id}: support totals and producer roster totals disagree")
    return {
        "case": config["id"],
        "kl": law,
        "support_sha256": digest,
        "scheduled": scheduled,
        "stop": entry["stop"],
        **certify_history(history, law),
    }
