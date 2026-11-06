# Closure of the all-graphs epic

Status: Proved

Epic `GENERAL-SIZE-20261020-001` closed on 2026-10-20. This is a ledger: one
line per conclusion, with its novelty label and evidence. It makes no new
claim. The decision note is `research/GENERAL-SIZE-20261020-001/general_size.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Resolution and PCR size of Tseitin formulas transfers along weak immersions, at a 2^{O(Δ)} factor. Identifying vertices is a weakening. | not found stated (targeted search) | `GENERAL-SIZE-20261020-001B-P001`, with checks on K₃,₃ and Petersen immersed in grids |
| 2 | Every connected graph of treewidth t needs resolution and PCR size 2^{Ω(t^{1/9}/polylog t)}. | PCR: not found stated. Resolution: Galesi et al. give 2^{t^{Ω(1)}} | `…001B-P001` |
| 3 | The open problem, up to polylog factors, follows if every subcubic graph has a cellular or compact topological minor keeping its treewidth up to polylog factors. Asking only for immersions does not weaken this hypothesis. | not searched separately | `…001B-P001` |
| 4 | On wall networks with block-scrambled bundles, every topological minor H has tw(H)² = O(m(\|V(H)\| + mwb)). With an expander skeleton, whose treewidth lower bound is sketched, compact minors fail at b = √w. Measured cells have length about 4 + √b. Uniform bundles give a compact ladder minor (spectral gap ≈ 0.04), and ordered bundles are cellular. | not searched separately | `…001B-P001` (proof, and checks E1–E3) |
| 5 | Corrections to earlier records:<br>• Dantchev and Riis (FOCS 2001) proved resolution 2^{Ω(n)} on the n × n grid, which earlier novelty lines missed;<br>• Lemma 5 of `CELL-SIZE-20261020-001B-P001` holds multiplicatively. | correction | the decision note |

## Recommendation

**Research directions.** Read the Dantchev–Riis grid argument, which uses no
cell restrictions. Decide whether it extends to planar graphs beyond grids, or
to the block-scrambled networks. Compare this with converting the PC-degree
and PCR-size results. Interest 2/3. The search is deferred to the owner.
