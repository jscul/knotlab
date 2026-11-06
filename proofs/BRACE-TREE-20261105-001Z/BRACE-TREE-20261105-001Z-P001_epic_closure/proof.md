# Closure of the brace-tree epic

Status: Proved

Ticket `BRACE-TREE-20261105-001Z`, 2026-11-05.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/BRACE-TREE-20261105-001/brace_tree.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | The Fano plane's creation map is complete; a Fano atom attached at a line creates among its lines exactly as the Fano plane does, so its lines form one block. | new; proved | A, §1–2 |
| 2 | Atoms attached at a point form one block too, on every design tested. | new; computed | A, §3 |
| 3 | Across a cut between two atoms, cut lines are mutual and intact lines create one way at the emitter: the cut's direction is read natively. | new; computed (676 pairs, then 213 cuts) | A, §4; B, §4; C |
| 4 | The native relation between two atom lines is a function of their place in the decomposition wherever only atoms join them; through plane glue it can depend on more. The prediction as stated (every place) is refuted. | new; computed | B, §1–2 |
| 5 | Glue lines are silent to each other when no handle lies between; across a non-Fano handle (B) or a Fano atom (C, one class) they can create. B's glue prediction is refuted as stated. | new; computed | B, §3; C, §4 |
| 6 | The source rule counts the Heawood braces, and the genus, on every space without a non-Fano brace: 47 of 47 where it was found, 110 of 110 fresh spaces (all three-fold classes of 23 to 26 points and new trees). | new; computed | B, §5; C, §5 |
| 7 | Non-Fano handles (census 58, the trisum brace) are not read: the rules do not fix their relations and the source rule miscounts them. | new; computed | B; C |

## Pending the owner

- **From STRIP-RELAY.** Whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`.
- **Still open from earlier epics.**
  - The SELECTION-NOTE erratum.
  - Superseding `KNOT-COMPOSE-20261101-001-D001`.
  - Whether counted length should ever count as a native magnitude.

## Recommendation

**Continue** (2/3): a two-bit screening lemma.
- **The question.** Does a side attached at a line, which passes its line's six patterns to the cut, act as that line for creation as
  well as for solutions?
- **What it would give.**
  - The splitting lemma in full.
  - Likely the block lemma for atoms attached at a point and the one-way rule across cuts.
  - The way to a theorem that the source rule counts Fano atoms.
- **Alternatives.**
  - What native creation sees in non-Fano handles (2/3).
  - Testing the source rule beyond 26 points with SAT enumeration (1/3).

The table is in the decision note.
