# Closure of the knot-images epic

Status: Proved

Epic `KNOT-IMAGES-20261021-001` closed on 2026-10-21. This is a ledger: one line
per conclusion, with its novelty label and evidence. It makes no new claim. The
decision note is `research/KNOT-IMAGES-20261021-001/knot_images.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | If every circuit is functional modulo common proper pp-definable equivalences, the law composes like cycles. So composing like cycles with no overlapping circuit is exactly having Latin circuits modulo the tops. | New to the program | `KNOT-IMAGES-20261021-001B-P001`, Theorem 1 and Corollary 2 |
| 2 | Every overlapping candidate fails, and all 65,159 knot top images in the surviving census laws are functional. The Latin conjecture (no overlapping) stays open. | Observation; conjecture | census `KNOT-IMAGES-20261021-001A-E001` (H3, H4) |
| 3 | A 2×2 subsquare's relation is functional exactly for group isotopes (Reidemeister). So a non-group square's 4-cycle circuit is not Latin, and every non-group square tested fails or collapses. | Classical theorem restated; observation | `…001B-P001`, Theorem 3; `…001A-E001` (H1) |
| 4 | The 3-net law of a finite abelian group composes like cycles exactly when the group is a p-group, and then carries GF(p)-representable matroids. | New to the program; an expert would derive it quickly | `…001B-P001`, Theorem 4; `…001A-E001` (H2) |
| 5 | If the elements with u^m = 1 generate a group without exhausting it, its 3-net law does not compose like cycles. This covers S₃, D₄ and Z₆. | New to the program | `…001B-P001`, Proposition 5; `…001A-E001` (H2b) |
| 6 | No polymorphism of the Q₈ 3-net law is Mal'tsev modulo ±1, by a 416-equation certificate. The census found no failure for it, so either it fails in larger systems or Conjecture 7 of `CYCLE-TOPS-20261021-001B-P001` is false. | New to the program | `…001B-P001`, Proposition 6; `…001A-E001` (H5 failed on Q₈ alone) |

## Recommendation

**Continue** with whether the 3-net of Q₈ composes like cycles, as a fresh
epic.
- **First:** build the relation behind the certificate (its top image cannot
  be affine), and test elimination and the Latin property on it.
- **Then:** attempt a proof through Theorem 1.
- **Interest:** 3/3.
- **Execution:** deferred to the owner.
