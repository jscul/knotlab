# The Sperner reduction needs only a flat disc

Status: Proved by hand. The statements are those of `FLAT-STATES-20261107-001`, carried from the octahedral sphere to every two-kind
sphere. The holonomies, the flat states, the cut paths and the measurements are checked by computation.

Ticket `HARD-FLAT-20261107-001A`, 2026-11-07.

## Standard statement

**Setting.** Two-kind knot spheres (co-lines of two or three points) with the local Kasteleyn sign rule, as in
`SPHERE-GROWTH-20261107-001A`. Each has exactly six digons. The **flat radius** r(S) is the largest r for which some ball of radius r in
the vertex graph of T is a corner-free embedded hexagon.

**Theorem 1 (flat states on every two-kind sphere).**
- The frames of `FLAT-STATES-20261107-001A` are flat around every three-point face and have label holonomy −1 around each digon.
- So, wherever six disjoint cut paths run from the triangles around a point z to the six digons, the flat state cut along them violates
  exactly one line, through z.

**Theorem 2 (the reduction needs only a flat disc).** Suppose S contains a corner-free lattice triangle R of side 2m (m ≥ 3), and six
disjoint cut paths run from three adjacent pairs of R's boundary edges to the six digons. Then the reduction of one-sided Sperner_m in
`FLAT-STATES-20261107-001B` holds on S verbatim. So, by `SPHERE-WIDTH-20261107-001B`, the knot on S needs resolution width at least
c·m, for an absolute constant c > 0.

**Corollary (hardness follows the flat disc, not roundness).**
- If the largest flat disc's rim reaches the digons by disjoint cut paths, the width is at least c′·r(S).
- It is at most O(√n) on every two-kind sphere.
- So spheres whose flat radius is of order √n need width Θ(√n), whether they are round or not.
- The octahedral spheres have r = 0.25 √n. In the sample, grown lopsided spheres (`GROW-COIN-20261107-001`) have r between 0.14 and
  0.35 √n, while a capped tube's r is bounded by its circumference.

## Nearest known result

- **Sources.** The flat states, the Sperner reduction and the grid Sperner width bound are `FLAT-STATES-20261107-001A`,
  `FLAT-STATES-20261107-001B` and `SPHERE-WIDTH-20261107-001B`, proved there for the octahedral sphere.
- **Sperner's lemma as a search problem** is classical: PPAD (Papadimitriou 1994), Ω(√N) queries (Crescenzi–Silvestri 1998), and
  tree-like resolution 2^Θ(n) (Itsykson, Malova, Oparin and Sokolov 2014).
- **Classification.** Known-with-delta. New: the reduction needs only a flat disc, so the knot's hardness on a sphere follows its
  largest corner-free disc, not its roundness.

## Proof of Theorem 1

- **The holonomy is local.** A face's holonomy composes the frame moves of its corners. Each move depends only on the line's rotation
  in the plane embedding and on its two signs. Under the local Kasteleyn rule:
  - around a three-point face the composite is trivial;
  - around a digon it is a sublattice turn plus a complement, a label shift of −1.

  This is the computation of `FLAT-STATES-20261107-001A`, which uses nothing beyond the face and its signs.
- **Flat states.** The sphere cut along a star of disjoint paths from z to the six digons is a disc, so a frame develops over it
  consistently.
  - Across a cut path the frame changes by one digon's holonomy, a label shift of 1. So every line away from z sees labels within two
    consecutive values and is not violated.
  - At z the six labels appear in cyclic order, and one line there is violated.

  These are the steps of `FLAT-STATES-20261107-001A`, which use only the star and the holonomies. ∎

## Proof of Theorem 2

The reduction in `FLAT-STATES-20261107-001B` uses three ingredients:
1. R holds no corner, so frames develop over R (Theorem 1);
2. a flat state outside R, with its vortex in R and its cut star crossing R's boundary in three adjacent pairs, one after each corner
   of R, and then running on to the six digons;
3. the local lemma inside R.

None of them uses the octahedral geometry beyond R and the cut paths. So the map Φ from Sperner colourings to assignments of S is
defined as before:
- its violated lines lie exactly in the full triangles oriented like the boundary;
- each point reads at most two Sperner colours.

A Duplicator for Sperner_m in the pebble game then becomes one for S by answering each point through its at most two colours. By
Atserias–Dalmau and the width bound Ω(m) for Sperner_m (`SPHERE-WIDTH-20261107-001B`), the knot on S needs width at least c·m. ∎

## Proof of the corollary

- **Lower bound.** A flat disc of radius r contains a corner-free lattice triangle of side about r, one wedge of the hexagon. Inside
  the flat disc, its boundary pairs can be joined to the disc's rim. So if the rim reaches the digons by disjoint cut paths,
  Theorem 2 gives width at least c′·r.
- **Upper bound.** Points are the triangles of one colour, and two points share a line inside that line's triangle. So the primal
  graph is planar with treewidth O(√n), and Davis–Putnam elimination along a tree decomposition refutes in width O(√n). ∎

## Checks

`check.py`, with `flatdisc_lib.py` (which runs `flat_lib` of `FLAT-STATES-20261107-001A` on general spheres), takes under a minute
and reproduces `result.json`. The spheres are K_4..K_10, four capped tubes and eight grown lopsided spheres of 106 to 504 triangles.

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependency artifacts bound by hash; upstream proofs Proved | pass |
| 1 | Every three-point face has holonomy 0 and each of the six digons −1, on every sphere | pass |
| 2 | Six flat states per sphere, each with exactly one violated line, through its vortex | pass |
| 3 | On K_m and every grown sphere the largest flat disc's rim (radius ≥ 2) reaches the digons by disjoint cut paths. On the two tubes of circumference 9 the largest disc reaches around the band and its paths fail. Flat radius 0.25 √n on K_m and 0.14 to 0.35 √n on grown spheres; elimination width 2.1 √n and 1.2 to 1.9 √n | pass |

## What this does not establish

- **The constant c is not computed,** and the cut-path condition is checked on examples, not proved in general. On a thin tube the
  largest disc reaches around the band, and a smaller disc must be used.
- **Whether random accretion stays fat as n grows** is not known: the sample reaches 252 points.
- **Resolution size** is not addressed. The island argument of `SPHERE-SIZE-20261107-001` may also need only flat regions.
- **No proof system beyond resolution,** and no P vs NP claim.
