# Closure of intermittent networks across time

Status: Proved

Ticket `INTERMITTENT-NET-20261108-001Z`, 2026-11-08.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/INTERMITTENT-NET-20261108-001/intermittent_net.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | A chain's composing lags recur with the period of its T-step maps, so intermittent composition is persistent composition of a strobed chain whose phase is the only input the chain does not fix. | known-with-delta (eventual periodicity); proved | A |
| 2 | Linear and affine chains compose exactly where the far contact depends on both end rings; in any chain composition implies that dependence. | known-with-delta (elementary); proved | A |
| 3 | Of 7,040 chains, 244 compose at recurring lags; in 92 the chain singles out its composing lags (composition exactly at arrival, both contacts binding there), every one with an affine rule; never with a nonlinear rule; one size past, the same (24 of 112, all affine). | not found in prior work; exploratory experiment | B |

## Answer

Intermittent composition across time is native only on affine substrates, where it happens exactly when the influence of both ends
arrives and both contacts bind; persistent composition remains absent, so A34's strict reading stands for the contact gate.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Recommendation

**Research directions**: a middle ring that carries without cancelling, now on affine chains (Payoff 3/3, Concreteness 2/3), and
the pulse law of affine chains (Payoff 2/3, Concreteness 2/3). Stop the process line if arrival sets of affine chains always have
gaps. The table is in the decision note.
