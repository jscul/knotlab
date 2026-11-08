# One size past: four junctions

Status: Proved (exact computation on one four-junction space, chosen before its map was computed)

Ticket `TRISUM-READ-20261107-001C`, 2026-11-07.

## Question

- **The rule.** Since 2026-11-08 the program tests a computed claim one size past the cases it was checked on, before publishing it.
- **Where the claim stood.** Tickets A and B checked the junction reading on seventeen spaces, up to 60 points and three junctions.
- **One size past.** Does it hold on a space with four junctions?

## Dependencies

- **`TRISUM-READ-20261107-001A`.** The frozen statements P1 to P7 (`predictions.json`) and the library.
- **`TRISUM-READ-20261107-001B`.** The lean enumerator (`map_lib.py`).

## The space

- **How it was chosen** (`space.json`, 20:21:59 PST, before the map). HANDLE-COUNT A's generator gives at most three trisums per
  seed. Run with four trisums over seeds 1 to 12 under hash seed 0, its smallest space is seed 7's: 62 lines and points, six atoms,
  four junctions and nine leaves. The next smallest have 76 lines.
- **Its map.** 62 rows of 5,062,500 solutions each, computed after the choice (`provenance.json`) with ticket B's lean
  enumerator in one fixed point order (`order_lib.py`).
- **The statements tested** are ticket A's P1 to P7, unchanged.

## Results

1. **Every frozen statement holds (P1 to P7).**
   - **The atoms.** Yes/no creation reads all six: the lines no removal blocks are their cores, and each root is created at by
     exactly its six core lines.
   - **The junctions.** With the atoms set aside, the pairs of lines that block only each other are exactly the four junctions'
     line pairs, so four junctions are counted. With the atoms included all four pairs are pinned too, since no junction line carries
     an atom here.
   - **Pair refinement** of the native map fixes the atoms, the skeleton lines, the junction lines, the roots, the loaded lines, the
     square-mates and the leaves.
2. **Yes/no creation is native here too.** Census 6 never creates where none of the three order-free far sides does.
3. **An engineering lesson.** Ticket B's enumerator walks the points breadth-first from point 0 of the space minus the removed line.
   Here that order keeps up to 34 lines open at once in most rows, and a first run finished one row in 77 minutes. One fixed order
   for every row, breadth-first through the whole space from point 8, keeps at most 19 open (`order_lib.py`). The solutions do not
   depend on the order: on row 0 it returns the same array as ticket B's enumeration and as the full-memory one (check 2).

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; tickets A and B Proved | pass |
| 1 | The space: regenerated exactly, the smallest candidate, four junctions; chosen before its map | pass |
| 2 | Three rows in the fixed order; row 0's solutions by both other enumerators | equal |
| 3 | P1 to P7 | all hold |
| 4 | Census 6 never creates alone | 0 entries |

## What this does not establish

- **Every four-junction space.** One space is tested, the smallest the generator gives.
- **A proof.** The junction signature is still measured, not derived.

## Novelty

- **New here.** The measurement.
