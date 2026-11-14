# FREE-TARGET-20261114-001A: computation record

Scope: `scope_kind: ticket`, `scope_id: FREE-TARGET-20261114-001A`.
This session prepares the shared-runner job and stops after gates and a
20-case foreground smoke. The full run has not been launched.

## Population and inputs

`population.json` freezes exactly **66** unique keys, in lexicographic key
order, with `c`, `lambda_path`, `L_path`, source row selection, and the SHA-256
digests of `G.jsonl` and `phase2.jsonl`. Rows of the latter replace matching
rows of the former before the `class_path == "grows"` filter. The prescribed
`paths_dp.py` and its census `reach_dp.Preparation` supply the usual limit,
limit relations, flattened bodies, `S`, and call arguments. `setup()` streams
the census archive and retains its records for the 66 frozen keys.

No tracker, ticket, source outside this directory, Git state, or publication
file is changed by this task. Existing `.keep`, `codex_exec_sol.log`, and
`last_message.md` are not task-owned outputs and are left alone.

## Computation and gates

Each per-call relation is a 64-bit Boolean matrix. Bit `8*a+b` denotes parent
port state `a` and child port state `b`, with slot zero the least significant
bit within each three-port state. All SELF calls, including literal duplicate
calls, retain their separate call labels. The selected onward call is omitted
from its block's constraints; every other holding call uses its exact `G`.

`relations.py` iterates the complete sets `P_n` until a set repeats, records the
least all-rectangular length, and checks rectangularity throughout the repeat.
Otherwise it records a reachable cycle in the non-rectangular product graph
as call-index prefix and cycle. `independent.py` uses fresh tuple enumeration
of the flattened block and set-valued Boolean products, with no import of the
production relation or semigroup code.

The relation gate covers all 66 families and all **161** labelled SELF calls.
It found zero relation or product mismatches. There are 43 finite `r` records
and 23 recurring-word records. The `r` counts are: 2: 9, 3: 14, 4: 6,
5: 9, 6: 5. These are gate computations, not a full run of the per-family job.

The small synthetic controls check 260 products on one- and two-state
relations, all 136 unordered pairs of two-state generators, and named controls
for a proper product, a second-power product, an identity relation, and the
empty relation. They pass with no mismatches.

The final mutant panel drops the **last** flat SELF call's side relation in
the first ten frozen families, leaving it omitted already when it is itself
the onward call. It changes one family's `R_i`, with no independent-check
mismatch. The initially tried **first**-call panel on those same ten families
changes none; both panels are retained in `mutants.json` and
`mutants_last_call.json`. The subsequent sensitivity diagnostic on the four
non-TOP `G[S]` families is retained in `mutant_diagnostics.json`; it examined
every possible single SELF side-relation omission in those four families.
The user specification permits either a verdict change or an `R_i` change;
the latter is the recorded mutant observable.

`bounded.py` computes a least closure of exact marked port tables and a
call-labelled finite graph whose states retain full and one-forgotten
boundary-mask families and the member count. Its subset construction searches
for an eventually periodic path with acceptance at every cycle step. Budgets
3, 4, and 5 are attempted in order. Arbitrary side members and members beyond
the target are represented by finite marked-table witness constructions.
Actual argument identities are substituted; incoming ports are never marked
again as fresh variables. Retained certificates contain the operations and
profile witnesses needed to reconstruct concrete member placements.

All three bounded-search positive controls pass: persistent top identity,
repeated child port identity, and a carried top identity requiring a side
member. Their independent SAT replays check depths 1, 2, and 3, for nine
concrete support checks in total. Each checks nonempty non-shatteredness,
every one-forgotten subset, and the two endpoint requirements. The side-member
control verifies both side support and a carried top identity. Results and
concrete member locations are retained in `bounded_controls.json`.

The shared-runner smoke finishes **20 cases**, all with runner status `ok`:

| Verdict | Count |
| --- | ---: |
| grows | 11 |
| bounded | 0 |
| unresolved | 9 |

The unresolved reasons are `no certificate at k <= 5` for eight cases and
`ambiguity` for one. Five of the 20 cases skip the bounded search because
main differs from `S`; the other 15 complete all three fixed budgets, yielding
45 completed no-certificate budget attempts. None reaches a resource cap.
The 46 unrun keys remain pending and are not labelled unresolved.

`gates.json` contains every gate and every mismatch list. Gate (a) passes on
all 66 families. Gate (b) has zero population bounded certificates to replay
in the smoke; its three synthetic positive controls do exercise the SAT
checker. Gate (c) checks all 20 smoke records and finds no family certified
both ways. Gate (d) passes through the recorded `R_i` change. Synthetic
relation and bounded-search controls pass. There are no mismatches or invalid
smoke records. This gate coverage is limited to the stated records and
controls; the full per-family job has not run on the remaining 46 keys.

The smoke's `summary.json` uses the requested denominator 66 and Wilson 95%
intervals: grows 11/66 [0.095696, 0.274306], bounded 0/66
[0, 0.055003], unresolved 9/66 [0.073433, 0.239296]. Its pending count is 46.
`gate_r_against_lambda_path.json` also retains the 43 relation-gate `r` rows
against their supplied path rates, separately from the 20 smoke records.

## Runner commands

All commands are run from `/home/jscul/p-vs-np-contact-first` with the repository
interpreter and bytecode disabled. The local smoke has one runner parent
and one worker, rather than two workers, to satisfy the session limit of two
processes and about 8 GB total. Its output stays in `codex/smoke/`.

The executed preparation and smoke commands are:

```sh
.venv/bin/python -B scripts/longrun.py launch \
  experiments/FREE-TARGET-20261114-001A/FREE-TARGET-20261114-001A-E001_free_target/codex/job.py \
  --out experiments/FREE-TARGET-20261114-001A/FREE-TARGET-20261114-001A-E001_free_target/codex/smoke \
  --unit free-target-20261114-001a-smoke \
  --workers 1 --case-mem 7G --mem-max 8G --case-timeout 1800 \
  --retry timeout,memory --runtime-max 20h --prepare-only
.venv/bin/python -B scripts/longrun.py run \
  --out experiments/FREE-TARGET-20261114-001A/FREE-TARGET-20261114-001A-E001_free_target/codex/smoke \
  --foreground --limit 20
```

`inputs.py` created the population freeze. `gates.py --recompute-relations`
ran the relation and synthetic controls before the smoke. `bounded.controls`
ran the three positive controls, with 150 s and 900,000,000-byte internal
control ceilings. `freeze_sources.py` then froze 25 code/input/document
digests, the interpreter path, and package versions in `source_manifest.json`.
`summarize.py .../codex/smoke` generated the smoke summary and final gate
aggregation after the runner stopped. All 25 source/input hashes were checked
again after execution and still match. No bytecode cache was generated.

The exact full-run command for the thread is:

```sh
.venv/bin/python -B scripts/longrun.py launch \
  experiments/FREE-TARGET-20261114-001A/FREE-TARGET-20261114-001A-E001_free_target/codex/job.py \
  --out experiments/FREE-TARGET-20261114-001A/FREE-TARGET-20261114-001A-E001_free_target/codex/full \
  --unit free-target-20261114-001a-full \
  --workers 2 --case-mem 7G --mem-max 15G --case-timeout 1800 \
  --retry timeout,memory --runtime-max 20h
```

That command has **not** been executed in this session. It intentionally has
no registration flags: registration writes the tracker outside the permitted
CODEX directory. Any thread-owned registration is a separate operation.

For a completed or partial runner directory, the summary command is:

```sh
.venv/bin/python -B experiments/FREE-TARGET-20261114-001A/FREE-TARGET-20261114-001A-E001_free_target/codex/summarize.py \
  experiments/FREE-TARGET-20261114-001A/FREE-TARGET-20261114-001A-E001_free_target/codex/full
```

It writes `summary.json` in that run directory. Wilson 95% intervals use
denominator 66; unrun cases remain a separate `pending_cases` count. It records
`r` against `lambda_path`, bounded witnesses, unresolved reasons, and the gates.

## Timings, memory, and limits

The first complete all-66 relation and independent-product pass took 0.132 s.
The synthetic controls plus first mutant panel took 0.109 s. The retained
relation pass peaks at 41,222,144 RSS bytes; its largest stored-product count
is 35. The largest selected flattened `S` block has 10 distinctions.

The job's cooperative per-case ceilings are 1,650 s and 6,000,000,000 RSS
bytes, inside the thread's 1,800 s and 7G limits. Semigroup storage is capped
at 250,000 stored products and 100,000 length sets. Exhaustion records `cap`
or `memory`; it supplies no negative certificate. The runner handles outer
timeouts, memory enforcement, resumption, and retries.

The bounded search has its own 1,500 s and 5,800,000,000-byte ceilings, in
addition to the enclosing job limits. Its explicit caps are 20,000 marked
profiles, 2,000,000 compositions, 4,096 operations, 30,000 NFA states,
400,000 NFA arcs, 5,000 subset states, and 20,000 subset transitions. Each
base block is limited to 65,536 local assignments, and each image cache to
30,000 entries. These limits are recorded in every bounded-search result.
The SAT checker also has explicit replay, copy, clause, witness-expansion,
and solver-call caps, recorded in its output.

The three bounded-search controls take 0.020154 s with a sampled peak RSS of
26,402,816 bytes. The smoke runs from 2026-11-14 00:02:24.337 UTC through
00:02:37.644 UTC: 13.307 s including setup and runner overhead. Per-case job
times sum to 12.146520 s; runner-recorded case times sum to 12.414756 s.
Individual job times range from 0.001109 s to 4.957918 s. The largest sampled
case RSS is 54,575,104 bytes; the runner's aggregate proportional-memory peak
is 54.224609 MiB, and its final parent RSS is 41.082031 MiB. The runner is
final, has no worker or in-flight case, and reports `complete: false` because
the requested 20-case limit leaves 46 cases pending. No timeout, memory kill,
crash, error, or contradiction occurs. There is no full-run timing or memory
measurement in this session, and the `full/` output directory does not exist.

## Deviations

- The smoke uses one worker and `--mem-max 8G`, within the session resource
  constraint. The full-run command uses the requested two-worker settings.
- No lifecycle, tracker, generated-view, commit, or publication operations run,
  because the user limits writes to CODEX and forbids changing Git state.
- The first-call mutant trial did not change `R_i`; the retained last-call
  trial on the same ten families meets the stated gate. All examined trials
  are preserved rather than discarded.
- The affected skipped bounded searches use an explicit `ambiguity` reason,
  in addition to the three normal unresolved reasons in the specification.
  In the smoke this changes one unresolved reason; the other four skipped
  cases have a forgetting certificate and retain the required `grows` verdict.

## Ambiguities

1. For the nine families with `Preparation.main != Preparation.S`, is target
   depth counted from the entries of the **flattened** main block, as in the
   reused path DP, or from the original derivation including the inlined
   nonholding calls? No depth convention is selected. Only affected bounded
   certificates are skipped; their per-call relations and semigroup tests are
   still computed.
2. The bounded claim begins at an onset, whereas gate (b) requests witness
   checks at **every** depth from 1 through onset plus two periods. Must a
   certificate also supply witnesses before its claimed onset? No weakened
   gate is selected: the implementation requires the literal requested
   replay range, report any missing witness as a mismatch, and withhold a gate
   pass when the ambiguity affects it.

No result interpretation is supplied here.
