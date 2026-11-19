# A literal later pair-distance failure with identical current triple minima

At the 1,999-junction reached stage, the marked permutation preserves every pair and triple minimum, every simultaneous pair-flip bit, and every distinction in the growing end. On the next complete round the least common bond sizes through the marked pair and its proposed image are **86 and 110**. All three involved names were already shared at the marked stage, so no choice of fresh names can extend this permutation.

The finite parameters are three old marks, five ordinary anchors including one distinguished anchor, seven shielding middles of each color, weight 22 on each heavy test bundle, and weight 28 on each shield bundle. A bundle of weight `w` consists of `w` separate parallel distinctions.

| Stage | Ordinary junctions | Distinctions | Minimum through `(26,74)` | Minimum through `(122,74)` |
| --- | ---: | ---: | ---: | ---: |
| Start | 1,607 | 24,174 | — | — |
| After round one | 1,999 | 24,566 | 110 | 110 |
| After round two | 2,013 | 24,580 | 86 | 110 |

## Literal growth and the exterior branches

Each shield middle has its own ordinary branch to the common exterior. In a branch with parameter `M = 28`, label old live junctions `a_i,b_i` for `0 ≤ i < M`. Every `a` has `M−1` loose distinctions and every `b` has one. A closed witness meets all the `a` junctions. Each `b_i` has two closed witnesses, which meet it and two nonempty parts partitioning the `a` junctions other than `a_i`. Both witnesses also meet the branch's shield middle. The candidate graph consists of the complete set of `a` junctions and the candidates from `b_i` to every `a` except `a_i`. The full set of `a` junctions has a common witness and gets no join. Each of the other maximal groups consists of `b_i` and all `a` junctions except `a_i`, and has no common witness. Those groups cover the candidate pairs and consume every loose name.

The first round creates `M` new junctions. Any two share old parents, and no old parent meets them all. The next group takes one loose distinction from each. The first round therefore gives one fresh distinction to each new junction. The second round gives their single child one fresh distinction, since other branches still hold loose names. At the first reached stage disjoint routes through the distinct `b_i` and their witnesses give terminal cut cost `M`. At the second reached stage the sole new loose distinction gives terminal cost one. All fourteen literal branches obey these calculations. The start and both reached stages have connected ordinary supports of arity at least three, and all holder-graph singleton cuts have connected complements.

The literal replay uses the archived stateful production rule with its GF(2) implication check. It substitutes a maximal-clique enumeration for its group search, which otherwise materializes large numbers of proper valid subcliques at this size. Extending a valid clique preserves its lack of a common witness, so the maximal valid groups are precisely the maximal candidate cliques without a common witness, with the usual uncovered candidate pairs then added. A separate implementation independently checks the two replayed rounds.

## Why all old pair and triple minima agree

For a bond containing any host distinction, a branch can contribute crossings only when its shield middle and the exterior lie on opposite shores. Each restriction to the branch is then a connected separating cut. Compress that branch to its minimum terminal cost and mark its compressed distinction if the query uses any names from the branch. To obtain the original minimum, add the difference between the branch's marked and unmarked separating costs. This difference is fixed under the permutation, including infinite marked cost when no branch cut contains the requested names. Queries entirely within the exterior branches have all names fixed.

At the marked stage there are 196 disjoint routes from each color hub to the exterior, by the seven shield branches with 28 routes each. A cut of size below 196 puts the two hubs and the exterior together. Folding those three junctions into one preserves each such bond. Conversely, every bond of size below 196 in the folded graph lifts with the three junctions together. At least one whole route from each color hub to the exterior stays on that side, so any connections through the folded junction can be lifted.

The folded graph has 122 labelled bundles. For any set of up to three marked bundles, choose the marked middles and one weak anchor untouched by the query. The resulting shore and its complement are connected and contain all requested crossings. The cut costs at most 195. The checker verifies this construction on all 122 singletons, 7,381 pairs, and 295,240 triples. Multiple marked names from a single parallel bundle use the same crossing. The proposed swap of test middles is an exact automorphism of the folded weighted arrangement and fixes the branches, so the whole current pair and triple tables agree. A direct folded calculation gives current bond size 110 through either marked pair. Adding the fixed literal branch name `24201` gives size 169 through either triple. The selected name lies in a branch cut of cost 28, so its compression adds no surcharge.

## The successor obstruction

In the next stage the shore containing the first hub, its seven shield middles, and their branch interiors has a bond of size `2 × 22 + 7 × 6 = 86`. It crosses both marked test bundles. The image pair lies on two distinction-disjoint four-cycles of heavy bundles. A cut crossing a marked bundle on each cycle must cross at least two bundles on each, giving a lower bound of 88. This already certifies failure. An exhaustive connected-cut search on the 26-holder compressed successor gives exact minima 86 and 110. Both attaining cuts are lifted and checked as literal connected-shore bonds. The image calculation requires the connected-shore condition.

The marked swap preserves the whole partition into equal holder columns, so it preserves every simultaneous pair-flip bit. The equation difference has a separate certificate. Selecting one distinction on each of the four bundles in the original red cycle gives an allowed state difference that meets the image of the red hub's equation in exactly one distinction.

```bash
.venv/bin/python -B experiments/LATER-BOND-READING-20261119-001/LATER-BOND-READING-20261119-001-E001_future/replay_shield.py
```

[Literal supports, branch routes and attaining bonds](../../../artifacts/LATER-BOND-READING-20261119-001/LATER-BOND-READING-20261119-001-E001_future/replay_shield.json)
