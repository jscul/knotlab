# Class-(K) counts on gadget surgeries are positive sums of sector partition functions

Status: Proved

## Standard statement

**Setting.**
- p is an odd prime and r ≥ 2 divides p − 1, so every character of C_r = ⟨h⟩ takes values in μ_r(F_p). Characters are written
  multiplicatively: χ, χ′, χχ′, χ⁻¹, χ^k, and 1 is the trivial character.
- **The group.** G = N ⋊ C_r is of class (K) (`COPRIME-CLASS2-20261026-001C`):
  - N = A × B with (a, b)(a′, b′) = (a + a′ + β(b, b′), b + b′);
  - A and B are elementary abelian, and β is a C_r-equivariant bilinear cocycle;
  - B = ⊕_χ B_χ and A = ⊕_ρ A_ρ are the eigenspace decompositions over F_p;
  - the commutator pairing κ = β − βᵀ has components κ_{χ,χ′}: B_χ × B_χ′ → A_{χχ′};
  - a **hard pair** is (χ, χ′) with χ, χ′ and χχ′ nontrivial and κ_{χ,χ′} ≠ 0.
- **Regraded groups.** For k ∈ Z/r, G^{(k)} is N ⋊ C_r with h acting by the k-th power of the original action. Its eigenspaces
  are B^{(k)}_θ = ⊕_{χ^k = θ} B_χ and A^{(k)}_θ = ⊕_{ρ^k = θ} A_ρ, and κ^{(k)}_{θ,θ′} is the sum of the κ_{χ,χ′} with χ^k = θ
  and χ′^k = θ′.
- **The manifold.** M is closed and oriented, with H₁(M; Z) = Z/r and ψ: π₁M → Z/r onto. Then H¹(M; F_p) = 0.
  - For θ ≠ 1, V_θ = H¹(M; F_p twisted by θ∘ψ), and d_θ = dim V_θ.
  - T(u, v, w) = ⟨u ⌣ v ⌣ w, [M]⟩ for classes in V_θ, V_θ′, V_θ″ with θθ′θ″ = 1. Degree-one classes anticommute, so T is an
    alternating trilinear form on V = ⊕_θ V_θ.
- **Slot triples.** S = (s₁, s₂, s₃) consists of nontrivial characters with s₁s₂s₃ = 1, in one of three patterns:
  - **P1:** s₁, s₂, s₃ distinct;
  - **P2:** S = (s, s, t) with t = s⁻² and s³ ≠ 1;
  - **P3:** S = (s, s, s) with s³ = 1.
- **Gadget manifolds.** Let Γ be a multigraph without loops, with n vertices, m edges and each edge oriented e = (u → v). M is a
  **Γ-gadget manifold for S** if:
  1. **Dimensions.** d_θ = Σ_τ c_τ [θ ∈ {τ, τ⁻¹}], where the base counts c_τ are:
     - P1: c_{s₁} = n and c_{s₂} = c_{s₃} = m;
     - P2: c_s = n + m and c_t = m;
     - P3: c_s = n + 2m.
  2. **Triple product.** V_{s₁}, V_{s₂}, V_{s₃} carry coordinates in which T = 𝒯_Γ = Σ_e f_{1e} ∧ f_{2e} ∧ f_{3e}, with every
     functional extended by zero to the other V_θ:
     - P1: V_{s₁} = F_p^V (coordinates x_u), V_{s₂} = F_p^E (y_e), V_{s₃} = F_p^E (t_e), and (f₁, f₂, f₃) = (x_u − x_v, y_e, t_e);
     - P2: V_s = F_p^V ⊕ F_p^E (x_u, p_e), V_t = F_p^E (w_e), and (x_u − x_v, p_e, w_e);
     - P3: V_s = F_p^V ⊕ F_p^E ⊕ F_p^E (x_u, p_e, q_e), and (x_u − x_v, p_e, q_e).

  In particular T vanishes on every component that is not a permutation of S. Ticket `CLASSK-DICHOTOMY-20261026-001C` shows that the
  construction of `COPRIME-CLASS2-20261026-001D` §3 produces such manifolds as r-surgeries on knots.

**Theorem A.** Let M be a Γ-gadget manifold for S, and G of class (K). Then

  |Hom(π₁M, G)| = Σ_{k ∈ Z/r} c_k λ_k^n μ_k^m Z_{W_k}(Γ),

where:
- c_k = Π_{χ^k ≠ 1} |B_χ| · Π_{ρ^k ≠ 1} |A_ρ| > 0, and λ_k, μ_k are integer powers of p given in §2 (step 4);
- Z_{W_k}(Γ) = Σ_{σ: V(Γ) → U_k} Π_{e = uv} W_k(σ_u − σ_v), with U_k = B₁ ⊕ A₂₃*;
- B_i = B^{(k)}_{s_i}, A_{ij} = A^{(k)}_{s_i s_j} and κ_{ij} = κ^{(k)}_{s_i, s_j}: B_i × B_j → A_{ij} (so B₁ = B₂ in P2, and
  B₁ = B₂ = B₃ in P3);
- W_k(ξ, η) = |K₂(ξ)| · |K₃(ξ)| · p^{−rank(η ∘ κ₂₃ on K₂(ξ) × K₃(ξ))};
- K₂(ξ) = {y ∈ B₂ : κ₁₂(ξ, y) = 0} and K₃(ξ) = {z ∈ B₃ : κ₁₃(ξ, z) = 0}.

Moreover:
- **(a) Positivity.** W_k is a positive integer-valued function with W_k(−u) = W_k(u), so 𝐖_k = [W_k(x − y)]_{x, y ∈ U_k} is
  symmetric with positive entries.
- **(b) Rank.** W_k is constant exactly when κ₁₂, κ₁₃ and κ₂₃ all vanish. 𝐖_k has rank one if W_k is constant, and rank at least
  two otherwise.
- **(c) Hard pairs.** If (χ₁, χ₂) is a hard pair of G and S is its slot triple (χ₁, χ₂, (χ₁χ₂)⁻¹), put in pattern form, then W_1
  is not constant. If G has no hard pair, every W_k is constant, for every S.
- **(d) Disjoint unions.** Each term λ_k^n μ_k^m Z_{W_k}(Γ) is multiplicative over disjoint unions of multigraphs.

**What it says.** On these manifolds, counting maps into any class-(K) group is a positive combination of r graph partition
functions, one per meridian character. A hard pair makes the first one a Bulatov–Grohe partition function of rank at least two.
Ticket C turns this into hardness.

## Nearest known result

- **`COPRIME-CLASS2-20261026-001C` §§1–3.** The count over a character and its graded components. They are used here unchanged.
- **`COPRIME-CLASS2-20261026-001B`, part (b).** Duality: the obstruction vanishes iff the triple form kills it. That proof is
  written for Heisenberg groups but uses only Poincaré duality with local coefficients.
- **`COPRIME-CLASS2-20261026-001D` §1.** The Heisenberg gadgets. They are special cases of the template:
  - D's pattern 2 is P2 with B₁ = B₂ two-dimensional, B₃ = 0 and A₂₃ = 0. Then W = p + (p² − p)[ξ = 0], giving p^m Z(p², p − 1).
  - D's pattern 4 is P2 with one-dimensional B_s and B_t and κ₁₂ = 0. Then W = p + (p² − p)[u = 0] on U = F_p², giving
    p^{m−n} Z(p², p − 1).
- **`NEXT-DIRECTION-SCAN-20261026-001A` (lane A), finding 2.** It computed this form on 199 cases without a general proof. Theorem A
  proves it, with the sectors made explicit.
- **Standard tools.** The Fourier step (a quadratic character sum over a bilinear form) and the rank criterion for convolution
  matrices on finite abelian groups.
- **Novelty.** The theorem is bookkeeping that makes every class-(K) count on gadget manifolds a positive sum of partition
  functions. It makes no complexity claim. Folklore risk: medium.

## Proof

### 1. The count over one character

**Lifting** (`COPRIME-CLASS2-20261026-001C` §1).
- Maps π → G over ψ are pairs: a cocycle c ∈ Z¹(π; B_ψ) whose class o(c) = [β_*(c ⌣ c)] ∈ H²(π; A_ψ) vanishes, and a lift. The
  lifts form a torsor under Z¹(π; A_ψ).
- Changing c by a coboundary conjugates the map inside G/A, which preserves liftability. So o depends only on x = [c].
- Hence |Hom_ψ| = |Z¹(π; A_ψ)| · |B¹(π; B_ψ)| · #{x ∈ H¹(π; B_ψ) : o(x) = 0}.

**Changing the section.** For p odd we may take β = κ/2.
- Let q(b) = β(b, b)/2. Then (a, b) ↦ (a − q(b), b) is an isomorphism from N with cocycle β onto N with cocycle κ/2. The key
  identity is q(b + b′) = q(b) + q(b′) + (β(b, b′) + β(b′, b))/2.
- q is equivariant, so the isomorphism commutes with the action.
- With β = κ/2 and x = Σ_χ x_χ, x_χ ∈ H¹(M; F_{χψ}) ⊗ B_χ:

  o(x) = ½ Σ_{χ, χ′} κ_*(x_χ ⌣ x_χ′) ∈ ⊕_ρ H²(M; F_{ρψ}) ⊗ A_ρ.

  This uses H²(π) ↪ H²(M).

**Duality** (as in `COPRIME-CLASS2-20261026-001B` (b)). Poincaré duality pairs H²(M; F_{ρψ}) perfectly with H¹(M; F_{ρ⁻¹ψ}). So
o_ρ(x) = 0 exactly when the following vanishes for every w ∈ H¹(M; F_{ρ⁻¹ψ}) and φ ∈ A_ρ*:

  ⟨o(x), w ⊗ φ⟩ = ½ Σ_{χχ′ = ρ} Σ_{i,j} T(v_i, v′_j, w) φ(κ(b_i, b′_j)),

where x_χ = Σ v_i ⊗ b_i and x_χ′ = Σ v′_j ⊗ b′_j.

**The characters.**
- Hom(π, Z/r) = {ψ_k = kψ}, and H¹(M; F_{χψ_k}) = V_{χ^k} (zero if χ^k = 1).
- The π-module B_{ψ_k} is B with π acting through ψ followed by the k-th power of the action, and the same holds for A. So the
  count over ψ_k for G is the count over ψ for G^{(k)}, constants included.
- Concretely, group the χ by θ = χ^k and the tests by θ″ = ρ^k. Testing all φ ∈ ⊕_{ρ^k = θ″} A_ρ* against one test space
  V_{θ″⁻¹} is the same as testing each ρ.

It is therefore enough to treat ψ itself for an arbitrary class-(K) group G′ (= G^{(k)}).

### 2. ψ itself on a gadget manifold

Variables are x_θ ∈ V_θ ⊗ B′_θ.

**Step 1: free parts and vacuous tests.** T vanishes off the permutations of S, so a term T(x_θ, x_θ′, w) with w ∈ V_{ρ⁻¹} and
θθ′ = ρ is nonzero only if (θ, θ′, ρ⁻¹) is a permutation of S.
- Components x_θ with θ ∉ S occur in no condition. They contribute p^{d_θ · dim B′_θ}.
- Tests with ρ⁻¹ ∉ S are vacuous.

**Step 2: the remaining conditions.**
- **Notation.** X_u ∈ B′_{s₁} is the coefficient of x on the coordinate x_u. Likewise Y_e is the coefficient on y_e (or p_e), and
  Z_e on t_e (or w_e, or q_e). Put L_e = X_u − X_v.
- **Expansion.** Cofactor expansion of det[f_a(v), f_a(v′), f_a(w)] along the last column gives

  (f₁ ∧ f₂ ∧ f₃)(v, v′, w) = f₁(w) (f₂ ∧ f₃)(v, v′) − f₂(w) (f₁ ∧ f₃)(v, v′) + f₃(w) (f₁ ∧ f₂)(v, v′).

  Also ½ Σ_{i,j} (f_a ∧ f_b)(v_i, v_j) κ(b_i, b_j) = ½ (κ(F_a, F_b) − κ(F_b, F_a)) = κ(F_a, F_b), where F_a = Σ_i f_a(v_i) b_i.
- **The pairing.** Summing over the edges,

  ⟨o(x), w ⊗ φ⟩ = Σ_e [ f_{1e}(w) φκ₂₃(Y_e, Z_e) − f_{2e}(w) φκ₁₃(L_e, Z_e) + f_{3e}(w) φκ₁₂(L_e, Y_e) ].

- **The tests match.** A coordinate of V_{s₃} tests A′_{s₃⁻¹} = A′_{s₁s₂}; one of V_{s₂} tests A′_{s₁s₃}; and the x-coordinates
  of V_{s₁} test A′_{s₂s₃}. In P2 and P3 the shared spaces split along the same coordinates.
- **The conditions.** The coordinates f_{2e} and f_{3e} occur in one edge each, and f_{1e}(w) = w_u − w_v. Taking w through the
  coordinate vectors gives:
  - κ₁₂(L_e, Y_e) = 0 for every edge;
  - κ₁₃(L_e, Z_e) = 0 for every edge;
  - Σ_e ε_{e,w} κ₂₃(Y_e, Z_e) = 0 at every vertex w, with ε = +1 at the tail and −1 at the head.
- **Coverage.** The coordinates X, Y, Z exhaust the slot components in every pattern.

  So the count over ψ is Π_{θ ∉ S} p^{d_θ dim B′_θ} · N_tmpl(Γ), where N_tmpl is the number of (X, Y, Z) satisfying these
  conditions.

**Step 3: Fourier.**
- Write each vertex condition as an average of characters:

  Π_w [·] = |A₂₃|^{−n} Σ_{φ: V → A₂₃*} Π_e e_p((φ_u − φ_v)(κ₂₃(Y_e, Z_e))).

- The pairs (Y_e, Z_e) are then independent across edges, so

  N_tmpl = |A₂₃|^{−n} Σ_{(X, φ)} Π_e W(X_u − X_v, φ_u − φ_v), with W(ξ, η) = Σ_{y ∈ K₂(ξ), z ∈ K₃(ξ)} e_p(η κ₂₃(y, z)).

- For a bilinear form g on K₂ × K₃, summing over z gives |K₃| [g(y, ·) = 0], and summing over y then gives |K₂| p^{−rank g}. This
  is the closed form of W.
- K_i(−ξ) = K_i(ξ), and negating η does not change the rank. So W is even, and the edge orientation does not matter.

**Step 4: assembling.**
- |B¹(π; B_{ψ_k})| = Π_{χ^k ≠ 1} |B_χ|, since B¹ ≅ B/B^π. The same holds for A.
- |H¹(π; A_{ψ_k})| = Π_ρ p^{d_{ρ^k} dim A_ρ}, with d_1 = 0.
- So the total is Σ_k c_k p^{E_k(n, m)} Z_{W_k}(Γ), where

  E_k = Σ_ρ d_{ρ^k} dim A_ρ + Σ_{χ^k ∉ S, χ^k ≠ 1} d_{χ^k} dim B_χ − n dim A₂₃^{(k)}.

- By hypothesis 1, each d_θ = α_θ n + β_θ m with no constant term. So E_k = a_k n + b_k m, and λ_k = p^{a_k}, μ_k = p^{b_k}.

### 3. The weights

**(a) Positivity.** Shown in step 3.

**(b) Constancy.**
- If all three pairings vanish, then K₂ = B₂, K₃ = B₃ and the rank is 0, so W ≡ |B₂| |B₃|.
- Conversely, suppose some pairing is nonzero:
  - if κ₁₂(ξ, ·) ≠ 0 for some ξ, then |K₂(ξ)| < |B₂|, so W(ξ, 0) < W(0, 0);
  - κ₁₃ works the same way;
  - if κ₂₃(y, z) ≠ 0, choose η with η(κ₂₃(y, z)) ≠ 0. Then W(0, η) < W(0, 0).

**(b) Rank.**
- 𝐖 is convolution by W on the abelian group U, so its eigenvalues are the Fourier coefficients Ŵ(ω), and
  rank 𝐖 = #{ω : Ŵ(ω) ≠ 0}.
- Ŵ(1) = Σ W > 0.
- A constant W has Ŵ(ω) = 0 for every ω ≠ 1. A nonconstant W has some Ŵ(ω) ≠ 0 with ω ≠ 1, by Fourier inversion.

**(c) Hard pairs.** Take k = 1, so the B_i are the original eigenspaces.
- **Three distinct characters.** S = (χ₁, χ₂, (χ₁χ₂)⁻¹) is P1 with κ₁₂ = κ_{χ₁,χ₂} ≠ 0.
- **χ₁ = χ₂ = s.** Then S = (s, s, s⁻²) is P2 (or P3 when s³ = 1), with κ₁₂ = κ_{s,s} ≠ 0.
- **χ₁ ≠ χ₂ with (χ₁χ₂)⁻¹ ∈ {χ₁, χ₂}.** Say (χ₁χ₂)⁻¹ = χ₁. Then χ₂ = χ₁⁻², and S = (s, s, s⁻²) is P2 with s = χ₁ and
  κ₁₃ = κ₂₃ = κ_{s, s⁻²} ≠ 0. Here s³ ≠ 1 because χ₁ ≠ χ₂. The other case is symmetric, using κ_{χ′,χ}(b′, b) = −κ_{χ,χ′}(b, b′).
- **No hard pair.** Every κ^{(k)}_{s_i, s_j} is a sum of κ_{χ,χ′} with χ^k = s_i, χ′^k = s_j and (χχ′)^k = s_i s_j.
  - These three are nontrivial: s_i s_j = s_l⁻¹ in P1, s² ≠ 1 in P2 and P3, and st = s⁻¹ in P2.
  - So χ, χ′ and χχ′ are nontrivial, and each κ_{χ,χ′} vanishes by hypothesis.

**(d) Disjoint unions.** The sum over σ factorizes over components, and n and m add.

## Check

`check.py` uses numpy and `ck_lib.py` in this directory. It imports `cp_lib.py` read-only from `COPRIME-CLASS2-20261026-001B-P001`
for braid presentations and the Heisenberg evaluation of cup products.

1. **The count formula against independent lifting counts.**
   - **Groups.** Four class-(K) groups that are not Heisenberg groups:
     - p = 5, r = 4: two groups, one with a symmetric diagonal term in the trivial character, one with commutators that involve
       the trivial character;
     - p = 7, r = 6: B characters (3, 2, 6, 6);
     - p = 7, r = 3: three coordinates of one character of order three.
   - **Manifolds.** r-surgeries and rp-surgeries (p-torsion in H₁) on 3₁, 4₁ and 6₁.
   - **Three counts, compared in every sector.**
     - Direct lifting counts: cocycles to G/A enumerated, then the affine lifting system solved with the group law.
     - The cohomological formula with β.
     - The cohomological formula with κ/2.
2. **Gadget models.** Random class-(K) groups, for 16 slot triples at (p, r) = (5, 4), (7, 3), (7, 6), (11, 5), (13, 4),
   (13, 6) and (13, 12), on K₂, P₃, the digon, K₃ and K₂ ⊔ K₂, in every sector. Three counts agree:
   - the direct obstruction count, with no regrouping;
   - the template count;
   - |A₂₃|^{−n} Z_W.
3. **Weights.**
   - W is symmetric and positive.
   - It is constant exactly when its pairings vanish, and rank 𝐖 ≥ 2 exactly then.
   - Every hard pair of a random group gives a nonconstant W_1.
   - Groups without a hard pair give constant weights for every slot triple and sector (negative control).
4. **Disjoint unions and assembly.**
   - Every sector count on K₂ ⊔ K₂ is the square of that on K₂.
   - Σ_k c_k (|H¹(A)| · free factors) N_k equals Σ_k c_k λ_k^n μ_k^m Z_{W_k} on K₂, P₃ and the digon.

## Scope

- **What is proved.** p odd, r | p − 1, and manifolds satisfying the gadget hypotheses. Their realization is ticket C.
- **Cited:** `COPRIME-CLASS2-20261026-001C` §§1–3 (lifting and components); Poincaré duality with local coefficients; the
  injection H²(π) → H²(M).
- **Not covered:** p = 2, where the diagonal terms are not κ-terms, and extension fields.
- No complexity claim here; no P versus NP claim.
