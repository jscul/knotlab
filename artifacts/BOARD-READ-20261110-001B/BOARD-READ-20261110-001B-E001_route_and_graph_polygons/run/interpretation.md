# Interpretation: route and graph polygons of four boards

Run of the frozen contract `BOARD-READ-20261110-001B-E001` (exploratory, blind on results), 2026-11-10. Readings exact.

## A correction to the run's analysis, made before reading the verdict

The first run (`result_first_run_without_torus_images.json`) compared breadth-first distances on the 48 × 48 torus with the polygon's
gauge in the plane, so on the hexagonal boards displacements whose shortest way wraps round the torus showed as deviations growing to
−238. The contract's check is of the theorem, which on a torus applies to the least gauge over the displacement's images; run.py was
amended to take that least value and rerun (`result.json`). The polygons, homotheties and anisotropies are the same in both runs.

## The hypotheses

| Hypothesis | Verdict | Evidence |
| --- | --- | --- |
| P1: square board homothetic at every g | **Holds**: route polygon = graph polygon / (2g), anisotropy √2 for both | `result.json` |
| H: on every board read the route polygon is homothetic to the graph polygon | **Holds** on all four boards at g = 2 to 6: square 1/(2g), triangular 1/(3g), honeycomb 2/(3g), kagome 1/(2g); anisotropies equal (√2 square, 2/√3 the three hexagonal boards) | `result.json` |
| The theorem's bounded error | **Holds**: route T − N within −22 and 0 lags, graph d − N_G within 0 and 1, at every distance read (to 20) | `result.json` |

## What it shows

- **The route reading is the board's graph distance times g·d/2.** The scale is half the ring's degree times g on every board read: a
  route crosses a ring by going half way round it on average over the turns a shortest path takes.
- **No board read is rounder or less round.** Every route polygon has the graph polygon's shape: a diamond on the square board, a
  hexagon on the three others.

## Nonclaims

- Four periodic boards, g = 2 to 6; the program's ring cells and contact law; declared rings (A45) on declared boards (A51).
