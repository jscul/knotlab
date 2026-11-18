# Closure of who picks the number of orders

Status: Proved

Ticket `PICK-TWO-20261118-001Z`, 2026-11-18. A ledger; it makes no new claim. The decision note is `research/PICK-TWO-20261118-001/pick_two.md`. Referee pending.

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | λ never decreases; the corner rule across crossing splits keeps every relation of splits, so the start's number of orders; one fill on a line makes exactly two orders. | local | A (S1, S2, S6) |
| 2 | A cap of d orders gives exactly d, with full d-grids before the first subdivision and recurring (d = 3 from lines of 5 to 8, d = 4 from the line of 5 and Q4). | local (median completion classical) | A (S3), B (C1) |
| 3 | A greedy price on states and orders raises at a full non-cube grid iff its increment is below two states; linear prices give one order or unboundedly many, quadratic ones settle where their increments cross two (4, 3, 2, 1 for w = 0.25, 0.35, 0.5, 1.0). | local | A (S4, S5), B (C2, C3) |
| 4 | Of six rules told no number, the seed-and-copy rule grows full two-way grids from every line of 5 to 12 (its two is the line's one order plus one fill's two sides); the odd-cycle rule does too, as the cap in parity's words; every rule keeps three from Q3 and the 3 x 3 x 3 grid. | computed (S6, S7 proved) | A (S6, S7), B (C4) |

**Recommendation:** Research directions; the distance on the grown grids (A97) is recommended next.
