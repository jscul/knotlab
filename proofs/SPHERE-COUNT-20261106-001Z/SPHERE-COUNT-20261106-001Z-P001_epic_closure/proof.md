# Closure of the sphere-count epic

Status: Proved

Ticket `SPHERE-COUNT-20261106-001Z`, 2026-11-06.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/SPHERE-COUNT-20261106-001/sphere_count.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | The violated line of a single-defect state can be pinned. Frozen states (concentric alternating rings) block local moves in the bulk at every radius up to 3, and on K_8 by whole-sphere states at radius 2 and 3 for each adjacent line of the central line. | known-with-delta; proved | A, §1–2 |
| 2 | Random states always move (149 of 149 pairs within radius 2). | measured | A, §2 |
| 3 | In label states (1-Lipschitz Z6 heights through six sublattice patterns) every triangle is not-all-equal except at vortices. A counterclockwise vortex is a violated line and a clockwise one a monochromatic face. | known-with-delta; proved | A, §3 |
| 4 | Resolution width Ω(√n) reduces to the flat-state pursuit lemma, which is open. The size step (B) was retired before activation. | reduction | A, B |

## Answer

- **Open.** Whether the sphere's Euler count is hard for resolution is not decided.
- **The planned route fails at its first step.** Unlike Tseitin's charge, the violated line is a height vortex that frozen states can
  pin. A width proof must keep Duplicator's states flat.

## Pending the owner

- **From STRIP-RELAY.** Whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`.
- **Still open from earlier epics.**
  - The SELECTION-NOTE erratum.
  - Superseding `KNOT-COMPOSE-20261101-001-D001`.
  - Counted length as a native magnitude.

## Recommendation

**Continue** (2/3): the flat-state pursuit lemma.
- **Steps.** Construct label states on the octahedral sphere with corner structures. Prove that the vortex's six strings re-route in
  thick pebble-free regions. Run the giant-component Duplicator for resolution width Θ(√n).
- **Alternative.** A literature search for planar height-function principles with known resolution bounds (1/3).

The table is in the decision note.
