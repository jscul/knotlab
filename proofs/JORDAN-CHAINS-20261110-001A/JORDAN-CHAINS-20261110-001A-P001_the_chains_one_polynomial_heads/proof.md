# The chains that one polynomial heads

Status: Partial (pre-registered 2026-11-10, before the proof attempt).

Ticket `JORDAN-CHAINS-20261110-001A`, epic `JORDAN-CHAINS-20261110-001` (sub-goal B73).

## What is registered

At n = 2^m, h = n/2, q = 2n, for a ∈ GF(q)* with b = √a: X_b is the operator of `KLOOSTERMAN-BOUNDS-20261110-001A` whose kernel holds the cone's
eigenvectors at 1/a, G_b its least-degree kernel element and k = h − deg G_b (so ker X_b = G_b·F[Y]_(<⌈k/2⌉), Y = k² + k).

To be proved:
1. **The family.** Z(w) = S + w^(1−n)·M_(ε(w⁻²k)) on polynomials of degree below h satisfies det Z(w) = w^(h(1−n)) det(I + C_s(w)) and Z(a) = X_b. Its Taylor
   coefficients at w = a of order i ≥ 1 are multiplications, by Ω_i(k) = Σ_e binom(1 − n − 2e, i) a^(1−n−2e−i) k^e, e over 0 and h − h/2^j.
2. **The reduction.** Z(w) is self-adjoint for ⟨ , ⟩ at every w, so the partial multiplicities of Z at a (the eigenvalue's Jordan blocks) are those of the
   Lyapunov–Schmidt reduction of Z to ker X_b, a ⌈k/2⌉ × ⌈k/2⌉ symmetric matrix function of w − a.

**Target, the chain lemma.** G_b·Y^j heads a Jordan chain of Z at a of length exactly 2k − 1 − 4j, for j < ⌈k/2⌉, and these lengths are the partial
multiplicities. Then the eigenvalue 1/a has algebraic multiplicity k(k + 1)/2 with k read off deg G_b alone; with the degree law (computed in
`KLOOSTERMAN-BOUNDS-20261110-001`) that is K(a)(K(a) − 2)/8. Found by exact computation at every a for sides 8 to 32 before registration.

## Planned checks

- (1) at sides 4 to 32 for every a (the determinant against the cone polynomials of `CONE-COLLAPSE-20261109-001A`, the Taylor coefficients exactly).
- The chain lemma at every a for side 64, after registration.
- Stress run: the chain lemma at side 128 for a sample of a including the eigenvalue 1 (k = 15).
