# Growing the grid: one knot for a new line, three for a filled cell

Status: Proved

Ticket `GRID-GROW-20261117-001A`, 17 November 2026, by Claude. Epic `GRID-GROW-20261117-001`. The frozen census of ticket B checks
every statement on all Young diagrams in a 4 × 4 box. The proofs below follow the advisor's derivation, which I checked.

## Words

- **Shape.** A shape S is a Young diagram: cells (x, y) with x, y ≥ 0, closed downward and leftward.
- **Cut system.** Its cut system is the base whose states are the column cuts {x ≥ k}, the row cuts {y ≥ k}, their flips and the
  two constants.
- **Steps.** A step adds an outer corner p. It *starts a new line* when p = (x, 0) or (0, y), and *fills a corner* otherwise. A
  filled corner has a = (x − 1, y), b = (x, y − 1) and c = (x − 1, y − 1) in S.
- **B(u, v, w)** is the betweenness knot: v lies between u and w.

## Statements

- **G1. The static base.** For every shape, the base of B on every triple with the middle cell in the box of the other two (box ∩
  S) is the cut system. Its disagreement count is 2·L1, which is twice the shape's graph distance.
- **G2. A new line costs exactly one knot, and that knot is unique.** Let p = (x, 0) start a new column, so b = (x − 1, 0) is its
  neighbour. Let z = (0, top) be the opposite corner, the one cell left of every column cut and above every row cut. Then B(z, b, p)
  alone extends the cut system, and no other single three-place knot does. Starting a new row is the mirror. From a single cell the
  step costs nothing.
- **G3. A filled corner costs exactly three knots.** No two three-place knots extend the cut system. Three do. The unit-square
  three, B(a, p, b), B(c, a, p) and B(c, b, p), are the only cover with every cell within L1 distance 2 of p. Every knot in a
  minimum cover is a betweenness knot. The four-place parity a + b + c + p even, the cut system's own relation on a unit square,
  also extends it alone.
- **G4. Totals do not depend on the order.** Growing an r × c rectangle from the three-cell L, which is one knot, costs
  (r + c − 3) + 3(r − 1)(c − 1) three-place knots in all: 32 at 4 × 4. With the parity on each filled square it is
  (r + c − 3) + (r − 1)(c − 1).
- **G5. The states name the placements.** By G1 the counts give the L1 geometry of the shape, up to its symmetries. So the outer
  corners, the neighbours a, b, c and the opposite corners are all read from the states, with names and history erased.

## Proofs

**G1.** A Young diagram is an isometric, median-closed subset of the grid: monotone staircase paths stay inside it, and among three
cells one dominates the coordinatewise median. The allowed states of every box triple are the sets that are convex with convex
complement. In a partial cube these are exactly the sides of its Djoković–Winkler classes, which here are the row and column cuts.
Distance in a partial cube is the number of classes separating two cells, so d = 2·L1. ∎

**G2.** On every old state p must take b's value: in row 0 for row cuts, and right of every column cut. The one new state is p
flipped alone, the new cut. A knot on (u, v, p) kills the bad state of a non-constant cut exactly when p's correct value is fixed by
(u, v). That needs u and v on opposite sides of every non-constant cut, with b's value read off. In a Young diagram the only cells
on opposite sides of every column cut and every row cut from b are z = (0, top). The other antipodal pair exists only for a full
rectangle, and it fails once both row and column cuts exist. The knot excluding exactly the wrong patterns on (z, b, p) is
B(z, b, p). ∎

**G3.** Three kinds of bad state must each be killed:
- p flipped while a, b, c agree;
- p wrong under the column cut C_x through the square;
- p wrong under the row cut R_y through the square.

A pair (u, v) with p kills a bad state exactly when p's correct value is constant on that state's classes of (u, v).
- *The constant states.* Killing p flipped there forces u up and left of p and v down and right. Such a pair is separated by both
  C_x and R_y, so it kills neither.
- *C_x and R_y together.* One pair would need a cell with x′ ≥ x and y′ ≥ y. None is in S, since p is an outer corner.

So no knot kills two of the three kinds, and three knots are needed. The unit-square three kill one kind each:
- B(a, p, b) kills p flipped while a and b agree;
- B(c, a, p) fixes p under R_y;
- B(c, b, p) fixes p under C_x.

Within L1 radius 2 of p the only cells are a, b and c, so this cover is unique there. On every cut state p equals a + b + c mod 2,
since a cut crosses the unit square through opposite sides or not at all. So the parity also covers alone. That a minimum cover's
knots are betweenness knots is checked by the census, not proved here. ∎

**G4.** Each new line costs one knot (G2) and each filled cell three (G3), whatever the order. The rectangle has r + c − 3 new-line
steps beyond the L and (r − 1)(c − 1) filled cells. ∎

**G5.** From G1. ∎

## Provenance

- **Classical:** Young diagrams as median-closed subsets of the grid; halfspaces as Djoković–Winkler classes (Djoković 1973;
  Winkler 1984); squaregraphs (Bandelt, Chepoi and Eppstein); the unit-square parity as the duality of cuts and cycles over two
  values.
- **Local:** the growth accounting (one knot per new line, three per filled cell), the uniqueness of the new-line knot, and the
  reading in the program's terms. Neither I nor the advisor knows a source for them.
- **The advisor** gave G3's lower bound, the cover family, G2's uniqueness and G4's totals. It corrected my "all inside the unit
  square": three are needed, and keeping them local is a choice.
