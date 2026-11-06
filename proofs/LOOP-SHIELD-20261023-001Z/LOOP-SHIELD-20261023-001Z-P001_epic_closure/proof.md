# Closure of the loop-shielding epic

Status: Proved

Epic `LOOP-SHIELD-20261023-001` closed on 2026-10-23. This is a ledger: one line per conclusion, with its novelty label and evidence. It makes no new claim. The decision note is `research/LOOP-SHIELD-20261023-001/loop_shielding.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | On every closed orientable surface with a cellularly embedded graph, the wall involution pairs the line events of the twists q and q + PD(c) and keeps every directed cycle, so their probabilities are equal under fair orientations. On a torus this is the odd-loop identity; on genus g it pairs only these two of the 2^(2g−1) twists odd on c. | New to the program; classical ingredients; moderate folklore risk for the technique, low for the statement | `LOOP-SHIELD-20261023-001C-P001`, Theorem 1 |
| 2 | Seams next to a vertex set carry exactly the duals of the classes of curves in its open star minus the graph on it (Lefschetz duality). Next to a lone odd loop with no square meeting it in two opposite corners, a seam carries only 0 or PD(c). In three dimensions the dual objects are closed surfaces, and a set whose open star lies in a solid torus carries no seam class. | Standard topology applied to seams; the application is new to the program | `…001C-P001`, Lemmas E and F |
| 3 | A first statement of Lemma E, with the graph on the set in place of its open star, was false (117 of 300 random sets) and was corrected before closure. | A recorded correction | `…001C-P001`, check.py |
| 4 | On eight genus-2 square-tiled surfaces (16 to 32 edges, every orientation counted), each of the 15 classes with lone odd loops has exactly equal dual pairs, and its four pair values are never all equal: only the dual twist is shielded. | A recorded computation | `LOOP-SHIELD-20261023-001A-E001` |
| 5 | No twist is shielded in three dimensions. On thin 3-tori two layers thick, all 28 comparisons between twists odd on a class that no symmetry relates differ by more than 5 standard errors (smallest 6.9), the smallest where a loop can fill a small slice. On the cubic 3 × 3 × 3 torus all 15 also differ (\|z\| 7.4 to 19.6). Lone loops are absent on 2 × 2 × 2. | A recorded computation | `LOOP-SHIELD-20261023-001B-E001` |

## Challenged assumptions

The decision note records four workspace assumptions this epic challenges:
- that the odd-loop identity is a fact about tori;
- that all twists odd on c are alike for a loop along c;
- that a seam next to the loop can carry only classes its graph carries;
- that the identity extends to 3-tori.

## Recommendation

**Full pivot: the three-literal side.**
- **The question.** A bounded direction search for a fair three-literal lattice world in which twisted sectors make sense and contradictions are not implication cycles.
- **The test.** Then one exhaustive small-torus test of whether any exact twist identity survives beyond symmetries.
- **Interest:** 1/3.
- **Alternatives:** the complete map of exact twist relations on genus 2 (1/3), and a self-contained note on shielding (1/3).
- **Execution:** deferred to the owner.
