# Referee R1: the hand-written baselines of WHERE-NEXT-20261116-001, rechecked

Referee R1 (Claude), 2026-11-16. Every search below except L3's runs used the referee's own engine,
`referee_sls.c`, written from the published rule definitions. It has its own occurrence lists, its own RNG
(xoshiro256** seeded by splitmix64), its own seeds and random tie-breaking. The study's code was read only
to learn its conventions: one step per flip, uniform initial state, caps, and the NAE break/make. The study's
`engine.planted` regenerated the instances. Each instance was then checked independently
(`referee_common.check_instance`):
- m = round(αn);
- every knot has three distinct in-range distinctions;
- the hidden state is not constant and satisfies every knot;
- each `local` knot lies within the window of 10.

810 instances passed: 100 test instances each at rand 200, 800 and 3200 and at local 200, 800 and 3200;
64 + 64 + 32 tuning instances (seeds 4,000,000+); and 50 at rand 12800. Every solved run's final state was
checked against every knot. The engine self-test passed: incremental counts matched a recomputation over
5,000 flips on one `rand` and one `local` instance, and the violated-count change equalled break − make.

L3 is the thing under test, so it was run in the study's engine (`referee_L3_rerun.py`). Using the study's
own run seeds, it reproduced `test/results.jsonl` exactly on 100 of 100 instances at each of n = 200, 800
and 3200.

Sizes and runtimes are wall times with 8 workers on a shared machine (load average about 20).

## Task 1: reference behaviour

**Verdict: Matches.**

Scripts: `referee_task1_reference.py` (53 s), `referee_task4_local3200.py` and
`referee_task1_rand12800.py`. Outputs: `referee_task1_reference.json`, `referee_task4_local3200.json` and
`referee_task1_rand12800.json`.

Setup:
- 100 test instances per cell, with the study's caps.
- Five independent runs per instance (two at local 3200 and at rand 12800).
- Each rule was run with its re-tuned parameters, and also with its training-tuned parameters where those
  differ.

Columns:
- *ratio*: the referee's pooled median divided by the study's, with a paired 95% bootstrap over instances.
- *MWU p*: a Mann–Whitney test of the referee's first run against the study's 100 runs.

| Cell | Rule (params) | Study arm | Study median | Referee median (runs) | ratio [95%] | MWU p |
| --- | --- | --- | ---: | ---: | --- | ---: |
| rand 200 | Novelty+ (0.7, 0.1) | @cell | 1,738 | 1,424 (500) | 0.82 [0.63, 1.03] | 0.34 |
| rand 200 | Novelty+ (0.7, 0.05) | @train | 1,164 | 1,274 (500) | 1.10 [0.81, 1.43] | 0.04 |
| rand 200 | probSAT (2.4, 1) | @cell | 2,994 | 3,315 (500) | 1.11 [0.74, 1.38] | 0.40 |
| rand 200 | probSAT (1.8, 1) | @train | 3,818 | 3,478 (500) | 0.91 [0.73, 1.17] | 0.61 |
| rand 200 | WalkSAT 0.5 | @cell | 3,078 | 3,143 (500) | 1.02 [0.77, 1.33] | 0.49 |
| rand 200 | WalkSAT 0.6 | @train | 3,078 | 3,334 (500) | 1.08 [0.89, 1.34] | 0.64 |
| rand 800 | Novelty+ (0.6, 0.05) | @cell | 15,073 | 13,974 (500) | 0.93 [0.75, 1.08] | 0.55 |
| rand 800 | Novelty+ (0.7, 0.05) | @train | 15,398 | 14,073 (500) | 0.91 [0.74, 1.05] | 0.05 |
| rand 800 | probSAT (1.5, 1) | @cell | 36,233 | 39,006 (500) | 1.08 [0.89, 1.31] | 0.33 |
| rand 800 | probSAT (1.8, 1) | @train | 48,898 | 35,602 (500) | 0.73 [0.61, 1.04] | 0.66 |
| rand 800 | WalkSAT 0.6 | @train | 40,839 | 39,306 (500) | 0.96 [0.84, 1.14] | 0.92 |
| rand 3200 | Novelty+ (0.7, 0.01) | @cell | 72,276 | 77,160 (500) | 1.07 [0.95, 1.18] | 0.34 |
| rand 3200 | Novelty+ (0.7, 0.05) | @train | 80,050 | 87,132 (500) | 1.09 [0.98, 1.19] | 0.45 |
| rand 3200 | probSAT (1.5, 1) | @cell | 243,494 | 239,775 (500) | 0.98 [0.87, 1.11] | 0.42 |
| rand 3200 | probSAT (1.8, 1) | @train | 277,236 | 269,272 (500) | 0.97 [0.89, 1.17] | 0.62 |
| rand 3200 | WalkSAT 0.7 | @cell | 294,174 | 276,533 (500) | 0.94 [0.87, 1.01] | 0.34 |
| rand 3200 | WalkSAT 0.6 | @train | 296,476 | 308,486 (500) | 1.04 [0.86, 1.20] | 0.94 |
| rand 12800 | Novelty+ (0.7, 0.05) | @cell | 401,581 | 382,711 (100) | 0.95 [0.80, 1.14] | 0.68 |
| local 200 | Novelty+ (0.7, 0.05) | @train | 1,592 | 1,426 (500) | 0.90 [0.67, 1.19] | 0.68 |
| local 200 | probSAT (1.2, 1) | @cell | 3,553 | 3,758 (500) | 1.06 [0.82, 1.43] | 0.81 |
| local 200 | probSAT (1.8, 1) | @train | 3,832 | 4,213 (500) | 1.10 [0.85, 1.59] | 0.35 |
| local 200 | WalkSAT 0.7 | @cell | 4,302 | 4,004 (500) | 0.93 [0.79, 1.20] | 0.25 |
| local 200 | WalkSAT 0.6 | @train | 3,548 | 3,828 (500) | 1.08 [0.79, 1.40] | 0.32 |
| local 800 | Novelty+ (0.7, 0.05) | @train | 39,578 | 30,719 (500) | 0.78 [0.59, 1.03] | 0.43 |
| local 800 | probSAT (1.8, 1) | @train | 206,874 | 205,088 (500) | 0.99 [0.80, 1.56] | 0.50 |
| local 800 | WalkSAT 0.8 | @cell | 79,081 | 76,704 (500) | 0.97 [0.77, 1.28] | 0.73 |
| local 800 | WalkSAT 0.6 | @train | 107,850 | 100,824 (500) | 0.93 [0.74, 1.45] | 0.15 |
| local 3200 | Novelty+ (0.7, 0.05) | @train | 596,670 | 599,670 (200) | 1.01 [0.75, 1.57] | 0.99 |
| local 3200 | probSAT (1.2, 1) | @cell | 1,302,606 | 1,596,764 (200) | 1.23 [0.95, 1.52] | 0.18 |
| local 3200 | probSAT (1.8, 1) | @train | 6,251,270 | 4,602,594 (200) | 0.74 [0.51, 1.03] | 0.20 |
| local 3200 | WalkSAT 0.8 | @cell | 1,045,650 | 1,067,588 (200) | 1.02 [0.73, 1.61] | 0.74 |
| local 3200 | WalkSAT 0.6 | @train | 2,225,099 | 2,121,828 (200) | 0.95 [0.66, 1.27] | 0.83 |

Every interval contains 1, and the rows show no direction. Two of the 32 MWU tests are near p = 0.05, which
is what chance gives.

The study's hand-written arms are therefore implemented as published.

One thing matters for R: **a median of one run per instance is noisy at small n**. At rand 200, the
study's re-tuned Novelty+ draw (1,738) is 1.22 times the referee's 500-run median for the same parameters
(1,424). The study's L3 draw (782.5) is 0.88 times L3's own 500-run median from fresh seeds (886.5, below).

## Task 2: is the training-size win robust to a wider tuning?

**Verdict: Differs in size, not in direction.**

Scripts: `referee_task2_wide_tuning.py` (tune and test at n = 200, 800 and 3200),
`referee_L3_rerun.py` and `referee_task2_summary.py`. Outputs: `referee_task2_{tune,test}_n{200,800,3200}.json`,
`referee_L3_rerun.json` and `referee_task2_summary.json`. Runtime: tuning 18 s, 253 s and 331 s; testing
55 s, 116 s and 587 s.

Grids. The coarse grids came first. The fine grids were added after the coarse ones showed a sharp optimum
near p = 0.7.

| Rule | Grid at n = 200 and 800 |
| --- | --- |
| Novelty+ | p ∈ {0.1, …, 1.0} × wp ∈ {0, 0.005, 0.01, 0.02, 0.05, 0.1, 0.15, 0.2}, plus p in steps of 0.025 over 0.55–0.80 × wp ≤ 0.05 |
| probSAT (poly form) | cb ∈ {1.0, 1.25, …, 4.0} × eps ∈ {0.25, 0.5, 1} |
| Adaptive Novelty+ (Hoos 2002) | wp ∈ {0, 0.01, 0.05} × 1/θ ∈ {3, 6, 12} × φ ∈ {0.1, 0.2, 0.4}; the published default is 1/θ = 6, φ = 0.2, wp = 0.01 |
| Novelty++ (Li and Huang 2005) | p ∈ {0.3, …, 0.9} × dp ∈ {0.01, …, 0.2}, plus a finer grid near the optimum |
| WalkSAT | p ∈ {0.1, …, 0.9} |

At n = 3200 the grid was lighter: only the regions that were competitive at n = 800.

Tuning and test:
- **Tuning** used seeds 4,000,000 + i: 64 instances × 2 runs at n = 200 and 800, and 32 × 1 at n = 3200.
  The objective was the median.
- **Test**: the top settings from tuning (5 for Novelty+ and Novelty++, 3 for the others) ran 5 times per
  test instance at the study's caps.
- **L3** was re-run 5 times per test instance with fresh seeds in the study's engine.
- **Ratios** are the rule's median over L3's median, with a paired 95% bootstrap over instances in which
  each instance brings all its runs.

| | n = 200 | n = 800 | n = 3200 |
| --- | ---: | ---: | ---: |
| Study L3 median (1 run per instance) | 782.5 | 9,060.5 | 77,115.5 |
| L3, 5 fresh runs per instance | 886.5 | 9,558 | 77,680.5 |
| Study's re-tuned Novelty+ (1 run per instance) | 1,738.5 | 15,073 | 72,276 |
| Study ratio, Novelty+ / L3 | 2.22 | 1.66 | 0.94 |
| **Tuning-selected Novelty+, 5 runs** | (0.675, 0.01): 1,244.5 | (0.675, 0.01): 12,418.5 | (0.7, 0): 70,520 |
| **Its ratio to fresh L3** | **1.40 [1.16, 1.59]** | **1.30 [1.15, 1.40]** | **0.91 [0.84, 0.98]** |
| Tuning-selected Novelty++, ratio to fresh L3 | 1.46 [1.22, 1.65] | 1.28 [1.16, 1.40] | 1.01 [0.94, 1.09] |
| Best of the top-5 on test (light selection on test), ratio to fresh L3 | Novelty++ (0.65, 0.005): 1.23 [1.03, 1.43] | Novelty+ (0.7, 0.01): 1.22 [1.12, 1.34] | 0.91 |
| Best single setting on the test grid (1 run; winner's curse), ratio to study L3 | Novelty++ (0.7, 0.01): 1.17 | Novelty++ (0.65, 0.01): 1.13 | Novelty++ (0.65, 0.02): 0.88 |
| Tuning-selected probSAT, ratio to fresh L3 | (2.0, 1): 3.39 | (1.25, 0.5): 3.59 | (1.25, 0.5): 2.97 |
| Tuning-selected WalkSAT, ratio to fresh L3 | 0.5: 3.70 | 0.6: 4.16 | not run |
| Tuning-selected Adaptive Novelty+, ratio to fresh L3 | (0.01, 12, 0.4): 1.96 | 3.91 | 6.71 |

Reading:
- **L3 does beat every tuned rule at its training sizes.** Every honest interval excludes 1. But the margin
  is about 1.3 to 1.4 times, not 1.7 to 2.2 times.
- Stated as the study's R = L3 / best rule:
  - n = 200: R ≈ 0.71 [0.63, 0.86], against the published 0.45.
  - n = 800: R ≈ 0.77 [0.71, 0.87], against the published 0.60.
- About half the published gap, in log terms, comes from three sources. At n = 200:

  | Source | Factor |
  | --- | ---: |
  | L3's lucky single draw | 1.13 |
  | Novelty+'s unlucky single draw | 1.22 |
  | Tuning: the study used a coarse grid with wp ≥ 0.01, scored on 16 instances | 1.14 |

  1.13 × 1.22 × 1.14 = 1.57, and 2.22 / 1.57 = 1.41. At n = 800 the factors are 1.06, 1.08 and 1.13.
- With an honest tuning, no standard rule comes within 1.2 times of L3. With light selection on the test
  instances, Novelty+ and Novelty++ reach 1.22 to 1.23 times, at the edge of that threshold.
- So the win is **not a tuning artefact, but its published size is about 1.6 times too large at n = 200 and
  1.3 times too large at n = 800**. With these estimates, P2 (R in [0.7, 1.1] at n = 200) would have held,
  narrowly, instead of "failed the other way".
- At the primary cell, rand n = 3200, the wider tuning leaves Novelty+ where it was. L3 / Novelty+ is about
  1.10 [1.02, 1.19]. That firms up the clean loss: the lower end is above 1, against the study's 0.90.
- Novelty+ is best at p ≈ 0.65–0.7 at every size, with wp small (0 to 0.01). The optimum in p is sharp at
  n = 800: in tuning, 0.6 is about 1.2 to 1.4 times worse and 0.8 about 3.4 to 3.8 times worse.

An aside: **Adaptive Novelty+ at its published defaults does badly here.**
- Its noise settles at about 0.3 to 0.4. The static optimum is about 0.7.
- At n = 3200 the default setting (0.01, 6, 0.2) has a median of 19.4 million flips, about 250 times L3.
- So it is not a stronger baseline than tuned Novelty+.

## Task 3: do the memory features saturate with size?

**Verdict: Matches the study's hypothesis.** The absolute memory features saturate as n grows, while age/n
stays nearly scale-free.

Script: `referee_task3_memory_scale.py` (3 s). Output: `referee_task3_memory_scale.json`. The runs were the
referee's Novelty+ with the study's re-tuned parameters per cell, all solved: 100 test instances each at
rand 200, 800 and 3200, and 20 at rand 12800. Every step was logged for the three members of the attended
knot, and for the knot itself. The figures below are pooled over all steps.

| n | 200 | 800 | 3200 | 12800 |
| --- | ---: | ---: | ---: | ---: |
| Median flips | 1,655 | 16,703 | 77,131 | 432,893 |
| Member age above 1,000, or never flipped | 7.5% | 24.0% | 45.3% | 64.8% |
| Never flipped | 5.7% | 2.7% | 2.9% | 2.4% |
| Median member age (never = ∞) | 56 | 142 | 720 | 2,976 |
| Interquartile range of age (flipped members) | 10–186 | 19–811 | 103–3,176 | 442–12,841 |
| **Median age / n** | **0.28** | **0.18** | **0.23** | **0.23** |
| Median of the agent's age feature, min(1, log1p(age)/log1p(1000)) | 0.58 | 0.72 | 0.95 | 1.00 (saturated) |
| Median decayed flip count (τ = 50) | 0.45 | 0.078 | 6e-7 | 2e-26 |
| Decayed count below 0.01 | 24% | 43% | 65% | 83% |
| Decayed count above 0.5 | 48% | 35% | 13% | 5% |
| Attended knot's visit age above 1,000, or never visited | 20% | 33% | 62% | 85% |
| Attended knot's median decayed visit count | 0.03 | 0.004 | ~0 | ~0 |

Reading:
- Raw ages grow about 53-fold from n = 200 to 12800. Age/n stays within 0.18–0.28.
- The clipped age feature and the decayed counts lose most of their range by n = 3200. At n = 12800 they are
  saturated or zero for most reads.
- This fits the study's account: memory still helped at 3200 (M = 0.37) and stopped helping at 12800
  (M = 0.96).
- Caveat: these are Novelty+ trajectories, not L3's. The study's engine has no hook to log L3's own
  features, so this is a proxy. L3 takes a just-violated knot 33–37% of the time, which shortens its
  knot-visit ages.
- The data support the retraining the study proposed, with ages divided by n, or by the number of knots m.

## Task 4: local n = 3200

**Verdict: Matches.**

Script: `referee_task4_local3200.py` (251 s). It ran 100 test instances × 2 runs for Novelty+, probSAT and
WalkSAT; the rows are in the Task 1 table.
- Novelty+ (0.7, 0.05): the referee's median is 599,670, against the study's 596,670 (ratio 1.01
  [0.75, 1.57]).
- The other rules match within noise.
- So R = 55 for L3 on `local` n = 3200 stands on a correct baseline.

## Files

| Role | Files |
| --- | --- |
| Engine | `referee_sls.c` (built into the session scratchpad) |
| Shared code | `referee_common.py`: instance checks, runner and statistics |
| Task scripts | `referee_task1_reference.py`, `referee_task1_rand12800.py`, `referee_task2_wide_tuning.py`, `referee_L3_rerun.py`, `referee_task2_summary.py`, `referee_task3_memory_scale.py`, `referee_task4_local3200.py` |
| Outputs | one JSON per script, named after it |

Every script runs with `.venv/bin/python -B <script>`.
