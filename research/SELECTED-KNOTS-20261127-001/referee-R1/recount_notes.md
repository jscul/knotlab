# Frozen counts and the family-tree reading

The recount reads every archived start record. The archives give the holder-step tables, exceptions to the pair and sum cost predictions, counts of kept sums and the selected place laws. The full lists of solver witnesses and kept masks are absent. For each cost table the recount uses the frozen formula and applies every recorded exception. It derives the component partitions and checks that their masks agree with the retained-sum counts. For the third-layer check the recount constructs the places afresh and enumerates every allowed word and every fact modulo the all-families parity equation. [Code](recount.py) · [Counts and raw-file digests](recount.json)

| Claim | Recount |
| --- | --- |
| SK1, exact pair costs | Three departures in 1,875 round-zero pair comparisons. The held-out eight-knot start has cost 6 against 8. The two sampled twelve-knot starts have costs 8 against 9 and 6 against 8. The 4,964 positive-round comparisons have zero recorded departures. |
| SK2, least crossing pair cost | 6,871 proper sums modulo complementation across 3,465 stages. In 204 stages with at least four families, there are 1,735 sums where a change flipping four or more families could flip the sum. The recorded exceptions to pair costs change zero crossing minima. The original sum scorer used crossing minima of the pair formula, and 24 eight-family stages have only an empty failure field for SK2. |
| SK3, two fixed scales | At scale eight, 1,932 rows have zero facts, 119 have a proper nonzero fact space and 1,414 keep all family sums. At scale twelve the counts are 3,182, 115 and 168. On 69 and 63 rows respectively, a component contains a pair whose direct cost exceeds the scale. Its parity agreement is forced by a chain of qualifying pair changes. On 1,870 matched row pairs, scale eight at round \(t\) gives the same partition as scale twelve at round \(t+2\). |
| SK4, tree places | The archive has 224 distinct nonzero facts modulo the place laws, on 156 of 975 starts. All 224 have a single reader of at least three places. The other 819 starts have zero facts. Among the 1,187 listed place laws, 863 are two-place root equalities between complementary child sums. The canonical knot checker requires at least three places. Under tied shortest changes through each place independently, all 975 starts have zero kept facts. |
| Shortest-change reading on grown distinctions | At positive rounds a sum is kept on 105/928 census stages, 245/1,268 held-out stages, 69/216 sampled stages and 86/86 built stages where sums were read. Across these four rosters, 373 stages keep every family sum and 132 keep a proper nonzero space of sums. At least one positive round keeps a sum on 137/628 starts that have a positive read round. These counts record the presence of some kept sum. Identifying the same partitions would require matching which sums are kept. |

Across the 967 starts with scale rows, 144 of the full tree's 180 nonroot internal places appear as partition groups at either recorded scale. On 32 of those starts at least one nonroot internal place is absent at both scales through all read rounds. This describes the reach of the two scales even under the tree's own selection rule.

## A five-family start that separates the two SK4 tests

A row of 17 start knots shares two distinct holdings between each consecutive pair. Give each of the knots at indices 0, 1, 4, 9 and 16 one loose distinction. These are the only live knots. No two share a common witness, so they are five separate families, (A,B,C,D,E). Their consecutive holder-step counts are 1, 3, 5 and 7. The frozen single-linkage rule gives the nonroot internal places (P=A+B), (Q=P+C) and (R=Q+D), and a root equality (R=E). All three internal places occur as groups at scale eight in rounds two, one and zero respectively. Ordinary growth reaches 137 distinctions by round four, and the measured least pair costs on this start agree with the frozen formula in all five rounds.

The place relations (A+B+P=0), (P+C+Q=0) and (Q+D+R=0) each project to 000, 011, 101 and 110. The root relation projects to 00 and 11. The only globally shortest change is the two-place change on (A,B). The seven kept nonzero facts are (P,C,Q,D,R,P+D,C+D), with equality of facts understood modulo the place laws. The first five have a single reader. Neither (P+D) nor (C+D) does. Both are sums of class facts read by individual knots. The frozen scorer returns zero dimension outside the local span here as well. Applying tied shortest changes through every place keeps zero facts. [Holdings, global and through-place changes, and every local reader](recount.json)

This is a counterexample to unrestricted literal SK4 using its own prescribed tree places. The absence of a fact outside the span of the local class facts holds in this example. Each singleton family's starting fact can also be read by its own first-layer knot, so this example does not establish a new layer of whole-held first-layer facts.

## Why the span test has the same result for every such tree

In the declared place code, a change chooses an even set of family leaves. It flips each place whose group meets that set oddly. Every nonzero change therefore flips at least two leaf places. Two leaves with the same immediate parent flip only their two leaf places, giving cost two. Such a pair exists at a deepest internal group, and these sibling pairs are exactly the global minimum changes.

A kept fact has constant coefficients on each group of leaf siblings. The parity of each such group is read at its parent and is itself kept. These parities span every kept fact, modulo the all-families parity equation. This argument uses the specified code and the global minimum reading alone. It applies to any tree of this form, independent of how the pair costs are obtained. The five-family start shows that the stronger single-reader statement does not follow.

With shortest changes through each place, view each nonroot place as the cut between its group and the rest of the tree. A place word gives the tree connections used by a change. At internal groups the number of used connections is even, including at the root. It decomposes into paths between active leaves that share no tree connection, so a least change through a place consists of a single shortest leaf-to-leaf path through its cut. These paths connect all leaves when all ties are kept. To see this, if the minimizing pairs left several separate classes of leaves, choose the nearest pair in different classes and take a middle connection on its path. Each endpoint is closest to that connection from its side. A closer leaf on either side would be nearer than the chosen pair to both endpoints, so it would form a shorter pair with an endpoint of a different class. The chosen pair thus minimizes across the middle cut, contradicting the split into separate classes. The shortest pair changes then span every even family change, leaving zero nonconstant class facts under that reading.

## Reproducing this recount

Use one process with a two-GiB virtual-memory limit. The pilot checked 153 archived starts plus all five witness rounds in 0.06 seconds, peaking at 21,736 KiB. The full recount took 0.13 seconds and peaked at 22,228 KiB. Growth of the new witness uses the [independent implementation in this review](cost_check.py). Its exact pair costs were cross-checked at each witness round by two calculations, additive closure of the least direct pair costs and shortest routes in a meeting pattern augmented by one bookkeeping holder per family. The archived shortest counts were retallied here. Replaying the first-layer shortest moves from archived starting presentations and validating the original least-cost solver require separate checks.

```sh
ulimit -v 2097152
r=research/SELECTED-KNOTS-20261127-001/referee-R1
.venv/bin/python -B "$r/recount.py" --pilot
.venv/bin/python -B "$r/recount.py"
PYTHONPATH=tools .venv/bin/python -B -m knotlab check --cnf 'A B ~C; A ~B C; ~A B C; ~A ~B ~C' --loops A B --contact C
PYTHONPATH=tools .venv/bin/python -B -m knotlab check --cnf '~A B C D; A ~B C D; A B ~C D; A B C ~D; ~A ~B ~C D; ~A ~B C ~D; ~A B ~C ~D; A ~B ~C ~D' --loops A B C --contact D
```
