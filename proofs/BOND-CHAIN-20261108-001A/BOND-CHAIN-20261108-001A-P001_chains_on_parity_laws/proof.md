# Chains of knots on parity laws

Status: Proved. The proof is by hand from a classical fact about matroids; `check.py` confirms both statements on finite windows of
the parity laws measured since 2026-11-07.

Ticket `BOND-CHAIN-20261108-001A`, 2026-11-08.

## Standard statement

- **The measures.** For two distinctions x and y of a law:
  - *bond distance* (A12): the size of the least knot containing both, minus one;
  - *chain distance counted in knots*: the fewest knots in a chain K1, ..., Km with x in K1, y in Km, and each Ki sharing a
    distinction with K(i+1);
  - *chain distance counted in distinctions*: the fewest distinctions in the union of such a chain, minus one.
- **Theorem.** On a consistent parity law, let x and y be joined by a chain of knots and not be parallel (not forced equal). Then
  some knot inside the chain's union contains both. So chain distance counted in knots is 1 for every such pair, and counted in
  distinctions it equals bond distance.

## Nearest known result

The theorem is a direct use of a classical fact: in a matroid, "x = y or some circuit contains x and y" is an equivalence
relation, whose classes are the connected components (Whitney 1935; Oxley, *Matroid Theory*, Proposition 4.1.2). No overlap with
the program's measure was found (known-with-delta).

## Terms

- **Knots of a parity law.** Write each distinction's column: its values in a basis of the allowed states. A set S of at least
  three distinctions is a knot (K1–K3) exactly when its columns sum to zero and have rank |S| − 1 (`LOGIC-AXIS-20261107-001A`). So
  the knots are the circuits of size at least three of the binary matroid M of the columns; a circuit of size two is a pair of
  parallel distinctions (x = y forced, or x = y + 1 for an affine law), a two-place tie and not a knot.

## Lemma 1 (a chain's union holds a knot through its ends)

If C1, ..., Cm are circuits of a matroid with Ci ∩ C(i+1) nonempty, x ∈ C1 and y ∈ Cm, then some circuit inside C1 ∪ ... ∪ Cm
contains x and y.

*Proof.* Let U be the union. Each Ci is a circuit of the restriction M|U, and all elements of one circuit lie in one connected
component. Consecutive circuits share an element and components are classes of an equivalence relation, so x and y lie in one
component of M|U, hence on a common circuit of M|U, which is a circuit of M inside U. ∎

## Theorem 2

On a consistent parity law, if x and y are joined by a chain of knots and are not parallel, a knot inside the chain's union
contains both. Hence chain distance counted in knots is 1, and counted in distinctions it is bond distance.

*Proof.* By Lemma 1 a circuit C inside the union contains x and y. It is not {x, y}, since they are not parallel, so it has at
least three elements and is a knot. Any chain's union therefore has at least bond(x, y) + 1 distinctions, and the least knot
through x and y is itself a chain of one knot. ∎

For an infinite parity law the same holds: knots are finite and the argument stays inside a finite union.

## What it says

- **On parity laws chains add nothing.** Counted in knots they see no spacing at all: everything joined is one step apart.
  Counted in distinctions they give back bond distance exactly. So every result measured with bond distance on a parity law (the
  gauge and Tseitin lattices, Ledrappier's axis, the pinwheel's parity laws) reads the same with this chain measure.
- **Where they could differ.** Only where knots are not the circuits of a matroid, so outside parity laws (ticket B).

## The check

`check.py` (with `LOGIC-AXIS-20261107-001A`'s axis_lib) tests on the gauge law on 4 × 4 and 3 × 5 boxes, Tseitin's law on 3 × 4
and 2 × 2 × 2 boxes and Ledrappier's triangle of side 5:
- the union lemma on every pair of meeting knots of at most six distinctions, for every x in the first only and y in the second
  only (over 6 million cases on Ledrappier's triangle alone): no failure;
- every pair of non-parallel distinctions joined by a chain of knots lies on a common knot: no exception.

Control: on two single clauses not(s0 ∧ a1 ∧ s1) and not(s1 ∧ a2 ∧ s2), which share s1 and are not a parity law, the same test by
brute force finds exactly the two clauses as knots, none through s0 and s2.

## Nonclaims

- **Not about other laws.** Outside parity laws the knots need not be a matroid's circuits, and the control shows the lemma can
  fail there.
- **Not a choice between measures by itself.** The theorem says when the measures agree; which one is native is read in the
  decision note.
