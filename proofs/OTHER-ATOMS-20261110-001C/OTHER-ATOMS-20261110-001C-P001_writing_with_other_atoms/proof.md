# Writing with other atoms

Status: Computed (searches and random learners; not exhaustive). `check.py` (6 seconds), tier T3 of
`research/OTHER-ATOMS-20261110-001/preregistration.md`, frozen before any run (commit `1fd95cc5f`).

## What is checked

`ADDRESS-SEQ-20261110-001A`'s procedure, unchanged except for the atom. Growth uses the atom's torus and Kasteleyn law (`multi_lib.grow_one`,
the frozen growth move with the atom swapped in), and an atom's role is read by SAT on its outer points (six patterns: acts; eight:
transparent) instead of by listing the Fano atom's six inner points. On K_3, at every line orbit, three atoms at l0 and distances 2 and 3;
the six two-atom addresses written in turn by the frozen targeted search, and after each write one random sphere point flipped and the
learner M1 run to the floor.

**Code control.** With the Fano atom and random.Random(88), the patched code reproduces `ADDRESS-SEQ-20261110-001A`'s three K_3 rows
exactly, configuration counts included.

## Results (random.Random(97))

| Atom | Points | Writes | Written | Held | Configurations searched |
| --- | --- | --- | --- | --- | --- |
| Fano (7,2,1) | 7 | 18 | 18 | 18 | 11,692 |
| thin (2,1,2) | 4 | 18 | 18 | 18 | 7,461 |
| thin (3,2,2) | 6 | 18 | 18 | 18 | 13,565 |
| thin (4,3,2) | 8 | 18 | 18 | 18 | 17,880 |

Every write was reached and every one held after the disturbance; prediction P4 held. The smallest atom that holds a written address
here is the thin torus of index 4 less a point: three points and four lines. These are computations on K_3 only.
