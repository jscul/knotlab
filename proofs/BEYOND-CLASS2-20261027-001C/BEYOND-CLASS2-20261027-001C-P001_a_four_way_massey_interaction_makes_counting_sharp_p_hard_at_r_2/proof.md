# A four-way Massey interaction makes counting #P-hard where no pair can be hard

Status: Proved

## Standard statement

**Setting.**
- p ≥ 5 is prime. 𝔽 = F_p, and ω = e^{2πi/p}.
- **The group.** G_p = U₄(𝔽) ⋊ ⟨D⟩ with D = diag(1, −1, 1, −1). Concretely, G_p is the group of upper triangular 4 × 4
  matrices over 𝔽 with diagonal (1, 1, 1, 1) or (1, −1, 1, −1), and it has order 2p⁶. Conjugation by D multiplies E₁₂, E₂₃, E₃₄
  and E₁₄ by −1 and fixes E₁₃ and E₂₄.
- **The layers.** The lower central series of U₄ gives three layers:
  - layer 1: the superdiagonal, (1,2), (2,3), (3,4);
  - layer 2: the entries (1,3) and (2,4);
  - layer 3: the entry (1,4), the centre γ₃ = {e^t := I + tE₁₄}.
- **The manifolds.** M = S³₂(K) is 2-surgery on a knot K. Then H₁(M) = Z/2 and ψ: π₁M → C₂ is the surjection. Write χ = (−1)^ψ.
  - V = V_M = H¹(M; 𝔽^χ) is first cohomology with twisted coefficients, and N = dim V. N is unbounded although H₁(M) is fixed.
  - Knots are given as closed braids, and G_p is fixed.

**Theorem 1 (the count is a four-way form).**
- For every such M there is a four-linear form Q_M: V³ × V → 𝔽 with

  |Hom(π₁M, G_p)| = 1 + p^{N+4} · #Λ(M),  where Λ(M) = {c ∈ V³ : Q_M(c; ·) = 0}.

- Hence #Λ(M) = p^{−N} Σ_{c ∈ V³, s ∈ V} ω^{Q_M(c; s)}.
- Q_M(c_y, c_x, c_w; s) is the twisted triple Massey product ⟨c_y, c_x, c_w⟩ paired with s. It is computed in §2 from any braid
  presentation through a duality J.

**Theorem 2 (the form of explicit surgeries).**
- **(a) Base.** If K = K₁ # ⋯ # K_N and every K_k has dim V_{S³₂(K_k)} = 1 (for example T(2, p)), then Q_M = 0.
- **(b) Steering.** Let P be a pure braid on four strands whose geometric conjugators W_j lie in γ₃F₄; for example
  P4 = [[A₁₂, A₂₃], A₃₄]. Insert γ · cable₂(P) · γ⁻¹ at any level of a braid word, where γ is any braid word. This adds

  2 Σ_j Λ_j(c) ℓ_j(s),  where Λ_j(c) = Σ_{(i₁, i₂, i₃)} M_j(i₁i₂i₃) ℓ_{i₁}(c_y) ℓ_{i₂}(c_x) ℓ_{i₃}(c_w).

  - M_j is the degree-3 Magnus part of W_j.
  - ℓ_k is the difference of the Fox colours of the two strands of bundle k at the insertion level.
  - Insertions add.
- **(c) The gadget.** Every loopless multigraph Γ (n vertices, m edges) gives, in polynomial time, a knot K_Γ with O(m(n + m))
  crossings. In coordinates X_v (vertices) and private coordinates per edge,

  Q_{M_Γ} = 2 Σ_{e = uv} T(X_v − X_u ; three private coordinates of e),

  where T is the Magnus tensor of P4.

**Theorem 3 (hardness).**
- **The weight.** Let f(d) = Σ_{π ∈ 𝔽¹²} ω^{2T(d; π)} for d ∈ 𝔽⁴. Then f is integer-valued and even, with f(0) = p¹² and
  f(0, 0, 0, 1) = p⁶(2p⁴ − p²).
- **The reduction.** |Hom(π₁M_Γ, G_p)| = 1 + p^{12m+4} Z_f(Γ), with Z_f(Γ) = Σ_{σ: V(Γ) → 𝔽⁴} Π_{uv ∈ E} f(σ_v − σ_u). The
  matrix W(σ, σ′) = f(σ′ − σ)² is not block-rank-1.
- **Conclusion.** Counting |Hom(π₁M, G_p)| for 2-surgeries on knots is #P-hard under polynomial-time Turing reductions.

**Proposition 4 (no pair can be hard at r = 2).**
- **No hard pair.** G_p has no graded hard pair: no homogeneous a, b with χ(a), χ(b) and χ(a)χ(b) nontrivial and [a, b] ≠ 0. At
  r = 2 no group N ⋊ C₂ can have one.
- **Class 2 is easy.** Every coprime class-2 group N ⋊ C₂ with N of exponent p, including G_p/γ₃, counts in polynomial time on
  closed manifolds with H₁ = Z/2 (`CLASSK-DICHOTOMY-20261026-001C`).

**What it says.**
- At r = 2 a pairwise interaction (class 2) never makes counting hard. The first hardness is a four-way interaction: a triple
  Massey product ⟨c_y, c_x, c_w⟩ read against a fourth class s.
- So past class 2 the line does not sit at three-way pairs. Interactions of three or more classes are needed:
  - `BEYOND-CLASS2-20261027-001A`, a graded hard pair across layers;
  - this proof, a four-way Massey interaction with no hard pair at all.

## Nearest known results

- **Samperton–Weiss (arXiv:2602.02885, v2 April 2026).**
  - Counting maps to a fixed nonabelian group is #P-hard for finitely presented groups.
  - For class-2 nilpotent G and 3-manifold groups with |H²(M, Z(G))| bounded, it is polynomial.
  - They ask whether class 2 is hard on 3-manifolds; class 3 and non-nilpotent targets are not treated.
  - For nilpotent targets with bounded homology, counting is polynomial for a simple reason: each layer has boundedly many
    choices. So hardness with bounded H₁ needs a coprime action, as here, where twisted H¹ is unbounded.
- **Kuperberg–Samperton (2018).** Hardness for nonabelian simple groups, on homology spheres.
- **Galindo (arXiv:2605.06984).** A dichotomy for unbounded homology.
- **This program.**
  - `CLASSK-DICHOTOMY-20261026-001C` (class-(K) dichotomy): hard exactly with a hard pair, so at r = 2 every class-(K) group is
    polynomial.
  - `BEYOND-CLASS2-20261027-001A`: graded hard pairs across layers.
- **Classical ingredients.**
  - Massey products as obstructions for unitriangular representations (Dwyer; Fenn–Sjerve).
  - Milnor invariants equal Massey products (Turaev 1979).
  - The Magnus expansion of pure-braid conjugators (Milnor).
  - The Burau representation at t = −1 preserves a form (Squier 1984). It is the symplectic action on the double branched cover
    (Brendle–Margalit–Putman 2015).
  - Bulatov–Grohe (as stated in Cai–Chen–Lu, Thm 2.1).
- **Novelty.**
  - Candidate new: hardness for a fixed non-nilpotent group of order 2p⁶ on closed 3-manifolds with H₁ = Z/2. Also new: the
    separation "class 2 always easy, class 3 can be hard" at r = 2.
  - Candidate new: the exact steering formula (Theorem 2(b)) for twisted mod-p Massey forms under cabled pure-braid insertions,
    with its proof by Fox calculus and the J-duality.
  - Folklore risk: low to medium for the theorem. Medium for Lemma 2.1 (a form of Squier's) and for the Sym constructions,
    which are classical in spirit. Searches in this epic and the earlier ones found no statement of the theorem.

## Proof

### 0. Conventions

- **Braids.** A braid word w = g₁ ⋯ g_m on n strands has letters ±1, …, ±(n − 1). The letter g acts on positions i = |g| − 1 and
  i + 1, counted from 0. On a tuple of labels:
  - for g > 0, (z_i, z_{i+1}) ↦ (z_i⁻¹ z_{i+1} z_i, z_i);
  - for g < 0, (z_i, z_{i+1}) ↦ (z_{i+1}, z_{i+1} z_i z_{i+1}⁻¹).

  The over-strand keeps its label. β(x)_q is the bottom label of strand q, a word in the top generators x₀, …, x_{n−1}.
- **The presentation 𝒫_w.** If the closure K is a knot, π₁M is presented on x₀, …, x_{n−1} with relators:
  - R_q = x_q⁻¹ β(x)_q for q = 0, …, n − 1 (one is redundant; all are kept);
  - S = x₀² λ, where λ is the Seifert longitude. It is read as in cp_lib: along the knot from strand 0 at the top, multiply the
    over-labels at undercrossings (to the power of the crossing sign), then multiply by x₀^{−writhe}.
- **Fox colours.**
  - A colour vector s ∈ 𝔽ⁿ is pushed through a letter by g > 0: (s_i, s_{i+1}) ↦ (2s_i − s_{i+1}, s_i), and by g < 0:
    (s_i, s_{i+1}) ↦ (s_{i+1}, 2s_{i+1} − s_i).
  - Bur(w) is the product of these matrices (top colours to bottom colours).
  - A cocycle c ∈ Z¹(π₁M; 𝔽^χ), with c(gh) = c(g) + χ(g)c(h), is the same as a fixed vector s = (c(x_q))_q of Bur(w).
    - Indeed c(x⁻¹yx) = 2c(x) − c(y).
    - Every such s also satisfies the surgery relator. First, c(x₀²) = 0. Second, c(λ) = 0: λ lies in π″, and c defines a map to
      the metabelian group 𝔽 ⋊ C₂.
  - B¹ = 𝔽·𝟙, the constant vectors. So V = Fix Bur(w)/𝔽𝟙.

### 1. The layered count (first half of Theorem 1)

A homomorphism ρ: π₁M → G_p over ψ has the form ρ(g) = U(g) D^{ψ(g)} with U(g) unitriangular. From
U(gh) = U(g) · D^{ψ(g)} U(h) D^{−ψ(g)}:

- **Layer 1.** The superdiagonal (c_y, c_x, c_w) = (U₁₂, U₂₃, U₃₄) is a triple of twisted cocycles. Every triple occurs: G_p/γ₂
  is 𝔽³ ⋊ C₂.
- **Layer 2.** The lifts to G_p/γ₃ form an extension by 𝔽² with trivial action.
  - Its obstruction lies in H²(π₁M; 𝔽)², which embeds in H²(M; 𝔽)² ≅ H₁(M; 𝔽)² = 0, so lifts exist.
  - The lifts form a torsor under Hom(π₁M, 𝔽)² = 0, so the lift is unique.
- **Layer 3.** γ₃ ≅ 𝔽^χ, since D acts by −1. A lift exists exactly when the obstruction o(c) ∈ H²(π₁M; 𝔽^χ) vanishes. The lifts
  then form a torsor under Z¹(π₁M; 𝔽^χ), of size p^{N+1}.
- **Classes.** Conjugating ρ by I + m (m superdiagonal) changes the layer-1 cocycles by the coboundary of m, and every element of
  (B¹)³ arises. So liftability depends only on the class triple in V³.
- **Sector 0.** Homomorphisms with ψ∘ρ trivial land in the p-group U₄. Their image has trivial abelianization, because
  H₁(M; 𝔽) = 0, so it is trivial.

Hence |Hom| = 1 + |B¹|³ · #Λ(M) · p^{N+1} = 1 + p^{N+4} #Λ(M), with Λ(M) = {ξ ∈ V³ : o(ξ) = 0}. In the presentation 𝒫_w,
assign generator lifts with layer 3 equal to 0. Then each relator evaluates to e^{o_R}, and the lift exists iff the vector o lies
in the column space of the twisted Fox matrix A.

### 2. The J-duality (second half of Theorem 1)

**The Fox matrix.** For 𝒫_w at the character χ (every x_q ↦ −1), the closure rows are A_{R_q, x_r} = δ_{qr} − Bur(w)_{qr}. This
is the Fox fundamental formula: c(β_q) = Σ_r (∂β_q/∂x_r)^χ c(x_r) is the bottom colour.

**The form J.** Let J be the n × n lower-unitriangular integer matrix with J_{qq′} = 2(−1)^{q−q′} for q > q′.

**Lemma 2.1.** For every letter g: Bur_g^T J Bur_g = J and Bur_g^T J^T Bur_g = J^T. Also

  (J^T s)_q + (J^T s)_{q+1} = s_q − s_{q+1},  and  J^T 𝟙 = ((−1)^{n−1−q})_q.

*Proof.*
- Bur_g differs from I in two rows and two columns only, so each entry of Bur_g^T J Bur_g − J is an integer polynomial in finitely
  many local patterns. Two indices lie in {i, i+1}, and the third lies below, between or above them, with a parity.
- These patterns already occur for n ≤ 6. `check.py` part 2 verifies the identity exactly over Z for every letter and every
  n ≤ 12, and also the two vector identities.
- The g < 0 case follows from g > 0 by inversion. ∎

*Remark (not used).* J + J^T = 2uu^T with u_q = (−1)^q, and J − J^T is an alternating form that Burau at t = −1 preserves. This is
Squier's unitarity at t = −1. The alternating form is presumably the intersection form of the double branched cover of the punctured
disk in a suitable basis (Brendle–Margalit–Putman); this identification is not checked here.

**Lemma 2.2 (left kernel).** Let Y = {y : y^T A = 0}.
- **(i)** For every s ∈ Fix Bur(w), y(s) := (J^T s, 0) ∈ Y.
- **(ii)** Y = y(Fix) ⊕ 𝔽 y^{id}, where y^{id} has a nonzero S-component.
- **(iii)** ⟨o, y^{id}⟩ = 0 and ⟨o, y(𝟙)⟩ = 0 for every obstruction vector o.

*Proof.*
- **(i)** By Lemma 2.1, Bur^T J Bur = J. So J Bur = Bur^{−T} J, and

  s^T J Bur = (Bur⁻¹ s)^T J = s^T J.

  Hence y(s)^T A = s^T J (I − Bur) = 0. The S-component of y(s) is 0.
- **(ii) Dimensions.** The right kernel of A is Fix Bur(w), since every colouring satisfies S. So dim Y = (n + 1) − rank A =
  dim Fix + 1. The map y is injective because J is invertible.
- **(ii) The extra vector.** λ commutes with x₀ in the knot group. So x₀ S x₀⁻¹ S⁻¹ = x₀² [x₀, λ] x₀⁻² is a product of conjugates
  u_k R_{q_k}^{ε_k} u_k⁻¹ in the free group.
  - Such an identity among relations gives a left-kernel vector, here with S-component χ(x₀) − 1 = −2 ≠ 0.
  - Evaluating it under ρ gives Σ ε χ(u) o_T = 0, since relator values lie in the centre γ₃ with π acting by χ.
- **(iii)** Artin's identity β(x)₀ ⋯ β(x)_{n−1} = x₀ ⋯ x_{n−1} gives Π_q (x₀ ⋯ x_q) R_q (x₀ ⋯ x_q)⁻¹ = 1. Its left-kernel vector
  ((−1)^{q+1})_q is ±J^T 𝟙. ∎

**Definition (the four-way form).** Q(c_y, c_x, c_w; s) := ⟨o(c), y(s)⟩ for cocycles c and s.
- It is well defined on V³ × V: changing the layer-3 lift changes o by A f₃, which is orthogonal to Y; it is class-invariant by
  §1; and y(𝟙) pairs to 0.
- It is four-linear. Layer 2 solves linear systems with bilinear right-hand sides. The (1,4) entry of a product of matrices is a
  sum of terms c_y · b, a · c_w and c_y c_x c_w, each with one y-, one x- and one w-factor.
- By Lemma 2.2, o(ξ) lies in the column space of A iff Q(ξ; s) = 0 for all s. This proves Theorem 1. The Fourier form is
  Σ_s ω^{Q(ξ; s)} = p^N [Q(ξ; ·) = 0].

### 3. Base vanishing (Theorem 2(a))

**Dihedral maps.** Let δ_c(g) = [[1, χ(g)c(g)], [0, χ(g)]] for a cocycle c. This is a homomorphism to the affine group
Aff(𝔽) = 𝔽 ⋊ C₂.

**Lemma 3.1.** Let K be a knot with dim V_{S³₂(K)} = 1. Let c be a cocycle generating it, normalized by c(μ) = 0 at the
meridian μ = x₀. Then for every (y, x, w) ∈ 𝔽³ there is ρ: π_K → G_p such that:
- its layer-1 cocycles are (yc, xc, wc);
- ρ(μ) = D;
- ρ(λ) = I.

*Proof.* There is one construction per support pattern of (y, x, w):

| pattern | construction |
| --- | --- |
| (1,1,1) | Sym³ δ_c |
| (1,1,0) | Sym² δ_c ⊕ χ |
| (0,1,1) | 1 ⊕ χ·Sym² δ_c |
| (1,0,1) | δ_c ⊕ δ_c |
| (1,0,0) | δ_c ⊕ 1 ⊕ χ |
| (0,1,0) | 1 ⊕ χδ_c ⊕ χ |
| (0,0,1) | 1 ⊕ χ ⊕ δ_c |
| (0,0,0) | D^ψ |

Here Sym^k is the k-th symmetric power: Y ↦ aX + εY in the basis X^k, X^{k−1}Y, …

- **Each is a homomorphism into G_p.** Each is a representation of Aff(𝔽) with values upper triangular, with diagonal
  (1, ε, 1, ε).
- **Superdiagonal.** The superdiagonal of U = ρ D^{−ψ} is (k₁c, k₂c, k₃c), with constants k_t ∈ 𝔽 independent of g and nonzero
  exactly on the pattern. For Sym³ the constants are (1, 2, 3); they are nonzero because p ≥ 5.
- **Scaling.** Conjugation by Δ = diag(1, t₁⁻¹, (t₁t₂)⁻¹, (t₁t₂t₃)⁻¹) commutes with D and scales the superdiagonal by
  (t₁, t₂, t₃). This reaches (yc, xc, wc).
- **The meridian and the longitude.** δ_c(μ) = diag(1, −1) maps to D. δ_c(λ) = I because λ ∈ π″ and Aff is metabelian, so λ maps
  to I.
- `check.py` part 3 verifies each construction exhaustively on Aff(𝔽) × Aff(𝔽) for p = 5, 7, 11, 13 (homomorphism, values,
  constants, D). ∎

**Proof of 2(a).**
- **The amalgam.** π_K = π_{K₁} ∗_{⟨μ⟩} ⋯ ∗_{⟨μ⟩} π_{K_N} is amalgamated along meridians, and λ = λ₁ ⋯ λ_N.
- **Restriction.** H⁰ and H¹ of ⟨μ⟩ ≅ Z with χ(μ) = −1 vanish. So restriction H¹(π_K; 𝔽^χ) → ⊕_k H¹(π_{K_k}; 𝔽^χ) is an
  isomorphism by Mayer–Vietoris, and V_M = H¹(π_K; 𝔽^χ) by §0.
- **Gluing.** Given ξ ∈ V³, take on each summand the representation ρ_k of Lemma 3.1 for the restriction of ξ. The ρ_k agree on μ
  (all send it to D), so they glue to ρ: π_K → G_p with ρ(λ) = Π ρ_k(λ_k) = I. Then ρ(x₀²λ) = D² = I, so ρ factors through π₁M.
  By the restriction isomorphism, its class triple is ξ.
- **Conclusion.** Every ξ lifts, so Λ(M) = V³ and Q_M = 0.
- **The example T(2, p).** Its colour space is all of 𝔽²: the block [[2, −1], [1, 0]]^p ≡ I mod p, since it is unipotent with
  (B − I)² = 0. So dim V = 1. ∎

### 4. Steering (Theorem 2(b))

Let w′ = w[:ℓ] · cable₂(P, o) · w[ℓ:]. Bundle k is (o + 2k, o + 2k + 1), with product Y_k = z_{o+2k+1} z_{o+2k} of the labels z at
level ℓ.

**Lemma 4.1 (the cable).** The letters of cable₂(P, o):
- fix the labels outside [o, o + 7];
- conjugate both labels of bundle j by W_j(Y). This is the geometric conjugator of strand j of P, with x_k ↦ Y_k.

The geometric conjugators are W_j with the image of x_j equal to W_j x_j W_j⁻¹. They are computed letter by letter: g > 0 replaces
the under-strand's conjugator W by z_i⁻¹ W, and g < 0 replaces it by z_{i+1} W.

*Proof.*
- **Induction over the letters of P.** A cabled letter moves the over-bundle intact. It conjugates both strands of the
  under-bundle by the over-bundle's product, or its inverse, exactly as the letter updates the under-strand's conjugator after the
  substitution x_k ↦ Y_k.
- **The base case.** This is a free-group identity on eight letters, verified for all six letters ±1, ±2, ±3 (`check.py` part 4).
- **The whole braid.** `check.py` part 4 also verifies the identity directly for P4, and experiment B for P4B. For P4, M_j has
  degree-1 and degree-2 Magnus parts 0 (verified over Z), so W_j ∈ γ₃F₄. ∎

**Lemma 4.2 (central conjugation).**
- **The Magnus substitution.** For labels ρ(z) ∈ G_p, the bundle products ρ(Y_k) = I + N_k are unitriangular. The substitution
  X_k ↦ N_k is an algebra homomorphism on the Magnus algebra, because products of four strictly upper triangular matrices vanish.
- **The conjugator lands in the centre.** Hence ρ(W_j(Y)) = I + Σ_{|v|=3} M_j(v) N_{v₁} N_{v₂} N_{v₃} = e^{Λ_j}, where
  (N_a N_b N_c)₁₄ = (N_a)₁₂ (N_b)₂₃ (N_c)₃₄.
- **Bundle functionals.** (N_k)₁₂ = c_y(z_{o+2k+1}) − c_y(z_{o+2k}) = ℓ_k(c_y), and likewise for x and w.
- **The effect on a label.** In G_p, e^λ (U D) e^{−λ} = U D e^{−2λ}, because U fixes E₁₄ and D E₁₄ D = −E₁₄. ∎

**Lemma 4.3.** The colour transport of cable₂(P, o) is the identity.

*Proof.* Lemma 4.1 holds in Aff(𝔽), where bundle products are translations, which commute. There W_j ∈ [F, F] evaluates to I.
`check.py` part 4 also verifies it over Z for P4. ∎

**Proposition 4.4.** Q_{w′}(c; s) − Q_w(c; s) = 2 Σ_j Λ_j(c) ℓ_j(s), where colours at level ℓ are s^{(ℓ)} = Bur(w[:ℓ]) s and
V_{w′} = V_w by Lemma 4.3.

*Proof.*
- **Layers 1 and 2 agree.** Modulo γ₃ the cable acts trivially on labels (Lemmas 4.1 and 4.2). Along each strand's passage through
  the cable, the longitude picks up letters whose product is W_j(Y)⁻¹ ∈ γ₃. Each update W ↦ fW of the conjugator, with
  f = z_i⁻¹ for g > 0 and f = z_{i+1} for g < 0, comes with the longitude letter f⁻¹. The cable has writhe 0.
  - So both presentations, which share the generators x_q, have the same layer-1 and layer-2 systems, and the same unique
    layer-2 lift.
- **Layer 3.** Assign layer 3 as 0. After the cable, the labels of bundle j become z e^{−2Λ_j}.
  - **Transport.** A shift z ↦ z e^{−δ} is transported by the letters like colours. For example
    (x e^{−δ_x})⁻¹ (y e^{−δ_y})(x e^{−δ_x}) = x⁻¹ y x e^{−(2δ_x − δ_y)}, because e^t commutes past U₄ and x e^t x⁻¹ = e^{−t} for
    x in the D-coset.
  - **The closure rows.** At the bottom the shift is Bur(w[ℓ:]) Δ, with Δ = 2 Σ_j Λ_j (e_{o+2j} + e_{o+2j+1}). The closure rows
    give o′ − o = −Bur(w[ℓ:]) Δ. The S-row changes too, but y_S = 0.
- **The pairing.** By Lemma 2.1,

  ⟨o′ − o, y(s)⟩ = −s^T J Bur(w[ℓ:]) Δ = −(s^{(ℓ)})^T J Δ = −Σ_j 2Λ_j [(J^T s^{(ℓ)})_{o+2j} + (J^T s^{(ℓ)})_{o+2j+1}]
                 = 2 Σ_j Λ_j ℓ_j(s).

  Here Bur(w[ℓ:])⁻¹ s = s^{(ℓ)} because s is fixed by Bur(w). ∎

**Corollary 4.5.**
- **(a) Additivity.** Insertions add: apply 4.4 repeatedly. Colours are unchanged by Lemma 4.3.
- **(b) Canceling pairs.** Inserting γ γ⁻¹ changes neither the bottom labels, as group elements, nor the longitude after free
  reduction.
  - Each strand's passage through γ⁻¹ meets the same over-strands, with the same labels and opposite signs, in reverse order.
  - So the presentations agree up to free reduction, and Q is unchanged.
- **(c) Conjugated insertions.** Hence γ · cable₂(P, o) · γ⁻¹ changes Q as in 4.4, with leaves read at the middle level. ∎

### 5. The gadget (Theorem 2(c))

**Construction.**
- Γ has vertices 1, …, n and edges e = 0, …, m − 1 with ends u_e < v_e. Put N = n + 6m and b_e = n + 6e.
- The base is w₀ = σ₁^p σ₂^p ⋯ σ_N^p on N + 1 strands. Its closure is #_N T(2, p).
- Put γ_e = σ_{v+1} ⋯ σ_{b} · σ_{u+1} ⋯ σ_{b−1}, with positive letters, so the moving strand is the over-strand.
- The gadget word is w_Γ = Π_e (γ_e · cable₂(P4, b_e − 1) · γ_e⁻¹) · w₀.

**Size and knot type.**
- |w_Γ| ≤ pN + m(80 + 4(N + 1)) = O(m(n + m)).
- Each conjugated insertion is pure, so the permutation is that of w₀, an (N + 1)-cycle. Hence K_Γ is a knot.

**Colours, coordinates and leaves.**
- **Colours.** Bur(w_Γ) = Bur(w₀) = I, using Lemma 4.3 and the T(2, p) blocks. So V = 𝔽^{N+1}/𝔽𝟙.
- **Coordinates.** X_v = s_v − s₀ for 1 ≤ v ≤ n, and z_j = s_j − s_{j−1} for n < j ≤ N. They form a basis of V^*.
- **Leaves.** At edge e's middle level, the strands u and v sit at b − 1 and b with their colours unchanged, since they moved over
  the others. The strands b + 1, …, b + 6 are untouched. So the leaves are

  ℓ₀ = X_v − X_u,  ℓ_k = z_{b+2k}  (k = 1, 2, 3).

- **The form.** By 2(a) and Corollary 4.5, Q_{M_Γ} = 2 Σ_e T(ℓ^{(e)}). Here T(A, B, C, S) = Σ_j Σ M_j(i₁i₂i₃) A_{i₁} B_{i₂} C_{i₃}
  S_j, with A, B, C, S the leaf values in the four slots y, x, w, s.
- **Unused coordinates.** The coordinates z_{b+1}, z_{b+3}, z_{b+5} occur in no leaf.

**Confirmation (`BEYOND-CLASS2-20261027-001B`).** The gadgets of K₂, P₃, the digon, K₃, K₁,₃ and C₄ at p = 5, 7, 11 were built, up
to 788 crossings. Their measured Q equals this formula on every sample. Base vanishing, steering, two pure braids, dragged
insertions, independent counts and the lifting criterion were all confirmed as well.

### 6. The edge weight

**The tensor.** T is the Magnus tensor of P4 (`check.py` part 4). Each M_j has four terms ±1. Each term uses every leaf exactly
once, with indices {i₁, i₂, i₃, j} = {0, 1, 2, 3}.

**Lemma 6.1.** f(d) is an integer. It does not depend on the nonzero constant in front of T, it is even, and it depends only on
the support of d.

*Proof.*
- **Linearity.** T is linear in leaf 0's values d, and in each private leaf's values.
- **Integrality.** Scaling leaf 1 in all four slots by λ ≠ 0 multiplies T by λ. So the number of π with 2T = x is the same for all
  x ≠ 0. Hence f(d) = (p · #{2T = 0} − p¹²)/(p − 1) is rational, and, being an algebraic integer, an integer.
- **The constant.** The same argument shows that the constant in front of T does not matter.
- **Evenness.** T(−d) = −T(d) gives f(−d) = f̄(d) = f(d).
- **Support.** Scaling one slot (leaf 0 and the privates) by λ multiplies T by λ, which leaves f unchanged. ∎

**Lemma 6.2.** f(0) = p¹² and f(d*) = p⁶(2p⁴ − p²) for d* = (0, 0, 0, 1).

*Proof.*
- At d*, only the terms with leaf 0 in the s-slot survive, so T(d*, π) = Φ₀(π_y, π_x, π_w), where

  Φ₀(A, B, C) = −A₃B₂C₁ + A₂B₃C₁ + A₁B₃C₂ − A₁B₂C₃.

  Summing over π_s gives p³. Summing over C = π_w gives p³ [Φ₀(A, B, ·) = 0].
- The conditions are A₁B₃ = A₁B₂ = 0 and A₂B₃ = A₃B₂.
  - A₁ ≠ 0 gives (p − 1)p³ solutions.
  - A₁ = 0 gives p(p³ + p² − p): B₁ is free, and the 2 × 2 matrix [[A₂, A₃], [B₂, B₃]] is singular.
- The total is 2p⁴ − p². `check.py` part 5 confirms it by enumeration for p = 5, 7, 11, 13, and computes f on every support
  pattern at p = 5. ∎

### 7. Hardness (Theorem 3)

**The count.** By §5 and Theorem 1, sum over the private and unused coordinates. Each private triple of an edge gives the factor
f(σ_v − σ_u) of Lemma 6.1, and each unused coordinate gives p⁴. Here σ_v ∈ 𝔽⁴ collects X_v in the four slots.

  #Λ(M_Γ) = p^{−N} · p^{12m} · Z_f(Γ) = p^{6m−n} Z_f(Γ),  so  |Hom(π₁M_Γ, G_p)| = 1 + p^{12m+4} Z_f(Γ).

`check.py` part 6 confirms the Fourier normalization on a reduced K₂ template at p = 5 by kernel ranks.

**The matrix W.**
- W(σ, σ′) = f(σ′ − σ)² is a symmetric non-negative integer p⁴ × p⁴ matrix, by Lemma 6.1.
- W(0, d*) > 0, so 0 and d* lie in one connected component.
- The minor on {0, d*} is f(0)⁴ − f(d*)⁴ ≠ 0 by Lemma 6.2, so that component has rank at least 2 and W is not block-rank-1.
- By Bulatov–Grohe, EVAL(W) is #P-hard.

**The reduction.**
- For a graph Γ let Γ^{(2)} double every edge. Then Z_W(Γ) = Z_f(Γ^{(2)}) = (|Hom(π₁M_{Γ^{(2)}}, G_p)| − 1)/p^{24m+4}.
- Building K_{Γ^{(2)}} is polynomial (§5).
- So EVAL(W) Turing-reduces to counting.

Doubling avoids needing f ≥ 0. In fact f ≥ 0 holds whenever some slot of d is 0: the sum over that slot's privates is then a
count. f ≥ 0 was also observed on all of 𝔽⁴ at p = 5 and on all support patterns at p = 7, but it is not needed. ∎

### 8. Proposition 4

- **No graded hard pair.** The nonzero brackets in the associated graded are:
  - [E₁₂, E₂₃] → E₁₃, with characters (−1)(−1) = 1;
  - [E₂₃, E₃₄] → E₂₄, likewise;
  - [E₁₂, E₂₄] and [E₁₃, E₃₄] → E₁₄, where one factor has the trivial character.

  None is hard (`check.py` part 1 with ticket A's graded_hard_pairs). A hard pair at r = 2 would need χχ′ ≠ 1 with
  χ = χ′ = −1, which is impossible.
- **Class 2 is easy.** `CLASSK-DICHOTOMY-20261026-001C` makes class 2 polynomial when no G_d with d | r has a hard pair. For
  G_p/γ₃ directly: |Hom| = 1 + p^{3(N+1)}.
- **The criterion is not a pair.** G_p's hardness is not a three-way pair. Its interaction is ⟨c_y, c_x, c_w⟩ against s:
  - the tree [[y, x], w];
  - all four characters equal to −1;
  - every intermediate bracket has the trivial character, so its layer-2 lift is unique and carries no class (H¹(M; 𝔽) = 0). ∎

### 9. What rests on citation, and the gaps

**Cited, not reproved.**
- Bulatov–Grohe (via Cai–Chen–Lu).
- Standard 3-manifold facts:
  - the closed-braid presentation and Seifert longitude;
  - λ ∈ π″;
  - meridian amalgams for connected sums;
  - Poincaré duality for H²(M; 𝔽).
- The CLASSK dichotomy, for Proposition 4.

**Gaps.**
- p = 2 and p = 3, which need other base constructions.
- r > 2. There the base form has channel terms, measured earlier in the epic, and the gadget would need them.
- Knot exteriors.
- A full criterion for when class 3 is hard. Open: is every coprime class-3 group without a graded hard pair and without a
  nonzero four-way form polynomial?
- No external review.
