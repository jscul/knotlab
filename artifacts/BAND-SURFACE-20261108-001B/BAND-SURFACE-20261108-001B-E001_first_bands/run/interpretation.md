# A census of first bands: interpretation

Experiment `BAND-SURFACE-20261108-001B-E001` (exploratory), run 2026-11-08 under the frozen contract: every rotation system of a loop
plus one band, 1,813,632 in all, in 20 s. Exact, with no lag cutoff. Counts are in `result.json`.

## Control

`BAND-SURFACE-20261108-001A`'s checks, and `GROW-NET-20261108-001A`'s exact test.

## Primary observable

| Loop and band | Rotation systems | Balanced, by genus (with a flip at every contact / without) |
| --- | --- | --- |
| 3 rings, single rungs | 64 | none |
| 4 rings, single rungs | 256 | genus 0: 2 / 0 (the cube); genus 1: 8 / 0 |
| 5 rings, single rungs | 1,024 | genus 2: 0 / 20 |
| 6 rings, single rungs | 4,096 | genus 1: 2 / 0; genus 2: 0 / 30; genus 3: 2 / 18 |
| 7 rings, single rungs | 16,384 | genus 3: 0 / 112 |
| 8 rings, single rungs | 65,536 | genus 1: 2 / 0; genus 3: 2 / 124; genus 4: 0 / 112 |
| 3 rings, double rungs | 46,656 | genus 1: 8 / 0 (the 3 × 2 torus); genus 2: 0 / 384; genus 3: 8 / 216 |
| 4 rings, double rungs | 1,679,616 | genus 1: 16 / 0 (the 4 × 2 torus); genus 3: 80 / 3,872; genus 4: 0 / 6,080 |

## Reading against the decision rule

- **H1 holds.** A balanced first band lies on the sphere only once: single rungs on a loop of 4 rings, the cube.
- **H2 holds.** With double rungs the n × 2 torus is among the balanced first bands, as `BAND-SURFACE-20261108-001A` proves.
- **Beyond the torus.** Most balanced first bands lie on surfaces of genus 2 to 4 and have no flip at every contact: balance without the
  symmetry that the proofs use. With single rungs the torus appears for loops of 4, 6 and 8 rings.

## Nonclaims

- **One band**, loops of 3 to 8 rings (single rungs) and 3 to 4 (double rungs).
- **Two-time knots only** (A30).
