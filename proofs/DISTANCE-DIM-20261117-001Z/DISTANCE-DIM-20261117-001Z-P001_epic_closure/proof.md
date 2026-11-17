# Closure of the dimension test: order and dimension read from the states

Status: Proved

Ticket `DISTANCE-DIM-20261117-001Z`, 2026-11-17. A ledger; it makes no new claim. The decision note is
`research/DISTANCE-DIM-20261117-001/distance_dim.md`. Referee pending.

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | On a base of two-place implications (states = up-sets of an order), w lies between u and v in the disagreement count iff w is in their interval; a pair is ordered iff a joint pattern never occurs. | folklore level | A, proved |
| 2 | If every comparable pair lies in a chain of three, betweenness gives the comparability graph, and on connected orders the order up to reversal; so the order dimension is read from the states. | known citations, local reading | A, proved |
| 3 | Read from the states: dimension 1 on a chain of 12; 2 on grids 4 × 4, 6 × 6, 3 × 7 and a corner-less grid; 3 on 3 × 3 × 3 and on S_3 with bottom and top; nothing on bare S_3. | computed, frozen | B (I1–I5) |
| 4 | Under not-all-equal knots no exact betweenness on the thread, the weave or the chain grid; the order-only gap graph has degree 12 on the weave, 8 and 2 on the chain grid (post hoc at L = 10, 12), 3–4 on the thread; levels grow quadratically, quadratically, linearly, and exponentially on the tree control. | computed, frozen (K3 failed on floating ties at L = 10, 12) | A (D4), B |
| 5 | The chain grid's transfer gap tends to Onsager's 0.3691; the weave's falls like one over the width (critical). | known (Onsager), computed | A (D5), B |

**Recommendation:** Research directions; the first (which knot laws on the weave are off-critical) starts on the coordinator's go-ahead.

## After the referee (R1, 17 November 2026)

Confirmed with fixes, no Block; folded in the same day with the owner's answer to B194 (knots first), logged in `docs/CORRECTIONS.md`.
The rows above are kept as written.
- **Narrowing** of rows 3 and 4's readings. Each reads the meeting pattern's own order or growth. Row 3 is the classical
  specialization order of the states' Alexandrov topology.
- **Narrowing** of row 4. Degree 12 belongs to the relative-neighbourhood test. The six-nearest test gives the same-class second
  neighbours and splits the weave's classes, and the unit-ball degree grows with L. No order-only reading gives an order.
- **Not a block.** Row 5's criticality is known exactly (Stephenson; Blöte and Hilhorst), with the conformal limit 1.238. Bare S_3's
  order and dimension 3 are read from its pairs, though not through betweenness.

