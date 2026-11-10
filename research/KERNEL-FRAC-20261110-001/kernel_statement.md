# The kernel statement, conjecture and stop rule (frozen before the work)

Epic `KERNEL-FRAC-20261110-001`, sub-goal B107, 2026-11-10. Written and committed before anything below was computed. Scope: the binary
left-pigeon principle LP_n only. Nothing here transfers to the knot sphere's count (`HOLE-SEP-20261110-001`'s note says why), and
nothing is called a lower bound unless (T) below is proved.

## Notation

As in `HOLE-SEP-20261110-001A`: n = 2^l holes, m = n + 1 pigeons, v = (n + 1)l + n(l + 1) variables, L_k the row-linear space,
τ̃ the reduced decoder, K_k = {p ∈ L_k : τ̃(p) ∈ Ideal_k(F^fun_{m,n})}, and the share φ_k = dim K_k / dim L_k. The inverse-counting
identities are κ_{a,j} = Σ_h a(h)·g_h,j + Σ_x x_j·a(f_x) for a = 1 or a = h_t (t < l) and j ≤ l.

## (1) The exact statement

- **The degree.** k*(n) = ⌊(n + 1) / (2l(12l + 2))⌋, the largest k for which B = k(12l + 2), the degree Braun's criterion uses (h = 3l,
  D = 12l + 1), meets Theorem (R)'s condition 2lB − 1 ≤ n.
- **What the bound needs, written out.** Take U a complement of K_k in L_k. By Theorem (R) U is separated at degree B, and Theorem 2 of
  `SEP-LEFT-20261110-001A` with U in place of L_k gives, for l ≥ 4 and k ≤ n/2,
  3S + n(n + 1)(l + 1) ≥ (1 − φ_k)·exp(k²/(3n) − 2).
  The share enters only through the factor 1 − φ_k. **A kernel share bounded away from 1, whatever its size, costs a constant factor
  and does not threaten the bound.** Only a share within exp(−k²/(6n)) of 1 does.
- **(T), the target.** For all large n: log(1/(1 − φ_{k*})) ≤ k*²/(6n). Then 3S + n(n + 1)(l + 1) ≥ exp(k*²/(6n) − 2), which is
  exp(Ω(n / log⁴ n)): every dag-like Res(⊕) refutation of LP_n has superpolynomial size. (The bound takes hold only at very large n:
  k* ≥ 1 needs n ≥ 4096.)

## (2) The conjecture and the predicted dimensions

- **Conjecture C.** K_k = I_k ∩ L_k, where I_k is the span of the products κ_{a,j}·M over multilinear monomials M in the pigeon and
  hole bits of degree at most k − 1 (multilinearized). The inclusion I_k ∩ L_k ⊆ K_k holds by construction (τ̃ extends to all
  multilinear polynomials, sends each κ into Ideal_1, and Ideal_1 times degree k − 1 lies in Ideal_k).
- **Predicted dimensions** (dim I_k ∩ L_k = dim K_k at each entry; the kernel side is already known except at (4, 4)):

| (n, k) | dim L_k | dim K_k known | prediction for dim I_k ∩ L_k |
| --- | --- | --- | --- |
| (4, 2) | 237 | 173 | 173 |
| (8, 2) | 1,696 | 839 | 839 |
| (16, 2) | 10,765 | 3,423 | 3,423 |
| (32, 2) | 63,094 | 12,287 | 12,287 |
| (4, 3) | 1,445 | 1,389 | 1,389 |
| (8, 3) | 30,012 | 20,378 | 20,378 |
| (4, 4) | 5,806 | not read | equal to dim K_4, expected between 5,700 and 5,806 (the share saturates at n = 4) |

  Larger entries (k = 3 at n = 16, 502,365 monomials; k = 4 at n = 8, 372,634) do not fit this pure-Python elimination and are not in
  the roster.

## (3) Stop rule (one epic)

Stop at the first of:
- **(a) A dimension proof.** (T) proved for all large n: then, and only then, the epic states a dag-like Res(⊕) lower bound for LP_n.
- **(b) A family whose share nears 1.** A proved family of kernel elements whose share at k* is at least 1 − exp(−k*²/(6n)) for
  infinitely many n: the route through τ̃ is closed.
- **(c) A kernel element outside I_k ∩ L_k** at any entry read: this closes conjecture C, **not the route**, since the route needs only
  (T). The epic then continues toward (a) or (b) within its effort and, if neither is reached, stops naming the step a proof of (T) lacks.
- **(d) No (a), (b) or (c).** If C holds at every entry read but (T) is not proved, stop naming that step.
