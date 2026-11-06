# A nonabelian triple system makes counting #P-hard: the r = 2 dichotomy

Status: Proved

## Standard statement

**Setting.**
- p ≥ 5 is prime.
- 𝔫 = L₁ ⊕ ⋯ ⊕ L_c is a graded nilpotent Lie algebra over F_p of class c ≤ 4. A graded involution θ splits each layer as
  L_k = L_k⁺ ⊕ L_k⁻.
- N = exp(𝔫), with the Lazard correspondence (c < p), and G = N ⋊ ⟨θ⟩.
- The **triple system** of 𝔫⁻ = ⊕_k L_k⁻ is the product B(a, b, c) = [[a, b], c]. It is **nonabelian** if B ≠ 0.
- **Manifolds.** M = S³₂(K) for knots K given as closed braids. ψ: π₁M → C₂ is the surjection,
  V = H¹(M; F_p^ψ), N_M = dim V and d = dim 𝔫⁻.

**Theorem 1 (hardness).** If the triple system of 𝔫⁻ is nonabelian, counting |Hom(π₁M, G)| over 2-surgeries on knots is #P-hard
under polynomial-time Turing reductions.

**Theorem 2 (the r = 2 dichotomy).**
- **Scope.** Graded 𝔫 of class at most 4 with a graded involution, p ≥ 5, and closed oriented 3-manifolds M with H₁(M; F_p) = 0
  and H₁(M) of bounded 2-rank.
- **Statement.** Counting |Hom(π₁M, G)| is polynomial if [[𝔫⁻, 𝔫⁻], 𝔫⁻] = 0 (`TRIPLE-SYSTEM-20261027-001A`, every class), and
  #P-hard otherwise (Theorem 1, already for H₁ = Z/2).

**Examples.**

| algebra | triple system | counting at r = 2 |
| --- | --- | --- |
| every class 2 | abelian | polynomial |
| u₄ with diag(1, −1, 1, −1) (`BEYOND-CLASS2-20261027-001C`) | [[E₁₂, E₂₃], E₃₄] = E₁₄ | #P-hard |
| free class 3 on two or three −1 generators | nonabelian | #P-hard |
| free class 3 on x (+), y (−) (the cross-layer group of `BEYOND-CLASS2-20261027-001A`) | abelian | polynomial at r = 2, hard at r > 2 |
| free class 4 on x (+), y (−) | [[y, [x, y]], y] ≠ 0, through the free layer-2 class [x, y] | #P-hard |
| class 4 on x (+), y (−) modulo [y, [y, [x, y]]] | abelian | polynomial |

**What it says.**
- With two values, a homomorphism is assembled from −1 classes by brackets. A bracket of two −1 elements has the trivial
  character and stays rigid.
- Hardness appears exactly when a bracket of three −1 elements survives: the triple product of the symmetric pair (𝔫, θ). This
  holds even when one of the three is a free class from a deeper layer.
- The criterion "pairs are easy, triples decide" is exact at r = 2 through class 4. It is a complexity statement, not an
  emergence result.

## Nearest known results

- **This program.**
  - `TRIPLE-SYSTEM-20261027-001A`: the polynomial side, every class.
  - `BEYOND-CLASS2-20261027-001C`: the four-way group u₄, whose gadget, J-duality and edge-weight method are generalized here.
  - `CLASSK-DICHOTOMY-20261026-001C`: class 2, all r.
- **Samperton–Weiss (arXiv:2602.02885).** Class-2 nilpotent targets are polynomial with bounded H². With bounded homology,
  nilpotent targets are trivially easy, so a coprime action is needed for hardness.
- **Lie triple systems and symmetric pairs** (Jacobson; Loos). The triple product [[a, b], c] on 𝔫⁻ is the curvature of the
  symmetric space.
- **Novelty.**
  - Candidate new: an exact complexity dichotomy for nilpotent-by-involution targets of class at most 4 on closed 3-manifolds with
    H₁(M; F_p) = 0, decided by the triple system.
  - Folklore risk: medium for the method, which generalizes the previous epic; low for the statement, which was not found.

## Proof

Write F = F_p, d = dim 𝔫⁻, and Z¹ = Z¹(π₁M; F^ψ), of size p^{N_M+1}.

### 1. The layered count

- **Layers.** Lift layer by layer through the lower central series. At layer k:
  - the +1 part of a lift is unique and unobstructed, since H¹(π; F) = H²(π; F) = 0;
  - the −1 part has obstruction o_k ∈ H²(π; F^ψ) ⊗ L_k⁻, and when it vanishes the lifts form a torsor under Z¹ ⊗ L_k⁻.
- **Classes.** Changing the layer-k data by a coboundary of m ∈ L_k⁻ is conjugation by exp(m). So obstructions depend only on
  the class sequence ξ = (ξ_k) ∈ ⊕_k V ⊗ L_k⁻ = V ⊗ 𝔫⁻.
- **J-duality.** By J-duality (`BEYOND-CLASS2-20261027-001C` §2, one −1 basis vector at a time), o_k(ξ) = 0 iff
  Q_k(ξ; s_k) = 0 for all s_k ∈ V ⊗ (L_k⁻)^*.
- **The count.**

  |Hom_ψ| = p^d · #{ξ ∈ V ⊗ 𝔫⁻ : Q_k(ξ; ·) = 0 for all k} = p^d · p^{−N_M d} Σ_{ξ, s} ω^{Q̃(ξ; s)},

  where s ∈ V ⊗ (𝔫⁻)^*, and Q̃ = Σ_k Q̃_k is any polynomial extension that agrees with Q_k wherever the lower obstructions
  vanish. The product of indicators is unchanged by such an extension.
- **Sector 0** contributes 1.

### 2. Base vanishing (any class)

- **One-parameter subgroups.** For a cocycle c and A ∈ 𝔫⁻, the map g ↦ exp(c(g)A) θ^{ψ(g)} is a homomorphism. Indeed θ(A) = −A
  and exp(sA) exp(tA) = exp((s + t)A).
- **On a summand.** Let K be a knot with dim V_K = 1, and normalize c(μ) = 0, so c(λ) = 0 (λ ∈ π″). Then every element c ⊗ A of
  V_K ⊗ 𝔫⁻ lifts with μ ↦ θ and λ ↦ 1. This realizes the class data of every layer at once.
- **Gluing.** Gluing over the meridian amalgam of a connected sum (`BEYOND-CLASS2-20261027-001C` §3) realizes every
  ξ ∈ V ⊗ 𝔫⁻.
- **Conclusion.** On S³₂(#_N T(2, p)) no obstruction occurs, and Q̃ = 0. This generalizes the symmetric-power constructions of
  the previous epic, which are one-parameter subgroups of U₄.

### 3. Steering in class at most 4

Insert cable₂(P, o) at level ℓ, where P is a pure braid with geometric conjugators W_j ∈ γ₃F₄ (P4 and P4B qualify). Let
y_k = log ρ(Y_k) be the bundle values, with −1 layer-1 and layer-2 parts ℓ_k(ξ) ∈ 𝔫⁻ (free data) and rigid +1 parts.

**Lemma 3.1 (the conjugator).** The −1 part of Λ_j := log ρ(W_j(Y)) ∈ γ₃ is W_j⁽³⁾(ℓ₀(ξ), …, ℓ₃(ξ))⁻, where W_j⁽³⁾ is the
degree-3 Lie part of W_j, (1/3) Σ_w M_j(w) [X_{w₁}, [X_{w₂}, X_{w₃}]] by Dynkin–Specht–Wever.

*Proof.* Modulo γ₅ = 0, log ρ(W(Y)) is the Lie part of W of degree 3 and 4, evaluated on the y_k by the BCH formula.
- **Degree 3 on layer-1 parts** gives brackets of three −1 elements: character −1. This is the stated term.
- **Degree 4 on layer-1 parts** gives character +1.
- **Degree 3 with one layer-2 part:**
  - with a −1 layer-2 part, the free class (character −1), this is the stated term with ℓ(ξ₂) included;
  - with a +1 layer-2 part, the character is (−)(−)(+) = +1.
- **Anything else** lies in layer at least 5, hence 0. ∎

**Lemma 3.2 (the shift).** A label z = exp(n)θ in the θ-coset becomes e^Λ z e^{−Λ} = z · exp(−2Λ⁻ − θ[n, Λ]). The term [n, Λ]
lies in layer 4 and has character (−)(−) = +1, so the −1 part of the shift is −2Λ⁻.

*Proof.* z⁻¹ e^Λ z = exp(θ(Ad_{exp(−n)} Λ)) = exp(θ(Λ − [n, Λ])), since [n, [n, Λ]] lies in layer at least 5. Combine with
e^{−Λ}: their bracket lies in layer at least 6. ∎

**Lemma 3.3 (transport).** Shifts of labels by elements of γ₃ pass through a letter like colours on their −1 part.
- The corrections are brackets of a layer-3 −1 shift with a layer-1 −1 part: layer 4, character +1.
- At the bottom, the −1 shift is Bur(w[ℓ:])Δ with Δ = 2 Σ_j Λ_j⁻ (e_{o+2j} + e_{o+2j+1}), as in `BEYOND-CLASS2-20261027-001C`
  Proposition 4.4.

**Proposition 3.4.** Let x = (ξ₁, ξ₂) be the free −1 data in layers 1 and 2 (layer-3 data does not enter in class 4). On data
where the lower obstructions vanish, the −1 obstructions of layers 3 and 4 change by

  ΔQ̃(ξ; s) = 2 Σ_j ⟨W_j⁽³⁾(ℓ(x))⁻, ℓ_j(s)⟩.

*Proof.*
- **Lower layers.** Layers 1 and 2 are unchanged, since the shifts lie in γ₃.
- **The +1 part of layer 3** is unchanged: Λ's layer-3 part is a bracket of three −1 elements, of character −1, by Lemma 3.1.
- **Layer 3.** The −1 relator values of layer 3 change by the transported −2Λ₃⁻. If the new layer-3 obstruction vanishes, the new
  lift differs from the old by −1 layer-3 cochains. These enter layer 4 only through brackets with −1 layer-1 parts (character +1)
  or with zero +1 layer-1 parts.
- **Layer 4.** The −1 relator values of layer 4 change by the transported −2Λ₄⁻, plus +1 corrections (Lemmas 3.2 and 3.3).
- **The pairing.** Pairing with J^T s (`BEYOND-CLASS2-20261027-001C` Lemma 2.1 and Proposition 4.4) gives the formula.
- **Additivity.** A later insertion sees earlier shifts only through bundle values changed in γ₃. They enter W⁽³⁾ only in layer
  at least 5. So insertions add, and canceling pairs γγ⁻¹ change nothing (as before). ∎

**Experimental support.** `TRIPLE-SYSTEM-20261027-001B-E001` confirms Proposition 3.4 exactly (κ = 2) on 36 of 36 fixture-algebra
pairs:
- u₄;
- free class 3 on two and three −1 generators and on (x+, y1−, y2−);
- the class-4 cross-layer algebras, with free layer-2 and layer-3 classes;
- gadgets K3 and C4 at p = 5, 7, 11.

### 4. The gadget

- **The construction.** It is that of `BEYOND-CLASS2-20261027-001C` §5: N = n + 6m summands T(2, p), and one conjugated
  cable₂(P4) per edge. The leaves are X_v − X_u and three private coordinates.
- **The form.** By §2 and Proposition 3.4,

  Q̃(ξ; s) = 2 Σ_e T_B(ℓ^{(e)}(ξ); ℓ^{(e)}(s)),  T_B(A₀, …, A₃; S₀, …, S₃) = Σ_j ⟨W_j⁽³⁾(A)⁻, S_j⟩,

  with A_i ∈ 𝔫⁻ and S_j ∈ (𝔫⁻)^*.
- **One leaf per term.** Each term of T_B uses each of the four leaves exactly once, either as an argument A or as the pairing S.
  In W_j⁽³⁾ the three arguments are the leaves other than j.

### 5. The edge weight

**Definition.** For d = (A, S) ∈ 𝔫⁻ ⊕ (𝔫⁻)^* (the vertex leaf),

  f_B(d) = Σ_{π} ω^{2 T_B(d; π)},

where π runs over the private leaves, in (𝔫⁻ ⊕ (𝔫⁻)^*)³.

**Lemma 5.1.** f_B is integer-valued, even, independent of the nonzero constant in front of T_B, and f_B(0) = p^{6d} is its
maximum.

*Proof.*
- **One leaf per term.** Every term contains leaf 0 once and each private leaf once.
- **Integrality.** Scaling private leaf 1 (both its A and S parts) by λ ≠ 0 multiplies T_B by λ. So f_B is rational, hence an
  integer.
- **Evenness.** Negating d negates T_B, so f(−d) = f̄(d). Negating all three private leaves negates T_B, so f_B is real.
- **The constant.** As in `BEYOND-CLASS2-20261027-001C` Lemma 6.1, the constant in front of T_B does not matter. ∎

**Lemma 5.2.** Suppose B ≠ 0, and let s* ∈ (𝔫⁻)^* with ⟨B(·, ·, ·), s*⟩ ≢ 0. Then 0 < f_B(0, s*) < f_B(0).

*Proof.*
- **Only j = 0 survives.** At d* = (0, s*), only the terms with leaf 0 in the S position survive, namely j = 0. Indeed every
  W_j⁽³⁾ with j ≠ 0 has leaf 0 among its arguments.
- **The phase.** W₀⁽³⁾ = −[X₁, [X₂, X₃]] (`BEYOND-CLASS2-20261027-001C` part 4, P4). So the phase is
  2⟨[[π₂, π₃], π₁], s*⟩ = 2⟨B(π₂, π₃, π₁), s*⟩, a trilinear form t in the A-parts of the private leaves. The S-parts and leaf 0's
  other entries are free.
- **The sum.** Summing over π₁ gives a count:

  f_B(d*) = p^{3d} · p^{d} · #{(π₂, π₃) ∈ (𝔫⁻)² : t(·, π₂, π₃) = 0} ∈ [p^{4d}, p^{6d}].

  The upper end is attained only if t ≡ 0, which is excluded. ∎

### 6. Hardness

- **The count.** Summing over the private and unused coordinates (each unused one gives p^{2d}),

  |Hom(π₁M_Γ, G)| = 1 + p^{d} · p^{−N_M d} · p^{6md} · Z_f(Γ) = 1 + p^{d(1−n)} Z_f(Γ),  Z_f(Γ) = Σ_{σ: V(Γ) → 𝔫⁻ ⊕ (𝔫⁻)^*} Π_e f_B(σ_v − σ_u).

- **The matrix.** W(σ, σ′) = f_B(σ′ − σ)² is a symmetric non-negative integer matrix. By Lemma 5.2, 0 and d* lie in one
  connected component, with a 2 × 2 minor f(0)⁴ − f(d*)⁴ ≠ 0. So W is not block-rank-1, and EVAL(W) is #P-hard by Bulatov–Grohe.
- **The reduction.** Doubling every edge gives Z_W(Γ) = Z_f(Γ^{(2)}), which one count recovers. This proves Theorem 1, and with
  ticket A, Theorem 2. ∎

### 7. Gaps

- **Class at least 5.** Odd brackets of five −1 elements enter through the degree-5 Lie parts of the conjugators. Earlier
  insertions also interact with later ones in layer 5. The gadget form gains edge-local and vertex-local degree-5 terms, and
  Lemma 5.2 needs a new argument.
- **Non-graded 𝔫.** The polynomial side uses 𝔫's triple system, and hardness uses gr 𝔫's. They agree for graded algebras; a
  non-graded algebra with abelian gr-triple system but nonabelian 𝔫-triple system is not covered.
- p = 2 and p = 3.
- r > 2.
- Manifolds with p-torsion in H₁ (trivial-character classes).
- Knot exteriors.
- No external review.
