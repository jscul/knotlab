# The sign survives the twist

Status: Proved

Ticket `TWIST-3D-20261025-001B`, 2026-10-25.

**What it uses:**
- from `TWIST-3D-20261025-001A-P001`: ordered triangulations, ordered moves with their orientation signs, and the cocycle counts;
- from `HUB-DIMENSION-20261024-001B-P001`: in symmetric Turaev–Viro form, the Fibonacci rule needs a negative weight;
- from `SOFT-HUB-20261024-001A-P001`: the eight non-windable knots are R_c = N[c] ∪ {c̄}, and each contains exactly one parity class.

## Standard statement

**Setting.**
- **Weights.** A *Turaev–Viro weighting* for a triangle rule R on ordered triangulations assigns non-negative numbers:
  - d[x] to each edge label x;
  - t[y] to each triangle labelling y ∈ R, read as (x_ab, x_bc, x_ac);
  - W_s[z] to each R-compatible tetrahedron labelling z, separately for the two orientation signs s;
  - v to each vertex.
- **The state sum.** It multiplies, over a labelling, one d per edge, one t per triangle, one W per tetrahedron and v^V, and sums over
  labellings.
- **The identities.**
  - **2–3:** t(shared face) W(F_p) W(F_q) = Σ over x_pq of d[x_pq] · t · t · t · W · W · W.
  - **1–4:** W(F_r) = v · Σ over the four new edges of their d's, the six new triangles' t's and the four new tetrahedra's W's.
  - Both are taken over every boundary labelling with boundary triangles in R and both global orientations. They make the state sum
    invariant under the ordered moves.
- **Support.** The *support* of a weighting is the set of its positive weights. *Full support* means every weight is positive.

**Theorem 1 (no positive full support).** For the triangle rule of each of the eight non-windable knots (the two no-lone knots and the
six twisted Fibonacci knots), some identity has monomials on one side only, between 60 and 162 identities depending on the knot. So no
weighting with full support satisfies the identities.

**Theorem 2 (positive supports).** The support of every positive weighting satisfying the identities has its tetrahedron part in one of
these families:
- constant labellings, one or both;
- the whole parity class of R, in both orientations, with the d and t weights of that class;
- for the two no-lone knots only, that parity class together with the one constant labelling outside it.

For each twisted knot exactly 34 supports are consistent, and for each no-lone knot 75.

**Theorem 3 (the parity class is a gauge orbit).**
- **The system.** Restricted to the parity class, each 2–3 identity has exactly one monomial on each side. In logarithms these
  identities form a homogeneous linear system in 22 unknowns, and its solution space has dimension 7.
- **The gauges.** The span of the following directions also has dimension 7, and each of them is a solution:
  - for each triangle labelling y of the class, the antisymmetric face gauge (W_s[z] times α^(s(−1)^i) for each face i of type y);
  - for each such y, the symmetric gauge (t[y] times β, and W times β^(−1/2) per face of type y);
  - the global direction (W times a, d divided by a, v times a).
- **The consequence.** Every positive weighting supported on the parity class is a gauge transform of the constant weighting
  d = t = W = 1, v = 1/2. Its state sum is |Z¹|/2^V = |H¹(M; Z/2)|/2.

**Corollary 4 (what positive weights see).** Every positive state sum on ordered triangulations whose triangle rule is a non-windable
knot is one of:
- 1 or 2 (constant sectors);
- |H¹(M; Z/2)|/2 (the parity class);
- |H¹(M; Z/2)|/2 + 1 (parity class and a constant, no-lone knots only).

In every case it is a function of the mod-2 first cohomology.

**Reading.**
- **The sign survives the twist.** In the Fibonacci basis the twist is a signed reflection. But positive weights cannot exploit it:
  with or without the twist, the Fibonacci support forces a cancellation that only a negative weight can provide.
- **Without signs, what is left is parity.** A positive weighting can only be supported where no cancellation is needed, on the parity
  class or on constants. There the weights are pure gauge, and the state sum counts cocycles.

## Nearest known result

- **The phenomenon is classical in spirit.**
  - Fibonacci state sums need signs (`HUB-DIMENSION-20261024-001B`; the Fibonacci string net's sign problem).
  - Positive real 3-cocycles on Z/2 are coboundaries, since the real cohomology of a finite group vanishes.
- **The local content** is:
  - the one-sided identities for the twisted supports;
  - the exhaustive classification of positive supports for the eight knots;
  - the exact gauge computation on the parity class, in the Turaev–Viro form with edge, triangle, tetrahedron and vertex weights.
- **Novelty:** `candidate-local-delta`; folklore risk medium.

## Proof

### Theorem 1

- **One-sided identities.** The check lists, for each knot, the identities with monomials on exactly one side.
- **The contradiction.** Under full support every monomial is positive, so such an identity would equate a positive sum with zero.
  ∎

### Theorem 2

- **The necessary condition.** With positive weights on a support, a side of an identity is positive exactly when some monomial lies
  entirely in the support. So in every identity, one side has such a monomial exactly when the other does.
- **The search.** The check enumerates all supports with v and some tetrahedron weight positive, by an exhaustive search that discards
  a partial support as soon as some decided identity has one side positive and the other zero.
- **The result.** Each consistent support has its tetrahedron part in the stated families, and every parity-family support contains
  the whole class with its d and t weights. ∎

### Theorem 3

- **One monomial per side.** In a 2–3 move inside the parity class, the new edge's label is determined by the parity of the three new
  triangles. So the right side has one term. The left side is a single product.
- **The linear algebra.** The check builds the logarithmic system and computes, over the rationals, its rank and the rank of the gauge
  directions; it also verifies that each gauge direction solves the system. The two solution spaces then coincide.
- **Gauges leave everything that matters unchanged.**
  - **Antisymmetric face gauges.** In a closed manifold every triangle lies in two tetrahedra with opposite induced signs, so these
    gauges cancel in the state sum. In a 1–4 identity the interior faces cancel and the boundary faces scale both sides equally.
  - **Symmetric gauges.** A triangle's factor β is cancelled by β^(−1/2) from each of its two tetrahedra, in the state sum and in both
    move identities.
  - **The global direction** changes d, W and v together. Since E = V + T, the state sum is unchanged, and so are the identities.
- **The constant point.** A positive weighting supported on the parity class therefore equals a gauge transform of the constant one.
  - Undoing the gauge keeps the 1–4 identity, which at the constant point reads 1 = v · 2, because the four new edges admit exactly two
    parity-respecting labellings.
  - So v = 1/2, and the state sum is (1/2)^V |Z¹| = |H¹(M; Z/2)|/2, by the cocycle count of ticket A. ∎

### Corollary 4

- **Sectors do not mix.** A constant tetrahedron outside the parity class has faces of the other parity, so it cannot share a face
  with a tetrahedron in the class. On a connected triangulation the state sum is therefore the sum of its sector contributions.
- **A constant sector contributes 1.** Its identities read d t² W₊ = 1 and d t² W₋ = 1, from the two orientations of one 2–3 move, and
  then v d = 1, from a 1–4 move. With E = V + T and F = 2T, the sector's weight is (v d)^V (d t² W)^T = 1.
- **The parity sector** contributes |H¹|/2 by Theorem 3. ∎

## Checks

`check.py` uses the standard library only and runs in a few seconds. It loads ticket A's check for the ordered machinery, and
confirms, for each of the eight knots:
- **Theorem 1:** the number of one-sided identities (60 for the no-lone knots, 160 or 162 for the twisted ones);
- **Theorem 2:** the exhaustive support enumeration (34 or 75 consistent supports), none outside the families, with parity supports
  covering the whole class;
- **Theorem 3:**
  - the logarithmic 2–3 system on the parity class has one monomial per side, 22 unknowns and solution dimension 7;
  - the gauge directions solve it and have rank 7.

**Controls.**
- **The one-sided test can come out negative.** The odd parity knot has no one-sided identity under full support.
- **The system is not trivial.** Changing one tetrahedron weight alone violates the 2–3 system.
- **The constant point is right.** The constant weighting evaluates to |H¹(M; Z/2)|/2 on 24 sampled ordered triangulations.

## What this does not show

- **Real weights with signs.** These include twisted Dijkgraaf–Witten weights and the Fibonacci Turaev–Viro weights; they exist but
  are not counts.
- **Other triangle rules.** Only the eight non-windable knots are treated, although ticket A's census covers all rules for unweighted
  counts.
- **Richer local structures.** Several bits per edge, labels on faces, or larger groups are not covered.
