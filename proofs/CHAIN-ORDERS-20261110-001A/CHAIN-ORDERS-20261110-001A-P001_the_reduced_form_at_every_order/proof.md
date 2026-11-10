# The reduced form at every order

Status: Partial (pre-registered 2026-11-10, before the proof attempt).

Ticket `CHAIN-ORDERS-20261110-001A`, epic `CHAIN-ORDERS-20261110-001` (sub-goal B73 continued).

## What is registered

At n = 2^m, h = n/2, q = 2n, for a ∈ GF(q)* with b = √a: Z(w) = S + M_(Ω(w)) is the family of `JORDAN-CHAINS-20261110-001A` (Z(a) = X_b),
G the monic least-degree element of ker X_b, k = h − deg G, J = ⌈k/2⌉, so that ker X_b = G·F[Y]_(<J), Y = k² + k. Write u = (w − a)/a and
L(x) = x + x² + x⁴ + ⋯.

To be proved:
1. **The sparse Taylor form.** Ω(a + δ) ≡ (1 + δ/a)·(Ω_a + Σ_(r=1)^(m−1) δ^(2^r) k^(h − 2^(r−1))) mod δ^n, that is, the family's perturbation
   is k^h·L(δ²/k).
2. **The Hankel reduction.** Near a, Z(w) is equivalent (as an analytic matrix family) to diag(H(w), I), H(w) the (h/2) × (h/2) Hankel
   matrix of ψ_1(w), …, ψ_(h−1)(w), where ψ(w) = (Ω(w) + k + 1)/(kΩ(w) + (k + 1)²) mod k^h is written as a series in Y. So the Jordan
   blocks at 1/a are the partial multiplicities of one moment matrix.
3. **The leading matrix.** Γ^(k) = [k − i − j is a power of two (1, 2, 4, …)]_(0 ≤ i, j < J) is invertible over GF(2) for every k.

**Target, the leading form.** The symmetric Lyapunov–Schmidt reduction M(w) of Z to ker X_b (basis G·Y^j; complement spanned by the
monomials k^d off the kernel's top degrees deg G + 2j) satisfies M_ij = u^(2k − 1 − 2(i + j))·(Γ^(k)_ij + O(u)): its leading part is
u⁻¹Y^k L(u²/Y), the same linearized polynomial as the family's perturbation. With 3 this gives the chain lemma at every order: G·Y^j heads a
Jordan chain of exactly 2k − 1 − 4j and these are the Jordan blocks. The lower half alone (the valuations) gives the multiplicity
k(k + 1)/2 as a lower bound, which with the degree bound deg G ≤ h − k_a of sub-goal B74 would prove the collapse (the Kloosterman multiplicities
fill the cone's degree n(n − 1)/2, `LINEAR-ROOTS-20261109-001A`, Theorem 1).

Found by exact computation before registration: 1 at every a for sides 8 to 32; the partial multiplicities of H at every a for sides 8 to
32; 3 for k < 400; the target at every a for sides 8 to 64. Also found: the second-order term of the reduction vanishes on the chains of
length at least 2 (sides 8 to 64).

## Planned checks

- 1 at sides 4 to 128; 2 (the partial multiplicities of H against those of Z) at sides 8 to 64, side 64 after registration; 3 for k < 1000.
- The target at side 128 for a sample of a including the eigenvalue 1 (k = 15), after registration, as a registered long-running check.
