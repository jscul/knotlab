# Frozen addressed-census summary

Registered coverage is complete.

W weights are ordinary empirical fair-coin draw frequencies. Code lengths are never multiplied into those frequencies.

## Coverage and validation

| Population | Draws present | Registered draws | Draws with complete key |
| --- | --- | --- | --- |
| W | 40000 | 40000 | 28770 |
| E | 19416 | 19416 | 19416 |

Coverage complete: True. Validation: passed_with_skipped_ambiguous_assertions. Required core gate checks passed: True. All assertions passed: False.
Validation record: /home/jscul/p-vs-np-contact-first/experiments/ADDR-KNOTS-20261113-001A/ADDR-KNOTS-20261113-001A-E001_addressed_census/codex/validation.json. The master validation explicitly reports skipped ambiguous assertions; this is not an all-assertions pass.
Missing keys, rejected draws, duplicate identities, and record errors are retained in summary.json.

Solver budgets: 287 null level verdicts in 125 complete keys; 47 FU keys. A later null preserves an already determined F1 or F2.

## Fate shares

| Population | Condition and unit | Denominator | F0 | F1 | F2 | F3 | FU | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| W | raw distinct patterns | 3990 | 0.0003 | 0.0000 | 0.0787 | 0.9173 | 0.0038 | computed |
| W | accepted draw frequencies | 28770 | 0.7998 | 0.0000 | 0.0109 | 0.1887 | 0.0005 | computed |
| W | all W draw mass | 40000 | 0.5753 | 0.0000 | 0.0078 | 0.1358 | 0.0004 | computed |
| W | s >= 2, distinct | 3989 | 0.0000 | 0.0000 | 0.0787 | 0.9175 | 0.0038 | computed |
| W | s >= 2, draws | 5759 | 0.0000 | 0.0000 | 0.0545 | 0.9429 | 0.0026 | computed |
| W | s >= 3, distinct | 3493 | 0.0000 | 0.0000 | 0.0764 | 0.9196 | 0.0040 | computed |
| W | s >= 3, draws | 3641 | 0.0000 | 0.0000 | 0.0733 | 0.9228 | 0.0038 | computed |
| W | [0, 1), distinct | 1388 | 0.0007 | 0.0000 | 0.0000 | 0.9993 | 0.0000 | computed |
| W | [0, 1), draws | 25056 | 0.9184 | 0.0000 | 0.0000 | 0.0816 | 0.0000 | computed |
| W | [1, 1.5), distinct | 791 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | computed |
| W | [1, 1.5), draws | 1722 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | computed |
| W | [1.5, 2.1), distinct | 662 | 0.0000 | 0.0000 | 0.0000 | 0.9970 | 0.0030 | computed |
| W | [1.5, 2.1), draws | 813 | 0.0000 | 0.0000 | 0.0000 | 0.9975 | 0.0025 | computed |
| W | [2.1, 3), distinct | 503 | 0.0000 | 0.0000 | 0.0775 | 0.8966 | 0.0258 | computed |
| W | [2.1, 3), draws | 528 | 0.0000 | 0.0000 | 0.0739 | 0.9015 | 0.0246 | computed |
| W | [3, 4.5), distinct | 312 | 0.0000 | 0.0000 | 0.2372 | 0.7628 | 0.0000 | computed |
| W | [3, 4.5), draws | 316 | 0.0000 | 0.0000 | 0.2342 | 0.7658 | 0.0000 | computed |
| W | [4.5, infinity), distinct | 334 | 0.0000 | 0.0000 | 0.6018 | 0.3982 | 0.0000 | computed |
| W | [4.5, infinity), draws | 335 | 0.0000 | 0.0000 | 0.6000 | 0.4000 | 0.0000 | computed |
| E | raw distinct patterns | 8937 | 0.0001 | 0.0000 | 0.1674 | 0.8289 | 0.0036 | computed |
| E | accepted draw frequencies | 19416 | 0.3865 | 0.0000 | 0.0772 | 0.5347 | 0.0016 | computed |
| E | s >= 2, distinct | 8937 | 0.0001 | 0.0000 | 0.1674 | 0.8289 | 0.0036 | computed |
| E | s >= 2, draws | 19416 | 0.3865 | 0.0000 | 0.0772 | 0.5347 | 0.0016 | computed |
| E | s >= 3, distinct | 8550 | 0.0000 | 0.0000 | 0.1699 | 0.8263 | 0.0037 | computed |
| E | s >= 3, draws | 9249 | 0.0000 | 0.0000 | 0.1572 | 0.8393 | 0.0035 | computed |
| E | [0, 1), distinct | 520 | 0.0019 | 0.0000 | 0.0000 | 0.9981 | 0.0000 | computed |
| E | [0, 1), draws | 8784 | 0.8543 | 0.0000 | 0.0000 | 0.1457 | 0.0000 | computed |
| E | [1, 1.5), distinct | 1054 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | computed |
| E | [1, 1.5), draws | 2525 | 0.0000 | 0.0000 | 0.0000 | 1.0000 | 0.0000 | computed |
| E | [1.5, 2.1), distinct | 3300 | 0.0000 | 0.0000 | 0.0024 | 0.9927 | 0.0048 | computed |
| E | [1.5, 2.1), draws | 3886 | 0.0000 | 0.0000 | 0.0021 | 0.9938 | 0.0041 | computed |
| E | [2.1, 3), distinct | 1144 | 0.0000 | 0.0000 | 0.0743 | 0.9135 | 0.0122 | computed |
| E | [2.1, 3), draws | 1243 | 0.0000 | 0.0000 | 0.0684 | 0.9204 | 0.0113 | computed |
| E | [3, 4.5), distinct | 1235 | 0.0000 | 0.0000 | 0.2340 | 0.7644 | 0.0016 | computed |
| E | [3, 4.5), draws | 1291 | 0.0000 | 0.0000 | 0.2246 | 0.7738 | 0.0015 | computed |
| E | [4.5, infinity), distinct | 1684 | 0.0000 | 0.0000 | 0.6615 | 0.3385 | 0.0000 | computed |
| E | [4.5, infinity), draws | 1687 | 0.0000 | 0.0000 | 0.6609 | 0.3391 | 0.0000 | computed |

Rejected or missing W draws retain their mass outside the five fate cells. Accepted-draw fractions are shown separately. Unsplit counts use pattern hashes; s conditions use each pattern unit's least s, including for its summed draw frequency.

## Settled weight

| Population | Flag (overlaps allowed) | Draws | Raw draw mass/share | Accepted share | Distinct true | Ambiguous patterns |
| --- | --- | --- | --- | --- | --- | --- |
| W | s1 | 23011 | 0.5753 | 0.7998 | 1 | 0 |
| W | single_placement | 26496 | 0.6624 | 0.9210 | 1907 | 0 |
| W | first_letter_settled | 27094 | 0.6774 | 0.9417 | 2431 | 0 |
| W | settled_union | 27615 | 0.6904 | 0.9599 | 2852 | 0 |
| E | s1 | 0 | 0.0000 | 0.0000 | 0 | 0 |
| E | single_placement | 8829 | 0.4547 | 0.4547 | 34 | 0 |
| E | first_letter_settled | 14468 | 0.7452 | 0.7452 | 4180 | 0 |
| E | settled_union | 14485 | 0.7460 | 0.7460 | 4184 | 0 |

The union includes s = 1, single distinct placement, and first-letter-settled. The primary comparison excludes single-placement and first-letter-settled units; F0 is separately excluded.

## Joining and death summaries

The measured joining counts do not assign activity class. Complete first-death histograms and death-by-level curves for every relative class, letter class, density bin, and class-by-bin group are in summary.json. Deaths after level 12 are censored.

| Population | Unit | Relative class | Units | Mean rho_max | Mean rho12 | Mean J10 | Mean J11 | Mean J12 | Status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| W | pattern_relative_class | finitary | 28 | 0.8237 | 0.8237 | 0.0000 | 0.0000 | 0.0000 | computed |
| W | pattern_relative_class | bounded | 147 | 1.0841 | 1.0841 | 6.6667 | 6.7075 | 6.6803 | computed |
| W | pattern_relative_class | polynomial | 153 | 1.2216 | 1.2216 | 58.1830 | 69.9346 | 83.1111 | computed |
| W | pattern_relative_class | exponential | 3669 | 1.9978 | 1.9978 | 1169.3023 | 2303.1300 | 4557.6495 | computed |
| W | draw_frequencies | finitary | 11571 | 0.0058 | 0.0058 | 0.0000 | 0.0000 | 0.0000 | computed |
| W | draw_frequencies | bounded | 972 | 0.4600 | 0.4600 | 2.2243 | 2.2243 | 2.2284 | computed |
| W | draw_frequencies | polynomial | 175 | 1.0995 | 1.0995 | 51.6457 | 62.0114 | 73.6229 | computed |
| W | draw_frequencies | exponential | 16052 | 0.5562 | 0.5562 | 344.6465 | 681.3279 | 1351.2450 | computed |
| E | pattern_relative_class | finitary | 19 | 1.1382 | 1.1382 | 0.0000 | 0.0000 | 0.0000 | computed |
| E | pattern_relative_class | bounded | 293 | 1.4935 | 1.4935 | 8.6348 | 8.4027 | 8.6416 | computed |
| E | pattern_relative_class | polynomial | 196 | 1.9987 | 1.9987 | 65.0204 | 74.8776 | 85.7959 | computed |
| E | pattern_relative_class | exponential | 8444 | 3.1148 | 3.1148 | 1807.3006 | 3573.7795 | 7083.0407 | computed |
| E | draw_frequencies | finitary | 3821 | 0.0276 | 0.0276 | 0.0000 | 0.0000 | 0.0000 | computed |
| E | draw_frequencies | bounded | 1440 | 0.7191 | 0.7191 | 3.5069 | 3.4569 | 3.5083 | computed |
| E | draw_frequencies | polynomial | 216 | 1.8622 | 1.8622 | 60.1667 | 69.2407 | 79.2778 | computed |
| E | draw_frequencies | exponential | 13939 | 2.1109 | 2.1109 | 1263.0900 | 2501.1448 | 4963.1586 | computed |

| Population | Unit | Relative class | First deaths at levels 1 through 12 | No observed death |
| --- | --- | --- | --- | --- |
| W | pattern_relative_class | finitary | 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 | 28 |
| W | pattern_relative_class | bounded | 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 | 147 |
| W | pattern_relative_class | polynomial | 0, 0, 0, 1, 2, 0, 0, 0, 0, 0, 0, 0 | 150 |
| W | pattern_relative_class | exponential | 0, 0, 86, 111, 52, 35, 14, 7, 4, 2, 0, 0 | 3358 |
| W | draw_frequencies | finitary | 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 | 11571 |
| W | draw_frequencies | bounded | 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 | 972 |
| W | draw_frequencies | polynomial | 0, 0, 0, 1, 2, 0, 0, 0, 0, 0, 0, 0 | 172 |
| W | draw_frequencies | exponential | 0, 0, 86, 111, 52, 35, 14, 7, 4, 2, 0, 0 | 15741 |
| E | pattern_relative_class | finitary | 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 | 19 |
| E | pattern_relative_class | bounded | 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0 | 291 |
| E | pattern_relative_class | polynomial | 0, 0, 3, 5, 2, 1, 0, 0, 0, 0, 0, 0 | 185 |
| E | pattern_relative_class | exponential | 0, 0, 541, 557, 212, 105, 41, 12, 7, 3, 3, 2 | 6961 |
| E | draw_frequencies | finitary | 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 | 3821 |
| E | draw_frequencies | bounded | 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0 | 1438 |
| E | draw_frequencies | polynomial | 0, 0, 3, 5, 2, 1, 0, 0, 0, 0, 0, 0 | 205 |
| E | draw_frequencies | exponential | 0, 0, 543, 557, 212, 105, 41, 12, 7, 3, 3, 2 | 12454 |

## Matched-density comparisons

Each eligible E cell uses 2,000 automaton-class cluster resamples; W instead uses 2,000 resamples of empirical draws, independently within each arm, seed 20261115. FU remains in the denominator and is assigned dead and alive separately. A combined verdict requires agreement. Eligibility counts class units; W death shares use draw frequency. The correction family is the eligible cells within each displayed analysis.

### E_settled_excluded

Eligible cells: 1; eligibility unknown: 0; Bonferroni m: 1.

| Bin | C | FU assignment | C units | Exp units | C decided | Exp decided | FU C/exp | Decided clusters C/exp | Delta | 95% | Corrected | Eligible | Assignment verdict | Combined |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [0, 1) | finitary | FU_alive | 0 | 235 | 0 | 235 | 0/0 | 0/110 | — | — | — | False | ineligible | — |
| [0, 1) | finitary | FU_dead | 0 | 235 | 0 | 235 | 0/0 | 0/110 | — | — | — | False | ineligible | — |
| [0, 1) | bounded | FU_alive | 29 | 235 | 29 | 235 | 0/0 | 10/110 | 0.0000 | — | — | False | ineligible | — |
| [0, 1) | bounded | FU_dead | 29 | 235 | 29 | 235 | 0/0 | 10/110 | 0.0000 | — | — | False | ineligible | — |
| [0, 1) | polynomial | FU_alive | 14 | 235 | 14 | 235 | 0/0 | 9/110 | 0.0000 | — | — | False | ineligible | — |
| [0, 1) | polynomial | FU_dead | 14 | 235 | 14 | 235 | 0/0 | 9/110 | 0.0000 | — | — | False | ineligible | — |
| [1, 1.5) | finitary | FU_alive | 0 | 446 | 0 | 446 | 0/0 | 0/161 | — | — | — | False | ineligible | — |
| [1, 1.5) | finitary | FU_dead | 0 | 446 | 0 | 446 | 0/0 | 0/161 | — | — | — | False | ineligible | — |
| [1, 1.5) | bounded | FU_alive | 29 | 446 | 29 | 446 | 0/0 | 12/161 | 0.0000 | — | — | False | ineligible | — |
| [1, 1.5) | bounded | FU_dead | 29 | 446 | 29 | 446 | 0/0 | 12/161 | 0.0000 | — | — | False | ineligible | — |
| [1, 1.5) | polynomial | FU_alive | 17 | 446 | 17 | 446 | 0/0 | 8/161 | 0.0000 | — | — | False | ineligible | — |
| [1, 1.5) | polynomial | FU_dead | 17 | 446 | 17 | 446 | 0/0 | 8/161 | 0.0000 | — | — | False | ineligible | — |
| [1.5, 2.1) | finitary | FU_alive | 2 | 1108 | 2 | 1092 | 0/16 | 2/257 | -0.0072 | — | — | False | ineligible | — |
| [1.5, 2.1) | finitary | FU_dead | 2 | 1108 | 2 | 1092 | 0/16 | 2/257 | -0.0217 | — | — | False | ineligible | — |
| [1.5, 2.1) | bounded | FU_alive | 36 | 1108 | 36 | 1092 | 0/16 | 18/257 | -0.0072 | [-0.012534415890216324, -0.0026878722914448526] | [-0.012534415890216324, -0.0026878722914448526] | True | same | same |
| [1.5, 2.1) | bounded | FU_dead | 36 | 1108 | 36 | 1092 | 0/16 | 18/257 | -0.0217 | [-0.03116786617815673, -0.012818606627017852] | [-0.03116786617815673, -0.012818606627017852] | True | same | same |
| [1.5, 2.1) | polynomial | FU_alive | 21 | 1108 | 21 | 1092 | 0/16 | 11/257 | -0.0072 | — | — | False | ineligible | — |
| [1.5, 2.1) | polynomial | FU_dead | 21 | 1108 | 21 | 1092 | 0/16 | 11/257 | -0.0217 | — | — | False | ineligible | — |
| [2.1, 3) | finitary | FU_alive | 0 | 611 | 0 | 597 | 0/14 | 0/228 | — | — | — | False | ineligible | — |
| [2.1, 3) | finitary | FU_dead | 0 | 611 | 0 | 597 | 0/14 | 0/228 | — | — | — | False | ineligible | — |
| [2.1, 3) | bounded | FU_alive | 7 | 611 | 7 | 597 | 0/14 | 4/228 | -0.1375 | — | — | False | ineligible | — |
| [2.1, 3) | bounded | FU_dead | 7 | 611 | 7 | 597 | 0/14 | 4/228 | -0.1604 | — | — | False | ineligible | — |
| [2.1, 3) | polynomial | FU_alive | 12 | 611 | 12 | 597 | 0/14 | 5/228 | -0.0541 | — | — | False | ineligible | — |
| [2.1, 3) | polynomial | FU_dead | 12 | 611 | 12 | 597 | 0/14 | 5/228 | -0.0771 | — | — | False | ineligible | — |
| [3, 4.5) | finitary | FU_alive | 0 | 757 | 0 | 755 | 0/2 | 0/252 | — | — | — | False | ineligible | — |
| [3, 4.5) | finitary | FU_dead | 0 | 757 | 0 | 755 | 0/2 | 0/252 | — | — | — | False | ineligible | — |
| [3, 4.5) | bounded | FU_alive | 19 | 757 | 19 | 755 | 0/2 | 9/252 | -0.2646 | — | — | False | ineligible | — |
| [3, 4.5) | bounded | FU_dead | 19 | 757 | 19 | 755 | 0/2 | 9/252 | -0.2673 | — | — | False | ineligible | — |
| [3, 4.5) | polynomial | FU_alive | 14 | 757 | 14 | 755 | 0/2 | 4/252 | 0.1301 | — | — | False | ineligible | — |
| [3, 4.5) | polynomial | FU_dead | 14 | 757 | 14 | 755 | 0/2 | 4/252 | 0.1275 | — | — | False | ineligible | — |
| [4.5, infinity) | finitary | FU_alive | 0 | 1395 | 0 | 1395 | 0/0 | 0/238 | — | — | — | False | ineligible | — |
| [4.5, infinity) | finitary | FU_dead | 0 | 1395 | 0 | 1395 | 0/0 | 0/238 | — | — | — | False | ineligible | — |
| [4.5, infinity) | bounded | FU_alive | 1 | 1395 | 1 | 1395 | 0/0 | 1/238 | -0.7964 | — | — | False | ineligible | — |
| [4.5, infinity) | bounded | FU_dead | 1 | 1395 | 1 | 1395 | 0/0 | 1/238 | -0.7964 | — | — | False | ineligible | — |
| [4.5, infinity) | polynomial | FU_alive | 7 | 1395 | 7 | 1395 | 0/0 | 4/238 | -0.3678 | — | — | False | ineligible | — |
| [4.5, infinity) | polynomial | FU_dead | 7 | 1395 | 7 | 1395 | 0/0 | 4/238 | -0.3678 | — | — | False | ineligible | — |

### E_settled_included

Eligible cells: 6; eligibility unknown: 0; Bonferroni m: 6.

| Bin | C | FU assignment | C units | Exp units | C decided | Exp decided | FU C/exp | Decided clusters C/exp | Delta | 95% | Corrected | Eligible | Assignment verdict | Combined |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [0, 1) | finitary | FU_alive | 3 | 419 | 3 | 419 | 0/0 | 2/141 | 0.0000 | — | — | False | ineligible | — |
| [0, 1) | finitary | FU_dead | 3 | 419 | 3 | 419 | 0/0 | 2/141 | 0.0000 | — | — | False | ineligible | — |
| [0, 1) | bounded | FU_alive | 68 | 419 | 68 | 419 | 0/0 | 20/141 | 0.0000 | [0.0, 0.0] | [0.0, 0.0] | True | same | same |
| [0, 1) | bounded | FU_dead | 68 | 419 | 68 | 419 | 0/0 | 20/141 | 0.0000 | [0.0, 0.0] | [0.0, 0.0] | True | same | same |
| [0, 1) | polynomial | FU_alive | 35 | 419 | 35 | 419 | 0/0 | 14/141 | 0.0000 | [0.0, 0.0] | [0.0, 0.0] | True | same | same |
| [0, 1) | polynomial | FU_dead | 35 | 419 | 35 | 419 | 0/0 | 14/141 | 0.0000 | [0.0, 0.0] | [0.0, 0.0] | True | same | same |
| [1, 1.5) | finitary | FU_alive | 10 | 925 | 10 | 925 | 0/0 | 6/207 | 0.0000 | — | — | False | ineligible | — |
| [1, 1.5) | finitary | FU_dead | 10 | 925 | 10 | 925 | 0/0 | 6/207 | 0.0000 | — | — | False | ineligible | — |
| [1, 1.5) | bounded | FU_alive | 87 | 925 | 87 | 925 | 0/0 | 33/207 | 0.0000 | [0.0, 0.0] | [0.0, 0.0] | True | same | same |
| [1, 1.5) | bounded | FU_dead | 87 | 925 | 87 | 925 | 0/0 | 33/207 | 0.0000 | [0.0, 0.0] | [0.0, 0.0] | True | same | same |
| [1, 1.5) | polynomial | FU_alive | 38 | 925 | 38 | 925 | 0/0 | 16/207 | 0.0000 | [0.0, 0.0] | [0.0, 0.0] | True | same | same |
| [1, 1.5) | polynomial | FU_dead | 38 | 925 | 38 | 925 | 0/0 | 16/207 | 0.0000 | [0.0, 0.0] | [0.0, 0.0] | True | same | same |
| [1.5, 2.1) | finitary | FU_alive | 5 | 3124 | 5 | 3108 | 0/16 | 4/272 | -0.0026 | — | — | False | ineligible | — |
| [1.5, 2.1) | finitary | FU_dead | 5 | 3124 | 5 | 3108 | 0/16 | 4/272 | -0.0077 | — | — | False | ineligible | — |
| [1.5, 2.1) | bounded | FU_alive | 93 | 3124 | 93 | 3108 | 0/16 | 34/272 | -0.0026 | [-0.004542613054631425, -0.0009436781519400096] | [-0.005367130049644593, -0.0006141862161155593] | True | same | same |
| [1.5, 2.1) | bounded | FU_dead | 93 | 3124 | 93 | 3108 | 0/16 | 34/272 | -0.0077 | [-0.011494436487826373, -0.004635285819114708] | [-0.012832239572554282, -0.0037204819467863606] | True | same | same |
| [1.5, 2.1) | polynomial | FU_alive | 78 | 3124 | 78 | 3108 | 0/16 | 27/272 | -0.0026 | [-0.004489827539241632, -0.000947209038087164] | [-0.005054279963761519, -0.0006265572080362109] | True | same | same |
| [1.5, 2.1) | polynomial | FU_dead | 78 | 3124 | 78 | 3108 | 0/16 | 27/272 | -0.0077 | [-0.011199130539003286, -0.004567565726172004] | [-0.012575112181301015, -0.00345279548564456] | True | same | same |
| [2.1, 3) | finitary | FU_alive | 0 | 1110 | 0 | 1096 | 0/14 | 0/254 | — | — | — | False | ineligible | — |
| [2.1, 3) | finitary | FU_dead | 0 | 1110 | 0 | 1096 | 0/14 | 0/254 | — | — | — | False | ineligible | — |
| [2.1, 3) | bounded | FU_alive | 15 | 1110 | 15 | 1096 | 0/14 | 5/254 | -0.0757 | — | — | False | ineligible | — |
| [2.1, 3) | bounded | FU_dead | 15 | 1110 | 15 | 1096 | 0/14 | 5/254 | -0.0883 | — | — | False | ineligible | — |
| [2.1, 3) | polynomial | FU_alive | 19 | 1110 | 19 | 1096 | 0/14 | 7/254 | -0.0230 | — | — | False | ineligible | — |
| [2.1, 3) | polynomial | FU_dead | 19 | 1110 | 19 | 1096 | 0/14 | 7/254 | -0.0357 | — | — | False | ineligible | — |
| [3, 4.5) | finitary | FU_alive | 0 | 1191 | 0 | 1189 | 0/2 | 0/264 | — | — | — | False | ineligible | — |
| [3, 4.5) | finitary | FU_dead | 0 | 1191 | 0 | 1189 | 0/2 | 0/264 | — | — | — | False | ineligible | — |
| [3, 4.5) | bounded | FU_alive | 28 | 1191 | 28 | 1189 | 0/2 | 11/264 | -0.1637 | — | — | False | ineligible | — |
| [3, 4.5) | bounded | FU_dead | 28 | 1191 | 28 | 1189 | 0/2 | 11/264 | -0.1653 | — | — | False | ineligible | — |
| [3, 4.5) | polynomial | FU_alive | 16 | 1191 | 16 | 1189 | 0/2 | 4/264 | 0.2024 | — | — | False | ineligible | — |
| [3, 4.5) | polynomial | FU_dead | 16 | 1191 | 16 | 1189 | 0/2 | 4/264 | 0.2007 | — | — | False | ineligible | — |
| [4.5, infinity) | finitary | FU_alive | 0 | 1674 | 0 | 1674 | 0/0 | 0/246 | — | — | — | False | ineligible | — |
| [4.5, infinity) | finitary | FU_dead | 0 | 1674 | 0 | 1674 | 0/0 | 0/246 | — | — | — | False | ineligible | — |
| [4.5, infinity) | bounded | FU_alive | 1 | 1674 | 1 | 1674 | 0/0 | 1/246 | -0.6637 | — | — | False | ineligible | — |
| [4.5, infinity) | bounded | FU_dead | 1 | 1674 | 1 | 1674 | 0/0 | 1/246 | -0.6637 | — | — | False | ineligible | — |
| [4.5, infinity) | polynomial | FU_alive | 9 | 1674 | 9 | 1674 | 0/0 | 4/246 | -0.3303 | — | — | False | ineligible | — |
| [4.5, infinity) | polynomial | FU_dead | 9 | 1674 | 9 | 1674 | 0/0 | 4/246 | -0.3303 | — | — | False | ineligible | — |

### W_settled_excluded

Eligible cells: 0; eligibility unknown: 0; Bonferroni m: 0.

| Bin | C | FU assignment | C units | Exp units | C decided | Exp decided | FU C/exp | Decided clusters C/exp | Delta | 95% | Corrected | Eligible | Assignment verdict | Combined |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [0, 1) | finitary | FU_alive | 0 | 49 | 0 | 49 | 0/0 | 0/47 | — | — | — | False | ineligible | — |
| [0, 1) | finitary | FU_dead | 0 | 49 | 0 | 49 | 0/0 | 0/47 | — | — | — | False | ineligible | — |
| [0, 1) | bounded | FU_alive | 8 | 49 | 8 | 49 | 0/0 | 7/47 | 0.0000 | — | — | False | ineligible | — |
| [0, 1) | bounded | FU_dead | 8 | 49 | 8 | 49 | 0/0 | 7/47 | 0.0000 | — | — | False | ineligible | — |
| [0, 1) | polynomial | FU_alive | 3 | 49 | 3 | 49 | 0/0 | 3/47 | 0.0000 | — | — | False | ineligible | — |
| [0, 1) | polynomial | FU_dead | 3 | 49 | 3 | 49 | 0/0 | 3/47 | 0.0000 | — | — | False | ineligible | — |
| [1, 1.5) | finitary | FU_alive | 1 | 88 | 1 | 88 | 0/0 | 1/79 | 0.0000 | — | — | False | ineligible | — |
| [1, 1.5) | finitary | FU_dead | 1 | 88 | 1 | 88 | 0/0 | 1/79 | 0.0000 | — | — | False | ineligible | — |
| [1, 1.5) | bounded | FU_alive | 7 | 88 | 7 | 88 | 0/0 | 7/79 | 0.0000 | — | — | False | ineligible | — |
| [1, 1.5) | bounded | FU_dead | 7 | 88 | 7 | 88 | 0/0 | 7/79 | 0.0000 | — | — | False | ineligible | — |
| [1, 1.5) | polynomial | FU_alive | 5 | 88 | 5 | 88 | 0/0 | 5/79 | 0.0000 | — | — | False | ineligible | — |
| [1, 1.5) | polynomial | FU_dead | 5 | 88 | 5 | 88 | 0/0 | 5/79 | 0.0000 | — | — | False | ineligible | — |
| [1.5, 2.1) | finitary | FU_alive | 0 | 240 | 0 | 238 | 0/2 | 0/180 | — | — | — | False | ineligible | — |
| [1.5, 2.1) | finitary | FU_dead | 0 | 240 | 0 | 238 | 0/2 | 0/180 | — | — | — | False | ineligible | — |
| [1.5, 2.1) | bounded | FU_alive | 6 | 240 | 6 | 238 | 0/2 | 6/180 | 0.0000 | — | — | False | ineligible | — |
| [1.5, 2.1) | bounded | FU_dead | 6 | 240 | 6 | 238 | 0/2 | 6/180 | -0.0080 | — | — | False | ineligible | — |
| [1.5, 2.1) | polynomial | FU_alive | 7 | 240 | 7 | 238 | 0/2 | 7/180 | 0.0000 | — | — | False | ineligible | — |
| [1.5, 2.1) | polynomial | FU_dead | 7 | 240 | 7 | 238 | 0/2 | 7/180 | -0.0080 | — | — | False | ineligible | — |
| [2.1, 3) | finitary | FU_alive | 0 | 259 | 0 | 246 | 0/13 | 0/184 | — | — | — | False | ineligible | — |
| [2.1, 3) | finitary | FU_dead | 0 | 259 | 0 | 246 | 0/13 | 0/184 | — | — | — | False | ineligible | — |
| [2.1, 3) | bounded | FU_alive | 2 | 259 | 2 | 246 | 0/13 | 2/184 | -0.1456 | — | — | False | ineligible | — |
| [2.1, 3) | bounded | FU_dead | 2 | 259 | 2 | 246 | 0/13 | 2/184 | -0.1954 | — | — | False | ineligible | — |
| [2.1, 3) | polynomial | FU_alive | 3 | 259 | 3 | 246 | 0/13 | 2/184 | 0.1877 | — | — | False | ineligible | — |
| [2.1, 3) | polynomial | FU_dead | 3 | 259 | 3 | 246 | 0/13 | 2/184 | 0.1379 | — | — | False | ineligible | — |
| [3, 4.5) | finitary | FU_alive | 0 | 191 | 0 | 191 | 0/0 | 0/145 | — | — | — | False | ineligible | — |
| [3, 4.5) | finitary | FU_dead | 0 | 191 | 0 | 191 | 0/0 | 0/145 | — | — | — | False | ineligible | — |
| [3, 4.5) | bounded | FU_alive | 7 | 191 | 7 | 191 | 0/0 | 7/145 | -0.3822 | — | — | False | ineligible | — |
| [3, 4.5) | bounded | FU_dead | 7 | 191 | 7 | 191 | 0/0 | 7/145 | -0.3822 | — | — | False | ineligible | — |
| [3, 4.5) | polynomial | FU_alive | 3 | 191 | 3 | 191 | 0/0 | 3/145 | -0.0489 | — | — | False | ineligible | — |
| [3, 4.5) | polynomial | FU_dead | 3 | 191 | 3 | 191 | 0/0 | 3/145 | -0.0489 | — | — | False | ineligible | — |
| [4.5, infinity) | finitary | FU_alive | 0 | 260 | 0 | 260 | 0/0 | 0/189 | — | — | — | False | ineligible | — |
| [4.5, infinity) | finitary | FU_dead | 0 | 260 | 0 | 260 | 0/0 | 0/189 | — | — | — | False | ineligible | — |
| [4.5, infinity) | bounded | FU_alive | 0 | 260 | 0 | 260 | 0/0 | 0/189 | — | — | — | False | ineligible | — |
| [4.5, infinity) | bounded | FU_dead | 0 | 260 | 0 | 260 | 0/0 | 0/189 | — | — | — | False | ineligible | — |
| [4.5, infinity) | polynomial | FU_alive | 1 | 260 | 1 | 260 | 0/0 | 1/189 | 0.2337 | — | — | False | ineligible | — |
| [4.5, infinity) | polynomial | FU_dead | 1 | 260 | 1 | 260 | 0/0 | 1/189 | 0.2337 | — | — | False | ineligible | — |

### W_settled_included

Eligible cells: 4; eligibility unknown: 0; Bonferroni m: 4.

| Bin | C | FU assignment | C units | Exp units | C decided | Exp decided | FU C/exp | Decided clusters C/exp | Delta | 95% | Corrected | Eligible | Assignment verdict | Combined |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [0, 1) | finitary | FU_alive | 15 | 1235 | 15 | 1235 | 0/0 | 12/750 | 0.0000 | — | — | False | ineligible | — |
| [0, 1) | finitary | FU_dead | 15 | 1235 | 15 | 1235 | 0/0 | 12/750 | 0.0000 | — | — | False | ineligible | — |
| [0, 1) | bounded | FU_alive | 65 | 1235 | 65 | 1235 | 0/0 | 47/750 | 0.0000 | [0.0, 0.0] | [0.0, 0.0] | True | same | same |
| [0, 1) | bounded | FU_dead | 65 | 1235 | 65 | 1235 | 0/0 | 47/750 | 0.0000 | [0.0, 0.0] | [0.0, 0.0] | True | same | same |
| [0, 1) | polynomial | FU_alive | 73 | 1235 | 73 | 1235 | 0/0 | 50/750 | 0.0000 | [0.0, 0.0] | [0.0, 0.0] | True | same | same |
| [0, 1) | polynomial | FU_dead | 73 | 1235 | 73 | 1235 | 0/0 | 50/750 | 0.0000 | [0.0, 0.0] | [0.0, 0.0] | True | same | same |
| [1, 1.5) | finitary | FU_alive | 9 | 691 | 9 | 691 | 0/0 | 7/465 | 0.0000 | — | — | False | ineligible | — |
| [1, 1.5) | finitary | FU_dead | 9 | 691 | 9 | 691 | 0/0 | 7/465 | 0.0000 | — | — | False | ineligible | — |
| [1, 1.5) | bounded | FU_alive | 50 | 691 | 50 | 691 | 0/0 | 40/465 | 0.0000 | [0.0, 0.0] | [0.0, 0.0] | True | same | same |
| [1, 1.5) | bounded | FU_dead | 50 | 691 | 50 | 691 | 0/0 | 40/465 | 0.0000 | [0.0, 0.0] | [0.0, 0.0] | True | same | same |
| [1, 1.5) | polynomial | FU_alive | 44 | 691 | 44 | 691 | 0/0 | 38/465 | 0.0000 | [0.0, 0.0] | [0.0, 0.0] | True | same | same |
| [1, 1.5) | polynomial | FU_dead | 44 | 691 | 44 | 691 | 0/0 | 38/465 | 0.0000 | [0.0, 0.0] | [0.0, 0.0] | True | same | same |
| [1.5, 2.1) | finitary | FU_alive | 2 | 622 | 2 | 620 | 0/2 | 2/368 | 0.0000 | — | — | False | ineligible | — |
| [1.5, 2.1) | finitary | FU_dead | 2 | 622 | 2 | 620 | 0/2 | 2/368 | -0.0026 | — | — | False | ineligible | — |
| [1.5, 2.1) | bounded | FU_alive | 19 | 622 | 19 | 620 | 0/2 | 11/368 | 0.0000 | — | — | False | ineligible | — |
| [1.5, 2.1) | bounded | FU_dead | 19 | 622 | 19 | 620 | 0/2 | 11/368 | -0.0026 | — | — | False | ineligible | — |
| [1.5, 2.1) | polynomial | FU_alive | 19 | 622 | 19 | 620 | 0/2 | 18/368 | 0.0000 | — | — | False | ineligible | — |
| [1.5, 2.1) | polynomial | FU_dead | 19 | 622 | 19 | 620 | 0/2 | 18/368 | -0.0026 | — | — | False | ineligible | — |
| [2.1, 3) | finitary | FU_alive | 1 | 489 | 1 | 476 | 0/13 | 1/299 | -0.0739 | — | — | False | ineligible | — |
| [2.1, 3) | finitary | FU_dead | 1 | 489 | 1 | 476 | 0/13 | 1/299 | -0.0992 | — | — | False | ineligible | — |
| [2.1, 3) | bounded | FU_alive | 3 | 489 | 3 | 476 | 0/13 | 3/299 | -0.0739 | — | — | False | ineligible | — |
| [2.1, 3) | bounded | FU_dead | 3 | 489 | 3 | 476 | 0/13 | 3/299 | -0.0992 | — | — | False | ineligible | — |
| [2.1, 3) | polynomial | FU_alive | 10 | 489 | 10 | 476 | 0/13 | 9/299 | 0.0261 | — | — | False | ineligible | — |
| [2.1, 3) | polynomial | FU_dead | 10 | 489 | 10 | 476 | 0/13 | 9/299 | 0.0008 | — | — | False | ineligible | — |
| [3, 4.5) | finitary | FU_alive | 0 | 299 | 0 | 299 | 0/0 | 0/196 | — | — | — | False | ineligible | — |
| [3, 4.5) | finitary | FU_dead | 0 | 299 | 0 | 299 | 0/0 | 0/196 | — | — | — | False | ineligible | — |
| [3, 4.5) | bounded | FU_alive | 9 | 299 | 9 | 299 | 0/0 | 8/196 | -0.2409 | — | — | False | ineligible | — |
| [3, 4.5) | bounded | FU_dead | 9 | 299 | 9 | 299 | 0/0 | 8/196 | -0.2409 | — | — | False | ineligible | — |
| [3, 4.5) | polynomial | FU_alive | 4 | 299 | 4 | 299 | 0/0 | 4/196 | 0.0091 | — | — | False | ineligible | — |
| [3, 4.5) | polynomial | FU_dead | 4 | 299 | 4 | 299 | 0/0 | 4/196 | 0.0091 | — | — | False | ineligible | — |
| [4.5, infinity) | finitary | FU_alive | 0 | 332 | 0 | 332 | 0/0 | 0/228 | — | — | — | False | ineligible | — |
| [4.5, infinity) | finitary | FU_dead | 0 | 332 | 0 | 332 | 0/0 | 0/228 | — | — | — | False | ineligible | — |
| [4.5, infinity) | bounded | FU_alive | 0 | 332 | 0 | 332 | 0/0 | 0/228 | — | — | — | False | ineligible | — |
| [4.5, infinity) | bounded | FU_dead | 0 | 332 | 0 | 332 | 0/0 | 0/228 | — | — | — | False | ineligible | — |
| [4.5, infinity) | polynomial | FU_alive | 2 | 332 | 2 | 332 | 0/0 | 2/228 | -0.1006 | — | — | False | ineligible | — |
| [4.5, infinity) | polynomial | FU_dead | 2 | 332 | 2 | 332 | 0/0 | 2/228 | -0.1006 | — | — | False | ineligible | — |

## Frozen predictions

| Rule | Observed status |
| --- | --- |
| P1 | no_failure_observed |
| P2 | fails_return_observed |
| P4 | observed |
| H-dens | no_failure_observed |
| H-bound | fails |

P1 failures and excluded F0 counts, P2 returns, P4 witnesses, and H-dens/H-bound failure cells are listed by key or cell in summary.json. An incomplete census cannot establish an absence across the registered population.

## Logistic sensitivity

| Population | FU assignment | Matrix rows | FU units | Fit |
| --- | --- | --- | --- | --- |
| E | FU_alive | 4760 | 32 | skipped_statsmodels_unavailable |
| E | FU_dead | 4760 | 32 | skipped_statsmodels_unavailable |
| W | FU_alive | 1140 | 15 | skipped_statsmodels_unavailable |
| W | FU_dead | 1140 | 15 | skipped_statsmodels_unavailable |

Both design matrices, first-description cluster labels, frequency weights and column definitions are stored in summary.json. FU is assigned alive and dead separately; no null response is fitted.

## Addendum unit rules

Every class split, including the secondary letter-class split, uses (pattern hash, relative class). Automaton class and letter class come from the first description in numeric sorted key order within the unit. Settled means any member is single-placement or first-letter-settled. s is the least member s. Relative polynomial degrees are retained as memberships, without duplicating a primary class unit.

Verdicts are merged across all descriptions of a pattern before any summary; contradictory decided verdicts stop the program and list their pattern hashes, levels and key IDs. Resolved pattern-level nulls: 0. Resolved description-level nulls: 0.

All eleven original ambiguities are resolved by codex_spec_addendum.md. No claim extends beyond the twelve levels read.
