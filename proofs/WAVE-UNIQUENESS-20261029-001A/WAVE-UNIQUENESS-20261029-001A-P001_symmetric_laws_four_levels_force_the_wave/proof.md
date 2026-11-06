# Symmetric laws: four levels force the standing wave

Status: Proved

Ticket `WAVE-UNIQUENESS-20261029-001A`, 2026-10-29.

**What it uses:**
- `SIGNED-GASKETS-20261029-001A`: the gaskets SG_k and exactness.
- `SIMPLEX-GASKETS-20261029-001A`, Theorem 2: the standing wave w^(y) = (−1)^a U_(E−1)(y/2) has corner relation λ_k(y) w^(y) for every complex y.
- The exact corner-relation engine of `SIMPLEX-GASKETS-20261029-001A` (copied here as `gasket_engine.py`).
- Classical algebra: pencils of binary quadrics, resultants, Gröbner bases.

## Standard statement

**Setting.**
- **Laws.** Laws are symmetric in the two non-base corners: w(a, b, c) = f(a, b + c), six complex weights.
- **The gasket.** SG_k has the up triangles T(i, j) = ((i, j), (i+1, j), (i, j+1)) with i + j ≤ k − 1, read as (a, b, c), and the
  corners A = (0, 0), B = (k, 0), C = (0, k).
- **Exactness.** The law is exact at level k when its corner relation R_k is λ_k w with λ_k ≠ 0.
- **The final classes.**
  - **The standing waves** w^(y) for y ∈ C, with their limits: y = ±2 gives (−1)^a E, and y = ∞ gives the equality law [a = b = c].
  - **Products** u(a)v(b)v(c).
  - **The laws** u(a)[b = c].
  - **The frozen laws** F = [a = 0][b ≠ c] + [a = b = c = 1] and its complement F̄ = [a = 0][b = c = 0] + [a = 1][b ≠ c].

**Results.**
- **Theorem 1 (four levels force the wave, up to degenerate laws).** A symmetric law is exact at levels 2, 3, 4 and 5 if and only if it is
  one of the final classes, with nonzero factors at those levels. Each final class is exact at every level where its factor is nonzero.
- **Theorem 2 (fewer levels do not suffice).**
  - **(a) Level 2 alone.** In the generic stratum, the laws exact at level 2 form a two-dimensional family. Both the sine and the cosine
    waves lie in it.
  - **(b) Levels 2 and 3.** The generic laws exact at both are the standing waves and the laws on an irreducible curve K of degree 10. K
    contains real laws, which are not waves, and none of its laws is exact at level 4.
  - **(c) Levels 2, 3 and 4.** Besides the waves, exactly 16 laws are exact at all three: complex, in 8 conjugate pairs, none real. All 16
    fail level 5.
- **Corollary 3 (knots).** Among the laws exact at levels 2 to 5, the only knot is signed not-all-equal: y = ±1, θ = π/3.

| Levels | Generic stratum: exact laws besides the waves | Degenerate strata |
| --- | --- | --- |
| 2 | a two-dimensional family (biorthogonal two-sector laws with one balance condition) | tangent: a curve; rank one: Q² ∝ Q |
| 2, 3 | the curve K (degree 10, irreducible, real points) | (−1)^a E, F, F̄; products, u(a)[b = c] |
| 2, 3, 4 | 16 complex laws | as above |
| 2, 3, 4, 5 | none | as above |

## Nearest known result

- **In the repository.**
  - `SIGNED-GASKETS-20261029-001B` is the census of ±1 laws with knot supports in the plane, where only the wave persists. This ticket
    shows the same holds for all complex symmetric laws, with explicit exceptions at two and three levels.
  - `SIMPLEX-GASKETS-20261029-001B` is the censuses in dimensions 3 and 4.
- **Outside.**
  - Decimation on gaskets is classical. Its familiar fixed points, zero temperature (equality) and infinite temperature (products),
    are among the degenerate classes here.
  - Pencils of binary quadrics, resultants and Gröbner bases are classical.
  - No classification of the laws exact at several consecutive gasket levels was found in the bounded search of
    `SIMPLEX-GASKETS-20261029-001A`.
- **Classification.** Theorems 1 and 2: no overlap found (candidate local delta).

## Proof

### The strata

- **The pencil.** Write the law as two binary quadrics f(0, ·) and f(1, ·), and consider the pencil they span. Exactly one of three cases
  holds.
  - **S1.** The pencil contains two distinct squares v₁² and v₂², and w = u₁v₁v₁ + u₂v₂v₂ with u₁, u₂ independent.
  - **S2.** The pencil contains exactly one square v², and its other members share the factor v. Then w = u₁vv + u₂(ve + ev) with u₁, u₂
    independent.
  - **S3.** w = u ⊗ Q, rank one in the base corner. This covers a one-dimensional pencil and dependent u's.
- **Why only these.** The squares of a pencil are the zeros of its discriminant, a binary quadratic that cannot vanish identically. Two
  roots give S1. A double root means the bilinear discriminant pairing vanishes, so the other members share v: that is S2.

### Level 2 for two sectors (Lemma 4)

- **Check 1.** For w = u₁v₁v₁ + u₂v₂v₂, summing the three inner vertices of SG_2 gives R₂ = Σ_ijk P_ji P_ki G_jk u_i v_j v_k. Here
  P_ij = ⟨u_i, v_j⟩ and G_ij = ⟨v_i, v_j⟩ (bilinear pairings), and the identity is checked symbolically.
- **Consequence.** In S1 the six tensors u_i ⊗ v_j v_k form a basis. Exactness therefore needs a diagonal coefficient tensor:
  P₁₁²G₁₁ = P₂₂²G₂₂ = λ ≠ 0, and P₂₁ = P₁₂ = 0. That is biorthogonality, u₁ ⊥ v₂ and u₂ ⊥ v₁. In C² this means u₁ = A·Jv₂ and
  u₂ = B·Jv₁, with J the rotation.

### The sector formulas (Lemma 5)

- **The locked triangles.** For a biorthogonal law, the base corners on the edges from A pair u with v of the neighbouring triangle. Mixed
  sectors pair to zero, so all triangles with i = 0 or j = 0 carry one sector s₀, including the three corner triangles.
- **The formula.** R_k = Z_k(1) u₁v₁v₁ + Z_k(2) u₂v₂v₂. Here Z_k(s₀) sums over the sectors of the other triangles the product of the vertex
  pairings.
- **Exactness.** It holds at level k exactly when Z_k(1) = Z_k(2) ≠ 0.
- **Check 2** compares the formula with exact integer corner relations for k = 3, 4, 5.

### Theorem 2 (S1)

- **Coordinates.** v₁ = (1, p), v₂ = (1, q) and r = B/A. Let L_k be the numerator of Z_k(1) − Z_k(2), with the powers of A and of p − q
  removed.
  - The case v_i = (0, 1) reduces to these coordinates by complementing every bit, which preserves exactness, except for the pair
    {(1, 0), (0, 1)}.
  - That pair gives B = −A, which is the equality law (check 4).
- **(a)** Level 2 is the single equation L₂ = 0 in the three coordinates (p, q, r).
- **(b) Levels 2 and 3.** res_r(L₂, L₃) = ±(p − q)³(p² + 1)(q² + 1)(pq − 1)K(p, q), with K irreducible over Q, symmetric, of degree 10.
  - p = q is excluded (v₁ ∥ v₂), and p² + 1 = 0 or q² + 1 = 0 makes G_ii = 0, so λ = 0.
  - **On pq = 1.** L₂ gives r = ±p. The value r = −p satisfies L₂ and L₃ identically and gives the standing wave with
    y² = (1 + p)²/p. The value r = +p is the cosine wave, which fails level 3 (check 4).
  - **On K.** The common root r gives laws exact at levels 2 and 3. The real point p = −1.572, q = 0.0765, r = 1.858 is one of them, and
    they fail level 4 (check 11).
- **(c) Level 4.** res_r(L₂, L₄) = (pq − 1)(p + q)²(p − q)⁵(p² + 1)²(q² + 1)²K₄, with K₄ of degree 22.
  - res_q(K, K₄) = p⁶(p² + 1)³²F₃₂F₃₆, both F irreducible.
  - At p = 0, K(0, q) and K₄(0, q) share only q = 0, the degenerate case p = q. The factor p² + 1 is isotropic.
  - At 80 digits, a ratio r common to L₂, L₃ and L₄ exists at all 32 roots of F₃₂ and at none of the 36 roots of F₃₆.
  - The 32 points form 16 laws, since swapping the sectors gives the same law.
  - K meets p + q = 0 only at degenerate points.
- **Level 5.** All 16 laws fail level 5. The relative residual of Z₅ is at least 0.16 at 80 digits, and the double-precision corner
  relation is at least 7% from proportional (check 6).
- **Which waves this covers.** The waves with y ≠ 0, ±2 lie in S1. y = ±2 is (−1)^a E, in S2. y = 0 has λ = 0. ∎

### The other strata

- **S2 (check 7).**
  - **Chart v = (1, p), e = (0, 1).** Saturating the level-2 minors by det(u₁, u₂) leaves the curve a₀ + a₁p − b₁ = 0,
    a₁(p² + 1) + b₁p = 0, b₀ + b₁p = 0.
  - On the curve, the level-3 minors have gcd 4p(p − 1)(p² + 1)⁷.
    - p = ±i gives R₂ = R₃ = 0, so λ = 0.
    - p = 1 gives −(−1)^a E.
    - p = 0 gives F̄.
  - **Chart v = (0, 1), e = (1, 0).** The saturated ideal (a₀, a₁ − b₀, b₁) gives only F.
- **S3 (check 8).**
  - For w = u ⊗ Q, R_k = u ⊗ Q^k times a scalar polynomial, for k = 2, 3. So level-2 exactness forces Q² = cQ with c ≠ 0, and Q is
    diagonalizable with eigenvalues in {0, c}.
  - Rank 1 gives a product. Rank 2 gives Q ∝ I, that is u(a)[b = c].

### Theorem 1: the final classes are exact at every level

- **Waves.** `SIMPLEX-GASKETS-20261029-001A`, Theorem 2: R_k = λ_k(y) w^(y) for all complex y. The limits are the values y = ±2 and the
  equality law, which composes to itself.
- **Products.** A product law turns the gasket into a rank-one network. R_k is the product of the vertex sums times the law.
- **u(a)[b = c].**
  - Every triangle forces its b- and c-corners equal, so each level |v| = j ≥ 1 is constant and B = C.
  - Hence R_k = Π_(j=1)^(k−1) (u₀^(j+1) + u₁^(j+1)) · u(a)[b = c].
- **F.**
  - **Base corner 1.** It forces its whole upper cone to 1.
  - **Base corner 0.** It forces exactly one of its b- and c-corners to 0. So the zero vertices form a monotone path from A.
  - **The path is straight.** A turn would put a zero vertex in the b- or c-corner of a triangle with base 1.
  - **Conclusion.** The path is the bottom edge or the left edge. With x_A = 1 everything is 1. Each allowed corner triple therefore has
    exactly one completion, and R_k = F with λ = 1. F̄ is its complement.
- **Exhaustiveness.** Strata S1, S2 and S3 exhaust the symmetric laws, so together with Theorem 2 this proves Theorem 1. Check 9 confirms
  exactness of every class in exact integers for k = 2 to 8. ∎

### Corollary 3

- **The waves.** A wave's support is a knot only at y = ±1, which is signed not-all-equal (`SIGNED-GASKETS-20261029-001A`).
- **The rest.** The other classes have product supports, supports forcing b = c, or frozen supports, and none passes K2 (check 10). ∎

## What the computation checks

`check.py` (about 20 seconds):
- **The algebra.** The level-2 coefficient identity (symbolic), the sector formulas against exact integer relations (12 cases), and the
  level-3 and level-4 eliminations and factorizations.
- **The intersections.** K with level 4, at 80 digits, with level 5 for the 16 laws.
- **The strata.** The tangent and rank-one strata.
- **The final classes and knots.** Exactness of eight sample class members at levels 2 to 8 in exact integers, and the knot status of
  every class.
- **Controls.** The cosine wave fails level 3, a law on K fails level 4, and a random law fails level 2.

## Reading

- **The wave is forced, but not quickly.**
  - Two levels admit a whole curve of impostors, and three levels admit 16 complex ones. Four levels leave only the standing wave,
    besides laws that never couple anything: products, the b = c laws and two frozen laws.
  - Self-reproduction at every scale is therefore, in this class, the same as being a standing wave: two opposite phases held in step.
- **Harmonies.** Among the symmetric laws, the only non-degenerate way to look the same at every scale is to be two cancelling phases. The
  only such law that is a knot is signed not-all-equal.
- **What the impostors are.** The laws on K are genuinely two-sector laws, real ones included, whose sector sums agree at levels 2 and 3 by
  coincidence. The phases are not locked by any mechanism, and level 4 exposes them.

## Nonclaims

- **Scope.** Only laws symmetric in the two non-base corners. General three-bit laws are ticket B.
- **"Exact at every level"** for the final classes holds wherever their factor is nonzero. For the waves the factor's zeros are the
  exceptional angles of `SIMPLEX-GASKETS-20261029-001B`.
- **The 80-digit root isolation** is numerical. The factorizations behind it are exact.
