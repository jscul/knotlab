# Distance across time is native as a cone; cuts count the ring graph's distance

Status: Proved by hand. The finite claims are checked in `check.py`; checks 9 to 11 are computations, not theorems.

Ticket `DISTANCE-20261108-001B`, 2026-11-08.

## Standard statement

- **Networks.** Rule-60 rings joined by contacts with law (12, 12), each contact reading its left neighbour on both of its rings
  (`LOOP-NET-20261108-001A`), consecutive contacts on a ring at least two cells apart. The **contact graph** Γ has an arc d → e for
  every corner, the ℓ ≥ 1 own cells on a ring between a contact d and the next contact e; the arc **carries** ℓ + 1 cells, its own
  cells and the contact it reaches. Throughout, no two corners of the same length run from one contact to the same contact (true of
  every network here: none has two corners between the same two contacts).
- **Needs and cuts.** A contact c **needs** ring X at lag T when c's value at lag T depends on X's own first-row cells (A32), and
  c needs a contact e when it depends on e's first value. A cut freezes a contact (A38): it reads nothing and keeps its first value.
- **Routes.** A **route** from ring X to contact c is a directed path c_0 → c_1 → … → c_L = c of Γ whose first contact c_0 is its
  only contact on X, each hop along exactly one corner. It is **chordless** when no arc c_i → c_j with j > i + 1 joins two of its
  contacts, and **induced** when no arc joins two of its contacts except its hops. **Isolating** a route freezes every contact off it.
- **Lengths.** δ(X → c), the **directed distance**, is the least number of arcs of a route from X to c, and δ(e → c) the least
  number of arcs of a walk from contact e to c; λ(X → c) is the least number of cells a route from X to c carries. With contacts g
  cells apart (**equal spacing**) every arc carries g cells and λ = g·δ. D(X, Y) is the **ring graph's distance** (rings as
  vertices, contacts as edges), and D(X, c) the least of D(X, R) over the two rings R of c.
- **The plain first need.** At equal spacing, κ(X → c) is the least k such that an odd number of walks of k arcs lead from a contact
  of X to c, and κ(e → c) the same from one contact e. By the argument of `LATTICE-NET-20261108-001A`, Theorem 1, which uses only
  equal spacing, c first needs X at lag g·κ(X → c) + 1, and first needs e's first value at lag g·κ(e → c).

**Theorem 1 (counted length along an isolated route).** Let P be a chordless route of L arcs from X to c whose hops carry n_1, …, n_L
cells, and isolate it. Then c first needs X at lag 1 + n_1 + … + n_L, which is g·L + 1 at equal spacing, and the first lags of two
routes joined at a shared contact add: t − 1 = (t_1 − 1) + (t_2 − 1). If P is induced, with ℓ_i = n_i − 1 own cells per hop and ℓ_X own
cells in X's corner into c_0, then c needs X at lag T exactly when C(T − L − 1, ℓ_1 + … + ℓ_L + m) is odd for some m < ℓ_X, and every
contact of P binds both of its rings at every lag: an isolated induced route composes at the recurring lags its dynamics fixes (A37),
first at 1 + n_1 + … + n_L, periodically from there.

**Theorem 2 (the earliest need is the time of flight).** For every set F of contacts not containing c, after F is frozen c needs X at
no lag before 1 + λ(X → c), and freezing every contact off a route that carries the fewest cells, with the fewest arcs among those,
makes c need X at exactly that lag. So the earliest need any freeze allows is 1 + λ(X → c), and g·δ(X → c) + 1 at equal spacing; the
plain first need (F empty) is never earlier. Between contacts δ is a directed metric: it satisfies the triangle inequality and
vanishes only on the diagonal, and it is not symmetric.

**Theorem 3 (cut counts).**
1. **Pieces.** For rings X ≠ Y, the most pairwise disjoint sets of contacts each of whose freezing leaves X and Y in different native
   pieces (`GENUS-CUT-20261108-001A`, Theorem 1) is D(X, Y).
2. **Blocking for good.** For a ring X and a contact c not on X, the most pairwise disjoint sets of contacts, none containing c, each
   of whose freezing leaves c needing X at no lag however many more contacts are frozen, is δ(X → c).

**Theorem 4 (the plain first need is the cone filtered by parity).** At equal spacing κ(X → c) ≥ δ(X → c), with equality exactly when
some contact of X at directed distance δ(X → c) from c has an odd number of shortest routes to c.
1. **Square torus, closed forms.** Rings at p ∈ Z_n², h(p) joining p and p + e1 at p + (1/2, 0), v(p) joining p and p + e2 at
   p + (0, 1/2), and u = x + y, w = y − x. From an h contact every arc changes w by ±1, from a v contact u by ±1. With Δu, Δw taken
   over the least lift: δ(h → h′) = δ(v → v′) = 2·max(|Δu|, |Δw|), δ(h → v) = 2·max(|Δu|, |Δw| − 1) + 1 and
   δ(v → h) = 2·max(|Δw|, |Δu| − 1) + 1.
2. **Square torus, rings and contacts.** For every ring X and contact c, 2D − 1 ≤ δ(X → c) ≤ 2D with D = D(X, c) ≥ 1, so
   D = ⌈δ/2⌉.
3. **Square torus, one kind.** For contacts e and c of one kind at offset (a, b), |a|, |b| < n/2, δ(e → c) = 2(|a| + |b|) and c's need
   on e's first value comes at lag g·δ exactly when a AND b = 0 in binary; when |a| or |b| is n/2 it never comes then.
4. **The plane.** A contact needs the first value of the contact of its kind at offset (a, b) ≠ (0, 0) at some lag exactly when
   v2(a) ≠ v2(b) (v2 the 2-adic valuation, v2(0) = ∞), and κ at offset (2a, 2b) is twice κ at (a, b). The offsets never needed have
   density 1/3.

**Theorem 5 (translates).** On the square, triangular and honeycomb tori, the directed distance from a contact to its translate by a
lattice vector v is (m/2)·D(0, v), where m = 4, 6, 3 is the number of contacts per ring and D(0, v) the ring graph's distance from a
ring to its translate.

## Nearest known result

- **Cuts and distance.** The most pairwise disjoint s–t cuts equal the s–t distance (Robacker 1956; Fulkerson's max-potential
  min-work duality), the dual of Menger's theorem; the layer cuts are the classical witnesses.
- **Light cones and parity.** Additive cellular automata over GF(2) and their light cones (Martin, Odlyzko and Wolfram 1984);
  Lucas' and Kummer's theorems; the self-similarity of Pascal's triangle mod 2 under doubling (the Frobenius map), as in Willson's
  analysis of additive automata.
- **Maps.** The medial graph of a map oriented by the rotation, rotating an edge about one end; the hexagonal norm on Eisenstein
  integers.
- **Classification.** Known-with-delta. The min-max facts, the walk counts and the parity criteria are classical. The delta is reading
  them across time in persistent networks of rings: the earliest need any freeze allows as a time of flight, the cut counts as native
  lengths, and the plain first need as the light cone filtered by the parity of shortest routes.

## Proof of Theorem 1

By `LOOP-NET-20261108-001A`, Theorem 1, the contacts' generating functions satisfy C = S + KC, K summing corner weights z a^ℓ with
a = z/(1 + z) over GF(2); a frozen contact reads nothing, so its row of K is zero and no walk enters it (`SEPARATE-20261108-001A`,
Lemma B). An own cell at depth m of a corner ending at contact e (depth 0 the last cell) appears only in S_e, with coefficient
z a^m/(1 + z), so its coefficient in C_c is D_ce · z a^m/(1 + z), where D = (I + K)^(−1) sums the weights of the walks of unfrozen
contacts from e to c. The own cells of X lie in corners ending at contacts of X; every contact of X but c_0 is frozen, so only the cells
of X's corner into c_0 can reach c, each with coefficient D_(c c_0) · z a^m/(1 + z), m < ℓ_X. Distinct cells are distinct variables,
so c needs X at lag T exactly when one of these coefficients has a nonzero coefficient of z^T.

A walk from c_0 to c among the route's contacts can cross from {c_0, …, c_i} to {c_(i+1), …, c_L} only by the hop c_i → c_(i+1), since
P is chordless. So every such walk uses every hop, and a walk other than P uses at least one more arc. A walk's weight z^k a^(Σℓ) =
z^(k + Σℓ)/(1 + z)^(Σℓ) has lowest order equal to the cells it carries, with coefficient 1, and every arc carries at least 2 cells. So
D_(c c_0) = w(P) + (terms of higher order), and the lowest-order term of all the coefficients is w(P) · z/(1 + z), of order
n_1 + … + n_L + 1, from m = 0 alone: c first needs X at lag 1 + Σ n_i. When P is the concatenation of two chordless routes joined at a
shared contact and is itself chordless, its cells are the sum of theirs, which is the additivity.

If P is induced, P is the only walk among its contacts, so D_(c c_0) = z^L a^(Σℓ) exactly, and the coefficient of the cell at depth m is
z^(L + Σℓ + m + 1)/(1 + z)^(Σℓ + m + 1). Since 1/(1 + z)^r = Σ_j C(j + r − 1, r − 1) z^j, its coefficient of z^T is C(T − L − 1, Σℓ + m)
mod 2. By Lucas' theorem C(N, K) is odd exactly when every binary digit of K is a digit of N, a condition periodic in N with period a
power of two, met first at N = K; so c needs X periodically from lag 1 + Σ n_i on. An induced route has no closed walk, so no return
reaches any of its contacts, D_(c_i c_i) = 1, and by `LOOP-NET-20261108-001A`, Theorem 1, each contact of P keeps both chain-end
witnesses, one own cell of each of its rings, at every lag. ∎

## Proof of Theorem 2

**No earlier.** After F is frozen, as in the proof of Theorem 1, an own cell of X reaches c only through an unfrozen contact e of X,
with coefficient D^F_ce · z a^m/(1 + z), D^F summing walks of Γ − F. Each walk from e to c contains a route from X to c (from its last
contact on X), so it carries at least λ(X → c) cells, and the coefficient has order at least λ(X → c) + 1.

**Exactly then.** Let φ(x) be the least number of cells a walk from contact x to c carries, so that every arc x → y carries at least
φ(x) − φ(y) cells, and call an arc tight when equality holds. Let P = c_0 … c_L be a route from X carrying the fewest cells, λ(X → c),
with the fewest arcs among those. A walk from c_0 to c carries Σ (cells of its arcs) ≥ φ(c_0) = λ cells, with equality exactly when
all its arcs are tight. Tight arcs lower φ, so a tight walk among P's contacts visits them in increasing order. A tight arc
c_i → c_j with j > i + 1 would carry as many cells as P's segment from c_i to c_j, and replacing the segment by it would give a route
with as few cells and fewer arcs. So the only walk among P's contacts with λ cells uses the hops of P, each along its one corner of
that length (no twin corners), and is P. Isolating P, the lowest-order term is w(P) · z/(1 + z) alone, and c needs X at lag 1 + λ.

**A directed metric.** δ between contacts is the length of a shortest directed path, so it satisfies the triangle inequality and is 0
only from a contact to itself. It is not symmetric: on the square torus h(p) → v(p) is one arc, while from v(p) the arcs go to
h(p − e1) and h(p + e2) and δ(v(p) → h(p)) = 3. ∎

## Proof of Theorem 3

**Part 1.** By `GENUS-CUT-20261108-001A`, Theorem 1, after F is frozen the native pieces are the components of the ring graph G
without the edges F. Let L_i, for i = 1, …, D(X, Y), be the contacts joining a ring at distance i − 1 from X to one at distance i. They
are pairwise disjoint. An edge of G joins rings whose distances from X differ by at most one, so G without L_i has no edge from the
rings at distance less than i to the rest; X and Y fall in different pieces. Conversely, a shortest path from X to Y in G uses D(X, Y)
contacts, and every set whose freezing separates X from Y contains one of them, so pairwise disjoint such sets number at most D(X, Y).

**Part 2.** A set F blocks for good exactly when every route from X to c meets F. If every route meets F, then after freezing any
F′ ⊇ F a walk of Γ − F′ from a contact of X to c would contain a route avoiding F, so D^(F′) vanishes on X's contacts and c needs X at no
lag. If some route avoids F, a shortest route P of Γ − F from X to c has no forward chord in Γ (a chord would be an arc of Γ − F
shortening it), and freezing every contact off P, a superset of F, makes c need X (Theorem 1). Now let B_i, for i = 0, …, δ(X → c) − 1,
be the contacts at directed distance i from X. They are pairwise disjoint and none is c. Along an arc the directed distance from X
grows by at most one, from 0 at the start of a route to δ(X → c) at c, so every route meets every B_i. Conversely, every blocking set
not containing c contains one of the first δ(X → c) contacts of a fixed shortest route, so pairwise disjoint ones number at most
δ(X → c). ∎

## Proof of Theorem 4

**The cone.** A walk of k arcs from a contact e of X to c has k ≥ δ(e → c) ≥ δ(X → c). A walk of exactly δ(X → c) arcs from e is a
shortest path, and it holds no other contact e′ of X, since δ(e′ → c) would then be smaller. So the number of walks of δ(X → c) arcs from
e to c is e's number of shortest routes to c, and κ = δ exactly when one of them is odd. That the plain first lag is g·κ + 1 is
`LATTICE-NET-20261108-001A`, Theorem 1's reading, whose argument needs only equal spacing (D_ce = Σ_k ω^k (A^k)_ce with ω transcendental).

**Part 1.** The arcs from h(p) go to v(p) and v(p + e1 − e2), displacements ±(−1/2, 1/2), which change w by ±1 and leave u; the arcs
from v(p) go to h(p − e1) and h(p + e2), displacements ±(1/2, 1/2), which change u by ±1. So a walk alternates w-steps and u-steps,
each of either sign. From h, a walk of 2j arcs makes j steps of each kind, so it reaches (Δu, Δw) exactly when |Δu|, |Δw| ≤ j and
both are ≡ j (mod 2); h contacts have u − w odd, so Δu ≡ Δw, and the least j is max(|Δu|, |Δw|). From h to v a walk of 2j + 1 arcs makes
j + 1 w-steps and j u-steps, and v contacts have u − w even, so Δu − Δw is odd and the least j is max(|Δu|, |Δw| − 1). The other two
cases are the same with u and w exchanged. On the torus a walk lifts to the plane, so δ is the least over lifts.

**Part 2.** A ring X sits at an integer point (u_X, w_X) with u_X ≡ w_X (mod 2), its contacts at (±1/2, ±1/2) from it: h(X) and h(X − e1)
at (s, −s), v(X) and v(X − e2) at (s, s), s = ±1/2. Let c be an h contact at (U, W) from X, so U − W is odd and U, W ∈ Z + 1/2. Its
rings sit at (U − 1/2, W + 1/2) and (U + 1/2, W − 1/2), and ring graph distance is max(|Δu|, |Δw|) between rings, so
D = M − 1/2 with M = max(|U|, |W|) (if |U| = |W| then W = −U, and one of c's rings is at max(|U|, |W|) − 1/2). By Part 1, through
X's h contacts δ = 2·max(|U − s|, |W + s|) ≥ 2(M − 1/2) = 2D, with equality for one of the two values of s; through its v
contacts δ = 2·max(|W − s|, |U − s| − 1) + 1 ≥ 2(M − 3/2) + 1 = 2D − 1. So 2D − 1 ≤ δ ≤ 2D, and the quarter turn about a ring, an
automorphism of the map that exchanges h and v contacts, gives the same for v contacts. Least over lifts, D = ⌈δ/2⌉ on the torus.

**Part 3.** Two arcs from an h contact make one u-step and one w-step, which together move the ring lattice one step: (+, +) is +e2,
(+, −) is −e1, (−, +) is +e1 and (−, −) is −e2. So walks of 2j arcs between h contacts are lattice walks of j steps, and the
shortest ones to offset (a, b) number C(|a| + |b|, |a|) on each least lift. With |a|, |b| < n/2 the least lift is unique, and the
count is odd exactly when adding |a| and |b| in binary has no carry (Kummer), that is when a AND b = 0. With |a| or |b| equal to n/2
there are two or four least lifts with equal counts, so the count is even. The coefficient of e's first value in C_c is D_ce, of
lowest order g·κ(e → c).

**Part 4.** On the plane the coefficient of x^a y^b in L^k, L = x + 1/x + y + 1/y, is the single term C(k, i)·C(k, j) with
i − j = a and i + j = k − b (`LATTICE-NET-20261108-001A`, Theorem 1). Over GF(2), L² = L(x², y²), so L^(2j) = L^j(x², y²) has only
even exponents and L^(2j+1) = L · L^j(x², y²) has exactly one odd exponent in each term. Hence an offset with both coordinates odd is
never reached, and the coefficient of x^(2a) y^(2b) in L^k is 0 for odd k and equals that of x^a y^b in L^(k/2) for even k: κ doubles.
By induction an offset 2^v (a′, b′) with a′, b′ odd is never reached. If v2(a) ≠ v2(b), divide by the smaller power of two to get one
odd and one even coordinate, and take k = 2^r − 1 ≥ |a| + |b|: then i and j are integers in [0, k], and every C(k, i) is odd, so the
offset is reached. The offsets with v2(a) = v2(b) have density Σ_v 4^(−(v+1)) = 1/3. ∎

## Proof of Theorem 5

Embed the lattice in the plane with every ring's contacts at equal angles 2π/m in counterclockwise order, each contact a unit
segment, and let ρ = e^(2πi/m). An arc of Γ from a contact with midpoint M and direction d (a unit vector up to sign) goes to the
next contact counterclockwise at one of its ends: about the end M − d/2 the new midpoint is M + (ρ − 1)d/2, about M + d/2 it is
M − (ρ − 1)d/2, and in both cases the new direction is ±ρd. So after k arcs the direction is ±ρ^k d_0 and the midpoint has moved by
((ρ − 1)d_0/2)·Σ_(t<k) ε_t ρ^t, every sign sequence ε being a walk. A translate keeps the direction, so k ≡ 0 modulo p, the order
of ρ up to sign: p = 2 for m = 4 (ρ² = −1), p = 3 for m = 6 (ρ³ = −1) and for m = 3 (ρ³ = 1). With k = pj, grouping t by its residue
gives Σ_(s<p) A_s ρ^s with each A_s a sum of j signs: any integer with |A_s| ≤ j and A_s ≡ j (mod 2).
- **Square, ρ = i.** For a horizontal contact and v = (a, b), v = ((i − 1)/2)(A_0 + iA_1) gives A_0 = b − a and A_1 = −(a + b), so the
  least j is |a| + |b| = D(0, v) and δ = 2D.
- **Triangular, ρ = e^(iπ/3), ρ − 1 = ρ².** Write 2v/(ρ²d_0) = 2(x + yρ). Since ρ² = ρ − 1, A_0 + A_1ρ + A_2ρ² = (A_0 − A_2) + (A_1 + A_2)ρ,
  so A_0 = 2x + s, A_1 = 2y − s, A_2 = s. The least j is the least max(|s + 2x|, |s − 2y|, |s|), attained at the middle of the three
  points −2x, 2y and 0: j = max(−x, y, 0) − min(−x, y, 0), the hexagonal norm of x + yρ, which is D(0, v), and s has the parity of j.
  So δ = 3D.
- **Honeycomb, ρ = ω = e^(2πi/3).** The translations are (ω − 1)d_0·Z[ω]; write 2v/((ω − 1)d_0) = 2(x + yω). Since 1 + ω + ω² = 0,
  A_0 = 2x + s, A_1 = 2y + s, A_2 = s, and the least j is max(x, y, 0) − min(x, y, 0), the hexagonal norm of x + yω: the distance
  between a ring and its translate in the lattice of rings of one kind, whose steps are pairs of edges. So D(0, v) = 2j and δ = 3j =
  (3/2)D.
On the torus, walks and paths lift to the plane, so both sides are least over lifts, and they correspond. ∎

## Remarks

- **Two counts of one length.** The time reading (Theorem 2) counts cells and the blocking reading (Theorem 3, part 2) counts
  contacts; they agree, as λ = g·δ, when contacts are equally spaced. The pieces reading (Theorem 3, part 1) is symmetric and counts
  rings crossed: D, the ring graph's distance, on every network.
- **The directed distance is chiral.** Rule 60 and law (12, 12) read leftward, so influence goes one way round every ring. Between
  contacts δ is a directed metric whose asymmetry is at most 2 arcs on every lattice and genus-2 and genus-3 network checked, and 1
  on the Platonic networks (check 10). Between rings, least over their contacts, it fails the triangle inequality (except on the
  tetrahedron): a ring is entered at one contact and left at another. Between rings, D is the metric.
- **The plain first need on regular networks.** On the five Platonic networks, the genus-2 networks of GL(2,3) and the genus-3
  networks of PSL(2,7), every contact needs every ring exactly at the directed distance (check 5). On the lattices it is late or
  absent where shortest routes pair up. On time, of all ring–contact pairs: square tori of side 5, 6, 7 and 8, 1,050 of 1,250,
  2,016 of 2,592 (288 never), 3,234 of 4,802 and 4,608 of 8,192 (3,072 never); triangular tori of side 4 to 7, 768 of 768, 1,575 of
  1,875, 3,240 of 3,888 and 6,321 of 7,203; honeycomb tori of side 3 to 6, 486 of 486, 1,248 of 1,536 (288 never), 2,850 of 3,750
  (450 never) and 6,480 of 7,776.
- **Not a metric (computed, check 10).** Contact to contact the plain first need breaks the triangle inequality in 24 of 54
  admissible triples on the tetrahedron, 20,000 of 61,250 on the square torus of side 5 and 30,912 of 551,124 on the Klein quartic
  network; ring to ring (least over their contacts) in 0 of 64 on the tetrahedron, 2,600 of 15,625 on the square torus of side 5 and
  13,272 of 175,616 on the Klein quartic network. It is not symmetric.
- **Full reach on honeycomb tori (computed, check 10).** On sides 4, 5 and 7 every ring has exactly one ring it never needs, ring to
  ring, and on sides 3 and 9 none. Unlike the square torus (`LATTICE-NET-20261108-001A`), the side's parity does not decide it.
- **Unequal spacing (computed, check 11).** With consecutive contacts 2 to 9 cells apart at random, the plain first need meets
  1 + λ for 98% to 100% of the ring–contact pairs, since walks of equal cells rarely pair up; but every contact then loses its
  witnesses, and 2 to 10 contacts per network miss a ring by lag 300. The symmetry that makes returns cancel, which keeps contacts
  persistent, is the symmetry that makes routes cancel.
- **No cutoffs.** Walk counts follow rows of A^k until the next lies in the span of the earlier ones; cell-level readings either stop
  at the lag the theorem names or follow rows of M^T to the span (checks 2 and 4).

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependencies bound by hash, ticket A's frozen files among them | pass |
| 1 | Theorem 1 at the cell level: induced isolated routes of 1 to 8 arcs on seven networks at spacings 2, 3, 4 and unequal (2 to 9): the need set to its horizon is the Lucas set, and every route contact keeps both witnesses | pass: 502 routes |
| 2 | Theorem 2 at the cell level: for ring–contact pairs of ten networks at spacings 2 and 3 and of two at unequal spacing, isolating a fewest-cells, fewest-arcs route gives 1 + λ, two random freeze sets and the plain network give nothing earlier, and the plain first need comes at g·κ + 1 | pass: 18,052 pairs |
| 3 | Theorem 3, part 1: layer cuts on nine networks, each leaving the two rings in different native pieces | pass: 1,938 ring pairs, 5,164 cuts |
| 4 | Theorem 3, part 2: layers of the contact graph on seven networks, each blocking every route, 1,304 of them read at the cell level to the span | pass: 2,308 pairs |
| 5 | Theorem 4, the cone and its parity, on every ring–contact pair of 21 networks | pass |
| 6 | Theorem 4, parts 1 to 3, on square tori of side 5 to 13: closed forms on every contact pair, D = ⌈δ/2⌉ on every ring–contact pair, Lucas on 177,834 same-kind pairs | pass |
| 7 | Theorem 4, part 4, on the plane: offsets with \|a\|, \|b\| ≤ 31 against L^k to k = 63 (enough by the proof): 1,364 of 3,969 never reached, exactly those with v2(a) = v2(b); doubling on 621 offsets | pass |
| 8 | Theorem 5 on square tori of side 5 to 10, triangular 4 to 9 and honeycomb 3 to 8 | pass: 121,928 pairs |
| 9 | Computed: D = ⌈δ/3⌉ on triangular tori of side 4 to 10; ⌈3D/2⌉ − 1 ≤ δ ≤ ⌈3D/2⌉ on honeycomb tori of side 3 to 9; the tables of (D, δ) on the genus-2, genus-3 and Platonic networks | pass |
| 10 | Computed: triangle-inequality and symmetry counts for the plain first need and the directed distance, and pairs never needed | pass |
| 11 | Computed: unequal spacing, the plain first need against 1 + λ, witnesses and missed rings to lag 300 | recorded |

## Nonclaims

- **These networks only:** rule-60 rings with law (12, 12) at every contact and no two corners of one length between the same two
  contacts. The triangular and honeycomb bands for rings and contacts (check 9) are computed, not proved.
- **Lengths, not a geometry.** The lengths here are counted lengths across time (A40). No coordinate, angle or embedding is read
  from the substrate; the plane embeddings in the proofs of Theorems 4 and 5 are the prover's, used to count walks.
- **Given, not grown.** The networks are given, not grown from a law.
- **Two-time knots only** (A30).
