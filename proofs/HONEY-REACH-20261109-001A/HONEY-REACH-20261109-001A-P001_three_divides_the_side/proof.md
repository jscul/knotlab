# Composition on honeycomb tori reaches every ring exactly when 3 divides the side

Status: Theorems 1 to 5 proved by hand; their finite claims are checked exactly in `check.py`. That composition reaches every ring when
3 divides the side is computed, not proved: on every side from 3 to 300.

Ticket `HONEY-REACH-20261109-001A`, 2026-11-09.

## Standard statement

- **The honeycomb torus of rings.** Rings sit at A(p) and B(p) for p in Z_n × Z_n (n ≥ 3), each of 3g cells (g ≥ 2) on rule 60, with
  three contacts equally spaced in counterclockwise order: A(p) holds e0(p), e1(p), e2(p), and B(p) holds e0(p), e1(p + e1),
  e2(p + e2), where e0(p) joins A(p) to B(p), e1(p) joins A(p) to B(p − e1) and e2(p) joins A(p) to B(p − e2). Every contact has law
  (12, 12). This is the honeycomb lattice of `LOOP-NET-20261108-001A`, Theorem 3: every corner weighs ω = z a^(g−1), a = z/(1 + z),
  and every contact persists at every lag. The A rings form a triangular lattice; the B ring B(p) sits at the centre of the triangle
  A(p), A(p + e1), A(p + e2).
- **Needing a ring.** A contact c needs ring X at lag T when c's value at lag T depends on X's own first-row cells; a ring Y needs X
  when one of Y's contacts does, as in `DISTANCE-20261108-001B`'s check 10. **Full reach** means every ring needs every ring.
- **Polynomials.** GF(2)[Z_n²] holds the Laurent polynomials in x and y with x^n = y^n = 1; the coefficient of F at q is F(q). The
  **units** are ±e1, ±e2, ±(e1 − e2), and M = x + x^(−1) + y + y^(−1) + x^(−1)y + xy^(−1) is their sum.
- **Mirror lines.** The three lines through the origin in the directions (1, 1), (−2, 1) and (1, −2), without the origin. They are the
  A rings on the three mirrors of the honeycomb through A(0), each mirror running along one of A(0)'s contacts.
- **Windows.** N̄ = {0} ∪ units, the ring A(0) and its six neighbours; H = {0, e1, e2, e1 + e2, e2 − e1, e1 − e2}, the three A rings
  round B(0) and the three beyond them, a six-pointed star centred on B(0).

**Theorem 1 (composition is the six-neighbour sum).** Write F_k for the generating function of the contacts e_k, as a polynomial in x
and y over GF(2)((z)). Then F_1 = S_1 + ω(1 + x)F_0, F_2 = S_2 + ω(1 + x^(−1)y)F_1 and F_0 = S_0 + ω(1 + y^(−1))F_2, and
(1 + x)(1 + x^(−1)y)(1 + y^(−1)) = M. So the walks of length 3m + ((j − i) mod 3) from e_i(0) to e_j(q) number, mod 2, the coefficient
of P_ij M^m at q, where P_ii = 1 and P_ij is the product of the steps T_01 = 1 + x, T_12 = 1 + x^(−1)y, T_20 = 1 + y^(−1) from type i
to type j. A contact c needs ring X exactly when, for some k, an odd number of walks of length k lead from one of X's contacts to c,
first at lag g·k + 1 for the least such k and then at infinitely many, eventually periodic lags.

**Lemma 2 (windows).** Ring A(p) never needs A(0) exactly when every power M^m vanishes at every point of p + N̄, and B(p) never needs
A(0) exactly when every power vanishes at every point of p + H.

**Theorem 3 (powers vanish on the mirrors).** For every n ≥ 3 and every k ≥ 1, M^k vanishes at every point of the mirror lines.

**Theorem 4 (when 3 does not divide n, the turn-fixed ring is never reached).** Let 3 ∤ n and t ≡ −3^(−1) (mod n). The turn of 120°
about A(0) fixes exactly one ring of the other kind, B(t, t). B(t, t) never needs A(0), and A(0) never needs B(t, t). So every ring
has a ring that never needs it, and composition never reaches every ring.

**Theorem 5 (the mirrors pin only the turn-fixed ring).** For n ≥ 7, no window p + N̄ lies inside the mirror lines, and a window p + H
lies inside them exactly when 3 ∤ n and p = (t, t). So on every side where the points no power reaches are exactly the mirror lines,
composition reaches every ring when 3 | n, and otherwise each ring is never needed by exactly one ring, the ring fixed by the turn
about it.

**Computed, not theorems (checks 8 and 9, and the stress test).**
1. **Full reach when 3 divides n.** On every side n from 3 to 300 divisible by 3, every ring needs every ring.
2. **How many rings never need a ring.** When 3 ∤ n, each ring is never needed by exactly 2(N − 1)(N − 2) + 1 rings, where
   N = 2^(v + 1), v the power of 2 in n, and N = 2^(v − 1) when n is itself a power of two: one ring on odd sides and at n = 4, then
   13, 85, 421, 1,861 and 7,813 as v grows (13 at n = 8, 85 at 16), on every side from 3 to 300.
3. **Where the extra zeros sit.** The points no power reaches are exactly the mirror lines on every odd side to 299 and at n = 4. On
   other even sides there are more, also on sides divisible by 3 (66, 126 and 132 up to 200), where composition still reaches every
   ring. So Theorem 5 explains the odd sides; the even sides keep full reach for a reason not found here.

## Nearest known result

- **Additive cellular automata.** Linear cellular automata read through polynomials over GF(2) modulo x^n − 1 (Martin, Odlyzko and
  Wolfram 1984), here the six-neighbour rule of the triangular lattice; parity counts of lattice walks.
- **Symmetry pairing.** An involution without fixed points on a set of walks makes their number even, the argument of
  `LATTICE-NET-20261108-001A`, Theorem 3, for the square torus's antipode, here applied to the mirrors of the honeycomb.
- **Maps.** The contact graph is the honeycomb's medial graph, the kagome lattice, oriented by the rotation; the honeycomb's
  rotation centres of order 3 are its vertices and face centres.
- **Classification.** Known-with-delta. The pairing argument is classical. The delta is composition across time on the honeycomb torus
  of rings: the obstruction to full reach is the ring the turn of order 3 pins, which exists exactly when 3 ∤ n, as the antipode the
  half-turn pins on the square torus exists exactly when n is even.

## Proof of Theorem 1

**Readings.** A contact reads the contact before it, counterclockwise, on each of its two rings. On A(p) the order is e0(p), e1(p),
e2(p), and on B(p) it is e0(p), e1(p + e1), e2(p + e2). So e1(p) reads e0(p) on A(p) and e0(p − e1) on B(p − e1); e2(p) reads e1(p)
on A(p) and e1(p + e1 − e2) on B(p − e2); e0(p) reads e2(p) on A(p) and e2(p + e2) on B(p). Multiplying by x shifts by +e1 and by y by
+e2, so with every corner weighing ω (`LOOP-NET-20261108-001A`, Theorem 1),

  F_1 = S_1 + ω(1 + x)F_0,  F_2 = S_2 + ω(1 + x^(−1)y)F_1,  F_0 = S_0 + ω(1 + y^(−1))F_2.

Expanding, (1 + x)(1 + x^(−1)y) = 1 + x + x^(−1)y + y, and multiplying by 1 + y^(−1) gives the eight terms 1 + x + x^(−1)y + y + y^(−1)
+ xy^(−1) + x^(−1) + 1, in which the two 1s cancel: M. One step from type k to type k + 1 multiplies by T_k(k+1), so a walk of length
3m + ((j − i) mod 3) from type i to type j passes round the types m times and then from i to j, and the walk counts are P_ij M^m.

**Needing.** The argument of `LATTICE-NET-20261108-001A`, Theorem 1 ("Needing" and "Infinitely many lags"), uses only that contacts
are equally spaced, so that every corner weighs ω, and that each contact of X heads one of X's corners: c needs X at lag T exactly when
some (A^k)_dc = 1 with d a contact of X, first at g·k + 1, and the need recurs at infinitely many, eventually periodic lags. ∎

## Proof of Lemma 2

Put μ = M^m. The contacts of A(p) sit at p and those of A(0) at 0, so by Theorem 1 the nine walk counts from A(0) to A(p) are
(P_ij μ)(p). With P_01 = 1 + x, P_12 = 1 + x^(−1)y, P_20 = 1 + y^(−1), P_02 = 1 + x + x^(−1)y + y, P_10 = 1 + x^(−1)y + y^(−1) + x^(−1)
and P_21 = 1 + y^(−1) + x + xy^(−1), they are μ(p) three times, μ(p) + μ(p − e1), μ(p) + μ(p + e1 − e2), μ(p) + μ(p + e2), and

  μ(p) + μ(p − e1) + μ(p + e1 − e2) + μ(p − e2),  μ(p) + μ(p + e1 − e2) + μ(p + e2) + μ(p + e1),  μ(p) + μ(p + e2) + μ(p − e1) + μ(p − e1 + e2).

All nine vanish exactly when μ vanishes at p and at its six neighbours, read off in that order: p + N̄. For B(p), whose contacts sit at
p, p + e1 and p + e2, the same nine polynomials give μ(p), μ(p + e1), μ(p + e2) and sums that, in turn, add the points p + e2 − e1
(from P_02 at p + e2), p + e1 − e2 (from P_10 at p) and p + e1 + e2 (from P_21 at p + e1): all nine vanish exactly when μ vanishes on
p + H. A ring never needs A(0) when no walk count from any of A(0)'s contacts to any of its contacts is ever odd. ∎

## Proof of Theorem 3

M^k(q) is the number, mod 2, of sequences (u_1, …, u_k) of units with u_1 + … + u_k ≡ q. The reflection σ(a, b) = (b, a) of Z_n²
permutes the units, exchanging e1 with e2, −e1 with −e2 and e1 − e2 with its negative, and fixes none of them. It acts on sequences
term by term, so it fixes no sequence of length k ≥ 1, and it maps the sequences with sum q to those with sum σq. On the line
{(s, s)}, σq = q, so the sequences pair up and M^k(q) = 0. The turn ρ(a, b) = (−a − b, a) also permutes the units (ρe1 = e2 − e1,
ρe2 = −e1, ρ(e1 − e2) = e2), so M^k(ρq) = M^k(q); it carries the line {(s, s)} to {(−2s, s)} and that to {(s, −2s)}. ∎

## Proof of Theorem 4

**The turn-fixed ring.** ρ fixes A(0), and as a map of the honeycomb it carries B(p), at p + (e1 + e2)/3, to the vertex at
ρp + ρ(e1 + e2)/3 = ρp − e1 + (e1 + e2)/3, which is B(ρp − e1). So B(p) is fixed exactly when (ρ − 1)p = e1. Since det(ρ − 1) = 3 is
a unit mod n, there is exactly one solution, and p = (t, t) is it: ρ(t, t) − e1 = (−2t − 1, t), and −2t − 1 ≡ t because 3t ≡ −1.

**It is never reached.** The six points of (t, t) + H are (t, t) and (t + 1, t + 1) on the first mirror line; (t + 1, t) = t·(−2, 1)
and (t − 1, t + 1) = (t + 1)·(−2, 1) on the second, since −2t ≡ t + 1; and (t, t + 1) = t·(1, −2) and (t + 1, t − 1) = (t + 1)·(1, −2)
on the third. None is the origin: t ≡ 0 would give 0 ≡ −1, and t ≡ −1 would give 3 ≡ 1, impossible for n ≥ 3. By Theorem 3 every
M^m with m ≥ 1 vanishes on all six, and so does M^0, which is 1 only at the origin. By Lemma 2, B(t, t) never needs A(0).

**The other way, and every ring.** Translations and the half-turn A(p) ↔ B(−p) about the midpoint of e0(0) preserve the rings,
contacts and counterclockwise orders, so they preserve the contact graph (check 2). The rings that never need B(t, t) are the
translate by (t, t) of the half-turn's image of those that never need A(0), and that image of B(t, t), translated, is A(0). So A(0)
never needs B(t, t). By translations and the half-turn, every ring has a ring that never needs it. ∎

## Proof of Theorem 5

A point (a, b) lies on a mirror line exactly when it is not the origin and one of f_1 = a − b, f_2 = a + 2b, f_3 = 2a + b vanishes mod
n; note f_2 − f_3 = −f_1 and f_2 + f_3 = 3(a + b). For a window p + W, each point p + w needs some F_i ≡ −f_i(w), where F_i = f_i(p).
Each F_i takes one value, so it covers the points of W with one value of f_i.
- **The window N̄.** On N̄ = {0, ±e1, ±e2, ±(e1 − e2)}, f_1 takes 0, ±1, ∓1, ±2, f_2 takes 0, ±1, ±2, ∓1 and f_3 takes 0, ±2, ±1, ±1, so
  no value is taken more than twice by any f_i while n ≥ 5. Three forms cover at most six of the seven points.
- **The window H.** On H = {0, e1, e2, e1 + e2, e2 − e1, e1 − e2}, f_1 takes 0, 1, −1, 0, −2, 2, f_2 takes 0, 1, 2, 3, 1, −1 and f_3
  takes 0, 2, 1, 3, −1, 1. With n ≥ 7 the values −3 to 3 are distinct, and each form takes a value at most twice, the repeated values
  being 0 for f_1 (at 0 and e1 + e2), 1 for f_2 (at e1 and e2 − e1) and 1 for f_3 (at e2 and e1 − e2). Covering all six points
  therefore needs F_1 ≡ 0, F_2 ≡ −1 and F_3 ≡ −1, and these are consistent with F_2 − F_3 = −F_1. Then 3(p_1 + p_2) = F_2 + F_3 ≡ −2.
  If 3 | n this is impossible, since it would make 2 divisible by 3. If 3 ∤ n, F_1 ≡ 0 gives p = (s, s) with 3s ≡ −1, so p = (t, t).

So when the points no power reaches are exactly the mirror lines, Lemma 2 leaves only B(t, t), and only when 3 ∤ n. ∎

## Remarks

- **Why 3.** On the square torus the ring a source never needs is the antipode, fixed by the half-turn about the source, and it exists
  exactly when the side is even (`LATTICE-NET-20261108-001A`, Theorem 3). On the honeycomb torus it is the ring of the other kind fixed
  by the turn of order 3 about the source, which exists exactly when 3 ∤ n. In both, the routes into the pinned ring pair up across
  mirrors and cancel. When 3 | n the turn fixes three A rings and no B ring, and the mirror lines pin nothing.
- **Powers of two make it worse.** On even sides more points escape every power, and the rings left unreached grow with the power of
  2 in the side (computed 2): 13 at side 8 and at twice an odd side, 85 at 16 and at four times an odd side, then 421, 1,861, 7,813
  and, at side 256, 32,005. The square torus shows the same growth (h(0) misses 4 rings at sides ≡ 2 mod 4, 24 at 8 and 12, 112 at
  16). The count does not grow with the odd part of the side.
- **What is open.** Full reach when 3 | n rests on computation. Theorem 5 reduces it, on odd sides, to the points no power reaches
  being exactly the mirror lines, computed on every odd side to 299; it fails on some even sides divisible by 3 (66 is the first), where
  full reach holds all the same.
- **Not a metric.** The least walk length sets the first lag g·k + 1; it is used as a lag only.
- **No lag cutoffs.** Every reading follows powers of M, walk counts or rows of M^T until the next lies in the span of the earlier ones.

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependencies bound by hash | pass |
| 1 | The library's honeycomb torus (n = 3 to 10, g = 2, 3) has the readings of Theorem 1 and the ring contacts of the model | pass |
| 2 | Three steps between contacts of one type are M (n = 3 to 10); the turn and the half-turn preserve the rings and their orders | pass |
| 3 | Lemma 2: the windows give the same rings as the nine reach sets, from A(0), and the rings that never need B(0) are the half-turn's image (n = 3 to 30) | pass |
| 4 | Contact level, exact: for every pair of rings X, Y, Y never needs X by the library's walk reach exactly as the model says (n = 3 to 16) | pass: 975,324 pairs over 14 sides |
| 5 | Cell level, exact: for every contact and ring, the contact depends on the ring's first-row cells exactly when a walk count is odd (n = 3 to 7 at g = 2, 4 and 5 at g = 3) | pass: 33,240 pairs |
| 6 | Theorem 3: the span of M^k, k ≥ 1, vanishes on the mirror lines (n = 3 to 200) | pass |
| 7 | Theorem 4: for 3 ∤ n (n = 4 to 200), the six points of (t, t) + H are on the mirror lines and B(t, t) never needs A(0) | pass |
| 8 | Computed: full reach exactly when 3 | n (n = 3 to 200) | pass |
| 9 | Computed: the count 2(N − 1)(N − 2) + 1 of rings that never need A(0) (n = 3 to 200); the sides with points off the mirror lines that no power reaches | pass |

The stress test of `HONEY-REACH-20261109-001` carries checks 6 to 9 to sides 201 to 300, check 4 to sides 17 to 20 and check 5 to sides
8 and 9.

## Nonclaims

- **Honeycomb tori with equally spaced contacts** and law (12, 12) only.
- **Full reach when 3 | n is computed**, to side 300; it is not proved.
- **No distance.** No length, path count used as a magnitude, or metric is formed.
- **Two-time knots only** (A30).
