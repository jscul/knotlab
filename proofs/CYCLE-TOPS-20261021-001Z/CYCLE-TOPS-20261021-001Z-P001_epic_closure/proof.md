# Closure of the cycle-tops epic

Status: Proved

Epic `CYCLE-TOPS-20261021-001` closed on 2026-10-21. This is a ledger: one line
per conclusion, with its novelty label and evidence. It makes no new claim.
The decision note is `research/CYCLE-TOPS-20261021-001/cycle_tops.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | In a law that composes like cycles, every reflexive pp-definable relation on a range is total or lies inside the range's top. | Elementary strengthening of the matroid proof's Proposition 6 | `CYCLE-TOPS-20261021-001B-P001`, Lemma 1 |
| 2 | Top lemma: every system of such a law has exactly the circuits of its image modulo the tops, because each variable and its blurred copy are parallel. No circuit hides below the tops. This proves the top-lemma form of `MATROID-CONVERSE-20261021-001B-P001` Conjecture 5. | New to the program; textbook matroid exchange | `…001B-P001`, Theorem 2; census `CYCLE-TOPS-20261021-001A-E001` (H2) |
| 3 | The top image of every tie is the graph of a bijection, an isomorphism between the two tops. | New to the program | `…001B-P001`, Corollary 3; `…001A-E001` (H3) |
| 4 | At each variable of a knot the top image is functional, or every two top classes share a fibre. Only the functional case was observed. | New to the program | `…001B-P001`, Corollary 4; `…001A-E001` (H4) |
| 5 | Conjecture 6 of `MALTSEV-CONDITIONS-20261021-001B-P001` is false. Parity beside J, and K₄ beside the Z₃ law, compose like cycles, but their whole-domain top is equality and no operation is Mal'tsev there. | Correction; the example was already in `MALTSEV-CONVERSE-20261020-001B-P001` | `…001B-P001`, Proposition 5; `…001A-E001` (H6) |
| 6 | In a disjoint union every knot lies in one part. So being Mal'tsev modulo the tops of knot ranges passes to disjoint unions. | Elementary | `…001B-P001`, Proposition 6 |
| 7 | Of the 46 classes of removals from the lift's (2,2,2)-block, exactly five have no failure: nothing, (2,2,2), (2,2,3), {223,232} and {223,232,322}. All are dressed, and all are Mal'tsev on their knot tops, as are both lifts of K₆. | Observation | `…001A-E001` (H1, H5) |
| 8 | Open: Conjecture 7, that every such law has a polymorphism Mal'tsev modulo the tops on its knot ranges, and whether a knot's top image can overlap. | Conjecture | `…001B-P001`, Conjecture 7 |

## Recommendation

**Continue** with knot top images, as a fresh epic.
- **First:** try to prove that knot top images are functional, and so Latin
  hypercubes of their tops.
- **Then:** test whether elimination forces the Reidemeister condition, which
  gives group isotopes and a Mal'tsev operation on knot tops.
- **Start with:** a census of overlapping and non-group Latin knots on small
  tops.
- **Interest:** 2/3.
- **Execution:** deferred to the owner.
