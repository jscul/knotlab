# Pre-registration: the board as distinctions

Epic `BOARD-DIST-20261110-001` (backlog B92, G1; program topology, group `spacing`), written on 2026-11-10 before any run of the
census, at the coordinator's assignment. It challenges A51, "Places and their neighbours are given before the rules".

## The question

In Life, and in every law the program has measured for space, the board (which places exist and which are neighbours) is fixed before
the rules are read. The owner's idea is that the axes themselves follow rules, governed by an essentially infinite CNF. Here the
board becomes part of every allowed state: names are the reduced words in x, y and their inverses, an identity distinction e(u, v)
says whether two names are one place, and one uniform value law reads each place and its four neighbours. Which boards do the rules
allow, and can they force a plane?

## What is known before the run

- **Boards are subgroups.** With transitivity, letter closure and constancy, the boards are exactly the Schreier graphs of subgroups
  of F2 (classical). This turns B92's question into one about which subgroups a law allows.
- **A sketch of an obstruction.** For a law that names no relation (every identity literal relates the same offset of two base
  names), an allowed infinite board seems to force the tree to be allowed too, by compactness. Ticket A is to prove it or find the
  gap. If it holds, no such law forces the plane, and only finite boards can be forced.
- **The sharp side.** One named relation, the commutator e(u, u x y X Y), with an aperiodic tile law appears to force exactly the
  plane, so the line between drawn and chosen would run through naming a relation.

## Frozen

- **Ticket B's census, predictions and decision rules** are as written in its contract
  (`experiments/BOARD-DIST-20261110-001B/BOARD-DIST-20261110-001B-E001_which_boards_one_bit_laws_allow/contract.json`), frozen with
  the code's hashes. The family is the 1,024 Life-like one-bit laws and the atom; the boards are the tree, six lines, the plane and
  every finite board with at most six places; identity of indiscernibles is tested at radius 1; an independent truncated-SAT code
  checks parity 0, parity 1 and the atom.
- **Stress, one size past.** Finite boards with 7 and 8 places; radius 2 for the three named laws; truncations at L = 7 and L = 5.
- **Stop rule.** Every prediction of ticket B decided and ticket A's targets proved or their failure recorded.

## What would count against

- **Against the obstruction.** A law that names no relation with an allowed infinite board and no allowed state on the tree; in the
  census, an allowed board with a listed cover that is not allowed, or the collapse allowed without every listed board.
- **For the owner's idea, in finite form.** A law whose radius-1 identity boards are all abelian and plane-like: a two-dimensional
  board chosen by the rules.
- **The board bound to the values.** A knot between the square's identity distinction and two values along the square other than
  the constancy clause itself.

## Readings fixed in advance

- **Identity is not contact.** Identity distinctions are distinctions of the law; a knot that involves one is reported as such and
  is never read as a contact (A51; equality is not a binding).
- **The source-aware reading** (adopted 2026-10-20) is applied as written: a distinction is native at a state only if a change of
  finitely many variables flips it. Target 5 of ticket A says what that does to boards made of names.
