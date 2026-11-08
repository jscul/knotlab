# Closure of which shared contacts persist

Status: Proved

Ticket `SHARED-CONTACT-20261108-001Z`, 2026-11-08.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/SHARED-CONTACT-20261108-001/shared_contact.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | At lag 1 a proposal-combining shared contact binds both rings exactly when its combiner is a parity and neither rule is canalizing at its centre; a self-blind contact binds exactly when its 4 x 4 table has no constant row or column (its parities exactly when both parts are nonconstant); for linear rings with an affine contact, binding at lag T is the contact's row of M^T meeting both rings. | known-with-delta (elementary); proved | A |
| 2 | Self-blind parities bind at every lag in 6.4% of 68,992 configurations against 4.5% for proposal parities on the same rings (4.2% against 4.7% without the rings that never read the contact), but on 157 rule-size pairs against 22; rules canalizing in a neighbour input persist in 1.1%. | not found in prior work; exploratory experiment | B |
| 3 | The fraction binding at every lag grows with ring size, from 1.1% to 20.5% for proposal parities and from 3.6% to 26.0% for self-blind parities between 3 + 4 and 8 + 9 cells. | not found in prior work; exploratory experiment | C |

## Answer

A contact shared by identity between two processes persists rarely on small rings and in a fifth to a quarter of parity
configurations on rings of 8 and 9 cells. Not reading its own value spreads persistence over many more rules but adds only a few
points. The full contact gate can pass across time with the contact a cell of both loops.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Recommendation

**Continue** with two contacts across time (G5, with G1): three rings in a chain sharing two contacts, and whether the chain binds
its ends through the middle ring. Rated Payoff 3/3 (Major), Concreteness 2/3 (Testable). The table is in the decision note. The
stress test at 9 + 10 cells is running as SHARED-CONTACT-S1 (`docs/LONG_RUNNING.md`).
