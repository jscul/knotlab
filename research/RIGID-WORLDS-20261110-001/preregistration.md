# Pre-registration: rigid worlds at radius 2

Epic `RIGID-WORLDS-20261110-001` (`BOARD-DIST-20261110-001` direction 2, G1; program topology, group `spacing`), written on
2026-11-10 before any run, at the coordinator's go-ahead.

## The question

Laws that name no relation never force an infinite board (`BOARD-DIST-20261110-001`), and the identity rule in the limit does not
force the plane for one-bit Life-like laws (`LEIBNIZ-BOARDS-20261110-001`). Finite boards can be forced. The constructive side of the
owner's idea asks for a rule that makes a two-dimensional world. Does a one-bit law with identity at radius 2 force every board to be
a genuinely two-dimensional torus?

## Frozen

- **The family, the rule, the definitions, the steps and the predictions** are in the contract
  (`experiments/RIGID-WORLDS-20261110-001A/RIGID-WORLDS-20261110-001A-E001_rigid_worlds_at_radius_two/contract.json`).
- **What counts as two-dimensional.** An abelian board Z²/Λ with no lattice vector of L1 norm at most 4, so that every radius-2 ball
  is the plane's. Thick cylinders, cycles and non-abelian boards do not count.
- **The bound.** A forced torus has at most 256 places (the radius-2 swap), so any family of forced sizes is bounded.
- **The failure line.** No law of the family forces a two-dimensional world (prediction R1).
- **Stop rule, one epic.** The census runs once and every law is classified; the family and the radius are not extended here.

## What is known before the run

- **The swap at radius 1** already rules out a forced plane-like torus for one bit. At radius 2 there is room below 256 places.
- **The controls behave** (disclosed). A law drawn from one 13-place torus forces exactly that torus, and the full law is refuted by
  the one-place board.
- **Recorded as the alternative.** Weakly aperiodic laws under Leibniz's rule (`LEIBNIZ-BOARDS-20261110-001` direction 2).
