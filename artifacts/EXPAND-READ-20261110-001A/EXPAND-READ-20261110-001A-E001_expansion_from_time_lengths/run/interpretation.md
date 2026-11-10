# Interpretation: the expansion read from time lengths

Run of the frozen contract `EXPAND-READ-20261110-001A-E001` (exploratory, not blind: what METRIC-GROW-20261110-001 had read is
disclosed), 2026-11-10, launch `expand-read-a1` at 16:51 UTC, 32 seconds. 891 schedules; code 2 agrees with code 1 on all 34 sampled
schedules (T and T1). Readings exact.

## The predictions

| Prediction | Verdict | Evidence |
| --- | --- | --- |
| X1: no triangle excess within a stage (a theorem, checked) | **Holds**: of 8,987 directed T1 violations, none has its two legs ending within the first stage | `result.json`, summary |
| X2: along an axis, the time per original spacing is 4g 2^k in stage k | **Holds for every ring-to-ring reading** (2,368 of 2,368: 12 and 24 at g = 3 in stages 0 and 1, 48 in stage 2; 8 and 16 at g = 2; 20 and 40 at g = 5) and for 1,586 of 1,614 cell readings. As frozen it **fails**: 28 cell increments, all along +x or −y in 14 schedules, are 30 instead of 40 (g = 5, stage 1) or 42 instead of 48 (g = 3, stage 2) | summary, `X2` rows |
| X3: in conformal time the round trip satisfies the triangle inequality on every schedule | **Fails as frozen**, by a bounded residual: 28 of 891 schedules have conformal violations (80 triples), the largest excess 2 conformal lags (1 or 1.5 at g = 3, 2 at g = 2) | summary |
| Comparison: the plain round trip | Violated in 240 schedules, with excesses up to 78 lags (median 12 to 18 per family) | rows |

The contract's rule: X3 fails, so its violations are reported with their size; the excess is not only the scale, but what is left is
bounded by 2 conformal lags, against up to 78 lags before.

## What it shows

- **The scale factor is read exactly between rings.** Every ring-to-ring time length along an axis grows by 4g 2^k lags per original
  spacing in stage k: a front crosses one ring in 2g lags at every stage, and each doubling doubles the rings between original rings.
- **Conformal time removes almost all of the excess.** Counting a lag after k doublings as 2^-k, 212 of the 240 schedules whose round
  trips break the triangle inequality satisfy it, and the other 28 break it by at most 2 conformal lags. So, post hoc, the conformal
  round trip plus 2 is a metric on every schedule read: a metric up to a bounded error, where the plain round trip's error grows with
  the doublings a trip crosses.
- **The residual sits at particular first runs.** The 28 schedules share first runs: [28, 24, *] at g = 3 on 5 × 5, [4, *] and [8, *]
  with long second runs at g = 2, [40, *] on 7 × 7, and in F4 [28, 60]. The X2 deviations sit at other first runs ([12, 16, *],
  [20, 4, *], g = 5 [36, *]); the two never share a schedule.
- **The balanced schedules agree.** Of the 43 known to keep every stage balanced, X2 holds for all 116 increments, and one, [28, 60],
  has a conformal violation of 1 lag.

## Nonclaims

- Two tubes, three spacings, the frozen families; the freeze readings exact per case; conformal time a reading of the law's own
  doublings (A56); no physics claim. Balance is not read here, except as known for F4.
