# Which signed laws reproduce themselves on which gaskets

Status: Proved

Ticket `SIGNED-GASKETS-20261029-001B`, 2026-10-29.

## Standard statement

**Setting.** As in `SIGNED-GASKETS-20261029-001A`.
- **The gasket.** SG_k is the k(k+1)/2 up triangles T(i, j) = ((i, j), (i+1, j), (i, j+1)) = (a, b, c) of a triangle cut into k².
  Its corners are A = (0, 0), B = (k, 0) and C = (0, k).
- **Exact.** R_k is the corner relation, and a law is exact on SG_k when R_k = λ_k w with λ_k ≠ 0.
- **Signed laws.** These are the 34 three-bit knots with weights ±1 on their tuples, the first allowed tuple (in the order 000, …,
  111) carrying +1: 1,168 laws.
- **Signed not-all-equal.** w = (−1)^a((a+b+c)|3), the law of ticket A.
- **The second family's law.** w′ = (−1)^a [NAE] = −(−1)^(a+b+c) w.

**Results.**
- **Lemma 1 (symmetries).**
  - The six symmetries of the gasket permute the roles a, b, c of every up triangle in the same way, and the corners A, B, C
    likewise. So w is exact on SG_k if and only if w∘π is, with the same factor, for every permutation π of the three places.
  - Complementing every bit preserves exactness too.
- **Lemma 2 (relabeling by position parity).** Suppose w(x̄) = ε w(x) for all tuples, with ε = ±1, and let k be odd. Then for
  α, β ∈ {0, 1} the law w^(αβ)(a, b, c) = w(a, b ⊕ α, c ⊕ β) has corner relation ±R_k(y_A, y_B ⊕ α, y_C ⊕ β). So it is exact
  whenever w is, with the same factor up to sign.
- **Theorem 3 (the second family).** For every k, one of two cases holds.
  - If k ≡ 1 or 2 (mod 4), R_k = λ′_k w′, so w′ is exact whenever λ′_k ≠ 0.
  - If k ≡ 0 or 3 (mod 4), R_k = μ_k (−1)^(x_B + x_C) c(E), where c = −2 at E = ±3 and c = 1 at E = ±1. This is never a multiple
    of w′, so w′ is never exact there.
  - λ′_k ≠ 0 is checked for every k ≡ 1, 2 (mod 4) up to 22 and conjectured for all k. No single small modulus decides it: λ′_6 =
    126 and λ′_13 = −292272084.
- **Theorem 4 (parity, by Lucas's theorem).** Unsigned even and odd parity are exact on SG_k exactly when k is a power of 2, with
  factor 2^(k−1). Otherwise their corner relation allows all eight corner triples.
- **Theorem 5 (census, k = 2 to 12).** Exactly 68 of the 1,168 signed laws are exact on some SG_k with 2 ≤ k ≤ 12.

| Family | Laws | Exact at | Why |
| --- | --- | --- | --- |
| F1: signed not-all-equal and its rotations | 3 | every k | Ticket A, Lemma 1 |
| F2: relabelings of F1 | 9 | odd k | Lemma 2 |
| F3: (−1)^a [NAE] and its rotations | 3 | k ≡ 1, 2 (mod 4) | Theorem 3 (factor checked to k = 22) |
| F4: relabelings of F3 | 9 | k ≡ 1 (mod 4) | Theorem 3 with Lemma 2 |
| P: unsigned even and odd parity | 2 | k = 2, 4, 8 (powers of 2) | Theorem 4 |
| Sporadic three-excluded laws | 30 | k = 3 only | none known |
| Sporadic not-all-equal laws | 12 | k = 5 only | none known |

Every family law is exact exactly at the levels its family predicts. Within k ≤ 12, every other exact law is one of the 42
sporadic ones, and three of the twelve not-all-equal laws at k = 5 are not exact at k = 13 to 20 either.

## Nearest known result

- **In the repository.** `SIGNED-GASKETS-20261029-001A` proves F1 for every k. `SIGNED-SUBDIVISION-20261029-001A` is the signed
  census under shared subdivision of the plane.
- **Outside.**
  - Lucas's theorem and the self-similarity of Pascal's triangle modulo 2 (Newman–Moore) are classical.
  - The relabeling is a standard change of variables.
  - No census of signed laws on level-k gaskets was found.
- **Classification.**
  - Lemmas 1, 2 and Theorem 4 are elementary or classical.
  - Theorem 3 and the census: no overlap found (candidate local delta).

## Proof of Lemma 1

- **Rotation.** The rotation (i, j) ↦ (k − i − j, i) maps T(i, j) onto T(k − i − j − 1, i). It sends its a-, b- and c-corners to
  the b-, c- and a-corners there, and it sends A, B, C to B, C, A.
- **Reflection.** The reflection (i, j) ↦ (j, i) fixes a, exchanges b and c, and exchanges B and C.
- **Conclusion.** Relabeling the sum by a symmetry turns the corner relation of w into that of w∘π, with its corners permuted by the
  same π. Complementing every bit is a bijection of the configurations. ∎

## Proof of Lemma 2

- **The substitution.** Substitute x(i, j) = y(i, j) ⊕ f(i, j) with f = αi + βj (mod 2). On T(i, j) the three corners carry f,
  f + α and f + β. So w(x_a, x_b, x_c) = w(y_a ⊕ f, y_b ⊕ f ⊕ α, y_c ⊕ f ⊕ β) = ε^f w^(αβ)(y_a, y_b, y_c).
- **The corners.** f vanishes at A and equals αk and βk at B and C, which is α and β when k is odd. So the corner relation of
  w^(αβ) at y equals ε^(Σf) R_k(y_A, y_B ⊕ α, y_C ⊕ β) = ε^(Σf) λ_k w^(αβ)(y).
- **Even k.** Then the shift at the corners vanishes. The relabeled law is exact only if it is proportional to w itself, which fails
  for every law of F1 and F3. ∎

## Proof of Theorem 3

- **Reduction to w with a field.** w′ = −(−1)^(a+b+c) w on all tuples. On SG_k, Π_T (−1)^(a_T+b_T+c_T) = Π_v (−1)^(x_v deg v), and
  the degree is 1 at the corners, 2 on the edges and 3 inside. So the sum for w′ is (−1)^(#T) (−1)^(x_A+x_B+x_C) times the sum for w
  with an extra factor (−1)^(x_v) at every inner vertex.
- **Sectors, as in ticket A.**
  - At an inner vertex the extra factor cancels the a-corner sign. The vertex sum becomes 2cos(πS/3) instead of 2i sin(πS/3).
  - The vertices of the bottom row and the left side are unchanged, so the triangles at A, B and C still share one sector s₀.
  - Flipping every sector now multiplies the weight by (−1)^(#T + 2(k−1)) = (−1)^(#T). So Z(−s₀) = (−1)^(#T) Z(s₀).
- **The two cases.**
  - If #T = k(k+1)/2 is odd, that is k ≡ 1, 2 (mod 4), the sum is Z(1)(ω^E − ω^(−E)) = Z(1) D (−1)^(x_A) w. Then
    R_k = (−1)^(#T+1) D Z(1) w′.
  - If #T is even, the sum is 2 Z(1) cos(πE/3). Then R_k = 2(−1)^(#T) Z(1) (−1)^(x_B + x_C) cos(πE/3). This is nonzero on all
    eight tuples unless Z(1) = 0, so in either case it is not a multiple of w′.
- **The data agree.** The checks find the cosine form, with μ_k ≠ 0, at every k ≡ 0, 3 (mod 4) up to 16, and exactness at every
  k ≡ 1, 2 up to 16. The factor is nonzero modulo some prime for every k ≡ 1, 2 up to 22. ∎

## Proof of Theorem 4

- **The rule.** Parity b on up triangles reads x(i, j+1) = x(i, j) + x(i+1, j) + b (mod 2). Each row is (1 + S) applied to the
  row below, plus the constant b. Since (1 + S) kills the constant row, the apex is x(0, k) = Σ_i C(k, i) x(i, 0) + b.
- **Powers of 2.** By Lucas's theorem C(k, i) is even for all 0 < i < k exactly when k is a power of 2. Then x_C = x_A + x_B + b,
  the parity law itself, and each allowed corner triple has 2^(k−1) extensions (the free bottom row).
- **Other k.** Some C(k, i) with 0 < i < k is odd, so flipping x(i, 0) flips the apex. Hence every corner triple occurs. ∎

## Proof of Theorem 5

- **The census.** Exact computation of every corner relation (integers by the Chinese remainder theorem), for all 1,168 laws and
  k = 2 to 12. The engine agrees with brute-force enumeration on 40 random laws at k = 2 and 3.
- **The families.** F1 to F4 and P are built from their definitions (rotations, complements and relabelings, then normalized). They
  are disjoint and number 26 laws. Each is exact exactly at its predicted levels.
- **The rest.** The remaining 42 exact laws are 30 three-excluded laws exact only at k = 3, and 12 not-all-equal laws exact only at
  k = 5. ∎

## Reading

- **What the gaskets select.** Only two mechanisms persist across infinitely many levels.
  - The Eisenstein standing wave (F1, with its field-twisted and relabeled forms F2 to F4). Its period in k comes from the parity of
    the number of triangles and of k.
  - Linear parity, at the powers of 2, the Newman–Moore self-similarity.
  - Everything else exact on a gasket is a single-level coincidence: 30 three-excluded laws at k = 3 and 12 not-all-equal laws at
    k = 5.
- **Knots that build every gasket.** Of the knots, only signed not-all-equal and its rotations are exact at every level, by ticket A.
  The second family follows if its factor never vanishes. Parity is affine and builds only the gaskets of level 2^m.

## Nonclaims

- The census stops at k = 12, and the sporadic laws are not explained.
- The nonvanishing of λ′_k for every k ≡ 1, 2 (mod 4) is a conjecture, checked to k = 22.
- Laws with real weights, or with different laws on different triangles, are not covered.
