# Closure of the twists-in-three-dimensions epic

Status: Proved

Epic `TWIST-3D-20261025-001` closed on 2026-10-25. This is a ledger: one line per conclusion, with its novelty label and evidence. It
makes no new claim. The decision note is `research/TWIST-3D-20261025-001/twists_in_three_dimensions.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | On ordered triangulations, the counting laws with one bit per edge that satisfy the ordered 2–3 and 1–4 identities, for any of the 255 triangle rules read in vertex order and any tetrahedron rules (possibly orientation-dependent), are exactly the seven symmetric laws inside each rule: 354 laws, never using orientation or an asymmetric part of the rule. | `candidate-local-delta`; folklore risk low to medium | `TWIST-3D-20261025-001A-P001`, Theorem 1; exhaustive standard-library census |
| 2 | Their invariants are 1, 2, \|H¹(M; Z/2)\|/2 and \|H¹(M; Z/2)\|; each twisted Fibonacci knot carries one constant law and one parity law. | Classical invariants (Dijkgraaf–Witten for Z/2); the restriction is local | `…001A-P001`, Corollaries 2 and 3; 60 sampled triangulations |
| 3 | In Turaev–Viro form, positive weights for the Fibonacci and twisted Fibonacci triangle rules cannot have full support: 60 to 162 identities have terms on one side only. | `candidate-local-delta`; folklore risk medium | `TWIST-3D-20261025-001B-P001`, Theorem 1 |
| 4 | Every positive weighting for these rules is supported on constants, on the parity class, or (no-lone knots) on the parity class with one constant; on the parity class the weights are pure gauge, so every positive state sum is 1, 2, \|H¹\|/2 or \|H¹\|/2 + 1. | Local form of a classical fact; folklore risk medium | `…001B-P001`, Theorems 2 and 3, Corollary 4 |

## Challenged assumptions

The decision note records three workspace assumptions this epic challenges:
- that the twist might replace Fibonacci's negative weight (false);
- that order or orientation might give bits more three-dimensional information (false for one bit per edge);
- that seeing more three-dimensional topology requires signs (refined: for bits; larger labels already see more by counting).

## Recommendation

**Continue with a fresh epic: patterns of patterns in three dimensions.**
- **The question.** Which counting laws with composite labels (three or four states per edge) survive the ordered moves, and what do
  they see?
- **Why now.**
  - Bits are exhausted in three dimensions.
  - Finite-group counts see far more than mod-2 cohomology, and bits can only reach them as patterns.
- **The first discriminator.** A census of function-type laws over all magmas of orders 3 and 4 under the ordered identities.
  - Prediction to test: only groups survive.
- **Interest:** 2/3.
- **Alternatives:** a note on Boolean state sums in three dimensions (1/3); signed counts as a native resource (1/3); the global proof
  of the arm inequality (1/3).
- **Stop if** only group laws survive.
- **Execution:** deferred to the owner.
