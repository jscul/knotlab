# Full reach at the sides that are not powers of two

Status: Proposition 5 proved by hand; its criterion and the census B2 are exact computations. Read by an independent referee
pass on 2026-11-10, whose findings are folded in. The registered target B1, full reach
at every side that is not a power of two from 8, is **not proved** for any infinite family; the census carries it to side 130.

Ticket `REACH-HALVES-20261110-001B`, 2026-11-10 (pre-registered in commit 03bd5937b, before the census ran).

## Standard statement

The walk A, the box, the rings and reading are as in `REACH-HALVES-20261110-001A`. **Full reach** at side n: every contact reads some
contact of every ring. A vector x is **cyclic** when x, xA, xA², … span the whole space of contacts.

**Proposition 5 (a cyclic contact in every ring suffices).** If every ring contains a contact d whose basis vector e_d is cyclic, full
reach holds. In particular, if the corner contact (0, 1) is cyclic, every contact reads the corner ring (0, 0), and by the quarter turn
every corner ring.

**Computed.**
- **The criterion (check 1).** Among sides 3 to 26 it holds exactly at 3, 5, 7, 9, 11, 13, 18, 19, 21, 23 and 25. It fails at 4, 6, 10,
  12, 14, 15, 17, 20, 22, 24 and 26, where full reach nevertheless holds, and at the failing sides 8 and 16; at 4, 8, 14, 16, 20 and 24 no
  basis vector is cyclic at all. So it is not the general mechanism. `FULL-REACH-PROOF-20261108-001A`'s Proposition 6 (a layer's
  polynomial irreducible of full degree, so that every nonzero vector of a layer generates that layer and every basis vector is
  cyclic) covers 3, 5, 7 and 11.
- **The census B2 (`research/REACH-HALVES-20261110-001/census.json`, REACH-HALVES-B2).** Every side from 3 to 130. At every side but
  8, 16, 32, 64 and 128 full reach is certified: every contact had met every ring by step 32 to 672 (an upper bound, since coverage is
  checked every 32 steps; 1,064 s for the whole census). The powers of two 4 to 128 were
  run over a whole period P = e(2n − 1) of the walk, with A^P = I checked, so their reach sets are exact: at 4 full reach holds; at 8, 16,
  32, 64 and 128 exactly n − 4 contacts miss a ring (4, 12, 28, 60, 124): the quarter-turn images of (X, X + 1), X = n + 2, n + 6, …,
  2n − 6, each missing exactly one corner ring and its two neighbours (recomputed from the census's ring lists by check 2), and 3n + 20
  contacts miss some contact (44, 68, 116, 212, 404). The frozen prediction holds at every side.

**What resists.** A proof at sides that are not powers of two. Reach there is generic: the strip already has the extra branches
λ = t + t⁻¹ + (ζ + ζ⁻¹)^(1/2), ζ^(k′) = 1, ζ ≠ 1, k′ the odd part of n (`REACH-HALVES-20261110-001A`, Theorem 3), the spectrum is not
even in the field of (2n − 1)-th roots of unity (`LINEAR-ROOTS-20261109-001`, computed at 3 to 20), and the cyclicity that would give full reach at once is not available at every
such side. A proof would need either control of the box's eigenvectors at every such side or a combinatorial certificate (an odd count at
a definite time) for every contact and ring; neither is in hand. The census certifies full reach early, within 4.4n to 6.4n steps at every
side from 20 to 130, which points to a short-time certificate but does not give one.

## Proof of Proposition 5

By Theorem 2 of `FULL-REACH-PROOF-20261108-001A`, A^k[c, d] = A^k[Dd, Dc], so c reads d exactly when Dd reads Dc. If e_(Dd) is cyclic,
the vectors e_(Dd)A^k span everything, so their supports cover every contact: Dd reads every contact, Dc among them, and c reads d.
D carries ring (i, j) onto ring (j, i) (it swaps (2i ± 1, 2j) with (2j, 2i ± 1)), so if every ring contains a contact with a cyclic basis
vector, then for every ring r the ring Dr contains such a contact Dd with d ∈ r, and every contact reads d. For the corner: (0, 1) and
D(0, 1) = (1, 0) form ring (0, 0), so a cyclic e_(0,1) gives the statement for ring (0, 0), and ρ, which commutes with A, carries it to the
other corners. ∎

## Checks

| # | Check | Result |
| --- | --- | --- |
| 0 | `FULL-REACH-PROOF-20261108-001A`'s manifest bound by hash | pass |
| 1 | The criterion at sides 3 to 26: where it holds, where no contact is cyclic, and full reach read at every side | pass |
| 2 | The census B2, sides 3 to 130, its file bound by hash, against its frozen prediction, the failing sets recomputed from its ring lists | pass |

## Nonclaims

- **B1 is not proved** for any infinite family of sides; full reach at the sides that are not powers of two is computed, to 130.
- **The census certifies, it does not explain**: a side's certificate is the list of times at which every contact met every ring.
