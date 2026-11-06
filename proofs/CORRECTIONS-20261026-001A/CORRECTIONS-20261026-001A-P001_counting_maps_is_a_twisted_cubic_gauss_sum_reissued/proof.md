# Counting maps is a twisted cubic Gauss sum

Status: Proved

**Reissue.**
- This is the reissue of `TRIPLE-PRODUCT-20261026-001A-P001`, made in `CORRECTIONS-20261026-001A` on 2026-10-26 after the independent
  review `COPRIME-CLASS2-20261026-001A`. It supersedes the closed version, which is left unchanged.
- **What changed:**
  - the sentence about Samperton–Weiß's twisted question (review item R2);
  - the shared library's `insert_at`, which now handles insertions at a common level (item m9; no check used that case).
- The mathematics and the checks are unchanged.

## Standard statement

**Notation.**
- F₄ = F₂[ω]/(ω² + ω + 1), with trace tr(x) = x + x² ∈ F₂.
- N = UT₃(F₄) is the set of triples (x, y, z) with (x, y, z)(u, v, w) = (x + u, y + v, z + w + x·v).
- G = N ⋊ ⟨h⟩, where h acts by α(x, y, z) = (ω²x, ω²y, ωz). Then |G| = 192, Z(G) = 1, and the Fitting height is 2.
- M is a closed orientable 3-manifold with π = π₁(M).
- For a surjection ψ: π → C₃ = ⟨h⟩, F₄_{ω^k} denotes F₄ with g acting by ω^{kψ(g)}.
- V_ψ = H¹(M; F₄_{ω²}).
- T_ψ(a, b, c) = ⟨a ⌣ b ⌣ c, [M]⟩ ∈ F₄. The coefficients are multiplied; the product of three copies of F₄_{ω²} is the trivial
  module because ω⁶ = 1.

**Theorem 1.**
- **(a) The form.** T_ψ is a symmetric F₄-trilinear form on V_ψ.
- **(b) The count over ψ.** The homomorphisms f: π → G with f mod N = ψ number

  |Z¹(π; F₄_ω)| · |B¹(π; F₄_{ω²})|² · 𝒩(T_ψ),

  where

  𝒩(T) = #{(a, b) ∈ V × V : T(a, b, ·) = 0} = |V|⁻¹ Σ_{a,b,c ∈ V} (−1)^{tr T(a,b,c)}.
- **(c) Symmetry.** ψ and ψ² contribute equally.
- **(d) Bounded homology.** If H₁(M) ≅ Z/3, then

  |Hom(π, G)| = 1 + 128 · 4^d · 𝒩(T_ψ), with d = dim_{F₄} V_ψ.
- **(e) The cover.** T_ψ is the triple cup product of the 3-fold cyclic cover M̃_ψ, with F₄ coefficients, restricted to one
  eigenspace of the deck transformation.

**What it says.** Counting maps into G is a statistic of a single symmetric cubic form: three-way interaction among first
cohomology classes.
- For SL(2,3), with an untwisted central layer, the obstruction was a bounded family of quadratic forms. That is pairwise
  interaction, which Gauss sums count (`SL23-BOUNDED-20261025-001A`).
- Here the twisting moves the obstruction into H²(M; F₄_ω), which can be large even when H₁(M) is bounded
  (`UT3-TWIST-PROBE-20261025-001`). Poincaré duality then turns "the obstruction vanishes" into "a cubic form vanishes on a pair".

## Nearest known result

- **Matei and Suciu (J. Algebra 286, 2005).**
  - They give the general twisted lifting test: ρ lifts if and only if ρ*[χ] = 0 in H²_{σρ}(G, A).
  - Part (b) is that test for this group, combined with the cohomological description of maps into a split extension. They give no
    complexity bounds.
- **Samperton and Weiß (arXiv:2602.02885v2, 2026).**
  - For class-2 nilpotent G with untwisted coefficients, the obstruction map Hom(π, B) → H²(π, Z(G)) is quadratic. Gauss sums
    count its zeros in polynomial time when |H²(M, Z(G))| is bounded.
  - Their footnote 11 says it is not clear that this holds in the twisted setting. This proof describes the twisted obstruction: one
    cubic form.
  - It does not settle their question. Their theorem bounds H² with the twisted coefficients, and that is unbounded in the instances
    of the hardness proof. What the hardness proof shows is that bounded H₁ is not enough.
- **Nosaka (arXiv:1808.08532, Theorem 3.1).**
  - The trilinear form with coefficients Z[t^{±1}]/(n, t² + t + 1) is the triple cup product of the 3-fold cyclic branched cover of
    a link.
  - For n = 2 these coefficients are F₄. It is the closest statement to (e), and it has no counting content.
- **The untwisted analogue.** For D₈ = UT₃(F₂), the same duality gives |Hom| = |H¹| · #{(a, b) : a ⌣ b = 0}.
- **Novelty.** Parts (a)–(c) and (e) are standard obstruction theory and duality, with high folklore risk. What this proof adds is
  the reading: with bounded homology, the twisted obstruction is one cubic form on a space that can grow.

## 1. Lifting through the two layers

**The layers.**
- A = Z(N) = {(0, 0, z)} ≅ F₄, and N/A ≅ F₄² through (x, y).
- With the section s(x, y) = (x, y, 0), we get s(x, y) s(u, v) = (0, 0, x·v) · s(x + u, y + v). So the 2-cocycle of N over N/A is
  β((x, y), (u, v)) = x·v, which is bilinear.
- α preserves {z = 0}, so (x, y, e) ↦ (x, y, 0) hᵉ is a section of G → G/A compatible with the complement ⟨h⟩.
- G/A = (F₄_{ω²})² ⋊ C₃.

**Maps to G/A.**
- Maps π → G/A over ψ are exactly the pairs of 1-cocycles (c_x, c_y) ∈ Z¹(π; F₄_{ω²})². This is the standard description of maps
  into a split extension.

**The lifting obstruction.**
- Lift each g to s(c_x(g), c_y(g)) h^{ψ(g)}. Multiplying two lifts gives the A-valued 2-cocycle

  (g, g′) ↦ β((c_x(g), c_y(g)), g·(c_x(g′), c_y(g′))) = c_x(g) · (g·c_y(g′)).

  This is the cup product c_x ⌣ c_y for the coefficient product F₄_{ω²} ⊗ F₄_{ω²} → F₄_ω, (x, y) ↦ xy. Its values lie in
  A_ψ = F₄_ω, since h acts on z by ω.
- So the map lifts if and only if [c_x ⌣ c_y] = 0 in H²(π; F₄_ω).
- When it lifts, the lifts form a torsor under Z¹(π; F₄_ω).
- The class depends only on the cohomology classes a = [c_x] and b = [c_y], because δu ⌣ c_y = δ(u · c_y).

**Count over ψ.**

  |Z¹(π; F₄_ω)| · |B¹(π; F₄_{ω²})|² · #{(a, b) ∈ V_ψ² : a ⌣ b = 0 in H²(π; F₄_ω)}.

## 2. Poincaré duality turns the obstruction into a cubic form

**Passing from π to M.**
- A K(π, 1) is obtained from M by attaching cells of dimension at least 3. So H²(π; L) → H²(M; L) is injective for every local
  system L.
- Cup products are natural. So a ⌣ b = 0 in H²(π) if and only if a ⌣ b = 0 in H²(M).

**Duality.**
- M is closed and orientable, and F₄ is a field.
- The local system F₄_{ω²} is the F₄-dual of F₄_ω, since the dual of monodromy ω is ω⁻¹ = ω².
- So the pairing H²(M; F₄_ω) × H¹(M; F₄_{ω²}) → H³(M; F₄) ≅ F₄, (x, c) ↦ ⟨x ⌣ c, [M]⟩, is perfect.
- Hence a ⌣ b = 0 if and only if T_ψ(a, b, c) = 0 for every c ∈ V_ψ. This proves (b), first form.

**Symmetry.**
- In characteristic 2, graded commutativity of degree-one classes with a commutative coefficient product gives a ⌣ b = b ⌣ a.
- Associativity then makes T_ψ totally symmetric, which is (a).

**The character sum.**
- For fixed (a, b), the map c ↦ tr T(a, b, c) is an F₂-linear functional on V_ψ.
- It vanishes identically if and only if T(a, b, ·) = 0, because the trace form (x, y) ↦ tr(xy) on F₄ is nondegenerate and
  T(a, b, ·) is F₄-linear.
- So Σ_c (−1)^{tr T(a,b,c)} = |V| · [T(a, b, ·) = 0], which is the second form of 𝒩.

## 3. ψ and ψ² (part c)

- Let σ be the Frobenius automorphism applied entrywise. Then σ ∘ α = α² ∘ σ.
- So Φ(n, hᵉ) = (σ(n), h^{2e}) is an automorphism of G.
- Composition with Φ is a bijection from the maps over ψ to the maps over ψ².

## 4. Bounded homology (part d)

**The trivial character.**
- If H₁(M) ≅ Z/3, then π has three maps to C₃: the trivial one, ψ and ψ².
- Over the trivial one, the maps go into the 2-group N.
- A nontrivial image P would have a nontrivial abelian quotient, which would give a nontrivial map π → (abelian 2-group). That is
  impossible, so this term is 1.

**The nontrivial characters.**
- Every vector is moved, so H⁰(M; F₄_{ω^k}) = 0. Hence B¹ ≅ F₄ and |B¹| = 4.
- Applying σ to cocycle values is an F₂-isomorphism Z¹(F₄_{ω²}) → Z¹(F₄_ω) that preserves coboundaries. So
  |Z¹(F₄_ω)| = 4 · 4^d.
- Therefore |Hom(π, G)| = 1 + 2 · 4^{d+1} · 16 · 𝒩 = 1 + 128 · 4^d · 𝒩.

## 5. The cover (part e)

- Let p: M̃ → M be the 3-fold cyclic cover of ψ. Then p*F₄_{ω^k} is trivial.
- By Shapiro's lemma, H¹(M̃; F₄) = ⊕_k H¹(M; F₄_{ω^k}), the eigenspace decomposition of the deck transformation. So p* identifies
  V_ψ with one eigenspace. p* is injective, since the transfer composed with p* is multiplication by 3, which is 1.
- Cup products are natural, and ⟨p*y, [M̃]⟩ = 3⟨y, [M]⟩ = ⟨y, [M]⟩ for y ∈ H³(M; F₄). So
  T_ψ(a, b, c) = ⟨p*a ⌣ p*b ⌣ p*c, [M̃]⟩.
- For a knot surgery S³₃(K) with ψ(μ) = 1, the cover is +1-surgery on the lift of K in the 3-fold branched cover Σ₃(K). This is a
  remark only.

## Check

`check.py` uses only the standard library and the fresh module `tp_lib.py` in this directory; it takes about 20 s. Results are in
`result.json`.

1. **The group.**
   - |G| = 192.
   - Associativity holds on 20,000 random triples.
   - Φ is an automorphism, checked on all pairs.
   - Z(G) = 1.
2. **Brute force.**
   - On S³₃(K) for K ∈ {3₁, 5₁, 4₁, 5₂, 8₁₈, 3₁ # 3₁}, every homomorphism is enumerated. The enumeration propagates the images of
     the top arcs through the braid and checks every relator.
   - The enumeration agrees with 1 + 128 · 4^d · 𝒩, where 𝒩 is counted from the obstruction bimap: 3585, 129, 8193, 129, 229377
     and 100353.
   - H₁ = Z/3 by Smith normal form.
   - ψ² gives the same 𝒩.
3. **Duality.**
   - Six manifolds are tested: 3₁, 8₁₈, 3₁ # 3₁, (3₁)^{#3}, the coupled knot with n = 6, and (4₁)^{#5} with one Borromean
     insertion (`TRIPLE-PRODUCT-20261026-001C`).
   - On each, the bimap is the contraction of a symmetric, F₄-balanced trilinear form with injective pairing.
   - The form's kernel count equals 𝒩.
   - Where V is small, the explicit cubic character sum |V|⁻¹ Σ (−1)^{tr T} also equals 𝒩: 7, 112, 49, 343.
4. **Regression against the probes.**
   - (3₁)^{#k} gives 1 + 128 · 28^k for k = 1, 2, 3.
   - (4₁)^{#k} gives 1 + 128 · 64^k for k = 1, 2.
5. **Controls.**
   - Dropping the obstruction overcounts on S³₃(3₁).
   - The figure-eight knot has zero obstruction.

## Scope

- **Where it holds.** The counting formula holds for every closed orientable 3-manifold. The closed form 1 + 128 · 4^d · 𝒩 needs
  H₁(M) = Z/3.
- **Cited, not proved:**
  - central-extension obstruction theory with twisted coefficients (Matei–Suciu 2005);
  - Poincaré duality with local coefficients;
  - the injection H²(π) → H²(M).
- **Checked** on knot surgeries given by braid closures.
- **No complexity claim** here. Complexity is `CORRECTIONS-20261026-001D`, the reissue of `TRIPLE-PRODUCT-20261026-001D`. No P versus NP claim.
