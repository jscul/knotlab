# Closure of why how the knots meet changes the number of orders

Status: Proved

Ticket `MEET-ORDERS-20261118-001Z`, 2026-11-18. A ledger; it makes no new claim. The decision note is
`research/MEET-ORDERS-20261118-001/meet_orders.md`. Referee pending.

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | The fewest-knot presentations of a line (n − 2 betweenness knots) are exactly its bracketings, Catalan(n − 2) per labelling. | local (no source found) | A (Lemma 0), B (P5 to n0 = 9) |
| 2 | Under KF3 the chance of two orders after the second new distinction is (1/(n − 2)) Σ [s + 2p + c] / [(n − 3) + 2(p + c)], a function of the bare bracketing: 5/12 for chains (shared distinction at an end or next to an end), 11/18 for the middle, 51/140 for both six-starts. | local | A (Theorem 1), B (M1, all 6,916 bracketings to n0 = 11) |
| 3 | Through n0 + 3 the distribution of the number of orders depends only on the bare bracketing and separates bare bracketings; at n0 + 4 the halves enter, with one tie at n0 = 8 and 24 pairs at n0 = 9. | computed (exact) | B (C) |
| 4 | Post hoc: the labelled base counts and odd-set weights follow the meeting pattern read as an abstract pattern (n0 = 5 to 7), not the pair-sharing tree (Q8 failed). | computed, post hoc | B (X, posthoc_meeting.py) |

**Recommendation:** Continue; the two-layer question (direction 1) is selected.
