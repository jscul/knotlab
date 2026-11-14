# CARRY-BOUND window jobs: Codex handoff

Scope: ticket `CARRY-BOUND-20261114-001A`. This is implementation and gate evidence for the frozen
[preregistration](../../../../research/CARRY-BOUND-20261114-001/preregistration.md), not a population result.
Every write in this session is confined to this CODEX directory. No Git mutation, publication,
tracker registration, population run, or P1–P5 evaluation is authorized or performed here.

Scientific interface: deterministic code analysis of one canonical family key per window case;
outputs are exact finite window projections, eventually periodic upper-bound certificates,
and the specified algebraic growth certificates. The comparisons are the prior census tables,
independent CNF projections, minimality rechecks, and the declared controls. Completion here
means the jobs and sample/summary consumers are built, gates are recorded, configurations are
prepared, and a 20-case window smoke is retained. It does not mean the population hypotheses
have been tested, that a missing upper bound is a growth proof, or that an experiment establishes
a theorem. No new goal, direction, term, canonical definition, or research artifact is adopted.

## What was built

- `inputs.py`: read-only reuse of the census results, original family archive, draw weights,
  FREE-TARGET relations, EVERY-RAY machinery, and TIE-CYCLE classifier. Inputs are not copied.
- `scope.py`: the two scope exclusions, identity cycle, and I/T/O/X classification.
- `window.py`: living and relation checks; the joint relation and identity partition; exact
  allowed window states; all tied least minimal non-shattered sets through size 6; Q_s repetition
  with the 200,000-state and 2,000-level caps; U and residue readings; syntactic B; literal
  least-fixed-point dead positions; G and trimmed G2, including the live quotient.
- `job_window.py`: one shared-runner case per family, with gate a/b/e in each result.
- `brute.py`: separate explicit CNF unfolding, independently reconstructed usual limits and
  identity merging, SAT projection, and support/deletion rechecks. It imports no window code.
- `gates.py`: scope comparisons, four synthetic controls, 300 negative controls, 50 I families,
  seeded selection and rechecking of 200 recorded least bonds, and `gates.json` aggregation.
- `sample.py`, `job_paths.py`: post-census frozen sampling and the unchanged EVERY-RAY per-family
  entry point. No sample is selected before the full census results exist.
- `direct.py`, `job_direct.py`: the reused independent direct search, all covered targets at
  absolute depths 1 through 6, and all members in the unfolding through s+2. Finite exclusions,
  verified upper bounds, and caps have separate output labels; no finite reading proves growth.
- `summarize.py`: population analysis for the thread, including count/draw shares, Wilson
  intervals, sensitivity and missing-result cells, out-of-scope results, and T family readings.
  It refuses incomplete population inputs. Codex does not invoke its prediction analysis.

Canonical window symbols are main ports `0..k-1` followed by symbols `k+v` for end-block
distinction v, with each identical distinction represented by its first symbol. Equal values
without shared identity remain different variables. All tied least supports are retained rather
than selecting one bond type. `"> 6"` is the prescribed search-limit marker, not an exclusion of
larger bonds. G2 needs the complete reachable context set; a Q_s cap cannot certify it.

## Gates and smoke

**The gates do not all pass.** No full run was launched. Machine-readable evidence is in
`gates.json`, `smoke_gates.json`, the runner directories, and `smoke_metrics.json`.

| Check | Recorded result |
| --- | --- |
| Scope predicates | Passed: all published inventory count tables and all 657 directly recorded own-distinction predicates match; all certified delayed-S count cells match. |
| a: living and per-call tables | 369 recorded checks passed; zero empty living checks or census-table mismatches. Counts are checks, with overlap between the gate and smoke selections. |
| b: B-covered residues | No violation in 358 available checks. Eleven checks lack a completed window because of ambiguous starts or a cap; the aggregate is partial, not passed. |
| c: 300 forgetting controls | 293 passed. All computed lower-bound comparisons passed. Six starts were skipped for A1; one original G2 search has no certificate through r=8 (census r=11, A7). The companion quotient results are recorded separately below. |
| d: explicit projection | 2,314 word projections matched for 45 of the prescribed first 50 I families, with zero mismatches. Four multi-entry wrappers and one wrapper with the depth ambiguity were skipped, retaining their selected places. |
| d: minimality recheck | All 200 passed, drawn without replacement from 6,471 recorded least bonds using `random.Random(20261114)`. Every tested support is non-shattered and every one-member deletion is shattered. |
| e: incompatible certificates | 369 recorded checks passed; no simultaneous full window bound and growth certificate. |

| Synthetic control | Result |
| --- | --- |
| Carried pendant knot | Passed: U(0)=U(1)=3, then period 1. |
| Carriage in port-only knots | Passed: `"> 6"` at both computed levels, then period 1. |
| Identity carriage at a constraint-free coordinate | Failed the required G certification under the stated least fixed point (A2). U(0)=3 and all repeating U are `"> 6"`; no false eventual window bound is recorded. |
| Forgetting | Passed: U=3,4,`"> 6"`; original G2 certifies at r=2 and live-quotient G2 at r=1. |

The companion `gate_negative_live/` run completed all 300 cases with `ok` runner records; 293 live-quotient G2 certificates were found. It reuses saved window contexts and recomputes only the prescribed literal reduction and G2 length tests. The same six starts are skipped; the r=11 case still has no certificate through r=8. No additional population window case was run.

The family-gate run has 355 `ok` runner records, 478.29 seconds of summed case time, and a
253.04 MiB maximum runner case peak. Its independent-projection portion accounts for 465.36
seconds, including one 268.08-second case. The 200 bond rechecks took 13.76 summed case
seconds, with a 121.13 MiB maximum runner case peak. No gate had a timeout, memory failure,
crash, or runner error in the completed attempts.

The smoke has exactly 20 `ok` cases, 26.94 summed case seconds and 28.04 seconds from runner
start to final heartbeat. Maximum runner case peak: 151.72 MiB; maximum parent-plus-worker
runner peak: 223.85 MiB. One case reaches the prescribed Q_s/product storage caps and two
skip ambiguous wrapper starts. They remain undecided. Gates a and e pass on all 20; b has
17 completed, nonapplicable checks and three unavailable checks, with no observed violation.

| CARRY key prefix | c | Wrapper | Verdict | Seconds | Runner peak MiB | Window RSS MiB |
| --- | ---: | :---: | --- | ---: | ---: | ---: |
| 0001e4875df4 | 2 | yes | undecided | 0.092026 | 56.54 | 94.80 |
| 0008564c9ad7 | 5 | no | bounded | 0.075342 | 58.15 | 96.30 |
| 001b38fb4521 | 2 | no | undecided | 0.009927 | 58.27 | 96.33 |
| 001ddeb65496 | 2 | no | bounded | 0.305035 | 62.83 | 96.86 |
| 00202e31b0eb | 3 | no | undecided | 24.408694 | 151.72 | 168.60 |
| 00415487c940 | 2 | no | undecided | 0.094188 | 143.49 | 167.09 |
| 0046f8341e18 | 2 | no | bounded | 0.021412 | 134.83 | 133.94 |
| 0049d81dd3eb | 2 | no | bounded | 0.057974 | 134.83 | 133.95 |
| 004bcd84d820 | 2 | no | bounded | 0.075945 | 134.83 | 133.95 |
| 007282c55f6c | 4 | no | bounded | 0.456254 | 134.83 | 133.95 |
| 007b58da377d | 4 | no | bounded | 0.072323 | 134.83 | 132.95 |
| 007d596a4084 | 2 | no | bounded | 0.193043 | 134.83 | 132.95 |
| 0080c1c03e47 | 2 | no | bounded | 0.080883 | 134.83 | 132.95 |
| 00958d5b001b | 2 | yes | undecided | 0.001293 | 134.83 | 132.95 |
| 009607149c9c | 2 | no | bounded | 0.084839 | 134.83 | 132.95 |
| 0099db2328d2 | 3 | no | undecided | 0.115247 | 134.83 | 132.95 |
| 00a1e2eb9913 | 3 | no | bounded | 0.116174 | 134.83 | 132.95 |
| 00a25bdfff5d | 2 | no | bounded | 0.025693 | 134.83 | 132.95 |
| 00a56113e7dc | 2 | no | bounded | 0.123559 | 134.83 | 132.95 |
| 00b5f28a7b90 | 3 | no | bounded | 0.528345 | 134.83 | 132.95 |

Case identifiers in the table are the first 12 characters of `sha256("CARRY:" + key)`. Full keys and
exact metrics are in `smoke_metrics.json`. Memory is MiB. The runner's high-water component
can retain an earlier case's allocation in the reused worker; the second memory column is
the window's current-case RSS checkpoint maximum. Neither column claims isolated-process
memory for each family.

The initial `gate_families/` attempt stopped during case generation because the lightweight
scope preparation omitted its inlined-own counts. That implementation error was repaired;
the failed attempt is retained, and the gate rerun uses `gate_families_v2/`.

Experiment execution uses one shared-runner worker, hence two compute processes including the
runner parent. The initial read-only inspection mistakenly batched five short command calls,
exceeding the requested two-process limit for that inspection. Subsequent command lanes were
serialized, and no other command ran alongside a shared-runner parent and worker.
Per case: 600 seconds, 3 GiB outer memory limit; window checkpoints use
585 seconds and 2.8 GB RSS. The foreground configuration reserves 4 GiB for parent plus worker.
Gate output, manifests, logs, smoke results, and frozen job configurations remain in CODEX.
All retained runner output is validation evidence, including the failed setup attempt and
capped/ambiguous results; it is not disposable scratch. Existing `last_message.md` is untouched.

Source snapshots: `source_manifest_smoke.json` binds the 20-case smoke. A final metadata fix
restricts a tie reading to main ports actually in the candidate bond; it changes no allowed set,
bond minimum, Q_s state, or certificate. That fix passed syntax checks and is in
`source_manifest_before_negative_live.json`. The final `source_manifest.json` additionally
includes the completed negative-control quotient logging and companion job. Per-residue
nonexclusive witness readings were added after the family gates and are exercised by the smoke.
No population prediction or post-smoke population window case was computed.

## Commands for the thread

Run from `/home/jscul/p-vs-np-contact-first`, using `.venv/bin/python -B` throughout.
The `window_full/`, `paths_full/`, and `direct_full/` configurations have already been prepared
with `launch --prepare-only`. Each has 3 workers, 600 seconds and 3 GiB per case, and
`MemoryMax=12G`. They have no results or launched service. No automatic retry policy is selected
pending A8. The separate `smoke/` configuration has one worker and `MemoryMax=4G`.

After the thread resolves the failed gates and affected ambiguities, these are the exact
service-start and analysis commands. They are supplied for the thread, not executed by Codex:

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

If a frozen list is empty, its job simply has no cases. After each service starts, the runner
prints its UTC `track.py long-add` command; the thread fills its run identity and description
and registers runs expected to exceed ten minutes. Registration is deferred because it writes
outside CODEX. `sample.py` writes the path list before paths run; its direct stage preserves
that exact earlier sample and extends it only after every path result exists. The final
summary invocation is the thread's single population P1–P5 reading; P3 remains explicitly
skipped until A4 is answered. No `sample.json` or population `summary.json` exists at handoff.

The preparation actually performed for each full job was:

```bash
.venv/bin/python -B scripts/longrun.py launch "$CARRY_CODEX/job_window.py" \
  --out "$CARRY_CODEX/window_full" --unit carry-window-full \
  --workers 3 --case-timeout 600 --case-mem 3G --mem-max 12G --prepare-only
.venv/bin/python -B scripts/longrun.py launch "$CARRY_CODEX/job_paths.py" \
  --out "$CARRY_CODEX/paths_full" --unit carry-window-paths \
  --workers 3 --case-timeout 600 --case-mem 3G --mem-max 12G --prepare-only
.venv/bin/python -B scripts/longrun.py launch "$CARRY_CODEX/job_direct.py" \
  --out "$CARRY_CODEX/direct_full" --unit carry-window-direct \
  --workers 3 --case-timeout 600 --case-mem 3G --mem-max 12G --prepare-only
```

Gate aggregation and the smoke-only check (no P1–P5) are reproducible with:

```bash
.venv/bin/python -B "$CARRY_CODEX/gates.py" summarize \
  --families "$CARRY_CODEX/gate_families_v2" --bonds "$CARRY_CODEX/gate_bonds" \
  --negative-live "$CARRY_CODEX/gate_negative_live" --smoke "$CARRY_CODEX/smoke"
.venv/bin/python -B "$CARRY_CODEX/summarize.py" \
  --window "$CARRY_CODEX/smoke" --check-gates --output smoke_gates.json
```

## Ambiguities

1. **A1 — multiple wrapper entries.** Which S-call should be chosen when a wrapper main has
   more than one direct S-call? Step 2 says a chosen call and step 3 says Q_0 has one start,
   while the objective permits every covered target. No entry is selected silently. For these
   families, the window and context-dependent G2 are skipped; independent basics and G remain
   computable. No union of starts is substituted for the specified singleton.
2. **A2 — dead-position fixed point and the required control.** Should the dead-position rule
   use the stated least fixed point, or another rule for constraint-free self-carriage? A port
   occurring only at the same position of its SELF call cannot enter the least fixed point from
   the empty set, although it occurs in no constraint at any finite unfolding. Thus the literal
   rule retains it and cannot meet the specified dead-carriage synthetic G certificate. The
   code computes the stated least fixed point and records the synthetic failure; no repair is
   adopted. G2 on that unchanged quotient is also retained as computed.
3. **A3 — wrapper depth in the independent gate.** Is s in gate d a SELF-word length from the
   top S copy, or the absolute depth used by FREE-TARGET? They agree for main=S; a wrapper's
   end copy for a word of length s is at absolute depth s+1. The explicit unfolding also needs
   a convention for whether the frontier at s+1 is included or replaced by its limit. Wrapper
   comparisons are skipped until that convention is selected. Their place in the prescribed
   first-50 selection is retained, rather than replaced by another family.
4. **A4 — P3 with multiple unbounded residues.** Does a family satisfy P3 when *some*, or
   *every*, residue lacking a window bound has no carried position sharing a knot with an own
   distinction? The frozen prose says “on that residue.” The code retains every residue's
   carried and knot-meeting flags, and the summarizer skips the P3 scalar pending this answer.
5. **A5 — incomplete sample cells.** How should an I family whose cap or ambiguous start
   prevents a carried-period/unbounded-residue cell be sampled? The selector records the
   missing cell and skips only that family's cell selection. Likewise it retains failed runner
   records whose scope or stratum is unavailable, without assigning them from another source.
6. **A6 — overlapping or tied bond readings.** A B witness also meets the literal widened-B
   description, and tied smallest supports can have different readings. All tied supports and
   their Boolean features are retained. Which exclusive attribution, if any, is intended for
   a single B/widened-B share? The code does not select an exclusive attribution.
7. **A7 — negative control with r=11.** Should gate c's G2 requirement extend beyond the
   stated r=1..8 search? One of the prescribed 300 negative controls has census r=11 and
   receives no G2 certificate through 8. The lower-bound comparisons pass; the required G2
   certification does not. Its search is not extended silently.
8. **A8 — one retry.** How should the preregistration's one retry be expressed with the
   unchanged shared runner? `longrun.py` makes selected failures final on attempt 3, so
   `--retry timeout,memory` permits two retries. There is no maximum-attempts option. Prepared
   full configurations leave automatic retry selection unset; the one-retry part is deferred.
   No custom retry loop or shared-runner edit is introduced.

These questions are implementation handoff questions, not changes to the frozen mathematics,
the canonical knot test, or the glossary's meanings.
