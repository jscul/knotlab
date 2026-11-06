# Closure of the cutwidth-depth epic

Status: Proved

Epic `CUTWIDTH-DEPTH-20261020-001` was closed on 2026-10-20, after its two
tickets ended. This is a ledger: one line per conclusion, with its novelty
label and evidence. It makes no new claim. The decision note is
`research/CUTWIDTH-DEPTH-20261020-001/cutwidth_depth.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Peak elimination: on a connected graph with at least 3 vertices, a toggle path of cost k can be rearranged so that every visited cut has at most k - 1 edges, with every step still costing at most k. | elementary; not found stated | `CUTWIDTH-DEPTH-20261020-001B-P001` (prose; run on 4,359 paths) |
| 2 | With the monotonicity lemma of Fomin and Thilikos (2003, Lemma 1, after Bienstock and Seymour), the toggle width is at least cutwidth + 1 on every connected graph with at least 3 vertices. A monotone sweep costs at most cutwidth + floor(maxdegree/2). | Lemma 1 known; the sandwich not found stated | `…001B-P001` |
| 3 | On graphs of maximum degree at most 3 the toggle width, its monotone version and cutwidth + 1 coincide. With `DEEP-HOLES-20261020-001B-P001`, an impossible charge network on a connected cubic graph is refuted by every field that cannot compute in its group exactly at cutwidth + 1. Modified cutwidth = cutwidth - 2 on cubic graphs. | not found stated (brief search) | `…001B-P001`; census P1 and P5 |
| 4 | On 1,453 census graphs (all connected cubic graphs on 4-12 vertices, all connected graphs on 3-6 vertices, 1,200 sampled graphs of degree up to 8): degree at most 3 gives cutwidth + 1 exactly; higher degree gives gaps of 2 and 3; vertex removals never help in either game. | finite evidence | `CUTWIDTH-DEPTH-20261020-001A-E001` (exploratory, supported) |

## Recommendation

**Continue**, as conversion, with Interest **2/3 — Promising**: write up the
depth theorem.
- Write a self-contained note on the exact depth of Tseitin-type charge
  networks for affine relaxations over a field of the other characteristic:
  cutwidth + 1 on cubic graphs.
- Run a targeted literature search first.
- Execution is deferred to the owner.
