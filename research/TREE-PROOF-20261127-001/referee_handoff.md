# Referee hand-off: TREE-PROOF-20261127-001

The proof is [tree_proof.md](tree_proof.md); the note is [README.md](README.md); the decision is [decision.md](decision.md);
the computed check is [chain_check.py](chain_check.py) with [chain_check.json](chain_check.json), on the frozen runs of
`SELECTED-KNOTS-20261127-001` (research/SELECTED-KNOTS-20261127-001/frozen_*.jsonl, tree.py).

| # | Claim | Evidence class | Where |
| --- | --- | --- | --- |
| 1 | Lemma 1: a birth's neighbours are its parents and children, and its parents lie in one lineage | proved (also THIRD-LAYER referee R1) | tree_proof.md |
| 2 | Lemma 2: every route between start knots through births can be replaced by a route of the start's own graph that is no longer | proved | tree_proof.md |
| 3 | Theorem: the least change flipping exactly two families' facts at round t is the shortest chain of families with steps d + 2t + 2 (upper bound by rising routes, lower bound by pairing routes) | proved | tree_proof.md |
| 4 | Consequences: set costs, class facts at a scale, the single-linkage tree | proved | tree_proof.md |
| 5 | The tree is the single-linkage tree of distances between allowed states; no reading of a small change is needed for it | reading | tree_proof.md, "Distance, the owner's premise, and the reading" |
| 6 | All 6,839 recorded pair costs equal the shortest chain; the three round-0 exceptions of SK1 are chains through a third family | computed | chain_check.json |

**Points to press.** Lemma 2 (the replacement at a highest birth, and whether every route through births has such a
birth with two parents as its neighbours on the route); the pairing argument in the lower bound (routes that return to
the same lineage, odd points with several loose distinctions); the hypotheses (funded and not closing; the engine
facts E1 to E3); the three round-0 exceptions; and whether "no reading is needed for the tree" says more than the proof.
