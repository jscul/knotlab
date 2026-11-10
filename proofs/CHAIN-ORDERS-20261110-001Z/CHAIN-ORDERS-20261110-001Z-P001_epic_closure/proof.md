# Closure of the chain lemma at every order

Status: Proved

Ticket `CHAIN-ORDERS-20261110-001Z`, 2026-11-10.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/CHAIN-ORDERS-20261110-001/chain_orders.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | Near each eigenvalue parameter a, the family is Z(w) = S + (w/a)(b + k^h L(w²/k)), L(x) = x + x² + x⁴ + ⋯. | new as far as found; proved | A (Theorem 1) |
| 2 | Z(w) is equivalent to diag(H(w), I), H(w) the moment (Hankel) matrix of ψ(w) = (Ω + k + 1)/(kΩ + (k + 1)²) in Y. | new as far as found; proved | A (Theorem 2) |
| 3 | The reduction to the eigenvectors G·Y^j has entries starting at u^(2k−1−2(i+j)), u = (w − a)/a, with coefficient 1 exactly when k − i − j is a power of two: its leading part is the Hankel matrix of u⁻¹Y^k L(u²/Y). Every eigenvalue, sides 8 to 256. | computed | A (checks 6 and 7) |
| 4 | [k − i − j a power of two] is invertible over GF(2) for every k (determinant 1, by halving k), so conclusion 3 is the whole chain lemma. | proved; ingredients classical | A (Theorem 3) |
| 5 | Every eigenvalue has exactly k mod 2 Jordan blocks of size 1, none of size 2, and one of size 3 exactly when k is even; for k ≤ 2 this is the whole chain lemma. | new as far as found; proved | A (Theorems 4 and 5) |
| 6 | The leading form from order 4 on, and the degree law, are not proved. | the gap | A |

## Answer

The chain lemma comes down to one explicit leading form, which holds at every eigenvalue to side 256 and whose leading matrix is
invertible by proof; the form is proved for its first three orders, the higher orders and the degree law are open.

## Recommendation

**Continue**, selected #1 (the leading form at every order, sub-goal B73), unless the coordinator chooses otherwise; #2 (halving the
index, B91) attacks the same statement. The table is in the decision note.
