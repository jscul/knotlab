# Measured circles of right-triangle substitution laws: interpretation

Experiment `PINWHEEL-ROUND-20261107-001B-E001`, exploratory and non-promotable. Run on 2026-11-07, 188 s, as frozen in `contract.json`.
- **Bond distances** are exact least cycles through two edges of each law's bond graph, minus one.
- **Directions and sources.** 24 directions; profiles average 3 sources at R ≤ 64 and use 1 source at R = 128.

## How the run was made

- **The first launch** used the pure-Python flow solver. Under heavy machine load it had produced no measurement after several
  minutes, and was stopped.
- **The replacement solver** computes the same quantity exactly: Suurballe's two shortest paths on the vertex-split graph, with
  scipy's Dijkstra.
  - It was validated against the original solver on 360 random pairs of the three tilings at small size, and on 24 pairs at full
    size, with 0 mismatches.
- **A fault, found and fixed.** A second launch exposed an integer overflow in the solver's arc keys on large graphs. It was
  stopped before any result was written. The overflow was fixed and re-validated on full-size tilings with warnings as errors.
- **The run reported here** is the third launch, which ran with warnings as errors.

## Readings

**Anisotropy** (max/min of the mean radial profile):

| Tiling / law | R = 8 | 16 | 32 | 64 | 128 | Contract reading |
| --- | --- | --- | --- | --- | --- | --- |
| 1:1 (tetrakis) / corner | 1.150 | 1.123 | 1.120 | 1.120 | 1.124 | control passes: exact octagon √5/2 = 1.118 |
| 1:1 (tetrakis) / tile | 1.321 | 1.369 | 1.389 | 1.402 | 1.410 | control passes: exact square √2 = 1.414 |
| pinwheel / corner | 1.106 | 1.073 | 1.045 | 1.033 | 1.030 | **rounding** (falls at every doubling; 1.030 ≤ 1.06) |
| pinwheel / tile | 1.326 | 1.183 | 1.143 | 1.091 | 1.078 | unresolved: falls at every doubling, but 1.078 > 1.06 |
| consistent / corner | 1.267 | 1.278 | 1.192 | 1.197 | 1.235 | unresolved: neither falling nor stalled within 0.02 |
| consistent / tile | 1.222 | 1.249 | 1.191 | 1.237 | 1.269 | unresolved, as above |

**Relative amplitude of the 4-fold harmonic, |c₄|/c₀:**

| Tiling / law | R = 8 | 16 | 32 | 64 | 128 |
| --- | --- | --- | --- | --- | --- |
| 1:1 / tile (square) | 0.120 | 0.130 | 0.138 | 0.143 | 0.145 |
| pinwheel / corner | 0.0136 | 0.0083 | 0.0064 | 0.0022 | 0.0001 |
| pinwheel / tile | 0.031 | 0.017 | 0.015 | 0.004 | 0.015 |
| consistent / corner | 0.010 | 0.055 | 0.064 | 0.073 | 0.085 |
| consistent / tile | 0.024 | 0.050 | 0.071 | 0.091 | 0.100 |

**Tile orientations within distance R of the centre:**

| R | 8 | 16 | 32 | 64 | 128 |
| --- | --- | --- | --- | --- | --- |
| pinwheel | 13 | 19 | 20 | 24 | 28 |
| consistent | 4 | 4 | 4 | 4 | 4 |
| 1:1 | 4 | 4 | 4 | 4 | 4 |

The pinwheel's count grows like log R.

## What this says

- **The pipeline reproduces exact polygons.** The 1:1 laws converge to the octagon and the square proved in ticket A, and keep their
  harmonics.
- **The pinwheel's circles round off, slowly.**
  - **Corner law.** Its anisotropy falls from 1.106 to 1.030, and its 4-fold harmonic almost vanishes by R = 128.
  - **Tile law.** It falls from 1.33 to 1.08 and has not yet crossed the contract's threshold.
  - **Why so slow.** At R = 128 only 28 orientations are present. That is the large-scale trend of ticket A's Proposition 4.
- **The same triangle cut frame-consistently does not round off.** Its 4-fold harmonic grows steadily, to 0.085 and 0.100, while the
  pinwheel's shrinks. Its anisotropy fluctuates around 1.2 to 1.27. The irrational angle alone does not round the circle; the
  tiles must also turn against each other.
- **The frozen thresholds** leave three laws unresolved: the pinwheel tile law (still falling), and both consistent laws, whose
  anisotropy is not monotone. The harmonic data, which the contract also records, separate the pinwheel from the consistent cut
  clearly.

## Limits

- **Finite radii.** Finite radii do not prove limit shapes. The pinwheel's roundness is ticket A's theorem, conditional on Radin's
  results.
- **The consistent cut** is not proved non-round. Its hull is invariant only under quarter turns, and the growing 4-fold harmonic
  is evidence, not proof.
- **Noise.** The R = 128 points use one source, so they are noisier than the rest.
