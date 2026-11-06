# Pair failures: reductions, inert layers, clean edges and conserved flows

Epic `COPRIME-PAIRS-20261027-001` (2026-10-27).

**The question.** The owner (via Codex) asked for two phases.
- **Phase 1.** Address the independent AI review of `COPRIME-DICHOTOMY-20261027-001`: four corrections and two expansions, with
  precise references, preserving the frozen predecessors.
- **Phase 2.** Pursue the remaining pair failures in classes 3 and 4. Start with the reduction when higher layers avoid the
  class-(K) gadget characters, then genuinely interacting cases. Recover the actual total count across sectors. Seek a general
  hardness proof or a polynomial counterexample, or state the obstruction precisely.

## Outcome

**Phase 1: the corrected and expanded presentation.**
- `COPRIME-PAIRS-20261027-001A-P001` (proved) reissues the triple-hardness proof:
  - the literal Fox matrix is t⁻¹(Bur_t − I), with the same column space;
  - the cable homomorphism exp(c(g)A)θ′^{u(g)} uses the integer exponent (θ′ of order 6 at d = 12, k = 2);
  - the edge-weight lemma uses the actual coefficients;
  - "(P2) supplies a compatible parity automorphism" replaces "the action collapses to an involution".
- It expands two steps:
  - canonical pinned coordinates, on which the amphichiral symmetry acts linearly;
  - the reading strands and basis for both summand families. Cable colourings are bundle constants, and for amphichiral summands
    the two-partition lemma plus an over-strand conjugation supplies them.
- It gives precise references.
- `COPRIME-PAIRS-20261027-001B-P001` (proved) is the corrected presentation. It records every review as an independent AI review
  with finite V2 checks, and its check verifies the reviewed hashes.

**Phase 2: three hardness theorems for interacting pair failures, and a precisely stated obstruction for the rest.**
1. **Reduction to the ideal of nonzero characters** (`COPRIME-PAIRS-20261027-001C`, Theorem 1). Every map over a sector of order d
   from a group with H¹(π; F_p) = 0 lands in exp(𝔪_d) ⋊ C_d, and so does every pinned knot-group map. Trivial-character generators
   drop out. The cross-layer theorem of `BEYOND-CLASS2-20261027-001A` is this reduction (𝔪_d has class 2 there).
2. **Inert transfer** (C, Theorems 2–3). Suppose a quotient 𝔪/𝔨 has a pinned slope-d/p hardness family with active characters A,
   and no component of 𝔨 has a character in A. Then G is hard, and Lemma I recovers the total count across sectors. Instances:
   - class-2 quotients with a hard pair (class-(K) gadget knots at slope d/p);
   - graded quotients satisfying (P2) with a near triple (the triple construction).
3. **Clean edges** (`COPRIME-PAIRS-20261027-001E`, Theorem 4). Interacting pair failures (higher layers at active characters) are
   hard whenever there is a clean edge:
   - a hard pair of 𝔪̄/γ₃ (𝔪̄ = 𝔪 or 𝔪/γ₄(𝔪), class ≤ 3);
   - brackets between distinct leaves vanish modulo γ₃ outside the characters that the private duals force to zero;
   - the layer-3 brackets of the two private leaves, including their determined layer-2 parts, avoid the vertex roots;
   - γ₄ is inert.

   Theorem 5 refines this: vertex–private brackets may also land at character 0, provided their character-0 parts commute with the
   private leaves at vertex roots. A character-0 conjugator commutes with τ, so it never moves a junction strand.

   The proof:
   - **Zero-jump gadget knots.** Summand blocks whose junction strands carry the meridian value exactly, and dedicated copies of
     vertex strands, make every colour local.
   - **Locality.** On the layer-2 variety every insertion acts by central shifts, so the pinned count is an edge-local integer
     partition function Σ_σ Π_e F(σ_u, σ_v).
   - **The Brunnian rank lemma.** F(σ, σ) is maximal, because the insertion is trivial when its vertex bundle is. A pair-failing
     difference makes F strictly smaller but positive.
   - **Subdivision.** It turns F into the symmetric M = F Fᵀ of rank ≥ 2.
   - **The total count** across sectors is recovered by Lemma I, and Bulatov–Grohe applies.
4. **Conserved flows** (`COPRIME-PAIRS-20261027-001F`, Theorem 6). When an edge fails only (V₃), its vertex equations are a flow
   that every vertex conserves: by the bundle identity, the tail's d − 1 copies and the head's one copy read the same flow with
   opposite signs. Fourier duality turns the count into a spin system on vertex states and potentials. It has non-negative integer
   weights when:
   - the flow vanishes off the diagonal, because the deficit equations kill the private layer-1 leaves (F1), and the vertex has no
     layer-2 data (F0);
   - the flow is bilinear on the diagonal (F2).

   The Brunnian rank witness and subdivision then give hardness as before.
5. **Census** (850 free graded algebras on two or three generators, classes 3 and 4, d ≤ 12, every divisor allowed):

   | status | count |
   | --- | --- |
   | criterion at every order (polynomial) | 10 |
   | hard by the triple theorem at a divisor | 511 |
   | residual, decided by reduction and inert transfer | 153 |
   | residual, interacting, decided by a clean edge (Theorem 4) | 50 |
   | residual, interacting, decided by the character-0 refinement (Theorem 5) | 5 |
   | residual, interacting, decided by conserved flows (Theorem 6) | 8 |
   | residual, interacting, open | 113 (34 of class 3, 79 of class 4) |

   - The Theorem 4 row includes 4 class-4 algebras. Each has a trivial-character generator, so 𝔪_d has class 3.
   - The quotient option 𝔪/γ₄(𝔪) decides no census algebra.
   - The Theorem 5 row is free class 3 on (0, 1, −1) at d = 5, 7 and 9, on (0, 2, 8) at d = 10 and on (2, 5, 8) at d = 10.
   - The Theorem 6 row is free class 3 on (1, 1, 2) at d = 5, (1, 2, 4) at d = 6, (1, 1, 4) at d = 7, (1, 2, 3) at d = 9,
     (1, 4, 6) and (2, 2, 4) at d = 10, and (2, 3, 4) and (2, 4, 8) at d = 12.

6. **Experiments** (ticket `COPRIME-PAIRS-20261027-001D`, five interacting algebras, single-edge and path gadgets).
   - **E001** (frozen contract): **refuted**. Its path-locality rule drew the neighbouring edge's private data at random, mostly off
     that edge's solution set. A5 (free class 3 on (1, 2) at d = 4) failed it in one of three configurations. Every other rule held
     in all five algebras, and both controls behaved as required.
   - **Diagnostics** (post hoc, other seeds). With the neighbouring data on its solution set, A5's path sets matched the single edge
     in 36 of 36 comparisons. Off it they differed in 7 of 24. The theorem claims locality only on the solution variety.
   - **E002** (successor contract, fresh seeds): **supported**. Every rule held in all five algebras. On the variety, e₀'s path
     solution sets equalled the single edge's in all 32 comparisons, and e₁'s equations and the vertex pairings vanished on every e₀
     solution. The controls behaved as required: the cumulative design broke locality (6 of 6 comparisons), a missing dual slot left
     no deficit, and off-variety data reproduced E001's failure (11 of 24).

## The precise remaining obstruction

An interacting algebra is decided by the present constructions when one failing order has a clean edge (Theorem 5) or a flow edge
(Theorem 6). For each of the 113 open census algebras, take every failing order, quotient option and hard pair, and record which
conditions of Theorem 5 fail. The minimal failing sets are (checked in E, check 7, and F, check 1):

| class | minimal failing sets | algebras |
| --- | --- | --- |
| 3 | (V₃), with (F0) or (F1) failing | 8 |
| 3 | (B₀) + (V₃) | 9 |
| 3 | (B₀) + (V₃) + (V₃′) | 8 |
| 3 | (B₂′) | 2 |
| 3 | two alternatives | 7 |
| 4 | (K) | 26 |
| 4 | (B₀) + (K) + (V₃) | 20 |
| 4 | (K) + (V₃) | 12 |
| 4 | (B₀) + (K) + (V₃) + (V₃′) | 8 |
| 4 | (B₂′) + (K) | 2 |
| 4 | two alternatives | 7 |
| 4 | no hard pair modulo γ₃ | 4 |

Every open class-3 algebra has three generators. The (V₃) row started at 16, and Theorem 6 decided 8 of them.

The mechanisms:
- **(B₀).** The two private leaves bracket nontrivially modulo γ₃. The vertex copies then receive a non-central layer-2 shift.
- **(B₁′)/(B₂′).** A vertex–private bracket lands at a nonzero character outside the forced ones. Its layer-2 conjugator moves the
  junction strands of the private bundle off τ, so colours stop being local.
- **(V₃), (V₃′).** A layer-3 bracket of the private leaves sits at a vertex root. This gives vertex equations: a flow conserved at
  every vertex. Theorem 6 handles the flow when it vanishes off the diagonal and is bilinear on it. In the 8 remaining algebras,
  either the deficit equations leave a private leaf parallel to the vertex difference (F1 fails), so off-diagonal flows can
  survive, or the vertex has layer-2 data (F0 fails).
- **(K).** Class 4 with γ₄ at an active character, for example free class 4 on two generators of one character at d = 5, where
  γ₄ sits at −a. Two things are missing there: class-4 locality, since layer-4 shifts on passed strands are not central, and a
  treatment of the layer-4 flows.
- **No hard pair modulo γ₃.** One algebra up to coarsening: free class 4 on characters (a, −a) of order 3. Its pair failures
  bracket layer 1 with layer 3 into γ₄. A gadget for it would steer at layer 4 rather than through a hard pair modulo γ₃.

**The vertex equations are conserved flows** (`COPRIME-PAIRS-20261027-001E`, check 6, with scoping probes). On the single-edge gadget
at the diagonal, every private configuration solves the private equations, so the vertex equations alone decide whether edges
couple. At d = 5, p = 11:
- **(K)**, free class 4 on (1, 1): the layer-4 vertex equations are nonzero at 396 of 400 random points;
- **(V₃)**, free class 3 on (1, 1, 2): the layer-3 vertex equations are nonzero at 349 of 400;
- **(B₂) at character 0**, free class 3 on (0, 1, 4): they vanish at all 400. This is the first algebra of Theorem 5.

The two endpoints' vertex equations are exact negatives (F, check 2, and scoping on the class-4 example: 300 of 300 diagonal
points). Each edge carries a flow in F_p^k, leaving one end and entering the other, and every vertex conserves it. The vertex duals
read the same root characters through which the vertex sends its state, so at prime d no arrangement of the bundle separates them.
For (K) and (V₃), the count is therefore a sum over conserved flows, not directly an EVAL(M).

Conserved flows are not by themselves an obstruction. Their Fourier dual is a spin system on states and potentials, and in the
(V₃) example it has non-negative weights:
- the flow vanishes on all 112 sampled off-diagonal solutions;
- on the diagonal it is exactly bilinear, with N̂(μ) = 11⁶ > 0 for μ ≠ 0.

That is Theorem 6. In the class-4 example (scoping), the diagonal flow is conserved too, with a real, positive Fourier transform over
all 161 051 private configurations (minimum 1331), though not uniform on a subspace. Off the diagonal it differs from class 3. At a
pair-failing difference (0, Δ), the vertex terms survive on the 121 solutions, and the two endpoints' terms no longer cancel, because
layer-4 corrections depend on the endpoint colours. So (K) needs both class-4 locality and a treatment of these non-conserved vertex
terms.

This corrects an earlier scoping remark, repeated in the red-team notes of both frozen contracts, that free class 4 on (a, a) at
d = 5 had vanishing vertex pairings on single-edge solutions. That held only at random vertex pairs, where solutions are rare.

No polynomial counterexample was found. Every interacting algebra tested on gadgets showed the maximal-diagonal, deficient-difference
structure for the private equations.

## Steps and what was new

- **The trivial-character reduction** explains the cross-layer theorem and shrinks the problem to the C_d-algebra 𝔪_d.
- **Inertness as a transfer principle** works for any pinned family, not only for a fixed gadget. Hardness then passes from any
  quotient whose kernel avoids the active characters.
- **Zero-jump blocks.** Making every block return to the meridian value removes cumulative colours. These were the source of
  non-locality: the cumulative design gave non-local layer-3 monomials on the solution variety in scoping.
- **The Brunnian rank lemma.** The Borromean commutator braid acts trivially when its vertex bundle is trivial. So the diagonal of
  the edge count is maximal regardless of the higher layers, and the pair failure alone forces rank ≥ 2. Higher layers change the
  weights (11 against 121 in the first example) but cannot cancel hardness while the count stays local.
- **Subdivision symmetrization.** Ordering subdivision vertices last turns an asymmetric edge count into the Gram matrix F Fᵀ.
- **Locality lives on the solution variety.** Off it, an insertion's layer-2 part conjugates passed strands and shifts distant
  blocks at layer 3. E001 measured exactly that failure, and E002's control X3 reproduces it.
- **Character-0 brackets are invisible** (Theorem 5). A character-0 conjugator commutes with τ, so it never moves a junction strand.
  Only brackets at nonzero characters outside the forced ones break locality.
- **Vertex conservation laws dualize to potentials** (Theorem 6). The bundle identity makes every vertex equation a conserved flow.
  When the flow lives on the diagonal and is bilinear there, Fourier duality gives non-negative weights, and the same rank witness
  works.
- **A correction to (V₃).** The leaves' determined layer-2 parts ([X₊, X₋] at character 0) must be included. No census count
  changed.

## Challenged assumptions

- **"Higher layers at the gadget characters break the class-(K) route."** Only when their couplings are non-local. Inside the
  clean-edge range they change the weights, not the rank.
- **"Pair failures need parity for the steering to be clean."** No. On the layer-2 variety the pair steering becomes central, which
  plays the role parity played for triples.
- **"The class-2 quotient must carry the hard pair."** Not after the trivial-character reduction. The quotient of 𝔪_d can carry it
  when the quotient of 𝔫 cannot.
- **"An edge count is local if its equations ignore distant data."** Only on the joint solution variety, which is all the count
  needs. E001's rule asked for more and was refuted.
- **"Vertex conservation laws block the spin-system reduction."** Not when the flow lives on the diagonal and is bilinear there:
  then the Fourier dual has non-negative weights (Theorem 6).
- **"Free class 3 on (a, a) at d = 4 is a test case of the residual family."** Not when 2 ∈ 𝒟: (P2₂) always holds and (P3₂) fails
  there, so the triple theorem decides it.

## Literature

No new external search was run in this epic. The comparison boundaries are those of the predecessor epics: Samperton–Weiss,
Galindo, Kuperberg–Samperton, Rowell, Moussard, Matei–Suciu, Nosaka. The review rechecked Samperton–Weiss and Galindo in the
primary sources. Bulatov–Grohe via Cai–Chen–Lu, Theorem 2.1, is used throughout. Novelty remains a candidate claim. Folklore risk:
- Theorem 1: high (standard p-residual argument);
- Theorems 2, 4 and 5: medium;
- Theorem 6: medium. Fourier duality between flows and potentials is classical (flow–tension duality). Its use to turn a gadget
  count with vertex conservation laws into a non-negative spin system is the candidate contribution.

## Gaps

1. The 113 open census algebras and, beyond the census, every interacting algebra without a clean or flow edge (the mechanisms
   above).
2. Class at least 5; non-graded algebras; p = 2, 3; knot exteriors at d ≥ 3; unbounded sectors.
3. The census covers free algebras on at most three generators with d ≤ 12. Quotients of free algebras can behave differently.
4. No human or external review of the phase-2 results.

## End-of-epic assessment

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: corrections plus the residual pair-failure family | **Status:** partially successful | Phase 1 complete. Phase 2 decides the inert family and the clean-edge interacting family, decides 63 interacting census algebras by gadgets (Theorems 4–6), and reduces the remaining 113 of 850 to stated mechanisms. |
| Local direction: coprime p-group-by-cyclic counting with bounded H₁ | Continue | Every tested interacting algebra shows the hard private structure. The obstruction is a property of the gadget, not a sign of easiness: flows conserved at vertices for (K) and (V₃), non-local junction shifts for (B₂′). |
| Broader exploration: complexity of 3-manifold invariants | Known alternatives | Samperton–Weiss (bounded H²) and Galindo (unbounded homology) cover other regimes. |
| Long-term goal: the complexity side of "two versus three" | Capability gained | Pairs that bracket outside the fixed part are hard as soon as the count can be made edge-local or reduced to conserved flows with a non-negative dual. The Brunnian (three-component, pairwise-unlinked) insertion carries the pair interaction. Not an emergence result: r counts action characters. |
| Next recommendation | **Next step:** Continue, with a fresh epic on class-4 locality and flows | The 26 class-4 algebras blocked only by (K) are the largest family. In the example probed, the diagonal flow is conserved with a positive Fourier transform. Two pieces are missing: at pair-failing differences the endpoint terms stop cancelling, and passed strands receive layer-4 shifts [x, (τ − 1)w] from layer-3 conjugators. First discriminator: path locality on the full solution variety for free class 4 on (a, a) at d = 5, then a layer-4 condition analogous to (V₃) for passed strands. Second: the 8 vertex-root algebras where (F1) fails (off-diagonal flows along the vertex difference). Then (B₀), and the cross-layer algebra (a, −a) at order 3. Alternative: class ≥ 5. |
| Interest: that recommendation | **2/3 (Promising)** | The flow mechanism transferred cleanly in class 3, and the (K) example's diagonal flow already has a positive Fourier transform. Main uncertainty: non-cancelling off-diagonal vertex terms and layer-4 shifts on passed strands may need a new gadget design rather than a new condition. |
| Execution: that next action | Deferred to the owner | This continuation stops at its stated endpoint: theorems for the clean-edge, character-0 and flow-edge families, and a precise obstruction for the rest, where each remaining family needs a new gadget idea. No successor created. Reassess with one test: path locality on the full solution variety for free class 4 on (a, a) at d = 5 decides whether (K) needs a new condition or a new design. |
