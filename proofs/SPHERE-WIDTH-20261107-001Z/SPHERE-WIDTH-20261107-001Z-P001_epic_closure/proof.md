# Closure of the sphere-width epic

Status: Proved

Ticket `SPHERE-WIDTH-20261107-001Z`, 2026-11-07.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/SPHERE-WIDTH-20261107-001/sphere_width.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | The sphere's count needs resolution width Θ(√n): every refutation of the octahedral knot sphere K_k has width ≥ c·k − 1, and O(k) suffices. | new as far as found; proved (two lemmas by sketch) | A |
| 2 | Window criterion on the sphere: pebbled colours admit a label state with a given vortex iff a sheet system has no negative cycle; obstructions are closed walks with a bounded number of steps per pebble. | standard technique; proved | A |
| 3 | Grid Sperner needs resolution width Θ(m) (fixed boundary, one- or two-sided). So does Itsykson et al.'s Sperner CSP, for which only tree-like size was known. The knot sphere gets its bound a second time through the Sperner reduction. | new as far as found; proved | B |
| 4 | On the disk, consistent pebble chains block only nearby triangles; chains turning 5 or more times fit no state at all. | measured | B |

## Answer

- **Settled.** Width is Θ(√n) for the sphere's count and Θ(m) for grid Sperner.
- **No winding control needed.** The winding-control lemma that `FLAT-STATES-20261107-001` named turned out to be unnecessary.
- **Size is open.** Resolution size is the remaining question.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Recommendation

**Continue** (2/3): resolution size of the sphere's count.
- **Steps.** Adapt Dantchev–Riis tiling games, with zones carrying random label states and the density bad set as the bad region.
- **Alternative.** Settle whether the level-3 Sherali–Adams refutation is unary (1/3).

The table is in the decision note.
