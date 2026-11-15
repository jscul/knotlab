# Two separately revealed XORs of path products

Status: Proved

## Accepted conclusions

- The minima over both fixed masks and all adaptive visible affine queries are 2,2,4,4,6,6,8,8 leaves for one through eight path products. Exactly 92, 72 and 860 ordered five-product pairs require six, seven and eight leaves, and a six-product off-center split beats the literal midpoint six to eight. [A, candidate-local-delta](../../TWO-PRODUCT-SKETCHES-20261115-001A/TWO-PRODUCT-SKETCHES-20261115-001A-P001_small_minimax/proof.md)
- Arbitrary separate extra product XORs leave optimal case count of order two to one quarter of the number of path products. Allowing more XORs gives a polynomial case bound exactly at the order of m/log m bits on each side when their choices can be optimized. For 31 products each rank-seven component in a sub-512 candidate must split off independently from the total. [B, candidate-local-delta](../../TWO-PRODUCT-SKETCHES-20261115-001B/TWO-PRODUCT-SKETCHES-20261115-001B-P001_uniform_lower/proof.md)
- On 31 adjacent products the common midpoint requires exactly 512 leaves and depth nine under arbitrary adaptive visible affine questions, and 512 is the optimum across all common masks. A rank criterion gives the same lower bound when all four partial checksums have half-rank at least eight, even for unequal choices. [C, candidate-local-delta](../../TWO-PRODUCT-SKETCHES-20261115-001C/TWO-PRODUCT-SKETCHES-20261115-001C-P001_sketch_strategies/proof.md)

The synthesis binds the accepted conclusions and the decision note. The scientific arguments and independent checks are in the linked proof records.
