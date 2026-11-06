# The moves force a groupoid

Status: Proved

## Standard statement

**Laws.**
- Let L be a finite set of labels and R ⊆ L³ a **triangle rule**. In an ordered triangulation, a triangle with vertices a < b < c
  reads (x_ab, x_bc, x_ac) and is allowed when that triple lies in R.
- A labelling of the six edges of a tetrahedron is **allowed** when its four faces are.
- The **pure counting law** of R assigns to an ordered triangulation its number of edge labellings with every triangle allowed.

**The ordered identities**, as in `TWIST-3D-20261025-001A`, with vertices 0 < 1 < 2 < 3 < 4 of a 4-simplex:
- **1–4.** Every allowed tetrahedron, placed as the facet opposite a vertex r ∈ {0, …, 4}, extends in exactly μ ways. An extension is a
  labelling of the four edges at r putting the six triangles through r in R.
- **2–3.** Fix p < q and let τ be the triangle on the other three vertices. Take any labelling of the nine edges other than pq that
  puts in R the six triangles avoiding p or q, τ excepted. The number of labels of pq putting the three triangles through p and q in R
  must equal λ·[τ ∈ R].
- The law **survives** when both hold with constants λ, μ ≥ 1.

**Further definitions.**
- R is **deterministic** when (x, y, z) and (x, y, z′) in R force z = z′. Then R is the graph of a partial operation, written x·y or xy.
- The **reduced rule** R° is the set of triangles that are faces of allowed tetrahedra.

**Theorem 1 (reduction).** For every rule R, deterministic or not, the move identities of R and of R° are the same statements. In
particular R survives if and only if R° does, with the same constants.

**Theorem 2 (classification).** Let R be deterministic with at least one allowed tetrahedron. The law survives if and only if R° is the
set of composable triples (f, g, f∘g) of a finite groupoid 𝒢 whose connected components 𝒢ᵢ all have the same value
|Ob 𝒢ᵢ|·|Gᵢ|. Here the labels are the arrows, the objects are unlabelled, and Gᵢ is the vertex group. Then λ = 1 and μ is that common
value.

**Corollary 3 (the invariant).** Let M be a closed connected oriented 3-manifold with an ordered triangulation having V vertices.
For a surviving deterministic law,

  #labellings = μ^V · Σᵢ |Hom(π₁(M), Gᵢ)| / |Gᵢ|.

**Corollary 4 (what deterministic laws see).**
- (a) The values of all surviving deterministic laws on M determine, and are determined by, the numbers |Hom(π₁(M), G)| over finite
  groups G.
- (b) Cited background: two such manifolds therefore get equal values from every deterministic law exactly when their fundamental
  groups have the same finite quotients.
- (c) Every lens space L(p, q) gets the same values for all q, because π₁ = Z/p. For example, L(5,1) and L(5,2) agree although they
  are not homotopy equivalent.
- (d) The Sol torus bundles of Funar and the Seifert fibred pairs of Hempel are not separated by any deterministic law.

## Nearest known result

- **The forward direction is classical.**
  - Dijkgraaf and Witten (1990) gave the state sum of a finite group, and Wakui (1992) its form on ordered triangulations.
  - With no cocycle the invariant is |Hom(π₁(M), G)|/|G|.
  - Freed and Quinn (1993), and later homotopy-cardinality treatments, give the groupoid version.
- **The nearest converse** is the Duskin–Glenn characterization (see [nLab: hypergroupoid](https://ncatlab.org/nlab/show/hypergroupoid)).
  A simplicial set is the nerve of a groupoid exactly when it is 2-coskeletal and its 2- and 3-horns have unique fillers.
- **What differs here.**
  - The vertices carry no labels, so objects are not given.
  - The hypotheses are the counting identities of the moves, not horn conditions.
  - The rule may be partial and may contain triangles that never occur.
  - The proof recovers objects as the idempotent labels.
- **Novelty.** The bounded scan (`research/PATTERN-3D-20261025-001/scan.md`) found no statement of this converse. Folklore risk is
  medium: the conclusion is natural and the ingredients are standard.

## Notation for deterministic rules

**Paths.**
- When R is deterministic, an allowed tetrahedron is determined by its **path** (x₀₁, x₁₂, x₂₃) = (a, b, c), since x₀₂ = ab,
  x₁₃ = bc and x₀₃ = (ab)c = a(bc).
- Write (a, b, c) for it. It is allowed if and only if ab, bc, (ab)c and a(bc) are defined and (ab)c = a(bc).
- A 4-simplex labelling is allowed when all ten triangles are in R, equivalently when its five facets are allowed. It too is
  determined by its path (a, b, c, d).
- Its facets, named by the omitted vertex, are F₄ = (a, b, c), F₀ = (b, c, d), F₁ = (ab, c, d), F₂ = (a, bc, d) and F₃ = (a, b, cd).

**Sets attached to triangles and labels.** For a triangle (x, y, xy) ∈ R°:
- Right(x, y) = {c : (x, y, c) allowed};
- Left(x, y) = {a : (a, x, y) allowed}.

For a label b:
- P_R(b) = {c : (b, c, bc) ∈ R°};
- P_L(b) = {a : (a, b, ab) ∈ R°}.

## Proof of Theorem 1

**Both sides involve only allowed tetrahedra.**
- **The 1–4 identity.** The given tetrahedron is allowed. Every counted extension makes all five facets of the 4-simplex allowed. So
  every triangle involved is in R°, and the count is the same for R and R°.
- **The 2–3 identity, old side.** If the six boundary triangles and τ are in R, the two old facets are allowed and all seven
  triangles are in R°.
- **The 2–3 identity, new side.** If a label of pq puts the three interior triangles in R, the three new facets are allowed. Each has
  two boundary faces and two interior faces. So the nine boundary and interior triangles are in R°.

**The two identities agree.** Take a labelling of the nine edges.
- **Boundary in R°.** Counted labels are the same for R and R°. Moreover τ ∈ R implies τ ∈ R°, because the old facets are then
  allowed.
- **Boundary in R but not in R°.** Then τ ∉ R and no label completes the interior, since either would put the boundary in R°. The
  identity of R reads 0 = λ·0, and the hypothesis of the identity of R° fails.
- **Boundary not in R.** Both hypotheses fail.

R and R° also have the same allowed tetrahedra. ∎

## Proof of Theorem 2

By Theorem 1 we may assume R = R°. Then every label lies on an allowed tetrahedron, and P_R(b) = {c : bc defined}.

**Lemma 2.1 (λ = 1, unique completion, exclusion).**
- Some allowed tetrahedron exists and μ ≥ 1, so allowed 4-simplices exist.
- For p = 1 and q = 3 the triangle (1, 2, 3) forces x₁₃ = x₁₂x₂₃, so the 2–3 count is at most 1.
- An allowed 4-simplex gives a boundary labelling with τ ∈ R and count 1. Hence λ = 1, and for every pair p < q:
  - **(U)** two allowed facets opposite p and q that agree on τ extend to exactly one allowed 4-simplex;
  - **(V)** if the six boundary triangles are in R and τ ∉ R, no label of pq completes the interior.

  Consequently, if nine of the ten triangles of a 4-simplex labelling are in R, so is the tenth. Take {p, q} to be the vertices off
  the tenth triangle and apply (V).

**Lemma 2.2 (moving a triangle).** If t ∈ R° is the face opposite vertex m of an allowed tetrahedron, then for each
j ∈ {0, 1, 2, 3} it is the face opposite vertex j of some allowed tetrahedron.

*Proof.*
- **The extension.** Insert a new vertex at position r ∈ {0, …, 4} by an extension (μ ≥ 1). The old tetrahedron becomes facet r of an
  allowed 4-simplex. Its vertex m becomes m′ = m if m < r and m′ = m + 1 if m ≥ r.
- **Where t goes.** The triangle t lies in exactly two facets, r and m′. In facet m′ it is the face opposite the vertex r. That
  vertex sits at position r if r < m′, and r − 1 if r > m′.
- **The positions reached.**
  - For r ≤ m this gives position r, so the positions 0, …, m.
  - For r > m it gives r − 1, so the positions m, …, 3.

  Together these are all positions. ∎

**Lemma 2.3 (fibres).** For every (x, y, xy) ∈ R, |Right(x, y)| = |Left(x, y)| = μ.

*Proof.*
- **An allowed tetrahedron with t on the right.** By Lemma 2.2 the triangle is the face on vertices 1, 2, 3 of some allowed
  (z, x, y). By the 1–4 identity at r = 4, (z, x, y) has μ extensions (z, x, y, d).
- **Extensions give Right.** Each extension has facet F₀ = (x, y, d), so d ∈ Right(x, y).
- **Right gives extensions.** If (x, y, d) is allowed, the facets F₄ = (z, x, y) and F₀ = (x, y, d) agree on the triangle on 1, 2, 3,
  namely (x, y, xy). By (U) for the pair (0, 4) they extend to an allowed 4-simplex, which is (z, x, y, d).
- **Conclusion.** So d ↦ (z, x, y, d) is a bijection from Right(x, y) to the extensions, and |Right(x, y)| = μ. The 1–4 identity at
  r = 0 gives |Left(x, y)| = μ in the same way. ∎

**Lemma 2.4 (shifts).** Let (a, b, c) be allowed.
- The map d ↦ cd is a bijection from Right(b, c) to Right(a, b).
- The map z ↦ za is a bijection from Left(a, b) to Left(b, c).

*Proof.*
- **The first map lands in Right(a, b).** For d ∈ Right(b, c), the facets (a, b, c) and (b, c, d) agree on (b, c, bc). By (U) for
  (0, 4), the 4-simplex (a, b, c, d) is allowed. Its facet F₃ = (a, b, cd) shows cd ∈ Right(a, b).
- **The first map is injective.** If cd = cd′ = k, the 4-simplices (a, b, c, d) and (a, b, c, d′) share the facets F₄ = (a, b, c) and
  F₃ = (a, b, k). By the uniqueness in (U) for (3, 4), d = d′.
- **Both sets have μ elements** by Lemma 2.3, so the first map is a bijection.
- **The second map** is the mirror argument: (U) for (0, 4) and the facet F₁ = (za, b, c) show it lands in Left(b, c), and (U) for
  (0, 1) gives injectivity. ∎

**Lemma 2.5 (blocks).** Fix a label b.
- The sets Right(a, b), for a ∈ P_L(b), are pairwise equal or disjoint, and they cover P_R(b).
- Hence (a, b, c) is allowed exactly when a and c lie in matching blocks Aᵢ × Cᵢ, and |Aᵢ| = |Cᵢ| = μ.

*Proof.*
- **Equal or disjoint.** Suppose k ∈ Right(a, b) ∩ Right(a′, b) and c ∈ Right(a′, b).
  - Lemma 2.4 for (a′, b, c) gives d ∈ Right(b, c) with cd = k.
  - The facets F₀ = (b, c, d) and F₃ = (a, b, cd) = (a, b, k) agree on the triangle on 1, 2, 4, namely (b, cd, b(cd)). By (U) for
    (0, 3), the 4-simplex (a, b, c, d) is allowed, so c ∈ Right(a, b).
  - Thus Right(a′, b) ⊆ Right(a, b), and equality follows from Lemma 2.3.
- **Covering.** For c ∈ P_R(b), Lemma 2.3 gives Left(b, c) ≠ ∅, so c lies in some Right(a, b).
- **Matching blocks.** For a block C, let A = {a : Right(a, b) = C}. Then A = Left(b, c) for any c ∈ C, so |A| = μ. ∎

**Lemma 2.6 (units in every block).** For every block (A, C) of b there are d ∈ C with bd = b and e ∈ A with eb = b.

*Proof.*
- **The right unit.**
  - Take a ∈ A. By Lemma 2.2 the triangle (a, b, ab) is the face on vertices 1, 2, 3 of some allowed (z, a, b).
  - Use (z, a, b) as both facet F₄ (on vertices 0, 1, 2, 3, so x₂₃ = b) and facet F₃ (on vertices 0, 1, 2, 4, so x₂₄ = b). The two
    agree on the triangle on 0, 1, 2.
  - By (U) for (3, 4) there is d = x₃₄ making the 4-simplex allowed.
  - Its triangle on 2, 3, 4 reads (b, d, b), so bd = b. Its facet F₀ = (a, b, d) is allowed, so d ∈ Right(a, b) = C.
- **The left unit** is the mirror argument, using (U) for (0, 1) with the face on vertices 0, 1, 2 of some allowed (b, c, w), c ∈ C. ∎

**Proposition 2.7 (one block).** Every label has exactly one block. Equivalently, if ab and bc are defined, then (a, b, c) is allowed.

*Proof.*
- **Units from two blocks.** Let (Aᵢ, Cᵢ) and (Aⱼ, Cⱼ) be blocks of b. Take dᵢ ∈ Cᵢ with bdᵢ = b and eⱼ ∈ Aⱼ with eⱼb = b, by
  Lemma 2.6.
- **They form an allowed tetrahedron (eⱼ, b, dᵢ).** Its faces are:
  - (eⱼ, b, b) on 0, 1, 2;
  - (b, dᵢ, b) on 1, 2, 3;
  - (b, dᵢ, b) on 0, 2, 3;
  - (eⱼ, b, b) on 0, 1, 3.

  All four are in R, with x₀₃ = b.
- **Conclusion.** So dᵢ ∈ Right(eⱼ, b) = Cⱼ, the blocks meet, and i = j.
- **Every label has a block.** The sets P_L(b) and P_R(b) are nonempty for every label b.
  - b lies in some triangle of R.
  - If b is a short edge, that triangle and Lemma 2.2 give both sets.
  - If b is the long edge of (x, y, b), move the triangle to the face on vertices 0, 1, 2 of some allowed (x, y, w). Then b = x₀₂ is
    the first edge of (b, w, bw) ∈ R, so P_R(b) ≠ ∅.
  - Moving the triangle instead to the face on vertices 1, 2, 3 of some allowed (z, x, y) gives P_L(b) ≠ ∅. ∎

**Theorem 2, the groupoid.**
- **(a) Units.**
  - Let t(b) be a d ∈ P_R(b) with bd = b, which exists by Lemma 2.6.
  - It is unique. If bd = bd′ = b with d, d′ ∈ P_R(b), choose an allowed (z, a, b). The 4-simplices (z, a, b, d) and (z, a, b, d′) are
    allowed by (U) for (0, 4) and Proposition 2.7. They share the facets F₄ = F₃ = (z, a, b), so d = d′ by (U) for (3, 4).
  - Define s(b) symmetrically.
- **(b) Units are idempotent.** Let d = t(b) and d′ = t(d).
  - Proposition 2.7 for (b, d, d′) gives bd′ = (bd)d′ = b(dd′) = bd = b, with bd′ defined.
  - So d′ = t(b) = d, that is, dd = d.
  - Likewise s(b)s(b) = s(b).
- **(c) Composability.** ab is defined if and only if t(a) = s(b).
  - If t(a) = s(b) = e, Proposition 2.7 for (a, e, b) makes ab = (ae)b defined.
  - Conversely, let ab be defined and e = t(a), and take z with (z, a, e) allowed.
  - Lemma 2.4 gives b = ed for some d ∈ P_R(e).
  - Then eb = e(ed) = (ee)d = ed = b. By uniqueness, e = s(b).
- **(d) Sources and targets of composites.** Proposition 2.7 for (a, b, t(b)) gives (ab)t(b) = ab, so t(ab) = t(b). Likewise
  s(ab) = s(a).
- **(e) Associativity** is Proposition 2.7.
- **(f) A category.**
  - An idempotent u has t(u) = s(u) = u.
  - ub = b whenever s(b) = u, and bu = b whenever t(b) = u.
  - So the idempotents are the objects and s, t are source and target.
- **(g) Inverses.**
  - For c with s(c) = u, the tetrahedron (u, u, c) is allowed. Lemma 2.4 makes d ↦ cd a bijection from P_R(c) onto P_R(u) ∋ u, so
    cd = u for some d.
  - Symmetrically, a left inverse comes from z ↦ zc.
  - In a category, left and right inverses coincide, so this is a groupoid.
- **(h) The value of μ.** μ = |P_R(b)| is the number of arrows out of the object t(b), which is |Ob 𝒢ᵢ|·|Gᵢ| for its component. So
  all components share this value.

**The converse.** Let R be the composable triples of such a groupoid.
- **The 1–4 identity.** An allowed tetrahedron is a chain of three composable arrows. An extension at r chooses the new object in the
  same component (|Ob 𝒢ᵢ| ways) and one new arrow (|Gᵢ| ways), and the other new arrows are then forced. For r = 4, the new arrow goes
  out of the old vertex 3; for 0 < r < 4, out of the vertex before r; for r = 0, into the old vertex 0. So μ = |Ob 𝒢ᵢ||Gᵢ|.
- **The 2–3 identity.**
  - The nine boundary arrows fix the objects. The missing arrow is forced: it is x_ps·x_sq when q ≥ p + 2, and a quotient when
    q = p + 1. So λ = 1 for (U).
  - **Nine triangles force the tenth.** Let the tenth triangle be i < j < k and pick l ∉ {i, j, k}. The three triangles joining l to
    two of i, j, k give x_ik = x_ij x_jk after cancelling the arrow at l:
    - for l < i: x_li x_ik = x_lk = x_lj x_jk = x_li x_ij x_jk;
    - for i < l < j: x_ik = x_il x_lk = x_il x_lj x_jk = x_ij x_jk;
    - for j < l < k: x_ik = x_il x_lk = x_ij x_jl x_lk = x_ij x_jk;
    - for l > k: x_ik x_kl = x_il = x_ij x_jl = x_ij x_jk x_kl.

    This gives (V). ∎

## Proof of Corollary 3

**One component per labelling.**
- A labelling of a connected triangulation by a groupoid rule uses one component.
- Every vertex receives one object, because the arrows at a vertex are related through the triangles of its link, which is a sphere.

**Functors.**
- The labellings are exactly the functors to 𝒢 from the edge-path groupoid of the triangulation. That groupoid has the vertices as
  objects, the edges as generators and the triangles as relations, and it is the fundamental groupoid Π₁(M, V).
- Functors to 𝒢ᵢ are counted by:
  - choosing the objects (|Ob 𝒢ᵢ|^V);
  - choosing the arrows on a maximal tree (|Gᵢ|^(V−1));
  - choosing a homomorphism π₁(M) → Gᵢ.

**Summation.** Summing over components and using |Ob 𝒢ᵢ||Gᵢ| = μ gives the formula. ∎

## Proof of Corollary 4

- **(a)** The one-object groupoid G gives |Hom(π₁(M), G)|/|G|, and every value is a sum of such terms.
- **(b)** Cited background:
  - P. Hall (1936): the numbers |Hom(Γ, G)| determine the numbers of epimorphisms by Möbius inversion over subgroups.
  - Dixon, Formanek, Poland and Ribes (1982): for finitely generated groups, having the same finite quotients is equivalent to having
    isomorphic profinite completions.
- **(c)** π₁(L(p, q)) ≅ Z/p. Whitehead's classical theorem: L(p, q) and L(p, q′) are homotopy equivalent exactly when
  qq′ ≡ ±n² (mod p). The number 2 is not ±n² (mod 5).
- **(d)** Cited:
  - Funar, *Torus bundles not distinguished by TQFT invariants*, Geom. Topol. 17 (2013);
  - Hempel, *Some 3-manifold groups with the same finite quotients*, arXiv:1409.3509.

  Their pairs have fundamental groups with the same finite quotients. ∎

## Check

`check.py` uses the standard library only and runs in about 30 s. Its result is `result.json`.

**1. Every partial operation on one, two or three labels: 2 + 81 + 262,144 tables.**
- **Survival.** A path-based 1–4 test decides survival. A generic propagation test confirms the 2–3 identity for every table passing
  1–4, and agrees with the fast test on 1,500 random tables.
- **Survivors.** 3,902 tables survive. Their reduced rules are groupoids with λ = 1 and μ = objects × group order:

  | Reduced rule | Tables |
  | --- | --- |
  | One constant label | 3,500 |
  | Two constants | 289 |
  | Three constants | 54 |
  | Z₂ | 56 |
  | Z₃ | 3 |

- **The converse.** The 8 tables that are groupoids with equal values and use all their labels each survive.

**2. Groupoids with up to eight arrows.**
- Twenty-three groupoids whose components share one value survive with λ = 1 and μ = objects × group order. They are:
  - every group of order at most 8, including S₃, D₄ and Q₈;
  - 2 objects × 1 and 2 objects × Z₂;
  - two and four constants;
  - Z₂ + Z₂, Z₃ + Z₃ and Z₄ + Z₂×Z₂;
  - Z₂ + the pair groupoid, and two pair groupoids.
- Three unions with unequal values fail.

**3. Controls, all of which fail as required:**
- the pair groupoid with its identities merged;
- two pair groupoids with two arrows merged into one label;
- the monoid {0, 1} under multiplication;
- the projection table x·y = x, which passes 1–4 and fails 2–3;
- Z₂ plus a constant;
- the Z₃ table with one entry changed.

**4. The count formula on 40 sampled ordered triangulations** (1 to 4 tetrahedra, H₁ ∈ {0, Z₂, Z₂², Z₃, Z₄, Z₅, Z}).
- For Z₃, Z₄, Z₂×Z₂, the pair groupoid and Z₂ + Z₂, every count equals μ^V Σᵢ |Hom(H₁, Gᵢ)|/|Gᵢ|.
- The test can fail: some samples separate Z₄ from Z₂×Z₂, and Z₃ from the trivial value.

**5. Theorem 1.** Re-testing 61 survivors on their reduced rules, and 300 random rules with junk triangles, gives identical verdicts
and constants. The random rules include arbitrary relations on three labels.

## Scope

- **What is covered.** Pure counting laws whose triangle rule is a partial operation on a finite label set, every size, on ordered
  triangulations of closed orientable 3-manifolds.
- **Relations.** Non-deterministic rules are covered only by Theorem 1. Ticket B censuses them on three labels.
- **What is not covered.** Weighted, signed or phased laws, and laws with labels on triangles.
- **Computation.** The exhaustive computations stop at three labels and eight arrows. The theorem covers every size by the prose proof.
- **No overclaim.** No claim about P versus NP, physics or ontology.
