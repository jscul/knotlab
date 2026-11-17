# Speculative merges from the search's own evidence do not pay: the evidence is real, but too often wrong on random patterns, and the undo cannot tell a good merge from a bad one

Epic `SPEC-MERGE-20261117-001`, ticket `SPEC-MERGE-20261117-001A` (sub-goal B191, direction A gated by D, the coordinator's
go-ahead; goals G15, G16), 2026-11-17. Evidence: **computed** on finite experiments with planted instances, every run kept. Frozen
before the gate, any tuning or any test instance ran ([pre-registration](preregistration.md), freeze commit `8147c8202`;
[advisor review](advisor_review.md), "freeze with changes", taken). **Referee pending.** The canonical K1–K3 test is unchanged.
**These moves do not keep the allowed states**; every state reported in the 11,050 test runs was checked on the original knots
and satisfied them all.

## The question, and the answer

The two earlier studies changed the knot pattern only with moves a refutation proves, and those found nothing on random patterns.
This study tested mutations that are not proofs:
- **The evidence.** The slow loop watches the fast loop (Novelty+) and counts, for every co-knotted pair of distinctions, how many
  epochs in a row both flipped while their relative value stayed the same.
- **The move.** When the search is stuck, it merges the most stable pairs at their current relative value, without proof.
- **The undo.** It undoes the latest round of merges if the search does not then get below where it was stuck.

**The answer has four parts.**

1. **The evidence is real (gate D passed on both families).**
   - **On `rand` 2.1 at 3,200,** the 1% most stable pairs agreed with the planted relative values in 0.66, 0.69 and 0.75 of cases
     at 4, 8 and 16 epochs. Random co-knotted pairs agreed in 0.55, 0.58 and 0.63; the difference is 0.11 to 0.13, with the lower
     end at least 0.05. The same held against the solution each run went on to find (0.65 to 0.74 against 0.55 to 0.65).
   - **On `local` w10,** they were provably tied (pair probe) in 0.54 to 0.59 of cases against 0.22 to 0.23, about 2.5 times as
     often, with agreement 0.98 to 1.00.
   - **This is the first signal from the fast loop's history** that predicts structure better than chance. SLOW-LOOP's attention
     counts did not.
2. **But speculative merges never paid.** Every speculative arm lost on every random cell, and none won on the local one.
   - **On the primary (`rand` 2.1, 3,200):**
     - the tuned arm A cost 1.17 [1.13, 1.33] of the better Novelty+ (it rarely acted);
     - the default A0 cost 1.29;
     - the fixed eager arm AE cost 2.26 [1.70, 6.28], with 10% of its runs stalled at the cap.
   - **At 12,800:** 1.21, 1.34 and 1.85.
   - **On `rand` 3.0:** 2.25 to 4.40. Most of that is the fast loop: Novelty+ (0.7, 0.01) costs twice the re-tuned (0.6, 0.02)
     there. Against its own fast loop the arms still cost 1.09 to 2.13.
   - **On `local` w10:** the best arm, Aloc (tuned there), was 1.41 [0.85, 1.97], and 0.89 [0.59, 1.21] against its own fast
     loop. The proof-based eager loop (Gpr) was 0.15 [0.11, 0.19], 9 to 20 times better than any speculative arm.
3. **Why: on random patterns the evidence is right too rarely for unproved merges.**
   - **The precision of AE's merges** was 0.70 on `rand` 2.1 and 0.66 at 12,800. A round of 320 merges at that precision is almost
     never wholly right: no round of AE on `rand` 2.1 was consistent with the planted state.
   - **Where the evidence is near-certain,** on `rand` 3.0 (precision 0.98) and `local` w10 (0.99), the search was rarely stuck,
     or the merges were too few to matter beside the cost of watching. Proof-based probing gets the same structure far more cheaply
     and completely.
4. **The undo cannot tell a good merge from a bad one.** On `local` w10 the rounds were logged against the planted state:
   - AE undid 2,071 of its 2,446 wholly correct rounds (85%), and kept 449 of its 4,829 rounds with a wrong merge (9%);
   - A0 undid 2,141 of 2,430 correct rounds;
   - on `rand` 2.1, AE kept 85 wrong rounds of 2,879, and 10% of its runs stalled at the cap.

   Whether the search gets below its pre-round best within a few epochs is no test of a merge. This is assumption A93, overturned.

**The evidence matters only in one arm.** On `local` w10 the tuned arm A cost 0.32 [0.21, 0.57] of its activity-matched random
control: random merges where the search is active are worse still. A0, AE and Aloc were not separated from their controls, and on
`rand` the arms rarely merged at all.

**By the frozen rule this is reading 5: no win anywhere.**
- **Not untested.** AE merged in the median run on `rand` 2.1.
- **No random cell won,** so the publication hold did not arise.
- **No speculative arm won on `local`.**

**Known neighbours, and what differs.**
- **The neighbours.** Multilevel refinement (Walshaw 2002) coarsens by graph matching before the search. Backbone-guided local
  search (Zhang 2004) biases choices by pseudo-backbones. Decimation by survey propagation fixes values by estimated marginals,
  and is near-perfect only near the solution cluster.
- **What differs here.** The merges fixed relative values chosen from the search's own co-flip history during the search, and
  were undone on stalls.
- **What the result says.** Such history carries structural information, but on random planted patterns near the threshold it is
  about 70% right. Unproved merges need far more than that, and a stall-based undo does not supply the missing check.

## Results

Charged work under the corrected charge (v2): the median over fresh instances of five-run geometric means, against the better of
Novelty+ (0.7, 0.01) and EARN-BUDGET's re-tuned Novelty+, re-chosen per resample (99% intervals). 50 instances per cell (20 at
12,800).

| Arm | `rand` 2.1, 3,200 (primary) | `rand` 3.0, 3,200 | `rand` 2.1, 12,800 | `local` w10, 3,200 |
| --- | --- | --- | --- | --- |
| A0 (default) | 1.29 [1.24, 1.46] | 2.57 [2.21, 3.30] | 1.34 [1.26, 1.55] | 2.10 [1.44, 3.06] |
| Arand0 | 1.29 | 2.57 | 1.34 | 2.37 |
| AE (fixed eager) | 2.26 [1.70, 6.28]* | 4.40 [3.17, 5.40] | 1.85 [1.62, 2.43] | 3.13 [1.65, 5.33]* |
| AErand | 1.94 | 3.85 | 1.86 | 2.72 |
| A (tuned on `rand` 2.1) | 1.17 [1.13, 1.33] | 2.25 [1.96, 3.00] | 1.21 [1.13, 1.34] | 1.56 [1.09, 2.34] |
| Arand | 1.17 | 2.29 | 1.21 | 4.83* |
| Aloc (tuned on `local` w10) | 1.17 | 2.29 | 1.21 | 1.41 [0.85, 1.97] |
| Arandloc | 1.17 | 2.29 | 1.21 | 1.80 |
| Gpr (proof-based eager) | 1.69 | 6.20 | 1.59 | **0.15 [0.11, 0.19]** |
| Dr, seed 0 / seed 1 (context) | 6.15 / 4.09 | 4.89 / 4.31 | 6.69 / 4.09 | 3.71 / 3.36 |

\* Over 5% of runs censored, so the figure is a bound.

- **Verdicts.** Every speculative arm is a loss or parity in every cell; Gpr is a charged win on `local` w10 only (CPU 0.14).
- **CPU** follows the work in every cell (R_CPU within about 15% of R_W, except Dr).
- **Against the arms' own fast loop** (Novelty+ (0.7, 0.01)): A is 1.14, 1.09, 1.14 and 0.99 on the four cells; Aloc is 0.89
  [0.59, 1.21] on `local` w10.
- **Dr.** MEET-TRANSFER's learned fast loop (unrefereed), alone, made 0.80 to 1.53 times the flips of the better Novelty+. Its
  reads make its charged work 3.4 to 6.7 times, and its CPU 4.5 to 14 times.
- **Merges** (median per run): A, Aloc and A0 made none on the random cells; AE made 320 on `rand` 2.1 and 1,280 at 12,800. On
  `local` w10: A0 192, AE 2,791, A 48, Aloc 864.

**The undo, round by round** (all rounds of the five runs per instance; "right" means every merge of the round agreed with the
planted state):

| Arm, cell | Right, kept | Right, undone | Wrong, kept | Wrong, undone |
| --- | ---: | ---: | ---: | ---: |
| AE, `rand` 2.1 | 0 | 0 | 85 | 2,794 |
| A0, `rand` 2.1 | 0 | 0 | 28 | 95 |
| AE, `local` w10 | 375 | 2,071 | 449 | 4,380 |
| A0, `local` w10 | 289 | 2,141 | 30 | 121 |
| Aloc, `local` w10 | 163 | 680 | 187 | 689 |

**Soundness.** No contradiction went unhandled, and no reported state failed an original knot (11,050 test runs). Runs censored
at the cap are listed by `summary.json` (`censored`). Apart from one Novelty+ (0.7, 0.01) run on `local` w10 (0.4%), they are all in the
speculative arms and their random controls, up to 18% (Arand on `local`).

## Gate D

30 fresh instances per cell; checkpoints at 4, 8 and 16 epochs of n flips; k = 1% of n pairs. On `rand` 2.1, 7 instances were
solved before epoch 16; on `local` w10, 1.

| Cell, epoch | Co-flip agreement (planted) | Random agreement | Difference [99%] | Against the found solution | Tied share, co-flip / random |
| --- | ---: | ---: | --- | --- | --- |
| `rand` 2.1, 4 | 0.664 | 0.551 | 0.113 [0.047, 0.176] | 0.645 / 0.545 | — |
| `rand` 2.1, 8 | 0.685 | 0.579 | 0.106 [0.049, 0.165] | 0.668 / 0.567 | — |
| `rand` 2.1, 16 | 0.754 | 0.629 | 0.125 [0.076, 0.186] | 0.742 / 0.645 | — |
| `local` w10, 4 | 0.926 | 0.891 | 0.035 | 0.932 / 0.887 | 0.38 / 0.23 |
| `local` w10, 8 | 0.981 | 0.899 | 0.082 | 0.984 / 0.903 | 0.54 / 0.23 |
| `local` w10, 16 | 0.998 | 0.941 | 0.057 | 0.999 / 0.950 | 0.59 / 0.22 |

Both frozen tests passed: the difference is at least 0.10 on `rand` with its lower end above 0, and the tied share is at least 1.5
times on `local`.

## Predictions

| # | Prediction (probability) | Outcome |
| --- | --- | --- |
| S | Gates S1–S5 | **Passed** (`gates/check_output.txt`): 544,573 speculative merges at n = 800 with every reported state checked |
| P1 | D passes on `rand` (80%) | **Held** |
| P2 | D passes on `local` (90%) | **Held** |
| P3 | No speculative arm wins on `rand` 2.1 at 3,200 (95%) | **Held** |
| P4 | A costs at most 10% on `rand` 2.1 at 3,200 (15%) | **Failed**: 1.17 |
| P5 | Some speculative arm wins on `local` w10 (60%) | **Failed**: the best, Aloc, at 1.41 |
| P6 | The best speculative arm on `local` w10 beats its random control (85%) | **Failed**: Aloc/Arandloc 0.78 [0.52, 1.16] (A/Arand 0.32 [0.21, 0.57] would pass) |
| P7 | Speculative merging beats proof on `local` w10 (10%) | **Failed**, as predicted, 9 to 20 times worse |
| P8 | AE's merges on `rand` 2.1 are often wrong: precision below 0.8 (45%) | **Held**: 0.70 |
| P9 | Every reported state satisfies the original knots (99.9%) | **Held** |

Five of nine held.

**Decision (frozen rule).** Reading 5, **no win anywhere**.

## Deviations

- **The test ran in two parts.** The fixed arms launched once the gate had passed and while tuning ran. The tuned arms followed on
  the same instances and initial states, and the analysis reads both.
- **The learned fast loop Dr** was added before the freeze as a context arm, at the coordinator's offer. Its engine reads unsigned
  knots, so no slow loop ran on it.

Nothing else differs from the frozen text.

## Limitations

- **The instances.** Planted instances only, with one density per random cell beside 2.1.
- **The rules tried.** One evidence rule (stability of the relative value) and one undo rule. Kept rounds are never undone later.
- **The fast loop.** It is Novelty+ (0.7, 0.01), as the coordinator asked, which is weaker than the re-tuned setting on `rand` 3.0.
- **Not tried:**
  - using the evidence to choose which pairs to *prove* (direction #1);
  - a per-merge check other than the search's progress.
- **CPU.** Thread CPU on a machine shared with other studies.

## Where to start again

- **Code** (in `experiments/SPEC-MERGE-20261117-001A/SPEC-MERGE-20261117-001A-E001_spec_merge/`):
  - `spec_merge.py`: the evidence, the merges and undos, and gate D;
  - `slow_engine.c`: EARN-BUDGET's engine with flip counts and a pair probe;
  - `job.py`, `choose.py` and `analyze.py`;
  - the gates: `.venv/bin/python -B experiments/.../check.py`.
- **Runs** (in `artifacts/SPEC-MERGE-20261117-001A/SPEC-MERGE-20261117-001A-E001_spec_merge/`):
  - `gate/`, `policy/`, `test_fixed/` and `test_tuned/`;
  - the choice `policies.json`;
  - the summaries `gate_summary.json` and `summary.json`.
- **To rebuild:** `.venv/bin/python -B experiments/.../analyze.py test artifacts/.../test_fixed,artifacts/.../test_tuned artifacts/.../summary.json`.
