"""Shared-runner adapter around EVERY-RAY's unchanged per-family entry point."""
from __future__ import annotations

import json
from pathlib import Path
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import inputs

_sample = _archive = _paths = None


def setup(params):
    global _sample, _archive, _paths
    if params:
        raise ValueError("path DP uses the unchanged entry point's defaults")
    inputs.verify_sources()
    _sample = json.loads((HERE / "sample.json").read_text())
    if not _sample.get("path_ready"):
        raise ValueError("freeze sample.json before running paths")
    _paths = inputs.load_paths()
    _archive = inputs.load_archive(row["key"] for row in _sample["path"])


def cases():
    for row in _sample["path"]:
        yield row["key"], dict(key=row["key"])


def run(case_id, payload):
    if payload != dict(key=case_id) or case_id not in _archive:
        raise ValueError("case outside frozen path sample")
    # Same call as run_paths._worker; no force_dp or classifier changes.
    return _paths.compute_family(case_id, census_row=_archive[case_id])
