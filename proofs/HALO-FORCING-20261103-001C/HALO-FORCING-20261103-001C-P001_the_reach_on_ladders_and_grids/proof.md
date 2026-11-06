# The reach on ladders and grids

Status: Proved as computation (exhaustive on the stated families, by a pipeline validated against exact creation)

Ticket `HALO-FORCING-20261103-001C`, 2026-11-03.

## Question

- **Background (HANDLE-LOCALITY B).** An opened handle attached at a point creates at plane gluing lines out to distance 5 on small
  plane pieces.
- **The question.** How far does it reach on large plane pieces, and does that depend on the shape of the plane glue: thin ladders
  against fat grids?

## Dependencies

- **`HALO-FORCING-20261103-001A`.** The route criterion, and creation as a function of the transfer.
- **`HALO-FORCING-20261103-001B`.** The transfer by heights (`transfer_lib.py`).
- **`HANDLE-LOCALITY-20261103-001B`.** The join method, used for exact creation (`join_lib.py`).

## Method

`halo_pipeline.py` never enumerates the plane piece.
- **The splice.** The Fano plane minus a line is spliced into a point z of the plane space (glue_lib's construction). The twist is chosen
  by theory: the splice fails exactly when the ports' consistent pair is the line's all-equal pair.
- **The transfer.** For every plane gluing line, R(L) is computed by heights on the point split.
- **The decision.** For every removal inside the handle and every far side, creation is decided by the route criterion over pairs of
  handle points. Its inputs are the handle's own solutions joined with R(L), and the far side.
- **Validation (check 1).** The Fano plane is spliced into two points of each of five grown plane spaces (10 to 14 points).
  - The fast splice equals glue_lib.splice in all 10 spaces.
  - The pipeline equals exact creation (new crossing knots up to three points, join method) in all 2,784 cases: 364 create, 2,420 do
    not.
- **Distances.** Measured in the incidence graph, from a gluing line to the nearest point or line of the handle. They only describe where
  creation was found; they are not a native magnitude.

## Results

### Ladders (prisms over 2k-cycles)

| Points | Reach | Farthest gluing line | Creating lines |
| --- | --- | --- | --- |
| 10 | 5 | 5 | 7 of 10 |
| 16 | 9 | 9 | 10 of 16 |
| 24 | 13 | 13 | 14 of 24 |
| 32 | 17 | 17 | 18 of 32 |
| 40 | 21 | 21 | 22 of 40 |
| 50 | 25 | 25 | 27 of 50 |
| 60 | 31 | 31 | 32 of 60 |
| 80 | 41 | 41 | 42 of 80 |

- **The reach.** The halo reaches the farthest gluing line at every size, so the reach grows linearly with the ladder.
- **At each distance.** At every distance with four gluing lines, exactly two create.
- **The far sides.** K4^(3) and census 6 create all along the ladder. The Fano plane and census 58 create only at the three lines through
  the cut.

### Grids (duals of the octahedron subdivided once, twice and three times)

| Points | Attachment points | Reach | Farthest gluing line | Creating lines |
| --- | --- | --- | --- | --- |
| 16 | 1 | 3 | 7 | 6 of 16 |
| 64 | 4 | 3 | 13 to 15 | 8 or 9 of 64 |
| 256 | 1 | 3 | 29 | 8 of 256 |

The reach is exactly 3 at every size.

### Why: the forcing profile (check 4)

Fix the split point's three copies.
- **On the 40-point ladder.** Every gluing line at distance 3 or more is left with exactly two patterns (an edge), however far away. The
  constraint is passed along the ladder without loss.
- **On the 64- and 256-point grids.** Every gluing line at distance 7 or more (41 and 233 lines) has the full transfer, all 36 pairs. It is
  exactly independent of the split point. At distance 5 the transfer is restricted, but no pattern set falls to two.

**Reading.** Creation needs the opened handle to force a gluing line into one or two patterns, and the plane glue carries that forcing
through its matchings.
- **A ladder** is a thin strip, frozen in the dimer sense: forcing propagates without decay.
- **A grid** is fat and liquid: the heights fluctuate, and forcing dies out within a few steps.

### Random grown spaces (check 5, recorded)

- **The reaches.** 5, 7 and 7 on 20, 30 and 40 points; the farthest gluing lines are at 7, 9 and 9.
- **So** they lie between the ladder and the grid.

## Checks

`check.py` (`result.json`, about two minutes):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Pipeline against exact creation | 2,784 of 2,784 cases agree; 10 of 10 splices equal |
| 2 | Ladders (k = 5 to 40) | reach = farthest gluing line; two of four at each distance; Fano plane and census 58 only at the cut |
| 3 | Grids (16, 64, 256 points) | reach exactly 3 |
| 4 | Forcing profile | ladder: exactly two patterns left at every distance ≥ 3; grids: full transfer at every distance ≥ 7 |
| 5 | Random grown spaces (recorded) | reach 5, 7, 7 |

## What this does not establish

- **The criterion on large spaces.** Its exactness there (no route implies new) is checked only on the small spaces of check 1. On the
  large families it is applied, not re-verified.
- **A proof of either law.** The ladder law (a periodic transfer along the strip) and the grid bound (independence beyond a few steps) are
  computed, not proved.
- **Other handles and gluings.** Only the Fano plane attached at a point is used.

## Novelty

- **New here.** The measurements and the forcing explanation.
- **Classical.** Frozen and liquid regions of dimer models (Kenyon, Okounkov and Sheffield, among others). The connection to native
  creation is new.
