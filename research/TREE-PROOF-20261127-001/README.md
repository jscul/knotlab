# A proof of the pair cost, and with it the families' tree

Epic `TREE-PROOF-20261127-001`, at the coordinator's go-ahead while the referee of `SELECTED-KNOTS-20261127-001` runs.
A proof by the thread, not refereed; with one computed check. The proof is [tree_proof.md](tree_proof.md).

**Result.** Under ordinary parity growth, funded and not closing through round t, the least change flipping exactly two
families' facts is the length of a shortest chain of families between them, each step costing d + 2t + 2, d the start's
distance between the two families (a step count on the meeting pattern). Usually that is d + 2t + 2 itself; a chain
through other families is shorter only while 2t + 2 is small (on the records, three starts at round 0). From it: a set
of families' cost is its cheapest crossing step; at a scale k the kept family sums are the clusters joined when
d + 2t + 2 ≤ k; and the clusters split, round by round, along the single-linkage tree of the families by d. Proved from
the engine's definitions (one input per parent; parents pairwise candidates; the closing law), except the engine facts
themselves, which are checked on every record.

**Computed check.** All 6,839 pair costs of the selected-knots frozen runs equal the shortest chain ([chain_check.py](chain_check.py)).

**On the owner's premise (A97).** The pair cost is a distance between allowed states (the least number of distinctions
in which two allowed states differ when they differ in exactly two families' facts), and its clusters are the tree's: the
second layer growth selects is read off distances alone. No reading of a small change is needed for the tree; a scale
only decides which level counts as the facts.

**Not covered.** Closing or stalled growth, the forbidding cuts, capped group rules, other laws.
