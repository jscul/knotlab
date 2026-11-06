# Class-4 gadget locality: equal in intrinsic coordinates wherever tested, not proved

Epic `CLASS4-LOCALITY-20261028-001` (2026-10-28).

**The question.** The owner asked to prove hypothesis (L4) of `CLASS4-PAIRS-20261028-001C` (Theorem 7): "Let's continue with proving
L4". (L4) says that for a zero-jump gadget whose edge is clean modulo γ₄, and fixed data D of degree ≤ 2 on the variety, the
layer-4 system E(c) = A c + b(D) of a graph gadget has the same linear part as the system assembled from single-edge gadgets, and
constant parts differing by an element of its image. Six census algebras are #P-hard if it holds.

## Outcome

1. **The relabeling is the solver's choice** (Lemma R below, proved here).
   - The model solves each layer with a particular solution chosen by a linear solver. At layer 3 that solution may contain an
     arbitrary multiple of each slot-2 block's class colouring.
   - Measure each slot-2 coordinate intrinsically instead: reading-strand colour minus base-strand colour, divided by the class
     colouring at the reading strand. The relabeling of `CLASS4-PAIRS-20261028-001B` is exactly the difference between the global
     and local solvers' choices.
   - So (L4) follows from the sharper statement (L4′): **in intrinsic coordinates the global and local systems are equal.**
2. **(L4′) held in every main configuration, but the frozen run is invalid** (`CLASS4-LOCALITY-20261028-001A`, experiment;
   [report](../CLASS4-LOCALITY-20261028-001A/report.md)).
   - **What held.** In all 84 main configurations (three algebras, graphs up to K₄, four configuration types), the global system in
     intrinsic coordinates equalled the assembled one. Control XA broke equality in 6 of its 15 configurations.
   - **Why the verdict is invalid.** Control XB, an edge whose failures are rare (1 in 15 in the earlier probes), matched in all 7
     of its configurations on the variety. So the run does not certify that the test would catch a failure there; choosing that
     control was a design error.
   - **A coverage gap.** For free class 4 on (0, 1, 1) no parallel configuration reached the twisted regime (P5).
   - The data are descriptive, not confirmatory.
3. **No proof.** Three routes were tried and each stops at a precise point (below). (L4′) remains open (consistent with every main configuration tested, neither proved nor confirmed), and the six
   census algebras remain conditional.

## Lemma R

Fix a gadget, data D of degree ≤ 2 on the variety, and a slot-2 block b with class colouring v_b at character 3 (zero on b's base
strand, nonzero on its reading strand).
- Any two layer-3 solutions differ by a cocycle: a constant plus Σ_b c_b v_b. The functional "reading colour minus base colour"
  kills constants and returns c_b v_b(read_b).
- So there is exactly one particular solution X°(D) whose reading-minus-base difference vanishes on every slot-2 block. The
  solver's X(D) equals X°(D) + Σ_b Φ_b(D) v_b, with Φ_b(D) = (X(D)[read_b] − X(D)[base_b]) / v_b(read_b).
- Intrinsic coordinates a = c + Φ(D) are coordinates relative to X°. The layer-4 system becomes E = A a + b°(D), with
  b° = b − A Φ.

**Lemma R.** If, for every D on the variety, A_Γ = A_loc and b°_Γ(D) = b°_loc(D) (each single-edge system in its own intrinsic
coordinates), then b_Γ − b_loc = A(Φ_Γ − Φ_loc) lies in the image of A. That is (L4), and the counts agree for every D.

*Proof.* Substitute b = b° + A Φ on both sides. ∎

The interpretation of the previous epic stands: the solver picks a defining system, and different choices differ by layer-3
cocycles, which is the indeterminacy of a Massey-type obstruction. The new point is that with the canonical choice X° there is no
indeterminacy left to absorb.

## The crossing-sum formula

For layer k, character χ, t = ζ^χ, and a dual s fixed by Bur_{t⁻¹}(β), with the lower layers solved:

  ⟨R^{(k)}, J_t^T s⟩ = Σ_c ⟨N_c, J_t^T s_c⟩,

summed over the letters c of the braid word. N_c is the layer-k nonlinear part (brackets of lower-layer colours) of the colour
change at letter c, and s_c is the dual transported to that slice.

*Proof.* At layer k the colours propagate linearly (Bur_t) plus the nonlinear terms, so
R^{(k)} = (Bur_t(β) − I)x^{(k)} + Σ_c Bur_t(β[c:])N_c. The first term pairs to zero with the left-kernel vector J_t^T s. Squier
invariance gives Bur_t(β[c:])^T J_t^T s = J_t^T s_c. ∎

So each block equation is a sum over crossings. The dual weight J_t^T s_c equals s_c plus a geometric tail c_b t^{−q} on every
position left of the block's strands, with c_b = (t − 1)t^{−1} Σ_q t^q s(q), the same at every slice.

## Why the tried proofs stop

- **Bookkeeping in the braid presentation.** Locality would follow if each block's tail picked up nothing from other blocks.
  - The tails are real: the twisted sums Σ_q t^q v_b(q) of the class colourings are nonzero for vertex and slot blocks.
  - In a stretch twisted by one edge's degree-3 conjugator, a free vertex bead has constant layer-3 colour on its interior and a
    different constant on its junction strands. Its layer-4 flux depends on its own state.
  - The next bead's equation is still exact, so the cancellation runs through their shared junction.
  - The reversed-product identity does show that an insertion's own crossings contribute nothing to a block lying right of all its
    grabbed strands; the field changes it induces elsewhere are not covered by that argument.
  - Straddled blocks are unavoidable. To avoid them, each edge's touched beads would have to be consecutive on the spine. At a
    vertex of degree 3, the three intervals all contain the vertex's bead, and a bead has only two sides, so two of them overlap
    and one edge's span contains another edge's bead.
- **Isotopy.** If intrinsic equations were isotopy invariant, an untouched bead could be slid to the front of the chain, where
  nothing passes over it and it has no tail.
  - Beads carrying other edges' fingers cannot slide past each other: the fingers would cross the other bead's arcs.
  - Intrinsic coordinates depend on the basepoint paths. Moving a bundle of strands over a bead conjugates it by an element whose
    degree-1 part is a twisted sum of other beads' data, which shifts a slot-2 coordinate by a bracket with those data. A change
    of presentation therefore relabels non-locally, even though counts are unchanged.
- **Duality.** The cleanest route would identify the model's pairing ⟨o, J_t^T s⟩ with the twisted cup-product pairing of the
  exterior, then localize the cup product to a neighbourhood of the bead.
  - The identification is not in the literature in usable form: Goldschmidt (1990) states that the scaled Squier form is
    "probably" the Blanchfield form for knots.
  - Even granted, an untouched bead in a twisted stretch sees the band's holonomy as a genuine twist of its own closure. So
    localization must still show the equation is blind to that twist.

## A route not yet carried out: gluing along bead spheres

- **The idea.** Cut the knot exterior along small spheres around the summand beads. A clasper's fingers run in front of the
  diagram, so they can be kept off the spheres of beads they do not touch. Van Kampen then writes the pinned count as a sum over
  boundary data of per-bead amplitudes times per-clasper Borromean relations. That is graph-local by construction, with no
  basepoint path crossing another bead.
- **What it leaves.** The amplitude of one vertex bead carrying several groups of fingers must be additive in the groups and
  independent of where each group sits along the read strand, and each clasper's leaves must read the bundle products.
- **A naive version fails.** Take a closed vertex bead and conjugate its copies' top values (jumps, no passing).
  - The same jump gives different equations at copies 0–3 and at copies 4–7 of an eight-copy bead.
  - Jumps that do not preserve the reversed product break the identity among relators that the duality relies on, so these
    "equations" are not obstructions of the bead piece.
  - The bead piece has to be treated with relative obstruction theory, with boundary data on its punctured sphere.

## The precise remaining obstruction

(L4′) on all graphs. It is equivalent to: in intrinsic coordinates, a block's layer-4 equation does not depend on the degree-3
conjugators of edges that straddle it without touching it, nor on the junction offsets they induce. Every tested configuration
satisfies it. A proof needs a presentation-independent version of intrinsic coordinates, or the duality above together with a
twist-blindness lemma for a single bead.

## Literature

- Squier, The Burau representation is unitary (1984), as used in `COPRIME-PAIRS-20261027-001A`.
- Goldschmidt, Pacific J. Math. 144 (1990): the scaled Squier form is probably the Blanchfield form for knots.
- Krushkal's additivity of μ̄-invariants under band sums (via secondary sources, as in the predecessor) remains the closest
  analogue; it needs separating spheres, which shared beads do not provide.

## Gaps

1. (L4′), hence (L4), on all graphs: the obstruction above. Theorem 7 and Corollary 7.1 stay conditional.
2. A confirmatory test of (L4′): the frozen run is invalid (an underpowered control, and no twisted regime for (0, 1, 1)).
3. The other twenty (K)-only census algebras (d = 7, 9) are untested (no summand braids).
4. No human or external review.

## An owner-requested todo

On 2026-10-28 the owner asked for a todo on whether to share the note on Rowell's conjecture. It is ticket
`ROWELL-NOTE-SHARING-20261028-001`, blocked on the owner's decision, created in this scope. It is administrative: no research
content, no result.

## Work ratio

- **Artifacts that changed a conclusion (1):** Lemma R with the intrinsic reformulation. The frozen experiment ran but is invalid,
  so it changed no conclusion.
- **Scoping that sharpened the obstruction:** the crossing-sum formula, the free-bead structure, the twisted sums.
- **Administrative:** the closure ledger and records.

## End-of-epic assessment

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: prove (L4) | **Status:** Partially successful | The relabeling is explained (Lemma R), and (L4) follows from the sharper (L4′). (L4′) held in all 84 main configurations, but the frozen run is invalid (an underpowered control; no twisted regime for (0, 1, 1)). No proof. |
| Local direction: proofs inside the braid presentation, and by isotopy | Practically exhausted for these two routes | Bookkeeping cannot localize block by block (tails, nonzero twisted sums, cancellation through shared junctions). Isotopy cannot move beads that carry fingers, and intrinsic coordinates depend on basepoint paths. |
| Broader exploration: complexity of 3-manifold invariants (coprime dichotomy) | Known alternatives, diminishing returns | 105 of 850 census algebras open; six conditional on (L4). Samperton–Weiss and Galindo cover other regimes. The last epics completed a census rather than moving the program's intuitions. |
| Long-term goal: the program's core intuitions | Side tangent | The counting chain (18 epics from `HARD-3D-20261025-001` to this one) took the complexity boundary that `PATTERN-3D-20261025-001` only cited and made it the program, on manifolds drawn in advance. Its "two versus three" is the quadratic-versus-cubic boundary of obstruction forms, not 2-CNF versus 3-CNF, and K1–K3 does not see it (`NEXT-DIRECTION-SCAN-20261026-001`, lane C). Not an emergence result. |
| Next recommendation | **Next step:** Full pivot back to the core, at the open half of question 9: geometry from a law, with nothing drawn in advance | Native gluing builds surfaces (`SURFACE-GLUING-20261024-001`), but "no geometry (metric, flatness) appears", and dimension three is answered for bits. First discriminator, in a fresh epic: what a Boolean law of three-place knots fixes of native geometry beyond topology. The gluing route above stays recorded as the best way to finish the census, if it is ever resumed. |
| Interest: that recommendation | **2/3 (Promising)** | Evidence: it is the program's headline question, and both drifts (22–24 October, 25–28 October) came from setups drawn in advance. Main uncertainty: the Boolean base may fix nothing geometric beyond the type of curvature, in which case the answer is a precise negative. |
| Execution: that next action | Taken on the owner's agreement (2026-10-28) | The geometry epic starts after this closure. Whether to share the existing note on Rowell's conjecture is recorded as `ROWELL-NOTE-SHARING-20261028-001`, blocked on the owner's decision. |
