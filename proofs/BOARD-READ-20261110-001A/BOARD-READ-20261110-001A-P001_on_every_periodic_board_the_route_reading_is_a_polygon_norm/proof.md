# On every periodic board the route reading is a polygon norm up to a constant

Status: Partial (frozen statement, before the proof is written)

Ticket `BOARD-READ-20261110-001A`, 2026-11-10.

## Frozen statement

- **Boards.** A board is a connected locally finite map in the plane, periodic under a lattice Λ ≅ Z² with finite quotient: rings at
  its vertices, a contact at each edge, ring v carrying deg(v)·g cells with its contacts every g cells in counterclockwise order, rule
  60 on own cells and law (12, 12) at contacts, as in `LOOP-NET-20261108-001`'s networks. The **route digraph** Γ has the cells as
  vertices and an arc from each cell to the next cell on every ring it lies on; the **route reading** T(c, c') is its directed distance
  (the time length of `CONF-METRIC-20261110-001A`). The **ring graph** G has the rings as vertices and the contacts as edges.
- **Theorem.** Let Q = Γ/Λ, a finite digraph whose arcs carry displacements in Λ, and let P be the convex hull of the points
  disp(C)/len(C) over the simple cycles C of Q. Then 0 lies inside P, its gauge N(v) = min{t ≥ 0 : v ∈ tP} is an asymmetric norm whose
  unit ball is the polygon P, and there is a constant K (depending on the board and g) with |T(c, c') − N(x(c') − x(c))| ≤ K for all
  cells c, c', where x(c) is the lattice position of c's ring. The same holds for the ring graph G with its own polygon P_G.
- **Corollary.** No periodic board's route reading or graph distance is round: each is, up to a constant, a norm whose unit ball is a
  polygon. Whether the two polygons have the same shape depends on the board (ticket B).

## Stop rule

Stop at a proof of the theorem, with the cycle-polygon computed exactly for three boards and checked against breadth-first distances
(ticket B). If the computed slopes disagree with the polygon, the proof has a gap: report and narrow.
