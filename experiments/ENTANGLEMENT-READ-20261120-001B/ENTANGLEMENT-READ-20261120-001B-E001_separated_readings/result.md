# Exact separated readings of ordinary growth

The largest external CHSH score was **1106/855**. The largest embodied score was **2**. Both maxima came from the not-all-equal pair-pattern reading. The run covered 694 fixed placements on 33 starts and their first grown stages under parity and not-all-equal. The common-state bound for external settings is established separately. These are exact finite counts, with independent referee review pending.

## What was measured

All 33 starts passed K1–K3 under both laws with the full stated law on each displayed support. The two laws produced identical complete first stages in this cohort. Every displayed support remained eligible. The producer checked the list of joins and the next demand against the original growth implementation. It recorded the distinctions consumed by each birth and the fresh distinctions it received. The projection onto the old distinctions stayed the same in all 66 grown presentations.

The cohort comprises three minimum controls, a six-knot funded chain, two five-knot rings, 12 labelled tree draws with their 12 matched extra-loose starts, and three archived starts selected for past jumps. The draws are equally weighted within each four-draw size and funding group. The three archived starts have equal weight in their own group. The two six-knot archived starts that eventually end after a burst made 8 and 10 first-stage births. The seven-knot start with proved unbounded births under parity made 15. This run reads the first stage of each lineage under both laws. The archive and its prior parity proofs supply the later growth evidence.

| Cross steps | All measured placements | With a newborn distinction |
| --- | ---: | ---: |
| 2 | 366 | 128 |
| Finite, at least 3 | 316 | 124 |
| No chain | 12 | 4 |
| **Total** | **694** | **256** |

There were 376 placements with two marked pairs and 318 with six marked distinctions. Each law contributed half of each count. The measurement retained one placement per populated band, origin, and reading size. Of 4,739,066 candidates in the declared orientation, 298,674 repeated a mark, 1,410,172 had a cross step of one, and 3,030,220 were eligible. There were 890 empty placement slots and no empty embodied setting cells on the retained placements. A marked tuple with several supporting knot pairs contributes once for each supporting pair.

## Scores and marginals

I reads the selected distinction. II returns one exactly when both marked distinctions equal the setting. U weights the complete allowed assignments equally. L gives each complete start assignment equal mass and divides it equally over its extensions. T gives twice the U mass to assignments with Alice's first marked distinction equal to one. The table gives the maximum over measured placements and over the eight odd-minus CHSH signs. There were 347 external placements and 159 embodied placements per law and weighting.

| Law | Weighting | External I | External II | Embodied I | Embodied II |
| --- | --- | ---: | ---: | ---: | ---: |
| Parity | U | 0 | 1 | 0 | 1 |
| Parity | L | 0 | 1 | 0 | 1 |
| Parity | T | 0 | 1 | 0 | 4/3 |
| Not-all-equal | U | 122/285 | 22/19 | 163/410 | 2 |
| Not-all-equal | L | 4/9 | 32/27 | 146/273 | 2 |
| Not-all-equal | T | 122/285 | 1106/855 | 3988/6831 | 2 |

The embodied not-all-equal score of 2 is reached when both reader supports are ternary. Each one forbids the pair taking the selector's own value on both marks, so both answers to II are always zero. On the two ternary parity knots that share one unmarked distinction, each I context has counts `(2,2,2,2)` and each II context has `(5,1,1,1)` in `00,01,10,11` order under U. I factors into its local marginals. II has total variation (1/8) from that reading's product of marginals. There were 20 parity placements with I independent in all four external contexts and II dependent in at least one, under each weighting.

Every external outcome marginal and full local pair marginal was unchanged across the other setting. The no-chain controls factored under U, L and T, both before and after conditioning on the two selectors. In the parity samples, the embodied marginal changes also vanished even where conditioning moved the joint distribution of the marked pairs by total variation (3/4). In not-all-equal under U, the largest embodied full-pair marginal change was (919/6862), over both observers and both fixed own settings. The largest variation between the conditioned and common distribution of the two pairs was (27628/81991). The raw record also includes total variation on all six marks, including the selectors.

Among the 233 first-stage placements per law, U on not-all-equal changed the probabilities of the marked old distinctions in 221, with total variation up to (434/2565) from U on the start. L preserved their probabilities in all 233. The support stayed the same in every comparison. U and L agreed under parity because all start assignments had the same number of extensions.

## Replay

The initial allocation follows the supplied order of the recorded meetings. The ordinary engine processes the groups of at least three in lexicographic parent order, then uncovered pairs in lexicographic order, and then the stored loose remainder of each live knot. Each use takes the next loose distinction of its parent. Reader supports are ordered by their sorted literal distinctions. Alice gets the earlier support, each marked pair is in ascending order, and selectors are tried in ascending order after each pair. The two minimum two-knot specimens use the specified marks. Eligibility and all chosen placements were computed before measuring any score. The sampled maxima are for these choices.

`exact_readings.json.gz` contains literal supports, support certificates, placement counts and exclusions, joint counts including zeros, exact common-unit denominators, both marginal tests, and all four correlations and eight CHSH scores. The histogram order is Alice's (u,v) and possible selector, followed by Bob's marks in the same order. `summary.json` gives coverage and ranges by source group, law, growth stage, cross-step band and origin. Means of defined scores use equal weight among the measured sources and give the count alongside the predetermined source denominator.

```sh
study=experiments/ENTANGLEMENT-READ-20261120-001B/ENTANGLEMENT-READ-20261120-001B-E001_separated_readings
.venv/bin/python -B "$study/run.py"
.venv/bin/python -B "$study/verify.py"
```

The full run took 1.84 seconds with peak RSS 145,292 KiB. The first raw measured placement was available in 0.37 seconds from the start of cohort preparation, with substantive computation dominating that interval. The verifier took 5.14 seconds and checked the 4,739,066 candidate placements and 2,082 weighted tables. It independently counted all 30 measured minimum-control placements by enumeration and 12 histograms from the three archived sources by inclusion and exclusion. A replay with a different Python hash seed reproduced both output files byte for byte. The regular cohort supplies measured contrasts for the common-state argument. The separate targeted control tests embodied settings on a construction with shared pair constraints.
