# Referee job AGE-NEST-R1: the brief

The coordinator handed this job over on 2026-11-12 (16:38 UTC), to follow OLD-CORE-R1. It comes from the random-meeting-patterns
thread: `AGE-NEST-20261112-001`, in commits b949770f9 and 6fa86e8c6, pre-registered in 283e418e9. The census loads OLD-CORE's
`census.py`, regenerates its X endings, and holds out 12 pilot endings.

## Claims under review

**Fairness, computed exactly** on 5 enumerated degree sequences (17 to 16,534 patterns). The transition matrices of SW (degrees kept)
and R2 (degrees and each knot's youngest member kept) are symmetric, and connected within the classes they preserve.

| # | Claim | Outcome |
| --- | --- | --- |
| N1 | The median P_SW is 0 at X(0.3) and X(0.35); the 90th percentiles are 0.05 and 0.3. | held |
| N2 | The median P_R2 is 0.4 and 0.5; among untied cores, R2 > SW in 95% (76 cores) and 92% (84 cores). | held |
| N3 | R2p (youngest kept, degrees free) gives 0.4 and 0.55; FULL (the growth's own schedule) gives 0.35 and 0.575. Each ties R2 in about half the cores, and every rung's share with the same pair counts is 0. | reported |
| Q0 | All 104 Pasch trades keep the pair counts and stay without a state. | held |

## The coordinator's checks

1. **Mixing.** The chains start from the real core and run 20·m steps, and mixing on the real heavy-tailed cores is not proven. Do the
   results move with longer chains or independent starts?
2. **R2's move rule.** It swaps only the two older members, and only if each stays older than its new triple's youngest. Does it keep
   every prefix count?
3. **`redraw_full`'s schedule reconstruction.**
4. **Is "the nesting by age carries the end" fair,** given that R2p ends as often as R2? Is it settled by definition or known? For
   instance, does a pattern with those prefix counts simply contain an early part dense enough to pass the known uniform threshold?
5. **The held-out pilot handling,** and whether tied cores are excluded fairly.
