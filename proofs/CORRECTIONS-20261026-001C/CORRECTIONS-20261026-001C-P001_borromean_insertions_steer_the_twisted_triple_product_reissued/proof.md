# Borromean insertions steer the twisted triple product

Status: Proved

**Reissue.**
- This is the reissue of `TRIPLE-PRODUCT-20261026-001C-P001`, made in `CORRECTIONS-20261026-001C` on 2026-10-26 after the independent
  review `COPRIME-CLASS2-20261026-001A`. It supersedes the closed version, which is left unchanged.
- **What changed:**
  - Moussard 2017 is cited as the precursor, and the novelty is downgraded;
  - Habiro's Props. 3.3–3.4, with disk framing and preservation of the Seifert framing (m1);
  - the trivial covering over the Y-graph's neighbourhood, and existence of the cocycle extensions (m2);
  - basing paths (m3);
  - the leaf convention, with a typo fixed (m4);
  - what is proved versus interpreted about realizable forms (m7).
- The checks are unchanged. They import the reissued library.

## Standard statement

**Setting.**
- As in `TRIPLE-PRODUCT-20261026-001A`: M is a closed oriented 3-manifold, ψ: π₁(M) → C₃ is a surjection, V = H¹(M; F₄_{ω²}),
  and T(a, b, c) = ⟨a ⌣ b ⌣ c, [M]⟩ is the twisted triple product.
- **Y-graph.** A Y-graph Γ ⊂ M (Matveev; Habiro's Y-clasper) has three framed leaves ℓ₁, ℓ₂, ℓ₃, joined by edges to one vertex.
- **Y-surgery.** M_Γ is the result of Y-surgery (Borromean surgery) along Γ.
- **Leaf functionals.** For a leaf ℓ, based at the vertex through its edge, set λ_ℓ(a) = c_a(ℓ). Here c_a is any cocycle
  representing a. The value is well defined when ψ(ℓ) = 0.
- **The wedge.** (λ₁ ∧ λ₂ ∧ λ₃)(a, b, c) is the determinant of the 3 × 3 matrix (λ_i(a), λ_i(b), λ_i(c)). It is an alternating
  F₄-trilinear form.

**Theorem 2 (a twisted Borromean formula).** Suppose ψ(ℓ_j) = 0 for j = 1, 2, 3. Then:
- (a) H₁(M_Γ) ≅ H₁(M) canonically, through the complement of Γ. ψ extends to M_Γ, and V(M_Γ) ≅ V(M).
- (b) Under these identifications, T_{M_Γ} = T_M + λ₁ ∧ λ₂ ∧ λ₃.

**Corollary 3 (steering).** Every F₄-linear functional on V is λ_ℓ for some loop ℓ ∈ ker ψ. Hence for every alternating
F₄-trilinear form A on V there is a manifold M′ with:
- H₁(M′) ≅ H₁(M);
- T_{M′} = T_M + A;
- M′ obtained from M by at most C(d, 3) Y-surgeries along disjoint Y-graphs with leaves in ker ψ.

**Corollary 4 (knot surgeries).**
- Suppose M = S³₃(K), and each of the Y-graphs has a leaf bounding a disk that meets K but no other part of the Y-graphs. Then
  M′ = S³₃(K′) for a knot K′ obtained from K by Borromean moves.
- In the braid model the move is an insertion. Insert the 3-cabled Borromean braid (σ₁σ₂⁻¹)³ on three bundles of three adjacent
  strands at a level.
  - This is surgery on a Y-clasper whose leaves encircle the bundles (Habiro).
  - Its leaf functionals are the right-to-left bundle products: λ(a) = c_a(x_{q+2} x_{q+1} x_q) = c_a(x_{q+2}) + ω² c_a(x_{q+1}) +
    ω c_a(x_q).

**What it says.**
- With bounded homology, the alternating part of the twisted triple product is free: Borromean moves change it at will.
- The non-alternating part, a ↦ T(a, a, ·), is invariant. It is a twisted Bockstein, governed by the linking pairing, which
  Borromean surgery preserves.
- So the forms reachable from M by such Y-surgeries are exactly T₀ + (all alternating forms). Each change is alternating, and every
  alternating form is reached. Both directions are proved.
- **Interpretation, not proved:**
  - that every 3-manifold with the same H₁ and V has a form of this kind;
  - that the invariant non-alternating part is a twisted Bockstein governed by the linking pairing.

## Nearest known result

- **Massuyeau, AGT 3 (2003), Lemma 3.2.** For a Y-graph G with leaves L₁, L₂, L₃ in a closed manifold M and any n ≥ 0,
  u⁽ⁿ⁾_{M_G}(y′) − u⁽ⁿ⁾_M(Φ(y′)) = ⟨Φ(y′₁) ∧ Φ(y′₂) ∧ Φ(y′₃), [L₁] ∧ [L₂] ∧ [L₃]⟩⁽ⁿ⁾ ∈ Z_n.
  - It has untwisted Z_n coefficients, and torsion is allowed.
  - Massuyeau's Remark 3.3 says the lemma essentially appears in Turaev's "Borromean replacements".
  - This is exactly the untwisted case of Theorem 2(b).
- **Matveev (1987).** Borromean surgery preserves H₁ and the linking pairing, and these classify Borromean-surgery equivalence.
- **Sullivan (1975) and Turaev.** They realize alternating trilinear forms on free abelian groups (untwisted).
- **Niu (arXiv:2606.12094, June 2026).** Borromean band-sums realize arbitrary mod-p triple cup tensors on rational homology spheres
  with H₁ ≅ (Z/p)⁶. This is untwisted and of fixed rank.
- **Novelty.**
  - No twisted or equivariant realization theorem was found in the scan.
  - What is new here is the twisted statement: leaves in ker ψ, a lift to the 3-fold cover, and the constant 3 = 1. With it, the
    alternating part of the twisted form becomes steerable while H₁ = Z/3 stays fixed.
  - **Moussard**, "Equivariant triple intersections", Ann. Fac. Sci. Toulouse (2017), arXiv:1403.0446, Prop. 2.5 and Thm. 2.7, is
    the precursor.
    - For a Y-graph null in M ∖ K, the equivariant triple intersection map on the infinite cyclic cover changes by
      Σ_σ ε(σ) Π_j δ(t_j) b(β_j, [γ_{σ(j)}])(t_j), with rational coefficients.
    - Ours is the finite-cover, F₄ analogue, for leaves that only lie in ker ψ: a bundle of three strands links K three times, so it
      is not null.
  - Folklore risk: medium to high. The argument is routine once one passes to the cover, and its rational version is in Moussard.

## 1. Lifting the surgery to the cover

**Γ lifts to three copies.**
- π₁(Γ) is generated by the leaf loops, read through the edges. Since ψ(ℓ_j) = 0, ψ is trivial on Γ.
- So the preimage of Γ in the 3-fold cyclic cover p: M̃ → M is three disjoint copies Γ_g, one for each g ∈ C₃. Each copy maps
  homeomorphically to Γ.

**The surgery lifts.**
- Y-surgery replaces a regular neighbourhood N(Γ), a genus-3 handlebody, by another handlebody glued to the same boundary.
- N(Γ) lifts to three disjoint copies, so the cover of M_Γ is M̃ surgered along Γ₁, Γ_t and Γ_{t²}.
- The cover is taken for ψ, extended through the canonical isomorphism H₁(M_Γ) ≅ H₁(M) induced by the common complement
  (Matveev).
- **The cover over the surgery region is trivial.** ψ vanishes on ∂N(Γ), and H₁(∂N) → H₁(N) is onto, both for N(Γ) and for the
  handlebody glued in. So ψ extends over each handlebody trivially, and the cover restricts to three disjoint copies of each.
- **This gives (a).** The same surjectivity shows that every twisted cocycle on M − N(Γ) extends across either handlebody, and
  uniquely. So V(M′) ≅ V(M).
- **The hypothesis matters.** In the referee's control in `COPRIME-CLASS2-20261026-001A`, leaves with ψ = 2 changed dim V from 6 to
  4.

## 2. The eigenspace computation

**The cup-product change in the cover.**
- Apply Massuyeau's Lemma 3.2 with n = 2 three times, once for each of the disjoint copies.
- Each copy's leaves lie in the complement of the other copies, so their homology classes and the identifications Φ compose.
- For x, y, z ∈ H¹(M̃; F₂) this gives

  u_{M̃_Γ}(x, y, z) − u_{M̃}(x, y, z) = Σ_{g ∈ C₃} det(x(gL_i), y(gL_i), z(gL_i)).

  Signs and orientations do not matter in characteristic 2.

**Extending to F₄.**
- H¹(·; F₄) = H¹(·; F₂) ⊗ F₄, and the cup product extends F₄-trilinearly. So the same formula holds with F₄ coefficients.

**Restricting to the eigenspace.**
- Take x = p*a, y = p*b, z = p*c for a, b, c ∈ V. They lie in one eigenspace of a deck generator t: t*x = εx, with ε = ω^{±2}
  depending on the convention.
- Then x(gL) = ε^k x(L) for g = t^k. The g-th term is ε^{3k} det(…) = det(…).
- The three terms add to 3 det = det.
- Since T = u ∘ p* (`TRIPLE-PRODUCT-20261026-001A`, part e) and (p*a)(L̃_i) = c_a(ℓ_i) for the based lift L̃_i of ℓ_i, this is (b).
- **Basing.** Reading a leaf needs a path from the base point to the Y-graph's vertex, then the edge. Changing that path by g
  multiplies the three leaf functionals by the same eigenvalue factor. The determinant then changes by its cube, ε^{3k} = 1.

## 3. Every functional is a leaf (Corollary 3)

**The leaf functionals form an F₄-subspace.**
- For ℓ, ℓ′ ∈ ker ψ, λ_{ℓℓ′} = λ_ℓ + λ_{ℓ′}, because c(ℓℓ′) = c(ℓ) + ψ(ℓ)·c(ℓ′) and ψ(ℓ) = 0.
- If ψ(τ) = 1, then c(τℓτ⁻¹) = ω² c(ℓ).
- So {λ_ℓ : ℓ ∈ ker ψ} is closed under addition and under multiplication by ω.

**It is all of V*.**
- Suppose λ_ℓ(a) = 0 for every ℓ ∈ ker ψ. Then p*a vanishes on H₁(M̃), which is generated by lifts of such loops. So p*a = 0, and
  a = 0 because p* is injective.

**Realizing an alternating form.**
- Every element of ker ψ is represented by an embedded framed loop, and disjoint Y-graphs with prescribed leaves exist by general
  position.
- An alternating F₄-trilinear form is Σ_{i<j<k} A_{ijk} e*_i ∧ e*_j ∧ e*_k in a basis of V*, and A_{ijk} e*_i is again a
  functional.
- So C(d, 3) Y-surgeries suffice, and their changes add by (b).

## 4. Knot surgeries (Corollary 4)

- **The hypothesis.** A leaf of Γ bounds a disk D ⊂ S³ that meets K but no other part of the Y-graphs, and the leaf carries the
  framing induced by D (a disk-leaf).
- **Forgetting K, the Y-graph is trivial.** Habiro (Geom. Topol. 4, 2000) Prop. 3.3: every admissible tree clasper is tame. Prop. 3.4: if
  a tree clasper T for a link γ has a trivial disk-leaf, then γ^T is equivalent to γ. Here K is forgotten, so γ is empty and surgery
  along T gives back S³.
- **With K present the disk-leaf is not trivial,** since it meets K. That is why the argument forgets K and tracks K through the
  diffeomorphism.
- **The framing.** With framing ±1 relative to the disk, the clasper would not be trivial.
- So the Y-surgeries turn (S³, K) into (S³, K′).
- **The Seifert framing is preserved.** The diffeomorphism is the identity near a meridian of K, so it carries the Seifert
  longitude of K to that of K′. Hence surgery with coefficient 3 on K corresponds to coefficient 3 on K′, and M′ = S³₃(K′).

## 5. The braid model

- **The insertion is a Y-surgery.** Inserting the cabled Borromean braid at bundles B₁, B₂, B₃ is surgery along a Y-clasper whose
  leaf j bounds a small disk crossing the three strands of B_j. This is Habiro's description of the Borromean move, applied to
  parallel strands.
- **The leaves lie in ker ψ:** each leaf has ψ = 3 · 1 = 0.
- **The leaf class.** Across a crossing, the Wirtinger relator x_j = x_o^{−s} x_i x_o^{s} preserves the right-to-left product of
  adjacent arcs: x_o x_j = x_i x_o for s = 1. So the leaf class is x_{q+2} x_{q+1} x_q.
- **This is a convention.** With the opposite relator x_j = x_o^{s} x_i x_o^{−s}, the reversed product holds instead. The independent
  replay in `COPRIME-CLASS2-20261026-001A` confirms this, 120 of 120 configurations each way.
- **The cocycles do not change across an insertion.** The braid action on the bundle arcs conjugates them by commutators of bundle
  products. Bundle products lie in ker ψ, where every cocycle restricts to a homomorphism. So cocycle values on the top arcs carry
  through unchanged. The check confirms that the cocycles of K and K′, read on the top arcs, span the same space.

## Check

`check.py` uses the standard library and imports `tp_lib.py` read-only from `CORRECTIONS-20261026-001A-P001`. It runs in
about 3 s; results are in `result.json`. For every a ∈ V, it compares the kernel of b ↦ B(a, b), computed from the obstruction
bimap of the actual knot, with the kernel of b ↦ T_pred(a, b, ·).

1. **One insertion at each of the 20 levels of (4₁)^{#5}**, on the window of positions 1–9.
   - At the four levels where the three leaves are independent (6, 7, 13, 14), the form becomes λ₁ ∧ λ₂ ∧ λ₃. 𝒩 = 80896, the
     count of a decomposable form on F₄⁵, and no a mismatches.
   - At the other 16 levels the leaves are dependent. The predicted change is 0, and 𝒩 stays 4^{10} = 1048576.
   - H₁ = Z/3 throughout, and the cocycles read on the top arcs span the same space as for the base knot.
2. **Additivity.**
   - Two or three insertions (levels (6, 13), (7, 14), (6, 14), (6, 13, 14)) match Σ λ ∧ λ ∧ λ with the same constant 1, with no
     mismatch.
   - Control: scaling one insertion's form by ω mismatches 984 values of a.
   - Control: the left-to-right leaf convention mismatches 1023 values of a.
3. **A base with T₀ ≠ 0: 3₁ # (4₁)^{#4}.**
   - T₀ is recovered from the base by the duality method of `TRIPLE-PRODUCT-20261026-001A`: a symmetric balanced solution space
     of F₂-dimension 2, the F₄ scalars. It is transported to the new knot through the top arcs.
   - After an insertion at either window, T₀ + λ₁ ∧ λ₂ ∧ λ₃ matches every kernel, with 𝒩 = 44032 and 35392.
   - The match holds for all three scalars of T₀. This is expected: the zero set of μξ³ + A does not depend on μ.
   - Control: dropping T₀ mismatches 768 values of a.

The end-to-end instances that realize cycles (a triangle and a digon) are in `CORRECTIONS-20261026-001D`, the reissue of `TRIPLE-PRODUCT-20261026-001D`.

## Scope

- **Where it holds.** Closed oriented 3-manifolds with a surjection to C₃.
- **Cited, not proved:**
  - Massuyeau's Lemma 3.2 (Z_n coefficients);
  - Moussard 2017 (the rational precursor);
  - Matveev's theorem that Y-surgery preserves H₁ and the linking pairing;
  - Habiro's clasper calculus: Props. 3.3–3.4 (disk-leaves with their disk framing), and the identification of a cabled Borromean
    insertion with a Y-clasper whose leaves encircle bundles.
- **Proved here:** the twisted statement, by lifting to the 3-fold cover, and the surjectivity of leaf functionals.
- **Checked exactly** on knots built from figure-eight and trefoil connected sums.
- No complexity claim (see `CORRECTIONS-20261026-001D`); no P versus NP claim.
