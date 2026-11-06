# Closure of the native-genus epic

Status: Proved

Ticket `NATIVE-GENUS-20261104-001Z`, 2026-11-04.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/NATIVE-GENUS-20261104-001/native_genus.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | The splitting lemma: whether a removal creates at a gluing line depends only on the atoms holding the two lines. Proved for atoms attached at a point; checked exactly for atoms attached at a line. | new | A, §3 |
| 2 | Each removal's halo is its own atom's; on plane glue, atoms attached at a line have no halo. | new; exact | A |
| 3 | The native count: the lines outside a largest creation-free set fall into one piece per atom when plane glue separates the atoms (416 of 420), and the pieces locate the atoms. | new; finite | B, §1–3 |
| 4 | Touching atoms merge; atoms meeting at a glue point merge through shared points; census-58 atoms can split through interior points; three atoms on the 4-point cube merge. | new; finite | B |
| 5 | On every three-fold space up to 22 points the count equals the genus in 10 of 32; it counts Fano atoms, not the trisum handle. | new; finite | B, §5 |
| 6 | Exploratory: blocks of mutual creation equal the genus in 29 of the 32 and in all 310 Fano pairs, overcount where two point-attached atoms hang from one Fano atom, and split census 58. | new; exploratory | B, §4–5 |
| 7 | Wires and hubs land one atom's halo on another's cut in every placement tested, and the count and each halo's attribution are unchanged. | new; finite, exact | C |

## Pending the owner

- **From STRIP-RELAY.** Whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`.
- **Still open from earlier epics.**
  - The SELECTION-NOTE erratum.
  - Superseding `KNOT-COMPOSE-20261101-001-D001`.
  - Whether counted length should ever count as a native magnitude.

## Recommendation

**Continue** (2/3): a native reading of the brace tree.
- **The question.** Do blocks of mutual creation, one-way creation and mutual silence recover a three-fold space's whole tight-cut
  decomposition (Fano atoms, cut directions, doubled squares), including where atoms touch?
- **First.** Fix a refined block statistic in advance, test it on fresh and larger families, and try to prove the block lemma for Fano
  atoms.
- **Alternatives.**
  - Proving that plane glue never creates, the premise every count here rests on (2/3).
  - The display rule (1/3).

The table is in the decision note.
