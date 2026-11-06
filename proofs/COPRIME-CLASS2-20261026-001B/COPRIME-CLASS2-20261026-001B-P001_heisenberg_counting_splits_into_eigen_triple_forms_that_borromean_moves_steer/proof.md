# Heisenberg counting splits into eigen-triple forms that Borromean moves steer

Status: Proved

## Standard statement

**Notation.**
- **The field.** q = pᵏ, and r ≥ 2 divides q − 1, so p ∤ r and F_q contains the r-th roots of unity.
- **The groups.** H(F_q) is the Heisenberg group of triples (x, y, z) with (x, y, z)(u, v, t) = (x + u, y + v, z + t + xv). For
  α, β ∈ μ_r(F_q), let G = G_{α,β} = H(F_q) ⋊ C_r, where the generator h acts by (x, y, z) ↦ (αx, βy, αβz).
- **The manifold.** M is a closed oriented 3-manifold with π = π₁(M) and ψ: π → C_r = Z/r.
- **Eigenspaces.** For a character χ ∈ μ_r(F_q), V_χ = H¹(M; F_q twisted by χ^ψ). Set γ = (αβ)⁻¹.
- **The triple form.** T(a, b, c) = ⟨a ⌣ b ⌣ c, [M]⟩ for a ∈ V_α, b ∈ V_β, c ∈ V_γ. The product of the three characters is
  trivial.

**Theorem 1.**
- **(a) Count.** The homomorphisms π → G over ψ number |Z¹(π; F_{αβ})| · |B¹(π; F_α)| · |B¹(π; F_β)| · 𝒩_ψ, where
  𝒩_ψ = #{(a, b) ∈ V_α × V_β : a ⌣ b = 0 ∈ H²(M; F_{αβ})}. Summing over ψ gives |Hom(π, G)|.
- **(b) Duality.** a ⌣ b = 0 if and only if T(a, b, c) = 0 for every c ∈ V_γ. So 𝒩_ψ is the kernel count of one trilinear form
  on V_α × V_β × V_γ.
- **(c) Steering.** Let Γ be a Y-graph whose leaves ℓ₁, ℓ₂, ℓ₃ lie in ker ψ, and M′ the result of Y-surgery.
  - H₁(M′) ≅ H₁(M) canonically, ψ extends, and every V_χ is unchanged.
  - Every eigen-component of the triple product changes by the same law. For characters (χ₁, χ₂, χ₃) with χ₁χ₂χ₃ = 1:

    T′(a, b, c) − T(a, b, c) = ε Σ_σ sgn(σ) λ^{(χ₁)}_{σ1}(a) λ^{(χ₂)}_{σ2}(b) λ^{(χ₃)}_{σ3}(c).

  - Here λ^{(χ)}_i(a) = c_a(ℓ_i) evaluates a χ-twisted cocycle on the based leaf ℓ_i, and ε = ±1 is a fixed orientation
    convention.
- **(d) Realizability (prime fields).** Let q = p.
  - Leaf classes can be chosen with prescribed functionals on any finite set of eigenspaces and zero on all others.
  - A "pure" leaf, supported on one eigenspace, is the image of a loop under an eigenprojector, written as a product of
    conjugates by meridian powers.
  - So the changes realizable on the component (α, β, γ) are exactly the trilinear forms that are alternating in every pair of
    slots whose characters coincide. With pure leaves, only the components that are permutations of (α, β, γ) change.

**What it says.**
- The coprime twisting splits the triple cup product of the r-fold cover into eigen-components.
- Counting maps into G reads the single component (α, β, γ).
- Borromean moves steer that component freely, up to the symmetries that coinciding characters force.

## Nearest known result

- **`TRIPLE-PRODUCT-20261026-001A` and `TRIPLE-PRODUCT-20261026-001C`.** The case q = 4, r = 3, (α, β) = (ω², ω²), where the three
  characters coincide.
- **Massuyeau, AGT 3 (2003), Lemma 3.2.** The untwisted Y-surgery formula with Z_n coefficients, applied here in the r-fold cover.
- **Moussard, "Equivariant triple intersections", Ann. Fac. Sci. Toulouse (2017), Proposition 2.5 and Theorem 2.7.** This is the
  closest precursor.
  - For a Y-graph null in M ∖ K, lifted to the infinite cyclic cover, the equivariant triple intersection map changes by
    Σ_σ ε(σ) Π_j δ(t_j) b(β_j, [γ_{σ(j)}])(t_j).
  - The realized maps are Λ³A modulo relations.
  - Part (c) is the finite-cover, F_q analogue. Its leaves need only lie in ker ψ: a bundle of r strands links K r times, so it is not
    null in Moussard's sense.
- **Matei–Suciu (2005).** Twisted lifting obstructions.
- **Nosaka (arXiv:1808.08532).** Triple cup products of cyclic branched covers.
- **Novelty.**
  - The splitting and steering are routine extensions of the q = 4 case and of Moussard's rational formula. Folklore risk is medium
    to high.
  - The bookkeeping of coincidence patterns and of the other characters ψ_k is what the hardness proof uses.

## 1. The count (part a)

**The layers.**
- A = Z(H) = {(0, 0, z)}, and H/A = F_q² through (x, y).
- The section s(x, y) = (x, y, 0) has the bilinear cocycle β((x, y), (u, v)) = xv.
- h preserves {z = 0}, so G/A = (F_{q,α} ⊕ F_{q,β}) ⋊ C_r.

**Maps over ψ.**
- Maps π → G/A over ψ are the pairs of cocycles (c_x, c_y) ∈ Z¹(π; F_α) × Z¹(π; F_β).
- The lifting obstruction is [c_x ⌣ c_y] ∈ H²(π; F_{αβ}), the cup product for the coefficient product F_α ⊗ F_β → F_{αβ}.
- When the obstruction vanishes, the lifts form a torsor under Z¹(π; F_{αβ}).
- The class depends only on [c_x] and [c_y].

This is the argument of `TRIPLE-PRODUCT-20261026-001A` §1 with general characters.

## 2. Duality (part b)

- H²(π; L) injects into H²(M; L).
- Poincaré duality over F_q pairs H²(M; F_{αβ}) perfectly with H¹(M; F_{(αβ)⁻¹}) = V_γ, since the dual of a rank-one local
  system with monodromy ζ has monodromy ζ⁻¹.
- So a ⌣ b = 0 exactly when T(a, b, ·) = 0. For p odd, graded commutativity makes T change sign under a transposition of two slots
  with equal characters, and T(a, a, ·) = 0.

## 3. Steering (part c)

**Lifting to the cover.**
- ψ is trivial on Γ, so Γ lifts to r disjoint copies in the r-fold cyclic cover M̃ of ψ.
- The cover is trivial over the regular neighbourhood N = N(Γ), and over the handlebody N′ glued in by the surgery. The reason: ψ
  vanishes on ∂N, and H₁(∂N) → H₁(N) and H₁(∂N) → H₁(N′) are onto. So the surgery lifts, and ψ extends to M′.
- The same surjectivity gives both injectivity and existence of the twisted cocycle extensions across N′. That is part (a): V is
  unchanged.
- The hypothesis is essential. In the referee's control (`COPRIME-CLASS2-20261026-001A`), leaves with ψ = 2 changed dim V from 6
  to 4.
- Massuyeau's Lemma 3.2 with Z/p coefficients is applied r times, then extended F_q-linearly. For x, y, z ∈ H¹(M̃; F_q):

  u′ − u = ε Σ_g det(x(gL_i), y(gL_i), z(gL_i)).

**Restricting to eigencomponents.**
- Take x, y, z in eigenspaces with eigenvalues χ₁, χ₂, χ₃. Then the g-th term is (χ₁χ₂χ₃)(g) det(…) = det(…).
- The r terms add to r det(…) on the cover.
- On M, T(a, b, c) = r⁻¹ ⟨p*a ⌣ p*b ⌣ p*c, [M̃]⟩, because ⟨p*y, [M̃]⟩ = r⟨y, [M]⟩ and r is invertible in F_q. So the factor r
  cancels, and the change in T is ε det(…).
- The identification (p*a)(L̃_i) = c_a(ℓ_i) is as in `TRIPLE-PRODUCT-20261026-001C` §2.
  - Reading a leaf needs a path from the base point to the Y-graph's vertex, and then the edge.
  - Changing the first path multiplies all three leaf functionals of one Y-graph by χ₁(g), χ₂(g), χ₃(g). Their product is 1, so the
    determinant does not change. For r = 3 and q = 4 the factor was invisible,
  because 3 = 1 in F₄.

**What does not change.** H₁ and the V_χ are preserved by Matveev's theorem, lifted.

## 4. Realizability over prime fields (part d)

**Every functional is a leaf.**
- Let q = p. Then H₁(M̃; F_p) → ⊕_χ V_χ* is onto, by the perfect pairing of H¹ and H₁ with field coefficients, and every class
  in H₁(M̃; F_p) comes from a loop of ker ψ.
- The eigenprojector P_ζ = r⁻¹ Σ_j ζ^{−j} t^j, where t is a meridian conjugation, has coefficients in F_p. Applied to a loop class,
  it is realized as the product of the conjugates t^j ℓ t^{−j}, raised to the powers (r⁻¹ζ^{−j} mod p). That is one loop, whose
  functional is supported on V_ζ.

**Pure leaves.**
- Give leaf i support on one eigenspace. The sum over σ in (c) then has nonzero terms only for assignments that send each leaf to a
  slot of its own character.
- So:
  - with characters pairwise distinct, the change is a rank-one tensor λ ⊗ μ ⊗ ν, and sums of these give every trilinear form;
  - two slots with the same character give λ ∧ λ′ in those slots;
  - three equal characters give λ₁ ∧ λ₂ ∧ λ₃.
- Only components whose character triple is a permutation of the leaves' characters change.

**Interpretation, not proved.** That the realizable forms are exactly T₀ plus the forms of the symmetry type above is an
interpretation. Only the inclusion ⊇ is proved here. So is the reading of the non-alternating part as a twisted Bockstein governed by
the linking pairing, which these moves preserve.

**The convention for leaves in braids.**
- The Wirtinger relator used is x_out = x_over^{−s} x_in x_over^{s} for a crossing of sign s.
- With it, the right-to-left product of adjacent arcs is preserved across crossings: x_over x_out = x_in x_over for s = 1. So the
  leaf around a bundle is x_{q+r−1} ⋯ x_q.
- With the opposite relator the reversed product applies. The independent replay in `COPRIME-CLASS2-20261026-001A` confirms this,
  120 of 120 configurations each way.

## Check

`check.py` uses only the standard library and `cp_lib.py` in this directory; it runs in about 40 s.

1. **The groups.** For five (p, r, α, β): |G| = p³r, conjugation by h is the stated automorphism, associativity is sampled, and
   inverses are correct.
2. **The count against brute-force enumeration.** Twelve cases, including the characters with r = 6, and r·p-surgeries with
   p-torsion in H₁. Examples: 687, 1876, 4950, 7302, 3500, 4500.
3. **The steering law in all four coincidence patterns.**
   - The patterns: α = β = γ (p = 7, r = 3); α = β ≠ γ and γ = α ≠ β (p = 5, r = 4); α, β, γ distinct (p = 7, r = 6).
   - Single insertions and pairs of Borromean insertions agree with the prediction for every a: the kernel of b ↦ B(a, b) against
     that of b ↦ T_pred(a, b, ·).
   - Five character pairs on one knot with three insertions also agree, so every eigen-component changes by the same law.
   - Control: reversing the leaf products mismatches.

## Scope

- **Where it holds.** Parts (a)–(c) hold for every q with r | q − 1. Part (d) is proved for prime fields; for q = 4, r = 3 see
  `TRIPLE-PRODUCT-20261026-001C`.
- **Cited:** Massuyeau's Lemma 3.2, Matveev's theorem and Poincaré duality with local coefficients.
- **Checked** on knots that are braid closures, with Borromean insertions on bundles of r adjacent strands.
- No complexity claim; no P versus NP claim.
