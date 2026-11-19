# Advisor question 1 (JUNCTION-MAP-20261119-001, before the freeze)

Analysis please; I will check it. This is short, and I ran everything myself.

**Setting.** The cheapest parity growth and the cluster rule as before. The growth continued from its stage after s rounds equals
the growth of that stage taken as a start, with its junctions as knots and the live ones the last round's. In the break-shape eddies
(BREAK-EDDIES-20261119-001), 36 starts grow with W = y^2 (1 + y), the plastic number, and every loop of at most three steps needs a
first-round group of three. The go-ahead asks for a map with first-round junctions as points, which admits the rule's excluded case
(a group of three sharing two knots with another block) as a loop of length two.

**Pilot results (disclosed).**
1. **Knot-level map, cut lifted** (the overlap kept as two blocks forming a 2-cycle). It differs from the growth at round 2 on all
   36, and overcounts heavily (22 against 16 at round 2; rate about 3.3).
2. **Junction map** (the stage-1 or stage-2 presentation, cut lifted). It equals the growth for one round, then differs at the
   second round on all 36, at both s = 1 and s = 2.
3. **Control, ordinary eddies** (the ring of five with a spare, five five-place knots, the ring of seven with a spare). At s = 1 the
   stage is inside the rule's scope, and the junction map equals the growth for 8 rounds. At s = 2 and 3 the stage already holds the
   overlap, and the cut-lifted map differs at the second round. Yet the knot-level rule on the original start is exact. Two touching
   knots and a chain of three are exact at s = 1, 2, 3, with no overlap.
4. **Merged reading** (the overlapping group of three demoted to an ordinary simplex and merged). It differs at round 1 on all.

**My reading.** A group of three that shares two knots with a block is not a loop of length two. In the growth, going round that
2-cycle reaches the same junction again, where the unrolled map counts a new cluster on each wrap. It is the same identification as
the rule's first break (two clusters, one junction). The ordinary rings show that the knot-level unrolled map handles these overlaps
correctly when they arise later, so the break-shape eddies' short loops must be read at the knot level, not from a later stage.

**Planned freeze.** On the 80 other rational break-shape starts, the referee's two six-knot eddies, the 5 catalogue entries, the
rings of 9 to 13 knots with a spare, and two touching knots and a chain as controls, at s = 1, 2, 3:
- **J1.** Where the stage holds an overlap, the junction map equals the growth at round s + 1 and differs by round s + 2.
- **J2.** Where it holds none, it equals the growth for 8 rounds.
- **J3.** The knot-level cut-lifted map differs by round 2 on every rational break-shape start.

## Questions

1. Is my reading of the failure right? Can you make the identification exact: which pairs of clusters on the unrolled map does the
   growth make into one junction when a group of three shares two knots with a block?
2. Given that identification, is there a corrected count whose series could give W = y^2 (1 + y) for such a start? Sketch it on the
   smallest example: two triangles of knots joined so that their first-round groups of three share two knots with the joining block.
   Or explain why no cluster count can.
3. Are J1 to J3 the right confirmatory tests, and what would you add?
