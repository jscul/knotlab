# The same two-block proposal across the other unread histories

The transfer panel uses the latest archived source for each of the thirteen histories other than start-03. Each panel fixes 128 particles and 16 independent replicates, with no mutation. The extension inserts the remaining junctions in ascending candidate-degree order, with order seed 73,121 for ties. Sampling seeds begin at 202611238000 plus 64 times the history number. Each announced source retains its own next-round target. [Input manifests](inputs.md) · [Panel observations](../../artifacts/HUB-GUIDED-SAMPLE-20261119-001/HUB-GUIDED-SAMPLE-20261119-001-E001_sampler/prefix_targets.json)

## Exact prefix weighting

First fold literal junctions with equal closed neighborhoods in the candidate graph. They occur together in every maximal candidate set, and each quotient set lifts uniquely by including every member of each chosen class. The exporter uses block incidence to form one neighborhood union at a time and checks equality after a hash hit. It preserves the literal-to-quotient map. The largest input that needs a 32-bit junction index uses an isolated build of the same extension code. Its only index change is the width of the index type.

The seeded prefix is the largest quotient block \(B\) together with up to 14 outsiders from the largest second block containing any outsiders. The selected outsiders have distinct exclusion sets in \(B\), in ascending quotient name order. They are mutually joinable. For an outsider \(s\), let \(E(s)\) be the names in \(B\) that cannot join it. Any subset of outsiders determines the union \(U\) of its exclusion sets. Its maximal candidate set contains exactly \(B\setminus U\) and all outsiders with \(E(s)\subseteq U\). Those extra outsiders keep the same union. Distinct unions give distinct maximal candidate sets, and every maximal candidate set in the prefix has this form. Grouping names of \(B\) by their membership in the exclusion sets preserves the unions and keeps the rank computation compact.

The bank samples those distinct union ranks uniformly and assigns the exact count of the prefix sets as initial mass. The existing packed prefix extension gives each later maximal set a unique parent, then applies unbiased resampling with the retained exact integer factors. The report reconstructs the resulting estimates as rational numbers. The displayed central ranges are empirical 2.5th and 97.5th percentiles with linear interpolation. [Implementation](../../experiments/HUB-GUIDED-SAMPLE-20261119-001/HUB-GUIDED-SAMPLE-20261119-001-E001_sampler/prefix_targets.py)

To obtain births, subtract the exact held and isolated counts and add the exact offshoot count and the residual pairs. The report uses full residual certificates when available. Otherwise it pairs the prefix replicates with the first 16 independent residual-pair batches and also retains the deterministic correction bracket. The raw maximal-set estimate is visible alongside the corrected birth estimate. [Independent pair correction](../../artifacts/HUB-GUIDED-SAMPLE-20261119-001/HUB-GUIDED-SAMPLE-20261119-001-E001_sampler/pair_corrections.json)

## Calibration

The order-three partnered control gives eight in every replicate. The 16-bit and 32-bit builds agree exactly. An independent power-set enumeration matches both prefix sets on this control. Another control folds equal closed neighborhoods whose literal block memberships differ.

| Source | Exact next births | Mean estimate | Observed relative mean error | Central empirical factor |
|---|---:|---:|---:|---:|
| start-02 age 9 | 1,061,953 | 950,396 | −10.50% | 2.24 |
| start-05 age 9 | 1,061,953 | 1,070,735 | +0.83% | 2.40 |
| start-08 age 9 | 1,061,953 | 1,017,304 | −4.20% | 2.11 |
| start-03 age 7 | 28,065 | 20,790 | −25.92% | 120.59 |
| start-04 age 7 | 781 | 775.49 | −0.71% | 2.34 |

The near-dominant-block truth is an exhaustive count shared by three exactly relabeled sources. Their panels use independent seeds. The two earlier controls use distinct seeds beginning at 202611239103 and 202611239104. Every known truth falls within its panel's empirical central range. The start-03 age-seven spread shows why the small empirical spread on the near-dominant histories does not transfer automatically to a different growing end. [Exhaustive near-block count](../../artifacts/HUB-GUIDED-SAMPLE-20261119-001/HUB-GUIDED-SAMPLE-20261119-001-E001_sampler/near_block_02.json) · [Earlier control panels](../../artifacts/HUB-GUIDED-SAMPLE-20261119-001/HUB-GUIDED-SAMPLE-20261119-001-E001_sampler/prefix_targets_controls.json)

## Transfer results

All thirteen panels completed all 16 scheduled replicates. Four panels have an empirical factor below ten, representing two distinct inputs once the three near-dominant relabelings are identified. The residual correction is exact for twelve panels. For start-14, the 4,096 independent residual-pair draws in the panel had zero hits. Even the full deterministic range of possible residual corrections leaves the empirical factor between \(4.3787\times10^8\) and \(4.4042\times10^8\). [Results with all exact weights and correction sources](../../artifacts/HUB-GUIDED-SAMPLE-20261119-001/HUB-GUIDED-SAMPLE-20261119-001-E001_sampler/prefix_targets.json)

| Source | Target round | Quotient size | Mean births | Central empirical factor |
|---|---:|---:|---:|---:|
| start-01 | 11 | 21,516 | 192,824 | 600.27 |
| start-02 | 10 | 354 | 950,396 | 2.24 |
| start-05 | 10 | 354 | 1,070,735 | 2.40 |
| start-06 | 8 | 10,392 | \(4.3204\times10^{12}\) | 5,979.88 |
| start-07 | 8 | 15,583 | \(5.7498\times10^8\) | 25,603.81 |
| start-08 | 10 | 354 | 1,017,304 | 2.11 |
| start-09 | 7 | 4,639 | \(2.1956\times10^6\) | 513.78 |
| start-10 | 8 | 2,049 | 840,581 | 13.85 |
| start-11 | 8 | 877 | 54,138 | 4.88 |
| start-12 | 8 | 29,187 | \(1.1649\times10^9\) | 2,763.99 |
| start-13 | 8 | 33,337 | \(1.1293\times10^7\) | 998.47 |
| start-14 | 9 | 161,870 | \(7.7070\times10^{19}\) | \(4.4042\times10^8\) |
| start-15 | 9 | 33,593 | \(1.7309\times10^{12}\) | 87.08 |

## Wide-stage execution

Start-14 has 161,870 true-twin classes, so its run uses 32-bit names. Its initial prefix has 70,182 classes and exactly 76 maximal candidate sets. The serial job completed three fixed replicates. Four more finished with four processes sharing one read-only graph and validating each clique directly. The final nine use the same shared graph and validate their original bank slices by checking the full compatible part of the largest block and blocking every omitted outsider. Both parts are certified cliques, so these conditions characterize maximality in this prefix. The reader uses the original seed and bank rows for every replicate. Both parallel readers matched five complete records from the start-02 bank with the 16-bit serial output, including all resampling factors. The final reader also reproduced all seven earlier start-14 records exactly. [Scheduling implementation](../../experiments/HUB-GUIDED-SAMPLE-20261119-001/HUB-GUIDED-SAMPLE-20261119-001-E001_sampler/prefix_targets_continue.py) · [Native wrapper](../../experiments/HUB-GUIDED-SAMPLE-20261119-001/HUB-GUIDED-SAMPLE-20261119-001-E001_sampler/prefix_targets_parallel.cpp)

The result archive preserves the literal-to-quotient maps and the sources used to compile both integer widths. The input manifests bind each starting stage. The separate control file preserves the two earlier calibration panels. [Archived mappers and engine sources](../../artifacts/HUB-GUIDED-SAMPLE-20261119-001/HUB-GUIDED-SAMPLE-20261119-001-E001_sampler/prefix_targets_inputs.tar.gz)
