# Where growth breaks a native path: interpretation

Experiment `PATH-GROWTH-20261108-001B-E001` (exploratory), run 2026-11-08 under the frozen contract as the long-running unit
`path-growth-b1` (PATH-GROWTH-B1 in `docs/LONG_RUNNING.md`): 407,552,000 paths in 1,071 s on 16 workers, with the machine shared.
Every verdict is exact by the row-sequence reduction, and none was undecided. Totals are in `result.json`, per-shape counts and every
native path in `shapes.json`.

## Control

It passes. The map's 3/5/5/3 shapes give PATH-HYBRID-20261108-001A's 16 native and 13,464 persistent paths, and 3/4/4/3 its 3,728
persistent paths and none native.

## Part 1: the funnel

| Full level | Paths | All three contacts persist | Native |
| --- | --- | --- | --- |
| Four rings of 3 cells | 16,384,000 | 424 | 0 |
| Four rings of 4 cells | 4,096,000 | 4,014 | 0 |
| Four rings of 5 cells | 16,384,000 | 12,916 | 0 |
| Four rings, 3/5/5/3, equal middle positions | 1,024,000 | 3,900 | 8 |
| Five rings, 3/5/5/5/3 | 1,024,000 | 3,396 | 0 |

- **Growth breaks composition, not persistence.** Paths whose three contacts all persist exist at every level, more of them as the
  rings grow. None of them is native except at 3/5/5/3.
- **Their cycles are short.** Of the 24,650 persistent paths, the last contact's row period is 1 in 15,386 and at most 12 in all
  but 536, whose periods are 13 to 100. So the absence of composition is not a matter of long cycles.

## Part 2: the map

Native paths occur at 3 of the 36 combinations of end-ring and middle-ring sizes:

| Shape | Native | Rules (A, B, C, D) |
| --- | --- | --- |
| 3/5/5/3 | 16 | shift, 150, 150, shift (the construction of PATH-HYBRID-20261108-001A) |
| 5/6/6/5 | 48 | 90, then 60 or 102 on each middle ring, then 90 |
| 4/7/7/5 | 16 | 150, 60 or 102, 90, 90 |

- **Each family at one shape.** No family, with its rules, laws and antipodal choices, is native at two shapes of the map.
- **Other shapes have none.** The other 33 combinations, end rings of 3 to 5 cells and middle rings of 4 to 7, have persistent paths
  (3,720 to 16,676 each) and no native one.
- **The new natives.** Their last contact's row period is 6 (4/7/7/5) or 12 (5/6/6/5). Their rules are again affine: rule 90 and the
  one-sided additive rules 60 and 102.

## Reading

- **Nativeness lives at isolated shapes.** Native paths with one rule per ring are not rare because rings fail to remember: they
  remember at every size. They are rare because composition, the last contact needing both ends at every lag, holds only at a few
  shapes, each with its own rules.
- **For A34.** The evidence of ticket A is confirmed and sharpened: binding at every lag is tied to particular sizes.

## Nonclaims

- **These families only.** Linear rules and laws, the declared shapes.
- **Two-time knots only** (A30).
