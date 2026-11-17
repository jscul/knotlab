# Closure of how knots build an order

Status: Proved

Ticket `KNOT-ORDER-20261117-001Z`, 2026-11-17. A ledger; it makes no new claim. The decision note is
`research/KNOT-ORDER-20261117-001/knot_order.md`. Referee pending.

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | A constraint excluding a two-change state while allowing every threshold must straddle both changes; knots in windows of r places cannot make a line. | elementary | A |
| 2 | Growing a line at an end needs a knot holding both ends and the new distinction (one knot per step: B(start, end, new), the start a hub); inserting between neighbours needs only them; exactly m + 1 single knots keep a line (all 34 kinds checked to m = 8). | elementary; computed | A, B (X1) |
| 3 | The states, with names and history erased, name every placement (ends at the largest count, neighbours at count 2); a states-only rule grew an exact line to n = 14; no direction is stored. | elementary; computed | A, B (G4) |
| 4 | The grown line is pairwise with an exact ruler 2\|i − j\|; box-triple betweenness on 3 × 3 and 3 × 4 grids allows exactly the row and column cuts (d = 2·L1, two independent orders). | classical cited (cut systems); computed | A, B (X2) |

**Recommendation:** Research directions; the first (grow the two-way grid with knots) starts on the coordinator's go-ahead.
