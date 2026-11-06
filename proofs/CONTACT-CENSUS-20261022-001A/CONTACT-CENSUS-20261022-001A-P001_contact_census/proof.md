# The census of fair contacts on square tori

Status: Proved

Ticket `CONTACT-CENSUS-20261022-001A`, 2026-10-22. It uses:
- `BASE-CRITICALITY-20261022-001A-P001` ("the criticality proof"): the
  recolouring, the percolation coupling and the blocking theorem;
- `EMERGENCE-BITS-20261021-001B-P001` ("the accounting proof"): in a network
  with hidden joints, emergence is minus log₂ of the consistency chance. That
  proof also gives:
  - at most one bit per independent cycle, exactly for parity;
  - zero for contacts with a vacuum;
  - superadditivity over edge-disjoint patches.

It cites:
- **Crossing and correlation:** the crossing bounds of Russo (1978) and of
  Seymour and Welsh (1978), and positive correlation (Harris 1960), for bond
  percolation at 1/2 on the square lattice.
- **Pinson's winding probabilities** for critical percolation on the torus
  (Pinson, *J. Stat. Phys.* 75, 1994), in the form restated by Pruessner and
  Moloney (2003, equations (1)–(6)). This is a Coulomb-gas, conformal
  prediction, not a theorem. The check reproduces Newman and Ziff's reference
  values for square tori.

## Standard statement

Place the same three-variable relation C(h_u, x_e, h_v) on every edge of a
square-lattice torus, oriented east and north. The x_e are independent fair
bits, and the h are free.
1. **Ten classes.** Up to swapping spoke values, swapping joint values and
   reversing edges, the 204 placements of the 34 relations whose one-deleted
   projections are full form 10 classes. All members of a class have the same
   satisfiability law.
2. **The three regimes of the census.**
   - **Six classes** have a constant solution and are always satisfiable.
   - **Parity and "swap-or-order"** have a small unsatisfiable patch (one face,
     or a 2 × 3 domino), so −log₂ P(satisfiable) grows linearly with the area.
   - **Not-all-equal and "x or (h ≠ h′)"** are satisfiable on every
     non-wrapping patch.
3. **Bipartite percolation.** "x or (h ≠ h′)" is satisfiable exactly when the
   edges with x_e = 0, a Bernoulli(1/2) bond percolation, form a bipartite
   graph. On the torus that means no cluster with a cross topology and none
   winding in a class of odd length.
   - **Two-sided bounds.** Its satisfiability probability is bounded away from
     0 and 1 at fixed shape.
   - **Pinson's prediction.** Its scaling limit is predicted by Pinson's
     formula.

## Nearest known result

- **Items 1 and 2** are elementary consequences of the accounting proof and of
  bipartiteness of planar regions.
- **Item 3, the reduction,** is elementary. It says when diluted
  antiferromagnetic bonds on a torus are frustration-free.
- **The bounds** use standard crossing estimates.
- **Pinson's formula** is classical (Coulomb gas; confirmed numerically by
  Newman and Ziff 2000–2001 and by Pruessner and Moloney 2003).
- **The delta.** A bounded search did not find the identification of a
  three-literal contact world's emergence with a torus-topology probability of
  critical percolation.

Novelty: `candidate-local-delta`, with moderate folklore risk for the
reduction: frustration of diluted antiferromagnets on tori may be studied
under other names.

## Definitions

- **Contact.** A knot R on three bits placed on an edge as C(h_u, x_e, h_v):
  two joints at the vertices, hidden, and one visible spoke.
- **Transfers.** The tables M(x)[h_u][h_v] = [C(h_u, x, h_v)]. A knot's two
  transfers have no zero row or column, and their union is the all-ones
  table.
- **The seven tables.**

| Name | Allowed pairs (h, h′) | Reading |
| --- | --- | --- |
| I | 00, 11 | equality |
| S | 01, 10 | disequality |
| J | all four | no constraint |
| U | 00, 01, 11 | the implication h → h′ |
| L | 00, 10, 11 | the implication h′ → h |
| A1 | 01, 10, 11 | the clause h ∨ h′ |
| A2 | 00, 01, 10 | the clause ¬h ∨ ¬h′ |

- **Emergence.** E = −log₂ P(consistent). On these simple torus graphs it is
  the logical emergence of the visible relation (accounting proof).

## Theorem 1: ten classes

Every placement determines an unordered pair of transfers {M(0), M(1)}. Three
operations preserve the law of consistency on every square torus:
- **swapping the spoke values,** because the spokes are fair;
- **swapping the joint values everywhere,** a bijection of joint assignments,
  which conjugates both tables;
- **reversing every edge,** which transposes both tables. The reflection
  (i, j) ↦ (−i, −j) maps the torus onto itself and turns east and north edges
  into west and south ones.

Under these operations the 204 placements form 10 classes:

| Class | Placements | Name |
| --- | --- | --- |
| {A1, A2} | 12 | not-all-equal |
| {J, S} | 12 | "x or (h ≠ h′)" |
| {I, S} | 12 | parity |
| {L, S} | 24 | "swap-or-order" |
| {I, J}, {L, U} | 12 each | — |
| {A1, I}, {A1, J}, {J, L} | 24 each | — |
| {A1, L} | 48 | — |

*Check.*
- **The classes.** All 34 knots × 6 placements are enumerated and give these
  10 classes with these counts.
- **One law per class.** On the 3 × 2 torus (every spoke pattern), all
  placements in a class have the same number of consistent patterns. The
  classes give 4,096 (the six vacuum classes), 3,754 (not-all-equal), 2,650
  ("x or (h ≠ h′)"), 628 (swap-or-order) and 32 (parity).

## Theorem 2: six classes hold nothing

{I, J}, {L, U}, {A1, I}, {A1, J}, {J, L} and {A1, L} each have a common vacuum:
a value c with M(x)[c][c] = 1 for both spokes. All joints at c satisfy every
edge, so E = 0 on every graph (accounting proof).

*Check.* On the 3 × 2 torus (every pattern) and on 50 random graphs (20
patterns each), they are always consistent.

## Theorem 3: two classes grow with the area

- **Parity** holds exactly the cycle rank (accounting proof): E = ab + 1 on the
  a × b torus. One square face is frustrated for 8 of its 16 spoke patterns.
- **Swap-or-order** has no single frustrated face, but the 2 × 3 domino (two
  faces) is inconsistent for 8 of its 128 patterns, so E(domino) = log₂(16/15).
  - **Why it grows.** Vertex-disjoint dominos tile ⌊a/2⌋⌊b/3⌋ blocks of the
    torus. By superadditivity, E ≥ ⌊a/2⌋⌊b/3⌋·log₂(16/15).

*Check.*
- **Smallest patches.** Over open grids up to 3 × 4, the smallest
  frustrating patches are one face (parity) and the domino (swap-or-order).
- **Parity's count.** On the 3 × 3 torus parity is consistent for exactly
  256 of 2¹⁸ patterns, that is 2^(−(cycle rank)).

## Theorem 4: two classes are global only

Not-all-equal ({A1, A2}) and "x or (h ≠ h′)" ({J, S}) have no vacuum. But they are
consistent for every spoke pattern on every bipartite graph:
- **not-all-equal,** by a proper two-colouring;
- **"x or (h ≠ h′)",** because its constraints are disequalities on a subgraph.

Every part of a square torus that does not wrap around is bipartite. So their
emergence on tori comes only from global cycles.

*Check.*
- **Grids.** Both are consistent for every pattern on every open grid up to
  3 × 4.
- **The even torus.** Both are always consistent on the even 4 × 4 torus
  (2,000 samples).

## Theorem 5: "x or (h ≠ h′)" is bipartite percolation

Call an edge *open* when its spoke selects the disequality table S. The
world is consistent exactly when the open subgraph is bipartite. On a torus
with sides l_h (horizontal) and l_v (vertical), a cycle with a horizontal and
b vertical windings has length ≡ a·l_h + b·l_v (mod 2). So the world is
inconsistent exactly when some open cluster:
- **has a cross topology** (it contains cycles of two independent classes),
  or
- **winds in a single class (a, b)** with a·l_h + b·l_v odd.

*Proof.*
- **Bipartiteness.** The S edges demand h_u ≠ h_v, and the J edges demand
  nothing. A system of disequalities is solvable exactly when its graph is
  bipartite.
- **Odd cycles are odd windings.** Contractible cycles on the square lattice
  are even. A closed walk's length parity is a homomorphism of its homology
  class.
- **The two cases.** A cluster with a single winding class (a, b) has cycles
  only in multiples of (a, b). A cluster with a cross topology contains a
  (1, 0) cycle and a (0, 1) cycle, one of which is odd when the torus is not
  bipartite. ∎

*Check.*
- **Exhaustive.** On the 3 × 3 torus (all 262,144 patterns), consistency
  equals bipartiteness of the open edges. Bipartiteness equals the absence of
  an odd topology, computed independently by union-find with lattice
  displacements and a classification of each cluster's winding lattice.
- **Sampled.** The same holds on 20,000 patterns each of the 5 × 5, 3 × 4 and
  5 × 6 tori.

## Theorem 6: two-sided bounds for "x or (h ≠ h′)"

On non-bipartite square tori of fixed shape, there are constants
0 < c₁ ≤ 1 − c₂ < 1 with c₁ ≤ P(inconsistent) ≤ 1 − c₂ at every size. So the
emergence is bounded away from 0 and from infinity.

*Proof.*
- **Inconsistency is likely enough.**
  - With probability at least some c > 0, depending only on the shape, there
    is an open circuit winding horizontally. This follows from the crossing
    bounds, gluing a fixed number of crossings of overlapping boxes around the
    torus by positive correlation. The same holds for an open vertical circuit.
  - Both events are increasing, so they occur together with probability at
    least c².
  - A horizontal and a vertical circuit share a vertex, so they lie in one
    cluster with a cross topology. That cluster contains an odd cycle, so
    c₁ = c².
- **Consistency is likely enough.** Likewise, with probability at least c² the
  dual percolation, also critical, has both winding circuits. Then every open
  cluster is enclosed and contractible, and the world is consistent, so
  c₂ = c².
- **The comparison.** Not-all-equal has the upper bound but not yet this lower
  bound (criticality proof). Here the reduction to undirected percolation
  makes positive correlation available. ∎

## Pinson's prediction (cited, not proved)

Pinson's formulas give, in the scaling limit, the probabilities that the
cluster structure:
- is all contractible, P̂(0, r);
- has a cross topology, P̂(X, r) = P̂(0, r);
- has winding clusters of a normalized class (a, b), P̂((a, b), r).

Here r is the ratio of the vertical to the horizontal circumference. By
Theorem 5 the predicted limit of the emergence is

E∞ = −log₂[ P̂(0, r) + Σ over even classes (a, b) of P̂((a, b), r) ].

| Torus shape | r | Odd classes | Predicted E∞ (bits) |
| --- | --- | --- | --- |
| square, both sides odd | 1 | a + b odd | 1.508460 |
| rows odd, twice as many columns | 1/2 | b odd | 1.985201 |
| columns odd, twice as many rows | 2 | a odd | 1.985201 |
| rows 3k odd, columns 2k | 3/2 | b odd | 0.677388 |
| both odd, rows 3/5 of the columns | 3/5 | a + b odd | 1.789802 |

*Check.*
- **Reference values.** The implementation reproduces Newman and Ziff's
  1 − R^(e) = 0.309526275 and R^(1) = 0.169415435 for square tori.
- **Normalization.** The topologies sum to 1 for every shape.
- **A control.** Dropping the cross term breaks the normalization.

The experiment `CONTACT-CENSUS-20261022-001B-E001` tests these predictions.

## What this means (interpretation, not theorem)

- **What fair contacts do on the square lattice.** Of all the ways to place
  one three-variable knot as a contact:
  - most (6 of 10 classes, 144 of 204 placements) hold nothing at scale,
    because they have a vacuum;
  - two hold a quantity that grows with the world, because they frustrate
    locally;
  - exactly two hold a scale-free amount fixed by the world's shape:
    not-all-equal and "x or (h ≠ h′)".
- **Two different critical readings.**
  - "x or (h ≠ h′)" is undirected percolation: its emergence is a classical
    conformal invariant.
  - Not-all-equal is directed, through the random orientation and the seam:
    its emergence is a different, so far unidentified, invariant.

## Scope

- One contact on every edge, uniform orientation, square-lattice tori.
- Pinson's formula is a conformal prediction, tested empirically in ticket B,
  not proved here.
- The bounds in Theorem 6 rest on the cited percolation theorems.
