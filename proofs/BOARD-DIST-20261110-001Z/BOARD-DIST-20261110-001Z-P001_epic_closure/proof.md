# Closure of the board as distinctions

Status: Proved

Ticket `BOARD-DIST-20261110-001Z`, 2026-11-10.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/BOARD-DIST-20261110-001/board_dist.md`; the pre-registration is beside it.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | With names the words of F2 and an identity distinction per pair, the boards are exactly the Schreier graphs of subgroups of F2 (on a ball, the restrictions of them). | classical; proved | A (Theorem 1) |
| 2 | With no positive identity literal beyond the board axioms, refining an allowed board keeps it allowed; the tree is allowed whenever any board is. | proved | A (Theorem 2) |
| 3 | A law that names no relation and allows an infinite board allows the tree, so no such law forces the plane or any infinite board. | new as far as found; proved | A (Theorem 3) |
| 4 | Every finite board is the only board of some law that names no relation; identity of indiscernibles makes every board finite, and at radius 1 a plane-like abelian board always has a non-abelian sibling. | proved | A (Theorems 4 and 7) |
| 5 | The commutator rule with an aperiodic tile law forces exactly the plane. | classical ingredients; proved | A (Theorem 8) |
| 6 | Two boards differ in infinitely many identity distinctions, and off the tree every place holds infinitely many names: no distinction off the tree, and no identity distinction anywhere, is flipped by a finite change. | new as far as found; proved | A (Theorem 5) |
| 7 | Over the 1,024 Life-like one-bit laws the frozen predictions P1 to P4 hold with no violation; 768 laws allow every board, 31 none, 225 the tree without every board. | computed, exact, frozen | B |
| 8 | In 60 laws the square's identity distinction is knotted with two values it does not identify (56 single clauses of three, by knotlab). | computed, exact | B |
| 9 | The independent truncated-SAT code agrees for parity 0, parity 1 and the atom (P5). | computed, exact | B |

## Answer

No law that names no relation chooses the plane: whenever such a law allows an infinite board it allows the tree. Finite boards can
be forced, and one named relation, the square with an aperiodic law, forces exactly the plane. The census agrees with every frozen
prediction.

## Recommendation

**Continue**, selected #1 (Leibniz boards: identity of indiscernibles in the limit, where the unfolding theorem does not reach),
unless the coordinator chooses otherwise. The table is in the decision note.
