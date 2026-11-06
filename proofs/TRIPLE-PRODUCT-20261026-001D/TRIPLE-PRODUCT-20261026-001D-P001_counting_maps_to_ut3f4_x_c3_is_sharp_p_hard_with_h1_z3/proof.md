# Counting maps to UT₃(F₄) ⋊ C₃ is #P-hard with H₁ = Z/3

Status: Proved

## Standard statement

**The group.** G = UT₃(F₄) ⋊ C₃, where the generator of C₃ acts by (x, y, z) ↦ (ω²x, ω²y, ωz). It has order 192, trivial centre and
Fitting height 2.

**Theorem 5.** The following problem is #P-hard under polynomial-time Turing reductions, using one oracle call:
- **Input:** a knot diagram K.
- **Output:** |Hom(π₁(S³₃(K)), G)|.

Every such manifold has H₁ = Z/3. The problem lies in #P, so it is #P-complete.

**Lemma 6 (Potts gadget).** Let Γ be a multigraph with n vertices, m edges and k connected components. On F_q^{n+2m}, with
coordinates x_v for vertices and p_e, s_e for edges, let

  A_Γ = Σ_{e = uv} (x_u + x_v) ∧ p_e ∧ s_e,

where ∧ is the determinant of the three functionals. Then

  𝒩(A_Γ) = #{(a, b) : A_Γ(a, b, ·) = 0} = q^{2m−n} Z_Γ(q³, q² − 1).

Here Z_Γ(Q, v) = Σ_{σ: V(Γ) → [Q]} Π_{e = uv} (1 + v·[σ(u) = σ(v)]) is the Potts partition function, and

  Z_Γ(Q, v) = Q^k v^{n−k} T_Γ(1 + Q/v, 1 + v).

For q = 4 the Tutte point is (79/15, 16), on the hyperbola (x − 1)(y − 1) = 64.

**Construction 7.**
- Start from 3-surgery on the connected sum of n + 2m figure-eight knots. There V = F₄^{n+2m} and T = 0.
- Make one Borromean move per edge e = uv. Its leaves are:
  - a band sum of loops in the summands of u and v;
  - a loop in the summand of p_e;
  - a loop in the summand of s_e.
- The result is a knot K_Γ, of size polynomial in |Γ|, with T = A_Γ and

  |Hom(π₁ S³₃(K_Γ), G)| = 1 + 128 · 4^{n+2m} · 4^{2m−n} · Z_Γ(64, 15).

**What it says.** With bounded first homology, Fitting height 2 does not separate easy from hard.
- SL(2,3), whose central layer is untwisted, has a quadratic obstruction with a bounded target, and it is polynomial
  (`SL23-BOUNDED-20261025-001A`).
- This group's central layer is twisted. Its obstruction is a cubic form on a space that can grow, and Borromean moves steer the
  form's alternating part at will (`TRIPLE-PRODUCT-20261026-001C`). That freedom encodes the Potts model.
- As tested, the line runs between pairwise (quadratic, untwisted) and three-way (cubic, twisted) obstructions.

## Nearest known result

- **Kuperberg and Samperton (Geom. Topol. 22, 2018).** Counting maps to a nonabelian finite simple group is #P-hard, even on integer
  homology spheres. Their Fig. 3 marks nilpotent and solvable targets as open.
- **Galindo (arXiv:2605.06984, 2026).** Turaev–Viro invariants are #P-hard unless the category is trivializable pointed. For Vec_G
  this gives hardness of |Hom(π₁M, G)| for every nonabelian G. The hard instances are graph manifolds whose first Betti number grows
  with the input. They say nothing about bounded homology.
- **Samperton and Weiß (arXiv:2602.02885v2, 2026).**
  - For class-2 nilpotent G with bounded |H²(M, Z(G))|, counting is in FP.
  - Footnote 11: the twisted setting is unclear.
  - Whether class-2 nilpotent targets are hard is left for future work. Galindo has since answered this with unbounded homology.
- **Delaney, Maria and Samperton (arXiv:2311.08514).** They list Vec(G) for nonabelian solvable G as unknown.
- **Burton, Maria and Spreer (2015), following Kirby and Melvin (2004).** TV₄ is #P-hard through cubic forms over Z/2 on 0-surgeries
  of large links. These are a sum over spin structures with unbounded homology, not a homomorphism count with bounded homology.
- **Rossmann (Bull. LMS 2022) and Rossmann–Voll (Mem. AMS 2024).**
  - They study kernel sizes of modules of alternating matrices: commuting-pair counts and average kernel sizes.
  - Rossmann remarks that his polynomial "resembles the Tutte polynomial" but that it is unclear whether this is more than a formal
    similarity.
  - No Potts or Tutte formula for trilinear kernel counts was found.
- **This program.**
  - S₄, of Fitting height 3, is #P-hard on knots (`BOUNDED-H1-20261025-001A`) and on closed manifolds with H₁ = Z/2
    (`CLOSED-H1-20261025-001C`).
  - SL(2,3), of Fitting height 2, is polynomial with bounded homology (`SL23-BOUNDED-20261025-001A`).
- **Novelty.**
  - Candidate new: #P-hardness with bounded first homology for a solvable target of Fitting height 2. This also answers
    Samperton–Weiß's twisted question negatively for this group.
  - Candidate new: Lemma 6.
  - Folklore risk: medium. The gadget is elementary, and the realization is routine given Massuyeau's lemma.

## 1. Proof of Lemma 6

**Setup.**
- Let χ = (−1)^{tr} on F_q. By `TRIPLE-PRODUCT-20261026-001A` §2, 𝒩(A) = |V|⁻¹ Σ_{a,b,c} χ(A(a, b, c)).
- Fix the vertex parts of a, b, c. For an edge e, let u_e = (ℓ_e(a), ℓ_e(b), ℓ_e(c)) ∈ F_q³, where ℓ_e = x_u + x_v.
- Let P_e ∈ F_q^{3×2} hold the (p_e, s_e)-coordinates of a, b, c. Then A(a, b, c) = Σ_e det(u_e | P_e), and the sum over the P_e
  factorizes over the edges.

**The edge factor.** Σ_P χ(det(u | P)) equals q⁶ if u = 0 and q⁴ otherwise.
- If u = 0, the determinant vanishes.
- If u ≠ 0, choose g ∈ GL₃ with g e₁ = u. Then det(u | P) = det g · det(e₁ | g⁻¹P), and substituting P′ = g⁻¹P reduces to u = e₁.
- For u = e₁, det(e₁ | P′) = p₂s₃ − p₃s₂.
  - The first row of P′ is free: q² terms.
  - Σ_{p₂, s₃} χ(c p₂ s₃) = q for every c ≠ 0, because only p₂ = 0 survives. The same holds for (p₃, s₂).
  - Total: q² · q · q = q⁴.

**Assembling.**
- So Σ_{a,b,c} χ(A) = q^{4m} Σ Π_e (1 + (q² − 1)·[u_e = 0]), summed over the vertex parts.
- Write σ(v) = (a_v, b_v, c_v), one of Q = q³ colours. Then u_e = 0 exactly when σ(u) = σ(v), so the sum is q^{4m} Z_Γ(q³, q² − 1).
- Dividing by |V| = q^{n+2m} gives the lemma.
- The Potts–Tutte identity is the Fortuin–Kasteleyn expansion: Z_Γ(Q, v) = Σ_{S ⊆ E} Q^{k(S)} v^{|S|}.

## 2. Hardness of the Potts point

- **Jaeger, Vertigan and Welsh (1990).** Evaluating T_Γ(x, y) on graphs at a rational point is #P-hard unless (x − 1)(y − 1) = 1
  or (x, y) is one of (1, 1), (−1, −1), (0, −1), (−1, 0), (i, −i), (−i, i), (j, j²), (j², j).
- **Vertigan (2005).** For planar graphs it is still #P-hard off the hyperbolas H₁ and H₂ and those points.
- At (79/15, 16), (x − 1)(y − 1) = 64. So computing Z_Γ(64, 15) = 64^k 15^{n−k} T_Γ(79/15, 16) is #P-hard, even for planar Γ.

## 3. The construction (Construction 7)

**The base.**
- Let d = n + 2m and K₀ = #_{i=1}^{d} 4₁, drawn as d figure-eight diagrams in disjoint balls B_i joined by bands.
- M₀ = S³₃(K₀) has H₁ = Z/3, with ψ(meridian) = 1.

**V(M₀) = ⊕ V_i with V_i ≅ F₄, and T₀ = 0.**
- (a) The twisted cohomology of S³₃(K) is that of the exterior X_K. ψ is nontrivial on the boundary torus and on the core of the
  surgery torus, so both have zero twisted cohomology, and Mayer–Vietoris applies.
- (b) X_{K₁#K₂} = X₁ ∪_A X₂, where A is an annulus with meridian core. A has zero twisted cohomology, so restriction is an
  isomorphism H*(X) ≅ H*(X₁) ⊕ H*(X₂). Let V_i be the classes that vanish on the other summands.
  - A product of classes from different summands restricts to zero on every piece, so it vanishes.
  - Hence T = ⊕ T_i.
- (c) For 4₁, V = F₄ and the obstruction bimap is zero (exact computation), so T = 0. This is consistent with Σ₃(4₁) being the
  Hantzsche–Wendt manifold, with H₁ = (Z/4)².

**Vertex and edge loops.**
- A nonzero class is not constant on arcs, since constant cochains are coboundaries.
- So in each B_i there are arcs a_i, b_i with c(x_{a_i}) ≠ c(x_{b_i}) (the check lists them for 4₁).
- Let γ_i be the band loop that encircles a_i positively and b_i negatively.
  - ψ(γ_i) = 1 − 1 = 0.
  - It bounds a small disk meeting K₀ in two points.
  - λ_{γ_i}(c) = c(x_{a_i}) + c(x_{b_i}), since c(x⁻¹) = ω c(x) when ψ(x) = 1. This is nonzero on V_i.
  - It vanishes on V_j for j ≠ i, because γ_i lies in X_i.
- So x_i := λ_{γ_i} is a basis of V*.

**One Borromean move per edge e = uv.**
- Γ_e is a Y-graph with three leaves:
  - L₁ is a band sum of parallel copies of γ_u and γ_v, along a band β_e whose core links K₀ a multiple of 3 times. Then
    λ_{L₁} = x_u + ω^{2 lk(β_e)} x_v = x_u + x_v.
  - L₂ is a parallel copy of γ_{p_e}.
  - L₃ is a parallel copy of γ_{s_e}.
- The Γ_e are pairwise disjoint.
- L₂ bounds a small disk that meets only K₀, because the summand p_e belongs to e alone.

**The result.**
- By `TRIPLE-PRODUCT-20261026-001C` (Theorem 2, applied once per edge, and Corollary 4), the result is S³₃(K_Γ) for a knot K_Γ.
- It has H₁ = Z/3, V = F₄^d, and T = Σ_e (x_u + x_v) ∧ x_{p_e} ∧ x_{s_e}, which is A_Γ in the basis (x_i).
- **The band twists must be normalized.** Gains ζ_e on the triangle, giving x_u + ζ_e x_v, reproduce the graphic count when their
  product is 1. Otherwise the count changes (the check: 45162496 against 31554496).

**Size.**
- K₀ has 4d crossings.
- Each band and each Y-graph crosses O(d) arcs.
- Habiro's clasper calculus draws Y-surgery along Γ_e as a tangle replacement on the strands through its leaf disks (2, 4 and 2
  points), dragging parallel copies of the bands and edges along.
- So K_Γ has O(m(n + m)) crossings and is computable in polynomial time.

## 4. Proof of Theorem 5

- Given Γ, build K_Γ and make one oracle query for |Hom(π₁ S³₃(K_Γ), G)|.
- By `TRIPLE-PRODUCT-20261026-001A` (d), the answer is 1 + 128 · 4^d · 𝒩(A_Γ).
- By Lemma 6, that is 1 + 128 · 4^d · 4^{2m−n} Z_Γ(64, 15). Solving for Z_Γ(64, 15) gives T_Γ(79/15, 16), which is #P-hard by §2.
- Membership in #P: a homomorphism is a polynomial-size certificate checked relator by relator.

## 5. What changes for the bounded-homology line

| Target | Fitting height | Obstruction with bounded H₁ | Complexity |
| --- | --- | --- | --- |
| Abelian-by-nilpotent | ≤ 2 | none beyond linear algebra | polynomial (`BOUNDED-H1-20261025-001B`) |
| SL(2,3) and class (H) | 2 | untwisted, quadratic, bounded target | polynomial (`SL23-BOUNDED-20261025-001A`) |
| UT₃(F₄) ⋊ C₃ | 2 | twisted, cubic, alternating part free | **#P-hard** (this proof) |
| S₄, GL(2,3), 2O | 3 | bicycle law (a level whose dimension depends on the level below) | #P-hard (`BOUNDED-H1-20261025-001A`, `CLOSED-H1-20261025-001C`, `SL23-BOUNDED-20261025-001B`) |

- **The line, as tested.** The Fitting height does not mark it. What marks it is whether the top obstruction is pairwise with a
  bounded target, or three-way with a free alternating part.
- **The program's 2-versus-3 reading.** Pairwise interaction is countable by quadratic Gauss sums; three-way interaction, written as
  determinants of leaf functionals, encodes the Potts model. This is an interpretation, not part of the theorem.

## Check

`check.py` uses the standard library and imports `tp_lib.py` read-only from `TRIPLE-PRODUCT-20261026-001A-P001`. It runs in
about 30 s; results are in `result.json`.

1. **Lemma 6, by brute force.**
   - For q = 2 and q = 4, on K₂, K₂ plus an isolated vertex, P₃, the digon and K₃, the count Σ_a q^{corank A(a, ·, ·)} is computed
     over all a.
   - It equals q^{2m−n} Z_Γ(q³, q² − 1). For q = 4, K₃ gives 45162496 = 4³ · 705664.
   - Z_Γ, computed by enumerating colourings, equals the Tutte expression at (11/3, 4) and (79/15, 16).
2. **Figure-eight sums.** For (4₁)^{#k}, k = 1, …, 9: dim_{F₄} V = k, B = 0 and H₁ = Z/3. The check also lists the arc pairs of 4₁
   that give band loops with nonzero functional.
3. **End to end.**
   - Four knots realize cycle configurations:
     - two triangles on (4₁)^{#9}, each with three insertions, whose leaf spans have ranks 3, 3, 3, pairwise 6 and total 8;
     - two digons on (4₁)^{#6}, with spans 3, 3 and sum 5.
   - Their obstruction kernels match the predicted form for every a.
   - Their counts equal the gadget values 45162496 and 326656, so |Hom| = 1515401900982273 and 171261820929.
   - These configurations were found by a search over insertion windows, not built by the band recipe of §3. They are equal to the
     gadget up to a change of basis, which the rank pattern certifies.
4. **Control.** On the triangle, balanced gains (ω, ω², 1) give the graphic count. Unbalanced gains (1, 1, ω) give 31554496.

## Scope

- **What is shown.** #P-hardness of exact counting, under Turing reductions with one oracle call, for 3-surgeries on knots given by
  diagrams, all with H₁ = Z/3.
- **Cited, not proved:**
  - Jaeger–Vertigan–Welsh (1990) and Vertigan (2005);
  - Habiro's clasper calculus for drawing the moves;
  - the results cited by `TRIPLE-PRODUCT-20261026-001A` and `TRIPLE-PRODUCT-20261026-001C`.
- **Not claimed:**
  - The explicit band recipe was not run end to end. The computed instances use leaf configurations found by search.
  - Approximate counting (the ferromagnetic Potts point suggests #BIS-type questions) and decision versions.
  - P versus NP; physics.
