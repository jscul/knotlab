# Closure of the Gallai-knots epic

Status: Proved

Epic `GALLAI-KNOTS-20261020-001` closed on 2026-10-20. This is a ledger: one
line per conclusion, with its novelty label and evidence. It makes no new
claim. The decision note is
`research/GALLAI-KNOTS-20261020-001/gallai_knots.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | In the proper q-colouring law, hidden witnesses forming a connected graph W of maximum degree at most q, each carrying q − deg(v) leaves, give a leaf relation that passes K1–K3 exactly when W is a Gallai tree with a leaf. K2 and K3 hold for every W; a non-Gallai W imposes nothing. | Classical core (Borodin 1977; Erdős–Rubin–Taylor 1979); the reading is the program's | `GALLAI-KNOTS-20261020-001B-P001`, Theorem 3; census `GALLAI-KNOTS-20261020-001A-E001` (27 knots, exactly the 27 Gallai trees among 83 networks) |
| 2 | Gluing two witness networks at a vertex joins their excluded leaf colourings through a unique hidden split of the glued vertex's colours. | Elementary; the composition reading is the program's | `…001B-P001`, Theorem 1 |
| 3 | The excluded colourings of a Gallai tree are its block colour-set systems. Their number is q! times a product of block masses, and q!·((q − 1)!)^(k−1) for any tree on k witnesses. | Systems classical (Kostochka–Stiebitz–Wirth 1996); the multiplicative mass was not found stated | `…001B-P001`, Theorem 4 |
| 4 | On the d-regular tree, every finite subtree with chosen leaves carries such a knot. All of them are native at almost every broadcast world when p* = 0, including d = q for every q ≥ 3. The rainbow world at d = q makes none native. | Short consequence of the freezing recursion | `…001B-P001`, Corollary 5 |
| 5 | Two knots sharing a visible vertex form a common hub, not a knot. In this law, knots compose by fusing into one knot over a larger hidden witness network. | Elementary | `…001B-P001`, Remark 6 |
| 6 | Witness networks with a vertex of degree q + 1 also give knots (9 for q = 3 and 1 for q = 4 on at most 6 witnesses). These are not classified. | Observation | `…001A-E001` |

## Recommendation

**Research directions.** Knots as circuits: is composition like cycles the
mark of group-like, or almost affine, laws?
- First step: a prior-art check, then a census of small relations.
- Interest 1/3. Deferred to the owner.
- The alternative already on the table is to convert the Tseitin results into
  one note (2/3).
