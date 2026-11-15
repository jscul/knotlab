# Regroup an AND proof and carry its pair parity directly

2026-11-15 (Pacific). Goals G3 and G16.

## The question

How does regrouping the same AND affect an actual checked quadratic proof when the suffix uses the final output, the XOR of the pair products, or a fresh bit multiplied by that XOR? Give proof-size bounds or the first real degree obstruction.

## Prior work in the program

`scripts/track.py objects "proof regroup associative product root same named AND" --until 2026-11-15 --exclude GROUPED-PRODUCT-REPLAY-20261115-001 --limit 3`

`scripts/track.py objects "formal quadratic XOR pair products direct unnamed aggregate" --until 2026-11-15 --exclude GROUPED-PRODUCT-REPLAY-20261115-001 --limit 3`

`scripts/track.py objects "affine checked proof degree two fresh bit restriction" --until 2026-11-15 --exclude GROUPED-PRODUCT-REPLAY-20261115-001 --limit 3`

- `PRODUCT-NAME-TRANSFER-20261115-001` studied Whole-proof route transport with sequentially named affine products. Use the same refutation with the same final conjunction, premises, degree and pair-parity data where applicable. Compare exact verified deductions, scope and explicit proof size, including certificate inputs.
- `QUADRATIC-ROUTE-TRANSFER-20261115-001` studied Signed substitution of syntactic quadratic polynomial-resolution DAGs. Use the same refutation with the same final conjunction, premises, degree and pair-parity data where applicable. Compare exact verified deductions, scope and explicit proof size, including certificate inputs.
- `AFFINE-FACTOR-RANK-20261115-001` studied Rank-controlled elimination of reused product names. Use the same refutation with the same final conjunction, premises, degree and pair-parity data where applicable. Compare exact verified deductions, scope and explicit proof size, including certificate inputs.

The affine-rank study fixes controls until each supplied name is affine and identified the balanced four-input five-part example. The named-substitution study permits charged product names, formal multipliers and reused ordinary deductions. Neither establishes safe replacement of a subproof by a different AND grouping while representing a nonlinear aggregate of the original intermediate products.

## Prior work outside the program

The bounded-degree polynomial resolution calculus is standard: The original paper studies disjunctions of bounded-degree equations (https://eccc.weizmann.ac.il/report/2020/034/). Hrubeš and Tzameret prove balancing results for a different system of arithmetic-circuit identities (https://arxiv.org/abs/1112.6265). Their results are background. Here the finite-field derivations are built and checked directly in the previously specified named and unnamed multiset proof kernels.

## Evidence and stopping rule

First replace balanced ANDs by a chain and verify the same continuation and premises. Then export the pair parity as an ordinary quadratic, including its Boolean choice and nontrivial consequence in a contradiction. Audit all written expressions, extension factors and cross-boundary parents. Finally restrict a fresh bit in one common retained proof, reconstruct genuine input axioms on each case, remove the product and join the branches to the empty conclusion. Compare the next unrepaired use, exact Boolean functions and false alternative explanations. Keep the cost of transporting a supplied certificate distinct from SAT decision time.
