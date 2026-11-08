# The glue block on the smallest trisum glue

Status: Proved (exhaustive computation on one glue; the row reduction follows from SWITCH-PROOF's theorem and is
cross-checked on 256 direct rows; the colliding pair is checked on its plain spaces)

Ticket `SWITCH-COMPLETE-20261108-001A`, 2026-11-08.

## Question

- **Where it came from.** SWITCH-PROOF proved that creation between glue lines of a plain edge-atom space depends only on the
  switching class of the signing: the glue block is the signed glue's own creation map. Does the glue block tell every switching class
  apart?
- **The test.** The smallest of TRISUM-READ's glues, seed 3, has 8 lines and 8 points, and its incidence graph has cycle rank 9, so its
  signings fall into 512 switching classes. Compute the glue block of every class and compare.

## Dependencies

- **`SWITCH-PROOF-20261108-001A`.** The theorem, and the signed glue's creation map (`proof_lib.signed_row`).
- **`SWITCH-READ-20261108-001A`.** The generator's interface (`sw_lib.generate`).
- **`TRISUM-READ-20261107-001A`.** The glues and the engine; HANDLE-COUNT A's edge atoms (`families.py`).

## Setting

- **Classes.** Fix a spanning tree of the glue's incidence graph. A signing's class is its parity on each of the nine fundamental
  cycles. The class's representative signs exactly the off-tree incidences of odd parity.
- **The glue block of a class.** For glue lines a ≠ b, remove a from the signed glue, glue a far side at b's three points, and record
  the order-free vector (K4^(3), the Fano plane, census 58) or degeneracy. By SWITCH-PROOF this is the glue block of every plain
  edge-atom space whose signing lies in the class.
- **Symmetries.** An automorphism of the incidence graph that keeps lines and points maps classes to classes and permutes the block's
  lines. The glue is self-dual, so automorphisms exchanging lines and points also map signings to signings.

## Results

1. **A row sees only the glue without its line (check 2).** By SWITCH-PROOF's theorem applied to the glue without line a, row a depends
   only on the signing's class there: cycle rank 7, so 128 classes. Each row takes only 55 or 57 values on them. Rows recomputed
   directly from 16 random classes, from their representatives and from randomly switched signings, agree (256 of 256).
2. **The glue block is not a complete invariant (check 4).** The 512 classes give 448 distinct blocks. 395 classes have a block of
   their own; 51 pairs and one triple share a block within the group; one group of 12 shares one block.
3. **It is nearly complete up to symmetry (checks 3 and 4).** The glue has 24 symmetries that keep lines and points, acting faithfully
   on the lines, with 42 orbits on the classes, and the blocks are equivariant. Every collision but one lies inside an orbit: it
   comes from a symmetry of the block, not from blindness. Up to symmetry the blocks take 41 values on the 42 orbits.
4. **One collision across orbits (checks 4 and 5).** The group of 12 is two whole orbits of six, those of the signings
   X = {(4,4), (5,4), (6,6), (6,7), (7,3)} and Y = {(4,5), (5,4), (6,6), (6,7), (7,3)} (incidences as (line, point)). They differ
   by moving one sign along line 4, from point 4 to point 5.
   - **Not a symmetry.** Their signed glues have 40 and 34 solutions, so no symmetry takes one to the other, and none of the 24
     automorphisms exchanging lines and points does either.
   - **On the spaces themselves.** The plain edge-atom spaces of X and Y (43 points each), computed with their own engine, have
     identical blocks of glue lines, equal to the signed glue's. Their solution counts are 5^5 × 40 and 5^5 × 34.
   - **The shared block.** K4^(3) creates at 12 entries; nothing creates at the other 44.
5. **The Pfaffian class is recognized (check 6).** The generator's signing lies in the only class whose signed glue has no solution,
   the class whose plain spaces are three-fold spaces, and no other class has its block.

## Reading

- **What creation sees of the glue.** Each row reads a coarse function of the class on the glue without its line, 55 or 57 values of
  128. Together the rows recover the class up to the glue's symmetries, except for one pair of orbits.
- **Creation does not read the count.** X and Y have the same creation between glue lines but different numbers of solutions, the
  quantity that counting computes. On this glue, native creation between glue lines does not determine the count.
- **Three-fold spaces.** The Pfaffian class, the one whose plain spaces are three-fold, has a block of its own.
- **Doctrine.** Everything here is invariant under relabeling lines and points; the spanning tree only names the classes.

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | The glue and its 512 classes | 8 lines, 8 points, cubic, cycle rank 9 |
| 2 | Rows from the classes of the glue without each line; 256 rows recomputed directly | 1,024 rows; 55 or 57 values each; 256 of 256 agree |
| 3 | Symmetries and equivariance | 48 automorphisms (24 keep lines and points, 24 exchange them); 42 orbits; equivariant |
| 4 | Collisions | 448 blocks; one collision across orbits (X and Y, 40 and 34 solutions); 41 blocks on 42 orbits |
| 5 | The colliding pair on its plain spaces | identical glue blocks; 5^5 × 40 and 5^5 × 34 solutions |
| 6 | The Pfaffian class | the only class without solutions; its block is its own |

## What this does not establish

- **Other glues.** Only the smallest glue is computed here. Ticket B goes one size past.
- **Why X and Y collide.** No mechanism is given.
- **Census 6.** The order-dependent far side is not used here; ticket B checks it.

## Novelty

- **New here.** The computation, and the finding that the glue block separates the classes up to symmetry with one exception.
- **Classical.** Switching classes of signed graphs and the action of automorphisms on them (Zaslavsky).
