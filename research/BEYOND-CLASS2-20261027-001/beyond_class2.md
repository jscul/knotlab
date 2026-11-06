# Past class 2: cross-layer pairs and four-way Massey interactions

Epic `BEYOND-CLASS2-20261027-001` (2026-10-27).

**The question.** The owner chose to continue past class 2 after the class-(K) dichotomy (`CLASSK-DICHOTOMY-20261026-001`). That
dichotomy says that for coprime class-2 groups N ⋊ C_r, counting is hard exactly with a hard pair: a commutator joining two
nontrivial characters whose product is nontrivial. Two discriminators were open:

1. **The cross-layer test.** Does a class-3 group with no class-2 hard pair become hard through a bracket between layers?
2. **The four-way test.** Is a four-way interaction (a triple Massey product) hard when there is no hard pair at all? The answer
   decides whether the line sits at three-way pairs or at "three or more".

## Outcome

**Both answers are yes. The line is not at three-way pairs.**

1. **A cross-layer hard pair makes counting #P-hard** (`BEYOND-CLASS2-20261027-001A-P001`, proved).
   - The group: the free class-3 group on x (trivial character) and y (α, with α² ≠ 1).
   - The identity: on every closed manifold with H₁ = Z/r and in every sector k, its count equals |Z¹(F_{α^k})| times the
     Heisenberg (α, α) count.
   - So it is #P-hard, while its class-2 quotient has no hard pair and is polynomial.
   - Past class 2, the criterion lives in the associated graded Lie algebra.
2. **A four-way Massey interaction makes counting #P-hard where no pair can be hard**
   (`BEYOND-CLASS2-20261027-001C-P001`, proved).
   - The group: for p ≥ 5, counting maps from π₁ of 2-surgeries on knots (H₁ = Z/2) into G_p = U₄(F_p) ⋊ ⟨diag(1, −1, 1, −1)⟩, of
     order 2p⁶, is #P-hard.
   - At r = 2 no group has a hard pair, and every coprime class-2 group is polynomial.
   - The hardness is carried by the twisted triple Massey product ⟨c_y, c_x, c_w⟩ paired with a fourth class.
3. **The realization was measured** (`BEYOND-CLASS2-20261027-001B-E001`, supported under a frozen contract).
   - The four-way form of the gadget surgeries equals the predicted sum of Magnus tensors exactly. This held on 64 samples per
     fixture for 6 graphs at p = 5, 7, 11.
   - Base vanishing and exact steering held for two pure braids, combined and dragged insertions, and p = 5, 7, 11, 13.
   - Independent group-law counts and a lifting test, on a different presentation and group model, agree.

## Steps

**Ticket A.** Layered crossed homomorphisms through the Lazard correspondence (BCH to degree 3). The count depends only on classes,
and on H₁ = Z/r manifolds the trivial-character parts drop out. The cross-layer group's layer-3 obstruction is the Heisenberg one
for the pair (y, z = [x, y]).

**Ticket C, and its discovery.**
- **Massey products by matrices.** The four-way group is the unitriangular group U₄ with the involution D. Layer 1 is the
  superdiagonal and layer 3 the corner.
- **The J-duality.** For a closed braid, a left-kernel vector of the layer-3 Fox matrix is J^T s for a Fox colouring s. Here J is
  lower-unitriangular with 2(−1)^{q−q′}, the Squier form of Burau at t = −1, and one extra direction comes from [x₀, S]. This turns
  the triple Massey obstruction into an explicit four-linear form Q(c; s).
- **Steering, proved exactly.**
  - The 2-cable of a pure braid with conjugators in γ₃F₄ conjugates each bundle by a central element. Its value is the degree-3
    Magnus tensor of the conjugators, evaluated on bundle functionals.
  - The resulting shift is carried to the bottom by Burau, and J-invariance brings it back to the insertion level: ΔQ = 2 Σ_j Λ_j ℓ_j.
  - No clasper calculus is cited. The steering was first measured up to isomorphism, then predicted exactly with κ = 2, and
    confirmed at four primes and for a second braid.
- **Base vanishing.**
  - Symmetric powers of dihedral representations, Sym³, Sym² and sums, realize every proportional class triple with μ ↦ D and
    λ ↦ I.
  - The meridian amalgam then glues summands. Hence every connected sum of knots with one-dimensional twisted H¹ has Q = 0.
- **The gadget.**
  - One conjugated cabled insertion of P4 per edge, dragging two vertex strands over the others, on a sum of T(2, p).
  - Q = 2 Σ_e T(X_v − X_u; privates), so #Λ = p^{6m−n} Z_f.
- **Hardness.**
  - f is integer and even (scalings and the Galois action), with f(0) = p¹² and f(0, 0, 0, 1) = p⁶(2p⁴ − p²).
  - W = f² is not block-rank-1, so Bulatov–Grohe applies after doubling every edge.
  - No anchor isolation is needed, since r = 2 has one nontrivial sector.

## Challenged assumptions

- **"Lemma S needs a twisted Garoufalidis–Levine theorem or a clasper citation."** Not needed. It is proved directly by Fox
  calculus, centrality and the J-duality.
- **"The template weight is non-negative because of linear sums over private b-coordinates."** That argument was incomplete: the
  affine sums can carry phases. f ≥ 0 holds when some slot of d is 0, and was observed everywhere at p = 5, 7. The proof avoids the
  question by doubling edges.
- **"The base form vanishes on twist-knot sums at α = −1, measured."** Now proved for every sum of knots with one-dimensional V,
  by representations rather than computation.
- **"Hardness past class 2 needs a three-way pair somewhere."** False at r = 2.

## Literature

- **Samperton–Weiss (arXiv:2602.02885).** Class-2 nilpotent targets are polynomial on 3-manifolds with bounded H²; class 3 and
  non-nilpotent targets are left open.
  - With bounded homology, nilpotent targets are trivially polynomial, so any hardness must come from a coprime action.
  - That is exactly this program's setting: H₁ is bounded, but twisted H¹ is not.
- **Other hardness results.** Kuperberg–Samperton 2018 (simple groups); Galindo 2026 (unbounded homology).
- **Classical ingredients.** Turaev 1979 (Milnor invariants and Massey products); Squier and Brendle–Margalit–Putman (Burau at
  −1); Bulatov–Grohe.
- **The search.** Bounded, and nothing found that states hardness for a coprime class-3 target with bounded H₁.

## Gaps

1. p = 2 and p = 3.
2. **r > 2.** The base form has channel terms, measured at p = 7 with r = 3 and r = 6 earlier in the epic. The gadget would need
   to absorb them.
3. Knot exteriors.
4. **A full class-3 criterion.** Which coprime class-3 groups are polynomial?
5. No external review.

## End-of-epic assessment

| Layer | Assessment | Evidence or consequence |
| --- | --- | --- |
| Current attempt: the two discriminators past class 2 | **Status:** Successful | Both proved hard. A cross-layer hard pair is hard (A). A four-way Massey interaction is hard where no pair can be: U₄(F_p) ⋊ ⟨diag(1, −1, 1, −1)⟩ on H₁ = Z/2 surgeries (C). Realization and steering are supported under a frozen contract (B). |
| Local direction: coprime p-group-by-cyclic counting with bounded H₁ | Continue. At r = 2 the boundary now lies strictly between class 2 (always easy) and class 3 (can be hard). | The hard-pair criterion is not the whole story past class 2. Which class-3 groups are easy, and r > 2, are open. |
| Broader exploration: complexity of 3-manifold invariants | Known alternatives | Samperton–Weiss make class-2 nilpotent groups easy and leave class 3 open; Galindo covers unbounded homology. Our line is the coprime, bounded-H₁ regime, where twisted H¹ is unbounded. |
| Long-term goal: the complexity side of 2 versus 3 | Capability gained | With two values (r = 2), pairwise brackets are always countable. The first hard interaction is a nested bracket of three classes read against a fourth. This is a complexity theorem, not an emergence result. |
| Next recommendation: an r = 2 dichotomy in every nilpotency class | **Next step:** Continue, with a fresh epic | Conjecture: hard exactly when some odd bracket tree of character −1 survives in cohomology, else polynomial. First discriminator: a class-3 group at r = 2 with trivial-character layer-one generators and no surviving odd tree; does it stay easy? Alternative: r > 2, where channel terms enter the base form. |
| Interest: that recommendation | **2/3 (Promising)** | A clean conjecture with a cheap first test. The main uncertainty is whether trees landing in higher layers produce new hard cases or collapse to the four-way one. |
| Execution: that next action | Deferred to the owner | No successor created. Stop condition for a successor: a polynomial algorithm for the general r = 2 case, or a class-3 counterexample to the conjecture. |
