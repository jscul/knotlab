# Closure of the cell epic

Status: Proved

Epic `CELL-SIZE-20261020-001` closed on 2026-10-20. This is a ledger: one line
per conclusion, with its novelty label and evidence. It makes no new claim.
The decision note is `research/CELL-SIZE-20261020-001/cell_size.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Detour lemma: if every fixed edge has a detour in the remaining graph and no edge carries more than C detours, every cut keeps a 1/(C+1) fraction. | elementary | `CELL-SIZE-20261020-001B-P001` |
| 2 | Cell theorem: if every edge outside a bounded exceptional set lies on a cycle of length ≤ L with detours of length ≤ ℓ, Tseitin needs PC, PCR and resolution size 2^{Ω(tangle order)}. PC and PCR are over characteristic other than 2. | not found stated | `…001B-P001` |
| 3 | The corollaries:<br>• plane graphs with short faces pairwise sharing ≤ 1 edge: 2^{Θ(tw)};<br>• d-dimensional grids: 2^{Θ(k^{d−1})};<br>• every graph excluding a fixed minor, planar included: 2^{Ω_H(tw)} for PCR and resolution, by restriction and renaming to a wall topological minor. | not found stated (targeted search) | `…001B-P001` (checks of cell conditions, detours, retention, kill probabilities, transfer) |

## Recommendation

**Continue** with `GENERAL-SIZE-20261020-001`, as the owner asked: immersions,
the unconditional bound for all graphs, and the barrier. Execution is under
way at the owner's request.
