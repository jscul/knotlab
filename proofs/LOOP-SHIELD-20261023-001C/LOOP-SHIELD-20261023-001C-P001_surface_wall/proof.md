# The wall on closed surfaces, and which twists a seam can carry

Status: Proved

Ticket `LOOP-SHIELD-20261023-001C`, 2026-10-23.

**What it uses:**
- from `ODD-LOOP-20261023-001B-P001`, these lemmas, which are statements about digraphs and hold verbatim on any graph:
  - Lemma A (gauge);
  - Lemma D (moving a seam along edges that join a swap-invariant strong component to the rest changes no directed cycle);
- from the same proof, the torus versions of Lemmas B and C, generalized here;
- from `NAE-INVARIANT-20261022-001A-P001`: the twisted model.

## Standard statement

**Setting.**
- **The surface.** Σ is a closed orientable surface of genus g ≥ 1, with a cellularly embedded graph G: every face is an open disk. Every edge has a reference direction (lattice tail and head).
- **Orientations and the double cover.** An orientation is x ∈ {0, 1}^E. A twist cocycle t is a mod-2 1-cochain that vanishes on every face boundary. The double cover D(x, t), the swap τ and the symmetry (R) are as on the torus.
- **Sectors.** A sector is a class q ∈ H¹(Σ; ℤ₂), with a fixed standard cocycle t_q.
- **Line events.** For a primitive class c ∈ H₁(Σ; ℤ) with q(c) = 1, L_q(c) is the set of orientations whose clusters of cyclic edges all have periods in ℤc, at least one nonzero.
- **The dual twist.** PD(c) ∈ H¹(Σ; ℤ₂) is γ ↦ c·γ mod 2, the twist that counts crossings with c.
- **Seams next to a set.** For a vertex set P, a seam next to P is a mod-2 cocycle supported on the edges with exactly one end in P.

**Theorem 1 (the wall on a closed surface).**
- **The involution.** For every Σ and G, every primitive c and every q with q(c) = 1, there is an explicit map Φ_q: L_q(c) → L_{q+PD(c)}(c). The same construction from q + PD(c) gives its inverse.
- **What it preserves.** D(Φ_q(x), t_{q+PD(c)}) is a relabelling of sheets of a digraph with exactly the same directed cycles as D(x, t_q).
- **Hence** |L_q(c)| = |L_{q+PD(c)}(c)|. Every statistic of the cyclic structure has the same law on the two events under fair orientations.
- **On the torus.** The twists vanishing on c are 0 and PD(c), so this is the odd-loop identity of `ODD-LOOP-20261023-001B-P001`.
- **On genus g.** The twists odd on c are a coset of 2^{2g−1}. Theorem 1 pairs them only as a ↔ a + PD(c).

**Lemma E (seams on a surface).**
- **Duality.** The classes of seams next to P are exactly the Poincaré duals of the classes of closed curves in Ω_P = St(P) ∖ |G[P]|. Here St(P) is the open star of P and G[P] the graph induced on P.
- **For a square tiling.** St(P) deformation retracts onto three pieces:
  - G[P];
  - a diagonal across every square that has exactly two opposite corners in P;
  - the squares with all four corners in P.
  So every seam class is dual to a class carried by G[P] together with those diagonals.
- **(a) The loop case.** Take P = π(S*) for x ∈ L_q(c), with no square meeting P in exactly two opposite corners. Then every seam next to P carries 0 or PD(c): a wall next to the loop can only shield the dual twist.
- **(b) The canonical wall** of Theorem 1 is a seam next to P of class PD(c).
- **(c) Other classes.** Without that hypothesis other seam classes can exist: two disjoint loops of different classes, or diagonal squares, supply them. Nothing makes such a choice canonical across an event.

**Lemma F (seams in three dimensions).**
- **Duality.** In a closed 3-manifold with a cell structure, such as the cubic 3-torus, the classes of seams next to P are exactly the duals of the classes of closed surfaces in St(P) ∖ |G[P]|.
- **Hence** a seam next to P carries a nonzero twist only if the open star of P carries a closed surface that is essential mod 2.
- **A tube carries none.** If St(P) lies in a solid torus, for example a loop confined to a narrow tube, every seam next to P has class 0. Around a loop in three dimensions there is no wall.

## Nearest known result

- **The ingredients are classical:**
  - infinite cyclic covers of surfaces;
  - simple closed curves being separating (class 0) or non-separating (primitive class);
  - Lefschetz duality H^k(M, A) ≅ H_{n−k}(M ∖ A);
  - regular neighbourhoods.
- **What is new to the program.** Applying them to the twisted double cover of a random orientation. A lone odd loop shields exactly the twist dual to itself on any closed orientable surface, and in three dimensions no loop shields anything.
- **The literature.** The odd-loop identity itself was not found in the literature by the earlier epics.
- **Folklore risk.** Moderate for the lemmas (standard topology), low for the statements about the twisted model.

## Proof

### Lemma B on Σ (the odd strong component)

**The statement is as on the torus.** For x ∈ L_q(c):
- some strong component S* has τS* = S*;
- for such an S* and P = π(S*), both sheets of every vertex of P lie in S*;
- every edge with both ends in P has both arcs in S*;
- every closed walk of G[P] has class in ℤc, and some simple cycle of G[P] has class ±c.

**What changes on Σ.** The torus proof used only two facts beyond the graph:
- the period lattice of a connected subgraph is generated by the classes of its simple cycles (fundamental cycles of a spanning tree);
- each simple cycle is a simple closed curve, so its class is 0 or primitive.

On Σ, a simple closed curve is separating (class 0) or non-separating (primitive class), so both facts hold.

### Lemma C on Σ (the wall)

**The cover.**
- **Definition.** Σ_c → Σ is the infinite cyclic cover with monodromy γ ↦ c·γ. It is connected because c is primitive, so some d has c·d = 1.
- **The lifted graph.** G_c is the lifted graph, with deck generator s. The cover has two ends.
- **Ends of sets.** For a finite vertex set A, let U⁺(A) and U⁻(A) be the components of G_c − A that contain all vertices far enough toward the + and − ends.
  - They are well defined. Take a finite connected fundamental domain F with F ∪ sF connected (a lift of a spanning tree, extended along a closed walk ω with c·ω = 1).
  - For large J, ∪_{j≥J} s^j F is then connected and avoids A.

**(a) The lift of P.**
- Closed walks of G[P] have classes in ℤc and c·c = 0, so they lift to closed walks.
- A path in a lift from z to s^j z would project to a closed walk of class κ with c·κ = j ≠ 0, which is impossible.
- So the component K of the preimage of P through a chosen vertex is a copy of G[P]: one lift of each vertex and edge. The preimage is the disjoint union of the s^j K.

**(b) K separates the two ends.**
- **The neighbourhood of G[P] is planar.** Let N be a thin regular neighbourhood of |G[P]| in Σ. Its loops have classes in ℤc. N has genus 0: a handle would contain two curves with intersection number 1, whose classes are independent.
- **A boundary circle of class ±c.** The boundary circles of N generate H₁(N). Each is a simple closed curve of class 0 or ±c. Since the image contains c, some boundary circle ∂ has class ±c and is non-separating.
- **Lifts of ∂ separate.** Cutting Σ along ∂ and stacking ℤ copies builds Σ_c. So every lift of ∂ is a gluing circle, which separates the two ends.
- **N lifts.** Its loops have c·γ = 0, so N lifts homeomorphically to a neighbourhood Ñ of K, with a lift ∂̃ of ∂ on its boundary.
- **No path avoids K.** A path of G_c that avoids the vertices of K uses no edge incident to K, so it avoids the thin Ñ and ∂̃. Hence it cannot join the ends, and U⁺(K) ≠ U⁻(K).

**(c) Translates are ordered.**
- **Ordering lemma.** Let A and B be disjoint, finite, connected vertex sets that each separate the ends. Then B ⊂ U⁺(A) or B ⊂ U⁻(A). Moreover B ⊂ U⁺(A) forces A ⊂ U⁻(B).
  - B lies in one component of G_c − A.
  - Suppose A ⊂ U⁺(B). Then B ∪ U⁻(B) is connected, since B separates and so U⁻(B) touches B. It avoids A and reaches the − end, so B ⊂ U⁻(A).
  - A ⊂ U⁻(B) gives B ⊂ U⁺(A) symmetrically.
  - A cannot lie in a finite component of G_c − B: then U⁺(B) ∪ B ∪ U⁻(B) would be a connected set avoiding A that joins the ends.
- **"Above" is transitive.** If B ⊂ U⁺(A) and C ⊂ U⁺(B), then U⁺(B) is connected, avoids A (since A ⊂ U⁻(B)) and reaches the + end. So U⁺(B) ⊂ U⁺(A).
- **Applied to K.** The order is invariant under s, and s^J K ⊂ U⁺(K) for large J.
  - If sK were below K, induction would put every s^J K below K. So s^j K ⊂ U⁺(K) for every j ≥ 1.
  - Also U⁺(s^{j+1}K) ⊂ U⁺(s^j K).

**(d) The wall.**
- **Definition.** γ̃ is the set of edges from K to U⁺(K) (that is, δU⁺(K)), and γ is its projection.
- **(i) Its translates are disjoint.**
  - An edge in γ̃ ∩ s^j γ̃ with j ≥ 1 would join k ∈ K to z ∈ U⁺(K), and k′ ∈ s^jK to z′ ∈ U⁺(s^jK).
  - Disjointness forces k = z′, but K ⊂ U⁻(s^jK).
  - So γ̃ projects injectively.
- **(ii) Each edge of γ joins P to V ∖ P.** Its U⁺ end lies in no s^jK, or two components of the preimage of P would be adjacent.
- **(iii) The wall has class PD(c).**
  - **The counting function.** Let N(z) = max{j : z ∈ U⁺(s^j K)}. It is finite, and the sets U⁺(s^j K) are nested.
  - **It jumps only on the wall.** It changes by exactly 1 across an edge of some translate of γ̃, and is unchanged elsewhere (by (i)).
  - **The class.** Fix a lift z_v of each vertex. Lifting e from z_u ends at s^{β_e} z_w, where β is an integer cocycle with β(ω) = c·ω. So δ(N(z_v) mod 2) = 1_γ + β mod 2.
  - **The gauge set.** β mod 2 represents PD(c). So 1_γ + χ⁰ = δR for the standard cocycle χ⁰ of PD(c) and some R ⊆ V, unique once a base vertex is excluded. ∎

### Proof of Theorem 1

The torus proof applies word for word, with Lemmas B and C above in place of their torus versions.
- **The map.** Let F be the wall edges whose free end is their head. Set Φ_q(x) = x + 1_F + 1_{tail ∈ R}.
- **Cycles are kept.** Lemma D keeps every directed cycle of D(x + 1_F, t_q + 1_γ). The gauge by R turns that digraph into D(Φ_q(x), t_{q+PD(c)}).
- **The construction repeats.** The swap-invariant strong components keep their projections. So the construction applied from q + PD(c) picks the same P, γ, F and R, and returns x. ∎

### Proof of Lemma E

- **Seams form a relative cohomology group.** Let L be the full subcomplex on V ∖ P (cells all of whose vertices lie outside P), and A = |L| ∪ |G[P]|.
  - A seam next to P is exactly a 1-cocycle vanishing on the edges of A.
  - A contains every vertex, so there are no relative coboundaries. The seams are H¹(Σ, A; ℤ₂).
- **Duality.** Lefschetz duality gives H¹(Σ, A; ℤ₂) ≅ H₁(Σ ∖ A; ℤ₂), compatibly with the maps to H¹(Σ) ≅ H₁(Σ). Here Σ ∖ |L| = St(P) and Σ ∖ A = Ω_P.
- **The open star of a square tiling.** Sort the squares by the corners they have in P.
  - **One corner:** the square's part of St(P) retracts to that corner.
  - **Two adjacent corners:** it retracts to their edge.
  - **Three corners:** it retracts to two edges of G[P].
  - **Four corners:** it is a square of the full subcomplex on P.
  - **Two opposite corners:** it is a contractible region joining them, homotopic to a diagonal.
  - So Ω_P ⊂ St(P) ≃ G[P] ∪ diagonals ∪ inner squares.
- **(a)** With no diagonals, the classes carried by St(P) are those of G[P], which lie in ℤc by Lemma B. So the seams carry 0 or PD(c).
- **(b)** This is Lemma C(d).
- **(c)** The check exhibits two disjoint loops (classes h2 and v2 on L(3, 2, 2, 2)) whose seams carry both duals. On random sets, ignoring the diagonals misses seam classes about a third of the time. ∎

### Proof of Lemma F

- **Duality in three dimensions.** The same argument in a closed 3-manifold M gives H¹(M, A; ℤ₂) ≅ H₂(M ∖ A; ℤ₂). A seam's class is dual to a mod-2 2-cycle in Ω_P ⊂ St(P).
- **A solid torus carries no surface.** If St(P) lies in a solid torus T, every 2-cycle of St(P) is a 2-cycle of T, and H₂(T; ℤ₂) = 0. Its class in M is then 0. ∎

## Correction recorded during the proof

- **The first version was wrong.** It stated Lemma E with G[P] in place of the open star.
- **How it was caught.** check.py rejected it: on 117 of 300 random vertex sets, seams carried classes that no cycle of G[P] carries.
- **The cause.** A square with two opposite corners in P joins them through its interior.
- **The fix.** The duality statement and the open-star model above replace it. The loop case (a) carries the explicit hypothesis that no such square exists.
- **Line configurations seen.** On all of them, the seams next to the loop carried only 0 and PD(c).

## Interpretation (not theorem)

- **A loop shields exactly what it bounds.** On a surface, a lone contradiction loop runs along c, and its wall is the curve beside it. The only twist that curve can absorb is the one measured by crossing c. All the other twists odd on c remain visible.
- **Dimension matters.** In three dimensions a loop has no wall at all. Shielding needs the emergent structure to have codimension one.
- **The relational reading.** The background a structure screens is exactly the background dual to its own shape.

## Check

`check.py` (standard library):
- **Random walks with restarts** inside line events on L(2, 2, 2, 2) (classes h2 and v2) and L(3, 1, 2, 2) (class v1): 425 distinct orientations. On every one:
  - the wall lemma holds;
  - the image lies in the partner line event;
  - the involution returns the orientation;
  - the wall realizes PD(c);
  - every seam next to the loop carries only 0 or PD(c).
- **Lemma E on random sets.** On 300 random vertex sets of L(3, 2, 2, 2), every seam class lies among the duals of the open star's classes. On 104 of them, G[P] alone misses some.
- **Lemma F on tubes.** On 200 loops along x confined to a 2 × 2 tube of the 5 × 5 × 5 torus, only the zero seam class occurs.
- **Controls (each rejected):**
  - bits flipped on the wrong wall edges change the cyclic arcs (425 times);
  - two disjoint loops support two independent seam classes;
  - a full slice of the 3 × 3 × 3 torus supports a nonzero class;
  - the diagonal squares matter.

## Scope

- **Exact results.** Theorem 1 and Lemmas E and F are exact, for every closed orientable surface with a cellularly embedded graph (E: the retraction statement is for square tilings) and for every closed 3-manifold with a cell structure (F).
- **What remains open.** Whether the twists odd on c that are not paired by Theorem 1 differ in probability is not a theorem. It is tested by `LOOP-SHIELD-20261023-001A-E001` (genus 2) and `LOOP-SHIELD-20261023-001B-E001` (3-tori).
- **Measure.** Fair orientations only.
- **Not claimed.** No space or physics is claimed.
