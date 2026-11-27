# The parity agreement test

The stage's homogeneous parity laws determine the joint image of its agreement readings. A bond on three disjoint carriers of size two or three requires a sum of the stage's laws with precisely two distinctions from each carrier and no others. The converse fails on the study's own growth. The complete held-out sample has a source bond on **811 of 1,000** starts. Testing every connected set of up to four holders corrects the bond totals in both rounds.

## The argument

For each carrier, choose one of its distinctions and form the binary differences between that distinction and the others. Its reading is 1 precisely when every difference is zero. Write $T$ for the map from assignments to these three groups of differences, $M$ for the matrix of parity laws, and $W=T(\ker M)$ for the possible joint differences. A character $p$ vanishes on $W$ precisely when $T^\mathsf{t}p$ is a sum of rows of $M$. This is the earlier row-sum criterion. For agreement readings it gives an explicit reconstruction. If $r(S)$ is the rank of the differences in groups $S$ on allowed assignments, the fraction of allowed assignments for which exactly the groups $A$ agree is

\[
\sum_{T'\subseteq \{1,2,3\}\setminus A}(-1)^{|T'|}\,2^{-r(A\cup T')}.
\]

This counts each allowed binary assignment once. Positivity determines the words without a choice of weighting on starts.

**Why a six-distinction sum is necessary.** Let $D$ be the characters vanishing on $W$. Suppose no member is nonzero in all three groups. If $D$ omits a group entirely, that group's differences can be chosen independently. Once the other two readings take all four pairs, the three take all eight words. Otherwise $D$ uses all three groups and contains a word on two groups, since two words using distinct single groups sum to such a word. Write the two-group word as $(u,v,0)$. A word using the third group cannot use that group alone, since adding the first word would use all three. After exchanging the first two groups if needed, it is $(u,0,w)$. Its first entry must be $u$ for the same reason. Their sum is $(0,v,w)$. No single-group word can now occur, since the other two groups already give a word. Any further two-group word must agree on both entries with the word just listed for its pair, by adding each of the other two words. This exhausts $D$.

The resulting constraints equate one nonzero binary linear form from each group. A carrier of size two has just one difference. Its disagreement sets the shared value to 1, precluding agreement in either other carrier and violating pair freedom. If all three carriers have size three, set the shared value to 0. In each two-dimensional group the form can then vanish on both zero and a nonzero difference, independently across groups, so all eight words occur. Both cases contradict a bond. Therefore some character uses all three groups. For two- and three-distinction carriers, every nonzero character of one difference group is the sum of exactly two of that carrier's distinctions. Disjointness gives six different distinctions. The argument works on the holder laws whenever those laws already give the bond.

The all-zero assignment witnesses 111 for every agreement triple. The six-sum test in the archived census sought a row sum after finding each bond, so the implementation could have reported a discrepancy. Mathematically there are zero eligible exceptions to either test under these definitions. One six-sum is compatible with all eight words. On the grown eight-distinction source with source laws (0,1,2,3), (0,4,5), (1,6,7), take the first birth (4,6,8,9). The carriers (0,1,4), (2,5,7), (3,8,9) have the sum (0,1,5,7,8,9). Each reading is unread at each individual knot. All eight words occur on the four holders and on the whole grown stage. [Literal checks](parity_checks_results.json)

The earlier parity record identifies which linear readings are sums of the laws. The new implication just proved uses both pair freedom and the sizes of the carriers. It remains true when a three-distinction reading is nonlinear. The earlier start-origin result concerns class facts under a specified rule of change. [Earlier row-sum test](../../BINDING-20261126-001/referee-R1/report.md) · [Earlier class facts](../../BUILT-BINDING-20261126-001/referee-R1/report.md)

## Unconditioned checks

The first enumeration takes every binary linear subspace of the possible differences for each labelled carrier shape. A shape such as 233 means one carrier of two distinctions and two of three. The search generates the possible differences directly and tests every Boolean image before asking about a six-sum. No holder cap, holder-selection rule or six-sum filter enters this check.

| Carrier sizes | Linear images tested | All pairs free and some word missing | Of these, lacking a six-sum | Six-sum with all eight words |
| --- | ---: | ---: | ---: | ---: |
| 222 | 16 | 1 | 0 | 0 |
| 223 | 67 | 6 | 0 | 0 |
| 233 | 374 | 54 | 0 | 0 |
| 333 | 2,825 | 981 | 0 | 135 |
| Total | 3,282 | 1,042 | 0 | 135 |

Across these 3,282 labelled images, 2,928 have a six-sum. All 3,282 contain 111. The frozen table of missing counts is exact if each carrier's observed differences have the full rank its size permits. A three-distinction agreement of effective rank one equals a pair agreement on all allowed states, because two of the carrier's distinctions always coincide. This accounts for all 24 four-missing 223 cases and all 188 two-missing 233 cases in the original parity archive, and for all 162 and 2,008 more respectively in its unfinished portion. With arbitrary effective rank the exhaustive calculation also permits four missing words for 233 and 333. Those additional shapes were absent on the 1,000 selected starts with the code's chosen holders.

Literal enumeration of all 1,540 disjoint triples on the eight-distinction source above gave 420 individually unread triples with full pair images and 168 full-stage bonds. All 168 have a six-sum. On the three-knot ring, the sole parity birth is (3,4,5) and introduces zero fresh distinctions. Before and after it, there are just 15 disjoint triples, one with three individually unread readings and zero with that property and full pair images. The sum of the three source laws is the birth law. All distinctions then have two holders. [Image and ring counts](parity_checks_results.json)

## Recount and fixes

The original eight timed shards completed 8, 33, 9, 31, 21, 20, 20 and 37 starts. Each is a prefix of its increasing-index shard. Five-knot starts accounted for 40 of these 179 completions and 836 of the 1,000 preselected starts. The preselection sampled uniformly without replacement after excluding the ten pilot starts. Each archive identifier, all 295 stage summaries and all 684 saved examples agree with the independent replay under the original code's choice of holders. [Archive replay](parity_replay_results.json) · [Previously unfinished starts](parity_extension.json)

| Count | Archived 179 | Further 821 | Preselected 1,000 |
| --- | ---: | ---: | ---: |
| Sources with a bond | 125 | 686 | 811 |
| Funded first rounds | 116 | 614 | 730 |
| Funded stages with a bond | 103 | 544 | 647 |
| Source bonds, original holder choice | 61,417 | 433,758 | 495,175 |
| Source bonds, any qualifying holders | 61,469 | 434,164 | 495,633 |
| Grown bonds, original holder choice | 133,238 | 649,330 | 782,568 |
| Grown bonds, any qualifying holders | 133,312 | 650,018 | 783,330 |
| Grown bonds whose chosen holders include a birth | 108,396 | 381,140 | 489,536 |
| Grown bonds with a birth in some qualifying holder set | 109,740 | 386,146 | 495,886 |
| Funded stages with a birth in some qualifying holder set | 99 | 507 | 606 |

1. **Narrowing, which holder set is checked.** In [the local-search definition](../README.md), specify that the implementation keeps the first shortest local holder set before testing its image on the stage. To count all bonds admitting the stated holders, compare every candidate holder set with the stage before deduplication. [The early discard](../ringbond.py) occurs at lines 221–222. On the first grown stage of census row 180, a four-knot source, the carriers (0,10), (2,3,6), (4,5,7) give a direct failure. Holders 0,2,4 exclude 011 alone. Holders 0,1,2,4 exclude 011, 101 and 110, exactly the stage exclusions. All four laws are essential on those holders. Across the original sample the early discard loses 52 source bonds and 74 grown bonds. There are also 1,146 grown carrier triples having equally small qualifying holder sets that disagree on whether they include a birth. Across the complete 1,000 the respective figures are 458, 762 and 5,612. [Direct allowed states and deletions](parity_checks_results.json)
2. **Narrowing, origin in the start.** Replace “Parity's bonds add nothing to the class facts' ‘start's sum of laws’” in [the decision](../decision.md) with “The stage laws determine the agreement image, and each bond has a six-distinction sum of holder laws. A grown bond can require a born law.” On the eight-distinction source above, the three pairs (0,6), (2,12), (7,13) take eight words with the fresh distinctions free. After growth they take 001, 010, 100 and 111. The relevant sum combines (0,1,2,3), (1,6,7) and the born law (3,12,13). It involves two fresh distinctions, so no sum of source laws yields it. The canonical checker verifies the projected holder relation with all eight underlying distinctions forgotten. [Direct image](parity_checks_results.json) · [Knot check](parity_knot.json)
3. **Narrowing, sample weighting.** Replace “Bonds are common under parity: 125 of 179 starts have one at round 0” in [the decision](../decision.md) with “A source bond appeared on 125 of the 179 originally completed starts and on 811 of the complete 1,000-start held-out sample, with at most four holders.” The original 821 omissions are now independently calculated. The 1,000-source denominator belongs to this sample.
4. **Narrowing, the six-loose prediction.** The [earlier predictions entry](../../../docs/ADVISOR_HIVEMIND.md) says “every law essential exactly when the stage has six loose distinctions.” On the original completed stages, 3,213 accepted bonds use every law essentially on stages with two, three, four, five or seven loose distinctions. On the four-knot source (0,1,2,3,4), (0,5,6), (1,2,7), (3,4,8,9), there are five loose distinctions. The carriers (1,5), (0,2,8), (6,7,9) take five words, and removing each of the four laws restores at least one. The six-sum prediction holds separately.

The accelerated census uses the proved six-sum necessity to generate candidates. On the 179 archived starts, the connected holder sets have 742,835,705 disjoint carrier triples counted once per holder set. There were 16,038,753 with a six-sum on linearly independent holder sets, including 4,894,201 with three individually unread readings and all eight words. The original post-search six-sum check had 194,655 accepted bonds. Its zero failures agree with the enumeration independent of that filter above. [Opportunities](parity_replay_results.json)

## Reproduction and limits

The local replay follows the earlier independently written parent-choice and demand rule and recomputes the fresh count with the parity implication on the actual inputs. It checks connected holder sets independently of the study's search. Inclusion and exclusion using ranks give the eight exact word counts. Every holder law is removed in turn. A reading is determined at one knot exactly when all its differences vanish after that knot's values are fixed to zero on the homogeneous difference of two states. The script checks this for every knot. It records both the first-shortest selection and the comparison over every qualifying holder set. Literal assignment tables separately verify the ring, an entire finite source, the exceptional shapes, the wrong holder choice and the new-law example. The study's analysis modules are never imported.

Run from the repository root in one process at a time. The three original high-cost starts took 0.24 seconds together, giving an estimate of 15–18 seconds for the original 179. Five unfinished five-knot cases took 0.22 seconds, giving a 36-second estimate for the other 821. The respective runs took 8.0 and 55.2 seconds with peak memory below 54,000 KiB. The small image classification and literal witness took 0.09 seconds. All classifications and literal checks together took 0.28 seconds, below the one-second estimate. The canonical check and its pilot each took 0.03 seconds.

```sh
ulimit -v 2441406
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
r=research/RING-BOND-20261127-001/referee-R1
.venv/bin/python -B "$r/parity_replay.py" --indices 1 --out "$r/parity_replay_pilot.json"
.venv/bin/python -B "$r/parity_replay.py" --indices 87 133 111 --out "$r/parity_replay_sizing.json"
.venv/bin/python -B "$r/parity_replay.py" --selection completed --out "$r/parity_replay_results.json"
.venv/bin/python -B "$r/parity_replay.py" --indices 3145 4239 5584 6398 7050 --out "$r/parity_extension_pilot.json"
.venv/bin/python -B "$r/parity_replay.py" --selection unrun --out "$r/parity_extension.json"
.venv/bin/python -B "$r/parity_checks.py" --pilot --out "$r/parity_checks_pilot.json"
.venv/bin/python -B "$r/parity_checks.py" --out "$r/parity_checks_results.json"
export PYTHONPATH=tools
.venv/bin/python -B -m knotlab check --cnf 'a b c; a ~b ~c; ~a b ~c; ~a ~b c' \
  --loops a b --contact c --json > "$r/parity_knot_pilot.json"
formula=$(jq -r '.["a grown parity relation needs a born law"]["holder CNF"]' "$r/parity_checks_results.json")
.venv/bin/python -B -m knotlab check --cnf "$formula" --loops a b --contact c \
  --witnesses x0 x1 x2 x3 x6 x7 x12 x13 --json > "$r/parity_knot.json"
.venv/bin/python -B scripts/track.py objects 'parity pair sums carrier readings' \
  --until 2026-11-27 --exclude RING-BOND-20261127-001 --limit 3
```

The other 6,075 census starts, parity holder caps above four, later census growth rounds, and other reading classes were not run here. The subspace count applies to three disjoint agreement carriers of sizes two or three in any finite homogeneous parity system. Extending it to translated affine laws or to wider carriers was not run.
