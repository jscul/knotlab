# The directed cone of a random orientation on a torus

Status: Proved

Ticket `SC-TORUS-EXACT-20261022-001A`, 2026-10-22. It uses
`NAE-INVARIANT-20261022-001A-P001` ("the reduction proof") for:
- twisted orientations of the double cover;
- the rotated dual orientation;
- Minty's painting lemma;
- the sign rule: every crossing of a directed primal closed walk with a
  directed dual closed walk has intersection sign +1.

It cites the wrapping values of
[Newman, Grassberger and Ziff (2026)](https://arxiv.org/abs/2607.24975),
including their conjecture that one-direction wrapping is exactly 3/4.

## Standard statement

Let T = ℝ²/Λ be a square-lattice torus (Λ ⊆ ℤ², with T a simple graph).
- **Orientations.** D is an orientation of T, and D* is the rotated dual
  orientation of the dual torus T*.
- **Classes.** S(D) ⊆ Λ is the set of classes [W] of directed closed walks.
- **Pairing.** det is the determinant; for periods it is a positive multiple
  of the intersection number.
- **The cone.** C = cone(S(D)) is a closed convex cone. Its polar is
  C° = {y : det(c, y) ≥ 0 for all c ∈ C}.

1. **Directional duality.** For every primitive period d, exactly one holds:
   - (i) D has a directed closed walk W with det([W], d) < 0;
   - (ii) D* has a directed closed walk of class exactly d.
2. **The cone theorem.** A primitive period is the class of a directed closed
   walk of D exactly when it lies in C. A primitive period is the class of a
   directed closed walk of D* exactly when it lies in C°. Moreover,
   cone(S(D*)) = C°.
   - **The six cone types,** with their polars:

     | C | C° |
     | --- | --- |
     | {0} | the plane |
     | a ray | a half-plane |
     | a line | the same line |
     | a sector of opening α ∈ (0, π) | a sector of opening π − α |
     | a half-plane | a ray |
     | the plane | {0} |

3. **Twisted sectors.** For a nonzero twist p, the same holds on the double
   cover (lattice ker p) for the swap-reversed orientation, and C = −C. So C
   is {0}, a line or the plane, and C° is the plane, the same line or {0}.
   This is the exact duality of the reduction proof, in cone form.
4. **Laws.** For the uniform orientation, the law of C is unchanged by C ↦ C°
   and by the symmetries of T. On square tori (V and H are the vertical and
   horizontal lines):
   - **Four equal probabilities.**
     P(C ⊆ V) = P(C ⊇ V) = P(C ⊆ H) = P(C ⊇ H). Here C ⊆ V means no strong
     component winds horizontally, and C ⊇ V means there are pure vertical
     directed cycles in both senses.
   - **Pure versus positive winding.** P(a directed closed walk with positive
     horizontal winding) = 1 − P(a directed closed walk of class exactly
     (1, 0)), which is at least 1/2.
   - **The conjecture restated.** Newman, Grassberger and Ziff's 3/4 is
     equivalent to P(no directed closed walk winds horizontally) = 1/4.
   - **Twisted square, twist along x.** P(no horizontal winding) +
     P(no vertical winding) = 1 − P(C is a line in a class with both
     coordinates nonzero).

## Nearest known result

- **Ingredients.** Minty's lemma and planar duality between directed cycles
  and directed cuts are classical. Theorem 1 is their toroidal version: on an
  annulus, either a directed cycle goes around or a dual directed path goes
  across.
- **The class of models.** Newman, Grassberger and Ziff measure undirected
  wrapping of strong components. Directed classes and polar cones do not
  appear there.
- **Novelty.** `candidate-local-delta`; not found in a bounded search.
  Theorem 1 is a Farkas-type duality, so similar statements may exist for
  periodic orientations or toroidal flows (moderate folklore risk).

## Theorem 1: directional duality

**(ii) excludes (i).** By the sign rule, det([W], [Γ]) ≥ 0 for every directed
primal closed walk W and directed dual closed walk Γ.

**Without (i), (ii) holds.**
- **The cylinder cover.** Let T_d = ℝ²/ℤd, a cylinder whose deck group shifts
  transversally to d, and lift D to it. The level is
  ℓ(x) = det(x, d)/det(Λ). A directed closed walk W lifts to a path changing
  level by det([W], d)/det(Λ), which is ≥ 0 when (i) fails.
- **A region bounded below.** Write any directed walk as a simple path plus
  closed walks. Every directed walk then drops by at most B, the largest drop
  along a simple path of T. So the forward closure R of the upper half
  {ℓ ≥ 0} contains that half, lies in {ℓ ≥ −B}, and is invariant under d.
- **Its boundary is a dual cycle of class d.** Every arc between R and its
  complement points into R. Give each vertex its unit cell, with dual edges
  as sides. The union of the cells of R has a boundary made of the dual edges
  e* for e on that cut.
  - **Orientation.** By the rotation convention, these dual arcs keep R on
    the same side.
  - **Decomposition.** Turning consistently at touching corners splits the
    boundary into simple directed dual closed curves.
  - **Classes.** Each such curve has class 0 or ±d on the cylinder, and their
    classes sum to the class of the boundary of the upper end. In the
    example d = (0, L), arcs pointing right into R rotate to arcs pointing
    up, so that class is +d.
  - **Conclusion.** Some curve has class exactly d. Its projection is a
    directed closed walk of D* of class d. ∎

## Theorem 2: the cone theorem

Apply Theorem 1 to D* on T*. Rotating the dual orientation once more gives
the reverse of D on T.
- **Membership in S(D).** D has a directed closed walk of class −d exactly
  when det(s*, d) ≥ 0 for every s* ∈ S(D*). Replacing d by −d: d ∈ S(D)
  exactly when det(d, s*) ≥ 0 for all s*.
- **The chain of inclusions.** For primitive d, write
  Prim(X) = the primitive periods in X. Then
  Prim(S(D)) ⊆ Prim(C) ⊆ Prim(°C*) = Prim(S(D)),
  where °C* = {y : det(y, c*) ≥ 0 for all c* ∈ C*} and C* = cone(S(D*)).
  - The first inclusion is trivial.
  - The second is the sign rule.
  - The equality is the previous point.
- **So all three agree.**
  - **The primal.** Every primitive period of C is realized.
  - **The dual.** The same argument with the roles exchanged gives
    Prim(S(D*)) = Prim(C°).
  - **The cones.** The cones are rational, so C* = C°.
- **The polar table.** Polarity reverses inclusion, and C°° = −C. ∎

## Theorem 3: twisted sectors

The double cover is a square-lattice torus with lattice ker p, so Theorems 1
and 2 apply to it.
- **The swap.** The swap is a translation, so it acts trivially on classes.
  It maps the twisted orientation to its reverse, hence S(D̃) = −S(D̃) and
  C = −C.
- **The types.** The only closed convex cones equal to their negatives are
  {0}, lines and the plane.
- **Recovering the exact duality.** Under polarity these map to the plane, the
  same line and {0}. That is the reduction proof's exact duality, with
  contractible ↔ cross and winding ↔ winding in the same class. ∎

## Theorem 4: laws

**The symmetries of the law.**
- **Polarity.** D ↦ D* is a bijection between orientations, and T* is a
  translate of T with the same periods. Uniform maps to uniform, and
  C(D*) = C(D)°, so the law of C equals the law of C°.
- **Lattice symmetries.** A symmetry g of T maps uniform orientations to
  uniform orientations, with C(gD) = g·C(D).

**On a square torus.**
- **The four equal probabilities.**
  - **Polarity.** The line V is its own polar. So C ⊆ V exactly when C° ⊇ V,
    which has the probability of C ⊇ V.
  - **Rotation.** Rotation by 90° exchanges V and H.
  - **Meaning of C ⊆ V.** A strongly connected digraph's cycle space is
    spanned by directed cycles. So C ⊆ V exactly when no strong component
    has a cycle with horizontal winding.
  - **Meaning of C ⊇ V.** By Theorem 2, C ⊇ V exactly when classes (0, 1)
    and (0, −1) are both realized.
- **Pure versus positive winding.** Let L⁻ be the closed left half-plane. Its
  polar is the ray through (0, −1).
  - **The identity.** "No walk winds positively" is C ⊆ L⁻, equivalently
    C° ∋ (0, −1). That has the probability that (0, −1) is realized, which by
    symmetry is P(pure (1, 0)).
  - **The bound.** A pure (1, 0) walk winds positively, so
    P(pure (1, 0)) ≤ 1/2.
- **The twisted identity.** With a twist, C is {0}, a line or the plane, and
  P({0}) = P(plane).
  - No horizontal winding is C ∈ {0, the vertical line}.
  - No vertical winding is C ∈ {0, the horizontal line}.
  - Adding the two and using P({0}) = P(plane) gives the stated sum. ∎

## Check

`check.py` (standard library) samples orientations of untwisted tori (3 × 3,
3 × 4, 4 × 4, sheared 3 × 3) and twisted ones (3 × 3 with twists (1, 0) and
(1, 1), 4 × 3, sheared 3 × 3). For every primitive period d with
|d| ≤ 2 of the relevant lattice it checks:
- **Theorem 1.** Exactly one of (i) and (ii) holds. (i) is computed by
  Bellman–Ford with arc weights det(arc, d). (ii) is computed by searching
  (dual vertex, period offset) states in a box of the dual's universal cover.
- **Theorem 2.** The realized primal classes are the primitive periods of
  their cone, and the realized dual classes are those of its polar.
- **Theorem 3.** Twisted cones are {0}, a line or the plane. Twisted class
  sets are symmetric: a class of size ≤ 2 found in a search box of
  radius 4 has its negative found in radius 6. The swapped walk's partial
  offsets shift by the class.
- **Theorem 4.**
  - Polar invariance of the law: the counts of {0} and plane cones, and of
    rays and half-planes, agree within sampling error.
  - On the 5 × 5 torus, the two square-torus identities by sampling.
- **Controls (must be rejected):**
  - the opposite sign convention breaks Theorem 1;
  - untwisted class sets are not always symmetric.

## The derivation attempt (interpretation, not theorem)

The cone theorem is the structure the duality identities give. Theorem 4
uses all of its symmetries, and they do not fix the values.
- **The untwisted square.** P(C ⊆ V) is tied to three other events of equal
  probability. Those events overlap in the cones {0}, the plane and the two
  axis lines, and they miss the diagonal cones.
- **The measured directed law.** On 64 × 64 tori, the probabilities of
  "positive only", "negative only", "both" and "neither" horizontal winding
  are 0.231, 0.231, 0.287 and 0.249 (a scoping measurement, not evidence).
  These are not the four equal quarters that would make 3/4 a symmetry
  consequence.
- **Conclusion of the attempt.** 3/4, and half a bit with a twist, would need
  information beyond duality and symmetry: the actual law of the random cone.
- **What the attempt gives instead.** Exact statements of what each candidate
  value means:
  - 3/4: the uniform random orientation has no directed closed walk winding
    horizontally with probability 1/4;
  - half a bit: the x-twisted orientation has none with probability 1/√2, up
    to the small diagonal-line term in Theorem 4.

## Scope

- Square-lattice tori and their double covers.
- Theorems 1–3 hold for every orientation. Theorem 4 holds for the uniform
  and twisted uniform measures.
- No space or physics is claimed.
