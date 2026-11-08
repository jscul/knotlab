# Closure of composition at recurring lags across sizes

Status: Proved

Ticket `RECUR-PATH-20261108-001Z`, 2026-11-08.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/RECUR-PATH-20261108-001/recur_path.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | 452 families of paths compose at recurring lags with every contact persistent at every size of their schedule (rings of 4 to 9 cells, or 4 to 9 rings); none composes at every lag at two sizes. | not found in prior work; exploratory census, exact, verified independently and on full state spaces at the smallest sizes | A (E002) |
| 2 | With every contact binding only at the composing lags, 16,384, 1,016 and 748 families compose at every size of the three schedules. | not found in prior work; exploratory, exact | A (E002) |
| 3 | E001's every-lag control failed on a bug in that check; E002 fixes it, changes nothing else, and passes. | not applicable: a record of the failed control | A (E001, E002) |

## Answer

By the rule pre-registered in `docs/ASSUMPTIONS.md` before the census, A34 is overturned and replaced by A37: a path composes at
the recurring lags its own dynamics fixes, with every contact persistent. One earlier reading that rested on A34 is corrected in
`docs/CORRECTIONS.md`.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Recommendation

**Continue**: prove recurring composition at every size for the rule-60 family (Payoff 3/3, Concreteness 2/3). The table is in the
decision note.
