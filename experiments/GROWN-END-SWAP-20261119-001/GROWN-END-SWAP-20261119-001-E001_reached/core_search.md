# A grown symmetry that fails at the next complete round

A seven-junction start reaches a twelve-junction stage whose full bond-distance table and growing end are fixed by swapping distinctions 0 and 2. After the next complete cheapest-count round, the bond distances of the old pairs \(\{0,1\}\) and \(\{1,2\}\) are 2 and 3. All three distinctions were already shared before that round. A renaming of fresh distinctions or a re-pairing of old loose distinctions cannot repair this mismatch. The comparison concerns the specified map on one source. [Frozen scope](../../../research/GROWN-END-SWAP-20261119-001/preregistration.md)

## The literal start and the two rounds

The first three supports belong to the middle junction \(M\) and its neighbors \(A,B\). The next three are leaves at \(A\), and the last is a leaf at \(B\). The right leaf's two shared distinctions give the right side enough capacity for the initial symmetry.

```text
(0,1,2,3)
(0,1,4,5,6)
(2,3,7,8)
(4,9,10)
(5,11,12)
(6,13,14)
(7,8,15,16)
```

At the first round the left leaves have one common neighbor, so the law uses all three pairs and gives one fresh output to each. The three newborn supports have pair witnesses at the three older leaves, with no one common witness of all three. Their next demand is one apiece. The right leaf produces two singleton additions, each with two fresh outputs. The second round uses all three new left holders in one junction, making just one fresh distinction. Its inputs are only the left side's loose distinctions. The right side remains open. All of these groups and fresh counts were regenerated from the production law and independently checked by exhaustive parent subsets.

At the twelve-junction stage, exhaustive connected-cut measurement verified all 276 pair entries under the swap. The live supports are fixed pointwise, so their loose distinctions and common-neighbor families are preserved. The allowed assignment with ones at exactly 0 and 1 goes to a forbidden assignment with ones at 1 and 2. At the sixteen-junction successor, 4 of 465 entries differ under the literal extended swap. In particular the named pair has bond-distance readings \((3,3)\) before and \((2,3)\) afterward.

## Why the two-bundle pivot gives an exact test

In the classical incidence representation used to compute bonds, connect loose distinctions to one exterior vertex. Suppose a closed junction \(M\) has just two ordinary neighbors \(A,B\), with \(m\ge2\) parallel distinctions to each. Delete \(M\) and let \(\lambda\) be the minimum cut size between \(A\) and \(B\) in the remaining graph, keeping the exterior when present.

Any bond that separates \(A\) from \(B\) can move \(M\) to the other side. In each location \(M\) meets exactly one neighbor on its own side, so both shores stay connected. This exchanges the two bundles in the boundary, preserves its size, and keeps every other distinction's membership. A bond that cuts both bundles must have \(M\) alone on one shore. Its size is \(2m\), and it exists exactly when the remaining graph is connected. If the remaining graph is connected, a minimum \(A\)-\(B\) cut has both shores connected. Moving any component without its pinned terminal to the other shore would lower the cut. Adding \(M\) next to either terminal therefore gives a single-bundle bond of size \(m+\lambda\), which is the minimum among single-bundle bonds. If deletion disconnects the two neighbors, the minimum single-bundle bond has size \(m\) and there is no bond through both bundles.

Consequently the transposition of one distinction from each bundle preserves the entire pair table exactly when \(\lambda\ge m\). Readings to all other distinctions agree by the bond correspondence. Readings within a bundle and between bundles compare the sizes \(\min(2m,m+\lambda)\) and \(2m\) in the connected case. If the next round lowers \(\lambda\) below \(m\), two old distinctions from the same bundle provide an obstruction. In the seven-start example, \(m=2\) and the exact cut values across the three stages are \(2,2,1\). The left ternary birth converts three outgoing distinctions to one.

## Controls and stopping point

The static seven-junction detector control recovers the known false extension beginning at age zero. A control with one shared distinction to the right leaf already fails the current table test. A transposition within one parallel bundle extends in each measured case. The finite run stops at the certified grown witness and its named controls.

Run `python3 -B core_search.py`. The checker uses integral flow for the pivot values and independently enumerates connected shores for all current and next pair entries. The largest documented check uses seventeen vertices including the exterior, within the cap of eighteen. [Checker](core_search.py) · [Exact results](../../../artifacts/GROWN-END-SWAP-20261119-001/GROWN-END-SWAP-20261119-001-E001_reached/core_results.json)
