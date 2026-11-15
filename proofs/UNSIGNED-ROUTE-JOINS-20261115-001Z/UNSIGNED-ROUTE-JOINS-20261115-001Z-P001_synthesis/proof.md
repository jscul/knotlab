# Sharing a middle variable between two routes

Status: Proved

## Accepted conclusions

- Joining middle names in one stage doubles the minimal supports. Across two adjacent stages the count stays fixed despite a different answer on some inputs; more distant joins reduce the count while introducing bypasses. [A, candidate-local-delta](../../UNSIGNED-ROUTE-JOINS-20261115-001A/UNSIGNED-ROUTE-JOINS-20261115-001A-P001_single_join_census/proof.md)
- The original stage scan decides every activation exactly when all middle variables are distinct. For arbitrary positive joins, reachability on the actual variable names decides in linear indexed time and minimal switch obstructions are occurrence-labelled simple paths plus endpoint blocks. [B, candidate-local-delta](../../UNSIGNED-ROUTE-JOINS-20261115-001B/UNSIGNED-ROUTE-JOINS-20261115-001B-P001_joined_reachability/proof.md)

The synthesis binds the accepted conclusions and the decision note. The scientific arguments and independent checks are in the linked proof records.
