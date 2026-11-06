# Closure of the Mal'tsev-conditions epic

Status: Proved

Epic `MALTSEV-CONDITIONS-20261021-001` closed on 2026-10-21. This is a
ledger: one line per conclusion, with its novelty label and evidence. It makes
no new claim. The decision note is
`research/MALTSEV-CONDITIONS-20261021-001/maltsev_conditions.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | The lift K₄ is congruence 3-permutable and congruence modular, with explicit Hagemann–Mitschke and Gumm terms, but has no Mal'tsev polymorphism. | New to the program; elementary | `MALTSEV-CONDITIONS-20261021-001B-P001`, Theorem 1; census `MALTSEV-CONDITIONS-20261021-001A-E001` (H1) |
| 2 | Restriction lemma. Linear identities among a shadow's polymorphisms pass to its fibre clone, and idempotent identities pass to congruence classes. | Routine | `…001B-P001`, Theorem 2 |
| 3 | The shadow K₆ composes like cycles, but its polymorphisms generate a variety that is neither congruence modular nor n-permutable for any n. Its fibre clone has only conjunctions and constants. | New to the program | `…001B-P001`, Theorem 3; `…001A-E001` (H3) |
| 4 | Composing like cycles is incomparable with congruence permutability, n-permutability and modularity. Z₆ has a Mal'tsev polymorphism and fails elimination. | New to the program | `…001B-P001`, Corollary 4 |
| 5 | Every difference law that composes like cycles is Mal'tsev on its tops. So is every lift of one, and every shadow of one in which equality of first components is pp-definable. The shadow hypothesis is needed for the operation used. | New to the program; resembles difference terms | `…001B-P001`, Theorem 5; `…001A-E001` (H4) |
| 6 | L₂₂₃ and L₂₃₃ have no Hagemann–Mitschke terms for n ≤ 6, and their block clones have no chains, yet both have operations Mal'tsev on their tops. Of the eight Boolean dressings of the Z₃ shadow, only the full relation keeps chains. | Observation | `…001A-E001` (H2, H4, H5) |
| 7 | Correction: x ⊕ y ⊕ z = 0 over Z₂ × Z₂ alone composes like cycles (parity's free sets). Census A's control text said otherwise, but the census tested only the Mal'tsev operation, so its results stand. | Correction | `…001B-P001`, Corollary 4 |
| 8 | Open: every law that composes like cycles is Mal'tsev on its tops. | Conjecture | `…001B-P001`, Conjecture 6 |

## Recommendation

**Continue** with the tops of laws that compose like cycles, as a fresh epic.
- **First discriminator:** a census of the closest laws outside Theorem 5.
  - It covers the 256 subsets removed from the lift's (2,2,2)-block and lifts
    of the shadow K₆.
  - It tests elimination, a Mal'tsev-on-tops operation, and whether any
    circuit is invisible modulo the tops.
- **Then:** attempt Conjecture 6 through rectangularity modulo the tops.
- **Interest:** 2/3.
- **Execution:** deferred to the owner.
