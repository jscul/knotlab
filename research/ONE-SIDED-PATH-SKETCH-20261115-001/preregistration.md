# One exposed quadratic sum on the 17-product path

2026-11-15 (Pacific). Goals G3 and G16.

## The question

On 17 adjacent Boolean products does a single evaluator exposing the XOR of the eight even-numbered products permit a tree with fewer than 512 leaves? Ascertain the actual case complexity, then test the rank-nine one-sided generalization if 512 is sharp or the lift of a cheaper tree to 31 products if it improves.

## Prior work in the program

`scripts/track.py objects "one-sided quadratic sketch affine proofs path even product" --until 2026-11-15 --exclude ONE-SIDED-PATH-SKETCH-20261115-001 --limit 3`

`scripts/track.py objects "first effective inference honest assignment nine rank" --until 2026-11-15 --exclude ONE-SIDED-PATH-SKETCH-20261115-001 --limit 3`

`scripts/track.py objects "asymmetric fixed product masks pair embedding 31 path" --until 2026-11-15 --exclude ONE-SIDED-PATH-SKETCH-20261115-001 --limit 3`

- `TWO-PRODUCT-SKETCHES-20261115-001` studied Optimal exponential growth with one fixed observation on each evaluator. Use the same separate whole-evaluator affine hulls to saturation, opposed totals and arbitrary mixed adaptive affine questions. Distinguish the one-sided restriction, arbitrary quadratic observations at half-rank nine, and the longer original instance.
- `TERNARY-REPORT-JOINS-20261115-001` studied Decision and exact counting with affine constraints on products. Use the same separate whole-evaluator affine hulls to saturation, opposed totals and arbitrary mixed adaptive affine questions. Distinguish the one-sided restriction, arbitrary quadratic observations at half-rank nine, and the longer original instance.

The predecessor establishes a one-sided honest-mass lower bound of 342 and an affine-input upper bound of 512 at half-rank nine. It determines the 31-edge common-mask optimum and reduces any improvement to a particular rank-seven component with a one-sided residual. Its elementary independent-pair lower bound assumes the sketch selects products in the same diagonal basis. The proposed even-edge mask has half-rank eight and is a strict triangular pencil with the total, so the diagonal formula needs a new argument.

## Prior work outside the program

Cohen and Shinkar study DNF of parities of inner product (https://eccc.weizmann.ac.il/report/2014/099/). Parity decision-tree Fourier methods and direct-sum results concern different tasks (https://doi.org/10.4230/LIPIcs.CCC.2025.16). Assess the charged leaf count with free alternating local hull deductions directly. An affine restriction, Fourier bias or an ordinary parity-tree result requires proof of transfer to this rule.

## Evidence and stopping rule

Number edges from one, hide every individual product, and set the one-sided extra bit to the even-edge sum. Allow mixed queries of the sketch, total and all raw inputs. Start with low-dimensional analogues, seek a uniform proof or a checked tree with fewer leaves, and stress-test short exceptional branches and complementary children. Condition further work on the 17-edge outcome. If the broad extension remains open, give explicit surviving bounds or the first genuine obstruction. Only a refutation on the full 31-edge instance or a uniform reduction in the right direction can settle its unrestricted optimum.
