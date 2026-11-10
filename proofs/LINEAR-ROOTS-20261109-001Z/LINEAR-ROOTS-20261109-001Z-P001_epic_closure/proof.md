# Closure of the roots of the linearized determinant

Status: Proved

Ticket `LINEAR-ROOTS-20261109-001Z`, 2026-11-09.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/LINEAR-ROOTS-20261109-001/linear_roots.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | The Kloosterman law: at sides 2^m the eigenvalue 1/a of the cone has K(a)(K(a) − 2)/8 copies, \|K(a)\|/4 eigenvectors and Jordan blocks 1, 5, 9, ... (K(a) > 0) or 3, 7, 11, ... (K(a) < 0), K(a) the Kloosterman sum of GF(2n) with x = 0 included; equivalently (t² − 1)/8 for the trace t of y² + xy = x³ + a. | new as far as found; computed, exact | A (checks 4, 5), stress test (sides 256, 512) |
| 2 | K(a) ≡ 0 mod 4 and the law's multiplicities add up to n(n − 1)/2; lower bounds at every a would prove the collapse and the law. | ingredients classical; proved | A (Theorem 1) |
| 3 | The eigenvectors at 1/a are the solutions of (k + 1)F(k + 1) ≡ Ω_b(k)F(k) mod k^h, b = √a. | new as far as found; proved | A (Theorem 2) |
| 4 | On GF(2n)*, Ω_b(y) = y^h Tr(b⁴/y) + b²/y^h. | new as far as found; proved | A (Theorem 3) |
| 5 | The curve of the shift K ↦ K + c is birational to the Kloosterman curve Y² + Y = x + c^(−4)/x. | new as far as found; proved | A (Proposition 4) |
| 6 | The law's period exponent equals the computed one at sides 4 to 128. | computed | A (check 6) |
| 7 | The eigenvalue 1 has multiplicity (t² − 1)/8 for y² + xy = x³ + 1 over GF(2n). | computed | A (check 7) |
| 8 | At sides 3 to 20 other than powers of two the eigenvalues are not in the field of (2n − 1)-th roots of unity. | computed | A (check 8) |

## Answer

The multiplicities of the cut-open torus's eigenvalues at powers of two are Kloosterman sums over GF(2n), computed exactly to side 128
(eigenvector counts to 512), and they add up to the whole degree; the lower bounds that would prove the collapse are not proved.

## Recommendation

**Continue**, selected #1 (prove the Kloosterman lower bounds, sub-goal B58), unless the coordinator chooses otherwise. The table is
in the decision note.
