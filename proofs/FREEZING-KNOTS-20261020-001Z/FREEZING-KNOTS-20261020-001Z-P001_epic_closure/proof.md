# Closure of the freezing-knots epic

Status: Proved

Epic `FREEZING-KNOTS-20261020-001` closed on 2026-10-20. This is a ledger: one
line per conclusion, with its novelty label and evidence. It makes no new
claim. The decision note is
`research/FREEZING-KNOTS-20261020-001/freezing_knots.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | On the d-regular tree with the broadcast colouring, a vertex is frozen exactly when every other colour is carried by a neighbour frozen within its branch. Branches freeze with probability p*, the largest fixed point of the coverage polynomial. | classical (hard fields; naive reconstruction) | `FREEZING-KNOTS-20261020-001B-P001`, Theorem 1 |
| 2 | The star relation "not all q colours used" on q neighbours of a vertex passes K1–K3 at every degree d ≥ q. | elementary; the reading is the program's | `…001B-P001`, Theorem 2 |
| 3 | Under the source-aware reading, the star knot is native with probability (1 − p*)^q (1 − ζ) + (1 − μ)^q ζ. This equals 1 exactly when p* = 0. | not found stated; a short consequence of the recursion | `…001B-P001`, Theorem 3 |
| 4 | p* = 0 below d = 6, 10 and 15 for q = 3, 4 and 5. At and beyond those degrees, p* is at least 0.898, 0.854 and 0.876, and nativity is below 0.0011, 0.00046 and 0.00003. All values are certified exactly. Star knots stop being native exactly, and discontinuously, at the freezing threshold. | thresholds classical in substance (not compared with a table); the bound is new to the program | `…001B-P001`, Theorem 4 |
| 5 | At planted colourings of random regular graphs, the fractions frozen and native at radius L match the tree's exact values within about 0.01 at every measured radius. In small graphs (n ≤ 36), the source-blind relation over all colourings collapses from degree 5, together with the count of colourings. | exploratory evidence | `FREEZING-KNOTS-20261020-001A-E001` |
| 6 | As a threshold, native-knot density restates freezing. This was the stop condition set beforehand for this line. | assessment | decision note |

## Recommendation

**Research directions.** Run a bounded scan between two candidates:
- space from native moves (question 9);
- composition of native knots (question 3).

Interest 2/3. Deferred to the owner.
