# Closure of the glue-reading epic

Status: Proved

Ticket `GLUE-READ-20261106-001Z`, 2026-11-06.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/GLUE-READ-20261106-001/glue_read.md`.

Words (2026-11-11). Reworded under the owner's language rule: a three-fold or knot space is now a three-regular
contradiction, its lines knots and its points distinctions, and a Fano atom a Fano piece (Intuitions guide, Glossary). The
mathematics is unchanged; the earlier text is in git history.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Creation at a closed Fano piece from a removal beyond one of its cuts depends only on the relation the removal's side shows on that cut. Emitter's knots receive iff the ports may be equal. A receiver's cut knot receives iff the other two ports are not forced equal; its intact knot iff the side tells the ports apart. | new; proved (exhaustive, 8,190 cases) | A |
| 2 | In actual contradictions the removal's side acts only through that relation. | new; computed (47,550 census pairs) | A |
| 3 | Through Fano pieces the cut is always free (touching rule). Through glue the side can exclude a pattern pair or tie two ports. The touching rule holds wherever the side is free, and fails only at constrained sides. | new; computed (191 contradictions) | B |
| 4 | Joined glue knots are doubled-square knots meeting two or more of the Fano piece's ports. Split Fano pieces emit into a planar brace and split by the distinctions of the emitted knot, differing only on glue knots. | new; computed (191 contradictions) | B |
| 5 | The two-stage twin rule reads every Fano tree with at most four cuts per Fano piece, all 111 census contradictions and 57 of 80 random contradictions. | new; proved (Fano trees) and computed | C |
| 6 | In 15 random contradictions with planar glue, two knots of different Fano pieces are twins of the yes/no creation relation, so no rule reading only whether creation occurs returns their Fano pieces. | new; computed instances, elementary argument | C |
| 7 | Which far side creates separates every cross-Fano piece pair in all 191 contradictions, but varies inside Fano pieces. | new; computed | C |

## Pending the owner

- **From STRIP-RELAY.** Whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`.
- **Still open from earlier epics.**
  - The SELECTION-NOTE erratum.
  - Superseding `KNOT-COMPOSE-20261101-001-D001`.
  - Whether counted length should ever count as a native magnitude.
  - Whether to publish today's epics to knotlab and jscul.dev.

## Recommendation

**Continue** (2/3): reading with the far sides.
- **The question.** On the 191 saved exact maps, look for a rule that uses which far side creates to separate Fano pieces meeting one planar
  brace without splitting Fano pieces.
- **Alternatives.** Derive the relation a planar brace presents from its faces (1/3); read non-Fano handles through the receiving-cut law
  (1/3).

The table is in the decision note.
