# Closure of the Kloosterman lower bounds

Status: Proved

Ticket `KLOOSTERMAN-BOUNDS-20261110-001Z`, 2026-11-10.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/KLOOSTERMAN-BOUNDS-20261110-001/kloosterman_bounds.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | The operator holding the eigenvectors at each eigenvalue is self-adjoint for ⟨F, G⟩ = Σ_{j<h}[k^j](FG). | new as far as found; proved | A (Theorem 1) |
| 2 | Any two eigenvectors at one eigenvalue have a ratio unchanged by the shift k ↦ k + 1. | new as far as found; proved | A (Theorem 2) |
| 3 | The eigenvectors are G·r(Y), Y = k² + k, for one least-degree polynomial G; their number is ⌈(h − deg G)/2⌉. | new as far as found; proved | A (Theorem 3) |
| 4 | The same number is h/2 minus the rank of one explicit Toeplitz matrix. | new as far as found; proved | A (Theorem 4) |
| 5 | deg G = h − k at every eigenvalue, k(k + 1)/2 its multiplicity, sides 8 to 512: the Kloosterman count. | computed | A (check 5), stress test |
| 6 | The Toeplitz rank is the linear complexity of the Padé series, h/2 − \|K\|/4, sides 8 to 64. | computed | A (check 6) |
| 7 | The eigenvector lower bound is exactly deg G ≤ h − k; not proved, nor the Jordan chains. | the gap | A |

## Answer

The eigenvector count at each eigenvalue is reduced, with proofs, to the degree of one polynomial, and that degree matches the Kloosterman
law at every eigenvalue to side 512; the degree bound and the Jordan chains, and with them the collapse, are not proved.

## Recommendation

**Continue**, selected #1 (the Jordan chains from one polynomial, sub-goal B73), unless the coordinator chooses otherwise. The table is
in the decision note.
