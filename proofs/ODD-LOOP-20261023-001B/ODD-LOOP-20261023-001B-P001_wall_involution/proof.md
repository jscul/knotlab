# The wall involution and the odd-loop identity

Status: Proved

Ticket `ODD-LOOP-20261023-001B`, 2026-10-23.

**What it uses:**
- from `NAE-INVARIANT-20261022-001A-P001`: the twisted model (the swap-reversed orientation of the double cover);
- from `TWIST-RELATIONS-20261022-001A-P001`: the gauge transformation of the seam, and the exact identity 1 − cons10 − cons01 + cons11 − P00 = −D + odd10 + odd01 − odd11;
- from `SC-TORUS-EXACT-20261022-001A-P001`: the cone theorem, used only to restate the event as "the cone is the line ℝc".

## Standard statement

**Setting.**
- **The torus.** T = ℤ²/Λ with Λ = ⟨w1, w2⟩, w1 = (Lh, 0), w2 = (s, Lv), Lh, Lv ≥ 3 and s ∈ ℤ. Classes are written in the basis (w1, w2).
- **Edges.** Each edge e of the square lattice on T has a lattice tail u_e and a lattice head w_e, one step to the right or up, and an offset o_e = (a_e, b_e): the step from u_e equals the head's position plus a_e w1 + b_e w2.
- **Orientations.** x ∈ {0, 1}^E, with x_e = 1 meaning "from tail to head". Uniform random.
- **The double cover.** For a twist cocycle t ∈ {0, 1}^E, D(x, t) has vertices V × {0, 1}:
  - x_e = 1 gives the arcs (u, 0) → (w, t_e) and (w, 1 − t_e) → (u, 1);
  - x_e = 0 gives (w, t_e) → (u, 0) and (u, 1) → (w, 1 − t_e).
  - So on the tail's sheet 0 an arc follows the orientation, and on sheet 1 it runs against it.
- **The swap.** τ(v, k) = (v, 1 − k). **(R):** a → b is an arc exactly when τb → τa is an arc.
- **Sectors.** A twist q = (q1, q2) ≠ 0 has the standard cocycle t_q(e) = q1 a_e + q2 b_e mod 2. Write q(c) = q1 c1 + q2 c2 mod 2.
- **Line events.** For a primitive class c with q(c) odd:
  - an edge is *cyclic* when its arcs lie on directed cycles of D(x, t_q);
  - L_q(c) is the set of orientations whose clusters of cyclic edges (connected components) all have period lattices inside ℤc, at least one of them nonzero.
  - This is "the sector's strong components wind along c and nothing else". By the cone theorem it is the event that the cone of sector q is the line ℝc.
- **The other twist.** χ_c = (c2, c1) mod 2 is the nonzero twist that vanishes on c. The two twists odd on c are q and q′ = q + χ_c, and t_q′ = t_q + χ⁰, where χ⁰(e) = χ_c(o_e) mod 2.

**Theorem 1 (the odd-loop identity).**
- **The involution.** On every such torus, for every primitive class c and the two twists q, q′ odd on c, there is an explicit map Φ_q: L_q(c) → L_q′(c). The same construction from sector q′ gives its inverse.
- **The identity.** |L_q(c)| = |L_q′(c)|. For uniform orientations, P(cone of sector q = ℝc) = P(cone of sector q′ = ℝc).
- **More.** D(Φ_q(x), t_q′) is a relabelling of sheets of a digraph with exactly the same directed cycles as D(x, t_q). So every statistic of the cyclic structure has the same law on L_q(c) as on L_q′(c), for example:
  - the strong components that carry cycles, and their projections;
  - the number of odd loops.

**Corollary 2.** On every such torus, with ℓ(c) the common value of Theorem 1 and odd_q = P(sector q has an odd winding):
- odd10 + odd01 − odd11 = 2 Σ ℓ(c), summed over the classes c ≡ (1, 1) mod 2;
- hence 1 − cons10 − cons01 + cons11 − P00 = −D + 2 Σ_{c ≡ (1,1)} ℓ(c), exactly.
- So the consistency relation measured on rectangles holds exactly when D equals twice the probability of an odd loop in a diagonal class.

**Proposition 3 (the first attempt, preserved).**
- **Inert bands.** Call a straight band of rows [a, b) *inert* when its lift splits into a set closed under predecessors and that set's swap image.
- **What holds.** Moving the second twist's seam to the top of an inert band leaves every directed cycle unchanged.
- **The resulting involution.** "Move the seam to the smallest inert top" is an involution between the two sectors' line events, when it is restricted to bands that avoid the row just above the default seam.
- **What fails.** Without that restriction it is not an involution. The stored 4 × 4 orientation in check.py has smallest inert top 4 in sector (1, 0). Its image has smallest inert top 1 in sector (1, 1).
- **Coverage.**
  - Every line configuration has an inert straight band on 3 × 3 (exhaustive) and on sampled 4 × 3, 5 × 3 and 6 × 3.
  - About 57% do on 5 × 4 and 33% on 6 × 5 (scratch sampling).
  - So straight bands cannot prove the identity in general. The wall in Theorem 1 replaces the band with the odd loop itself, which every configuration in the event has.

## Nearest known result

- **Moving a defect line.** Moving a ℤ₂ twist (a seam, or antiperiodic boundary condition) across a region by a gauge transformation is standard: interface arguments for the Ising model, ℤ₂ lattice gauge theory, and the Fortuin–Kasteleyn representation all use it.
- **What is specific here:**
  - the swap-reversed double cover of a random orientation, which comes from the program's not-all-equal analysis;
  - the barrier: the wall is the upper boundary of the odd strong component itself, in the cyclic cover along c;
  - the bit flips on wall edges whose end off the component is their head, which make the move cycle-preserving under the "sheet read at the tail" convention.
- **The statement.** Equality of the probabilities that a lone odd strong component winds along c under the two twists odd on c was not found in the literature in the previous epic's check.
- **Folklore risk.** Moderate for the technique, low for the statement.

## Proof

### Lemma A (gauge; `TWIST-RELATIONS-20261022-001A-P001`)

- **Statement.** For R ⊆ V, swapping the sheets of the vertices in R is an isomorphism D(x, t) → D(x + 1_{tail ∈ R}, t + δR). Here δR(e) = [u_e ∈ R] + [w_e ∈ R].
- **What it preserves.** It commutes with τ and preserves the projection to V.
- **Proof for one arc.** Take x_e = 1, t = t_e, u = u_e, w = w_e:
  - **If u ∉ R,** (u, 0) → (w, t) becomes (u, 0) → (w, t + [w ∈ R]), which is the x_e = 1 arc for the new twist t + δR(e).
  - **If u ∈ R,** it becomes (u, 1) → (w, t + [w ∈ R]). That is the x_e = 0 arc (u, 1) → (w, 1 − t′) for the new twist t′ = t + 1 + [w ∈ R].
- The other arcs are checked the same way. ∎

### Lemma B (the odd strong component)

Let x ∈ L_q(c) with q(c) odd, and D = D(x, t_q).

**(a) D has a strong component S with τS = S, and every such S contains a closed walk whose projection has a q-odd class.**
- **Clusters come from strong components.** If two strong components meet the same base vertex v, one contains (v, 0) and the other (v, 1). The second is then τ of the first, by (R).
- **A component that τ does not fix.** Suppose τS ≠ S. Then S holds one sheet k(v) of each vertex of its projection. An arc of edge e inside S forces k(w_e) = k(u_e) + t_e, so every closed walk along S's arcs has q-even class.
- **Its cluster has period lattice 0.**
  - The period lattice is generated by the classes of simple cycles of the cluster.
  - A simple closed curve on the torus has class 0 or a primitive class, and here the class must lie in ℤc.
  - A nonzero generator would therefore be ±c, which is q-odd.
- **So the cluster with nonzero period comes from an S with τS = S.**
- **The odd closed walk.** If τS = S, S contains a directed path from (v, 0) to (v, 1). Its projection is a closed walk whose class κ has q(κ) = 1.

**(b) If τS = S and P = π(S), then:**
- **Both sheets.** Both sheets of every vertex of P lie in S.
- **Edges inside P.** Every edge with both ends in P has both arcs inside S.
- **Classes.** Every closed walk of the subgraph G[P] induced on P has class in ℤc. Some simple cycle of G[P] has class ±c.

**Proof of (b).**
- **Sheets and edges.** If (v, k) ∈ S then τ(v, k) ∈ τS = S. An arc joining two vertices of S lies inside S.
- **Lifting a closed walk.** Let γ be a closed walk in G[P] of class κ. Lift it from (v, 0) through the arcs of its edges, which all lie inside S. Going around twice gives a closed walk inside S's underlying graph, of class 2κ.
- **Directed cycles span.** The undirected cycle space of a strongly connected digraph is spanned by its directed cycles: an ear decomposition into directed ears gives one directed cycle per ear, and these form a basis.
- **Their classes lie in ℤc.** Each directed cycle of D projects into one cluster.
- **Conclusion.** So 2κ ∈ ℚc ∩ ℤ², hence κ ∈ ℤc, as c is primitive. The odd closed walk of (a) lies in G[P]. So the period lattice of G[P] is a nonzero sublattice of ℤc. It is generated by simple cycles, each of class 0 or ±c. ∎

### Lemma C (the wall)

Fix x ∈ L_q(c). Let S* be the strong component with τS* = S* whose projection contains the smallest vertex, and P = π(S*).

**The cover along c.**
- **The cover.** T_c = ℝ²/ℤc⃗, where c⃗ = c1 w1 + c2 w2, with the lattice graph G_c. It is a cylinder, and its deck group is Λ/ℤc⃗ ≅ ℤ.
- **The deck generator.** It is d⃗ for any d with det(c, d) = 1.
- **Height.** h(z) = det(c⃗, z)/det(c⃗, d⃗) is well defined on T_c, and h(z + d⃗) = h(z) + 1.
- **Lifting edges.** An edge e lifts from level j at its tail to level j + β_e at its head, where β_e = det(c, o_e) = c1 b_e − c2 a_e.

**(a) The lift of P.**
- **Statement.** The preimage of P is the disjoint union of the translates K + jd⃗ of one finite connected set K. K holds exactly one lift of each vertex of P, and it contains a closed walk going once around T_c.
- **Proof.**
  - G[P] is connected, so the deck group permutes the components of the preimage transitively.
  - If K + jd⃗ = K for some j ≠ 0, K would contain a path from a lift z to z + jd⃗. That path projects to a closed walk of G[P] whose class is not in ℤc, which Lemma B(b) forbids.
  - A cycle of G[P] of class ±c lifts to a closed walk in K going once around T_c.

**(b) Separation and order.**
- **K separates the ends.** Every path in G_c from below min_K h to above max_K h meets K, because two lattice polylines can cross only at lattice vertices. Let:
  - U⁺(K) be the component of G_c − K holding every vertex of height > max_K h (a half-plane's lattice points are connected);
  - U⁻(K) be the component holding every vertex below min_K h.
- **The translates.** K + jd⃗ ⊂ U⁺(K) for j ≥ 1 and K + jd⃗ ⊂ U⁻(K) for j ≤ −1.
  - For j ≥ 1, K + jd⃗ is connected and disjoint from K.
  - Its highest vertex has height max_K h + j > max_K h, so that vertex lies in U⁺(K). Hence all of K + jd⃗ does.
  - The case j ≤ −1 is symmetric.
- **Nesting.** For j ≥ 1, U⁺(K + jd⃗) ⊂ U⁺(K).
  - K ⊂ U⁻(K + jd⃗), so U⁺(K + jd⃗) avoids K.
  - It is connected and contains high vertices.

**(c) The wall.**
- **Definition.** γ̃ is the set of edges of G_c joining K to U⁺(K). Since U⁺(K) is a component of G_c − K, γ̃ = δU⁺(K).
- **(i) It projects injectively.** γ̃ shares no edge with any translate γ̃ + jd⃗, j ≠ 0.
  - Suppose an edge {k, z} with k ∈ K and z ∈ U⁺(K) also joins K + jd⃗ to U⁺(K + jd⃗).
  - Then k ∈ U⁺(K + jd⃗) and z ∈ K + jd⃗.
  - For j ≥ 1, K lies below K + jd⃗, so k ∉ U⁺(K + jd⃗).
  - For j ≤ −1, z ∈ U⁺(K) cannot lie in K + jd⃗ ⊂ U⁻(K).
  - Its projection γ is a set of edges of T.
- **(ii) Every edge of γ joins a vertex of P (its far end) to a vertex outside P (its free end).** If the U⁺ end were in a translate K + jd⃗, an edge would join two different components of the preimage of P.
- **(iii) γ represents χ_c.** 1_γ + χ⁰ = δR for a set R ⊆ V, unique once 0 ∉ R.
  - **Construction.** Let N(z) = max{j : z ∈ U⁺(K + jd⃗)}.
    - It is finite: z lies above every vertex of K + jd⃗ for j small enough, and below every vertex for j large enough.
    - The sets U⁺(K + jd⃗) decrease in j (nesting), so z lies in U⁺(K + jd⃗) exactly when j ≤ N(z).
    - N(z + d⃗) = N(z) + 1.
  - **N jumps only on translates of γ̃.** Across an edge, N changes exactly when the edge lies in some γ̃ + jd⃗, and by (i) then by exactly 1.
  - **The level-0 lifts.** Let z_v be the lift of v at level 0. The lift of an edge e from z_u ends at z_w + β_e d⃗. So N(z_w) − N(z_u) + β_e ≡ 1_γ(e).
  - **Parity of β.** β_e ≡ c2 a_e + c1 b_e = χ⁰(e) mod 2.
  - **Conclusion.** R = {v : N(z_v) odd} works. ∎

### Lemma D (moving the seam along a wall)

**Statement.**
- **Hypotheses.** Let t be any twist cocycle and S a strong component of D = D(x, t) with τS = S. Let γ be any set of edges, each joining a vertex of π(S) (its far end f) to a vertex outside π(S) (its free end y).
- **The move.** Let F ⊆ γ be the edges whose free end is their lattice head. Set D′ = D(x + 1_F, t + 1_γ).
- **Conclusion.** D and D′ have exactly the same directed cycles.

**Proof.**
1. **Two arcs per wall edge.** Each arc of e ∈ γ joins a sheet of y to a sheet of f, and both sheets of f lie in S. By (R), one arc runs from y into S and the other from S into y, at different sheets of y.
2. **The upstream sheet.** For every free end y there is a sheet σ(y) such that, for every edge between y and π(S):
   - the arc at (y, σ(y)) leaves into S;
   - the arc at (y, 1 − σ(y)) comes from S.
   - **Why.** Otherwise both sheets of y would reach S and be reached from it, so y ∈ π(S).
3. **The set M.** Let M be the set of vertices from which some (y, σ(y)) can be reached. M is closed under predecessors in D. It has two more properties:
   - **M ∩ S = ∅.** A vertex of S reaching (y, σ(y)) → S would put (y, σ(y)) in S.
   - **(y, 1 − σ(y)) ∉ M.** S → (y, 1 − σ(y)), so if (y, 1 − σ(y)) reached (y′, σ(y′)), then (y′, σ(y′)) would be in S.
4. **The move keeps directions at the free end.**
   - **Twist only.** Flipping t_e reattaches the head end of both arcs to the other sheet and keeps the tail end with its directions.
   - **Twist and bit.** Flipping t_e and x_e together keeps the direction of the arc at each head sheet and reattaches the tail ends.
   - **On the wall.** Either way, after the move every arc of e still leaves (y, σ(y)) into S or enters (y, 1 − σ(y)) from S. Only the sheet of f changes, and both sheets of f are in S.
   - **Other arcs.** Arcs of edges outside γ do not change.
5. **No directed cycle of D′ uses a moved arc.**
   - **M stays closed under predecessors in D′.** Moved arcs enter only vertices of S or vertices (y, 1 − σ(y)), and none of those is in M.
   - **Hence τM is closed under successors,** by (R) for D′.
   - **An arc (y, σ(y)) → S.** A cycle through it lies in M, but its next vertex is in S, outside M.
   - **An arc S → (y, 1 − σ(y)) ∈ τM.** A cycle through it lies in τM, but its previous vertex is in S, and S ∩ τM = τ(S ∩ M) = ∅.
6. **The same holds in D.** The cycles of both digraphs therefore use only the common arcs, so they are the same cycles. ∎

### Proof of Theorem 1

**The map.** For x ∈ L_q(c), take S*, P, γ and R from Lemma C, and F from Lemma D. Set Φ_q(x) = x + 1_F + 1_{tail ∈ R}.

**Φ_q(x) lies in L_q′(c).**
- By Lemma D (with t = t_q and S = S*), D₁ = D(x + 1_F, t_q + 1_γ) has the same directed cycles as D(x, t_q).
- By Lemma A with R, D₁ ≅ D(x + 1_F + 1_{tail ∈ R}, t_q + 1_γ + δR) = D(Φ_q(x), t_q + χ⁰) = D(Φ_q(x), t_q′). The isomorphism is a sheet relabelling ρ_R.
- ρ_R preserves projections and offsets. So the cyclic edges, clusters and periods of sector q′ for Φ_q(x) are those of sector q for x.

**Φ_q′ undoes Φ_q.**
- The strong components fixed by τ correspond under ρ_R with the same projections.
- So the construction applied to Φ_q(x) in sector q′ picks the same P, and therefore the same γ, F and R. These depend only on P and the lattice.
- Hence Φ_q′(Φ_q(x)) = Φ_q(x) + 1_F + 1_{tail ∈ R} = x.
- **Why the twist comes back.** From sector q′ the move gives the twist t_q′ + 1_γ = t_q + δR, and the gauge by R returns t_q.

**Conclusion.**
- **The bijection.** Symmetrically, Φ_q(Φ_q′(y)) = y, so Φ_q is a bijection L_q(c) → L_q′(c).
- **The laws.** Uniform measure gives every orientation the same weight, so the probabilities agree. The cycle statistics agree because D(Φ_q(x), t_q′) = ρ_R(D₁). ∎

### Proof of Corollary 2

- **The sums.** odd_q = Σ ℓ_q(c) over the classes with q(c) odd: an odd winding and a cross exclude each other.
- **Which classes count where.** By Theorem 1, ℓ_q(c) = ℓ(c) for both twists odd on c:
  - classes ≡ (1, 0) count in sectors 10 and 11;
  - classes ≡ (0, 1) count in sectors 01 and 11;
  - classes ≡ (1, 1) count in sectors 10 and 01.
- **The rest.** Substitute into the exact identity of `TWIST-RELATIONS-20261022-001A-P001`. ∎

### Proof of Proposition 3

**What holds.**
- **The band's split.** Let B = [a, b) be inert, with halves M and τM. Every arc between the lift L of B and the rest leaves M or enters τM.
- **The crossing edges at the top cut.** They have their lattice tail in row b − 1 ⊆ B. A seam there flips their twists, which keeps the tail end and its direction and moves only the head ends outside L.
- **Directed cycles.** M stays closed under predecessors, and any directed cycle meeting L lies inside M or τM. So directed cycles do not change.
- **Bands whose inertness can change.** These are bands that contain row b, the head row.
  - Bands with smaller top contain row b only when b = Lv and they contain row 0.
  - So the minimal-top rule is an involution once bands containing row 0 are excluded.

**What fails.** check.py shows on the stored orientation that, without the exclusion, the rule's image has a different smallest top.

## Interpretation (not theorem)

- **The loop shields the twist.** A lone contradiction loop along c carries its own barrier. Every arrow crossing its upper boundary leaves the upstream sheet or enters the downstream sheet. So the transverse twist can be slid onto that boundary without the loop noticing. "The loop is blind to the transverse twist" is now a theorem, in the form stated above.
- **A relation, not a value.** The identity fixes the relation between two unknown probabilities exactly, on every torus, while neither probability is known in closed form.

## Check

`check.py` (standard library):
- **Exhaustive 3 × 3 at shears 0 and 1.** For each of the 8112 and 4056 line configurations in the twisted sectors:
  - the wall lemma: the same arcs on directed cycles;
  - the image lies in the other line event;
  - the involution returns the orientation.
  - The line counts equal those of `TWIST-RELATIONS-20261022-001A-P001`: 2028 per sector and class.
- **Random walks inside nine line events.** On tori from 4 × 4 to 9 × 4 and 7 × 7, with shears from −3 to 4 and classes (1, 0), (0, 1), (1, −1) and (1, 1): 10,558 distinct orientations, every one passing. 8,341 of them have bent walls that use both edge directions.
- **Controls (each rejected):**
  - moving the twist along the wall without the bit flips changes the cyclic arcs (18,668 times);
  - changing the sector without any move leaves the line event (17,254 times);
  - the unrestricted straight-band rule is not an involution on the stored 4 × 4 orientation, on which the wall involution works.
- **Independent exact evidence.** `ODD-LOOP-20261023-001A-E001` counts every orientation of 13 tori up to 4 × 4 by separate C code. The identity holds in all 126 comparisons.

## Scope

- **Model.** Square-lattice tori with periods (Lh, 0) and (s, Lv), uniform random orientations, and their twisted double covers.
- **Exact results.** Theorem 1 and Corollary 2 hold exactly at every size, shear and primitive class. The argument does not use Lh, Lv ≥ 3.
- **Measure.** The bijection flips bits, so it preserves only the uniform measure. Biased orientations are not covered.
- **A different statement.** The stronger claim that the line probability does not depend on the shear is a statement about different tori. It is refuted by `TWIST-RELATIONS-20261022-001B-E001` and, exactly, by `ODD-LOOP-20261023-001A-E001`: on 4 × 4 the horizontal line has 39168000 orientations at shears 0 and 1 and 39085056 at shear 2.
- **Not claimed.** No space or physics is claimed.
