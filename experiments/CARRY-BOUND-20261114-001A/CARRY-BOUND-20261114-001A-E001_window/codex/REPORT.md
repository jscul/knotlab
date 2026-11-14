# CARRY-BOUND window jobs: resolved-addendum handoff

Scope: ticket `CARRY-BOUND-20261114-001A`. **Gates a–e and all four synthetic controls pass.**
The fresh smoke contains exactly 20 `ok` records. The three full jobs are prepared with the
resolved retry policy and remain unlaunched. No population P1–P5 evaluation was performed.

This implements the final section of the
[preregistration](../../../../research/CARRY-BOUND-20261114-001/preregistration.md),
“Addendum: Codex's implementation questions, resolved before the full run.” All writes are
inside CODEX. No Git commands, publication, tracker changes, or writes outside CODEX were used.
This is implementation and finite gate evidence, not a population finding or theorem.

## Implemented answers

| Answer | Final behavior |
| --- | --- |
| A1 | `start_states` retains one start per wrapper S-call. Q_0 contains all those states, U takes the minimum over them, and G2 collects contexts reached from every start. S as main retains its diagonal start. |
| A2 | Dead positions are the complement of the least liveness fixed point, seeded by knot occurrences and propagated backwards through live call positions across definitions. The dead-carriage control now certifies G. |
| A3 | The independent CNF gate checks every wrapper entry and every S-word of length s≤3. The end copy has absolute depth s for main=S and s+1 for a wrapper. Copies through its children's level are explicit; copies below are replaced by usual-limit relations. Entry indices are retained in the bond sample and rechecks. |
| A4 | P3 is enabled in `summarize.py`: a family satisfies its explanatory flag only when **every** unbounded repeating residue has no carried position sharing a knot with an own distinction. Caps or incomplete residue evidence remain unknown, count as unsuccessful in the full share, and are omitted in the sensitivity. |
| A5 | I-family sample cells use only the identity-graph R_s period and whether its repeating part has a knot-meeting phase. They require no completed Q_s or window residues, including for failed/capped I records. Every in-scope I family receives a syntactic cell before eligibility filtering. |
| A6 | Each residue selects the first available reading across tied least supports: B, widened B, tie, other. A bounded family's reading is the lowest-priority reading needed by any repeating residue. Summary shares use this exclusive attribution; nonexclusive details remain explicitly secondary. |
| A7 | Gate c searches both original and live-quotient G2 through each family's census r. Population G2 remains capped at r≤8. |
| A8 | All three full configurations were re-prepared with `--retry timeout,memory,crashed`, 3 workers, 600 seconds, 3G per case, and `MemoryMax=12G`, using `--prepare-only`. |

Changed code: `window.py`, `brute.py`, `gates.py`, `scope.py`, `sample.py`, `summarize.py`,
`inputs.py`, and `freeze_sources.py`. The latter supports preserving a prior manifest when
refreezing. Original input material is reused in place. No sample for path/direct search or
population summary has been selected or computed during this follow-up.

All CODEX Python files passed AST parsing. Synthetic summary fixtures checked the every-residue
P3 rule, exclusive readings, and gate-b completeness. The smoke's recorded exclusive readings
were also checked against their priority flags and the family's lowest-priority residue.

## Gate results

The current aggregate is [gates.json](gates.json). Fresh evidence is in
`gate_families_resolved_addendum/`, `gate_bonds_resolved_addendum/`, and
`smoke_resolved_addendum/`. Counts below include overlapping selections as separate recorded
checks, not distinct population families.

| Check | Result |
| --- | --- |
| Scope predicates | Passed: all inventory count tables and all 657 directly recorded own-distinction predicates match. |
| a: living and per-call relations | Passed: 374 recorded checks; no empty living relation or census-table mismatch. |
| b: B-covered residues | Passed: 374 checks, no violation or unavailable check. A capped window with syntactically no B-covered repeating phase has a complete, nonapplicable B check; it gains no window certificate. |
| c: forgetting controls | Passed: all 300; every computed lower-bound comparison, including the repeated level, passes. Original G2 and live-quotient G2 each certify all 300. The control with census r=11 certifies at r=11 in both readings. |
| d: explicit projections | Passed: all prescribed first 50 I families, including all 5 wrappers; 2,686 word/entry projections matched, with no skipped place or mismatch. |
| d: independent bond rechecks | Passed: all 200, drawn without replacement from 6,764 recorded least bonds using `random.Random(20261114)`. Each support is non-shattered and every one-member deletion is shattered. |
| e: incompatible certificates | Passed: 374 checks; no simultaneous full window bound and growth certificate. |

| Synthetic control | Result |
| --- | --- |
| Carried pendant knot | Passed: U=3 at every computed depth, with repeating period 1. |
| Carriage only in port-only knots | Passed: every computed U is `"> 6"`; no repeating window bound. |
| Identity carriage with a dead coordinate | Passed: coordinate 0 is dead, live positions are 1 and 2, and G certifies. U(0)=3 through live distinctions; repeating U is `"> 6"`, with no bound through the dead coordinate. |
| Forgetting | Passed: U=3,4,`"> 6"`; original G2 certifies at r=2 and live-quotient G2 at r=1. |

The family gates have 355 `ok` records, 906.917 summed case seconds, and a 270.14 MiB maximum
runner case peak. The largest case took 429.168 seconds; the runner's parent-plus-workers peak
was 370.59 MiB. The 200 bond checks took 16.172 summed case seconds, with a 120.95 MiB maximum
runner case peak and a 188.01 MiB parent-plus-workers peak. No fresh gate had a runner error,
timeout, memory failure, or crash.

## Fresh 20-case smoke

`smoke_resolved_addendum/` contains 20 `ok` cases: 15 bounded, 4 growing, and 1 undecided.
These are smoke readings only. Both former wrapper skips now compute: `0001e4875df4` has
three starts and is bounded; `00958d5b001b` has two starts and has a growth certificate.
All three smoke gate checks pass; B is nonapplicable on all 20 cases.

The undecided family `00202e31b0eb` retains the inherited census length-set cap and reaches the
prescribed Q_s construction and product-storage caps. K is empty, so its B implication is
nonapplicable. No cap is treated as a bound or growth certificate.

Summed case time: **35.430 seconds**. Runner start to final heartbeat: **37.173 seconds**.
Maximum runner case peak: **151.80 MiB**; maximum parent-plus-workers peak: **232.33 MiB**.
Exact per-case metrics and full keys are in [metrics_resolved_addendum.json](metrics_resolved_addendum.json).

| CARRY key prefix | c | Wrapper | Verdict | Seconds | Runner peak MiB | Window RSS MiB |
| --- | ---: | :---: | --- | ---: | ---: | ---: |
| 0001e4875df4 | 2 | yes | bounded | 0.728691 | 59.36 | 97.10 |
| 0008564c9ad7 | 5 | no | bounded | 0.136416 | 59.57 | 97.17 |
| 001b38fb4521 | 2 | no | growing | 0.021365 | 59.58 | 97.18 |
| 001ddeb65496 | 2 | no | bounded | 0.545402 | 63.56 | 97.39 |
| 00202e31b0eb | 3 | no | undecided | 31.524888 | 151.17 | 169.77 |
| 00415487c940 | 2 | no | growing | 0.211876 | 151.80 | 175.53 |
| 0046f8341e18 | 2 | no | bounded | 0.046986 | 143.37 | 129.54 |
| 0049d81dd3eb | 2 | no | bounded | 0.131067 | 143.37 | 129.54 |
| 004bcd84d820 | 2 | no | bounded | 0.138349 | 143.37 | 129.54 |
| 007282c55f6c | 4 | no | bounded | 0.503549 | 143.37 | 129.54 |
| 007b58da377d | 4 | no | bounded | 0.077295 | 143.37 | 128.54 |
| 007d596a4084 | 2 | no | bounded | 0.197644 | 143.37 | 128.54 |
| 0080c1c03e47 | 2 | no | bounded | 0.072210 | 143.37 | 128.54 |
| 00958d5b001b | 2 | yes | growing | 0.018032 | 143.37 | 128.54 |
| 009607149c9c | 2 | no | bounded | 0.073937 | 143.37 | 128.54 |
| 0099db2328d2 | 3 | no | growing | 0.113073 | 143.37 | 128.54 |
| 00a1e2eb9913 | 3 | no | bounded | 0.138538 | 143.37 | 127.54 |
| 00a25bdfff5d | 2 | no | bounded | 0.011129 | 143.37 | 125.54 |
| 00a56113e7dc | 2 | no | bounded | 0.115313 | 143.37 | 125.54 |
| 00b5f28a7b90 | 3 | no | bounded | 0.624480 | 143.37 | 124.54 |

Prefixes are the first 12 characters of `sha256("CARRY:" + key)`. Memory values are MiB.
The reused worker can retain allocations from an earlier case. The window column records
its RSS checkpoint maximum; the runner uses its own proportional accounting. Neither is an
isolated fresh-process measurement for every family.

## Sources and retained evidence

[source_manifest.json](source_manifest.json) freezes 35 code/input digests, including the
resolved preregistration. Verification passed after the gates and smoke. The final entry-point
SHA-256 matches each re-prepared `job.json`; all three full directories have neither results
nor execution state. No implementation changed after the freeze or between the fresh checks.

The preceding report, gate aggregate, manifest, and full-job configurations are preserved as
`REPORT_before_resolved_addendum.md`, `gates_before_resolved_addendum.json`,
`source_manifest_before_resolved_addendum.json`, and each full directory's
`job_before_resolved_addendum.json`. Earlier runs and samples remain intact. The new bond
sample is `bond_sample_resolved_addendum.json`; the new smoke-only check is
`smoke_gates_resolved_addendum.json`. All retained runs are validation evidence.

Execution used one shared-runner worker, hence two compute processes including the parent,
with 600 seconds and 3G per case and a 4G foreground configuration. The window retains its
585-second and 2.8-GB internal checkpoints. Full settings below were prepared only. Tracker
registration remains with the thread because it writes outside CODEX.

## Commands for the thread

Run from `/home/jscul/p-vs-np-contact-first`, using `.venv/bin/python -B` throughout.
The following starts the already prepared full jobs. Codex has not executed these commands.

```bash
CARRY_CODEX=experiments/CARRY-BOUND-20261114-001A/CARRY-BOUND-20261114-001A-E001_window/codex

.venv/bin/python -B scripts/longrun.py resume --out "$CARRY_CODEX/window_full"
.venv/bin/python -B scripts/longrun.py wait --out "$CARRY_CODEX/window_full"

.venv/bin/python -B "$CARRY_CODEX/sample.py" paths --results "$CARRY_CODEX/window_full"
.venv/bin/python -B scripts/longrun.py resume --out "$CARRY_CODEX/paths_full"
.venv/bin/python -B scripts/longrun.py wait --out "$CARRY_CODEX/paths_full"

.venv/bin/python -B "$CARRY_CODEX/sample.py" direct --results "$CARRY_CODEX/paths_full"
.venv/bin/python -B scripts/longrun.py resume --out "$CARRY_CODEX/direct_full"
.venv/bin/python -B scripts/longrun.py wait --out "$CARRY_CODEX/direct_full"

.venv/bin/python -B "$CARRY_CODEX/summarize.py" \
  --window "$CARRY_CODEX/window_full" \
  --paths "$CARRY_CODEX/paths_full" \
  --direct "$CARRY_CODEX/direct_full"
```

After each service starts, use the printed UTC registration command to register a run expected
to exceed ten minutes. `sample.py` freezes the path list before paths run, then preserves that
list before extending it with the post-path direct sample. An empty frozen list has no cases.
The final summary command is the thread's population P1–P5 reading; P3 is now enabled.

The preparations actually performed, after preserving the previous configurations, were:

```bash
.venv/bin/python -B scripts/longrun.py launch "$CARRY_CODEX/job_window.py" \
  --out "$CARRY_CODEX/window_full" --unit carry-window-full \
  --workers 3 --case-timeout 600 --case-mem 3G --mem-max 12G \
  --retry timeout,memory,crashed --prepare-only
.venv/bin/python -B scripts/longrun.py launch "$CARRY_CODEX/job_paths.py" \
  --out "$CARRY_CODEX/paths_full" --unit carry-window-paths \
  --workers 3 --case-timeout 600 --case-mem 3G --mem-max 12G \
  --retry timeout,memory,crashed --prepare-only
.venv/bin/python -B scripts/longrun.py launch "$CARRY_CODEX/job_direct.py" \
  --out "$CARRY_CODEX/direct_full" --unit carry-window-direct \
  --workers 3 --case-timeout 600 --case-mem 3G --mem-max 12G \
  --retry timeout,memory,crashed --prepare-only
```

The fresh validation execution was:

```bash
.venv/bin/python -B "$CARRY_CODEX/freeze_sources.py" \
  --archive-existing source_manifest_before_resolved_addendum.json
.venv/bin/python -B scripts/longrun.py launch "$CARRY_CODEX/gates.py" \
  --out "$CARRY_CODEX/gate_families_resolved_addendum" --unit carry-gates-resolved-addendum \
  --workers 1 --case-timeout 600 --case-mem 3G --mem-max 4G --prepare-only
.venv/bin/python -B scripts/longrun.py run \
  --out "$CARRY_CODEX/gate_families_resolved_addendum" --foreground --limit 5
.venv/bin/python -B scripts/longrun.py run \
  --out "$CARRY_CODEX/gate_families_resolved_addendum" --foreground --limit 350

.venv/bin/python -B "$CARRY_CODEX/gates.py" freeze-bonds \
  --families "$CARRY_CODEX/gate_families_resolved_addendum" \
  --output bond_sample_resolved_addendum.json
.venv/bin/python -B scripts/longrun.py launch "$CARRY_CODEX/gates.py" \
  --out "$CARRY_CODEX/gate_bonds_resolved_addendum" --unit carry-bonds-resolved-addendum \
  --workers 1 --case-timeout 600 --case-mem 3G --mem-max 4G \
  --param phase=bonds --param bond_sample=bond_sample_resolved_addendum.json --prepare-only
.venv/bin/python -B scripts/longrun.py run \
  --out "$CARRY_CODEX/gate_bonds_resolved_addendum" --foreground --limit 200

.venv/bin/python -B scripts/longrun.py launch "$CARRY_CODEX/job_window.py" \
  --out "$CARRY_CODEX/smoke_resolved_addendum" --unit carry-smoke-resolved-addendum \
  --workers 1 --case-timeout 600 --case-mem 3G --mem-max 4G --prepare-only
.venv/bin/python -B scripts/longrun.py run \
  --out "$CARRY_CODEX/smoke_resolved_addendum" --foreground --limit 20

.venv/bin/python -B "$CARRY_CODEX/gates.py" summarize \
  --families "$CARRY_CODEX/gate_families_resolved_addendum" \
  --bonds "$CARRY_CODEX/gate_bonds_resolved_addendum" --smoke "$CARRY_CODEX/smoke_resolved_addendum"
.venv/bin/python -B "$CARRY_CODEX/summarize.py" \
  --window "$CARRY_CODEX/smoke_resolved_addendum" --check-gates \
  --output smoke_gates_resolved_addendum.json
```

Preparation and freeze commands above are an execution record, not commands to repeat over
existing immutable outputs. Gate aggregation and the smoke-only gate check may be repeated.

## Ambiguities

None remain. A1–A8 are resolved by the preregistration's addendum and implemented above.
No additional interpretation was selected and no new question arose. The preceding unresolved
questions remain available in `REPORT_before_resolved_addendum.md` for provenance.
