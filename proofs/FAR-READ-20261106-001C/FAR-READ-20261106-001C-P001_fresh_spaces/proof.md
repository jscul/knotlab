# Fresh spaces

Status: Proved (exact computation on fresh spaces fixed in advance; ticket B's rule frozen and bound by hash)

Ticket `FAR-READ-20261106-001C`, 2026-11-06.

## Question

- **Background (ticket B).** A four-step rule reads every one of the 191 saved spaces, but its thresholds and its fourth step were chosen
  on those maps.
- **The question.** Frozen, does it read the atoms of spaces it was not developed on?

## Dependencies

- **`FAR-READ-20261106-001B`.** The rule (`rule_lib.py`, bound by hash, unchanged since ticket B).
- **`FAR-READ-20261106-001A`.** The far-side map, and the fact that atoms act as one from outside.
- **`GLUE-READ-20261106-001B` and `C`.**
  - The space builders and the exact creation maps.
  - The atoms of each space, and the two-stage rule.
- **BRACE-TREE.** The source rule, for comparison.

## The fresh spaces (`fresh_lib.py`)

- **The candidates.** They were fixed by seeds before any map was computed. Each splice is the creation map's own, with a random element,
  lost element and port permutation.
  - **60 plane spaces** (seeds 7000 to 7059). Each is a random plane space of 6, 8, 10 or 12 points with two to five Fano atoms hung on
    it, mostly on the plane itself. Ticket B's random spaces hung atoms anywhere.
  - **40 census spaces** (seeds 8000 to 8039). Each is a census space with plane glue plus one to three more Fano atoms.
- **The cost cap.**
  - **Why it was set.** A first run on all 100 candidates was stopped for cost before any map was stored or any verdict seen.
  - **The cap.** A candidate is kept when the space minus its first line has at most 60,000 solutions. The cap was fixed before the
    second run.
  - **What it keeps.** 86 spaces: 58 plane spaces and 28 census spaces.
  - **What it drops.** Two plane spaces (12 points, 5 atoms) and 12 census spaces. Every dropped census space has three more atoms; only one
    census candidate with three more atoms survives.
- **The kept spaces.**
  - 18 to 41 points.
  - Two to five atoms in plane spaces and four to six in census spaces: 334 Fano atoms in all.
  - Every one is a knot space: no solutions.
- **Exact maps.**
  - Every row was computed exactly. The maps are in `maps.json.gz`, whose hash `result.json` records.
  - The default check recomputes two random rows of every space and compares them.

## Results (checks 2 and 3)

| Spaces | Spaces | Fano atoms | The frozen rule | Two-stage rule (GLUE-READ C) | Source rule counts | Yes/no obstructed | Far sides obstructed | Atoms acting as one |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Fresh plane, with plane glue | 58 | 188 | 58 | 23 | 40 | 24 | 0 | 188 |
| Fresh census, Fano trees | 3 | 17 | 3 | 3 | 3 | 0 | 0 | 17 |
| Fresh census, with plane glue | 25 | 129 | 25 | 25 | 25 | 0 | 0 | 129 |
| **All 86** | **86** | **334** | **86** | **51** | **68** | **24** | **0** | **334** |

"Yes/no obstructed" means that two lines of different atoms are indistinguishable to whether creation occurs. "Far sides obstructed" means
that they are indistinguishable far side by far side.

- **The frozen rule reads every fresh space.** It returns exactly the Fano atoms of all 86 spaces, and so counts them: 334 atoms.
- **The earlier rules do not.**
  - The two-stage twin rule reads 51 spaces, only 23 of the 58 plane spaces.
  - The source rule counts 68.
- **The obstruction is common here, and the far sides always lift it.**
  - **Yes/no.** In 24 of the 58 plane spaces, two lines of different atoms are indistinguishable to whether creation occurs. No rule
    that reads only whether creation occurs returns their atoms.
  - **Far sides.** In no space are two such lines indistinguishable far side by far side.
- **Atoms act as one.** All 334 atoms act as one from outside, as in ticket A.

## Reading

- **The rule was not fitted to its development maps.**
  - **Harder spaces.** The yes/no obstruction is far more common here than in ticket B's maps: 24 of 58 plane spaces, against 15 of 80
    random spaces there.
  - **No error.** The frozen rule makes none.
- **The record.** Every space computed in this epic is read: 277 spaces and 1,065 Fano atoms.
  - **How the rule reads them.** The atoms are the finest parts of the atom lines that act as one far side by far side. Single lines left
    out of a port piece are then reattached.
  - **Their number.** It is the genus wherever every handle is a Fano atom.

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings (ticket B's frozen rule included); upstream proofs Proved | pass |
| 1 | The fresh spaces and their exact maps | 86 within the cap (58 plane, 28 census), all knot spaces; sampled rows recomputed and equal |
| 2 | Ticket B's frozen rule, against the two-stage rule and the source rule | 86, 51 and 68 of 86 |
| 3 | The far sides on fresh spaces | no cross-atom pair indistinguishable far side by far side; 24 spaces yes/no obstructed; 334 of 334 atoms act as one |

## What this does not establish

- **A proof.** That the rule is correct is computed on 277 spaces, not proved. Neither "atoms act as one" nor the split and the
  reattachment is proved, even on Fano trees.
- **The cap's bias.**
  - **Census spaces.** Census spaces with three more atoms are almost absent: 1 of 13 kept.
  - **Plane spaces.** The largest plane spaces (12 points, 5 atoms) are absent as well.
- **Other families.**
  - **Construction.** Every space here is built by hanging Fano atoms on plane or census spaces.
  - **Non-Fano handles.** Handles that are not Fano atoms, such as census 58, are not read.
- **Native standing.** The rule reads the creation map, which tests each pair against four fixed far sides. It is native in the sense the
  creation map is, and no more.

## Novelty

New here: the confirmation of the rule on fresh spaces.
