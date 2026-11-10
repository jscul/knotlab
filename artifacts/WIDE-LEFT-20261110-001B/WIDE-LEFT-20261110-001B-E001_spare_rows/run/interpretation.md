# Interpretation of WIDE-LEFT-20261110-001B-E001

Exploratory and exact, pre-registered (frozen target ca1f7e64e, contract 2887bc48f, before any check was computed).

## Two disclosed changes to the frozen run

- **Q2 at (16, 2) sampled.** run.py checked every top monomial of U_0 against every monomial; at (16, 2) that is 5,925 × 5,926 cube
  evaluations, about 39 hours. It was stopped there after Q1 had finished at all three entries and Q2 at (4, 1) and (8, 1). finish.py
  checks 60 top monomials drawn with a fixed seed (30 of degree 2, 30 of degree 1) against every monomial, with run.py's functions.
- **Q4 bounded beyond l = 32.** run.py summed e_k term by term, which for k up to 10^17 does not finish. finish.py sums term by term for
  l ≤ 32 and uses the sequential lower bound of `WIDE-LEFT-20261110-001A`'s Lemma 3 beyond, so Q4 is checked conservatively there.

## Readings

| Check | Entry | Result |
| --- | --- | --- |
| Q1: dim(U_0 ∩ K_k) | (4, 1): dim U_0 = 12 | 0 |
| Q1 | (8, 1): dim U_0 = 50 | 0 |
| Q1 | (16, 2): dim U_0 = 5,926 | 0 |
| Q2: the cube isolates each top monomial | (4, 1) all 11, (8, 1) all 49, (16, 2) 60 sampled | every identity holds |
| Q3: WLP_n's whole kernel fraction | (4, 2), (8, 2) | 0.625 and 0.362 (predicted about 0.64 and 0.40; LP_{n+1}'s 0.73 and 0.49) |
| Q4: the density count | l = 20 to 60 | positive from l = 20; ratio to n/l⁵ at least 0.000135 for l ≥ 40 |

All four predictions hold. The whole kernel is far from zero (Q3) while the spare-row space meets it in zero (Q1), which is what Lemma 2 of
ticket A says: every kernel element found uses a spare row or the full set of holes.
