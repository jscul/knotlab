# Closure of recurring composition at every ring size

Status: Proved

Ticket `RECUR-PROOF-20261108-001Z`, 2026-11-08.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/RECUR-PROOF-20261108-001/recur_proof.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | A contact that reads two partners, cells reading only it and themselves, depends on both partners' first values at every lag. | known-with-delta; proved | A |
| 2 | The 64 two-apart families with rule 60 or 102 on each ring keep every contact persistent at every ring size s >= 4, and the last contact binds the end rings exactly when C(T - 3, m) is odd: composition at recurring lags at every ring size, at every lag at none. | known-with-delta (Lucas); proved | A |
| 3 | The same at every length: the last contact binds the first ring exactly when C(T - (n - 1), e) is odd. | known-with-delta; proved | B |
| 4 | Rule 102 is covered by mirror symmetry; the rule-90 families are not. | computed | decision note |

## Answer

A theorem for every ring size and every length, for the one-sided additive families. RECUR-PATH-20261108-001's repeated counts are
corrected in `docs/CORRECTIONS.md`.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Recommendation

**Continue**: native separation and cycles of rings on the proved families (backlog B12, for its own thread). The table is in the
decision note.
