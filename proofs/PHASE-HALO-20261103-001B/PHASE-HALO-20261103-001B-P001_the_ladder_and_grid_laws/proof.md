# The ladder and grid laws

Status: Proved (the ladder reduction and the independence lemma); the finite cases and the grid certificates are computed

Ticket `PHASE-HALO-20261103-001B`, 2026-11-03.

## Question

- **The measurement (HALO-FORCING C).** An opened handle attached at a point creates along a whole ladder but only three steps into a
  grid.
- **The ladder law.** On every ladder, the halo runs the full length of the face opposite the attachment point.
- **The grid law.** Far grid lines are independent of the attachment point.
- **The question.** Can these be proved?

## Dependencies

- **`PHASE-HALO-20261103-001A`.** The opposite-face law, and the plane families (`families_lib.py`).
- **`HALO-FORCING-20261103-001B`.** The transfer by heights (exact).
- **`HALO-FORCING-20261103-001C`.** The validated pipeline.
- **Classical.**
  - Boolean transfer matrices.
  - Kasteleyn signings of a plane graph agree up to switching. Here that is complementing a point's values, or all three signs of a
    line; both rename values, so creation is unchanged.

## 1. The ladder law (proved, with a finite certificate)

- **A ladder is a chain.** The prism over a 2k-cycle is the cyclic chain of consecutive triples: points 0, …, 2k−1 and lines
  {j−1, j, j+1}. The isomorphism is explicit:
  - top vertex j goes to point j if j is even, and to line j if j is odd;
  - bottom vertex j goes to line j if j is even, and to point j if j is odd.
- **Canonical signs.** Every line gets signs (0, 0, 1), except lines 0 and 1, which get (0, 0, 0) and (0, 1, 0). All faces are odd for
  every k ≥ 4:
  - **The squares.** They are local and repeat with the chain.
  - **The two long faces.** A standard line's corner on a long face joins points j−1 and j+1, with signs 0 and 1. It adds 1 + 1, so it
    leaves the parity unchanged as k grows.
  - **Checked** directly for k = 4 to 40.
- **The transfer matrix.** On states (x_{j−1}, x_j) → (x_j, x_{j+1}), a standard line forbids exactly x_{j−1} = x_j ≠ x_{j+1}:
  - (0,0) → (0,0) and (1,1) → (1,1);
  - (0,1) → {(1,0), (1,1)} and (1,0) → {(0,0), (0,1)}.
  - Its powers repeat with period 2 from the second: T² = T⁴ and T³ = T⁵.
- **Assembly.** Split the chain at point 0, so the ports sit on lines 2k−1, 0 and 1. For a line j with 2 ≤ j ≤ 2k−2, the transfer R(j)
  is the join of three pieces:
  - the boundary relation of lines 2k−1, 0 and 1 with the ports;
  - T^{j−2} from (x₁, x₂) to (x_{j−1}, x_j), then line j itself;
  - T^{2k−2−j} to (x_{2k−2}, x_{2k−1}).
  - This agrees with the heights computation on every line, for k = 4 to 25.
- **Hence.** For j − 2 ≥ 2 and 2k − 2 − j ≥ 2, R(j) depends only on the parity of j. There is one transfer for the even lines (the long
  face opposite point 0) and one for the odd lines (point 0's own long face), and they are the same on every prism.
- **The halo.** Creation at a line is decided from its transfer, its handle and its far side (the route criterion). So on every prism
  the halo is constant along each parity class. Computed for k = 5 to 40: every far line on the opposite face creates, and no far line on
  the point's own face does.
- **The theorem.** On every prism over a 2k-cycle, k ≥ 5, the halo of an opened Fano handle attached at a point runs the full length of
  the face opposite that point.
- **Caveat.** The route criterion is proved sufficient for generation. Its converse, and its agreement with exact creation, are checked
  on small spaces.

## 2. The grid law

- **The independence lemma (proved).** Suppose R(L) is all 36 pairs. Then every near set of handle points and ports leaves all six of L's
  patterns. So no crossing knot through handle points alone exists at L, whatever the handle and far side.
- **Exact certificates (computed; the transfer by heights is exact).**
  - **64-point grid, four attachment points.** Every line at distance 9 or more has the full transfer. From two of the points, so does
    every line at distance 7 or more.
  - **256-point grid.** Every line at distance 7 or more has the full transfer.
  - **The exceptions.** One line at distance 7 from each of the other two points, with transfers of 32 and 34 pairs.
- **The reason: height ranges.**
  - **The quantity.** The smallest range of height differences between a port's region and the line's, D(a, b) + D(b, a). It does not
    depend on the reference matching.
  - **Grids (liquid).** The range grows with distance: on the 256-point grid, 0 at distance 3, 1 at 5, 1–2 at 7, and up to 11–12 at 29.
    The heights fluctuate, so the parities decouple.
  - **Ladders (frozen).** The range is 0 at every distance: some height difference between a port and the line is fixed however far away.
- **With the opposite-face law.** The grid's opposite faces have at most three corners, which explains the reach of 3.

## Checks

`check.py` (`result.json`, about five minutes):

| # | Check | Result |
| --- | --- | --- |
| 0 | Hash bindings; upstream proofs Proved | pass |
| 1 | Grid independence and height ranges | far grid lines independent as stated; ranges 0 on ladders, growing on grids |
| 2 | Ladder reduction | isomorphism and Kasteleyn signs for k = 4 to 40; T² = T⁴, T³ = T⁵; matrices = heights on every line, k = 4 to 25; one transfer per parity |
| 3 | Ladder halo | k = 5 to 40: far opposite-face lines all create, far own-face lines none |

## What this does not establish

- **The grid law for every grid size.** The certificates cover the 64- and 256-point grids.
- **Exact creation at every size.** The ladder theorem rests on the route criterion, whose converse is checked only on small spaces.

## Novelty

- **New here.** The chain picture of the ladder, the reduction, and the height-range explanation.
- **Classical.** Transfer matrices and Kasteleyn's theorem.
