# Hybrid second middle rings: interpretation

Experiment `PATH-HYBRID-20261108-001B-E001` (exploratory), run 2026-11-08 under the frozen contract: 3,175,200 paths in 201 s on
16 workers. Every verdict is exact by the row-sequence reduction, which covers hybrid rings since every cell is linear. Paths whose
three contacts all persist are in `paths.json`, and the totals are in `result.json`.

## Control

It passes. The ten smallest native paths give the same verdicts on their full state spaces.

## Primary observable

| Paths | Count |
| --- | --- |
| In the family | 3,175,200 |
| All three contacts persist | 18,592 |
| Native: the last contact binds the end rings at every lag from the light cone on | 1,120 |
| … and the last contact binds all four rings | 1,120 |

- **H1 holds.** Hybrid second middle rings give native paths across time: the first composed topology of three contacts found.
- **The smallest.** Rule 102 on ring A (3 cells), 60 on ring B (5 cells), a hybrid ring C of 5 cells whose non-contact cells run 60,
  102 and 60, and rule 204 on ring D (3 cells), the contacts two apart on both middle rings. The last contact needs all four rings'
  first rows at every lag from the light-cone lag 5 on.
- **Kinds of cells in the hybrid rings of native paths.**
  - additive, buffer and shift: 480;
  - additive and shift: 320;
  - only additive, but different additive rules: 256;
  - buffer and shift: 64.
- **Where they sit.** Every native ring C has 5 cells. The commonest patterns, from c2 round to c2, are:
  - c2, 60, c3, buffer, shift;
  - c2, 60, c3, 102, 60;
  - c2, shift, buffer, c3, 102;
  - c2, 102, 60, c3, 102 (128 each).

  In each, the cells between c2 and c3 on one side carry c2's past toward c3. A rule-60 cell reads its left neighbour and a shift
  copies it.
- **Laws.** c2 always reads both of its ring-C neighbours, and c3 mostly does.
- **End ring D.** Rule 204 in 768 of the 1,120, 90 or 150 in 160 each, 60 in 32. So the end ring need not be frozen.

## Reading against the decision rule

- **Hybridness removes the tension.** NATIVE-PATH's diagnosis was that a second middle ring must keep its own first row and carry the
  first ring's influence. A ring whose cells differ can do both: some cells carry c2's past to c3, others keep the ring's own state
  in both contacts' supports. Rings with only additive cells also work, if their additive rules differ from cell to cell.
- **A caveat for the program.** These rings are inhomogeneous: each cell has its own rule, a wider substrate than one law per ring.
  Whether such a substrate is native, or a law drawn cell by cell, is a reading to record, not a fact. The broad sweep of ticket A
  tests uniform rings, one rule each, at small sizes.
- **Addendum, after ticket A.** The broad sweep found 16 native paths with uniform rings, all with shift end rings and rule-150
  middle rings (ticket A's interpretation).

## Nonclaims

- **This family only.** No claim about other paths.
- **Two-time knots only** (A30).
