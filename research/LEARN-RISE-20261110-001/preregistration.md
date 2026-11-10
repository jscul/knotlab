# Pre-registration: learning at a rise

Epic `LEARN-RISE-20261110-001` (backlog B80, G15), written on 2026-11-10 before any run, at the coordinator's go-ahead.

## The question

The leftover unit at the genus-2 floor sits in whichever Fano atom still acts as its line (`LAW-HOLDS-20261110-001`, exact). To move it to
the other atom the law must change so that the atoms swap roles, and at the floor learning has no step. One unit above the floor a
violated line appears, so learning has somewhere to act. With state flips (A50) and learning steps (A26 sites) together, never more than
one unit above the floor, can the unit be brought to the other atom?

## The test

From the floor states of `ATOM-LAYERS-20261110-001` with the unit in atom 1 (atoms at l0 and at distance 1, 2, 3): all six on K_2 and the
three of K_3's first line orbit. Breadth-first search over pairs (law, state); a move is a single state flip or a single learning step
(a sign change on a side of a violated line or with an end at an even face); every configuration keeps W ≤ floor + 2 (one unit; on genus
2 W is odd). Stop at the first floor configuration whose unit sits inside atom 0, or at 300,000 configurations. Record the number of
moves, of learning steps and of flips on the path found, and the atoms' roles at the end.

## Expectations, frozen

- **R1.** The unit reaches atom 0 from every start within the cap, and at the end atom 0 acts as its line and atom 1 is transparent
  (`LAW-HOLDS-20261110-001` says it must).
- **R2.** The path needs learning steps (the law must change) and at least one flip (to make the first rise), and is short: at most 20
  moves on K_2.

## What would count against them

A start with no such path within the cap (against R1: then even learning at a one-unit rise cannot move the leftover); a path without
learning steps (impossible by `LAW-HOLDS-20261110-001`, so a bug).
