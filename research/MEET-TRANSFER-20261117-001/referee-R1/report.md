# Referee report MEET-TRANSFER-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.** Every number recomputes, and the design holds up:
- The held-out patterns were unseen by training and tuning, and the comparator was fixed before any learned arm was tested.
- The frozen inner-loop verdict, "usable on the primary only", is right.
- An off-grid Novelty+ does not change it.

Three Narrowings concern wording and how the frozen seed-agreement clause is applied:
- "Beats the best rule in flips" is stronger than the frozen tiers allow: 3 of 9 cells, with the primary inconclusive.
- The CPU cost is quoted from single seeds: the arm level is 4.7 to 13.5 times, not "1.5 to 9 times".
- The `rand` 2.1 "loss" and the "mixture hurts" readings are seed splits, which the frozen clause reads as learner variance.

## What holds

- **Order.** The UTC times come from the runner's own files:

  | Event | Time (UTC) |
  | --- | --- |
  | Freeze, 19c8b1ed1 | 04:48:26 |
  | Training starts | 04:48:52 |
  | Comparator screen | 04:48:55 |
  | Edge extension, 572bf3e42 | 06:00:28 |
  | Confirm | 07:19 |
  | `retuned.json` written | 07:20 |
  | Training ends | 08:03 |
  | `policies.json` | 08:06:33 |
  | Test | 08:06:59 |

  So the comparator was tuned blind to the learned arms. The edge extension only added settings ("before any learned arm is
  tested", as disclosed).
- **Held out and unseen.**
  - `train_mixed.py`: D, Dn and Dr train and validate on `rand` 2.1, `rand` 4.0 and `block` 2.5 only (Dr on `rand` 2.1 alone).
    Only the oracle Dl adds `local` w10.
  - Seeds are disjoint: training pool 1,000,000+, validation 2,000,000+, test 3.0, 3.5, 3.7 and 3.8 M, screen 4.0 to 4.8 M,
    confirm 4.1 to 4.85 M.
  - The primary's test instances are WHERE-NEXT's local test instances, knot for knot (helper check). The pre-registration discloses
    that the primary "is a development pattern as much as a held-out one". So the clean held-out evidence is the untouched cells:
    `local` w40, `local` w160 and `heavy`.
- **The gate.** `check.py` passes, including G6, run-for-run identity with SCALE-MEMORY's engine on 120 runs (30 s).
- **The headline, recomputed with the referee's own code** (`referee_R_meet.py`, `.json`). The statistic: per-instance five-run
  geometric means, each seed's median, the arm figure as the geometric mean of its seeds, and R against the best of the five tuned
  rules, re-chosen in each of 10,000 resamples, with 99% intervals. Every value matches the note:

  | Cell | D [99%] (seeds) | Dr | Dl | L3sm |
  | --- | --- | --- | --- | --- |
  | `local` w10 3200 (primary) | 0.833 [0.631, 1.090] (0.58, 0.83, 1.18, 0.85) | 0.765 | 0.475 | 24.7 |
  | `local` w10 800 | **0.664 [0.598, 0.811]** (0.55, 0.68, 0.79, 0.66) | 0.701 | 0.460 | 8.57 |
  | `local` w40 800 | 0.754 [0.623, 1.037] (0.31, 0.65, 2.99, 0.53) | 0.442 | 0.365 | 3.44 |
  | `local` w160 800 | 0.946 [0.886, 1.001] | 1.210 | 0.916 | 1.02 |
  | `heavy` 800 | 0.809 [0.756, 0.875] | 0.995 | 0.781 | 1.09 |
  | `heavy` 3200 | **0.724 [0.667, 0.773]** (0.73, 0.76, 0.71, 0.69) | 0.911 | 0.680 | 1.13 |
  | `block` 3200 | **0.614 [0.543, 0.672]** (0.60, 0.57, 0.65, 0.64) | 0.672 | 0.609 | 0.71 |
  | `rand` 4.0 3200 | 0.889 [0.862, 0.954] | 1.146 | 0.875 | 1.02 |
  | `rand` 2.1 3200 | 1.597 [1.398, 1.867] (1.08, 1.87, 0.83, 3.86) | 1.066 | 1.301 | 0.84 |

  Bold marks the frozen-tier flips wins: R ≤ 0.8, upper end < 0.9, every seed ≤ 0.8. They are exactly `local` 800, `heavy` 3200 and
  `block` 3200, with seeds agreeing in all three.
- **The inner-loop bar.**
  - *D on the primary* passes: R 0.83, upper end 1.09 < 2.5, solved 1.00, 95th-percentile ratio 0.35, every seed ≤ 2.
  - *D on w40* fails, with one seed at 2.99, so the frozen "usable on the primary only" is right.
  - *Dr* meets the bar on the primary and every untouched cell. This is labelled post hoc ("read after the fact") in the note.
- **The comparator** (helper, `NOTES_offgrid.md`).
  - *Primary.* The only truly off-grid values, p = 0.95, are hopeless. The best setting found, (0.8, 0), screened but not tested by
    the study, is 6% below the study's best. Even taken at face value, after choosing the minimum of 20 settings on the test
    instances, D's R becomes 0.886 instead of 0.833: still inconclusive, and still usable.
  - *Heavy 3200.* The best off-grid setting ties the study's, so R stays at 0.72.
  - The helper's runs of the study's three tested settings are within 6 to 8%.
- **Gate G-learn and the stated readings.** Dn fails G-learn, a learner failure, as stated. X, Y, Z, K and O recompute, for example
  Z = Dr / L3sm = 0.031 and O = 1.75.

## 1. "Beats the best rule in flips": stronger than the tiers allow (Narrowing, wording)

- **What the summaries say.**
  - The decision headline: "In flips it beats the best rule on most held-out and training patterns".
  - The position table: "The agent now beats well-tuned Novelty+ in flips across meeting patterns".
  - The G15 line: "carries across meeting patterns and beats a well-tuned rule there in flips".
- **What the data show.**
  - By the frozen tiers the flips wins are 3 of 9 cells.
  - The primary is inconclusive: 0.83 [0.63, 1.09], with one seed at 1.18.
  - Point estimates are below 1 in 7 of 9 cells, but intervals include or approach 1 at w40, w160, `rand` 4.0 and the primary.
- **A fair wording.** "Carries over" read as "no longer loses: from 25 times worse to about parity or better" is fair. "Beats" should
  be "beats in flips on `local` 800, `heavy` 3200 and `block` 3200 (frozen tiers), and is at or near parity elsewhere, the
  held-out primary included".

## 2. The CPU cost is quoted from single seeds (Narrowing, a number)

- **What the summaries say.** "1.5 to 9 times Novelty+'s CPU (3.1 times at the primary cell)", in the note, the decision, P7 and the
  goals lines.
- **The arm-level figure** is the geometric mean of the four D seeds' median CPU per instance, over the best rule's (from the
  study's own `summary.json`). It is 4.7 to 13.5 times, and 4.8 times on the primary.
- **Where the quoted numbers come from.** The primary's 3.1 is seed 0's ratio (0.5408 s against 0.1728 s). The seed-level range is
  1.5 (w40, seed 0) to 59 (w40, seed 2).
- **What it changes.** P7 (no CPU win) holds either way; only the cost figure changes.

## 3. Seed splits are learner variance under the frozen clause (Narrowing)

The pre-registration: *"Seed agreement for every verdict and ratio. A claim holds only when the arm-level interval satisfies it and
every seed's own value lies on the same side of the threshold … A split is read as learner variance, not as a verdict on
transfer."*

- **G-learn on `rand` 2.1.** D's per-seed ratios are 1.155, 1.325, 0.870 and 1.301, so three of four fail the 1.15 line. Only the
  arm-level geometric mean, 1.147, passes. So "D passed (borderline)" does not hold with seed agreement; it is a split.
- **The `rand` 2.1 result** (1.60, seeds 0.83 to 3.86) is a split across the 1.0 line. The note's "it loses on the plainest pattern
  … Training on the mixture traded some `rand` 2.1 performance for the rest" reads it as a verdict. By the frozen clause it is
  learner variance.
- **"The mixture hurts on `rand` 2.1 (X = 1.50) and window 40 (1.71)"** rests on D's split seeds (w40: 0.31 to 2.99). It too is
  learner variance, not an effect of the mixture.
- **The verdicts that do hold with seed agreement** are untouched: the three flips wins, the primary's usability, and "fails the bar
  on w40" (the bar itself requires every seed ≤ 2).

## 4. Smaller points (Not a block)

- **The objects gate.** Rerun today, `track.py objects-gate` prints "prior-work line: missing epic `SLOW-LOOP-20261117-001`". That
  epic closed after this freeze. The pre-registration's search used `--until 2026-11-18`, later than its own freeze; rerun with the
  freeze date.
- **Words.** No spatial word is used for the program's objects.

## Fixes for the thread (listed for the owner, not folded in)

1. Replace "beats the best rule in flips on most patterns / across meeting patterns" with the three frozen-tier wins and "at or near
   parity elsewhere, the primary included" (decision, position table, G15 line, note). **Narrowing.**
2. Replace "1.5 to 9 times the CPU (3.1 at the primary)" with the arm-level 4.7 to 13.5 times (4.8 at the primary), seeds 1.5 to 59
   (note, decision, P7 row, goals lines). **Narrowing.**
3. Read D's G-learn on `rand` 2.1 as a split (three of four seeds above 1.15), and read the `rand` 2.1 result and the "mixture hurts"
   ratios as learner variance, per the frozen seed-agreement clause. **Narrowing.**
4. The objects-gate cut-off date. **Not a block.**

## How the work was split

- **The referee.** Read the pre-registration, the note, the decision and the training configuration. Reran the gate, recomputed
  every ratio per seed, and checked the CPU from `summary.json`, the order, the seeds and the wording.
- **One Claude helper.** The off-grid Novelty+ on the primary and on `heavy` (`NOTES_offgrid.md`).
- **Codex** was not used. **The advisor** was not consulted.

## Files

- `referee_R_meet.py` and `.json`: the referee's recomputation.
- `NOTES_offgrid.md` and `referee_offgrid*`: the helper's checks.
