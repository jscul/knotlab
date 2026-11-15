# How many independent affine factors a named proof must fix

2026-11-15 (Pacific). Goals G3 and G16.

## The question

First test two independent affine forms on a live nested proof; then determine when rank r original controls suffice to remove all names, whether the factor choices can be found, and what reuse alone or algebraic dependence can imply.

## Prior work in the program

`scripts/track.py objects "common affine factor degree two named products branch cases" --until 2026-11-15 --exclude AFFINE-FACTOR-RANK-20261115-001 --limit 3`

`scripts/track.py objects "rank affine original factor low rank product declaration proof" --until 2026-11-15 --exclude AFFINE-FACTOR-RANK-20261115-001 --limit 3`

`scripts/track.py objects "two independent forms per gate affine restriction binary products" --until 2026-11-15 --exclude AFFINE-FACTOR-RANK-20261115-001 --limit 3`

- `PRODUCT-NAME-TRANSFER-20261115-001` studied Unrestricted product names simulate ordinary extended resolution. Compare branch count, proof size and formal degree on the same named proof, including complementary, dependent and mixed factors.

The preceding named-product study proves the one-common-factor case, the sublinear declaration-count bound and a fixed-depth bound. Its grouped correction requires honoring raw name scope, normalizing before renumbering and correctly handling a reused empty axiom and zero multiplied by a displayed quadratic factor. Those controls enter the new tests.

## Prior work outside the program

Boyar, Find and Peralta compare multiplicative complexity and affine restrictions of Boolean functions (https://pmc.ncbi.nlm.nih.gov/articles/PMC4957665/). Meesum et al. study Rank Vertex Cover on a represented matroid (https://doi.org/10.1137/17M1154370); the present search specializes that known problem to the original factors available at live proof declarations. Pang v2 Theorem 7.2(a), at degree two over F2, is already admitted in QUADRATIC-ROUTE-TRANSFER-20261115-001B. This study proves the simulations and limitations directly; the credited preprint is used only for its existing lower-bound specialization.

## Evidence and stopping rule

Start with four assignments to two independent forms, with overlapping supports and both polarities. Then prove a formal unnamed degree-two conversion for a supplied rank-r span, search for the span when appropriate, compare to a semantic affine test on every fixed-value part of the Boolean cube, and demonstrate failure of an ancestry-only reading. Count all proof nodes; separate the number of cases, construction cost and universal SAT work. Test actual proof DAGs and independent extensional checks, formal squares, depth, certification or a sharp obstruction; stop at the stated scope.
