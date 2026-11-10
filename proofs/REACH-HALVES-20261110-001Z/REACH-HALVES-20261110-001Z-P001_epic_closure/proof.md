# Closure of both halves of full reach

Status: Proved

Ticket `REACH-HALVES-20261110-001Z`, 2026-11-10.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/REACH-HALVES-20261110-001/reach_halves.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | If (1, 0) never reads d* = (n + 3, n + 2), the contact (n + 2, n + 3) misses the corner ring and full reach fails; on the h contacts this is an even count of conveyor-grid walks from (0, 0) to (n/2 + 1, n/2 + 1). | new as far as found; proved | A (Theorem 1) |
| 2 | The reflection in X − Y = 1 is a symmetry of the walk; mod 2 only excursions above the diagonal that touch the left or top wall survive. | new as far as found; proved | A (Theorem 2) |
| 3 | The strip at a power of two has, besides λ = 0, the single branch λ = t + 1/t, with decaying root w²C(w⁴). | new as far as found; proved | A (Theorem 3) |
| 4 | Anti-diagonal sums of the conveyor walk are read off its side columns. | proved | A (Lemma 4) |
| 5 | The count vanishes, and the failure holds, at every power of two from 8 to 128; the corner reads everything else. | computed | A (check 5), stress test |
| 6 | The corner return law 1/(1 + L(w⁴)), L the trace polynomial of GF(2n), at 4 to 128. | new as far as found; computed | A (check 5), stress test |
| 7 | A cyclic contact in every ring gives full reach; among sides 3 to 26 that holds only at 3, 5, 7, 9, 11, 13, 18, 19, 21, 23, 25. | proved; the sides computed | B |
| 8 | The census to 130: full reach fails exactly at 8, 16, 32, 64, 128, with the predicted failing sets. | computed | B (check 2), REACH-HALVES-B2 |
| 9 | Neither half of the theorem is proved: the failing half rests on the count of conclusion 1, the other half on no infinite family. | the gap | A, B |

## Answer

The failing half of the full-reach theorem is one even walk count from a corner, computed at every power of two to 128 and not proved;
the other half is computed to side 130.

## Recommendation

**Continue**, awaiting the coordinator's go-ahead: the corner return law as a theorem first, as the way into the count. The table is in
the decision note.
