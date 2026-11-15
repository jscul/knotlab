# Join four surviving reports and test growing non-affine checks

2026-11-15 (Pacific). Goals G3 and G16.

## The question

Can the unnamed degree-two calculus derive a reusable four-report summary from two actual strict ternary parity checks? For growing equally sized connected systems of AND checks plus a parity condition, do Gaussian elimination and boundedly many affine case splits still suffice, and which stronger operations change the answer?

## Prior work in the program

`scripts/track.py objects "four-report guarded parity proofs strict ternary join quadratic checks" --until 2026-11-15 --exclude TERNARY-REPORT-JOINS-20261115-001 --limit 3`

`scripts/track.py objects "connected product conjunction affine cover rank path vertex cover" --until 2026-11-15 --exclude TERNARY-REPORT-JOINS-20261115-001 --limit 3`

`scripts/track.py objects "Boolean affine hull local propagation quadratic equal checksums" --until 2026-11-15 --exclude TERNARY-REPORT-JOINS-20261115-001 --limit 3`

- `SHARED-REPORT-CANCELLATION-20261115-001` studied Decision and original-input certificates for all supplied pair-check networks. Use identical strict inputs within each proof comparison. Match the number of nonlinear pair products and input bits in two overlap patterns. Distinguish an exact relation cover, deciding one contradiction, projected witnesses, and access to intermediate product values.
- `QUADRATIC-ROUTE-TRANSFER-20261115-001` studied Random-input route proof bounds with formal degree-two multiplication. Use identical strict inputs within each proof comparison. Match the number of nonlinear pair products and input bits in two overlap patterns. Distinguish an exact relation cover, deciding one contradiction, projected witnesses, and access to intermediate product values.
- `AFFINE-FACTOR-RANK-20261115-001` studied Exact affine restriction of all sequentially named products. Use identical strict inputs within each proof comparison. Match the number of nonlinear pair products and input bits in two overlap patterns. Distinguish an exact relation cover, deciding one contradiction, projected witnesses, and access to intermediate product values.
- `GROUPED-PRODUCT-REPLAY-20261115-001` studied Carrying pair XOR as an actual quadratic beside a regrouped AND. Use identical strict inputs within each proof comparison. Match the number of nonlinear pair products and input bits in two overlap patterns. Distinguish an exact relation cover, deciding one contradiction, projected witnesses, and access to intermediate product values.
- `COMMON-FOLD-20261112-001` studied Forced fraction of a finite uniform-growth base from a conditioned pair, split by ties, propagation and search. Use identical strict inputs within each proof comparison. Match the number of nonlinear pair products and input bits in two overlap patterns. Distinguish an exact relation cover, deciding one contradiction, projected witnesses, and access to intermediate product values.

The signed pair-cycle study supplies checked primitive rules, four selector-guarded lines for two reports, and the six-report four-check test with no two-check sum of weight below four. It also proves simultaneous report realization. Neither a four-report source deduction nor the effect of interacting non-affine checks on a particular inconsistent instance was decided there. Product and rank-transfer studies distinguish conditioning on named values from conditioning on input bits. Earlier corrections require actual derived premises, written operands and multiset occurrences to survive every claimed replay.

## Prior work outside the program

Dechter's Bucket Elimination (https://ics.uci.edu/~dechter/publications/r76A.pdf) covers bounded-width variable elimination. Binary quadratic normal form and affine restrictions are classical; the inner-product comparison has appeared in parity-query work (https://eccc.weizmann.ac.il/report/2014/099/), and Mirwald and Schnorr study matrix rank under a circuit measure (https://doi.org/10.1016/0304-3975(92)90235-8). Use those sources as background. The source deductions, full versus visible reports, saturating hull oracle and exact decision-model controls here require direct proofs.

## Evidence and stopping rule

Freeze the four check supports 012,034,135,245, signs 0,0,0,1, and the predecessor's six raw report functions. Validate all four-survivor masks, source ancestry, full strict refutation and changed-charge controls. For non-affine checks use m original pair products on m+1 inputs on a common-center star and a path; preserve supports and change only output parity for matched SAT/UNSAT. Test both exact descriptions and a particular double-evaluator contradiction allowing all affine queries on source inputs and the two checksums, then expose private products, group the source constraints, or retain quadratic equations. Stop at a checked summary or failing inference plus a sound uniform split bound or surviving shortcut, without promoting these proof or representation models to all SAT algorithms.
