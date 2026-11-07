# The far-side map

Status: Proved (exact computation on the 191 saved creation maps)

Ticket `FAR-READ-20261106-001A`, 2026-11-06.

## Question

- **Background (GLUE-READ C).** Whether creation occurs cannot read the atoms of every three-fold space. Which far side creates
  separates every two lines of different atoms, but it also varies inside atoms.
- **The question.** What does the far-side map look like, and what in it could hold an atom together?

## Dependencies

- **`GLUE-READ-20261106-001B`.** The 191 exact creation maps (`maps.json.gz`, bound by hash): 111 census spaces and 80 random spaces with
  plane glue.
- **`GLUE-READ-20261106-001A` and `C`.** The receiving-cut law, and the atoms of each space (`atoms_lib.py`).

## Setting

- **The far sides.** The creation map records, for a removal a and a gluing line b, which of the four far sides create: K4^(3), census
  6, the Fano plane, census 58.
- **Codes.** A vector is written with K, c, F and C for those far sides, and a dot for each that does not create. "-" means b shows fewer
  than six patterns.
- **Kinds of line.** An atom line is a line of a Fano atom; a glue line is any other.

## Results

1. **How the far sides create together (check 1, all 142,420 pairs).**
   - **The Fano plane and census 58 agree.** They create at exactly the same pairs.
   - **K4^(3) needs census 6.** It creates only where census 6 does.
   - **Census 6 without the Fano plane** happens only at glue lines (712 pairs, all `Kc..`).
   - **So at an atom line creation is one of four strengths:**
     - none;
     - the Fano plane and census 58 (`..FC`);
     - with census 6 (`.cFC`);
     - with all four (`KcFC`).

   | Gluing line | `-` | `....` | `..FC` | `.cFC` | `KcFC` | `Kc..` |
   | --- | --- | --- | --- | --- | --- | --- |
   | atom line | 964 | 18,543 | 69,573 | 17,915 | 16,689 | 0 |
   | glue line | 10,751 | 4,607 | 1,430 | 784 | 452 | 712 |

2. **Every Fano atom acts as one from outside (check 2).**
   - **On atom lines.** Every atom line outside an atom receives the same far-side vector from each of the atom's lines: 731 of 731
     atoms.
   - **Not on glue lines.** The atom's lines can differ there: only 452 of 731 atoms act as one on glue lines.
   - **Not in what they receive.** Only 247 of 731 atoms are seen alike by every outside atom line.

## Reading

- **Two far sides are interchangeable as probes.** The Fano plane and census 58 always agree.
- **The smaller far sides see more finely.**
  - Census 6 and K4^(3) add strength where deeper relations allow it. Ticket A of GLUE-READ shows that deeper relations can add far sides
    but never decide whether creation occurs.
  - At glue lines the small far sides can even create where the large ones cannot.
- **An atom acts as one from outside.** What any other atom receives from an atom does not depend on which of its lines was removed, even
  far side by far side.
  - **What tells an atom's lines apart.** Only what they do to glue, and what they receive.
  - **What ticket B uses.** This is the property behind ticket B's rule.

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings (GLUE-READ B's maps included); upstream proofs Proved | pass |
| 1 | How the far sides create together | as in the table; census 6 without the Fano plane only at glue lines |
| 2 | Atoms act as one from outside | 731 of 731 on atom lines; 452 on glue lines; 247 seen alike |

## What this does not establish

- **Proofs.** Neither the agreement of the far sides nor the fact that atoms act as one is proved; both are computed on these maps.
- **Other spaces.** Ticket C tests the consequence on fresh spaces.

## Novelty

New here: the structure of the far-side map, and that a Fano atom acts as one from outside.
