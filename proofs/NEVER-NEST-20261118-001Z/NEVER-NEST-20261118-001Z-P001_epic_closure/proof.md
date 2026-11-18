# Closure of a rule that never nests its fills

Status: Proved

Ticket `NEVER-NEST-20261118-001Z`, 2026-11-18. A ledger; it makes no new claim. The decision note is
`research/NEVER-NEST-20261118-001/never_nest.md`. Referee pending.

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | A subdivision keeps k and lambda; on a line with fills of triples a full grid needs at most two middles and every allowed fill. | local | A (N1, N2) |
| 2 | The never-nest rule with any old pairs (NNF), told to keep at most two orders and reading only the states, reaches a full grid from any line before its first subdivision and then refills every new row or column forever. | local (median completion classical) | A (N3, N4), B (R2, 250 of 250 runs) |
| 3 | The corner rule across crossing splits (CC) refills from a full grid forever and never fills a line; a split that crosses nothing never comes to cross under it, so after one fill of a line it reaches a full grid exactly when that fill's ends are the line's ends. | local | A (N5, N6 after the read-out), B (R2) |
| 4 | The never-nest rule with knots only on co-knotted pairs (NN, B197) keeps two orders at every step and grows full two-way grids: median fill fraction 0.80 on steps 21 to 40, a full grid at some n from 30 to 40 in 93% to 100% of runs, from every bracketing of 5 to 8; exact to n = 12 with two orders with probability 1. | computed | B (R1, E1) |

**Recommendation:** Research directions; the first (who picks two: a cap of d orders, and a rule told no number) is recommended next.
