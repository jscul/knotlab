# The failure of full reach at every power of two from 8

Status: Proved by hand where marked (Theorems 1 to 3, Lemma 4), with the finite checks of `check.py`, and read by an independent
referee pass on 2026-11-10, whose findings are folded in (an edge case of Theorem 2(c), Lemma 4's range, Theorem 3's wording and
proof, and checks for every computed claim). The registered target A1, the failure at every power of two, is **not proved**: it is
reduced to one walk count, which is computed to vanish at every power of two from 8 to 128. The laws A2 and A3 are computed.

Ticket `REACH-HALVES-20261110-001A`, 2026-11-10 (pre-registered in commit 03bd5937b).

## Standard statement

- **The walk.** As in `FULL-REACH-PROOF-20261108-001A`: the contacts of the n × n torus of rule-60 rings cut open both ways are the
  points (X, Y) of the box B = [0, N]², N = 2n − 2, with X + Y odd; an h (X odd) reads (X ± 1, Y ± 1) with equal signs, a v (X even)
  reads (X ± 1, Y ∓ 1), reads leaving the box die, and A[c, d] = 1 when c reads d, over GF(2). Ring (i, j) holds the contacts
  (2i ± 1, 2j) and (2i, 2j ± 1) of the box. G_{c,d}(w) = Σ_k A^k[c, d] w^k, and c **reads** d when G_{c,d} ≠ 0. D(X, Y) = (Y, X) and
  ρ(X, Y) = (Y, N − X) are the diagonal reflection and the quarter turn; A^k[c, d] = A^k[Dd, Dc] and ρ commutes with A
  (`FULL-REACH-PROOF-20261108-001A`, Theorem 2).
- **The points.** d* = (n + 3, n + 2) and c* = Dd* = (n + 2, n + 3), just below and just above the diagonal X = Y, half a side from the
  corner (0, 0).
- **The targets** (registered). A1: at n = 2^m ≥ 8, c* never reads (0, 1) or (1, 0), the contacts of the corner ring (0, 0), so full
  reach fails. A2: the corner return law. A3: the exact failing set.

**Theorem 1 (the failure follows from one walk count).** (a) The corner contact (0, 1) reads only (1, 0) and is read only by (1, 2); (1, 0)
reads only (2, 1) and is read only by (0, 1). (b) For every n ≥ 5 and every k, A^k[c*, (0, 1)] = A^k[(1, 0), d*] and
A^(k+1)[c*, (1, 0)] = A^(k+1)[(0, 1), d*] = A^k[(1, 0), d*]. (c) Hence, if (1, 0) never reads d*, then c* misses the ring (0, 0) and full
reach fails at n. (d) On the h contacts h(i, j) = (2i + 1, 2j), A² is the walk of the **conveyor grid** [0, n − 2] × [0, n − 1]: a step
to a 4-neighbour inside the grid, except that from the bottom row (j = 0) there is no step to the left and from the top row (j = n − 1)
no step to the right. So for even n the failure at n follows from

  (★) the number of conveyor-grid walks of each length from (0, 0) to (n/2 + 1, n/2 + 1) is even.

**Theorem 2 (the reflection about the near diagonal).** Let σ(X, Y) = (Y + 1, X − 1), the reflection in the line X − Y = 1 on which
(1, 0) and d* lie. (a) σ maps contacts to contacts, h to h and v to v, and c reads d in the whole plane exactly when σc reads σd: unlike
the box's own reflections, which carry A to Aᵀ, σ is a symmetry of the walk. (b) For c, d on the line X − Y = 1, G^B_{c,d} = G^{σB}_{c,d},
σB = [1, N + 1] × [−1, N − 1] the box moved one step along the line's normal. (c) Mod 2, the walks from c to d in B are as many as those
whose every excursion off the line lies above it (Y > X − 1) and touches the left wall X = 0 or the top wall Y = N. In the whole plane
the only walks that survive are the empty walk and the single step from an h of the line to its neighbour along it; so for c ≠ d with d
an h (the case of (1, 0) and d*), no walk survives in the plane, and in the box an odd count needs excursions above the diagonal that
reach the left or the top wall.

**Theorem 3 (the strip, and what is special about powers of two).** On the strip [0, N] × Z (X bounded, Y free), in the Fourier variable
t of Y the walk is the (2n − 1) × (2n − 1) matrix A(t) = t T_e + t⁻¹ T_o (T_e, T_o the matchings of even and odd bonds), and

  det(λI − A(t)) = λ U_(n−1)((λ + t + t⁻¹)²),

U_k the Chebyshev polynomials over GF(2) (U_(−1) = 0, U_0 = 1, U_(k+1) = τU_k + U_(k−1)). U_(n−1)(τ) = τ^(n−1) exactly when n is a
power of two, so then det(λI − A(t)) = λ(λ + t + t⁻¹)^(2n−2): besides the flat band λ = 0, present at every side, the strip has a single
branch λ = t + t⁻¹, the free walk in Y, with one eigenvector of period 4 in X, ψ = (t, t + t⁻¹, t⁻¹, 0, t, t + t⁻¹, t⁻¹, 0, …), and (for
t ≠ 0, 1) one Jordan block of size 2n − 2. At the eigenvalue 1/w the decaying root of s + s⁻¹ = w⁻² (s = t²) is s₋ = w² C(w⁴),
C(z) = Σ_j z^(2^j − 1) the Catalan series mod 2, the same at every power of two. At a side n = 2^a·k′ with k′ > 1 odd, the branch
λ = t + t⁻¹ has multiplicity 2(2^a − 1) (none at odd n), and the other branches are λ = t + t⁻¹ + (ζ + ζ⁻¹)^(1/2), ζ^(k′) = 1, ζ ≠ 1.

**Lemma 4 (anti-diagonal sums on the conveyor grid).** For every vector x on the conveyor grid and every anti-diagonal 0 ≤ s ≤ 2n − 3,
Σ_{i+j=s} (xM)(i, j) = x(0, s + 1) + x(n − 2, s + 1 − n) (values outside the grid read as 0): the sum of xM along an anti-diagonal is
read off the left and right columns of x. With x the corner's generating function this is a conservation law for the corner's orbit.

**Computed (exact; check 5 to side 64, the stress test to 128).**
- **A1 holds at 8, 16, 32, 64 and 128.** At every power of two from 4 to 128 the corner (0, 1) reads every contact except exactly the
  points (X + 1, X), X = n + 2, n + 6, …, 2n − 6 (none at 4), d* among them; so (★) holds there and c* misses the corner ring.
- **A2, the corner return law, at 4 to 128.** G_{(0,1),(0,1)}(w) = 1/(1 + L(w⁴)), L(z) = z + z² + z⁴ + ⋯ + z^n the trace polynomial of
  GF(2n): the corner returns at time 4j exactly when j + 1 is a power of two modulo 2n − 1. Its first-return series is the polynomial
  L(w⁴) = w⁴ + w⁸ + ⋯ + w^(4n). In the quadrant the return series is C(w⁴) (returns at 4(2^i − 1); computed below w^1200 at 8, 16 and
  32, where the far walls are out of reach), and the box's is that series folded modulo 2n − 1; since L(z) = L_∞(z + z^(2n)) with
  L_∞(z) = Σ_j z^(2^j), the box's return series is the quadrant's with z replaced by z + z^(2n). It obeys 1/r_(2n)(w) = 1/r_n(w²) + w⁴.
- **One far wall is not enough.** With either far wall removed (a half-strip) the corner's return series is the quadrant's below w^1200
  at 8, 16 and 32, and in the quadrant and both half-strips the corner does read d* (first at times 29, 29, 41 at n = 8; 61, 61, 93 at
  16; 125, 125, 189 at 32). The failure needs all four walls.
- **The far corner.** G_{(0,1),(N,N−1)} = w^(4n−2) G_{(0,1),(0,1)} at 4 to 128: the corner meets the opposite corner contact exactly as
  it meets itself, half a period of its return series later.
- **A3** is ticket B's census: at 8, 16, 32, 64 and 128 exactly the n − 4 contacts ρ^i(X, X + 1), X = n + 2, n + 6, …, 2n − 6, miss a ring,
  each the three rings of one corner (`REACH-HALVES-20261110-001B`).

**What resists.** (★) at every power of two. Theorem 1 makes it the whole of A1; Theorem 2 says which walks carry it (excursions above
the diagonal that reach the left or top wall), and Theorem 3 says what is special about powers of two along one axis (the strip's
spectrum collapses, besides λ = 0, to the single branch λ = t + t⁻¹). Neither closes the count. The last step needs the excursions of
Theorem 2 in closed form, or equivalently the corner's component at each eigenvalue, which must vanish at d* (an equivalent form of (★),
since the sequences k ↦ C(k, j)λ^(k−j) are independent); no route to that closed form was found.

## Nearest known result

- **Ingredients.** Reflection principles for lattice walks; Chebyshev polynomials over GF(2) and the nilpotency of rule 90 on 2^r − 1
  sites (Martin, Odlyzko and Wolfram 1984; Sutner's σ-automata); the parity of Catalan numbers (odd exactly at 2^j − 1); linearized
  polynomials and the trace of a finite field (Lidl and Niederreiter, chapter 3).
- **Related records here.** `FULL-REACH-PROOF-20261108-001A` (the symmetries, the transfer identity of its Theorem 5, which Theorem 1(d)
  restates in the walk's own terms), `CONE-COLLAPSE-20261109-001A` (two particles), `LINEAR-ROOTS-20261109-001` (the multiplicities;
  the corner sees exactly the eigenvalues of odd multiplicity, those with Tr(1/λ) = 1).
- **Classification.** New as far as found. A bounded web search on 2026-11-10 found nothing on this walk's reach or on a corner return
  series equal to 1/(1 + Tr-polynomial); the ingredients are classical. Not a priority claim.

## Proof of Theorem 1

(a) (0, 1) is a v; its reads are (1, 0) and (−1, 2), the second outside. Its readers are the h's at (−1, 0) and (1, 2) (an h reads
(X ± 1, Y ± 1) with equal signs), the first outside. (1, 0) is an h; its reads are (0, −1) and (2, 1), the first outside; its readers are the
v's at (0, 1) and (2, −1), the second outside.

(b) By Theorem 2 of `FULL-REACH-PROOF-20261108-001A`, A^k[c, d] = A^k[Dd, Dc]. With c = c*, d = (0, 1): A^k[c*, (0, 1)] =
A^k[(1, 0), d*]. With d = (1, 0): A^k[c*, (1, 0)] = A^k[(0, 1), d*]. By (a), e_(0,1)A = e_(1,0), so A^(k+1)[(0, 1), d*] = A^k[(1, 0), d*]
(and A^0[(0, 1), d*] = 0).

(c) If A^k[(1, 0), d*] = 0 for all k, then by (b) A^k[c*, (0, 1)] = 0 and A^k[c*, (1, 0)] = 0 for all k (at k = 0 because c* is neither).

(d) The h at (2i + 1, 2j) reads the v's at (2i, 2j − 1) and (2i + 2, 2j + 1). The first reads the h's at (2i + 1, 2j − 2) = h(i, j − 1) and
(2i − 1, 2j) = h(i − 1, j); the second reads (2i + 3, 2j) = h(i + 1, j) and (2i + 1, 2j + 2) = h(i, j + 1). The four end points are
distinct, so A² takes h(i, j) to its four grid neighbours, each once, as far as the reads stay in the box: the two through (2i, 2j − 1)
need 2j − 1 ≥ 0, that is j ≥ 1 (the step down, and the step to the left), and the two through (2i + 2, 2j + 1) need 2j + 1 ≤ N, that is
j ≤ n − 2 (the step up, and the step to the right); the last reads need the neighbour inside the grid. On the bottom row the step to the
left is lost and on the top row the step to the right, and nothing else. A walk of odd length from an h ends at a v; d* = h(n/2 + 1,
n/2 + 1) for even n. ∎

## Proof of Theorem 2

(a) σ keeps X + Y and sends X to Y + 1; for a contact X + Y is odd, so Y + 1 ≡ X (mod 2): σ keeps the type. An h at (X, Y) reads
(X + 1, Y + 1) and (X − 1, Y − 1), whose images (Y + 2, X) and (Y, X − 2) are σ(X, Y) + (1, 1) and σ(X, Y) − (1, 1), the reads of the h
σ(X, Y). A v at (X, Y) reads (X + 1, Y − 1) and (X − 1, Y + 1), with images (Y, X) and (Y + 2, X − 2) = σ(X, Y) ∓ (1, −1), the reads of the
v σ(X, Y).

(b) A walk in B, mapped point by point by σ, is a walk in σB with the same length, and conversely; c and d are fixed.

(c) Write u = (X + Y − 1)/2 and v = (X − Y − 1)/2: the line is v = 0, σ is (u, v) ↦ (u, −v), an h moves u by ±1 and a v moves v by ±1.
Cut a walk from c to d at its visits to the line into steps along it and **excursions**, maximal stretches with v ≠ 0, each on one side.
σ fixes the line pointwise, so reflecting one excursion gives a walk with the same ends and length. In the coordinates (u, v) the box is
−1 ≤ u + v ≤ N − 1, 0 ≤ u − v ≤ N; its part with v ≥ 0 is carried by σ onto {v ≤ 0, u + v ≥ 0, u − v ≤ N − 1}, the part of the box with
v ≤ 0 that avoids the left wall u + v = −1 (X = 0) and the top wall u − v = N (Y = N). So an excursion below the line can always be
reflected into the box, and one above it exactly when it avoids both walls. Reflecting the first reflectable excursion is an involution on
the walks from c to d in B, without fixed points among the walks that have one; the walks left are those whose every excursion is above
the line and touches X = 0 or Y = N. In the whole plane every excursion is reflectable, so only walks with no excursion remain. Such a
walk stays on the line, and a v-site of the line (odd u) must leave it at its next step, so the walk is empty or a single step from an h
of the line (even u) to a neighbouring v-site; it cannot end at an h other than its start. ∎

## Proof of Theorem 3

A strip contact (X, Y) carries the row vector e_X ⊗ e_Y; A = T_e ⊗ λ_Y + T_o ⊗ ρ_Y (`CONE-COLLAPSE-20261109-001A`, Theorem 1, with λ_Y
and ρ_Y the shifts down and up in Y). On ψ ⊗ Σ_Y t^Y e_Y it acts as ψ(t T_e + t⁻¹ T_o) ⊗ Σ_Y t^Y e_Y, so the strip's Fourier matrix is
A(t): symmetric, tridiagonal with zero diagonal, t on the even bonds (2j, 2j + 1) and t⁻¹ on the odd bonds. Its leading principal
minors D_k = det(λI − A(t)) restricted to the sites 0, …, k − 1 satisfy D_0 = 1, D_1 = λ and D_(k+1) = λD_k + a²_(k−1) D_(k−1) over GF(2),
a_(k−1) the weight of the bond (k − 1, k). Two steps at a time, (D_(2j+2), D_(2j+3)) = 𝕄(D_(2j), D_(2j+1)) with
𝕄 = [[t², λ], [λt², λ² + t⁻²]], det 𝕄 = 1 and tr 𝕄 = t² + t⁻² + λ² = (λ + t + t⁻¹)² =: τ. By Cayley–Hamilton,
𝕄^j = U_(j−1)(τ)𝕄 + U_(j−2)(τ)I, and the second coordinate of 𝕄^j(1, λ) is U_(j−1)(τ)·λτ + U_(j−2)(τ)·λ = λU_j(τ). The whole matrix
has the 2n − 1 sites 0, …, N, so det(λI − A(t)) = D_(2n−1) = λU_(n−1)(τ).

Over GF(2), U_(2k+1)(τ) = τ U_k(τ)² (as for the u_k of Theorem 5 of `FULL-REACH-PROOF-20261108-001A`; by induction from
U_1 = τ). So for n = 2^a·k′ with k′ odd, U_(n−1)(τ) = τ^(2^a − 1) U_(k′−1)(τ)^(2^a), and U_(k′−1)(0) = 1 because k′ − 1 is even. At a
power of two (k′ = 1) this is U_(n−1)(τ) = τ^(n−1). Otherwise U_(k′−1) has degree k′ − 1 > 0, with the roots ζ + ζ⁻¹, ζ^(k′) = 1,
ζ ≠ 1 (from U_(k−1)(ζ + ζ⁻¹) = (ζ^k + ζ^(−k))/(ζ + ζ⁻¹)), and λ = t + t⁻¹ is a root of det(λI − A(t)) of multiplicity 2(2^a − 1).
For the eigenvector at λ = t + t⁻¹ write a_j = ψ(2j), b_j = ψ(2j + 1); the equations ψA(t) = λψ at the sites 2j and 2j + 1 read
t b_j + t⁻¹ b_(j−1) = λ a_j and t a_j + t⁻¹ a_(j+1) = λ b_j, with b_(−1) = 0, so (a_(j+1), b_(j+1)) = 𝕋(a_j, b_j) from (a_0, b_0) = (t, λ),
𝕋 = [[t², tλ], [tλ, λ² + t⁻²]], and the last equation asks b_(n−1) = 0 (there is no site 2n − 1). At λ = t + t⁻¹,
𝕋 = [[t², t² + 1], [t² + 1, t²]] = I + (t² + 1)[[1, 1], [1, 1]], whose square of the second term vanishes, so
(a_j, b_j) = (t, λ) + j(t² + 1)t⁻¹(1, 1) = (t + jλ, (j + 1)λ): ψ has period 4, (t, λ, t⁻¹, 0, …), and b_(n−1) = nλ = 0 for even n. The
recursion fixes ψ from (a_0, b_0), so the eigenvalue has one eigenvector, hence (for t ≠ 1) one Jordan block, of size 2n − 2. With λ = 1/w,
(1/w + t + t⁻¹)² = 0 gives s + s⁻¹ = w⁻², whose root in w²GF(2)[[w]] satisfies s = w²(1 + s²); with s = w²σ this is σ = 1 + w⁴σ², the
Catalan equation, whose solution mod 2 is Σ_j w^(4(2^j − 1)). ∎

## Proof of Lemma 4

The value of xM at a point is the sum of x over the points with a step into it. Summed along the anti-diagonal i + j = s, each
point q of an adjacent anti-diagonal is counted once for each of its steps that lands on it. A point q = (i, j) on i + j = s − 1 lands
there by its step up, allowed when j ≤ n − 2, and its step to the right, allowed when j ≤ n − 2 and i ≤ n − 3: two steps (they cancel)
unless i = n − 2 and j ≤ n − 2, when only the step up is left, and none on the top row j = n − 1. A point on i + j = s + 1 lands by its
step down, allowed when j ≥ 1, and its step to the left, allowed when j ≥ 1 and i ≥ 1: two steps unless i = 0 and j ≥ 1, when only the
step down is left, and none on the bottom row j = 0. The single steps are those of (n − 2, s − 1 − (n − 2)) = (n − 2, s + 1 − n) and of
(0, s + 1), each counted only when it is a point of the grid. For 0 ≤ s ≤ 2n − 3 that is the formula with values outside the grid read
as 0: the right-column point has j = s + 1 − n ≤ n − 2, below the top row, and the left-column point has j = s + 1 ≥ 1, above the bottom
row. (At s = −1 or s = 2n − 2 the left side is an empty sum and the formula would wrongly give x(0, 0) or x(n − 2, n − 1).) ∎

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | `FULL-REACH-PROOF-20261108-001A`'s and `CONE-COLLAPSE-20261109-001A`'s manifests bound by hash | pass |
| 1 | Theorem 1: the corner funnel, the two D-identities over 40n steps, and A² on h = the conveyor grid, sides 3 to 16 | pass |
| 2 | Theorem 2: σ a symmetry of the free walk; G^B = G^(σB) on the line, sides 3 to 10; the excursion form for (1, 0) → d* (sides 5 to 16, 25n steps) and for every pair of line points, h and v ends (sides 5 to 9, 12n steps) | pass |
| 3 | Theorem 3: the determinant at random points of GF(2^10), sides 2 to 16; the period-4 eigenvector at 2, 4, 8, 16; rank A(t) = 2n − 2 and the kernel dimensions of (A(t) − t − t⁻¹)^j equal to j up to 2n − 2 at 4 and 8; s₋ = w²C(w⁴) | pass |
| 4 | Lemma 4 for 0 ≤ s ≤ 2n − 3, on random vectors, sides 3 to 20 | pass |
| 5 | Computed at 4 to 64: A^P, P = e(2n − 1) = 28, 120, 496, 1,008, 4,064, fixes the corner's orbit and c*'s (P is a period, not always the least); A1; the corner reads every contact but the predicted d*'s; A2; the far-corner delay | pass |
| S | The stress test (`research/REACH-HALVES-20261110-001/stress_test.py`): A2, the never-read set and the far-corner delay at 64 and 128; at 8, 16 and 32 the first times the corner reads d* in the quadrant and the half-strips, and their return series below w^1200 (the Catalan series C(w⁴)) | pass (6.9 s) |

## Nonclaims

- **A1 is not proved** at any power of two beyond the computed sides 8 to 128; Theorem 1 reduces it to (★), which is computed, not
  proved.
- **A2 and the far-corner delay are computed laws**, to side 128.
- **Nothing here is a length or a distance**; the square grid only, cut open both ways; rule-60 rings with law-(12, 12) contacts
  (A30, A32, A37, A38).
