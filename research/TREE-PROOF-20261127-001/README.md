# A proof of the pair cost, and with it the families' tree

Epic `TREE-PROOF-20261127-001`, at the coordinator's go-ahead while the referee of `SELECTED-KNOTS-20261127-001` runs.
A proof by the thread; with one computed check. The proof is [tree_proof.md](tree_proof.md). Refereed (R1: the theorem
confirmed with proof fixes; **one Block**, on reading the tree off allowed-state distances alone; folded in there).

**Result.** Under ordinary parity growth, funded and not closing through round t, the least change flipping exactly two
families' facts is the length of a shortest chain of families between them, each step costing d + 2t + 2, d the start's
distance between the two families (a step count on the meeting pattern). The direct step attains the minimum on 6,836 of 6,839 recorded pairs; for a fixed start every direct step does once
2t + 2 is at least the largest d(A, B) − d(A, C) − d(C, B) (R1: a wide middle family can delay that to round 17). From it: a set
of families' cost is its cheapest crossing step; at a scale k the kept sums are the parities of unions of clusters (modulo the
complement), families joined when d + 2t + 2 ≤ k; and the clusters split, round by round, along the single-linkage tree of the families by d. Proved from the engine's group and spending rules (one input per parent; parents pairwise candidates) and the earlier
closing proof.

**Computed check.** All 6,839 pair costs of the selected-knots frozen runs equal the shortest chain ([chain_check.py](chain_check.py)).

**On the owner's premise (A97).** [Corrected after R1, Block.] The pair cost is a distance between allowed states, and
given the family parity map its clusters are the tree's at every resolution; but the allowed states alone do not fix
the tree (two starts with the same allowed states give different trees), so the tree is read off distances only once
the families' facts are named from the holdings. No scale is needed for the tree; a scale decides which level counts as
the facts.

**Not covered.** Closing or stalled growth, the forbidding cuts, capped group rules, other laws.
