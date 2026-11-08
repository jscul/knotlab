# Closure of paths through mixed middle rings

Status: Proved

Ticket `PATH-HYBRID-20261108-001Z`, 2026-11-08.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/PATH-HYBRID-20261108-001/path_hybrid.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Of 20,480,000 four-ring paths with one linear rule per ring and any laws, 16 are native, all one construction: 3-cell shift end rings, 5-cell rule-150 middle rings, the end contacts reading both neighbours and the middle contact relaying along the short arcs. | not found in prior work; exploratory search, every verdict exact, verified on full state spaces | A |
| 2 | Each end ring with its contact is a feedback shift register with polynomial x³ + x + 1; with rule 150 on the end rings the same paths keep no contact. | known-with-delta (shift registers); computed exactly | A, decision note |
| 3 | Of 3,175,200 paths with a hybrid second middle ring, 1,120 are native, each binding all four rings at its last contact. | not found in prior work; exploratory search, verified | B |
| 4 | Each of the 1,120 needs its hybrid ring; the last contact keeps two or three of its own cells; the smallest's knot meets all four rings. | not found in prior work; exploratory | C |
| 5 | The paths are tied to their sizes: no larger or five-ring version of the uniform construction is native, and the hybrid paths survive one more cell only on the far end ring. | exploratory stress test, exact | decision note |

## Answer

Native paths across time exist at particular sizes: with one rule per ring (one construction of 16 paths) and with hybrid middle
rings (1,120 paths). They do not transport, which leaves the network gate's transport clause open. NATIVE-PATH's candidate
obstruction does not hold; its diagnosis is corrected in `docs/CORRECTIONS.md`.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Recommendation

**Continue**: native paths that survive growth (Payoff 3/3, Concreteness 2/3). If no family stays native at every tested size,
record the size dependence, reassess A34 and take native separation on the found paths next. The table is in the decision note.
