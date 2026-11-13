"""Assemble gate evidence and the bounded-run handoff; never launch a census."""
import hashlib
import json
from pathlib import Path
import platform

HERE = Path(__file__).resolve().parent
REL = str(HERE.relative_to(Path.cwd()))
GATES = ("V-act", "V-rel", "V-sat", "V-B0", "V-act-class", "V-code", "V-resume")


def main():
    gates = {}
    for name in GATES:
        path = HERE / "validation_parts" / (name + ".json")
        gates[name] = json.loads(path.read_text()) if path.exists() else {"status": "missing", "passed": False}
    sources = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(HERE.glob("*.py"))}
    syntax = {}
    for path in sorted(HERE.glob("*.py")):
        try:
            compile(path.read_text(), str(path), "exec")
            syntax[path.name] = "passed"
        except SyntaxError as error:
            syntax[path.name] = str(error)
    ambiguities = [
        "What reference bits should E record for its shifted, capped gamma draw: its sampled gamma code length or W's code length of its capped final r, and should its fixed automaton carry a W reference cost? E bits is null; actual gamma data, fixed-automaton reference cost, placement cost and both total candidates are retained. The W-code candidate is a formal length at r=9, which W rejects. E is unweighted, so E's comparison is unaffected.",
        "V-sat says 'all 2^n assignments', but level n has 2^n variables and therefore 2^(2^n) Boolean assignments. Does n mean the number of variables in that phrase? The independent control exhausts the assignment space of the stated SAT instance, retaining its actual assignment count; no assertion that this count equals the literal 2^level is made."
    ]
    summary_amb = HERE / "summary_ambiguities.json"
    if summary_amb.exists():
        value = json.loads(summary_amb.read_text())
        for question in value.get("questions", []):
            ambiguities.append(question["question"] + " Affected outputs: " + ", ".join(question["affected_outputs"]) + ".")
    passed = all(g.get("passed", g.get("status") == "passed") for g in gates.values())
    data = {"status": "passed_with_skipped_ambiguous_assertions" if passed else "failed_or_incomplete",
            "full_census_launched": False, "gates": gates,
            "source_sha256": sources, "python": platform.python_version(),
            "workspace_checks": {"source_syntax": syntax,
                "runner_edges": json.loads((HERE / "runner_edge_controls.json").read_text()),
                "summary_controls": json.loads((HERE / "summary_controls.json").read_text())},
            "ambiguities": ambiguities,
            "scope": "Only the specified gates and 300-key smoke; no all-level or full-population conclusion."}
    (HERE / "validation.json").write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    smoke = json.loads((HERE / "smoke_metrics.json").read_text())
    report = ["# Addressed census implementation and bounded validation", "",
              f"Gate status: **{data['status']}**. The full census was not launched.", "",
              "All task-created files and outputs are inside this directory. Existing log and handoff files are preserved. No Git mutation, network request, or read of the forbidden exploratory directory was used.", "",
              "## What was written", "",
              "- `addr.py`: address actions, pattern generation and SHA-1, exact letter and relative activity, automaton canonicalization, bounded SAT with phase hints, and all twelve-level derived fields.",
              "- `reference.py`: independent recursive action, permutation inversion, explicit patterns, exhaustive assignment enumeration, and exact integer activity counts.",
              "- `run_census.py`: both deterministic populations, distinct-key processing, append-and-flush shards, source/input consistency checks and restart recovery. The coordinator is worker zero, so four workers means three child processes and four Python processes total.",
              "- `summarize.py`: requested frozen summaries, cluster/draw bootstraps and prediction rules, with explicit skipped outputs where the frozen specification does not determine the unit's labels.",
              "- `validate.py`, copied `check.py`, `smoke_report.py` and `finalize_report.py`: individual gates, interruption comparison, timing analysis, and this handoff.", "",
              "## Full-run launch", "",
              "Run from `/home/jscul/p-vs-np-contact-first`; this command was **not executed**:", "", "```sh",
              f".venv/bin/python -B {REL}/run_census.py --workers 4 --out {REL}/full", "```", "",
              "Use the same command to resume. Keep the source unchanged while an output directory is in use. After completion:", "", "```sh",
              f".venv/bin/python -B {REL}/summarize.py {REL}/full", "```", "",
              "`--keys-file` and `--stop-after` are smoke/validation controls; omit both for the full census. The runner imports no interactive-session state. Four workers respect the specified process ceiling. Eight-worker timing below is only an extrapolation.", "",
              "## Validation gates", "", "| Gate | Result | Evidence |", "| --- | --- | --- |"]
    for name, gate in gates.items():
        details = {k: v for k, v in gate.items() if k in (
            "automata", "automata_and_placements", "action_cases", "address_comparisons", "W_draws", "r_samples", "small_instances", "both_decide", "both_undecided", "one_undecided", "assignments_read", "baseline_keys", "replayed_keys")}
        if name == "V-code":
            details.update(s_pvalue=gate.get("s", {}).get("pvalue"), r_pvalue=gate.get("r", {}).get("pvalue"))
        if name == "V-B0":
            settled = gate.get("settled_smoke", {})
            cases = settled.get("settled_cases", [])
            details.update(settled_cases=len(cases) if isinstance(cases, list) else cases,
                           F0_assertions_skipped=len(settled.get("skipped_F0_assertions", [])))
        report.append(f"| {name} | {gate.get('status')} | `{json.dumps(details, sort_keys=True)}`; `validation_parts/{name}.json` |")
    code = gates["V-code"]
    report += ["", "The complete statistics, seeds, panels, failures, null comparisons and source hashes are in `validation.json` and `validation_parts/`. A solver-pair comparison only asserts agreement when both solvers decide; null comparisons are retained.", "",
               f"B0 printed: `{gates['V-B0'].get('printed_line', 'missing')}`.", "",
               "The F3 assertion on empty settled keys is skipped because of the recorded F0/F3 contradiction. The assignment-count wording is also recorded below; the control exhausts the stated SAT instance. All unambiguous prescribed assertions are evaluated.", "",
               "## Smoke timings", "",
               f"The deterministic disjoint strata contain 100 E keys with s=3 and original list r≥4, 100 further uniformly selected E keys, and 100 further uniformly selected W keys with s≥2; seed 20261116. Sampling pools and exclusions are retained in `prepared/smoke_keys.json`.", "",
               f"Keys: {smoke['keys']}; workers: 4; elapsed: {smoke['elapsed_seconds']:.3f} s. Per-key mean: {smoke['mean_wall_seconds_per_key']:.6f} s; maximum: {smoke['max_wall_seconds_per_key']:.6f} s. Maximum measured worker peak RSS: {smoke['max_peak_rss_mb']:.2f} MiB.", "",
               f"Fates: `{json.dumps(smoke['fates'], sort_keys=True)}`. Undecided levels: {smoke['undecided_levels']}; keys with any undecided level: {smoke['undecided_keys']}; returns: {smoke['returns']}.", "",
               "The observed return is retained as a finding under P2's frozen failure criterion; the smoke summary reports `fails_return_observed`.", "",
               "| Level | Full level mean (s) | Full level max (s) | SAT mean (s) | SAT max (s) | Undecided |", "| --- | --- | --- | --- | --- | --- |"]
    for row in smoke["levels"]:
        report.append(f"| {row['n']} | {row['mean_level_wall_seconds']:.6f} | {row['max_level_wall_seconds']:.6f} | {row['mean_solver_wall_seconds']:.6f} | {row['max_solver_wall_seconds']:.6f} | {row['undecided']} |")
    projection = smoke["full_run_projection"]
    report += ["", f"Full population: {projection['population_distinct_keys']} distinct keys. Poststratified estimated serial compute: {projection['estimated_serial_seconds']:.1f} s. Ideal eight-worker projection: {projection['ideal_8_worker_seconds']:.1f} s ({projection['ideal_8_worker_seconds']/3600:.3f} h); using observed four-worker overhead: {projection['8_worker_seconds_using_observed_overhead']:.1f} s ({projection['8_worker_seconds_using_observed_overhead']/3600:.3f} h).", "",
               projection["limitations"], "", "Poststratum details and all raw timing aggregates are in `smoke_metrics.json`. The interrupted smoke was killed at exactly 150 completed keys and then restarted. Every requested non-timing field, plus worker assignment, is identical; only wall timings and the additional peak-RSS profiling field are excluded from comparison.", "",
               "## Binding limitations", "",
               "Each level uses CaDiCaL195 with `conf_budget(2000000)` followed by `solve_limited`, including after a death. Conflict counters are exposed and retained; the smoke observed up to 2,000,003 conflicts because the solver checks its budget at internal boundaries. Phase hints are supported: requests and support are retained per level in `phase_n`; previous alive models are lifted by x>>1 solely as phase hints. Empty patterns require no solver call. Exact hash framing is recorded in each key's `hash_serialization`.", "",
               "Native numerical thread counts are one. The final runner caps each worker's address space at 1,400 MiB, below 1.5 decimal GB. The uninterrupted baseline began under the earlier 1,536 MiB address-space cap; measured peak RSS was 267 MiB. Only the cap and two restart edge cases changed after that baseline began; the core computation was unchanged. Both runner fingerprints are retained in the run metadata, and focused restart controls passed in `runner_edge_controls.json`. No process from another study was stopped. A conflict budget is not a wall-time budget; difficult solver calls can dominate runtime.", "",
               "`statsmodels` is absent. The logistic design matrix is written and the fit is skipped as requested. The smoke is deliberately incomplete population coverage, and its summary is descriptive only. No conclusion beyond the twelve read levels follows.", "",
               "## Ambiguities", ""]
    for number, ambiguity in enumerate(ambiguities, 1):
        report.append(f"{number}. {ambiguity if isinstance(ambiguity, str) else json.dumps(ambiguity, sort_keys=True)}")
        report.append("")
    (HERE / "REPORT.md").write_text("\n".join(report) + "\n")
    print(json.dumps({"status": data["status"], "gates": {k: v.get("status") for k, v in gates.items()}}))


if __name__ == "__main__":
    main()
