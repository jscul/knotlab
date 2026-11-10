# Cut and name, class by class

Status: Claim D proved by hand; the census computed exhaustively per class. `check.py` (1 second), as frozen in
`research/NAME-LAYERS-20261110-001/preregistration.md` (commit `6901b52a8`). The pattern lists quoted under "What names carry" were read
after the run.

## Claim D (by hand)

Let T be a closed knot space with a Kasteleyn law, in a class c with no satisfying state.
- **Through a cut** T less a point (free there) offers the replaced line's six patterns (lemma 2 of `OTHER-ATOMS-20261110-001A`), so the
  upper level gains exactly the constraint the line imposed: the lower contradiction becomes an upper constraint, and lower-level learning
  that changes c creates or removes the upper level's forced dissonance (`NEST-ATOMS-20261110-001`).
- **Through a name** T keeps its own lines, which no state satisfies, so R_N = ∅ whatever is named: the whole two-level system has no
  satisfying state, the dissonance stays among T's lines whatever the upper level does, and the upper level's own forced dissonance (a
  sphere's, by the count) stays among its lines whatever the lower level does. A point cannot cross a name. ∎

So the two channels differ in the unsatisfiable class of every class-forced T: two readings of layers.

## The census (computed)

| Space T | Classes | R_C (unsatisfiable / satisfiable classes) | R_N, line pairs | R_N, far pairs |
| --- | --- | --- | --- | --- |
| Fano torus (7,2,1) | 4 | 6 / 8 | undefined | undefined |
| thin (2,1,2) | 4 | 6 / 8 | undefined | undefined |
| thin (3,2,2) | 4 | 6 / 8 | undefined | 0 / 5, 2, 8 |
| thin (4,3,2) | 4 | 6 / 8 | 0 / 8, 2, 8 | 0 / 7, 1, 8 |
| all-satisfiable (2,0,2) | 4 | — / 8 | undefined | undefined |
| K_2 | 1 | 6 / — | 0 | 0 |
| C(2, Fano) | 16 | 6 / 8 | 0 / 5 (3), 8 (12) | 0 / 6 (3), 2 (3), 7 (9) |
| C(2, thin) | 16 | 6 / 8 | as C(2, Fano) | as C(2, Fano) |

"Undefined": the frozen naming rule did not find three disjoint pairs (the space has too few points, or every point shares a line with
the next free one); no substitute was chosen.

- **D held:** R_C is the line in every unsatisfiable class.
- **N1 held:** R_N is empty exactly in the unsatisfiable classes, wherever a naming was defined.
- **N2 failed:** in satisfiable classes the names carry correlations, and which ones depends on the class: R_N has 1, 2, 5, 6 or 7 patterns
  in 41 of the 69 satisfiable class readings.

## What names carry (post hoc)

The relations seen include a single pattern (the names frozen, on thin (4,3,2)), a complementary pair, five- and six-pattern relations that
are not closed under complement, and seven patterns, one excluded: a single three-literal clause on the names. A cut never offers such a
relation, since every relation a knot gadget offers is closed under complementing all points. So the name channel carries state
correlations that change with the lower level's class, including clauses, which no cut can carry; and the cut carries contradictions,
which no name can.
