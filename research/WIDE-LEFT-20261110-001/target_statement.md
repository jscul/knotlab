# Target, spare-row lemma, predictions, density count and stop rule (frozen before the work)

Epic `WIDE-LEFT-20261110-001`, sub-goal B114, 2026-11-10. Written and committed after `novelty_and_transfer.md` and before anything below
was computed or proved. This is the last epic on the decoder route (the coordinator, 2026-11-10). Nothing in it is a lower bound unless
proved, and nothing transfers to the knot sphere's count.

## Notation

WLP_n = WLP_{2n} of `novelty_and_transfer.md`: n = 2^l holes, m = 2n pigeons, pigeon rows f_x of l bits, hole rows g_h of l + 1 bits
(every code names a pigeon), v = 2nl + n(l + 1) variables, the clauses "f_x ≠ h or g_h,j = x_j" (|J| = 2n²(l + 1)). L_k, the reduced
decoder τ̃ and the kernel K_k as in `HOLE-SEP-20261110-001A`, with Braun's unary system F^fun_{2n,n}.

## The target

**(W)** There is c > 0 such that every dag-like Res(⊕) refutation of WLP_n has at least exp(c·n/l⁵) − poly(n) lines, and so, by
`novelty_and_transfer.md`, does every refutation of LP_{n+1}.

## The steps

1. **(R′) Reduction.** Theorem (R) of `HOLE-SEP-20261110-001A` for WLP_n: if 2lB − 1 ≤ n, B ≥ 2 and k ≤ B, a row-linear polynomial derived
   from WLP_n in PC degree B lies in K_k. (The same proof: Lemma 1's substitution, Braun's decoder transfer and stability, which allow
   any number of pigeons.)
2. **(S) The spare-row lemma.** Let E be a union of 2k disjoint hole stars {q, q + e_0, …, q + e_{l−1}} and P a union of k disjoint pigeon
   stars {p, p + e_0, …, p + e_l} (codes as vectors, + bitwise). Let U_0 be the span of the row-linear monomials of degree at most k
   whose rows avoid E and P. If 2k(l + 1) ≤ n, k(l + 2) ≤ 2n and n ≥ 2k − 1, then U_0 ∩ K_k = {0}.
   *Planned proof:* for p ∈ U_0 with a top monomial M_0 (pigeon pairs (x, t_x), hole pairs (h, j_h)), a cube with one coordinate per pair:
   a pigeon coordinate places x in one of two spare holes of a star that differ in bit t_x; a hole coordinate places one of two spare
   pigeons differing in bit j_h in h and the other in a spare hole. Braun's cube-drop lemma maps Ideal_k into the residual unary ideal of
   degree k − t; the cube sends τ̃(p) to M_0's coefficient, 1; a normalized residual functional (Braun's moments) separates.
3. **(D) The density count.** With U = U_0 in Braun's Corollary 9.2:
   log(3S + |J|) ≥ log dim U_0 − log C(v + k, k) + hk²/(v + k),
   at **k = ⌊n/(64 l³)⌋** and **h = the largest integer with 2l·k(4h + 2) ≤ n + 1** (so B = k(4h + 2) meets (R′), and D = 4h + 1 ≥ 2h + l + 1).
   Predicted: the right side is at least c·n/l⁵ for all l from some l₀ on (the hand count gives about k/(96 l²) = n/(6144 l⁵)).

## Predictions for the checks (exact GF(2) linear algebra)

- **Q1.** dim(U_0 ∩ K_k) = 0 at (n, k) = (4, 1), (8, 1) and (16, 2), with E and P the smallest unions of stars the lemma's cube needs
  for degree k (at n = 4, 8 one hole star and one pigeon star; at n = 16, two of each). (At n = 8, k = 2 the stars would take every
  hole, so that entry is not read.)
- **Q2.** The cube identities: for every pair in Q1's entries, the cube sends each monomial's image to 0 unless it holds every selected
  pair, and the selected monomial's to 1.
- **Q3 (context, not a test of the lemma).** WLP_n's whole kernel fraction at (4, 2) and (8, 2): no top-bit family, so a fraction near
  the inverse-counting share (l + 1)² k / v, about 0.64 and 0.40, below LP_{n+1}'s 0.73 and 0.49.
- **Q4.** (D) evaluated for l = 20 to 60 is positive and its ratio to n/l⁵ is bounded below.

## Stop rule (one epic)

Stop at the first of:
- **(a) A proved bound.** (R′), (S) and (D) proved: state (W) as a theorem for WLP_n and LP_{n+1}, with novelty classified.
- **(b) A proved reduction to one named lemma.** If one step resists, state the bound conditional on that step, named exactly.
- **(c) A refutation of the lemma.** A nonzero element of U_0 ∩ K_k at a Q1 entry, or a failed Q2 identity: (S) is false as stated.
- **(d) Neither.** Stop naming the failing step.

After (b), (c) or (d) the decoder route is finished in this program: the line moves to B101 or B82, or the thread moves to another line,
as the coordinator directed.
