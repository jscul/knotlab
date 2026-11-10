# The second vector on the pair of solutions

Status: Proved by hand (Theorems 1 to 3, with finite checks 1 to 3 of `check.py`); the identity the target reduces to, and a negative
reading, are exact computations (checks 3 and 4). The registered target, the co-distance-3 cancellation, is not derived: by the frozen
stop rule the collapse line is parked, and where the argument stops is stated at the end.

Ticket `CODIST-THREE-20261110-001A`, epic `CODIST-THREE-20261110-001` (sub-goal B73), 2026-11-10 (pre-registered in commit 56e1ba31d).

## Standard statement

- **Setting.** As `LEADING-FORM-20261110-001A`: n = 2^m, h = n/2, a ∈ GF(2n)*, G = Q(Y) + k·P(Y) the monic least polynomial,
  k = h − deg G, J = ⌈k/2⌉, N = G(k)G(k + 1) ∈ F[Y], L(Y) = Y + Y² + ⋯ + Y^(h/2), W the Wronskian, Ẑ the family of
  `CHAIN-ORDERS-20261110-001A`, M its reduction to K = G·F[Y]_(<J) along a complement W′ containing k·G·Y^j for 2j < k − 1, and
  K_1 = span{G·Y^i : 2i < k − 1}.
- **Coefficient extraction.** For P ∈ F[Y], [k^(h−1)]P = [Y^(h−1)]P and [k^(h−2)]P = Σ_(t≥0) [Y^(h−1−2^t)]P
  (`JORDAN-CHAINS-20261110-001A`, proof of Theorem 3: [k^(h−2)]Y^l is 1 exactly at l = h − 1 − 2^t).

**Theorem 1 (the gap).** For k ≥ 2, [Y^d](N·L(Y)) = 0 for h − k + 1 ≤ d ≤ h − 2, and [Y^(h−1)](N·L(Y)) = a²G(0)². This is the
second-order solvability of the chains in its plainest form.

**Theorem 2 (the order-4 coefficient).** For x = G·Y^i, y = G·Y^j in K_1 with i + j ≤ k − 3, and any second chain vector φ_2 of x,

[λ⁴]M(x, y) = Q1 + Q2 + Q3 + Q4 + Q5, with Q1 = [k^(h−2)](Y^j·W_x), Q2 = [Y^(h−2−j)]W_x, Q3 = [k^(h−2)](Y^j·I_x),
Q4 = a²φ_2(0)y(0), Q5 = B_4(x, y),

where W_x = W(G, φ_2), I_x = G·τφ_2 + k·W_x ∈ F[Y], and B_4(x, y) = a²x(0)y(0) + a⁴([k⁰] + [k¹])(xy). The sum does not depend on the
choice of φ_2, and Q1 = Q2 = 0.

**Theorem 3 (a canonical second vector).** Let Q″, P″ be the Bezout cofactors, P·Q″ + Q·P″ = 1 (gcd(P, Q) = 1 when G(0) ≠ 0). Then
ψ̂_x = R_x + k·(W_x + P·R_x)/Q, R_x = (W_x·Q″) mod Q, with W_x as in `LEADING-FORM-20261110-001A`'s Theorem 3, is a second chain
vector of x whenever its degree is below h (at every eigenvalue for sides 16 to 64, check 3), and every second chain vector is
ψ̂_x + K.

**Computed.** With ψ̂_x, Q3 + Q4 + Q5 = 0 at every pair with i + j ≤ k − 3 in K_1, sides 16 to 64 (check 3), so the order-4
coefficient vanishes there. A first continued-fraction reading, the top coefficients of φ = ξN/(1 + ξ(k + 1 + Λ″_0)) with ξ the
multiplier's perturbation and Λ″_0 the invariant part of G·τ(Q″ + kP″), does not show the leading form (check 4).

**Where the argument stops.** The order-4 cancellation at co-distance at least 3 is reduced to Q3 + Q4 + Q5 = 0 for ψ̂_x, an identity
about the top coefficients of I(ψ̂_x) = W_x + (Q + P)R_x + Y·P·(W_x + P·R_x)/Q, a quotient by Q whose high coefficients were not found
in closed form. The order-5 coefficient ⟨Sψ_2(x), ψ_2(y)⟩ was not reduced. By the frozen rule the collapse line is parked.

## Nearest known result

- **Ingredients.** Bezout cofactors and the Euclidean algorithm over F[Y]; Wronskians over F(k)/F(Y); sums over powers of two in
  characteristic 2 (a double sum Σ_(t,t′) f(2^t + 2^t′) collapses to Σ_t f(2^(t+1))).
- **Classification.** New as far as found for this walk (bounded search of 2026-11-09); the ingredients are classical.

## Proof of Theorem 1

By `LEADING-FORM-20261110-001A`, Theorem 3, for every i with 2i < k − 1 the polynomial N·Y^i·(1 + L) + a²G(0)²[i = 0]Y^(h−1) reduced
mod Y^h has no terms in degrees h − J to h − 1. As deg N = h − k and i < k − J, N·Y^i has no terms there either, so N·Y^i·L has none
except, for i = 0, the term a²G(0)²Y^(h−1). Shifting by i, [Y^d](N·L) = 0 for h − J − i ≤ d ≤ h − 2 − i, and [Y^(h−1)](N·L) = a²G(0)².
The largest i in K_1 is J − 1 for k even and J − 2 for k odd; in both cases h − J − i reaches h − k + 1. ∎

## Proof of Theorem 2

As in `CHAIN-ORDERS-20261110-001A`'s proof of Theorem 5, one order further: [λ⁴]M(x, y) = ⟨Sψ_3(x), y⟩ + a²ψ_2(x)(0)y(0) + B_4(x, y),
and ⟨Sψ_3(x), y⟩ = ⟨ψ_3(x), Z_0(ky)⟩ = ⟨Z_0ψ_3(x), ky⟩ = ⟨Sψ_2(x), ky⟩ by the order-3 equation tested on ky ∈ W′ (B_3 = 0 and
(kx)(0) = 0). Every x ∈ K_1 heads a chain of length at least 3 (all its pairs have i + j ≤ k − 2, where the second-order form vanishes),
so ψ_2(x) = φ_2 + κ with φ_2 an exact second vector and κ ∈ K; replacing φ_2 by φ_2 + G·r changes the sum by the second-order form
M_2(G·r, y), which vanishes as all pairs with y ∈ K_1 have index sum at most k − 2.

For the split, ⟨Sφ_2, ky⟩ = [k^(h−1)](τφ_2·k·y) = [k^(h−1)](k·Y^j·G·τφ_2), and G·τφ_2 = I_x + k·W_x with I_x, W_x ∈ F[Y] (W_x is its
trace). With k² = k + Y this is [k^(h−2)](Y^jI_x) + [Y^(h−2−j)]W_x + [k^(h−2)](Y^jW_x).

Q2: [Y^(h−2−j)]W_x = [Y^(h−2−s)](N(1 + L)), s = i + j, as the correction term sits at Y^(h−1) and the reduction mod Y^h does not reach
degree h − 2 − j. N has no term there (h − 2 − s > h − k), and N·L has none by Theorem 1, as h − k + 1 ≤ h − 2 − s ≤ h − 2.

Q1: [k^(h−2)](Y^jW_x) = Σ_t [Y^(h−1−2^t−s)](N(1 + L)) (the correction and the reduction mod Y^h do not reach these degrees)
= Σ_t N_(h−1−2^t−s) + Σ_(t,t′) N_(h−1−2^t−2^t′−s), t, t′ from 0 to m − 2. In the double sum the pairs t ≠ t′ cancel in characteristic 2,
leaving Σ_t N_(h−1−2^(t+1)−s); with the single sum this leaves N_(h−2−s) + N_(−1−s) = N_(h−2−s), zero as h − 2 − s > h − k. ∎

## Proof of Theorem 3

W(G, A + kC) = P·A + Q·C, so W(G, ψ̂_x) = P·R_x + (W_x + P·R_x) = W_x. The quotient is exact: P·Q″ ≡ 1 mod Q, so
P·R_x ≡ W_x mod Q. With G(0) ≠ 0, G is a unit mod k^h, and `LEADING-FORM-20261110-001A`'s Theorems 1 and 2 give
Z_0ψ̂_x ≡ (k + 1)W(G, ψ̂_x)/G = (k + 1)W_x/G ≡ Z_0φ_2, so ψ̂_x − φ_2 ∈ K for any second vector φ_2 of degree below h. A common divisor of
P and Q would make G/d a polynomial with W(G, G/d) = 0, against G·F[Y] being the module of such polynomials. ∎

## Checks

`check.py` (one process, about ten seconds; `--write` rewrites `result.json`):
- **0.** The dependencies (`LEADING-FORM-20261110-001A`'s manifest and library) bound by hash.
- **1.** Theorem 1, every a with k ≥ 2, sides 8 to 128.
- **2.** Theorem 2: the split equals the coefficient and Q1 = Q2 = 0, every pair, sides 16 to 64.
- **3.** Theorem 3 (ψ̂_x of degree below h and a second chain vector) and the computed identity Q3 + Q4 + Q5 = 0, sides 16 to 64.
- **4.** The negative continued-fraction reading, sides 16 to 64.
