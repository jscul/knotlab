# Sharing a middle variable between two routes

2026-11-14 (Pacific). Goals G3 and G16.

## The question

G3 and G16: determine exactly when identifying middle variables defeats the two-route decision scan, what happens to minimal switch obstructions, and what grouping can still decide one input.

## Prior work in the program

`scripts/track.py objects "two-route implications" --until 2026-11-14 --exclude UNSIGNED-ROUTE-JOINS-20261115-001 --limit 3`

`scripts/track.py objects "minimal switch obstructions" --until 2026-11-14 --exclude UNSIGNED-ROUTE-JOINS-20261115-001 --limit 3`

`scripts/track.py objects "shared middle reachability" --until 2026-11-14 --exclude UNSIGNED-ROUTE-JOINS-20261115-001 --limit 3`

- `LEIBNIZ-BOARDS-20261110-001` studied Boards identified by agreement of every finite view. The predecessor counted source-to-sink choices with fresh middle names. Here the raw switches and strict clauses keep their identities while the middle variables are identified in the logical formula.
- `ODD-SEARCH-20261112-001` studied Words searched for an odd harmony or a flip certificate. The predecessor counted source-to-sink choices with fresh middle names. Here the raw switches and strict clauses keep their identities while the middle variables are identified in the logical formula.
- `FAR-BOUND-20261112-001` studied Uniform bond-distance bound on two opposite quadrants of the rule-selected travelling base. The predecessor counted source-to-sink choices with fresh middle names. Here the raw switches and strict clauses keep their identities while the middle variables are identified in the logical formula.
- `PLACE-FLIP-20261110-001` studied Board-value knots read by flips in place in copies of finite boards. The predecessor counted source-to-sink choices with fresh middle names. Here the raw switches and strict clauses keep their identities while the middle variables are identified in the logical formula.
- `BARE-NAMES-20261110-001` studied Boards on abstract names with neighbour distinctions and cell values. The predecessor counted source-to-sink choices with fresh middle names. Here the raw switches and strict clauses keep their identities while the middle variables are identified in the logical formula.
- `WEAK-APER-20261110-001` studied Three-value level laws and their finite-board drift obstruction. The predecessor counted source-to-sink choices with fresh middle names. Here the raw switches and strict clauses keep their identities while the middle variables are identified in the logical formula.
- `BRANCH-DEPTH-20261112-001` studied Depths reached by unrestricted bonds of a fixed maximum size k on a repeating branch. The predecessor counted source-to-sink choices with fresh middle names. Here the raw switches and strict clauses keep their identities while the middle variables are identified in the logical formula.
- `TOP-INFO-20261114-001` studied Which conditions at the root and the target bound the least bond to a covered copy at depth s: effective reading, bond-pinning, middle members. The predecessor counted source-to-sink choices with fresh middle names. Here the raw switches and strict clauses keep their identities while the middle variables are identified in the logical formula.
- `LOOP-LOCK-20261112-001` studied Locks in overlapping closed chains and circulants of stitched harmony copies. The predecessor counted source-to-sink choices with fresh middle names. Here the raw switches and strict clauses keep their identities while the middle variables are identified in the logical formula.

The predecessor counted source-to-sink choices with fresh middle names. Here the raw switches and strict clauses keep their identities while the middle variables are identified in the logical formula.

## Prior work outside the program

The original two-route example is García de la Banda, Stuckey and Wazny, Example 3 (https://doi.org/10.1145/888251.888256). Reachability and minimal path sets are classical (https://doi.org/10.1287/opre.32.3.516). The targets are the universal equality criterion for the old scan on this template and the precise count and sizes of switch supports after an identification.

## Evidence and stopping rule

Freeze positive-polarity identifications of middle variables only; every implication/endpoint keeps its own switches and padding. Compare the old scan against the formula for all small activations, derive an all-size counterexample or equivalence, and reconstruct a satisfying assignment using reached names. Check a larger size, labelled paths, same-stage mixing, cross-stage jumps and a wrong checker.
