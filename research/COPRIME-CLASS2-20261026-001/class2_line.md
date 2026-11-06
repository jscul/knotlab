# Coprime class-2-by-cyclic groups with bounded homology

Epic `COPRIME-CLASS2-20261026-001`, closed 2026-10-26.

## The question

**How the owner approved it.** The owner answered "Yes, let's continue" to the recommendation of `TRIPLE-PRODUCT-20261026-001`:
1. First, an independent review of its realization and hardness proofs, plus a last prior-art pass under TQFT names.
2. Then an epic on G = N ⋊ C_r, with N of class 2 and order coprime to r. Its conjecture: with bounded H₁, counting is #P-hard exactly
   when the commutator pairing is nonzero on two eigencharacters χ, χ′ with χ, χ′ and χχ′ all nontrivial.

**Intuitions this epic targets.**
- **The complexity side of the 2-versus-3 thesis.** Is the easy/hard line exactly "three nontrivial characters", meaning a genuinely
  three-way twisted interaction?
- **Binding between loops.** The hard instances are built by Borromean moves.

**The evidence:**
- [Independent review](../COPRIME-CLASS2-20261026-001A/review.md) (A, documentation);
- [Heisenberg counting splits into eigen-triple forms that Borromean moves steer](../../proofs/COPRIME-CLASS2-20261026-001B/COPRIME-CLASS2-20261026-001B-P001_heisenberg_counting_splits_into_eigen_triple_forms_that_borromean_moves_steer/proof.md)
  (B, proof);
- [Without a hard pair, counting is polynomial with bounded homology](../../proofs/COPRIME-CLASS2-20261026-001C/COPRIME-CLASS2-20261026-001C-P001_without_a_hard_pair_counting_is_polynomial_with_bounded_homology/proof.md)
  (C, proof);
- [With a hard pair, Heisenberg counting is #P-hard](../../proofs/COPRIME-CLASS2-20261026-001D/COPRIME-CLASS2-20261026-001D-P001_with_a_hard_pair_heisenberg_counting_is_sharp_p_hard/proof.md)
  (D, proof);
- [bounded scan](scan.md).

## Outcome in one paragraph

**The review found no blocking gap** in the twisted-triple-product hardness. Two repairs (the explicit construction, and a novelty
sentence) were carried out here.

**The conjecture is proved for Heisenberg groups over odd prime fields.** For G = H(F_p) ⋊ C_r with the generator acting by
(αx, βy, αβz), counting is:
- polynomial when α = 1, β = 1 or αβ = 1. This holds generally: for every coprime class-2 group without a hard pair (C);
- #P-hard when α, β and αβ are all nontrivial, on r-surgeries of knots and on knot groups (D).

**The mechanism, as tested.**
- The twisted obstruction splits into eigen-triple forms (B).
- Borromean moves steer the component (α, β, (αβ)⁻¹) freely, up to the symmetries forced when characters coincide.
- Each of the four coincidence patterns has a Potts gadget on a #P-hard Tutte hyperbola.

**A consequence for a published conjecture.** Exact counting of homomorphisms from knot groups to these solvable groups is #P-hard.
So is it for S₄, by `BOUNDED-H1-20261025-001A` with `SL23-BOUNDED-20261025-001B`, and for UT₃(F₄) ⋊ C₃, by the +63 identity.
- Rowell's Conjecture 3.2(b) (2009) predicts a polynomial algorithm for every solvable target. It therefore fails, unless every #P
  function is computable in polynomial time.
- No earlier refutation was found. Kuperberg–Samperton (2018) called it doubtful but open.

## How it was found

| Step | Result | Status |
| --- | --- | --- |
| Review, three fresh-context passes | No blocking gap. R1 (construction sketch) and R2 (novelty wording) to repair; nine clarifications | Documentation (A) |
| Prior art | Moussard 2017 is the precursor of the steering. Rowell's Conjecture 3.2(b) was located and quoted | Scan, verified in the primary texts |
| General count and steering over F_p | Brute force agrees in twelve cases. Steering holds in all four coincidence patterns and five character pairs, with zero kernel mismatches | Proved (B) |
| The steering constant | Is the change ±r·det or ±det? The r lifted surgeries contribute r·det, and the transfer divides by r, so it is ±det (invisible over F₄, where 3 = 1) | Corrected while drafting |
| Base knots | Twist knots K_m with m ≡ ζ(ζ − 1)⁻² (mod p) put one-dimensional eigenspaces at ζ^{±1}. Checked for four primes and four knots | Proved (D) |
| The first triangle search at p = 5 | Failed because all figure-eights sat at one end of the braid, so the windows that saw them saw too little of V₂. Interleaving the summands fixed it | Scratch |
| Gadgets | Four Potts gadgets, checked by brute force over F₃ and F₅ (30 cases) | Proved (D) |
| End to end | p = 7 digon 46101601; p = 5 triangles 25925 and 3240625 | Checked (D) |
| Knot groups | The formula agrees with brute force; UT₃(F₄) ⋊ C₃ knot-group counts equal the surgery counts plus 63 | Checked (D) |
| Easy side | The polynomial route agrees with enumeration in 56 cases with p-torsion; brute force in eight | Proved (C) |

## What was proved

| Result | Content |
| --- | --- |
| A | No blocking gap in `TRIPLE-PRODUCT-20261026-001C`/`D`. Repairs and clarifications recorded; novelty labels corrected (steering is the finite-cover analogue of Moussard). |
| B | For H(F_q) ⋊ C_r: count = \|Z¹\| \|B¹\|² × the kernel count of the eigen-triple form on V_α × V_β × V_{(αβ)⁻¹}. Y-surgery with leaves in ker ψ changes every eigen-component by ε Σ_σ sgn(σ) Π (leaf functionals). Over prime fields, pure leaves make every form of the allowed symmetry type realizable. |
| C | Coprime class-2 groups (elementary abelian layers, equivariant bilinear cocycle) without a hard pair: polynomial with bounded H₁, and on knot groups. |
| D | Heisenberg-by-cyclic groups over odd prime fields with a hard pair: #P-hard on r-surgeries of knots and on knot groups (Turing). Dichotomy with C. Explicit polynomial-size construction (review repair). Rowell's 3.2(b) fails for these groups. |

## Observed, not proved

**The general conjecture for arbitrary class-2 N.**
- A route exists: Bulatov–Grohe's weighted-homomorphism dichotomy applied to the edge weight q^{d − rank κ(δ, ·)}.
- But a group with several nonzero κ-components on the same character triples needs a uniform gadget, which was not built.

**Pattern 1, all characters distinct.**
- The steering is checked (p = 7, r = 6).
- No end-to-end knot was built: braid windows rarely give rank-one leaf families.

## What this changes

**For the complexity side of the 2-versus-3 thesis.** For these groups, with bounded homology, the line is:
- no hard pair, meaning each obstruction component has a trivial character in some slot: countable, by enumeration of a bounded part
  or by bounded quadratic Gauss sums;
- a hard pair, meaning three nontrivial characters: a genuinely three-way twisted form whose free part encodes the Potts model.

"Three-way" is now a precise condition on characters, and the dichotomy is exact for the Heisenberg family.

**For binding between loops.** This is interpretation, not proof.
- The hard instances come from Borromean (Y-) moves, which bind three loops as a whole.
- Pairwise data, such as linking pairings and Bocksteins, are invariant under these moves.

**For the literature.**
- A 2009 conjecture about exact counting for solvable targets on link groups fails, already for S₄, a result this program proved on
  2026-10-25 without noticing the connection.
- The positive cases that Rowell listed (abelian groups; nilpotent groups on knots) are consistent with our polynomial classes.

## Assumptions in the workspace this challenges

| Assumption | Where it lives | Verdict |
| --- | --- | --- |
| The steering formula is new | `TRIPLE-PRODUCT-20261026-001C` novelty | **Corrected.** Moussard's 2017 rational formula is the precursor; ours is the finite-cover, F_q analogue. |
| The hardness answers Samperton–Weiß's twisted question negatively | `TRIPLE-PRODUCT-20261026-001D` novelty | **Withdrawn.** Their theorem assumes bounded twisted H². What we show is that bounded H₁ is not enough. |
| The S₄ knot result is "only" bounded-homology hardness | `BOUNDED-H1-20261025-001A` framing | **Understated.** It contradicts Rowell's Conjecture 3.2(b). |
| The steering change is r·det | Draft of B | **Corrected** to ±det, since the transfer cancels r. |

## Provenance and novelty

| Result | Where it came from | Novelty |
| --- | --- | --- |
| A | Three independent passes | Review; no new claim |
| B | Massuyeau's lemma in the r-fold cover; eigenprojectors over F_p | Finite-cover analogue of Moussard. Folklore risk medium to high |
| C | Matei–Suciu lifting; Samperton–Weiß Gauss sums | Candidate-local-delta. Folklore risk medium |
| D | B, C, four character-sum gadgets, twist knots, Jaeger–Vertigan–Welsh | Candidate new: bounded-homology and knot-group hardness for this family, and the dichotomy. Folklore risk medium |
| The Rowell consequence | `BOUNDED-H1-20261025-001A` + `SL23-BOUNDED-20261025-001B` + D | Candidate new as an observation. It needs external confirmation before any claim leaves the repository. |

**Did the perspective do real work? Yes.**
- The 2-versus-3 framing predicted the criterion: three nontrivial characters.
- The Borromean (irreducibly three-way) move was the tool.
- The proofs themselves are standard topology and counting complexity.

## Recommendation

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: the coprime class-2-by-cyclic criterion | **Status:** Successful for the Heisenberg family; partially for general N | Dichotomy proved for H(F_p) ⋊ C_r (p odd) and q = 4, r = 3. The easy side is proved for all coprime class-2 groups. General class-2 hardness and p = 2 in patterns 2 and 4 remain open. |
| Local direction: Heisenberg-type twisted layers | Practically exhausted for prime fields | Remaining: extension fields, p = 2 patterns 2 and 4, pattern-1 end to end. Each is a refinement. |
| Broader exploration: solvable targets with bounded homology | Known alternatives | General class-2 N (Bulatov–Grohe route); approximate counting, where Rowell's 3.2(a) asks for an FPRAS and our reductions go to ferromagnetic Potts, which is #BIS-hard; higher Fitting heights. |
| Long-term goal: the complexity side of the 2-versus-3 thesis | Capability gained | An exact dichotomy, for a natural family, in which "hard" means a three-way interaction of three nontrivial characters. |
| Next recommendation: write the Rowell result up | **Next step:** Continue, as result conversion. A short note: "Counting homomorphisms from knot groups to solvable groups can be #P-hard", covering S₄, UT₃(F₄) ⋊ C₃ and the Heisenberg dichotomy. | It contradicts a published conjecture that Kuperberg–Samperton called open. Add a one-paragraph check of the #BIS consequence for part (a). Prepare an external-review package. Sharing is the owner's call. |
| Interest: that recommendation | **3/3: Hot** | A clean, checkable refutation of a stated conjecture, with an exact dichotomy for a family. Main uncertainty: prior art not found by the scans (the Chlopecki–Samperton work is still unpublished), and whether experts consider S₄ hardness folklore. |
| Execution | Deferred to the owner | Bound: one note, reusing the existing proofs. Stop if an external check finds prior art or a gap. |

**Alternatives:**
- **General class-2 hardness (2/3).** The Bulatov–Grohe route, with a uniform gadget for several κ-components.
- **Approximate counting (2/3).** #BIS-hardness of approximating H_L(G) for these groups, which bears on Rowell's 3.2(a).
- **Return to the core program (2/3).** Through the Borromean bridge: which constraint systems on loops realize free three-way forms?
