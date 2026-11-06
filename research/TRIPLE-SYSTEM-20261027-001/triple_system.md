# The r = 2 dichotomy: the Lie triple system decides

Epic `TRIPLE-SYSTEM-20261027-001` (2026-10-27).

**The question.** After the past-class-2 epic, the owner chose to continue with an r = 2 dichotomy in every nilpotency class. The
conjecture: counting maps from closed 3-manifold groups into N ⋊ C₂ is hard exactly when some odd bracket tree of character −1
survives.

## Outcome

**The conjecture holds through class 4, and its polynomial half in every class.** The criterion is the Lie triple system of the
involution: 𝔫⁻ with the product [[a, b], c].

1. **Polynomial side, every class** (`TRIPLE-SYSTEM-20261027-001A-P001`, proved).
   - Take π with H¹(π; F_p) = H²(π; F_p) = 0. If [[𝔫⁻, 𝔫⁻], 𝔫⁻] = 0, then |Hom_ψ(π, N ⋊ C₂)| = |Z¹(π; F_p^ψ)|^{dim 𝔫⁻}.
   - Every homomorphism lands in the class-2 subgroup exp(𝔫⁻ + [𝔫⁻, 𝔫⁻]) ⋊ ⟨θ⟩.
   - The condition is equivalent to the vanishing of all odd Lie words of degree at least 3 in 𝔫⁻.
2. **Steering measured** (`TRIPLE-SYSTEM-20261027-001B-E001`, supported under a frozen contract).
   - The obstruction of N ⋊ C₂ on gadget surgeries is the degree-3 Lie part of the cable conjugators, evaluated on all free −1
     classes, including classes in layers 2 and 3.
   - It held for six nonabelian triple systems of class 3 and 4 at p = 5, 7, 11, on 36 of 36 fixture-algebra pairs.
   - Bases and abelian triple systems never obstruct (42 of 42). An independent matrix model and a group-law count agree.
3. **Hardness through class 4, and the dichotomy** (`TRIPLE-SYSTEM-20261027-001C-P001`, proved).
   - Graded algebras of class at most 4 with a nonabelian triple system are #P-hard on 2-surgeries of knots.
   - With A: at r = 2, for closed 3-manifolds with H₁(M; F_p) = 0 and bounded 2-rank, counting is polynomial iff 𝔫⁻ is an abelian
     Lie triple system.

## Steps and what was new

- **The rigid count (A).** At r = 2 with no F_p-homology, the +1 parts cannot vary and cannot obstruct.
  - If triple brackets of −1 elements vanish, 𝔫⁻ + [𝔫⁻, 𝔫⁻] is a class-2 algebra whose +1 part is central.
  - Every twisted cocycle then lifts uniquely, and the lower-central-series bound matches.
  - The argument is a few lines.
- **One-parameter subgroups.** g ↦ exp(c(g)A)θ^{ψ(g)} realizes every class on a summand with one-dimensional H¹, for any N. This
  replaces the symmetric-power constructions of the previous epic.
- **Steering in class 4.** The conjugator value, the label shift and the transport each carry corrections, but every correction
  has the trivial character, so the −1 obstructions see only the degree-3 Lie part. Free layer-2 classes enter exactly as the triple
  bracket predicts; the class-4 cross-layer algebra on x (+) and y (−) is the clean example.
- **The edge weight for any triple product B.** f_B(0, s*) counts zeros of a trilinear form ⟨B(·, ·, ·), s*⟩. It lies strictly
  between its bounds whenever B ≠ 0, so the weight is never constant. For u₄ it reproduces the previous epic's 1225 (times 25 for
  the inert layer-3 coordinate).

## Challenged assumptions

- **"An odd tree landing in a higher layer might add new hard cases, or collapse."** Through class 4 it does neither. Free classes
  of deeper layers act exactly as further −1 elements of the triple system. The criterion is the triple system of all of 𝔫⁻, not
  of layer 1 only.
- **"The first test (trivial-character generators without a surviving odd tree) needs a new argument."** It does not. The
  class-3 cross-layer group is polynomial at r = 2 by the rigid count, and was confirmed by independent counts.
- **"Hardness needs explicit Sym constructions per group."** It does not: one-parameter subgroups work uniformly.

## Literature

- **Lie triple systems and symmetric pairs** (Jacobson; Loos). They supply the right invariant.
- **Samperton–Weiss (arXiv:2602.02885).** Class 2, nilpotent targets, bounded H².
- **Galindo (arXiv:2605.06984).** Unbounded homology.
- **The search.** Bounded, and nothing found that states a complexity dichotomy for nilpotent-by-involution targets.

## Gaps

1. **Class at least 5.**
   - Degree-5 Lie parts of the conjugators and interactions between insertions in layer 5 add terms to the gadget form. Lemma 5.2
     then needs a new argument.
   - Where layer-1 triple brackets vanish, these terms vanish too, and the class-4 argument should go through; this is not
     written.
2. **Non-graded algebras whose gr-triple system is abelian but whose own is not.**
3. p = 2 and p = 3.
4. **r > 2.** The general coprime criterion is open.
5. Manifolds with p-torsion in H₁.
6. Knot exteriors.
7. No external review.

## End-of-epic assessment

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: the r = 2 dichotomy | **Status:** Successful (through class 4; polynomial side for every class) | Polynomial iff the Lie triple system 𝔫⁻ is abelian; hardness by one-parameter bases, class-4 steering and the B-twisted edge weight; experiment supported. |
| Local direction: coprime p-group-by-cyclic counting with bounded H₁ | Continue | At r = 2 the picture is complete through class 4. Class 2 at all r and pairs across layers were settled in earlier epics. |
| Broader exploration: complexity of 3-manifold invariants | Known alternatives | Samperton–Weiss and Galindo cover other regimes; the coprime, bounded-H₁ regime is this program's. |
| Long-term goal: the complexity side of 2 versus 3 | Capability gained | With two values, pairs are rigid and triples decide, exactly. This is the clearest instance yet of "two is easy, three is hard" on the complexity side. It is not an emergence result. |
| Next recommendation: the general coprime dichotomy (every r) | **Next step:** Continue, with a fresh epic | Conjecture: counting is polynomial iff (P2) [𝔫_χ, 𝔫_χ′] = 0 whenever χ, χ′, χχ′ are nontrivial and (P3) [[𝔫_χ, 𝔫_χ⁻¹], 𝔫_η] = 0 for nontrivial χ, η; #P-hard otherwise. The polynomial side should follow from the rigid count verbatim (cheap first test). Hardness combines the class-(K) pairs, the cross-layer pairs and these triples, but must absorb the channel terms of the base at r > 2. Alternative: class at least 5 at r = 2. |
| Interest: that recommendation | **2/3 (Promising)** | It would close the coprime picture. The main uncertainty is the channel terms at r > 2, where the base form is not zero. |
| Execution: that next action | Deferred to the owner | No successor created. Stop condition: a proof of both sides, or a group violating the conjecture. |
