# A triple failure under the pair condition makes counting #P-hard at every sector order

Status: Proved

## Standard statement

**Setting.**
- p ≥ 5 is prime, r | p − 1, and ζ ∈ F_p^× has order r.
- 𝔫 = L₁ ⊕ ⋯ ⊕ L_c is a graded nilpotent Lie algebra over F_p of class c ≤ 4. C_r = ⟨σ⟩ acts by graded automorphisms, σ acting
  on 𝔫_j by ζ^j. N = exp(𝔫) (Lazard) and G = N ⋊ C_r.
- For d | r, write 𝔤_α = 𝔫^{(d)}_α (α mod d), as in `COPRIME-DICHOTOMY-20261027-001A`, with the criterion:
  - (P2_d) [𝔤_α, 𝔤_β] = 0 whenever α, β and α + β are nonzero;
  - (P3_d) [[𝔤_α, 𝔤_{−α}], 𝔤_β] = 0 for nonzero α, β.
- **Manifolds.** M = S³_{d/p}(K) for a knot K given by a diagram (here a closed braid). H₁(M) = Z/d and H₁(M; F_p) = 0.
- **Odd and even.** Under (P2_d), call components with nonzero character *odd* and 𝔤₀ *even*: θ_d = (+1 on 𝔤₀, −1 elsewhere) is
  then an automorphism (A, Lemma 1).

**Lemma 1 (only near triples).** Assume (P2_d). If α and β are nonzero and β ≢ ±α, then [[𝔤_α, 𝔤_{−α}], 𝔤_β] = 0.
- So under (P2_d), (P3_d) fails iff some **near triple** [[𝔤_a, 𝔤_{−a}], 𝔤_{±a}] is nonzero.
- Equivalently, for some a the symmetric pair (𝔤₀ ⊕ 𝔤_a ⊕ 𝔤_{−a}, θ_d) has a nonabelian triple system. For 2a ≡ 0 this is
  [[𝔤_a, 𝔤_a], 𝔤_a] ≠ 0.

**Theorem 2 (hardness at every sector order).** Let d | r. Assume (P2_d) holds and (P3_d) fails. Then the following problem is
#P-hard under polynomial-time Turing reductions:
- **Input:** a knot diagram K.
- **Output:** |Hom(π₁ S³_{d/p}(K), G)|.

For d = 2 this is `TRIPLE-SYSTEM-20261027-001C`. The proof below treats every d, with d = 2 as its simplest instance.

**Corollary 3 (the dichotomy and its remaining case).**
- **Scope.** Fix a divisor-closed set 𝒟 of divisors of r. Consider closed oriented 3-manifolds M with H₁(M; F_p) = 0, boundedly
  many sectors ψ ∈ Hom(H₁(M), C_r), and sector orders in 𝒟. For example, |H₁(M)| ≤ C gives 𝒟 = {d | r : d ≤ C}.
- **Polynomial.** If the criterion holds at every d ∈ 𝒟, counting is polynomial (`COPRIME-DICHOTOMY-20261027-001A`).
- **Hard.** Counting is #P-hard if, for some d ∈ 𝒟, the criterion fails and either:
  - (P2_d) holds (Theorem 2, on S³_{d/p}(K)); or
  - 𝔫 has class 2 (`CLASSK-DICHOTOMY-20261026-001C`, applied to G_d = N ⋊ C_d on S³_d(K); every map from a group with H₁ = Z/d
    to G lands in G_d).
- **Remaining case.** 𝔫 of class 3 or 4 for which, at every d ∈ 𝒟 where the criterion fails, (P2_d) fails too. This is not decided
  here.

**Examples.**

| algebra (characters mod d) | (P2_d) | near triple | consequence |
| --- | --- | --- | --- |
| four-way: x (a), y and w (−a), t = [[x, y], w] | holds | yes | #P-hard at every d with 2a ≢ 0 (new for d ≥ 3) |
| pair quotient of free class 3 on (a, −a) | holds | yes | #P-hard |
| pair quotient of free class 4 on (x: 0, y: a, v: −a), modulo [[y, v], y] and [[y, v], v] | holds | through the free layer-2 classes [x, y] and [x, v] | #P-hard (layer-4 near triples) |
| criterion quotients (A) | holds | no | polynomial |
| free class 2 on (1, 2, 3) mod 6, p = 7 | fails | — | #P-hard at d = 6 (class 2) |
| cross-layer: x (0), y (α), [y, [x, y]] ≠ 0, α² ≠ 1 | fails (pair (α, α) in layer 3) | — | remaining case in general; this one is #P-hard by `BEYOND-CLASS2-20261027-001A` |

**What it says.**
- **At every sector order, as at r = 2.** Once pairs are clean, so that the action collapses to an involution, hardness is decided
  by near triples. A near triple is a pair of inverse characters together with a third element of one of them.
- **The new difficulty for d ≥ 3 is in the base.** Every summand carries classes at both t₀ and t₀⁻¹, and these produce local
  Massey terms. Choosing summands whose local forms vanish removes them:
  - negative amphichiral two-bridge knots at roots of odd order;
  - (k,1)-cables of T(2, p) at roots of even order.
  Slope d/p removes the cross-summand channels.
- **Interpretation boundary.** r counts the characters of the action, not Boolean values. This is a counting-complexity statement
  only, not an emergence result.

## Nearest known results

- **This program.**
  - `TRIPLE-SYSTEM-20261027-001C`: d = 2. Its gadget, edge weight and class-4 parity argument are generalized here.
  - `BEYOND-CLASS2-20261027-001C`: the Fox-colour duality and the steering rule at t = −1. Its Lemma 2.2(iii) used the wrong
    Artin product order; the reversed identity is used here (§3).
  - `CLASSK-DICHOTOMY-20261026-001C`: the class-2 dichotomy and Lemma I (anchor isolation).
- **Samperton–Weiss (arXiv:2602.02885).** Class-2 nilpotent targets are polynomial with bounded H². With bounded homology,
  nilpotent targets are trivially easy, so a coprime action is needed for hardness.
- **Galindo (arXiv:2605.06984).** Hardness for nonabelian targets with unbounded homology.
- **Classical ingredients, cited and not reproved.**
  - Squier: the Burau representation is unitary for a sesquilinear form. Here that form is the explicit J_t, checked directly.
  - Schubert's classification of two-bridge knots: b(α, β) ≅ b(α, β′) iff β′ ≡ β^{±1} (mod α), and the mirror image is b(α, −β).
  - The satellite formula Δ_{C}(t) = Δ_P(t) Δ_K(t^k) for winding number k.
  - Universal coefficients over Λ = F_p[t^{±1}] for the infinite cyclic cover.
  - Schur–Zassenhaus, the Lazard correspondence, and Bulatov–Grohe as stated by Cai–Chen–Lu (arXiv:0903.4728, Theorem 2.1 and
    Corollary 2.1).
- **Novelty.**
  - Candidate new: hardness at sector orders d ≥ 3, and the two summand constructions that remove local Massey forms.
  - Folklore risk: medium for the method, which generalizes the r = 2 proofs; low for the statement, which was not found.

## Proof

Throughout, τ ∈ C_r has order d, ζ_d = ζ^{r/d}, and τ acts on 𝔤_α by ζ_d^α. For a character value t ∈ F_p^×, F^t is F_p with the
meridian acting by t.

### 1. Lemma 1

Let x ∈ 𝔤_α, y ∈ 𝔤_{−α} and w ∈ 𝔤_β. By Jacobi, [[x, y], w] = [x, [y, w]] − [y, [x, w]].
- [y, w] ∈ [𝔤_{−α}, 𝔤_β] = 0 by (P2_d), since −α, β and β − α are nonzero.
- [x, w] ∈ [𝔤_α, 𝔤_β] = 0 likewise, since α + β ≢ 0.

So [[x, y], w] = 0. ∎

**Lemma 1′ (parity).** Under (P2_d), a nonzero Lie monomial in elements of nonzero characters has character 0 if its degree is even
and a nonzero character if its degree is odd.

*Proof.* Induct on [P, Q].
- If P and Q both have odd degree, their characters α and β are nonzero. [𝔤_α, 𝔤_β] ≠ 0 forces α + β = 0 by (P2_d).
- The other cases add a zero character. ∎

### 2. Pinning at slope d/p

**Lemma 2.1.** Let K be a knot with meridian μ and Seifert longitude λ, and M = S³_{d/p}(K). Then

  |Hom(π₁M, G)| = Σ_{e ∈ (r/d)Z/rZ} p^{dim 𝔫 − dim 𝔫^{σ^e}} · P_{σ^e}(K),  P_υ(K) := #{ρ: π_K → G : ρ(μ) = υ}.

*Proof.*
- **Only μ^d remains.** π₁M = π_K/⟨⟨μ^d λ^p⟩⟩. For ρ: π_K → G, ρ(λ) ∈ N because λ ∈ [π_K, π_K], and N has exponent p. So
  ρ(μ^d λ^p) = ρ(μ)^d, and Hom(π₁M, G) = {ρ : ρ(μ)^d = 1}.
- **Which cosets.** Let ρ(μ) = g ∈ Nσ^e. Then g^d = 1 forces σ^{ed} = 1.
- **One conjugacy class per coset.**
  - g has order prime to p, and ⟨g⟩ maps onto ⟨σ^e⟩. So ⟨g⟩ is a complement to N in N⟨σ^e⟩.
  - By Schur–Zassenhaus, g is N-conjugate to σ^e.
  - The class of σ^e has |N : C_N(σ^e)| = p^{dim 𝔫 − dim 𝔫^{σ^e}} elements, since C_N(σ^e) = exp(𝔫^{σ^e}).
- **Conjugation.** It matches homomorphisms with ρ(μ) = nσ^e n⁻¹ to those with ρ(μ) = σ^e. ∎

**Lemma 2.2 (multiplicativity).** P_υ(K₁ # K₂) = P_υ(K₁) P_υ(K₂), P_υ(unknot) = 1 and P_υ(K) ≥ 1.

*Proof.*
- π_{K₁#K₂} = π_{K₁} ∗_{⟨μ⟩} π_{K₂}, so pinned homomorphisms on the amalgam are pairs of pinned homomorphisms.
- The map μ ↦ υ through π_K → Z gives P_υ(K) ≥ 1. ∎

So there are no cross-summand channel terms at slope d/p. At slope d/1 they appear: `COPRIME-DICHOTOMY-20261027-001B-E002` R1
measured an exact non-multiplicative count there.

### 3. The pinned layered count and Squier duality

**The layered count.** Write V_α = H¹(π_K; F^{ζ_d^α}) for α ≢ 0, and X for the exterior.
- **Torsors.** Pinned lifts through L_k = γ_k/γ_{k+1} form torsors under the relative cocycles {c : c(μ) = 0}.
  - For a nontrivial character these are ≅ H¹(X; F^t): coboundaries adjust c(μ) freely.
  - For the trivial character they are 0, because u(μ) = 1 for the generator u of H¹(X; F_p).
- **Obstructions.**
  - H²(X, μ; F_p) = 0, so trivial-character parts are unique and unobstructed.
  - For t ≠ 1, H²(X, μ; F^t) ≅ H²(X; F^t) ≅ H¹(X; F^{t⁻¹})^* (Lefschetz duality; ∂X is F^t-acyclic).
- **The count.**

  P_τ(K) = #{ξ ∈ ⊕_{k, α ≢ 0} V_α ⊗ L_{k,α} : o(ξ) = 0}.

  Coboundary changes are conjugations and do not change obstructions.
- **No coboundary factors.** Unlike the closed count of `BEYOND-CLASS2-20261027-001C` §1, P_τ carries no B¹ factors.

**Fox colours at t.** For a closed braid β on n strands, the colour of a label at a letter is propagated by:
- g > 0: (s_i, s_{i+1}) ↦ ((1 − t⁻¹)s_i + t⁻¹s_{i+1}, s_i), since c(x⁻¹yx) = (1 − t⁻¹)c(x) + t⁻¹c(y);
- g < 0: (s_i, s_{i+1}) ↦ (s_{i+1}, t s_i + (1 − t)s_{i+1}).

Bur_t(β) is their product. Twisted cocycles are the fixed vectors of Bur_t(β), and coboundaries are the constant vectors 𝟙. The
closure relators R_q = x_q⁻¹β(x)_q have Fox matrix I − Bur_t(β). The pinned generator x₀ does not change the column space, because
𝟙 lies in the kernel.

**Lemma 3.1 (Squier form).** Let J_t be lower unitriangular with (J_t)_{qq′} = (t − 1)t^{q−q′−1} for q > q′. Then
Bur_{t⁻¹}(g)^T J_t Bur_t(g) = J_t for every letter g. Moreover, if t^d = 1 ≠ t:
- Σ_{i<d} (J_t^T s)_{o+i} = Σ_{i<d} t^i s_{o+i} (the bundle identity);
- J_t^T 𝟙 = (t^{n−1−q})_q.

At t = −1, J_t is the form J of `BEYOND-CLASS2-20261027-001C`.

*Proof.*
- **Invariance.** It is a polynomial identity in two rows and columns with finitely many local patterns. `check.py` verifies it in
  Z[t, t⁻¹] for every letter and n ≤ 7, and modulo p for n ≤ 12.
- **The bundle identity.** (J_t^T s)_q − t(J_t^T s)_{q+1} = s_q − s_{q+1}. Telescoping with the weights 1 + t + ⋯ + t^i, the
  boundary term carries 1 + t + ⋯ + t^{d−1} = 0. ∎

**Lemma 3.2 (left kernel).** Let o ∈ F^n be the vector of relator values at a central layer component of character t ≠ 1. Then o
lies in the column space of I − Bur_t(β) iff ⟨o, J_t^T s⟩ = 0 for every s ∈ Fix Bur_{t⁻¹}(β). Moreover ⟨o, J_t^T 𝟙⟩ = 0 always, so
s may be taken modulo 𝟙, that is, in V_{t⁻¹}.

*Proof.*
- **Left-kernel vectors.** By Lemma 3.1, s^T J_t Bur_t(β) = (Bur_{t⁻¹}(β)⁻¹ s)^T J_t = s^T J_t for s ∈ Fix Bur_{t⁻¹}(β). So
  J_t^T s is a left-kernel vector.
- **Dimensions.** The left kernel has dimension dim Fix Bur_t(β) = 1 + dim H¹(X; F^t). This equals
  1 + dim H¹(X; F^{t⁻¹}) = dim Fix Bur_{t⁻¹}(β), because dim H¹(X; F^t) = dim H²(X; F^t) = dim H¹(X; F^{t⁻¹}) (Euler
  characteristic and duality). J_t is invertible, so these vectors fill the left kernel.
- **The coboundary vector (corrected Artin identity).**
  - A positive letter maps (a, b) ↦ (a⁻¹ba, a) and preserves the *reverse* product ba. So
    β(x)_{n−1} ⋯ β(x)₀ = x_{n−1} ⋯ x₀.
  - With β(x)_j = x_j R_j and P_j = x_{n−1} ⋯ x_j, this gives Π_{j = n−1, …, 0} P_j R_j P_j⁻¹ = 1 in the free group.
  - An identity among relations Π u_k R_{q_k}^{ε_k} u_k⁻¹ = 1 gives Σ ε_k χ(u_k) o_{q_k} = 0 for central relator values. Here the
    coefficients are χ(P_j) = t^{n−j}, which is t · J_t^T 𝟙 by Lemma 3.1.
- **The correction.** `BEYOND-CLASS2-20261027-001C` Lemma 2.2(iii) used the forward product, which positive letters do not
  preserve. The reversed identity gives the needed vector, at t = −1 equal to −J^T 𝟙. ∎

**The Fourier form.** Q(ξ; s) = Σ ⟨o_{k,α}(ξ), J^T s_{k,α}⟩, extended polynomially as in `TRIPLE-SYSTEM-20261027-001C` §1. Then

  P_τ(K) = p^{−D} Σ_{ξ, s} ω^{Q(ξ; s)},

with s ranging over the duals of the obstruction components and D their dimension.

### 4. Summands without local forms

A **summand of type t₀** is a knot whose twisted cohomology at characters other than 1 sits only at a prescribed set R(t₀) of
characters, one dimension each. It is **unobstructed** if every class datum at R(t₀) lifts, pinned at τ, for the algebras in
question.

**Lemma 4.1 (negative amphichiral summands; odd orders).** Let K be negative amphichiral: there is an orientation-reversing
homeomorphism h of S³ with h(K) = K reversing the orientation of K, so h(μ) is conjugate to μ. Let t₀ ≠ ±1 be a simple root of
Δ_K mod p, and assume (P2_d) and c ≤ 4. Then K is unobstructed at R = {t₀, t₀⁻¹}.

*Proof.*
- **(a) One dimension each.** At a simple root the t₀-primary part of the F_p-Alexander module A is Λ/(t − t₀). So
  H¹(X; F^{t₀^{±1}}) ≅ Hom_Λ(A, F_{t₀^{±1}}) is one-dimensional.
- **(b) The u-pairing is perfect.** Let P(c, c′) = ⟨u ∪ c ∪ c′, [X, ∂X]⟩ for c ∈ V₊ = H¹(X; F^{t₀}) and c′ ∈ V₋.
  - With duality, P is perfect iff u ∪ (−): H¹(X; F^{t₀}) → H²(X; F^{t₀}) is an isomorphism.
  - Up to sign, this map is the connecting map of 0 → F^{t₀} → E → F^{t₀} → 0, with E = Λ/(t − t₀)² and extension class u.
  - For modules on which t − 1 is invertible, H¹(X; M) ≅ Hom_Λ(A, M), by universal coefficients over Λ, since
    H₀(X̃) = Λ/(t − 1).
  - So H¹(X; E) → H¹(X; F^{t₀}) is Hom_Λ(Λ/(t − t₀), E) → Hom_Λ(Λ/(t − t₀), E/(t − t₀)E). This map is 0, because the
    (t − t₀)-torsion of E is (t − t₀)E. The connecting map is therefore injective, hence bijective.
- **(c) Scalars.**
  - h fixes the meridian class, so it preserves each character and acts on V_± by scalars ε_±, with h^*u = u.
  - h reverses [X, ∂X]. So P(h^*c, h^*c′) = −P(c, c′), and by (b), ε₊ε₋ = −1.
- **(d) Vanishing.** Suppose all data lift through layer k − 1.
  - The layer-k obstruction is natural: o(h^*ξ) = h^*o(ξ). Pairing with s ∈ V_∓ gives L(ξ, s) = ⟨o(ξ) ∪ s, [X, ∂X]⟩ with
    L(h^*ξ, h^*s) = −L(ξ, s).
  - By Lemma 1′, the obstruction at a nonzero character consists of odd-degree monomials in the data. They have degree ≥ 3, since
    the linear part is the cocycle condition, and layer ≤ 4, so the degree is exactly 3.
  - By (P2_d) each such monomial has the shape [[𝔤_a, 𝔤_{−a}], 𝔤_{±a}]. Together with s, it uses V₊ twice and V₋ twice.
  - So L(h^*ξ, h^*s) = (ε₊ε₋)² L(ξ, s) = L(ξ, s). Hence L = 0, and by perfect duality o = 0. ∎

**Lemma 4.2 (cable summands; even orders).** Let k ≥ 1 and C_k be the (k,1)-cable of T(2, p) (C₁ = T(2, p)). Then:
- (i) Δ_{C_k}(t) ≡ (t^k + 1)^{p−1} mod p. The twisted cohomology at t ≠ 1 sits exactly at the characters with t^k = −1, one
  dimension each.
- (ii) For every 𝔫 (every class c < p, with no condition on the brackets) and τ of order d, C_k is unobstructed at
  R = {α : ζ_d^{αk} = −1}.

*Proof.*
- **(i) The polynomial.** Δ_{T(2,p)} = (t^p + 1)/(t + 1) ≡ (t + 1)^{p−1}, and the satellite formula gives Δ_{T(2,p)}(t^k), since
  Δ_{T(k,1)} = 1.
- **(i) The restriction isomorphism.** Write X_C = X_T ∪ S, with S the (k,1)-cable space. S is the mapping torus of the k-punctured
  disc D_k with monodromy δ_k = σ₁ ⋯ σ_{k−1}.
  - For t^k = −1 the torus ∂X_T is F^t-acyclic, because μ_T ↦ t^k ≠ 1.
  - S is F^t-acyclic: δ_k^k is the full twist and acts on reduced Burau by the scalar t^{±k} = −1, so no eigenvalue of δ_k is 1.
  - Mayer–Vietoris gives H^*(X_C; F^t) ≅ H^*(X_T; F^{−1}), which is one-dimensional in degree 1, since T(2, p) has cyclic
    Alexander module.
  - At t ≠ 1 with t^k ≠ −1, Δ_{C_k}(t) ≠ 0, so there is no cohomology.
- **(ii) Building the lifts.** Let θ′ = τ^k. It acts by −1 on U = ⊕_{α ∈ R} 𝔤_α (all layers).
  - **The companion.** For a twisted cocycle c of π_T at the sign character with c(μ_T) = 0 and A ∈ U, the map
    ρ₀(g) = exp(c(g)A) θ′^{ψ(g)} is a homomorphism π_T → G, as in `TRIPLE-SYSTEM-20261027-001C` §2. It has ρ₀(μ_T) = θ′ and
    ρ₀(λ_T) = 1, because λ_T ∈ π″ and c is a homomorphism on the kernel of the sign.
  - **The cable space.** π₁S = ⟨a₁, …, a_k, c | c a_i c⁻¹ = δ_k(a_i)⟩, with μ_T = a₁ ⋯ a_k and λ_T = c. Set ρ_S(a_i) = τ and
    ρ_S(c) = 1. Each δ_k(a_i) is a conjugate of some a_j by a word in the a's, so the relations hold.
  - **Gluing.** The two maps agree on ⟨μ_T, λ_T⟩ (τ^k and 1). They glue to ρ: π_{C_k} → G with ρ(μ_C) = ρ(a₁) = τ.
  - **Every datum is reached.**
    - Through the restriction isomorphism, the class data of ρ at each α ∈ R are c ⊗ A_α.
    - As in `TRIPLE-SYSTEM-20261027-001C` §2, varying the layer-ℓ part of A moves the layer-ℓ lift through the whole pinned torsor
      V ⊗ (U ∩ L_ℓ).
    - So every class datum at R is realized. ∎

**Lemma 4.3 (existence).** Let t₀ = ζ_d^a with ord(t₀) ≥ 3.
- **Odd order.** Then t₀ is a square, and K_m = b(4m² + 1, 2m) with m ≡ ±√t₀/(t₀ − 1) (mod p) qualifies for Lemma 4.1.
  - Its Alexander polynomial is −m²(t + t⁻¹) + 2m² + 1 (genus one, Conway notation [2m, 2m]), whose roots are exactly t₀^{±1}, and
    simple.
  - It is negative amphichiral: (2m)² ≡ −1 (mod 4m² + 1), so b(α, −β) ≅ b(α, β) by Schubert, and two-bridge knots are invertible.
- **Even order 2k.** C_k qualifies for Lemma 4.2, and R = {α : ζ_d^{αk} = −1} ∋ a.

The summand depends only on G, so it has constant size.

**Remarks.**
- **Why two constructions.** Simple roots of the Alexander polynomial of a strongly negative amphichiral knot are squares mod p
  (by the Hartley–Kawauchi form Δ(t²) = f(t)f(−t)). Odd-order roots are squares and every non-square has even order, so the two
  constructions cover all orders.
- **Measurement.** `COPRIME-DICHOTOMY-20261027-001B` measures both constructions, and controls that obstruct (twist knots and other
  chiral knots).

### 5. Steering at t

Insert cable_d(P, o) at level ℓ. Here P is a pure braid on four strands whose geometric conjugators W_j lie in γ₃F₄; P4 =
[[A₁₂, A₂₃], A₃₄] qualifies. Bundle j consists of the d strands o + dj, …, o + dj + d − 1, and Y_j = z_{o+dj+d−1} ⋯ z_{o+dj} is
the reverse-order product of their labels at level ℓ.

**Lemma 5.1 (the cable).** The letters of cable_d(P, o) fix the labels outside the 4d strands, and conjugate every label of bundle j
by W_j(Y₀, …, Y₃).

*Proof.* As in `BEYOND-CLASS2-20261027-001C` Lemma 4.1, by induction over the letters of P. A cabled letter moves the over-bundle
intact and conjugates the under-bundle by the over-bundle's reverse product. `check.py` verifies the whole cable in the free group
for d = 2, …, 6. ∎

**Lemma 5.2 (bundle values and conjugators).** Each Y_j lies in N, because a product of d labels from the coset Nτ lies in
Nτ^d = N.
- The odd linear part of log ρ(Y_j) at a character t is the leaf ℓ_j = Σ_{i<d} t^{d−1−i} c(z_{o+dj+i}). It vanishes on coboundaries,
  because the coefficients sum to 0.
- Under (P2_d) and c ≤ 4, the odd part of Λ_j := log ρ(W_j(Y)) is the Dynkin degree-3 part
  W_j⁽³⁾ = (1/3) Σ_w M_j(w) [X_{w₁}, [X_{w₂}, X_{w₃}]], evaluated on the odd parts of log ρ(Y) in layers 1 and 2.

*Proof.* This is `TRIPLE-SYSTEM-20261027-001C` Lemma 3.1 with "−1" read as "odd" and "+1" as "even", using Lemma 1′.
- Degree-4 terms in layer-1 parts are even.
- Brackets of labels inside a bundle are even, or of odd degree ≥ 3 and so of layer ≥ 3; inside W⁽³⁾ these reach layer ≥ 5.
- Layer-2 odd parts are free classes and enter as data.
- Layer-1 even parts vanish, by pinning and H¹(X; F_p)'s generator u. ∎

**Lemma 5.3 (the shift).** For z = nτ, e^Λ z e^{−Λ} = z · exp(−(1 − t⁻¹)Λ_t − (even)), where Λ_t is the component at character t.

*Proof.*
- z⁻¹e^Λ z = exp(τ⁻¹(Ad_{n⁻¹}Λ)), and τ⁻¹ multiplies the t-component by t⁻¹.
- [n, Λ] has layer ≥ 4 and is a bracket of odd and odd, or of even (layer ≥ 2) and odd, so it is even or of layer ≥ 5. ∎

**Lemma 5.4 (transport).** Odd shifts in γ₃ pass through letters like colours (Bur_t). The corrections are brackets with odd layer-1
parts, of layer 4 and even. The colour transport of cable_d(P, o) is the identity: in F_p ⋊ ⟨t⟩ the bundle products are
translations, so W_j ∈ [F, F] evaluates to 1. ∎

**Proposition 5.5 (the steering rule).** On data where the lower obstructions vanish, the odd obstructions of layers 3 and 4 change
by

  ΔQ(ξ; s) = Σ_t κ_t Σ_j ⟨W_j⁽³⁾(ℓ(ξ))_t, ℓ_j(s_t)⟩,  κ_t = t⁻² − t⁻¹,

where t runs over the characters of the obstruction components and s_t ∈ V_{t⁻¹}. At t = −1, κ_t = 2, as in the r = 2 proofs.

*Proof.*
- **Lower layers.** Layers 1 and 2 and the even part of layer 3 are unchanged (Lemmas 5.2–5.4).
- **The shift.** By Lemma 5.3 the odd shift of each label of bundle j is (1 − t⁻¹)Λ_j. It is transported to the bottom by
  Bur_t(β[ℓ:]), and the closure rows change by o′ − o = −Bur_t(β[ℓ:])Δ, where Δ = (1 − t⁻¹) Σ_j Λ_j Σ_{i ∈ B_j} e_i.
- **The pairing.** By Lemma 3.1,

  ⟨o′ − o, J_t^T s⟩ = −(s^{(ℓ)})^T J_t Δ = −(1 − t⁻¹) Σ_j Λ_j Σ_{i<d} t^i s^{(ℓ)}_{o+dj+i}.

  Here s^{(ℓ)} = Bur_{t⁻¹}(β[:ℓ]) s is the colouring at level ℓ.
- **The dual leaf.** At character t⁻¹, the leaf ℓ_j(s) = Σ_i t^{−(d−1−i)} s_i equals t Σ_i t^i s_i. So the change is
  −(1 − t⁻¹)t⁻¹ Σ_j Λ_j ℓ_j(s) = (t⁻² − t⁻¹) Σ_j Λ_j ℓ_j(s).
- **Layer 4.** Layer-3 odd lifts enter layer 4 only through brackets with odd layer-1 parts, which are even. ∎

**Corollary 5.6.**
- Insertions add.
- A cancelling pair γγ⁻¹ changes nothing.
- A conjugated insertion γ · cable_d(P, o) · γ⁻¹ acts as in 5.5, with leaves read at the middle level.

The proofs are those of `BEYOND-CLASS2-20261027-001C` Corollary 4.5.

`COPRIME-DICHOTOMY-20261027-001B-E002` confirms Proposition 5.5 exactly at d = 3, 4, 5, 6 on single insertions and on gadgets. This
includes layer-4 obstructions through free layer-2 classes. The controls fail as required: κ = 2 in place of κ_t, forward-order
bundles, and a twist-knot base.

### 6. The gadget

Fix a near triple at a (Lemma 1), t₀ = ζ_d^a, and a summand S of type t₀ (Lemma 4.3), with root characters R ∋ ±a. Let Γ be a
loopless multigraph on vertices 1, …, n with edges e = (u_e, v_e), u_e < v_e.

**The base.** A connected sum of closed-braid blocks, in this order:
- for each vertex v, a copy of S followed by d − 2 unknot blocks σ₁ on two strands;
- for each edge e and k = 1, 2, 3, a run of d − 1 unknot blocks followed by a copy of S.

An unknot block adds a strand whose colour equals that of the strand before it, at every character. The base is a knot. It is
unobstructed by Lemmas 2.2 and 4.1–4.2.

**Reading strands and coordinates.** Let r_v be the last strand of v's copy of S, and r_{e,k} that of the private copy. At each
α ∈ R:
- X_v = c(r_v) − c(strand 0);
- z_{e,k} = c(r_{e,k}) − c(the strand before its unknot run).

Together they are a basis of V_α^*, with one coordinate per copy of S, triangular in the order of the sum.

**The insertion.** For each edge e:
- The 4d strands
  (r_u, the d − 2 copies after r_u, r_v), (copies, r_{e,1}), (copies, r_{e,2}), (copies, r_{e,3})
  appear left to right in this order.
- A braid γ_e moves them as over-strands, rightmost first, to the last 4d positions. Over-strands keep their labels and colours,
  and no chosen strand passes under another.
- Insert γ_e · cable_d(P4, n_strands − 4d) · γ_e⁻¹. The insertion is pure, so K_Γ is a knot. Its size is O(m(n + m)), with
  constants depending on G.

**Leaves.** The bundle coefficients t^{d−1−i} sum to 0, so a bundle of d − 1 equal colours c and one colour c′ reads t^{…}(c′ − c).
Hence, exactly at every character:

  ℓ₀ = X_v − X_u,  ℓ_k = z_{e,k} (k = 1, 2, 3).

**The form.** By §§3–5:

  Q_{K_Γ} = Σ_e T(ℓ^{(e)}),  T(A₀, …, A₃; S₀, …, S₃) = Σ_j κ ⟨W_j⁽³⁾(A_{≠j}), S_j⟩.

Each term of T uses each of the four leaves exactly once. In the P4 tensor, W_j⁽³⁾ is multilinear in the leaves other than j.

### 7. The edge weight

Let U be the odd data read by one leaf: the layer-1 and layer-2 parts of ⊕_{α∈R} 𝔤_α, one copy per summand, since dim V_α = 1. Let
U′ be the duals of the odd obstruction components of layers 3 and 4 at R. For σ = (A, S) ∈ U ⊕ U′, set

  f(σ) = Σ_{π ∈ (U ⊕ U′)³} ω^{T(σ, π₁, π₂, π₃)}.

**Lemma 7.1.** f is an integer, real and even, independent of the nonzero constants κ_t and of nonzero rescalings of each character,
and f(0) = |U ⊕ U′|³ is its maximum.

*Proof.*
- **Rescaling.** T is linear in each leaf. Rescaling private leaf 1 in all its slots by λ ≠ 0 multiplies T by λ. So f is rational,
  hence an integer.
- **Realness.** Negating leaf 1 gives f = f̄.
- **Evenness.** Negating σ negates T.
- **Constants.** Per-character constants are absorbed by rescaling the private duals character by character. ∎

**Lemma 7.2.** There is s* ∈ U′ with 0 < f(0, s*) < f(0).

*Proof.*
- **Only j = 0 survives.** At (0, s*) only the term j = 0 remains, with W₀⁽³⁾ = −[X₁, [X₂, X₃]] (P4). So
  T = −κ⟨[π₁, [π₂, π₃]], s*⟩ on the data parts.
- **Summing.** Summing the private duals gives |U′|³. Summing π₁ gives

  f(0, s*) = |U′|³ |U| · #{(π₂, π₃) ∈ U² : ⟨[·, [π₂, π₃]], s*⟩ ≡ 0}.

- **The witness.** The near triple gives x ∈ 𝔤_a, y ∈ 𝔤_{−a} and w ∈ 𝔤_{±a}, in layers 1–2 with total layer ≤ 4, such that
  [w, [x, y]] = −[[x, y], w] ≠ 0. Choose s* detecting it. Then the trilinear form is nonzero, so the count lies in [1, |U|²), with
  the pair (0, 0) giving the lower end. ∎

### 8. Proof of Theorem 2

- **The count.** Sum over the private coordinates (giving f) and over the coordinates read by no leaf (layer-3 and layer-4 data,
  giving constant factors). Then

  P_τ(K_Γ) = λ^n μ^m Z_f(Γ),  Z_f(Γ) = Σ_{σ: V(Γ) → U ⊕ U′} Π_e f(σ_{v_e} − σ_{u_e}),

  with constants λ, μ > 0 depending only on G and S.
- **The sectors.** By Lemma 2.1, |Hom(π₁ S³_{d/p}(K_Γ), G)| = Σ_e c_e f_e(Γ), with f_e(Γ) = P_{σ^e}(K_Γ).
  - Set K_{Γ ⊔ Γ′} := K_Γ # K_{Γ′}. Each f_e is multiplicative (Lemma 2.2), positive, and equal to 1 on the empty graph.
  - Lemma I of `CLASSK-DICHOTOMY-20261026-001C` computes (Σ_{e ∈ I} c_e) f_{e*}(Γ) from the counts for Γ ⊔ F^{⊔j},
    j = 0, …, R − 1. Here e* is the sector of τ, and F and the constants depend only on G.
- **The hard problem.** Let W(σ, σ′) = f(σ′ − σ)². It is symmetric and non-negative.
  - W(0, d*) = f(d*)² > 0, with d* = (0, s*), so 0 and d* lie in one component.
  - Its 2 × 2 minor is f(0)⁴ − f(d*)⁴ ≠ 0 (Lemma 7.2). So W is not block-rank-1, and EVAL(W) is #P-hard by Bulatov–Grohe, which
    allows multigraph inputs.
- **The reduction.** Doubling edges gives Z_W(Γ) = Z_f(Γ^{(2)}). Building K_{Γ^{(2)} ⊔ F^{⊔j}} is polynomial.
- **Membership.** Counting homomorphisms from a finitely presented group to a fixed finite group is in #P. ∎

### 9. Corollary 3

- **Polynomial side and the hard cases.** These follow from ticket A, Theorem 2 and `CLASSK-DICHOTOMY-20261026-001C` (Corollary D
  there, with G_d).
- **The manifolds.** S³_{d/p}(K) has H₁ = Z/d. Its sector orders divide d, and they lie in 𝒟 because 𝒟 is closed under divisors.
- **The remaining case.** A pair failure in class 3 or 4 has no parity structure.
  - The steering corrections can land at root characters.
  - Edges that read a P2 bracket also carry degree-3 and degree-4 terms. These make the edge weight a general exponential sum rather
    than a count.
  - The parity argument of Lemma 7.2 is unavailable, and no substitute is proved here. ∎

### 10. What rests on citation, and the gaps

**Cited, not reproved.**
- Bulatov–Grohe (via Cai–Chen–Lu) and Lemma I.
- Schubert's classification of two-bridge knots, and invertibility of two-bridge knots.
- The satellite formula and the cable-space description.
- Universal coefficients over Λ.
- Schur–Zassenhaus and Lazard.
- Standard 3-manifold facts: closed-braid presentations, meridian amalgams, Lefschetz duality.

**Gaps.**
1. **Pair failures in classes 3 and 4** (the remaining case of Corollary 3). Special cases are known, for example the cross-layer
   pair of `BEYOND-CLASS2-20261027-001A`.
2. **Class 5 or higher.** Lemma 4.1 kills (2,2)-balanced terms, but degree-5 terms are (3,3)-balanced, and (ε₊ε₋)³ = −1 does
   not kill them. Lemma 4.2 survives in every class; Proposition 5.5 needs degree-5 parts.
3. Non-graded algebras; p = 2 and p = 3; manifolds with p-torsion in H₁; unbounded sectors; knot exteriors.
4. No external review.

## What `check.py` verifies

`check.py` imports read-only: cd_lib.py (`COPRIME-DICHOTOMY-20261027-001A-P001`), gd.py (`COPRIME-DICHOTOMY-20261027-001B-E002`),
mlib.py (`TRIPLE-SYSTEM-20261027-001B-E001`) and cp_lib.py (`COPRIME-CLASS2-20261026-001B-P001`).

1. **Lemma 1 and parity.** On pair quotients of free graded algebras, every triple failure is near. Every nonzero Lie monomial of
   degree ≤ 4 in odd basis elements obeys Lemma 1′.
2. **Lemma 3.1.** J_t invariance in Z[t, t⁻¹] (sympy) for every letter and n ≤ 7, and modulo p for n ≤ 12; the bundle identity; the
   formula for J_t^T 𝟙.
3. **Lemma 3.2.** In the free group, for random braids: the reversed identity Π_{j desc} P_j R_j P_j⁻¹ = 1 holds and the forward
   one fails. Its coefficient vector is t · J_t^T 𝟙.
4. **Lemma 4.1 inputs.**
   - The Schubert presentation of b(4m² + 1, 2m) has Alexander polynomial −m²(t + t⁻¹) + 2m² + 1 (up to units) for m ≤ 5, and
     (2m)² ≡ −1.
   - For several (p, t₀) of odd order, the knot built from the formula has twisted cohomology exactly at t₀^{±1}, one dimension each,
     and every class datum lifts for the four-way, F3 and class-4 algebras (μ^d presentation).
5. **Lemma 4.2.** C_k has Fox Alexander polynomial (t^k + 1)^{p−1} mod p and cohomology exactly at t^k = −1. Every datum lifts,
   including for the pair-failing free class 3 on (a, a).
6. **Lemma 5.1.** cable_d(P4) conjugates each bundle strand by W_j evaluated on reverse-order bundle products, in the free group,
   for d = 2, …, 6.
7. **Lemma 7.2.** Exact edge-weight counts for the four-way and class-4 algebras at (p, d) = (7, 3), (13, 4), (7, 6) and (11, 5):
   0 < f(0, s*) < f(0).
8. **Proposition 5.5 and the gadgets.** These are cited from experiment `COPRIME-DICHOTOMY-20261027-001B-E002` (frozen contract),
   and replicated here on one gadget per construction.
