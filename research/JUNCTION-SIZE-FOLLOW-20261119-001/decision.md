# Junction size along one start

**A finite start can have unbounded exhausted junction size.** The order-three partnered start has successive birth sizes $8,16,2048,2^{2042},\ldots$. Every round is lawful and makes the previous live junctions exhausted. The one-block cases have a finite support bound throughout their much larger later populations. The full touch census exceeds the earlier sparse probe’s ceiling of eight. [All-age proof and reading consequence](size_proof.md)

For a birth taking $p$ parents and making $f$ fresh distinctions, the support size is $p+f$. We counted the largest birth, largest parent count, largest support among all current junctions, and largest exhausted support separately. Initial arities are included in the current and exhausted measures. A live support enters the exhausted measure at the next complete round. A row born with no fresh distinction is already exhausted. [Frozen design](preregistration.md)

## Full touch census

All **26,441** starts were followed through round **15** or a natural stop. There were **289,359** positive-age observations in the extension to round 24. Of the initial starts, **11,010** stalled in round one, **3,726** had closed by the end of the probe or were already closed, **11,700** reached round 24, and **five** hit explicit computation caps after complete ages 15, 17, 22, 22 and 22. The caps stopped recording a round before its fresh counts had all been established.

| Complete age | Stages reached at that age | Largest current support | Largest exhausted support |
| ---: | ---: | ---: | ---: |
| 1 | 15,197 | 13 | 5 |
| 2 | 13,588 | 13 | 13 |
| 10 | 11,705 | 15 | 14 |
| 15 | 11,705 | 20 | 19 |
| 24 | 11,700 | 14 | 14 |

The rows show the population present at each age. The last row excludes earlier terminal and capped trajectories. On their observed histories, **69** starts exceed eight in exhausted size, **28** set a new personal exhausted-size record after age three, and **13** do so after age ten. Two do so as late as age 23. [Census summary, per-age counts and caps](../../artifacts/JUNCTION-SIZE-FOLLOW-20261119-001/JUNCTION-SIZE-FOLLOW-20261119-001-E001_growth/probe_summary.json)

The largest measured birth support was **20** for census key `26174`. Its five arity-five junctions meet once at each adjacency of a classical five-cycle, with three loose distinctions each. The first 15 birth populations are five times the Fibonacci numbers beginning at 2 and end at 7,985. The largest birth support is $t+5$ at each measured age $t$. The size-20 births each have **two parents and 18 fresh distinctions**. The largest parent count in that round is nine. At age 15 the full stage has 20,895 junctions and 181,425 distinctions. The next round would make 12,920 junctions, above the explicit 12,000-birth budget. The observed formulas describe the checked prefix. [Exact roster histories and census keys](../../artifacts/JUNCTION-SIZE-FOLLOW-20261119-001/JUNCTION-SIZE-FOLLOW-20261119-001-E001_growth/probe_census.json.gz)

The compact calculation grouped the original starts into 1,515 equivalent live rosters, using only exact permutations of open counts and maximal blocks. Every distinct roster agreed with the archived independent roster engine through six rounds or a terminal event. Literal birth counts also agreed with 8,268 overlapping round entries in the earlier physical census and with all 14,736 overlapping natural endings. Repeated exact rosters give certified periodic birth rows for 2,081 starts, and the one-block rule gives exact continuation for 1,015. [Independent census checks](../../artifacts/JUNCTION-SIZE-FOLLOW-20261119-001/JUNCTION-SIZE-FOLLOW-20261119-001-E001_growth/probe_census_check.json)

## Larger starts under three named weightings

The sample has **64 starts at each of five initial sizes** per weighting, 320 per weighting and **960** total. Every sampled start is admissible. Every reaching start continues through the full 24 rounds, with no cap or closure. Every other sampled start stalls in the first round.

| Weighting | Reach at initial sizes 6, 8, 12, 20, 32 | Reached out of 320 | First-round stalls out of 320 |
| --- | --- | ---: | ---: |
| Uniform labelled tree | 5, 7, 4, 1, 0 | 17 | 303 |
| Uniform recursive tree, then uniform naming | 6, 17, 9, 0, 0 | 32 | 288 |
| Uniform labelled tree plus extra meetings | 23, 16, 15, 9, 2 | 65 | 255 |

Across these 114 reaching histories and their **2,736** positive-age observations, the largest birth support is **four**. The initial arities belong to a different count. One initial exhausted junction has size nine in a recursive start of 32 junctions, and that start stalls. The sample gives separate finite observations under the three laws. [Sampled starts and growth histories](../../artifacts/JUNCTION-SIZE-FOLLOW-20261119-001/JUNCTION-SIZE-FOLLOW-20261119-001-E001_growth/probe_samples.json.gz)

## Infinite growth and finite bursts

The partnered recurrence gives $N_0=6$ live junctions, $N_1=8$, and $N_{t+1}=2^{N_t/2}-N_{t-1}$. A birth at round $t$ has $p=N_{t-1}/2$ and $f=2^{N_t/2-1}-p$, so its support has size $2^{N_t/2-1}$. A second physical realization, with 18 junctions and 60 distinctions initially, independently replays the first three rounds with $(p,f)=(3,5),(4,12),(5,2043)$ and populations 8, 10 and 24. Later partnered values use the proved recurrence. The order-two partnered control has four births of size four per round, literally checked through ten rounds. [Partnered and four-junction-roster controls](../../artifacts/JUNCTION-SIZE-FOLLOW-20261119-001/JUNCTION-SIZE-FOLLOW-20261119-001-E001_growth/probe_paired.json) · [WALL-READ theorem](../../proofs/WALL-READ-20261119-001A/WALL-READ-20261119-001A-P001_partnered/proof.md)

Once all $b$ live junctions occupy one block and each has exactly $b-1$ loose distinctions, the succession is indexed by the $k$-subsets, $2\le k\le b$. The population at that level is $\binom bk$, and each birth has $k$ parents and $b-k$ fresh distinctions. The sole final row is implied and exhausts the remaining loose distinctions. The tail’s support size is exactly $b$ throughout.

For archived `start-00`, a block of nine appears at age 14, where a birth of $309+8=317$ distinctions attains the all-age maximum. The tail closes at age 22. For `start-04`, a block of 781 appears at age eight, where a birth of $974+780=1754$ distinctions attains the all-age maximum. At age nine the tail has 304,590 births of size $2+779=781$, and it closes at age 788. The first four physical rounds of each start were independently replayed. Their exact roster prefixes match all archived parent and population counts. [Replay and exact tails](../../artifacts/JUNCTION-SIZE-FOLLOW-20261119-001/JUNCTION-SIZE-FOLLOW-20261119-001-E001_growth/probe_merge.json) · [Archived finite bursts](../MERGE-BURST-20261119-001/merge_burst.md)

The sixteen starts below were selected in the earlier study by a large increase in round population. The table uses the latest archived age for which full birth sizes were determined, including the eight checked single-block tail rounds for `start-00`. Each displayed sum is the support of an actual birth attaining the observed maximum. The 14 other explosive growths outside the two finite tails remain unresolved past their evidenced prefixes.

| Archived start | Latest archived age with complete birth sizes | Peak observed birth support and its age |
| --- | ---: | --- |
| `start-00` | 22 | 309 + 8 = **317**, age 14 |
| `start-01` | 9 | 145 + 3,148 = **3,293**, age 9 |
| `start-02` | 8 | 17 + 102,475 = **102,492**, age 8 |
| `start-03` | 7 | 12 + 17,207 = **17,219**, age 7 |
| `start-04` | 8 | 974 + 780 = **1,754**, age 8 |
| `start-05` | 8 | 17 + 102,475 = **102,492**, age 8 |
| `start-06` | 6 | 42 + 8,028 = **8,070**, age 6 |
| `start-07` | 6 | 10 + 22,693 = **22,703**, age 6 |
| `start-08` | 8 | 17 + 102,475 = **102,492**, age 8 |
| `start-09` | 5 | 9 + 2,420 = **2,429**, age 5 |
| `start-10` | 6 | 15 + 3,637 = **3,652**, age 6 |
| `start-11` | 6 | 20 + 3,067 = **3,087**, age 6 |
| `start-12` | 6 | 19 + 23,396 = **23,415**, age 6 |
| `start-13` | 6 | 10 + 23,541 = **23,551**, age 6 |
| `start-14` | 7 | 14 + 70,421 = **70,435**, age 7 |
| `start-15` | 7 | 11 + 20,264 = **20,275**, age 7 |

Later parent-only records give lower bounds on support size at those ages. They remain marked separately in the archive. [All sixteen archived maximum-size traces](../../artifacts/JUNCTION-SIZE-FOLLOW-20261119-001/JUNCTION-SIZE-FOLLOW-20261119-001-E001_growth/archive_maxima.json)

## What the size bound gives the reader

Theorem M gives a sufficient reading at any observed stage. Read through the largest current junction size and supply the growing end to carry the current equation span and every future stage under a self-renaming. A uniform all-age support bound therefore gives one fixed sufficient order throughout that start. The proved unbounded partnered sizes show that the sufficient order obtained this way can grow without bound. The least sufficient order for those partnered stages remains open. Comparing distinct stages uses a common bound or a separate rank check. [Size bound and its quantifiers](size_proof.md)
