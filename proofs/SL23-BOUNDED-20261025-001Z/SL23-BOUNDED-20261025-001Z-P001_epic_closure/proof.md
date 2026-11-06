# Closure of the SL(2,3) epic

Status: Proved

Epic `SL23-BOUNDED-20261025-001` closed on 2026-10-25. This is a ledger: one line per conclusion, with its novelty label and evidence.
It makes no new claim. The decision note is `research/SL23-BOUNDED-20261025-001/sl23_line.md`, and the literature scan is
`research/SL23-BOUNDED-20261025-001/scan.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Take G with a central (Z/2)^m layer over an elementary abelian 2-layer over a nilpotent quotient. Counting homomorphisms into G is a sum, over boundedly many top maps, of zero counts of a quadratic map on an affine twisted lift space, with a bounded number of quadratic conditions. Gauss sums make it polynomial for closed 3-manifolds with bounded first homology. | `candidate-local-delta`; folklore risk medium | `SL23-BOUNDED-20261025-001A-P001` |
| 2 | SL(2,3) satisfies these hypotheses but is not abelian-by-nilpotent. So with bounded homology the line is not "abelian-by-nilpotent". SL(2,3), of Fitting height 2, is polynomial; S₄, of Fitting height 3, is #P-hard. | Same | `…001A-P001`, Corollary 3 |
| 3 | Maps from knot groups to GL(2,3) or the binary octahedral group are exactly twice the maps to S₄, and \|Hom(π, S₄)\| = 4 + R + 2T. So S₄ and both double covers are #P-hard on knots, with or without the meridian condition. | Routine; the hardness rests on `BOUNDED-H1-20261025-001A` | `SL23-BOUNDED-20261025-001B-P001` |
| 4 | The closed-manifold hardness of the double covers is open: the identity 8 + 2T for 4-surgery fails on some knots. | Recorded open step | `…001B-P001`, part 3 |

## Challenged assumptions

The decision note records three workspace assumptions this epic challenges:
- **The bounded-homology line might be "abelian-by-nilpotent".** False: SL(2,3) is polynomial.
- **Central extensions of S₄ inherit the closed hardness directly.** Not directly: the lifted longitude signs vary.
- **Gauss sums only serve nilpotent targets.** Too narrow: they work over twisted domains when the obstruction target is untwisted.

## Recommendation

**Research directions: twisted central layers.**
- **First discriminator:** UT₃(F₄) ⋊ Z₃ (order 192, Fitting height 2), whose central layer is twisted by ω. Is its count with
  bounded homology polynomial, or #P-hard?
- **Interest:** 2/3.
- **Alternatives:**
  - closed-manifold hardness for GL(2,3) and 2O (1/3);
  - a single-query S₄ result through the parity rule (1/3);
  - a short note on the bounded-homology picture (2/3);
  - return to the core intuitions (1/3).
- **Execution:** deferred to the owner.
