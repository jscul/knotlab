# Closure of the grid size epic

Status: Proved

Epic `PC-SIZE-GRID-20261020-001` closed on 2026-10-20. This is a ledger: one
line per conclusion, with its novelty label and evidence. It makes no new
claim. The decision note is
`research/PC-SIZE-GRID-20261020-001/pc_size_grid.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Over a field of characteristic other than 2, every PC (0/1 basis) or PCR refutation of the Tseitin formula of the a × b grid has size 2^{Ω(min(a,b))}. Size 2^{O(min(a,b))}·poly(ab) suffices, so the bound is tight up to the constant. As a corollary, resolution also needs 2^{Ω(min(a,b))} on grids. | not found stated after a targeted search; standard ingredients | `PC-SIZE-GRID-20261020-001B-P001` (prose; lemmas checked exhaustively on small grids and sampled on larger ones) |
| 2 | Deleting the edges of faces that lie at pairwise L∞-distance at least 3, excluding corner faces, keeps at least a fifth of every cut of the grid, and the factor 5 is attained. Both conditions are needed. | elementary; not found stated | `…001B-P001`; exhaustive check and controls |

## Recommendation

**Continue**, rated by barrier potential:
- **A (Interest 2/3).** 3-connected planar graphs of bounded degree with
  short inner faces: 2^{Θ(tw)} for resolution, PC and PCR.
- **B (Interest 2/3 if achievable).** All bounded-degree graphs, which is
  the open problem itself. There is no approach yet.
- **C (Interest 1/3).** Return to the foundations (question 9).

Execution is the owner's decision.
