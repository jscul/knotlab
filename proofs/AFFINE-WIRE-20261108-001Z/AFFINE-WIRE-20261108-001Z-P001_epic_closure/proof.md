# Closure of a middle ring that carries without cancelling

Status: Proved

Ticket `AFFINE-WIRE-20261108-001Z`, 2026-11-08.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/AFFINE-WIRE-20261108-001/affine_wire.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | In affine chains binding and composition are read from the supports r_T(c) = e_c M^T, and persistence and composition are decided exactly by iterating two row vectors until they repeat. | known-with-delta (linear recurring sequences); proved | A |
| 2 | Of 9,216,000 affine chains, 2,376 keep both contacts persistent and compose at every lag from d + 1 on (380 at both contacts), 430 of them with the middle ring carrying c1's past across its own cells; verified on full state spaces, with a canonical knot check. | not found in prior work; exploratory search | B |
| 3 | One size past, with a middle ring of 8 cells, 80 chains in 40 of 337 composing rule-law groups still compose persistently. | not found in prior work; exploratory stress test | B |

## Answer

Gaps are not forced: on affine substrates two complete contacts between processes can coexist, persist and compose at every lag,
a persistent native network across time.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Recommendation

**Continue** with native paths across time (G5, with G1): chains of four rings and three contacts built from the composing families,
with the gate's restrictions and transports. Rated Payoff 3/3 (Major), Concreteness 2/3 (Testable). The table is in the decision
note.
