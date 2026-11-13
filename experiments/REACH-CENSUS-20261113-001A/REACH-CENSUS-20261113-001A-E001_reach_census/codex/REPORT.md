# Reach census: computation hand-off

Scope: ticket `REACH-CENSUS-20261113-001A`, experiment E001. All created files are inside CODEX. The full census and the all-664 census-cap repeat have not been run.

## Execution and gates

| Gate | Executed coverage | Result |
| --- | --- | --- |
| G0 | 1,200,000 sampler calls; 223,261 draws; 1,651 stored definitions | Passed; no mismatches |
| G1 | 618 eligible families; 13,598 BD depths; 95 referee cases | Passed; no mismatches |
| G2 | 618 wrappers; 17,922 shifted depths | Two class-only mismatches: indices 580 and 762 |
| G3 | Independent checker and controls; required 150-family panel unselected | Panel skipped under ambiguity A1 |
| G4 | 122,191 distinct forever families; 220,880 draws | Passed; no failures |

Every mismatch, including both full canonical family keys, is in `gates.json` and `validation_g2.jsonl`. For both G2 mismatches, the original class is `none at any depth` and the wrapped class is `lost at large depths`. Original L(1..3) is `[INF, INF, INF]`; wrapped L(1..3) is `[3, INF, INF]`. Lambda is None and completeness is true for both. Independent CNF searches at depths 1–3 agree within the size-7 search bound (`g2_diagnostic.json`). `INF` is 1,000,000,000.

The smoke run used `Random(1113).sample(sorted_keys, 1000)` from 124,572 distinct families. The alternative used section 5's `Random(20261113).sample` on sorted eligible smoke keys, with the section 7 ceiling of 200: 275 eligible, 200 run. Frozen keys are in `smoke_selection.json` and `smoke_alt_selection.json`. Smoke class shares are written only in `smoke_summary.json`.

## Commands actually run

```sh
cd /home/jscul/p-vs-np-contact-first
CODEX=experiments/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/codex
.venv/bin/python -B "$CODEX/replay_draws.py"
.venv/bin/python -B "$CODEX/gate_compactness.py"
.venv/bin/python -B "$CODEX/validation.py" --gates G1 G2 G3 --workers 1 --summary "$CODEX/validation_summary.json"
.venv/bin/python -B "$CODEX/smoke.py" --workers 2 > "$CODEX/smoke.log" 2>&1
.venv/bin/python -B "$CODEX/smoke.py" --workers 2 > "$CODEX/smoke_alt.log" 2>&1
.venv/bin/python -B "$CODEX/smoke.py" --workers 2
.venv/bin/python -B "$CODEX/brute_tests.py"
.venv/bin/python -B "$CODEX/check_runtime.py"
```

The second smoke invocation resumed the 1,000 first-call rows and ran the alternative sample; the final invocation checked resume and regenerated timing fields without recomputing any family. `check_runtime.py` exercised timeout, node, block, product-size and memory caps, and valid/malformed interrupted tails. A separate eight-family scheduler check exercised four actual computing processes and safe idle signals (`runner_checks.json`). Summary code passed syntax, help, boundary and small-fixture checks; no production full-run summary was generated.

## Timings and memory

G0: 14.852 s. G4: 22.569 s. G1: 269.186 s. G2: 271.304 s (G1/G2 each used one process).
First-call smoke wall time: 496.917 s; alternative wall time: 185.490 s. Each used two computing processes including its parent.

Observed aggregate smoke RSS peaks: first 2,011,820,032 bytes; alternative 810,749,952 bytes. Validation's largest recorded RSS: 167,387,136 bytes. Adding separate validation/G0/G4 maxima to the larger smoke aggregate peak gives 2,307,870,720 bytes; this is a sum of recorded stage maxima, not a continuously measured combined peak. RSS monitors sampled only this task's own PIDs.

The final runner enforces 300 seconds, 300,000 nodes, at most 12 distinctions per block, 3 GB worker RSS and a 7.5 GB aggregate guard. Scientific workers use one BLAS/OpenMP thread. At most four computing processes ran concurrently. The normal census counts its computing parent among `--workers`; the G1 preflight uses at most N−1 children plus its idle parent.

### First-call timings by class

| Class or block size | Total seconds | Mean seconds | Maximum seconds |
| --- | ---: | ---: | ---: |
| S1 limit dead | 0.012837 | 0.000856 | 0.001120 |
| S2 no copy | 0.068237 | 0.000573 | 0.001258 |
| S3 no own distinctions | 0.224270 | 0.000598 | 0.005321 |
| S4 free own distinctions | 0.006873 | 0.000529 | 0.000722 |
| bounded | 297.731207 | 1.266941 | 99.311748 |
| grows | 60.268381 | 0.602684 | 25.266690 |
| lost at large depths | 1.544375 | 0.128698 | 0.274961 |
| none at any depth | 10.294798 | 0.081705 | 1.077474 |
| unresolved | 601.023204 | 120.204641 | 300.848761 |

### First-call timings by block size

| Class or block size | Total seconds | Mean seconds | Maximum seconds |
| --- | ---: | ---: | ---: |
| 3 | 0.187241 | 0.000571 | 0.002183 |
| 4 | 5.210591 | 0.029946 | 1.417380 |
| 5 | 44.456806 | 0.216862 | 29.637379 |
| 6 | 3.579494 | 0.044744 | 0.975385 |
| 7 | 105.371771 | 1.672568 | 99.311748 |
| 8 | 329.038202 | 5.062126 | 300.172072 |
| 9 | 353.710455 | 6.098456 | 300.848761 |
| 10 | 111.031777 | 8.540906 | 91.702985 |
| 11 | 17.723011 | 2.531859 | 16.174813 |
| 12 | 0.860049 | 0.860049 | 0.860049 |
| 13 | 0.002209 | 0.000736 | 0.000958 |
| 14 | 0.000855 | 0.000855 | 0.000855 |
| 19 | 0.000784 | 0.000784 | 0.000784 |
| 21 | 0.000937 | 0.000937 | 0.000937 |

### Last-call timings by class

| Class or block size | Total seconds | Mean seconds | Maximum seconds |
| --- | ---: | ---: | ---: |
| bounded | 237.022568 | 2.301190 | 183.771542 |
| grows | 19.450137 | 0.422829 | 14.117037 |
| lost at large depths | 0.963464 | 0.240866 | 0.284586 |
| none at any depth | 2.844764 | 0.061843 | 0.283139 |
| unresolved | 0.000794 | 0.000794 | 0.000794 |

### Last-call timings by block size

| Class or block size | Total seconds | Mean seconds | Maximum seconds |
| --- | ---: | ---: | ---: |
| 4 | 1.016017 | 0.018143 | 0.241307 |
| 5 | 1.448904 | 0.027864 | 0.191598 |
| 6 | 15.602446 | 0.538015 | 14.117037 |
| 7 | 46.273469 | 2.435446 | 45.206788 |
| 8 | 6.025236 | 0.286916 | 2.738629 |
| 9 | 5.011278 | 0.263751 | 0.392846 |
| 10 | 183.934478 | 91.967239 | 183.771542 |
| 12 | 0.969105 | 0.969105 | 0.969105 |
| 19 | 0.000794 | 0.000794 | 0.000794 |

Block-size grouping uses the maximum of main's and S's distinction counts; absent S contributes zero. These are timings, without smoke class shares.

Four-worker projection from summed per-family smoke seconds: first-call census 30245.3 s (8.40 h); a 3,000-family alternative sample 976.1 s (0.27 h); combined family work 8.67 h. This scales sampled family work and divides by four. It excludes the all-664 preflight, summary/bootstrap work, and startup/I/O overhead; the alternative projection uses its 3,000-family ceiling. It is a runtime projection, not a measured full run.

## Full-run commands for the thread

```sh
cd /home/jscul/p-vs-np-contact-first
CODEX=experiments/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/codex
.venv/bin/python -B "$CODEX/run_census.py" --workers 4 --out "$CODEX/full" --only-gate664
.venv/bin/python -B "$CODEX/run_census.py" --workers 4 --out "$CODEX/full" --alt-ray
.venv/bin/python -B "$CODEX/summarize.py" "$CODEX/full"
```

The ordinary runner always performs/resumes the all-664 G1 preflight; the first command is optional when using the second. Output is appended to `full/families.jsonl` and `full/alt_families.jsonl`; rerunning the same command skips recorded keys. Only an interrupted final fragment is repaired, and its bytes are preserved. G1 cap-affected comparisons are pending under A2; genuine mismatches remain failures. A partial ambiguity-only G1 does not prevent the independent family computation. The alternative sample is frozen in `full/alt_selection.json`. Output directories are restricted to CODEX, and execution has no session-state dependency.

`summarize.py DIR` writes counts, point bands, distributions and the agreement matrix. Ambiguity-dependent interval fields remain explicitly pending. Its opt-in quantile, stream and sampling-frame flags have no selected defaults. The bootstrap engine uses 2,000 individual-draw resamples and `Random(20261113)` after those conventions are supplied.

## Deviations and implementation checks

G2 did not pass its literal class requirement; both failures are retained. The required G3 panel and ambiguity-dependent bootstrap fields are skipped as listed below. No scientific definition or class rule was changed.

The implementation audit found and corrected the RSS-check gap during the exact test, gate return-field mismatch, gate process-budget error, interrupted-tail handling, and idle-signal race. `implementation_audit.json` preserves the earlier snapshot; `runtime_checks.json`, `runner_checks.json`, and `validation_summary.json` record the fixes' focused checks. G1/G2 rows preserve their actual pre-fix source hashes. Later changes added resource guards, metadata defaults, output guards and runner handling; the block maps and class rules were unchanged. The primary smoke measurements precede those resource guard fixes; the alternative used them.

No full census, publication, Git mutation, or write outside CODEX was performed. The forbidden study directory was not read. Regenerable control scratch was removed; code, raw rows, gates, logs and check evidence remain in CODEX.

## Ambiguities

**A1. The frozen spec does not define the eligible pool/cutoff or ranking for 'among the smallest-block families', or a unique allocation/selection procedure satisfying 150 total, at least 10 of each computed class where available, and at least 40 families with more than one definition. The full census is forbidden at this hand-off. Which explicitly supplied family keys and computed reference rows constitute the G3 panel?**

Affected: G3 150-family panel selection and its required run. Action: not selected; skipped.

**A2. For the all-664 G1 repeat, which comparisons apply when PR is incomplete at its 2,000,000-node/1,200-second caps, or its complete graph exceeds 300,000 nodes, or this run stops at the new resource caps?**

Affected: cap-incompatible comparisons in the later full-run preflight. Action: affected comparisons pending; numerical results retained; no semantic mismatch inferred from differing caps.

**A3. G2 requires equal classes. At indices 580 and 762 the literal classes differ, while lambda, completeness and all shifted depths agree. Should this requirement change?**

Affected: G2 class-equality requirement. Action: no change chosen; both mismatches retained as failures.

**A4. Which finite-sample quantile convention defines the bootstrap 2.5% and 97.5% endpoints?**

Affected: bootstrap endpoints. Action: pending; no convention selected.

**A5. Is Random(20261113) reset per bootstrap group or shared, and in what group order?**

Affected: bootstrap endpoints. Action: pending; no stream policy selected.

**A6. Does P1 resample its conditional denominator directly, or all computed draws before conditioning?**

Affected: P1 bootstrap interval. Action: pending; no frame selected.

**A7. Does P3 resample each comparison cell independently or pool the cells before regrouping?**

Affected: P3 bootstrap lower endpoint. Action: pending; no frame selected.

**A8. For the unresolved class itself, what does assigning unresolved against or for its own class share mean?**

Affected: unresolved class low/high bands. Action: pending; exact unresolved share is still reported.
