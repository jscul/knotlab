# Closure of the cone behind the collapse at powers of two

Status: Proved

Ticket `CONE-COLLAPSE-20261109-001Z`, 2026-11-09.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/CONE-COLLAPSE-20261109-001/cone_collapse.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | The cut-open torus walk is two particles on one side: A = T_e ⊗ R + T_o ⊗ L = L ⊗ T_e + R ⊗ T_o on the contacts. | new as far as found; proved | A (Theorem 1) |
| 2 | At every side the quarter turn acts freely and commutes with A, so det(xI − A) = det(xI − A_cone)⁴ for the walk on its n(n − 1)/2 orbits. | new as far as found; proved | A (Theorem 2) |
| 3 | At n = 2^m the uncut walk's 2^j-th powers are the four translations by 2^j, so its resolvent is a product over binary digits. | known-with-delta (Lucas' theorem); proved | A (Theorem 3) |
| 4 | At n = 2^m, det(I − wA_cone) = det(I + C_s(w)), C_s the (n/2) × (n/2) return map of the cut line on J-symmetric vectors. | new as far as found; proved | A (Theorem 4) |
| 5 | The Smith form of I + C_s at 4, 8, 16 is the cone's Jordan data. | computed | A (check 4) |
| 6 | At 4 to 64 every eigenvalue λ of the cone is a (2n − 1)-th root of unity of multiplicity k(k + 1)/2 with Jordan blocks 2k − 1, 2k − 5, ...; the multiplicity is odd exactly when Tr(1/λ) = 1. | computed | A (checks 5, 6), stress test |
| 7 | The cone polynomials of n and 2n agree below degree 2n and differ there; the return map's characteristic polynomial has e_1 = w + w³ and val e_j = j(2j − 1). | computed | A (checks 7, 8), stress test |

## Answer

The collapse at every power of two is not proved. The spectrum is four copies of a cone's, which at powers of two is one (n/2) × (n/2)
determinant whose Smith form is the cone's Jordan data; the eigenvalues follow a rigid law to side 64 (and, for the collapse, the traces
and stability, at 128).

## Recommendation

**Continue**, selected #1 (the single particle behind the symmetric square), unless the coordinator chooses otherwise. The table is
in the decision note.
