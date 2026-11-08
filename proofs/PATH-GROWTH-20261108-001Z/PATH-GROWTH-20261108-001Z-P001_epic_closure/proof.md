# Closure of native paths that survive growth

Status: Proved

Ticket `PATH-GROWTH-20261108-001Z`, 2026-11-08.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/PATH-GROWTH-20261108-001/path_growth.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | No family of paths with one linear rule per ring is native at every size: with all four rings of 3, 4 or 5 cells no path is native at all, and the 8 longer families native at four rings fail at five. | not found in prior work; exploratory search, exact | A |
| 2 | Growth breaks composition, not persistence: persistent paths with short row cycles remain at every size, and none is native. | not found in prior work; exploratory measure, exact | B |
| 3 | Native paths sit at isolated shapes (3/5/5/3, 5/6/6/5, 4/7/7/5 in the map; five more with rule 150 on every ring), each family at one shape, none surviving one more cell. | not found in prior work; exploratory, exact, verified on full state spaces | B, decision note |

## Answer

No family survives growth, and binding at every lag is tied to particular sizes. By the epic's stop rule A34 is put under
challenge. Two corrections to earlier readings are logged in `docs/CORRECTIONS.md`.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Recommendation

**Research directions**: challenge A34 with composition at recurring lags across sizes (Payoff 3/3, Concreteness 3/3). If that
fails too, reassess G5 against question 4. The table is in the decision note.
