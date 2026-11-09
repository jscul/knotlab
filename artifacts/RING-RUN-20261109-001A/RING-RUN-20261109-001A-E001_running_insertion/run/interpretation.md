# What survives a ring inserted while the twist tube runs: interpretation

Experiment `RING-RUN-20261109-001A-E001` (exploratory), run once on 2026-11-09 under the frozen contract (pre-registered in 18a82abb9,
amended before its first run in c08b94272), in 86 s on 16 workers. Exact: bindings after the insertion read through the orbit of each
contact's row. Every row is in `result.json`.

## Control

Every stage persists before the insertion, and an insertion at lag 0 gives the next stage, which persists, on all 19 tubes and both splits.

## Primary observable

| Split | H1: lag 0 clean on every tube | H2: failures of rings not reached or of the new ring | H3: reached bindings that fail | Clean lags |
| --- | --- | --- | --- | --- |
| keep (the three rewired contacts keep their values) | yes | 0 (of 3,860) | 7,893 of 14,892 (53%) | 46 of 559 |
| fresh (they are born anew) | yes | 0 (of 3,688) | 7,738 of 15,064 (51%) | 87 of 559 |

- **All three hypotheses hold.** An insertion at lag 0 keeps every contact persistent; no ring the insertion has not reached, and not
  the new ring, loses a binding; and just over half of the bindings of reached rings fail, against 68% for bands
  (`GROW-RUN-20261109-001A`).
- **Clean lags.** With the keep split only lag 0 is clean, except on the tubes of 5 and 7 rings at g = 4, where 19 of 41 and 10 of 64
  lags are. With the fresh split lags 0 and 1 are clean on every tube, lag 2 too on odd tubes at g = 2, and many more on the same two
  tubes at g = 4.
- **Coverage.** 17 of the 19 tubes have every insertion lag read; the 7-ring tubes at g = 3 and 4 (state periods 2,044 and 10,920) have
  their first 64, as the amendment set.

## Reading against the decision rule

H3 holds, so growth must come between runs for single rings as for bands: an insertion while the network runs breaks about half the
bindings its influence has reached. It is a little gentler than a band, and a fresh insertion is clean for a lag or two longer, before
influence crosses the gap.

## Nonclaims

- **Exploratory and finite:** the roster only; one insertion per run.
- **Two-time knots only** (A30); equally spaced rings only.
