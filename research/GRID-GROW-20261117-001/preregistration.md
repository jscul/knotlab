# Growing the two-way grid with knots, one at a time: pre-registration

Epic `GRID-GROW-20261117-001`, 17 November 2026, by Claude, on the coordinator's go-ahead (the first direction of
`KNOT-ORDER-20261117-001`). Goals G1 and G16; tests A97. Frozen before any read-out of ticket B. The canonical K1–K3 test is
unchanged.

## The question

`KNOT-ORDER-20261117-001` grew a line, one order, one betweenness knot at a time, with its own states naming where each next knot
must go. Statically, betweenness on every box of a grid holds two independent orders, its row cuts and its column cuts. Can that
two-way base be grown the same way? For each new distinction: how many knots, which ones, how far they reach, and do the states
name them?

The shapes are a given sample, Young diagrams inside a 4 × 4 box. As before, what is read is this meeting pattern's own two
orders. Nothing here shows a law choosing to grow two ways.

## Ticket A: the proof

`proofs/GRID-GROW-20261117-001A/GRID-GROW-20261117-001A-P001_grid_growth/proof.md`.
- **G1.** On every shape the box-betweenness base is the cut system, and d = 2·L1.
- **G2.** A new line costs exactly one knot, B(opposite corner, neighbour, new), and that knot is unique. From a single cell a step
  costs nothing.
- **G3.** A filled corner costs exactly three knots. They can sit in the unit square, where they are the only cover within L1
  distance 2. The unit-square parity also covers.
- **G4.** Totals do not depend on the order: 32 three-place knots to grow 4 × 4 from the three-cell L.
- **G5.** The states name every placement.

## Ticket B: computations

- **C1.** All 69 Young diagrams in the 4 × 4 box: whether the box-betweenness base equals the cut system, and whether d = 2·L1.
- **C2.** Every step (shape, outer corner in the box), with the old base taken as its exact cut system. The read-out:
  - the minimum number of three-place knots, and the minimum using only cells within each L1 radius of p;
  - the number of distinct single-knot covers and their cells;
  - the number of distinct three-knot covers within radius 2, and whether all their knots are betweenness knots;
  - whether the unit-square parity alone covers.
- **C3.** Growth from the three-cell L to the 4 × 4 square in two orders, arms then fill and raster. At each step the most local
  minimum cover is added, and the base is recomputed by brute force from all knots. The read-out is exactness at every step, knots
  added and reach, total knots, and the most knots on one distinction. By construction this is a bookkeeping check, not new
  evidence.

## Predictions (frozen; checked with the advisor)

| # | Prediction | Fails when |
| --- | --- | --- |
| P1 | C1: base = cut system and d = 2·L1 on all 69 shapes | any shape fails |
| P2 | Every new-line step from a shape of two or more cells: minimum 1, exactly one single-knot cover, with cells {opposite corner, neighbour, p}, a betweenness knot; from a single cell: minimum 0 | otherwise |
| P3 | Every corner fill: minimum 3, never 2; the minimum is reached at radius 2 by exactly one cover, the unit-square three, all betweenness; the unit-square parity covers alone | otherwise |
| P4 | C3: exact at every step in both orders; 32 three-place knots in all for both | otherwise |

**What would count against it.**
- A two-knot fill.
- A second single new-line knot.
- A non-betweenness knot in a minimum cover.
- Order-dependent totals.
- A shape whose base is not its cuts.

**The headline, stated before running.** Two independent orders grow from betweenness knots.
- Each new line costs one knot. It ties the new cell to its neighbour and to the opposite corner, the one cell across every cut:
  the line's end growth along the antipodes.
- Each filled cell costs exactly three, and they can be kept inside its unit square.
- The states name every placement.
- The far reach is needed only to start a line; filling is local.

**Classical:** Young diagrams as median-closed subsets of the grid, halfspaces as Djoković–Winkler classes, squaregraphs, and the
parity of a unit square as the duality of cuts and cycles. **Local:** the growth accounting and the uniqueness of the new-line
knot.

## Prior work in the program

`python3 -B scripts/track.py objects "growing two independent orders grid cuts knots" --until 2026-11-17 --exclude GRID-GROW-20261117-001`

- `KNOT-ORDER-20261117-001`: the line grown by knots, and the static grid (the predecessor).
- `LOGIC-AXIS-20261107-001`: "a native parity plane needs a distinction per lattice direction"; grids read through bond distance.
- `OPEN-END-GROWTH-20261107-001`: growth at open ends gives a line, not a plane.
- `DISTANCE-DIM-20261117-001`: implication grids read back their order dimension; nearness levels on the weave.
- `DISTANCE-ORDER-20261117-001`: betweenness in the disagreement count is a three-place constraint.

## Runs and stop rule

One script, `run.py`, one process, expected under ten minutes. The study stops after its read-out, followed by A97 status, the
decision note, the referee hand-off and the report.

The advisor was consulted before this freeze. It:
- gave G3's lower bound, the full cover family, G2's uniqueness and G4's totals;
- corrected my prediction that the corner-fill knots must lie in the unit square: three are needed, and keeping them local is a
  choice.
