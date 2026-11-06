# The standing wave reproduces itself on every Sierpinski simplex

Status: Proved

Ticket `SIMPLEX-GASKETS-20261029-001A`, 2026-10-29.

## Standard statement

**Setting.**
- **The Sierpinski simplex.** SG^d_k is a d-simplex cut into k^d small simplices, keeping the up simplices.
  - Its vertices are the points v ∈ Z^d with v ≥ 0 and |v| = v₁ + … + v_d ≤ k.
  - Its up simplices are T(v) = (v, v+e₁, …, v+e_d) for |v| ≤ k − 1. There are #T = C(k+d−1, d) of them.
  - Role 0 of T(v) is its *base corner* v; role i is v + e_i.
  - Its corners are A = 0 and B_i = k e_i. The other N = C(k+d, d) − d − 1 vertices are *summed*.
  - For d = 2 this is the level-k gasket of `SIGNED-GASKETS-20261029-001`.
- **Copies of a law.** A law w assigns a number to each (d+1)-bit tuple. Every up simplex carries a copy, glued at shared vertices.
  - The *corner relation* R(x_A, x_B₁, …, x_B_d) sums the product of the copies over all values of the summed vertices.
  - A law is *exact* on SG^d_k when R = λ w with λ ≠ 0.
- **Notation.** Write s = (−1)^x for a bit x, and E(x) = s₀ + s₁ + … + s_d. Then E = d + 1 − 2|x|, where |x| is the number of ones.
- **The standing wave.** For y ∈ C, w^(y)(x) = s₀ U_(E−1)(y/2). Here U_n is the Chebyshev polynomial of the second kind, extended by
  U₋₁ = 0 and U₋ₙ₋₂ = −U_n.
  - For y = 2 cos θ with sin θ ≠ 0 this is w_θ(x) = (−1)^(x₀) sin(θE)/sin θ.
  - Its *limit law* is τ = w^(2) = s₀E = 1 + Σᵢ s₀sᵢ, the case θ → 0.
  - Its *Legendre law* is L_d(x) = (−1)^(x₀) (E | 3), with the Legendre symbol modulo 3.

**Results.**
- **Lemma 1 (closed forms).**
  - U_(E−1)(y/2) is an integer polynomial in y. For even E it is divisible by y.
  - **Two sectors.** With y = ζ + ζ⁻¹ and D = ζ − ζ⁻¹ ≠ 0, w^(y) = (1/D) Σ_(σ=±1) σ s₀ ζ^(σE).
  - w^(−y) = (−1)^d w^(y), and w^(−2) = (−1)^d τ.
  - L_d = (−1)^d w^(1), the case θ = π/3, and L_d ≡ τ (mod 3).
  - For d = 1, w^(y) = y [x₀ = x₁].
- **Theorem 2 (every dimension, every level).** For every d ≥ 1, k ≥ 1 and every complex y, the corner relation of w^(y) on SG^d_k is
  λ_(d,k)(y) w^(y), with λ_(d,k) a polynomial with integer coefficients.
- **Theorem 3 (the factor).**
  - λ_(d,k) is monic of degree d(#T − 1), and λ(−y) = (−1)^(d(#T−1)) λ(y).
  - λ(2) = 2^N and λ(−2) = (−1)^(d(#T−1)) 2^N.
  - At level 2 it is λ_(d,2) = y^d (y² − 2)^(d(d−1)/2).
  - For k ≥ 2, y = 0 (θ = π/2) is always a root.
- **Lemma 4 (edge sets).** Expand each copy of τ as 1 plus one edge (v, v + e_i). The only edge sets with even degree at every summed
  vertex are the empty set and the d axis paths from A to B_i. Hence the corner relation of τ is exactly 2^N τ.
- **Corollary 5 (nonvanishing).**
  - For each d and k, the exceptional angles (λ(2 cos θ) = 0) are finitely many, and at each of them 2 cos θ is an algebraic
    integer.
  - λ(2 cos θ) ≠ 0 at every θ = jπ/q with q a power of an odd prime and gcd(j, q) = 1.
  - **The Legendre law.** Its factor is (−1)^(d(#T−1)) λ(1) ≡ (−1)^N (mod 3), never zero. So L_d is exact on every SG^d_k.
- **Proposition 6 (knots).** Let d ≥ 2 and sin 2θ ≠ 0. The support of w_θ is a knot under K1–K3 exactly when it excludes some
  weight. That happens for every θ when d is odd. When d is even it happens exactly at θ = jπ/q in lowest terms with q odd and
  q ≤ d + 1.
- **Corollary 7 (exact knots and towers in every dimension).**
  - For every d ≥ 2 the Legendre law is an exact knot on SG^d_k for every k. For odd d, every w_θ outside the finitely many
    exceptional angles of each level is one.
  - Each exact law builds an exact tower of every level. These are finitely ramified self-similar spaces of similarity dimension
    log C(k+d−1, d)/log k. That dimension increases with k, lies in [d − log(d!)/log k, d), and tends to d.
- **Remark 8 (dimensions 2 and 3).** Here the waves exhaust the laws (−1)^(x₀) g(E) with g odd.
  - Every such law is a multiple of w^(y) (d = 2), or of the reduced wave w^(y)/y (d = 3), for some complex y. Otherwise it is the
    equality law.
  - y may have |y| > 2 (hyperbolic) or be imaginary. So all of them reproduce themselves wherever the factor (λ, resp. λ/y^(#T−1)) is
    nonzero.
  - From d = 4 on this fails: a sum of two waves is not exact.

| d | Knot supports of the wave | Legendre factor, levels 2, 3, … |
| --- | --- | --- |
| 2 | not-all-equal (θ = π/3 only) | −1, −4, 13, 85, −634, −7492 |
| 3 | not exactly two ones (every θ); odd parity (θ = π/4, not exact at levels 2 and 4) | 1, −128, −187, 124990 |
| 4 | five-place not-all-equal (θ = π/5 with weights 1, φ; 2π/5 with 1, −1/φ); not one or four ones (π/3) | 1, 65536 |
| 5 | not exactly three ones (every θ); not zero, three or six ones (π/3); … | −1 |
| 6 | seven-place not-all-equal (π/7); not one or six ones (π/5); not two or five ones (π/3) | −1 |

## Nearest known result

- **In the repository.**
  - `SIGNED-GASKETS-20261029-001A` is the case d = 2. Its factor was described as a Laurent polynomial in e^(iθ). Theorem 3 sharpens
    this to a monic integer polynomial in 2 cos θ with value 2^N at θ = 0, which gives nonvanishing at every odd prime-power angle.
  - `INTERFERENCE-20261029-001B` treats towers from exact signed gadgets.
  - `HUB-DIMENSION-20261024-001` is the contrast. There, unsigned bit laws on the edges of triangulated three-manifolds, invariant
    under Pachner moves, see only parity.
- **Outside.**
  - Generalized Sierpinski gaskets in d dimensions with base b are Hilfer and Blumen's (1984), with dimension ln C(b+d−1, d)/ln b.
  - Exact decimation on finitely ramified fractals is classical: Ising, Potts and Gaussian models on gaskets, and spectral decimation.
    It is mostly done at b = 2, with positive weights.
  - Chebyshev polynomials, and the ramification of p in Q(ζ_(p^m)), are classical.
  - The two-sector form makes each copy a rank-2 (GHZ-type) tensor, a standard object for tensor networks.
  - A bounded search on 2026-10-29 used four queries: generalized gasket decimation fixed points, complex or signed weights, every-b
    exact solvability, and GHZ tensor networks on fractals. It found no law exact at every level in every dimension, and no factor
    of this arithmetic form.
- **Classification.**
  - Lemma 1, Lemma 4 and Proposition 6 are elementary.
  - Theorems 2 and 3 and Corollary 5: no overlap found (candidate local delta).
  - The geometry in Corollary 7 is classical.

## Proof of Lemma 1

- **Chebyshev.** U₀ = 1, U₁(y/2) = y and U_(n+1)(y/2) = y U_n(y/2) − U_(n−1)(y/2), so every U_n(y/2) lies in Z[y].
  - For y = 2 cos θ, U_(n)(y/2) = sin((n+1)θ)/sin θ. The extension to negative n matches sin(−φ) = −sin φ.
  - For even E = 2m, sin(2mθ)/sin θ = 2 cos θ · sin(m·2θ)/sin 2θ = y U_(m−1)(cos 2θ), and 2 cos 2θ = y² − 2. So y divides it in
    Z[y].
- **Two sectors.** sin(θE)/sin θ = (ζ^E − ζ^(−E))/(ζ − ζ⁻¹), multiplied by s₀.
- **Signs.** U_n(−t) = (−1)^n U_n(t), and E − 1 ≡ d (mod 2), so w^(−y) = (−1)^d w^(y).
- **The limit law.** U_(E−1)(1) = E, so w^(2) = s₀E = 1 + Σᵢ s₀sᵢ.
- **The Legendre law.**
  - sin(πE/3)/sin(π/3) runs 0, 1, 1, 0, −1, −1 for E ≡ 0, …, 5 (mod 6), while (E | 3) runs 0, 1, −1, 0, 1, −1. They agree for odd
    E and are opposite for even E, and E ≡ d + 1 (mod 2). So w^(1) = (−1)^d L_d.
  - (E | 3) ≡ E (mod 3), so L_d ≡ s₀E = τ.
- **d = 1.** E ∈ {2, 0, −2} and U₁(y/2) = y. ∎

## Proof of Theorem 2

- **Vertex degrees.** A vertex u lies in T(u) as base corner when |u| ≤ k − 1, and in T(u − e_i) as role i when u_i ≥ 1.
  - The corners have degree 1. A is the base corner of T(0) only. B_i is role i of T((k−1)e_i) only, and is no base corner, since
    |B_i| = k.
  - The *axis vertices* j e_i (1 ≤ j ≤ k − 1) lie in exactly T(j e_i), as base corner, and T((j−1)e_i), as role i.
- **Sectors.** Take y = 2 cos θ with sin θ ≠ 0, ζ = e^(iθ) and D = ζ − ζ⁻¹. Expand every copy by Lemma 1, choosing a sector σ_T = ±1
  for each simplex.
  - Vertex u collects ζ^(S_u s_u), with S_u the sum of the sectors at u. It also collects s_u if it is a base corner, which happens
    in exactly one simplex.
  - Summing a summed vertex gives f_u(S_u), with f_u(S) = ζ^S − ζ^(−S) at a base corner and ζ^S + ζ^(−S) elsewhere.
  - So R = D^(−#T) Σ_σ (Π_T σ_T) Π_(u summed) f_u(S_u) · (corner factors).
- **The axes lock the corners.** At an axis vertex, f = ζ^S − ζ^(−S) vanishes unless its two simplices share a sector.
  - So in every surviving term all of T(0), T(e_i), …, T((k−1)e_i) carry one sector σ₀, for every i. These include the simplices of
    all d + 1 corners.
  - The corners therefore contribute s_A ζ^(σ₀(s_A + Σᵢ s_(B_i))) = s_A ζ^(σ₀ E_c), where E_c is E of the corner tuple.
  - Hence R = D^(−#T) s_A Σ_(σ₀ = ±1) ζ^(σ₀E_c) Z(σ₀), where Z(σ₀) sums over the sectors with σ_(T(0)) = σ₀. Terms with unlocked axes
    are zero, so including them changes nothing.
- **The flip is odd.** Reversing every sector multiplies Π σ_T by (−1)^(#T).
  - It changes the sign of every base-corner factor and of no other. There are #T − 1 summed base corners: every base corner except
    A.
  - So Z(−1) = (−1)^(2#T − 1) Z(1) = −Z(1).
  - Hence R = D^(−#T) s_A Z(1)(ζ^(E_c) − ζ^(−E_c)) = D^(1−#T) Z(1) w^(y)(corners).
- **The factor is an integer polynomial.**
  - *d even.* Some tuple t₀ has E = 1, where w^(y)(t₀) = ±1. So λ = ±R(t₀), a polynomial in the table entries, which lie in Z[y].
  - *d odd.* Every E is even, so w^(y) = y w̃ with w̃ integer-polynomial valued and w̃(t₀) = ±1 at a tuple with E = 2. Then
    R = y^(#T) R̃ and λ = ±y^(#T−1) R̃(t₀). At y = 0 the law vanishes, so the identity is trivial there.
  - Call this polynomial λ_(d,k). The identity R(t) = λ_(d,k)(y) w^(y)(t) holds for infinitely many y, namely every 2 cos θ, and
    both sides are polynomials. So it holds for every complex y.
  - For k = 1, R = w and λ = 1. ∎

## Proof of Theorem 3

- **Degree and leading coefficient.**
  - **One configuration reaches the top degree.** In Z(1), the term of a sector choice σ has top ζ-degree at most Σ_u |S_u| ≤
    Σ_(u summed) deg u = (d+1)(#T − 1).
  - Equality needs every summed vertex to see a single sector. Every T(v) with v ≠ 0 meets T(v − e_i) at its base corner v, which is
    summed. So the simplices are connected through summed vertices, and equality forces σ ≡ σ_(T(0)) = +1.
  - In that configuration every factor has top coefficient +1. So Z(1) has leading term ζ^((d+1)(#T−1)).
  - **Transfer to λ.** λ D^(#T−1) = Z(1) holds as Laurent polynomials in ζ, since it holds on the unit circle. Leading terms
    multiply, so λ has leading term ζ^(d(#T−1)).
  - A polynomial of degree m in y = ζ + ζ⁻¹ with leading coefficient a has leading term a ζ^m. So λ is monic of degree d(#T − 1).
- **Parity.** By Lemma 1, R^(−y) = (−1)^(d#T) R^(y) and w^(−y) = (−1)^d w^(y). So λ(−y) = (−1)^(d(#T−1)) λ(y).
- **Value at 2.** w^(2) = τ, and Lemma 4 gives R_τ = 2^N τ, so λ(2) = 2^N. Parity gives λ(−2).
- **Level 2.**
  - Every simplex of SG^d_2 lies on an axis, so all sectors equal σ₀.
  - The summed vertices are the e_i, each a base corner shared by two simplices, with factor ζ² − ζ⁻² = Dy. They are also the
    e_i + e_j with i < j, each in T(e_i) and T(e_j) and not a base corner, with factor ζ² + ζ⁻² = y² − 2.
  - So λ = D^(−d) (Dy)^d (y² − 2)^(d(d−1)/2).
- **The root y = 0.** For k ≥ 2 there is an axis vertex, and its factor ζ² − ζ⁻² vanishes at ζ = i. ∎

## Proof of Lemma 4

- **The expansion.** Π_T τ = Π_(T(v)) (1 + Σᵢ s_v s_(v+e_i)) expands into edge sets F that use at most one edge (v, v + e_i) per
  base corner v.
  - Summing a summed spin keeps F only if that vertex has even degree, with a factor 2.
  - So R_τ = 2^N Σ_F Π_corners s_c^(deg_F c), over the F with even degree at every summed vertex.
- **Up-edges.** Every edge of F goes from v to v + e_i, and is the *up-edge* of its lower end. Each vertex has at most one, and B_i,
  with |B_i| = k, has none.
- **Every component contains A.** Let C be a component of F with at least one edge, and u a vertex of C with |u| least.
  - Every edge of C at u goes up, so u has degree 1. It is therefore a corner with an up-edge, which makes it A.
  - So F has at most one component with edges.
- **That component is a tree.** Each edge of C is the up-edge of exactly one vertex of C, and a vertex of C with |u| greatest has
  none. So C has at most |V(C)| − 1 edges, being connected, exactly |V(C)| − 1, and exactly one vertex t of C has no up-edge.
- **It is a path from A.** A vertex of C other than A and t has an up-edge. Being summed (B_i has no up-edge), it has even degree,
  so it also has a down-edge and degree at least 2.
  - So the leaves of the tree C are exactly A and t. C is a path, and t has degree 1, so t is a corner: t = B_i.
  - Walking from A, each inner vertex is entered by its down-edge and left by its up-edge, so |·| rises by 1 at every step.
  - The k steps add up to k e_i, so every step is e_i: C is the i-th axis path.
- **Conclusion.** The empty set and the d axis paths are valid. So R_τ = 2^N (1 + Σᵢ s_A s_(B_i)) = 2^N τ(corners). ∎

## Proof of Corollary 5

- **Finitely many exceptional angles.** λ is a nonzero monic integer polynomial of degree d(#T − 1). So it has at most that many
  roots, each an algebraic integer.
- **Prime-power angles.**
  - **The root of unity.** Let θ = jπ/q with q = p^m, p an odd prime, gcd(j, q) = 1, and ζ = e^(iθ). Put η = ζ if j is even and
    η = −ζ if j is odd. Then η is a primitive q-th root of unity: if j is odd, −ζ = e^(2πi((j+q)/2)/q).
  - **The prime.** The ideal 𝔭 = (1 − η) of Z[η] is prime with 𝔭 ∩ Z = pZ, and η ≡ 1 (mod 𝔭). So y = ζ + ζ⁻¹ = ±(η + η⁻¹) ≡ ±2
    (mod 𝔭).
  - **The value.** Since λ has integer coefficients, λ(y) ≡ λ(±2) = ±2^N (mod 𝔭). That is not in 𝔭 because p is odd, so λ(y) ≠ 0.
- **The Legendre law.**
  - L_d = (−1)^d w^(1). So R_L = (−1)^(d#T) λ(1) w^(1) = (−1)^(d(#T−1)) λ(1) L_d.
  - For an integer polynomial, λ(1) ≡ λ(−2) (mod 3). So the factor is congruent to (−1)^(d(#T−1)) (−1)^(d(#T−1)) 2^N =
    2^N ≡ (−1)^N. ∎

## Proof of Proposition 6

- **The support.** w_θ vanishes at x exactly when sin(θ(d + 1 − 2|x|)) = 0. So its support is a union of weight classes, with
  allowed weights W ⊆ {0, …, d+1}.
- **The three conditions for a weight-defined relation.**
  - K3 holds when W is nonempty, and K1 when some weight is missing.
  - Forgetting one place leaves the other d places, and the projection contains a d-tuple of weight m exactly when m ∈ W or
    m + 1 ∈ W. So K2 holds exactly when no two consecutive weights are both missing.
  - Since W is symmetric, the verdict does not depend on which place is read as the contact.
- **No two consecutive weights are missing.** If t and t + 1 were, then θ(d+1−2t) and θ(d−1−2t) would both lie in πZ, and so would
  their difference 2θ. That is excluded. So K2 and K3 hold, and the support is a knot exactly when some weight is missing.
- **When a weight is missing.** This happens when θE ∈ πZ for some E ∈ {d+1, d−1, …, −d−1}.
  - For odd d, E = 0 qualifies (|x| = (d+1)/2).
  - For even d every E is odd and nonzero. If θ/π is irrational, nothing qualifies. If θ = jπ/q in lowest terms, E qualifies
    exactly when q | E, which needs q odd and q ≤ |E| ≤ d + 1, and then E = q works.
- **The excluded case.** At sin 2θ = 0, that is θ = π/2, the law vanishes for odd d and has full support for even d. ∎

## Proof of Corollary 7

- **Exact knots.**
  - The Legendre law is exact by Corollary 5. Its support is a knot by Proposition 6, with q = 3 ≤ d + 1.
  - For odd d every θ with sin 2θ ≠ 0 gives a knot, and λ(2 cos θ) ≠ 0 outside finitely many θ per level.
- **Towers.**
  - **The construction.** Let T₁ = SG^d_k, and build T_(m+1) by putting a copy of SG^d_k, scaled, on every up simplex of T_m, glued
    at its corners.
  - **The factor.** Summing each copy's inner vertices replaces its law by λ w. So R(T_m) = λ^(1 + n + … + n^(m−1)) w with
    n = #T, by induction.
  - **Finitely ramified.** Two up simplices T(v) ≠ T(v′) share at most one vertex.
    - Write their vertices v + e_a and v′ + e_b, with e₀ = 0. A common vertex v + e_a = v′ + e_b gives v′ − v = e_a − e_b ≠ 0.
    - That vector determines a and b. So there is only one common vertex, and copies meet in single points.
- **The dimension.**
  - **The self-similar set.** The limit is the attractor of n similarities of ratio 1/k. These map the open simplex onto the disjoint
    open up simplices, so the open set condition holds and its dimension is log n/log k (Hutchinson; Hilfer and Blumen for these
    sets).
  - **The bounds.** k^d/d! ≤ C(k+d−1, d) ≤ k^d gives d − log(d!)/log k ≤ log n/log k ≤ d. ∎

## Proof of Remark 8

- **The ratios.** For d = 2 the wave has g(1) = 1 and g(3) = y² − 1. For d = 3 the reduced wave w^(y)/y has g(2) = 1 and
  g(4) = y² − 2. It is defined at y = 0 too, and its corner relation is (λ/y^(#T−1)) times itself, by the proof of Theorem 2.
- **Matching a profile.** An odd profile g with g(1) ≠ 0 (resp. g(2) ≠ 0) is g(1)·w^(y) (resp. g(2)·w^(y)/y) with
  y² = 1 + g(3)/g(1) (resp. y² = 2 + g(4)/g(2)), and y may be complex.
- **The equality law.** If g(1) = 0 (resp. g(2) = 0), the law is a multiple of the equality law, which composes to itself.
- **From d = 4 on.** The odd profiles form a projective space of dimension at least 2, and the waves form a curve in it. The control
  in check 10 shows a sum of two waves failing on SG^4_2. ∎

## What the computation checks

`check.py` (17 s) replays every finite ingredient:
- **Closed forms (Lemma 1)**, for d = 1 to 7 on all tuples at four angles.
- **Exactness of the Legendre law in exact integers**, for d = 2 (k ≤ 7), 3 (k ≤ 5), 4 (k ≤ 3), and 5 to 7 (k ≤ 2), with
  factor ≡ (−1)^N mod 3.
- **The factor polynomial (Theorem 3)**, for 11 pairs (d, k) up to (3, 4), (4, 3) and (6, 2).
  - Method: three primes, and d#T + 3 values of y each. The identity R = λ(y) w^(y) at that many values is a polynomial identity
    modulo each prime, by degree.
  - Monic of degree d(#T − 1), with the right parity, λ(±2) = ±2^N, and the level-2 closed form.
  - The same integer polynomial from three further primes, and λ(1) against the exact Legendre factors.
- **The sector formula**, against direct factors at three angles in eight cases.
- **Lemma 4.**
  - Exactly: τ reproduces itself with factor 2^N in every exactness case. This counts the edge sets by their odd corners, and the
    counts are nonnegative, so the lemma follows in each case.
  - By direct enumeration for d = 2 (k ≤ 4), 3 (k ≤ 3), 4 and 5 (k = 2).
- **Nonvanishing.** Exact gcds with the minimal polynomials of 2 cos(2π/n) for n ≤ 60. The only n whose values are roots are n = 4
  (θ = π/2, every case) and n = 8 (θ = π/4, at k = 2 for every d, at k = 4 for d = 2 and 3). No odd prime power or twice one
  occurs.
- **Proposition 6** for d = 2 to 9 at every jπ/q with q ≤ 13 and at a generic angle. knotlab confirms six named supports.
- **Towers** of levels 2 and 3 in eight cases, exactly λ^((n^m−1)/(n−1)), and the dimension bounds.
- **Floating point** at four angles in 12 cases.
- **Controls.**
  - These fail to be exact: the unsigned support, one flipped sign, the wave without (−1)^(x₀), a sum of two waves in d = 4, and
    (−1)^(x₀) sign(E) in d = 4.
  - The corner relation vanishes at θ = π/4 on SG^3_2.
  - One positive case is checked: a sum of two waves in d = 3 is again exact (Remark 8).

## Reading

- **A knot builds exactly self-similar space in every dimension.**
  - The standing wave reproduces itself on every Sierpinski simplex of every dimension and level. Its Legendre member is a knot in
    every dimension d ≥ 2 and is never exceptional.
  - So for every d there are knots building finitely ramified self-similar spaces whose dimensions log C(k+d−1, d)/log k rise
    towards d. Nothing is drawn: one law on one simplex, glued to copies of itself, fixes the space.
- **Why it works.**
  - The law is two opposite phases, ζ^E and ζ^(−E). The d edges from the base corner lock the phases of all d + 1 corners together,
    and reversing every phase is odd, so the phases always recombine into the same wave.
  - The factor's arithmetic has the same content. At θ → 0 the wave becomes the linear law 1 + Σ s₀sᵢ, whose expansion lives on
    edges, and the only surviving edge sets are the d edges of the big simplex itself. So the gasket "sees" exactly its own edges,
    and λ(2) = 2^N.
- **Odd and even dimensions differ.**
  - In odd dimension the whole family is knots, with the balanced weight missing: a continuous family of exact knots. In three
    dimensions this is "not exactly two ones".
  - In even dimension only the angles jπ/q with q odd and q ≤ d + 1 are knots. In the plane that is only signed not-all-equal.
- **Contrast with three-manifolds.** `HUB-DIMENSION-20261024-001` found that unsigned bit laws on triangulated three-manifolds see
  only parity.
  - These spaces are not manifolds. Their cells meet at points, and the laws are signed.
  - So nothing here contradicts that obstruction. The comparison suggests it comes from bulk coupling (and, for counts, positivity)
    rather than from dimension itself.
  - The plane's exclusion even with signs (`SIGNED-SUBDIVISION-20261029-001`) points the same way.

## Nonclaims

- Only Sierpinski simplices and their towers are covered: finitely ramified spaces, built level by level from finite gadgets.
  "Dimension" means similarity (Hausdorff) dimension, and no manifold or space-filling claim is made.
- Exceptional angles are located only where checked (n ≤ 60 for the cases computed). Angles jπ/q with q not an odd prime power are
  not decided in general.
- Nothing infinite-volume or source-aware is claimed, and there is no physical interpretation.
