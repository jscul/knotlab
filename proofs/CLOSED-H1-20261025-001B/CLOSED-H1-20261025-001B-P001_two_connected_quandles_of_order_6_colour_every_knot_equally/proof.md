# The two connected quandles of order 6 colour every knot equally

Status: Proved

## Standard statement

**Setting.**
- K ⊂ S³ is a knot with exterior X, group π = π₁(X), meridian μ and preferred longitude λ.
- λ lies in the commutator subgroup π′ and commutes with μ.
- In S₄, the normal subgroup V₄ = {1, (12)(34), (13)(24), (14)(23)} has quotient S₄/V₄ ≅ S₃, which acts on the three pairings of
  {1, 2, 3, 4}.
- Every transposition and every 4-cycle maps to a transposition of S₃.
- Over each transposition t̄ of S₃ lie two transpositions and two 4-cycles. Over {12 | 34}, these are (12), (34), (1324) and (1423).
- For a transposition t, write z_t for the double transposition that commutes with it. If c is a 4-cycle over the same t̄ as t, then
  c² = z_t.

**Theorem.**
- **(a) Transposition longitudes are trivial.** Every homomorphism ρ: π → S₄ with ρ(μ) a transposition has ρ(λ) = 1.
- **(b) Equal lifts over every S₃ colouring.**
  - Let φ: π → S₃ send μ to t̄, and fix a transposition t and a 4-cycle c over t̄.
  - The lifts ρ of φ (homomorphisms π → S₄ with ρ ≡ φ mod V₄) with ρ(μ) = t are as many as those with ρ(μ) = c.
  - All lifts with ρ(μ) = c have the same longitude, 1 or c².
- **(c) The two quandles colour every knot equally.**
  - Every knot diagram has as many colourings by the conjugation quandle of the transpositions of S₄ as by that of the 4-cycles.
  - These are the two connected quandles of order 6: C[6,1] = G(Z₂, 0) and C[6,2] = G(Z₂, 1) in the notation of Clark, Elhamdadi,
    Hou, Saito and Yeatman.
  - So their colouring numbers agree on every classical knot.
  - Every knot with a non-trivial Fox 3-colouring has a non-trivial C[6,2] colouring.

## Nearest known result

- **Clark, Elhamdadi, Hou, Saito and Yeatman**, *Connected quandles associated with pointed abelian groups*, Pacific J. Math. 264
  (2013); arXiv 1107.5777.
  - Remark 6.6 conjectures that C[6,1] and C[6,2] have the same colouring numbers for all knots, among other pairs of Galkin quandles.
    The evidence is a computer check on the 2,977 knots with at most 12 crossings.
  - Remark 6.8 gives a virtual knot on which the two numbers differ.
- **Carter, Oshiro and Saito**, *Symmetric extensions of dihedral quandles and triple points of non-orientable surfaces*, Topology
  Appl. 157 (2010); arXiv 0905.3374.
  - They conjecture that every 3-colourable classical knot has a non-trivial colouring by R̃₃, which is C[6,2].
  - They note a virtual counterexample.
- **Ishikawa**, *Generalization of Galkin quandles and lifting property of dihedral colorings*, Geom. Dedicata 219 (2025), article 70.
  - The abstract proves that every colouring by the dihedral quandle of order 2m + 1 lifts to the (2m + 1)-dimensional hyper-octahedral
    quandle.
  - It also says that lifts carry homological information about irregular branched covers.
  - The full text is behind a paywall and was not read. It may contain the existence statement at the end of (c). The abstract does not
    mention equal counts.
- **Johnson and Livingston**, *Peripherally specified homomorphs of knot groups*, Trans. AMS 311 (1989), as cited by Eisermann, *Knot
  colouring polynomials*, Pacific J. Math. 231 (2007), §2B.
  - They characterize the possible longitude images by homological obstructions.
  - Part (a) is an instance of that theory.
- **What is new here.**
  - The proof of the equal-count conjecture for the pair {C[6,1], C[6,2]}, by half-lives-half-dies for the twisted lifting cohomology.
  - The refinement that the equality holds over every S₃ colouring, with one longitude per colouring.
- **Novelty.**
  - No proof of the 2013 or 2009 conjecture was found in the bounded scan (`research/CLOSED-H1-20261025-001/scan.md`).
  - Overlap risk is medium for the existence part (Ishikawa 2025) and high for (a).

## 1. Transposition longitudes

**Group facts (check part 1).**
- GL(2, 3) acts on the four lines of F₃². This gives a surjection GL(2, 3) → PGL(2, 3) ≅ S₄ with kernel {I, −I}, a central extension.
- For every transposition t, every lift of t and every lift of z_t anticommute: their commutator is −I.
- The lifts of a 4-cycle and of its square commute.

**The lift exists.**
- The obstruction to lifting ρ: π → S₄ through a central extension by Z₂ is a class in H²(π; F₂).
- For a knot group this group vanishes:
  - X is aspherical (Papakyriakopoulos), so H²(π; F₂) = H²(X; F₂);
  - X has the homology of a circle (Alexander duality).
- **The same fact in Wirtinger terms.** Lift every arc generator arbitrarily. Each relator then evaluates to ±I. Changing the lift of
  one arc flips the signs of the two relators at its ends, because over-arcs enter each relator twice with opposite exponents. So the
  signs can be cleared iff their product is +I. That holds because one Wirtinger relator is a consequence of the others, by an
  identity in the free group that comes from planarity (Rolfsen; Burde and Zieschang). This is the step that fails for virtual knots.

**Proof of (a).**
- Let ρ(μ) = t and let ρ̃: π → GL(2, 3) be a lift.
- Since λ ∈ π′, ρ(λ) ∈ A₄. Since λ commutes with μ, ρ(λ) ∈ C(t) ∩ A₄ = {1, z_t}.
- ρ̃(λ) and ρ̃(μ) commute, because λ and μ do. Lifts of t and z_t anticommute, so ρ(λ) ≠ z_t. Hence ρ(λ) = 1. ∎

## 2. Lifts as twisted cocycles

Fix φ: π → S₃ with φ(μ) = t̄.
- **The section.** Let s: S₃ → S₄ be the inclusion of the stabilizer of a point fixed by t, so that s(t̄) = t. Its image is a
  complement of V₄.
- **The module.** Let V be V₄, written additively, with π acting on the right by v·g = s(φ(g))⁻¹ v s(φ(g)).
- **Lifts are cocycles.** The lifts of φ correspond bijectively to 1-cocycles c ∈ Z¹(π; V), with c(gh) = c(g)·h + c(h), by
  ρ(g) = s(φ(g))·c(g). Expanding ρ(g)ρ(h) gives the cocycle identity.
- **The meridian.** ρ(μ) = t·c(μ). So:
  - ρ(μ) = t iff c(μ) = 0;
  - ρ(μ) = t z_t, the other transposition, iff c(μ) = z_t;
  - ρ(μ) is one of the two 4-cycles iff c(μ) ∉ {0, z_t}.
- **The longitude.**
  - φ(λ) lies in φ(π′) ⊂ A₃ and commutes with t̄, which inverts A₃. So φ(λ) = 1, and ρ(λ) = c(λ).
  - On the boundary torus, μ acts on V as conjugation by t, with fixed line V^t = {0, z_t} = (t − 1)V, and λ acts trivially.

## 3. Half-lives-half-dies

**V is self-dual.** S₃ acts on V ≅ F₂² through GL(2, 2) = Sp(2, 2), which preserves the unique non-degenerate alternating form on F₂².
So V ≅ V* as F₂[π]-modules.

**Lemma 3.1.** The restriction i*: H¹(X; V) → H¹(∂X; V) has rank ½ dim H¹(∂X; V).
- **Exactness.** In H¹(X; V) → H¹(∂X; V) → H²(X, ∂X; V), the second map δ has kernel im i*.
- **Duality.**
  - Poincaré–Lefschetz duality with local coefficients identifies δ with j_*: H₁(∂X; V) → H₁(X; V).
  - The universal coefficient theorem over F₂ identifies j_* with the dual of i*: H¹(X; V*) → H¹(∂X; V*).
  - Hence rank δ = rank i*_{V*} = rank i*_V, using V ≅ V*.
- **Conclusion.** Exactness gives rank i* = dim H¹(∂X; V) − rank δ = dim H¹(∂X; V) − rank i*. ∎

This is the standard half-lives-half-dies argument, with local coefficients. The duality theorems are cited, not proved.

**The boundary.** π₁(∂X) = ⟨μ, λ⟩ ≅ Z².
- The cocycles on Z² are the pairs (c(μ), c(λ)) with (t − 1)c(λ) = 0, so c(λ) ∈ V^t. That is 2 + 1 = 3 dimensions.
- The coboundaries are ((t − 1)v, 0): 1 dimension.
- So H¹(∂X; V) ≅ F₂² has coordinates x = c(μ) mod V^t and y = c(λ) ∈ V^t ≅ F₂.
- The image ℓ of i* is a line.

## 4. Proof of (b) and (c)

**ℓ is a graph over the meridian.**
- Suppose a cocycle c on X had class (0, 1) on ∂X: c(μ) ∈ V^t = {0, z_t} and c(λ) = z_t.
- Then the lift ρ would send μ to the transposition t or t z_t, and λ to z_t. This contradicts (a), since z_{t z_t} = z_t.
- So ℓ ≠ span(0, 1), and ℓ = span(1, ε) for some ε ∈ F₂.

**Consequences.**
- **Evaluation at μ is onto.** The map Z¹(X; V) → V, c ↦ c(μ), is linear. Its image contains (t − 1)V = {0, z_t}, from the
  coboundaries, and a value with x = 1. So it is all of V, and each of the four values is taken by |Z¹(X; V)|/4 cocycles.
- **Equal lifts.** By §2, the lifts with ρ(μ) = t (c(μ) = 0) and those with ρ(μ) = c (one fixed value outside {0, z_t}) number
  |Z¹(X; V)|/4 each.
- **One longitude.** A cocycle with c(μ) ∉ V^t has boundary class (1, y) ∈ ℓ, so y = ε and c(λ) = ε·z_t. All lifts with ρ(μ) = c
  therefore have longitude z_t^ε = (c²)^ε. This proves (b).

**Proof of (c).**
- **Colourings are homomorphisms.** For a conjugation quandle, colourings of a knot diagram are the homomorphisms π → S₄ sending the
  Wirtinger generators into the class.
  - Both classes have six elements and are closed under inversion, so the crossing-sign convention does not matter.
  - By conjugation invariance, the colouring number of a class C is |C| times the number of homomorphisms with ρ(μ) equal to one fixed
    element of C.
- **Summing over φ.** Summing (b) over all φ with φ(μ) = t̄ gives equal numbers for t and c.
- **The identification.**
  - Table 1 of Clark et al. lists C[6,1] = G(Z₂, [0]) and C[6,2] = G(Z₂, [1]).
  - Check part 2 shows that G(Z₂, 0) is isomorphic to the transposition quandle, and G(Z₂, 1) to the 4-cycle quandle (24
    isomorphisms each, none crosswise).
- **The existence statement.** If φ is a non-trivial Fox 3-colouring, (b) gives |Z¹|/4 ≥ 1 lifts with ρ(μ) = c. Each is a
  non-trivial C[6,2] colouring, because its image mod V₄ is the non-constant φ. ∎

**Where the 3-manifold enters.** Part (a) uses H²(π; F₂) = 0, and Lemma 3.1 uses duality. Neither holds for the group of a virtual
knot. The trefoil's Gauss word with one crossing sign flipped is a virtual knot with 5 lifts for t and 1 for c (check part 4), in line
with the virtual counterexamples of Carter–Oshiro–Saito and Clark et al.

## Check

`check.py` uses the standard library only. Its output is `result.json`.

1. **GL(2, 3).** Order 48, onto S₄ with kernel {I, −I}. Every pair of lifts of a transposition and of its commuting double transposition
   anticommutes. Lifts of a 4-cycle and of its square commute (control).
2. **Quandles.**
   - G(Z₂, 0) ≅ the transposition quandle and G(Z₂, 1) ≅ the 4-cycle quandle, 24 isomorphisms each.
   - There are no crosswise isomorphisms.
3. **Knots.** The zoo:
   - braid closures 3₁, 4₁, 5₁, 5₂, 6₁, 6₂, 6₃, 7₁, 8₁₈, 8₁₉ and 10₁₂₄;
   - the alternating diagrams of C₃, C₅ and of the pretzel P(3, 3, 3);
   - the tripled alternating diagrams of six plane graphs;
   - two connected sums;
   - six random 3-colourable braid knots.

   For each knot, every colouring whose meridian lies over t̄ is enumerated by brute force from the Wirtinger presentation, with its
   longitude.
   - **(a)** All transposition longitudes are 1.
   - **(b)** Over every S₃ colouring, each of the four meridian values over t̄ is taken by the same number of lifts, with one longitude
     per value.
   - **(c)** The totals for t and c agree, and 3-colourable knots have non-trivial 4-cycle colourings.
4. **Controls.**
   - The classical trefoil word gives equal counts.
   - The same word with one sign flipped, a virtual knot, gives 5 against 1.
   - The 4-cycle longitudes take both values 1 and c² on the zoo, so (b) is not vacuous.

## Scope

- **Covered.** Classical knots in S³, and colouring counts by the two connected quandles of order 6.
- **Not covered.**
  - Links: the boundary has several tori, and the argument needs restating.
  - Virtual knots, where the statement is false.
  - The other pairs of Galkin quandles in the 2013 conjecture.
- **Cited, not proved.**
  - Poincaré–Lefschetz duality and the universal coefficient theorem with local coefficients.
  - The asphericity of knot exteriors, or the redundancy of one Wirtinger relator.
  - S₄ ≅ PGL(2, 3).
- **No overclaim.** No claim about P versus NP.
