# A cross-layer hard pair makes counting #P-hard although the class-2 quotient is easy

Status: Proved

## Standard statement

**Setting.**
- p ≥ 5 is prime, r | p − 1, and Z ∈ F_p^× has order r. A character is an exponent e ∈ Z/r, acting by Z^e; 1 is the trivial
  character.
- 𝔫 = L₁ ⊕ L₂ ⊕ L₃ is a graded Lie algebra over F_p of class at most 3, so [L_i, L_j] ⊆ L_{i+j}.
- C_r acts by graded Lie automorphisms, diagonally: L_i = ⊕_χ L_{i,χ}.
- N = (𝔫, ∗) carries the Baker–Campbell–Hausdorff product to degree 3:

  X ∗ Y = X + Y + ½[X, Y] + (1/12)([X, [X, Y]] − [Y, [X, Y]]).

  Because the class is below p, this is a group of exponent p (the Lazard correspondence), and C_r acts on it by automorphisms.
- G = N ⋊ C_r.
- **Cochains.** For π finitely presented and ψ: π → C_r, cochains are twisted by ψ. Put δc(g, h) = c(g) + g·c(h) − c(gh). The
  bracket-cup of 1-cochains is (a ⌣ b)(g, h) = [a(g), g·b(h)].

**Proposition 1 (the layered count).**
- **(a) Layers.** Maps π → G over ψ correspond to triples (f₁, f₂, f₃) of 1-cochains with values in L₁, L₂, L₃ satisfying
  - δf₁ = 0,
  - δf₂ = −½ f₁ ⌣ f₁,
  - δf₃ = −R(f₁, f₂), where R = ½(f₁ ⌣ f₂ + f₂ ⌣ f₁) + (1/12) C(f₁) and

    C(f₁)(g, h) = [f₁(g), [f₁(g), g f₁(h)]] − [g f₁(h), [f₁(g), g f₁(h)]].
- **(b) Classes.** The number of completions of f₁ depends only on its class ξ ∈ H¹(π; L₁). For fixed f₁, the number of completions
  of f₂ depends only on f₂ modulo coboundaries. Hence

  |Hom_ψ(π, G)| = |B¹(L₁)| · |B¹(L₂)| · |Z¹(L₃)| · Σ_{ξ : o₂(ξ) = 0} #{ζ : o₃(ξ, ζ) = 0},

  where o₂(ξ) = [½ f₁ ⌣ f₁] ∈ H²(π; L₂), and ζ runs over an affine space over H¹(π; L₂). Here o₃(ξ, ζ) = [R] ∈ H²(π; L₃) is
  affine in ζ, with linear part ζ ↦ [ξ ⌣ ζ].
- **(c) Trivial characters.** If π = π₁M with M closed and oriented, H₁(M) = Z/r and ψ onto, the trivial-character parts of every
  L_i contribute no classes and no conditions: H¹ and H² of M with coefficients F_p both vanish.

**Theorem 2 (the cross-layer group).**
- **The group.** Let 𝔫_× be the free class-3 Lie algebra on x and y, with basis x, y, z = [x, y], a = [x, z], b = [y, z]. C_r fixes
  x and acts on y by a character α with α ≠ 1 and α² ≠ 1. So the characters are 1, α, α, α and α² respectively.
- **The identity.** Let G_× = N_× ⋊ C_r. For every M as in (c) and every k ∈ Z/r,

  |Hom_{ψ_k}(π₁M, G_×)| = |Z¹(π₁M; F_{α^k})| · |Hom_{ψ_k}(π₁M, H_{α,α} ⋊ C_r)|.

  Here H_{α,α} is the Heisenberg group whose two generators both have character α, and ψ_k = kψ.

**Corollary 3 (the class-2 quotient does not decide).**
- **Hardness.** Counting |Hom(π₁(S³_r(K)), G_×)| for knots K given by diagrams is #P-hard under polynomial-time Turing reductions.
- **The quotient is easy.** The class-2 quotient G_×/γ₃ is H_{1,α} ⋊ C_r, the Heisenberg group with characters (1, α). It has no hard
  pair, so its counting is polynomial for closed manifolds with bounded H₁ (`COPRIME-CLASS2-20261026-001C`).
- **What carries the hardness.** G_× has a graded hard pair across layers: y ∈ L₁ and z ∈ L₂, both of character α, with
  [y, z] = b ≠ 0 and α² ≠ 1.
- **The control.** With α² = 1, b has the trivial character, and the count on these manifolds is a product of dimension factors.

**What it says.** Past class 2, the hard-pair criterion must be read in the associated graded Lie algebra, between any two layers.
A trivial character in layer one can make a free, nontrivial-character layer-two lift whose bracket with layer one is a three-way
interaction.

## Nearest known result

- **Dwyer, "Homology, Massey products and maps between groups" (1975), and Matei–Suciu.** Lifting obstructions through central series
  and twisted cohomology. Proposition 1 is the BCH form of this, for exponent-p groups with a coprime action.
- **The Lazard correspondence.** Exponent-p groups of class below p correspond to Lie algebras through BCH.
- **`COPRIME-CLASS2-20261026-001B`, C and `CLASSK-DICHOTOMY-20261026-001`.** The class-2 theory, the Heisenberg count, and the
  hardness machinery used in Corollary 3.
- **Novelty.** Proposition 1 is standard bookkeeping. Theorem 2 is a short computation. Corollary 3 is new as an example showing that
  bounded-homology hardness is not determined by the class-2 quotient. Folklore risk: medium.

## Proof

### Proposition 1

**(a) Layers.**
- A homomorphism is g ↦ (f(g), ψ(g)) with f(gh) = f(g) ∗ (g·f(h)).
- Split f by degree. Brackets raise degree, so the degree-1, 2 and 3 parts of the BCH product give the three equations.
- In degree 3 the terms are the cross terms ½([f₁(g), g f₂(h)] + [f₂(g), g f₁(h)]) and the cubic BCH terms.
- Relators evaluated in G are exactly these conditions on the presentation complex.

**(b) Classes.**
- **f₁.** Conjugating a homomorphism by exp(b), b ∈ L₁, is a bijection of Hom_ψ. It changes f₁ by the coboundary of b.
- **f₂.** For fixed f₁, the solutions f₂ form a coset of Z¹(L₂). Conjugation by exp(c), c ∈ L₂, fixes f₁ and changes f₂ by the
  coboundary of c, so the number of f₃-completions depends on f₂ modulo B¹(L₂).
- **f₃.** f₃ exists iff [R] = 0, and then there are |Z¹(L₃)| choices.
- **Linearity in ζ.** For z ∈ Z¹(L₂), R(f₁, f₂ + z) − R(f₁, f₂) = ½(f₁ ⌣ z + z ⌣ f₁). The bracket is antisymmetric and degree-one
  classes anticommute, so this has the class [f₁ ⌣ z].

**(c) Trivial characters.** With H₁(M) = Z/r and p ∤ r, H¹(M; F_p) = 0, and H²(M; F_p) = 0 by duality.

### Theorem 2

Fix k and write α for α^k. If α^k = 1, both sides are 1 by (c). Otherwise:
- **Layer one.** f_x ∈ Z¹(π; F_p) = 0, so f₁ = f_y y with f_y ∈ Z¹(F_α).
- **Layer two.** f₁ ⌣ f₁ = (f_y ∪ f_y)[y, y] = 0, so f₂ = f_z z with f_z ∈ Z¹(F_α) free.
- **Layer three.**
  - f₁ ⌣ f₂ = (f_y ∪ f_z) b and f₂ ⌣ f₁ = −(f_z ∪ f_y) b.
  - C(f₁) = 0, because only y occurs in f₁.
  - The a-component vanishes, because f_x = 0.
  - So o₃ = [f_y ∪ f_z] b, with values in H²(F_{α²}). (If α² were trivial this would be no condition, by (c).)
- **The cross-layer count.** By (b),

  |Hom_{ψ_k}| = |B¹(F_α)|² · |Z¹(F_α)| · |Z¹(F_{α²})| · #{(u, v) ∈ V_α × V_α : u ⌣ v = 0}.

  Here |B¹(L₁)| = |B¹(L₂)| = |B¹(F_α)|, and |Z¹(L₃)| = |Z¹(F_α)| |Z¹(F_{α²})|.
- **The Heisenberg count.** `COPRIME-CLASS2-20261026-001B` (a) gives |Z¹(F_{α²})| |B¹(F_α)|² times the same kernel count. The ratio is
  |Z¹(F_α)|.

### Corollary 3

- **The manifolds.** Let S = (α, α, α⁻²). That is pattern {s, s, s⁻²}, or {s, s, s} when α³ = 1. Take the gadget manifolds M_Γ of
  `CLASSK-DICHOTOMY-20261026-001C` (Lemma R).
- **The Heisenberg count.** By Theorem A of `CLASSK-DICHOTOMY-20261026-001A`, the Heisenberg (α, α) count is Σ_k c_k f_k(Γ). Each
  f_k is multiplicative over disjoint unions. Because (α, α) is a hard pair (α² ≠ 1), the sector-1 weight is nonconstant with rank at
  least two.
- **The extra factor.** |Z¹(F_{α^k})| = p^{[α^k ≠ 1]} p^{d_{α^k}}. Its exponent d_{α^k} is linear in (n, m) with no constant term,
  so h_×(Γ) = Σ_k c′_k f′_k(Γ) with every f′_k multiplicative and positive.
- **Hardness.** Lemma I of `CLASSK-DICHOTOMY-20261026-001C` (an anchor graph and a Vandermonde solve over disjoint unions) recovers
  the sector-1 term. Bulatov–Grohe makes it #P-hard.
- **The quotient.** Its hard pairs would need two nontrivial characters among (1, α), so it has none.

## Check

`check.py` uses numpy and `bc_lib.py` in this directory. It imports `cp_lib.py` (`COPRIME-CLASS2-20261026-001B-P001`) and `ck_lib.py`
(`CLASSK-DICHOTOMY-20261026-001A-P001`) read-only.

1. **The BCH groups.** The constructor checks grading, equivariance and Jacobi. On 200 random samples each, for the cross-layer and
   four-way algebras at (5, 4), (7, 3) and (7, 6): associativity, inverses, exponent p, and equivariance of the group law.
2. **Class dependence (Proposition 1 (b)).** On 3₁ and 6₁ surgeries, in every sector, for the cross-layer and four-way groups:
   - the layered direct count (cocycles, then the affine layer-2 and layer-3 systems solved with the group law) equals |B¹(L₁)| times
     the sum of completions over representatives of H¹(L₁);
   - completions agree on coboundary-shifted representatives.
3. **Theorem 2.** On knot surgeries with H₁ = Z/r (3₁, 4₁, 5₂, 6₁ and three connected sums) at (p, r, α) = (5, 4, Z), (7, 3, Z),
   (7, 6, Z), (7, 6, Z²) and (13, 4, Z), in every sector: the direct count equals |B¹(L₁)| |B¹(L₂)| |Z¹(L₃)| times cp_lib's
   Heisenberg (α, α) kernel count.
   - **Control.** α = −1 at (5, 4) gives dimension factors times |V_α|². This is bookkeeping only: with α² = 1 the cup product lands in the trivial character, so the Heisenberg kernel count is also |V_α|².
4. **The hard-pair structure.**
   - The cross-layer algebra's only graded hard pair is (y, z).
   - The quotient has none, and the Heisenberg (α, α) has (x, y).
   - The sector-1 weight on the gadget model is nonconstant.
5. **Hardness bookkeeping on the gadget model.**
   - f_k = (Heisenberg sector function) × p^{d_{α^k}}, computed through the Fourier form.
   - K₂ is an anchor, and exact Vandermonde solves recover the sector-1 term on P₃ and the digon.

## Scope

- **What is proved.** p ≥ 5, r | p − 1, graded class-3 Lie algebras (Proposition 1), and Theorem 2 and Corollary 3 for the
  cross-layer group on r-surgeries of knots.
- **Cited:**
  - the Lazard correspondence and BCH to degree 3;
  - `CLASSK-DICHOTOMY-20261026-001` A and C (and through them Bulatov–Grohe and the realization);
  - `COPRIME-CLASS2-20261026-001B` (a) and C.
- **Not covered:**
  - knot groups, where x has a nonzero cocycle and the quotient's trivial-character coupling enters;
  - p-torsion in H₁;
  - filtered (non-graded) Lie algebras;
  - p = 2, 3.
- No P versus NP claim.
