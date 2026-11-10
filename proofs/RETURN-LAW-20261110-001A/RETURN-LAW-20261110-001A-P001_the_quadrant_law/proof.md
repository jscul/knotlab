# The quadrant law: the corner returns at the Catalan times

Status: Partial (pre-registered 2026-11-10, before the proof attempt).

Ticket `RETURN-LAW-20261110-001A`, epic `RETURN-LAW-20261110-001` (B138, the corner return law, at the coordinator's go-ahead after `REACH-HALVES-20261110-001`).

## What is registered

Doubled coordinates of FULL-REACH-PROOF-20261108-001A: contacts are the points (X, Y) with X + Y odd; an h (X odd) reads (X +- 1, Y +- 1) with equal signs, a v (X even) reads (X +- 1, Y -+ 1); reads leaving the region die; A[c, d] = 1 when c reads d, over GF(2). The box is [0, N]^2, N = 2n - 2; the quadrant is [0, oo)^2; the half-strips are [0, N] x [0, oo) and [0, oo) x [0, N]. The corner contact is c = (0, 1), and r(w) = sum_k A^k[c, c] w^k its return series. C(z) = sum_j z^(2^j - 1) is the Catalan series mod 2 and L(z) = z + z^2 + z^4 + ... + z^n the trace polynomial of GF(2n). Target A1: in the quadrant r(w) = C(w^4) over GF(2), equivalently the corner's first returns are odd exactly at the times 4 * 2^j. Target A2 (secondary, over the integers): the corner returns of length 4k number C_k^2; on the h contacts (2i + 1, 2j) this is the statement that the simple walks in the quarter plane that never step west along the x-axis have C_k^2 excursions of length 2k. Found before registration (computed, this thread): A1 below w^1200 (REACH-HALVES-20261110-001A); A2 for k <= 12 (exact integers); under the reflection in the line X - Y = -1 through the corner, a symmetry of the walk, the walks left over mod 2 are those whose every excursion off the line lies on the bottom-wall side and touches Y = 0 (their numbers 1, 2, 7, 34, 206, 1458, ... at k = 1, 2, 3, ... have the parity of C_k^2 to k = 12).

## Criteria, frozen

- **Proved:** a proof by hand of A1 (and of A2 if reached), each formula checked exactly (below w^1200; for A2 to k = 16), read by an independent referee pass before publication.
- **Refuted:** a time at which the count disagrees with A1 (or A2).
- **Obstructed:** the attempt names the lemma that would finish A1, checks it exactly, and says why it was not proved.

## Planned routes

1. **The reflection through the corner.** The reflection in the line X - Y = -1, (X, Y) -> (Y - 1, X + 1), is a symmetry of the free walk (as the reflection in X - Y = 1 is, `REACH-HALVES-20261110-001A`, Theorem 2); reflecting the first reflectable excursion off the line is an involution, and mod 2 only the walks whose every excursion lies on the bottom-wall side and touches Y = 0 (or X = N in the box) are left.
2. **The kernel method on the conveyor grid.** On the h contacts A^2 is the simple walk with no west step along the bottom row; its kernel xy - s(x + y)(1 + xy) is symmetric in x and y, and the unknowns are the bottom-row and left-column series.
3. **Row-to-row transfer.** Each step moves Y by one, so the walk is a matrix continued fraction over the rows, with the shift and truncation maps between rows of n - 1 and n contacts; along one axis this is the strip's Chebyshev structure (`REACH-HALVES-20261110-001A`, Theorem 3).
4. **Doubling.** The relation 1/r_2n(w) = 1/r_n(w^2) + w^4 asks for a map between the sides n and 2n; over GF(2) the free walk's A^4 is its A^2 at twice the scale.
