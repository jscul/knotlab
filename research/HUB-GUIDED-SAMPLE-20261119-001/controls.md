# Exact-roster and blind-count controls

The controls use exact next-round births from the same parity law as the main study. They include the complete partnered rosters, the two archived single-block bursts, every pre-tail age of start-00 and start-04, and the exact round-seven stage of start-03. The independent control reader lists literal maximal candidate sets, removes the held sets, counts residual pairs and checks unused loose distinctions. It also matches all 28,065 literal next parent sets on start-03. [Control rosters, hashes and exact totals](../../artifacts/HUB-GUIDED-SAMPLE-20261119-001/HUB-GUIDED-SAMPLE-20261119-001-E001_sampler/control_rosters.json)

## Exact shape selection

The complete partnered recognizer tests the complement of the candidate relation on **all** live names. It requires exactly one noncandidate partner per name. For \(k\) pairs with \(k\ge3\), its maximal candidate sets are the \(2^k\) transversals. Each full transversal held by a supplied block is removed once. A compatible pair becomes residual exactly when all \(2^{k-2}\) transversals through it are held. The resulting demand at each point counts its unheld transversals and its residual partners. The two-pair case consists of four pair groups. The recognizer rejected a missing candidate relation and preserved the full group support under an arbitrary renaming. A control with two held transversals forced one residual pair. When all eight transversals were held, all 12 compatible pairs remained as births.

With one block holding every live name, the next joint groups are all unordered pairs. Any unused loose distinctions supply unary births. When a block of \(b\) names has exactly \(b-1\) loose distinctions at each name, the full binomial tail applies. From a level indexed by \(k\)-subsets, each new \((k+1)\)-subset names the group of its \(k+1\) parent subsets; the birth count is \(\binom b{k+1}\). A uniform subset draw therefore has inverse probability \(\binom b{k+1}\). Every level of the nine-name control was checked against the literal group sets. The 781-name start-04 block gives 304,590 next births. The last binomial transition has one birth and zero fresh distinctions. The closed roster after it has zero births.

For a paired roster, drawing one uniform eligible integer and skipping the held transversal words samples the actual unheld groups uniformly. The same group-index sampler handles exact residual pairs and the named slots of repeated unary births. In each selected stratum the inverse probability is the size of that stratum. Literal support enumeration confirmed the rank map where the population is small. The controls include six, eight, ten and 24 live names on the order-three partnered history, with next births **8, 10, 24 and 4,086**, and the order-four and order-five controls. [Exact formulas and uniform-draw checks](../../artifacts/HUB-GUIDED-SAMPLE-20261119-001/HUB-GUIDED-SAMPLE-20261119-001-E001_sampler/control_hybrid_checks.json)

Exact-class count spread is fixed by that uniform weighting. The same draws estimated how many births consume a distinction from live name zero; those marked totals vary across runs and are compared to its exact loose count. This tests the sampled names in addition to their constant weight.

## Blind count and structural marks

The independent baseline makes one uniform child choice at each split in a disjoint maximal-set search. It returns the product of the split sizes for an unheld maximal group with at least three parents, and zero on other leaves. Each counted group occurs on one path. The path probability and inverse weight cancel, giving theoretical bias zero for a count and for any marked total. Direct enumeration checked the sampled support and the exact second moment on the 20 rosters within its literal audit cap.

For each large group the markers record its parent count reaching four, at least two of its names outside every one current maximal block, and whether it meets every pair of one explicitly certified partnered part. The part is chosen using only the candidate relation. Its literal pairs and each exact marked count are in the artifact. For instance, the age-seven start-04 part has two pairs and is met across both pairs by **138 of 781** large groups. The weighted outputs estimate totals in the unheld large-group stratum. A ratio of two estimated totals would need its own analysis.

On each of the 23 fixed rosters the baseline used 32 independently seeded batches. Its 64-draw and 256-draw results use nested prefixes within each batch. At age six of start-04 the 256-draw estimates had mean **761.04** against **1,015**, with empirical central spread **9.20-fold**. At age seven the mean was **766.03** against **781**, with spread **30.83-fold**. On start-03 age seven the same blind design averaged **9,376.65** against **28,008** unheld large groups, with a **16.35-fold** spread. Only 20 large groups met both pairs of its chosen partnered part, and 14 batches had zero weighted observations of that mark. These examples separate empirical spread from accuracy and formal unbiasedness. Zero-weight draws remain in every batch. The exact residual-pair and offshoot counts are recorded separately. [Blind estimates, exact truths and structural marks](../../artifacts/HUB-GUIDED-SAMPLE-20261119-001/HUB-GUIDED-SAMPLE-20261119-001-E001_sampler/control_blind_checks.json)

## Generic kernel calibration

The actual generic kernel was run blind on each of those 23 rosters, with 32 independent seeds at each width and policy. It received only the block file and the pilot settings. It estimates all maximal candidate sets, including held maxima and isolated names. For each control we retain that raw estimate and separately show the birth estimate after subtracting the exact held and isolated counts and adding the exact residual pairs and offshoots. These additions and subtractions are control information. The reported empirical spread uses 2.5th and 97.5th percentiles with linear interpolation.

There were 92 settings across both policies and both widths. Eighty-three exhausted the search frontier without thinning and gave the exact counts. The remaining nine used randomized thinning. Selected genuinely sampled birth estimates follow.

| Control age | Policy | Width | Exact births | Mean of 32 | Central 95% spread |
| --- | --- | ---: | ---: | ---: | ---: |
| start-04 age 6 | hub | 64 | 1,015 | 1,015.69 | 1.014× |
| start-04 age 7 | hub | 64 | 781 | 782.38 | 1.062× |
| start-04 age 7 | partner | 64 | 781 | 786.78 | 1.354× |
| start-03 age 7 | hub | 64 | 28,065 | 31,550.06 | 8.022× |
| start-03 age 7 | partner | 64 | 28,065 | 26,998.84 | 4.237× |
| start-03 age 7 | hub | 256 | 28,065 | 26,960.25 | 1.670× |
| start-03 age 7 | partner | 256 | 28,065 | 27,451.91 | 1.412× |

At start-03 age seven the exact correction is \(28,099-91+56+1=28,065\). The kernel settings here used a local exact cutoff of six and omitted component factorization and the initial twin quotient to expose randomization on these controls. The seeds are outside the reserved validation range. These are pilot controls on known stages. [Actual kernel runs, exact integer weights and signed errors](../../artifacts/HUB-GUIDED-SAMPLE-20261119-001/HUB-GUIDED-SAMPLE-20261119-001-E001_sampler/control_generic_kernel.json)
