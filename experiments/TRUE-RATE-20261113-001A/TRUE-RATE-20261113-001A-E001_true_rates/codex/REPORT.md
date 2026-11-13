# TRUE-RATE implementation and bounded validation

The implementation is written. **The ten-family gate passes: 120/120 reference
values match, with every side table closed and every graph complete.** The
no-side-call control also passes. The five-family smoke run completed two
families exactly and retained finite upper bounds for three others. The full
226-family computation was **not run**.

All task writes are in this CODEX directory. The pre-existing `.keep` and
`last_message.md` were preserved. No ticket, contract, prediction, navigation,
publication record, or Git state was changed by this task. Commands used the
repository's `.venv/bin/python -B`, ran in the foreground, and each finished
within twenty minutes.

## What was written

- `true_rate.py`: import-safe module. Reuses TB's `FamilyDP`, exact `(F,G)`
  summaries, local forgetting, lifting, intersection, projection, pruning,
  and `study_families`. Its streamed generic composition is TB's combination
  without a cost cap. Iteration stops only when neither a new summary nor a
  lower cost appears, or an explicitly reported resource limit intervenes.
  The summary cap stops at the first entry past 200,000.
- The ray-summary graph uses target bases with **every SELF call treated as a
  side call**. A middle transition inserts its current ray summary at the
  first SELF occurrence at cost zero, charging own choices and other side
  choices once. Graph composition enumerates full-environment joins without
  merging intermediate alternatives; projection and minimum-cost merging
  happen after every child has joined. Root acceptance chooses a top port
  and requires `0 in F` and `0 not in G`.
- The depth gate uses **s−1 middle transitions and one root transition**:
  the s steps from C_s to C_0 include the root step. At s=1 the base closes
  directly at C_0. Uniform truncation is the settled depth convention; no
  common-side-height convention was substituted.
- Graph analysis reuses PROVED-RATE's iterative trimming/components and exact
  rational Karp algorithm. Every listed node is base-reachable. Acceptance
  costs are retained for the gate; only their finiteness is used to trim.
  All cyclic trimmed components are analyzed. The old `bounded_all` test is
  discarded. `lambda_true` is a rational string, with rendering
  `lambda_true_float`; neither floating-point comparisons nor cost sentinels
  determine the rate.
- `run_rate.py`: requested append/resume CLI. A recorded index is skipped
  regardless of status. Strict JSONL validation refuses malformed journals
  without appending. Paths must stay inside CODEX. Appends are locked,
  flushed, and fsynced. Three workers means **three total processes**: the
  parent computes one lane and forks two children. It creates no pool or
  resource-tracker process. Children are reaped on completion or interruption.
- `validate_rate.py`: reproducible bounded checks and the conditional depth-7
  diagnostic. `validation.json` retains case results, source hashes, focused
  checks, runner checks, and smoke/resume evidence. `smoke.jsonl` contains
  exactly five family rows.

### Resource handling and partial results

Each runner process has a 2304 MiB address-space ceiling: three processes
budget 6912 MiB, below 8 GiB. Numerical-library thread counts are one. Each
family has a cooperative deadline and an outer alarm with 0.5 seconds grace.
The command ceiling is 1190 seconds; it stops starting new families when
insufficient time remains and leaves them resumable. There are no background
jobs. Deterministic worker lanes can have unequal completion times.

To leave time for a useful fallback, the side-table deadline is 55% of the
family budget, graph construction 88%, and gate/analysis 100%. Earlier
completion passes time forward. A preliminary all-empty-side graph is given
at most `min(3 seconds, 8% of the budget)`. Its exact witnessed bases, arcs,
and accepting costs are retained by minimum-cost union. The later graph pass
must enumerate all bases and re-expand every node using the current side
table before claiming completeness. This changes execution order, not the
uncapped fixed-point target or the final graph.

Every finite partial rate is marked `upper_bound: true`; removing unavailable
constructions can only increase the minimum cycle mean. A null rate means
no rate was established, not a numerical infinity. For an incomplete graph,
`acyclic` and `zero_cycle: false` describe only its listed part. The claim
that bonds eventually stop requires both closure and completeness. A passing
partial gate means agreement only at the available reference depths; it does
not imply graph completeness. All differing depths are retained, including
missing witnesses in a partial graph.

`peak_mb` is process high-water RSS in MiB. A worker serving several families
can inherit a previous family's high-water value; `peak_scope` records this.
It is a conservative resource measurement, not a reset per-family peak.

## Validation

### Ten closed and complete families

Fixtures were chosen for low computational cost among the completed TB
records, ordered by own count, reference table size, SELF count, and index.
They are not a representative population sample. Each row checks all twelve
nonnull reference depths. No mismatch occurred, and every row completed its
Karp analysis. None has a zero-weight trimmed cycle.

| Family | Side summaries | Graph nodes | Trimmed nodes | Exact λ_true | Seconds |
|---:|---:|---:|---:|---:|---:|
| 429 | 7 | 6 | 2 | 1 | 0.040 |
| 212 | 15 | 15 | 3 | 1/3 | 0.192 |
| 105 | 15 | 15 | 3 | 1/3 | 0.365 |
| 470 | 15 | 15 | 3 | 1/3 | 0.223 |
| 549 | 15 | 15 | 3 | 1/3 | 0.355 |
| 973 | 15 | 15 | 3 | 1/3 | 0.436 |
| 441 | 15 | 12 | 1 | 1 | 0.260 |
| 989 | 15 | 14 | 2 | 1/2 | 0.397 |
| 1311 | 15 | 14 | 2 | 1/2 | 0.424 |
| 774 | 15 | 14 | 3 | 1/2 | 0.581 |

### No-side-call control

No original study family has just one SELF call. An in-memory copy of family
429 kept its first SELF and removed all subsequent SELF calls, preserving its
two own distinctions and K call:

```text
(3, 2, [('SELF', (3,4,2)), ('K', (0,4,3))])
```

This new definition is not an original study member, so its original
`rates_all.jsonl` row would be an invalid comparator. The independent BD ray
DP, through PROVED-RATE's `ray_dp.py`, instead constructs its full graph
(59 nodes). Its exact minimum cycle mean is **1**, equal to the new
implementation's **1** (closed table, complete three-node graph). Both give
`L(1..12) = [4,5,6,7,8,9,10,11,12,13,14,15]`.

### Conditional four-family diagnostic

The following are the four rows with a recorded deficit of 3 **at s=7**;
their identification as the requested four remains unresolved under the
wording discussed in Ambiguities. Each used a 30-second family budget.

| Family | λ_true bound from listed graph | Reference λ_ray | Table closed | Graph complete | Seconds | Worker peak MiB |
|---:|---:|---:|:---:|:---:|---:|---:|
| 269 | ≤ 1/2 | 1/2 | no | no | 26.929 | 1539.434 |
| 302 | ≤ 1/2 | 1/2 | no | no | 26.872 | 1714.309 |
| 642 | ≤ 1/2 | 1/2 | no | no | 26.918 | 2190.367 |
| 908 | ≤ 1/2 | 1/2 | no | no | 26.766 | 2190.367 |

The bound is not an established equality or a true/ray rate gap. Family 642
hit the address-space ceiling during table construction; the other three
hit the table time allowance. All four hit the graph time allowance. Their
retained graphs have no observed zero-weight trimmed cycle, which does not
establish absence in the full graph.

**Every observed mismatch:** each of 269, 302, 642, and 908 has the following
six mismatches in this diagnostic. Smoke family 269 repeats exactly the same
six. All are labeled `missing_witness_in_partial_graph` in JSON; none is a
disagreement from a closed and complete computation.

| Depth s | Reference L | Listed-graph L | Families |
|---:|---:|---:|---|
| 2 | 3 | 4 | 269, 302, 642, 908 |
| 3 | 3 | 4 | 269, 302, 642, 908 |
| 4 | 3 | 5 | 269, 302, 642, 908 |
| 5 | 3 | 5 | 269, 302, 642, 908 |
| 6 | 3 | 6 | 269, 302, 642, 908 |
| 7 | 3 | 6 | 269, 302, 642, 908 |

### Focused implementation checks

All **13 focused checks pass**: streamed table composition equals TB's
uncapped combination for three iterations on each of two families; four
hand-built graph fixtures cover trimming a nonaccepting zero cycle, an
accepting zero cycle, acyclicity, and a 1/2 cycle mean; forced summary cap,
node cap, and timeout cases retain conservative partial outputs.

The runner worker's mocked checks passed for process count and lane
assignment, reaping, append/resume, timeout/error skipping, malformed journals,
path escapes, duplicate appends, concurrent journals, family alarms, command
allowances, interruption cleanup, invalid arguments, and help. The real smoke
used three processes. A real replay skipped all five indices and preserved
`smoke.jsonl` byte-for-byte; its before/after SHA-256 is in `validation.json`.
Changed Python files also pass in-memory syntax compilation without bytecode
outputs. A read-only independent review found no blocking graph/cost defect.

`validate_rate.py` exits successfully when its implemented checks pass; consult
`complete_requested_validation`, which remains **false** for the ambiguous
four-family selection. The conditional panel is explicitly incomplete. These
are implementation checks, not the registered full study or a new theorem.

## Five-family smoke and estimate

The smoke deliberately includes two cheap validation fixtures and three
difficult fixtures. It used three total processes, a 30-second per-family
budget, and completed in **28.025 seconds** wall time.

| Family | Seconds | Worker peak MiB | Closed / complete | Rate or upper bound | Gate |
|---:|---:|---:|:---:|---:|---|
| 8 | 27.015 | 1685.816 | no / no | ≤ 1 | 4 available depths match |
| 212 | 0.205 | 47.785 | yes / yes | 1/3 exact | 12 match |
| 269 | 27.136 | 1549.566 | no / no | ≤ 1/2 | 6 partial mismatches above |
| 429 | 0.039 | 1685.816 | yes / yes | 1 exact | 12 match |
| 914 | 26.817 | 753.727 | no / no | ≤ 1/4 | 12 match |

Family 429 inherits family 8's high-water RSS because they share a worker.
The sum of each lane's measured high-water RSS is about **3989 MiB**, a
conservative upper envelope for simultaneous measured RSS in this smoke.
All three incomplete families reached time allowances. Passing all twelve
known depths, as 914 does, still does not establish closure.

Total family time was 81.211 seconds. A purely mechanical extrapolation of
this deliberately mixed, censored sample to 226 families at three workers is
about **20.4 minutes plus overhead** at the same 30-second budget. It is not a
population runtime forecast or an estimate for closing all tables. Budgeting
all 226 attempts at 30 seconds gives a nominal **37.7 minutes** at three
perfectly balanced workers (about 38.3 with alarm grace), plus startup,
collection, and journal overhead. At the runner's default 60-second family
budget, the corresponding nominal attempt budget is **75.3 minutes** plus
overhead. Repeated foreground chunks are necessary under the 1190-second
command ceiling. There is **no defensible finite forecast for completing all
226 families exactly** from these censored observations.

## Reproduction and deviations

From the repository root:

```sh
.venv/bin/python -B experiments/TRUE-RATE-20261113-001A/TRUE-RATE-20261113-001A-E001_true_rates/codex/validate_rate.py --seconds-limit 30 --panel-seconds 30 --output validation_replay.json
.venv/bin/python -B experiments/TRUE-RATE-20261113-001A/TRUE-RATE-20261113-001A-E001_true_rates/codex/run_rate.py --workers 3 --only 429 212 269 914 8 --seconds-limit 30 --output smoke.jsonl
```

The second command now skips all five existing rows. A fresh output name is
needed to retry partial families. The validation helper refuses to overwrite
an existing validation file.

For the **thread to launch**, not run by Codex:

```sh
.venv/bin/python -B experiments/TRUE-RATE-20261113-001A/TRUE-RATE-20261113-001A-E001_true_rates/codex/run_rate.py --workers 3 --seconds-limit 60 --output true_rates.jsonl
```

Repeat that identical command after its foreground chunk ends until its
summary has no remaining indices. Already recorded partial/error attempts
are skipped as requested. `true_rates.jsonl` was not created by this task.

Resource-related deviations are explicit: phase reservations and the bounded
empty-side prepass improve partial-bound availability; memory exhaustion is
an additional honest stop under the 8 GiB ceiling; process RSS is a worker
high-water measure; the original no-side study comparator is unavailable, so
the authorized modified-family/BD alternative was used. There was no full
test suite, full-study launch, or change outside CODEX.

## Ambiguities

1. **Which four families?** “The 4 families whose reference deficit L_ray − L
   reaches 3 by depth 7” identifies **nine** rows when “by” means at any
   recorded depth at most 7:
   `33, 269, 302, 579, 642, 678, 908, 911, 1144`.
   Only `269, 302, 642, 908` have a nonnull L at depth 7; the other five
   already reach 3 earlier but have null L at depth 7. No reading was chosen
   as authoritative. The conditional at-depth-7 diagnostic is reported above;
   identifying an unambiguous requested four and asserting a four-family
   conclusion are skipped. All other implementation and validation work was
   performed.

The old TB depth ambiguity is settled by `thread_settled_validation.py` and
the user's explicit uniform-truncation instruction; it is not reopened here.
