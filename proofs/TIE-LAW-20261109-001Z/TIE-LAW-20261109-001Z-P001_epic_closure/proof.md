# Closure of the first tie of shortest routes

Status: Proved

Ticket `TIE-LAW-20261109-001Z`, 2026-11-09.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/TIE-LAW-20261109-001/tie_law.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | For two routes with common ends that meet nowhere else, the disc between them satisfies km = I + d_P, jf = I + d_Q and n = k + j − 2 − p_F − q_V, so equal lengths d give d = K(1 − 1/m − 1/f) + 1 − n with K = km = jf. | known-with-delta (combinatorial Gauss–Bonnet); proved | A (Theorem 1) |
| 2 | A shortest route runs along each cell of the disc on its side at most once, and runs at most ⌊m(f − 1)/f⌋ arcs about a ring and ⌊f(m − 1)/m⌋ about a face. | new as far as found; proved | A (Lemmas 1 and 2) |
| 3 | On every regular tessellation {f, m}, no two different shortest routes with the same ends are shorter than τ = L − L/m − L/f + 1. | new as far as found; proved | A (Theorem 2) |
| 4 | Every closed route has length at least min(m, f); for m = f the first tie is exactly at τ. | new as far as found; proved | A (Theorem 3) |
| 5 | The first tie is at τ on 42 hyperbolic covers and the larger stress-test covers read; every pair of shortest routes read is thin. | computed | A (checks 2, 3), stress test |

## Answer

No tie comes before τ on any regular tessellation (proved); a tie comes at τ when m = f (proved) and on every cover read (computed).

## Recommendation

**Continue**, selected #2 (the full-reach collapse) at the coordinator's instruction. The table is in the decision note.
