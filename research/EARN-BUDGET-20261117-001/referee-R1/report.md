# Referee report EARN-BUDGET-R1 (fresh code, no Codex; the stress cell included)

**Verdict: Confirmed. No Block.** Charge v2 now counts the rebuild's work to within a few percent. The switch preceded every test
run, the primary pattern was untouched before the freeze, and frozen reading 2 recomputes. The comparator on the primary cannot be
improved by widening its grid. Only wording fixes remain, all **Not a block**.

## What holds

- **Order.** The UTC times come from the runner's own files:

  | Event | Time (UTC) |
  | --- | --- |
  | Freeze, fd9e95c8d | 07:04:47 |
  | Re-tuning | 07:05:09 |
  | Tuning-cell re-tuning | 07:15:37 |
  | Policy (v1) | 07:32:06 |
  | Oracle part A (v1) | 07:34:35 |
  | The referee's SLOW-LOOP report, 8e9cc2f51 | 07:38:30 |
  | Policy v2 and oracle A v2 | 07:46:26 |
  | `policies.json`, from v2 | 07:48:55 |
  | Charge commit, 13ae23679 | 08:05:43 |
  | Oracle part B (v2) | 08:15:56 |
  | Test | 08:17:41 |
  | Stress | 08:36:30 |

  - **The test ran the committed v2 code.** The test job's sha256 equals `job.py` at 13ae23679, and `slow_loop.py` and
    `slow_engine.c` are unchanged from that commit to HEAD.
  - **The v1 runs are kept,** as `policy/`, `oracle_a/` and `policies_v1charge.json`.
- **The primary was untouched before the freeze.**
  - No SLOW-LOOP artifact or code mentions `w15`.
  - The first EARN-BUDGET artifact for `local35-w15-3200` is the re-tuning output at 07:34 UTC, after the freeze.
  - Seeds: tuning 8,500,000+, policy 8,000,000+, test 8,100,000+, stress 8,200,000+. The per-cell oracle GbO was tuned on the
    tuning seeds, disjoint from the test's.
- **Charge v2 counts the rebuild's work** (helper, `referee_earn_task1_charging.*`).
  - **The reruns.** 40 instrumented runs of E reproduce the stored test runs bit for bit.
  - **What v2 adds.** Its additions are 68–70% of `work_rebuild`, and the rebuild costs 5.4–5.8 ns of CPU per charged incidence,
    as the fast loop does (5.0–5.4). Under v1 it was 17–64 ns.
  - **What remains uncharged.** 0.8–1.6% of `work_rebuild`, or 0.2% of the total. One `idx.sort()` is uncharged, but the dedup
    charge on every knot more than covers it.
  - **Corrected R.** 0.56–0.59 on the primary and 0.75–0.78 on `local` w20: still charged wins.
  - **The referee's own check** (`referee_R_earn.json`). Over all cells the rebuild's CPU per charged incidence is 4.6–8.3 ns,
    against 4.7–7.0 for the fast loop. R_work tracks R_CPU within about 10%.
- **The headline, recomputed with the referee's own code** (`referee_R_earn.py`, `.json`). The statistic is the median over
  instances of five-run geometric means of `work`, against the better of NOV and PS, re-chosen in each of 10,000 resamples, with
  99% intervals:

  | Cell | E | E CPU | Gb | GbO | GO | ST | Erb |
  | --- | --- | --- | --- | --- | --- | --- | --- |
  | `local` w15 d3.5 (primary) | **0.557 [0.508, 0.676]** | 0.61 | 0.82 | 0.165 | 0.336 | 7.0 (46 of 250 runs censored) | 0.883 |
  | `local` w20 | 0.747 [0.605, 0.871] | 0.76 | 0.87 | 0.183 | 0.320 | 0.406 | 0.981 |
  | `local` w10 (d 4.0; E's tuning family) | 0.558 [0.424, 0.802] | 0.72 | 0.78 | 0.164 | 0.344 | 0.612 | 0.806 |
  | `local` w40 | 1.031 (ρ stays at 0.03, 0 doublings) | 1.04 | 1.03 | 0.382 | 0.632 | 1.45 | 1.011 |
  | `rand` 2.1, `rand` 3.0, `heavy`, `block` | 1.025–1.036 | 1.10–1.23 | = E | = E | 1.7–4.8 | 1.0–1.8 | 1.01 |
  | `local` w20, n = 12,800 (stress) | **0.182 [0.130, 0.208]** | 0.22 | 0.288 | — | — | 0.114 | 0.482 |
  | `heavy`, n = 12,800 (stress) | 1.026 | 1.02 | 1.026 | — | — | 1.31 | 1.009 |

  The pairs are:
  - E/Gb = 0.68, 0.86 and 0.71 on the winning local cells, 0.97 to 1.00 elsewhere;
  - E/GbO = 3.38, 4.08 and 3.41;
  - E/GO = 1.62 [1.47, 1.71] on `local` w10;
  - E/ST = 0.91 [0.89, 0.95] on `local` w10, and 1.60 at 12,800 on w20.

  All of these match the note.
- **Frozen reading 2 is right.** Every reading-1 condition holds except E/GO ≤ 1.5 on `local` w10, which is 1.62.
  - E wins on the primary and on `local` w20, both structured held-out cells.
  - There is no loss on a structure-poor cell: the lower ends are about 1.03, well below 1.1.
  - E/Gb ≤ 0.9 with upper end < 1 in some cell, and its upper end < 1.1 everywhere (the largest is `embed`, 1.08).
  - E/ST's upper end < 1 in a win cell. This holds on `local` w10 as well as on the primary, so it does not rest on ST's stalls.
- **The ramp diagnosis** (`E_diag` in `referee_R_earn.json`).
  - On `local` w40, E's median ρ_top is 0.03 with 0 doublings and 0 rebuilds in 250 runs.
  - On `local` w20 the median is 4 doublings, and on the primary and on w10 about 8 to 9.
  - GbO reaches 0.38 on w40, so the moves exist.
  - The claim that the ramp, not the moves, limits E is supported.
- **The comparator** (helper, `referee_earn_task2_*`).
  - **The edge.** The primary's NOV best, (0.8, 0.0), is flagged as an edge only because a walk probability of 0 is the floor. The
    grid already includes noise 0.85 and 0.9, and both are far worse: 0.85 hits the cap in 19 to 23 of 40 runs, 0.9 in all of
    them.
  - **The helper's own tuning.** Its own Novelty+ also picks (0.8, 0), and the runners-up are 1 to 14% worse.
  - **Effect on E.** E uses the cell's NOV setting, so even a 10% better rule would leave E's R at 0.58 to 0.62.
- **CDCL.** All 60 new-pattern instances are solved in at most 0.062 s of wall time, and every model checks (P10).
- **Prior work.** `objects-gate` prints "prior-work line: ok".

## Wording fixes (Not a block)

1. **Decision, position table.** "No transfer from structure-poor tuning" should be scoped "at 3,200". At 12,800 Erb wins (0.48).
   The note, the goals checkpoint and the intuition entry already scope it.
2. **Intuition entry.** "A local pattern nothing had touched before the test" should be "before the freeze". The comparator and the
   per-cell oracle were tuned on that cell's tuning instances before the test.
3. **`local` w10 is one of E's tuning families** (density 4.0, at n = 800). Say so where its 0.56 is listed with the wins in the
   headline, the answer's part 1 and the objects row. The note's title says "wins on new local patterns".
4. **The 0.08 against static probing on the primary.** Put the stall caveat next to it (ST stalls in 46 of 250 runs, so its figure
   is a lower bound). It is in the table, but not where part 1 quotes the number.

## How the work was split

- **The referee.** Recomputed every ratio and the reading. Checked the order, the seeds, the code hashes, the CDCL times and the
  wording.
- **One Claude helper.** The instrumented charge audit and the comparator's grid edge (`NOTES_earn.md`).
- **Codex** was not used. **The advisor** was not consulted.

## Files

- `referee_R_earn.py` and `.json`: the referee's recomputation.
- `NOTES_earn.md` and the `referee_earn_*` scripts with their JSON: the helper's checks.
