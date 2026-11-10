# One far wall is invisible at even sides

Status: Partial (pre-registered 2026-11-10, before the proof attempt).

Ticket `RETURN-LAW-20261110-001B`, epic `RETURN-LAW-20261110-001` (B138, the corner return law, at the coordinator's go-ahead after `REACH-HALVES-20261110-001`).

## What is registered

Doubled coordinates of FULL-REACH-PROOF-20261108-001A: contacts are the points (X, Y) with X + Y odd; an h (X odd) reads (X +- 1, Y +- 1) with equal signs, a v (X even) reads (X +- 1, Y -+ 1); reads leaving the region die; A[c, d] = 1 when c reads d, over GF(2). The box is [0, N]^2, N = 2n - 2; the quadrant is [0, oo)^2; the half-strips are [0, N] x [0, oo) and [0, oo) x [0, N]. The corner contact is c = (0, 1), and r(w) = sum_k A^k[c, c] w^k its return series. C(z) = sum_j z^(2^j - 1) is the Catalan series mod 2 and L(z) = z + z^2 + z^4 + ... + z^n the trace polynomial of GF(2n). Target B1: at every even n >= 2 the corner's return series in either half-strip equals the quadrant's, C(w^4), over GF(2). Target B2: at every odd n >= 3 they differ, first at time 4n. Found before registration (computed, this thread): B1 below w^1200 at the even sides 2 to 38 and below w^700 at 2 to 20; B2 at the odd sides 3 to 21 (first difference at 4n) and some difference below w^1200 at every odd side 3 to 39. The two half-strips have the same return series at every side (the diagonal reflection carries one to the other with A to its transpose, and the corner's return series is the same read from (0, 1) or (1, 0)).

## Criteria, frozen

- **Proved:** a proof by hand of B1 for every even n (and of B2 if reached), each formula checked exactly at the sides 2 to 40, read by an independent referee pass before publication.
- **Refuted:** an even side at which the half-strip's corner return series differs from the quadrant's.
- **Obstructed:** the attempt names the lemma that would finish B1, checks it exactly at the even sides 2 to 40, and says why it was not proved.

## Planned routes

1. **The reflection through the corner.** The reflection in the line X - Y = -1, (X, Y) -> (Y - 1, X + 1), is a symmetry of the free walk (as the reflection in X - Y = 1 is, `REACH-HALVES-20261110-001A`, Theorem 2); reflecting the first reflectable excursion off the line is an involution, and mod 2 only the walks whose every excursion lies on the bottom-wall side and touches Y = 0 (or X = N in the box) are left.
2. **The kernel method on the conveyor grid.** On the h contacts A^2 is the simple walk with no west step along the bottom row; its kernel xy - s(x + y)(1 + xy) is symmetric in x and y, and the unknowns are the bottom-row and left-column series.
3. **Row-to-row transfer.** Each step moves Y by one, so the walk is a matrix continued fraction over the rows, with the shift and truncation maps between rows of n - 1 and n contacts; along one axis this is the strip's Chebyshev structure (`REACH-HALVES-20261110-001A`, Theorem 3).
4. **Doubling.** The relation 1/r_2n(w) = 1/r_n(w^2) + w^4 asks for a map between the sides n and 2n; over GF(2) the free walk's A^4 is its A^2 at twice the scale.
