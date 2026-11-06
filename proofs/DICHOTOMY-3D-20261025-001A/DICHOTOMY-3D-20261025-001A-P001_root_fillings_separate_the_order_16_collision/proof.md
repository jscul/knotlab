# Root fillings separate the order-16 collision

Status: Proved

## Standard statement

**Setting.**
- Γ is a finite group with an abelian normal subgroup A of prime index p. Fix σ ∈ Γ \ A. Write:
  - pA = {a^p : a ∈ A} and A[p] = {a ∈ A : a^p = e};
  - [B, σ] = {x⁻¹σxσ⁻¹ : x ∈ B} for B = A or pA (a subgroup, since A is abelian);
  - Z = Z(Γ) and Γ′ for the derived subgroup.
- G is a connected plane multigraph with n vertices and m edges, and P(G, q) is its chromatic polynomial.
- M_{G,k} is the closed double of `HARD-3D-20261025-001B` with every edge carrying k fins (Σ₁,₁ × S¹ pieces). In M_{G,k}^root, every
  edge also carries two parallel copies of its curve, Dehn-filled along the slopes λμ^(−p) and λμ^p.

**Theorem 1 (index p).** Let Γ be non-abelian, with A, p and σ as above.
- **(a) Γ acts nontrivially on pA.** Then |Hom(π₁(M_{G,k}^root), Γ)| = Σ_{j=0}^{m} c_j ((|Γ|/p)^{2m} p^{2j})^k, and

  c₀ = |A[p]|^{2m} · |Γ : pA| · |A[p]| · (|L′|/|A|)ⁿ · P(G, q), with q = |[pA, σ]|² ≥ 4 and |L′| = (|pA|/|[pA, σ]|)².
- **(b1) Γ acts trivially on pA and |[A, σ]| = p.** Then, with fins alone, |Hom(π₁(M_{G,k}), Γ)| = Σ_j c_j ((|Γ|/p)^{2m} p^{2j})^k
  and c₀ = (|Z|/|Γ′|)ⁿ · P(G, |Γ : Z|·|Γ′|).
- **(b2) Γ acts trivially on pA, |[A, σ]| = p^i with i ≥ 2, and p ≥ 3.** Then, with fins alone, the coefficient of the smallest base
  (|Γ|/p^i)^{2mk} is |A|ⁿ · P(G, p).

**Corollary 2.** In cases (a), (b1) and (b2), counting homomorphisms from closed orientable 3-manifold groups, given by
triangulations, into Γ is #P-hard under polynomial-time Turing reductions.
- This covers every finite group with an abelian normal subgroup of prime index, except possibly the case p = 2 with trivial action on
  2A and |[A, σ]| ≥ 4.
- In particular:
  - **The dihedral group of order 16:** c₀ = 4^m · 8 · P(G, 4)/2ⁿ.
  - **Every dihedral, semidihedral and generalized quaternion group of order 2N with N = 2^j ≥ 8:** q = N²/16.
  - **The other cases** include every non-abelian group of order p³ (case b1, q = p³), every Z_ℓ ⋊ Z_p with nontrivial action
    (q = ℓ²), A₄ (q = 16) and every dicyclic group of order at least 12.

## Nearest known result

- **Galindo (2026),** [arXiv:2605.06984](https://arxiv.org/abs/2605.06984), Theorem 1.2.
  - Turaev–Viro invariants of a spherical fusion category 𝒜 are #P-hard to evaluate from triangulations unless 𝒜 is trivializable
    pointed.
  - For 𝒜 = Vec_Γ the invariant is |Hom(π₁(M), Γ)|/|Γ|, and Vec_Γ is trivializable pointed only for abelian Γ.
  - So Corollary 2, and its extension to every non-abelian Γ, already follows from that theorem.
  - Galindo's route: graph manifolds over bounded-degree graphs, and the Cai–Govorov dichotomy for the anyon matrix S_ij/(d_i d_j).
- **`HARD-3D-20261025-001B`.**
  - It gives the closed doubles, their presentation and count, the S₃, dihedral, Q₈ and A₄ identities, and the order-16 collision
    256 · 16 = 64².
  - It named that collision as the obstruction. Samperton and Weiß (2026) had listed the order-16 dihedral group as open.
- **What is new here.**
  - The root-filling gadget. It separates the collision because no reflection is a square.
  - The explicit chromatic coefficients of Theorem 1.
  - An elementary route to these hardness results: planar chromatic polynomials and Vandermonde systems, without the general
    graph-homomorphism dichotomy.
- **Novelty.** Hardness is not new. The gadget and the identities are a `candidate-local-delta`, folklore risk medium.

## 1. The model with Dehn fillings

**From `HARD-3D-20261025-001B`** (cited, Proposition 1.3 and Lemma 1.1):
- M_G = (Y \ N(L)) ∪ ⋃ Q_e, with Y = #ⁿ(S¹ × S²).
- Each boundary torus ∂N(γ_e) carries:
  - the surface-framed longitude λ_e, with holonomy y_v⁻¹ y_u;
  - the meridian μ_e, with holonomy s_{f′} s_f⁻¹.
- With every edge repeated, the parallel copies of γ_e bound digons.

**Lemma 1.1 (any pieces).** Glue to the torus of each copy c of each edge a compact piece P_c with torus boundary. Then

  |Hom(π₁(M), Γ)| = Σ_{(y, s)} [cons] Π_c W_{P_c}(λ_c, μ_c),

where W_P(λ, μ) is the number of homomorphisms π₁(P) → Γ restricting to (λ, μ) on the boundary.

*Proof.* Van Kampen for gluing along tori is a pushout. So a homomorphism is a homomorphism of the link complement, enumerated by
(y, s) as in `HARD-3D-20261025-001B`, together with compatible homomorphisms of the pieces. ∎

**The pieces.**
- **The fin** Σ₁,₁ × S¹ has W(λ, μ) = #{(τ, κ) ∈ C(λ)² : [τ, κ] = μ}.
- **Filling a copy along λμ^(−p)** adds the relation λ = μ^p, so W(λ, μ) = [λ = μ^p].
- **The mirror slope λμ^p** gives W(λ, μ) = [λ = μ^(−p)].

**Lemma 1.2 (consistency is commutation).** For y ∈ Γ^V and s ∈ Γ^F with s_{f₀} = e, mirror labels ȳ exist (and are then unique) exactly
when [λ_e, μ_e] = 1 for every edge.

*Proof.*
- **Within a face.** The face relations fix ȳ on the corners of a face f up to a left factor g_f: ȳ_u = g_f s_f⁻¹ y_u s_f.
- **Across an edge.** Across an edge e = uv between faces f and f′, the two descriptions agree on the relative position ȳ_v⁻¹ ȳ_u exactly
  when μ_e = s_{f′} s_f⁻¹ commutes with λ_e. They then determine g_{f′}⁻¹ g_f.
- **Around a vertex.** Around a vertex w with faces f₁, …, f_r, write a_i = s_{f_i}⁻¹ y_w s_{f_i}. The transitions are a_{i+1} a_i⁻¹,
  whose product around w telescopes to e.
- **Conclusion.** Vertex cycles generate the cycle space of the dual graph, so the g_f exist. ∎

**Lemma 1.3 (parallel copies).** Copies of one edge carrying weights W₁, …, W_r collapse to the convolution W₁ * ⋯ * W_r over C(λ).

*Proof.* This is the telescoping argument of `HARD-3D-20261025-001B`, Proposition 2.2. It uses only that each W_i(λ, ·) vanishes off
C(λ), which holds for every piece by Lemma 1.2. ∎

**Lemma 1.4 (channels).**
- **The basis.** Each W(λ, ·) is a class function on C(λ). Expand W = Σ_a f_a w_a over anyons a = ([λ], ψ), ψ ∈ Irr C(λ), with
  w_a(λ, μ) = (ψ(1)/|C(λ)|) ψ(μ), transported to conjugates of λ.
- **Convolution multiplies the factors f_a.** The identity weight [μ = e] has f ≡ 1.
- **The fin** has factor (|C(λ)|/ψ(1))² (Frobenius), which equals (|Γ|/d_a)² with d_a = |[λ]|·ψ(1).
- **The two fillings** have factors s_a = Σ_{τ ∈ C(λ), τ^p = λ} ψ̄(τ)/ψ(1) and its conjugate. Their product is
  ρ_a = |Σ_{τ ∈ C(λ), τ^p = λ} ψ(τ)|²/ψ(1)².
- **Hence**

  |Hom(π₁(M_{G,k}^root), Γ)| = Σ_{(a_e)} Π_e (|Γ|/d_{a_e})^{2k} ρ_{a_e} · T(a), with T(a) = Σ_{(y,s)} Π_e w_{a_e}(λ_e, μ_e). (1)

## 2. Which channels survive

**Lemma 2.1.**
- Every p-th power lies in A, because Γ/A has order p.
- So for λ ∉ A no τ satisfies τ^p = λ, and ρ_a = 0.

**Lemma 2.2 (fluxes in A).** Let λ ∈ A and ψ ∈ Irr C(λ). C(λ) contains A, and ψ lies over a C(λ)-orbit of characters χ of A. The
stabilizer of the pair (λ, χ) in Γ contains A and has prime index, so it is A or Γ.
- **Fixed pair (stabilizer Γ).** λ is central and χ is Γ-invariant. Since Γ/A is cyclic, χ extends, so ψ is linear and d_a = 1.
- **Free pair (stabilizer A).** Then d_a = p and ψ = Ind_A^{C(λ)} χ.
  - If λ is central, χ has orbit size p and ψ = Ind_A^Γ χ has degree p.
  - Otherwise C(λ) = A, |[λ]| = p and ψ = χ.

**Lemma 2.3 (root factors of free pairs).** For a free pair, ρ_a = |A[p]|² when λ ∈ pA and χ is trivial on A[p], and ρ_a = 0 otherwise.

*Proof.*
- **Only roots in A count.** ψ = Ind_A^{C(λ)} χ vanishes off A, so only roots τ ∈ A count. They form τ₀·A[p] when λ = τ₀^p, and none
  exist when λ ∉ pA.
- **The sum.** With ψ|_A = Σ_{χ′ ∈ O} χ′ we get Σ_{a ∈ A[p]} χ′(τ₀ a) = |A[p]|·χ′(τ₀)·[χ′ trivial on A[p]].
- **Equal values.** A[p] is characteristic, so the bracket is the same for all of O. Each χ′ = χ ∘ c⁻¹ with c ∈ C(λ). The element
  c⁻¹ τ₀ c is another p-th root of λ in A, so χ′(τ₀) = χ(τ₀).
- **Conclusion.** The sum is |O|·|A[p]|·χ(τ₀), and |O| = ψ(1). ∎

**Consequence for case (a).**
- **The survivors.** The channels with ρ_a ≠ 0 have flux in A and dimension 1 or p. Those of dimension p are the free pairs lying in
  X = W \ L′, where:
  - W = pA × Ann(A[p]);
  - L′ = (pA ∩ Z) × (Ann(A[p]) ∩ Â^Γ) is the subgroup of fixed pairs in W.
- **The bases.** Their fin factors are |Γ|² and (|Γ|/p)². The bases in (1) are (|Γ|/p)^{2m} p^{2j}, where j counts one-dimensional
  edges. They are distinct for distinct j.
- **The coefficient c₀** is |A[p]|^{2m} T_X, where T_X sums over all edges in channels of X.

## 3. The top coefficient

**Lemma 3.1 (Clifford sum).** For λ ∈ A and a C(λ)-orbit O ⊂ Â:

  Σ_{ψ over O} (ψ(1)/|C(λ)|) ψ(μ) = [μ ∈ A] (1/|A|) Σ_{χ ∈ O} χ(μ).

*Proof.* Σ_ψ ψ(1)ψ = |O|·Ind_A^{C(λ)} χ, and the induced character vanishes off A. On A it equals (|C(λ) : A|/|O|) Σ_{χ′ ∈ O} χ′. ∎

**Lemma 3.2 (reduction to A).** Let X ⊂ A × Â be invariant under Γ and under negating either coordinate. Then

  T_X = |Γ : A| · |A|^{F−1−m} · |A|⁻¹ · #{(c, φ) ∈ (A × Â)^V : (c_u − c_v, φ_u − φ_v) ∈ X for every edge}.

*Proof.*
- **The weight.** By Lemma 3.1 the weight is [λ ∈ A][μ ∈ A](1/|A|) Σ_{χ ∈ X_λ} χ(μ).
- **One coset.** Nonzero terms put all y in one left coset gA (|Γ : A| choices), with y_u = g c_u and λ_e = c_u − c_v. They put every
  s_f in A.
- **Characters as tensions.** Expand the product over the edges into characters χ_e. Summing over the face variables gives |A|^{F−1}
  times the condition that χ has trivial product around every bounded face. The face boundaries span the cycle space, so χ is a
  tension χ_e = φ_u − φ_v, with φ unique up to |A| constants.
- **Orientation.** The orientation convention is immaterial, by the symmetry of X. ∎

**Lemma 3.3.** For X = W \ L′ with L′ ⊂ W ⊂ A × Â subgroups, the count in Lemma 3.2 is

  |A : pA| · |A[p]| · |L′|ⁿ · P(G, |W|/|L′|).

*Proof.* (c, φ) lies in one coset of W; there are |A × Â : W| = |A : pA| · |A[p]| choices. Within it, colour vertices by cosets of L′. ∎

**Lemma 3.4.** |L′| = (|pA|/|[pA, σ]|)², and q = |W|/|L′| = |[pA, σ]|².

*Proof.*
- **The flux part.** x ↦ x⁻¹σxσ⁻¹ is a homomorphism of pA with kernel C_{pA}(σ) = pA ∩ Z and image [pA, σ].
- **The charge part.** x ↦ x^p maps A/A[p] onto pA, commuting with σ, so Ann(A[p]) ≅ (pA)^ equivariantly. Its σ-invariant
  characters are those trivial on [pA, σ].
- **Sizes.** Both parts have |pA|/|[pA, σ]| elements, and |W| = |pA|². ∎

**Proof of Theorem 1(a).** Combine (1), Lemmas 2.1–2.3 and Lemmas 3.2–3.4, using F − 1 − m = 1 − n:
- c₀ = |A[p]|^{2m} · |Γ : A| · |A|^{−n} · |A : pA| · |A[p]| · |L′|ⁿ · P(G, q);
- this is the stated formula, since |Γ : A|·|A : pA| = |Γ : pA|;
- q ≥ 4 because the action on pA is nontrivial. ∎

## 4. The trivial-action cases

**Common facts.**
- **Z ⊂ A.** Otherwise Γ = AZ would be abelian.
- **Index.** |[A, σ]| = |A : A ∩ Z|, because the kernel of x ↦ x⁻¹σxσ⁻¹ on A is C_A(σ) = A ∩ Z.
- **Exponent.** p[A, σ] = [pA, σ] = 1, so [A, σ] has exponent p.
- **Fluxes outside A.** For λ ∉ A, C(λ) = (A ∩ Z)⟨λ⟩ is abelian and |[λ]| = |A : A ∩ Z|. So every anyon with flux outside A has
  dimension |[A, σ]|.
- **Fluxes in A** have dimension 1 or p (Lemma 2.2).

**(b1) |[A, σ]| = p.**
- **One dimension.** Every non-abelian anyon has dimension p. So the fin bases are (|Γ|/p)^{2m} p^{2j}, and c₀ sums over all edges in
  non-abelian channels.
- **The weight.** The sum of all channels is [μ = e]. The abelian anyons (z, χ), with z central and χ linear, sum to
  [λ ∈ Z][μ ∈ Γ′]/|Γ′|.
- **Expansion.** Expand Π_e ([μ_e = e] − [λ_e ∈ Z][μ_e ∈ Γ′]/|Γ′|) over the set E′ of edges taking the second term:
  - **Vertex labels.** They are constant modulo Z on the components of (V, E′), giving |Γ|^{k(E′)} |Z|^{n−k(E′)}.
  - **Face labels.** They lie in Γ′ and are constant across E \ E′, giving |Γ′|^{|E′|−n+k(E′)}.
- **The sum.** It is (|Z|/|Γ′|)ⁿ Σ_{E′} (−1)^{|E′|} (|Γ : Z|·|Γ′|)^{k(E′)} = (|Z|/|Γ′|)ⁿ P(G, |Γ : Z|·|Γ′|).
- **The number of colours.** q ≥ 8, since |Γ : Z| ≥ 4 and |Γ′| ≥ 2.

**(b2) |[A, σ]| = p^i ≥ p², p ≥ 3.**
- **The smallest base.** The anyons of largest dimension p^i are exactly those with flux outside A, with any charge. The smallest
  base (|Γ|/p^i)^{2mk} arises only when every edge is in such a channel.
- **The weight.** Their weight is [λ ∉ A][μ = e], by orthogonality.
- **The count.** It is #{y : y_u A ≠ y_v A on every edge} = |A|ⁿ P(G, p).

**The excluded case.** p = 2, trivial action on 2A, |[A, σ]| ≥ 4.
- **Fins alone.** The free pairs collide with products of abelian and outside-A channels, and the outside-A sector has q = 2.
- **Square-root fillings** kill every free pair, since 2A is central.
- **Not treated here.** Groups such as V₄ ≀ Z₂ fall here; Galindo's theorem covers them.

## 5. Hardness

**Proof of Corollary 2.**
- **The source problem.** For a connected plane graph G, computing P(G, q) is #P-hard for every q ∉ {0, 1, 2} (Vertigan 2005, cited).
- **The reduction.**
  - Build triangulations of M_{G,k}^root, or M_{G,k}, for k = 0, …, K. Here K + 1 is the number of distinct bases: m + 1 in cases
    (a) and (b1), at most 2m + 1 in case (b2) when i = 2, and polynomial in m in general.
  - Query the oracle and solve the Vandermonde system.
  - Divide c₀ by its known factor.
- **Sizes and membership.** Sizes are polynomial; triangulating the explicit description is standard, as in `HARD-3D-20261025-001B`.
  Membership in #P is as there.

**The families.**
- **Dihedral, semidihedral, generalized quaternion.**
  - In D_{2N}, SD_{2N} and the generalized quaternion group Q_{2N} with N = 2^j ≥ 8, take A cyclic of order N.
  - σ acts on pA = ⟨r²⟩ by inversion. In SD_{2N}, r² ↦ r^{2(N/2−1)} = r^{−2}.
  - So [pA, σ] = ⟨r⁴⟩ has order N/4, and q = N²/16.
- **Groups of order p³.** A non-abelian group of order p³ has an abelian A of index p with [A, σ] = Γ′ = Z of order p, and σ trivial on
  pA. So it is case (b1), with q = p²·p.
- **Z_ℓ ⋊ Z_p and A₄.** For Z_ℓ ⋊ Z_p and for A₄ = V₄ ⋊ Z₃, multiplication by p is invertible on A, so pA = A and the action is
  nontrivial: case (a).
- **Dicyclic groups.** In a dicyclic group of order 4n, with A = ⟨a⟩ of order 2n, [pA, σ] = ⟨a⁴⟩, which is nontrivial for n ≥ 3.

## 6. How the order-16 collision is separated

**With fins alone**, the order-16 dihedral group has channel factors:
- 256 (dimension 1);
- 64 (dimension 2: rotations, and the degree-2 characters on central fluxes);
- 16 (reflections).

Since 64² = 256 · 16, the coefficient of 64^{mk} mixes the target with pairs of a dimension-1 edge and a reflection edge.

**With the doubled square-root filling**, the reflection channels vanish, since no reflection is a square. The bases are then products
of 64 and 256 only, 64^m · 4^j, and they are distinct. The surviving dimension-2 channels are:
- the flux pairs (r², χ) with χ even;
- (e, ψ₂) and (r⁴, ψ₂).

Each has factor 4, and they form X = (⟨r²⟩ × Ann(A[2])) \ L′ with |L′| = 4. That gives 4^m · 8 · P(G, 4)/2ⁿ.

## Check

`check.py` uses the standard library only, plus the propagation code of `HARD-3D-20261025-001B` loaded by path. It runs in about 14 s,
and its output is `result.json`.

1. **The model.**
   - Mirror-label consistency equals per-edge commutation, as sets of configurations, for S₃ and the order-8 dihedral group on seven
     plane graphs.
   - Thickened graphs whose copies carry different gadgets match the collapsed convolution:
     - S₃ on the path with fin, + and − copies: 124416;
     - the order-16 dihedral group on one edge with the same three copies: 47104;
     - the order-8 dihedral group on the triangle with fin and + copies: 12582912.
2. **Case (a).**
   - Closed counts with k fins and one doubled root filling per edge are fitted in k by the predicted bases. Each fit has two extra
     values, and both are reproduced.
   - The top coefficient equals Theorem 1(a) exactly, for:
     - the order-16 dihedral group, on seven graphs (C₄: 10752 = 4⁴ · 8 · P(C₄, 4)/2⁴);
     - Q₁₆ and SD₁₆ (q = 4) and the order-32 dihedral group (q = 16), on five graphs each;
     - Z₃ ⋊ Z₄ (q = 9), on six graphs;
     - Z₇ ⋊ Z₃ (q = 49), on five graphs;
     - A₄ with cube-root fillings (q = 16), on six graphs.
3. **Cases (b1) and (b2), fins alone.**
   - The order-8 dihedral group on seven graphs, including K₄, and the modular group of order 16 on five: q = 8.
   - Z₃ ≀ Z₃, case (b2), on four graphs: q = 3, with coefficient 27ⁿ P(G, 3).
4. **Index-p data.** Abelian, normal and index p are asserted for each A. The case of each group, and q = 4, 4, 4, 16 for the order-16
   dihedral, Q₁₆, SD₁₆ and order-32 dihedral groups, are computed from the group tables.
5. **Controls.**
   - **Without root fillings**, the order-16 coefficient of 64^{4k} on C₄ is 6522, not the identity's 6330. This reproduces the
     collision of `HARD-3D-20261025-001B`.
   - **A doubled cube-root filling**, of order coprime to 16, gives counts identical to fins alone.
   - **A single, undoubled square-root filling** gives top coefficient 96, not 2⁴ times the identity (672).
   - **The wrong number of colours**, q = 16, is rejected.

## Scope

- **Covered.** Closed orientable 3-manifolds obtained from the doubles of `HARD-3D-20261025-001B` by Dehn filling parallel copies of the
  edge curves.
- **Kind of reduction.** Turing reductions by interpolation, on instances whose first Betti number grows with the graph.
- **Cited, not proved.** Planar colouring hardness and polynomial-time triangulation.
- **Not new.** The hardness itself follows from Galindo (2026), cited.
- **No overclaim.** No claim about P versus NP, approximation, parsimony or bounded homology.
