# Triple failures at every sector order: the corrected and expanded hardness proof

Status: Proved

This is the successor of `COPRIME-DICHOTOMY-20261027-001C-P001`, which stays frozen. It answers the independent review
`research/COPRIME-DICHOTOMY-20261027-001/codex_review_20261027.md` (an AI review with finite V2 checks, not human expert review or
formal verification).

**What changed from the predecessor.**

| item | predecessor | here |
| --- | --- | --- |
| parity language | "the action collapses to an involution" | (P2_d) supplies a compatible **parity automorphism** θ_d; the action itself need not factor through C₂ (§1, Remark) |
| Fox normalization | "Fox matrix I − Bur_t" | the literal matrix is t⁻¹(Bur_t − I), with the same column space (Lemma 3.0) |
| cable homomorphism | exponent ψ(g) | the integer abelianization u: π_T → Z; θ′ = τ^k may have any order (Lemma 4.3) |
| edge-weight lemma | "independent of the constants κ_t" | removed; Lemma 7.2 uses the actual coefficients |
| amphichiral class-4 argument | sketched | canonical pinned coordinates and the symmetry action written out (Lemmas 4.0, 4.2) |
| reading strands | asserted basis | Lemmas 6.1–6.2: cable colourings are bundle constants; two-partition lemma and conjugation for amphichiral summands |
| references | names | precise references (§10) |

The main theorem is unchanged.

## Standard statement

**Setting.**
- p ≥ 5 is prime, r | p − 1, and ζ ∈ F_p^× has order r.
- 𝔫 = L₁ ⊕ ⋯ ⊕ L_c is graded nilpotent over F_p, c ≤ 4. C_r = ⟨σ⟩ acts by automorphisms preserving the grading, and 𝔫_j
  (j mod r) is the ζ^j-eigenspace of σ. N = exp(𝔫) (Lazard [La], [Kh]) and G = N ⋊ C_r.
- For d | r: 𝔤_α = 𝔫^{(d)}_α (α mod d), and the criterion of `COPRIME-DICHOTOMY-20261027-001A`:
  - (P2_d) [𝔤_α, 𝔤_β] = 0 whenever α, β and α + β are nonzero;
  - (P3_d) [[𝔤_α, 𝔤_{−α}], 𝔤_β] = 0 for nonzero α, β.
- **Odd and even.** Components of nonzero character are *odd*; 𝔤₀ is *even*.
- **Manifolds.** M = S³_{d/p}(K) for knot diagrams K, with H₁(M) = Z/d and H₁(M; F_p) = 0.

**Lemma 1 (only near triples).** Under (P2_d): [[𝔤_α, 𝔤_{−α}], 𝔤_β] = 0 whenever β ≢ ±α. So under (P2_d), (P3_d) fails iff some
near triple [[𝔤_a, 𝔤_{−a}], 𝔤_{±a}] is nonzero.

**Theorem 2 (hardness at every sector order).** If d | r, (P2_d) holds and (P3_d) fails, then counting |Hom(π₁ S³_{d/p}(K), G)|
over knot diagrams K is #P-hard under polynomial-time Turing reductions, for each fixed G. For d = 2 this is
`TRIPLE-SYSTEM-20261027-001C`; the proof below treats every d.

**Corollary 3 (the dichotomy and its remaining case).**
- **Scope.** Fix a divisor-closed set 𝒟 of divisors of r. Consider closed oriented 3-manifolds M with H₁(M; F_p) = 0, boundedly
  many sectors ψ ∈ Hom(H₁(M), C_r), and sector orders in 𝒟.
- **Polynomial** if the criterion holds at every d ∈ 𝒟 (`COPRIME-DICHOTOMY-20261027-001A`).
- **Hard** if, for some d ∈ 𝒟, the criterion fails and either (P2_d) holds (Theorem 2) or 𝔫 has class 2
  (`CLASSK-DICHOTOMY-20261026-001C`, on S³_d(K) with G_d = N ⋊ C_d).
- **Remaining case.** 𝔫 of class 3 or 4 for which (P2_d) fails at every d ∈ 𝒟 where the criterion fails.

## Proof

τ ∈ C_r has order d, ζ_d = ζ^{r/d}, and τ acts on 𝔤_α by ζ_d^α. A value t ∈ F_p^× also names the local system F^t with the
meridian acting by t. Cochains follow the left convention c(gh) = c(g) + χ(g) c(h).

### 1. Lemma 1, parity, and the parity automorphism

*Proof of Lemma 1.* [[x, y], w] = [x, [y, w]] − [y, [x, w]]. Both inner brackets vanish by (P2_d) when β ≢ ±α. ∎

**Lemma 1′ (parity).** Under (P2_d), a nonzero Lie monomial in odd elements has even character iff its degree is even.

*Proof.* Induct on [P, Q]. If both have odd degree, their nonzero characters must sum to 0. ∎

**Remark (parity automorphism, not a collapse).**
- (P2_d) is equivalent to θ_d (+1 on 𝔤₀, −1 on odd components) being a Lie automorphism (`COPRIME-DICHOTOMY-20261027-001A`,
  Lemma 1). θ_d commutes with the C_r action.
- The C_d action is unchanged. Example: a one-dimensional abelian algebra over F₇ with an order-3 scalar action satisfies (P2)
  and (P3), and its action still has order 3.
- Only the bracket structure behaves as for an involution.

### 2. Pinning at slope d/p

**Lemma 2.1.** For M = S³_{d/p}(K),

  |Hom(π₁M, G)| = Σ_{e ∈ (r/d)Z/rZ} p^{dim 𝔫 − dim 𝔫^{σ^e}} P_{σ^e}(K),  P_υ(K) = #{ρ: π_K → G : ρ(μ) = υ}.

*Proof.*
- **Only μ^d remains.** ρ(λ) ∈ N has order dividing p, so the relator μ^d λ^p only imposes ρ(μ)^d = 1.
- **Conjugacy.** An element of Nσ^e of order dividing d generates a complement to N in N⟨σ^e⟩, so it is N-conjugate to σ^e by
  Schur–Zassenhaus ([Go, Thm 6.2.1]).
- **Centralizers.** C_N(σ^e) = exp(𝔫^{σ^e}), since Lazard's correspondence is equivariant. ∎

**Lemma 2.2.**
- π_{K₁#K₂} = π_{K₁} ∗_{⟨μ⟩} π_{K₂}, so P_υ(K₁ # K₂) = P_υ(K₁) P_υ(K₂).
- P_υ(unknot) = 1, and P_υ(K) ≥ 1 (via π_K → Z). ∎

### 3. The pinned layered count; Fox normalization; Squier duality

**The layered count.**
- Pinned lifts through L_k form torsors under the relative cocycles {c : c(μ) = 0}. These are ≅ H¹(X; F^t) at nontrivial
  characters, and 0 at the trivial character, since u(μ) = 1 for the generator u of H¹(X; F_p).
- Obstructions lie in H²(X, μ; F^t), which is ≅ H²(X; F^t) for t ≠ 1 and 0 for t = 1.
- So P_τ(K) = #{ξ : o(ξ) = 0}, with ξ ∈ ⊕ V_α ⊗ L_{k,α}, α ≢ 0, and V_α = H¹(X; F^{ζ_d^α}).

**Fox colours.** For a closed braid β on n strands, the colour of an arc is its cocycle value. The letters act by:
- g > 0: (s_i, s_{i+1}) ↦ ((1 − t⁻¹)s_i + t⁻¹s_{i+1}, s_i);
- g < 0: (s_i, s_{i+1}) ↦ (s_{i+1}, t s_i + (1 − t)s_{i+1}).

Bur_t(β) is their product. Cocycles are the vectors fixed by Bur_t(β), and coboundaries are the constant vectors 𝟙.

**Lemma 3.0 (Fox normalization).** For the closure relators R_j = x_j⁻¹ β(x)_j, the literal Fox matrix under the left convention is
t⁻¹(Bur_t(β) − I). Its column space and left kernel equal those of I − Bur_t(β).

*Proof.*
- c(R_j) = c(x_j⁻¹) + t⁻¹ c(β(x)_j) = t⁻¹(c(β(x)_j) − c(x_j)), and c(β(x)_j) = (Bur_t(β)s)_j.
- The scalar −t⁻¹ is invertible.
- Pinning x₀ removes one column without changing the column space, since 𝟙 lies in the kernel. ∎

The obstruction test (o lies in the column space) and the steering computation of §5 use only the column space and the actual
relator values. So κ_t below is unaffected. The independent literal-matrix review confirms the coefficient.

**Lemma 3.1 (Squier form, [Sq]).** Let J_t be lower unitriangular with (J_t)_{qq′} = (t − 1)t^{q−q′−1} for q > q′. Then
Bur_{t⁻¹}(g)^T J_t Bur_t(g) = J_t for every letter. Also J_t^T 𝟙 = (t^{n−1−q})_q, and if t^d = 1 ≠ t, then
Σ_{i<d} (J_t^T s)_{o+i} = Σ_{i<d} t^i s_{o+i}.

*Proof.*
- The invariance is checked directly: symbolically in Z[t, t⁻¹] for n ≤ 7, and modulo p for n ≤ 12; it is a local identity in two
  rows and columns.
- The bundle identity telescopes from (J_t^T s)_q − t(J_t^T s)_{q+1} = s_q − s_{q+1}, since 1 + ⋯ + t^{d−1} = 0. ∎

**Lemma 3.2 (left kernel).** A central obstruction vector o at character t ≠ 1 lies in the column space iff ⟨o, J_t^T s⟩ = 0 for
all s ∈ Fix Bur_{t⁻¹}(β). Moreover ⟨o, J_t^T 𝟙⟩ = 0 always.

*Proof.*
- **Left-kernel vectors.** J_t^T s are left-kernel vectors (Lemma 3.1).
- **Dimensions.** They fill the kernel, since dim H¹(X; F^t) = dim H²(X; F^t) = dim H¹(X; F^{t⁻¹}), by the Euler characteristic and
  Lefschetz duality with local coefficients ([Wa, Ch. 2], [Ha, §3.H]).
- **The reversed Artin identity.** A positive letter maps (a, b) ↦ (a⁻¹ba, a), which preserves the reverse product ba (Artin
  [Ar]; [Bi, Ch. 1]). With P_j = x_{n−1} ⋯ x_j this gives Π_{j = n−1, …, 0} P_j R_j P_j⁻¹ = 1 in the free group.
- **Its coefficients** are t^{n−j} = t · (J_t^T 𝟙)_j, so ⟨o, J_t^T 𝟙⟩ = 0. ∎

**The Fourier form.** P_τ(K) = p^{−D} Σ_{ξ, s} ω^{Q(ξ; s)}, with Q(ξ; s) = Σ ⟨o_{k,α}(ξ), J^T s_{k,α}⟩ extended polynomially.

### 4. Summands without local forms

**Lemma 4.0 (canonical pinned coordinates).** Let K be a knot, τ of order d, (P2_d), and c ≤ 4. Write a pinned
homomorphism as ρ(g) = exp(Σ_k v_k(g)) τ^{ψ(g)}, with v_k(g) ∈ L_k (a graded splitting, so canonical).
- (a) v₁ is odd, and is a pinned cocycle. The even part of v₁ vanishes: it is a pinned trivial-character cocycle.
- (b) The odd part v₂^odd is a pinned cocycle. The even part v₂^ev is the unique pinned solution of δv₂^ev = D₂(v₁).
- (c) v₃^ev is the unique pinned solution of δv₃^ev = D₃^ev(v₁, v₂). The odd part v₃^odd exists iff the layer-3 obstruction
  vanishes.
- (d) The odd part D₄^odd of the layer-4 defect does not involve v₃^odd.

Hence:
- **Canonical coordinates.** The odd obstructions of layers 3 and 4 are well-defined polynomial functions of
  ξ = (v₁, v₂^odd) ∈ Z¹_pin ⊗ (L₁^odd ⊕ L₂^odd).
- **Naturality.** Every automorphism φ of π_K with φ(μ) = μ acts on ξ by precomposition, ξ ↦ ξ ∘ φ, linearly, and
  ob(ξ ∘ φ) = φ^* ob(ξ).

*Proof.*
- **The defects.** The defects D_k are universal polynomial expressions in lower cochains (from the BCH group law). The twisted
  cup-brackets and differentials are natural under precomposition by automorphisms preserving every character, as φ does.
- **(a), (b).** D₂(v₁) = −½ [v₁ ⌣ v₁]. Its odd part is a sum of [odd, odd] brackets, which are even by (P2_d), so δv₂^odd = 0. The
  even parts are unique because H¹(X, μ; F_p) = H²(X, μ; F_p) = 0.
- **(c)** is the same uniqueness.
- **(d).** v₃^odd enters layer 4 only through [v₁, v₃^odd], which is a bracket of two odd elements, hence even (Lemma 1′).
- **Uniqueness gives naturality.** v₂^ev(ξ ∘ φ) = v₂^ev(ξ) ∘ φ and v₃^ev(ξ ∘ φ) = v₃^ev(ξ) ∘ φ. So D_k(ξ ∘ φ) = φ^* D_k(ξ) as
  cochains, and the obstruction classes correspond. ∎

**Lemma 4.1 (the u-pairing).** Let t₀ ≠ ±1 be a simple root of Δ_K mod p, and V_± = H¹(X; F^{t₀^{±1}}). Then V_± are
one-dimensional, and P(c₊, c₋) = ⟨u ⌣ c₊ ⌣ c₋, [X, ∂X]⟩ is a perfect pairing V₊ × V₋ → F_p.

*Proof.*
- **Universal coefficients.** Over Λ = F_p[t^{±1}] ([Le], [Hi, Ch. 2–3]), H¹(X; M) ≅ Hom_Λ(A, M) for every Λ-module M on which
  t − 1 is invertible. Here A is the F_p-Alexander module, and H₀(X̃) = Λ/(t − 1).
- **One-dimensional.** At a simple root the (t − t₀)-primary part of A is Λ/(t − t₀). So V₊ is one-dimensional, and V₋ likewise
  at t₀⁻¹.
- **The connecting map.** u ⌣ (−): H¹(X; F^{t₀}) → H²(X; F^{t₀}) is, up to a nonzero scalar, the connecting map of
  0 → F^{t₀} → E → F^{t₀} → 0, with E = Λ/(t − t₀)² and extension class u. The comparison
  Hom_Λ(Λ/(t − t₀), E) → Hom_Λ(Λ/(t − t₀), E/(t − t₀)E) is zero, because the (t − t₀)-torsion of E is (t − t₀)E. So the
  connecting map is injective, hence bijective.
- **Duality** then makes P perfect. Here c₋ is read in H¹(X, ∂X; F^{t₀⁻¹}) ≅ H¹(X; F^{t₀⁻¹}), an isomorphism because ∂X is
  F^t-acyclic for t ≠ 1, so the triple product lies in H³(X, ∂X; F_p) ≅ F_p. The obstruction pairings of Lemma 4.2 are read the
  same way. ∎

**Lemma 4.2 (negative amphichiral summands; odd orders).** Let K be negative amphichiral: an orientation-reversing homeomorphism
h of S³ with h(K) = K reverses the orientation of K, so h(μ) is conjugate to μ. Let t₀ ≠ ±1 be a simple root of Δ_K mod p, and
R = {α : ζ_d^α ∈ {t₀^{±1}}}. Under (P2_d) and c ≤ 4, every class datum at R lifts.

*Proof.*
- **The automorphism.** Let φ = c_{g⁻¹} ∘ h_*, with h_*(μ) = g μ g⁻¹, so φ(μ) = μ.
- **Scalars.** φ preserves each character, so φ^* acts on the one-dimensional V_± by scalars ε₊ and ε₋.
- **Their product.** Inner automorphisms act on H^*(π; F^χ) by scalars and trivially on products of trivial total character, h
  reverses [X, ∂X], and φ^* u = u. So the perfect pairing P of Lemma 4.1 gives P(φ^*c₊, φ^*c₋) = −P(c₊, c₋), hence ε₊ε₋ = −1.
- **The pairing.** By induction suppose all data lift through layer k − 1 (k = 3, 4). By Lemma 4.0, L(ξ, s) = ⟨ob_k(ξ) ⌣ s,
  [X, ∂X]⟩ is a polynomial in the canonical coordinates ξ = (ξ₊, ξ₋), linear in the dual s. It satisfies
  L(ξ ∘ φ, φ^* s) = −L(ξ, s).
- **(2,2)-balance.** Each monomial of ob_k at character a has three data factors with characters summing to a.
  - By (P2_d) and Lemma 1′, a nonzero Lie part needs two factors from V₊ and one from V₋ (shape [[𝔤_a, 𝔤_{−a}], 𝔤_a]).
  - The shapes (3, 0) and (0, 3) would need [𝔤_{±a}, 𝔤_{±a}] ≠ 0, excluded since 2a ≢ 0.
  - Symmetrically at −a. With the dual factor, every monomial uses V₊ twice and V₋ twice.
  - The canonical even parts v₂^ev and v₃^ev are polynomials of bidegree (1,1), and (1,1) or (2,1) and (1,2) as their characters
    require. They obey the same count.
- **Vanishing.** So L(ξ ∘ φ, φ^* s) = (ε₊ε₋)² L(ξ, s) = L(ξ, s), hence L = 0. By perfect duality, ob_k = 0. ∎

**Lemma 4.3 (cable summands; even orders).** Let k ≥ 1, and let C_k = (k-cable of σ₁^p) · δ_k^{1−kp}, with δ_k = σ₁ ⋯ σ_{k−1} on
the first bundle. This is the (k,1)-cable of T(2, p), and C₁ = T(2, p).
- (i) **Spectrum.** For t with t^k = −1, Bur_t(δ_k) acts on F^k/𝟙 with eigenvalues t⁻¹ω, ω running over the nontrivial k-th roots
  of unity. In particular no eigenvalue is 1.
- (ii) **Colourings.** Fix Bur_t(C_k) = {(a𝟙, b𝟙)}: colourings constant on each bundle. So dim H¹(X_C; F^t) = 1 at every t with
  t^k = −1, and the class is the bundle jump b − a, the same pattern at every such t. At t ≠ 1 with t^k ≠ −1 the twisted
  cohomology vanishes.
- (iii) **Unobstructed.** For every 𝔫 (any class c < p, no condition on brackets) and τ of order d, C_k is unobstructed at
  R = {α : ζ_d^{αk} = −1}.

*Proof.*
- **(i) The matrix.** δ_k moves strand 0 over the others to the end. Strand i (i ≥ 1) moves left with colour
  (1 − t⁻¹)s₀ + t⁻¹s_i. In the coordinates e_i = s_i − s₀ modulo constants, this is t⁻¹C, with
  C(e₁, …, e_{k−1}) = (e₂ − e₁, …, e_{k−1} − e₁, −e₁): the action of the k-cycle on the augmentation quotient. Its eigenvalues are the
  nontrivial k-th roots of unity. And t⁻¹ω = 1 would force t^k = 1.
- **(ii) A positive fat crossing.** Bundle colours (U_L, U_R) go to (U_R′, U_L), where the under-bundle's strands are conjugated by
  the over-bundle's product Y, with χ(Y) = t^k = −1:

  c(Y⁻¹zY) = t^{−k}c(z) + t^{−k}(t − 1)c(Y) = −c(z) + (1 − t)c(Y).

  - **Patterns.** Patterns (colours modulo constants) therefore transform by (P_L, P_R) ↦ (−P_R, P_L).
  - **After p crossings** (p odd): (P_L, P_R) ↦ (−1)^{(p−1)/2}(−P_R, P_L).
  - **Fixed patterns.** Let D̄ be the action of δ_k^{1−kp} on bundle-1 patterns. A fixed pattern needs D̄P_L = −P_L. By (i), D̄ has
    eigenvalues (t⁻¹ω)^{1−kp} = −t⁻¹ω (using t^k = −1 and p odd). These equal −1 only if t = ω, which t^k = −1 excludes. So all
    patterns vanish.
  - **Constants.** For constant bundles, c(Y) = 2a/(1 − t), and a crossing acts by (a, b) ↦ (2a − b, a): the Burau matrix of T(2, p)
    at −1. It is unipotent, so its p-th power is the identity mod p, and the twist fixes constant bundles. Hence
    Fix = {(a𝟙, b𝟙)}.
  - **Elsewhere.** By the satellite formula ([Se], [Li, Ch. 6]; the pattern is unknotted in S³),
    Δ_{C_k}(t) = Δ_{T(2,p)}(t^k) ≡ (t^k + 1)^{p−1} (mod p). So at t ≠ 1 with t^k ≠ −1, Δ_{C_k}(t) ≠ 0 and only constants are
    fixed.
- **(iii) The decomposition.** X_C = X_T ∪_{T²} S, with S the cable space: the mapping torus of the k-punctured disc D_k with
  monodromy δ_k, and π₁S = ⟨a₁, …, a_k, c | c a_i c⁻¹ = δ_k(a_i)⟩, μ_T = a₁ ⋯ a_k, λ_T = c.
- **(iii) Acyclicity.** At t^k = −1 the torus is F^t-acyclic (μ_T ↦ t^k ≠ 1). S is F^t-acyclic too: by the Wang sequence its
  cohomology is the kernel and cokernel of Bur_t(δ_k) − 1 on H¹(D_k; F^t) = F^k/𝟙, which is invertible by (i).
- **(iii) The integer-exponent homomorphism.** Let θ′ = τ^k; it acts by −1 on U = ⊕_{α ∈ R} 𝔤_α. Let u: π_T → Z be the
  abelianization, c a cocycle for the sign character g ↦ (−1)^{u(g)} with c(μ_T) = 0, and A ∈ U. Then

  ρ₀(g) = exp(c(g)A) θ′^{u(g)}

  is a homomorphism. Indeed θ′^{m}(A) = (−1)^m A for every integer m, so
  ρ₀(g)ρ₀(h) = exp((c(g) + (−1)^{u(g)}c(h))A) θ′^{u(g)+u(h)} = ρ₀(gh).
  - **Order of θ′.** θ′ need not have order 2: for d = 12 and a character of order 4, k = 2 and θ′ has order 6. A mod-2 exponent
    would not define a homomorphism.
  - **Meridian and longitude.** ρ₀(μ_T) = θ′, and ρ₀(λ_T) = 1, because λ_T ∈ π″ and c restricted to the kernel of the sign is a
    homomorphism.
- **(iii) Gluing.** ρ_S(a_i) = τ and ρ_S(c) = 1 satisfy the cable-space relations, since each δ_k(a_i) is a conjugate of some a_j by a
  word in the a's. ρ_S agrees with ρ₀ on the boundary torus: μ_T ↦ τ^k and λ_T ↦ 1. So ρ = ρ₀ ∪ ρ_S is a homomorphism π_{C_k} → G
  with ρ(μ_C) = τ.
- **(iii) Every datum.** The restriction H¹(X_C; F^t) → H¹(X_T; F^{−1}) is an isomorphism by Mayer–Vietoris, using the acyclicity.
  Varying the layer-ℓ part of A moves the layer-ℓ lift through the whole pinned torsor (`TRIPLE-SYSTEM-20261027-001C` §2). So every
  class datum at R is realized. ∎

**Lemma 4.4 (existence).** Let t₀ = ζ_d^a ≠ 1.
- **Odd order.** t₀ is a square, and t₀ ≠ t₀⁻¹. Then K_m = b(4m² + 1, 2m), with m ≡ ±√t₀/(t₀ − 1) (mod p), qualifies for
  Lemma 4.2:
  - its Alexander polynomial is −m²(t + t⁻¹) + 2m² + 1, with simple roots exactly t₀^{±1} (since 1/m² = t₀ − 2 + t₀⁻¹), and
    Δ(−1) = 4m² + 1 = (t₀ + 1)²/(t₀ − 1)² ≢ 0;
  - it is negative amphichiral, because (2m)² ≡ −1 (mod 4m² + 1), the mirror image of b(α, β) is b(α, −β), and two-bridge knots
    are invertible ([Sch]; [BZ, Ch. 12]).
- **Even order 2k** (k ≥ 1; k = 1 is t₀ = −1). C_k qualifies for Lemma 4.3, with R = {α : ζ_d^{αk} = −1} ∋ a.

Simple roots of strongly negative amphichiral knots are squares mod p ([HK]), so the even orders need the cables.

### 5. Steering at t

This section is unchanged from the predecessor's §5.
- **Lemma 5.1, the cable.** cable_d(P4) conjugates bundle j by W_j on the reverse-order bundle products. This is checked in the free
  group for d = 2, …, 6.
- **Lemma 5.2, bundle values.** Y_j ∈ N. The leaves are ℓ_j = Σ_i t^{d−1−i}c(z_i). The odd part of log ρ(W_j(Y)) is the Dynkin
  degree-3 part W_j⁽³⁾ ([Re, Thm 1.4]; Magnus expansion [MKS, §5.5]) on the odd layer-1 and layer-2 leaves.
- **Lemma 5.3, the shift.** −(1 − t⁻¹)Λ_t.
- **Lemma 5.4, transport.** By Bur_t.

**Proposition 5.5.** ΔQ = Σ_t κ_t Σ_j ⟨W_j⁽³⁾(ℓ(ξ))_t, ℓ_j(s_t)⟩, with κ_t = t⁻² − t⁻¹.

The proof uses the actual relator values. Each label of bundle j is shifted by (1 − t⁻¹)Λ_j, and the shifts are transported to the
bottom. The closure rows change by o′ − o = −Bur_t(β[ℓ:])Δ. This holds whatever scalar normalizes the Fox matrix (Lemma 3.0), and
the pairing with J_t^T s and the bundle identity give the constant. All corrections are even (Lemma 1′), and pinned even parts are
rigid.

**Corollary 5.6.** Insertions add, cancelling pairs change nothing, and conjugated insertions act with leaves read at the middle
level.

### 6. The gadget, with the reading strands

Fix a near triple at a, t₀ = ζ_d^a, a summand type S (Lemma 4.4) with root characters R ∋ ±a, and a closed-braid representative of S
chosen by the next lemma.

**Lemma 6.1 (reading strands).** Each summand type has a closed-braid representative whose first and last strands receive different
colours under the class at every α ∈ R.

*Proof.*
- **Cables.** The braid C_k of Lemma 4.3 works as it stands. Its first strand lies in bundle 1, its last in bundle 2, and by
  Lemma 4.3(ii) their colours differ by the bundle jump b − a ≠ 0 at every t with t^k = −1.
- **Amphichiral summands**, with R = {t₀, t₀⁻¹}.
  - Take any closed braid of K_m (Alexander's theorem).
  - The class colourings at t₀ and at t₀⁻¹ are non-constant, so each partitions the strands into at least two colour classes.
  - **Two-partition lemma.** Two partitions of a set, each with at least two blocks, admit a pair of points in different blocks of
    both. Suppose not, and take x, y in different blocks of the first partition: they share a block of the second. Take z outside
    that block of the second partition. Then z shares the first-partition block of x and of y, which are different blocks; a
    contradiction.
  - So some strands q′, q have colours differing at both t₀ and t₀⁻¹.
  - **Conjugation.** Let η move q′ to position 0 and q to position n − 1, each as an over-strand, so their colours are preserved.
    Then η⁻¹βη has the same closure, and its top colours are Bur(η) applied to those of β. So its first and last strands carry the
    colours of q′ and q. ∎

**Lemma 6.2 (basis).** In the connected sum of the gadget, at each α ∈ R, V_α is the direct sum of one line per summand copy, and
- the functionals X_v = c(r_v) − c(strand 0) for vertex reading strands, and
- z_{e,k} = c(r_{e,k}) − c(the strand before its unknot run)

form a basis of V_α^*.

*Proof.*
- **Classes of a summand copy.** A class of the summand copy in block j colours:
  - every strand before block j constantly;
  - block j by its class colouring;
  - every strand after block j by the constant c + J_j, where J_j is the block's jump, nonzero by Lemma 6.1.
- **Unknot blocks** add no class and copy the preceding colour.
- **Triangularity.** X_v takes the value J_j on every vertex copy up to and including v's own, and 0 on private copies (which come
  after all vertex copies). z_{e,k} takes the value J_j on its own copy only. So the matrix of the functionals against the summand
  classes is triangular, with the nonzero jumps J_j on the diagonal. ∎

**The construction.**
- **Base.** A connected sum of: for each vertex, S followed by d − 2 unknot blocks; then, for each edge and k = 1, 2, 3, d − 1 unknot
  blocks followed by S.
- **Insertions.** For each edge (u, v), u < v, the 4d strands (r_u, d − 2 copies of c(r_u), r_v) and (copies, r_{e,k}) appear left
  to right. They are moved as over-strands to the last 4d positions, cable_d(P4) is inserted, and the move is undone. The result
  K_Γ is a knot of size O(m(n + m)).
- **Leaves.** Since Σ_i t^{d−1−i} = 0, a bundle of d − 1 equal colours c and one colour c′ reads t^{…}(c′ − c). So exactly at every
  character the leaves are

  ℓ₀ = X_v − X_u and ℓ_k = z_{e,k}.

- **The form.** By Lemma 6.2 these are coordinates. By §§3–5, Q_{K_Γ} = Σ_e T(ℓ^{(e)}), with T(A₀, …, A₃; S₀, …, S₃) =
  Σ_j κ⟨W_j⁽³⁾(A_{≠j}), S_j⟩. Each term uses each leaf exactly once.

### 7. The edge weight

Let U be the odd data read by one leaf (the layer-1 and layer-2 parts of ⊕_{α∈R} 𝔤_α), and U′ the duals of the odd obstructions of
layers 3 and 4 at R. For σ = (A, S) ∈ U ⊕ U′, put f(σ) = Σ_{π ∈ (U ⊕ U′)³} ω^{T(σ, π₁, π₂, π₃)}, with the actual coefficients κ_t.

**Lemma 7.1.** f is integer-valued, real and even, and f(0) = |U ⊕ U′|³ is its maximum.

*Proof.*
- **Integer.** Every term of T contains each leaf exactly once. Rescaling private leaf 1 (data and dual together) by λ ≠ 0
  multiplies T by λ, so the distribution of T over π is invariant under F_p^×, and f is an integer.
- **Real.** λ = −1 gives f = f̄.
- **Even.** Negating σ negates T, so f(−σ) = f̄(σ) = f(σ). ∎

No claim is made that f is independent of the κ_t. The relabeling f_κ(A, S) = f₁(A, K S), with K rescaling every dual character
component by κ_t (the vertex dual included), holds and would suffice, but it is not needed.

**Lemma 7.2.** If s* ∈ U′ detects the near triple, then 0 < f(0, s*) < f(0).

*Proof.*
- **Only j = 0 survives.** At (0, s*) only the term j = 0 remains (P4: W₀⁽³⁾ = −[X₁, [X₂, X₃]]), so
  T = −κ_{t*}⟨[π₁, [π₂, π₃]], s*⟩ on the data parts, with κ_{t*} ≠ 0.
- **Summing.** The private duals give |U′|³, and π₁ gives

  f(0, s*) = |U′|³ |U| · #{(π₂, π₃) : κ_{t*}⟨[·, [π₂, π₃]], s*⟩ ≡ 0}.

  The zero set does not depend on the nonzero constant κ_{t*}.
- **The witness.** The near triple gives w ∈ 𝔤_{±a}, x ∈ 𝔤_a and y ∈ 𝔤_{−a}, in layers 1–2 with total layer ≤ 4, such that
  [w, [x, y]] ≠ 0. So the count lies in [1, |U|²): the pair (0, 0) is a zero, and some pair is not. ∎

### 8. Proof of Theorem 2

- **The count.** Summing private and unread coordinates gives P_τ(K_Γ) = λ^n μ^m Z_f(Γ), with
  Z_f(Γ) = Σ_σ Π_e f(σ_{v_e} − σ_{u_e}).
- **The sectors.** The closed count is Σ_e c_e P_{σ^e}(K_Γ) (Lemma 2.1).
  - Each P_{σ^e}(K_Γ) is multiplicative with K_{Γ⊔Γ′} = K_Γ # K_{Γ′} (Lemma 2.2), positive, and 1 on the empty graph.
  - Lemma I (`CLASSK-DICHOTOMY-20261026-001C` §3; for each fixed G) recovers (Σ_{e∈I} c_e) Z-values from the counts for
    Γ ⊔ F^{⊔j}, so the actual total count is used.
- **The hard problem.** W(σ, σ′) = f(σ′ − σ)² is symmetric and non-negative. W(0, d*) = f(d*)² > 0, and the minor
  f(0)⁴ − f(d*)⁴ ≠ 0 (Lemma 7.2).
- **Bulatov–Grohe.** EVAL(W) is #P-hard by Bulatov–Grohe ([BG]; as stated in [CCL, Thm 2.1, Cor 2.1], multigraphs allowed), and
  Z_W(Γ) = Z_f(Γ^{(2)}).
- **Membership.** Counting homomorphisms from finitely presented groups to a fixed finite group is in #P. ∎

### 9. Corollary 3

As in the predecessor: Theorem A of `COPRIME-DICHOTOMY-20261027-001A`, Theorem 2, and `CLASSK-DICHOTOMY-20261026-001C` for class 2.
The open case is pair failures in classes 3 and 4. It is the subject of `COPRIME-PAIRS-20261027-001C` and its successors.

### 10. References

Theorem numbers follow the cited editions. Where a book's numbering could not be confirmed, the chapter is given.

- **[Ar]** E. Artin, Theory of braids, Ann. of Math. 48 (1947) 101–126.
- **[BG]** A. Bulatov, M. Grohe, The complexity of partition functions, Theoret. Comput. Sci. 348 (2005) 148–186.
- **[Bi]** J. Birman, Braids, Links, and Mapping Class Groups, Ann. of Math. Stud. 82 (1974), Ch. 1 (Artin's characterization of braid
  automorphisms).
- **[BZ]** G. Burde, H. Zieschang, M. Heusener, Knots, 3rd ed., de Gruyter Stud. Math. 5 (2014), Ch. 12 (two-bridge knots:
  Schubert's classification, mirror images, symmetries).
- **[CCL]** J.-Y. Cai, X. Chen, P. Lu, Graph homomorphisms with complex values: a dichotomy theorem, SIAM J. Comput. 42 (2013)
  924–1029; arXiv:0903.4728, Theorem 2.1 and Corollary 2.1.
- **[Go]** D. Gorenstein, Finite Groups (Harper & Row 1968), Theorem 6.2.1 (Schur–Zassenhaus).
- **[Ha]** A. Hatcher, Algebraic Topology (Cambridge 2002), §3.H (local coefficients).
- **[Hi]** J. Hillman, Algebraic Invariants of Links, 2nd ed. (World Scientific 2012), Ch. 2–3.
- **[HK]** R. Hartley, A. Kawauchi, Polynomials of amphicheiral knots, Math. Ann. 243 (1979) 63–70.
- **[Kh]** E. I. Khukhro, p-Automorphisms of Finite p-Groups, LMS Lecture Note Ser. 246 (Cambridge 1998), Ch. 9–10 (Lazard
  correspondence).
- **[La]** M. Lazard, Sur les groupes nilpotents et les anneaux de Lie, Ann. Sci. ÉNS (3) 71 (1954) 101–190.
- **[Le]** J. Levine, Knot modules. I, Trans. Amer. Math. Soc. 229 (1977) 1–50.
- **[Li]** W. B. R. Lickorish, An Introduction to Knot Theory, GTM 175 (Springer 1997), Ch. 6 (Alexander polynomials of satellites).
- **[MKS]** W. Magnus, A. Karrass, D. Solitar, Combinatorial Group Theory (1966), §5.5–5.7 (Magnus expansion).
- **[Re]** C. Reutenauer, Free Lie Algebras (Oxford 1993), Theorem 1.4 (Dynkin–Specht–Wever).
- **[Sch]** H. Schubert, Knoten mit zwei Brücken, Math. Z. 65 (1956) 133–170.
- **[Se]** H. Seifert, On the homology invariants of knots, Quart. J. Math. Oxford (2) 1 (1950) 23–32.
- **[Sq]** C. C. Squier, The Burau representation is unitary, Proc. Amer. Math. Soc. 90 (1984) 199–202.
- **[Wa]** C. T. C. Wall, Surgery on Compact Manifolds, 2nd ed. (AMS 1999), Ch. 2 (Poincaré duality with local coefficients).

### 11. Gaps

1. Pair failures in classes 3 and 4.
2. Class at least 5, where Lemma 4.2 does not kill (3,3)-balanced terms.
3. Non-graded algebras.
4. p = 2 and 3.
5. Knot exteriors.
6. External human review.

## What `check.py` verifies

`check.py` imports read-only `cd_lib` (COPRIME-DICHOTOMY-20261027-001A), `gd` (COPRIME-DICHOTOMY-20261027-001B-E002), `mlib`
(TRIPLE-SYSTEM-20261027-001B-E001) and `cp_lib` (COPRIME-CLASS2-20261026-001B). Its last run passed every part (178 s).

1. **Lemma 3.0.** On 40 random braids closing to knots, at (p, d) = (7, 3), (13, 4), (11, 5), (7, 6) and (13, 12), the literal Fox
   closure rows computed from relator values equal t⁻¹(Bur_t − I) at all 240 characters.
2. **Lemma 3.1 and the reversed Artin identity** (replay). Squier invariance symbolically for n ≤ 7 and mod p for n ≤ 12, with
   J_t^T 𝟙 and the bundle identity; the reversed identity on 60 of 60 random braids, the forward one failing on 57.
3. **Lemma 4.0.**
   - On eight pair quotients of free graded algebras: no far triple failures, no parity violations, and only the balanced shapes
     (2, 1) and (1, 2) among nonzero triple brackets of elements of 𝔤_{±a} with 2a ≢ 0.
   - On five knot models (the chiral 6₁ at (7, 3) with two algebras, 6₃ at (7, 3), C₂ of T(2, 13) at (13, 4), 4₁ at (11, 5)), with
     class-4 pair quotients: the odd layer-2 residuals vanish identically; the pinned trivial-character cocycles are 0; replacing the
     odd layer-3 cocycles leaves every odd layer-4 residual unchanged, while the even layer-4 residuals move (control).
4. **Lemma 4.3.**
   - The characteristic polynomial of Bur_t(δ_k) is (x − 1) Σ_{i<k} t^{i−k+1} x^i in all 258 cases with p ≤ 17, k ≤ 6, t ≠ 1.
   - Fix Bur_t(C_k) is exactly the bundle constants at every t with t^k = −1 and the constants elsewhere, at eight (p, k) up to
     (13, 6).
   - At p = 13, d = 12, k = 2 (root characters 3 and 9, θ′ of order 6), the integer-exponent map satisfies the T(2, 13) relators
     and sends the longitude to 1, for three algebras (dim U up to 10).
   - Every datum lifts on C_k at eight (p, d, k), including (13, 12, 2), for four algebras, one of them pair-failing.
5. **Lemma 4.4.** The Alexander polynomial of b(4m² + 1, 2m) and (2m)² ≡ −1 for m ≤ 6; at every odd-order t₀ for six (p, d), the
   roots are exactly t₀^{±1} and Δ(−1) ≢ 0.
6. **Lemma 6.1.** The two-partition lemma on all 43,618 pairs of partitions with at least two blocks of sets of size ≤ 6; for cables,
   first and last strands separated at every root character; 120 random conjugates of the five amphichiral braids at ten
   (knot, p, d) cases: 10 had first and last strands not separated, and all 120 are separated after the over-strand conjugation.
7. **Lemma 7.2 with the actual κ.**
   - W₀⁽³⁾ = −[X₁, [X₂, X₃]] from the degree-3 Magnus part of P4 (p = 5, 7, 11).
   - Exact counts 0 < f(0, s*) < f(0) in six cases (four-way at (7, 3), (13, 4), (7, 6), (11, 5); layer4 at (5, 4), (7, 3)).
   - At (7, 3) the direct exponential sum including κ_{t*} = 2 equals 1,630,279 = |U| × count, with zero imaginary part.
8. **Gadget replication.** Measured forms equal the predictions on K₂ gadgets for 6₃ at (7, 3), C₂ of T(2, 13) at (13, 4), and a
   conjugated figure-eight representative at (11, 5) (29 strands, 700 crossings), each with two algebras.
