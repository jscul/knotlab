# With a hard pair, Heisenberg counting is #P-hard with H₁ = Z/r

Status: Proved

## Standard statement

**The group.** p is an odd prime, r ≥ 2 divides p − 1, and α, β ∈ F_p^× satisfy α^r = β^r = 1. G = H(F_p) ⋊ C_r, where the
generator acts by (x, y, z) ↦ (αx, βy, αβz).

**Theorem 3.** Suppose α ≠ 1, β ≠ 1 and αβ ≠ 1, the "hard pair" condition. Then the following problem is #P-hard under
polynomial-time Turing reductions:
- **Input:** a knot diagram K.
- **Output:** |Hom(π₁(S³_r(K)), G)|.

Every such manifold has H₁ = Z/r.

**Corollary 4 (dichotomy).** For these groups and closed orientable 3-manifolds with bounded |H₁|, counting is:
- polynomial if α = 1, β = 1 or αβ = 1 (`COPRIME-CLASS2-20261026-001C`);
- #P-hard otherwise.

**Corollary 5 (knot groups).** The same holds for |Hom(π₁(S³ ∖ K), G)|, with knots given by diagrams.
- So Rowell's Conjecture 3.2(b), which asks for a polynomial algorithm for exact counting on link groups and every finite solvable G,
  fails for each of these groups unless every #P function is computable in polynomial time.
- For the case q = 4, r = 3 it fails because |Hom(π₁(S³ ∖ K), G)| = |Hom(π₁ S³₃(K), G)| + 63.

**The case q = 4, r = 3** (`TRIPLE-PRODUCT-20261026-001D`) is the same pattern over F₄.

**The four coincidence patterns of (α, β, γ), with γ = (αβ)⁻¹, and their gadgets.**

| Pattern | Steerable forms on V_α × V_β × V_γ | Gadget (graph with n vertices, m edges) | 𝒩 | Tutte point |
| --- | --- | --- | --- | --- |
| 1: α, β, γ distinct | all trilinear forms | the alternating form A = Σ_e (x_u − x_v) ∧ p_e ∧ s_e, transported to the three slots | p^{2m−n} Z(p³, p² − 1) | (1 + p³/(p² − 1), p²) |
| 2: α = β ≠ γ | alternating in (x, y) | Σ_e w_e · ((x_u − x_v) ∧ p_e)(x, y), with x, y ∈ X ⊕ P and w ∈ F^m | p^m Z(p², p − 1) | (1 + p²/(p − 1), p) |
| 3: α = β = γ (α³ = 1) | alternating 3-forms | A | p^{2m−n} Z(p³, p² − 1) | (1 + p³/(p² − 1), p²) |
| 4: γ = α ≠ β (or γ = β ≠ α) | alternating in (x, test) | Σ_e s_e(y) · ((x_u − x_v) ∧ p_e)(x, test) | p^{m−n} Z(p², p − 1) | (1 + p²/(p − 1), p) |

- Z(Q, v) = Σ_{σ: V → [Q]} Π_{uv} (1 + v[σ(u) = σ(v)]) is the Potts partition function, equal to Q^k v^{n−k} T(1 + Q/v, 1 + v).
- Both kinds of Tutte point lie on (x − 1)(y − 1) = p³ or p². So they are off the hyperbola H₁ and differ from the special points
  of Jaeger, Vertigan and Welsh.

## Nearest known result

- **`TRIPLE-PRODUCT-20261026-001D`.** The case q = 4, r = 3, with pattern 3.
- **Kuperberg–Samperton (Geom. Topol. 2018), §5.3.** They mark solvable targets as open, and report Rowell's conjecture
  (paraphrased) that #Hom(π₁M, G) is polynomial for link complements and finite solvable G.
- **Rowell, Contemp. Math. 482 (2009), Conjecture 3.2(b).** "Suppose G is solvable. Then there is a polynomial algorithm for exact
  computation of H_L(G)", where H_L(G) = |Hom(π₁(S³ ∖ L), G)|. Corollary 5 shows this fails for every group here unless every #P
  function is computable in polynomial time. The S₄ case already follows from `BOUNDED-H1-20261025-001A` with
  `SL23-BOUNDED-20261025-001B`.
- **Galindo (arXiv:2605.06984).** Hardness for every nonabelian G, with unbounded homology.
- **Moussard (Ann. Fac. Sci. Toulouse 2017).** The rational, infinite-cyclic equivariant Y-surgery formula and its realization
  theorem. Our steering is the finite-cover, F_p analogue (`COPRIME-CLASS2-20261026-001B`).
- **Jaeger–Vertigan–Welsh (1990).** Tutte evaluation is #P-hard off H₁ and the special points.
- **Novelty.**
  - Candidate new: #P-hardness with H₁ = Z/r for every Heisenberg-by-cyclic group with a hard pair, over odd prime fields. With
    twisted central layers, bounded first homology is therefore not enough for Samperton–Weiß-type tractability.
  - Their Theorem 3.3.2 needs bounded H² with the twisted coefficients, and that space is unbounded here. So this does not refute
    their theorem.
  - The four gadgets are elementary character sums.
  - Folklore risk: medium.

## 1. The gadget lemmas

Write χ(z) = e_p(z) and 𝒩 = |V_γ|⁻¹ Σ_{a,b,c} χ(T(a, b, c)) (`COPRIME-CLASS2-20261026-001B`, part b). The sums over the edge
coordinates factor over the edges.

**Patterns 1 and 3 (the alternating form A).**
- This is the computation of `TRIPLE-PRODUCT-20261026-001D` Lemma 6, which works over any F_q.
- Fix the vertex parts and let u_e be the vector of ℓ_e = x_u − x_v evaluated on (a, b, c).
- Summing over the edge pair (p_e, s_e) gives q⁶ if u_e = 0 and q⁴ otherwise. The proof is the GL₃-transitivity argument for
  det(u | P), with det g absorbed because Σ χ(c p s) = q for every c ≠ 0.
- Hence 𝒩 = q^{2m−n} Z(q³, q² − 1).
- In pattern 1 the three slots carry copies of the same coordinates. A is alternating, so every permutation of the slots gives the
  same count.

**Pattern 2.**
- The condition at edge e is ℓ_e(a) p_e(b) − p_e(a) ℓ_e(b) = 0.
- Summed over (p_e(a), p_e(b)) ∈ F², it leaves q² solutions if ℓ_e(a) = ℓ_e(b) = 0 and q otherwise.
- So 𝒩 = q^m Σ_{σ: V → F²} Π_e (1 + (q − 1)[σ(u) = σ(v)]) = q^m Z(q², q − 1).

**Pattern 4.**
- The conditions are:
  - s_e(b) ℓ_e(a) = 0 for each edge;
  - Σ_{e∋w} ±s_e(b) p_e(a) = 0 for each vertex w.
- Summing over p(a) gives q^{m − n + c(supp s)}, because a signed incidence matrix restricted to an edge set S has rank n − c(S).
- Edges with s_e ≠ 0 must be monochromatic. So 𝒩 = q^{m−n} Σ_{S ⊆ E} (q − 1)^{|S|} q^{2c(S)} = q^{m−n} Z(q², q − 1), by the
  Fortuin–Kasteleyn expansion.

**Hardness.** For Q ≥ 2, Z(Q, v) and T at (1 + Q/v, 1 + v) determine each other in polynomial time. Jaeger–Vertigan–Welsh make
these points #P-hard on graphs.

## 2. Base manifolds: twist knots

- The twist knot K_m has Alexander polynomial m t² − (2m + 1) t + m, and genus one. For ζ ∈ F_p^×, ζ ≠ 1, take
  m ≡ ζ(ζ − 1)⁻² (mod p). Then ζ and ζ⁻¹ are roots mod p.
- The Alexander module is cyclic, so V_ζ and V_{ζ⁻¹} of S³_r(K_m), for the meridian character, are one-dimensional. All other
  V_χ vanish.
- In a connected sum, V and T split over the summands (`TRIPLE-PRODUCT-20261026-001D` §3).
- Every component of T₀ vanishes. A component needs three characters with product 1, drawn from one summand's {ζ, ζ⁻¹}. That forces
  ζ³ = 1 on a one-dimensional space, where an alternating form is zero (p odd).
- The base for a gadget is the connected sum of copies of K_α, K_β and K_γ, as many as each slot needs.
  - These are distinct knots, because no two of α, β, γ are inverse to each other: α = β⁻¹ means αβ = 1; α = γ⁻¹ means β = 1;
    β = γ⁻¹ means α = 1.
  - Under the meridian character, the base has H₁ = Z/r.

## 3. Realizing the gadget: the explicit construction

This section repairs the sketch of `TRIPLE-PRODUCT-20261026-001D` §3, following the review in `COPRIME-CLASS2-20261026-001A`
(items R1a–c, m1).

**The construction**, given a graph with n vertices and m edges and a pattern from §1:

1. **Base diagram.**
   - Draw K₀ = #_i K_{m_i} as twist-knot diagrams in disjoint balls B_i along a line, joined by bands.
   - There is one summand for each coordinate of each slot of the gadget, of the type needed for that slot's character (§2).
   - Fix a base point above the diagram, and for each ball a reference path from the base point into B_i.
2. **A reference loop in each summand.**
   - In B_i, choose two arcs a_i, b_i of the summand's diagram whose ζ-cocycle values differ. Such arcs exist because a nonzero class
     is not constant on arcs: constant cochains are coboundaries.
   - Let γ_i be the band loop that encircles a_i positively and b_i negatively. It bounds a disk D_i ⊂ B_i meeting K₀ in two points.
   - Its class is x_{a_i} x_{b_i}^{−1}, read through the reference path. Since c(x⁻¹) = −ζ⁻¹ c(x) for a meridian, its functional is
     a ↦ c_a(x_{a_i}) − c_a(x_{b_i}), which is nonzero on V_ζ^{(i)}.
   - The projector of step 3 keeps exactly this V_ζ-part, because P_ζ acts on V_ζ as the identity and on the other eigenspaces as
     zero.
3. **Pure leaves.**
   - Apply the eigenprojector P_ζ = r⁻¹ Σ_j ζ^{−j} t^j. This means a band sum of parallel copies of D_i, the j-th copy repeated
     (r⁻¹ζ^{−j} mod p) times, joined by bands inside B_i that wind j times around a meridian of the summand.
   - The resulting leaf bounds a disk inside B_i ∪ (thin bands) meeting K₀ only in the copies' points. Its functional is supported on
     V_ζ^{(i)}.
4. **Shared functionals.** x_u − x_v is a band sum of the pure leaves of summands u and v, with the second orientation reversed,
   along a band from B_u to B_v.
5. **One Y-graph per decomposable term of the gadget**, with the three leaves that term names (§1, B part (d)).
   - Each edge of the Y-graph runs from the Y-graph's vertex to a leaf.
   - The condition: for each leaf, the closed loop "base point → vertex (along a fixed path) → edge to the leaf → reference path back"
     must have ψ ≡ 0 mod r. Winding the edge once around a strand of K₀ changes ψ by ±1, so the condition can always be met.
   - It makes every leaf functional, read from the vertex, equal to its reference value. Unbalanced choices change the count: the
     control in `TRIPLE-PRODUCT-20261026-001D` gives 31554496 instead of 45162496.
6. **Disjointness.**
   - Leaves are parallel push-offs, so each leaf and leaf disk of one Y-graph is disjoint from all others. Edges avoid other leaves'
     disks by passing around their boundaries, inside the balls.
   - Leaf functionals are evaluated in M, so this rerouting changes nothing.
   - Every leaf carries the framing induced by its disk.
7. **The private leaf.**
   - Every Y-graph has a leaf carrying a private functional: p_e or s_e, or w_e in pattern 2. Its disk lies in balls that no other
     Y-graph uses.
   - Forgetting K, that leaf is a trivial disk-leaf, so Y-surgery along the graph gives back S³: Habiro, Props. 3.3–3.4, applied with
     K forgotten.
   - The diffeomorphism is the identity near a meridian of K, so it carries K to a knot K_Γ with the same Seifert framing. Hence the
     result is S³_r(K_Γ).

**Size.**
- The Y-graphs and their leaf disks are pairwise disjoint, so the surgeries are independent tangle replacements (Habiro).
- Each one replaces the strands through its leaf disks by a Borromean tangle, and its edges and bands cross O(n + m) arcs.
- So K_Γ has O(m(n + m)) crossings and is computable in polynomial time.

**The F₄ case** (`TRIPLE-PRODUCT-20261026-001D`) is the same recipe without projectors. There, a band loop inside B_i is already
supported on the summand's block, and the Galois-conjugate character ψ² contributes equally (`TRIPLE-PRODUCT-20261026-001A` (c)).

## 4. The other characters

- |Hom| = 1 + Σ_{k=1}^{r−1} c_k 𝒩_k, where c_k is a product of |Z¹| and |B¹| sizes that depends only on the dimensions.
- The k-th term reads the component (α^k, β^k, γ^k).
- With pure leaves, a component changes only if it is a permutation of (α, β, γ).
  - In patterns 2–4, multiplicities force the identity roles, so 𝒩_k = 𝒩₁.
  - In pattern 1, a permutation that swaps the x and y roles gives the same zero set. Any other permutation gives the same count
    because the gadget is alternating.
- Every other component keeps its base value 0. Its 𝒩_k is |V_{α^k}| · |V_{β^k}|, or the term has a trivial character and no
  obstruction (H²(M; F_p) = 0 since p ∤ r).
- So |Hom| = 1 + C₁ · 𝒩_gadget + C₂, with C₁ > 0 and C₂ computable from the dimensions.

## 5. Knot groups (Corollary 5)

- Let X be the exterior of K_Γ.
- For a character χ ≠ 1 on the meridian, the boundary torus has no χ-twisted cohomology. So H^i(X; F_χ) = H^i(M; F_χ) for i = 1, 2,
  compatibly with cup products, and the terms of the count with nontrivial characters agree with those of M.
- A term with a trivial character involves H¹(X; F_p) = F_p and H²(X; F_p) = 0. With pure leaves it does not change under the moves.
  In any case it is computable in polynomial time by the algorithm of `COPRIME-CLASS2-20261026-001C`, which needs only bounded
  dim H¹(X; F_p), boundedly many ψ and bounded H²(X; A₁) = 0.
- So |Hom(π₁(X), G)| = (polynomial-time computable) + C₁ · 𝒩_gadget, and the reduction goes through.

## 6. Proof of Theorem 3

1. Given a graph, build K_Γ.
2. Query |Hom| once.
3. Recover 𝒩_gadget from §4, then Z, then the Tutte value.
4. That Tutte value is #P-hard to compute by Jaeger–Vertigan–Welsh, through interpolation, which is a Turing reduction with many
   calls. Ours adds one call per Tutte evaluation.

Membership in #P is clear. Corollary 4 combines this with `COPRIME-CLASS2-20261026-001C`.

## Check

`check.py` uses the standard library and imports `cp_lib.py` read-only from `COPRIME-CLASS2-20261026-001B-P001`, with the
search-and-compare helper `e2e_lib.py` in this directory. It runs in about 60 s.

1. **The gadget lemmas, by brute force.** All four patterns over F₃ and F₅ on K₂, P₃, the digon and K₃, where feasible: 30 cases.
   - Each count equals its Potts value.
   - The Potts values equal the Tutte expressions.
   - Each Tutte point satisfies (x − 1)(y − 1) ∉ {0, 1}.
2. **Twist knots.** For p ∈ {5, 7, 11, 13}, and 3₁, 4₁, 5₂, 6₁ (m = −1, 1, −2, 2): the twisted cohomology is nonzero exactly at the
   roots of m t² − (2m + 1) t + m, in dimension one.
3. **End to end.** Knots with Borromean insertions found by search, realizing a gadget up to a change of basis:
   - p = 7, r = 3, pattern 3: a digon, 𝒩 = 46101601;
   - p = 5, r = 4, pattern 4: a triangle, 𝒩 = 25925;
   - p = 5, r = 4, pattern 2: a triangle, 𝒩 = 3240625.

   Each matches the gadget value, and every first argument a has the predicted obstruction kernel.
4. **Knot groups.**
   - The counting formula on knot groups agrees with brute-force enumeration for (2, 2) at p = 7, and (2, 2) and (2, 4) at p = 5,
     on 3₁ and 4₁: 1029, 1029, 500, 4500, 500, 4500.
   - For UT₃(F₄) ⋊ C₃, |Hom(π₁(S³ ∖ K), G)| − |Hom(π₁ S³₃(K), G)| = 63 on 3₁, 4₁, 5₂ and 3₁ # 3₁. This uses `tp_lib.py` from
     `TRIPLE-PRODUCT-20261026-001A`, read-only.

## Scope

- **What is shown.** #P-hardness under Turing reductions, one call to the counting oracle per Tutte evaluation, for odd prime fields,
  on r-surgeries of knots and on knot groups.
- **Cited:**
  - Jaeger–Vertigan–Welsh;
  - Massuyeau's lemma (through B);
  - Habiro, Props. 3.3–3.4 (disk-leaves with their disk framing);
  - Rolfsen and others for the Alexander polynomials of twist knots.
- **Not run end to end.** Pattern 1 (needs r ≥ 6), and the pure-leaf recipe itself. The computed instances use bundle leaves found by
  search.
- **Not covered:**
  - extension fields other than F₄ with r = 3;
  - q = 2^k in patterns 2 and 4, where the Bockstein diagonal can be nonzero;
  - general class-2 groups N (the conjecture);
  - approximate counting.
