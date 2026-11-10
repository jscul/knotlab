# One polynomial per eigenvalue

Status: Partial (pre-registered 2026-11-10, before the proof attempt).

Ticket `KLOOSTERMAN-BOUNDS-20261110-001A`, epic `KLOOSTERMAN-BOUNDS-20261110-001` (sub-goal B58).

## What is registered

Let n = 2^m, h = n/2 and q = 2n. For b ∈ GF(q)* let X_b be the operator F ↦ (k + 1)F(k + 1) + Ω_b(k)F(k) mod k^h on polynomials of
degree below h, Ω_b(k) = b + Σ_{i=2}^{m} b^(2^i) k^(h − 2^(i−2)). Its kernel is ker(I + C_s(b²)) (`LINEAR-ROOTS-20261109-001A`,
Theorem 2). Let K(b) be the Kloosterman sum of GF(q) with x = 0 included and k_b = (|K(b) − 1| − 1)/2, so that the cone's eigenvalue
1/b² has multiplicity k_b(k_b + 1)/2 by the Kloosterman law.

Found before registration, to be proved:
1. **Self-adjointness.** The shift F ↦ (k + 1)F(k + 1) mod k^h and every multiplication mod k^h are self-adjoint for
   ⟨F, G⟩ = Σ_{j<h} [k^j](FG). So X_b is self-adjoint, and its kernel is the radical of B_b(F, G) = ⟨X_bF, G⟩.
2. **The Wronskian.** Any two solutions satisfy F_1(k)F_2(k + 1) = F_1(k + 1)F_2(k).
3. **One polynomial.** Hence the solutions are exactly G·r(Y), Y = k² + k, r a polynomial, of degree below h, for one polynomial
   G = G_b; dim ker X_b = ⌈(h − deg G_b)/2⌉.

Computed exactly before registration: (3) holds with deg G_b = h − k_b for every b at sides 8 to 128. With (3) this is the geometric
multiplicity |K(b)|/4.

**Target.** deg G_b ≤ h − k_b for every b (the geometric lower bound), and lower bounds on the Jordan chains giving the algebraic
multiplicity K(b)(K(b) − 2)/8; with `LINEAR-ROOTS-20261109-001A`'s Theorem 1 these prove the collapse. If they stall, the point where
the argument stops is to be stated, with the kernel count computed precisely.

## Planned checks

- (1) as the matrix identity Γ X_b = X_bᵀ Γ, Γ the Gram matrix of ⟨ , ⟩, for every b at sides 4 to 64.
- (2) and (3), with deg G_b = h − k_b, for every b at sides 8 to 128.
- Stress run: (3) and deg G_b = h − k_b for every b at side 256.
