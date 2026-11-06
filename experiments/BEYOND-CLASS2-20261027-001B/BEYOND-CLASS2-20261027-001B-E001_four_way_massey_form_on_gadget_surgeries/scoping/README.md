# Scoping before the contract (disclosed)

Everything below was run before `contract.json` was frozen. The scripts are kept as run; they import scratch copies of the
modules that became `mlib.py`, `bm.py` and `lp.py`.

## Earlier in the epic (before this experiment was designed)

Column-space tests of the measured four-way form against the Milnor tensor contracted with bundle functionals. These were
run with the BCH group of ticket A on cp_lib's Wirtinger presentations: cabled `P4` on sums of `4_1` at p = 5 and of `5_2` at
p = 7. The column spaces were equal. The random-tensor and permuted-leaf controls failed. The base form was zero on these sums.

## For this experiment

| script | what it computed | outcome |
| --- | --- | --- |
| `conj2.py` | two cabled `P4` insertions on six summands of `4_1` (p = 5), column-space test | sum of the two tensors matches (ranks 6, 6, 6); difference and each single term do not |
| `cable_check2.py` | Artin action of the 2-cable of `P4` versus substitution of bundle products into the geometric conjugators | equal for bundle product x_{2k+1} x_{2k}; conjugators have zero degree 1 and 2 Magnus parts |
| `lp_test1.py` | level presentations of 4_1, T(2,5), T(2,5)#T(2,5) at p = 5: is y(s) = (J s_{l+1}) in the left kernel? | yes for y = J s and y = J^T s; left kernel = y(Z1) plus one vector with surgery component |
| `lp_test2.py` (`lp_test2.log`) | level model: full tables of the base form on 4_1 x1..3 and T(2,5) x1..3 (p = 5); exact change of the form for `P4` at (0,0), (4,1), (6,0) on 4_1 x4 | base form zero; change = 3 x rule (3 = -2 mod 5) on all entries: this fixed KAPPA (level convention -2) |
| `bm_test1.py` | braid model on 4_1 x4 (p = 5), 64 samples: base form; `P4` at (0,0), (4,1), (6,0), (9,1) | base form zero; Q / rule = 2 on all nonzero samples: KAPPA = 2 in the braid convention |
| `gadget.py` | gadgets K2, P3, digon, K3, star at p = 5 and 7, 48 samples each | Q = KAPPA x sum of edge tensors on every sample; closed-form leaves hold; dropping one edge's tensor fails |
| `dc_scope.py` | ticket A's direct layered count on S^3_2(T(2,5)) and S^3_2(4_1) at p = 5; fix_f1 completions on 4_1 x4 + `P4` (0,0), 12 samples | 390625 = p^8 for both; lift <=> Q(c; .) = 0 on 12/12 (3 lift) |
| `fweight.py`, `fpattern.py` (`fweight_p5.log`) | the gadget's edge weight f(d) (for ticket C, not a prediction here) | p = 5: values p^12, p^6 * 1225, p^6 * 361; p = 7: p^12, p^6 * 4753, p^6 * 1009 |
| `geom.log` | construction of every fixture of the contract (words, closures, crossings), no forms or counts | all closures are knots |

## Confirmatory under the contract

The following were never computed before the contract:
- primes 11 and 13;
- sums of `5_2`, T(2,7), T(2,11) and T(2,13), apart from the earlier column-space test on `5_2` sums;
- the second pure braid `P4B` = [[A23, A34], A12];
- mixed `P4` + `P4B` insertions and doubled `P4` insertions;
- under-dragged and shifted insertions;
- the C4 gadget and every gadget at p = 11;
- level-model tables for `P4B`;
- the 40-sample lifting test with structured samples;
- direct counts of S^3_2(T(2,5)#T(2,5)) and of sector 0.

The scoped fixtures are rerun as regression.
