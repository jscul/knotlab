# The glue block one size past, on the 10-line trisum glue

Status: Proved (exhaustive computation on one glue; the row reduction as in ticket A, cross-checked on 320 direct rows; a
cross-orbit pair checked on its plain spaces)

Ticket `SWITCH-COMPLETE-20261108-001B`, 2026-11-08.

## Question

- **Where it came from.** On the smallest trisum glue (ticket A), the glue block separates the switching classes up to the glue's
  symmetries except for one pair of orbits. Is that blind pair sporadic, or does blindness grow with the glue?
- **The test.** The next size: TRISUM-READ's two 10-line glues, seeds 6 and 36. Its incidence graph has cycle rank 11, so 2,048
  switching classes. Compute every glue block as in ticket A and classify the collisions.

## Dependencies

- **`SWITCH-COMPLETE-20261108-001A`.** The method: classes as parities on fundamental cycles, rows computed once per class of the glue
  without their line, symmetries and orbits; the smallest glue's colliding pair.
- **`SWITCH-PROOF-20261108-001A`.** The theorem behind the row reduction, and the signed glue's creation map.
- **`TRISUM-READ-20261107-001A`.** The glues and the engine; HANDLE-COUNT A's edge atoms.

## Results

1. **One glue (check 1).** Seeds 6 and 36 give isomorphic glues, so one size past is a single glue: 10 lines, 10 points, cycle rank
   11, 2,048 classes.
2. **The blocks (check 2).** Computed row by row (5,120 rows, 512 classes of the glue without each line); a row takes 119 to 141 values
   on them. 320 rows recomputed directly, from representatives and from randomly switched signings, agree.
3. **Symmetries (check 3).** Four automorphisms keep lines and points; the blocks are equivariant; 576 orbits of classes.
4. **Blindness grows (check 4).** The blocks take 1,526 values on the 2,048 classes and 429 on the 576 orbits. Of the 98 groups of
   classes sharing a block, 92 span several orbits and 76 mix solution counts.
   - **Where nothing creates.** The largest group is exactly the 190 classes at which no far side creates at any entry. They come from
     66 orbits and have from 60 to 110 solutions.
5. **On the plain spaces (check 5).** The first pair of classes from two orbits sharing a block, the signings {(3,1), (6,5)} and
   {(3,1), (4,6), (6,4), (6,5), (7,4)}, has 62 and 60 solutions, and its plain edge-atom spaces, computed with their own engine, have
   identical blocks of glue lines.
6. **Census 6 does not help (check 6).** Adding census 6 under each of the six orders of each gluing line's points separates neither
   that pair nor ticket A's pair on the smallest glue.
7. **The Pfaffian class again (check 7).** The generator's signing lies in the only class without solutions, and no other class has its
   block.

## Reading

- **Native creation sees a signing where it creates.** Where nothing creates, as for 190 classes here, creation between glue lines sees
  nothing, and those classes differ in their counts by almost a factor of two.
- **The smallest glue was a near miss.** Its near-completeness up to symmetry (41 values on 42 orbits) does not persist: one size past
  the blocks take 429 values on 576 orbits.
- **The three-fold class stands out.** At both sizes the Pfaffian class, the one whose plain spaces are three-fold, has a block no
  other class shares.

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | The glue one size past | seeds 6 and 36 isomorphic; 10 lines, cycle rank 11, 2,048 classes |
| 2 | Rows by class of the glue without each line; 320 rows recomputed directly | 5,120 rows; 320 of 320 agree |
| 3 | Symmetries | 4 automorphisms; equivariant; 576 orbits |
| 4 | Collisions | 1,526 blocks; 429 on 576 orbits; 92 of 98 groups span orbits, 76 mix counts; 190 classes where nothing creates |
| 5 | A cross-orbit pair on its plain spaces | identical glue blocks; different counts |
| 6 | Census 6 under every order, both pairs | identical |
| 7 | The Pfaffian class | the only class without solutions; its own block |

## What this does not establish

- **Larger glues.** Only the 10-line glue; the four 12-line glues are not computed.
- **Why nothing creates.** No characterization of the classes where nothing creates is given.

## Novelty

- **New here.** The computation, and the finding that the glue block's blindness grows with the glue while the Pfaffian class stays
  singled out.
- **Classical.** Switching classes of signed graphs and the action of automorphisms on them (Zaslavsky).
