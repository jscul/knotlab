# Short loops rescue late rings: every torus that reads distance plainly

Status: Proved. Theorem 1 by hand; Theorem 2 by hand for the square tube and by a checked certificate for the triangular one; Theorem 3
by Theorems 1 and 2 and an exact census of every lattice below an explicit index bound. The finite claims are checked in `check.py`.

Ticket `RESCUE-MAP-20261109-001A`, 2026-11-09.

## Standard statement

- **Networks and readings.** Equally spaced rule-60 rings with law (12, 12) contacts, read through their contact graph: δ is the
  directed distance, and a ring is **on time** for a contact it does not hold when an odd number of shortest routes reach that contact
  from one of the ring's closest contacts (`DISTANCE-20261108-001B`, Theorem 4), **late** otherwise. A network is on time when every
  ring is on time for every contact it does not hold (`PLAIN-TIME-20261108-001B`).
- **Tori of every shape.** The square, triangular and honeycomb lattices of rings T, with m = 4, 6, 3 contacts per ring and first late
  distances ℓ = 4, 6, 5 (`PLAIN-TIME-20261108-001B`, Theorem 2). A **torus** is T modulo a sublattice Λ of Z² (the translations, of the
  A rings on the honeycomb) whose quotient joins no ring to itself; its **index** N is the number of rings, of A rings on the honeycomb.
  Coordinates: square rings at p with E, N, W, S contacts h(p), v(p), h(p − e1), v(p − e2); triangular rings with neighbours in the
  directions (1, 0), (1, 1), (0, 1) and their negatives, counterclockwise, so e1 and e2 meet at 120°; the honeycomb as in
  `HONEY-REACH-20261109-001A`, its e1 and e2 at 60°.
- **Tubes.** The **tube** of a lattice vector v is T/⟨v⟩, a network infinite in one direction that covers every torus whose lattice
  holds v. Its rings and contacts are read at a position along it, det(v, p) for v primitive.
- **Families.** The **ladder** vectors (2, 0) and (0, 2) and the **twist** vectors (2, 1) and (−1, 2) on the square lattice (a quarter
  turn apart within each pair; (1, 2) and (2, −1), the mirror images of the twist vectors, are not among them); the six vectors of length
  √3 on the triangular lattice, (1, −1), (2, 1), (1, 2) and their negatives, one orbit of the turn of 60°.

**Theorem 1 (the systole lemma for every cover).** Let C → M be a covering of networks, C with a ring late for a contact at directed
distance ℓ_C, and suppose distinct lifts of each contact of M are at least 2ℓ_C + m apart in C's contact graph with arcs taken both
ways. Then M is late.

**Theorem 2 (the twist and √3 tubes, and every torus they cover).**
1. In the tube of (2, 1) and in the triangular tube of (1, −1), every ring is on time for every contact, and its closest contacts are
   each reached by an odd number of shortest routes (by exactly one, in every case read).
2. Every square torus whose lattice holds a twist vector is on time, except the two of index 3, and every triangular torus whose lattice
   holds a vector of length √3 is on time.
3. The tube of (1, 2), the twist tube's mirror image, is late, first at distance 4. Along it the least distance climbs two at a time,
   and at each distance 2j one ring has its single closest contact reached by j shortest routes, so it is late whenever j is even (the
   counts computed on a window).

**Theorem 3 (every torus that reads distance plainly).**
- **Square.** A square torus is on time exactly when its lattice holds a ladder or twist vector, the two twist tori of index 3 apart, or
  it is one of 23 listed tori of index 5 to 17.
- **Triangular.** A triangular torus is on time exactly when its lattice holds a vector of length √3, or it is one of 85 listed tori of
  index 4 to 21.
- **Honeycomb.** A honeycomb torus is on time exactly when it is one of 15 listed tori of index 1 to 9 (2 to 18 rings).

The listed tori, by the canonical basis ((p, 0), (q, r)) of their lattice, are in `result.json`, check 6. The square ones are
((5,0),(3,1)); ((3,0),(1,2)), ((6,0),(4,1)); ((7,0),(4,1)), ((7,0),(5,1)); ((4,0),(2,2)), ((8,0),(3,1)), ((8,0),(5,1)); ((3,0),(0,3)),
((3,0),(1,3)), ((9,0),(5,1)), ((9,0),(6,1)), ((9,0),(7,1)); ((10,0),(3,1)), ((10,0),(7,1)); ((11,0),(3,1)), ((11,0),(7,1));
((3,0),(1,4)), ((12,0),(8,1)); ((13,0),(8,1)), ((13,0),(9,1)), ((13,0),(10,1)); ((17,0),(13,1)). The honeycomb ones are ((1,0),(0,1));
((3,0),(1,1)); ((2,0),(0,2)); ((2,0),(0,3)), ((2,0),(1,3)), ((3,0),(0,2)), ((3,0),(1,2)), ((6,0),(2,1)), ((6,0),(3,1)); ((7,0),(2,1)),
((7,0),(4,1)); ((4,0),(1,2)), ((8,0),(2,1)), ((8,0),(5,1)); ((3,0),(0,3)). The triangular ones number 1, 6, 2, 9, 7, 6, 6, 13, 5, 6, 9,
7, 3, 4 and 1 at index 4, 6, 7, …, 17, 19 and 21. The rotation-invariant lattices among all on-time tori are exactly
`PLAIN-TIME-20261108-001B`'s 9, 11 and 6 regular tori, with the square torus {4,4}_(1,1) of index 2 (two rings sharing four contacts),
below that census's range.

## Nearest known result

- **Covers and systoles.** The systole argument of `PLAIN-TIME-20261108-001B`, Theorem 3, which `GROWN-DISTANCE-20261109-001A` already
  applied to cylinders of the square torus; injectivity radius of quotients.
- **Certificates for shortest paths.** A function that vanishes at the target, drops by at most one along every arc and by exactly one
  along some arc out of every other vertex is the distance (the Bellman equations); shortest-path counts satisfy the same local
  recursion. Periodic graphs: distance in a quotient as the least over lifts.
- **Classification.** New as far as found for the question asked: which tori of the three regular lattices read distance across time
  plainly, with the ladders of `GROWN-DISTANCE-20261109-001A` as one family. The ingredients are classical.

## Proof of Theorem 1

The proof of `PLAIN-TIME-20261108-001B`, Theorem 3, uses only that walks of M lift uniquely to C from a chosen lift of their end, and that
distinct lifts of a contact are at least 2ℓ_C + m apart (`GROWN-DISTANCE-20261109-001A`, proof of Theorem 3). Let r̃ be late for c̃ in C
at distance ℓ_C. Every contact of r̃ is within ℓ_C + m − 1 of c̃, going round r̃ to its closest contact; for a deck transformation λ ≠ 1, a
walk from a contact ẽ of r̃ to λc̃ has at least (2ℓ_C + m) − (ℓ_C + m − 1) = ℓ_C + 1 arcs. So r's least distance to c in M is ℓ_C, attained
only through c̃, by r̃'s closest contacts, each with its even count from C, and r is late in M. ∎

## Proof of Theorem 2

**A certificate for an infinite tube.** On any network, functions d ≥ 0 and c (mod 2) on contacts are the directed distance to a target
t and the parity of its shortest routes when (i) d = 0 exactly at t and c(t) = 1; (ii) d(x) ≤ d(y) + 1 along every arc x → y; (iii) every
x ≠ t has an arc x → y with d(y) = d(x) − 1; (iv) c(x) is the sum of c(y) over the arcs x → y with d(y) = d(x) − 1. By (ii) and
induction along a shortest route, d ≤ δ; by (iii), following arcs on which d drops reaches t after d(x) arcs, so δ ≤ d; then (iv) is
the recursion for route counts, by induction on δ. On a tube, translation along it by P positions is a symmetry. If d and c are read
off a breadth-first search on a window |position| ≤ F and extended beyond it by d(x + P) = d(x) + Δ and c(x + P) = c(x) on each side,
every condition at a contact more than w positions past the window (w the largest change of position along an arc) is the condition at
the contact P positions nearer, shifted. So the conditions on the window and one period past it on each side hold everywhere. Check 3
finds such a periodic extension (P = 4, Δ = 4 for the square tube; P = 2, Δ = 3 for the triangular one) for every type of target contact
and verifies (i) to (iv) on it.

**The square tube by hand.** Index the rings of the tube of (2, 1) by a = x − 2y, so that ring a's neighbours are a ± 1 (through h
contacts) and a ∓ 2 (through v contacts). Two arcs move a contact of one kind by one lattice step, each once, so in the plane the
contacts of one kind at offset (q1, q2) are 2(|q1| + |q2|) arcs away with C(|q1| + |q2|, |q1|) shortest routes; in the tube the least
over lifts (q1 + 2k, q2 + k) is 2⌈|s|/2⌉ with s = q1 − 2q2, attained at one lift, with one route when s is even. A v contact first steps
to h(q + e2) or h(q − e1), an h contact to v(q) or v(q + e1 − e2). Taking the least over each ring's four contacts:

| Target | Rings | Least distance | Its closest contacts, one route each |
| --- | --- | --- | --- |
| h(0) | a ≥ 2 | a − 1 | W if a is odd, N if a is even |
| h(0) | a ≤ −1 | \|a\| | E if a is even, S if a is odd |
| v(0) | a ≥ 1 | a | W if a is odd, N if a is even |
| v(0) | a = −1 | 2 | N and S |
| v(0) | a ≤ −3 | \|a\| − 2 | E if a is odd, S if a is even |

(rings 0 and 1 hold h(0), rings 0 and −2 hold v(0)). In each row the ring's other contacts are strictly farther. Check 3's certificate
confirms the table for every ring.

**From the tube to its tori.** Every lattice holding (2, 1) is ⟨(2, 1), (N, 0)⟩, N its index, and its torus is the tube with ring a
identified with a + N. A contact of a torus ring X is at the least distance over its lifts, with the sum of their route counts at that
distance (Theorem 1's lifting). Every lift of a contact of X lies on a lift of X with the same role (E, N, W or S), and a lift of X whose
least distance exceeds X's contributes nothing.
- **One side.** On each side the least distance grows strictly with |a|, except that on the left, for v(0), ring −1 (distance 2) ties
  ring −4, three positions away. So for N ≥ 4 two lifts on one side never tie.
- **Two sides.** If the nearest lifts on the two sides tie, their closest contacts have different roles: the right side uses W or N, the
  left E or S, and ring −1, the one ring using N on the left, also uses S. So some closest contact of X is attained at one lift only, with
  one route, and X is on time.
For N ≥ 4 every ring is on time; N = 4 is also a ladder. By the quarter turn, an orientation-preserving symmetry of the square lattice
carrying (2, 1) to (−1, 2), the same holds for every lattice holding (−1, 2). The two tori of index 3 are late (check 6).

**The triangular tube, and the general quotient argument.** For a tube with a certificate, check 3 reads every ring's least distance,
closest roles and their parities over the window and one period past it, so everywhere, and verifies: (Q1) the least distance grows
strictly on each side beyond the window, and two lifts on one side N ≥ N1 apart never tie (N1 = 11 for the square tube, 6 for the
triangular); (Q2) no set of closest roles occurs on both sides; (Q3) every closest contact has an odd number of routes. Then, for
N ≥ N1, at most one lift on each side attains X's least distance; if two do, Q2 gives a closest role of one that is not closest at the
other, and that contact's count is its count at one lift, odd by Q3. So every torus of index at least N1 holding the vector is on time,
and those of smaller index are read exactly in check 6. By the turn of 60°, the same holds for every vector of length √3.

**The mirror tube.** Check 4 builds the certificate for the tube of (1, 2) and finds Q3 false, and check 5 reads its late ring at
distance 4 exactly. Along it the least distance climbs two at a time (2, 2, 4, 4, … on one side of h(0)), and of the two rings at
distance 2j the first has its single closest contact reached by j routes (computed on the window). ∎

## Proof of Theorem 3

**Arcs move little (check 2).** An arc of the square lattice changes u = x + y or w = y − x of a contact's midpoint by ±1, so a walk between
a contact and its translate by λ has at least β(λ) = |λ1 + λ2| + |λ2 − λ1| = 2·max(|λ1|, |λ2|) arcs. On the triangular lattice an arc moves
a midpoint by 1/2 (unit ring spacing) and on the honeycomb by √3/2 (unit edges, A rings √3 apart), so β(λ) = 2|λ| in units of the lattice
of rings: |λ|² = λ1² − λ1λ2 + λ2² and λ1² + λ1λ2 + λ2², respectively.

**Short tubes (check 5).** Every nonzero v with β(v) < 2ℓ + m (12, 18 and 13) that is not a family vector either joins a ring to itself
(the units) or has a tube with a ring late at distance ℓ_v ≤ ℓ: ℓ_v is 2 for (1, ±1) and 4 otherwise on the square lattice, 6 on the
triangular, and 2, 3 or 5 on the honeycomb; 54, 141 and 75 tubes.

**The bound.** Let Λ hold no family vector and have index N above 50 (square), 93 (triangular) or 48 (honeycomb). If every nonzero λ ∈ Λ
has β(λ) ≥ 2ℓ + m, the torus is late by `PLAIN-TIME-20261108-001B`, Theorem 3. Otherwise take v ∈ Λ with β(v) < 2ℓ + m, primitive in Λ
(dividing only shortens it). Its tube is late at ℓ_v ≤ ℓ, and every λ ∈ Λ outside Zv has |det(v, λ)| a nonzero multiple of N. Since
|det(v, λ)| ≤ β(v)β(λ)/2 on the square lattice and ≤ β(v)β(λ)/(2√3) on the other two, β(λ) < 2ℓ_v + m would give N ≤ 50, 93 or 48. So
distinct lifts in the tube of a contact, which differ by such λ, are at least 2ℓ_v + m apart, and the torus is late by Theorem 1.

**The census (check 6).** Every lattice of index up to 50, 93 and 48 (each once, by its canonical basis, so both chiralities), 11,151 in
all, is read exactly. The on-time tori are the family tori, all but the two twist tori of index 3, and the listed ones, of index at most
17, 21 and 9. With Theorem 2 for the families above those indices and the bound for the rest, the classification is complete. ∎

## Remarks

- **How a short loop rescues.** The plane is late at distance ℓ because two shortest routes tie at a ring's single closest contact. A
  torus holding a family vector closes the plane into a tube along which the fastest way to every ring is a single route: in the twist
  tube the least distance grows by one per ring, and every closest contact is reached in one way. The rescue is not a third route that
  makes the count odd; it is a strictly shorter, unique route round the short loop, which makes a different contact the closest.
- **Why the mirror image fails.** In the tube of (1, 2) the fastest way climbs two rings per two arcs and can take its side step at any
  of j places, so the closest contact's count is j and even at every other step. Rule 60 reads one way round every ring, so a tube and its
  mirror image are different substrates; which short loops rescue depends on how they wind against the reading direction.
- **The honeycomb has no thin family.** Every honeycomb tube is late, by distance 5 at the latest, so only finitely many honeycomb tori
  read distance plainly, all with at most 18 rings.
- **Relation to the grown torus.** `GROWN-DISTANCE-20261109-001A` proved the ladders and computed the twist and √3 families to index 100
  and 80 and the bounds 17, 21 and 9; here the families are proved at every index and the bounds hold for every torus.

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependencies bound by hash | pass |
| 1 | `rescue_lib`'s quotient reading agrees with `loopnet_lib`'s (through `plain_lib`) on every lattice of index up to 24, all three lattices | pass: 1,473 tori |
| 2 | One arc moves a contact's midpoint by exactly 1 in u + w (square), 1/2 (triangular), √3/2 (honeycomb) | pass |
| 3 | Theorem 2: tube certificates for (2, 1) (both targets) and the triangular (1, −1) (three targets): conditions (i) to (iv), agreement with the search, Q1 to Q3 | pass |
| 4 | Theorem 2, part 3: the certificate of the tube of (1, 2) holds and Q3 fails (its late ring is check 5's) | pass |
| 5 | Every short non-family tube is late within ℓ, or joins a ring to itself | pass: 270 tubes |
| 6 | The census of every lattice to index 50, 93 and 48: the on-time tori are the family tori (the two twist tori of index 3 late) and the listed ones; the rotation-invariant on-time lattices number 10, 11 and 6 | pass: 23, 85 and 15 listed |
| 7 | Computed: every closest contact of the two tubes, on the 241 rings within 120 positions of the target, has exactly one shortest route | pass |

## Nonclaims

- **Tori of the three regular lattices only.** Maps of higher genus are not classified here (`PLAIN-TIME-20261108-001`: 141 of 706 on
  time).
- **Exactly one route** at every closest contact of the tubes is computed on a window; the parities are proved everywhere.
- **Two-time knots only** (A30); equally spaced rings only.
