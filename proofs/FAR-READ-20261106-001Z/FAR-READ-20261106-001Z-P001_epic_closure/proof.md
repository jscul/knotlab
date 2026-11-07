# Closure of the far-side reading epic

Status: Proved

Ticket `FAR-READ-20261106-001Z`, 2026-11-06.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/FAR-READ-20261106-001/far_read.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | The Fano plane and census 58 create at the same pairs. K4^(3) creates only where census 6 does, and census 6 creates without the Fano plane only at glue lines. At an atom line creation has one of four strengths. | new; computed (191 spaces, 142,420 pairs) | A |
| 2 | Every Fano atom acts as one from outside: every atom line outside it receives the same far-side vector from each of its lines. | new; computed (731 of 731 saved atoms, 334 of 334 fresh) | A, C |
| 3 | A four-step rule returns exactly the Fano atoms of all 191 saved spaces: twins, atom twins, a split into the finest parts of three or more lines that act as one, and reattachment through the Fano plane. Every step is needed. | new; computed (development) | B |
| 4 | Frozen, the rule returns exactly the Fano atoms of all 86 fresh spaces within the cost cap (334 atoms), including 24 where no yes/no rule can. The two-stage rule reads 51 and the source rule counts 68. | new; computed (fixed in advance) | C |
| 5 | In none of the 277 spaces are two lines of different atoms indistinguishable far side by far side. | new; computed | C |

## Pending the owner

- **From STRIP-RELAY.** Whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`.
- **Still open from earlier epics.**
  - The SELECTION-NOTE erratum.
  - Superseding `KNOT-COMPOSE-20261101-001-D001`.
  - Whether counted length should ever count as a native magnitude.
  - Whether to publish today's epics to knotlab and jscul.dev.

## Recommendation

**Continue** (2/3): prove that a Fano atom acts as one from outside.
- **The easy case.** Where removing any line of an atom leaves all its port patterns allowed, as in 576 of the 731 saved atoms by a scratch
  probe.
- **The hard case.** Atoms with five or more ports, where the proof must go through the receiving-cut law.
- **Alternatives.** Non-Fano handles through the receiving-cut law (1/3); a planar brace's relation from its faces (1/3).

The table is in the decision note.
