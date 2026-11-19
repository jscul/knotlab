# How often do pairs carry every later bond reading?

**Pairs sufficed on every continuing stage sampled from either tree weighting.** Under the tree-plus-links weighting, 201 of 228 stages needed pairs and 27 needed triples. The 27 observations came from the same nine starts followed through three ages. In every case the pair reading hid the same kind of exchange between two old distinctions. [Exact stage distribution](../../artifacts/BOND-READING-WEIGHTINGS-20261119-001/BOND-READING-WEIGHTINGS-20261119-001-E001_weightings/distribution.json) · [Proof](../../proofs/BOND-READING-WEIGHTINGS-20261119-001A/BOND-READING-WEIGHTINGS-20261119-001A-P001_certificate/proof.md)

| Starting law | Reached age one / original draws | Stalled before age one | Reached stage observations | Order 0, closed | Order 1 | Order 2 | Order 3 | Pairs suffice among continuing stages |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Uniform labelled tree | 85 / 384 | 299 | 241 | 14 | 0 | 227 | 0 | 227 / 227 |
| Uniform labelled tree plus extra meetings | 76 / 384 | 308 | 228 | 0 | 0 | 201 | 27 | 201 / 228 |
| Uniform recursive tree, then renamed | 105 / 384 | 279 | 298 | 17 | 0 | 281 | 0 | 281 / 281 |

The order is the least number of distinctions that must be read together **now**. Every renaming of the same reached stage preserving those minima and fixing each distinction on every live junction must extend coherently to all later readings of every order. A closed stage has no later reading and receives zero. Each of the 736 continuing observations has a specific exchange preserving all singleton minima and changing an old equation, so each really requires at least two. All 767 observation orders are exact. These are claims about self-renamings of one stage. They do not assert that its table identifies its physical presentation among other starts or that a pair must change next. [Observable and transport criterion](../BOND-READING-SCALE-20261119-001/limiting-reading.md) · [Finite certificates](short_bonds.md)

## Denominators and uncertainty

Each law supplied 64 independent draws at each of six initial sizes. All 1,152 starts were admissible. Only 266 reached the first round, 266 reached the second, and 235 reached the third. The 31 missing at age three had closed at age two. Neither the expansion budget nor a later stall removed any sampled observation. Pooling ages gives each reached stage one observation, so a single start can appear up to three times. [Frozen design](preregistration.md) · [Growth outcomes](../../artifacts/BOND-READING-WEIGHTINGS-20261119-001/BOND-READING-WEIGHTINGS-20261119-001-E001_weightings/sample_summary.json)

For tree-plus-links the estimated share requiring more than pairs is **11.8%, with a 95% whole-draw bootstrap interval of 5.3–19.5%**. Equivalently the share carried by pairs is 88.2% (80.5–94.7%). Nine of the 76 reaching augmented starts needed triples, or 9/384 (2.34%) of all original augmented starts. Each bootstrap replicate resamples entire starting histories within their original size strata. The higher-order share on either pure-tree sample is zero, with empirical interval 0–0 because resampling cannot produce an unseen exception. A separate one-sided 95% bound per pure-tree law is **0.78% per original start** for seeing any order above two by age three under this equal-size mixture. With \(p_m\) the event probability at each chosen size, the probability of zero observed events is \(\prod_m(1-p_m)^{64}\le(1-\overline p)^{384}\). Solving gives \(1-0.05^{1/384}\). This bound uses original draws, including those that stall. [Whole-draw intervals and outcome shares](detail_tables.md)

## Starting size, reached size and age

Each cell below counts first-age reached stages out of 64 starts. Parentheses give how many of those stages required triples.

| Initial junctions | Uniform tree | Tree plus links | Recursive tree |
|---:|---:|---:|---:|
| 4 | 64 (0) | 11 (0) | 64 (0) |
| 6 | 5 (0) | 30 (8) | 5 (0) |
| 8 | 10 (0) | 16 (1) | 18 (0) |
| 12 | 4 (0) | 13 (0) | 14 (0) |
| 20 | 2 (0) | 5 (0) | 4 (0) |
| 32 | 0 | 1 (0) | 0 |

At first age the exact order-two counts were 85/85, 67/76 and 105/105 respectively. Tree-plus-links yielded the same 67 order-two and nine order-three observations at each age. At age two the pure tree laws had 71 and 88 continuing order-two stages, respectively, plus 14 and 17 closures. All their age-three observations had order two. The median and both quartiles of the order were two under every weighting. [Age-specific distributions](detail_tables.md)

Including all ages, uniform trees ranged from 7 to 93 current junctions and 12 to 184 distinctions, with medians 12 and 21. Tree-plus-links ranged from 6 to 103 junctions and 10 to 193 distinctions, with medians 17 and 32. Recursive trees ranged from 7 to 91 junctions and 12 to 180 distinctions, with medians 16 and 27. The order-three cases occupied 10–35 junctions and 19–70 distinctions. In the augmented sample, the order-three share was 17/101 at 10–19 junctions (16.8%, 95% interval 7.4–27.4%) and 10/74 at 20–39 (13.5%, 5.9–23.0%). The largest sampled stages all had order two. Only one start of size 32 reached any round. The detailed tables retain both units, their joint distribution and intervals in each size band. [Size tables](detail_tables.md)

Reaching even one round changes the population. With four initial junctions the exact reaching mass is one under each pure-tree weighting and one quarter under tree-plus-links. At five it is zero for all three. At arbitrary initial size \(m\), a pendant path comprising one leaf and four degree-two junctions forces a first-round deficit. A second-moment count of untouched paths gives an unconditional first-round reach probability \(O(1/m)\) under each of the three laws. This explanation was derived after observing the attrition. It supplies no asymptotic order distribution conditional on reaching. [Exact four- and five-junction populations](controls.md) · [Reach theorem](which_starts_reach.md)

## Which structure distinguishes the exceptions?

All 12 distinct stage shapes requiring triples had four exhausted junctions \(A,B,C,D\) meeting once along \(AC,AD,BC,BD,CD\). The junctions \(C,D\) met nothing else. The connected remainder could separate \(A,B\) by one distinction. Exchanging \(AC\) and \(BD\) fixes the growing end and preserves the complete pair reading. It sends the three-distinction equation at \(C\) to a set that crosses the \(B,C,D\) cycle oddly. This proves a pair failure at every size under those hypotheses, provided a strict successor exists. On these 12 shapes, a separate certificate proves that triple readings suffice. In contrast, an archived 13-junction, 91-distinction stage needs at least four. [Exchange proof and 12 exact upper bounds](short_bonds.md) · [Larger control](controls.md)

For a positive all-size class, consider an available simple tree start under the frozen loose-count rule in which every first-round group with multiple parents uses tree leaves only. The least first-age order is exactly two, even for a later pair target. Fixed distinctions on the newborn junctions identify the old spokes, and two fixed outlets beyond each backbone position identify the remaining names. This class covers **21/85**, **0/76** and **29/105** first-age observations in the three laws. Its subclass with no degree-two site covers 20, 0 and 28, and the narrower construction attaching two or three pendants at every backbone leaf covers 5, 0 and 5. A separate exact criterion for a reached ordinary graph that is itself a tree allows arbitrary meeting multiplicities. All three sampling laws have an ordinary cycle by the first successful round, so that criterion has zero positive-age coverage here. [Structural classes and boundary cases](structural.md) · [Counts by initial size](detail_tables.md)

Attachment counts alone did not distinguish the exceptions. In the augmented sample, stages with 3–5 older junctions meeting the live end had both orders (86 at two and 15 at three), while all 23 stages with at least ten such junctions had order two. The table gives the chance that the feature ranks a continuing order-three observation above an order-two observation, with half credit for a tie. Matched comparisons use only observations at the same initial size and age. The pure-tree samples had no order-three observation for this comparison.

| Feature on the augmented sample | Overall AUC | Matched AUC |
|---|---:|---:|
| Current junctions | .483 | .816 |
| Current distinctions | .507 | .846 |
| Older junctions meeting the live end | .441 | .604 |
| Most older neighbors of one live junction | .475 | .486 |
| Most attachments of one older component | .473 | .581 |
| Movable distinctions | .417 | .591 |
| Number of equal-singleton exchanges that change an equation | .383 | .296 |
| Unresolved by the directed minimum-bond certificate | .925 | .916 |

Every continuing stage had at least one harmful equal-singleton exchange. Counting them adds information about ambiguity, but a larger count did not predict the need for triples here. The directed certificate left 57 augmented and two recursive observations unresolved. Pair information restricted to bonds of size at most five resolved all 32 remaining order-two observations. The resulting unresolved indicator matched all 27 order-three observations (AUC 1.000 in both comparisons), whose verdicts were proved separately using the full pair exchange and the triple upper bound. These are in-sample comparisons on nine exceptional draws. Certificate success is a mathematical guarantee. Certificate failure alone carries no higher-order verdict. [Predictor measurements](../../artifacts/BOND-READING-WEIGHTINGS-20261119-001/BOND-READING-WEIGHTINGS-20261119-001-E001_weightings/distribution.json) · [Pair certificate](pair_certificate.md) · [Supplementary count definition](detail_tables.md)

The exact small-population controls enumerated all histories at four and five start junctions. Independent exact reading measurements agreed on 287 distinct sampled observation keys drawn from those controls and a prespecified small-stage audit. The short-bond computation was checked against complete connected-shore enumeration on nine candidate shapes within its audit limit, including uncapped comparisons on seven of the 12 shapes requiring triples. No final sampled order is a cutoff-based guess. Population estimates remain specific to the three initial laws, their equal mixture of the six sizes and the first three reached ages. General parity starts admit higher orders, and the true distribution among large surviving starts remains open. [Control coverage](controls.md) · [Short-bond validation](short_bonds.md) · [Worst-case size bounds](../BOND-READING-SCALE-20261119-001/limiting-reading.md)
