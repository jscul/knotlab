# Opposite faces carry the halo

Status: Proved (item 1); items 2 and 3 are exhaustive computations with a validated pipeline

Ticket `PHASE-HALO-20261103-001A`, 2026-11-03.

## Question

- **Background (HALO-FORCING C).** An opened handle attached at a point creates along a whole ladder but only three steps into a grid.
- **The reading tested here.** That this follows the dimer phase: the halo is the frozen region joined to the handle.
- **How it was tested.** On plane pieces that mix frozen and liquid parts.

## Dependencies

- **`HALO-FORCING-20261103-001A–C`.** The route criterion, the height transfer, and the validated pipeline (`halo_pipeline.py`).
- **`HANDLE-LOCALITY-20261103-001B`.** The join method, for exact creation.

## Setting

- **The handle.** A knot space minus a line (the Fano plane, or census 58), spliced into a point z of a plane knot space.
- **The point split.** In the point split at z, each line through z has two corners at z and one away from it.
- **The opposite faces.** The faces of those three far corners are the faces opposite z.
- **The point's own faces.** The three faces at z, which merge in the split.

## 1. The claiming lemma (proved)

**In any solution of the point split:**
- a port is the odd point of its line exactly when that line skips its corner opposite the port, in the opposite face f;
- so no other line of f skips into f;
- otherwise exactly one other line of f does.

*Proof.* A line skips the corner between its two agreeing points, so it skips the corner opposite the port exactly when the port is odd.
Every face receives exactly one skip (corner matchings, HALO-FORCING B). ∎

So whether a port is odd is a fact that every line around the opposite face feels: a face is a constraint shared by all its lines.

Checked by brute force on every point split of the planar census and two 10-point grown spaces: 5,544 (split, port line, solution)
triples.

## 2. The opposite-face law (computation, Fano plane as handle)

**At 126 attachment points, every halo line beyond distance 3 lies on a face opposite the attachment point.** The test covered every
removal inside the handle and four far sides.

| Family | Attachment points | Far halo inside the opposite faces | Equal to their far lines | Points with a far halo |
| --- | --- | --- | --- | --- |
| Ladders (prisms over 12-, 20-, 30-cycles) | 6 | 6 | 6 | 6 |
| Thick tubes (duals of bipyramids subdivided once or twice) | 34 | 34 | 34 | 10 |
| Grid (64-point octahedral dual) | 4 | 4 | 4 | 0 |
| Random grown spaces (20 to 40 points) | 50 | 50 | 50 | 36 |
| A ladder arm (prism over a 32-cycle) spliced onto the 64-point grid | 32 | 32 | 30 | 12 |
| **All** | **126** | **126** | **124** | **64** |

**Reading.** The reach is set by the opposite faces' size, not by a dimer phase as such.
- **A ladder.** One opposite face is a whole cycle of the ladder, so the halo runs its full length.
- **A grid.** Every face has at most three corners, so the opposite faces end within distance 3.
- **A thick tube.** Its halo goes around a large polar face only when the handle sits beside that face.
- **The mixed piece.**
  - **Arm points.** From points whose opposite face is one of the arm's long faces, the halo runs along the arm.
  - **Grid-body points.** From points in the grid body, it stays local.
- **The two exceptions to equality.** Both are next to the junction: lines on the opposite face that are forced but routable.

## 3. Census 58 as handle (computation)

- **The pipeline.** It equals exact creation in all 976 cases on two 10-point grown spaces at two attachment points each: 156 creating,
  820 not.
- **The law.** On the ladders, the grid and the mixed space, the halo beyond distance 3 lies on the attachment point's own or opposite
  faces at all 24 points tested.
  - **Where the opposite faces alone fail.** At the 5 arm points of the mixed space, it also runs along the point's own long face.
    With the Fano plane as handle, the lines of that face are forced but routable.
- **So** the general law is "the faces around the attachment point". Which of them a handle uses depends on the handle.

## Checks

`check.py` (`result.json`, about five minutes; families in `families_lib.py`):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Claiming lemma | 5,544 of 5,544 triples |
| 2 | Opposite-face law, Fano plane as handle | 126 of 126 points contained; 124 equal |
| 3 | Census 58 as handle | 976 of 976 pipeline cases equal exact creation; own-or-opposite law at 24 of 24 points; opposite-only at 19 |

## What this does not establish

- **A proof of the law.** Why a line off the faces around the attachment point never creates beyond distance 3.
- **Exactness at large sizes.** The route criterion's exactness there; it was checked only on small spaces.
- **Other handles.** Handles other than the Fano plane and census 58, and handles attached at a line (screened by HANDLE-LOCALITY B).

## Novelty

- **New here.** The claiming lemma, the opposite-face law, and the handle dependence.
- **Classical.** The skip model's matching structure.
