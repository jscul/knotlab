# Closure of which distance carries a base's information, and which gives an order with nothing skipped

Status: Proved

Ticket `DISTANCE-ORDER-20261117-001Z`, 2026-11-17. A ledger; it makes no new claim. The decision note is
`research/DISTANCE-ORDER-20261117-001/distance_order.md`. Referee pending.

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | In any base, c lies between a and b in the disagreement count iff no allowed state has a = b ≠ c; a not-all-equal knot is the count sum 2N. | elementary | A, proved |
| 2 | The disagreement table determines every nonempty not-all-equal base from four distinctions, and with N every base of complement-closed constraints on at most three places; it fails at three (one knot against none); parity is invisible to pairs. | local in this form, likely folklore | A, proved |
| 3 | A base-point chain of m distinctions allows at most 2m of their joint values; the threshold line is the base whose counts are a line. | local; classical (line metrics) | A, proved |
| 4 | On not-all-equal patterns with no cycle of knots, τ = −log₃ \|1 − 2d/N\| equals steps apart, and steps apart determines the base. | known model (tree distance), applied | A, proved |
| 5 | On the thread, the knot chain and the weave (L = 6, 9, 12) no distinction lies between two others in the disagreement count; it is not built from unit steps; with flips the longest chain is 4 (3 without the start's flip); τ is steps apart on the chain and not on the thread or the weave. | computed, frozen (9 of 9 held) | B |

**Recommendation:** Research directions; the first (can the weave's states read steps apart) starts on the coordinator's go-ahead.

## After the referee (R1, 17 November 2026)

Confirmed with fixes, no Block; folded in the same day and logged in `docs/CORRECTIONS.md`. The rows above are kept as written.
- **Narrowing** of row 5's reading, not its numbers. "No distinction lies between two others" holds under exact additive
  betweenness (A98). Read only as order, a weave start has twelve nearest neighbours with nothing between, the six knot-neighbours
  and six second neighbours of its own class. So the split on the thread and the weave rests on A98, and it is not a property of
  cycles: the census has cyclic bases with betweenness.
- **Not a block.** Row 2's statement 3(b) is proved for every n ≥ 4. Statement 7's "four" is six. "Non-constant P1" is 72 and 780 by
  the referee's definition. Bond distance has the order up to its offset.
- **Narrowing from the review of what the premise reopens.** Row 1's betweenness is a knot where its three pairs are free. On the
  chain of implications x → y → z the counts are 1, 1 and 2 with no knot.

**Recommendation, unchanged:** Research directions. The first, whether the weave's states read steps apart, is taken by the
dimension test on the coordinator's go-ahead.
