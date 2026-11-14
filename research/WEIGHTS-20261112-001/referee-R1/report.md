# Referee report WEIGHTS-R1 (Codex-assisted, fresh code)

**Verdict: Confirmed with fixes. No Block.**

**What holds.**
- **W1 passes under all three weightings**, on the prefix rule and on the all-samples reading alike.
- **The summary.** It reruns identically.
- **The four completion certificates and ten main-arm bases** are independently certified.
- **The ±42 window patch** changes nothing in the main arm.

**The fixes.**
- **The paused record.** Its partial results ("46 of 46", "27 of 27"; b3af3f5c7, `paused.md`, `partial_summary.json`) were biased:
  every sample containing a main-arm miss was missing from them. This is a correction to a published claim, a **Narrowing**: W1
  still passes.
- **The calibration.** It has no outcome at all: all 4 attempts were capped.
- **"Big knots make travelling rarer".** It holds across weightings only, not within one.

**How the work was split.** The background referee thread owns the verdict.
- **The referee.**
  - Ran the objects gate. It reports the pre-registration has no prior-work section, because it was frozen on 2026-11-12, before
    that rule; **Not a block**.
  - Reran the study's `summary.py` into this folder (`rerun_summary.py`, `rerun_summary.json`). It is identical to `summary.json`.
  - Recounted the three readings of the stop (`referee_readings.py`, `referee_readings.json`).
  - Found the selection bias in the paused record.
  - Read the resumption job: the window patch is dead code.
- **Codex.** The Codex command-line tool, at the owner's choice of model and effort, ran at reduced load for about 20 minutes.
  - It certified the completions and the spot checks with fresh code and the earlier SHIFT-COUNT and COMMON-FOLD referees' code.
  - It recounted from the raw records and tabulated by diameter.
  - It caught the calibration's capped records and the polarity metadata.
  - It did not flag the paused record's bias, though its table of missing samples shows it.
- **Advisor.** The advisor model was not consulted.

## 1. The summary and the prefix rule (the referee; Codex recounted)

**The summary reruns identically.** The stopping indices are 101, 55 and 89, giving prefixes of 102, 56 and 90 samples.

| β | Prefix rule (frozen reading) | All completed samples | Pause view (census.jsonl only) |
| --- | --- | --- | --- |
| 0 | 39/40 (Wilson 87.1–99.6%) | 47/48 (89.1–99.6%) | 46/46 |
| 1 | 35/40 (73.9–94.5%) | 73/82 (80.4–94.1%) | 27/27 |
| 2 | 38/41 (80.6–97.5%) | 41/45 (79.3–96.5%) | — |

**The prefix rule is a fair reading.** **Not a block.**
- **Why.** The frozen stop is "samples in index order until 40 travelling new-kind bases". Every sample in each prefix is complete,
  and the boundary is fixed by the count, not by the outcomes.
- **The alternative.** Counting every completed sample also passes, so the reading does not decide the verdict.
- **The workers.** Running samples past the stop in parallel does not bias the prefix.

**The pause view is biased.** **Narrowing**, a correction to the published partial.
- **What was missing.** At the pause, every sample with a main-arm miss was absent: β0 samples 38 and 98, and β1 samples 2, 10, 18,
  20, 28, 33, 41 and 50.
  - **Why.** The frozen pipeline runs the enlarged arm only when the main arm misses. That arm either died on the window bug (the 7
    logged "dropped at the cap") or was still running (3).
  - **The reruns.** Every one of the 10 reruns contains a base with one certified direction, or one forced but uncertified
    (Codex's table in `codex/codex_report.md`, section 3).
- **What the paused record said.**
  - "All 46 with two certified unlengthened shifts (Wilson 92 to 100%) ... W1 passes";
  - "27 of 27";
  - "no forced-but-uncertified case among the 73 travelling new-kind bases".

  All three counted only samples with no miss.
- **The final note.** It has the right numbers, but says "Corrections: none" and does not state this selection.

The fix: log it in `docs/CORRECTIONS.md`, and add one sentence to the deviation on the window bug saying that the drops were
exactly the main-arm misses.

## 2. The four completion certificates (Codex)

All four are certified with polarity σ = 1: p on A forces p ⊕ 1 on A + k·d.

| β/sample/r | Direction, k | P, Q | Also rechecked (main arm) |
| --- | --- | --- | --- |
| 0/38/4 | (−1, 1), 1 | 12, 12 | (1, 0) |
| 1/18/4 | (−1, −1), 1 | 4, 2 | (−1, 0) |
| 1/28/4 | (−1, 0), 2 | 4, 4 | (0, −1) |
| 1/41/3 | (1, 0), 2 | 4, 4 | (1, 1) |

**How each was certified.**
- **Forcing.** UNSAT of every image violation in a 61 × 61 window proves forcing, because every infinite state restricts to a model
  of the window.
- **Existence and freeness.** These come from legal states that repeat along and across outside a finite central rectangle, with
  two copies of each tail block equated. The verifier checks every boundary position and a full period in each pure tail.
- **The periods for 1/18.** P = 4 and Q = 2 are below the kinds' spans, so the two-copy span argument alone does not cover them, but
  the direct infinite-extension check does.

All 160 stored witnesses replay, and the wrong-polarity and other controls are rejected. **Not a block:** store σ, the frame and the
witness data with the certificates.

## 3. Ten main-arm spot checks (Codex)

Ten bases were checked: six from before the pause and four resumed, across all three β and both strata.
- **The class.** Travelling was recomputed with the earlier COMMON-FOLD referee's reader.
- **The directions.** Both recorded directions were independently certified with fresh patterns and explicit states.

All 20 checks pass. **Not a block.**

## 4. The deviations (the referee)

**The ±42 window patch is dead code in the resumed run.** **Not a block.**
- **Why.** `resume_census_job.py` wraps the enlarged arm with the ±42 window, and then replaces the enlarged arm with a stub that
  returns nothing. The main arm keeps the frozen window, and its shifts (entries up to 6, multiples up to 4) stay inside ±30.
- **What follows.** No main-arm result can change.
- **The wording.** The note's "the resumption reran them" should say "reran them with the main arm only".

**Bases with one certified direction are counted as unresolved, never against the rule** (summary.py's three categories). That is
correct for W1's lower bound. **Not a block.**

**The calibration has no outcome.** **Narrowing.** All 4 calibration records (11/5, 17/4, 9/4, 17/5) are "dropped at the cap", and
summary.py counts them as "not gained". The note's "ran 4 of 23 (none gained a second direction)", the paused record and the goals
commit should say "4 attempted, all capped, no outcome; W3 undecided with no observation".

## 5. "Big knots travel less" (Codex)

**What holds.** Across weightings the travelling rate rises as short knots are preferred (13.5%, 27.4%, 33.9%). With r = 3, 4 and 5
weighted equally it is 13.8%, 26.6% and 34.1%, so it is not only a mixture of r.

**Within a weighting, the picture is mixed.**
- **By largest diameter.** There is no consistent fall. At β0, travelling and other new-kind bases have the same pooled mean largest
  diameter, 5.625.
- **By mean diameter.** There is a descriptive downward association in the well-populated bins, but it reverses at fixed r. For
  example, at β1 and r = 5 the rates are 7/27 against 9/22.
- **What else moves.** The weighting also changes the stratum's composition and which readings become bases.

**Narrowing.** Write "the identified travelling rate is lower under weightings favouring larger kinds; within a weighting the
association with knot size varies with r and the size measure", not "big knots make it rarer". Tables: `codex/diameter_tables.md`.

## 6. Wording (Codex and the referee)

1. **"Share kinds and seeding".** **Not a block.** The seeds differ per weighting (70000 + 1000·w + i). What is shared is the kind
   universe and the pipeline, and the nested r-prefixes of one sample share a draw. Say so.
2. **The Wilson intervals.** **Narrowing.** Nested readings are dependent, and the stop depends on observed counts, so the intervals
   are descriptive, not calibrated 95% coverage.
3. **"At 88 to 98%".** The point estimates are 97.5%, 87.5% and 92.7%. **Not a block:** say "among travelling bases identified by
   this search".
4. **"Two-way folding is typical ... under four declared weightings".** **Narrowing.** COMMON-FOLD's census has r = 3 to 6 and
   another stratum and certificate family; say so.
5. **The old box at β0.** It holds one base and no travelling ones, so it is not empty. **Not a block.**

## Fixes for the thread

1. **Log a correction for the paused record**, and state in the deviations that the drops were exactly the main-arm misses.
   **Narrowing.**
2. **Restate the calibration** as 4 attempted, all capped, no outcome. **Narrowing.**
3. **Narrow "big knots travel less"** to the across-weighting description. **Narrowing.**
4. **Call the Wilson intervals descriptive**, and qualify "four declared weightings". **Narrowing.**
5. **The rest.** The seeding wording, "main arm only" for the reruns, σ in the certificates, and the old box at β0. **Not a
   block.**

## Files

- **The referee's.** `rerun_summary.py` and `rerun_summary.json`; `referee_readings.py` and `referee_readings.json`.
- **Codex's, in `codex/`.** `codex_report.md`, `audit_certificates.py`, `audit_data.py`, `completion_checks.json`,
  `spot_checks.json`, `recount.json`, `diameter_tables.{md,json}`, `validation_checks.json` and `provenance.json`.
