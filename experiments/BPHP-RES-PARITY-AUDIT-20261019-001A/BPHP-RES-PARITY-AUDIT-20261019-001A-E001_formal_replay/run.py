#!/usr/bin/env python3
"""Replay of Braun's pinned bit-PHP formalization (BPHP-RES-PARITY-AUDIT-20261019-001A-E001).

Follows the published procedure (arXiv 2609.23015v1, Appendix B.2) on a checkout
outside this repository, without editing any pinned source, then runs two
controls. Temporary control files go under the checkout's .lake directory, as
the author's own verify.py does. Writes a log, the verifier's report and
result.json under artifacts/.

    python3 -B run.py
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / "BPHP-RES-PARITY-AUDIT-20261019-001A" / HERE.name
CHECKOUT = Path("/home/jscul/external-audits/bit-php-check")
FORMAL = CHECKOUT / "formalization"
COMMIT = "8904bf09a5376f48a00d1c25d079bf0c6441502a"
AGGREGATE = "claims/BitPHPPreprintRevision1.lean"
STANDARD = {"propext", "Classical.choice", "Quot.sound"}
ENV = {**os.environ, "MATHLIB_NO_CACHE_ON_UPDATE": "1", "LEAN_NUM_THREADS": "8"}


def run(log, label: str, command: list[str], timeout: int) -> dict:
    started = time.time()
    log.write(f"\n$ {' '.join(command)}\n")
    log.flush()
    try:
        done = subprocess.run(command, cwd=FORMAL, env=ENV, capture_output=True, text=True, timeout=timeout)
        code, output = done.returncode, done.stdout + done.stderr
    except subprocess.TimeoutExpired as exc:
        code, output = "timeout", (exc.stdout or "") + (exc.stderr or "") if isinstance(exc.stdout, str) else "timeout"
    log.write(output)
    log.flush()
    return {"label": label, "command": command, "exit": code, "seconds": round(time.time() - started, 1),
            "tail": output[-4000:] if isinstance(output, str) else ""}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    head = subprocess.run(["git", "-C", str(CHECKOUT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "-C", str(CHECKOUT), "status", "--porcelain", "--untracked-files=no"],
                           capture_output=True, text=True).stdout.strip()
    result: dict = {
        "schema_version": 1,
        "experiment_id": "BPHP-RES-PARITY-AUDIT-20261019-001A-E001",
        "ticket": "BPHP-RES-PARITY-AUDIT-20261019-001A",
        "checkout_commit": head,
        "checkout_matches_pin": head == COMMIT,
        "checkout_tracked_changes": dirty,
        "toolchain_pin": (FORMAL / "lean-toolchain").read_text().strip(),
        "steps": [],
    }
    with (OUT / "replay.log").open("w") as log:
        steps = result["steps"]
        steps.append(run(log, "lean_version", ["lean", "--version"], 1800))
        steps.append(run(log, "cache_get", ["lake", "exe", "cache", "get", AGGREGATE], 7200))
        report = OUT / "verification.txt"
        if report.exists():
            report.unlink()
        steps.append(run(log, "verify", ["python3", "verify.py", "--target", AGGREGATE, "--out", str(report)], 14400))
        steps.append(run(log, "leanchecker_fresh",
                         ["lake", "env", "leanchecker", "--fresh", "claims.BitPHPPreprintRevision1"], 14400))

        # Controls, in temporary files under .lake (no pinned source is edited).
        tmp = FORMAL / ".lake" / "audit_controls"
        tmp.mkdir(parents=True, exist_ok=True)
        sorry_file = tmp / "SorryControl.lean"
        sorry_file.write_text("import claims.BitPHPPreprintRevision1\n"
                              "theorem auditSorryControl : (2:ℕ) + 2 = 5 := by sorry\n"
                              "#print axioms auditSorryControl\n")
        steps.append(run(log, "control_sorry", ["lake", "env", "lean", str(sorry_file)], 3600))
        source = (FORMAL / "claims" / "BitPHPExponential.lean").read_text()
        mutated = source.replace("theorem bitPHP_exponential :", "theorem auditMutatedExponential :", 1)
        mutated = mutated.replace("Real.exp (((2^ℓ:ℕ):ℝ)/(32768*(ℓ:ℝ)^2)) < (S:ℝ)",
                                  "Real.exp (((2^ℓ:ℕ):ℝ)/(1*(ℓ:ℝ)^2)) < (S:ℝ)", 1)
        result["mutation_applied"] = mutated != source and "auditMutatedExponential" in mutated \
            and "(1*(ℓ:ℝ)^2)" in mutated
        mutated_file = tmp / "MutatedExponential.lean"
        mutated_file.write_text(mutated)
        steps.append(run(log, "control_mutated_bound", ["lake", "env", "lean", str(mutated_file)], 7200))

    by = {s["label"]: s for s in steps}
    verification = report.read_text() if report.exists() else ""
    axioms: dict[str, list[str] | str] = {}
    for match in re.finditer(r"'([^']+)' depends on axioms: \[([^\]]*)\]", verification):
        axioms[match.group(1)] = sorted(a.strip() for a in match.group(2).split(",") if a.strip())
    for match in re.finditer(r"'([^']+)' does not depend on any axioms", verification):
        axioms[match.group(1)] = []
    typed = re.search(r"MathResearch\.bitPHP_exponential :(.*?)(?:\n'|\n\S+ depends|\Z)", verification, re.S)
    result.update({
        "axiom_reports": axioms,
        "all_reported_axioms_standard": bool(axioms) and all(set(v) <= STANDARD for v in axioms.values()),
        "main_theorem_elaborated_type": typed.group(1).strip() if typed else None,
        "verify_pass_line": next((l for l in verification.splitlines() if l.startswith(("PASS", "FAIL"))), None),
        "control_sorry_detected": "sorryAx" in by["control_sorry"]["tail"],
        "control_mutated_rejected": by["control_mutated_bound"]["exit"] not in (0, "timeout"),
    })
    passed = (result["checkout_matches_pin"] and not dirty
              and all(by[k]["exit"] == 0 for k in ("cache_get", "verify", "leanchecker_fresh"))
              and result["all_reported_axioms_standard"]
              and result["control_sorry_detected"] and result["mutation_applied"]
              and result["control_mutated_rejected"])
    result["status"] = "passed" if passed else "failed"
    (OUT / "result.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: result[k] for k in ("status", "checkout_matches_pin", "all_reported_axioms_standard",
                                              "control_sorry_detected", "control_mutated_rejected",
                                              "verify_pass_line")}, indent=1))
    for step in steps:
        print(f"  {step['label']}: exit {step['exit']} in {step['seconds']}s")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
