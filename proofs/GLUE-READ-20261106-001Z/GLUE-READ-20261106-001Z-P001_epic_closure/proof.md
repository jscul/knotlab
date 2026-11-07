# Closure of the glue-reading epic

Status: Proved

Ticket `GLUE-READ-20261106-001Z`, 2026-11-06.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/GLUE-READ-20261106-001/glue_read.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Creation at a closed Fano atom from a removal beyond one of its cuts depends only on the relation the removal's side shows on that cut. Emitter's lines receive iff the ports may be equal. A receiver's cut line receives iff the other two ports are not forced equal; its intact line iff the side tells the ports apart. | new; proved (exhaustive, 8,190 cases) | A |
| 2 | In real spaces the removal's side acts only through that relation. | new; computed (47,550 census pairs) | A |
| 3 | Through atoms the cut is always free (touching rule). Through glue the side can exclude a pattern pair or tie two ports. The touching rule holds wherever the side is free, and fails only at constrained sides. | new; computed (191 spaces) | B |
| 4 | Joined glue lines are doubled-square lines meeting two or more of the atom's ports. Split atoms emit into a planar brace and split by the points of the emitted line, differing only on glue lines. | new; computed (191 spaces) | B |
| 5 | The two-stage twin rule reads every Fano tree with at most four cuts per atom, all 111 census spaces and 57 of 80 random spaces. | new; proved (Fano trees) and computed | C |
| 6 | In 15 random spaces with plane glue, two lines of different atoms are twins of the yes/no creation relation, so no rule reading only whether creation occurs returns their atoms. | new; computed instances, elementary argument | C |
| 7 | Which far side creates separates every cross-atom pair in all 191 spaces, but varies inside atoms. | new; computed | C |

## Pending the owner

- **From STRIP-RELAY.** Whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`.
- **Still open from earlier epics.**
  - The SELECTION-NOTE erratum.
  - Superseding `KNOT-COMPOSE-20261101-001-D001`.
  - Whether counted length should ever count as a native magnitude.
  - Whether to publish today's epics to knotlab and jscul.dev.

## Recommendation

**Continue** (2/3): reading with the far sides.
- **The question.** On the 191 saved exact maps, look for a rule that uses which far side creates to separate atoms meeting one planar
  brace without splitting atoms.
- **Alternatives.** Derive the relation a planar brace presents from its faces (1/3); read non-Fano handles through the receiving-cut law
  (1/3).

The table is in the decision note.
