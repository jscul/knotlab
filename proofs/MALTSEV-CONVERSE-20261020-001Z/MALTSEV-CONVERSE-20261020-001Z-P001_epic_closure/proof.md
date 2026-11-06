# Closure of the converse epic

Status: Proved

Epic `MALTSEV-CONVERSE-20261020-001` closed on 2026-10-20. This is a ledger:
one line per conclusion, with its novelty label and evidence. It makes no new
claim. The decision note is
`research/MALTSEV-CONVERSE-20261020-001/maltsev_converse.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | The naive converse is false. Parity on {0,1} beside x ≤ y on {2,3} composes knots like cycles, and parity beside an isolated-value relation on {2,3,4} composes all circuits like cycles. Neither has a Mal'tsev polymorphism. | Elementary | `MALTSEV-CONVERSE-20261020-001B-P001`, Proposition 1; census `MALTSEV-CONVERSE-20261020-001A-E001` |
| 2 | A knot whose fibres pairwise meet at a variable, or that has a selector, forms a hub with a copy of itself. NAE has a selector. | Elementary | `…001B-P001`, Lemma 2 |
| 3 | In a law composing knots like cycles, every knot on one two-element range is a single parity. | Corollary of `KNOT-CIRCUITS-20261020-001B-P001` | `…001B-P001`, Theorem 3 |
| 4 | If every knot is rectangular, knots compose like cycles exactly when no two knots meeting at a variable induce partitions that compose to the total relation. No Mal'tsev operation is needed, so the converse reduces to rectangularity of knots. | New to the program; elementary | `…001B-P001`, Theorem 4 |
| 5 | Open: does composing knots like cycles force rectangular knots? Every 3-variable knot tested on 2, 3 and 4 values gives a hub directly or through the diagonal derivation. All 34 sampled laws with knots have hubs between knots. | Conjecture with computational evidence | `…001B-P001`, Observation 6; `…001A-E001` |

## Recommendation

**Continue:** the diagonal lemma, which would complete the characterization.
- Interest 2/3.
- Deferred: the space question runs in the same request.
