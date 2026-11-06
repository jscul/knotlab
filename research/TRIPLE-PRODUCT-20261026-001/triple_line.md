# The twisted triple product and bounded-homology hardness

Epic `TRIPLE-PRODUCT-20261026-001`, closed 2026-10-26.

## The question

**How the owner approved it.** The recommended epic was "Does the twisted triple product make counting hard?". The owner answered
"Yes, let's do it", also approved identifying the coupled blocks, and asked to "keep investigating a bit, then … move back [to the
core program] if it doesn't pan out".

**The setting.** `UT3-TWIST-PROBE-20261025-001` and `UT3-INTERACT-PROBE-20261026-001` showed that for G = UT₃(F₄) ⋊ C₃, a group of
Fitting height 2, the twisted lifting obstruction grows and couples on manifolds with H₁ = Z/3. They left two questions open:
- whether this makes counting hard;
- what the coupled blocks are.

**Intuitions this epic targets.**
- **The complexity side of the 2-versus-3 thesis.** The SL(2,3) obstruction was pairwise (quadratic); this one is three-way
  (cubic).
- **Binding between loops.** The steering moves are Borromean: three loops bound as a whole, with no pairwise linking.

**The evidence:**
- [Counting maps is a twisted cubic Gauss sum](../../proofs/TRIPLE-PRODUCT-20261026-001A/TRIPLE-PRODUCT-20261026-001A-P001_counting_maps_is_a_twisted_cubic_gauss_sum/proof.md)
  (A, proof);
- [The triple forms of the coupled blocks](../../proofs/TRIPLE-PRODUCT-20261026-001B/TRIPLE-PRODUCT-20261026-001B-P001_the_triple_forms_of_the_coupled_blocks/proof.md)
  (B, proof);
- [Borromean insertions steer the twisted triple product](../../proofs/TRIPLE-PRODUCT-20261026-001C/TRIPLE-PRODUCT-20261026-001C-P001_borromean_insertions_steer_the_twisted_triple_product/proof.md)
  (C, proof);
- [Counting maps to UT₃(F₄) ⋊ C₃ is #P-hard with H₁ = Z/3](../../proofs/TRIPLE-PRODUCT-20261026-001D/TRIPLE-PRODUCT-20261026-001D-P001_counting_maps_to_ut3f4_x_c3_is_sharp_p_hard_with_h1_z3/proof.md)
  (D, proof);
- [bounded scan](scan.md).

## Outcome in one paragraph

**Counting homomorphisms into UT₃(F₄) ⋊ C₃ is #P-hard on 3-surgeries of knots, all of which have H₁ = Z/3.** So with bounded first
homology, a solvable group of Fitting height 2 can be hard. The chain:
- **A.** By Poincaré duality, the count is a statistic of one symmetric cubic form, the twisted triple product T on H¹(M; F₄_{ω²}).
- **C.** Borromean (Y-) moves whose leaves lie in the kernel of the character keep H₁ and add any alternating form λ₁ ∧ λ₂ ∧ λ₃ to
  T. So on a given V the realizable forms are T₀ plus every alternating form.
- **D.**
  - For a graph, the alternating form Σ_{uv} (x_u + x_v) ∧ p_e ∧ s_e has kernel count 4^{2m−n} times the 64-state Potts
    partition function at v = 15. That is the Tutte polynomial at (79/15, 16), which is #P-hard to evaluate.
  - Figure-eight connected sums supply V = F₄^d with T₀ = 0, and one Borromean move per edge builds the gadget.
- **The line moves.** It is not the Fitting height. It separates pairwise obstructions with bounded targets (polynomial: SL(2,3))
  from three-way twisted obstructions with a free alternating part (hard).
- **B.** The coupled blocks of the last probe are a twisted Bockstein part of corank one plus an alternating part. Their counts
  depend on the alternating part, which Borromean moves change freely, so no closed form follows from the twisting.

## How it was found

| Step | Result | Status |
| --- | --- | --- |
| Reformulation | Obstruction class = a ⌣ b; duality turns "a ⌣ b = 0" into "T(a, b, ·) = 0" | Proved (A) |
| Steering idea | Y-surgery with leaves in ker ψ lifts to three surgeries in the 3-fold cover; on the eigenspace they add with constant 3 = 1 | Proved (C), citing Massuyeau's Lemma 3.2 |
| Gadget idea | A determinant per edge makes the sum over (p_e, s_e) give q⁴ or q⁶ according to whether the vertex colours agree: a Potts model with q³ colours | Proved (D); brute force over F₂ and F₄ |
| First insertion test | No change at the first level tried: the leaves there are dependent under the correct right-to-left convention | Consistent with C |
| Insertion law | 20 single insertions, multiple insertions and a trefoil base: exact kernel match for every a; wrong conventions and scalars mismatch | Checked (C) |
| End to end | Triangle (two knots) and digon (two knots): 𝒩 = 45162496 and 326656, equal to the gadget values; \|Hom\| = 1 + 128 · 4^d · 𝒩 | Checked (D) |
| A library bug | Partial reduction modulo coboundaries gave non-canonical obstruction classes; caught by the triangle test and fixed before any result was written | Fixed |
| Coupled blocks | Bockstein rank d − 1; counts change with the alternating part | Proved (B) |
| Literature | No preemption; closest are Massuyeau, Nosaka, Galindo (unbounded homology) and Rossmann | Scan |

## What was proved

| Result | Content |
| --- | --- |
| A | \|Hom(π, G)\| over ψ = \|Z¹(F₄_ω)\| · \|B¹(F₄_{ω²})\|² · 𝒩(T), where 𝒩(T) = #{(a, b) : T(a, b, ·) = 0} = \|V\|⁻¹ Σ (−1)^{tr T(a,b,c)}. With H₁ = Z/3, \|Hom\| = 1 + 128 · 4^d · 𝒩. Brute force agrees on six knot surgeries. |
| B | On the coupled family n = 6, 9, 12: one inseparable block of dimension 3, 5, 7 with Bockstein rank d − 1, plus trefoil singletons; counts 244, 8176, 367684; the counts are not functions of the Bockstein part. |
| C | Y-surgery with leaves in ker ψ keeps H₁ and V and adds λ₁ ∧ λ₂ ∧ λ₃. Every functional is a leaf, so T₀ plus every alternating form is realizable, by Borromean moves on knots. |
| D | #P-hard under Turing reductions with one oracle call, on 3-surgeries of knots with H₁ = Z/3, via the Potts gadget and Jaeger–Vertigan–Welsh. |

## Observed, not proved

- **The explicit band recipe was not run end to end.** The four end-to-end knots use leaf configurations found by searching over
  insertion windows. They are equal to the triangle and digon gadgets up to a change of basis, as certified by their rank patterns.
- **A pattern in the coupled family.** The Bockstein rank on the coupled block is d − 1 for d = 3, 5, 7. Whether this holds for all
  m is untested.

## What this changes

**For the complexity side of the 2-versus-3 thesis.** With bounded first homology, the line now reads as follows.

| Kind of obstruction | Example | Complexity |
| --- | --- | --- |
| None beyond linear algebra | abelian-by-nilpotent | polynomial |
| Pairwise (quadratic) with a bounded target | SL(2,3) | polynomial |
| Three-way (cubic) and twisted | UT₃(F₄) ⋊ C₃ | #P-hard |
| A level whose dimension depends on the level below | S₄ | #P-hard |

- Over F₂, counting zeros is easy in degree 2 and hard in degree 3. The bounded-homology line now has a matching topological
  instance: the hard side is reached exactly when the obstruction becomes a genuinely three-way form.

**For binding between loops.** This is interpretation, not proof.
- The move that makes counting hard is Borromean. Its three leaves are bound as a whole, with no pairwise linking: forgetting any
  one leaf unbinds the others, the K2 pattern of the canonical knot test.
- Its effect on the cubic form is the determinant λ₁ ∧ λ₂ ∧ λ₃, which is alternating: it hides every pairwise and diagonal part.
- Pairwise data (linking pairings and the Bockstein part) are invariant under these moves and stay countable.
- So in this setting the source of hardness is irreducibly three-way binding of loops. The thesis predicts exactly this, but here it
  appears in a 3-manifold invariant rather than in a constraint system.

**For patterns of patterns.**
- SL(2,3) had a quadratic sign over an affine level.
- UT₃(F₄) ⋊ C₃ has a cubic form over an affine level, made possible by the twisting.
- The degree of the top pattern, not the number of levels, decides.

## Assumptions in the workspace this challenges

| Assumption | Where it lives | Verdict |
| --- | --- | --- |
| The bounded-homology line separates Fitting heights 2 and 3 | `SL23-BOUNDED-20261025-001` outcome ("as far as tested") | **False.** A Fitting-height-2 group is #P-hard with H₁ = Z/3. |
| Twisted central layers behave like untwisted ones under bounded homology | Samperton–Weiß footnote 11 (an open caveat); `SL23-BOUNDED-20261025-001` scope | **False for this group.** The twisted obstruction lives in a space that can grow, and its cubic form is steerable. |
| A closed form for the coupled-block counts would decide the complexity | `UT3-INTERACT-PROBE-20261026-001` recommendation | **Beside the point.** The counts depend on a freely steerable alternating part; the realizable class contains #P-hard instances. |
| Realizable forms on knot surgeries are constrained by the knot structure beyond the linking data | Implicit in the probes' family-by-family search | **False.** Every alternating perturbation is realizable by Borromean moves. |

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| A | Central-extension obstruction theory (Matei–Suciu) and Poincaré duality with local coefficients | Routine (folklore risk high); the reading as one cubic form is the point |
| B | Duality recovery, singleton splitting, Bockstein rank | Exact computation (low novelty) |
| C | Massuyeau's Lemma 3.2 lifted to the 3-fold cover; leaf functionals span V* | Candidate new (twisted version); folklore risk medium |
| D | Potts gadget (elementary character sums) with Jaeger–Vertigan–Welsh, plus C | Candidate new: bounded-homology hardness for a solvable target of Fitting height 2, and a Potts/Tutte formula for trilinear kernel counts. Folklore risk medium. |

**Did the perspective do real work? Yes, in two places.**
- The 2-versus-3 framing ("is the obstruction pairwise or three-way?") pointed at the triple product. That led to the duality
  reformulation.
- The Borromean (irreducibly three-way) move was the natural steering tool.

The proofs themselves are standard topology and counting complexity.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: does the twisted triple product make counting hard? | **Status:** Successful | #P-hard on 3-surgeries of knots (H₁ = Z/3), proved with end-to-end checks; coupled blocks identified. |
| Local direction: UT₃(F₄) ⋊ C₃ | Practically exhausted | Hardness settled. Open side questions: approximate counting (the Potts point is ferromagnetic), and closed hardness for GL(2,3) and 2O. |
| Broader exploration: the bounded-homology line for solvable targets | Known alternatives | Untested: other characters and characteristics (C_p acting on class-2 p′-groups), deeper nilpotent layers, approximate counting. |
| Long-term goal: the complexity side of the 2-versus-3 thesis | Capability gained | First topological instance where the easy/hard line with bounded homology is the passage from pairwise to irreducibly three-way (Borromean) interaction. The missing bridge: a general criterion. |
| Next recommendation: independent review, then the coprime class-2-by-cyclic criterion | **Next step:** Continue. First: independent review of C and D (Codex, as for the S₄ results) and a last TQFT-phrasing prior-art pass. Then an epic on G = N ⋊ C_r, with N of class 2 and gcd(r, \|N\|) = 1. | Conjecture: with bounded H₁, counting is #P-hard if and only if the commutator pairing is nonzero on two eigencharacters χ, χ′ with χ, χ′ and χχ′ all nontrivial; otherwise polynomial. The hard direction should follow from C and D (the lift constant is r, invertible mod p). The easy direction should reduce to bounded families of bilinear forms. Converting the result into a short note is the owner's call. |
| Interest: that recommendation | **3/3: Hot** | A clean conjecture with a ready proof route; it would give a dichotomy-type statement for bounded homology, where the literature lists solvable targets as unknown. Main uncertainty: the easy direction with mixed characters, and whether r ≥ 3 is really needed. |
| Execution | Deferred to the owner | Bound: one review pass plus one epic. Stop if the review finds a gap in C or D, or if a counterexample to the criterion appears in the first small cases (UT₃(F₄) ⋊ C₃ variants, Heisenberg groups mod 5 with C₃ or C₄ actions). |

**Alternatives:**
- **A short note on the bounded-homology line (2/3).** S₄ and UT₃(F₄) ⋊ C₃ hard, SL(2,3) easy. It needs the review first; sharing
  is the owner's call.
- **Approximate counting (1/3).** Ferromagnetic Potts with 64 colours is #BIS-hard to approximate (Goldberg–Jerrum), and the
  reduction looks approximation-preserving.
- **Return to the core program (2/3).** The Borromean source of hardness gives a bridge back to binding between loops: which
  constraint systems on loops realize free alternating three-way forms?
