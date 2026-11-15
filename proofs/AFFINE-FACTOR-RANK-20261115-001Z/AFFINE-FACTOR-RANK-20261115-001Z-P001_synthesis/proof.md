# How many independent affine factors a named proof must fix

Status: Proved

## Accepted conclusions

- A supplied rank-r span containing one original factor, up to constants, at every declaration eliminates arbitrary-depth product names in at most 2^r cases and O(2^r(n+r+1)(S+1)) unnamed quadratic proof nodes. [A, candidate-local-delta](../../AFFINE-FACTOR-RANK-20261115-001A/AFFINE-FACTOR-RANK-20261115-001A-P001_ranked_elimination/proof.md)
- The minimum static original factor rank of a supplied refutation is a represented Rank Vertex Cover optimum, computable up to rank r in O(2^r poly(N)) time. The unbounded-budget decision is NP-complete even for verified refutations of minimally unsatisfiable strict ternary formulas with all named products used as pivots. [B, known-overlap-found](../../AFFINE-FACTOR-RANK-20261115-001B/AFFINE-FACTOR-RANK-20261115-001B-P001_finding_factors/proof.md)
- A fixed observation of rank r removes all names on the full Boolean cube when on every case each successive pair of affine factors has a constant factor or constant sum. The resulting formal degree-two conversion uses 2^r cases regardless of depth. The rank bound is sharp in general and a minimum such observation up to rank r can be found in O(6^r poly(N)) work. [C, candidate-local-delta](../../AFFINE-FACTOR-RANK-20261115-001C/AFFINE-FACTOR-RANK-20261115-001C-P001_affine_restrictions/proof.md)

The synthesis binds the accepted conclusions and the decision note. The scientific arguments and independent checks are in the linked proof records.
