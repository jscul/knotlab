# Choosing how to order two routes within each stage

Status: Proved

## Accepted conclusions

- A linear indexed parity test finds a nested order of the two branches in each stage whenever one exists. Such orders cover 2,071 of the 7,640 two-stage layouts up to typed renaming. [A, known-overlap-found](../../SWAPPED-ROUTE-GROUPING-20261115-001A/SWAPPED-ROUTE-GROUPING-20261115-001A-P001_swap_equations/proof.md)
- A deterministic quadratic-time and quadratic-space calculation on the graph of legal stage orders recovers the globally minimum number of exceptional names, an attaining order and the set of exceptions. [B, known-overlap-found](../../SWAPPED-ROUTE-GROUPING-20261115-001B/SWAPPED-ROUTE-GROUPING-20261115-001B-P001_minimum_exceptions/proof.md)
- After optimal swapping, k exceptions give a witness-producing decision bound O((r+1)^2+2^k(r+1)); k=0 takes linear work. Independent blocks can use different linear solvers even when the global k and the number of pads active with both polarities grow linearly. [C, candidate-local-delta](../../SWAPPED-ROUTE-GROUPING-20261115-001C/SWAPPED-ROUTE-GROUPING-20261115-001C-P001_decision_and_controls/proof.md)

The synthesis binds the accepted conclusions and the decision note. The scientific arguments and independent checks are in the linked proof records.
