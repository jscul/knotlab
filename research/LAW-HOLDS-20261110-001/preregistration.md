# Pre-registration: does the law decide which atom holds the unit?

Epic `LAW-HOLDS-20261110-001` (backlog B79, G15), written on 2026-11-10 before any run, at the coordinator's go-ahead.

## The question

In `RISE-ESCAPE-20261110-001`, with the law fixed, a unit settled at the genus-2 floor never left its Fano atom under state flips, even one
unit above the floor (exhaustive on five K_2 components; capped elsewhere). Is that because no state of that law at all has the unit
anywhere else?

## The test

On the 15 genus-2 floor states of `ATOM-LAYERS-20261110-001` (K_2 and K_3; one atom at l0, one at distance 1, 2 or 3):

- **H (hosts of the fixed law).** For every face v with three line corners, decide by SAT whether some state of the fixed law has no
  violated line, all three corners agreeing at v, and no other face with three agreeing corners (a floor state with the unit at v). This
  covers every state, not only those reachable by flips.
- **C (by class).** Repeat for each of the 16 sign classes of the genus-2 space (the law changed by a flat change of each class), and in
  each class read whether each atom acts as its line (it allows on its three outer points exactly the six patterns the line allowed) or is
  transparent (all eight).

## Expectations, frozen

- **L1.** For the learned law, every host face lies inside the atom the unit settled in or at that atom's junction faces: the law decides
  which atom holds the unit.
- **L2.** Across classes, the hosts follow the atoms' roles: in a class where exactly one atom acts as its line the hosts lie in that atom
  and its junctions; where both act as their lines there is no floor state (the sphere's contradiction returns); where neither does, the
  hosts include upper faces.

## What would count against them

A host face of the learned law outside the settled atom and its junctions (against L1: then the trap is in the dynamics, not the law); a
class whose hosts do not follow the atoms' roles (against L2).
