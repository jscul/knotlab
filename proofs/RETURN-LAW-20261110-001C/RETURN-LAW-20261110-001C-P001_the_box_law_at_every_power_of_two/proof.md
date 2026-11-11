# The box law at every power of two

Status: **Obstructed** under the frozen criterion. The registered target C1 is not proved for every m. It is reduced, by proved steps,
to a finite identity at each side (Theorem 7 with Proposition 8), and it is now **proved at each power of two from 4 to 512 by exact
computation**: the corner's return series agrees with 1/(1 + L(w⁴)) on as many terms as the sum of the orders of the two linear
recurrences they obey, which forces equality (256 in `check.py`, 512 in the stress test). The lemma that would finish C1 is the
identity of Proposition 8; Theorem 7 makes it equivalent to C1 at each n, so that exact check checks it at every power of two from 4 to
512. Proposition 9 restates the law: read every four steps, the corner of the box returns as the loop end of a looped path of n sites
does. Read by an independent referee pass on 2026-11-10, whose findings are folded in (see the decision note).

Ticket `RETURN-LAW-20261110-001C`, epic `RETURN-LAW-20261110-001` (pre-registered in commit a5769c7a7).

## Standard statement

The walk, the box [0, N]², N = 2n − 2, c = (0, 1), r(w), C(z) and the v-grid are as in `RETURN-LAW-20261110-001A` (Lemma 1: columns
a = 0, …, n − 1, rows b = 0, …, n − 2, moves E, W, N, S, no N from column 0, no S from column n − 1). L(z) = z + z² + z⁴ + ⋯ + z^n is
the trace polynomial of GF(2n) when n = 2^m, and C_j(x) = Σ_(i≤j) x^(2^i − 1) is the Catalan series cut after j + 1 terms. P_k is the
adjacency matrix of the path on k vertices and P_k^∘ the same path with a loop at one end.

**Targets** (registered). C1: at every n = 2^m ≥ 4, r(w) = 1/(1 + L(w⁴)) over GF(2). C2: 1/r_(2n)(w) = 1/r_n(w²) + w⁴. C3: at every
side n ≥ 3 the box's first-return series is the quadrant's plus w^(8n) plus higher terms.

**Theorem 7 (the two-sided column decomposition).** For the box at side n ≥ 2, let V be the space of the n − 1 rows, P = P_(n−1) its
path, D and Dᵀ its lowering and raising parts (time order), and N_XY(h) the number of walks of length h on the column path [0, n − 1]
from end X to end Y (X, Y ∈ {L, R}, the columns 0 and n − 1) that stay strictly inside in between. On V_L ⊕ V_R put

  𝒦_n = I − [[sD + S_LL, S_LR], [S_RL, sDᵀ + S_RR]],  S_XY = Σ_h N_XY(h) s^h (I − sP)^(−(h−1)).

Then over the integers R(s) = Σ_ℓ M^ℓ[c, c] s^ℓ = [𝒦_n^(−1)]_((L,0),(L,0)), and r(w) = R(w²).

**Proposition 8 (at a power of two).** Over GF(2) and at n = 2^m ≥ 4: det(I + xP_(n−1)) = 1 and P_(n−1)^(n−1) = 0;
det(I + xP_(n−2)) = C_(m−1)(x²); det(I + xP_(n−3)) = C_(m−2)(x⁴). Hence Σ_h N_LL(h) x^h = x² C_(m−2)(x⁴)/C_(m−1)(x²),
Σ_h N_LR(h) x^h = x^(n−1)/C_(m−1)(x²), and S_XY = (I + sP) 𝒩_XY(Π) with Π = s(I + sP)^(−1) = Σ_(k<n−1) s^(k+1) P^k, a polynomial in s.
So C1 at n is the identity [𝒦_n^(−1)]_(0,0) = 1/(1 + L(s²)) between explicit 2(n − 1) × 2(n − 1) matrices over GF(2)(s).

**Proposition 9 (the looped path).** Over GF(2) and at n = 2^m: det(I + zP_n^∘) = 1 + L(z), and det(I + zP_(n−1)) = 1. So
1/(1 + L(z)) is the return series at the loop end of P_n^∘, and C1 says: read every four steps of the walk, the corner of the box
returns exactly as the loop end of a looped path of n sites does. In the quadrant the path is infinite (ticket A, Proposition 5); the
box cuts it at n sites, which in time folds the Catalan series modulo 2n − 1.

**Computed (exact; `check.py`, and the stress test where marked).**
- **C1 at every power of two from 4 to 256, and 512 in the stress test, exactly.** The corner's sequence a_k = A^k[c, c] obeys the
  linear recurrence of A's minimal polynomial, of order at most 2n(n − 1) (the number of contacts), and the sequence of
  1/(1 + L(w⁴)) obeys one of order 4n; their difference obeys a recurrence of order at most 2n(n − 1) + 4n, and it vanishes on that
  many first terms, so it vanishes. This is a proof of C1 at each of these sides, by computation; it is not a proof for every m.
- **C2** at n needs C1 at n and at 2n (1 + L_(2n)(z) = 1 + z + L_n(z²)), so it holds from 4 to 8, 8 to 16, …, 256 to 512; it fails
  from 2 to 4, 3 to 6, 5 to 10 and 6 to 12, first at w^16, w^64, w^96 and w^128.
- **C3 at every side 3 to 64** (to 128 in the stress test): the box's corner series first differs from the quadrant's C(w⁴) at time
  8n.
- **The four-corner formula** Σ_i G_(c, ρ^i c) ρ^i = C_m(w⁴)/(1 + w^(2n−1)ρ) + w^(2n−3)ρ³, ρ the quarter turn, below w^1200 at 4 to 64
  (128 below w^2000 in the stress test).
- **The corner's orbit** has period 2^(⌊m/2⌋+1)(2n − 1) at every n = 2^m from 4 to 128: e_c A^P = e_c first at P = 28, 60, 248, 504,
  2032, 4080.
- Theorem 7 against the walk: over GF(2) to s^60 at every side 2 to 12 (13 to 16 to s^40 in the stress test), over the integers to
  s^18 at 3, 4 and 5.

**What resists.** The identity of Proposition 8 for every m. A proof by doubling (C2) would need a map from the block operator at n to
the one at 2n; the square of the walk is not a renormalized copy of the walk (ticket A: M² carries loops on the axes and an attached
plain quadrant), and no such map was found. Nor does the looped path sit inside the walk as a subspace. At n = 2^m,
(1 + L(z)) C_m(z) = 1 + z^(2n−1), so (P_n^∘)^(2n−1) = I, and an A⁴-invariant subspace through e_c on which A⁴ acted as P_n^∘ would force
e_c A^(4(2n−1)) = e_c; that fails at 16 to 128, where the corner's orbit has period 2^(⌊m/2⌋+1)(2n − 1) (computed). The looped path is a
quotient instead: wherever C1 holds, the corner's A⁴-cyclic space modulo the vectors whose c-coordinate vanishes along their whole orbit
is a minimal realization of the corner's sequence, so by the uniqueness of minimal realizations it is similar to P_n^∘, with e_c going
to the loop end. That quotient exists at every power of two from 4 to 512; an explicit description of it is what is missing.

**Corollary 10 (interior targets, for B137).** For an inner column a (1 ≤ a ≤ n − 2) and any row b, the walks from c to the v contact
v(a, b) are counted, over GF(2), by Σ_(X, b′) [𝒦_n^(−1)]_((L,0),(X,b′)) [𝒩_(X→a)(Π)]_(b′,b), where 𝒩_(X→a)(x) = Σ_h N_(X→a)(h) x^h counts
the walks on the column path that leave the end X and stay strictly inside until they end at column a after h steps. So the count that
decides the failure of full reach (`REACH-HALVES-20261110-001A`, the walks from c to c* and to (n + 4, n + 1)) and the return law are
identities in the same 2(n − 1)-dimensional operators: the return law needs the corner's entry of 𝒦_n^(−1), the count needs the
corner's whole row. The reflection route registered as the first step (ticket A, Theorem 2) describes the surviving walks but does not
count them, so it gives no handle by itself.

## Nearest known result

- **Ingredients.** Chebyshev polynomials and continuants over GF(2) (the nilpotency of rule 90 on 2^m − 1 sites: Martin, Odlyzko and
  Wolfram 1984; Sutner's σ-automata); the characteristic polynomial of the looped path, U_n − U_(n−1) in the usual normalisation
  (a loop of weight +1), whose roots are −2 cos(2πj/(2n + 1)), j = 1, …, n, a product of minimal polynomials of −(ζ + ζ⁻¹) for roots of
  unity ζ of order dividing 2n + 1; the trace of a finite field and linearized polynomials (Lidl and Niederreiter, chapters 2 and 3).
- **Classification.** New as far as found. A bounded web search on 2026-11-10 (Catalan parity, trace polynomial, Chebyshev
  polynomials over GF(2), looped path) found no statement that det(I + zP_(2^m)^∘) is 1 + z + z² + z⁴ + ⋯ + z^(2^m) over GF(2), though
  it follows in a few lines from classical identities, and nothing on a lattice walk whose corner return series is 1/(1 + Tr) or the
  Catalan series folded modulo 2n − 1. Not a priority claim.

## Proof of Theorem 7

By Lemma 1 of ticket A, on column 0 only S (for b ≥ 1) and E are possible, and on column n − 1 only N (for b ≤ n − 3) and W: N is
banned on column 0 and W leaves the box there, S is banned on column n − 1 and E leaves the box there. On the inner columns
1, …, n − 2 there is no ban. Cut a walk from c at its visits to the two end columns. While on an end column the walk makes row steps,
sD on column 0 and sDᵀ on column n − 1. Between two consecutive end visits the column coordinate makes a walk of some length h ≥ 1 from
one end to an end that stays strictly inside in between (N_XY(h) choices), and the row coordinate makes a free walk on the row path,
whose steps sit in the h − 1 gaps between the h column steps, with repetition: Σ_m C(m + h − 2, m) s^m P^m = (I − sP)^(−(h−1)). With
s per column step this is S_XY. A walk from c back to c is a finite sequence of these pieces from (L, 0) to (L, 0), counted by the
(L, 0) entry of Σ_k (I − 𝒦_n)^k = 𝒦_n^(−1). ∎

## Proof of Corollary 10

Cut a walk from c to v(a, b) at its last visit to an end column, at row b′ of column X. Up to that visit it is a walk from (L, 0) to
(X, b′) of the kind Theorem 7 counts. After it, the column coordinate leaves X and stays strictly inside until the walk ends, at column a
after h column steps (N_(X→a)(h) choices), and the row coordinate makes a free walk from b′ to b whose steps sit in the h gaps after the
h column steps, with repetition: Σ_m C(m + h − 1, m) s^m P^m = (I − sP)^(−h). With s per column step the final segment is
Σ_h N_(X→a)(h) s^h (I − sP)^(−h) = 𝒩_(X→a)(Π) (over GF(2), Π = s(I + sP)^(−1)). There is no (I + sP) factor, unlike S_XY, because the walk
does not return to an end column. ∎

## Proof of Proposition 8

Write D_k(x) = det(I + xP_k) over GF(2). Expanding along an end, D_k = D_(k−1) + x²D_(k−2), D_0 = D_1 = 1, so D_k(x) = x^k U_k(1/x)
with U_0 = 1, U_1 = y, U_(k+1) = yU_k + U_(k−1) (the characteristic polynomials of the paths over GF(2)). The continuants satisfy
U_(j+k) = U_jU_k + U_(j−1)U_(k−1), so U_(2k) = U_k² + U_(k−1)² and U_(2k+1) = U_k(U_(k+1) + U_(k−1)) = yU_k². By induction on m,
U_(2^m−1) = y^(2^m−1), so D_(n−1) = 1 and, by Cayley–Hamilton, P_(n−1)^(n−1) = 0; and U_(2^m−2) = y^(2^m−2) + U_(2^(m−1)−2)², which gives
U_(2^m−2)(y) = y^(2^m) T_m(1/y)² with T_m(z) = Σ_(j<m) z^(2^j) (base U_0 = 1), hence D_(n−2)(x) = (T_m(x)/x)² = C_(m−1)(x²).
Next U_(2^m−3) = yU_(2^(m−1)−2)², so D_(n−3)(x) = x^(n−4) U_(2^(m−1)−2)(1/x)² = (T_(m−1)(x)/x)⁴ = C_(m−2)(x⁴). The walks counted by
N_LL(h) step from column 0 to 1, walk on the inner path P_(n−2) from its first vertex back to it, and step back, so
Σ_h N_LL(h) x^h = x² [(I + xP_(n−2))^(−1)]_(first,first) = x² D_(n−3)/D_(n−2); likewise N_LR uses the entry between the two ends of the
inner path, which for a tridiagonal matrix is the product of the n − 3 off-diagonal entries divided by the determinant, x^(n−3)/D_(n−2).
Finally s^h (I + sP)^(−(h−1)) = (I + sP) Π^h, and Π = s Σ_(k<n−1) (sP)^k because P^(n−1) = 0. ∎

## Proof of Proposition 9

Expanding det(I + zP_k^∘) along the looped end, E_k = (1 + z)D_(k−1) + z²D_(k−2) = D_k + zD_(k−1). At n = 2^m, D_(n−1) = 1 by
Proposition 8. Put d_m = D_(2^m); from U_(2^m) = U_(2^(m−1))² + U_(2^(m−1)−1)² = U_(2^(m−1))² + y^(2^m − 2) one gets
d_m(z) = d_(m−1)(z)² + z² = d_(m−1)(z²) + z², with d_0 = D_1 = 1, so d_m(z) = 1 + z² + z⁴ + ⋯ + z^(2^m). Hence
E_n = d_m + z = 1 + z + z² + z⁴ + ⋯ + z^n = 1 + L(z). The return series at the loop end of P_n^∘ is the cofactor of that site over the
determinant, det(I + zP_(n−1))/E_n = 1/(1 + L(z)). ∎

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependencies bound by hash | pass |
| 1 | Theorem 7 against the walk: over GF(2) to s^60 at the sides 2 to 12, over the integers (the walk A itself) to s^18 at 3, 4, 5 | pass |
| 2 | Proposition 8: the three determinants for m = 2 to 10, nilpotency for m ≤ 5, the first-passage series for n = 4 to 32 below x^80 | pass |
| 3 | Proposition 9 for m = 1 to 12 | pass |
| 4 | Computed: C1 exactly at 4 to 256; C2's failures at 2, 3, 5, 6; C3 at 3 to 64; the four-corner formula at 4 to 64 below w^1200; the orbit's period at 4 to 128 | pass |
| 5 | Corollary 10 against the walk: every inner target at 4, 5, 6 and the two targets of B137 at 8 and 16, each target separately (below s^40) | pass |

## Nonclaims

- **C1 is not proved for every m**; it is proved at each power of two from 4 to 512 by exact computation. C2 and C3 are computed.
- Proposition 9 is a restatement of C1, not evidence for it.
- Corollary 10 reduces the count of B137 to the same operators; it does not evaluate it.
