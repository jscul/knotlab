# When agreements bind again

Eight first bonds on six disjoint agreement readings hold an upper bond. One connected twelve-knot not-all-equal start realizes the full relation allowed by the eight first bonds. The original three-knot ring realizes the same upper relation at rounds three and four when two first readings compared to each other can overlap.

## What the frozen clusters tested

Let J be the joint image of the cluster's readings on the source stage. The cluster conjunction uses its chosen two or three bonds. The last column below uses every first bond whose three readings belong to that cluster.

| Ring stage and choice of carriers | Clusters of two or three bonds | Clusters with six or more distinct readings | J smaller than the cluster conjunction | J smaller than the conjunction of every bond on these readings |
| --- | ---: | ---: | ---: | ---: |
| Round one, disjoint | 0 | 0 | 0 | 0 |
| Round two, disjoint | 24 | 0 | 18 | 0 |
| Round one, overlap allowed | 70 | 49 | 70 | 70 |

All 24 disjoint clusters at round two have exactly four readings. Three disjoint upper carriers of size at least two require six. Their six disjoint underlying carriers would require at least twelve distinctions. The entire round-two stage has nine. The 18 two-bond clusters each allow 13 words. Each has a third bond on the same four readings, and adding it leaves exactly the 12 that occur. The six three-bond clusters already give those 12 words. The pre-freeze note called all 24 two-bond clusters. The archived run correctly counts 18 pairs and six triples. [Raw recount](layer_recount.json)

At round one with overlap allowed, 21 clusters have five readings, four have six, and 45 have seven. Across the clusters there are 9,510 choices of three disjoint upper carriers. On the cluster's own laws, 2,104 have every reading unread at a single lower bond and every pair free. All eight triples occur in all 2,104 cases. Substituting the *actual* joint image for the conjunction gives 1,093 constrained, pairwise-free triples across the 49 eligible clusters when each upper reading must still be unread at a cluster bond. These are cluster/choice incidences. The actual stage imposes further restrictions on its overlapping first readings. It takes a separate deletion test to attribute an upper exclusion to the lower bonds. [Counts by cluster](layer_recount.json)

**Why three single-clause bonds cannot suffice.** Fix any target triple of upper values. Independently in each upper carrier choose a uniformly weighted word giving its target value. Give every unused lower distinction an independent fair value. Every individual lower distinction is fair because complementing a whole carrier leaves its agreement unchanged. A lower law cannot contain all three places of an upper triple carrier under the single-bond unreadability condition. Its three distinctions therefore come from at least two independently sampled groups. If two come from the same group, a prescribed pair of values has probability at most one half because the first member is fair. The third prescribed value costs another half. If the three come from different groups, their prescribed word has probability one eighth. Thus each single-clause law excludes at most one quarter of the choices for the target. Three such laws together exclude at most three quarters. Every target remains possible. This applies to either overlap convention when the conjunction treats distinct lower readings as variables. It also settles the upper-bond part of the unrun round-two overlap test on this ring, since all 411 first bonds exclude one triple each. The round-two overlap joint-image census remains unrun.

## A disjoint example on a closed start

Name the six lower readings in order A0, A1, B0, B1, C0, C1. The first reads agreement on distinctions (0,1,2), the next on (3,4,5), continuing in threes through (15,16,17). The twelve source knots carry the ordinary not-all-equal law on these supports.

```
(0,1,6)    (1,2,9)    (3,4,8)    (4,5,11)
(6,7,12)   (7,8,15)   (9,10,14)  (10,11,17)
(12,13,0)  (13,14,3)  (15,16,2)  (16,17,5)
```

Every distinction has two holders and the start is connected. There are 7,570 allowed source states. On the six readings, exactly 37 words occur. Take any one reading from each of the A, B and C pairs. If all three agree, each makes its three underlying values equal within its carrier. Three of the source laws then demand that the A and B values differ, that the B and C values differ, and that the C and A values differ. This is impossible for bits. All seven other triples occur. These are eight first bonds, one per choice, and they are the only first bonds on the six named readings. All their pair projections are full. For each of the 72 source-knot/reading combinations, at least two fixes of the knot leave both values of the reading possible. Each of the 18 carrier members can change its reading by a single allowed change. [Source and deletion tables](layer_witness.json)

Read P as A0 = A1, Q as B0 = B1, and R as C0 = C1. The eight lower laws exclude 000 on P,Q,R. If all three pairs disagree, each has one 1, and the three 1s violate the corresponding lower law. Every other upper word occurs. Forgetting any one upper reading gives all four pairs. Deleting any one lower law admits the unique six-reading word with its three 1s on that law and its other three values zero. This restores upper word 000. For each of the 24 combinations of an upper reading and a lower bond, six of the lower bond's seven fixes leave both upper values possible. The canonical test passes with each upper reading as contact and all six lower readings quantified away. [Eight separate deletions and canonical checks](layer_witness.json)

Eight is minimal in the class where each lower law forbids exactly 111 on three distinct readings. For a target upper word, assign every agreeing group all zeros. In each disagreeing group choose exactly one member to be 1. If fewer than three groups disagree, no 111 is possible. If all three disagree, a forbidden triple must be the set of three chosen members. To exclude the upper word requires a law for every choice of one member per group. With at least two members per group this takes at least eight laws.

The lower bonds meet the full-stage definition. Each has three source laws that are individually essential and jointly sufficient. For two lower bonds those three source laws are connected and omit one place of each carrier. For six their supports split into two parts and omit one carrier member in total. Thus none of these eight lower bonds qualifies for the separate local search requiring connected holders containing all carrier members. The separately checked 4,095 ways to shorten one or more of these six carriers lose the upper obstruction. The example establishes existence for chosen readings. Its source is closed before growth. [Holder sets](layer_witness.json) · [Carrier shortenings](carrier_shrink.json)

## A grown-ring example when first readings can overlap

At round three compare the following pairs of agreement readings.

| Upper reading | First carrier | Second carrier |
| --- | --- | --- |
| P | (0,1,2) | (0,1,6) |
| Q | (3,9,10) | (3,11,12) |
| R | (4,7,8) | (5,7,8) |

The carriers overlap within each pair. The three upper readings use mutually disjoint sets of raw distinctions. All eight choices of one first reading per pair are bonds of the stage, each missing 111. They are connected by shared readings. They allow 37 lower words, of which 25 occur on the actual stage. Both relations yield exactly the seven upper words other than 000. Removing each lower law in turn restores 000 in the eight-law conjunction. Each upper reading remains unread at each individual lower bond on either relation. The same carriers, lower bonds, 25 lower words and seven upper words persist at round four. On the physical round-three stage, each of its two newest laws individually excludes 12 assignments that would realize upper word 000, and all but the first birth's law form the unique minimal set of source laws sufficient to exclude it. [Ring certificates](layer_ring_search.json) · [Source-law deletions](ring_upper_deletions.json)

The signed version of the eight-law pattern allows each named lower reading to have either value in the excluded words. We searched for any such pattern with all six carriers disjoint. The eligible choices of a first pair with at least four shared signed pairs were 0, 0, 598 and 4,370 at rounds one through four. None completed the pattern. This limits only this signed eight-law construction. The overlap search stopped at its first witness at rounds three and four. Other forms of cluster above the frozen cap, larger ring stages, other starts and arbitrary further iteration were not exhaustively tested. [Pattern and deletion controls](layer_ring_search.json)

## Corrections to the reading

- **Block on the first-layer-only claim.** Replace “Under not-all-equal, bonds are a first-layer phenomenon of agreement readings” in the local-direction row of the decision with “Eight full-stage bonds bind three upper agreements on a constructed closed start with disjoint first carriers. The grown three-knot ring does the same at rounds three and four when comparisons within each upper pair may overlap. Selection of these readings by growth remains open.” Qualify the hand-off, goals checkpoint and guide's iteration question correspondingly. [Decision](../decision.md)
- **Narrowing on the exact presentation.** Replace “on every cluster read, the bonds together present the readings' joint image exactly” in the decision's iteration section, and the parallel sentence in its tower summary, with “On all 24 disjoint round-two clusters, all bonds on the cluster's readings recover their exact joint image. The 70 overlapping round-one clusters each have further restrictions on those readings.” [Raw recount](layer_recount.json)

## Replay

From the repository root, each command below runs one process. The first reconstruction uses the earlier independent ordinary-growth rule. The two archived strict summary rows, six saved examples and 18 post-hoc records all match. The historical overlap run left no dedicated output file. The signed ring search uses the independent ring recount in this directory. Its positive controls recover the unsigned and signed planted patterns and lose each pattern under all eight single deletions.

```sh
ulimit -v 2097152
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd research/RING-BOND-20261127-001/referee-R1
../../../.venv/bin/python -B layer_recount.py
../../../.venv/bin/python -B layer_witness.py
../../../.venv/bin/python -B layer_ring_search.py --through 4
```

The small runs used two actual overlap clusters, 8,192 of 262,144 raw assignments, and the first ring round respectively. Each took under 0.1 seconds. The complete cluster recount and the constructed witness each took about a quarter second. The signed ring search took 6.5 seconds and peaked below 140 MiB.
