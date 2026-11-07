# Closure of the chain-transfer epic

Status: Proved

Ticket `CHAIN-TRANSFER-20261106-001Z`, 2026-11-06.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/CHAIN-TRANSFER-20261106-001/chain_transfer.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | The touching rule holds at every distance in Fano trees: a line receives creation from a removal in another atom exactly when it touches its atom's cut facing the removal. With the block lemma, creation on a Fano tree is fixed by its tree. | new; proved (47 chain profiles, closed after three atoms; 12,894 verdicts) | A |
| 2 | A removal leaves the three ports of every cut beyond it free, and the receiving atom alone decides creation. | new; proved | A |
| 3 | BRACE-TREE's source rule keeps one block per atom on every Fano tree of at most five atoms (100,830) and fails at six; a second failure occurs at seven atoms with non-collinear points. | new; proved (exact creation maps of both counterexamples) | B |
| 4 | Twins and footprints read the atoms and the directed tree of every Fano tree whose atoms have at most four cuts (condition N). Where N fails, the rule loses the tree. | new; proved (by hand from 1 and the block lemma; exhaustive up to five atoms; random trees) | C |
| 5 | Through plane glue the reading rule does not extend as stated: a glue line can join an atom's twin class, and an atom can split into three twin pairs. No class ever mixes two atoms. | new; computed (BRACE-TREE C's 111 fresh spaces, exact creation maps) | C, check 5 |

## Pending the owner

- **From STRIP-RELAY.** Whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`.
- **Still open from earlier epics.**
  - The SELECTION-NOTE erratum.
  - Superseding `KNOT-COMPOSE-20261101-001-D001`.
  - Whether counted length should ever count as a native magnitude.
- **Unaffected.** `BRACE-TREE-20261105-001-D002` and `D003` stay correct as stated, since their spaces have at most four atoms.

## Recommendation

**Continue** (2/3): reading through plane glue.
- **The question.** Add plane pieces to the profile automaton, starting with doubled squares and the smallest planar braces, and look for
  one rule that reads the atoms, and so the genus, of every three-fold space.
- **Alternatives.** Non-Fano handles through the same automaton (1/3); the bridge to proof complexity (2/3).

The table is in the decision note.
