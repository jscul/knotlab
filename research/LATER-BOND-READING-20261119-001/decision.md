# When a hidden parity equation changes a later bond distance

**Pair and three-distinction bond distances, even with the growing end fixed pointwise, can miss a difference that changes a pair of old distinctions in the very next complete round.** For every fixed number of distinctions to read together there is a reached arrangement that passes the whole present reading through that order and fails on a later pair. This holds even when every two ordinary junctions share at most one distinction. The argument uses the complete cheapest-fresh-count parity law and allows its junction arities to grow. [Proof](../../proofs/LATER-BOND-READING-20261119-001A/LATER-BOND-READING-20261119-001A-P001_future/proof.md)

The smallest reached example found so far, ordering by the number of ordinary junctions and then distinctions, has **104 junctions and 372 distinctions**. A start with 56 junctions and 276 distinctions reaches it in one round. The next has 146 junctions and 450 distinctions. The full-stage verifier numbers the selected old pair (4,10) and its image (10,16). The exchange moves distinctions held by two middle junctions and fixes all 180 distinctions at the growing end.

| Old distinctions followed | Current pair bond distance | Next-round pair bond distance |
|---|---:|---:|
| Selected old pair | 23 | 21 |
| Image of that pair | 23 | 23 |

The four distinctions (0,3,24,26) have no common bond. Their image (12,15,24,26) has a smallest common bond of size 46. Four repairs the **whole marked stage** in this example. After factoring out exchanges of distinctions with identical holders, exactly 24 renamings preserve all pair and triple readings. Exactly four survive the full four-distinction table, and each preserves the complete parity equation space. Each therefore carries every later reading. The triple readings themselves identify the relevant holder classes; the comparison uses no separate flip reading. The independent calculation checked all 1,770 compressed pairs and 34,220 compressed triples for the specified exchange and accounted for every literal distinction through the branch formula. [Full 104-junction verification](../../artifacts/LATER-BOND-READING-20261119-001/LATER-BOND-READING-20261119-001-E001_future/replay_shield_uniform_group_104.json) · [Growth replay and stabilizers](../../experiments/LATER-BOND-READING-20261119-001/LATER-BOND-READING-20261119-001-E001_future/replay_shield_uniform.md)


In the separately enumerated uniform branch family, the first example has 224 junctions and 700 distinctions. All 4,352 parameter tuples in the stated four-dimensional range were considered, with 3,378 admissible starts inside the cut of 328 current junctions. Of these, 119 pass every current triple and fail on the designated next pair. The asymmetric search examined 3,162,112 parameter assignments across seven specified panels. The four panels with four or five attachments per color had a cap of 240 current junctions; the three panels containing six attachments of at least one color had a cap of 118. It varied the two test weights independently from 1 to 4, the two hub weights from 1 to 16, and the two initial branch costs from 2 to 14 within each cap. The 104-junction witness is the smallest in these panels. [Uniform census](census.md) · [Asymmetric panels and literal permutation](../../experiments/LATER-BOND-READING-20261119-001/LATER-BOND-READING-20261119-001-E001_future/weighted_shield.md)

## Why a hidden equation begins to matter

Take four middle junctions called a, b, c and d. One hub with a and b forms a four-step parity cycle through an ordinary junction v. A second hub with c and d forms another such cycle through the same v. Exchange the names at a and c. This renaming exchanges one spoke of the first cycle for one from the second. It fixes every distinction at every live junction.

Many separate growing branches initially make a cut separating the hubs expensive. An arbitrarily large but prescribed number of marked distinctions still fits into a smaller bond. All such readings therefore see the same result as a calculation in which the hubs are identified. In that calculation the exchange is an exact symmetry. Marks inside the branches are included in the proof.

The next complete round brings the many loose distinctions at the end of each branch to one. A bond can now enclose the first hub cheaply. Two of its spokes can cross together. The exchanged pair has a spoke in each of two cycles, and each cycle must cross a cut an even number of times. Both need another crossing. That is the cost that finally separates the two readings. An allowed change along the first cycle also directly witnesses the hidden equation at the earlier stage.

The two readings are on the same arrangement undergoing the same round. Because the failing pair uses old distinctions, the discrepancy survives every choice of names for the fresh distinctions.

## Four distinctions and larger readings

The explicit family works for every fixed order r≥3. At each displayed order the current matching preserves all minima on every set through that order. The numbers in the table are pair bond distances (minimum size of a common bond minus one).

| Current reading guaranteed to match | Old pair at observation | Its image at observation | Same pair one round later | Its image one round later |
|---|---:|---:|---:|---:|
| Through three distinctions | 109 | 109 | 85 | 109 |
| Through four distinctions | 155 | 155 | 126 | 155 |
| Through five distinctions | 213 | 213 | 177 | 213 |

Each exact pair entry was computed by enumerating every partition up to permuting identical junctions and requiring both shores to be connected. A second implementation checks the three-distinction construction using actual complete-round junctions. The general proof uses a strict upper and a strict lower bound and does not rely on equality of the optimized numerical entries. On the displayed order-three example a current quartet already detects this particular exchange (bond sizes 240 and 241). The next row gives a different stage where every quartet still misses the future discrepancy. [Exact readings](../../artifacts/LATER-BOND-READING-20261119-001/LATER-BOND-READING-20261119-001-E001_future/future_reading.json) · [Literal replay and connected cuts](../../experiments/LATER-BOND-READING-20261119-001/LATER-BOND-READING-20261119-001-E001_future/replay_shield.md)

For every integer r≥2 a refinement makes the first reading that exposes the specified failing renaming **exactly r+1**. Use r−1 ordinary anchors. The extra query fixes one additional middle against the first hub and marks every anchor incidence at the exchanged middle. Under its image that middle is isolated on a shore that must also contain another site. No bond can realize the query there. The whole family can be realized with O(r²) junctions and distinctions, including when ordinary junctions meet once. Along these examples the necessary order is at least a constant times the square root of the size. The optimal growth rate is open. [Explicit parameters and proof](constructive-proof.md)

There is no size-independent number of distinctions per reading sufficient for all arrangements. At any particular finite stage a large enough order recovers the equations. A set of k distinctions is itself a bond precisely when its minimum common bond has size k. If every exhausted junction has at most d distinctions and its support is a bond, the readings through d recover every such support as a bond. A span-preserving renaming follows because its image takes every generating row into the same finite row space, and the live rows are already fixed. This suffices at all later rounds. The unbounded result is a worst-case requirement over the allowed finite stages.

## What two attachments protect

At two attachment junctions, a bond using both parts must put those junctions on opposite shores. A third distinction in the growing part can therefore read the price of crossing a specified inner pair while separating the attachment junctions. With a fourth distinction one can do the same for an inner triple. This gives every later pair from the first three readings and every later pair and triple from readings through four, provided all growth is confined to that changing part and the old matching fixes that part. For a single fixed connection whose replacement changes cost, its values at the initial cost and at unit cost determine every intermediate reading.

With three or more attachments several choices of which junctions stay together can produce the same current minimum. A general computation must keep both the assignment of the attachments to the two shores and the connections within each shore. The construction exposes one of those choices after growth. In the 104-junction example the four distinguished middles and their incident distinctions form an unchanged part. It meets the rest at exactly four junctions: the two hubs and the two ordinary anchors. The case of exactly three attachment junctions remains open for the full pair and triple premise. [Exact formulas and several-attachment comparison](boundary-proof.md)

The marked 239-junction, 643-distinction stage from the previous study has one unit-cost attachment between its two terminal junctions for all time. Its own hidden equation stays invisible to every later pair and triple. The new quartet at that stage has bond sizes 117 and infinity under the exchange. It distinguishes the current equations there; it does not break that example's later pair or triple tables. Six specified lawful histories, including that one, two parallel terminal links and a branch whose cost falls, were additionally replayed from age zero through age 12 (72 complete rounds). These six histories sample the relatives. The all-age conclusion on the original is a proof. [Six histories](replay.md) · [Four old marks](../../artifacts/LATER-BOND-READING-20261119-001/LATER-BOND-READING-20261119-001-E001_future/constructive_four.json)

## Exact search bounds and remaining minimality question

The global lower check excludes every failing reached stage with **17 or fewer current distinctions**, with arbitrary meeting multiplicities and no cap on rounds. Its static superset contains 18,330,249 eligible rooted allocations. A rank argument handles all but 1,751 of these. Their 194,984 surviving literal permutations all carry the parity equations. [Exact population and lower-bound proof](small-width.md)

The independent two-attachment search covered 306,057 admissible cores: two to five ordinary sites with each multiplicity from zero to three, six sites with multiplicities zero to two, and seven sites with unit multiplicity on each present meeting. It tested all relevant renamings for all positive integer decreases of the attachment cost. No old pair or triple failed in this population. A separate search of 7,262 non-equational marked core and port choices, with 2,637,594 admissible independent-branch assignments and 10,550,376 marked stages at ages one to four, screened the specified exchange. In that family 5,376 stage tests passed pairs and none passed triples. These are different restricted populations. [Two-attachment enumeration](weighted.md) · [Several growing branches](census.md)

The earlier 30,189-stage census remains an independent bounded positive result. Its surviving permutations preserve the entire equation space and therefore transport both tables indefinitely. It covered 33,430 admissible connected meet-once starts through 15 starting distinctions and every open reached stage through 16 current junctions, at all ages (maximum encountered six). [Earlier census](../GROWN-END-READING-20261119-001/decision.md)

The general transport claim is refuted. The global least failing reached stage and the exact least order necessary as a function of its size remain open. A97 and G1 record the difference between recovering the future at particular stages and the impossibility of doing so at every size with any fixed reading order. Independent program referee pending.

## Prior work in the program

`python3 -B scripts/track.py objects "later bond readings growing end marked" --until 2026-11-19 --limit 5`

The mathematical predecessors are `GROWN-END-READING-20261119-001` (the literal 239-junction example and the bounded marked census), `EXTEND-ROUND-20261119-001` (equation-space transport) and `PARENT-RULE-20261119-001` (the positive-age growth structure). The object-index results `BRANCH-DEPTH-20261112-001`, `MEET-TWIST-20261118-001` and `LIFE-JUMPS-20261112-001` concern other growth laws or observables. The classical criterion that both shores of a bond are connected underlies the enumeration. [Listing the bonds of a graph](https://www.sciencedirect.com/science/article/pii/S0166218X24000155)

The pre-run advisor's adjacent-twin proposal used a different joining rule and moved loose distinctions. The present construction uses the actual complete-round law and fixes the whole growing end. A second advisory read checked the bond bounds and the meet-once replacement. The literal checks separately tested parent selection, demand and fresh counts.
