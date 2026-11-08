# Composition at recurring lags across sizes (E002): interpretation

Experiment `RECUR-PATH-20261108-001A-E002` (exploratory), run 2026-11-08 under E001's contract with one amendment, the every-lag
check fixed: 21,504,000 paths at the full levels and 272,582 followed families in 170 s on 16 workers. Every verdict is exact by the
row-sequence reduction, and none was undecided.

## Control

It passes. The every-lag counts reproduce `PATH-GROWTH-20261108-001A` (0 at three and four cells, 8 in the longer schedule at four
rings), and ten small paths meeting a recurring reading agree on their full state spaces.

## Primary observable

| Full level | Paths | Every lag | Recurring, persistent | Recurring, binding there |
| --- | --- | --- | --- | --- |
| Four rings of 3 cells | 16,384,000 | 0 | 200 | 37,352 |
| Four rings of 4 cells | 4,096,000 | 0 | 144 | 13,928 |
| Four rings, longer schedule | 1,024,000 | 8 | 636 | 12,382 |

| Schedule (sizes) | Families followed | Every lag at every size | Recurring, persistent at every size | Recurring, binding there at every size |
| --- | --- | --- | --- | --- |
| Antipodal (3 to 9 cells) | 37,352 | 0 | 0 | 748 |
| Two apart (4 to 9 cells) | 222,848 | 0 | 256 | 16,384 |
| Longer (4 to 9 rings) | 12,382 | 0 | 196 | 1,016 |

## Reading against the pre-registered rule

- **A34 is overturned.** 452 families compose at recurring lags with every contact persistent at every size of their schedule,
  while no family composes at every lag at two sizes. The pre-registered rule then replaces A34 by the recurring reading.
- **The families.** With contacts two apart, every ring runs rule 60 or 102. In the longer schedule the end rings are frozen (204)
  or run rule 90 and the middle rings run 90, 60 or 102. The independent verification is in
  `research/RECUR-PATH-20261108-001/verify_recurring.json`.

## Nonclaims

- **These families and schedules only;** sizes to 9 cells and 9 rings.
- **Two-time knots only** (A30); linear rules and laws only.
