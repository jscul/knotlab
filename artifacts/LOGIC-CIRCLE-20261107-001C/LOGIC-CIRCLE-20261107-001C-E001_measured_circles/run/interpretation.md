# Measured circles of random laws: interpretation

Experiment `LOGIC-CIRCLE-20261107-001C-E001`, exploratory and non-promotable. Run on 2026-11-07, 287 s, as frozen in
`contract.json`. Bond distances are exact least cycles of each law's plane dual through two dual edges, minus one.

## Readings

| Law | Radii | Anisotropy (max/min of the mean radial profile) | Deviation from the prediction (max, relative) | Reading under the contract |
| --- | --- | --- | --- | --- |
| square (control) | 10, 20, 40 | 1.363, 1.387, 1.400 (exact polygon: √2 = 1.414) | 0.150, 0.075, 0.038 | control passes (within 0.05, below 0.1) |
| honeycomb (control) | 10, 20, 40 | 1.134, 1.144, 1.149 (exact polygon: 2/√3 = 1.155) | 0.100, 0.050, 0.025 | control passes |
| split, p = 1/2 | 20, 40, 80 | 1.148, 1.189, 1.167 (limit 1.207) | 0.158, 0.108, 0.080 | consistent with ticket B: the deviation falls with R |
| split, p = 1/4 | 20, 40, 80 | 1.320, 1.287, 1.287 (limit 1.319) | 0.182, 0.116, 0.057 | consistent with ticket B |
| Poisson-Voronoi | 10, 20, 40, 60 | 1.153, 1.104, 1.073, 1.054 | (round predicted) | round: falls with R, below 1.06 at R = 60 |

**The uniform random quadrangulation law.** Mean bond distance between random variables is:

| n | 1,000 | 4,000 | 16,000 | 64,000 |
| --- | --- | --- | --- | --- |
| mean bond distance | 17.4 | 26.8 | 41.1 | 56.2 |
| mean graph distance in the quadrangulation | 7.9 | 11.7 | 18.5 | 25.7 |

- The least-squares slope of log(bond distance) against log n is 0.284. The last step, from 16,000 to 64,000, gives 0.226.
- A plane gives 0.5 and the Brownian map 0.25. By the contract's rule (slope at most 0.35), the law is **not a plane**.
- Between 62% and 65% of the drawn pairs (106 to 118 per size, against 64 measured pairs) had no common bond, so their bond distance
  is infinite; they were counted and skipped.
  - Such pairs lie in different 2-connected blocks of the quadrangulation, cut apart by pendant edges and other cut vertices.
  - In the law, such variables share no knot.

## What this says

- **The pipeline reproduces exact polygons.** The square and honeycomb controls converge to √2 and 2/√3 at the rate of the bounded
  excess (deviation halves when R doubles).
- **Coins bend the circle, but the lattice stays visible.** The split laws converge more slowly than the controls, as last-passage
  fluctuations predict (corrections of order R^(-2/3) rather than R^(-1)), but toward ticket B's shapes, not toward a disc:
  - at p = 1/4 the anisotropy is already at its limit, 1.32;
  - at p = 1/2 it sits between 1.15 and 1.19, against a limit of 1.21.
- **Isotropic randomness rounds the circle.** The Voronoi law's anisotropy falls steadily toward 1, as the isotropy argument of ticket B
  predicts. Its roundness comes from the Poisson input, which is drawn in the Euclidean plane.
- **Uniform randomness with nothing drawn gives no plane.** A uniformly random planar law of four-place knots has bond distances growing
  like n^0.28 at these sizes, near the Brownian map's n^(1/4) and far from a plane's n^(1/2). It is a space of dimension about 4, the
  same in every direction but not flat.

## Limits

- **Finite sizes.** Finite radii and sizes do not prove limit shapes. The Voronoi law's roundness is proved in ticket B; the
  quadrangulation exponent is the literature's (Chassaing–Schaeffer 2004; Le Gall 2013; Miermont 2013).
- **Sampling.** The profiles average 4 sources per radius. Their fluctuations make the split-law anisotropy non-monotone at p = 1/2.
