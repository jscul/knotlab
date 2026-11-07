# What plane glue does

Status: Proved (exact computation on 191 spaces; explained through ticket A's law)

Ticket `GLUE-READ-20261106-001B`, 2026-11-06.

## Question

- **Plane glue disturbs native creation.** In BRACE-TREE C's census:
  - the touching rule fails at some pairs of atom lines with glue between;
  - the twin rule gains glue lines and splits atoms.
- **The question.** What exactly does glue do, and how does ticket A's law account for it?

## Dependencies

- **`GLUE-READ-20261106-001A`.** The receiving-cut law (`port_lib.py`): creation at a Fano atom depends only on the relation the removal's side
  shows on the facing cut.
- **The census and the machinery behind it.** BRACE-TREE C's fresh census, and CHAIN-TRANSFER's exact creation rows.

## The spaces (check 1)

- **The census.** BRACE-TREE C's 111 fresh spaces, of 19 to 26 points: 17 Fano trees, 93 with plane glue, and one with census 58.
- **Random spaces.** 80 random spaces with plane glue, of 18 to 38 points and 2 to 6 Fano atoms:
  - 40 hang atoms on a random plane space (a cube grown by ladder rungs);
  - 40 hang one or two more atoms on a census space;
  - every splice is the creation map's own, with a random element, lost element and port permutation;
  - 3 of them came out as Fano trees.
- **Knot spaces.** All 191 have no solutions.
- **The maps.** Each exact creation map is computed from all solutions by the two-round rule and stored in `maps.json.gz` for ticket C.

## Results

1. **Creation through glue (check 2).**
   - **Through atoms the side is always free.** Wherever only Fano atoms lie between a removal and an atom, the removal's side leaves the
     facing cut's ports free, and the touching rule holds: 37,014 of 37,014 pairs.
   - **Through glue it varies.** The side is one of:
     - free;
     - one pattern pair excluded;
     - two ports tied, the third free. A doubled square can tie two ports by making them one point.
   - **The touching rule holds wherever the side is free:** 88,764 of 88,764 pairs, through atoms or glue, from removals in atoms or in
     glue.
   - **Every failure is at a constrained side:** 7,319 of the 11,100 constrained pairs. This is ticket A's law at work: a constrained side
     can make intact lines receive and cut lines go silent.
2. **The joined glue line (check 3).**
   - **Which lines join.** Every glue line that joins an atom's twin class (218) is a doubled-square line meeting the atom's cuts at two or
     more ports. A point that is a port of two of its cuts counts for each.
   - **The converse fails.** 20 such doubled-square lines do not join.
   - **Lines that never join.** Planar lines never join (85 that meet two or more ports).
3. **The split atom (check 3).**
   - **Which atoms split.** Of 731 atoms, 64 split, always into three twin classes.
   - **How.** Each split atom emits a line into a planar brace, and its classes are its lines through each point of that line. When the
     atom also lost one of those points, that class is its lines through the lost point.
   - **Where the classes differ.** Their out-sets differ only on glue lines.

## Reading

- **Glue lines see what atom lines do not.**
  - **Atom lines.** By ticket A's law, a Fano atom's lines respond only to the relation on their cut. An emitter's removal always leaves that
    relation free, so the other atoms cannot tell which of its lines was removed.
  - **Planar lines.** A planar brace's lines are not covered by the law. They do respond to which point of the emitted line the removed
    line passed through, and that is the split.
- **The joined line acts as part of the atom.** A doubled-square line through two of an atom's ports stands where the atom's lost line
  stood, so it creates and receives like the atom's own lines.
- **Glue constrains what a cut sees.** It can exclude a pattern pair or tie two ports, and then the table of ticket A replaces the touching
  rule.

## Checks

`check.py` (`result.json`; `maps.json.gz` holds the maps):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | The spaces and their exact creation maps | 111 census and 80 random spaces, all knot spaces; maps stored identically |
| 2 | Creation through glue | through atoms always free; touching rule at 88,764 of 88,764 free pairs; 7,319 failures, all at constrained sides |
| 3 | The two disturbances | 218 joined lines, all doubled-square lines meeting two or more ports; 64 split atoms, all by the points of a line emitted into a planar brace, differing only on glue lines |

## What this does not establish

- **Proofs about glue.** Which relation a plane piece presents is recorded, not derived from the plane's structure.
- **Larger spaces.** Nothing beyond 38 points.
- **Other far sides.**

## Novelty

New here: the record of what glue presents to atoms, and the local explanation of the twin rule's two disturbances.
