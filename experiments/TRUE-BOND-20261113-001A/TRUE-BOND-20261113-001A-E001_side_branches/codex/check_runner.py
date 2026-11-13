#!/usr/bin/env python
"""Focused runner checks; no registered full-study computation."""
import ast
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import subprocess
import sys
import time

import run_true as runner
from true_bond import HERE, ROOT


def crash_worker(task, sender, memory_mb):
    os._exit(17)


def stuck_worker(task, sender, memory_mb):
    time.sleep(10)


def main():
    checks = []
    for file in sorted(HERE.glob("*.py")):
        ast.parse(file.read_text())
    checks.append({"name": "python_syntax", "pass": True})
    command = [str(ROOT / ".venv/bin/python"), "-B", str(HERE / "run_true.py"),
               "--workers", "2", "--only", "212", "709", "914", "--smax", "1",
               "--seconds-limit", "5", "--output", "runner_check_rows.jsonl"]
    rows_file = HERE / "runner_check_rows.jsonl"
    # This script creates its own scratch; unique evidence is retained in JSON.
    if rows_file.exists():
        raise FileExistsError("runner check output already exists; preserve it and use its existing receipt")
    try:
        result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=25)
        raw = rows_file.read_bytes()
        rows = [json.loads(line) for line in raw.splitlines()]
        checks.append({"name": "two_worker_append", "pass": result.returncode == 0
                       and len(rows) == 3 and all(row["status"] == "done" for row in rows)
                       and {row["idx"] for row in rows} == {212, 709, 914},
                       "rows": rows, "returncode": result.returncode, "stderr": result.stderr})
        again = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=10)
        checks.append({"name": "resume_skips_existing_without_modification",
                       "pass": again.returncode == 0 and rows_file.read_bytes() == raw,
                       "sha256": hashlib.sha256(raw).hexdigest()})
    finally:
        if rows_file.exists():
            rows_file.unlink()
    bad_file = HERE / "runner_check_missing_newline.jsonl"
    if bad_file.exists():
        raise FileExistsError(bad_file)
    try:
        bad_file.write_text('{"idx": 709}')
        bad_command = command[:-1] + [bad_file.name]
        bad = subprocess.run(bad_command, cwd=ROOT, text=True, capture_output=True, timeout=10)
        checks.append({"name": "reject_unterminated_jsonl_without_append", "pass": bad.returncode != 0
                       and bad_file.read_text() == '{"idx": 709}', "stderr": bad.stderr})
    finally:
        if bad_file.exists():
            bad_file.unlink()
    original_worker = runner._worker
    try:
        runner._worker = crash_worker
        result = list(runner.run_tasks([(709, [], 1, 0.1)], 1, 1024))
        checks.append({"name": "dead_worker_yields_failure_row", "pass": len(result) == 1
                       and result[0]["status"] == "worker_crash" and result[0]["worker_exitcode"] == 17,
                       "result": result})
        runner._worker = stuck_worker
        started = time.monotonic()
        result = list(runner.run_tasks([(709, [], 1, 0.01)], 1, 1024))
        checks.append({"name": "stuck_owned_worker_is_killed_and_reaped", "pass": len(result) == 1
                       and result[0]["status"] == "timeout" and time.monotonic() - started < 3,
                       "result": result})
    finally:
        runner._worker = original_worker
    checks.append({"name": "no_owned_children_left", "pass": not mp.active_children()})
    validation_file = HERE / "validation.json"
    validation = json.loads(validation_file.read_text())
    validation["runner_checks"] = {"pass": all(check["pass"] for check in checks), "cases": checks}
    validation_file.write_text(json.dumps(validation, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"checks": len(checks), "pass": validation["runner_checks"]["pass"]}))


if __name__ == "__main__":
    main()
