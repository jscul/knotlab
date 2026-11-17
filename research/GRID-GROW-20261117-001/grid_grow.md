# Growing the two-way grid with knots, one at a time

Epic `GRID-GROW-20261117-001`, 17 November 2026, by Claude, on the coordinator's go-ahead. Goals G1 and G16; tests A97. Referee
pending. Pre-registration: [preregistration.md](preregistration.md), frozen in commit `675e4ef24` at 20:30:26 UTC; the run went
from 20:30:26 to 20:30:40 UTC. Proof: [proof.md](../../proofs/GRID-GROW-20261117-001A/GRID-GROW-20261117-001A-P001_grid_growth/proof.md).
Code: [gridgrow.py and run.py](../../experiments/GRID-GROW-20261117-001B/GRID-GROW-20261117-001B-E001_covers/). Results:
[results.json](../../artifacts/GRID-GROW-20261117-001B/GRID-GROW-20261117-001B-E001_covers/results.json).

## The answer

**The grid's two independent orders can be grown from betweenness knots one distinction at a time, with fixed costs** (proved;
every case in a 4 × 4 box checked). The knot is "b lies between a and c". The two orders are the grid's own arrangement of places,
its row and column cuts (the classical halfspaces of a product of two paths), and the placement of each new distinction is given.
The growth reads and extends that meeting pattern's own two orders. *Scoped on 17 November 2026, after `KNOT-ORDER-20261117-001`'s
referee, before this study's own.*
- **A new line costs one knot, and that knot is forced.** A new line is the first cell of a new row or column. Its knot ties the
  new cell to its neighbour and to the opposite corner, the one cell on the far side of every cut. No other single knot works.
  This is the line's growth at an end, done along the shape's two far corners. In all 66 such steps there was exactly one such
  knot, and it was that one.
- **A filled cell costs exactly three knots, and they can stay in its unit square.** Two never suffice. The three that use only
  the cell's three neighbours in its unit square are the only cover that close: "the new cell between its left and lower
  neighbours", and "each of those between the corner and the new cell". In all 71 fills the minimum was 3, reached within the unit
  square by exactly one cover, all betweenness knots. A single four-place parity on the unit square also does it. That parity is
  the cut system's own law: a cut crosses a unit square through opposite sides or not at all.
- **Totals do not depend on the order.** Growing the 4 × 4 square from the three-cell L took 32 knots both ways, arms first then
  filling, and row by row. That is 5 new lines plus 3 × 9 fills, exact at every step.
- **The states name every placement.** On every shape the disagreement count is twice the L1 distance, and the knot base is
  exactly the row and column cuts (69 of 69). So an outside rule that uses only the states, with names and history erased, can
  find the outer corners, the neighbours and the opposite corners. The knots do not choose; the rule does.

In the owner's terms: a base of knots alone holds the grid's two independent orders, and it can be grown one distinction at a
time. Reaching far is needed only to start a line, where the new cell is tied to the far corner, so in that sense every cell
relates to all the others. Everything inside is filled locally. The two-way structure is this meeting pattern's own: the growth
reads and extends it, and nothing here shows a law choosing to grow two ways.

| Step | Knots | Reach (largest L1 from the new cell) | Unique? |
| --- | --- | --- | --- |
| new line, from two or more cells (66) | 1 | the opposite corner | yes, always the same knot |
| new line, from one cell (2) | 0 | — | — |
| filled cell (71) | 3 | 2, inside the unit square | yes, within L1 radius 2 |
| filled cell, with a four-place knot | 1 (unit-square parity) | 2 | — |

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| P1 | base = cuts and d = 2·L1 on all 69 shapes | held | 69 of 69 |
| P2 | new line: minimum 1, one single cover {opposite corner, neighbour, p}, betweenness; from one cell 0 | held | 66 of 66; 2 of 2 |
| P3 | filled cell: minimum 3, reached at radius 2 by exactly one cover, all betweenness; parity covers | held | 71 of 71 |
| P4 | growth exact at every step; 32 knots in both orders | held | both |

4 of 4 held. As pre-registered, P4 is bookkeeping: each step kills exactly the bad states by construction.

**Not predicted.** In the grown 4 × 4 square the busiest distinctions, the inner cells (1, 1), (2, 1) and (1, 2), each sit in 9
knots. The sharing is bounded and local, since each filled square uses three of its neighbours. The far-reaching knots are the 5
new-line knots, each holding an opposite corner.

## What it means for A97

*Scoped on 17 November 2026, after `KNOT-ORDER-20261117-001`'s referee.* Under the ruler of A98's exact betweenness, d = 2·L1, a
base of betweenness knots holds the grid's two independent orders, its rows and columns, with nothing skipped, and its base is
determined by its pair counts. It grows one distinction at a time, and an outside rule that reads only its states finds where the
next knots go.
- **By `WEAVE-LAWS-20261117-001`'s transfer-gap reading, the grid base is frozen.** The 4 × 4 grid has 14 states for 16
  distinctions. So a comparison with the weave would cross two readings, and none is made.
- **The two orders are put in by where the knots go and read back.** They are the classical cut system of a product of two paths.
- **What is new is the growth accounting.**

A97 stays under challenge. Under A98's reading it has a two-way case built from knots, on a given meeting pattern.

## What the knot picture explained

- **Two kinds of growth, two costs.** Starting a line is end growth: the new cell's knot must straddle every cut, which only the
  opposite corner does. Filling is local: each cut through the new cell's square is caught by one of three knots inside it.
- **The parity knot.** The cut system's law on a unit square is a four-place parity, the knot that hides the most. Three
  betweenness knots do the same job, so here the parity knot is the compact form of three three-place ones.

Known mathematics, labelled: Young diagrams as median-closed subsets of the grid, halfspaces as Djoković–Winkler classes,
squaregraphs, and the duality of cuts and cycles. Local: the growth accounting and the uniqueness of the new-line knot.

## Limitations

- Shapes are Young diagrams in a 4 × 4 box, grown from one corner.
- Three-place knots, plus the one four-place parity tried.
- The meeting pattern is given: the growth fills a two-way pattern, and no law here chooses to grow two ways.
- The base is nearly frozen: 2(r + c) − 2 states for r·c distinctions.

## Reproduce

```sh
python3 -B experiments/GRID-GROW-20261117-001B/GRID-GROW-20261117-001B-E001_covers/run.py
```

## Advisor

Consulted before the freeze. It:
- proved the corner-fill lower bound and gave the full cover family;
- gave the new-line knot's uniqueness and the order-independent totals;
- corrected my claim that the fill knots must lie in the unit square: three are needed, and keeping them local is a choice.

Not consulted after the read-out.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: grow two independent orders with knots | **Status:** Successful (referee pending) | One forced knot per new line, three per filled cell, order-independent totals, placements named by the states; 4 of 4 held |
| Local direction: dimension built by knots | Promising | Grown in two dimensions on a given pattern; whether a law chooses its dimension is open |
| Broader exploration: knots alone, nothing given | Unexplored | A rule reading only the states that decides by itself to start a second line |
| Long-term goal: G1 and G16 | Capability gained | A base of knots alone holds and grows the grid's two orders; an outside rule reading only the states finds each next step |

**Next step:** Research directions. None is selected; the first starts on the coordinator's go-ahead.

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A law that chooses: a uniform rule that reads only the states and adds knots, then which shapes it grows (a line, a grid, a tree) and whether two orders are typical or rare | 3/3 | 2/3: the cover costs are known now | Freeze a few state-reading rules and grow to n = 16 → stop at the shapes and their frequencies | Alternative |
| 2 | Three independent orders: the same accounting on a three-way grid (a filled cell costs how many?) | 2/3 | 3/3 | Census of plane-partition shapes in a 3 × 3 × 3 box → stop at the costs | Alternative |
| 3 | Fewer states: whether hidden distinctions or joint facts let a two-way order keep more states | 1/3 | 2/3 | Census on small grids → stop at a bound | Alternative |

**Corrections:** none.

**Goals:** a G1 and G16 checkpoint (capability gained); no goal changed.

**Assumptions:** A97 stays Under challenge, with a positive case in two dimensions; no new entry.

**Basket:** read; B195 (outlines) is left to its owner.
