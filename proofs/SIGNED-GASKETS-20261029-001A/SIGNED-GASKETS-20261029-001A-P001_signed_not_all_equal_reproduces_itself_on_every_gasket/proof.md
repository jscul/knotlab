# Signed not-all-equal reproduces itself on every level-k Sierpinski gasket

Status: Proved

Ticket `SIGNED-GASKETS-20261029-001A`, 2026-10-29.

## Standard statement

**Setting.**
- **The gasket.** SG_k is a triangle cut into k² small triangles, keeping the k(k+1)/2 up triangles.
  - Its vertices are (i, j) with i, j ≥ 0 and i + j ≤ k.
  - Its triangles are T(i, j) = ((i, j), (i+1, j), (i, j+1)) for i + j ≤ k − 1. The three positions are the *a*-, *b*- and *c*-corner.
  - Its corners are A = (0, 0), B = (k, 0) and C = (0, k).
- **Copies of a law.** A law w assigns a weight to each of the eight tuples, and every triangle carries a copy, glued at shared
  vertices. The *corner relation* R_k(x_A, x_B, x_C) sums, over all values of the other vertices, the product of the weights.
- **Exact.** A law is *exact* on SG_k when R_k = λ_k w with λ_k ≠ 0. Substituting SG_k for every copy, level after level, then
  gives a tower whose corner relation is w (up to a factor) at every level. The tower is a finitely ramified self-similar space of
  similarity dimension log(k(k+1)/2)/log k.
- **The law.** *Signed not-all-equal* is w(a, b, c) = (−1)^((a⊕b)(a⊕c)) − [a = b = c]. Its support is not-all-equal, and it is −1
  exactly when the a-corner is the odd one out.

**Results.**
- **Lemma 1 (closed forms).**
  - w(a, b, c) = (−1)^a · ((a + b + c) | 3), with the Legendre symbol modulo 3.
  - w = (−1)^a sin(πE/3)/sin(π/3), where E = (−1)^a + (−1)^b + (−1)^c.
  - Equivalently w = (−1)^a (ω^E − ω^(−E))/(ω − ω^(−1)) with ω = e^(iπ/3): a standing wave of two opposite phases.
  - 4w = 1 + s_a s_b + s_a s_c − 3 s_b s_c in spins s = (−1)^x.
  - **The Eisenstein field.** w is the multiplication of Q(ω) in the basis e₀ = ω, e₁ = ω̄, with the a-corner as output:
    e_b · e_c = Σ_a w(a, b, c) e_a.
  - **Row matrices.** The matrices M_c = w(·, ·, c) satisfy M₀M₁ = I = M₀ + M₁ and M₀³ = −I. So summing a free row of the gasket
    multiplies the field elements of the row above.
- **Theorem 2 (every level).** For every k ≥ 1, R_k = λ_k w.
  - **The family.** More generally, for every θ with sin θ ≠ 0, the law w_θ = (−1)^a sin(θE)/sin θ has R_k = λ_k(θ) w_θ.
  - λ_k(θ) is a Laurent polynomial in e^(iθ).
  - w_{π/3} = w, and signed not-all-equal is the only member of the family whose support is a knot. Every other member is
    nonzero on all eight tuples.
- **Theorem 3 (the factor is never zero).** λ_k is an integer with λ_k ≡ (−1)^⌊k/2⌋ (mod 3). Indeed R_k ≡ (−1)^(N_k) w (mod 3),
  with N_k = (k−1)(k+4)/2 the number of summed vertices.
  - **Consequence.** λ_k ≠ 0 for every k, and λ_k(θ) ≠ 0 for all but finitely many θ modulo 2π.
- **Corollary 4 (towers of every level).** Signed not-all-equal is exact on SG_k for every k.
  - It therefore builds an exact tower of every level k. The towers have dimensions log 3/log 2 ≈ 1.585, log 6/log 3 ≈ 1.631,
    log 10/log 4 ≈ 1.661, …, tending to 2.
  - The corner relation's support, not-all-equal, is a knot under K1–K3: knotlab reports binding, invisible in its parts, lost on
    erasure, minimum width 3.

## Nearest known result

- **In the repository.**
  - `INTERFERENCE-20261029-001B`: signed not-all-equal laws exact on the native triangle (k = 2, with placements chosen per copy),
    and Theorem 1 there, by which an exact signed fixed point keeps its law at every level of its tower.
  - `EXACT-TOWERS-20261029-001B`: towers from exact gadgets, with counts.
  - `SHARED-SUBDIVISION-20261029-001` and `SIGNED-SUBDIVISION-20261029-001`: under shared subdivision of the plane, no non-affine
    knot reproduces itself, whether with counts, with signs or with real weights.
- **Outside.**
  - **Level-k gaskets.** These are classical (Hilfer and Blumen 1984), with dimension ln(k(k+1)/2)/ln k.
  - **Exact decimation.** Exact decimation on finitely ramified fractals is classical: decimating a three-corner weight on a gasket
    always gives a three-corner weight again. Its fixed points are studied for Ising and Potts weights, mostly at k = 2.
  - **Arithmetic.** The Legendre symbol modulo 3 and the Eisenstein integers are classical. So is the complex rank 2 (negative
    hyperdeterminant) of not-all-equal-type tensors.
  - A bounded search on 2026-10-29 found no law that is a fixed point of every level at once, and none with this arithmetic form.
- **Classification.**
  - Lemma 1 is elementary.
  - Theorems 2 and 3: no overlap found (candidate local delta).
  - Corollary 4 follows from them and from `INTERFERENCE-20261029-001B`.

## Proof of Lemma 1

- **Tuple by tuple.** Write t = a + b + c. If t is 0 or 3 the tuple is constant, and w = 0 = (t | 3).
  - If t = 1, the odd corner holds the 1. It is a exactly when a = 1, so w = (−1)^a = (−1)^a (1 | 3).
  - If t = 2, the odd corner holds the 0. It is a exactly when a = 0, so w = −(−1)^a = (−1)^a (2 | 3).
- **The sine form.** E = 3 − 2t, and sin(πE/3)/sin(π/3) equals 0, 1, −1, 0 for t = 0, 1, 2, 3. This is (t | 3).
- **The phases.** The phase form is the sine form rewritten, and the spin form is checked on the eight tuples.
- **The field.** In Q(ω) with ω² = ω − 1: ω·ω = −ω̄, ω·ω̄ = 1 = ω + ω̄, ω̄·ω̄ = −ω. These are the columns (w(0, b, c), w(1, b, c)).
- **The row matrices.** M₀ = [[0, 1], [−1, 1]] and M₁ = [[1, −1], [1, 0]] = I − M₀, and M₀ has trace 1 and determinant 1.
- **Free rows.** Along a row of the gasket, an interior vertex is the b-corner of one triangle and the a-corner of the next. So
  summing it composes the two products, and summing a whole free row with fixed ends gives M^(#0 − #1) of the row above. ∎

## Proof of Theorem 2

- **Sectors.** Let ζ = e^(iθ) and D = ζ − ζ^(−1). Then w_θ(a, b, c) = (1/D) Σ_{s = ±1} s (−1)^a ζ^(s((−1)^a + (−1)^b + (−1)^c)).
  - Choose a sector s_T for every triangle and expand R_k as a sum over the choices. Each vertex v collects ζ^(s_T (−1)^(x_v)) from
    every triangle T containing it, and (−1)^(x_v) from the one triangle whose a-corner it is, if any.
  - Let S_v be the sum of the sectors of the triangles at v. Summing a non-corner vertex gives 2i sin(θ S_v) if v is an a-corner,
    and 2 cos(θ S_v) if not.
- **The vertices of SG_k.**
  - Every vertex with i + j ≤ k − 1 is the a-corner of exactly one triangle, T(i, j), and no other vertex is an a-corner.
  - An interior vertex of the bottom row, (i, 0) with 0 < i < k, is the a-corner of T(i, 0) and the b-corner of T(i−1, 0), so
    S ∈ {0, ±2}. Its factor 2i sin(θS) vanishes unless the two sectors agree.
  - The same holds on the left side, between T(0, j) and T(0, j−1).
  - So all triangles of the bottom row and of the left side share one sector s₀. These include the triangles at A, B and C.
- **The corners.** The corners are not summed. Their factors are (−1)^(x_A) ζ^(s₀E), with E = (−1)^(x_A) + (−1)^(x_B) + (−1)^(x_C).
  Hence R_k = (−1)^(x_A) Σ_{s₀} Z(s₀) ζ^(s₀E), where Z(s₀) collects every other factor.
- **The flip is odd.** Changing every sector's sign multiplies Π_T s_T by (−1)^(#T). It multiplies each summed a-corner factor
  (a sine) by −1, and there are #T − 1 of them: every a-corner but A. Each cosine factor is unchanged. So Z(−s₀) = (−1)^(2#T−1)
  Z(s₀) = −Z(s₀).
- **Conclusion.** R_k = Z(1) (−1)^(x_A) (ζ^E − ζ^(−E)) = D Z(1) w_θ, so λ_k(θ) = D Z(1), a Laurent polynomial in ζ.
  - If sin 2θ = 0, every term vanishes for k ≥ 2 and λ_k(θ) = 0.
  - The support of w_θ omits a tuple only when sin 3θ = 0. With sin θ ≠ 0 this means θ ≡ ±π/3 (mod π), where w_θ = w.
  - Everywhere else w_θ allows all eight tuples and is unconstrained, so it is not a knot (K1 fails). ∎
- **The factor at θ = π/3, explicitly.**
  - Here D = i√3, the interior factor is ±D (NAE of the three sectors) or 0, the hypotenuse factor is 2 or −1, and the powers of D
    cancel. So λ_k is the sum over sectors d on the triangle positions, with d = 0 on the bottom row and the left side, of
    Π_v w(d(i, j), d(i−1, j), d(i, j−1)) × Π_{i=1}^{k−1} h(d(i−1, k−i), d(i, k−i−1)).
  - The first product runs over the interior vertices v = (i, j) with i, j ≥ 1. The hypotenuse factor is h = 2 if the two sectors
    differ and −1 if they agree.
  - The sectors therefore carry signed not-all-equal again, on a dual gasket. This formula is checked against the direct values
    for k ≤ 7.

## Proof of Theorem 3

- **Reduction.** Since 4 ≡ 1 (mod 3), w ≡ 1 + s_a s_b + s_a s_c. Expanding Π_T (1 + s_a s_b + s_a s_c) picks, for every triangle,
  nothing, its edge ab (horizontal, from the a-corner (i, j)) or its edge ac (vertical, from (i, j)).
  - The result is a sum over edge sets E using at most one of the right and up edges at each (i, j).
  - Summing each non-corner spin keeps only the E with even degree there, with a factor 2 each. So
    R_k ≡ 2^(N_k) Σ_E s_A^(d_A) s_B^(d_B) s_C^(d_C) (mod 3).
- **Lemma 5.** The only such E are the empty set, the bottom row (from A to B) and the left side (from A to C).
  - *No even part.* Take a nonempty set of edges with even degree everywhere. Its vertex with the least i + j (then the least i) has
    no edge to the left or downwards, since those neighbours have smaller i + j. So its two or more edges are its right edge and its
    up edge, which is forbidden.
  - *A single path.* Odd degrees occur only at corners, each of degree at most one. (A has at most one of its right and up edges; B
    only its left edge; C only its down edge.) So E is empty or a single path between two corners.
  - *No interior minimum.* No inner vertex of the path is a local minimum of i + j, since it would use its right and its up edge.
  - *From B.* The path leaves B (where i + j = k) to the left, so it keeps decreasing. Every step goes left or down, which forces
    the bottom row to A, and the path never reaches C. The path from C is the left side, by the same argument. ∎
- **Conclusion.** R_k ≡ 2^(N_k) (1 + s_A s_B + s_A s_C) ≡ (−1)^(N_k) w (mod 3).
  - Comparing with R_k = λ_k w (Theorem 2) gives λ_k ≡ (−1)^(N_k) (mod 3).
  - N_k = (k−1)(k+4)/2 has the parity of ⌊k/2⌋.
  - λ_k is an integer because R_k is an integer sum.
  - Finally, λ_k(θ) is a Laurent polynomial in ζ that is nonzero at ζ = e^(iπ/3), so it has only finitely many zeros on the unit
    circle. ∎

## Corollary 4 and the knot check

- **Towers.** By `INTERFERENCE-20261029-001B` (Theorem 1), an exact signed fixed point keeps its law at every level of its tower.
  So the level-m tower of SG_k has corner relation λ_k^(1 + n + … + n^(m−1)) w, with n = k(k+1)/2.
- **The space.** Sub-gaskets meet only at corner points, so the tower is finitely ramified. Its similarity dimension is
  log n / log k.
- **The knot.** The knot check runs `knotlab check` on not-all-equal (loops a, b; contact c) and finds a knot.

## What the computation checks

- **Exactness.** R_k = λ_k w exactly (integers, Chinese remainder theorem) for k = 1 to 14.
  λ_k = 1, −1, −4, 13, 85, −634, −7492, 115321, 2573863, −78217747, −3343529104, 197140264285, 16183882770340, −1838549462850652.
- **Modulo 3.** R_k ≡ (−1)^(N_k) w for k = 1 to 21.
- **The sector formula.** For k ≤ 7.
- **The family w_θ.** At six angles for k ≤ 7 (floating point, relative error below 1e-15), and symbolically for k = 2 and 3.
- **Lemma 5.** By enumeration for k ≤ 4.
- **Lemma 1.** On all eight tuples.
- **Controls.**
  - Unsigned not-all-equal is not exact on SG_2.
  - Flipping the sign of one tuple breaks exactness on SG_3.
  - Dropping (−1)^a from w_θ breaks exactness on SG_2.

## Reading

- **A knot builds space of every dimension below 2.**
  - Signed not-all-equal is the frustrated triangle law with a sign. It reproduces itself exactly on every level-k gasket, so it
    builds a finitely ramified self-similar space of dimension log(k(k+1)/2)/log k for every k.
  - The plane stays out of reach. For laws on up triangles, the subdivided plane is these gaskets plus the up triangles that join
    neighbouring ones, and `SIGNED-SUBDIVISION-20261029-001B` rules out not-all-equal shapes there for every real weighting.
- **Why it works: harmonies.**
  - The law is a standing wave of two opposite phases, ω^E and ω^(−E). On the gasket each phase travels as a product.
  - The gasket's edges lock the phases at the three corners together, and flipping every phase is odd. So the two phases always
    recombine into the same standing wave.
  - The knot is the point θ = π/3 of the family, where the all-equal tuples cancel exactly.
- **The mechanism is not about knots.** The whole family w_θ reproduces itself on every gasket. The knot is the single member whose
  allowed states are constrained.

## Nonclaims

- Only the level-k gaskets and their towers are covered: finitely ramified spaces, built level by level from finite gadgets.
- No statement about the plane beyond the cited exclusion, and no infinite-volume or source-aware claim.
- No physical interpretation.
