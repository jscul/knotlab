# Closure of knots across time

Status: Proved

Ticket `TIME-KNOTS-20261107-001Z`, 2026-11-08.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/TIME-KNOTS-20261107-001/time_knots.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Written as its space-time law, a process's knots joining a cell's future value to first-row cells are exactly the minimally decisive sets of two or more cells of its T-step map; a decisive single cell gives a tie. | known-with-delta (implicants, certificates); proved | A |
| 2 | A nonconstant Boolean function has no knot in its graph exactly when it is a single conjunction or disjunction of literals: pairwise memory. | known-with-delta (elementary); proved | A |
| 3 | A linear rule has one two-time knot per lag, the support of p^T plus the cell: \|supp p\| + 1 places at every lag 2^k, 2^popcount(T) + 1 for rule 60; intermediate rows give 2 + w(T) in rule 102's light cone for T <= 6, and the cone is too small at T = 7. | known-with-delta (Lucas, Frobenius, Ledrappier); proved and computed | A |
| 4 | In one step of Life the knots are the 70 sets of four neighbours; the cell's own present value is in none. | proved by exhaustion | A |
| 5 | Of the 88 elementary automata over lags 1 to 6: 15 knot-free at every lag, 8 with one knot per lag, 49 growing, 16 other; rule 184's knots are all C(2T + 1, T + 1) sets of T + 1 cells (to T = 7). | not found in prior work; exploratory experiment | B |

## Answer

A process written as a law is a static law on its trajectories, and its knots across time are the minimal sets of past cells that
decide a future cell. A process knows its past only pairwise exactly when each future value is a single AND or OR.

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Recommendation

**Continue** with knots between processes (G5): two rings coupled by a contact cell, and which couplings bind both loops' pasts in
the contact's future. Rated Payoff 2/3 (Substantial), Concreteness 2/3 (Testable). The table is in the decision note.
