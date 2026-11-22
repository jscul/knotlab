"""Shared-runner entry for development, paired growth search and reserved validation."""

from time import perf_counter_ns, process_time_ns

import_cpu, import_wall = process_time_ns(), perf_counter_ns()

from hashlib import sha256
from importlib.metadata import version
import json
from pathlib import Path
from platform import python_version

from calibration import calibrate
from search import LAWS, pair
from source import ROOT, warm_laws


HERE = Path(__file__).resolve().parent
ARTIFACTS = ROOT / "artifacts" / HERE.parent.name / HERE.name
EXPERIMENT = HERE.name.rsplit("_", 1)[0]
CALIBRATION = ARTIFACTS / "calibration.json"
REPEATS = 48
CONFIG = None


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def authorize(params, mode):
    contract_path = HERE / "contract.json"
    contract = json.loads(contract_path.read_bytes())
    if contract.get("status") != "Frozen":
        raise ValueError("sealed execution requires a frozen contract")
    for relative, expected in contract["input_sha256"].items():
        if digest(ROOT / relative) != expected:
            raise ValueError(f"frozen input changed: {relative}")
    runtime = contract["runtime_versions"]
    if python_version() != runtime["python"] or any(version(p) != v for p, v in runtime["packages"].items()):
        raise ValueError("frozen Python or package version changed")
    report_arg = params.get("r1")
    review_digest = params.get("r1_sha256")
    if not report_arg or not review_digest:
        raise ValueError("sealed execution requires the coordinating task's independent R1 release")
    report_path = Path(report_arg).resolve(strict=True)
    if digest(report_path) != review_digest:
        raise ValueError("review authorization digest changed")
    report = json.loads(report_path.read_bytes())
    if any(report.get(k) != value for k, value in (
        ("experiment_id", EXPERIMENT), ("tier", "R1"), ("gate", "run_authorization"), ("verdict", "PASS"),
        ("attack_plan_frozen_before_results", True),
    )) or report.get("reviewer_independence") not in {"separate_implementation_lane", "independent_replay"}:
        raise ValueError("authorization must be an independent experimental R1 PASS")
    bound = {((report_path.parent / entry["path"]).resolve(), entry["sha256"])
             for entry in report["input_digests"]}
    if (contract_path, digest(contract_path)) not in bound:
        raise ValueError("R1 approval must bind the exact current contract")
    for path, expected in bound:
        if digest(path) != expected:
            raise ValueError(f"R1 approval bound a different input: {path}")
    if mode == "validation":
        raw_summary = params.get("search_summary")
        if not raw_summary:
            raise ValueError("fresh validation requires the completed search summary")
        summary = Path(raw_summary).resolve(strict=True)
        record = json.loads(summary.read_bytes())
        if (not record.get("complete") or record.get("source_partition") != "search" or
                record.get("contract_sha256") != digest(contract_path) or
                record.get("calibration_sha256") != digest(CALIBRATION)):
            raise ValueError("fresh validation begins only after this frozen search completed and was parsed")
        return {"r1_sha256": review_digest, "search_summary_sha256": digest(summary)}
    return {"r1_sha256": review_digest}


def setup(params):
    global CONFIG
    cpu, wall = process_time_ns(), perf_counter_ns()
    mode = params.get("mode", "development")
    if mode not in {"calibration", "development", "search", "validation"}:
        raise ValueError(f"unknown experiment mode {mode!r}")
    authorization = authorize(params, mode) if mode in {"search", "validation"} else {}
    laws = warm_laws()
    dictionary = {law: set() for law in LAWS}
    excluded = set()
    if mode != "calibration":
        calibration = json.loads(CALIBRATION.read_bytes())
        excluded = set(calibration["excluded_founders"])
        dictionary = {law: set(map(tuple, values))
                      for law, values in calibration["signature_dictionary"].items()}
    CONFIG = {"mode": mode, "laws": laws, "dictionary": dictionary, "excluded": excluded,
              "import_cpu_ns": cpu - import_cpu, "import_wall_ns": wall - import_wall,
              "warmup_cpu_ns": process_time_ns() - cpu, "warmup_wall_ns": perf_counter_ns() - wall,
              "authorization": authorization}


def cases():
    mode = CONFIG["mode"]
    if mode in {"calibration", "validation"}:
        yield mode, {}
        return
    for index in range(REPEATS if mode == "search" else 10):
        for law in LAWS:
            yield f"{law}/{index:02}", {"index": index, "law": law}


def run(case_id, payload):
    mode = CONFIG["mode"]
    if mode == "calibration":
        told = calibrate()
    elif mode == "validation":
        from validation import census
        told = census(CONFIG["excluded"])
    else:
        law, index = payload["law"], payload["index"]
        told = pair(law, index, mode, CONFIG["dictionary"][law], CONFIG["excluded"])
    if case_id in {"calibration", "validation", "parity/00"}:
        told["shared_setup_once"] = {k: v for k, v in CONFIG.items() if k not in {"excluded", "dictionary"}}
    return told
