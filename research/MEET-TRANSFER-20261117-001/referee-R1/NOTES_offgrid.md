# Referee R1: does an off-grid Novelty+ setting beat the study's comparator?

Referee R1 (Claude), 2026-11-17, for MEET-TRANSFER-20261117-001.

**The engine.** `referee_sls.c` is the referee's own Novelty+, copied from the earlier referee folders and
unchanged.

**The instances** come from MEET-TRANSFER's own `engine.planted`:
- They were checked independently: three distinct distinctions per knot, the hidden state satisfies every
  knot, and local knots lie within the window.
- At `local` they are identical, knot for knot, to WHERE-NEXT's generator on all 50 seeds.

**The runs:**
- 50 test instances, 3 runs each, with the referee's own seeds, on 8 workers.
- *Statistic*, as in the study: the median over instances of each instance's geometric mean of its runs.
- *Comparisons*:
  - against the study's best value;
  - against the referee's own run of that setting, with a paired 95% bootstrap over instances.
- *Settings* fall into three groups:
  - tested by the study;
  - screened by the study (on 8 tuning instances) but not tested;
  - off-grid, never screened.

Script: `referee_offgrid.py`. Outputs: `referee_offgrid_*.json` and `referee_offgrid_summary.json`.

## Primary cell: `local`, α = 4.0, window 10, n = 3200

**Verdict: No.** No setting beats the study's best by more than 10%, and R for D stays below 1.

The grid was p ∈ {0.75, …, 0.95} × wp ∈ {0, 0.005, 0.01, 0.02}, plus the study's (0.8, 0.05), with cap
4e8. Wall times were 34, 39 and 29 s for p = 0.8, 0.75 and 0.85.

The study's best is (0.8, 0.01) at 425,512. D's figure is 0.833 × 425,512 = 354,345.

| Setting | Status | Referee geo-stat | / study's best | / referee's run of (0.8, 0.01) |
| --- | --- | ---: | ---: | --- |
| (0.8, 0) | screened, not tested | 399,798 | 0.94 | 0.89 [0.70, 1.18] |
| (0.8, 0.02) | screened, not tested | 439,936 | 1.03 | 0.98 [0.75, 1.26] |
| (0.8, 0.01) | tested (study: 425,512) | 450,590 | 1.06 | 1 |
| (0.8, 0.005) | tested (study: 504,947) | 477,779 | 1.12 | 1.06 [0.78, 1.32] |
| (0.8, 0.05) | tested (study: 496,178) | 535,950 | 1.26 | 1.19 [0.80, 1.63] |

The rest of the grid is slower:

| p | Geo-stat | Note |
| --- | --- | --- |
| 0.75 | 562,052–639,085 | |
| 0.85 | 582,928–751,942 | |
| 0.9 | ≥ 8.6 million | Lower bound: 92–121 of 150 runs exceeded a budget of 1e7 flips |
| 0.95 (off-grid) | ≥ 10 million | Lower bound: every run exceeded 1e7 |

The first full-cap run at p = 0.9 passed 9 minutes. That chunk was stopped and rerun with the 1e7 flip
budget, which can rule a setting out but not in.

Reading:
- The only off-grid values, p = 0.95, are hopeless.
- The best setting found is (0.8, 0). The study screened it but did not test it. It is 6% below the study's
  best value. It is 11% below the referee's own run of that setting, but with an interval of
  [0.70, 1.18], and it was picked as the minimum of 20 settings on the test instances.
- The referee's runs of the three tested settings match the study's values within noise: 1.06, 0.95 and 1.08
  times.
- Even taking (0.8, 0) at face value, R for D becomes 354,345 / 399,798 = 0.886, against the study's 0.833.

## `heavy`, α = 3.0, n = 3200

**Verdict: No.**

The grid was p ∈ {0.5, 0.55, …, 0.9} × wp ∈ {0, 0.005, 0.01}, 113 s. The study's cap of 2e8 ran past 10
minutes on the p ≥ 0.75 settings, so the grid used a budget of 1e6 flips, about 110 times the best
median. No run at p ≤ 0.7 hit the budget, so those values are exact.

The study's best is (0.6, 0) at 8,837. D's figure is 0.724 × 8,837 = 6,396.

| Setting | Status | Referee geo-stat | / study's best | / referee's run of (0.6, 0) |
| --- | --- | ---: | ---: | --- |
| (0.55, 0.01) | off-grid | 8,874 | 1.00 | 0.94 [0.85, 1.07] |
| (0.55, 0.005) | off-grid | 9,092 | 1.03 | 0.96 [0.86, 1.09] |
| (0.55, 0) | off-grid | 9,250 | 1.05 | 0.98 [0.88, 1.16] |
| (0.6, 0) | tested | 9,483 | 1.07 | 1 |

The rest of the grid:

| p | Geo-stat | Note |
| --- | --- | --- |
| 0.5 to 0.65 | 9,354–10,461 | |
| 0.7 | 20,753–25,083 | |
| 0.75 to 0.9 | ≥ 1 million | Lower bound: no run solved within 1e6 |

R for D against the best setting found is 6,396 / 8,874 = 0.721, unchanged from the study's 0.724.

## A caution for both families

Novelty+ has a sharp limit in p that depends on the meeting pattern:
- **`local`**: fine at p ≤ 0.85, fails at p ≥ 0.9.
- **`heavy`**: fine at p ≤ 0.7, fails at p ≥ 0.75.

A grid that steps over the limit costs the hand-written side little, as here. But a run time capped by flips
can hide a setting that never finishes.
