# The separation statement and stop rule (frozen before the work)

Epic `HOLE-SEP-20261110-001`, sub-goal B103, 2026-11-10. Written and committed before any kernel below was computed.

## Notation

LP_n, its rows, Q_{m,l}, L_k and Theorem 2 are as in `SEP-LEFT-20261110-001A`: n = 2^l holes (l ≥ 2), m = n + 1 pigeons, pigeon rows f_x
of l bits, hole rows g_h of l + 1 bits. F^fun_{m,n} is Braun's unary functional pigeonhole system (cells X_x,h; Booleanity, row and
column exclusions, row sums ρ_x = 1), Ideal_k and Cons_B its degree-k Nullstellensatz span and degree-B PC consequences. The reduced
decoder τ̃ sends a pigeon bit f_x,t to β_x,t = Σ_{z : z_t = 1} X_x,z and a hole bit g_h,j to γ_h,j = Σ_x x_j X_x,h, and a row-linear
monomial to the product of its bits' images.

## The statement to prove

**(R) Reduction.** For l ≥ 2, B ≥ 2, k ≤ B and 2lB − 1 ≤ n: every p ∈ L_k that lies in Cons_B(LP_n) lies in the kernel
K_k = {p ∈ L_k : τ̃(p) ∈ Ideal_k(F^fun_{m,n})}. (Planned proof: Lemma 1 of `SEP-LEFT-20261110-001A`, then Braun's decoder transfer and
his stability corollary, Cons_{B′} = Ideal_{B′} and Ideal_{B′} ∩ Pol_{≤k} = Ideal_k for n ≥ 2B′ − 1.)

**(K) Kernel bound.** dim K_k is small next to dim L_k: precisely, any bound dim K_k ≤ (1 − e^{−εk²/n})·dim L_k with ε < 1/3 turns
Theorem 2 of `SEP-LEFT-20261110-001A` into an unconditional dag-like Res(⊕) lower bound for LP_n, applied to a complement U of K_k in
L_k at k ≈ n/(24 l² + 4l) (so that B = k(12l + 2) meets 2lB − 1 ≤ n).

Known kernel elements, from the substitution: for each hole bit j ≤ l and each affine function a of the hole label (a = 1 or a = h_t),
κ_{a,j} = Σ_h a(h) g_h,j + (Σ_x x_j f_x,t if a = h_t; the constant c_j if a = 1). These (l + 1)² elements lie in K_1.

## Readings before any proof attempt

Exact GF(2) linear algebra, dim K_k for n = 4, 8, 16 and k = 1, 2 (k = 3 where it fits), with dim L_k, from the matching normal form
and the row-sum relations (Braun's Lemma on complete moment equations). Frozen predictions:
- **P1.** dim K_1 = (l + 1)²: the known elements span K_1.
- **P2.** dim K_k / dim L_k falls as n grows, for k = 2 (and 3 where read), and is below 1% at n = 16, k = 2.

## Stop rule

Stop at the first of:
- **(a) A theorem.** (R) proved and a bound (K) proved for all large n at k ≈ n/(24l² + 4l), giving the Res(⊕) lower bound for LP_n.
- **(b) The killed combination.** If P2 fails (dim K_k / dim L_k does not fall, or exceeds 10% at n = 16, k = 2), name the family of
  row-linear combinations that every moment functional kills, and stop: the route through τ̃ cannot give a dense separated space.
- **(c) The failing step.** If (R) holds and the kernel is small at the sizes read but no proof of (K) is found, name the step that a
  proof of (K) needs and record it, with the readings.

A bound for LP_n would not transfer to the knot sphere's count: the count's own Res(⊕) route is closed by its polynomial-calculus
degree O(√n) (`RES-XOR-COUNT-20261110-001A`, Lemma 1), and the reduction from LeftPigeon to the count (`COUNT-SYSTEMS-20261110-001A`)
uses non-affine decision trees, which Res(⊕) is not closed under.
