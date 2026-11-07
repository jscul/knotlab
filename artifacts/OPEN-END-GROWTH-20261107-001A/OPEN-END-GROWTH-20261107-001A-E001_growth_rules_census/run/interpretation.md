# A census of growth rules at open ends: exploratory reading

Run: `.venv/bin/python -B experiments/OPEN-END-GROWTH-20261107-001A/OPEN-END-GROWTH-20261107-001A-E001_growth_rules_census/run.py`
(2026-11-07, 1,545 s, within the 60-minute budget). Raw output: `result.json`.

## Exact bond distance

- **The method.** Bond distance is the least knot through two distinctions. It is computed exactly as
  a minimum cut whose inside and outside are both connected, by a mixed-integer program.
- **The pre-check.** Pairs split by a pinned seam (a bridge of the knot graph with the outside vertex)
  are answered "no knot" by a bridge check, following ticket B, Proposition 2.
- **Validation.**
  - The program agreed with an exhaustive circuit search on all 160 random pairs (12-knot laws, all
    five rules).
  - The bridge pre-check never contradicted the full program on 75 pairs.

## The census

| Rule | Bond distance from a seed distinction | Bond balls at 200 knots (every distinction) | Structure | Class |
| --- | --- | --- | --- | --- |
| R1 sprout at random | slope 0.94 per graph step; largest 15 at 200 knots, 17 at 400 | count doubles per step, then saturates | a tree (cycle rank 0) | small world (diameter grows like log N) |
| R2 grow at knots holding two open ends | slope 1.00; largest 105 at 200 knots, 207 at 400 | 4 per unit of radius (exponent 1.05) | a path, every inner knot holding one open end | **ruler, dimension 1** (the two-way thread) |
| R3 close the nearest pair, else sprout | no knot for 370 of 374 pairs (seed 1), 294 of 300 (balls) | — | two open ends; 74 pinned seams, 14,098 tied pairs at 300 knots | **decoupled cells** |
| R4 as R3, never creating a pin or tie | largest 5 at every separation (slope 0.003) | all 301 distinctions within 5 | four open ends; no pins or ties | **collapse** |
| R5 flat-face closing (exactly 6) | slope 0.23; largest 11 at 300 knots, 10 at 200 | 24, 48, 116, 214, 290 at r = 4..8 | 48–66 open ends, cycle rank 118–127 | small world (no plane) |

All three seeds agree on the structural counts for R3 and R4 (pins, ties, open ends), and on R5's
frontier.

## Controls

- **Connectivity control: passed.** On R3, the program without its outside-connectivity constraint
  reports finite values (4, 4, 5, 4, 4) for five far targets where the constrained program finds no
  knot.
- **R2 control: failed as frozen.** The frozen control "bond distance = graph distance + 2 for every
  target" failed because it was mis-specified.
  - The profile's source distinction is the seam between the seed and its first neighbour, not an
    open end, and graph distance was measured from the seed knot.
  - So the offset is 1 or 2 depending on the target's side and kind. A recheck of 80 targets gave:
    open ends +2: 25, +1: 18; seams +1: 21, +2: 15.
  - The slope is exactly 1.00, and the path-structure control passed.
  - Exactness, with distances measured from an open end, is proved in ticket B (Proposition 4) and
    checked there exhaustively.

## Decision rule

The rule is met:
- no rule was classified as a ruler of dimension 2;
- R2 is a ruler of dimension 1;
- the boundary principle explaining R3 and R4 is proved in ticket B.

The plane is constructed rather than grown, as the product of two lines (ticket C).
