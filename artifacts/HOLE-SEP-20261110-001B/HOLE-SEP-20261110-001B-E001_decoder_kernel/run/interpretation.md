# Interpretation of HOLE-SEP-20261110-001B-E001

Exploratory and exact, pre-registered (frozen statement 0596397e3, contract 1115cfa1e, before any kernel was computed). The run took
31 seconds.

| n | variables v | k | dim L_k | dim K_k | kernel fraction | (l + 1)² k / v |
| --- | --- | --- | --- | --- | --- | --- |
| 4 | 22 | 1 | 23 | 9 | 0.39 | 0.41 |
| 4 | 22 | 2 | 237 | 173 | 0.73 | 0.82 |
| 4 | 22 | 3 | 1,445 | 1,389 | 0.96 | 1.23 |
| 8 | 59 | 1 | 60 | 16 | 0.27 | 0.27 |
| 8 | 59 | 2 | 1,696 | 839 | 0.49 | 0.54 |
| 8 | 59 | 3 | 30,012 | 20,378 | 0.68 | 0.81 |
| 16 | 148 | 1 | 149 | 25 | 0.17 | 0.17 |
| 16 | 148 | 2 | 10,765 | 3,423 | 0.32 | 0.34 |

- **P1 holds:** dim K_1 = (l + 1)² at n = 4, 8 and 16, and the (l + 1)² inverse-counting identities lie in K_1: they span it.
- **P2 fails:** the kernel fraction falls with n (0.73, 0.49, 0.32 at k = 2; 0.96, 0.68 at k = 3) but is 32% at n = 16, k = 2, not below
  1%.
- **Rule (b) is triggered** (above 10% at n = 16, k = 2). The family it asks to name, found after the run
  (`research/HOLE-SEP-20261110-001/killed_family.py`): the inverse-counting identities κ_{a,j} times row-linear monomials. The products
  whose rows do not collide lie in K_2 and span 134 of its 173 dimensions at n = 4, 614 of 839 at n = 8 and 2,324 of 3,423 at n = 16.
  Adding the pairs whose colliding rows cancel (κ_{a,j}·g_h,j′ + κ_{a,j′}·g_h,j, and κ_{h_t,j}·f_y,s + κ_{h_s,j}·f_y,t) gives 142, 701
  and 2,822 (`killed_family_pairs.py`); the remaining 31, 138 and 601 dimensions are not identified (products of two κ's, about
  (l + 1)⁴ of them, are the natural candidates, not checked). Throughout, the fraction tracks (l + 1)² k / v, the share of L_k made of
  κ's times L_{k−1}.

## The rule's reading does not follow

The frozen rule said that a kernel above 10% at n = 16, k = 2 means "the route through τ̃ cannot give a dense separated space". It
does not mean that. A complement U of K_k has density (1 − fraction) times L_k's, so Theorem 2 of `SEP-LEFT-20261110-001A` loses only the
factor 1 − fraction; any fraction bounded away from 1 costs a constant. The threshold was set without that count, and the readings fit
(l + 1)² k / v, which at the k the theorem needs, about n/(24 l²), is about 1/(48 l). The epic stops here as its rule says; the
corrected question, whether the kernel fraction stays below 1 − e^{−k²/(6n)} at that k, is recorded as the next direction, and the
rule's reading is logged in `docs/CORRECTIONS.md`.
