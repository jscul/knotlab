# Reading the labels from the law: interpretation

Experiment `PINWHEEL-NATIVE-20261107-001B-E001`, exploratory and non-promotable. Run on 2026-11-07, 634 s, as frozen in `contract.json`.

## Readings

**The Whitney step.** The vertex graph of the level-k pinwheel patch, with one vertex joined to every boundary vertex, has vertex
connectivity 3:

| Level | 2 | 3 | 4 | 5 |
| --- | --- | --- | --- | --- |
| Vertices | 26 | 104 | 478 | 2,288 |
| Connectivity | 3 | 3 | 3 | 3 |

**Readability.**
- **What is tested.** Darts of interior distinctions, farther than r + 1 from the patch boundary.
- **The question.** Does the dart's unlabelled rooted neighbourhood of radius r determine its oriented label, that is, its left and
  right tiles' side types and intervals and whether the sides run the same way?

| Level | Darts tested at r = 2 | Distinct codes, r = 1 / 2 / 3 | Conflicting codes, r = 1 / 2 / 3 … 8 |
| --- | --- | --- | --- |
| 5 | 5,162 | 196 / 1,019 / 1,946 | 8 / 0 / 0 … 0 |
| 6 | 40,104 | 198 / 1,158 / 3,288 | 9 / 0 / 0 … 0 |
| 7 | 235,394 | 198 / 1,168 / 3,522 | 9 / 0 / 0 … 0 |

**The least conflict-free radius** is 2, at all three levels.

**Controls at radius 2.** Both conflict, as required.

| Level | Codes | Labels permuted among the tested darts | Side of a vertical line through the patch centre |
| --- | --- | --- | --- |
| 5 | 1,019 | 875 conflict | 491 conflict |
| 6 | 1,158 | 1,157 conflict | 1,102 conflict |
| 7 | 1,168 | 1,168 conflict | 1,168 conflict |

## What this says

- **The law determines its map.** The pinwheel law's graph is 3-connected on every tested patch. By Whitney's theorems, the law's
  allowed states, through the cycle matroid for the tile law or its dual for the corner law, determine the planar map up to a global
  mirror image. The mirror image of a pinwheel patch is again one.
- **The map determines the labels within radius 2.**
  - **Every tested label is determined.** In patches with up to 235,394 tested darts, the unlabelled neighbourhood of radius 2
    determines every distinction's label, and which side of it belongs to which knot. Each knot's side assignment and handedness
    follow.
  - **The test is not vacuous.** Each radius-2 neighbourhood type occurs about 200 times at level 7, and the shuffled and non-local
    labellings conflict on nearly every type.
  - **The set is levelling off.** The number of radius-2 neighbourhood types grows from 1,019 to 1,158 to 1,168 across levels 5–7.
- **Combined with ticket A.** The rule needs no labels from outside: at each step it can read them from the law within radius 2,
  then apply its eleven-label table. On these patches, the pinwheel law grows itself by a local rule that reads only the law.

## Limits

- **Finite patches.** Radius 2 is established on patches to level 7, not proved for every pinwheel tiling. Every radius-2
  neighbourhood occurring anywhere would need to occur by some fixed level; that is plausible, given the levelling-off, but not
  shown.
- **The rotation order.** The code uses the counterclockwise rotation order from the drawing. Whitney's theorem supplies it from the
  law up to the global mirror; that step is cited, not re-derived.
