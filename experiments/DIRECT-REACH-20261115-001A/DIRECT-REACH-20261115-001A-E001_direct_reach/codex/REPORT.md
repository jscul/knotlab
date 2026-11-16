# DIRECT-REACH-20261115-001A

Scope: computational implementation and gates for the supplied specification.
All authored code, scratch, retained certificates, and runner outputs are in
this directory. The census and its implementation are read-only inputs. No
Git mutations, network access, or full population launch is authorized here.

**Result:** all final gates pass, and the smoke finished with ten `ok`
records (nine D and one U), no runner failures, and no active workers. All 30
N=10/11/12 life checks allow independently checked total states. The U
continuation found certified `L_N=4` at s=2; s=3 and s=4 remain undecided after
their 900 s budgets. No full D or U job was launched.

## What was written

- `job.py`: shared-runner `setup(params)` (`pop=D` or `pop=U`), sorted `cases()`,
  and all five specified computations in `run()`. Per-case scratch is removed
  at entry and in `finally`; durable per-case JSON is under `case_results/`.
  Life is checked at N=10, 11, and 12 with a 600 s union-solving budget each.
  For U, originally undecided census cells first reuse a certified spanning
  tie class or the new top-3 threshold answer when that resolves `L_N`;
  otherwise a separate query uses `k_max=10` and 900 s at that s.
- `reuse.py`, `population.py`: read-only imports and exact census selection.
  D has **146** descriptions: 34 constant-2, 66 constant-3, and 46 with
  `[3,3,4,4]`. U has **88** descriptions and 215 originally undecided `L_N`
  cells. The populations are disjoint and sorted by the full case identifier.
- `ties.py`: 64 fresh CaDiCaL random-phase states, checked against every knot,
  propose equal/complement-signature candidates. Each proposed pair receives
  two SAT calls. A confirmed pair has two retained checked refutations and
  joins the signed union-find. Counterstates refine candidate groups. At
  termination each signature class is one certified union-find class, so the
  listed classes encode **all** forced pairs, with relative signs and a
  two-refutation certificate forest. Singleton addresses are listed separately.
  Sampling is a candidate filter, never a statistical proof of a tie.
- `reach.py`: reuses the census `compute` body by a guarded local AST/source
  adaptation: configurable `k_max`, selected `s`, no histogram or additional
  target-restricted search. The original census engine and bond checker are
  imported unchanged. Top 2 uses `s=1..6`; top 3 uses `s=1..5`. A size-four
  search for the half-rate profile answers both thresholds in the same 300 s.
- `homomorphisms.py`, `hom_gate.py`: exact membership of every mapped stored
  depth-8 knot in the depth-9 pattern, with three distinct images. Prefix and
  suffix bits are applied after the ordinary state word; products act right
  to left. Identity composites occur once. Accepted maps and rejection
  counterexamples are recorded.
- `retention.py`: content-addressed, atomic gzip retention, including union
  refutations and the census engine's internal original/auxiliary CNF UNSAT
  answers. An internal negative answer is consumed only after CaDiCaL emits
  LRAT and `lrat_check` accepts it. Hashes and paths are in each case record.
  A timed-out certification is retained as an explicitly incomplete attempt
  and makes the affected query undecided. Models are retained and checked.
- `gate_job.py`, `tie_gate.py`, `gates.py`: shared-runner gates and their
  `gates.json` summary. The plain tie reference exhausts N=4 assignments by
  backtracking; fully unconstrained completions are represented together,
  counting every completion and both possible pair parities exactly.
- `smoke_job.py`: invokes the same production job on exactly ten cases, the
  first nine D cases and first U case, sorted by full case identifier. These
  cover all three D profiles, both threshold bounds, and U continuation.

The implementation computes finite observables only. No finite result is an
infinite-life assertion or a proof of a broader foundational claim. A mapped
stored knot is an exact three-distinction membership check, with no semantic
contact claim. Terminology follows the [Intuitions glossary](../../../../publication/knotlab/INTUITIONS.md#glossary).

## Gates

The final verdict in [gates.json](gates.json) is `passed: true`. Its source is
the fresh [gates_checked/results.jsonl](gates_checked/results.jsonl), containing
197 `ok` records, with no error, timeout, memory, or crashed records. The run
finished in 3,951.3 s (65.9 min) with one supervisor, two workers, and at most
one serialized external solver/checker process.

| Check | Coverage | Result |
| --- | --- | --- |
| G-tie | 50 descriptions at N=4: 48 allow states and 2 allow none | Exact agreement with independent plain backtracking; unconstrained completions counted together without omitting any states or pair parities |
| G-reach | All 146 D descriptions, s=1..4: 584 comparisons | Spanning tie classes agree with census `L_N=2`, and threshold-3 decisions agree with census `L_N<=3`; none undecided |
| G-hom | 20 deterministic descriptions at depths 8 to 9; 592 candidate decisions | 92 accepted maps checked on 23,460 knot images; all 500 rejection counterexamples verified by independent plain Python state action, pattern, and map code |
| Size-four control | First half-rate case, top 3, s=3, `k_max=4` | Actual `L_N=4`, with a checked bond and proper-projection states; [threshold4_control.json](threshold4_control.json) passes |
| Retention failure controls | Checker rejection, expiration during retention, disagreeing orphan gzip bytes, and persistent cache hash mismatch | All four pass; no failed refutation is consumed; see [retention_controls.json](retention_controls.json) |
| Retained-certificate audit | All 3,073 pairs possibly affected by the earlier overlap | Every raw-content hash and LRAT replay passes; no failures or runner errors in [certificate_audit.json](certificate_audit.json) |

Each case records a source manifest saved before workers fork. The final gate
execution manifest is
`source_manifests/2c10b54eae26d934125d4d63e4d8b768f9a1e7836c1222123d39ec1255dba26a.json`.
`gates.json` keeps this execution provenance separate from its later
`inspection_provenance`. While the final gates ran, changes were limited to
production U result reuse, smoke-panel wiring, and the summary script; the
tie, reach, retention, and homomorphism core used by those gates did not change.

### Execution incident and recovery

The first foreground execution survived a tool-session interruption. Starting
the replacement therefore left two owned gate supervisors running at once,
exceeding the requested process cap. This was an execution error. Their case
scratch paths also coincided. Exactly one case had overlapping intervals:
`57d2b6f04b592efbd9e5a32649dd70ab2361151f2dd20b37bf1bfd2bb0c1674c`;
one run completed it and the other received `FileNotFoundError`. No census
disagreement was observed in that error.

Both earlier runs were verified terminal through their own saved runner state
before the fresh gate run.
Their records are retained in `gates_run/` and `gates_run_final/`, but they are
not the final gate evidence. The deliberate error barrier and scratch were
preserved in `interrupted_runs/`;
`restart_collision.json`, `overlapping_gate_cases.json`, and
`affected_certificates.json` record the recovery. The completed audit above
checks all 3,073 possibly affected retained CNF/LRAT pairs. The fresh final run
repeated all 50 tie cases, all 146 D reach cases, and G-hom under one supervisor
with two workers, restoring the four-process compute limit.

Gate scratch now has a run-specific directory, production scratch has a
separate directory, and the shared certificate lock has its own directory.
Atomic temporary names use random identifiers rather than namespace-local
PIDs. Certification also verifies that its input CNF bytes remain unchanged
before and after proof generation/checking.

The long case `57d2b6f04b59...` completed afresh in 2,098.9 s; 2,070.4 s was
sampling. No cached-result replacement was needed. The recovery-job draft is
retained, unused, at `interrupted_runs/unused_recover_gate_job.py`, with
`unused_recovery_note.json` stating that it was never imported or run.
The retention controls' real solver/checker evidence and labeled failure
fixtures remain in `retention_controls.json` and `retention_control_fixtures/`.

## Smoke and estimates

The smoke uses `smoke_job.py -> job.run`, the same implementation as the full
jobs. The specified ten cases are the first nine D cases and the first U case,
then sorted by full case identifier. This selection covers two constant-2,
five constant-3, and two half-rate D descriptions, both requested top bounds,
and the U continuation path. It is a coverage panel, not a random timing
sample. Raw records are in [smoke/results.jsonl](smoke/results.jsonl).

Times below are `result.seconds`, rounded to three decimals, and exclude the
runner's small per-case wrapper cost. In the threshold columns, counts are
yes/no for `L_N<=3` and `L_N<=4` across the requested top/s pairs. The size-four
threshold is queried only for half-rate cases. All completed D cells are
decided. Each short identifier links to its complete case record.

| Case | Population/profile | Seconds | Tie seconds | Threshold 3 yes/no | Threshold 4 yes/no | Accepted/candidate maps | N=10/11/12 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| [0195d32248c7](case_results/D/0195d32248c7abfd4cb7d55f298237cc953b862dac87402e5f64d2818c011bb8.json) | D constant-2 | 6.111 | 1.809 | 11/0 | — | 0/12 | alive/alive/alive |
| [08ff6a6d9b37](case_results/D/08ff6a6d9b3738bd60dc00ca113e809091af8207464016445259fc3379e6e030.json) | D constant-2 | 4.639 | 3.544 | 11/0 | — | 0/84 | alive/alive/alive |
| [0e1011a44217](case_results/D/0e1011a442178d666c9429b64e73b1177799029a8e7222991bd59892566998e4.json) | D constant-3 | 8.341 | 0.124 | 11/0 | — | 0/12 | alive/alive/alive |
| [0ef7bddf5068](case_results/D/0ef7bddf506801ee6b9e5d729ed0b7c2c57bfd542a26f54980362a3eeb086198.json) | D constant-3 | 29.552 | 0.141 | 11/0 | — | 0/28 | alive/alive/alive |
| [10a3d1d9be57](case_results/D/10a3d1d9be57cf4219a4e5759dd63a120506c7857c2de8a99a1af49403533fe6.json) | D constant-3 | 0.479 | 0.049 | 11/0 | — | 14/124 | alive/alive/alive |
| [10e63af5c86c](case_results/D/10e63af5c86c9ad3062d9b9f830b13f74997b4b269e35042ac184ed9e2394755.json) | D half-rate | 89.042 | 0.094 | 4/7 | 8/3 | 0/12 | alive/alive/alive |
| [14eecfa49650](case_results/D/14eecfa49650a32c4b699bc273c4ea9d59dc9fec734d03f6d39d4dbcbbbcb2d4.json) | D constant-3 | 17.126 | 0.098 | 11/0 | — | 0/28 | alive/alive/alive |
| [169a421ffaaf](case_results/D/169a421ffaaf0239acc2b8a0f5ea0298beefcf9a0b4f85248d1dbd96ec22f982.json) | D half-rate | 95.356 | 0.133 | 4/7 | 8/3 | 0/52 | alive/alive/alive |
| [17077291124f](case_results/D/17077291124f474905cadf34c81d42ce129ac178ebe438de1cce826a24e67929.json) | D constant-3 | 5.848 | 0.089 | 11/0 | — | 0/12 | alive/alive/alive |
| [00a344d3f150](case_results/U/00a344d3f150db37014b0d13d3ca12acf65eee4350350df05052e6df304ce805.json) | U bounded E_R | 2707.187 | 0.089 | 2/6 (+3 undecided) | — | 0/52 | alive/alive/alive |

The nine D cases total 256.495 case-seconds. Their 99 threshold-3 answers are
85 yes and 14 no; their 22 threshold-4 answers are 16 yes and 6 no. All 27
life checks allow total states checked against every stored knot: these
patterns are still bases at those finite horizons. The smoke is complete: ten `ok` records, no error, runner-timeout, memory,
or crashed records, and an empty in-flight set. Its final peak worker-group
memory was 646.25 MiB. [smoke_summary.json](smoke_summary.json)
contains the phase timings, decisions, estimates, and source checks.

The U case took **2707.187 s (45.1 min)**. Its threshold stage
took 902.400 s: 2 yes, 6 no, and 3 undecided threshold-3
answers. The undecided pairs are top 3 at s=3, 4, and 5; top 2 has no
undecided pairs. Its N=10, 11, and 12 unions all allow checked states.

Only the three originally undecided census cells received continuation
queries; none was resolved through step 1/2 reuse in this case:

| Top 3, s | Census `L_N` | Continuation seconds | Answer |
| --- | --- | ---: | --- |
| 2 | undecided | 4.556 | `L_N=4`; bond `[14, 29, 33, 50]` |
| 3 | undecided | 900.052 | undecided |
| 4 | undecided | 900.009 | undecided |

These continuations took 1804.632 s in total. The new s=5
threshold uncertainty receives no 900 s continuation because it was not a
census cell. The ten cases reference 2,439 distinct checked
refutations; every referenced CNF/LRAT gzip path exists and is named by its
CNF SHA-256. No incomplete-certification attempts were recorded. The supplied
source files and census hashes are unchanged, and the smoke's source hashes
match its saved pre-fork manifest.

### Hypothetical six-worker planning estimate

Six workers were not tested or launched: the actual compute limit is four
processes, met by the two-worker configurations below. This calculation is a
rough planning estimate, not a measured six-worker runtime or a runtime bound.
The smoke reused checked certificate storage populated by the gates; it does
not measure a cold certificate store.

For each D description i, use its measured final-gate tie time and the mean
non-tie smoke time for the same census profile:

`T_i = gate_i.ties.seconds + mean_profile(smoke.result.seconds - smoke.ties.seconds)`.

| D profile | Population | Completed smoke cases | Mean non-tie seconds | Mean newly executed serialized solver/checker seconds |
| --- | ---: | ---: | ---: | ---: |
| constant-2 | 34 | 2 | 2.698 | 0.013 |
| constant-3 | 66 | 5 | 12.169 | 1.281 |
| half-rate | 46 | 2 | 92.086 | 36.622 |

Across all 146 measured gate tie times, the sum is 3,769.492 s. The projected
sum of `T_i` is 8,900.332 s, giving 1,483.389 s if divided ideally among six
workers. The longest projected case is 2,099.770 s, and scaling the observed
new serialized external work by the same profile counts gives 1,769.574 s.
Thus `max(sum(T_i)/6, max(T_i), scaled serialized external seconds)` is
**2,099.770 s, about 35.0 min**. The observed 35-minute sampling case is a
planning floor if that behavior repeats. More difficult extension queries,
certificate work without cache reuse, lock waiting, and the small coverage
panel can all increase elapsed time. The authorized two-worker launch does
not acquire six-worker throughput from this estimate.

For U, the measured per-description time excluding continuations is
`B = 902.556 s`. Continuation costs are stratified by s,
using the exact counts of the census's 215 undecided cells:

| s | Originally undecided U cells | Continuation seconds charged per cell |
| --- | ---: | ---: |
| 1 | 1 | 900.000 (unmeasured; full budget assumed) |
| 2 | 43 | 4.556 (measured) |
| 3 | 83 | 900.052 (measured) |
| 4 | 88 | 900.009 (measured) |

Estimate each U description by B plus these costs for its originally undecided
cells. The projected work totals 234,425.847 s;
`sum(T_i)/6 = 39,070.974 s`. The longest projected case is
3,607.172 s and the scaled newly executed serialized external
work is 1.424 s. Their maximum gives
**10.9 hours at six hypothetical workers**.

| Population | Six-worker planning estimate | Measurement basis |
| --- | ---: | --- |
| D (146) | about 35 min | All 146 gate tie times plus profile-stratified non-tie times from nine smoke cases |
| U (88) | about 10.9 h | One full U smoke case and the exact undecided-cell counts by s |

The U estimate has only one measured description; s=1 continuation is
unmeasured and charged its full 900 s budget. Other descriptions, unbudgeted
tie work, cache state, and contention can change runtime. Both estimates
assume enough parallel CPU capacity and are planning calculations, not tested
six-worker performance. The actual commands below remain at two workers.

## Commands used

Run from `/home/jscul/p-vs-np-contact-first`. The following records the final
gate and current smoke invocations; `launch --prepare-only` wrote their
configuration without starting a service. The earlier interrupted runs remain
available under the paths documented above.

```bash
DIRECT_REACH_CODEX=experiments/DIRECT-REACH-20261115-001A/DIRECT-REACH-20261115-001A-E001_direct_reach/codex

.venv/bin/python -B "$DIRECT_REACH_CODEX/retention_controls.py"
.venv/bin/python -B scripts/longrun.py launch "$DIRECT_REACH_CODEX/certificate_audit_job.py" \
  --out "$DIRECT_REACH_CODEX/certificate_audit" --unit direct-reach-001a-certificate-audit \
  --workers 2 --case-mem 1G --mem-max 4G --prepare-only
.venv/bin/python -B scripts/longrun.py run --out "$DIRECT_REACH_CODEX/certificate_audit" --foreground

.venv/bin/python -B scripts/longrun.py launch "$DIRECT_REACH_CODEX/gate_job.py" \
  --out "$DIRECT_REACH_CODEX/gates_checked" --unit direct-reach-001a-gates-checked \
  --workers 2 --case-mem 3G --mem-max 7G --param run_tag=checked --prepare-only
.venv/bin/python -B scripts/longrun.py run --out "$DIRECT_REACH_CODEX/gates_checked" --foreground
.venv/bin/python -B "$DIRECT_REACH_CODEX/gates.py"

.venv/bin/python -B scripts/longrun.py launch "$DIRECT_REACH_CODEX/smoke_job.py" \
  --out "$DIRECT_REACH_CODEX/smoke" --unit direct-reach-001a-smoke \
  --workers 2 --case-mem 3G --mem-max 7G --prepare-only
.venv/bin/python -B scripts/longrun.py run --out "$DIRECT_REACH_CODEX/smoke" --foreground --limit 10
```

## Launch commands

These are commands for the thread's full population runs. They have **not**
been executed by this task. Run one
population at a time, waiting for D to terminate before launching U. Use
fresh output directories; do not add `--register`, which would write outside
CODEX and commit tracking state.

```bash
DIRECT_REACH_CODEX=experiments/DIRECT-REACH-20261115-001A/DIRECT-REACH-20261115-001A-E001_direct_reach/codex

# Full D only; wait for termination before the separate U command.
.venv/bin/python -B scripts/longrun.py launch "$DIRECT_REACH_CODEX/job.py" \
  --out "$DIRECT_REACH_CODEX/full_D" --unit direct-reach-001a-full-d \
  --workers 2 --case-mem 3G --mem-max 7G --param pop=D

# Full U only, after D has terminated.
.venv/bin/python -B scripts/longrun.py launch "$DIRECT_REACH_CODEX/job.py" \
  --out "$DIRECT_REACH_CODEX/full_U" --unit direct-reach-001a-full-u \
  --workers 2 --case-mem 3G --mem-max 7G --param pop=U
```

The actual configurations use two workers and a shared lock serializing all
external SAT/checker processes: one supervisor + two workers + one external
process = four. `--case-mem 3G --mem-max 7G` stays below 8 GB. NumPy/BLAS
threads are restricted to one. Foreground execution uses the runner's worker
memory monitoring; aggregate cgroup enforcement applies to later service runs.

## Ambiguities

- The approximate D count is 145 in the specification; its exact stated
  predicate selects 146 in the supplied census. The exact predicate is used.
- Upstream `compute` has no `k_max` argument and hardcodes 10. The local guarded
  adaptation exposes the requested setting without editing the census source.
- The six-worker estimate is hypothetical because the execution rule permits
  at most four processes. Actual gate/smoke/full-run commands use two workers.
- U selection and G-reach use census `L_N` (unrestricted bond support), rather
  than the different `L_target` observable. This gives the specified 88 U cases.
- The map set contains `4*(1+s+s*s)` syntactic candidates: prefix/suffix,
  c=0/1, and identity, single states, or ordinary state pairs. The word acts
  first, right to left; prefix adds c as the most significant bit and suffix
  as the least significant bit. Bare maps and empty-word composites are listed
  once; nonempty words are retained separately even if their actions coincide.
- One inherited timeout reason says `300-second search budget exhausted`
  for the U s=4 continuation. That text is inaccurate for this call: its
  recorded configured budget is 900 s and its elapsed time is 900.009 s.
  The reason text is excluded from budget interpretation; the raw record is
  preserved and the answer remains undecided.
- The smoke panel was unspecified. The chosen nine D plus one U cases cover
  all D profiles and both threshold bounds while exercising U continuation.
- Tie classes represent all pairs through a signed certificate forest;
  explicitly storing a proof for every pair would duplicate consequences of
  the same checked equalities/inequalities. G-tie's independent exact
  backtracking groups unconstrained completions while counting all of them.

No affected computation is skipped by these resolved input/API readings.
All requested gates, ten smoke cases, estimates, and commands are recorded.
The full population jobs remain for the thread.
