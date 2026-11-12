# Referee job RANDOM-FATES-R1: the brief

The coordinator handed this job over on 2026-11-12 (08:14 UTC). It is stage 1's census (ticket A) of `RANDOM-FATES-20261112-001`,
closed "referee pending" (epic ef3948363, documents 8b6d40e5b). Ticket B and stage 2 were refereed in that thread and are out of
scope. The thread's next step does not depend on the verdict.

## Claims (all computed against frozen predictions unless marked)

1. **Outcomes by process (P4).** X(q) is still a base at 2,000 moves in 100% of runs at q ≤ 0.2 and in none at q ≥ 0.35. O global
   (0.3) is still a base in 6% of runs and O local (0.3) in 0%. Newest-five and newest-six growth end in 99 to 100% of runs at
   q ≥ 0.5. Uniform patterns end at a median of 2.09 to 2.16 knots per distinction.
2. **The ruler away from the end (P1).** The least bond at d steps has d + 2 members for 96 to 100% of pairs at n = 200 and 300,
   d ≤ 3, f = 0.5 and 0.75. It fails at n = 100, f = 0.75, d = 3 (86%).
3. **The uniform end is a jump of fixed length in knots (P2), and its minimal contradictions are large (P3).** The largest tie class
   at k = 50, 20, 10, 5 and 1 knots before the end holds shares that are the same at every n from 50 to 300. Minimal contradictions
   hold 55%, 73% and 86% of the knots at n = 50, 100 and 200.
4. **Growth with new distinctions (P5c).** Last bases of X and O growth have a largest tie class of at least 10% of the distinctions
   in 99% of cases, already 0.2 to 0.43 at k = 50. The whole-life trajectories are exploratory.
5. **Endings among the newest distinctions (P5a, P5b).** Newest-w endings come from minimal contradictions of 10 to 12 knots. P5b
   failed (Spearman 0.61).
6. **Living patterns as rulers (P6).** P6 failed only at Og(0.1), d = 3. The ratio B3/B1 runs from 43 to 150.
7. **Newest-four survivors (P7).** Shortcuts at d = 2 and 3 occur in 73% and 94% of pairs; ties reach at most 8 steps.

## Known issues to check

- **The guarded summary.** It should differ from `census.py` by one guarded line.
- **The resume.** The registered unit stopped at its 4-hour cap with 969 of 2,990 runs written, and `resume_driver.py` ran the rest.
  Check that it used the same frozen code and seeds, and neither double-counted nor skipped a run.

## The coordinator's questions

- Are the partly failed predictions (P1, P5, P6) reported with the same weight as the ones that held?
- Is "independent of n" supported by the spread, or only asserted?
- Is anything exploratory worded as registered?
