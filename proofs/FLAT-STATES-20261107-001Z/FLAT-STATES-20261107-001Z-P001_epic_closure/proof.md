# Closure of the flat-states epic

Status: Proved

Ticket `FLAT-STATES-20261107-001Z`, 2026-11-07.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/FLAT-STATES-20261107-001/flat_states.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Flat states exist on the whole octahedral knot sphere. Each of the six corners twists labels by exactly −1, so for every point z and every six disjoint cut paths from z to the corners, one constant label developed over the cut sphere violates exactly one line, through z. | known-with-delta; proved | A, §1–2 |
| 2 | Re-routing the cut inside a region changes colours only there; from shortest cuts the vortex steps to every neighbour inside radius 3. | proved (locality); measured (steps) | A, §3 |
| 3 | The knot sphere contains one-sided 2D Sperner: a depth-2 decision-tree reduction whose violated lines are exactly the fully labelled triangles oriented like the boundary. | new as far as found; proved | B, §1–2 |
| 4 | Window criterion: pebbled colours admit a Sperner state with a given full triangle iff a difference system on pebble sheets has no negative cycle; obstructions need tight closed walks through pebbles. | standard technique; proved | B, §3 |
| 5 | Resolution width Ω(√n) for the knot spheres reduces to width Ω(m) for grid Sperner, which reduces to an open winding-control lemma. | reduction | B |

## Answer

- **Open.** The width of the sphere's count is not decided.
- **The question is now a Sperner question.** The knot's Euler count on the sphere is a one-sided Sperner principle, with the six
  corner disclinations as its boundary.
- **The literature gives no ready-made reduction.** Dimer and matching bounds use edge variables; Sperner is the nearest known
  principle, and its resolution width was not found.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Recommendation

**Continue** (2/3): the resolution width of 2D Sperner.
- **Steps.** A corridor Duplicator (the door path with a buffer, as in Itsykson et al.'s tree-like adversary) plus the window criterion.
  The open point is keeping forced windings along pebble chains small.
- **Payoff.** Width Θ(√n) for the knot spheres.
- **Alternative.** Check whether the level-3 Sherali–Adams refutation is unary, which would place the sphere's count in PPADS (1/3).

The table is in the decision note.
