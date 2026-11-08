# A census of loops of five to eight rings: interpretation

Experiment `LOOP-ANY-20261108-001B-E001` (exploratory), run 2026-11-08 under the frozen contract: 65,472 loops (rotation classes) in
152 s on 16 workers. Rows of M^T are exact; the reading goes to lag 400. Totals are in `result.json`, the balanced and the persistent
loops in `loops.json`.

## Control

net_lib's control is `SEPARATE-20261108-001A`'s check 1; the four-ring case is `LOOP-PROOF-20261108-001A`, checked to size 30.

## Primary observable

| Loops of 5 to 8 rings, sizes 4 to 16 | Count |
| --- | --- |
| Balanced, every contact binding both rings to lag 400 | 5,354 of 5,354 |
| Balanced, the chain-end witnesses holding to lag 400 | 5,354 of 5,354 |
| Unbalanced, persistent to lag 400 | 11,322 |
| Unbalanced, some contact missing a ring | 48,796 |

## Reading against the decision rule

- **H1 holds.** Every balanced loop persists through the chain-end witnesses, as `LOOP-ANY-20261108-001A` proves for every number of
  rings.
- **Balance is sufficient, not necessary.** 11,322 unbalanced loops also persist to lag 400, through other cells; the proof does not
  cover them, and lag 400 does not decide them.

## Nonclaims

- **Lags to 400** and these positions only.
- **Two-time knots only** (A30).
