# Odd tori compose everywhere, even tori never reach the antipode; rings of cuts separate when they bound

Status: Proved by hand. The finite claims are checked exactly in `check.py`.

Ticket `LATTICE-NET-20261108-001A`, 2026-11-08.

## Standard statement

- **The square torus of rings.** Rings sit at the points p of Z_n × Z_n (n ≥ 3), each of 4g cells (g ≥ 2) on rule 60, with four
  contacts equally spaced in counterclockwise order: h(p), shared with the ring at p + e1, and v(p), shared with the ring at p + e2.
  Every contact has law (12, 12). This is the square lattice of `LOOP-NET-20261108-001A`, Theorem 3: every corner holds g − 1 own
  cells and weighs ω = z a^(g−1), a = z/(1 + z), and every contact persists at every lag.
- **Needing a ring.** A contact c needs ring X at lag T when c's value at lag T depends on X's own first-row cells. A cut freezes a
  contact, so that it reads nothing (A38).
- **Polynomials.** GF(2)[Z_n²] holds the Laurent polynomials in x and y with x^n = y^n = 1, and L = x + x^(−1) + y + y^(−1). The
  **diagonals** are the points (a, b) with a ≡ b or a ≡ −b (mod n).

**Theorem 1 (composition is the four-neighbour sum).** Write F_h and F_v for the generating functions of the h and v contacts, as
polynomials in x and y over GF(2)((z)). Then F_h = S_h + ω(y + x^(−1))F_v and F_v = S_v + ω(1 + xy^(−1))F_h, and
(y + x^(−1))(1 + xy^(−1)) = L = (x + y)(1 + x^(−1)y^(−1)). So (1 + ω²L)F_h = S_h + ω(y + x^(−1))S_v, and the coefficient of x^a y^b
in L^k is the sum of C(k, i)·C(k, j) over i − j ≡ a, i + j ≡ k − b (mod n). A contact c needs ring X exactly when, for some k, an odd
number of walks of length k in the contact graph lead from one of X's contacts to c. It first needs X at lag g·k + 1 for the least
such k, and then at infinitely many lags, eventually periodically.

**Theorem 2 (odd tori: composition reaches every ring).** For odd n, every power of L vanishes at every point of the diagonals except
the origin, and L^(2^r − 1), with 2^r ≡ 1 (mod n), is 1 at every point off the diagonals. So h(p) is reached from h(q) exactly when
q − p is 0 or off the diagonals, and every contact needs every ring.

**Theorem 3 (even tori: the antipode is never reached).** For even n ≥ 4, every power L^k with k ≥ 1 vanishes at the nonzero points of
the diagonals and at (n/2 − 1, n/2) and its reflections, and h(p) never needs the ring at p + (n/2, n/2). When n is a power of two,
L^(n/2) = 0 and the feedback is finite. So composition stops reaching at every even side.

**Theorem 4 (rings of cuts).**
1. **A bounding ring of cuts separates.** Cut the contacts on the boundary of any set R of rings, those joining a ring of R to a ring
   outside it. Afterwards no uncut contact between two rings of R needs a ring outside R, and no contact between two rings outside R
   needs a ring of R. On an odd torus every contact needed every ring before the cut, so this is a native separation across time.
2. **One ring of cuts round the torus does not separate.** Cut the n contacts h(n − 1, j) between the last column and the first.
   Afterwards h(0, 0) still needs the ring at (n − 1, 0), across the cut, through a single walk of length 2(n − 2) round the other way.
3. **Two rings of cuts round the torus separate.** Cutting the contacts between columns n − 1 and 0 and between columns n/2 − 1 and
   n/2 (rounded down) cuts the boundary of a band of rings, so part 1 applies.

## Nearest known result

- **Additive cellular automata.** Linear cellular automata on rings and tori read through polynomials over GF(2) modulo x^n − 1 (Martin,
  Odlyzko and Wolfram 1984); Pascal's triangle mod 2 and Lucas' theorem; the factorisation x + x^(−1) + y + y^(−1) = (x + y)(1 + x^(−1)y^(−1)).
- **Cuts.** Menger's theorem; on a surface a closed curve separates exactly when it bounds.
- **Classification.** Known-with-delta. The delta is composition and native separation across time in a lattice of rings: the parity of
  the torus's side decides whether composition reaches every ring, and a ring of cuts that does not bound fails to separate.

## Proof of Theorem 1

**Readings.** h(p) is the E contact of ring p and the W contact of ring p + e1. Counterclockwise, the contact before E on ring p is
S = v(p − e2), and the contact before W on ring p + e1 is N = v(p + e1). So h(p) reads the last cells of the corners from v(p − e2) and
from v(p + e1). Likewise v(p) is the N contact of ring p, preceded by E = h(p), and the S contact of ring p + e2, preceded by
W = h(p − e1 + e2). Multiplying by y shifts by +e2 and by x^(−1) by −e1, so with every corner weighing ω (`LOOP-NET-20261108-001A`,
Theorem 1),

  F_h = S_h + ω(y + x^(−1))F_v,  F_v = S_v + ω(1 + xy^(−1))F_h.

Substituting the second into the first gives (1 + ω²L)F_h = S_h + ω(y + x^(−1))S_v, since (y + x^(−1))(1 + xy^(−1)) = y + x + x^(−1) + y^(−1).
Expanding (x + y)(1 + x^(−1)y^(−1)) gives the same four terms. Then (x + y)^k (1 + x^(−1)y^(−1))^k = Σ C(k, i)C(k, j) x^(i−j) y^(k−i−j), which
is the coefficient formula.

**Needing.** By `LOOP-NET-20261108-001A`, Theorem 1, a cell at depth m of X's corner into contact d has coefficient D_cd · z a^m/(1 + z) in
c's value, with D = Σ_k ω^k A^k and A the contact graph's arc matrix mod 2. Since ω is transcendental over GF(2), D_cd ≠ 0 exactly when
some (A^k)_cd = 1, and each contact of X heads one of X's corners. The term ω^k z a^m/(1 + z) = z^(kg+m+1)/(1 + z)^(k(g−1)+m+1) has lowest
order kg + m + 1 with coefficient 1, so the first lag at which c needs X is g·k + 1, with k least and m = 0.

**Infinitely many lags.** D_cd = R(ω) for a rational function R = P/Q over GF(2), Q = det(I + tA) with Q(0) = 1. If R is a polynomial of
degree e, ω has a pole of order g − 1 at z = 1, so D_cd · z/(1 + z) has a pole there of order (g − 1)e + 1. Otherwise R has a pole at some
t_0 ≠ 0, and z^g = t_0(1 + z)^(g−1) has a root z_0 ≠ 0, 1, where D_cd · z/(1 + z) has a pole. Either way it is not a polynomial, so it has
infinitely many nonzero coefficients, eventually periodic since it is rational. ∎

## Proof of Theorem 2

Let n be odd and h = 2^(−1) mod n. From i − j ≡ a and i + j ≡ k − b, i ≡ (k + a − b)h and j ≡ (k − a − b)h independently, so the
coefficient of x^a y^b in L^k is F_k((k + a − b)h) · F_k((k − a − b)h), where F_k(r) = Σ_(i ≡ r) C(k, i) mod 2.
- **The diagonals.** If a ≡ b the first factor is F_k(kh). The map i ↦ k − i preserves the class of kh and pairs its terms, except
  i = k/2 when k is even; C(k, k/2) is even for k ≥ 2 by Lucas' theorem. So F_k(kh) = 0 for k ≥ 1. If a ≡ −b the second factor is
  F_k(kh) = 0.
- **Off the diagonals.** Take r with 2^r ≡ 1 (mod n) and k = 2^r − 1. Every C(k, i) with 0 ≤ i ≤ k is odd, and k = qn with
  q = (2^r − 1)/n odd, so each residue class mod n contains q of the numbers 0, …, k, except the class of 0, which contains q + 1. Hence
  F_k(r′) = 1 exactly when r′ ≢ 0, and the coefficient of L^k at (a, b) is 1 exactly when a ≢ b and a ≢ −b.
- **Every ring.** By Theorem 1, h(0) reaches h(q) exactly when q lies in U, the origin and the points off the diagonals, and reaches
  v(q) exactly when L^k(−q − e2) + L^k(−q + e1) = 1 for some k (the term ω(y + x^(−1))S_v). Ring p has the contacts h(p), v(p), h(p − e1)
  and v(p − e2). If p or p − e1 lies in U, h(0) needs ring p. Otherwise p is a nonzero point of a diagonal and so is p − e1, which leaves
  p = (h, h) and p = (h, −h). Take k = 2^r − 1. For p = (h, h), −p − e2 = (−h, −h − 1) is off the diagonals and −p + e1 = (1 − h, −h) is
  on one, so h(0) reaches v(p). For p = (h, −h) and q = p − e2, −q − e2 = (−h, h) is on a diagonal and −q + e1 = (1 − h, h + 1) is off
  both, so h(0) reaches v(p − e2). So h(0) needs every ring. The translations and the quarter turn of the torus, which takes h contacts
  to v contacts, carry this to every contact. ∎

## Proof of Theorem 3

Let n be even. From i − j ≡ a and i + j ≡ k − b, 2i ≡ k + a − b (mod n), so i takes two values n/2 apart and j ≡ i − a.
- **The diagonals.** For (a, a) with a ≢ 0, k is even, i ∈ {k/2, k/2 + n/2}, and the coefficient is
  F_k(k/2)F_k(k/2 − a) + F_k(k/2 + n/2)F_k(k/2 + n/2 − a). The map i ↦ k − i preserves both classes; the first has the single fixed point
  k/2, with C(k, k/2) even for k ≥ 2, and the second has none. So both F_k(k/2) and F_k(k/2 + n/2) vanish for k ≥ 1. The other diagonal
  follows by the symmetry y ↦ y^(−1) of L.
- **The point (n/2 − 1, n/2).** Here k is odd. With u = (k − 1)/2, i ∈ {u, u + n/2}, and the coefficient is
  F_k(u)F_k(u + 1 + n/2) + F_k(u + n/2)F_k(u + 1). Since F_k(r) = F_k(k − r), F_k(u + 1 + n/2) = F_k(u + n/2) and F_k(u + 1) = F_k(u), so
  the two products are equal and cancel. Its reflections follow by the symmetries x ↦ x^(−1), y ↦ y^(−1) and x ↔ y of L.
- **The antipode.** Let p = (n/2, n/2). h(0) reaches neither h(p), a nonzero diagonal point, nor h(p − e1) = h(n/2 − 1, n/2). For v(p),
  −p − e2 = (n/2, n/2 − 1) and −p + e1 = (n/2 + 1, n/2) are reflections of (n/2 − 1, n/2). For v(p − e2), −(p − e2) − e2 = (n/2, n/2) and
  −(p − e2) + e1 = −(n/2 − 1, n/2 − 1) are nonzero diagonal points (n ≥ 4). Every term vanishes for every k, so h(0) never needs ring p.
- **Powers of two.** If n = 2^m, L^(n/2) = x^(n/2) + x^(−n/2) + y^(n/2) + y^(−n/2) = 0, since squaring is additive over GF(2) and
  x^(n/2) = x^(−n/2). So D is a polynomial in ω. ∎

## Proof of Theorem 4

**Part 1.** Consecutive contacts on a walk of the contact graph share a ring. Follow a walk from a contact between two rings outside R
to a contact between two rings of R, and take the first contact on it with a ring in R. The contact before it has both rings outside R
and shares one of them with it, so it joins a ring of R to a ring outside R: it is cut. A cut contact reads nothing, so no arc enters it
and no walk passes through it (`SEPARATE-20261108-001A`, Lemma B). So no walk avoiding the cut runs between the two kinds of contacts in
either direction. The cells of a ring's corner ending at a cut contact are read by that contact only, so an uncut contact needs only
rings with an uncut contact in its reach, and that reach stays on its own side. Before the cut, on an odd torus, every contact needed
every ring (Theorem 2).

**Part 2.** On the h contacts two steps of the contact graph move the lattice one step: from h(p) the walks of length 2 end at
h(p ± e1) and h(p ± e2), one walk each (Theorem 1). After the cut a walk of length 2k from h(n − 2, 0) to h(0, 0) is a lattice walk of
k steps on the columns 0, …, n − 2, which it cannot leave without entering a cut contact. To get from column n − 2 to column 0 it needs
k ≥ n − 2, and for k = n − 2 the only walk goes straight west. So the count at length 2(n − 2) is 1, h(0, 0) reaches h(n − 2, 0), which
is the W contact of ring (n − 1, 0), and by Theorem 1 it needs that ring, which lies across the cut.

**Part 3.** The cut contacts are exactly those joining the band of rings in columns 0, …, ⌊n/2⌋ − 1 to the rest. ∎

## Remarks

- **A cut can add reach.** On even tori the two ways round can cancel, and cutting one of them lets the other through: after one ring of
  cuts round the 4 × 4 torus, 24 of the 28 uncut contacts need every ring, though none did before (check 8, computed).
- **The antipode is a symmetry, not a range.** The ring never needed on an even square torus is the one reached by routes round the
  torus in opposite directions that pair up and cancel. On rectangular tori the gap appears only on some shapes: of 52 tori with sides 3
  to 12, the ones with a ring some contact never needs are 4 × 4, 4 × 8, 4 × 12, 6 × 6, 8 × 8, 8 × 12 and 10 × 10 (check 11, computed).
  On 4 × 6 or 6 × 10 every contact needs every ring.
- **Not a metric.** The least walk length k sets the first lag g·k + 1 at which a ring is needed. It is used as a lag only; no length or
  distance is formed.
- **No lag cutoffs.** Every reading in `check.py` follows walk counts, powers of L, or rows of M^T until they repeat.

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependencies bound by hash | pass |
| 1 | The contact graph of the n × n torus is the convolution of Theorem 1, and two steps from h(0) are L (n = 3 to 8) | pass |
| 2 | Odd n = 3 to 21: the powers of L reach exactly the origin and the points off the diagonals, and L^(2^r − 1) is 1 exactly off them | pass (L^(2^r − 1) computed explicitly except at n = 19) |
| 3 | Odd n = 3 to 13: every contact needs every ring (every contact up to n = 7, then h(0) and v(0)) | pass |
| 4 | Even n = 4 to 20: every power of L vanishes at the nonzero diagonal points and at (n/2 − 1, n/2); L^(n/2) = 0 for n = 4, 8, 16 | pass |
| 5 | Even n = 4 to 16: h(0) never needs the ring at (n/2, n/2) | pass: h(0) misses 4 rings at n ≡ 2 (mod 4), 24 at n = 8 and 12, 112 at n = 16 |
| 6 | Cell level, exact: for every contact of the 3 × 3 and 4 × 4 tori (g = 2, 3) and for h(0) and v(0) of larger ones, the lags at which it needs each ring: needed exactly when reached, first at g·k + 1, and again in the periodic part | pass: 1,434 contact-ring pairs |
| 7 | Theorem 4, part 1, on n = 3 to 9: every square block of rings and two irregular sets; pre-reach on every odd torus | pass: 31 cuts |
| 8 | Theorem 4, part 2, on n = 3 to 12: the walk count 1 at length 2(n − 2), and how many uncut contacts still need every ring | pass; on odd sides every uncut contact still needs every ring |
| 9 | Theorem 4, part 3, on n = 4 to 10 | pass |
| 10 | Cell level, exact: a block on the 5 × 5 and 4 × 4 tori, one ring of cuts on the 5 × 5, two on the 6 × 6, every uncut contact against every ring | pass |
| 11 | Computed, not a theorem: n × m tori with 3 ≤ n ≤ 10 and n ≤ m ≤ 12, the most rings any contact never needs | pass: none when a side is odd |

## Nonclaims

- **Square tori with equally spaced contacts** and law (12, 12) only.
- **No distance.** No length, path count used as a magnitude, or metric is formed.
- **Two-time knots only** (A30).
