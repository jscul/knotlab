# Pre-registration: negation inside a cut leaf

Epic `NOT-INSIDE-20261110-001` (backlog B123, G15), written on 2026-11-10 before any run, at the coordinator's go-ahead, as the deciding
epic for the gates question: it ends with an explicit NOT, or a proof that the readings are monotone, with the proof's exact scope.

## The question

`GATES-20261110-001` proved that a cut leaf read only from outside is never negated (lemma C), so a negation of a stored acting bit needs
names that read inside a cut leaf. Is there one?

## A distinction, stated before any run

A leaf's law is a signing; its stored class is that signing up to gauge (flipping a point together with its sides, or complementing a
line). Learning writes signings, and which signing of a class it leaves depends on the path it took. Names read states, and a gauge flip
of a named point changes what the name reads. So a reading can be:
- **class-level:** the same for every signing of each leaf's class (a function of the stored classes alone); or
- **frame-level:** computed with one fixed signing per class (the leaf's torus's labelled class laws, as in `GATES-20261110-001` and
  `CLASS-READ-20261110-001`).

## Claim M (to prove by hand), frozen

For any network (components with knot laws, any parity names, any further constraints that do not involve a leaf's own signs), a
class-level reading is non-decreasing in each leaf's acting bit and takes the same value on all of a leaf's non-acting classes. Planned
proof: if the network has a satisfying state with a leaf in class c, and the leaf in class c′ allows on its outer points every pattern it
allows in c, then some signing of c′ admits the same state, by a gauge on the leaf's inner points. So no class-level reading negates a
stored bit, and none tells two non-acting classes apart.

## The census (computed, exact)

- **N (the frame-level NOT).** Leaves: thin tori (3,2,2) and (4,3,2), and the Fano atom (7,2,1); host: the torus (2,0,2) in its first
  class with the leaf cut in at its first line (as in `GATES-20261110-001`'s F4′); one fixed signing per leaf class. Let S_c be the
  component's satisfying states with the leaf in class c. Some network (names and constraints on the component's points) reads NOT a_1 in
  this frame exactly when S_ω is not contained in the union of the S_c over the non-acting classes. Computed by enumerating all states. For
  a leaf where it holds, an explicit network is built (names on a spanning set of the points, parity knots pinning each name to a witness
  state) and its reading checked by SAT, together with a second signing of one non-acting class under which it reads 0 (as claim M says).
- **F (frame dependence of the σ readings).** For each of the 718 networks of `CLASS-READ-20261110-001`'s G1 that read {ω, σ}: is there a
  signing of σ (σ's labelled law with a set of points flipped) under which the network has a satisfying state?

## Predictions

- **M** proved.
- **N:** a frame-level NOT exists for at least one of the three leaves.
- **F:** every one of the 718 networks has such a signing, so the σ reading reads the frame, not the class; then the wording of
  `CLASS-READ-20261110-001` (and the post hoc parity remark of `GATES-20261110-001`) is corrected.
- **Failure line.** A network whose reading is the same for every signing and negates an acting bit, or a σ network that reads σ under every
  signing of σ: either would contradict M (a proof or code error).

## Stop rule (one epic)

The gates question closes here: with M proved, class-level readings are monotone; the frame-level readings are recorded for what they are.

Assumptions in force: A20, A21, A46, A47, A49, A50, A52. Each check is expected to take under ten minutes.
