# Closure of distance in a grown network

Status: Proved

Ticket `GROWN-DISTANCE-20261109-001Z`, 2026-11-09.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/GROWN-DISTANCE-20261109-001/grown_distance.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Every stage of band growth (the loop, the n × 2 ladder, every n × m torus) reads the cut length D and the time length g·δ + 1 exactly; on the ladder and tori D = ⌈δ/2⌉. | known-with-delta; proved | A (Theorem 1) |
| 2 | Every square torus whose lattice holds (2, 0) or (0, 2), the ladder and its twisted forms, reads distance without freezing at every size. | new as far as found; proved | A (Theorem 2) |
| 3 | The n × m torus (2 ≤ n ≤ m) is on time exactly when n = 2 or n = m = 3: from the second band on, every stage but 3 × 3 needs freezing. | new as far as found; proved | A (Theorem 3) |
| 4 | Ring balls are Σ_b min(n, 2(r − \|b\|) + 1); on the cylinder 2r² + 2r + 1 out to half the loop, then 2n per step; the time length's balls are the same. | known-with-delta; proved | A (Theorem 4) |
| 5 | The square tori holding (2, 1) or a rotation of it and the triangular tori holding a vector of length √3 read distance plainly too; every other on-time torus is small; the rotation-invariant ones are `PLAIN-TIME-20261108-001`'s 26. | computed to index 100, 80 and 50; stress test to 140 and 110 | A (check 5), stress test |
| 6 | Correction: `PLAIN-TIME-20261108-001B`, Theorem 4, holds for rotation-invariant tori only (Narrowing). | correction | A (Theorem 2, check 5) |

## Answer

The grown torus reads both freeze lengths at every stage; without freezing only its first stage, the ladder, reads distance; its balls
are a tube's, dimension 2 out to half its loop and 1 beyond.

## Recommendation

**Research directions**, selected #1, growth while running. The table is in the decision note.
