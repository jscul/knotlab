# Three-fold spaces are an Euler count

Status: Proved (theorems 1–5 by hand, their finite claims checked; §6 records measurements and a conjecture)

Ticket `TWO-ROUND-BRIDGE-20261106-001B`, 2026-11-06.

## Standard statement

Let H be a cubic 3-uniform hypergraph with as many edges as vertices that is not 2-colourable (equivalently, its incidence matrix is
sign-nonsingular), or a system of signed not-all-equal constraints on such a hypergraph whose incidence graph is planar with Kasteleyn
signs.
1. Resolution refutations compose along the 3-edge tight cuts of the incidence graph at constant cost per Fano piece.
2. On a planar incidence graph the contradiction is a count from Euler's formula: there are two more faces than edges, every face must
   contain an "agreeing corner", and every satisfied edge contains exactly one.
3. Hence the Sherali–Adams relaxation of level 3 refutes every Kasteleyn-signed planar instance whose faces carry at most three points.
4. Resolution gets only the treewidth bound 2^{O(√n)}, and on a natural planar family the cost of conflict-driven solvers grows
   exponentially in √n.

## Nearest known result

- **Planar max-cut is an LP.** For graphs without a K5 minor, the cut polytope is cut out by the cycle inequalities
  (Barahona–Mahjoub 1986). Planar not-all-equal 3-SAT is polynomial through planar max-cut (Moret 1988).
- **Counting principles on grids.** The mutilated chessboard needs resolution size exponential in the side (Dantchev–Riis 2001,
  Alekhnovich 2004), though linear counting refutes it.
- **Structure.** Seymour 1974 and Robertson–Seymour–Thomas 1999 (sign-nonsingular matrices, Pfaffian braces). Treewidth dynamic
  programming gives resolution refutations of size exponential in the treewidth.
- **Classification.** known-with-delta. The certificate in theorem 4 is planar max-cut duality in disguise. The delta is the reading of
  the knot's three-fold spaces as an Euler count, with its consequences for proof systems. A bounded search found no proof-complexity
  treatment of these formulas.

## Setting

- **Spaces.** A signed knot space is a cubic triple system (n points, n lines) with a signed not-all-equal constraint on each line. A
  three-fold space is an unsigned one that is not 2-colourable (`THREEFOLD-SPACES-20261030-001A`).
- **The grammar (`THREEFOLD-GRAMMAR-20261030-001A`).** Three-fold spaces are Fano atoms in Pfaffian glue. Every plane cubic bipartite
  graph is glue: decorate its Kasteleyn signing with T14 pieces at negated incidences and Fano blocks at repeated points.
- **Pieces.** These are the parts cut off by a 3-edge tight cut.
  - A **Fano block** (the Fano plane minus a line) acts as a point.
  - A **dual block** (the Fano plane split at a point) acts as a line.
  - **T14 minus its root line** acts as a point with one negated incidence.
  - Contracting every piece leaves the space's **core**.
- **Corners.** Let B be the incidence graph, drawn in the plane. A line ℓ has three corners, one in each face around it. The corner in
  face f is the pair of ℓ's points that are consecutive along f. Under an assignment, the corner agrees when those two literals of ℓ are
  equal.
- **The test family.** The k-frequency octahedron is the octahedron with each face cut into k² triangles. Its dual, GC(k,0) of the
  cube, is a plane cubic bipartite graph with six squares and 4k² − 4 hexagons. Its signed space has n = 4k² points, and its
  decoration is a three-fold space.

## 1. Composition over the handle tree

**Theorem 1.** Let K be obtained from a signed knot space H by contracting one piece P across a 3-edge tight cut. Then
size(H) ≤ size(K) + s_P and width(H) ≤ max(width(K), w_P), where s_P and w_P are the size and width of a resolution derivation, from P's
clauses, of the relation P passes to its ports. For the three Fano pieces, Davis–Putnam gives w_P ≤ 5 and s_P ≤ 80 (check 1: block
32 clauses of width at most 4, dual block 40 of width at most 5, T14 80 of width at most 4). Iterating over the tight-cut tree:

  size(H) ≤ size(core) + O(#pieces),  width(H) ≤ max(width(core), 5).

*Proof.*
- **A piece that acts as a line ℓ.** H's clauses are those of K − ℓ together with P's. Derive ℓ's two clauses from P (size s_P, width
  w_P) and then run K's refutation.
- **A piece that acts as a point q.** In H, q is split into three ports, one on each of q's lines, and P forces the ports equal (or
  negated, for T14). Derive the ties between the ports from P. Replay K's refutation with q renamed to one port; each axiom of K that
  holds another port is first rewritten through a tie, a width-3 step. ∎

**What crosses a cut is a line's two clauses or two ties**, and passing it costs constant width (at most 5 here). This matches
ticket A, where every crossing knot needs width at most 4. So the handle tree costs O(1) per piece. All global cost lies in the core:
the glue.

## 2. The Euler count

**Theorem 2.** Let K be a signed knot space whose incidence graph B is plane with Kasteleyn signs: on every face of length 2l, the
number of negated incidences is l − 1 mod 2. Then for every assignment:
- (a) a satisfied line has exactly one agreeing corner, and a violated (monochromatic) line has three;
- (b) every face has an odd number of agreeing corners;
- (c) |faces| = |lines| + 2.

Consequently Σ_faces (agreeing corners − 1) = 2(violated lines − 1). Every assignment violates at least one line, and K is unsatisfiable.

*Proof.*
- **(a)** The three corners of a line are its three pairs of points. Exactly one pair is equal under not-all-equal, and all three are
  under a monochromatic pattern.
- **(b)** Walk around the face's cycle of points. Consecutive points disagree, as literals of their line, at every non-agreeing corner.
  Going once around, the disagreements must sum to the parity of the face's signs, and the Kasteleyn condition makes the number of
  agreeing corners odd. In particular it is at least one.
- **(c)** B has 2n vertices and 3n edges, so Euler's formula gives n + 2 faces.
- **Counting.** Every corner lies on one line and in one face, so the two sums of agreeing corners are equal. By (a) the sum over lines
  is n + 2·(violated lines). By (b) the sum over faces is at least n + 2. ∎

**The reading.** The sphere is a mutilated chessboard. Each face needs one agreeing corner and each satisfied line supplies exactly one.
The two squares that are missing are the Euler characteristic.
- **The genus.** On a surface of genus g the count is n + 2 − 2g faces against n lines, and the deficit is 2 − 2g. A Fano atom is a
  handle (`THREEFOLD-SURFACES-20261030-001A`). On the torus the count balances, so the Fano plane's contradiction lies in its two
  homology parities instead.
- **Contraction removes the handles.** Contracting the atoms (theorem 1) leaves a plane core, where the count alone decides.
- **Earlier form.** This is the skip model of `HANDLE-EMERGENCE-20261102-001C`, used here as a refutation.

## 3. The corner map

**Theorem 3.** Let Γ be the line–face graph: its vertices are the lines and the faces, and its edges are the corners. Assignments
modulo complement correspond one to one to the sets of corners that have odd degree at every line and every face. These are the
solutions of the parity system with charge 1 at every vertex of Γ.

*Proof.*
- **Into.** By (a) and (b), every assignment gives such a set.
- **Injective.** The agreeing corners fix every pair of points on a common line, and B is connected.
- **Onto.** Γ is connected, with 3n edges and 2n + 2 vertices, so the parity system has 2^{3n − (2n+2) + 1} = 2^{n−1} solutions. That
  is the number of assignments modulo complement. ∎

So a point assignment is a parity (Tseitin) solution on Γ, and not-all-equal says that every line has degree exactly 1 rather than 3.
The contradiction does not lie in the parity system, which is satisfiable. It lies in "exactly one" at every line against "at least
one" at every face. Check 3 verifies the dimensions on every family member, and verifies the bijection exhaustively up to 20 points.

## 4. Sherali–Adams sees the count

**Theorem 4.** If every face of the plane signed space K carries at most d points, the Sherali–Adams relaxation of level max(3, d) of
K's not-all-equal clauses is infeasible. For the octahedral family d = 3, so level 3 suffices: a refutation of polynomial size.

*Proof.*
- **Local distributions.** A level-max(3, d) solution gives a distribution on assignments to each line and to each face's points, with
  equal pair marginals.
- **The lines.** Each line's distribution is supported on not-all-equal patterns, so by (a) its corners agree once in expectation.
- **The faces.** Each face's distribution is a distribution over all assignments of its points, so by (b) its corners agree at least
  once in expectation.
- **The count.** Corner agreement depends on a pair, so the marginals make both sums the same linear expression. That gives
  n ≥ n + 2, a contradiction. ∎

**Corollary (three-fold spaces).** Let H contract to a plane core K. Take the level to be the largest number of points of H that lie on
a face of K or in pieces contracted to its points or lines. Then that level of Sherali–Adams refutes H.
- **Why.** On those points the pieces force their port relations, so (a) and (b) hold for K's corners read through the ports.
- **The octahedral three-fold spaces.** Their pieces are T14 pieces, so the level is at most 42: a constant.

Check 4 solves the level-3 relaxation restricted to the lines and the faces. It is infeasible on every family member with at most three
points per face and at most 40 points. Restricted to the lines alone it is feasible wherever some face's points lie in no line, so
there the faces are what refutes. On the cube, K4^(3), every face's two points lie in a line, and the lines alone already refute.

## 5. Resolution: the upper bound

**Theorem 5.** Every three-fold space on n points has a resolution refutation of size n^{O(1)}·2^{O(√n)}.

*Proof.*
- **Pieces and gluing.** By the grammar and Robertson–Seymour–Thomas (their 6.8), the incidence graph is glued from Heawood graphs and
  plane braces. The gluings run along 3-edge tight cuts and along 4-cycles (trisums).
- **Treewidth.** Gluing along separators of at most four vertices does not raise treewidth beyond the pieces' treewidth plus a
  constant. A plane graph on m vertices has treewidth O(√m) (Lipton–Tarjan). So the incidence graph has treewidth O(√n), and so does
  the primal graph of the clauses, within a factor 3.
- **Elimination.** Davis–Putnam elimination along an order of induced width t produces at most n·3^{t+1} clauses. ∎

**The octahedral family.** Measured upper bounds:
- **Davis–Putnam.** Refutations along a minimum-degree order have 263, 4,477 and 123,547 clauses, of widths 7, 12 and 18, for
  k = 2, 3, 4.
- **Treewidth.** The min-fill upper bounds on the primal treewidth grow linearly in k.

## 6. Resolution: measurements and a conjecture

- **Solver cost.** CaDiCaL 1.5.3 uses 36, 354, 3,530, 51,332 and 1,182,667 conflicts on the signed octahedral spaces for
  k = 2, …, 6 (n = 16 to 144). On their decorations (107 to 443 points) it uses 208, 539, 5,031, 37,757 and 1,812,645.
- **Growth.** Past the smallest case, each step in k multiplies the cost by 7 to 50. A conflict-driven solver's run is a resolution
  refutation, so these are upper bounds, not lower bounds. They show no polynomial behaviour.
- **The defect moves freely (scout).** A state violating one line can move its violated line to any adjacent line by changing points
  within distance 3 (148 of 148 random tests at k = 8). That is the mobility a width lower bound by a pebble game would need.

**Conjecture.** Resolution refutations of the octahedral three-fold spaces need size 2^{Ω(k)} = 2^{Ω(√n)}, as for the mutilated
chessboard. Width Ω(k) would follow from a mobility lemma for the violated line. That is a height-function statement for the dimer
model on Γ, not proved here.

## Answer to the bridge question

- **The handle tree composes.** Two-round derivations through a cut, and piece contractions, compose over the tree at constant cost.
- **No global resolution bound follows.** The tree's leaves are constant, but its glue braces are unbounded. A single brace carries
  the whole contradiction: the octahedral glue is a brace, since its dual triangulation has no separating triangle (checked for
  k ≤ 8; a separating triangle would be a chord in the link of a vertex, and the links take the same shapes for every k ≥ 3). That
  contradiction is the sphere's Euler count, which local width-3 or width-4 reasoning cannot express.
- **The global bound is a counting one.** Sherali–Adams of level 3 on the glue, and constant level on three-fold spaces with bounded
  pieces and faces. Resolution gets 2^{O(√n)}.

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | The Fano pieces | block: all equal; dual block: the six patterns; T14: not x0 = x1 = x2; Davis–Putnam derivations of width at most 5 |
| 2 | The Euler count on the families | every member passes; one flipped sign breaks exactly two faces |
| 3 | The corner map | dimensions agree everywhere; exhaustive bijection up to 20 points |
| 4 | Sherali–Adams | restricted level 3 infeasible with faces; feasible without them wherever faces add point sets |
| 5 | Octahedral three-fold spaces | cubic, not 2-colourable, glue a single brace |
| 6 | Resolution measurements | Davis–Putnam sizes, treewidth bounds, solver conflicts |

## What this does not establish

- **No resolution lower bound.** The conjecture of §6 is open; the solver data are upper bounds.
- **Non-planar glue.** Trisum glue is covered by theorem 5's treewidth bound, but theorem 4 needs a plane core.
- **Res(⊕), polynomial calculus, cutting planes.** Not settled. The count is invisible modulo 2, since faces − lines = 2 is even, so
  parity reasoning alone cannot see it.
