# One polynomial per eigenvalue

Status: Proved by hand (Theorems 1 to 4, with finite checks 1 to 4 of `check.py`); checks 5 and 6 and the stress run are exact
computations. The target registered with this ticket, deg G_b ≤ h − k_b and the Jordan chains, is not proved; the point where the
argument stops is stated at the end.

Ticket `KLOOSTERMAN-BOUNDS-20261110-001A`, epic `KLOOSTERMAN-BOUNDS-20261110-001` (sub-goal B58), 2026-11-10 (pre-registered in commit
78a919ba5).

## Standard statement

- **Setting.** n = 2^m, h = n/2, q = 2n, over a field F ⊇ GF(q); V = F[k]_(<h), the polynomials of degree below h; τ the substitution
  k ↦ k + 1 (an involution, characteristic 2); Y = k² + k, which generates the τ-invariant polynomials. For b ∈ GF(q)*,
  Ω_b(k) = b + Σ_{i=2}^{m} b^(2^i) k^(h − 2^(i−2)), and X_b : V → V, X_bF = (k + 1)F(k + 1) + Ω_b(k)F(k) mod k^h. By
  `LINEAR-ROOTS-20261109-001A`, Theorem 2, ker X_b ≅ ker(I + C_s(b²)), the eigenvectors of the cut-open torus's cone at the eigenvalue
  1/b², and its dimension is |K(b)|/4 by the computed Kloosterman law (K the Kloosterman sum of GF(q) with x = 0 included, K(b²) = K(b)).
  Write k_b = (|K(b) − 1| − 1)/2, so that the eigenvalue 1/b² has algebraic multiplicity k_b(k_b + 1)/2.
- **The pairing.** ⟨F, G⟩ = Σ_{j<h} [k^j](FG), the sum of the coefficients of FG below degree h. Its Gram matrix [i + j ≤ h − 1] has
  ones on the anti-diagonal and zeros below it, so the pairing is nondegenerate.

**Theorem 1 (self-adjointness).** The shift F ↦ (k + 1)F(k + 1) mod k^h and every multiplication F ↦ ΩF mod k^h are self-adjoint for
⟨ , ⟩. Hence X_b is self-adjoint, and ker X_b is the radical of the symmetric form B_b(F, G) = ⟨X_bF, G⟩.

**Theorem 2 (the Wronskian).** If F_1, F_2 ∈ ker X_b, then F_1(k)F_2(k + 1) = F_1(k + 1)F_2(k).

**Theorem 3 (one polynomial per eigenvalue).** If ker X_b ≠ 0, let G_b be a nonzero element of ker X_b of least degree. Then

ker X_b = {G_b·r(Y) : r a polynomial, deg G_b + 2 deg r < h},  dim ker X_b = ⌈(h − deg G_b)/2⌉.

All solutions share the shift multiplier F(k + 1)/F(k) = G_b(k + 1)/G_b(k).

**Theorem 4 (the Padé form).** Let U be the element of B = F[k]/(k^h(k + 1)^h) with U ≡ Ω_b(k)/(k + 1) mod k^h and
U ≡ k/Ω_b(k + 1) mod (k + 1)^h, written U = U_0(Y) + kU_1(Y), and ψ_b = (1 + U_0)/(1 + YU_1) mod Y^h. Then F = A(Y) + kC(Y) lies in
ker X_b exactly when deg A, deg C < h/2 and C ≡ ψ_b·A mod Y^h. So dim ker X_b = h/2 − rank T_b, T_b the (h/2) × (h/2) Toeplitz matrix
(ψ_b)_(h/2 + j − i), 0 ≤ i, j < h/2.

**Computed.**
- **The degree law** (check 5, stress run): deg G_b = h − k_b for every b ∈ GF(q)* at sides 8 to 128, and at 256 in the stress run;
  the valuations of the kernel are 0, 1, ..., dim − 1. With Theorem 3 this is the geometric multiplicity ⌈k_b/2⌉ = |K(b)|/4.
- **The Padé rank** (check 6): rank T_b equals the linear complexity of the sequence ψ_1, ..., ψ_(h−1), and both are h/2 − |K(b)|/4,
  every b at sides 8 to 64.

**Where the argument stops.** By Theorems 3 and 4, the geometric lower bound dim ker X_b ≥ |K(b)|/4 at every b is exactly the degree
bound deg G_b ≤ h − k_b, equivalently rank T_b ≤ h/2 − |K(b)|/4: one explicit polynomial, or one explicit Toeplitz matrix, per
eigenvalue. No argument here ties that degree to the Kloosterman sum. G_b and its norm G_b(k)G_b(k + 1) (a polynomial in Y) have no
roots or factors over GF(q) that follow the trace classes Tr(b/Y) of the Kloosterman curve, and the recurrence of ψ_b does not either
(computed at sides 8 to 64). The algebraic half, Jordan chains of lengths 2k_b − 1, 2k_b − 5, ..., was not reached.

## Nearest known result

- **Ingredients.** Hilbert's Theorem 90 for the quadratic extension F(k)/F(Y) (the shift multiplier is a norm-one function); Padé
  approximation and the rank of Toeplitz and Hankel matrices (Kronecker, Iohvidov); Kloosterman sums over GF(2^r) (Lachaud and
  Wolfmann).
- **Classification.** New as far as found for this walk (a bounded search on 2026-11-09 found no link between Kloosterman sums and the
  spectrum of a walk or matrix over GF(2)); the ingredients are classical.

## Proof of Theorem 1

Since (k + 1)^(h−1) = Σ_{j<h} k^j (h a power of two), ⟨F, G⟩ = [k^(h−1)](FG(k + 1)^(h−1)). For a multiplication, ⟨ΩF mod k^h, G⟩ =
⟨ΩF, G⟩ (terms of degree ≥ h do not reach the coefficients below h), which is symmetric in F and G.

For the shift, ⟨(k + 1)F(k + 1), G⟩ = [k^(h−1)]((k + 1)^h F(k + 1)G(k)) = [k^(h−1)](F(k + 1)G(k)), as (k + 1)^h = k^h + 1. So
⟨SF, G⟩ + ⟨F, SG⟩ = [k^(h−1)](Q + τQ) with Q = F·τG of degree at most 2h − 2. Q + τQ is τ-invariant, a polynomial in Y of degree at
most h − 1, and its coefficient of Y^(h−1) is [k^(2h−2)](Q + τQ) = 0 (τ keeps the leading coefficient). Finally [k^(h−1)]Y^j =
binom(j, h − 1 − j) mod 2 vanishes for j ≤ h − 2: it needs h − 1 − j ≤ j and the bits of l = h − 1 − j inside those of j (Lucas), but
j + l = h − 1 = 2^(m−1) − 1 forces j and l to have disjoint bits (a sum equal to 2^r − 1 has no carries), so l = 0, j = h − 1. Hence
[k^(h−1)](Q + τQ) = 0 and S is self-adjoint. ∎

## Proof of Theorem 2

From X_bF_i = 0, (k + 1)τF_i ≡ Ω_bF_i mod k^h. Then W = F_1τF_2 + F_2τF_1 satisfies (k + 1)W ≡ Ω_b(F_1F_2 + F_2F_1) = 0 mod k^h, so
W ≡ 0 mod k^h. W is τ-invariant, so also W ≡ 0 mod (k + 1)^h. Hence k^h(k + 1)^h divides W, of degree 2h, while deg W ≤ 2h − 2:
W = 0. ∎

## Proof of Theorem 3

Fix F_0 ≠ 0 in ker X_b and let Λ = {F ∈ F[k] : F·τF_0 = τF·F_0}. It is a module over F[Y] (τ fixes Y), torsion-free, inside the
free F[Y]-module F[k] = F[Y] ⊕ kF[Y], and of rank one (F/F_0 is τ-invariant, so Λ ⊂ F_0·F(Y)). A finitely generated torsion-free
module of rank one over the principal ideal domain F[Y] is free: Λ = G·F[Y] for some G. By Theorem 2, ker X_b ⊂ Λ.

For F = G·r with r ∈ F[Y], (k + 1)τF + Ω_bF = r·E with E = (k + 1)τG + Ω_bG. Let e be the order of E at k = 0 (e = ∞ if E = 0). Since
r is a polynomial in Y = k(k + 1), its order at k = 0 is its order v in Y, and F ∈ ker X_b exactly when deg F < h and v + e ≥ h. So
ker X_b = {G·Y^(v_0)·r′ : deg < h}, v_0 = max(0, h − e), the polynomials of degree below h in the free module G_b·F[Y] with
G_b = G·Y^(v_0), whose least-degree element is G_b. The elements G_b·Y^j with deg G_b + 2j < h form a basis. ∎

## Proof of Theorem 4

Write F = A(Y) + kC(Y). Every polynomial of degree below 2h has exactly one such form with deg A, deg C < h, and deg F < h exactly when
deg A, deg C < h/2 (degrees 2 deg A and 2 deg C + 1). By `LINEAR-ROOTS-20261109-001A` (its proof of Theorem 2, the cone's equation in
the normalized form), X_bF = 0 is τF ≡ U·F in B: modulo k^h it is (k + 1)τF ≡ Ω_bF, and modulo (k + 1)^h it is τ of that. In the basis
1, k of B over R = F[Y]/(Y^h), with τ(A + kC) = (A + C) + kC and k² = k + Y, this is the pair (1 + U_0)A + (1 + YU_1)C = 0 and
U_1A + (1 + U_0 + U_1)C = 0 in R. Its determinant 1 + U_0² + U_0U_1 + YU_1² = 1 + U·τU is 0, since U·τU ≡ 1 modulo k^h and (k + 1)^h by
construction. As 1 + YU_1 is a unit of R (constant term 1), the first equation gives C = ψ_bA and the second then holds (it is the
first times the unit (1 + U_0 + U_1)/(1 + YU_1), up to the vanishing determinant). So ker X_b ≅ {A ∈ F[Y]_(<h/2) : [Y^j](ψ_bA) = 0 for
h/2 ≤ j < h}, the kernel of T_b. ∎

## Checks

`check.py` (one process, a few seconds; `--write` rewrites `result.json`):
- **0.** The dependencies (`LINEAR-ROOTS-20261109-001A`'s manifest and library) bound by hash.
- **1.** Theorem 1 as Γ X_b = X_bᵀ Γ, every b, sides 4 to 64, and for the shift alone.
- **2.** Theorem 2 for every pair of kernel basis vectors, sides 8 to 64.
- **3.** Theorem 3: top degrees deg G_b + 2j, every G_b Y^j in the kernel, the dimension, every b, sides 8 to 128.
- **4.** Theorem 4, every b, sides 8 to 64.
- **5.** The degree law and the valuations, every b, sides 8 to 128.
- **6.** The Padé rank and the linear complexity, every b, sides 8 to 64.
- **7.** The stress run (`research/KLOOSTERMAN-BOUNDS-20261110-001/stress_test.json`): checks 3 and 5 at side 256.
