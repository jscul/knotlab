# Pre-registration: Leibniz boards

Epic `LEIBNIZ-BOARDS-20261110-001` (sub-goal B111, G1; program topology, group `spacing`), written on 2026-11-10 before any run, at
the coordinator's go-ahead.

## The question

`BOARD-DIST-20261110-001` proved that, with the board made of identity distinctions, a law that names no relation and allows an
infinite board allows the tree. Its theorem needs finitary clauses. Leibniz's rule in full, "two names whose views agree at every
radius are one place", is one infinitary rule the theorem does not reach. Under it the boards of a value law are the Schreier graphs
of the stabilizers of its solutions on the tree. Can such a law choose the plane?

## Frozen statements

- **S, the coordinator's form.** Every board is the tree or finite; refuted by an infinite board other than the tree.
  - **Disclosed: already refuted by hand.** While framing the epic, the horofunction law on Z/3 was found: a place of value k has
    exactly one neighbour of value k − 1 and three of value k + 1. Its solutions are Busemann functions of the tree's ends mod 3,
    and for the end x^∞ the stabilizer is ⟨x³⟩, so Sch(⟨x³⟩) is a board. Ticket A is to check this.
- **W, the dichotomy (the main target).** If some board is infinite, the tree is a board. Refuted by a law with an infinite board
  and no board on the tree.
- **P, the plane.** No law makes every board grow quadratically. Refuted by such a law. P follows from W.

## What is known before the run

- **No strongly aperiodic shift of finite type on free groups.** Every nonempty one has a solution with nontrivial stabilizer
  (Piantadosi 2008), so under Leibniz's rule every law with a solution has a board other than the tree. Free groups also carry
  shifts of finite type with no finite orbit, so some laws have no finite board.
- **Lemma A (sketch).** A periodic solution with a branching pattern has infinitely many disjoint, interchangeable half-trees.
  Independent choices there give a solution with trivial stabilizer, and choices repeated along one element give an infinite
  cyclic stabilizer.
- **Lemma B (sketch).** If no solution has trivial stabilizer, the Baire category theorem gives an h ≠ 1 whose fixed set has
  interior. Modifying a half-tree away from h's axis shows that the solutions in that interior are rigid there and finitely many.

## Frozen

- **Ticket B's census.** Its classes, prediction C1 (no law of the family undecided) and decision rules are in its contract
  (`experiments/LEIBNIZ-BOARDS-20261110-001B/LEIBNIZ-BOARDS-20261110-001B-E001_which_laws_leave_the_tree/contract.json`).
- **Stop rule, one epic.** Stop with W proved for every finitary value law over a finite alphabet, a law refuting W, or W reduced
  to an explicit statement with what failed recorded. If W is not settled, the line pauses; no second epic without a new route.

## Readings fixed in advance

- **Leibniz's rule is not finitary.** A positive answer to P would put dimension in a value law plus one infinitary identity rule,
  not in a CNF.
- **Identity is not contact (A51).**
