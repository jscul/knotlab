# The top hole bit closes the decoder route

Status: Proved by hand; the identities and the cap are checked in `check.py`.

Ticket `KERNEL-FRAC-20261110-001A`, 2026-11-10. Found while reading conjecture C's failure (`KERNEL-FRAC-20261110-001B`), after the
frozen statement (`research/KERNEL-FRAC-20261110-001/kernel_statement.md`).

## Standard statement

- **LP_n, L_k, τ̃, K_k, Theorem (R)** as in `HOLE-SEP-20261110-001A`: n = 2^l holes, m = n + 1 pigeons with codes 0, …, n in l + 1 bits
  (bit l is the top bit), v = (n + 1)l + n(l + 1) variables.
- **Braun's criterion** (his Corollary 9.2) as used in `SEP-LEFT-20261110-001A`'s Theorem 2: a space U of polynomials of degree at most k
  separated at degree B = k(D + 1), D = max(2h + w, 4h + 1), gives 3S + |J| ≥ (dim U / C(v + k, k))·exp(hk²/(v + k)).

**Theorem.**
1. τ̃(g_h,l) = X_n,h for every hole h, and τ̃(g_h,l·g_h′,l) = X_n,h X_n,h′ ∈ Ideal_2 for h ≠ h′. Hence every row-linear monomial with top
   bits on two different hole rows lies in K_k, and so does their span K′_k.
2. Every subspace U of L_k with U ∩ K_k = {0} has dim U ≤ low_k, the number of row-linear monomials of degree at most k with at most one
   top hole bit.
3. **The cap.** For every k ≤ n/2 and every accuracy h with 2l·k(4h + 2) ≤ n + 1 (Theorem (R)'s condition at B = k(4h + 2)), the most
   Braun's criterion can certify through Theorem (R) is (low_k / C(v + k, k))·exp(hk²/(v + k)) ≤ 5.2. So the decoder route gives no
   lower bound for LP_n beyond a constant number of lines.
4. **Where it comes from.** The obstruction is the extra pigeon: n + 1 codes in l + 1 bits leave the top bit to one pigeon. With 2n
   pigeons, whose codes fill the l + 1 bits, no code bit belongs to fewer than n pigeons and part 1 has no analogue.

## Nearest known result

- **Braun's §9** remarks that the criterion needs a dense separated space; part 3 shows that the space the decoder can certify is
  exponentially thin in k/l for this encoding. **Classification.** New as far as found; elementary.

## Proof

**1.** τ̃(g_h,j) = Σ_y y_j X_y,h, and among the codes 0, …, n only n = 2^l has bit l set. X_n,h X_n,h′ is a row exclusion. A row-linear
monomial with top bits on rows h ≠ h′ decodes to a multiple of X_n,h X_n,h′, which lies in Ideal_k (check 1: every pair of holes, n = 4, 8,
16, 32). ∎

**2.** U ∩ K_k = {0} and K′_k ⊆ K_k give U ∩ K′_k = {0}, so dim U ≤ dim L_k − dim K′_k, which is low_k since monomials form a basis of L_k
and K′_k is spanned by the monomials it contains. ∎

**3.** Bound low_k by the multisets of size at most k from the v − n variables that are not top bits, plus those with one top bit:
low_k ≤ C(v − n + k, k) + n·C(v − n + k − 1, k − 1). Then
low_k / C(v + k, k) ≤ (1 + nk/v)·exp(−(k − 1)n/(v + k)),
using C(a + k, k)/C(b + k, k) ≤ ((a + k)/(b + k))^k for a ≤ b. Theorem (R)'s condition gives hk ≤ (n + 1)/(8l), so
hk²/(v + k) ≤ k(n + 1)/(8l·v) ≤ k/(15l²) for n ≥ 16, since v ≥ 2nl. With n/(v + k) ≥ 1/(2l + 3) for k ≤ n/2, the certified value is at
most (1 + k/(2l))·exp(1 − k(1/(2l + 3) − 1/(15l²))) ≤ e·max_y (1 + 4y)e^{−y} ≤ 5.2 for l ≥ 2. Check 2 evaluates the exact count for l ≤ 12
and the bound above to l = 30, k up to n/2 with the largest allowed h: the largest value is 1.04. ∎

**4.** For 2n pigeons the codes are all of {0, 1}^{l+1}, so each code bit is set for exactly n pigeons and τ̃ of a hole bit is a sum over
n cells of its column; a product over different holes is a sum over injective placements, not forced to zero. ∎ (That the 2n-pigeon
principle escapes the obstruction is all part 4 says; whether its decoder kernel is small is open.)

## Remarks

- **This closes the route, not the question.** Monomials with two top hole bits are not consequences of LP_n: `SEP-LEFT-20261110-001B`
  found L_k fully separated at every degree read. The decoder, which empties every hole no pigeon names, makes "the top bit is set" mean
  "pigeon n sits here", which holds for one hole at most; LP_n itself allows any number of holes to carry codes with the top bit.
- **The way around.** The left-pigeon principle with 2n pigeons contains the clauses of the one with n + 1 (the first n + 1 pigeons'
  clauses, with the same hole rows), so a Res(⊕) lower bound for it is one for LP_n.

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | Dependencies bound by hash | pass |
| 1 | τ̃(g_h,l) = X_n,h and every pair of top bits decodes into the ideal, n = 4, 8, 16, 32 | pass |
| 2 | The cap, l = 2 to 30, k up to n/2, the largest allowed h | pass: at most 1.04 |

## Nonclaims

- **No lower bound** for LP_n or the 2n-pigeon principle is claimed.
- **Only the route through Theorem (R)** is closed; Braun's criterion with spaces that Theorem (R) does not certify is not addressed.
