# Closure of the return map digit by digit

Status: Proved

Ticket `RETURN-DIGITS-20261109-001Z`, 2026-11-09.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/RETURN-DIGITS-20261109-001/return_digits.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | At n = 2^m the return map of the cut line is one-dimensional: C_s = w^(n+1) T_h(w⁻²) on F[K]/(K^h), in the ball basis. | new as far as found; proved | A (Theorem 1) |
| 2 | The reversal in T_h is multiplication by the involution ε = W_(h−1) = 1 + Σ_j K^(h−h/2^j). | new as far as found; proved | A (Theorem 2) |
| 3 | Without the reversal the eigenvalues are c times the elements of GF(n) of trace 1. | new as far as found; proved | A (Theorem 3) |
| 4 | The digit recursion builds S_2h and ε_2h from S_h and ε_h in two-by-two blocks, from T_1 = [c]. | new as far as found; proved | A (Theorem 4) |
| 5 | The cone polynomial is the determinant of the linearized polynomial Σ_{i=0}^{m} μ^(2^i) C_i, C_m = I, the shape of the trace of GF(2n); the collapse holds exactly when its roots lie in GF(2n). | new as far as found; proved | A (Theorem 5) |
| 6 | 1 + Tr_(GF(2n)) divides the cone polynomial exactly once and leaves a square, at sides 4 to 128. | computed | A (check 6), stress test |

## Answer

The recursion in m is found and proved, and it turns the collapse into one statement about a linearized determinant; the collapse
itself is not proved.

## Recommendation

**Continue**, selected #1 (the roots of the linearized determinant), unless the coordinator chooses otherwise. The table is in the
decision note.
