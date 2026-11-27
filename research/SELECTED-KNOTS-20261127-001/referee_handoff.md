# Referee hand-off: SELECTED-KNOTS-20261127-001

The note is [README.md](README.md) (frozen section committed at `23c0cd52d0` before the frozen runs); the decision is
[decision.md](decision.md); the scores are [score.json](score.json) from [score.py](score.py).

| # | Claim | Evidence class | Code | Data |
| --- | --- | --- | --- | --- |
| 1 | The third-layer referee's shared-fact witness reproduces (two second-layer knots sharing a fact, five facts held by no part at rounds 5 and 6, separating law removals) | computed, before the freeze | `overlap.py` | `overlap.json` |
| 2 | Its chosen-reading third layer reproduces as algebra from its masks | computed, before the freeze | `third_algebra.py` | `third_algebra.json` |
| 3 | SK1: the least change flipping exactly two families' facts is d + 2 + 2t from round 1 on every pair read; at round 0 three starts have a cheaper route through a third family's loose distinctions | computed, frozen | `tree.py` (`distances`, `least_exact`) | `frozen_*.jsonl` |
| 4 | SK2 and SK3: set costs are least crossing pair costs; at scales 8 and 12 the kept family sums are the cluster facts, of dimension clusters less one, on every row | computed, frozen | `tree.py` | `frozen_*.jsonl` |
| 5 | SK4: with the tree's nodes as places, every layer-three class fact is read by a single knot of the tree | computed, frozen | `tree.py` (`dendrogram_layer3`) | `frozen_*.jsonl` |
| 6 | Under the shortest changes the tree shows on a minority of rows | computed, read | `tree.py` | `frozen_*.jsonl` |
| 7 | The conclusion: the knots growth selects are the tree's nodes, they meet as a tree, and no whole-held third layer arises from them | argument from 3 to 5 | decision.md | as above |

**Points to press.** Whether the tree's nodes are what growth selects or a choice of ours (the scale; single linkage;
the knot at each node); whether "read by a single knot of the tree" is the right test of a third layer held by no part;
the round-0 failures of SK1 and whether d should count routes through other families' loose distinctions; whether a
different natural choice of places gives a whole-held third layer without being chosen by hand.
