# Two separately revealed XORs of path products

2026-11-15 (Pacific). Goals G3 and G16.

## The question

Can arbitrary fixed XORs of the left and right private product lists, one per evaluator, beat the 512-case midpoint construction on 31 products, and can any choice of both masks yield polynomially many cases as the path grows?

## Prior work in the program

`scripts/track.py objects "affine proof cases opposed checksums intermediate prefix visibility" --until 2026-11-15 --exclude TWO-PRODUCT-SKETCHES-20261115-001 --limit 3`

`scripts/track.py objects "quadratic product reports adaptive affine query rank" --until 2026-11-15 --exclude TWO-PRODUCT-SKETCHES-20261115-001 --limit 3`

`scripts/track.py objects "tree leaves separate evaluators revealed product sums" --until 2026-11-15 --exclude TWO-PRODUCT-SKETCHES-20261115-001 --limit 3`

- `TERNARY-REPORT-JOINS-20261115-001` studied Decision and exact counting with affine constraints on products. Keep all input bits, the opposed checksums, separate exact affine-hull inferences and arbitrary mixed visible XOR questions fixed. Optimize the left and right masks independently.
- `AFFINE-FACTOR-RANK-20261115-001` studied Sharp fixed and adaptive affine partition counts. Keep all input bits, the opposed checksums, separate exact affine-hull inferences and arbitrary mixed visible XOR questions fixed. Optimize the left and right masks independently.

The predecessor proves the exact public-only bound and supplies a 512-leaf midpoint construction. Its private prefix result is an upper bound. It leaves open both optimality of that construction and whether a different fixed pair of one-bit summaries can suppress the exponential growth.

## Prior work outside the program

Cohen and Shinkar study inner product under DNF of parities (https://eccc.weizmann.ac.il/report/2014/099/). Direct Sums for Parity Decision Trees (https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CCC.2025.16) treats computing several outputs. Our terminal inference takes a separate exact affine hull for each quadratic evaluator, repeatedly, and intersects them under opposite total outputs. Verify the restricted-model arguments directly.

## Evidence and stopping rule

Begin with exact small path minima over both masks and arbitrary visible queries. Compare with the 31-product common midpoint and alternative masks. Seek an all-mask asymptotic lower bound, auditing restriction through repeated hull closure and branches with mixed inputs and outputs. Separate optimality for one mask, all masks, and the growing path. Stop after a verified lower bound or counterstrategy for polynomial growth plus a warranted finite assessment.
