# The quadrant law: the corner returns at the Catalan times

Status: **Obstructed** under the frozen criterion. The registered target A1 is not proved. It is reduced, by proved steps, to one
identity on the half-line, (★1D) below, which is computed; A1 itself is computed below w^4000. Lemma 1, Theorems 2 and 3, Lemma 4
and Proposition 5 are proved by hand, with the finite checks of `check.py`; so are the kernel equation and the doubling equivalence
under "What resists" and "Computed". Read by an independent referee pass on 2026-11-10, whose findings are folded in (see the decision
note).

Ticket `RETURN-LAW-20261110-001A`, epic `RETURN-LAW-20261110-001` (pre-registered in commit a5769c7a7).

## Standard statement

- **The walk.** As in `REACH-HALVES-20261110-001A`: the contacts are the points (X, Y) with X + Y odd; an h (X odd) reads
  (X ± 1, Y ± 1) with equal signs, a v (X even) reads (X ± 1, Y ∓ 1), reads leaving the region die, and A[c, d] = 1 when c reads d,
  over GF(2). The regions are the box [0, N]², N = 2n − 2, the quadrant [0, ∞)², and the half-strips [0, ∞) × [0, N] and
  [0, N] × [0, ∞). The corner contact is c = (0, 1) and r(w) = Σ_k A^k[c, c] w^k is its return series.
- **Series.** C(z) = Σ_j z^(2^j − 1) is the Catalan series mod 2 (C_k is odd exactly when k = 2^j − 1); it is the unique series with
  C = 1 + zC² over GF(2). L_∞(z) = Σ_j z^(2^j) = zC(z), so 1/C(z) = 1 + L_∞(z).
- **The targets** (registered). A1: in the quadrant r(w) = C(w⁴) over GF(2), so the first returns are odd exactly at the times
  4·2^j. A2: over the integers the corner returns of length 4k are C_k² in number.

**Lemma 1 (the v-grid).** Write v(a, b) for the v contact (2a, 2b + 1). On the v contacts, A² is the walk to the four neighbours
E = (a + 1, b), W = (a − 1, b), N = (a, b + 1), S = (a, b − 1), as far as they stay in the region, with two bans: no N from column 0,
and, when X is bounded (the box and [0, N] × [0, ∞)), no S from the last column a = n − 1. The corner is c = v(0, 0), returns occur
only at even times, and r(w) = R(w²) with R(s) = Σ_ℓ M^ℓ[c, c] s^ℓ, M the v-grid walk.

**Theorem 2 (the reflection through the corner).** σ′(X, Y) = (Y − 1, X + 1), the reflection in the line X − Y = −1 on which c lies,
is a symmetry of the walk in the plane. Mod 2, the returns of c in the quadrant are as many as those whose every excursion off the line
lies on the side X − Y ≥ 1 and touches the bottom wall Y = 0; in the box, as many as those whose every excursion lies on that side and
touches Y = 0 or the right wall X = N.

**Theorem 3 (the column decomposition).** Let the region be the quadrant or the half-strip [0, ∞) × [0, N] (any n ≥ 2). Let P be the
adjacency matrix of the path on its rows (b ≥ 0, or 0 ≤ b ≤ n − 2), D its lowering part (D[b, b − 1] = 1), matrices read from row to
row in time order, and

  f(P) = Σ_(h≥0) C_h s^(2h) (I − sP)^(−(2h+1)).

Then over the integers R(s) = [(I − sD − s²f(P))^(−1)]_(0,0). Over GF(2), f(P) = (I + sP)^(−1) C(s²(I + sP)^(−2)).

**Corollary.** A1 holds exactly when

  (★1D) [(I + sD + s²f(P))^(−1)]_(0,0) = C(s²) over GF(2), with P the path on the half-line;

and, at a side n, the half-strip law B1 of ticket B holds for [0, ∞) × [0, N] exactly when (★1D) holds with P the path on n − 1
vertices, and then for [0, N] × [0, ∞) too, by ticket B's Proposition 6(a).

**Lemma 4 (the plain quadrant is even).** For the half-line, f(P)[0, 0] = Σ_t s^(2t) Σ_h C(2t, 2h) C_h C_(t−h) = Σ_t C_t C_(t+1) s^(2t),
and over GF(2) f(P)[0, 0] = 1. The same decomposition with the ban lifted gives [(I − sP − s²f(P))^(−1)]_(0,0) = f(P)[0, 0]: the plain
walk in the quarter plane has an even number of returning walks of each positive length. (★1D) says that forbidding the north steps
on column 0, the single term sDᵀ, turns that 1 into C(s²).

**Proposition 5 (the looped half-line).** Over GF(2) the return series at the loop of the looped half-line (sites 0, 1, 2, …, with
an edge between neighbours and a loop at 0) is C(z). So A1 reads: every four steps of the walk, the corner of the quadrant returns
exactly as the loop end of a looped half-line does.

**Computed (exact; `check.py`).**
- **A1 below w^4000**: the quadrant's corner series is C(w⁴).
- **A2 for k ≤ 24**: the corner returns of length 4k are C_k² in number (k = 1, …, 24). Equivalently (Lemma 1), the simple walks in
  the quarter plane that never step north from the y-axis have C_k² excursions of length 2k.
- **The corner's row and column pair up.** For E = (I + sD + s²f(P))^(−1) on the half-line, E[2k, 0] = t₀E[2k − 1, 0] and
  E[0, 2k] = t₀E[0, 2k − 1] for k = 1, …, 8 below s^44, where t₀ = sC(s²) is the decaying root of t + 1/t = 1/s. The same relation
  fails in column 1 (E[2k, 1] ≠ t₀E[2k − 1, 1]), and so does the shifted one, E[2k + 1, 0] ≠ t₀E[2k, 0] (k = 1, 2, 3).
- **Doubling.** Over GF(2), R(s) = [(I + s²M²)^(−1)]_(c,c) (the v-grid is bipartite). M² is the v-grid walk at half scale on the
  even-even sites, plus a loop at every site of the two axes, plus a copy of the plain quadrant on the odd-odd sites joined to the left
  column, from (0, 2β) to (1, 2β + 1) and from (1, 2β + 1) to (0, 2β + 2) (computed on the sites up to 11; a finite case analysis of the
  sixteen two-step words). Eliminating that copy (its left-column resolvent is f(P), by the identity (I − sP − s²f(P))^(−1) = f(P) of
  Lemma 4) and decomposing the even-even sites as in Theorem 3, where the axis loops add I on column 0 and E₀, the projection on row 0,
  to the row walk inside excursions, gives [(I + uM²)^(−1)]_(c,c) = [(I + uD + uI + u²f(P + E₀) + u²f(P)Dᵀ)^(−1)]_(0,0) with u = s².
  So A1 is equivalent to that entry being 1 + uC(u²) (proved), which is computed below u^40. It is an identity of the same kind as
  (★1D).
- Theorem 3 against the walk: over GF(2) to s^60 at the half-strips 2 to 12 and to s^48 in the quadrant, over the integers, against
  the walk A itself, to s^22 at the half-strips 2 to 6.

**What resists.** (★1D). It is a kernel equation in disguise (proved below, and checked below s^23). With Y the small root of
Y + 1/Y = 1/s + z + 1/z and a(z) = Σ_b E[b, 0] z^b, the column decomposition gives

  s(z + Y) a(z) + s(1/z + Y) a(1/z) = (z + 1/z) Y over GF(2),

which forces a(z) = (1 + zY)(1 + Σ(z)/z) with Σ(z) = Σ(1/z), and (★1D) is a(0) = C(s²). By the diagonal reflection D, E[b, 0] is
also the series of the walks from (1, 0) to (2b + 1, 0) on the bottom row (checked for b < 6). The equation fixes a only together with
the condition that this product have no negative powers of z, and no way to impose that condition in closed form was found; an
exploratory search found no algebraic relation of degree at most 4 (coefficients of degree at most 8 in s and 4 in z) for the boundary
series (decision note). The reflection of Theorem 2 leaves 1, 2, 7, 34, 206, 1458 surviving walks at k = 1, …, 6 (computed), with no
visible closed form.

## Nearest known result

- **Ingredients.** The kernel method for walks in the quarter plane (Bousquet-Mélou and Mishna 2010); the simple walk's excursions
  C_t C_(t+1) (Guy, Krattenthaler and Sagan 1992); the diagonal walk's excursions C_t², a product of two Dyck paths; walks whose
  steps or weights change on the boundary (Beaton, Owczarek and Rechnitzer, arXiv 1807.08853); the parity of Catalan numbers.
- **Classification.** New as far as found. A bounded web search on 2026-11-10 found no study of this boundary rule (no north step
  from the y-axis, equivalently no west step along the x-axis) or of its excursion count C_k², which equals the diagonal walk's with no
  bijection known to us; and no study of a two-dimensional walk whose return series is the Catalan series mod 2 (on the half-line
  Dyck paths give C(z²), and the looped half-line gives C(z), Proposition 5). Not a priority claim.

## Proof of Lemma 1

The v at (2a, 2b + 1) reads h₁ = (2a + 1, 2b) and h₂ = (2a − 1, 2b + 2). h₁ reads (2a + 2, 2b + 1) = v(a + 1, b) and
(2a, 2b − 1) = v(a, b − 1); h₂ reads (2a, 2b + 3) = v(a, b + 1) and (2a − 2, 2b + 1) = v(a − 1, b). So E and S pass through h₁, N and W
through h₂, each target once. h₂ lies in the region exactly when a ≥ 1 (its Y = 2b + 2 is always in range: 2b + 1 ≤ N and N is
even), so N and W need a ≥ 1: for W this is the region's own wall, for N it is a ban on column 0. h₁ lies in the region
exactly when 2a + 1 ≤ N if X is bounded, that is a ≤ n − 2, so E and S need a ≤ n − 2: for E this is the wall, for S a ban on the
last column. Walks of odd length end at h's, so returns to c occur at even times. ∎

## Proof of Theorem 2

(a) σ′ keeps X + Y and sends X to Y − 1 ≡ X (mod 2), so it keeps the type. An h at (X, Y) reads (X ± 1, Y ± 1), with images
(Y, X + 2) and (Y − 2, X) = σ′(X, Y) ± (1, 1), the reads of the h at σ′(X, Y); a v at (X, Y) reads (X + 1, Y − 1) and (X − 1, Y + 1),
with images (Y − 2, X + 2) and (Y, X) = σ′(X, Y) ± (−1, 1), the reads of the v at σ′(X, Y).

(b) In u = (X + Y − 1)/2, v = (X − Y − 1)/2 the line is v = −1, σ′ is (u, v) ↦ (u, −2 − v), an h moves u and a v moves v. Cut a
return at its visits to the line into steps along it and **excursions**, maximal stretches with v ≠ −1, each on one side. σ′ fixes the
line pointwise, so reflecting one excursion gives a walk of the plane with the same ends and length. A point of the box with
X − Y ≤ −3 goes to (Y − 1, X + 1), and Y ≥ X + 3 and X ≤ Y − 3 ≤ N − 3 put that image in the box: excursions on that side are always
reflectable. A point with X − Y ≥ 1 goes into the box exactly when Y ≥ 1 and X ≤ N − 1: an excursion on that side is reflectable
exactly when it avoids Y = 0 and X = N (in the quadrant, Y = 0 only). Reflecting the first reflectable excursion of a walk keeps it the
first reflectable one, so it is an involution without fixed points on the walks that have one. The walks left are those whose every
excursion lies on the side X − Y ≥ 1 and touches Y = 0 (or X = N). ∎

## Proof of Theorem 3

By Lemma 1 the v-grid of these regions has columns a ≥ 0 and rows 0 ≤ b < B (B = ∞ or n − 1), with moves E always, W and N for
a ≥ 1 (N also needs b + 1 < B), and S for b ≥ 1; there is no last column. Cut a walk from c = v(0, 0) at its visits to column 0. On
column 0 only S (for b ≥ 1) and E are possible: N is banned there and W leaves the region. An E step from (0, b) opens an
**excursion**: the walk stays in the columns a ≥ 1 until a W step from column 1 returns it to column 0, at some row b′. In the columns
a ≥ 1 no ban applies, so during an excursion the column coordinate and the row coordinate move independently: the column coordinate
makes E, then a path from 1 back to 1 that stays at or above 1, of some length 2h (C_h choices), then W; the row coordinate makes
some walk of m steps on the row path from b to b′ ((P^m)[b, b′] choices); and the m row steps sit in the 2h + 1 gaps between the
2h + 2 column steps, with repetition, in C(m + 2h, m) ways. With s per step, the excursions from row b to row b′ are counted by

  Σ_(h,m) C_h C(m + 2h, m) s^(2h + 2 + m) (P^m)[b, b′] = s² Σ_h C_h s^(2h) [(I − sP)^(−(2h+1))][b, b′] = s² f(P)[b, b′],

since Σ_m C(m + r, m) y^m = (1 − y)^(−(r+1)). A walk from c back to c is then any finite sequence of S steps (the matrix sD) and
excursions (s²f(P)) leading from row 0 to row 0, and these are counted by Σ_k (sD + s²f(P))^k [0, 0] = [(I − sD − s²f(P))^(−1)]_(0,0).
Mod 2, Σ_h C_h x^h (1 − y)^(−(2h+1)) = (1 − y)^(−1) C(x/(1 − y)²) with C reduced mod 2 gives the second form. The corollary is
Lemma 1 (r(w) = R(w²)) with A1 read as R(s) = C(s²); for ticket B, the half-strip [0, ∞) × [0, N] has the row path on n − 1 vertices. ∎

## Proof of Lemma 4

[(I − sP)^(−(2h+1))]_(0,0) = Σ_m C(m + 2h, m) s^m (P^m)[0, 0] and (P^m)[0, 0] = C_(m/2) on the half-line (m even), so
f(P)[0, 0] = Σ_(h,v) C_h C_v C(2v + 2h, 2v) s^(2h + 2v), which is the stated sum with t = h + v; the identity
Σ_h C(2t, 2h) C_h C_(t−h) = C_t C_(t+1) is the classical count of the simple walk's excursions in the quarter plane (Guy, Krattenthaler
and Sagan), checked for t ≤ 200. Mod 2, by Lucas's theorem C(2t, 2h) ≡ C(t, h), and the terms h and t − h of the sum are equal, so they
cancel in pairs; for even t the middle term carries C(t, t/2), which is even for t ≥ 2. So only t = 0 survives. With the ban lifted,
column 0 also allows N, the walk on column 0 is a sequence of sP steps and excursions, and its (0, 0) entry is
[(I − sP − s²f(P))^(−1)]_(0,0); f solves (1 − sx) f = 1 + s² f², so (I − sP − s²f(P))^(−1) = f(P). ∎

## Proof of Proposition 5

At the loop the walk either stays (the loop) or steps to site 1, makes an excursion on the sites ≥ 1, and returns; the excursions
from site 1 back to site 1 are counted by C(z²) mod 2 (Dyck paths). So the return series is 1/(1 + z + z²C(z²)) over GF(2), and
since z + z²C(z²) = z + L_∞(z²) = L_∞(z), it is 1/(1 + L_∞(z)) = C(z). ∎

## Proof of the kernel equation

Let y be the column E e₀, so (I + sD + s²f(P))y = e₀ over GF(2), with (Dy)(b) = y(b − 1) and y(−1) = 0. On the half-line, by the
reflection principle for the path with its end at −1, P^k[b, b′] is the number of walks of the line from b to b′ plus the number from b
to −2 − b′ (mod 2), so any series g(P) has g(P)[b, b′] = ĝ_(b′−b) + ĝ_(b+b′+2), ĝ_k the coefficient of ζ^k in g(ζ + ζ⁻¹). For f,
f(ζ + ζ⁻¹) = φ(ζ) := Y/s, because f solves s²f² + (1 + sx)f + 1 = 0 and Y = sf then solves Y² + (1/s + x)Y + 1 = 0. Put
â(z) = a(z) + z⁻²a(1/z), whose coefficients satisfy â_m = â_(−2−m) and â_(−1) = 0. The product φâ has the same symmetry (φ is
symmetric under z ↔ 1/z) and its z⁻¹ coefficient vanishes (its terms pair off), so it is determined by its part with nonnegative
powers, which is s⁻² times the series of s²f(P)y. The equation for y therefore reads s²φâ = (1 + (1 + sz)a(z)) + z⁻²(1 + (1 + s/z)a(1/z)),
that is (1 + sz + sY)a(z) + z⁻²(1 + s/z + sY)a(1/z) = 1 + z⁻². From Y + 1/Y = 1/s + z + 1/z, 1 + sz + sY = s(1/Y + 1/z) and
1 + s/z + sY = s(1/Y + z); multiplying by zY gives the stated equation. For the factorisation, (z + Y)(1/z + Y) = Y(Y + 1/Y + z + 1/z)
= Y/s, so dividing the equation by s(z + Y)(1/z + Y) = Y gives h(z) + h(1/z) = z + 1/z with h(z) = a(z)/(1/z + Y) = za(z)/(1 + zY);
hence h(z) + z = Σ(z) is symmetric and a(z) = (1 + zY)(1 + Σ(z)/z). Finally E[b, 0] counts the v-grid walks from v(0, b) = (0, 2b + 1)
to c, and A^k[p, q] = A^k[Dq, Dp] (`FULL-REACH-PROOF-20261108-001A`, Theorem 2, in the quadrant) turns them into the walks from (1, 0)
to (2b + 1, 0). ∎

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependencies bound by hash | pass |
| 1 | Lemma 1: A² on the v contacts equals the v-grid walk with its bans (boxes 2 to 12, both half-strips, the quadrant) | pass |
| 2 | Theorem 2: σ′ is a symmetry; the survivors have the parity of all returns (quadrant to 48, boxes 4, 6, 8); their counts 1, 2, 7, 34, 206, 1458 | pass |
| 3 | Theorem 3 against the walk (GF(2): half-strips 2 to 12 to s^60, quadrant to s^48; integers, the walk A itself: half-strips 2 to 6 to s^22) | pass |
| 4 | Lemma 4: f(P)[0, 0] = 1 mod 2; the shuffle sum is C_t C_(t+1), even, t ≤ 200 | pass |
| 5 | Proposition 5 below z^4000 | pass |
| 6 | Computed: A1 below w^4000, A2 for k ≤ 24, the pairing of the corner's row and column (k ≤ 8) and where it fails | pass |
| 7 | Computed: the structure of M² and the doubled identity on the half-line below u^40 | pass |
| 8 | The kernel equation and the factorisation's symmetry below s^23; E[b, 0] as the bottom-row walks from (1, 0), b < 6 | pass |

## Nonclaims

- **A1 and A2 are not proved.** Both are computed; (★1D) is the step that resists.
- Theorem 2 describes the walks that carry the count; it does not count them.
