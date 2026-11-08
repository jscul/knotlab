# Closure of distance across time

Status: Proved

Ticket `DISTANCE-20261108-001Z`, 2026-11-08.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/DISTANCE-20261108-001/distance.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Counted length is read by the substrate: along a route isolated by freezing, the far contact first needs the near ring at lag g·L + 1, additively, and at unequal spacing at 1 plus the cells carried. A40 is confirmed by its frozen test, pre-registered in 510ff23fc. | new as far as found; frozen test, exact; proved for every network | A, B (Theorem 1) |
| 2 | The earliest need any freeze allows is 1 plus the fewest cells of a route, g·δ + 1 with δ the contact graph's directed distance, a directed metric between contacts. | known-with-delta; proved | B (Theorem 2) |
| 3 | The most disjoint cuts separating two rings into native pieces is the ring graph's distance D, on every network; the most disjoint sets blocking a contact from a ring for good is δ. | known-with-delta (Robacker's dual of Menger); proved | B (Theorem 3) |
| 4 | An isolated induced route composes at the recurring lags its dynamics fixes, given by Lucas' theorem, with every route contact persistent. | known-with-delta; proved | B (Theorem 1) |
| 5 | The plain first need is the cone filtered by the parity of shortest routes: on time exactly when an odd number arrive; on the square torus Lucas' a AND b = 0 for one kind; on the plane never at offsets with v2(a) = v2(b). Not a metric. | known-with-delta; proved; triangle counts computed | B (Theorem 4, check 10) |
| 6 | Between a contact and its translate δ = (m/2)·D on square, triangular and honeycomb tori; D = ⌈δ/2⌉ for every ring and contact on the square torus; D = ⌈δ/3⌉ on triangular tori and a band on honeycomb tori, computed. | known-with-delta; proved; computed where marked | B (Theorems 4, 5; check 9), stress test |

## Answer

Distance across time is native in two exact forms: the cut length D, the ring graph's distance, and the time length δ, the contact
graph's directed distance, both proved on every network; the plain first need is the same cone filtered by parity and is not a metric.

## Pending the owner

- None new; carried: whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`; the SELECTION-NOTE erratum;
  superseding `KNOT-COMPOSE-20261101-001-D001`.

## Recommendation

**Research directions**, selected: distance without freezing (Payoff 2/3, Concreteness 3/3), awaiting the coordinator's go-ahead. The
table is in the decision note.
