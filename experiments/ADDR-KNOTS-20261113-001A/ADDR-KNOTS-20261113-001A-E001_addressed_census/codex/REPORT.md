# Addressed census implementation and bounded validation

Gate status: **passed_with_skipped_ambiguous_assertions**. The full census was not launched.

All task-created files and outputs are inside this directory. Existing log and handoff files are preserved. No Git mutation, network request, or read of the forbidden exploratory directory was used.

## What was written

- `addr.py`: address actions, pattern generation and SHA-1, exact letter and relative activity, automaton canonicalization, bounded SAT with phase hints, and all twelve-level derived fields.
- `reference.py`: independent recursive action, permutation inversion, explicit patterns, exhaustive assignment enumeration, and exact integer activity counts.
- `run_census.py`: both deterministic populations, distinct-key processing, append-and-flush shards, source/input consistency checks and restart recovery. The coordinator is worker zero, so four workers means three child processes and four Python processes total.
- `summarize.py`: requested frozen summaries, cluster/draw bootstraps and prediction rules, with explicit skipped outputs where the frozen specification does not determine the unit's labels.
- `validate.py`, copied `check.py`, `smoke_report.py` and `finalize_report.py`: individual gates, interruption comparison, timing analysis, and this handoff.

## Full-run launch

Run from `/home/jscul/p-vs-np-contact-first`; this command was **not executed**:

```sh
.venv/bin/python -B experiments/ADDR-KNOTS-20261113-001A/ADDR-KNOTS-20261113-001A-E001_addressed_census/codex/run_census.py --workers 4 --out experiments/ADDR-KNOTS-20261113-001A/ADDR-KNOTS-20261113-001A-E001_addressed_census/codex/full
```

Use the same command to resume. Keep the source unchanged while an output directory is in use. After completion:

```sh
.venv/bin/python -B experiments/ADDR-KNOTS-20261113-001A/ADDR-KNOTS-20261113-001A-E001_addressed_census/codex/summarize.py experiments/ADDR-KNOTS-20261113-001A/ADDR-KNOTS-20261113-001A-E001_addressed_census/codex/full
```

`--keys-file` and `--stop-after` are smoke/validation controls; omit both for the full census. The runner imports no interactive-session state. Four workers respect the specified process ceiling. Eight-worker timing below is only an extrapolation.

## Validation gates

| Gate | Result | Evidence |
| --- | --- | --- |
| V-act | passed | `{"action_cases": 26136, "address_comparisons": 1483944, "automata": 200}`; `validation_parts/V-act.json` |
| V-rel | passed | `{"action_cases": 10800, "address_comparisons": 613200, "automata_and_placements": 200}`; `validation_parts/V-rel.json` |
| V-sat | passed | `{"assignments_read": 16453000, "both_decide": 300, "both_undecided": 0, "one_undecided": 0, "small_instances": 1000}`; `validation_parts/V-sat.json` |
| V-B0 | passed | `{"F0_assertions_skipped": 45, "settled_cases": 133}`; `validation_parts/V-B0.json` |
| V-act-class | passed | `{"automata": 500}`; `validation_parts/V-act-class.json` |
| V-code | passed | `{"W_draws": 40000, "r_pvalue": 0.22957655782851832, "r_samples": 32530, "s_pvalue": 0.0549810077710834}`; `validation_parts/V-code.json` |
| V-resume | passed | `{"baseline_keys": 300, "replayed_keys": 300}`; `validation_parts/V-resume.json` |

The complete statistics, seeds, panels, failures, null comparisons and source hashes are in `validation.json` and `validation_parts/`. A solver-pair comparison only asserts agreement when both solvers decide; null comparisons are retained.

B0 printed: `passed 2242 0 2000 0 {1: 'dead', 2: 'dead', 3: 'dead', 4: 'dead'}`.

The F3 assertion on empty settled keys is skipped because of the recorded F0/F3 contradiction. The assignment-count wording is also recorded below; the control exhausts the stated SAT instance. All unambiguous prescribed assertions are evaluated.

## Smoke timings

The deterministic disjoint strata contain 100 E keys with s=3 and original list r≥4, 100 further uniformly selected E keys, and 100 further uniformly selected W keys with s≥2; seed 20261116. Sampling pools and exclusions are retained in `prepared/smoke_keys.json`.

Keys: 300; workers: 4; elapsed: 533.228 s. Per-key mean: 4.124886 s; maximum: 481.468579 s. Maximum measured worker peak RSS: 266.81 MiB.

Fates: `{"F0": 123, "F2": 37, "F3": 140}`. Undecided levels: 7; keys with any undecided level: 3; returns: 1.

The observed return is retained as a finding under P2's frozen failure criterion; the smoke summary reports `fails_return_observed`.

| Level | Full level mean (s) | Full level max (s) | SAT mean (s) | SAT max (s) | Undecided |
| --- | --- | --- | --- | --- | --- |
| 1 | 0.000113 | 0.000601 | 0.000004 | 0.000017 | 0 |
| 2 | 0.000206 | 0.007728 | 0.000060 | 0.000249 | 0 |
| 3 | 0.000147 | 0.010377 | 0.000041 | 0.000205 | 0 |
| 4 | 0.000120 | 0.000322 | 0.000048 | 0.000168 | 0 |
| 5 | 0.000149 | 0.000516 | 0.000072 | 0.000354 | 0 |
| 6 | 0.000204 | 0.000796 | 0.000118 | 0.000621 | 0 |
| 7 | 0.000328 | 0.001643 | 0.000219 | 0.001494 | 0 |
| 8 | 0.000886 | 0.047878 | 0.000731 | 0.047656 | 0 |
| 9 | 0.006390 | 0.938502 | 0.006141 | 0.938112 | 0 |
| 10 | 1.304546 | 234.272407 | 1.304111 | 234.271678 | 2 |
| 11 | 0.986547 | 143.590722 | 0.985749 | 143.589312 | 2 |
| 12 | 1.824923 | 276.952361 | 1.823370 | 276.948778 | 3 |

Full population: 29339 distinct keys. Poststratified estimated serial compute: 50903.8 s. Ideal eight-worker projection: 6363.0 s (1.767 h); using observed four-worker overhead: 10967.3 s (3.046 h).

Extrapolation from 300 deliberately stratified keys. Eight workers were not launched; contention, heavy solver tails, absent s=1 samples, and scaling overhead are unmeasured. The two unsampled s=1 keys are charged the W-only mean as part of this coarse runtime estimate.

Poststratum details and all raw timing aggregates are in `smoke_metrics.json`. The interrupted smoke was killed at exactly 150 completed keys and then restarted. Every requested non-timing field, plus worker assignment, is identical; only wall timings and the additional peak-RSS profiling field are excluded from comparison.

## Binding limitations

Each level uses CaDiCaL195 with `conf_budget(2000000)` followed by `solve_limited`, including after a death. Conflict counters are exposed and retained; the smoke observed up to 2,000,003 conflicts because the solver checks its budget at internal boundaries. Phase hints are supported: requests and support are retained per level in `phase_n`; previous alive models are lifted by x>>1 solely as phase hints. Empty patterns require no solver call. Exact hash framing is recorded in each key's `hash_serialization`.

Native numerical thread counts are one. The final runner caps each worker's address space at 1,400 MiB, below 1.5 decimal GB. The uninterrupted baseline began under the earlier 1,536 MiB address-space cap; measured peak RSS was 267 MiB. Only the cap and two restart edge cases changed after that baseline began; the core computation was unchanged. Both runner fingerprints are retained in the run metadata, and focused restart controls passed in `runner_edge_controls.json`. No process from another study was stopped. A conflict budget is not a wall-time budget; difficult solver calls can dominate runtime.

`statsmodels` is absent. The logistic design matrix is written and the fit is skipped as requested. The smoke is deliberately incomplete population coverage, and its summary is descriptive only. No conclusion beyond the twelve read levels follows.

## Ambiguities

1. What reference bits should E record for its shifted, capped gamma draw: its sampled gamma code length or W's code length of its capped final r, and should its fixed automaton carry a W reference cost? E bits is null; actual gamma data, fixed-automaton reference cost, placement cost and both total candidates are retained. The W-code candidate is a formal length at r=9, which W rejects. E is unweighted, so E's comparison is unaffected.

2. V-sat says 'all 2^n assignments', but level n has 2^n variables and therefore 2^(2^n) Boolean assignments. Does n mean the number of variables in that phrase? The independent control exhausts the assignment space of the stated SAT instance, retaining its actual assignment count; no assertion that this count equals the literal 2^level is made.

3. When the same twelve-level pattern is generated by descriptions with different relative activity classes, which class, or what explicitly defined multiple-class treatment, belongs to that distinct-pattern unit? Affected outputs: distinct-pattern summaries by relative activity class, matched-density cells containing the pattern, logistic design rows.

4. When the same twelve-level pattern is generated by descriptions in different automaton classes, which automaton class is its bootstrap and logistic cluster? Affected outputs: cluster counts, cluster bootstrap intervals, logistic design rows.

5. When descriptions of the same distinct pattern disagree on s = 1, single-placement, or first-letter-settled flags, does the unit count as settled, unsettled, both, or according to a specified description? Affected outputs: distinct-pattern settled shares, settled-excluded matched-density membership.

6. When descriptions of the same distinct pattern fall on opposite sides of s >= 2 or s >= 3, how is that pattern's membership in the conditional distinct-pattern census defined? Affected outputs: the affected conditional distinct-pattern fate shares.

7. When descriptions of the same distinct pattern have different letter activity classes, which letter class belongs to the unit in the secondary summaries? Affected outputs: distinct-pattern secondary letter-class summaries.

8. When separate descriptions of the same twelve-level pattern yield different budgeted solver verdicts or fates, may the decided verdict from one description resolve another description's undecided verdict, or must a prescribed common solve be used? Affected outputs: fate cells for affected distinct patterns, first-death summaries, affected matched-density cells.

9. P1 literally requires every single-distinct-placement or first-letter-settled description to be F3, while F0 is separately assigned to descriptions with no knots. How should P1 classify such a description that is F0, including the s = 1 cases? Affected outputs: the interpretation of a literal P1/F0 failure.

10. For the weighted W secondary comparison, do the 30-decided-unit and under-10%-FU eligibility thresholds use distinct patterns or fair-coin draws, and how should a pattern represented in several automaton classes contribute to the five-cluster threshold? Affected outputs: W eligibility when these readings do not agree, affected W intervals and verdicts.

11. What response or inclusion rule should the logistic sensitivity fit use for FU units: count them as dead, count them as alive, fit both, or exclude them? The two-assignment rule is explicit for matched-cell verdicts but not for this fit. Affected outputs: a logistic fit containing FU units; its design matrix remains available.


## Addendum

Implemented the eleven answers in `research/ADDR-KNOTS-20261113-001/codex_spec_addendum.md` (2026-11-13, 18:05 UTC) in **`summarize_v2.py`**, copied from `summarize.py` and revised. The earlier report and its Ambiguities section remain the original handoff; the answers now resolve all eleven questions. This changes summary grouping only. `addr.py`, `run_census.py`, `summarize.py`, the original validation records, all smoke inputs, and the earlier smoke summaries are unchanged. Nothing under `codex/full/` was read, modified, or summarized; the running census and its processes were not inspected or changed. No census, solver, network, or Git mutation was run.

The implemented rules are:

- Every activity-class split, including the secondary letter class, uses `(pattern hash, relative class)`. Unsplit counts use the pattern hash. The primary relative-class labels remain finitary, bounded, polynomial, and exponential; exact polynomial degrees are retained as memberships without multiplying that primary unit. Automaton class and letter class come from the first description in numeric sorted key order within the unit.
- A unit is settled if any member is single-placement or first-letter-settled. Its `s` is the least member `s`. Conditional weighted fate shares sum the accepted draw frequencies of those selected units, using their least `s`; sampled-s coverage metadata is kept separate. s=1 descriptions must be F0.
- Decided verdicts are merged across all complete descriptions of each pattern, including across populations, before fates, first deaths, null flags, and returns are recomputed. Opposite decided verdicts stop the program with exit code 2 and list the pattern hash, level, values, key IDs, and source records. Replayed keys and records rejected for incorrect derived metadata cannot hide a contradiction. Compatible replay outcomes can resolve nulls without replacing the first record's other scientific metadata.
- P1 checks settled descriptions with a knot. F0 descriptions, including s=1, are excluded and counted.
- W secondary inference counts class units for eligibility: at least 30 decided units from at least five automaton classes in each arm, and under 10% FU by unit count. Death shares and density means use summed accepted W draw frequencies. Its bootstrap resamples W draws within each arm, 2,000 times, seed 20261115. E remains unweighted and resamples the first-description automaton classes. Rejected draws are excluded from weighted inference and counted separately.
- Logistic sensitivity writes both design matrices, `FU_alive` and `FU_dead`, for E and W, with the same class units and first-description clusters. W rows carry frequency weights; E rows have weight one. `statsmodels` remains absent, so every fit is explicitly skipped. E's bits remain null with their existing components retained. The earlier V-sat implementation already exhausted assignments of the instance's 2^n variables; it was not changed or rerun.

The default CLI retains `DIR/summary.json` and `DIR/summary.md`. The optional filename prefix preserves earlier smoke summaries:

```sh
.venv/bin/python -B experiments/ADDR-KNOTS-20261113-001A/ADDR-KNOTS-20261113-001A-E001_addressed_census/codex/summarize_v2.py experiments/ADDR-KNOTS-20261113-001A/ADDR-KNOTS-20261113-001A-E001_addressed_census/codex/smoke_uninterrupted --output-prefix summary_v2
```

This was run only on `smoke_uninterrupted/` and `smoke_resumed/`. Each now contains `summary_v2.json` and `summary_v2.md`; the JSON summaries are identical across the two runs. The new script supersedes the original summarizer for applying the addendum; it has **not** been run on the full census.

| Smoke population | Distinct pattern hashes | Pattern/relative-class units | Logistic rows per FU assignment |
| --- | --- | --- | --- |
| E | 102 | 105 | 65 |
| W | 56 | 58 | 12 |

Globally the smoke still has 300 descriptions and 154 distinct patterns. Its description fates remain F0 123, F2 37, F3 140, with one return. No smoke null was resolved by merging another description's decided verdict. The seven undecided level verdicts in three descriptions remain retained; their already-forced F2 fates remain decided, so there are no FU units. P1 checks 88 descriptions and has no failure; it excludes 123 F0 descriptions, of which 45 have a settled flag. There are no s=1 descriptions in this smoke. All four matched-density analyses have zero eligible cells, so the registered hypotheses remain unevaluated in this incomplete subset.

**Validation: 37 checks passed.** `validate_summary_v2.py` independently groups the raw smoke records and draw roster, checks the units and labels, conditional counts and weights, and both CLI outputs; confirms restart equality and input-order invariance; checks P1 and the retained return; and verifies protected input checksums. Explicit smoke-derived controls exercise null resolution, FU logistic responses, repeated-draw eligibility, weighted death shares, contradictory decided verdicts (including repeated keys and invalid derived metadata), and replay metadata preservation. E cluster and W draw bootstraps, with both FU responses, match an independent resampling-multiplicity calculation at 2,000 resamples and seed 20261115. These controls are validation fixtures, not new census observations. Temporary control files were removed.

```sh
.venv/bin/python -B experiments/ADDR-KNOTS-20261113-001A/ADDR-KNOTS-20261113-001A-E001_addressed_census/codex/validate_summary_v2.py
```

The receipt is `summary_v2_validation.json`, with check details, protected-input SHA-256 hashes, and the tested summarizer's hash. An independent read-only review found no remaining implementation issue after the replay controls were addressed. The original `validation.json` still records `passed_with_skipped_ambiguous_assertions`; it is preserved rather than relabelled or replaced. No original solver/action gate was rerun. Smoke-only validation establishes no registered result, all-level conclusion, or change to the canonical knot test. No generated-view change.
