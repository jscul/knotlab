# Referee job PARITY-SURVIVE-R1: the brief

The coordinator handed this job over on 2026-11-12 (15:45 UTC). It comes from the harmony thread: `PARITY-SURVIVE-20261112-001`,
in commits d4d3c753b (the freeze), b83c72450 (the epic) and 14bc09285. The decision note is
`research/PARITY-SURVIVE-20261112-001/parity_survive.md`.

## Claims under review

- **Lemma A.** It holds as a census on 8 of 8 harmonies; there is no proof.
- **Scale.** Under Bernoulli ρ, under 1% of placements survive for n ≥ 6, and none of 11,497 samples at 7 × 7 to 9 × 9 survives. The
  scale part hit its one-hour cap with 55 of 56 cells, assembled from the saved rows.
- **Survival rules.** B1 and B2 both fail. B1 has 705 placements where the classes fit but no state lifts. B2 fails on one class of
  8 placements of 000111 + 0011 + 01 on 4 × 4.
- **The fixing split.**

  | Survivors | Parity alone | Parity with the harmony's states | Needs the stitches | Beyond GAC |
  | --- | --- | --- | --- | --- |
  | all, on 3 × 3 and 4 × 4 | 10% | 14% | 76% | 36% |
  | sampled | 38% | 25% | 37% | 25% |

## The coordinator's checks

1. The tier definitions and code: especially P (stitches dropped, copies kept in W), GAC on classes, and the 216 pairs without GAC.
2. Recompute B1's 705 lifting obstructions independently.
3. The assembly of the capped part: could the missing cell change any stated claim?
