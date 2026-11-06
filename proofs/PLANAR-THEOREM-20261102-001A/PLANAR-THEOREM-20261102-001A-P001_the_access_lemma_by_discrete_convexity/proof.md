# The access lemma, by discrete convexity

Status: Proved (each ingredient checked numerically)

Ticket `PLANAR-THEOREM-20261102-001A`, 2026-11-02.

## Question

- **The access lemma (PLANAR-COMPOSE A).** On a plane near side, whenever the hub and a near point pin the gluing pattern, the hub
  reaches the ports in one of two ways:
  - **(i)** it is tied to a port other than the pinned odd port; or
  - **(ii)** it forms a near knot with the two non-odd ports whose excluded pattern is one step from the pinned one.
- **Status before this ticket.** Checked on 9020 pinnings, not proved.
- **This ticket.** It proves the lemma for every plane knot space with Kasteleyn signs.

## Dependencies

- **`PLANAR-COMPOSE-20261102-001A`.** The route lemma, the tie-class lemma, and the classification code.
- **`HANDLE-EMERGENCE-20261102-001C`.** The skip model: after a removal, the solutions up to complement are the perfect matchings of the
  other lines to the faces off M.
- **Classical.**
  - L-natural convex sets (Murota, *Discrete Convex Analysis*, 2003): they are closed under rounded midpoints, and their projections
    are L-natural convex.
  - Height functions of plane bipartite matchings (Thurston 1990; Propp).

## Setting

- **The space.** H is a plane knot space with Kasteleyn signs, and M is a removed line.
- **The graph B.** B is the line–face incidence graph: lines other than M against faces of H not touching M, with an edge for each
  corner.
- **Its faces.**
  - **The hole.** One face of B holds M's points and every point on M's three faces.
  - **Every other point** has a face of its own.
- **The gluing line.** L is a line sharing no face with M. Its three ports y₁, y₂, y₃ show six patterns.
- **Notation.** For a state of L, its odd port and non-odd ports are as in PLANAR-COMPOSE A. A pinning is a value of the hub and a
  near point a (not in the hub's tie class, not a port) that leaves one port pattern.

## 1. Potentials

- **Definition.** Fix a reference matching μ₀. For a matching μ, cross an edge of B from line K into face f, through the corner of f
  at K between incidences p (before K along f) and q (after). There the height jumps from p's region to q's by μ(K, f) − μ₀(K, f).
- **Well defined.** The jumps are integrated from the hole, which has potential 0. Around a line, or a face off M, exactly one edge
  is matched in μ and one in μ₀. So the jumps sum to zero around every vertex of B, and the integrated potential c_μ is well defined.
- **A bijection.** The integer potentials of matchings are exactly the integer solutions c of the difference constraints
  −μ₀(e) ≤ c(q) − c(p) ≤ 1 − μ₀(e), one per edge e, with c = 0 on the hole. Given such a c, setting μ(e) = c(q) − c(p) + μ₀(e)
  gives a value 0 or 1 on every edge. Single-valuedness forces exactly one matched edge at every vertex.
- **Hence convex.** The potential set is L-natural convex: closed under componentwise rounded-up and rounded-down midpoints. The same
  holds for its projections, so in particular the values of any coordinate, or of any difference of two coordinates, form an integer
  interval.
- **Parity.** The matchings μ and μ₀ differ by disjoint alternating cycles. Each cycle flips exactly the points it encloses
  (PLANAR-COMPOSE A, item 1), and c_μ(p) is the signed number of cycles enclosing p. So a point's value relative to the hub, compared
  with μ₀'s solution, is c_μ(p) mod 2.
- **Ties.** Two points are tied iff their potential difference is constant. Its parity is constant, and its values form an interval.

## 2. The staircase at the gluing line

- **Edges and states.** L has three edges in B. The edge to face φ_k (L's corner opposite y_k) separates the regions of the other two
  ports. L's state is its matched edge; matching to φ_k makes y_k odd.
- **(a) Non-odd ports.** For the state with odd port y_k, the difference of its non-odd ports' potentials is the jump across L's edge to
  φ_k. That jump is ε(1 − μ₀(φ_k)) on that state and −ε·μ₀(φ_k) on the others, where ε = ±1 is fixed by orientation. These are
  neighbouring integers.
- **(b) A tied port.** If y₀ is tied to the hub, its potential is constant. The other two ports' potentials are then fixed by L's
  state through the jumps across L's two edges at y₀'s region.
  - **The state with odd port y₀.** Neither of those edges is matched.
  - **The other two states.** Each matches one of them. The jumps go in opposite rotational directions, so they shift one coordinate
    down and the other coordinate up.
  - **So** the three points form a chain with y₀'s state in the middle.

## 3. The access lemma

Let a be a pinning near point, A = c(a), and β the parity of A at the pinning. Every point with A ≡ β is in the pinned state.

**(i) The hub is tied to a port y₀. Then the pinned odd port is not y₀.**

*Proof.* Suppose the pinned state is y₀'s, the middle of the chain. Let ℓ and h be the low and high states' points. These are single
points in the other two ports' potentials.
- **Off the pinned state.** On ℓ and on h, A ≡ β̄ is constant in parity, and A ranges over an interval. So A is constant there:
  A_ℓ and A_h.
- **A_ℓ = A_h.** Rounding the midpoint of (A_ℓ, ℓ) and (A_h, h) gives back (·, h) when rounded up and (·, ℓ) when rounded down. Since
  A_ℓ ≡ A_h, the midpoint's A is the integer (A_ℓ + A_h)/2, so A_ℓ = A_h =: A*.
- **The contradiction.** Take the pinning point (A_β, middle), with A_β ≢ A*.
  - Rounding its midpoint with (A*, h) upward lands at h, which forces ⌈(A_β + A*)/2⌉ = A*, so A_β = A* − 1.
  - Rounding its midpoint with (A*, ℓ) downward lands at ℓ, which forces A_β = A* + 1.
  - These cannot both hold. ∎

**(ii) No port is tied to the hub. Then the hub and the non-odd ports y, y′ form a near knot excluding a pattern one step from the
pinned one.**

*Proof.* By 2(a), the difference D = c(y) − c(y′) takes one value δ_on on the pinned state and the neighbouring value δ_off on the
other two states (the off-slice).
- **A is constant off the pinned state.** On the off-slice A ≡ β̄, so A is constant there: A*.
- **c(y) is constant off the pinned state.** Suppose c(y) took two consecutive values j, j+1 on the off-slice. Take the pinning point
  (A_β, k, k − δ_on) and an off-slice point (A*, j, j − δ_off).
  - **Their midpoint.** It has exactly one half-integer port coordinate, because δ_on + δ_off is odd. So one rounding lands on the
    off-slice and the other on the pinned state.
  - **What the off-slice forces.** The off-slice rounding must have A = A*. That forces A_β = A* − 1 if the off-slice rounding is the
    upward one, and A_β = A* + 1 if it is the downward one.
  - **Both cases occur.** Replacing j by j + 1 swaps which rounding lands on the off-slice. So both A_β = A* − 1 and A_β = A* + 1 would
    be forced, a contradiction.
- **The missing pattern.** So off the pinned state, (c(y), c(y′)) mod 2 is a single pair. Its difference parity is δ_off. On the
  pinned state the difference parity is δ_on.
  - The two pairs one step from the pinned pair are exactly the two pairs with difference parity δ_off.
  - One of them is the off-slice pair. The other occurs nowhere, so it is the missing pattern.
- **It is a knot.** {h, y, y′} is constrained. Its pairs are free: no port is tied to the hub, and the ports are pairwise free with
  six patterns. ∎

## Consequence

- **The route lemma.** PLANAR-COMPOSE A item 2 (proved for any near side) gives, under (i) or (ii), an elimination route for every
  pinned-and-separated three-point crossing knot through the hub. The far knot on the two non-odd ports is automatic.
- **The theorem.** On a plane near side with Kasteleyn signs, at a removal leaving six port patterns, no pinned-and-separated
  three-point knot through the hub is ever new, whatever knot space is glued on the far side.

## Checks

`check.py` (`result.json`, about a minute):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Potentials on 30 plane spaces | 325 of 325 removals: well defined, one per matching, parity = value relative to the hub, closed under rounded midpoints |
| 2 | Staircase | 4464 of 4464 (state, line, removal) triples; 877 of 877 tied-port chains with that port's state in the middle |
| 3 | Conclusion on 42 plane spaces (to 20 points) | 9020 pinnings, all of type (i) or (ii) |

## Correction

- **The error.** PLANAR-COMPOSE's decision note, KNOT_INTUITION entry and memory gave the plane pinning total as 8020.
- **The correct total.** 9020: 4560 in ticket A, plus 4460 in the scout.

## What this does not establish

- **The premise.** That every new knot is a pinned-and-separated three-point knot through the hub. Tickets B and C take it up.

## Novelty

- **New here.** The proof.
- **Classical.** L-natural convexity, and plane matching heights.
