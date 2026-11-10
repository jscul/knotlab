# Boards of laws that name no relation

Status: Partial

Ticket `BOARD-DIST-20261110-001A`, pre-registered 2026-11-10 before the proof attempt and before ticket B's census runs.

## Setting

- **Names.** The reduced words in x, y and their inverses X, Y: the free group F2. Each name u has four neighbour names ux, uX, uy,
  uY.
- **Distinctions.** A value s(u) in a finite alphabet Q for each name, and an identity distinction e(u, v) for each pair of names,
  read "u and v are one place".
- **Board axioms.** Transitivity e(u, v) ∧ e(v, w) → e(u, w); letter closure e(u, v) → e(ug, vg) for each letter g; constancy
  e(u, v) → s(u) = s(v).
- **A law.** Finitely many clause templates, each instantiated at every tuple of base names; every clause names finitely many
  variables. A **value law** has only value literals at one base name and its offsets.
- **Names no relation.** Every identity literal of a template relates the same offset of two base names, e(u_i a, u_j a); a template
  that relates different offsets, such as e(u, uxyXY), names the relation between them. Equivalently, the template's identity
  literals, read as edges labelled by the quotient of their offsets, close no cycle with a nontrivial label.
- **Boards.** The tree (the free group itself, no two names one place), the collapse (all names one place), lines, the plane
  (the commutator subgroup), finite boards.

## Targets

1. **Boards are Schreier graphs.** The board states are exactly the right congruences of F2, so the subgroups H with places the
   cosets Hu and the Schreier graph of H. On the ball B_L the board states of the truncated CNF are exactly the restrictions of right
   congruences (classical: Schreier; Stallings 1983).
2. **Refinement.** If no clause has a positive identity literal besides the board axioms, refining the board of an allowed state
   keeps it allowed. So the tree is allowed whenever any state is, and the allowed boards are closed under covering.
3. **Unfolding.** If a law names no relation and some allowed state has an infinite board, then some allowed state has the tree
   as its board. So no such law forces an infinite board; it can force only finite ones.
4. **Finite boards can be forced.** Every finite board is the only board of some law that names no relation.
5. **Every change of board is infinite.** Two different boards differ in infinitely many identity distinctions, and every place of
   a board other than the tree holds infinitely many names. So no distinction of an allowed state whose board is not the tree is
   flipped by a change of finitely many variables: under the source-aware reading, a knot can be native only at a state on the
   tree.
6. **The collapse.** For a value law, the collapse is allowed iff some constant colouring is allowed iff every board is allowed.
7. **Identity of indiscernibles.** The rule "two names whose radius-r views agree are one place" names no relation and makes every
   allowed board finite, with at most q^|B_r| places. At radius 1 with one bit, the allowed boards are exactly the balanced view sets
   (a set of distinct allowed views with letter-compatible permutations), and every law with a plane-like abelian board also has a
   non-abelian one.
8. **One named relation suffices.** The commutator rule e(u, u x y X Y) at every name, with an aperiodic Wang-tile value law, forces
   exactly the plane.

## Plan

Targets 1, 2, 5 and 6 by direct argument. Target 3 by compactness: on an infinite board only finitely many places carry a view type
that occurs at finitely many places, far from them every clause instance is realized on distinct places with the same types, and
the colourings that satisfy every instance with distinct names for distinct places form a nonempty compact set. Target 4 by a
Cayley-type value law with |Γ| values and identity of indiscernibles at radius 0. Target 7 by counting views and a swap of two
targets in one compatibility class. Target 8 from the existence of aperiodic tile sets (Berger 1966; Jeandel and Rao 2015).

## What would count against

A law of ticket B's census on which an allowed board has a cover that is not allowed (target 2), the collapse allowed without every
listed board (target 6), or a plane-like abelian board at radius 1 without a non-abelian one (target 7); for target 3, a law that
names no relation with an allowed infinite board and no allowed state on the tree.
