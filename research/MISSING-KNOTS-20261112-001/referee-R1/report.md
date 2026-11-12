# Referee report MISSING-KNOTS-R1: the law's count of missing knots

**Verdict: Confirmed with fixes.**
- **Everything reproduces.** I regenerated all 110 bases from the seeds with my own generators. All 4,400 pairs and their counts M,
  D, M3, M4 and W2 match the records. My own exact search agrees on the least bond wherever it can reach (634 pairs, no disagreement).
  Every slope and verdict recomputes.
- **M2r was frozen in advance,** with its bound of 0.8, before the run. It is not a rescue. But its pass is a coin flip: the 95%
  interval of the ratio is 0.74 to 0.86, and only 53% of bootstrap resamples fall at or below 0.8. Its gloss in the pre-registration
  also points the opposite way to its inequality.
- **M1 is a replication, as the advisor said.** Within each cell M follows the gap almost exactly (R² 0.91 to 1.00). So the slope on M
  is the slope on the gap, rescaled by the density.
- **M's real merit lies across cells.** Its slope varies by 9.6% across cells, against 60% for the gap, which M4 did not compare.
- **M3's failure at q = 0 and 0.1 is mostly a lack of variation,** not a failed unit.

Referee: the background referee thread, 2026-11-12. My code is `ref_missing.py`. It imports none of `census.py`, `fates.py` or
`bonddp.py`. It uses:
- RANDOM-FATES-R1's `gen_newest`, which draws in the frozen order of `proc_band`;
- the band as defined;
- RANDOM-FATES-R1's exact least-bond search, sizes 2 to 5, with members within 8 of the pair, as the census's margin.

Validation: V2. The advisor model was not consulted for this job.

## 1. What reproduces

**The regeneration.**
- All 110 bases have the recorded number of knots.
- All 4,400 between-cell pairs fall at the recorded positions.
- M, D, M3, M4 and W2 match the record on every pair.

**The least bond**, checked independently where my search reaches:

| Recorded L | Pairs checked | Result |
| --- | --- | --- |
| 2 to 5 | 300, in 9 cells | the same value in every case |
| above 5 | 334, gaps up to 40 | no bond of 5 or fewer in every case |

There is no disagreement. The census's dynamic programme was also refereed against brute force in RANDOM-FATES-C.

**The slopes** (least squares with an intercept, on the pairs with a bond):

| Cell | Slope on M (bootstrap 95% over bases) | Slope on the gap | R² of M on the gap |
| --- | --- | --- | --- |
| newest-four, q = 0 | 0.115 (0.110 to 0.119) | 0.310 | 1.000 |
| q = 0.1 | 0.118 (0.117 to 0.121) | 0.292 | 0.998 |
| q = 0.3 | 0.114 (0.107 to 0.118) | 0.236 | 0.996 |
| q = 0.5 | 0.113 (0.110 to 0.116) | 0.171 | 0.990 |
| q = 0.7 | 0.109 (0.103 to 0.115) | 0.089 | 0.960 |
| q = 0.9 | 0.098 (0.091 to 0.105) | 0.024 | 0.911 |
| band, p = 0.5 | 0.112 (0.107 to 0.114) | 0.220 | 0.995 |
| p = 0.6 | 0.106 (0.103 to 0.111) | 0.168 | 0.995 |
| p = 0.7 | 0.098 (0.095 to 0.100) | 0.116 | 0.993 |
| p = 0.8 | 0.088 (0.085 to 0.091) | 0.071 | 0.974 |
| p = 0.9 | 0.089 (0.083 to 0.095) | 0.035 | 0.949 |

**The verdicts.**
- **M1** held: pooled R² 0.986.
- **M2** failed: the band's slopes at p = 0.8 and 0.9 lie below 0.09, and their intervals exclude the registered band.
- **M3's within-base medians** match: −0.23, 0.056, 0.127, 0.113, 0.117, 0.118 on newest-four growth, and 0.138, 0.088, 0.111, 0.089,
  0.082 on the band.
- **M4's coefficients of variation** across cells match: M 9.6%, D 11.4%, M3 27%, M4 17%, W2 22%.

There are no deviations to check. The run followed the frozen code.

## 2. (ii) Was M2r a rescue?

**No.** M2r is in the pre-registration as committed in 68f4ef038, at 00:36 PST. It is worded as "rival (registered against M2)",
with "at most 0.8 times" fixed. The census's records are from 00:47, and the epic was committed at 00:49. The pre-registration file has
no later change.

**Two qualifications.**
1. **The pass is not resolved by the data.** The ratio is 0.795. Resampling bases within the two cells gives a 95% interval of 0.74
   to 0.86, and 53% of resamples are at or below 0.8. "Held, just" should read "at the bound, within noise: the data do not decide
   M2r".
2. **The registered gloss is reversed.** The pre-registration glosses M2r as "missing knots cost more where they are isolated". The
   inequality it registers (a smaller slope at p = 0.9, where missing knots are isolated) says they cost less. The note's reading,
   "missing knots cost less where they are isolated among present ones", follows the inequality and the data. It should say that
   the registered gloss pointed the other way.

## 3. (i) What is settled by definition or by selection

**M1 within a cell is the gap, rescaled.** Within each cell M is nearly proportional to the gap: R² 0.91 to 1.00 on the pairs with a
bond. So "L is linear in M" within a process says no more than "L is linear in the gap". That replicates RANDOM-FATES-C.

Pooled across the six newest-four cells, R² is 0.986 on M against 0.38 on the gap. So M's content is how it absorbs the density
across cells.

**M4 should include the gap.** Across the cells with at least half their pairs bound, the slope on the gap varies by 60%, against
9.6% on M. That comparison is what shows M to be the right kind of count. The frozen M4 compared only M against its four variants.

**M3 at low closing rates measures little variation.** At q = 0 every window lacks most knots, so across a base's eleven stretches of
64, M varies very little. The slope of L on M is then poorly determined: −0.23 at q = 0, where only 8 bases qualify, and 0.056 at
q = 0.1.

The note's explanation fits. The failure says that within a base at low q, M carries no information, not that a unit fails. M3's
eligibility rule (at least five bases with at least six stretches) admitted those cells.

**Selection by pairs with a bond.** Slopes are fitted on pairs whose least bond lies within the margin:
- 55% of pairs at q = 0 and on the band at p = 0.5;
- all of them at q = 0.9 and on the band at p ≥ 0.8.

The undefined pairs are those whose bonds lie farther out, likely the high-L ones. So the low-density slopes may be biased, in an
unknown direction, as the advisor warned. This cannot be checked without larger margins, and it is not tested here.

## 4. (iv) Known mathematics

**What is known.** In a bandwidth-3 system of not-all-equal knots, the states form a one-dimensional constraint system with a finite
transfer matrix: a sofic shift, or a Markov chain on windows. Influence between distant distinctions, and the cost of correlating
them, is set by products of local transfer matrices. A linear growth of the least bond with distance is the expected behaviour.
A cost per gap that depends on its neighbours is exactly what transfer matrices predict: the effect of a missing knot depends on
the local window structure.

**What is not known.** I found no result on least non-shattered sets through two vertices of a banded hypergraph. The census's
literature line ("not found") stands for the specific count.

**Classification.** Known in mechanism (one-dimensional transfer). The counts, slopes and the failure of a fixed unit are new data.
This epic does not involve the uniform 2-colouring threshold or the giant component.

## 5. Fixes for the thread

1. **M2r.** Say that it was frozen before the run, with its 0.8 bound fixed, and that the ratio 0.795 has a 95% interval of 0.74 to
   0.86 (53% of resamples at or below 0.8), so the rival is not decided. Note that the registered gloss ("cost more where isolated")
   points the other way to the registered inequality, which the note's reading follows. **Narrowing** (Overreading: a pass within noise).
2. **M1 and M4.** Within a cell M follows the gap (R² 0.91 to 1.00), so M1 replicates the gap fit. M's merit is across cells:
   slope CV 9.6% against 60% for the gap. Add the gap to M4's comparison. **Not a block.**
3. **M3.** At q = 0 and 0.1, M barely varies within a base, so the within-base slope is not informative there. Say so beside the
   failure. **Not a block.**
4. **Selection.** Say that the slopes at low density use about 55% of pairs, those with a bond within the margin, and may be biased.
   **Not a block.**

## Files

`brief.md`; `ref_missing.py` → `result_missing.json` (the slopes with bootstraps, M2r's interval, the coefficients of variation with
the gap, the regeneration and the least-bond checks).
