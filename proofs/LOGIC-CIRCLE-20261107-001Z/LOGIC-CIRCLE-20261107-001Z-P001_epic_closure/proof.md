# Closure of the circles epic

Status: Proved

Ticket `LOGIC-CIRCLE-20261107-001Z`, 2026-11-07.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/LOGIC-CIRCLE-20261107-001/logic_circle.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | For the cut space of a doubly periodic plane graph, the least bond through two edges is twice the graph distance of the dual up to a constant. Its large-scale ball is half the dual's velocity polygon, whose vertices are rational, so Gołąb's self-perimeter is rational. By Niven's theorem the ball is affinely regular only as a parallelogram or a hexagon. | classical core (velocity polygons); bond reduction and rational π new as far as found; proved | A |
| 2 | For a simple line arrangement with bounded gaps, the least bond through two segments is twice the number of separating lines plus O(1). The ball is half the polar of the zonotope of the line normals. Equiangular, equally dense families give regular 2n-gons with half self-perimeter 2n sin(π/2n) (n odd) or 2n tan(π/2n) (n even); these arrangements are doubly periodic only for n = 2, 3. | classical core (partial cubes, self-circumferences); reduction new as far as found; proved | A |
| 3 | The parity laws on the 11 Archimedean and 11 Laves tilings (19 distinct) have π in {3, 10/3, 16/5, 7/2, 11/3, 4}. | computed exactly | A |
| 4 | In ℤ² with one random diagonal per unit square, the graph distance between u ≤ w is \|dx\| + \|dy\| minus the longest strictly increasing chain of correctly oriented squares. With Seppäläinen's law of large numbers, the least cycle through two far edges is 2c_p n + o(n). So the ball is a square with elliptic corners, circular when p = 1/2, with π = 3.44120 at p = 1/2. | exact formula and corners new as far as found; proved, citing Seppäläinen 1997 | B |
| 5 | The least cycle through two edges of the Delaunay graph of a planar Poisson process is μR + o(R) in every direction, with one constant μ > 0. | known in substance (Vahidi-Asl–Wierman); proved for bonds | B |
| 6 | Measured with exact least cycles: the square and honeycomb controls reproduce their polygons; split laws approach the curved squares; the Voronoi law's anisotropy falls to 1.05 at radius 60; the dual of a uniform random quadrangulation has bond distance growing like n^0.28. | exploratory experiment | C |

## Answer

- **Periodic logic makes polygons with rational π.** Coins make curved corners but keep the lattice's flat sides. Only an isotropic
  input makes a round circle.
- **Uniform randomness with nothing drawn** gives no plane at all.
- **Roundness differs from polygons in kind:** a transcendental π against a rational one, infinitely many directions against
  finitely many, and a source with no preferred direction.

## Pending the owner

- **Carried.** Whether a native knot must also be natively bound (`LOGIC-AXIS-20261107-001`).
- **Carried from earlier epics.**
  - PHASE-HALO and FACE-CLAIM qualifications.
  - The SELECTION-NOTE erratum.
  - Superseding KNOT-COMPOSE D001.
  - Counted length as a native magnitude.

## Recommendation

**Continue** (2/3), as a fresh epic: round without coins, the pinwheel law.
- **The question.** The pinwheel tiling is forced by local matching rules, and its tiles turn through the irrational angle
  arctan(1/2), so orientations are uniformly distributed. Is the circle of its parity law exactly round?
- **The first discriminator.** Measure anisotropy against radius at 5^7 tiles.
- **Alternatives.** The spectrum of rational π among periodic laws (1/3); the exact taxicab formula (1/3).

The table is in the decision note.
