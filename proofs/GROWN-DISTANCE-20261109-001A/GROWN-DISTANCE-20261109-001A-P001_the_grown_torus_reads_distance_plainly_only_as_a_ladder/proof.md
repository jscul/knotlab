# The grown torus reads distance by freezing at every stage, and plainly only as a ladder

Status: Proved by hand. The finite claims are checked exactly in `check.py`; check 5 is a computation, not a theorem.

Ticket `GROWN-DISTANCE-20261109-001A`, 2026-11-09.

## Standard statement

- **Networks and readings.** Equally spaced rule-60 rings with law (12, 12) contacts, read through their contact graph Γ
  (`DISTANCE-20261108-001B`). D is the ring graph's distance, δ the directed distance in Γ, and the plain first need of contact c on ring r
  is **on time** when it comes at lag g·δ(r → c) + 1, which by `DISTANCE-20261108-001B`, Theorem 4, happens exactly when an odd number of
  shortest routes reach c from one of r's contacts at distance δ(r → c). A network is on time when every ring is on time for every contact
  it does not hold (`PLAIN-TIME-20261108-001B`).
- **Band growth.** The band law (`BAND-SURFACE-20261108-001A`, `GROW-NET-20261108-001A`) starts from a loop of n ≥ 3 rings and inserts
  whole bands of n rings: its stages are the loop, the **ladder** n × 2 (the band joined to the loop on both sides, double rungs), and the
  n × m torus for m = 3, 4, …, every stage balanced. A stage is read as a fixed network (A42).
- **Tori of every shape.** A **square torus** is Z² modulo any sublattice Λ of index at least 3, rings at the points, h(p) joining p and
  p + e1, v(p) joining p and p + e2, each ring listing E, N, W, S counterclockwise. The n × m torus is Λ = nZ × mZ. The rotation-invariant
  Λ are `PLAIN-TIME-20261108-001B`'s regular tori {4,4}_(b,c); the others are not regular maps. Every square torus has the half-turn about
  every contact, so every contact persists (`GROW-NET-20261108-001A`, Theorem 1, whose proof uses only that −Λ = Λ).

**Theorem 1 (every stage reads both freeze lengths).** At every stage of band growth, the most pairwise disjoint freeze sets that leave
two rings in different native pieces is their ring-graph distance D, and the earliest lag at which any freeze makes a contact c need a
ring X is g·δ(X → c) + 1, reached by isolating a shortest route; and on the ladder and every torus D = ⌈δ/2⌉ between a ring and a
contact (on the loop δ = D).

**Theorem 2 (ladders read distance plainly).** Every square torus whose lattice holds (0, 2) or (2, 0), the n × 2 ladder among them and
its twisted forms Λ = ⟨(0, 2), (n, 1)⟩, is on time, for every n ≥ 2: every contact needs every ring exactly at the time length, with
nothing frozen. In particular the band law's first stage reads distance plainly at every size.

**Theorem 3 (the rectangular tori).** The n × m torus with 2 ≤ n ≤ m is on time exactly when n = 2 or n = m = 3. So every stage of band
growth from the second band on (n × m with n, m ≥ 3, except 3 × 3) is late: it reads distance only through freezes.

**Theorem 4 (balls).** On the n × m torus, the rings within ring-graph distance r of a ring number Σ_b min(n, 2(r − |b|) + 1), the sum
over rows b ∈ Z_m with circular distance |b| ≤ r. On the cylinder Z_n × Z (the stages as m grows) this is 2r² + 2r + 1 for r ≤ (n − 1)/2,
and going from r to r + 1 adds min(n, 2r + 1) + min(n, 2r + 3) rings: 4r + 4 while 2r + 3 ≤ n, and exactly 2n once 2r + 1 ≥ n. The time length's balls are the same balls: the rings X with δ(X → c) ≤ 2r are
those within ring distance r of one of c's two rings. So a stage reads dimension 2 out to about half its loop and dimension 1 beyond,
and every later band only lengthens the tube.

**Computed (every torus).** Reading every square torus to index 100, triangular torus to index 80 and honeycomb torus to index 50 (all
sublattices, each once): the ladders (195 of 195), the square tori holding (2, 1) or a rotation of it (191 of 191; their mirror images,
holding (1, 2), are on time only at index 5 to 9) and the triangular tori holding a vector of length √3 (232 of 232) are on time at
every index read, and every other on-time torus has index at most 17 (square), 21 (triangular) or 9 (honeycomb). The rotation-invariant
ones among them are exactly `PLAIN-TIME-20261108-001B`'s 9, 11 and 6.

## Nearest known result

- **Geodesic counts on cylinders.** Counting shortest paths in strips and cylinders of the square lattice, and Pascal's triangle mod 2
  (Lucas' theorem) as in `DISTANCE-20261108-001B`; the systole argument of `PLAIN-TIME-20261108-001B`, Theorem 3, here applied to the
  cylinder as cover; the growth of balls in Z × Z_n (growth of a virtually cyclic group: linear).
- **Classification.** New as far as found for the question asked: which tori, of every shape, read distance plainly. The ingredients
  are classical.

## Proof of Theorem 1

`DISTANCE-20261108-001B`, Theorems 2 and 3, hold on every network with no two corners of one length between the same two contacts. A
loop's two corners at a contact go to its two neighbours; on a square torus the two corners out of a contact turn it about its two rings
and end at contacts of different rings, so no stage has twin corners (check 1 confirms it for loops of 3 to 12 rings, ladders of 2 to 40
and tori to 12 × 20, and reads isolated shortest routes at g·δ + 1 at the cell level on 316 ring–contact pairs). The bound
2D − 1 ≤ δ ≤ 2D of `DISTANCE-20261108-001B`, Theorem 4, part 2, is proved on the plane and passes to any quotient by taking least lifts:
both sides are minima over the same lifts, so ⌈δ/2⌉ = D on every square torus, the ladder included. On a loop of rings every ring has
two contacts and Γ is the cycle of contacts with arcs both ways, so δ(X → c) is the cyclic distance from X's nearer contact, which is the
ring distance D(X, c). ∎

## Proof of Theorem 2

By the quarter turn, an orientation-preserving symmetry of the square lattice that exchanges h and v contacts and maps a lattice holding
(2, 0) to one holding (0, 2), it suffices to treat Λ ∋ (0, 2). Such a Λ with no ring touching itself is ⟨(0, 2), (n, t)⟩ with n ≥ 2 (or
n = 1, t = 1, of index 2, excluded) and t ∈ {0, 1}, and its cover in the direction of (0, 2) is the strip Z × Z_2, rings (i, j) with
j a level mod 2, the deck group generated by (n, t).

**The strip's contact graph.** Ring (i, j) lists E = h(i, j), N = v(i, j), W = h(i − 1, j), S = v(i, j − 1) = v(i, j + 1), and an arc goes
to the next contact counterclockwise on each of the two rings, so

  h(i, j) → v(i, j), v(i + 1, j + 1);  v(i, j) → h(i − 1, j), h(i, j + 1).

Arcs alternate the two kinds, and two arcs from a contact x(i, j) of either kind reach x(i − 1, j), x(i + 1, j), and x(i, j + 1) by two
different walks. So in **moves** (pairs of arcs between contacts of one kind), a move changes i by ±1 keeping the level, or flips the level
keeping i, in two ways. Hence, between contacts of one kind, the least number of moves from (i, j) to (0, 0) is |i| + [j ≠ 0], and the
shortest walks number 1 when j = 0 (every move goes the same way) and 2(|i| + 1) when j = 1.

**Distances to h(0, 0).** From the moves: h(i, 0) at 2|i| with 1 route; h(i, 1) at 2|i| + 2 with 2|i| + 2. A v contact first steps to
h(i − 1, j) or h(i, j + 1): v(i, 0) at 2i − 1 with 1 route for i ≥ 1, and at 2|i| + 3 for i ≤ 0; v(i, 1) at 2|i| + 1 with 1 route for i ≤ 0,
and at 2i + 1 for i ≥ 1. Taking the least over each ring's four contacts:

| Ring lift | Least distance | Its only contact there |
| --- | --- | --- |
| (i, 0), i ≥ 2 | 2i − 2 | W = h(i − 1, 0), one route |
| (i, 0), i ≤ −1 | 2\|i\| | E = h(i, 0), one route |
| (i, 1), i ≥ 1 | 2i − 1 | S = v(i, 0), one route |
| (i, 1), i ≤ 0 | 2\|i\| + 1 | N = v(i, 1), one route |

(the rings (0, 0) and (1, 0) hold the target). In each row the other three contacts are strictly farther, by the values above.

**Distances to v(0, 0).** The same moves give v(i, 0) at 2|i| with 1 route and v(i, 1) at 2|i| + 2. An h contact first steps to v(i, j) or
v(i + 1, j + 1): h(i, 0) at 2i + 1 with 1 route for i ≥ 0 and at 2|i| + 1 for i ≤ −1; h(i, 1) at 2|i| − 1 with 1 route for i ≤ −1 and at
2i + 3 for i ≥ 0. So:

| Ring lift | Least distance | Its only contact there |
| --- | --- | --- |
| (i, 0), i ≥ 1 | 2i − 1 | W = h(i − 1, 0), one route |
| (i, 0), i ≤ −1 | 2\|i\| | N = v(i, 0), one route |
| (i, 1), i ≥ 1 | 2i | S = v(i, 0), one route |
| (i, 1), i ≤ −1 | 2\|i\| − 1 | E = h(i, 1), one route |

(the rings (0, 0) and (0, 1) hold the target). Check 2a compares both tables with breadth-first counts on a long ladder.

**From the strip to the torus.** Every walk of the torus ending at c lifts uniquely to the strip ending at the target, so a contact e of a
ring X is at the least distance over e's lifts, and its number of shortest routes is the sum over the lifts attaining it
(`PLAIN-TIME-20261108-001B`, proof of Theorem 3). The lifts of X are X̃ + k(n, t). In both tables the least distance of a ring lift grows
strictly with |i| on each side, at either level, so of all of X's lifts at most two attain X's least distance d: the nearest on the side
i ≥ 1 and the nearest on the side i ≤ 0. Each lift of a contact of X lies on a lift of X, and a translation keeps a contact's role
(E, N, W or S).
- If one lift X̃ attains d, its only contact ẽ at distance d has one route in the strip, and every other lift of e lies on another lift of
  X, which is strictly farther than d; so e has one shortest route.
- If two lifts attain d, one on each side, their contacts at d have different roles: the side i ≥ 1 uses W or S, the side i ≤ 0 uses E or
  N, in both tables. They are therefore different contacts of X (Λ holds no unit vector, so a ring's four roles are four contacts), and
  each has its other lifts on lifts of X where it is not that lift's nearest contact, so strictly farther than d. Each has one route.
Either way some contact of X at distance d has an odd number of shortest routes, and X is on time. ∎

## Proof of Theorem 3

**n = 2.** Theorem 2.

**n, m ≥ 6.** `PLAIN-TIME-20261108-001B`, Theorem 3, with the square plane's ℓ = 4 and m = 4 contacts per ring: the torus is late once its
medial systole is at least 12. An arc changes u = x + y or w = y − x of a contact's midpoint by ±1, so a walk between a contact and its
translate by λ = (a, b) has at least |a + b| + |b − a| = 2 max(|a|, |b|) arcs; on nZ × mZ every nonzero λ has max(|a|, |b|) ≥ min(n, m) ≥ 6.

**n ∈ {3, 4, 5}, m ≥ 6.** The proof of `PLAIN-TIME-20261108-001B`, Theorem 3, uses only that walks lift uniquely and that distinct lifts of
a contact are at least 2ℓ + m apart, so it holds for any cover, here the cylinder Z_n × Z covering the n × m torus with deck group
⟨(0, m)⟩. Each cylinder has a late ring at distance 4 (check 3, read exactly on the n × 46 torus, whose distances and counts to radius 40
are the cylinder's): ℓ = 4 for widths 3, 4 and 5 (for width 3 through a v contact; an h contact is first late at 5). An arc moves a
contact by at most 1/2 along the cylinder, so lifts differing by (0, km), k ≠ 0, are at least 2m ≥ 12 = 2ℓ + 4 arcs apart, and the torus
is late.

**3 ≤ n ≤ m ≤ 5.** Read exactly (check 3): 3 × 3 is on time and 3 × 4, 3 × 5, 4 × 4, 4 × 5 and 5 × 5 are late. Check 3 also reads every
n × m with 2 ≤ n ≤ 10 and n ≤ m ≤ 40, and finds on time exactly the n = 2 column and 3 × 3, and four late tori at the cell level. ∎

## Proof of Theorem 4

The ring graph of Z_n × Z_m is the product of two cycles, so the distance from (0, 0) to (a, b) is |a|_n + |b|_m (circular distances), and
a row b with |b|_m ≤ r contributes the a with |a|_n ≤ r − |b|_m, of which there are f(r − |b|_m) with f(s) = min(n, 2s + 1). On the
cylinder the rows are b ∈ Z, so |B(r)| = f(r) + 2·Σ_(s < r) f(s), and |B(r + 1)| − |B(r)| = f(r + 1) + f(r). For r ≤ (n − 1)/2 no term is
cut and |B(r)| = 2r² + 2r + 1; once 2r + 1 ≥ n both terms are n. Check 4 confirms the closed form against breadth-first search on every
torus to 10 × 14 and every cylinder to radius 14, and the increments for n = 2 to 10 to radius 3n. By Theorem 1, δ(X → c) ≤ 2r exactly
when D(X, c) ≤ r, with D(X, c) the least ring distance from X to one of c's two rings; check 4 compares the two balls on 140 cases. ∎

## Remarks

- **What the band law makes, in distance.** A tube: the loop's n rings stay its girth while bands lengthen it, so balls grow as in the
  plane only out to half the loop and then linearly. Inserting bands the other way too would grow both sides, and the law does not say
  which way to go.
- **Thin reads plainly, thick needs freezing.** The ladder's rungs give two walks for every level flip, which cancel in pairs mod 2: walk
  parities on the ladder are those of a loop, and loops are on time (`PLAIN-TIME-20261108-001B`, Theorem 1). A tube of girth 3 to 5 already
  holds the plane's late configuration at distance 4.
- **Chirality again.** Among the tubes holding a vector of length √5, those holding (2, 1) are on time at every index read and their
  mirror images, holding (1, 2), are late from index 8: influence goes one way round every ring.
- **A correction.** `PLAIN-TIME-20261108-001B`, Theorem 4, said that every square, triangular or honeycomb torus other than its 26 is late.
  Its census and its systole bound (the shortest lattice vector at least √N) covered only the rotation-invariant tori; Theorem 2 and the
  computed families give infinitely many other tori on time. It holds for regular tori (`docs/CORRECTIONS.md`, 2026-11-09).

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependencies bound by hash | pass |
| 1 | Theorem 1: no twin corners at any stage (loops 3 to 12, ladders 2 to 40, tori to 12 × 20); isolated shortest routes at g·δ + 1 at the cell level, g = 2, 3 | pass: 316 pairs |
| 2a | Theorem 2: the strip's two tables against breadth-first counts, both targets | pass: 200 ring lifts |
| 2b | Theorem 2: every square torus holding (0, 2), n = 2 to 200, both twists; n × 2 at the cell level for n = 2 to 12, g = 2, 3 | pass: 398 tori, 9,152 pairs |
| 3 | Theorem 3: cylinders of width 3 to 5 late at 4; the small tori; every n × m to 10 × 40 | pass |
| 4 | Theorem 4: ring balls in closed form and their growth; time balls at even radius | pass |
| 5 | Computed: every torus of the three lattices to index 100, 80 and 50 | pass |
| 6 | The computed families at the cell level: a twisted ladder, a (2, 1) tube of index 41, a √3 triangular tube of index 40 | pass |

## Nonclaims

- **Stages, not growth in time.** Each stage is read as a fixed network (A42); a network that grows while it runs is not read here.
- **The (2, 1) and √3 tubes are computed**, to index 100 and 80, not proved at every size; the other on-time tori of small index are
  read, not explained.
- **Two-time knots only** (A30); equally spaced rings only.
