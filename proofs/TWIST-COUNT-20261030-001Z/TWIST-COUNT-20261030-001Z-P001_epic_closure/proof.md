# Closure of the counting-one-twist-off-the-bound epic

Status: Proved

Ticket `TWIST-COUNT-20261030-001Z`, 2026-10-30. This is a ledger: one line per conclusion, with its novelty label and evidence. It makes
no new claim. The decision note is `research/TWIST-COUNT-20261030-001/counting_one_twist_off_the_bound.md`.

## Conclusions

| # | Conclusion (standard vocabulary) | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | For every signing of a cubic bipartite graph, #col = (3/2)^n Σ_χ (−1/3)^{\|χ\|/2} (−1)^{\|σ∩χ\|} over even subgraphs. Flipping one incidence of a non-colourable system gives #col(H − L). | signed form of a known identity | A-P001, Lemma 1 |
| 2 | Branch tensors at trisum squares are even in the Hadamard basis, and planar ones are matchgate signatures under any signing. A branch is untwisted iff its tensor has the split form. | consequence of matchgate theory; split form new | A-P001, Lemmas 2–3 |
| 3 | A junction with an untwisted side of split (α, β) is a similitude of the matchgate identity, with multiplier ±(α² + αβ + β²) = ±\|α + βe^{iπ/3}\|². | new (no overlap found) | A-P001, Theorem 4 |
| 4 | If no square has three twisted branches, a good root exists and #col is computable in polynomial time (matchgates, FKT). Otherwise some junctions leave the matchgate class. | new | A-P001, Lemma 5, Theorem 6, Proposition 7 |
| 5 | With nonnegative branch tensors the square lines carry no hard wire, so no junction is a crossover. With a signed branch one can be. | new | B-P001, Theorem 2 |
| 6 | Twisted truncated-octahedron pages give soft crossings: crossover-type junctions off the matchgate class with all straight entries nonzero, e.g. (40000, −1112, 3336, −192). | new (exact computation) | B-P001, Proposition 3 |

## Recommendation

**Continue**, as a fresh epic: soft crossings to hardness (3/3).
- **The plan.** Sharpen the soft crossing by interpolation (odd series compositions), then reduce from colouring counts of general cubic
  signed systems.
- **The target.** That would prove counting #P-hard exactly where twists branch.
- **Status.** Deferred to the owner. The decision note has the full assessment.
