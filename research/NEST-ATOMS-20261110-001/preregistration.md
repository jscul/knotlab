# Pre-registration: atoms within atoms

Epic `NEST-ATOMS-20261110-001` (backlog B104, G15), written on 2026-11-10 before any run, at the coordinator's go-ahead.

## The question

`OTHER-ATOMS-20261110-001` proved that a torus atom stands for its replaced line exactly where its torus has no satisfying state, when
the torus is free at the removed point. Its lemma 2 does not use the genus. So a **composite atom**, a knot sphere that already carries
atoms, less a point, should be an atom of the next level: it should stand for its line exactly where its own closed space has no
satisfying state, which is where every atom inside it acts. Then a group of atoms behind a three-edge cut reads, from outside, as the AND
of its atoms' bits, and named patterns of patterns (sub-goal B54) would have a rule.

## Objects, named before any run

- **Leaves:** the torus atoms of `OTHER-ATOMS-20261110-001`, here the Fano atom (7,2,1) and the thin-torus atom (2,1,2).
- **Composite C(k, leaf):** the knot sphere K_k with two leaves of one type grown in turn (first compatible bijection, chirality 0, first
  completion with no even face, the leaf's torus law) at l0, the first line-orbit representative, and at the first line at the largest
  distance from l0; then less one point P. The **removed point** P ranges over every point of the closed composite in ticket A; elsewhere
  it is the first point of the sphere part (lowest index) not on either replaced line.
- **Three-leaf composite:** K_3 with three Fano leaves at l0 and the first lines at distances 2 and 3 (ticket A only).
- **Depth two D(leaf):** K_2 carrying a composite C(2, leaf) with one leaf only (at its l0) grown at K_2's l0, and one leaf at the first line
  at the largest distance; then less the standard point.
- **Outer host:** K_2 with its Kasteleyn law. Composites are grown at L0, its first line-orbit representative, and, for two composites, at
  L1, the first line at the largest distance from L0.

The **role** of a leaf or composite is read by SAT on its three outer points in each class (six patterns: it acts as its line; eight:
transparent). Classes are reached by flat changes on each leaf's own sides, so a space with G leaves has 4^G classes.

## The claim to prove (ticket A, by hand) and its frozen expectation

**N1.** Let a knot sphere H with a Kasteleyn law carry atoms that each act as their line in exactly one class and are transparent in the
others (any class-forced free torus atoms, or composites satisfying N1 themselves), and suppose H has, at each of its lines, a state
violating only that line. Then H less a point P of its sphere part that lies on no replaced line is free at P in every class, and its
closed space is unsatisfiable exactly where every atom inside acts. So the composite acts as its line exactly where all its atoms act and is
transparent otherwise, on any host; by induction this holds at every depth. The units: a composite of genus g has at least g − 1 units of
the floor dissonance in its region in every state satisfying its lines, and at least g where it acts.

The check (ticket A) reads every composite named above at **every** removed point P, in every class, grown at the outer host's L0.

- **Expected (N1):** at every P of the sphere part off the replaced lines, the composite acts exactly in the classes where all its leaves
  act, and its relation then equals the replaced line's six patterns; it is transparent in every other class. The hypothesis about states
  violating one line is checked on every line of each sphere used.
- **N2 (a weaker prediction, not covered by the proof):** the same holds at every other P, on a replaced line or inside a leaf.
- **Failure:** any P off the replaced lines where the composite's role differs from the AND of its leaves (the proof or the code is then
  wrong). A P on a replaced line or inside a leaf where the role differs is a finding about N2, recorded as found.

## Ticket B: units at every level (exact, SAT over every state)

Spaces, for each leaf type: (a) the outer host with one composite C(2, leaf) at L0 (genus 2, 16 classes); (b) with two composites at L0
and L1 (genus 4, 256 classes); (c) with the depth-two composite D(leaf) at L0 (genus 2, 16 classes). In every class:

- each group's role (leaf, composite, nested composite), and whether every composite's role is the AND of its leaves;
- **R-a:** if every top-level group acts, no state satisfies every line;
- **R-b':** in every state satisfying every line, each group of genus g holds at least g − 1 + [it acts] units in its region (faces at its
  triangles), by SAT with a cardinality bound.

**Code control:** the new code on K_3 with two Fano leaves at l0 and distance 3 reproduces `OTHER-ATOMS-20261110-001B`'s tally there.
**Expected:** every check holds. **Failure:** a class breaking R-a, R-b' or the AND.

## Ticket C: a two-level address (computed)

On space (b) for each leaf type (leaves 0 and 1 in the composite at L0, 2 and 3 in the one at L1; floor 3 units), the frozen targeted
search of `ADDRESS-SEQ-20261110-001A` (unchanged; roles by SAT) writes the acting leaf sets A1 = {0, 1, 2}, A2 = {0, 2, 3}, A4 = {0, 1, 3},
A3 = {1, 2, 3}, A1, A2 in turn, so that the composite that acts alternates. It starts in the class where every leaf is transparent, at
the first satisfying state the SAT solver returns. After each write one random point of the outer host is flipped and the learner M1
runs to the floor (random.Random(104)). An address is **held** when the acting leaves after the return equal the written ones, and the
**outer address** is held when the acting composites do.

- **Expected:** every write reached; at least 95% of addresses held, and every outer address held whenever its address is.
- **Failure:** a write not reached within the search's cap, or fewer than 80% held.

## What it would mean

If N1 holds, the atom rule is closed under grouping: any group of atoms behind a three-edge cut is itself an atom of the next level, and
a host reads it as one bit, the AND of the bits inside. Assumptions in force: A20, A21, A46, A47, A49, A50, A52. Each check is expected to
take under ten minutes; one expected to take longer is registered in `docs/LONG_RUNNING.md` before it is launched.
