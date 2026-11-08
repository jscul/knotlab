# Closure of the switching-class epic

Status: Proved

Ticket `SWITCH-READ-20261108-001Z`, 2026-11-08.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/SWITCH-READ-20261108-001/switch_read.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Under hash seeds 0 to 23, HANDLE-COUNT A's generator gives each of TRISUM-READ's 17 glues one glue with Pfaffian and minimal signings in one switching class; 11 glues get two or three placements that are not isomorphic as spaces (25 in all). | new; computed | A |
| 2 | In all five pairs mapped (38 to 56 points), the native maps of the two placements are not isomorphic, neither with the glue's lines fixed nor under any bijection. | new; computed | A |
| 3 | In all five pairs the block of glue lines is identical, entry by entry. | new; computed | A |
| 4 | Removing a glue line creates at the atom lines with the same multiset of vectors in both placements; removing a line of an atom creates differently at glue lines. | new; computed | A |
| 5 | TRISUM-READ's frozen statements P1 to P7 hold on all five alternative placements. | new; computed | A |

## Pending

- **The other placements.** Nine more, 56 to 60 points, mapping in the background (`docs/LONG_RUNNING.md`, SWITCH-READ-M1), to be
  folded in by a follow-up commit.
- **Still open from earlier epics.** `JUNCTION-READ-20261106-001`, superseded in substance by TRISUM-READ; qualifying
  `FAR-READ-20261106-001-D002` and the second sentence of D001; qualifying `PHASE-HALO-20261103-001-D001` and
  `FACE-CLAIM-20261103-001-D003`; the SELECTION-NOTE erratum; superseding `KNOT-COMPOSE-20261101-001-D001`; whether counted length
  should ever count as a native magnitude.

## Recommendation

**Continue** (2/3): prove that the glue block of the native creation map depends only on the switching class (an intact atom acts as
one negated incidence, switching complements points, and the creation test should not see complementing).
- **Alternatives.** The glue block against Pfaffian counting (2/3, deferred); folding in the nine remaining placements (running).

The tables are in the decision note.
