# Pre-registration: abstract names

Epic `BARE-NAMES-20261110-001` (`WEAK-APER-20261110-001` direction 1, the same as `RIGID-WORLDS-20261110-001#3` and
`BOARD-DIST-20261110-001#3`; G1; program topology, group `spacing`; the challenge of A54), written on 2026-11-10 before any
computation, at the coordinator's go-ahead of 17:51 UTC.

## The question

- **A54.** Places are named by the words in x, y and their inverses. Every name then has four neighbour names, and every board is a
  quotient of the tree of names. The board line's four epics of 2026-11-10 rest on it.
- **The challenge.** Name places without letters: a countable set of names with no structure, a neighbour distinction for each pair
  of names, a value for each name, and laws that treat all names alike.
- **The questions.**
  - Can a finitary law then force any adjacency, or a bounded degree?
  - Does the unfolding theorem still hold?
  - What do the letters draw that a law cannot say for itself?
  - Are boards still frozen to finite changes, as `BOARD-DIST-20261110-001` found with letters (its conclusion 6)?

## Known before registration (disclosed)

Sketched by hand while this registration was written, before any computation:
- T1's argument: an infinite set of names on which adjacency and values are constant (Ramsey).
- T5's switch: two edges whose ends carry the same pair of values exchange partners.

## Frozen

- **Ticket A's targets.** T1 to T5, as stated in its proof stub
  (`proofs/BARE-NAMES-20261110-001A/BARE-NAMES-20261110-001A-P001_boards_of_abstract_names/proof.md`).
- **Ticket B's census.** Its family (the 1,024 one-bit count laws of degree four), relation, knot test, native moves, frozen boards and
  predictions are in its contract
  (`experiments/BARE-NAMES-20261110-001B/BARE-NAMES-20261110-001B-E001_board_value_knots/contract.json`).
- **Failure criteria for A54 (frozen at the coordinator's request).** The theory under test is that the obstruction "no law that
  names no relation forces the plane" does not depend on naming places by letters.

| Outcome | A54 |
| --- | --- |
| T1 or T3 refuted: a finitary law with no structureless state, or a count law with a board containing a cycle and no tree board | **Overturned**: the naming hid the tree |
| T1 and T3 proved, T5 refuted (boards frozen without letters too) | **Confirmed**: nothing proved depends on the naming |
| T1, T3 and T5 proved | **Confirmed for the obstruction**; its statement and "Rests on it" are split, recording that `BOARD-DIST-20261110-001`'s frozen boards (conclusion 6) and A53's reading rest on the naming |
| T2 refuted: some board whose degree comes from existence clauses is not a disjoint union of Schreier graphs | The history records that the letters draw more than degree and connectivity |

- **Failure criteria for the targets.** Each of T1 to T5 is proved, refuted by a counterexample, or left with its gap stated. A
  failure of ticket B's prediction C3 is a correction of T5.
- **Stop rule, one epic.** The census runs once, with no extension of the family. Leibniz's rule with abstract names is out of scope.
