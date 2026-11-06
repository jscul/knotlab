# Heights and reduction

Status: Proved (the heights lemma; the reduction lemma for the transfer and the pipeline); checked by computation, and exactly on a small
junction

Ticket `STRIP-RELAY-20261103-001A`, 2026-11-03.

## Question

- **The heights question (FACE-CLAIM C).** Creation needs a frozen gluing line. Which points does a port pattern freeze?
- **The junction question.** On a ladder arm spliced onto a grid, the frozen region left the faces around the attachment point, and so did
  the halo. Why?

## Dependencies

- **`HALO-FORCING-20261103-001B`.** Corner matchings correspond to integer heights: solutions of difference constraints. A point's value
  relative to another is the parity of their height difference, against the reference solution.
- **`PLANAR-THEOREM-20261102-001A`.** Such height sets are closed under rounded midpoints.
- **`HANDLE-LOCALITY-20261103-001A`.** Seen from across a 3-edge cut, an untouched side looks exactly like the point or line it replaced.
- **`FACE-CLAIM-20261103-001A` and `C`.** The reading lemma, the claim rule, and the junction counterexample.

## 1. The heights lemma (proved)

**The ports' heights are fixed by the class.** In the split at the attachment point, the merged face F0 receives one skip in every
corner matching μ.
- **Along an arc.** The heights of consecutive points differ by μ − μ0 at the corner between them. So along the arc A(i, j) from port i
  to port j, the heights differ by [μ skips on A(i, j)] − [μ0 skips on A(i, j)].
- **The class decides the arc.** It says which arc holds μ's skip (the one opposite the odd port, FACE-CLAIM A). So all three height
  differences between the ports are fixed, not just their parities.

**Frozen means fixed height.**
- **The set.** Heights with fixed port values are the integer solutions of a difference system with fixed boundary values. This set is
  closed under rounded midpoints.
- **One point's heights form an interval.** If two heights a < b of a point p occur, then halving repeatedly yields every integer between
  them.
- **So frozen means fixed height.** If p's height can vary, two consecutive heights occur, so both parities do, and p's value is free. If
  it cannot vary, p's value is fixed. **A port pattern freezes exactly the points whose height difference to the ports cannot vary.** ∎
- **A complement changes nothing.** A raw port pattern and its complement give the same parities.

**What the check computes.** The check computes everything with the halving of HALO-FORCING B.
- **The ports.** Every port pattern fixes every port height difference (halved range 0).
- **Frozen points.** A point is frozen exactly when one parity of its difference to port 0 is feasible. For that parity the difference
  is then fixed (halved range 0).
- **Agreement with the transfer.** A line shows at most two patterns exactly when two of its points are frozen.

## 2. The reduction lemma (proved for the transfer)

**Statement.** Let a 3-edge cut separate the plane piece into a side X, holding the attachment point and the gluing line, and a side Y
holding neither. Then the transfer R(L) and the pipeline's creation at L equal those of X with Y replaced by the vertex it lost: a point
or a line.

**Proof.**
- **What Y offers.** Y is untouched: no split, no gluing line, no removal. So its solutions offer the cut exactly the patterns of that
  vertex (the interface lemma).
- **The join.** By the join lemma, X's solutions together with Y's are those of X with the vertex restored, restricted to X's points.
- **The transfer.** R(L) projects them, so it is unchanged up to the renaming of values, the gauge.
- **Creation.** The pipeline decides creation from R(L), the handle and the far side alone. ∎
- **Port alignment.** The handle's ports must sit on corresponding lines. The line through the attachment point that crosses the cut
  corresponds to the restored vertex.

**Consequence: the faces-around-the-point law holds in the reduced space.**
- **The junction.** The junction of FACE-CLAIM C is a ring (a prism minus a line) spliced onto a grid.
- **What the ring sees.** From a ring point, with the gluing line on the ring, the grid acts as the missing line, so the ring sees the
  closed prism.
- **The far face.** There, the far long face is the attachment point's opposite face.

## Checks

`check.py` (`result.json`, about six minutes with 22 processes):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Heights lemma on a ladder, a grid, a grown space, a thick tube and the ladder arm on a grid | 102 of 102 port patterns fix the port heights; 488 of 488 frozen (point, pattern) pairs have a fixed height difference, none a varying one; 4,752 of 4,752 (line, pattern) pairs agree with the transfer |
| 2 | Reduction: creation in the spliced and the reduced space at every point of two rings and four small junctions | 253,536 (line, removal, far side) cases, no disagreement (2,232 far and 10,096 near creating) |
| 3 | The reduced-faces law | all 554 creating far lines on the point's side lie on a face around it in the reduced space, including the 28 off those faces in the spliced space; the 100 across the cut lie on faces around the point |
| 4 | Exact reduction on the 21-point junction | 1,080 cases, no disagreement (96 creating) |

## What this does not establish

- **Exact creation in general.** The reduction lemma is proved for the transfer and the pipeline. Exact creation is compared only on a
  small junction.
- **Junctions without an untouched side.** When both sides of a cut are touched, as with a handle on one side and the gluing line on the
  other, nothing collapses (ticket C).

## Novelty

- **New here.** The heights lemma (port heights fixed by the class; frozen means fixed height) and the reduction lemma with its
  explanation of the junction.
- **Prior.** Midpoint convexity of heights and the interface lemma.
