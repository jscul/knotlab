# Interpretation: does growth round the reading?

Run of the frozen contract `ROUND-READ-20261110-001A-E001` (exploratory, not blind: what the theorem and READ-GROW-20261110-001 said
was known), 2026-11-10, launch `round-read-a1` at 17:23 UTC, 85 seconds. 113 schedules. Part C: round_lib agrees with metric_lib on T,
T1 and L in all 7 small schedules. Readings exact.

## The predictions

| Prediction | Verdict | Evidence |
| --- | --- | --- |
| Q1: every route gap within ±(15g + 2) (a check of CONF-METRIC-20261110-001A) | **Holds**: T gaps from −8.75 to −0.625, T1 from −7.5 to 0 | summary |
| Q2: no route slope ≤ −g/2 | **Holds**: T slopes from −0.66 to 1.09, T1 from −1.31 to 0; at 41 × 41 within ±0.15 | summary |
| Q3: no growth schedule rounds the plain reading | **Holds**: no L or L1 slope ≤ −g/2 in any schedule; every L slope, and every L1 slope with three gaps defined, is ≥ g/2: the plain reading is squarer than taxicab, not rounder | summary |

## What it shows

- **Route readings are taxicab at every distance read.** Up to distance 20 the diagonal and the axis ring at the same taxicab distance
  are reached within 9 conformal lags of each other, the diagonal never more than 9 earlier, and the gap does not grow: at 41 × 41 the
  baseline's T gap is −3 at every even distance from 2 to 20.
- **The plain reading waits for powers of two along diagonals.** On the fixed first stage (the baselines), the diagonal ring at taxicab
  distance d is heard plainly 4g (2^⌈log₂ d⌉ − d) conformal lags after the axis ring at d: zero at d = 2, 4, 8 and 16, and at d = 6, 10,
  12, 14, 18, 20 the time the axis ring at the next power of two is heard. All 24 baseline gaps, at g = 2, 3 and 5, follow this.
- **Growth perturbs that pattern but does not round it.** 313 of the 456 plain gaps in growth schedules follow the same law; the rest
  differ, and every growth schedule's plain slope lies between 1.5g and 2.4g, on the square side.
- **Plain holes.** Rings reached by a route but never heard plainly within the schedule: 100 to 1,552 per family for L, more for L1.

## Nonclaims

- Five families, 113 schedules, distances to 20; the power-of-two law computed on the baselines, not proved; balance not read; declared
  rings (A45) on a declared board (A51); open births (A44); conformal time a reading (A56).
