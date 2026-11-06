# The frozen region

Status: Proved (creation needs a frozen line; the faces barred by a class are frozen); the extension at junctions and the counterexample
are computed, the counterexample exactly on a small piece

Ticket `FACE-CLAIM-20261103-001C`, 2026-11-03.

## Question

- **The law.** PHASE-HALO-20261103-001A proposed it from 126 tested attachment points: the halo beyond distance 3 lies on the faces
  around the attachment point, its own faces and the opposite ones.
- **The question.** Is that law true? If not, what replaces it?

## Dependencies

- **`FACE-CLAIM-20261103-001A`.** The reading lemma, the claim lemma, the claim rule, and `claim_lib.py`.
- **`PHASE-HALO-20261103-001A`.** The law under test, and the plane families.
- **The join method and the pipeline.** Exact creation and its validated stand-in.

## 1. Creation lies in the frozen region (proved)

- **Frozen lines.** A port pattern **freezes** a gluing line when it fixes two of its points, leaving two patterns.
- **Creation needs one.** A candidate knot of the claim rule needs a pair of handle points to leave the line two patterns with two points
  fixed. So some port pattern in the pair's pin freezes the line. Creation therefore lies in the **frozen region**: the lines frozen by
  some port pattern.
- **The bound from below.** By the reading lemma, the region contains every line of the faces barred by the pattern's class.

*Check 1:* on the generic pieces and on every point of a ladder arm spliced onto a grid, every line beyond distance 3 with a corner on
a barred face is frozen: 266 and 2,740 cases.

## 2. Unit propagation, and where it stops (computed)

**The procedure.** From the seeds of class k, propagate:
- **The seeds.** Port k's line takes its far corner, and the own arcs at k carry no skip.
- **The rules.** A line or face with one corner left must take it. A matched line or face blocks its other corners.
- **What it yields.** The points whose values are then fixed relative to the ports.

**Results.**
- **It is sound.** It never fixes two points of an unfrozen line.
- **On the generic pieces** (ladders, a grid, a thick tube, two grown spaces), it finds every frozen line beyond distance 3: 266 of 266.
  All of them lie on the faces around the point.
- **On the arm-on-grid piece** it misses 184 frozen (line, pattern) cases, at 8 of the 95 attachment points (0 to 5, 9 and 94). There
  the frozen region runs along the arm's far long face, which is not a face around the point. A global rigidity freezes it, not a chain
  of local claims: the arm's squares can only be matched one way once the junction is fixed.

## 3. Claim types (computed)

For each frozen line, count the port patterns under which it can claim its frozen corner, at each fixed value.

| Piece | Own arcs | Opposite faces | Off the faces around the point |
| --- | --- | --- | --- |
| Generic | (1, 1): 140 | (2, 2): 126 | none |
| Arm on grid | (1, 1): 1,664; rigid (0, 0): 112 | (2, 2): 876; rigid: 88 | rigid: 108; (2, 2): 26, all at point 94 |

Also on the arm-on-grid piece: 56 rigid cases on a face around the point that is barred by a different class.

**Reading.**
- **Generic pieces.** The claim lemma's types appear exactly.
- **Junctions.** Away from the faces around the point, the extended frozen lines are mostly rigid: they cannot claim at all, so no
  handle creates there. At one point, 94, they claim from two patterns, like an opposite face.

## 4. The counterexample (computed, and exact on a small piece)

- **On the arm-on-grid piece.** Each of the three handles (the Fano plane, census 58 minus line 0 or line 6) creates beyond distance 3
  off the faces around the attachment point. This happens at exactly one of the 95 points, point 94. There the halo runs along the arm's
  far long face.
- **On a small junction (exact).** The piece is a 21-point ladder arm spliced onto the 16-point grid, with the Fano plane at points 1,
  3 and 4. Exact creation (join method) agrees with the pipeline in every case. It creates beyond distance 3 off the faces around the
  point: 12 instances, at the three points, each with two removals and two far sides.

**So the law of PHASE-HALO-20261103-001A is false.** Its facts at the 126 tested points stand, but the generalization does not. Point 94
was not among them, since every third point was sampled.

**The corrected law.** The halo lies on frozen lines whose claims survive the handle's single points.
- **Generically** these are exactly the faces around the point, own arcs (one-pattern claims) and opposite faces (two-pattern claims).
- **At junctions** the frozen region can extend along a rigid strip, and creation follows it when the strip's claims are two-pattern.

## Checks

`check.py` (`result.json`, about fifteen minutes with 22 processes):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Barred faces frozen; unit propagation sound, complete on generic pieces, incomplete at 8 junction points | pass |
| 2 | Claim types | as tabulated |
| 3 | Creation off the faces around the point, all 95 points, three handles | exactly point 94, for each handle |
| 4 | Exact creation on the small junction | agreement in every case; 12 off-face far instances |

## What this does not establish

- **A characterization of the frozen region.** Junctions extend it by a global rigidity. Unit propagation misses this, and the exact
  extent is computed by the transfer, not described.
- **Whether junction creation is common.** The arm-on-grid piece has one such point out of 95; the small piece has three of 21.

## Novelty

- **New here.** The frozen-region bound, the propagation and claim-type measurements, and the counterexample.
- **Classical.** Unit propagation and forced edges of perfect matchings.
