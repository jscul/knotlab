# Native far sides through plane glue

Status: Proved (exact computation on the 191 saved and 86 fresh creation maps, reading only the far sides that do not depend on
gluing)

Ticket `GENUS-READ-20261107-001C`, 2026-11-07.

## Question

- **What ticket A changed.** Census 6's column depends on how a line's points are listed. K4^(3), the Fano plane and census 58 do not.
- **What stands to be lost.** FAR-READ's case that which far side creates separates atoms where whether creation occurs cannot (GLUE-READ
  C's obstruction) may have rested on census 6.
- **The question.** Does it stand on the three native far sides alone? And how far do native twin rules read the atoms?

## Dependencies

- **`GENUS-READ-20261107-001A`.** Which far sides are native.
- **`FAR-READ-20261106-001C`.** The fresh maps (`maps.json.gz`, bound by hash).
- **`GLUE-READ-20261106-001C`.** The yes/no obstruction and the two-stage rule.
- **GLUE-READ B's saved maps** (through FAR-READ A's `far_lib.py`).

## Results

1. **Acts as one, natively (check 1).** Every Fano atom acts as one on the three native far sides: every atom line outside it receives
   the same (K4^(3), Fano, census 58) vector from each of its lines. That holds for 1,065 of 1,065 atoms in 277 spaces.
2. **The obstruction is lifted natively (check 2).**
   - **The pairs.** 39 spaces hold 372 pairs of lines of different atoms that are twins of the yes/no creation relation.
   - **All are told apart** by the three native far sides.
   - **Where the difference lies.**

   | Where the two lines' native vectors differ | Pairs |
   | --- | --- |
   | Everywhere: between them, rows and columns at atom lines and at other lines | 114 |
   | Rows at atom lines and at other lines, and columns from other lines | 99 |
   | Rows at atom lines and at other lines, and columns from both | 29 |
   | Rows at atom lines and at other lines only | 15 |
   | Rows at atom lines and other lines, and columns from atom lines | 1 |
   | **Only their rows at lines outside the atoms** | **112** |
   | Their rows at lines outside the atoms, and columns from atom lines | 2 |

3. **Native twin rules (check 3).**

   | Spaces | Yes/no two-stage (GLUE-READ C) | Native rows at atom lines | Native rows and columns at atom lines |
   | --- | --- | --- | --- |
   | Saved census (111) | 111 | 111 | 11 |
   | Saved random, Fano trees (3) | 3 | 3 | 0 |
   | Saved random, plane glue (77) | 54 | 59 | 0 |
   | Fresh census (28) | 28 | 28 | 0 |
   | Fresh plane (58) | 23 | 33 | 0 |
   | **All 277** | **219** | **234** | **11** |

   - **How the row rule fails.** It merges atoms in 38 spaces and splits or drops an atom in 5.
   - **Why adding columns fails.** An atom's lines differ in what they receive (cut lines against intact lines), so columns split atoms.

## Reading

- **The information is native.** What separates lines of atoms that meet one plane piece survives the loss of census 6: the gluing-free
  far sides tell every such pair apart.
- **The atoms act as one natively too.**
- **But a rule must look outside the atoms.**
  - **Where the distinction sits.** For 114 of the 372 pairs it lies only in what the two lines do to lines outside the atoms, the glue.
  - **Why that is hard.** Lines of one atom can differ there too: FAR-READ A found atoms acting as one on glue lines in only 452 of 731
    cases.
  - **So** a native rule must tell a difference between atoms apart from a difference inside one atom, at the glue.
- **No native rule here reads every space.**
  - **The best tried.** Native row twins at atom lines read 234 of 277.
  - **The full map.** It holds the information, but turning it into a reading is open.

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings (both sets of maps); upstream proofs Proved | pass |
| 1 | Acts as one on the native far sides | 1,065 of 1,065 |
| 2 | Yes/no twins across atoms told apart natively | 372 of 372, in 39 spaces; 114 only through rows outside the atoms |
| 3 | Native twin rules | rows: 234 of 277 (yes/no: 219); rows and columns: 11 |

## What this does not establish

- **A native rule that reads every space.**
- **Native census 6 through glue.** The count of its gluings was not computed in glue spaces, since the three native far sides already
  separate every pair.
- **Larger spaces than these.**

## Novelty

New here: the native measurement.
