# Interpretation of KERNEL-FRAC-20261110-001B-E001

Exploratory and exact, pre-registered (frozen statement 1f78913cf, contract 362003103). The run took 380 seconds.

| (n, k) | dim L_k | dim K_k | dim I_k ∩ L_k | conjecture C |
| --- | --- | --- | --- | --- |
| (4, 2) | 237 | 173 | 146 | fails |
| (8, 2) | 1,696 | 839 | 752 | fails |
| (16, 2) | 10,765 | 3,423 | 3,144 | fails |
| (32, 2) | 63,094 | 12,287 | 11,422 | fails |
| (4, 3) | 1,445 | 1,389 | 1,079 | fails |
| (8, 3) | 30,012 | 20,378 | 16,848 | fails |
| (4, 4) | 5,806 | 5,805 | 4,780 | fails |

- **Conjecture C fails at every entry:** the kernel is larger than the row-linear part of the identities' ideal, already at k = 2. By
  stop rule (c) this closes C, not the route.
- **The (4, 4) expectation holds:** dim K_4 = 5,805, inside [5,700, 5,806].

## What the extra kernel is (found after the run)

Only pigeon n = 100…0 has the top code bit, so the top bit of a hole row decodes to the single cell X_n,h, and two top bits on
different holes multiply to zero (`research/KERNEL-FRAC-20261110-001/top_bit_family.py`). Adding to the ideal every monomial whose
decoded image is zero raises dim (I_2 + Z_2) ∩ L_2 to 157, 797 and 3,313 at n = 4, 8, 16, against 173, 839 and 3,423; the rest includes
relations such as g_h,l·f_n,t = h_t·g_h,l (pigeon n's row read in the hole it sits in), not enumerated here. The monomials with two top
hole bits are what closes the route: their share of L_k at the needed degree exceeds the frozen threshold at every l from 14 to 22
(0.0035 at l = 14 up to 0.997 at l = 22), and ticket A proves that through the decoder Braun's criterion certifies at most a constant
for every degree and accuracy.
