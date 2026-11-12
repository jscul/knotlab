# Referee job OLD-CORE-R1: the brief

The coordinator handed this job over on 2026-11-12 (16:26 UTC). It comes from the random-meeting-patterns thread:
`OLD-CORE-20261112-001` (B170), in commits 82732261e and 3b3edd088, pre-registered in a813eb17d. The census imports RANDOM-FATES' frozen
`fates.py`. Its records cover 498 of the 500 growths.

## Claims under review

All are computed and frozen.

| # | Claim | Outcome |
| --- | --- | --- |
| L1 | The median P_u (uniform resamples with the dying core's k* and m*) is 0 in X(0.3), X(0.35), Og(0.3) and Ol(0.3). D* is 1.55, 1.67, 1.66 and 1.74. | failed |
| L1p | After peeling, P_u2 is 0 for both X processes, 0.225 for Og and 0.425 for Ol. The peeled D2 is 1.70 and 1.81 for X, and 2.05 and 2.10 for O. | failed |
| L2 | The median P_d (degree-matched resamples) is 1.0 for O and 0 for X. | failed both ways |
| L3 | k*_deg ≤ k* in 82 to 88% of growths. | held |

**Also reported.** The median of k* over the floor is 1.0, except 1.17 at X(0.3). X(0.25) ends in 8 of 100 growths by 6,000
moves.

## The coordinator's checks

1. **The degree-matched generator.** `degree_pattern` shuffles stubs and repairs them by stub swaps. Is it a fair configuration model
   with repeats removed, given that O cores have a few very knotted distinctions? Does any bias change L2?
2. **The two stopped O global growths.** They were stopped after 90 minutes. Could they change a verdict, and is stopping them a
   selection on outcome?
3. **Known against new.** Uniform and degree-dependent thresholds, and grown-network effects, are known. Claimed as new: grown NAE
   patterns end below the uniform end; degrees explain the overlap growth's end but not the expanding growth's; the expanding
   growth's critical closing rate lies between 0.25 and 0.3.
4. **The dying core.** Is it identified the same way in every process? Is D* in the arithmetic band for X settled by definition?
