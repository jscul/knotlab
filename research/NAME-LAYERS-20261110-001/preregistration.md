# Pre-registration: layers through a naming knot

Epic `NAME-LAYERS-20261110-001` (direction `NEST-ATOMS-20261110-001`#4, first raised as `RESIGN-STEER-20261107-001`#3; G15), written on
2026-11-10 before any run, at the coordinator's go-ahead. Exploratory: if the first frozen test gives no foothold, the epic stops and reports.

## The question

The program has two candidate channels between levels of a learned network. A **parity name** (sub-goal B54, `GEOMETRY-LAW-20261029-001`):
an upper-level variable y named by two lower-level variables through the three-place parity knot y ⊕ a ⊕ b = 0. A **three-edge cut**
(`NEST-ATOMS-20261110-001`): a lower-level closed knot space, less a point, spliced into an upper-level line. Are these one reading of
layers or two, and can a point (a dissonance) cross levels through each?

## The two channels, exactly

Let T be a closed knot space with a law in class c, and let ℓ be a line of an upper-level space with three points q_0, q_1, q_2.
- **Cut channel.** T less a point P is spliced in place of ℓ (compatible splice, completion with no even face). It offers the upper level
  the relation R_C(c) on (q_0, q_1, q_2): the patterns that some assignment of T's other points completes on T's lines.
- **Name channel.** T keeps all its lines and three disjoint pairs of its points (a_k, b_k) are named: q_k = a_k ⊕ b_k, by three parity
  naming knots. It offers the relation R_N(c) on (q_0, q_1, q_2): the name patterns of T's satisfying states.

Both are relations that a lower level offers an upper level at the place of one line, so they can be compared class by class.

## What separates one reading from two

**One reading** if, for some naming of every T below, R_N(c) and R_C(c) have the same size in every class c (six where T has no satisfying
state, eight elsewhere): the name then carries what the cut carries. **Two readings** otherwise. The observation that decides it is the
unsatisfiable class: there the cut offers the replaced line (six patterns), so the lower level's contradiction becomes an upper-level
constraint, while the name channel offers nothing at all, since T has no satisfying state.

**Claim D (by hand), frozen as a prediction.** For every T with an unsatisfiable class and any naming, R_N = ∅ there while R_C is a line:
two readings. A point crosses levels through a cut (lower-level learning creates or removes the upper level's forced dissonance,
`NEST-ATOMS-20261110-001`) but not through a name: T's own lines stay unsatisfiable whatever the upper level does, so the dissonance stays
below, and the upper level's own forced dissonance stays above.

## The census (computed, exhaustive per class)

T, frozen: the class-forced lattice tori Fano (7,2,1), thin (2,1,2), (3,2,2) and (4,3,2) (4 classes each); the closed composites C(2, Fano)
and C(2, thin) of `NEST-ATOMS-20261110-001` (16 classes each); the knot sphere K_2 (one class); and the all-satisfiable torus (2,0,2) as a
control. Two namings per T, frozen: **line pairs** (lines in index order, each line whose points are all unused gives the pair of its first
two points, until three pairs) and **far pairs** (repeatedly the smallest unused point and the smallest unused point not sharing a line
with it). In every class: R_C by splicing T less a point into K_2 at its L0 (for a composite its standard point of
`NEST-ATOMS-20261110-001`, otherwise T's first point) and reading the ports by SAT; R_N by SAT on T's lines with the three naming knots.

- **N1.** R_N = ∅ exactly in the unsatisfiable classes (claim D).
- **N2 (predicted).** In every satisfiable class R_N has all eight patterns for both namings: names of these spaces carry no correlation.
- **Failure line.** A nonempty R_N in an unsatisfiable class (the claim or the code is wrong).

## Stop rule (one epic)

If D and N1 hold, the answer is two readings, with the separating observation above; the epic records what names do carry (N2's result)
and stops. Other namings, other spaces and learning dynamics across names are recorded, not run.

Assumptions in force: A20, A21, A46, A47, A49, A50, A52. Each check is expected to take under ten minutes.
