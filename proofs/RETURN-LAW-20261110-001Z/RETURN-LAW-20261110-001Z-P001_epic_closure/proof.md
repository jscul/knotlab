# Closure of the corner return law

Status: Proved

Ticket `RETURN-LAW-20261110-001Z`, 2026-11-10.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/RETURN-LAW-20261110-001/return_law.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | With at most one far wall, the corner's return series is the (0, 0) entry of (I − sD − s²f(P))^(−1) on the row path, s = w²; so the quadrant law and the half-strip law are each one identity on a path. | new as far as found; proved | A (Theorem 3) |
| 2 | In the box the corner's series is one entry of the inverse of a 2(n − 1) × 2(n − 1) block operator, explicit at a power of two (nilpotent row path, first-passage series from truncated Catalan polynomials). | new as far as found; proved | C (Theorem 7, Proposition 8) |
| 3 | The box law 1/(1 + L(w⁴)) holds at each power of two from 4 to 512. | new as far as found; computed, exact (a proof at each of those sides) | C (check 4), stress test |
| 4 | det(I + zP_n^∘) = 1 + L(z) at n = 2^m, so the box law says the corner returns, every four steps, as the loop end of a looped path of n sites, a quotient of its orbit; C(z) is the looped half-line's. | new as far as found, likely elementary; proved | C (Proposition 9), A (Proposition 5) |
| 5 | The reflection through the corner is a symmetry; mod 2 only excursions on the bottom side touching Y = 0 (or X = N) survive. | proved | A (Theorem 2) |
| 6 | The plain quadrant has an even number of returning walks of each positive length; the corner's column obeys a kernel equation. | proved | A (Lemma 4, the kernel equation) |
| 7 | One far wall is invisible at every even side 2 to 80 and seen first at 4n at every odd side to 79; the strip's four-periodic eigenvector exists exactly at even sides. | computed; proved (the eigenvector) | B, stress test |
| 8 | The quadrant's corner returns of length 4k are C_k², k ≤ 24; the box first differs from the quadrant at 8n (3 to 128); the four-corner formula (4 to 128). | computed | A, C, stress test |
| 9 | The same decomposition writes the count of B137 as a sum over the corner's row of the block inverse. | proved; checked | C (Corollary 10) |
| 10 | The quadrant law, the half-strip law and the box law are not proved for every side: each rests on an identity of conclusions 1 and 2. | the gap | A, B, C |

## Answer

The corner return law is proved at each power of two from 4 to 512 and reduced to one finite identity per side; the quadrant and
half-strip laws are each one identity on a path, computed and not proved.

## Recommendation

**Continue**, awaiting the coordinator's go-ahead: the corner's row of the block inverse (B140), which carries both the return law and
the count of B137. The table is in the decision note.
