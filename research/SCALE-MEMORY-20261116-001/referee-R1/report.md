# Referee report SCALE-MEMORY-R1 (fresh code, no Codex; the n = 51,200 stress cell is not refereed)

**Verdict: Confirmed with fixes. No Block.** The headline holds: memory reads that count no steps carry the agent to parity with
re-tuned Novelty+ at 4 and 16 times its training size, not to a win. Every frozen number recomputes, the gate passes and the
freeze preceded every training. Fixes:
- **L3m is inconclusive, not a clean loss.** The frozen seed-agreement clause fails: its seeds read 0.86 and 2.06 around the 0.9
  line. **Narrowing.**
- **The frozen comparator at 12,800 was weaker than the best Novelty+.** By 10 to 15%, confirmed in an independent engine, which
  flatters the frozen R there. The study's
  post hoc check already shows it. Say so beside the frozen 0.82. **Narrowing** (wording).
- **The script that made `posthoc_summary.json` is not committed.** **Not a block**, but the record should hold it.

## What holds

- **The freeze.** The pre-registration commit 40cf4237c is at 00:02:01 UTC on 2026-11-17.
  - The first training launch was created at 00:02:07, stopped, and relaunched at 00:02:39 after the one post-freeze code change
    (40d76bfec, 00:02:39). That change only restores SIGTERM in the trainer's pool and touches no result.
  - The post hoc job (2552bef06, 04:11 UTC) is labelled "not part of the frozen protocol". It uses fresh run seeds,
    `run_seed("posthoc", n, s, rep)`, distinct from the frozen `run_seed("test", …)`.
- **The gate.** `check.py` passes, G0–G6, including G6: this engine reproduces WHERE-NEXT's run for run on 108 runs. That licenses
  reusing WHERE-NEXT's rule runs and L3 seed 1.
- **The flag-16 code is as described.**
  - A distinction's age is read over the oldest of the knot's three, and a candidate's visit age over the oldest candidate's; never
    flipped or visited counts as t + 1.
  - The violated count is read as 10 × violated / knots, clipped at 1.
  - The 50-step counts are kept, as the limits say.
- **The headline, recomputed with the referee's own code** (`referee_R_scale.py`, `.json`). Inputs: this study's `test/`,
  WHERE-NEXT's `test/` and `stress/`. Arm flips are the geometric mean of the two seeds' medians, and R is taken against the best
  re-tuned rule, re-chosen in each of 10,000 paired resamples, with 99% intervals:

  | Cell | L3 | L3s | L3sm | L3m | L3c | L2m |
  | --- | --- | --- | --- | --- | --- | --- |
  | `rand` 800 | 0.656 | 0.664 | 0.712 | 0.694 | 0.702 | 2.16 |
  | `rand` 3200 | 1.358 [1.12, 1.63] | **0.938 [0.80, 1.11]** | 0.941 [0.80, 1.10] | 0.946 [0.81, 1.16] | 1.158 [0.97, 1.42] | 2.81 |
  | `rand` 12800 | 14.54 [10.6, 22.0] (seeds 84.1, 2.51) | 0.863 [0.76, 0.98] | **0.816 [0.727, 0.904]** | **1.334 [1.12, 1.57] (seeds 0.86, 2.06)** | **2.675 [2.20, 4.02] (seeds 4.59, 1.56)** | **2.55** |
  | `local` 3200 | 25.6 | 28.6 | 13.3 | 11.6 | 22.0 | 4.68 |

  Bold marks each new arm's primary cell. The ratios are S = 0.059 [0.039, 0.081], T = 0.092 [0.059, 0.131], C = 0.499
  [0.339, 0.626], L3sm / L3s = 0.946 [0.852, 1.061], L3sm / L3m = 0.612 and K = 0.523 [0.444, 0.608] at 12,800, and L3s / L3 = 1.012
  at 800 (P1). All of these match `summary_pilot.json` and the note.
- **The gates** (`gates.json`). G-learn passed for L3s, L3sm, L3m and L3c and failed for L2m (2.28, 2.12). G-train passed for L3m
  and L3sm and failed for L2m seed 1, as reported.
- **The verdicts that stand.**
  - L3s and L3sm: inconclusive. L3sm misses the flips-win line narrowly, at 0.816 against "≤ 0.8 with upper end < 0.9".
  - L3c: clean loss. Its lower end is 2.20 > 0.9, both seeds are above 0.9, and G-learn passed. G-train does not apply to its
    800-only last stage.
  - L2m: learner failure.
  - P1, P2, P3c, P6 and P7 held, and P4 failed. P3 held by its interval, but L3m's seeds disagree, as the note says.
  - No CPU win.
- **The post hoc check, recomputed** (`referee_posthoc.py`, `.json`). The study's statistic is the median over instances of each
  instance's geometric mean over its five runs, and it reproduces exactly (74,158.16, 63,419.13, 363,538.68 for the arms tried).
  On a pooled median over all 500 runs instead, the referee gets:

  | | n = 3200 | n = 12800 |
  | --- | --- | --- |
  | L3s / best Novelty+ | 0.855 [0.80, 0.91] | 0.973 [0.93, 1.03] |
  | L3sm / best Novelty+ | 0.875 [0.84, 0.93] | 0.923 [0.89, 0.97] |

  Both summaries say parity with at most a small margin and no flips win (nothing ≤ 0.8). The study's "0.88 to 1.01" is its
  statistic's range; on pooled medians the range is 0.85 to 0.97.
- **Post hoc labelling.** "Post hoc" or "five-run check, not frozen" appears beside every use in the note, the decision, the goals
  checkpoint and the objects row. The intuition entry gives one combined range ("about 0.8 to 1.0 times") without the label.
  Acceptable for that register.
- **Prior work.** `objects-gate`: "prior-work line: ok".
- **Words.** No spatial word for the program's objects.

## 1. L3m: inconclusive, not a clean loss (the frozen seed-agreement clause)

The frozen rule ("Measures", "Seed agreement") says: *"A claim holds only when the arm-level interval satisfies it and both seeds'
point values lie on the same side of its threshold."*
- **The interval.** L3m's 12,800 interval, [1.12, 1.57], satisfies clean loss (lower end above 0.9).
- **The seeds.** Its seeds read 0.86 and 2.06, on opposite sides of 0.9. So by the frozen rule the clean-loss claim does not hold,
  and L3m is **inconclusive**.
- **What the note says.** It reports "L3m … clean loss" and in the same breath "L3m's seeds disagree (0.86 and 2.06)".
- **What it changes.** The diagnosis's P3 (T = 0.092) is unaffected as stated, but it too rests on an arm whose seeds disagree.

**Narrowing**, a correction for docs/CORRECTIONS.md.

## 2. The frozen comparator was weaker at 12,800

- **At 12,800.** The frozen re-tuned Novelty+ is WHERE-NEXT's (0.7, 0.05), at 416,258, from single runs. In the post hoc check the
  best Novelty+ is (0.7, 0.01) or (0.7, 0) at about 362,000 to 368,000, so the frozen comparator is about 13% weaker. That accounts
  for most of L3sm's move from 0.82 (frozen) to 0.92 to 0.94 (post hoc).
- **At 3,200.** The frozen comparator, (0.7, 0.01) at 72,276, is about as good as the best (0.7, 0), with medians within 1 to 3%.

So the frozen R is fair at 3,200 and flatters the agent at 12,800. The frozen verdict, inconclusive, is unchanged.
**Narrowing** (wording): say beside the frozen 0.82 that the comparator lacked walk probability 0.01 and 0 at that cell.

## 3. Independent cross-check of the comparator and the reads (helper, `NOTES_comparator.md`)

**The comparator, rerun in the helper's own engine** (`referee_comparator.py`): Novelty+ on the same 100 test instances, with the
study's post hoc statistic.

| n | (0.7, 0) | (0.7, 0.01) | (0.7, 0.05) |
| --- | ---: | ---: | ---: |
| 3200, referee (5 runs) | 72,434 | 72,293 | 82,162 |
| 3200, study post hoc | 71,960 | 74,046 | 87,876 |
| 12800, referee (3 runs) | 361,874 | 373,847 | 398,899 |
| 12800, study post hoc | 363,539 | 367,547 | 416,884 |

- **Agreement.** All six values are within 7% of the study's.
- **At 12,800.** The frozen setting (0.7, 0.05) is 1.10 times [1.04, 1.19] the best of the other two, or 1.12 [1.07, 1.19] pooled.
  The frozen single-run 416,258 is 1.15 times the referee's best. So the frozen comparator was weaker by 10 to 15%, confirming §2.
- **At 3,200.** (0.7, 0.05) is also 1.14 times worse, but the frozen comparator there was (0.7, 0.01), which matches the best.
- **One caution.** Plain Novelty+ with walk probability 0 stalled at the cap on 1 of 500 runs at 3,200. The median is unaffected,
  but (0.7, 0.01) is as fast and does not stall.

**The new reads are nearly scale-free** (`referee_relage.py`). The relative age of the attended knot's distinctions was measured on
20 instances per size at n = 200, 800, 3,200 and 12,800.
- Its median is 0.32, 0.26, 0.25 and 0.24, and the fraction exactly 1 is 0.36, 0.34, 0.34 and 0.34.
- Its distribution moves by at most 0.018 from 800 up, while the clipped log age's share beyond the clip goes from 10% to 63%.
- The one drift is at the bottom: a distinction flipped one step ago reads 1/max, so the share below 0.001 rises from 0.3% to 4.7%.
  This is small, and worth knowing for the degree-normalized follow-up.

## Fixes for the thread (listed for the owner, not folded in)

1. **L3m: "clean loss" → "inconclusive (seeds disagree: 0.86 and 2.06)"** in the note, the decision and the goals and objects
   rows. **Narrowing.**
2. **Beside the frozen L3sm 0.82 at 12,800,** say the frozen comparator was 10 to 15% weaker than the best Novelty+ there, so the
   five-run 0.92 to 0.94 is the better reading. **Narrowing** (wording).
3. **Commit the script that wrote `posthoc_summary.json`,** and name its statistic: the median over instances of the per-instance
   geometric mean of five runs. **Not a block.**
4. **The 51,200 cell** is pending and was not refereed. P5 stays pending.

## How the work was split

- **The referee.** Read the pre-registration, the note, the decision and the flag-16 code. Reran the gate. Recomputed every frozen
  ratio and the post hoc check with own code. Checked the freeze timing, the gates, the labelling, the objects gate and the words.
- **One Claude helper,** the WHERE-NEXT referee's baseline helper with its own C engine. Cross-checked the Novelty+ comparator at
  3,200 and 12,800 and the scale-free reads (`NOTES_comparator.md`).
- **Codex** was not used. **The advisor** was not consulted.

## Files

- `referee_R_scale.py` and `.json`: the frozen recomputation.
- `referee_posthoc.py` and `.json`: the post hoc recomputation.
- The helper's `NOTES_comparator.md` and `referee_*`.
