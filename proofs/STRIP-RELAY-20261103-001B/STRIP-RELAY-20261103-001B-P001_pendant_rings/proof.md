# Pendant rings

Status: Proved (given the reduction lemma, the ladder law and the route criterion); checked for every ring length tested

Ticket `STRIP-RELAY-20261103-001B`, 2026-11-03.

## Question

- **The setting.** A **pendant ring** is the prism over a 2k-cycle minus one line, spliced onto a grid through one 3-edge cut. It is a
  rigid strip attached to a liquid body.
- **The question.** Does the halo of an opened handle follow it, and how far?

## Dependencies

- **`STRIP-RELAY-20261103-001A`.** The reduction lemma.
- **`PHASE-HALO-20261103-001B`.** The ladder law: on every prism, the far halo of an opened Fano handle is the far part of the long face
  opposite the attachment point.
- **The route criterion and the pipeline** (HALO-FORCING).

## 1. The ring law

**Statement.** Let a ring over a 2k-cycle (k ≥ 5) be spliced onto a grid. In the chain picture of the prism (PHASE-HALO B), let the
removed line be {j − 1, j, j + 1}. Attach an opened Fano handle at its middle point j. Then the far halo on the ring is exactly the far
part of the long face holding the removed line's far corner: k − 3 lines, running the whole length of the ring.

**Proof.**
- **Reduce.** With the attachment point and the gluing line on the ring, the grid side is untouched. By the reduction lemma it acts as
  the removed line, so creation at every ring line is creation in the closed prism, with the handle at j.
- **The ladder law.** In the closed prism the removed line is j's line whose far corner, (j − 1, j + 1), lies on the long face opposite
  j. So the far halo is that face's far lines: all k lines of the face but the three within three steps. ∎
- **Why it looked like a counterexample.** In the spliced space, the line through the cut point is a grid line. Its far corner lies in
  a small grid face, so the ring's far face is not among the faces around the point there. The ring, however, sees the closed prism.

## Checks

`check.py` (`result.json`, about three minutes with 22 processes):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Rings over 16- to 64-cycles on the 64-point grid, every attachment point | exactly one point creates beyond distance 3 off the faces around it, a cut point, at k − 3 ring lines (5, 9, 13, 21, 29) |
| 2 | The closed prism from that point | its removed line runs through it with its far corner on the opposite long face; the far halo is exactly that face's k − 3 far lines and contains the ring's creating lines |

## What this does not establish

- **Exact creation at these sizes.** It rests on the pipeline, validated on small spaces. The reduction itself is exact on a small
  junction (ticket A).
- **Strips between two liquid bodies.** No single cut leaves them untouched (ticket C).

## Novelty

New here: the ring law and its explanation of the FACE-CLAIM C junction.
