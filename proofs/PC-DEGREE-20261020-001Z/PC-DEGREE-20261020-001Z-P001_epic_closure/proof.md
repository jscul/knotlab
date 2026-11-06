# Closure of the polynomial calculus degree epic

Status: Proved

Epic `PC-DEGREE-20261020-001` closed on 2026-10-20, after both of its tickets
ended. This is a ledger: one line per conclusion, with its novelty label and
evidence. It makes no new claim. The decision note is
`research/PC-DEGREE-20261020-001/pc_degree.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | In the reduced convention, a polynomial calculus derivation from binomial Tseitin axioms is a closure of signed relations between monomials. Each relation is labelled by a vertex set whose cut is the symmetric difference of its monomials. A refutation is a relation labelled V, so the degree does not depend on where the odd charge sits. | elementary; this labelled form not found stated | `PC-DEGREE-20261020-001B-P001` (prose; matches linear algebra over F3 in 255 + 3,308 cases) |
| 2 | A tangle of order 2d+1 of the cut function keeps every label on its small side, so no refutation of degree d exists. With the tangle duality of Robertson and Seymour, the degree is at least ⌈cvw/2⌉. | not found stated (targeted search) | `…001B-P001`; tangles found by exhaustive search on small graphs agree with the duality |
| 3 | A carving of width w gives a refutation of degree ⌊w/2⌋+1 with balanced binomial axioms, since relations below 2d move freely. So the degree is ⌈cvw/2⌉ when cvw is odd and one of two values when it is even. The standard binomial and clause encodings need max(maxdegree, that), and counting degree before reduction adds at most one. | not found stated (targeted search) | `…001B-P001` (derivations replayed on 155 graphs); census P1–P3 |
| 4 | On 1,253 graphs (the earlier census roster, 300 held-out graphs and nine named graphs) every frozen prediction holds. Even-width graphs split 191 at cvw/2 and 628 at cvw/2+1. In the clause encoding the degree exceeds the maximum degree on wide graphs (Q4: 6 against 4; K55: 7 against 5). | finite evidence | `PC-DEGREE-20261020-001A-E001` (confirmatory, supported) |

## Recommendation

**Research directions**, rated by barrier potential:
- **A (Interest 2/3).** Polynomial calculus size of grid Tseitin in the 0/1
  basis, where the size–degree method gives nothing. First a literature
  check, then charge-preserving restrictions.
- **B (Interest 1/3).** The exact sum-of-squares degree of Tseitin: the
  tangle gives a block-rank-one pseudo-expectation, so the degree is likely
  cvw ± 2.
- **C (Interest 1/3).** Return to the foundations (question 9).

Execution is the owner's decision.
