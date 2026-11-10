# The second vector on the pair of solutions

Status: Partial (pre-registered 2026-11-10, before the proof attempt).

Ticket `CODIST-THREE-20261110-001A`, epic `CODIST-THREE-20261110-001` (sub-goal B73; the last epic on the collapse line for now).

## What is registered

At n = 2^m, h = n/2, q = 2n, for a ∈ GF(q)* with G the monic least-degree element of K = ker X_b, k = h − deg G ≥ 3, J = ⌈k/2⌉,
e = h − J − 1, G′ the second solution of `LEADING-FORM-20261110-001A` (W(G, G′) = c·Y^e), and M(λ) the reduction of the family Ẑ of
`CHAIN-ORDERS-20261110-001A` to K along a complement W′ containing k·G·Y^j for 2j < k − 1.

To be proved:
1. **The second vector.** For x = G·Y^i with 2i < k − 1, ψ_2(x) ≡ [Ŵ_x·G + W_x·G′]/(c·Y^e) modulo K, with W_x = W(G, ψ_2(x)) and Ŵ_x
   the polynomial in Y of degree below e congruent to W_x·G′/G mod k^e.

**Target, the co-distance-3 cancellation.** For all i, j < J with i + j ≤ k − 3, [λ⁴]M_ij = [λ⁵]M_ij = 0. Then the eigenvalue 1/a has no
Jordan block of size 4, exactly one of size 5 when k is odd and none when k is even, and the chain lemma holds in full for k ≤ 3.
Found before registration: the target at every a for sides 8 to 256 (`CHAIN-ORDERS-20261110-001`); at co-distance 3 the corrections to
the second vector add exactly 1 to a pure part of 1 (`LEADING-FORM-20261110-001`).

**Frozen stop rule.** If the target is not derived in this epic, the collapse line is parked: B73, B74 and B59 are recorded as parked,
with what is located and what failed, and the report picks between B74 and B59.

## Planned checks

- Every formula of the derivation, exactly at every a for sides 8 to 64, and at side 128.
- The target against the reduction computed directly, sides 8 to 128.
