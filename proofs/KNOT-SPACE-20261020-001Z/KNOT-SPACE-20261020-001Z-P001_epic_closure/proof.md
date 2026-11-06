# Closure of the space epic

Status: Proved

Epic `KNOT-SPACE-20261020-001` closed on 2026-10-20. This is a ledger: one line
per conclusion, with its novelty label and evidence. It makes no new claim.
The decision note is `research/KNOT-SPACE-20261020-001/knot_space.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Systems with the same allowed states have the same knots and readings. A parity law's knot matroid is the column matroid of its direction code. | Elementary | `KNOT-SPACE-20261020-001B-P001`, Proposition 1 and Lemma |
| 2 | A gauge law over any group with at least two elements has the cycles of its graph as circuits. A Tseitin law has the bonds. The two knot matroids are dual. | Classical, elementary | `…001B-P001`, Proposition 2; census `KNOT-SPACE-20261020-001A-E001` (S4) |
| 3 | The allowed states determine a 3-connected graph exactly: the cocircuits whose deletion leaves the matroid connected are the vertex stars. 2-isomorphic graphs have identical allowed states, so Whitney twists are invisible. | Classical (Whitney; cocircuit form of Tutte) | `…001B-P001`, Theorem 3; `…001A-E001` (S1, S2) |
| 4 | For a 3-connected planar graph, the dual reading returns the faces of its unique embedding, and the read cells form the 2-sphere. | Classical (Whitney) | `…001B-P001`, Theorem 4; `KNOT-SPACE-20261020-001C-E001` (T1) |
| 5 | For a 3-connected knot matroid, the reading succeeds exactly when the matroid is graphic, and Tutte's minors witness failure. So a law carries a graph exactly when it can be rewritten with every variable joining two sites. Space is recognized, not created: a random local law written on no graph carries a sphere, and almost every balanced code carries none. | Classical; the reading is the program's | `…001B-P001`, Theorem 5, Corollary 6 and Remark 8; `…001C-E001` |
| 6 | On a locally finite infinite graph, the Tseitin knot matroid depends on the reading. Over all solutions, its circuits are the minimal finite cuts with a finite side. Within one class of finitely different solutions, they are the finite bonds, whose dual has the circles through the ends as circuits (Bruhn and Diestel). | Cited, not checked | `…001B-P001`, Remark 7; `HOLES-AT-INFINITY-20261020-001B-P001` |
| 7 | Census predictions. S3 failed through a labelling error and S5 was vacuous. T2 was refuted on a small sample: 1 of 13 three-connected local laws carried a graph. | Observation | `…001A-E001`, `…001C-E001` |

## Recommendation

**Full pivot.** Leave the matroid reading of single laws. That line is
practically exhausted, because its answer is classical.

The next step is the diagonal lemma of `MALTSEV-CONVERSE-20261020-001`, which
decides which laws have a knot matroid to read.
- **Interest:** 2/3.
- **Execution:** deferred to the owner.
