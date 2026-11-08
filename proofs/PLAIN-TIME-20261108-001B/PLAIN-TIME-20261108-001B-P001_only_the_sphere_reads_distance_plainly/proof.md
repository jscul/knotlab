# Only the sphere reads distance plainly at every size

Status: Proved by hand where marked; checks 3 and 5 of `check.py` and the census of ticket A are computations.

Ticket `PLAIN-TIME-20261108-001B`, 2026-11-08.

## Standard statement

- **Networks and readings.** Networks of equally spaced rule-60 rings with law (12, 12) contacts, read through their contact graph Γ
  (`DISTANCE-20261108-001B`): δ(r → c) is the directed distance from ring r to contact c, and the plain first need of c on r is
  **on time** when it comes at lag g·δ + 1, which by `DISTANCE-20261108-001B`, Theorem 4, happens exactly when an odd number of shortest
  routes arrive at c from one of r's contacts at distance δ(r → c). A ring is **late** for c otherwise, and a network is **on time**
  when every ring is on time for every contact.
- **Maps.** A regular map of type (m, f) has m contacts per ring and f per face. Its universal cover is the tessellation T of type
  (m, f): the plane's square, triangular or honeycomb lattice when 1/m + 1/f = 1/2, a tessellation of the hyperbolic plane when
  1/m + 1/f < 1/2. The map is the quotient of T by a group of its rotations acting freely, which maps T's contact graph onto Γ.
- **Systole.** The **medial systole** of a quotient is the least distance, in T's contact graph with arcs taken in both directions,
  between two distinct lifts of one contact. ℓ(T) is the least directed distance at which some ring of T is late for some contact.

**Theorem 1 (the sphere).** Every loop of rings and every pair of rings sharing any number of contacts is on time. So are the five
Platonic networks (checked exactly). Every spherical regular network is therefore on time.

**Theorem 2 (the square plane is late at distance 4).** In the square lattice of rings, take the contact h(0) joining rings 0 and e1,
and the ring X at (2, −1). Its contacts are at directed distances 4, 5, 6 and 7 from h(0), and the closest one, h(1, −1), has exactly two
shortest routes to h(0). So X is late for h(0), first needed at distance 5, and ℓ = 4 for the square plane. The triangular plane has
ℓ = 6 and the honeycomb plane ℓ = 5 (computed exactly).

**Theorem 3 (the systole lemma).** If a quotient M of a tessellation T of type (m, f) has medial systole at least 2ℓ(T) + m, then M is
late.

**Theorem 4 (the tori).** A square, triangular or honeycomb torus is on time exactly when it is one of the following lattices (vectors v
spanning the lattice with their rotations, both chiralities listed), and every other torus is late:
- **square**, 9 lattices: (2, 0); (2, 1) and (2, −1); (2, 2); (3, 0); (3, 1) and (3, −1); (3, 2); (4, −1), of index 4, 5, 5, 8, 9, 10,
  10, 13 and 17;
- **triangular**, 11 lattices, of index 3, 4, 7, 7, 9, 12, 13, 13, 16, 19 and 21;
- **honeycomb**, 6 lattices, of index 1, 3, 4, 7, 7 and 9.
The proof is Theorem 3 for every torus of index at least 72 (square), 81 (triangular) or 43 (honeycomb), and the exact readings of every
smaller torus, both chiralities (check 4).

**The first failing map.** The smallest regular map that is late is the twisted square torus {4,4}_(2,3) (the lattice spanned by
(2, 3) and (−3, 2), 13 rings): every contact has exactly one late ring, at δ = 4, first needed at κ = 5 (lags 11 and 16 at g = 2 and 3,
read at the cell level on all 338 ring–contact pairs, check 6). Its mirror image {4,4}_(3,2) is on time. So no criterion by type,
genus, curvature or size decides a finite map: mirror images differ, since influence goes one way round every ring. The first failure
from a non-abelian group is the map of S5 with six contacts per ring and square faces (genus 6, 20 rings), late at distances 5 and 6.

**Computed (the covers' horizon).** In the cover of type (m, f), with L = lcm(m, f), the first contact reached by two shortest routes
comes at τ = L − L/m − L/f + 1 (two such contacts, two routes each; the law found by the coordinator, re-read here on 10 types, check 7),
and the first late ring comes at τ + 1, or τ + 2 when the faces are triangles and the rings larger (all 39 covers read, check 5, and the
stress test). For coprime m, f this is (m − 1)(f − 1) + 1, which predicted ℓ = 21 for (5, 6) and (6, 5), 25 for (3, 13) and 26 for (13, 3)
before they were read. So by Theorem 3 every regular map is late once its medial systole reaches 2ℓ + m. Below that bound the answer
depends on how the map wraps: the census of ticket A finds 141 of 706 maps of genus at least 2 on time, and maps can be late before
their cover is (the map of S5, late at 5 with ℓ = 9) or on time after it.

## Nearest known result

- **Counting geodesics.** Geodesic counts and their growth in Coxeter and triangle groups and in tessellations (growth series,
  automatic structures); Lucas' theorem for the flat case (`DISTANCE-20261108-001B`, Theorem 4).
- **Covers and systoles.** Injectivity radius and systoles of regular maps and of finite quotients of triangle groups; maps of
  PSL(2, q) (Macbeath; Conder's census of regular maps).
- **Classification.** New as far as found for the question asked (when the parity of shortest routes in a directed medial graph never
  hides the distance); the ingredients are classical.

## Proof of Theorem 1

**Loops.** In a loop of k rings each ring has two contacts, so the corner after c_(i−1) on ring i leads to c_i and the corner after c_i
leads back to c_(i−1): Γ is the cycle c_0, …, c_(k−1) with arcs both ways. From a contact at cyclic distance d < k/2 from the target
there is one shortest route; at d = k/2 (k even) there are two. A ring {c_(i−1), c_i} has its two contacts at cyclic distances differing
by one, and the nearer is at distance below k/2, or both are at the same distance only when that distance is below k/2. So its nearest
contact has a single shortest route and the ring is on time. **Two rings sharing k contacts.** Each ring holds every contact, so every
ring holds the target and is on time at distance 0. **Platonic networks.** Check 1, exact.

## Proof of Theorem 2

By `DISTANCE-20261108-001B`, Theorem 4, part 1, with u = x + y and w = y − x: the ring X = (2, −1) has contacts h(1, −1), v(2, −1),
h(2, −1) and v(2, −2), whose displacements (Δu, Δw) to h(0) give, by the closed forms, directed distances 4, 5, 6 and 7. The closest,
h(1, −1), is of h's kind at lattice offset (1, −1) from h(0), whose shortest routes number C(2, 1) = 2 (Theorem 4, part 3). So no contact
of X at distance 4 has an odd count, X is late, and its first need comes through v(2, −1) at distance 5, which has three routes. No ring is late below distance 4 (check 2 reads the plane exactly: a 41 × 41 torus within a third of its side).

## Proof of Theorem 3

Let r̃ be a ring of T late for the contact c̃ at distance ℓ, and let r and c be their images in M. Every walk of Γ ending at c lifts
uniquely to a walk of T ending at c̃ from the matching lift of its start, so for a contact e of r with lift ẽ on r̃, δ_M(e → c) is the
least δ_T(ẽ → λc̃) over the deck transformations λ, and the number of shortest routes is the sum over the λ attaining it.
- The contacts of r̃ lie within ℓ + m − 1 of c̃: from any of them, going round r̃ reaches its closest contact in at most m − 1 arcs.
- For λ ≠ 1, a walk from ẽ to λc̃ has length at least the undirected distance, which is at least the systole minus the undirected
  distance from c̃ to ẽ: δ_T(ẽ → λc̃) ≥ (2ℓ + m) − (ℓ + m − 1) = ℓ + 1.
So r's least distance to c is ℓ, attained only through the lift c̃, by the contacts of r̃ at distance ℓ, each with its even count from T.
r is late in M. ∎

## Proof of Theorem 4

**The bounds.** An arc of the contact graph of the plane lattices turns a contact about one of its rings by 2π/m, which moves its
midpoint by |ρ − 1|/2 with ρ = e^(2πi/m) (`DISTANCE-20261108-001B`, proof of Theorem 5): √2/2 on the square lattice, 1/2 on the
triangular and √3/2 on the honeycomb (unit spacing between neighbouring rings, or unit edges). Lifts of a contact differ by a vector of
the torus's lattice, of length at least √N for a square or triangular torus of index N and √(3N) for a honeycomb torus. So the medial
systole is at least √2·√N, 2√N and 2√N. With ℓ = 4, 6, 5 and m = 4, 6, 3, Theorem 3 applies once √2·√N ≥ 12, 2√N ≥ 18 and 2√N ≥ 13, that
is for N ≥ 72, 81 and 43.

**The small tori.** Check 4 builds every rotation-invariant sublattice of index up to 400, 300 and 200 (each lattice once, by its
canonical basis, so both chiralities), 612 tori in all, and reads each exactly: the on-time ones are the lists above, and every torus
of index at least 72, 81 or 43 is late, as Theorem 3 requires. ∎

## Remarks

- **The tie.** The two routes of the first tie bound a disc, one running along ring corners and the other along face corners; with k
  ring cells and j face cells inside, equal lengths force km = jf ≥ L (the coordinator's argument; that no shorter tie exists is
  computed, not proved).
- **Why the sphere.** The plain first need is the light cone filtered by the parity of shortest routes. On the sphere the networks are
  loops, pairs of rings, or small; on the flat lattices shortest routes multiply binomially and the first ring whose closest contacts all
  receive an even number appears at distance 4, 5 or 6; on hyperbolic lattices routes multiply too, but rings are rescued much longer,
  up to (m − 1)(f − 1) + 1 when m and f are coprime.
- **Chirality.** Mirror images can differ, since influence goes one way round every ring: the square torus of index 17 is on time in one
  chirality only, and so are the triangular tori of index 19 and 21.
- **Wrap-around both ways.** Finite quotients can be late before their cover is (the 20-ring map of S5, late at 5 with ℓ = 9) or on
  time after it (maps of PSL(2, 29) with diameter 16 and 17): below the systole bound, the answer depends on the map.

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependencies bound by hash, ticket A's frozen files among them | pass |
| 1 | Theorem 1: loops of 2 to 200 rings and pairs sharing 2 to 200 contacts; the spherical maps of A4, S4 and A5 | pass |
| 2 | Theorem 2: the square plane's first late ring at distance 4 with counts 2, 3, 3, 6; the triangular plane at 6 and the honeycomb at 5 | pass |
| 3 | Computed: the first late distance of 39 covers, two primes each (spherical ones none; flat ones as in check 2) | pass |
| 4 | Theorem 4: 312 square, 178 triangular and 122 honeycomb tori, every lattice and chirality up to index 400, 300 and 200 | pass |
| 5 | Computed: every cover's first late ring at τ + 1 (τ + 2 for triangular faces and larger rings), the six read only to radius 12 to 14 consistent | pass |
| 6 | The twisted square torus {4,4}_(2,3): 26 late pairs (δ 4, κ 5), cell-level lags 11 and 16; its mirror image on time | pass |
| 7 | Computed: the first tie at τ on 10 covers, two primes each, two tied contacts of two routes | pass |

## Nonclaims

- **Regular maps, tori and loops only.** Irregular networks of persistent contacts are not classified.
- **The hyperbolic covers are computed**, by balls in PSL(2, p) for two large primes; the formulas for ℓ are patterns, not theorems.
- **Two-time knots only** (A30).
