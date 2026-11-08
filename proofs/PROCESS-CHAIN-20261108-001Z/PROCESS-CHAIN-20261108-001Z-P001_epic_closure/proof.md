# Closure of two contacts across time

Status: Proved

Ticket `PROCESS-CHAIN-20261108-001Z`, 2026-11-08.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/PROCESS-CHAIN-20261108-001/process_chain.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Listening contacts never compose: the far contact never depends on the far ring. | known-with-delta (elementary); proved | A |
| 2 | In a shared chain the far contact cannot depend on the far ring before lag d + 1, d the contacts' distance on the middle ring. | known-with-delta (light cones); proved | A |
| 3 | In linear chains a contact binds two rings exactly when the support of its row of M^T meets both. | known-with-delta (elementary); proved | A |
| 4 | Of 5,632 chains both contacts persist in 182, and in none of them does a contact bind the end rings at every lag from d + 1 on; one size past, with off-centre contacts, the same (198 persistent chains, none composing). | not found in prior work; exploratory experiment | B |
| 5 | Post hoc: 195 chains bind their ends at some lags of the eventual cycle, 154 with both contacts binding there, never in a chain whose two contacts both persist. | not found in prior work; exploratory, post hoc | B |

## Answer

Two contacts that each persist across time do not compose at the sizes tested; composition, where it occurs, comes and goes with
the pulses a middle ring carries, and those chains lose a contact's persistence.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Recommendation

**Research directions**: intermittent networks (A34's alternative; Payoff 2/3, Concreteness 3/3) and a middle ring that carries
without mixing (Payoff 3/3, Concreteness 1/3). Stop the process line after them if neither finds a native composition law. The table
is in the decision note.
