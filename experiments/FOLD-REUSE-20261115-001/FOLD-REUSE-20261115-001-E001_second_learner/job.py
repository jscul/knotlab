"""Fit and certify a complete stream in a fresh worker for each method and repeat."""

import hashlib
import json
import os
import sys
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
STUDY = "FOLD-REUSE-20261115-001"
ROOT = HERE.parents[2]
DEFAULT_OUT = ROOT / "artifacts" / STUDY / HERE.name
sys.path.insert(0, str(HERE))
METHODS = ("first_plain", "first_fold", "median_plain", "median_fold")
REPEATS = 3


def content_sha(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def setup(params):
    global DATA_DIR, PANEL
    if set(params) - {"data_dir"}:
        raise ValueError("Unexpected shared-runner parameter")
    DATA_DIR = Path(params.get("data_dir", DEFAULT_OUT)).resolve()
    freeze = json.loads((DATA_DIR / "freeze.json").read_bytes())
    for name, expected in freeze["sources"].items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Changed frozen source {name}")
    for name, expected in freeze["inputs"].items():
        if hashlib.sha256((DATA_DIR / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Changed bound input {name}")
    PANEL = json.loads((DATA_DIR / "panel.json").read_bytes())


def cases():
    for repeat in range(REPEATS):
        for method in METHODS[repeat:] + METHODS[:repeat]:
            yield f"{repeat}-{method}", {"method": method, "repeat": repeat}


def run(case_id, payload):
    method = payload["method"]
    if method not in METHODS or case_id != f"{payload['repeat']}-{method}":
        raise ValueError("Unexpected method or repeat")
    started = time.perf_counter_ns()
    cpu_start = time.process_time_ns()
    import learner
    from protocol import RuleChecker, build_median_index, fit_median

    # The checker and the experimental harness own hidden information. Learner
    # functions get the catalogue, visible examples and a single checker callback.
    dag = json.loads((DATA_DIR / "fold.json").read_bytes()) if method.endswith("_fold") else None
    uses_median = method.startswith("median_")
    catalogues = {}
    indices = {}
    for n in (4, 5):
        catalogues[n] = learner.build_catalog(n, dag)
        if uses_median:
            rows = next(tuple(row["initial"]) for row in PANEL if row["n"] == n)
            indices[n] = build_median_index(catalogues[n], rows)
    setup_finished = time.perf_counter_ns()

    runs = []
    for task in PANEL:
        task_start = time.perf_counter_ns()
        n = task["n"]
        checker = RuleChecker(n, task["truth"], learner.expand, dag)
        examples = checker.examples(task["initial"])
        if uses_median:
            fit = fit_median(catalogues[n], indices[n], examples, checker.__call__)
        else:
            fit = learner.fit_rule(catalogues[n], examples, checker.__call__)
        # The charged operation ends with an executable, serialized result.
        program = json.dumps(fit["final_expr"], separators=(",", ":")).encode()
        task_ns = time.perf_counter_ns() - task_start
        runs.append({
            "id": task["id"], "n": n, "examples": examples, "fit": fit, "attempts": checker.attempts,
            "output_bytes": len(program), "wall_ns": task_ns,
        })
    elapsed_ns = time.perf_counter_ns() - started
    cpu_ns = time.process_time_ns() - cpu_start
    # Scientific receipts and hashing below are outside deployed cost for all methods.
    catalogue_records = {}
    for n, catalog in catalogues.items():
        signatures = [candidate["truth"] for candidate in catalog["candidates"]]
        catalogue_records[str(n)] = {
            "distinct": len(signatures), "initial_index_rows": list(indices[n]["rows"]) if uses_median else [],
            "median_indexed_functions": indices[n]["indexed_functions"] if uses_median else 0,
            "unordered_digest": content_sha(sorted(signatures)), "ordered_digest": content_sha(signatures),
            "construction": catalog["construction"],
        }
    if any(row["fit"]["status"] != "exact" or row["attempts"][-1]["counterexample"] is not None for row in runs):
        raise ValueError("A fitted program was returned without a passing certificate")
    return {"method": method, "repeat": payload["repeat"], "pid": os.getpid(), "rows": runs, "catalogues": catalogue_records,
            "setup_wall_ns": setup_finished - started, "downstream_wall_ns": elapsed_ns,
            "downstream_cpu_ns": cpu_ns}
