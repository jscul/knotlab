# A rule that reads every saved space

Status: Proved (exact computation on the 191 saved creation maps; the rule is frozen here for ticket C)

Ticket `FAR-READ-20261106-001B`, 2026-11-06.

## Question

- **Background (GLUE-READ C).**
  - **Its rule.** The two-stage twin rule reads 168 of the 191 saved spaces.
  - **The obstruction.** Where atoms meet one planar brace, whether creation occurs can fail to tell their lines apart. The far sides tell
    them apart.
- **The question.** Is there a rule, using which far side creates, that reads every saved space?

## Dependencies

- **`FAR-READ-20261106-001A`.** The far-side map, and the fact that every Fano atom acts as one from outside.
- **`GLUE-READ-20261106-001B` and `C`.** The 191 exact maps, and the two-stage rule.

## The rule (`rule_lib.py`)

Creation is the creation map's. "a creates at b" means some far side does, and a far-side vector says which do.

1. **Twins.** Two lines are twins when they create at each other and at the same other lines. The lines in twin classes of two or more
   are the atom lines.
2. **Atom twins.** Twins compared on atom lines alone give the candidate classes.
3. **Split by parts that act as one.**
   - **Acting as one.** A set S of atom lines acts as one when every atom line outside S receives the same far-side vector from each line
     of S.
   - **The split.** A candidate of six or more lines that is partitioned into two or more such sets, each of three or more lines, is split
     into the finest such partition. Each part is then examined again.
4. **Reattach.** A line left single by step 1 joins a class of three or more lines when two things hold, and when that class is the only
   one that fits:
   - the line and the class's lines create at each other through the Fano plane;
   - the class acts as one, and the line sends every atom line outside it the class's far-side vector.

**The output.** The classes are read as the atoms, and their number as the genus.

## Why each step

- **Step 3 separates atoms that meet one planar brace.**
  - **Atoms act as one (ticket A).** Two atoms merged by step 2 each act as one from outside.
  - **So the merge splits.** Their union is partitioned into two parts that act as one.
  - **A single atom does not split.** Its smaller parts that act as one never cover it, except in parts of two lines. That is why parts need
    three lines.
- **Step 4 recovers a line that step 1 drops.**
  - **Which line.** When an atom emits two lines, one into a planar brace, its line through the point where they meet carries a port
    piece of one line. That piece is a twin of nothing.
  - **Why the Fano plane.** Mutual creation through the Fano plane, rather than through any far side, keeps out glue lines. The small far
    sides create at glue lines where the Fano plane does not (ticket A).

## Results (checks 1 and 2)

| Spaces | Steps 1 and 2 | + step 3 | + step 4, through whether creation occurs | The rule |
| --- | --- | --- | --- | --- |
| Census, Fano trees (17) | 17 | 17 | 17 | 17 |
| Census, plane glue (93) | 93 | 93 | 93 | 93 |
| Census, census 58 (1) | 1 | 1 | 1 | 1 |
| Random, Fano trees (3) | 3 | 3 | 3 | 3 |
| Random, plane glue (77) | 54 | 71 | 74 | 77 |
| **All 191** | **168** | **185** | **188** | **191** |

- **Exact on every saved space.** The rule returns exactly the Fano atoms of all 191 saved spaces, 731 atoms, and so counts them.
- **The minimum part size matters.** Allowing parts of two lines breaks three spaces.
- **On the census-58 space** it reads the two Fano atoms but not the census-58 handle.

## Reading

- **Atoms are the finest parts that act as one.**
  - **From outside.** A handle shows itself to the rest of the space as a single unit: every other handle line sees each of its lines alike,
    far side by far side.
  - **From inside.** Its own lines are told apart only by what they do to glue and what they receive.
- **Why the far sides are needed.** Whether creation occurs makes two handles on one plane look alike. Which far side creates keeps each
  handle's unity visible from outside.

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings (GLUE-READ B's maps included); upstream proofs Proved | pass |
| 1 | The rule on all 191 saved spaces | 191 of 191, exactly the Fano atoms |
| 2 | Every step is needed | 168, 185, 188, 191; parts of two lines: 188 |

## What this does not establish

- **Fresh spaces.** The rule's thresholds and its fourth step were chosen on these maps, so this is a development result. Ticket C tests
  the frozen rule on fresh spaces.
- **Proofs.** Neither the split nor the reattachment is proved, even on Fano trees. There the rule agrees with CHAIN-TRANSFER C's on the
  20 saved trees.
- **Non-Fano handles.**

## Novelty

New here: the rule and its record.
