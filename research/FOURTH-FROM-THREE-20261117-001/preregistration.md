# Does a knot on three additions predict what the fourth can do?

Ticket `FOURTH-FROM-THREE-20261117-001`, 17 November 2026, serves G16. The owner selected this question after `FRESH-THREE-20261117-001`. This exploratory design was fixed before reading any fourth-addition result.

## What would settle the question

Starting with the original knots erased at eight, use the same anonymous transition through twelve distinctions. At eleven, each of the three additions remains unmarked to the grower. Their projected allowed states form either a six-state knot or a free triple. For every such full context, compute the exact conditional distribution of the relation on those three and the next addition. Does knowing the triple type suffice to give that distribution? Does it at least determine exactly which outcomes are possible?

The primary observer can distinguish the new arrival from the other three. The earlier three have no names or birth order. A second observer forgets which of all four came last. Both can swap each distinction's values independently. The original eight participate in growth and are hidden from both observers. Each of the 13 earlier cut inputs contributes all its reachable contexts. Their counts are indexed by cut input and column representation; finding a witness does not depend on this counting convention.

## In standard terms

For a Markov transition on finite binary relations, test whether it induces a well-defined one-step kernel on the observed ternary isomorphism class for the specified four-column readout. Compare full conditional laws at every input of the same type. Compare their supports separately. Also ask whether the ternary type helps predict a genuinely new event under the actual distribution of trajectories.

Count the pairs of the earlier triple which form a knot together with the fourth distinction. For both triple types record the probability that at least one such pair does. An additional observable asks whether the old triple determines the value of the fourth in every projected row. This occurs precisely when the four-column and three-column row counts agree. Pool with equal priors on the original two starts and their actual trajectory probabilities, conditioning on the triple type after mixing.

There is a structural prediction for a knotted triple. It has three complementary pairs of row assignments, so there are only four possible deterministic columns up to exchange of values. Its three columns already occupy three possibilities. In a representation that excludes 000 and 111, the remaining column returns the minority of the three bits. Placing a not-all-equal constraint on each old pair and the fourth forces exactly this choice. The old majority pair forces its opposite. When the column or its complement is already present among the hidden distinctions it is disallowed as a copy. When it is unused it is available as a zero-cost move. Check the prediction in every reached knot context, including the possibility that only one occupancy case occurs. This argument concerns the truth table of a determined column and supplies no notion of distance.

## Checks

Verify the per-cut triple probabilities and 22,475 indexed eleven-distinction configurations against the preceding study. Validate the group action by permuting and flipping test columns, preserving the identity of the fourth only for the primary observation. Use both an attainable-outcome witness and unequal probabilities when available. For witnesses, replay at least one path from the eight-cut input and reconstruct all the literal fourth-column options independently. Check the full probability totals, the three-column restrictions and the conditional averages. The advisor emphasized that equal averages can hide different supports and that simply recovering the old triple follows from conservative growth. Stop after this one addition.

## Prior work in the program

`python3 -B scripts/track.py objects "matched starts" --until 2026-11-17 --exclude FOURTH-FROM-THREE-20261117-001`

`python3 -B scripts/track.py objects "predicting the next allowed states" --until 2026-11-17 --exclude FOURTH-FROM-THREE-20261117-001`

`python3 -B scripts/track.py objects "ternary projection of allowed states" --until 2026-11-17 --exclude FOURTH-FROM-THREE-20261117-001`

- `ERASE-SEPARATELY-20261117-001` supplies the two eight-cut distributions. `FRESH-THREE-20261117-001` supplies the cohort, the signed growth rule and exact three-addition baselines. It stops at eleven.
- `KNOT-CAP-20261117-001` registered a shared-value whole-table study. `STATE-RULES-20261117-001` and `KNOT-ORDER-20261117-001` compare growth rules on states and knots.
- `BASES-WITHIN-20261112-001` measures a drawn nesting. `SHIFT-LOCK-20261112-001` studies ties on stitched patterns. `SIGNED-KNOT-OVERLAP-20261114-001` projects a fixed template and `HARMONY-ARITH-20261112-001` studies allowed periods. `CLAMP-LEARN-20261112-001` changes a walk's starting state and `ACROSS-FOLD-20261112-001` measures a bond across a fold.
