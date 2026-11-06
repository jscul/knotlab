# Heights compute the transfer

Status: Proved (each ingredient verified against enumeration)

Ticket `HALO-FORCING-20261103-001B`, 2026-11-03.

## Question

- **What ticket A shows.** Whether an opened handle creates at a plane gluing line L depends on the plane piece only through its
  transfer R(L): the set of (port pattern, L pattern) pairs that occur together in the point split of the plane closure.
- **The question.** Can R(L) be computed for large plane pieces without enumerating solutions?

## Dependencies

- **`HALO-FORCING-20261103-001A`.** The transfer lemma's consequence.
- **`HANDLE-LOCALITY-20261103-001A`.** Point splits are plane matching systems (clarified in item 1).
- **`PLANAR-THEOREM-20261102-001A`.** Heights, and the parity reading.
- **Classical.**
  - Height functions of plane bipartite matchings (Thurston, Propp).
  - Difference constraints, their projections and integrality (shortest paths; Murota).

## Setting

- **The split.** H is a plane knot space with Kasteleyn signs, and Q is H split at a point z into three ports y₁, y₂, y₃, one on each
  line through z.
- **The faces.** The three faces at z merge into one odd face F₀, which holds the ports as pendant points.

## 1. Corner matchings (proved; clarifies HANDLE-LOCALITY A)

- **The statement.** The solutions of Q up to complement correspond one to one to the choices of one corner per line with each face
  receiving exactly one.
- **The skip model.** A line skips the corner between its two agreeing points.
- **The counting.** HANDLE-LOCALITY A's argument applies: every face is odd, and there are as many faces as lines.
- **The double edges.** A port's line has two corners in F₀, one on each side of the port. So the line–face graph B has a double edge
  there, and the matching must choose the corner, not only the face. HANDLE-LOCALITY A's phrase "perfect matchings of lines to odd faces"
  is to be read with corners as the edges of B.
- **Unaffected.** Its conclusions were checked by brute force.
- **The ports' regions.** The region between a double edge is the port's own region.

## 2. Heights decide the transfer (proved)

- **Heights.** Fix a reference matching μ₀.
  - **The jumps.** Crossing the edge of B at a corner from the region of p (before the line along the face) to that of q (after), the
    height jumps by μ(e) − μ₀(e).
  - **The constraint set.** The heights of matchings are exactly the integer solutions c of −μ₀(e) ≤ c(q) − c(p) ≤ 1 − μ₀(e), up to an
    additive constant (PLANAR-THEOREM A). Every point of Q has its own region.
  - **The parity reading.** A point's value relative to another, compared with μ₀'s solution, is the parity of their height difference,
    because alternating cycles flip exactly the points they enclose.
- **Fixing L's state.** To fix L's matched corner, replace the bounds of L's three edges by equalities. This is still a system of
  difference constraints.
- **Projection.** Let Θ be the regions of the three ports and of L's points. The projection of the solution set onto Θ is
  {x : x_b − x_a ≤ D(a, b)}, where D is the shortest-path distance in the constraint graph (arc a → b of weight w for c(b) − c(a) ≤ w).
  Difference systems are closed under Fourier–Motzkin elimination by shortest paths, and their integer points lift.
- **Parity.**
  - **Substitution.** Put x = 2z + v. Then x_b − x_a ≤ D(a, b) with x ≡ v (mod 2) becomes z_b − z_a ≤ ⌊(D(a, b) − v_b + v_a)/2⌋. This
    is feasible iff the six-vertex system has no negative cycle.
  - **Patterns.** Each feasible pair (corner, v) gives one (port pattern, L pattern) pair and its complement.
- **Cost.** Bellman–Ford once per corner state, then Dijkstra from each of up to six terminals: polynomial, with no enumeration.

## Checks

`check.py` (`result.json`, about a minute; library `transfer_lib.py`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Corner matchings = solutions up to complement | all 71 point splits of the planar census and the 10-point grown and prism spaces (215 lines with a double edge) |
| 2 | Transfer by heights = enumeration | all 1,221 (split, line) pairs of the planar census, five grown and two prism spaces to 14 points |

## What this does not establish

- **Creation itself.** That needs ticket A's criterion as well. On larger spaces, its converse is used without a proof.

## Novelty

- **New here.** The transfer computation.
- **Classical.** Its ingredients.
