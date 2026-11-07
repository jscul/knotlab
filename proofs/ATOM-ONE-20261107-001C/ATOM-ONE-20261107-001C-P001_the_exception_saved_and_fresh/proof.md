# The exception, saved and fresh

Status: Proved (exact computation on the 191 saved spaces and FAR-READ C's 86 fresh spaces; predictions written before the run)

Ticket `ATOM-ONE-20261107-001C`, 2026-11-07.

## Question

Ticket B proves that a Fano atom acts as one, with two places it leaves to computation.
- **The exception.** A receiving atom's cut lines, when the port relation of the facing cut has six patterns. There deep pairs of the
  removal's side could add census 6 or K4^(3).
- **The closed verdict.** Bounding cannot show that an atom's lines receive exactly its closed verdict. Deep points behind its own other
  elements could add creation (ticket B, check 3).

What do real spaces do in both places?

## Dependencies

- **`ATOM-ONE-20261107-001B`.** The exception and the bound's limit.
- **`FAR-READ-20261106-001C`.** The 86 fresh spaces and their exact maps (`maps.json.gz`, bound by hash). They were fixed before this
  question was asked.
- **GLUE-READ B's saved maps** (through FAR-READ A's `far_lib.py`).

## Predictions

These were written before `exc_lib.py` had run on any space. They are kept in the epic's working notes and quoted in the decision note.
- **P1 (fresh).** The exact far-side vector equals the verdict of the atom's real side with the removal's side replaced by its port
  relation. This was already known on the saved spaces.
- **P2 (saved and fresh).** The exact far-side vector equals the atom's own closed verdict.
- **P3 (saved and fresh).** At every exception line, the real removal's side adds no far side.

## Method (`exc_lib.py`)

For every removal a and every line b of a Fano atom B not holding it, let C be B's cut facing a and R the relation the removal's side
shows there.
- **Own.** B's own verdict in the space's coordinates: B's lines, each other closed side replaced by the relation it shows on its
  channels, and R on C's channels. Masks come only from B's points and channels.
- **Near.** B's real side, with every point behind B's other cuts kept, and R on C.
- **Exact.** The creation map.
- **Far (at exception lines only).** B's own masks together with every point of the real removal's side.

## Results

| Spaces | Pairs | Exact = own | Exact = near | Receiving cuts with six patterns | Their cut lines | With room to add | Added by the real side |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Saved (191) | 99,864 | 99,864 | 99,864 | 599 | 1,782 | 1,193 | 0 |
| Fresh (86) | 54,301 | 54,301 | 54,301 | 726 | 2,141 | 1,432 | 0 |
| **All 277** | **154,165** | **154,165** | **154,165** | **1,325** | **3,923** | **2,625** | **0** |

"With room to add" counts the lines where the closed verdict lacks census 6 or K4^(3), so a far side could have been added there.

- **All three predictions held.**
- **A Fano atom's lines see only the port relation of their facing cut.** In every computed space, the closed verdict for that relation is
  the exact creation, far side by far side.
- **The exception never bites.**
  - It occurs: 1,325 receiving cuts, with 2,625 cut lines where a far side could be added.
  - The real removal's side adds none there.
- **The points behind the atom's own other elements never add anything.** Ticket B's bound allowed it.

## Reading

- **Acts-as-one, far side by far side, in every computed space.** Ticket B proves it outside the exception. Here the exception, which
  the proof leaves open, is empty on 277 spaces.
- **Real sides are narrower than the bound.**
  - The relations that would make a difference exist abstractly (ticket B), but no real side presents them.
  - **The likely reason.** The sides of a knot space are themselves knot pieces, built from Fano atoms and planar braces, and they cannot
    carry the port parities those relations need. This is a conjecture, not shown here.

## Checks

`check.py` (`result.json`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings (both sets of exact maps); upstream proofs Proved | pass |
| 1 | Saved spaces | 99,864 of 99,864 exact = own = near |
| 2 | Fresh spaces | 54,301 of 54,301 exact = own = near |
| 3 | The exception | 1,325 cuts, 3,923 lines, 2,625 with room; 0 far sides added |

## What this does not establish

- **A proof of the exception.** It is computed on these 277 spaces only.
- **The cost cap.** The fresh spaces are the 86 within FAR-READ C's cap. It drops most census spaces with three added atoms.
- **Non-Fano handles and glue lines.** Not treated.

## Novelty

New here: the measurement of both places on saved and fresh spaces.
