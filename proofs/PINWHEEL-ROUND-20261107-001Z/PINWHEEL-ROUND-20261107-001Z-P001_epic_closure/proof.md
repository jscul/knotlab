# Closure of the pinwheel epic

Status: Proved

Ticket `PINWHEEL-ROUND-20261107-001Z`, 2026-11-07.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/PINWHEEL-ROUND-20261107-001/pinwheel_round.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Suppose a compact space of plane tilings with finite local complexity up to rigid motions is rotation-invariant and uniquely ergodic under translations. Then every rigid-motion-covariant metric on edges with linear bounds has, for almost every tiling, the same asymptotic speed in every direction. | standard ergodic argument; proved | A |
| 2 | In pinwheel tilings, the least bond through two edges and the least cycle through two edges are asymptotically a constant multiple of Euclidean distance in every direction. These are the bond distances of the parity laws with knots at corners and with knots on tiles. | known for the length-weighted edge metric (Radin–Sadun 1996); new for these counts as far as found; proved, citing Radin | A |
| 3 | The 1:1 right triangle's substitution is the periodic tetrakis triangulation: its two bond distances have octagonal (π = 10/3) and square (π = 4) unit balls. The 1:2 triangle cut frame-consistently keeps four orientations. A disc of radius R in a pinwheel tiling meets O(log R) orientations. | elementary; proved | A |
| 4 | Measured with exact least cycles: the pinwheel corner law's anisotropy falls from 1.106 to 1.030 between R = 8 and 128, and the tile law's from 1.33 to 1.08. The frame-consistent cut keeps a growing four-fold harmonic. The 1:1 laws sit on their exact polygons. | exploratory experiment | B |

## Answer

- **Round without coins.** A law with no coins has a round circle: the parity law on the pinwheel tiling.
- **What makes it round.** The roundness needs an irrational angle together with tiles of both handednesses, and it is exact only
  as a large-scale trend.

## Pending the owner

- **Carried.** Whether a native knot must also be natively bound (`LOGIC-AXIS-20261107-001`).
- **Carried from earlier epics.**
  - PHASE-HALO and FACE-CLAIM qualifications.
  - The SELECTION-NOTE erratum.
  - Superseding KNOT-COMPOSE D001.
  - Counted length as a native magnitude.

## Recommendation

**Continue**, as a fresh epic: the pinwheel grown with nothing drawn.
- **Ratings.** Payoff 2/3 — Substantial · Concreteness 2/3 — Testable.
- **The task.** Write the substitution as a rule on knots and their shared distinctions, with labels but no coordinates. Check that
  it regrows the pinwheel's law exactly, up to isomorphism, at levels 1 to 7.
- **Alternatives.** The spectrum of rational π among periodic laws (Payoff 1/3 · Concreteness 3/3); a proved rate for the
  rounding (Payoff 1/3 · Concreteness 1/3).

The table is in the decision note.
