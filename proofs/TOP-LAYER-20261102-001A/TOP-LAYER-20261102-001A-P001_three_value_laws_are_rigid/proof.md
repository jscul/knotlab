# Every law on three values that composes like cycles is rigid

Status: Proved

Ticket `TOP-LAYER-20261102-001A`, 2026-11-02.

## Question

- **The test the owner asked for first.** BEYOND-TWO B showed that every Mal'tsev law on three values composes like cycles. The 1020
  non-simple ones are the natural place for a layered top.
- **What is asked here.** Do they ever keep a knot inside a globally failing space?

## Dependencies

- **`BEYOND-TWO-20261101-001B`.** The enumeration of Mal'tsev operations on three values.
- **`MUTUAL-SELECTION-20261031-001C`.** The census of cubic incidence graphs, read both ways (73 substrates).

## Setting

- **Systems and terms.** As in RIGID-SELECTION A: one knot per line of a connected k-regular k-uniform substrate. Global failure and
  rigidity mean the same as there.
- **Knots.** Knots are range-relative: constrained as a whole, every proper subset unconstrained relative to the ranges.
- **Pull-back.** A knot is pulled back from a two-element section when it has the form {x : Σ h_i(x_i) = c (mod 2)}. Here each h_i is
  a homomorphism from a subuniverse R_i (the range) onto the two-element affine algebra.

## What is checked

1. **The operations.** 531441 Mal'tsev operations on {0, 1, 2}. 1020 have exactly one nontrivial congruence and none has two; up to
   relabelling they form 185 classes.
2. **Three-place knots, exhaustively.**
   - **The enumeration.** For each class every subuniverse of A^3 is enumerated (a closure lattice), and its knots are picked out.
   - **The result.** There are 452 knots, in 57 classes. They coincide exactly with the pull-backs from two-element sections. No class
     has a three-element abelian section.
3. **Cubic substrates.** 16644 random systems of three-place knots on the 73 cubic substrates. One fails globally, and it is rigid.
4. **4-regular substrates.** 1710 random systems of four-place knots (pull-backs from two-element sections) on random 4-regular
   substrates with 5 to 8 points. 320 fail globally, and all are rigid.
5. **Simple laws.** Z3 and 300 sampled classes of the simple three-value laws.
   - **Knots.** Pulled back from two- or three-element sections, again coinciding exactly with the enumeration.
   - **Global failures.** 3 on cubic substrates and 119 on 4-regular ones, all rigid.

## Why

- **One bit per variable.** Every abelian section of a three-element algebra has two or three elements, so it is a field with one
  layer. So every knot reads one bit (or one digit mod 3) from each of its variables, and a system of knots is a linear system over a
  field, one coordinate per variable.
- **Hence rigid.** Over a field, a square system that fails globally leaves one line after any removal, so only ties remain.
- **In general.** Ticket C proves this for every Mal'tsev law whose abelian sections all have one layer.

## Correction during the ticket

- **The first version of check 3** expected no global failure on cubic substrates: each line is one parity and every point lies on
  three lines, an odd number.
- **That is wrong.** A variable can be confined by one line to a two-element block, inside a single top class. A line that reads its
  top bit then sees a constant, and that line's parity is shorter.
- **The fix.** One such global failure appeared, and it is rigid. The check now tests rigidity instead of expecting none.

## What this does not establish

- **Four-place knots** are generated as pull-backs (the form ticket C proves), not enumerated exhaustively.
- **The simple laws** are sampled: 300 of about 88000 classes.
- **Substrates** are the cubic census and random 4-regular ones with at most 8 points.

## Novelty

- **New here.** The exhaustive three-place enumeration. The statement is an elementary consequence of ticket C.
