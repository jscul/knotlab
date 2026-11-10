# The failure of full reach at every power of two from 8

Status: Partial (pre-registered 2026-11-10, before the proof attempt).

Ticket `REACH-HALVES-20261110-001A`, epic `REACH-HALVES-20261110-001` (B59 restarted at the coordinator's pick, as the full-reach
theorem itself).

## What is registered

Doubled coordinates of `FULL-REACH-PROOF-20261108-001A`: the contacts are the points (X, Y) of [0, N]², N = 2n − 2, with X + Y odd;
an h (X odd) reads (X ± 1, Y ± 1) with equal signs, a v (X even) reads (X ± 1, Y ∓ 1), reads leaving the box die, and A[c, d] = 1
when c reads d, over GF(2). Ring (i, j) holds the contacts (2i ± 1, 2j) and (2i, 2j ± 1) inside the box.

**Target A1.** At every n = 2^m ≥ 8, the contact c* = (n + 2, n + 3) never reads (0, 1) or (1, 0), the two contacts of the corner
ring (0, 0). Full reach therefore fails at every power of two from 8.

**On the way, A0 (a reduction).** A1 follows from one statement: the number of walks of each length from (1, 0) to
d* = (n + 3, n + 2) is even. On the h contacts h(i, j) = (2i + 1, 2j) this is a statement about a grid walk: on [0, n − 2] × [0, n − 1]
a walker moves to a 4-neighbour, except that on the bottom row it may not move left and on the top row it may not move right; the
walks from (0, 0) to (n/2 + 1, n/2 + 1) are even in number at every length.

**Secondary targets.**
- **A2, the corner return law.** Σ_k A^k[(0, 1), (0, 1)] w^k = 1/(1 + L(w⁴)), L(z) = z + z² + z⁴ + ⋯ + z^n the trace polynomial of
  GF(2n); equivalently the corner returns at time 4j exactly when j + 1 is a power of two modulo 2n − 1.
- **A3, the failing set.** Exactly the n − 4 contacts ρ^i(X, X + 1), X = n + 2, n + 6, …, 2n − 6 (ρ the quarter turn), miss a ring,
  each exactly the three rings of one corner.

**Found before registration (computed, this thread).** A1 and A3 at 8, 16, 32 and 64; A2 at 4, 8, 16 and 32; the grid statement at
8, 16 and 32, where the corner reaches every point of the grid except (i, i) for odd i from n/2 + 1 to n − 3. In the quadrant and in
both half-strips (one far wall removed) the corner does reach d*, so all four walls take part; in both half-strips the corner's return
series is the quadrant's, Σ_j w^(2^(j+2)) for the first return, which is the Catalan series in w⁴ mod 2.

## Criteria, frozen

- **Proved:** a proof by hand for every m ≥ 3, each of its formulas checked exactly at sides 8 to 64, read by an independent referee
  pass before publication.
- **Refuted:** a power of two where c* reads the corner ring.
- **Obstructed:** the attempt names the lemma that would finish A1, checks it exactly at sides 8 to 64, and says why it was not
  proved.

## Planned checks

- Every formula of the proof at sides 8 to 64, and the grid statement against the box walk.
- A2 and A3 at 64 and 128 in the stress test.
