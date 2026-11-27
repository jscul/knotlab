# What the allowed states and the marked loose distinctions tell a reader of the families' tree

Epic `MARKED-LOOSE-20261127-001`, at the coordinator's go-ahead: the cheap first check of direction 2 of
`TREE-PROOF-20261127-001`, which bears on the owner's premise that distance is the only form of information (A97). A
check by the thread, not registered; computed. The sections down to "Frozen" were committed before the frozen run.

## The question

The pair-cost referee showed two starts with the same allowed states on the same distinctions and different families'
trees: the allowed states alone do not fix the tree. A reader that also knows which distinctions are loose (held by
one knot) sees more. Does that pair, the allowed states and the loose set, fix the families (as groups of loose
distinctions) and their tree? Any start with the same pair is, to that reader, the same start.

## The test ([`presentations.py`](presentations.py))

For a start S, a **presentation** of its pair is a set of as many knots as S has, each a law in S's law space with at
least three places, holding each loose distinction once and every other distinction twice, whose laws span S's law
space (so it allows exactly S's states) and whose knots are connected. For each presentation: its families and its
tree (for every threshold of the families' distance d, the partition of the loose distinctions into the clusters of
families joined at d at most that threshold). Timed on 300 census starts: 0.1 seconds, 469 presentations, one tree
each (seen before the freeze, on the first 300 only).

## Frozen

**Set.** Every census start of three to five knots (round 0), every presentation of its pair.

**Hypothesis H.** On every census start, all presentations give the same family partition and the same tree: at this
size, the allowed states with the loose set marked fix the families' tree.

**Stop.** H holds: at up to five knots marking the loose distinctions is enough, and the next check is one size past
(sampled starts of six to eight knots, and the first grown round, where the referee's witness lives). H fails: the
smallest start whose pair has two trees is the A97 counterexample with the loose set marked.

**What it would not show.** Presentations with a different number of knots, or with knots of two places; grown
stages; anything about distance beyond this pair.
