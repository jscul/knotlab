# The reduction's vectors order by order

Status: Partial (pre-registered 2026-11-10, before the proof attempt).

Ticket `LEADING-FORM-20261110-001A`, epic `LEADING-FORM-20261110-001` (sub-goal B73).

## What is registered

At n = 2^m, h = n/2, q = 2n, for a ∈ GF(q)*: G is the monic least-degree element of ker X_b, k = h − deg G, J = ⌈k/2⌉, N = G(k)G(k + 1),
and Ẑ(λ) = Z_0 + λS + Σ_r a^(2^r)λ^(2^r)/(1 + λ^(2^r))·M_(k^(h−2^(r−1))) the family of `CHAIN-ORDERS-20261110-001A` (Theorem 4). M(λ) is its
reduction to K = ker X_b = G·F[Y]_(<J), with vectors Φ_x = x + Σ_r λ^r ψ_r(x) for x = G·Y^i.

**Method.** Write θ_r = ψ_r/G. In characteristic 2, Δ = 1 + τ is the trace of F(k)/F(Y), and the chain equations become
Tr θ_r ≡ τθ_(r−1) + (the family's high terms) mod k^h, with G·θ_r a polynomial of degree below h; the Wronskian W(G, F) = G·τF + F·τG
turns each into an equation in F[Y]. By the 2n + 1 rule the coefficient of M at λ^(2t−1) needs ψ_1, …, ψ_(t−1) only.

**Target.** For every co-distance t = k − i − j ≥ 1: [λ^(2t−1)] M_ij = [t is a power of two] and [λ^e] M_ij = 0 for e < 2t − 1. With
`CHAIN-ORDERS-20261110-001A`'s Theorem 3 this is the chain lemma at every order. Known before registration: t ≤ 2 among chains of
length at least 2 (Theorem 5 there), and the target computed at every a for sides 8 to 256 (`CHAIN-ORDERS-20261110-001`).

**Frozen stop rule.** The attempt ends at the first order r ≥ 2 for which no closed form of ψ_r is found, an explicit formula verified
exactly at every a for sides 8 to 64. The record then states how far the leading form is proved and the obstruction at order r.

## Planned checks

- Every closed form found, exactly at every a for sides 8 to 64, and at side 128.
- The leading coefficients it yields, against the reduction computed directly, sides 8 to 128.
