"""Assemble the hand-off from recorded validation and smoke; starts no jobs."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def read(name):
    return json.loads((HERE / name).read_text())


def number(value):
    return "unrecorded" if value is None else f"{value:,.3f}"


def timing_table(groups):
    lines = ["| Group | Families | Timed | Total seconds | Mean seconds | Median seconds | Maximum seconds |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for name, group in groups.items():
        lines.append(f"| {name} | {group['families']} | {group['timed_families']} | {number(group['total_seconds'])} | {number(group['mean_seconds'])} | {number(group['median_seconds'])} | {number(group['max_seconds'])} |")
    return "\n".join(lines)


def main():
    validation = dict(gates={})
    for short in ("node", "controls", "reg", "last"):
        gate = read(f"handoff2_validation/validation_{short}_summary.json")
        validation["gates"][gate["gate"]] = gate
    validation["validation_config"] = read("handoff2_validation/validation_summary.json").get("validation_config")
    smoke = read("smoke_summary.json")
    rows = [json.loads(line) for line in (HERE / "smoke_families.jsonl").read_text().splitlines() if line.strip()]
    selection = read("smoke_selection.json")
    keys = [row["key"] for row in rows]
    if len(rows) != 300 or len(set(keys)) != 300 or set(keys) != set(selection["keys"][:300]):
        raise ValueError("The first 300 frozen smoke families have not completed")
    gates = dict(validation["gates"])
    brute_path = HERE / "brute" / "brute_summary.json"
    gates["G-brute"] = json.loads(brute_path.read_text()) if brute_path.exists() else dict(
        gate="G-brute", status="pending", passed=None, checked_families=0, mismatches=[],
        pending_comparisons=["Independent panel has no summary."])
    required = ("G-last", "G-brute", "G-node")
    verdicts = [gates[name].get("passed") for name in required]
    passed = False if False in verdicts else None if any(v is None for v in verdicts) else True
    ambiguity_path = HERE / "handoff2_ambiguities.json"
    ambiguities = json.loads(ambiguity_path.read_text()) if ambiguity_path.exists() else []
    result = {
        "experiment_id": "EVERY-RAY-20261113-001A-E001", "handoff": 2,
        "full_run_launched": False, "status": "failed" if passed is False else "incomplete" if passed is None else "passed",
        "validation_passed": passed, "regression_passed": gates["G-reg"].get("passed"),
        "gates": gates, "validation_config": validation.get("validation_config"),
        "smoke": {"required_families": 300, "recorded_families": len(rows),
                  "exact_frozen_prefix_completed": True, "seed": 1113,
                  "extended_port_transport": True,
                  "incomplete_timing_rows": smoke.get("projection_incomplete_timing_rows"),
                  "aggregate_peak_complete": smoke.get("aggregate_peak_complete")},
        "ambiguities": ambiguities,
        "retained_preliminary_gate_attempt": "handoff2_validation/validation_last_initial_attempt.jsonl",
        "runtime_controls": {name: read(name) for name in (
            "handoff2_runtime_controls.json", "handoff2_interval_gate_controls.json",
            "handoff2_settled_controls.json", "handoff2_resume_controls.json", "transport_controls.json")},
        "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(HERE.glob("*.py"))},
    }
    (HERE / "gates.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    gate_lines = ["| Gate | Completed families/cases | Mismatches | Pending | Verdict |",
                  "|---|---:|---:|---:|---|"]
    for name in ("G-reg", "G-last", "G-node", "G-brute", "branching-zero-controls"):
        gate = gates[name]
        coverage = gate.get("rows", gate.get("finished_families", gate.get("checked_families", gate.get("cases", 0))))
        if isinstance(coverage, list):
            coverage = len(coverage)
        verdict = "passed" if gate.get("passed") is True else "failed" if gate.get("passed") is False else gate.get("status", "incomplete")
        gate_lines.append(f"| {name} | {coverage} | {len(gate.get('mismatches', []))} | {len(gate.get('pending_comparisons', []))} | {verdict} |")
    base = "experiments/EVERY-RAY-20261113-001A/EVERY-RAY-20261113-001A-E001_min_over_paths/codex"
    brute = gates["G-brute"]
    if brute.get("status") == "pending_panel_order":
        brute_accounting = "G-brute: 0 of 120 finished. No panel was selected and no scientific brute run was launched, because the block ordering remains ambiguous. Panel quotas therefore have not been assessed; the pending record is `brute/brute_summary.json`."
    else:
        brute_accounting = (f"G-brute finished-family accounting: {brute.get('finished_families', 0)} of 120; all-depth comparable families: {brute.get('complete_families', 0)}. Panel, quota, coverage, resource-stop and comparison records are retained under `brute/`.")
    report = [
        "# EVERY-RAY-20261113-001A: second computation hand-off", "",
        "Status: addendum changes, requested gates, and the 300-family smoke are recorded below. The full job has not been launched. No scientific interpretation is made.", "",
        "All writes stayed in CODEX. Commands used `.venv/bin/python -B` from the repository root. No Git command was run; neither prohibited experiment directory was read. Earlier hand-off outputs are preserved in `handoff1_preserved/` and the original validation journals.", "",
        "## Implementation", "",
        "`paths_dp.py` extends the census DP over every main entry (A1) and every onward SELF call. The extended node is `(F, Gf, T)` with eight port-transport masks. The plain closing accepts every mask; the uncarried closing accepts only `T=0`. Both readings retain min-plus depths 1–30, exact Karp rates and exact residue certificates with the frozen resource caps.", "",
        "Fixed rays use independent `(entry, SELF call)` pairs (A5); a bounded pair decides `mixed_path_needed=false`, otherwise all pairs must be resolved before asserting true. `call_symmetry.py` implements A6 by testing all six port permutations on full allowed flat-block assignments, fixing every own distinction. `brute_paths.py` extends the independent CNF/assignment/member search for individual descending paths (A2–A4). `summarize_paths.py` adds the A7 population, common full-archive draw resamples in A8, and A9 splits; it was checked on synthetic inputs, not run on the full population.", "",
        "`run_paths.py` is resumable and requires all 224 G-last cases to pass before computing the full population. Existing outputs with a different producer fingerprint are rejected. At most three computing processes are used; each family retains the 12-distinction, 300,000-node, 300-second and 3 GB limits, with a 7.5 GB aggregate stop.", "",
        "Settled S4 records retain `settled_case` and report the six-class verdict `none at any depth`, with explicit no-bond values through depth 30. This no-bond control was checked independently. The unresolved c=1/multiple-entry intersection is skipped as described under Ambiguities; identical entry argument tuples retain the one-ray carry.", "",
        "## Gates", "", "\n".join(gate_lines), "",
        "G-reg is regression only. Every mismatch and pending comparison remains in `gates.json` and the per-family validation journals. The seven failing keys found in the earlier saved journal were included with the sorted 60-key prefix; the addendum named six. The full runner still requires all 224.", "",
        "G-reg checked 500 families: 491 passed, and nine had 54 start/reachable-graph differences under A1. The compared depth values, rates and classes agreed. G-last checked 62 distinct keys: 61 passed; case 112 remains pending because its path and last-ray graphs both reached 300,000 nodes. It has no exact last-ray reference, so no pass is claimed and no inequality mismatch is established.", "",
        "G-last computes only its required 30 min-plus layers, using the same graph builders. Karp/residue work remains in the scientific family computation. A retained path graph gives an upper bound on the true path minimum: a value below an exact reference certifies the required inequality. Incomplete reference graphs, or path upper bounds that do not certify it, remain pending. Gate-only rows never enter population outputs.", "",
        "The preliminary G-last attempt retained 19 records, including one late-alarm cleanup error, in `handoff2_validation/validation_last_initial_attempt.jsonl`. It was interrupted for repair, then all 62 cases were computed afresh. The final gate took 588.671 seconds and peaked at 4,052,037,632 aggregate RSS bytes. The preliminary attempt's complete wall time and peak are unavailable; they are not included in that final-gate measurement.", "",
        "The cleanup repair blocks guard signals before changing handlers and restores the original mask. Eighteen real-signal/post-mask-change injection controls passed for family and validation guards; handlers, masks and timers were restored. Finite-layer replay, incomplete-reference controls, undefined-bootstrap-interval controls, settled-family brute checks, and producer resume/provenance controls passed. The synthetic rehearsal is retained separately under `runtime_rehearsal/`. No full test suite was run.", "",
        brute_accounting, "",
        "## Smoke resources", "",
        "Exactly the first 300 keys of the frozen `Random(1113)` 1,000-key selection were used. Smoke class shares appear only in `smoke_summary.json`.", "",
        "Timing by over-paths class:", "", timing_table(smoke["timings_by_class"]), "",
        "Timing by SELF-call count c:", "", timing_table(smoke["timings_by_c"]), "",
        f"Wall time: {number(smoke.get('wall_seconds'))} seconds. Measured aggregate peak RSS: {number(smoke.get('aggregate_peak_rss_bytes'))} bytes. Maximum recorded family peak: {number(smoke.get('maximum_family_peak_rss_bytes'))} bytes.", "",
        f"Projected full-run time on three workers: {number(smoke.get('projected_full_seconds_on_3_workers'))} seconds, using sample total per-family seconds / 300 × eligible families / 3. This includes fixed-pair and uncarried diagnostics, and excludes carry-only I/O, the mandatory all-224 pre-gate, and the full summary bootstrap. It is an estimate from this smoke.", "",
        "## Commands", "", "Requested gates and smoke (executed for this hand-off):", "", "```bash",
        f".venv/bin/python -B {base}/validate_paths.py --gates node controls reg last --workers 1 --last-count 60 --include-earlier-last-failures --out-dir {base}/handoff2_validation",
        f".venv/bin/python -B {base}/validate_paths.py --gates last --workers 3 --last-count 60 --include-earlier-last-failures --out-dir {base}/handoff2_validation",
        f".venv/bin/python -B {base}/validate_paths.py --gates node controls last --workers 3 --last-count 60 --include-earlier-last-failures --out-dir {base}/handoff2_validation",
        f".venv/bin/python -B {base}/smoke_paths.py --workers 3 --count 300", "```", "",
        "Full run and summary (not executed; the full runner first gates all 224):", "", "```bash",
        f".venv/bin/python -B {base}/run_paths.py --workers 3 --out {base}/full",
        f".venv/bin/python -B {base}/summarize_paths.py {base}/full", "```", "",
        "## Ambiguities", "",
        *([f"{i}. {item}" for i, item in enumerate(ambiguities, 1)] if ambiguities else ["None outstanding."]), "",
        "## Deviations and retained limitations", "",
        "No full job, full-population bootstrap, ticket/scope mutation, publication or commit was performed. The original eight questions are answered by the addendum; only outstanding questions above remain. Missing or capped calculations retain unresolved or incomplete status. No empirical gate is promoted to a theorem.", "",
    ]
    (HERE / "REPORT.md").write_text("\n".join(report))
    print(json.dumps({"smoke_families": len(rows), "validation_passed": passed,
                      "regression_passed": result["regression_passed"], "full_run_launched": False}))


if __name__ == "__main__":
    main()
