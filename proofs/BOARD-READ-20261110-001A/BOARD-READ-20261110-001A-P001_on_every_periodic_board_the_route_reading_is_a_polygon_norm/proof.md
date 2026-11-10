# On every periodic board the route reading is a polygon norm up to a constant

Status: Proved by hand. `check.py` checks the theorem's bounded error on four boards; the boards' polygons are ticket B's.

Ticket `BOARD-READ-20261110-001A`, 2026-11-10. The statement was frozen in `f69403540` before this proof was written.

## Standard statement

- **Boards.** A board is a connected locally finite map in the plane, periodic under a lattice Λ ≅ Z² with finite quotient: rings at
  its vertices, a contact at each edge, ring v carrying deg(v)·g cells with its contacts every g cells in counterclockwise order, rule
  60 on own cells and law (12, 12) at contacts, as in `LOOP-NET-20261108-001`'s networks. The **route digraph** Γ has the cells as
  vertices and an arc from each cell to the next cell on every ring it lies on; the **route reading** T(c, c') is its directed
  distance, the time length of `CONF-METRIC-20261110-001A`. The **ring graph** G has the rings as vertices and the contacts as edges.
  x(c) is the lattice position of the fundamental-domain copy holding c's ring.
- **Theorem.** Let Q = Γ/Λ, a finite digraph whose arcs carry displacements in Λ, and let P = conv{disp(C)/len(C)} over the simple
  cycles C of Q. Then 0 is interior to P, its gauge N(v) = min{t ≥ 0 : v ∈ tP} is an asymmetric norm whose unit ball is the polygon P,
  and there is a constant K (depending on the board and g) with |T(c, c') − N(x(c') − x(c))| ≤ K for all cells c, c'. The same holds
  for the ring graph G with its own polygon P_G (cycles not reusing an edge).
- **Corollary.** No periodic board's route reading or graph distance is round: each is, up to a constant, a norm whose unit ball is a
  polygon.

## Proof

**N is the gauge of P.** Writing μ_C = λ_C len(C), the linear programme N(v) = min{Σ λ_C len(C) : λ ≥ 0, Σ λ_C disp(C) = v} over simple
cycles becomes min{Σ μ_C : μ ≥ 0, Σ μ_C p_C = v} with p_C = disp(C)/len(C), which is the gauge of conv{p_C}. Any closed walk of Q splits
into simple cycles, so the same value is reached over all closed walks.

**0 is interior.** Γ is strongly connected: a cell runs round its ring to any of its contacts and crosses there to the next ring, and
the board is connected. So for each of ±e_1, ±e_2 there is a walk from a cell to its translate by that vector, a closed walk of Q with
that displacement, and P contains a positive multiple of each. Hence N is finite and positive away from 0, positively homogeneous and
subadditive, an asymmetric norm, and its unit ball is the polygon P (the hull of finitely many points).

**Lower bound.** Take a walk W in Γ from c to c' of length T(c, c'); its image in Q is a walk from [c] to [c'] with displacement
v = x(c') − x(c) up to a bounded fundamental-domain offset. Removing simple cycles one at a time leaves a simple path R of Q, of length at
most |Q| and displacement of norm at most a constant D. The removed cycles have total length at least N of their total displacement
v − disp(R), so T(c, c') ≥ N(v − disp(R)) ≥ N(v) − N(disp(R)) ≥ N(v) − K₁ by subadditivity.

**Upper bound.** The programme has two equality constraints, so an optimal basic solution uses at most two simple cycles C₁, C₂:
v = λ₁ d₁ + λ₂ d₂ with λ_i ≥ 0 and N(v) = λ₁ ℓ₁ + λ₂ ℓ₂ (Carathéodory). Walk from c to a lift of C₁ (bounded length), round it ⌊λ₁⌋
times, to a lift of C₂ (bounded), round it ⌊λ₂⌋ times, then to c'. The last leg covers a displacement bounded by the fractional parts
and the connectors, and between cells at bounded displacement Γ's distance is bounded (finitely many cases up to translation). So
T(c, c') ≤ ⌊λ₁⌋ℓ₁ + ⌊λ₂⌋ℓ₂ + K₂ ≤ N(v) + K₂.

The same argument applies to the ring graph G, with walks that do not immediately reuse an edge. ∎

## Remarks

- **The four boards (ticket B).** On the square, triangular, honeycomb and kagome boards at g = 2 to 6, P is exactly (g·d/2)^−1 times
  P_G, d the ring degree (4, 6, 3, 4): the route reading is the board's graph distance times g·d/2, up to a constant. A ring of degree d
  is crossed, on average over the directions a shortest path takes, by going half way round it.
- **Why half way, for round trips.** Entering a ring through one contact and leaving through another k slots further counterclockwise
  costs kg; the reverse trip enters through the second and leaves through the first, d − k slots on. So a ring path and its reverse cost
  together g·d per internal ring: on a d-regular board the round trip is at most g·d times graph distance plus a constant, for every
  board. That the one-way reading has the graph polygon's shape, as on the four boards, is computed, not proved in general.
- **Under growth.** `CONF-METRIC-20261110-001A` shows that on the square board growth adds, in conformal time, only a constant to the
  first stage's reading. A board with its own self-similar refinement would behave the same way by the same argument; this is not
  written here.

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependencies bound by hash | pass |
| 1 | On the four boards at g = 2 and 3, the polygon contains 0 in its interior, and breadth-first route distances on a 40 × 40 torus stay within a constant of the gauge (least over the torus's images), with no growth from the nearer to the farther half of the distances read | pass: the largest deviation is the same in both halves on every board (2 to 10 lags) |

## Nonclaims

- **Periodic boards only**, with the program's ring cells and contact law. Aperiodic or random boards are not covered.
- **The constant K is not computed** in general; the four boards' deviations are in ticket B.
- **The one-way homothety with the graph polygon is computed on four boards**, not proved for every board.
