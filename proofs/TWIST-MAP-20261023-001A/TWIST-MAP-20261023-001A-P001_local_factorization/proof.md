# Where a twist can enter a count: the local factorization, walls and symmetries

Status: Proved

Ticket `TWIST-MAP-20261023-001A`, 2026-10-23.

**What it uses:**
- from `ODD-LOOP-20261023-001B-P001`: the twisted double cover, the swap τ, the symmetry (R) and Lemma A (gauge);
- from `LOOP-SHIELD-20261023-001C-P001`: the setting on closed surfaces and the wall for a lone odd loop, which Corollary 3 recovers
  and extends.

## Standard statement

**Setting.**
- **Surface and graph.** Σ is a closed orientable surface with a cellularly embedded graph G. Every edge has a reference direction.
- **Orientations and twists.** An orientation is x ∈ {0,1}^E. A twist cocycle t is a mod-2 1-cochain vanishing on every face
  boundary; its class q ∈ H¹(Σ; ℤ₂) is the sector.
- **The double cover.** D(x, t) has nodes (v, s), s ∈ {0, 1}. An edge e from u to w gives the arcs (u, 0) → (w, t_e) and
  (w, 1 − t_e) → (u, 1) when x_e = 1, and their reverses when x_e = 0. τ swaps the sheets; (R) says p → q exactly when τq → τp.
- **Skeleton and clusters.** An edge is cyclic when its arcs lie on directed cycles. The skeleton λ(x, t) is the set of cyclic edges.
  A cluster is a connected component K of the skeleton; its lattice W_K is the image of H₁(K; ℤ) in H₁(Σ; ℤ). K is odd when t is
  not a coboundary on K, even otherwise.
- **Counts.** The label of x lists the parity and lattice of each cluster with W_K ≠ 0. N(q, E) counts the orientations with label E
  in sector q, and N_λ(q) those with skeleton exactly λ. By Lemma A these depend only on q.

**Lemma 0 (clusters are strong components).** Each cluster K is the projection of a strong component S. The nontrivial strong
components over K are S and τS, and S = τS exactly when K is odd.

**Theorem 1 (local factorization).** Fix t and a set of edges λ. Then N_λ(t) = c(λ, t) · A(λ, t), where:
- **c**, the cyclic factor, is the number of orientations of λ in which every edge of λ is cyclic, in the double cover of the graph
  (V(λ), λ) alone. It is a product over the clusters and depends only on each twisted cluster (K, t|K) up to switching.
- **A**, the acyclic factor, is the number of orientations of the other edges whose shrunken cover has no directed cycle:
  - the shrunken graph Γ_λ has the vertices outside V(λ) and one point per cluster, typed odd or even;
  - each other edge keeps its twist, corrected at even points by the cluster's own gauge;
  - its cover has two nodes per ordinary vertex and per even point, but a single node per odd point.

**Corollary 1 (reductions).**
- **(a) Parallel edges in the shrunken graph.** Edges joining the same two points with the same twist, edges at an odd point joining
  the same two points with any twists, and loops at one point with the same twist are oriented alike in every orientation counted by
  A. So A is unchanged when each such class is replaced by one edge.
- **(b) Series edges in a cluster.** Suppose a vertex of a cluster meets exactly two edge-ends of the skeleton, from two different
  edges, and carries no loop. Then c is unchanged when the two edges are replaced by one edge whose twist is their sum.
- **(c) Switching and isomorphism.** c and A are invariant under switching (at vertices, at even points) and under isomorphisms of
  the reduced graphs that keep the point types.

**Theorem 2 (local relations).** Let t and t′ give the same parities on the clusters of λ. Suppose:
- (i) the parallel-reduced shrunken graphs of (λ, t) and (λ, t′) are isomorphic, with point types kept, up to switching;
- (ii) the series-reduced twisted clusters of (λ, t) and (λ, t′) correspond under a type-preserving bijection, each isomorphic to
  its image up to switching.

Then N_λ(t) = N_λ(t′). If every skeleton with label E is related in this way, then N(q, E) = N(q′, E).

**Lemma W (the boundary of a cluster).** Let K be a connected subgraph and N a thin regular neighbourhood of |K|.
- **The radical.** The classes of the boundary circles of N span exactly rad(W_K) = {w ∈ W_K : w · W_K = 0} over ℤ.
- **The crossing cocycle.** The edges outside K met in the corners of the boundary walk along a circle ∂, counted mod 2, form a
  cocycle of class PD([∂]) mod 2.

**Corollary 3 (walls, for clusters of any rank).**
- **The wall.** Let K be an odd cluster of λ under t, and ∂ a boundary circle of N(K). Then N_λ(t) = N_λ(t + PD[∂]), and the two
  twists give the same label on λ.
- **The wall group.** For every label E, N(q, E) = N(q + χ, E) for every χ in G(E), the mod-2 span of the duals of rad(W_K) over
  the odd clusters of E.
- **How the twists relate.** The relation holds skeleton by skeleton, by the identity in Theorem 2.
- **Rank one.** For a lone odd loop, rad(ℤc) = ℤc, and this is the dual pairing of `LOOP-SHIELD-20261023-001C-P001`.

**Proposition 4 (symmetries).** A cellular automorphism g of (Σ, G) maps orientations to orientations. It maps sectors by g_* and
labels by the action on lattices, so N(q, E) = N(g_* q, g_* E).

**Remark 5 (duality gives nothing within one genus-2 tiling).** On an L-shaped genus-2 square tiling:
- **The tiling.** It has a vertex of degree 12 (the cone point) and only square faces.
- **Its dual.** The dual has all degrees 4 and a face of degree 12, so it is not isomorphic to the tiling.
- **Hence.** Duality maps counts on G to counts on the dual graph. It never relates two counts on G.

**Remark 6 (the matroid reading; checked, not used).**
- **The decomposition.** Theorem 1 is the signed-graph case of a classical decomposition of oriented matroids: every reorientation
  splits into its totally cyclic part (the union of positive circuits) and an acyclic contraction.
- **Signed graphs.** The twisted double cover is the signed covering graph of the signed graph (G, t), oriented by x. Its directed
  cycles project to positive circuits of the oriented frame matroid.
- **The two factors as evaluations.** c = T(0, 2) of the frame matroid of (λ, t|λ), and A = T(2, 0) of its contraction by λ. These are
  Las Vergnas's counts of totally cyclic and acyclic reorientations.
- **The reductions as evaluations.** Corollary 1 is the series invariance of T(0, 2) and the parallel invariance of T(2, 0).

## Nearest known result

- **Theorem 1.** It is the cyclic–acyclic decomposition of reorientations of an oriented matroid (Las Vergnas; Gioan), read
  through the correspondence between signed graphs and the implication digraphs of two-literal clauses (Zaslavsky's orientations of
  signed graphs). The evaluations c = T(0, 2) and A = T(2, 0) are Las Vergnas's theorem. **Folklore risk: high.** The proof below is
  self-contained.
- **Corollary 1 and Lemma W.** These are standard: series and parallel reductions, and Lefschetz duality for a subsurface.
  **Folklore risk: high.**
- **Corollary 3.** It extends the program's wall theorem from lone odd loops to odd clusters of any rank, and makes it hold skeleton
  by skeleton. **Folklore risk: moderate** for the technique, low for the statement about twisted orientations.
- **What is new to the program.** Every exact relation between twists must come from the two small pieces of Theorem 1. The shrunken
  graph forgets the embedding, so it can have symmetries the surface lacks.
- **The literature.** No search was run in this epic. The earlier epics did not find the odd-loop identity in the literature.

## Proof

### Lemma 0

- **τ maps strong components to strong components.** By (R), a directed path p ⇝ q gives a directed path τq ⇝ τp. So τ maps each
  strong component to a strong component.
- **Two components over one vertex.** Let S, S′ be strong components whose projections share a vertex v.
  - Both contain a node over v.
  - If they contain the same node, they are equal.
  - Otherwise S′ contains τ of S's node, so S′ = τS.
- **Clusters.** The arcs of a cyclic edge lie in a strong component, which projects onto a connected set of cyclic edges.
  - Projections of strong components that share a vertex are equal, by the previous step.
  - So each cluster is the projection of one strong component S, and the strong components over it are S and τS.
- **Parity.** Every arc of an edge e changes the sheet by t_e.
  - If S ≠ τS, then S contains exactly one node over each vertex of K; containing both would meet τS. The sheet of S over each vertex
    is a function s with s(u) + s(w) = t_e on every edge of K, so t is a coboundary on K.
  - If S = τS, a directed path inside S from (v, 0) to (v, 1) projects to a closed walk of K with odd twist. ∎

### Theorem 1

**Normalization.**
- **Make t vanish on even clusters.** For each even cluster K choose a gauge s_K with s_K(u) + s_K(w) = t_e on K. Let R be the set
  of vertices with s = 1.
- **Lemma A.** Gauging by R maps orientations bijectively, keeps cyclic edges and the parities, changes c by the same gauge on λ,
  and turns t into a cocycle vanishing on every even cluster. Its value on the other edges is the corrected twist θ of the
  shrunken graph.
- **So assume t = 0 on even clusters.** By Lemma 0 the strong components over an even K are then K × {0} and K × {1}. Over an odd K
  there is one, K × {0, 1}.

**From an orientation to the pair.** Let x have skeleton λ.
- **The cyclic part.** Every edge of λ lies on a directed cycle of D(x, t), whose edges are all cyclic and hence in λ. So y = x|λ is
  counted by c.
- **The rest.** Contract each nontrivial strong component of D(x, t) to a node.
  - The nodes are those of the shrunken cover: two per ordinary vertex, K₀ and K₁ for an even K, and one K* for an odd K.
  - The remaining arcs are exactly the arcs of the edges outside λ, with the shrunken rule.
  - A condensation has no directed cycle. An arc of an edge outside λ is not inside a strong component, or that edge would be cyclic,
    so it is not a loop.
  - So z = x on the other edges is counted by A.

**From the pair to an orientation.** Let y be counted by c and z by A, and put x = (y, z).
- **The clusters stay strong components.** In the double cover of (V(λ), λ) alone, every edge of λ is cyclic, so by Lemma 0 the
  nodes over each cluster form the strong components listed above. They remain strongly connected in D(x, t).
- **No new cyclic edge.** A directed cycle of D(x, t) through an arc of an edge outside λ would become, after contracting those
  strong components, a closed directed walk of the shrunken cover. That cover has none.
- **Hence** the skeleton of x is exactly λ.

**Conclusion.** The map x ↦ (x|λ, x|rest) is a bijection between the orientations with skeleton λ and the pairs counted by c and A.
- **c is a product.** Cycles of the skeleton stay inside one cluster, so c is the product of the clusters' factors.
- **What each factor depends on.** By Lemma A, c depends only on each (K, t|K) up to switching, and A only on the shrunken graph and θ
  up to switching. ∎

### Corollary 1

**(a) Parallel edges.**
- **Same twist, ordinary or even points a and b.** Two such edges oriented oppositely give the arcs (a, 0) → (b, θ) and
  (b, θ) → (a, 0), a 2-cycle.
- **Edges at an odd point b*.** One orientation gives (a, 0) → b* → (a, 1), the other b* → (a, 0) and (a, 1) → b*. Opposite
  orientations make a 2-cycle through b*, so the twist does not matter.
- **Loops.** A loop with θ = 0 is a directed loop, so it is never counted. Two loops with θ = 1 oriented oppositely give
  (n, 0) → (n, 1) → (n, 0).
- **Conclusion.** Every counted orientation orients a class alike. Repeated arcs do not change acyclicity, so the class acts as one
  edge.

**(b) Series edges.**
- **The arcs at v.** Each edge contributes, over v, one arc entering one lift and one arc leaving the other: e₁ enters (v, a) and
  leaves (v, 1 − a), and e₂ enters (v, b) and leaves (v, 1 − b).
- **One orientation of e₂ works.** For the arc entering (v, a) to lie on a cycle, (v, a) needs a leaving arc, which only e₂ can give.
  So 1 − b = a, and given e₁ exactly one orientation of e₂ qualifies.
- **The merged edge.** Each lift of v then passes one arc through. The two paths (u, ·) → (v, a) → (w, ·) and
  (w, ·) → (v, 1 − a) → (u, ·) are exactly the arcs of an edge from u to w with twist t₁ + t₂ (sheet changes add).
- **Conclusion.** The two qualifying pairs correspond to the two orientations of the merged edge, and every other edge keeps its
  cyclic status.

**(c) Switching and isomorphism.** Switching is Lemma A, applied in the cluster or in the shrunken cover; at an even point it swaps K₀
and K₁. Isomorphisms relabel. ∎

### Theorem 2

By Theorem 1 and Corollary 1:
- **(i) gives equal A.**
- **(ii) gives equal c,** as products over the clusters.

Summing over the skeletons with label E gives the second statement. ∎

### Lemma W

- **The homology of N.** N retracts onto |K|, so H₁(N) = H₁(K), and ι: H₁(N) → H₁(Σ) has image W_K.
- **The form on N.** The intersection form of Σ restricts to that of N. For a compact orientable surface with boundary, the radical
  of the form on H₁(N; ℤ) is the image of H₁(∂N; ℤ).
  - This follows from the exact sequence H₁(∂N) → H₁(N) → H₁(N, ∂N) ≅ Hom(H₁(N), ℤ).
  - The second map is n ↦ n · (−).
- **Radical classes are boundary classes.** If w = ι(n) and w · W_K = 0, then n · m = ι(n) · ι(m) = 0 for every m, so n lies in the
  image of H₁(∂N), and w is a combination of boundary classes.
- **Boundary classes are radical.** A boundary circle can be pushed off N, so it meets no cycle of K.
- **The crossing cocycle.** The boundary circles of a thin neighbourhood of an embedded graph are traced by the boundary walks of
  the ribbon subgraph. A circle ∂ crosses exactly the edges that leave K in the corners it passes, once per passage. The crossing
  cochain of a transverse closed curve is a cocycle whose class is the curve's Poincaré dual mod 2. ∎

### Corollary 3

**The wall.**
- **The representative.** Represent PD[∂] by the crossing cocycle ω of Lemma W. It is supported on edges outside λ that have an end
  at a vertex of K.
  - Edges of K lie in N, so ∂ does not cross them.
  - Other clusters share no vertex with K and no skeleton edge joins them to K, or they would be one cluster.
- **The cyclic factor.** t + ω agrees with t on λ, so c and every parity are unchanged.
- **The lattices.** [∂] is radical in W_K, and ∂ is disjoint from every other cluster, so the label is unchanged.
- **The acyclic factor.** In the shrunken graph, ω changes twists only on edges at the odd point K, where twists do not enter. So A
  is unchanged.
- **Conclusion.** Theorem 1 gives N_λ(t) = N_λ(t + ω), which is N_λ(t + PD[∂]) by Lemma A.

**The wall group.**
- **Every skeleton is covered.** Every skeleton with label E has odd clusters with the lattices listed in E.
- **The span.** By Lemma W, their boundary classes span PD(rad W_K) mod 2.
- **Conclusion.** Write χ ∈ G(E) as a sum of such duals, apply the wall once per term, and sum over the skeletons with label E. ∎

### Proposition 4 and Remark 5

**Proposition 4.**
- **Edges whose direction g reverses.** The pair of arc sets of an edge, one for each orientation, is the same whichever end is
  taken as the tail: for t = 0 the two sets swap, and for t = 1 each is preserved.
- **The cover.** So g maps orientations bijectively, and the double covers isomorphically, with twists mapped by g_* and lattices
  by g's action on homology.

**Remark 5.**
- **The tiling's degrees.** The degrees of the L-shaped tilings are checked to be {4, 12}, and every face is a square.
- **The dual.** The dual therefore has a face of degree 12 and no vertex of degree 12. ∎

## Interpretation (not theorem)

- **A twist acts through two small pieces.**
  - **Inside the clusters,** it decides which cycles are odd.
  - **Between them,** it twists the paths of the graph whose clusters are shrunk to points.
  - **Nothing else of the twist reaches a count.**
- **Walls are where the shrunken graph forgets the twist.** An odd cluster is a point whose two sheets have merged, so any twist on
  the edges around it is invisible.
- **Shrinking forgets the embedding.** Two twists that the surface treats differently can give isomorphic pieces, and then their
  counts agree exactly. These are the relations no symmetry of the surface explains.

## Check

`check.py` (standard library):
- **Theorem 1 and Corollary 1.** It enumerates all 2^16 orientations of L(2, 1, 2, 1) in all 16 twists and groups them by skeleton.
  On 120 sampled (twist, skeleton) pairs it checks, by brute force:
  - the count equals c · A;
  - c is unchanged by series reduction, and A by parallel reduction;
  - c = T(0, 2) and A = T(2, 0) of the frame matroids (Remark 6).
- **Proposition 4 and Corollary 3 on a whole surface.** On L(2, 1, 2, 1), every automorphism of the tiling and every element of
  every label's wall group preserves every count.
- **Lemma W.** On random clusters of L(2, 2, 2, 2), L(3, 1, 2, 2) and L(3, 2, 2, 2) it checks:
  - the boundary walks of the ribbon subgraph, traced with the tiling's rotation system, have classes spanning exactly the radical;
  - their corner edges form cocycles of class PD mod 2.
- **Corollary 3 on odd clusters with small skeletons.** It checks that:
  - adding the dual of a boundary class keeps the label;
  - it changes nothing in the two pieces up to switching;
  - it gives equal c · A.
- **Remark 5.** It checks the degrees of every L-shaped tiling of the experiment.
- **Controls (each rejected):**
  - dropping the even clusters' gauge breaks the factorization;
  - series-reducing the shrunken graph changes A;
  - parallel-reducing a cluster changes c;
  - twists outside the wall group change some counts.

## Scope

- **Exact results.** Theorems 1 and 2, Corollaries 1 and 3, Lemma W and Proposition 4 hold for every closed orientable surface with a
  cellularly embedded graph. Remark 5 concerns the L-shaped tilings.
- **Not claimed.** That every exact relation between twists arises from Theorem 2 is not claimed. It is tested by
  `TWIST-MAP-20261023-001B-E001`.
- **Measure.** Fair orientations only.
- **Not claimed.** No space or physics is claimed.
