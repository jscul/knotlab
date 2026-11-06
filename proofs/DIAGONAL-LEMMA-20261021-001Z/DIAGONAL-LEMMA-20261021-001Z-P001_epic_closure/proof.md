# Closure of the diagonal-lemma epic

Status: Proved

Epic `DIAGONAL-LEMMA-20261021-001` closed on 2026-10-21. This is a ledger: one
line per conclusion, with its novelty label and evidence. It makes no new
claim. The decision note is
`research/DIAGONAL-LEMMA-20261021-001/diagonal_lemma.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Shadows. If every system over M has full ranges and h(M) ⊆ K for a surjection h, the product M × K has exactly M's constrained sets in every system. | New to the program; elementary | `DIAGONAL-LEMMA-20261021-001B-P001`, Theorem 1 |
| 2 | Lifts. If M contains every constant tuple and has no free identifications, doubling a value a and removing (a, …, a) keeps M's constrained sets in every system. | New to the program; elementary | `…001B-P001`, Theorem 2 |
| 3 | The local converse and the diagonal lemma are false. K₄ (x̄ + ȳ + z̄ ≡ 0 mod 3 on {0,1,2,3}, reading 3 as 2, minus (2, 2, 2)) is a non-rectangular 3-variable knot with no direct case whose law composes all circuits like cycles. Products give such knots on 6 values (3 variables) and 4 values (4 variables). | New to the program | `…001B-P001`, Corollary 3 |
| 4 | Fibre distance. A knot whose fibre graph at a variable is connected, with fibres at distance at least 2 (or 1 with eccentricity at least 2), yields a failure. In a law whose knots compose like cycles, every fibre graph is disconnected or dense. | New to the program; elementary | `…001B-P001`, Theorem 4 |
| 5 | The lemma holds generically. Every random non-rectangular knot tested was resolved: 160 three-variable knots on 3–6 values with no direct case, and 50 four-variable knots. Two values admit no counterexample; three values are open. | Observation | `DIAGONAL-LEMMA-20261021-001A-E001` (L1–L3); `…001B-P001` |
| 6 | The census candidates that failed L4–L6 were resolved. Other lifted blocks and the dihedral action fail in larger systems. The inner factor fails through fibre distance. K₄ is a counterexample. | Observation, with verified witnesses | `…001B-P001`, census candidates |

## Recommendation

**Continue** with the matroid-level converse, as a fresh epic. The question:
does every law whose knots compose like cycles have, system by system, the
constrained sets of a difference law?
- **Interest:** 2/3.
- **Execution:** deferred to the owner.
