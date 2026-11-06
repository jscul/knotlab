# Closure of the Thomsen-knots epic

Status: Proved

Epic `THOMSEN-KNOTS-20261021-001` closed on 2026-10-21. This is a ledger: one
line per conclusion, with its novelty label and evidence. It makes no new claim.
The decision note is `research/THOMSEN-KNOTS-20261021-001/thomsen_knots.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | The 3-net law of Q₈ does not compose like cycles. Thomsen's configuration T is a knot that allows x₂ = x₁, and T(x₁, x₂, x₃) ∧ T(x₁, x₂, x₃′) violates elimination. Its top image, ω(c₁ + c₂, c₁ + c₃) = 0, is the relation that is not affine behind the 416-equation certificate. | New to the program | `THOMSEN-KNOTS-20261021-001A-P001`, Proposition 5 |
| 2 | In a law that composes like cycles, no circuit overlaps modulo the tops. This is the Latin conjecture of `KNOT-IMAGES-20261021-001B-P001`. | New to the program; elementary | `…001A-P001`, Lemma 1 and Theorem 2 |
| 3 | A law composes like cycles exactly when proper pp-definable equivalences on its ranges make every circuit functional at each variable. The tops serve. | New to the program | `…001A-P001`, Corollary 3 |
| 4 | A Latin square's 3-net law composes like cycles exactly when the square is isotopic to an abelian p-group. Every non-abelian group fails. | New to the program; built on Thomsen's classical theorem | `…001A-P001`, Theorem 4 |
| 5 | Conjecture 7 of `CYCLE-TOPS-20261021-001B-P001` (Mal'tsev on knot tops) survives, and no law is known that separates it from composing like cycles. | Conjecture | `…001A-P001`, after Corollary 3 |

## Recommendation

**Continue** with Mal'tsev structure on the tops, as a fresh epic.
- **First:** show that every three-variable circuit's top image is isotopic to
  an abelian p-group, by applying Theorem 4 to the 3-net law of that image.
- **Then:** show that the parallelogram operations of knots through one range
  agree, extend to larger circuits, and test whether every top image is closed
  under them.
- **Interest:** 3/3.
- **Execution:** deferred to the owner.
