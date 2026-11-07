# Pair refinement determines the atoms

Status: Proved (exact computation on the 191 saved and 86 fresh creation maps, through the order-free far sides)

Ticket `REFINE-READ-20261107-001A`, 2026-11-07.

## Question

- **The approved test.** GENUS-READ recommended running colour refinement on the native creation map and asking whether it ever merges
  lines of two different atoms.
- **Why that test is the wrong one.** A canonical procedure cannot separate lines that a symmetry of the space exchanges. In a symmetric
  space two atoms can be mirror images.
- **The decisive question.** Does every symmetry of the native creation map map atoms to atoms? If one does not, no
  representation-free rule can recover the atoms. If all do, the atoms are fixed by the map, even where single lines cannot be told
  apart.

## Dependencies

- **`GENUS-READ-20261107-001C`** (and A). The order-free far sides, K4^(3), the Fano plane and census 58, and the saved and fresh maps
  read through them (`native_glue_lib.py`).

## Setting

- **The native creation map of a space.**
  - **Its vertices** are its lines.
  - **Its edge colours.** Each ordered pair (a, b) carries the order-free vector of removing a and gluing at b. Where b shows fewer than
    six patterns it is degenerate.
  - **Why it is native.** By GENUS-READ A nothing in it depends on how a line's points are listed.
- **Colour refinement (1-WL).** Lines are recoloured by the multisets of (edge colour, colour) of their out- and in-neighbours, until
  stable.
- **Pair refinement (folklore 2-WL).**
  - **The start.** Ordered pairs begin from their atomic type, the vectors in both directions, with the diagonal apart.
  - **The step.** A pair (a, b) is recoloured by the multiset over c of the colours of (a, c) and (c, b), until stable.
  - **What it means.** Stable pair colours are the types of pairs in three-variable counting logic, C^3 (Cai, Fürer and Immerman). Every
    automorphism of the map preserves them.

## Results

1. **Colour refinement merges atoms where symmetry forces it (check 1).**
   - **How often.** It puts lines of two different atoms in one class in 87 of 277 spaces, 14 of the 23 Fano trees among them.
   - **Why this is not an obstruction.** In a symmetric Fano tree two mirror-image atoms must share colours. Yet the yes/no twin rule reads
     every Fano tree (CHAIN-TRANSFER C).
2. **Pair refinement separates within from across (check 2).**
   - **In all 277 spaces**, no stable pair class holds both a pair of lines of one atom and a pair of lines of two atoms.
   - **So the same-atom relation is a union of stable pair classes.** Hence:
     - every automorphism of the native creation map maps atoms to atoms;
     - in each space, "same atom" is definable in C^3, by a disjunction of the formulas that define its pair classes.
3. **The control: yes/no creation alone does not suffice (check 3).**
   - **On the bare relation.** Using only whether creation occurs, pair refinement mixes within and across in 42 spaces.
   - **That includes all 39 obstructed spaces**, those where lines of two atoms are yes/no twins: their transposition is a symmetry
     (GLUE-READ C).
   - **So the far sides are what remove the obstruction**, and they are the order-free ones.

## Reading

- **No space hides its handles from native creation.**
  - **Existence.** In every computed space, the native creation map fixes the partition of lines into Fano atoms. Every symmetry of the
    map respects it, so the genus is determined natively.
  - **What is not yet shown.** That one uniform rule computes it: each space may need its own C^3 definition (ticket B).
- **What the far sides add, precisely.**
  - **Without them** (yes/no), symmetry can exchange lines of different atoms, in 42 spaces.
  - **With the three order-free far sides**, no symmetry and no refinement class does.
- **Doctrine.** The map, the refinements and the conclusions are invariant under relabeling lines and under re-listing their points.

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings (both sets of maps); upstream proofs Proved | pass |
| 1 | Colour refinement on the native map | a class mixes two atoms in 87 of 277 spaces (14 of 23 Fano trees) |
| 2 | Pair refinement on the native map | within and across never share a class: 277 of 277 spaces |
| 3 | Control: pair refinement on the yes/no relation | mixes in 42 spaces, including all 39 with yes/no twins across atoms |

## What this does not establish

- **A uniform rule.** See ticket B.
- **Other spaces.** It is shown on these 277 spaces only, not for every knot space.
- **Census 6.** Its count over gluings is not used. The three order-free far sides suffice.

## Novelty

- **New here.** The measurement, and the conclusion that native creation fixes the atoms of every computed space.
- **Classical.** The refinements and their logic (Weisfeiler and Leman; Cai, Fürer and Immerman). Invariance of refinement colours under
  automorphisms is standard.
