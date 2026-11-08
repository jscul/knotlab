# Closure of native paths across time

Status: Proved

Ticket `NATIVE-PATH-20261108-001Z`, 2026-11-08.
- **What this is.** A ledger: one line per conclusion, with its label and evidence. It makes no new claim.
- **The decision note** is `research/NATIVE-PATH-20261108-001/native_path.md`.

## Conclusions

| # | Conclusion | Novelty | Evidence |
| --- | --- | --- | --- |
| 1 | In a path of rings the last contact cannot depend on the first ring before lag d_1 + .. + d_(n-2) + 1. | known-with-delta (light cones); proved | A |
| 2 | Every verdict of an affine path is decided exactly by the contacts' row sequences of M^T. | known-with-delta; proved | A |
| 3 | No native path among 996,840 paths in two restricted families (rule 150 everywhere; the carrying chains extended by one ring); the loss happens across the second middle ring. | not found in prior work; exploratory search | B |
| 4 | No path whose second middle ring is a shift keeps all three contacts persistent (3,059,280 paths). | not found in prior work; exploratory search | C |

## Answer

In the three families searched no native path exists: the second middle ring must keep its own first row and carry the first
ring's influence without cancelling it, and no tested ring does both. A wider run of the first family is pending (NATIVE-PATH-S1).

## Pending the owner

Carried from earlier epics:
- whether to qualify `PHASE-HALO-20261103-001-D001` and `FACE-CLAIM-20261103-001-D003`;
- the SELECTION-NOTE erratum;
- superseding `KNOT-COMPOSE-20261101-001-D001`;
- counted length as a native magnitude.

## Recommendation

**Research directions**: a broad sweep of mixed four-ring paths (Payoff 2/3, Concreteness 3/3), then a middle ring designed to
remember and transmit (Payoff 3/3, Concreteness 1/3); pause the process line if both fail. The table is in the decision note.
