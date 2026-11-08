# Closure of the shared coin

Status: Proved

Ticket `GROW-COIN-20261107-001Z`, 2026-11-07.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/GROW-COIN-20261107-001/grow_coin.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Refinement maps K_m to K_jm, is all-or-nothing in every order, and keeps the seed's shape, so it never places a corner. | known-with-delta (Goldberg–Coxeter); proved | A |
| 2 | Ring accretion gives K_m exactly when the four turns of one ring become corners. | proved | A |
| 3 | With turns decided one at a time, ring accretion also closes lopsided spheres: 38 distinct closures up to 100 triangles, 3 round; 12 of 400 random-coin runs non-round. | new as far as found; computed | A |
| 4 | In single-strip accretion a turn's decision window is the same in every lap, so tying the four corners needs a carried bit, a hidden witness. | known-with-delta (local growth rules); proved, windows computed | A |
| 5 | The window law of one order, run in random orders, closes only small round spheres or is stuck. | computed | A |

## Answer

Growth does not remove the witness. Refinement keeps roundness only by never placing a corner; accretion must place corners, and
making them agree needs a carried bit.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Recommendation

**Continue** with hardness without roundness (G3): extend the knot sphere's width bound to spheres whose corners are far apart.
Rated Payoff 2/3 (Substantial), Concreteness 2/3 (Testable). The table is in the decision note.
