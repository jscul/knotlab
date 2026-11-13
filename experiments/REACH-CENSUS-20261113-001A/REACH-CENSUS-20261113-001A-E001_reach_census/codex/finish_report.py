"""Assemble factual hand-off outputs. This never computes a family graph."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
REL = str(HERE.relative_to(ROOT))


def load(name):
    return json.loads((HERE/name).read_text())


def rows(name):
    return [json.loads(line) for line in (HERE/name).open() if line.strip()]


def save(name, value):
    (HERE/name).write_text(json.dumps(value, indent=2, sort_keys=True)+"\n")


def table(title, values):
    out = [f"### {title}", "", "| Class or block size | Total seconds | Mean seconds | Maximum seconds |",
           "| --- | ---: | ---: | ---: |"]
    order = sorted(values, key=int) if all(str(k).isdigit() for k in values) else list(values)
    for key in order:
        value = values[key]
        out.append(f"| {key} | {value['total_seconds']:.6f} | {value['mean_seconds']:.6f} | {value['max_seconds']:.6f} |")
    return "\n".join(out)


def main():
    replay, compact = load("replay_gate.json"), load("compactness_gate.json")
    val, smoke = load("validation_summary.json"), load("smoke_summary.json")
    g1, g2 = rows("validation_g1.jsonl"), rows("validation_g2.jsonl")
    runtime, runner = load("runtime_checks.json"), load("runner_checks.json")
    brute, diagnostic = load("brute_self_checks.json"), load("g2_diagnostic.json")
    questions = [
        dict(id="A1", question=val["G3"]["question"],
             affected="G3 150-family panel selection and its required run", action="not selected; skipped"),
        dict(id="A2", question="For the all-664 G1 repeat, which comparisons apply when PR is incomplete at its 2,000,000-node/1,200-second caps, or its complete graph exceeds 300,000 nodes, or this run stops at the new resource caps?",
             affected="cap-incompatible comparisons in the later full-run preflight", action="affected comparisons pending; numerical results retained; no semantic mismatch inferred from differing caps"),
        dict(id="A3", question="G2 requires equal classes. At indices 580 and 762 the literal classes differ, while lambda, completeness and all shifted depths agree. Should this requirement change?",
             affected="G2 class-equality requirement", action="no change chosen; both mismatches retained as failures"),
        dict(id="A4", question="Which finite-sample quantile convention defines the bootstrap 2.5% and 97.5% endpoints?",
             affected="bootstrap endpoints", action="pending; no convention selected"),
        dict(id="A5", question="Is Random(20261113) reset per bootstrap group or shared, and in what group order?",
             affected="bootstrap endpoints", action="pending; no stream policy selected"),
        dict(id="A6", question="Does P1 resample its conditional denominator directly, or all computed draws before conditioning?",
             affected="P1 bootstrap interval", action="pending; no frame selected"),
        dict(id="A7", question="Does P3 resample each comparison cell independently or pool the cells before regrouping?",
             affected="P3 bootstrap lower endpoint", action="pending; no frame selected"),
        dict(id="A8", question="For the unresolved class itself, what does assigning unresolved against or for its own class share mean?",
             affected="unresolved class low/high bands", action="pending; exact unresolved share is still reported"),
    ]
    gate1 = dict(val["G1"], passed=val["G1"]["gate_ok"],
                 BD_depth_comparisons=sum(row["BD_depths"] for row in g1),
                 referee_intersections=sum(row["referee_checked"] for row in g1),
                 eligibility="PR complete true and nodes <= 20000; 618 of BD's 664 families")
    gate2 = dict(val["G2"], passed=val["G2"]["gate_ok"],
                 shifted_depth_comparisons=29*len(g2),
                 independent_diagnostic=dict(depth_checks=len(diagnostic["checks"]),
                                             all_agree=diagnostic["all_depth_checks_agree"], file="g2_diagnostic.json"))
    gates = dict(G0=replay, G1=gate1, G2=gate2,
                 G3=dict(val["G3"], passed=None, requested_families=150,
                         panel_skipped_for_ambiguity=True, controls_passed=brute["passed"],
                         controls_file="brute_self_checks.json", additional_controls="brute_tests.py"),
                 G4=compact, all_gates_passed=False, ambiguities=questions,
                 resource_checks=dict(runtime=runtime, runner=runner,
                                      validation=val.get("support_checks")),
                 mathematical_validation_source_hashes=dict(G1=g1[0]["validation_config"]["code"],
                                                           G2=g2[0]["validation_config"]["code"]))
    save("gates.json", gates)
    extra_peak = max(val["run_resources"]["g1"]["max_process_peak_rss_kib"]*1024,
                     val["run_resources"]["g2"]["max_process_peak_rss_kib"]*1024,
                     val["run_resources"]["g1"]["max_sampled_peak_rss_bytes"],
                     val["run_resources"]["g2"]["max_sampled_peak_rss_bytes"])
    first_peak = smoke["run_info"]["aggregate_peak_rss_bytes"]
    alt_peak = smoke["alternative_run_info"]["aggregate_peak_rss_bytes"]
    conservative_peak = max(first_peak, alt_peak)+extra_peak+replay["peak_rss_bytes"]+compact["peak_rss_bytes"]
    first_projection = smoke["projected_full_first_ray_seconds_on_4_workers"]
    alt_projection = smoke.get("projected_full_alt_seconds_on_4_workers", 0)
    out = ["# Reach census: computation hand-off", "",
           "Scope: ticket `REACH-CENSUS-20261113-001A`, experiment E001. All created files are inside CODEX. The full census and the all-664 census-cap repeat have not been run.", "",
           "## Execution and gates", "",
           "| Gate | Executed coverage | Result |", "| --- | --- | --- |",
           f"| G0 | 1,200,000 sampler calls; {replay['total_draws']:,} draws; {replay['defs_checked']:,} stored definitions | Passed; no mismatches |",
           f"| G1 | {len(g1)} eligible families; {gate1['BD_depth_comparisons']:,} BD depths; {gate1['referee_intersections']} referee cases | Passed; no mismatches |",
           f"| G2 | {len(g2)} wrappers; {gate2['shifted_depth_comparisons']:,} shifted depths | Two class-only mismatches: indices 580 and 762 |",
           "| G3 | Independent checker and controls; required 150-family panel unselected | Panel skipped under ambiguity A1 |",
           f"| G4 | {compact['forever_families']:,} distinct forever families; {compact['forever_draws']:,} draws | Passed; no failures |", "",
           "Every mismatch, including both full canonical family keys, is in `gates.json` and `validation_g2.jsonl`. For both G2 mismatches, the original class is `none at any depth` and the wrapped class is `lost at large depths`. Original L(1..3) is `[INF, INF, INF]`; wrapped L(1..3) is `[3, INF, INF]`. Lambda is None and completeness is true for both. Independent CNF searches at depths 1–3 agree within the size-7 search bound (`g2_diagnostic.json`). `INF` is 1,000,000,000.", "",
           f"The smoke run used `Random(1113).sample(sorted_keys, 1000)` from {replay['distinct_families']:,} distinct families. The alternative used section 5's `Random(20261113).sample` on sorted eligible smoke keys, with the section 7 ceiling of 200: {smoke['alternative_eligible']} eligible, {smoke['alternative_families']} run. Frozen keys are in `smoke_selection.json` and `smoke_alt_selection.json`. Smoke class shares are written only in `smoke_summary.json`.", "",
           "## Commands actually run", "", "```sh", "cd /home/jscul/p-vs-np-contact-first",
           f"CODEX={REL}", '.venv/bin/python -B "$CODEX/replay_draws.py"',
           '.venv/bin/python -B "$CODEX/gate_compactness.py"',
           '.venv/bin/python -B "$CODEX/validation.py" --gates G1 G2 G3 --workers 1 --summary "$CODEX/validation_summary.json"',
           '.venv/bin/python -B "$CODEX/smoke.py" --workers 2 > "$CODEX/smoke.log" 2>&1',
           '.venv/bin/python -B "$CODEX/smoke.py" --workers 2 > "$CODEX/smoke_alt.log" 2>&1',
           '.venv/bin/python -B "$CODEX/smoke.py" --workers 2',
           '.venv/bin/python -B "$CODEX/brute_tests.py"',
           '.venv/bin/python -B "$CODEX/check_runtime.py"', "```", "",
           "The second smoke invocation resumed the 1,000 first-call rows and ran the alternative sample; the final invocation checked resume and regenerated timing fields without recomputing any family. `check_runtime.py` exercised timeout, node, block, product-size and memory caps, and valid/malformed interrupted tails. A separate eight-family scheduler check exercised four actual computing processes and safe idle signals (`runner_checks.json`). Summary code passed syntax, help, boundary and small-fixture checks; no production full-run summary was generated.", "",
           "## Timings and memory", "",
           f"G0: {replay['seconds']:.3f} s. G4: {compact['seconds']:.3f} s. G1: {val['G1']['seconds']:.3f} s. G2: {val['G2']['seconds']:.3f} s (G1/G2 each used one process).",
           f"First-call smoke wall time: {smoke['run_info']['wall_seconds']:.3f} s; alternative wall time: {smoke['alternative_run_info']['wall_seconds']:.3f} s. Each used two computing processes including its parent.", "",
           f"Observed aggregate smoke RSS peaks: first {first_peak:,} bytes; alternative {alt_peak:,} bytes. Validation's largest recorded RSS: {extra_peak:,} bytes. Adding separate validation/G0/G4 maxima to the larger smoke aggregate peak gives {conservative_peak:,} bytes; this is a sum of recorded stage maxima, not a continuously measured combined peak. RSS monitors sampled only this task's own PIDs.", "",
           "The final runner enforces 300 seconds, 300,000 nodes, at most 12 distinctions per block, 3 GB worker RSS and a 7.5 GB aggregate guard. Scientific workers use one BLAS/OpenMP thread. At most four computing processes ran concurrently. The normal census counts its computing parent among `--workers`; the G1 preflight uses at most N−1 children plus its idle parent.", "",
           table("First-call timings by class", smoke["timings_by_class"]), "",
           table("First-call timings by block size", smoke["timings_by_block_size"]), "",
           table("Last-call timings by class", smoke["alternative_timings_by_class"]), "",
           table("Last-call timings by block size", smoke["alternative_timings_by_block_size"]), "",
           "Block-size grouping uses the maximum of main's and S's distinction counts; absent S contributes zero. These are timings, without smoke class shares.", "",
           f"Four-worker projection from summed per-family smoke seconds: first-call census {first_projection:.1f} s ({first_projection/3600:.2f} h); a 3,000-family alternative sample {alt_projection:.1f} s ({alt_projection/3600:.2f} h); combined family work {(first_projection+alt_projection)/3600:.2f} h. This scales sampled family work and divides by four. It excludes the all-664 preflight, summary/bootstrap work, and startup/I/O overhead; the alternative projection uses its 3,000-family ceiling. It is a runtime projection, not a measured full run.", "",
           "## Full-run commands for the thread", "", "```sh", "cd /home/jscul/p-vs-np-contact-first", f"CODEX={REL}",
           '.venv/bin/python -B "$CODEX/run_census.py" --workers 4 --out "$CODEX/full" --only-gate664',
           '.venv/bin/python -B "$CODEX/run_census.py" --workers 4 --out "$CODEX/full" --alt-ray',
           '.venv/bin/python -B "$CODEX/summarize.py" "$CODEX/full"', "```", "",
           "The ordinary runner always performs/resumes the all-664 G1 preflight; the first command is optional when using the second. Output is appended to `full/families.jsonl` and `full/alt_families.jsonl`; rerunning the same command skips recorded keys. Only an interrupted final fragment is repaired, and its bytes are preserved. G1 cap-affected comparisons are pending under A2; genuine mismatches remain failures. A partial ambiguity-only G1 does not prevent the independent family computation. The alternative sample is frozen in `full/alt_selection.json`. Output directories are restricted to CODEX, and execution has no session-state dependency.", "",
           "`summarize.py DIR` writes counts, point bands, distributions and the agreement matrix. Ambiguity-dependent interval fields remain explicitly pending. Its opt-in quantile, stream and sampling-frame flags have no selected defaults. The bootstrap engine uses 2,000 individual-draw resamples and `Random(20261113)` after those conventions are supplied.", "",
           "## Deviations and implementation checks", "",
           "G2 did not pass its literal class requirement; both failures are retained. The required G3 panel and ambiguity-dependent bootstrap fields are skipped as listed below. No scientific definition or class rule was changed.", "",
           "The implementation audit found and corrected the RSS-check gap during the exact test, gate return-field mismatch, gate process-budget error, interrupted-tail handling, and idle-signal race. `implementation_audit.json` preserves the earlier snapshot; `runtime_checks.json`, `runner_checks.json`, and `validation_summary.json` record the fixes' focused checks. G1/G2 rows preserve their actual pre-fix source hashes. Later changes added resource guards, metadata defaults, output guards and runner handling; the block maps and class rules were unchanged. The primary smoke measurements precede those resource guard fixes; the alternative used them.", "",
           "No full census, publication, Git mutation, or write outside CODEX was performed. The forbidden study directory was not read. Regenerable control scratch was removed; code, raw rows, gates, logs and check evidence remain in CODEX.", "",
           "## Ambiguities", ""]
    for question in questions:
        out += [f"**{question['id']}. {question['question']}**", "",
                f"Affected: {question['affected']}. Action: {question['action']}.", ""]
    (HERE/"REPORT.md").write_text("\n".join(out))
    names = [p for p in HERE.iterdir() if p.is_file() and p.suffix in (".py", ".json", ".jsonl", ".gz", ".md")
             and p.name not in ("artifact_manifest.json", "last_message.md")]
    save("artifact_manifest.json", {p.name:dict(bytes=p.stat().st_size, sha256=hashlib.sha256(p.read_bytes()).hexdigest())
                                    for p in sorted(names)})
    print(json.dumps(dict(report="REPORT.md", gates="gates.json", first_smoke=smoke["families"],
                          alternative_smoke=smoke["alternative_families"], G2_mismatches=len(gate2["mismatches"]))))


if __name__ == "__main__":
    main()
