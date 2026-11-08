# Regrowth with the labels dropped: interpretation

Experiment `PINWHEEL-ATLAS-20261107-001D-E001`, exploratory and non-promotable. Run on 2026-11-07, 748 s, as frozen in
`contract.json`.

## Readings

**What is tested.** Every dart of the growing patch T_k (one triangle cut k times), boundary darts and their neighbours included,
grouped by its unlabelled rooted code. The patch's outer face is marked by one outside vertex that the code records as a leaf and
never expands.

| Level | Darts | Codes at r = 1 / 2 / 6 | Conflicting codes at r = 1 (next to the boundary) | Conflicting codes at r = 2 … 6 |
| --- | --- | --- | --- | --- |
| 4 | 2,202 | 577 / 1,593 / 2,202 | 10 (10) | 0 |
| 5 | 10,822 | 612 / 2,771 / 9,927 | 14 (14) | 0 |
| 6 | 53,746 | 615 / 2,960 / 26,825 | 15 (14) | 0 |
| 7 | 267,766 | 614 / 2,982 / 34,659 | 15 (14) | 0 |

**Pooled over levels 4–7.**
- **The least conflict-free radius is 2.** At radius 2 there are 3,227 codes with no conflict. At radius 1 there are 693 codes, 15
  of them with two labels.
- **The outside mark is not needed.** Without it, radius 1 has 32 conflicts and radius 2 again has none, with the same 3,227 codes.
  The boundary's shape shows through the vertex degrees.

**Control.** Labels shuffled over the level-6 darts conflict on 2,623 radius-2 codes.

## What this says

- **Decision.** By the frozen rule, the bare growing patch carries its own labels within radius 2, its boundary included, at every
  tested level.
- **No memory is needed to regrow.** The eleven-label regrowth rule of `PINWHEEL-NATIVE-20261107-001A` can run on the bare patch:
  read every label within radius 2, then cut.
- **The answer to the shared question, for regrowth.** Regrowth needs no hidden information beyond the patch's own shape.
  - **Inside.** Ticket A proves this for every pinwheel tiling.
  - **At the boundary.** This experiment shows it on the patches tested.

## Limits

- **Finite levels.** Radius 2 at the boundary is shown at levels 4–7, not proved for every level. Inside the patch it is ticket A's
  theorem.
- **Regrowth, not outward growth.** The patch grows by cutting every tile. Adding tiles at the boundary one at a time is a different
  process and was not run here.
- **The map, not the law.** The step from the law's allowed states to the map is the Whitney measurement of
  `PINWHEEL-NATIVE-20261107-001B`.
