# Referee report WHERE-NEXT-R1: the navigating-agent study (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.** The frozen verdict stands, and better estimates make it firmer: a clean loss on the
primary cell (`rand` n = 3200) and on both secondary cells. The engine, the baselines, the seeds and the headline recomputation all
check. Two things need restating:

- **The win at the training sizes is real but overstated.**
  - **True size.** Against a well-tuned Novelty+, with run noise averaged out, L3 takes about 0.71 and 0.77 times the flips at
    n = 200 and 800, that is 1.3 to 1.4 times fewer. The study says 0.45 and 0.60, that is 1.7 to 2.2 times fewer.
  - **Why the gap.** About half of it, in log terms, comes from one run per instance and a coarse re-tune. **Narrowing.**
- **The loss at larger sizes is a fair test of this agent, not of learned memory.** The memory features, counted in steps and
  clipped at 1,000, saturate as n grows, while the same ages divided by n stay nearly constant. That supports the study's own
  untested hypothesis and its next step. The goal-level wording "obstruction learned" should say so. **Narrowing** (wording).

## What holds

- **The gate.** `check.py` passes: G0–G5, in 8 s.
- **Reproducibility.** Rerun in the study's engine with the study's own run seeds, L3 reproduces `test/results.jsonl` exactly on
  100 of 100 instances at each of n = 200, 800 and 3200.
- **The headline, recomputed by the referee from the raw results with fresh code** (`referee_R_M.py`, `referee_R_M.json`):

  | Cell | L3 | Best re-tuned rule | R [interval] | M [interval] |
  | --- | ---: | ---: | --- | --- |
  | `rand` 200 | 782.5 | Novelty+ 1,738.5 | 0.450 [0.327, 0.618] | 0.357 [0.229, 0.510] |
  | `rand` 800 | 9,060.5 | Novelty+ 15,073 | 0.601 [0.440, 0.836] | 0.305 [0.241, 0.431] |
  | **`rand` 3200** (95%) | 77,115.5 | Novelty+ 72,276 | **1.067 [0.903, 1.213]** | 0.370 [0.305, 0.435] |
  | `rand` 12800 | 975,317 | Novelty+ 401,581 | 2.429 [1.729, 4.286] | 0.960 [0.709, 1.725] |
  | `local` 200 | 4,217 | Novelty+ 1,591.5 | 2.650 [0.943, 5.563] | 0.824 [0.303, 1.918] |
  | `local` 800 | 741,703 | Novelty+ 39,578.5 | 18.74 [11.50, 35.21] | 2.839 [1.573, 5.855] |
  | `local` 3200 | 32,878,164 | Novelty+ 596,669.5 | 55.10 [31.18, 95.19] | 4.694 [2.423, 8.432] |

  Secondary cells use 98.3% intervals. The best rule is re-chosen in every one of 10,000 paired resamples. All values match
  `summary.json`.
- **The primary verdict.** Its interval's lower end is 0.904 to 0.909 over 20 bootstrap seeds, never at or below 0.9. So "clean
  loss" is not a bootstrap accident, though it sits at the margin, as the note says.
  - Against the training-tuned comparator it would be inconclusive (0.963 [0.819, 1.093]). The frozen rule uses the re-tuned one.
  - With five runs per instance and a wider tuning (below), R = 1.10 [1.02, 1.19], which is firmer.
- **No leakage.** The seed ranges are disjoint: training pool 1,000,000–1,001,999, validation 2,000,000+, test 3,000,000–3,000,099
  (`rand`) and 3,500,000–3,500,099 (`local`), re-tuning 4,000,000–4,000,015 and 4,500,000–4,500,015, training-tuning 1,000,000–1,000,063
  (training pool). The generator's hash also includes n, so equal numbers at different sizes are different instances. Every arm
  shares a run seed, and so an initial state, per instance (`test_job.run_seed`).
- **Fairness checks.**
  - The caps are identical across arms in every cell.
  - Each first tuning grid is a subset of the widened one, so the widening only enlarged the hand-written side's choices.
  - The re-tune searched the stated neighbours.
- **The baselines match an independent implementation.** The helper's own C engine has its own occurrence lists, RNG and
  tie-breaking.
  - It reproduces WalkSAT, probSAT and Novelty+ in 32 cell and parameter comparisons. Every pooled median ratio has a 95%
    interval containing 1 (points 0.73 to 1.23, with no direction).
  - The local 3200 Novelty+ median is 599,670 against the study's 596,670, so R = 55 stands on a correct baseline.
  - All 810 instances used were checked as correctly planted.
- **The engine's rules are the published ones.**
  - WalkSAT/SKC: a free move, else noise, else least break.
  - probSAT: (ε + break)^(−cb).
  - Novelty+: break − make, ties to the oldest, the second best with probability p when the best is the most recently flipped,
    and a walk probability.
  - NAE break and make are right: a satisfied knot breaks when v is its only 1 or its only 0, and every violated knot of v is made.

## 1. Is the win at the training sizes real? Yes, but about 1.3 to 1.4 times, not 1.7 to 2.2

**Method** (helper, `referee_task2_*`, `referee_L3_rerun.*`).
- **Tuning.** Novelty+, Novelty++, probSAT, WalkSAT and Adaptive Novelty+ were tuned widely on separate instances (seeds 4,000,000+).
- **Rules on test.** The tuning-selected settings were run five times per test instance.
- **L3 on test.** L3, the thing under test, was rerun five times per test instance with fresh seeds in the study's engine.

| | n = 200 | n = 800 | n = 3200 |
| --- | ---: | ---: | ---: |
| Study's ratio, Novelty+ / L3 (one run per instance) | 2.22 | 1.66 | 0.94 |
| Tuning-selected Novelty+ / L3, five runs each | **1.40 [1.16, 1.59]** (0.675, 0.01) | **1.30 [1.15, 1.40]** (0.675, 0.01) | **0.91 [0.84, 0.98]** (0.7, 0) |
| The same as R = L3 / rule | ≈ 0.71 [0.63, 0.86] | ≈ 0.77 [0.71, 0.87] | ≈ 1.10 [1.02, 1.19] |
| Best of the top five on the test instances (light test selection) | Novelty++ 1.23 [1.03, 1.43] | Novelty+ 1.22 [1.12, 1.34] | 0.91 |

**Where the published gap came from**, at n = 200: L3's single draw was low (782.5 against 886.5 over 500 runs), Novelty+'s was
high (1,738.5 against 1,424 for the same parameters), and the re-tune was coarse: walk probability at least 0.01, five neighbours,
16 instances. Together that is 1.13 × 1.22 × 1.14 ≈ 1.57 of the 2.22.

**The bootstrap does not cover this.** Resampling instances does carry the noise of one run per instance. But the comparator's
tuning error is outside the interval, which is why the published [0.33, 0.62] at n = 200 excludes the better estimate of 0.71.

**So the win is real.** No honestly tuned standard rule comes within 1.2 times of L3 at n = 200 or 800. It is not a tuning
artefact, but it is smaller than published.

**P2 would have held.** P2 (R in [0.7, 1.1] at n = 200) is recorded as "failed, the other way". As computed under the frozen
protocol that verdict is correct, but on these better estimates it would hold narrowly (0.71). **Not a block**: the frozen
verdict stands as computed. The note should record the estimate.

**Aside.** Adaptive Novelty+ at its published defaults is poor here (19.4 M flips at n = 3200). It is not a stronger baseline.

## 2. Is the loss at larger sizes a fair test of the idea?

**It is a fair test of this agent, and of features counted in steps, trained on n ≤ 800.** It is not a test of learned memory as
such. The helper measured the features' regime in Novelty+ runs, a proxy for L3's own trajectories, which the engine cannot log
(`referee_task3_memory_scale.*`):

| | n = 200 | 800 | 3200 | 12800 |
| --- | ---: | ---: | ---: | ---: |
| Member ages above 1,000 steps, or never flipped | 7.5% | 24% | 45% | 65% |
| Median member age (steps) | 56 | 142 | 720 | 2,976 |
| Median age / n | 0.28 | 0.18 | 0.23 | 0.23 |
| Median clipped age feature (1 = saturated) | 0.58 | 0.72 | 0.95 | 1.00 |
| Median decayed flip count (τ = 50) | 0.45 | 0.08 | ≈ 0 | ≈ 0 |
| Attended knot's visit age above 1,000 | 20% | 33% | 62% | 85% |

**The features saturate.**
- By n = 3200 the absolute age and count features carry almost no information: they read "long ago" and zero.
- Age divided by n stays near 0.2 at every size.
- The rank features are scale-free, but the network evidently leaned on the absolute ones.
- This fits the study's hypothesis exactly, and its proposed next step: scale-free memory, mixed training sizes.
- The memory gain fades with the same timing: M = 0.36 and 0.31 at n = 200 and 800, 0.37 at 3200 where saturation is half done, and
  0.96 at 12800.

**On `local`, a second change.** Each distinction is in about 12 knots rather than 6.3, so counts per step also mean something
else there. A degree-normalised count belongs in the follow-up as well.

**The study's own wording is fair, with one exception.**
- The note says "what it learned does not carry over" and gives the step-count explanation as untested. Fair.
- The decision's G15/G16 line, "obstruction learned", should be scoped: "for memory features counted in steps and training at
  n ≤ 800". **Narrowing** (wording).

## 3. Prior work and words

- **The objects gate passes:** `track.py objects-gate` on the pre-registration prints "prior-work line: ok".
- **The referee's literature search** (other words: learned unsatisfied-clause selection in stochastic local search, reinforcement
  learning). It found learned *variable* selection inside a randomly chosen clause:
  - Interian and Bernardini, arXiv 2307.04608, which exists and matches the citation;
  - Yolcu and Póczos 2019;
  - work on adding CDCL-learned clauses to local search (2020).

  It found no learned choice of *which violated clause* to attend to. That is consistent with the study's "not found" claim, but
  the search was not exhaustive.
- **The citations checked.** Interian–Bernardini is right. The others are standard and stated from memory, as the study says.
- **Words.** The notes use the glossary's words. One loose word: "the walk takes more steps to come back to a region"
  (`where_next.md`), better "to the same distinctions". "Edge" there is a tuning grid's edge, which is fine. **Not a block.**
- **Not rechecked.** CPU per flip, which is machine-dependent and was measured under load, and incidences per flip.

## Fixes for the thread (listed for the owner, not folded in)

1. **Restate the training-size win.** Against a well-tuned Novelty+ with run noise averaged, L3 takes about 0.71 and 0.77 times
   the flips at n = 200 and 800, that is 1.3 to 1.4 times fewer, not 0.45 and 0.60 (1.7 to 2.2 times).
   - Keep the frozen R as the protocol's value.
   - Add the referee's estimate wherever the win is summarised: decision, `where_next.md`, final report, goals and intuition
     lines.
   - **Narrowing**, a correction for docs/CORRECTIONS.md.
2. **Record P2's sensitivity.** The frozen verdict, "failed the other way", stands as computed, but better estimates put R at
   n = 200 at about 0.71, narrowly inside P2's range. **Not a block.**
3. **Scope the goal-level "obstruction learned".** Scope it to step-counted memory features trained at n ≤ 800. Cite the saturation
   table as evidence for direction #1.
   - **Narrowing** (wording).
   - Suggested for the follow-up: memory reads divided by n, and counts divided by degree, with mixed sizes.
4. **The primary cell.** Note that the clean loss is firmer on better estimates (R = 1.10 [1.02, 1.19]) and is not an artefact of
   the bootstrap: the lower end is 0.904 to 0.909 over 20 seeds. **Not a block** (it supports the verdict).
5. **Wording.** "Region" → "the same distinctions". **Not a block.**

## How the work was split

- **The referee.** Read the decision, the note, the pre-registration and the engine (rules, features, run seeds). Reran the gate.
  Recomputed R and M with own code. Audited the seeds, caps and grids. Ran the objects gate and one literature search.
- **One Claude helper.** Wrote an independent C engine for the baselines (`referee_sls.c`), a wider tuning, the saturation probe
  and the L3 reruns. It used the study's `engine.planted` to regenerate the instances and checked each one independently
  (`NOTES_baselines.md`).
- **Codex** was not used. **The advisor** was not consulted.

## Files

- `referee_R_M.py` and `.json`, `referee_primary_lower_end_spread.json`: the referee's own checks.
- `NOTES_baselines.md`, `referee_sls.c`, `referee_common.py` and the `referee_task*` and `referee_L3_rerun` scripts with their JSON:
  the helper's checks.
