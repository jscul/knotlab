# Families of paths native at every size: interpretation

Experiment `PATH-GROWTH-20261108-001A-E001` (exploratory), run 2026-11-08 under the frozen contract as the unit `path-growth-a1`:
38,912,000 paths at the full levels in 84 s on 16 workers. Every verdict is exact by the row-sequence reduction, and no row sequence
was undecided. Totals are in `result.json`, and the followed families in `families.json`.

## Control

It passes. The full levels have 8 native paths, and all 8 agree on their full state spaces. Before freezing, `growth_lib.native`
agreed with `path_lib.analyze` on 3,000 random paths and on the 16 known native paths.

## Primary observable

| Full level | Paths | Native |
| --- | --- | --- |
| Four rings of 3 cells, middle contacts antipodal (index 1 or 2) | 16,384,000 | 0 |
| Four rings of 4 cells, middle contacts antipodal (index 2) | 4,096,000 | 0 |
| Four rings of 5 cells, middle contacts antipodal or two apart (index 2 or 3) | 16,384,000 | 0 |
| Four rings: end rings of 3 cells, middle rings of 5, each middle contact at the same index | 1,024,000 | 8 |
| Five rings: the same, one more middle ring | 1,024,000 | 0 |

- **H1 fails.** No family is native at every size of its schedule.
- **Equal rings give no native path.** With all four rings of one size, 3, 4 or 5 cells, none of the 36,864,000 paths is native, with
  any linear rules and laws. So the antipodal and two-apart schedules have no family to follow.
- **Longer paths.** The 8 families native at four rings are ticket A's construction of `PATH-HYBRID-20261108-001`: shift end rings,
  rule-150 middle rings, with both middle contacts at the same index. None is native at five rings, and no other family is native at
  five rings either.

## Reading against the decision rule

- **Binding at every lag is tied to particular sizes.** In these families a native path occurs at one shape only, 3/5/5/3, and does
  not survive growing its rings together or adding a ring. Every path with four equal rings fails. This is the evidence the decision
  rule names, and it puts A34 under challenge.
- **What the absence does not say.** The families fix one linear rule per ring and the shapes listed. Unequal shapes, hybrid rings
  and nonlinear rules are not covered; ticket B maps the unequal shapes near 3/5/5/3.

## Nonclaims

- **These families only.**
- **Two-time knots only** (A30); linear rules and laws only.
