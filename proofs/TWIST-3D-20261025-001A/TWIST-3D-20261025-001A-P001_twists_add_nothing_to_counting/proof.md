# Twists add nothing to counting laws in three dimensions

Status: Proved

Ticket `TWIST-3D-20261025-001A`, 2026-10-25.

**What it uses:**
- from `HUB-DIMENSION-20261024-001A-P001`:
  - the seven symmetric edge laws and their invariants;
  - the factorization argument that turns move identities into invariance;
- from `NATIVE-APPROX-20261024-001B-P001`: the six open knots are the Fibonacci knot with one or two places negated;
- classical background, cited and not admitted as local evidence: cellular cohomology with coefficients in Z/2. The values of the
  invariants are computed directly, so no theorem on connecting triangulations by moves is needed.

## Standard statement

**Setting.**
- **Ordered triangulations.** Every tetrahedron of a triangulation of a closed orientable three-manifold M carries an order 0 < 1 < 2 < 3
  of its vertices, and faces are glued by the order-preserving maps.
  - Each tetrahedron then has a sign ±1, according to whether its order agrees with the orientation of M.
  - V, E and T count vertices, edges and tetrahedra after gluing.
- **Ordered laws.** A law puts one bit on each edge and has:
  - a *triangle rule* R ⊆ {0, 1}³, read on (x_ab, x_bc, x_ac) for a triangle a < b < c. R may be any of the 255 non-empty relations,
    including the twisted Fibonacci knots;
  - two *tetrahedron rules* Q₊ and Q₋, sets of labellings of the six ordered edges whose four faces lie in R, for positive and negative
    tetrahedra.

  The count c(T) is the number of edge labellings with every tetrahedron in its rule.
- **Ordered moves.** They act inside the 4-simplex [01234], whose facet F_i omits vertex i.
  - A 2–3 move with apex pair {p, q} (10 kinds) replaces F_p and F_q by the other three facets.
  - A 1–4 move with new vertex r (5 kinds) replaces F_r by the other four.
  - For a global orientation ε = ±1, the sign of F_i is ε(−1)^i on the new side and −ε(−1)^i on the old side.
- **The identities.** Fix a labelling of the move's boundary edges whose boundary triangles lie in R. The new side, summed over the new
  edges, must equal λ (2–3) or μ (1–4) times the old side.

**Theorem 1 (census).** A law satisfies all ordered identities, for some λ ∈ {1, 2} and μ ∈ {1, …, 16}, with a non-empty tetrahedron
rule, exactly when:
- Q₊ = Q₋, and
- the common rule is one of the seven sets below, contained in the labellings compatible with R.

| Law | Tetrahedron rule | (λ, μ) | Triangle rules carrying it |
| --- | --- | --- | --- |
| all 0 | the zero labelling | (1, 1) | the 128 containing 000 |
| all 1 | the all-ones labelling | (1, 1) | the 128 containing 111 |
| all equal | both constant labellings | (1, 1) | the 64 containing both |
| even cocycles | every face has even parity | (1, 2) | the 16 containing the even class |
| odd cocycles | every face has odd parity | (1, 2) | the 16 containing the odd class |
| even or odd | all faces of one parity | (1, 2) | the full rule |
| free | every labelling | (2, 16) | the full rule |

That gives 354 laws over the 255 triangle rules. No law uses an asymmetric part of its triangle rule, and none depends on orientation.

**Corollary 2 (what counting sees).** For each law, N(T) = c(T) · (λ³/μ)^V · λ^(−T) is unchanged by every ordered move. Its values are:
- 1, 1 and 2 for the three constant laws;
- |H¹(M; Z/2)|/2 for even and for odd cocycles;
- |H¹(M; Z/2)| for "even or odd";
- 1 for "free".

So, with or without twists, counting with one bit per edge sees a three-manifold only through its mod-2 first cohomology.

**Corollary 3 (the twisted Fibonacci knots).**
- **The six open knots.** Each open knot R_c = N[c] ∪ {c̄}, with c non-constant, contains exactly one constant tuple and exactly one parity
  class. So it carries exactly two laws: one constant law (N = 1) and one cocycle law (N = |H¹|/2). The twist, its extra tuple, is never
  used.
- **The no-lone knots.** They contain both constants and the even class, and carry four laws: all 0, all 1, all equal, and even
  cocycles.

**Reading.**
- **Twists add nothing.** Letting each triangle read its edges in order, and letting tetrahedra see their orientation, produces exactly
  the same seven laws as the symmetric census of `HUB-DIMENSION-20261024-001A`.
- **The twisted Fibonacci knots fall back to their parity part.** Whatever the twist could carry in two dimensions does not survive the
  three-dimensional moves.

## Nearest known result

- **The invariants are classical.** They are the untwisted Dijkgraaf–Witten invariant for Z/2 (|H¹(M; Z/2)|/2) and its relatives, and
  Dijkgraaf–Witten state sums are defined on ordered triangulations.
- **The local content** is the exhaustive census of ordered Boolean laws, with orientation-dependent rules: twisting and orientation
  produce nothing new. No such census was found in the bounded scan.
- **Novelty:** `candidate-local-delta`; folklore risk low to medium.

## Proof

### Theorem 1

- **Finitely many conditions.** For each triangle rule R and each (λ, μ), the identities are finitely many equations in the unknown sets
  Q₊ and Q₋. There are at most 2 × (10 × 512 + 5 × 64) of them, each between sums of products of indicator values.
- **The search.** `check.py` decides them by a complete depth-first search over the indicator values.
  - At each node it applies unit propagation. A value is fixed only when every alternative makes some identity impossible under the
    current partial assignment. The test compares the identity's possible right-hand values with the range between the number of
    terms already true and the number not yet false.
  - So no solution is pruned. Every leaf reached is a full assignment, and it is kept only if all identities hold.
- **The two runs.** The search runs for all 255 triangle rules and all 32 values of (λ, μ), once with Q₊ = Q₋ imposed and once with
  independent Q₊ and Q₋. Both runs return exactly the 354 laws of the table, and every solution of the second run has Q₊ = Q₋.
- **Soundness.** Each of the 354 laws passes every identity by direct evaluation. ∎

### Corollary 2

- **Invariance.** The count factorizes over the move region. The region's contribution depends only on its boundary labelling, and the
  identities relate the two sides for every allowed boundary labelling, as in `HUB-DIMENSION-20261024-001A`. Orders and orientations
  are part of the region's data, and the identities cover all of them.
  - So a 2–3 move multiplies c by λ and a 1–4 move by μ.
  - Since E = V + T, N changes by λ · λ^(−1) = 1 under a 2–3 move and by μ · (λ³/μ) · λ^(−3) = 1 under a 1–4 move.
- **The values.**
  - The even-cocycle labellings are the 1-cocycles over Z/2, so c = |Z¹| = |H¹(M; Z/2)| · 2^(V−1) on a connected triangulation.
  - The all-ones labelling has three ones on every triangle, so the odd cocycles are the coset of the all-ones labelling, of the same
    size.
  - "Even or odd" counts both; "free" counts all 2^E labellings; the constant laws count one or two labellings.
  - Normalizing with the table's (λ, μ) gives the stated values. ∎

### Corollary 3

- **The shape.** By `SOFT-HUB-20261024-001A`, Proposition 6, R_c = N[c] ∪ {c̄}.
- **Constants.** For non-constant c, N[c] contains 000 when c has weight 1 and 111 when c has weight 2, and c̄ is non-constant. So R_c
  contains exactly one constant tuple.
- **Parity classes.** The excluded set is a parity class minus c. So R_c contains the whole other parity class and misses two tuples of
  the first.
- **The no-lone knots** contain both constants and the even class. Theorem 1 then gives the laws listed. ∎

## Checks

`check.py` uses the standard library only (seed 20261025) and runs in about 80 seconds. It confirms:
- **Theorem 1.**
  - Both searches return exactly the 354 expected laws (128, 128, 64, 16, 16, 1 and 1 by type).
  - The two orientations always agree.
  - Every expected law passes every identity by direct evaluation.
- **Corollary 2.** On 60 sampled ordered triangulations of closed orientable manifolds, with first homology 0, Z, Z/2, Z/3, Z/4,
  Z/5, Z/7, Z/8 and (Z/2)², the counts of the seven laws equal 1, 1, 2, |Z¹|, |Z¹|, 2|Z¹| and 2^E, with |Z¹| = |H¹(M; Z/2)| · 2^(V−1)
  computed from the Smith normal form.

**Controls.**
- **The identities can reject.** The full twisted rule, the knot excluding 000, 011 and 101 with all twelve compatible tetrahedra,
  fails some identity for every (λ, μ).
- **The 1–4 identities matter.** Without them, the search admits rules outside the seven for the full triangle rule.
- **The samples are not all spheres.** A sample with first homology of even order has |H¹(M; Z/2)| = 2.

## What this does not show

- **Weighted state sums.** Positive weights instead of counts are ticket B.
- **Richer labels.** Several bits per edge, or labels from a larger group, are not covered. Dijkgraaf–Witten counts with a non-abelian
  group see much more.
- **Other placements of bits.** Bits on faces or flags with other local structures are not covered.
