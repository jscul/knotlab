# The box law at every power of two

Status: Partial (pre-registered 2026-11-10, before the proof attempt).

Ticket `RETURN-LAW-20261110-001C`, epic `RETURN-LAW-20261110-001` (B138, the corner return law, at the coordinator's go-ahead after `REACH-HALVES-20261110-001`).

## What is registered

Doubled coordinates of FULL-REACH-PROOF-20261108-001A: contacts are the points (X, Y) with X + Y odd; an h (X odd) reads (X +- 1, Y +- 1) with equal signs, a v (X even) reads (X +- 1, Y -+ 1); reads leaving the region die; A[c, d] = 1 when c reads d, over GF(2). The box is [0, N]^2, N = 2n - 2; the quadrant is [0, oo)^2; the half-strips are [0, N] x [0, oo) and [0, oo) x [0, N]. The corner contact is c = (0, 1), and r(w) = sum_k A^k[c, c] w^k its return series. C(z) = sum_j z^(2^j - 1) is the Catalan series mod 2 and L(z) = z + z^2 + z^4 + ... + z^n the trace polynomial of GF(2n). Target C1: at every n = 2^m >= 4, r(w) = 1/(1 + L(w^4)) in the box over GF(2); equivalently the corner returns at time 4j exactly when j + 1 is a power of two modulo 2n - 1, or r(w) = C_m(w^4)/(1 + w^(4(2n - 1))) with C_m(z) = 1 + z + z^3 + ... + z^(n - 1) the quadrant's series truncated: the quadrant's Catalan series folded modulo 2n - 1. On the way, C2: the doubling relation 1/r_2n(w) = 1/r_n(w^2) + w^4 for n = 2^m >= 4, which with r_4 gives C1 (computed: it fails from 2 to 4, 3 to 6, 5 to 10 and 6 to 12); C3: at every side n >= 3 the box's first-return series is the quadrant's plus w^(8n) plus higher terms, so the box and the quadrant agree below time 8n and differ at 8n. Found before registration (computed): C1 at 4 to 128 (REACH-HALVES-20261110-001A and its stress test); C3 at every side from 3 to 21; at n = 2 the law fails (the box is one 4-cycle, r = 1/(1 + w^4)); the corner's whole vector returns, e_c A^(4(2n - 1)) = e_c, at 4 and 8, but at 16 and 32 only at 8(2n - 1); the four-corner formula sum_i G_(c, rho^i c) rho^i = C_m(w^4)/(1 + w^(2n - 1) rho) + w^(2n - 3) rho^3 (rho the quarter turn) below w^1200 at 4, 8, 16 and 32, false at 6 and 12.

## Criteria, frozen

- **Proved:** a proof by hand of C1 for every m >= 2, each of its formulas checked exactly at sides 4 to 64, read by an independent referee pass before publication.
- **Refuted:** a power of two n >= 4 at which the box's corner return series is not 1/(1 + L(w^4)).
- **Obstructed:** the attempt names the lemma that would finish C1, checks it exactly at sides 4 to 64, and says why it was not proved.

## Planned routes

1. **The reflection through the corner.** The reflection in the line X - Y = -1, (X, Y) -> (Y - 1, X + 1), is a symmetry of the free walk (as the reflection in X - Y = 1 is, `REACH-HALVES-20261110-001A`, Theorem 2); reflecting the first reflectable excursion off the line is an involution, and mod 2 only the walks whose every excursion lies on the bottom-wall side and touches Y = 0 (or X = N in the box) are left.
2. **The kernel method on the conveyor grid.** On the h contacts A^2 is the simple walk with no west step along the bottom row; its kernel xy - s(x + y)(1 + xy) is symmetric in x and y, and the unknowns are the bottom-row and left-column series.
3. **Row-to-row transfer.** Each step moves Y by one, so the walk is a matrix continued fraction over the rows, with the shift and truncation maps between rows of n - 1 and n contacts; along one axis this is the strip's Chebyshev structure (`REACH-HALVES-20261110-001A`, Theorem 3).
4. **Doubling.** The relation 1/r_2n(w) = 1/r_n(w^2) + w^4 asks for a map between the sides n and 2n; over GF(2) the free walk's A^4 is its A^2 at twice the scale.
