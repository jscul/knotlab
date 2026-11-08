# Full reach on the cut-open torus: interpretation

Experiment `FULL-REACH-20261108-001A-E001` (exploratory), run 2026-11-08 under the frozen contract: sides 3 to 48 in 133 s on 16
workers. Exact, with no lag cutoff. Totals and examples are in `result.json`.

## Control

`GENUS-CUT-20261108-001A`'s checks 4 and 6: sides 3 to 17 by the same computation, and the walk-count reading against rows of M^T.

## Primary observable

| Sides | Uncut contacts missing a ring |
| --- | --- |
| 3 to 7, 9 to 15, 17 to 31, 33 to 48 | none |
| 8 | 4 of 112, each never needing three rings in the far corner |
| 16 | 12 of 480 |
| 32 | 28 of 1,984 |

## Reading against the decision rule

- **H1 holds.** The failing sides are exactly 8, 16 and 32, the powers of two from 8 up to 48. The conjecture "every uncut contact needs
  every ring unless the side is a power of two of at least 8" is supported to side 48. Its proof is the next step.
- **The pattern of failures.** At side n = 2^m exactly n − 4 contacts fail (4, 12 and 28), and each never needs the three rings of one
  corner of the cut-open torus.

## Nonclaims

- **Sides 3 to 48 only**, spacing 2 (the needs relation does not depend on the spacing); no proof.
- **Two-time knots only** (A30).
