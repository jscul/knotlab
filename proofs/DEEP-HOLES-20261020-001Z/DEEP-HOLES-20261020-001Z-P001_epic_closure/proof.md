# Closure of the deep-holes epic

Status: Proved

Epic `DEEP-HOLES-20261020-001` was closed on 2026-10-20, after its two
tickets ended. This is a ledger: one line per conclusion, with its novelty
label and evidence. It makes no new claim. The decision note is
`research/DEEP-HOLES-20261020-001/deep_holes.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | In the complex of partial solutions, a knot on three Boolean distinctions is a hole at its own scope with rank \|E\| − 1 (E the excluded set), and the sum-mod-3 knot with rank 10. So every non-atom knot is a local hole, and the program's plain hole criterion certifies only level 2 on parity, sum-mod-3 and not-all-equal networks. | elementary; not found stated | `DEEP-HOLES-20261020-001B-P001` (prose, checked); census P3 |
| 2 | A Z_p charge network with nonzero total charge is refuted at the size of a star (3 on cubic graphs) by the affine relaxation over any ring of characteristic p and over Z. | known (Gaussian elimination for Tseitin) | `…001B-P001`; census P1 |
| 3 | Over every field in which p is invertible, the least refuting level is exactly the toggle width of the graph, whatever the charges. An integer sweep certificate refutes at it over every ring, and a closed-form Fourier solution exists one level below. | method standard (symmetrization and characters); exact statement not found | `…001B-P001` (prose; certificates verified on 30 census networks and 19 ten-vertex graphs); census P2 and P5 |
| 4 | On connected cubic graphs with at least 4 vertices, the monotone toggle width is cutwidth + 1. The toggle width equals it on all 27 such graphs with at most 10 vertices, so the depth there is cutwidth + 1. Depth is not a function of treewidth. On one 10-vertex graph it exceeds the variable graph's treewidth + 1. | not found stated | `…001B-P001`; census P4 |
| 5 | Not-all-equal networks on every connected cubic graph with at most 8 vertices are possible. | finite evidence | `DEEP-HOLES-20261020-001A-E001` (exploratory, supported) |

## Recommendation

**Continue** in a fresh epic, with Interest **2/3 — Promising**: close the
cutwidth gap.
- Test whether the toggle width ever drops below its monotone version on the
  connected cubic graphs with 12 vertices.
- Then prove monotonicity, or record the counterexample.
- Execution is deferred to the owner.
