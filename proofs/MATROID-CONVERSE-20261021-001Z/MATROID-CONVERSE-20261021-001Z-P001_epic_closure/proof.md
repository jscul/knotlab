# Closure of the matroid-converse epic

Status: Proved

Epic `MATROID-CONVERSE-20261021-001` closed on 2026-10-21. This is a ledger: one
line per conclusion, with its novelty label and evidence. It makes no new
claim. The decision note is
`research/MATROID-CONVERSE-20261021-001/matroid_converse.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Every downset of subsets containing the singletons is the free-set family of one relation. The Vámos matroid is carried by its support relation and by a union of two GF(7) codes, and both relations' laws fail elimination. | Trivial once seen; the Vámos union of codes is new to the program | `MATROID-CONVERSE-20261021-001B-P001`, Proposition 1; census `MATROID-CONVERSE-20261021-001A-E001` (Q1, Q2) |
| 2 | Top lemma. A subdirect product of Mal'tsev algebras, each with a unique maximal congruence, is full exactly when its image in the simple tops is full. | Classical tools; possibly folklore | `…001B-P001`, Theorem 2 |
| 3 | In group laws whose subgroups have unique maximal normal subgroups, every system's matroid is a direct sum of one GF(p)-representable matroid per prime plus parallel classes. Field laws carry F-representable matroids. | New to the program | `…001B-P001`, Theorem 3; `…001A-E001` (Q3) |
| 4 | The Vámos, non-Pappus and Fano/non-Fano 2-sum matroids never occur in such laws, nor in their shadows, lifts and disjoint unions. | New to the program | `…001B-P001`, Corollary 4 |
| 5 | In every law that composes like cycles, every pp-definable set has a unique maximal pp-definable equivalence, so tops exist without a difference operation. | New to the program; generalizes the circuits proof | `…001B-P001`, Proposition 6 |
| 6 | Of 91 one-tuple perturbations of x + y + z ≡ 0 over Z₃ and of its lift, 83 fail. The 8 survivors are exactly the removals from the lift's (2,2,2)-block, and each keeps the Z₃ law's constrained sets. | Observation | `…001A-E001` (Q4, Q5) |
| 7 | Open: whether every law that composes like cycles carries only direct sums of finite-field-representable matroids. Sharpened to a top lemma for all such laws. | Conjecture | `…001B-P001`, Conjecture 5 |

## Recommendation

**Continue** with the Mal'tsev conditions of laws that compose like cycles.
- **First discriminator:** whether the lift K₄ and the other dressed survivors
  are congruence n-permutable or modular. Settle it by polymorphism search.
- **Then:** try to prove that composing like cycles implies modularity, which
  would carry over half of the top lemma.
- **Interest:** 2/3.
- **Execution:** deferred to the owner.
