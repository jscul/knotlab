# Closure of the knots-as-circuits epic

Status: Proved

Epic `KNOT-CIRCUITS-20261020-001` closed on 2026-10-20. This is a ledger: one
line per conclusion, with its novelty label and evidence. It makes no new
claim. The decision note is
`research/KNOT-CIRCUITS-20261020-001/knot_circuits.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | A system's knots and ties are its minimal constrained sets, where a set is constrained when not every combination of its variables' possible values occurs. Where circuit elimination holds, they are the circuits of a matroid whose independent sets are the unconstrained sets. | Elementary | `KNOT-CIRCUITS-20261020-001B-P001`, Lemma 1 |
| 2 | A law with a Mal'tsev polymorphism composes like cycles exactly when every subalgebra of its polymorphism algebra with at least two elements has a unique maximal congruence. | Not found stated; short from rectangularity and Fleischer's lemma | `…001B-P001`, Theorem 1 |
| 3 | Affine laws over finite fields compose like cycles. A group's coset law does exactly when every subgroup has a unique maximal normal subgroup: Z_{p^k}, S3 and D_p do; Z6, Z2×Z2, A4, D4, Q8, Dic3 and Z12 do not. | Not found stated | `…001B-P001`, corollaries; census `KNOT-CIRCUITS-20261020-001A-E001` |
| 4 | A Boolean law composes like cycles exactly when it is affine. It composes its knots like cycles exactly when it is affine or bijunctive, and bijunctive laws have no knots. | Affine ⇒ matroid classical; the converse and the knot level not found stated (Post's lattice and explicit hubs) | `…001B-P001`, Theorem 2 |
| 5 | Two knots sharing only e form a hub exactly when every e-fibre of one meets every e-fibre of the other. Colouring stars, Horn clauses and OR₃ are hubs; parity never is. | Elementary | `…001B-P001`, Proposition 3 |
| 6 | Tseitin knots are bonds and gauge knots are cycles. Laws with an isolated reflexive value tie every linked pair and have no knots. | Classical / elementary | `…001B-P001`, Readings |
| 7 | The census holds P1, P3 and P4. Its frozen signal is false, because its bounded search found no knot for the eight negation-twists of 1-in-3 (P2). The proof gives explicit knot hubs for all eight. | Exploratory evidence; obstructed by search depth | `…001A-E001` |
| 8 | Open: whether every law that has knots and composes them like cycles is Mal'tsev. Proved for Boolean laws; true on all binary relations over three elements. | Conjecture | `…001B-P001`; `…001A-E001` |

## Recommendation

**Research directions.** Space from knot matroids: does a difference law's
knot matroid recover a graph or complex from allowed states alone (Whitney;
Tutte), and do laws written on no graph yield graphic knot matroids?
- Interest 2/3. Deferred to the owner.
- The alternative is the Mal'tsev conjecture (1/3).
