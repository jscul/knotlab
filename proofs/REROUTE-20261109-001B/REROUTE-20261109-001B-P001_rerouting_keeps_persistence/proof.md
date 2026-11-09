# Re-routing keeps persistence, and the plain reading needs long rings

Status: Theorems 1, 2 (square) and 3 proved by hand, their finite claims checked in `check.py`; the triangular and honeycomb lines are
computed.

Ticket `REROUTE-20261109-001B`, 2026-11-09.

## Standard statement

- **Networks.** Maps as dart permutations σ (`REROUTE-20261109-001A`), read as networks of equally spaced rule-60 rings with law-(12, 12)
  contacts: a contact persists exactly when its closed walks in the contact graph are even in number at every length
  (`LOOP-NET-20261108-001A`, Theorem 2 (a)). A ring's plain first need is **on time** for a target contact when one of the ring's
  contacts closest to the target has an odd number of shortest routes to it (`PLAIN-TIME-20261108-001B`); a network is on time when
  every ring is, for every target.
- **Re-routing.** At a contact the two rings cross. **Re-routing** at a set S of contacts exchanges, at each of them, which ring each
  arriving ring continues on: σ_S = τ_S σ, where τ_S swaps the two darts of every contact in S. The result is a network when no contact
  then joins a ring to itself.
- **Lines.** The **line network** of a torus re-routes it at every contact of one direction class: the vertical contacts of the square
  torus, one of the three classes of the triangular torus, two of the three of the honeycomb.
- **Square coordinates.** On the square lattice, H(q) is the contact from ring q towards q + e1 and V(q) the one towards q + e2. The
  contact graph has the arcs H(q) → V(q), H(q) → V(q + e1 − e2), V(q) → H(q − e1) and V(q) → H(q + e2), so two arcs take H(q) to
  H(q ± e1) or H(q ± e2), each by one route.

**Theorem 1 (re-routing keeps persistence).** Re-routing at any set S keeps every arc of the contact graph, so every count of walks,
every contact's persistence, its doubled pairs and its contact-graph flips (`REROUTE-20261109-001A`). Conversely the maps with the
contact graph of σ are exactly its 2^E re-routings. Re-routing is the partial duality of ribbon graphs (Chmutov): σ_S has as many rings
as the ribbon subgraph on S has boundary components.

**Theorem 2 (lines read their distance plainly).** The line network of the n × n square torus, n ≥ 3, has 2n rings, each a staircase
of 2n contacts running once round the torus; its ring graph is a cycle, so a ball of radius r holds 2r + 1 rings; every contact persists
(Theorem 1), and it is on time: for every ring and target, a closest contact is reached by exactly one shortest route. Computed: the same
holds for the line networks of the triangular and honeycomb n × n tori, n = 3 to 20.

**Theorem 3 (small rings are late on the square contact graph).** Let k ≥ 2 and let a network have the contact graph of a square torus
whose lattice has no nonzero vector of taxicab length below 2^(k+3). Then a ring whose contacts all lie in a box of 2^k − 2 by 2^k − 2
rings is not on time. Hence a network with the contact graph of the n × n square torus, n ≥ 64, that is on time has every ring of at
least n/8 − 4 contacts, so at most 64n rings, where the torus has n²: its rings are lines, not a plane of rings.

## Nearest known result

- **Partial duality.** Chmutov's partial duals of ribbon graphs (2009) share their medial graph (Ellis-Monaghan and Moffatt, *Graphs on
  Surfaces*, 2013); our contact graph is the medial graph directed by the orientation. Theorem 1 is that observation applied to
  persistence.
- **Binomial coefficients mod 2.** Lucas's theorem: C(a + b, a) is odd exactly when a and b share no binary digit.
- **The program's tori.** `RESCUE-MAP-20261109-001A` and `GROW-PLAIN-20261109-001B`, Theorem 2: tori of the three lattices read their
  distance plainly at large size only as tubes. Theorem 3 says the same of every re-routing of the square torus, whatever its rings.
- **Classification.** Known-with-delta for Theorem 1; new as far as found for Theorems 2 and 3 as readings of these networks.

## Proof of Theorem 1

An arc goes from contact(d) to contact(σ_S d) = contact(τ_S σ d) = contact(σ d), since τ_S moves a dart only within its contact; the
arcs, with their multiplicities, are unchanged, and everything `REROUTE-20261109-001A` and `LOOP-NET-20261108-001A` read is a function
of them. Conversely, if contact(σ′d) = contact(σd) for every dart, then σ′d is σd or its partner, and since σ′ is a bijection the two
darts arriving at a contact either both keep or both swap: σ′ = τ_S σ. Check 1 confirms both on 3,000 random re-routings and every map
to three contacts, and that the ring count of σ_S is the number of boundary components of the ribbon subgraph on S, which is how
Chmutov's partial dual G^S is defined. ∎

## Proof of Theorem 2

**The rings.** At a vertical contact V(q) a ring arriving from H(q) continues, after re-routing, round the upper ring q + e2 to
H(q + e2), and at the horizontal contact it turns round q + e2 again to V(q + e2): the ring U_x holds H(x, y) and V(x, y) for every y.
The ring arriving at V(q) from above continues round q to H(q − e1), then to V(q − e2): the ring D_x holds V(x, y) and H(x − 1, y). So
there are n rings of each kind, each of 2n contacts, U_x meets D_x and D_(x+1) only, and the ring graph is the cycle
U_0, D_1, U_1, D_2, …, of 2n rings.

**Single routes.** In the plane a shortest route between H contacts counts C(|a| + |b|, |a|) by the two-arc structure above, one route
when it runs along a row or column. For a target H(p) and a = x − p_x, the closest contact of U_x is V(x, p_y) at distance 2a − 1 when
a ≥ 1 and H(x, p_y) at distance −2a when a ≤ 0; that of D_x is H(x − 1, p_y) at distance 2(x − 1 − p_x) when x − 1 ≥ p_x and
V(x, p_y − 1) at distance 2(p_x − x) + 1 otherwise. Each is the only contact of its ring at that distance and is reached by one route
along row p_y. For a target V(p), whose two in-arcs come from H(p) and H(p − e1 + e2), the same count gives a unique closest contact with
one route along row p_y or p_y + 1. On the torus the ring is a whole column, so only the target's lifts across the line matter; the
closest contacts towards the lifts on either side lie at distances of opposite parity, so they never tie, and the vertical lifts are
farther. Check 2 reads every target and ring on every n × n torus from 3 to 32, both line networks (horizontal and vertical): every ring
on time, with a closest contact of exactly one route, and the ring balls 2r + 1. Check 3 reads the triangular and honeycomb line networks
from 3 to 20 the same way (108 networks), all on time with single routes. ∎

## Proof of Theorem 3

**An even box.** Take the target H(p) and a contact H(q) or V(q) with q − p in [2^k + 1, 2^(k+1) − 2]². For H(q) both coordinates of
q − p have bit k set, so C(a + b, a) is even by Lucas's theorem. V(q)'s two out-arcs lead to H(q − e1) and H(q + e2), with offsets
(a − 1, b) and (a, b + 1) in [2^k, 2^(k+1) − 1]², both even, so V(q)'s count, the sum over the closer of them, is even too. On the torus
the other lifts of the target are farther: a lattice vector of taxicab length at least 2^(k+3) leaves at least 2^(k+2) + 4 > a + b, so
the counts are the plane's.

**Small rings.** If a ring's contacts lie in a box of 2^k − 2 by 2^k − 2 ring positions with corner c, choose p = c − (2^k + 1, 2^k + 1):
all its contacts lie in the even box, so its closest contacts all have even counts and it is not on time for H(p).

**Few rings.** Each arc moves a contact's position by at most one in each coordinate, so a ring that fits in no such box spans
2^k − 2 or more in some coordinate and has at least 2(2^k − 2) contacts, or wraps round the torus and has at least n. On the n × n torus
take the largest k with 2^(k+3) ≤ n, so 2^(k+1) > n/8; the rings' sizes sum to 4n², twice the number of contacts, so there are at most
4n²/(n/8 − 4) ≤ 64n of them for n ≥ 64. Check 4 confirms the even box on the tori of side 32 and 64, and that every ring in such a box is
late at the predicted target: 120 rings sampled on the 32 × 32 torus, on two random re-routings of it, and on one of the 64 × 64. ∎

## Remarks

- **Persistence and the plain reading live at different levels.** The contact graph decides persistence and every walk count; the rings
  decide which contacts a ring's distance is read from. Re-routing changes only the second. So persistence without flips is cheap: any
  re-routing of a torus keeps every contact persistent and usually has no symmetry at all (`REROUTE-20261109-001C`).
- **What reads plainly is a line.** The line networks are on time by the mechanism `RESCUE-MAP-20261109-001A` found on tubes: a single
  fastest way, here straight across to the line. Their ring graph is a cycle, so they read a line's distance, though their contacts fill
  the plane. Theorem 3 shows that on the square contact graph nothing with small rings does better: reading plainly needs rings that
  span the torus.
- **A plane still needs freezing (A41).** Among networks with the square contact graph, Theorem 3 rules out a plane of small rings read
  plainly, whatever the re-routing. The triangular and honeycomb contact graphs are only computed (`REROUTE-20261109-001C`).

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependencies bound by hash | pass |
| 1 | Theorem 1: 3,000 random re-routings keep every arc and every contact's persistence; ring counts match Chmutov's boundary components; every map to three contacts shares its contact graph with exactly 2^E maps | pass |
| 2 | Theorem 2: square line networks n = 3 to 32, both directions, on time with single fastest ways, 2n rings of 2n contacts, balls 2r + 1; the reading agrees with `plain_lib.verdicts` on small tori | pass |
| 3 | Computed: triangular (one class) and honeycomb (two classes) line networks n = 3 to 20, on time with single fastest ways | pass: 108 networks |
| 4 | Theorem 3: the even box on tori of side 32 and 64; rings in a box of side 2^k − 2 late at the predicted target | pass: 480 of 480 |

## Nonclaims

- **Theorem 3 is for the square contact graph.** The triangular and honeycomb contact graphs are read by census only.
- **The bound 64n is not sharp**; the lines have 2n rings.
- **Two-time knots only** (A30); equally spaced rings only; each network read as fixed (A42).
