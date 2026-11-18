# Closure of a cap on knots per distinction, and what matched starts remember

Status: Proved

Ticket `KNOT-CAP-20261117-001Z`, 2026-11-18. A ledger; it makes no new claim. The decision note is
`research/KNOT-CAP-20261117-001/knot_cap.md`. Refereed (R1, confirmed with fixes; see the last section).

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | From one knot, a cap of three knots per distinction or two per pair gives the 2 x 2 pattern and then stops (probability 1). | local | A (T1, T2), B (K1) |
| 2 | Looser degree caps pass two orders (c = 4 to 6: mixtures, c = 4 often stalls; c >= 9: Q3 at 8 and Q4 at 16 in most runs); no cap keeps two orders growing at n = 16. | computed | B (K1) |
| 3 | The six-starts' growths correspond class for class with equal probabilities through n = 9 (number of orders exactly equal), first differing at n = 10; state distance 3/4 at n = 7. The five-starts (end hub, middle hub) differ in the number of orders from n = 7 (two orders 0.417 against 0.611). Under c = 5 the six-starts differ too (two orders at 10: 181 against 95 of 300). | computed (exact and sampled) | B (K2, K3, K5) |
| 4 | After erasure at n = 8 the distance is non-increasing and stays positive: 0.78, 0.66, 0.52, 0.41 (six-starts), 0.65, 0.46, 0.30, 0.20 (five-starts) at n = 8 to 11; with the knots kept, about 0.7 for the six-starts. | proved (T4); computed | A, B (K4) |

**Recommendation:** Research directions; S6 (cube growth at each doubling) starts next on the coordinator's queue.

## After the referee (R1, 18 November 2026)

Confirmed with fixes, no Block; folded in the same day and logged in `docs/CORRECTIONS.md`. The rows above are kept as written.
- **Narrowing** of row 4. For the five-starts the kept control fades too (0.65, 0.47, 0.40); only the six-starts' fading is due to
  erasure.
- **Not a block** on row 3. "Correspond class for class" is the multiset of probabilities of classes of states and knots and the
  order distributions; the classes of states differ. The c = 5 difference is the cap reading the fan's hub, not separate evidence.
