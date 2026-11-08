# Interpretation: which tested periodic planes become pinwheel-legal after cutting

Experiment `COLLAR-PLANE-20261108-001C-E001` (exploratory, non-promotable; contract in
`experiments/COLLAR-PLANE-20261108-001C/COLLAR-PLANE-20261108-001C-E001_periodic_planes_after_cutting/contract.json`).

## Controls

All four held: the rhombus lattice passes after one cut; the rectangle lattice fails after one and after two cuts; the interior of a
genuine pinwheel patch (T_5) passes. The first launch stopped at the controls: its genuine-patch window, a box around the median
centroid of T_4, reached the patch's boundary, so the control failed for a reason unrelated to the law. The window was moved to the
centroid of T_5's big triangle, about eight tile sizes from its edge, and the run started again with no census result seen
(`main_log_first_launch.txt`, `main_log.txt`).

## Results (main part)

| Family | Planes | Pass after 1 cut | After 2 cuts | After 3 cuts |
| --- | --- | --- | --- | --- |
| F1 rectangle grids, diagonals of period up to 2 x 2 | 26 | 2 | 2 | 2 |
| F2 brick rows, the same diagonals | 26 | 0 | 6 | 6 |
| F3 domino tilings of the 2 x 2, 2 x 4 and 4 x 2 tori, every diagonal choice | 1,184 | 8 | 24 | not run |
| F4 the six two-tile shapes tiled by half-turns | 6 | 2 | 2 | 2 |

- **After one cut, only the rhombus lattice.** Every plane that passes after one cut is the rhombus lattice of
  `COLLAR-PLANE-20261108-001A` in another presentation:
  - the grids whose diagonals alternate like a checkerboard;
  - the two isosceles shapes, each tiled by half-turns;
  - eight domino tilings of the 2 x 4 and 4 x 2 tori.

  Each uses exactly 10 of the 108 keys after one cut, 42 after two and 96 after three, as ticket A's fundamental domain does. Checked
  after the run: uncut, each of these planes has a single collar, the rhombus lattice's, and a tiling whose every collar is that one
  is the rhombus lattice, since a collar fixes a tile's neighbours.
- **After two cuts, a second plane.** Six brick-row planes fail after one cut and pass after two and three. They use 66 keys after
  two cuts and 94 after three. 16 more domino tilings of the 2 x 4 and 4 x 2 tori fail after one cut and pass after two, using 66 keys.
  In ticket B's terms, their collars lie in the law two levels up and not in L1.
- **Everything else fails** after three cuts (F1, F2, F4) or two (F3): the plain rectangle lattice, the kite, both parallelograms and
  the rectangle shape among them.

## Background part (folded in 2026-11-08)

F3's 2 x 6, 6 x 2 and 4 x 4 tori after one cut (`collar-plane-c1`, `big1_result.json`, `big1_rows.jsonl`, `big1_log.txt`; 95,232
planes, controls held):
- **24 pass, all on the 4 x 4 torus**; none of the 12,800 tilings of the 2 x 6 torus, or of the 6 x 2 torus, passes.
- **8 are the rhombus lattice** again: uncut, a single collar, the rhombus lattice's.
- **16 are not.** They are rectangle grids, every domino parallel, with diagonals of period 4 along a row. Uncut, each has two
  collars, eight tiles each, and both lie in the arc-consistent core of ticket B's level-one law. After one cut they use exactly the
  rhombus lattice's 10 keys. So the rhombus lattice is not the only plane that obeys the collar law after one cut (checked after the
  run, as for the main part).
- **A correction.** The main part's summary, "after one cut, only the rhombus lattice", was carried into the knot intuition doc and
  the goals doc without the pending tori; it is narrowed there and logged in `docs/CORRECTIONS.md` (not a block: the theory gains
  witnesses).

## Reading

- **Periodic planes are not rare after cutting.** A cut hides the crystal's own seams under the pinwheel's local forms. Two of the
  simplest periodic planes, the rhombus lattice and a brick row, obey the collar law after one and two cuts.
- **The tested families were rejected only uncut.** `PINWHEEL-ATLAS-20261107-001B` tested these planes as they are, so its finding
  that none of them obeys the law still stands. The cut planes are new planes.
