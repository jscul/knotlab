# Closure of rules that read only the states

Status: Proved

Ticket `STATE-RULES-20261117-001Z`, 2026-11-17. A ledger; it makes no new claim. The decision note is
`research/STATE-RULES-20261117-001/state_rules.md`. Refereed (R1, confirmed with fixes; see the last section).

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | A single betweenness knot leaves N + d or 2N − d states; the one-knot fewest-states rule keeps k and λ from any start with an adjacent pair (line, 2 × 2, star: 20 runs each to n = 14). | local | A (S1, S2), B (E1, E2) |
| 2 | One step from a line makes at most two orders, and the line's zero-cost three-knot steps are exactly its C(n, 3) fills, each two orders (20, 35, 56 at n = 6, 7, 8); from one knot the only one is the 2 × 2 pattern. | local | A (S3, S4), B (E6) |
| 3 | The fewest-states rule with three knots grows the cube: Q3 at n = 8 and Q4 at n = 16 in 40 of 40 runs, counting extensions or classes; two orders with probability 1, 1, 1/2, 0 at n = 4 to 7 (5/12 at 6 with classes once). | computed (S5 proved, S6 conjectured) | A, B (E1, E3, E3c) |
| 4 | Uniform and softmax weightings give two orders in 0 of 40 to 50 runs at n = 10. | computed | B (E4, E5) |
| 5 | Reading which knots meet changes where the first fill can go and the odds (two orders 2/3 at n = 6 against 1/2) but not the destination; no knot-reading rule tried keeps two orders. | computed | B (E8) |
| 6 | A coin-free continuation invariant under every signed renaming exists once (parity, the 2 × 2 pattern) and then only fixed or free ones; under renamings with the global swap only, the 2 × 2 pattern has one invariant knot continuation (10 states). | computed | B (E7) |

**Recommendation:** Research directions; the first (a cap on knots per distinction) starts on the coordinator's go-ahead.

## After the referee (R1, 17 November 2026)

Confirmed with fixes, no Block; folded in the same day and logged in `docs/CORRECTIONS.md`. The rows above are kept as written.
- **Narrowing** of row 5. With 1,000 runs per start the two six-starts grow different bases (TV distance 0.76 at n = 7) with the
  same number of orders (two orders at n = 8: 375 and 361). The 2/3 against 1/2 at n = 6 is the knot arm's weighting, not its
  reading of knots (closure control 0.70, knot-local 0.65).
