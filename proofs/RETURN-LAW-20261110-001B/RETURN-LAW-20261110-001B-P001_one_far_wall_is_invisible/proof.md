# One far wall is invisible at even sides

Status: **Obstructed** under the frozen criterion. The registered target B1 is not proved: by ticket A's Theorem 3 it is the identity
(★1D) on the path of n − 1 vertices, which is computed, and B1 itself is computed at every even side 2 to 64 below w^2400 (to 80
below w^3200 in the stress test). Proposition 6 is proved by hand, with the finite checks of `check.py`. Read by an independent
referee pass on 2026-11-10, whose findings are folded in (see the decision note).

Ticket `RETURN-LAW-20261110-001B`, epic `RETURN-LAW-20261110-001` (pre-registered in commit a5769c7a7).

## Standard statement

The walk, the regions, c = (0, 1), r(w), C(z) and the v-grid are as in `RETURN-LAW-20261110-001A`. The half-strips are
H_Y = [0, ∞) × [0, N] and H_X = [0, N] × [0, ∞), N = 2n − 2.

**Targets** (registered). B1: at every even n ≥ 2 the corner's return series in either half-strip is the quadrant's, C(w⁴), over
GF(2). B2: at every odd n ≥ 3 they differ, first at time 4n.

**Proposition 6.** (a) The two half-strips have the same corner return series at every side. (b) On the strip [0, N] × Z, in the
Fourier variable t of Y, the vector ψ_t = (t, t + t⁻¹, t⁻¹, 0, t, t + t⁻¹, t⁻¹, 0, …) on X = 0, …, N is an eigenvector with eigenvalue
λ = t + t⁻¹ exactly when n is even, and the same pattern on X ≥ 0 is one for the half-plane at every n. (c) On that branch the
two-site transfer matrix 𝕄 of `REACH-HALVES-20261110-001A`'s Theorem 3 satisfies 𝕄² = I: four more columns change nothing there.

**The reduction.** By ticket A's Theorem 3 with the row path on n − 1 vertices, the corner series of H_Y is
r(w) = [(I + sD + s²f(P_(n−1)))^(−1)]_(0,0) at s = w² over GF(2); so B1 at n is (★1D) on P_(n−1), and B2 says that identity fails on
paths with an even number of vertices.

**Computed (exact; `check.py`).**
- **B1 at every even side 2 to 64 below w^2400**: H_X's corner series is C(w⁴). **B2 at every odd side 3 to 63**: it first differs
  from C(w⁴) at time 4n. The stress test adds the sides 65 to 80, below w^3200.
- **The bottom wall is needed.** Without it, on the strip [0, N] × Z against the half-plane [0, ∞) × Z, the returns of a contact
  (0, Y₀) on the left wall, far from any other wall, first differ at time 4n at every side 2 to 40, even or odd. So the invisibility of the far wall at even sides is a joint effect of the
  far wall and the bottom wall, not of the strip's spectrum alone.

**What resists.** (★1D) on the paths with an odd number of vertices, or any direct cancellation, mod 2, of the walks that reach the far
wall. Proposition 6 identifies a branch whose decaying root gives the computed quadrant series: (t₀/w)² = C(w⁴), t₀ = wC(w²) the
decaying root of t + t⁻¹ = 1/w, the free walk in Y; on that branch four extra columns act as the identity (𝕄² = I). But the computation without a
bottom wall shows the far wall is seen at 4n at every side once the bottom wall is removed, so the branch alone does not carry B1, and
no argument isolating the bottom wall's part was found.

## Nearest known result

The same as ticket A's. Proposition 6(b) restates the period-4 eigenvector found in `REACH-HALVES-20261110-001A` (Theorem 3), where
it was stated at the powers of two; (c) is Cayley–Hamilton on that theorem's 𝕄. New as far as found; not a priority claim.

## Proof of Proposition 6

(a) The diagonal reflection D(X, Y) = (Y, X) carries H_X onto H_Y and the walk to its transpose, by the same local computation as in
the box (`FULL-REACH-PROOF-20261108-001A`, Theorem 2): A^k_(H_X)[p, q] = A^k_(H_Y)[Dq, Dp]. So the corner series of H_X is the
series of returns of D(c) = (1, 0) in H_Y. In any region containing the corner's funnel, (0, 1) reads only (1, 0) and is read only by
(1, 2), and (1, 0) is read only by (0, 1) (`REACH-HALVES-20261110-001A`, Theorem 1(a)); both return series are therefore
1 + w² G_((1,0),(1,2))(w).

(b) For a row vector x(X, Y) = ψ(X) t^Y on the strip, the contact (X′, Y′) is read from X′ − 1 and from X′ + 1, and the bond
(j, j + 1) moves Y by +1 when j is odd and by −1 when j is even, whichever way it is crossed. So (xA)(X′, Y′) = t^(Y′)(tψ(X′ − 1) +
t⁻¹ψ(X′ + 1)) for odd X′ and t^(Y′)(t⁻¹ψ(X′ − 1) + tψ(X′ + 1)) for even X′, with ψ(−1) = ψ(N + 1) = 0. With λ = t + t⁻¹ and the
pattern of period 4, the four residues of X′ give: at 0, t⁻¹·0 + t(t + t⁻¹) = t² + 1 = λt; at 1, t·t + t⁻¹·t⁻¹ = λ(t + t⁻¹); at 2,
t⁻¹(t + t⁻¹) + t·0 = λt⁻¹; at 3, t·t⁻¹ + t⁻¹·t = 0 = λ·0. So the pattern solves the equation wherever the values it needs past the
ends agree with the walls' zeros. At the left end the pattern's value at −1 (residue 3) is 0. At the right end its value at N + 1 is 0
exactly when N + 1 ≡ 3 (mod 4), that is n even; for odd n, N ≡ 0 and the equation at X′ = N would need ψ(N + 1) = t + t⁻¹, so it
fails there. On X ≥ 0 only the left end is present.

(c) 𝕄 = [[t², λ], [λt², λ² + t⁻²]] has det 𝕄 = 1 and tr 𝕄 = (λ + t + t⁻¹)², which vanishes on the branch; by Cayley–Hamilton over
GF(2), 𝕄² = tr 𝕄 · 𝕄 + det 𝕄 · I = I. ∎

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependencies bound by hash | pass |
| 1 | Proposition 6(a): the two half-strips have the same corner series below w^1600, sides 2 to 30 | pass |
| 2 | Proposition 6(b), (c): the eigenvector exactly at the even sides 2 to 40 (exact, over GF(2)[t, t⁻¹]); 𝕄² = I on the branch | pass |
| 3 | Computed: B1 at the even sides 2 to 64 below w^2400; B2 (first difference at 4n) at the odd sides 3 to 63 | pass |
| 4 | Computed: without the bottom wall the far wall is seen first at 4n, sides 2 to 40 | pass |

## Nonclaims

- **B1 and B2 are not proved**; both are computed. The reduction to (★1D) is ticket A's Theorem 3.
- Proposition 6 names a branch whose decaying root matches the computed quadrant series; it does not show that the quadrant's or the
  half-strip's series is carried by it.
