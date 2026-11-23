## Gate row G
| Gate | Result |
| --- | --- |
| G1: 173 recorded simple sharing patterns, fail verdict equals recorded admit verdict | 173 patterns, 115 admit; every verdict equal: True |
| G2: planarity routine against brute-force minor search (K5 or K3,3 minor), patterns of at most six knots | 23 recorded patterns of at most six knots, 202 simple graphs on 1 to 6 knots, plus (beyond the requirement) 150 recorded seven-knot patterns, 1043 simple graphs on 7 knots, 61 small incidence patterns with a distinction of three or more holders; disagreements: 0 |
| G3: mutant unlinking the second holder of every shared distinction | passes 173/173 recorded patterns (115 of them fail unmutated), 13/13 engine stages (11 fail unmutated), every benchmark construction with at most two holders per distinction; literal mutant passes the bounded-bond windows 1: True, 2: False, 3: False, 4: False (distinctions of up to six holders) |
| G4: knot-side check, five structures | five_knot_closure: 5 knots, 10 distinctions, 1024 answer words, agree True; two_split_three_place_knots: 2 knots, 4 distinctions, 16 answer words, agree True; P3 part 1 (arm 0, draw 75, stage 2): 8 knots, 12 distinctions, 4096 answer words, agree True; P3 part 2 (arm 1, draw 78, stage 2): 8 knots, 14 distinctions, 16384 answer words, agree True; P3 part 3 (arm 1, draw 146, stage 2): 8 knots, 13 distinctions, 8192 answer words, agree True |
| Supporting: Euler shortcut equals networkx on | 173 recorded patterns, 20 benchmark patterns, 995 engine stages (disagreements 0) |
| Supporting: growth driver equals the other recorded engine (naelib) on counts per parent step | 80/80 |
| Supporting: archived starts 00, 04, 13 reproduce recorded supports and birth counts | True |

## P1: shape benchmark
| Construction | Depth or window | Knots | Distinctions | Loop rank | T | Lower bound | Upper bound at first failure | Most holders of a distinction |
| --- | ---: | ---: | ---: | ---: | --- | ---: | --- | ---: |
| cubic | 0 | 1 | 3 | 0 | pass | 0 |  | 1 |
| cubic | 1 | 4 | 12 | 0 | pass | 0 |  | 2 |
| cubic | 2 | 10 | 30 | 3 | pass | 0 |  | 2 |
| cubic | 3 | 20 | 60 | 11 | pass | 0 |  | 2 |
| cubic | 4 | 35 | 105 | 26 | fail | 0 | 7 | 2 |
| cubic | 5 | 56 | 168 | 50 | fail | 0 | only computed at the first failing stage | 2 |
| cubic | 6 | 84 | 252 | 85 | fail | 0 | only computed at the first failing stage | 2 |
| pinwheel | 1 | 5 | 11 | 1 | pass | 0 |  | 2 |
| pinwheel | 2 | 25 | 49 | 11 | pass | 0 |  | 2 |
| pinwheel | 3 | 125 | 227 | 73 | pass | 0 |  | 2 |
| pinwheel | 4 | 625 | 1101 | 407 | pass | 0 |  | 2 |
| pinwheel | 5 | 3125 | 5411 | 2137 | pass | 0 |  | 2 |
| periodic | 1 | 2 | 5 | 0 | pass | 0 |  | 2 |
| periodic | 2 | 4 | 9 | 0 | pass | 0 |  | 2 |
| periodic | 3 | 8 | 16 | 1 | pass | 0 |  | 2 |
| periodic | 4 | 16 | 30 | 3 | pass | 0 |  | 2 |
| periodic | 5 | 32 | 56 | 9 | pass | 0 |  | 2 |
| periodic | 6 | 64 | 108 | 21 | pass | 0 |  | 2 |
| periodic | 7 | 128 | 208 | 49 | pass | 0 |  | 2 |
| periodic | 8 | 256 | 408 | 105 | pass | 0 |  | 2 |
| bounded_bond | 1 | 6 | 9 | 4 | pass | 0 |  | 3 |
| bounded_bond | 2 | 28 | 25 | 32 | fail | 41 | 5 | 6 |
| bounded_bond | 3 | 66 | 49 | 84 | fail | 149 | only computed at the first failing stage | 6 |
| bounded_bond | 4 | 120 | 81 | 160 | fail | 321 | only computed at the first failing stage | 6 |

P1 verdicts: cubic passes to depth 3 and fails from depth 4: **holds**; pinwheel passes at every depth: **holds**; polygonal control passes at every depth: **holds**; bounded-bond fails from window 2: **holds**

## Settled by construction, checked on the data
Stages with loop rank below 4: 2471, failing: 0. Histories in which a failing stage is followed by a passing one: 0. Histories whose births are all one-parent: 21, of which fail: 0.

## P2: T against loop rank
Loop ranks with both a passing and a failing reached stage, within one population: P1: 0 ranks; P2: 1 ranks (least 16); P3: 101 ranks (least 5).
Loop ranks that have at least one passing and at least one failing reached stage: 104 of 210 ranks seen; least: 5; first example pair at rank 5: pass ('P3', 'P3', 32, 0, 'nae', 2, 11), fail ('P3', 'P3', 180, 2, 'nae', 1, 10).

| Population | Law | Reached stages | Failing stages | Least loop rank of a failing stage | Smallest failing stage (knots, distinctions, loop rank; where) |
| --- | --- | ---: | ---: | ---: | --- |
| P1 | - | 24 | 6 | 26 | 28, 25, 32; bounded_bond t=2 |
| P2 | parity | 82 | 74 | 9 | 10, 28, 9; five_founder_clock t=1 |
| P2 | nae | 82 | 74 | 9 | 10, 28, 9; five_founder_clock t=1 |
| P3 | parity | 3552 | 325 | 5 | 7, 16, 7; P3 t=1 arm 3 draw 162 |
| P3 | nae | 4384 | 335 | 5 | 7, 16, 7; P3 t=1 arm 3 draw 162 |

Pass/fail counts by loop rank, P3 stages, both laws pooled (ranks seen in P3; every stage is a row, so a start counts once per stage):
| Loop rank | Passing stages | Failing stages |
| ---: | ---: | ---: |
| 0 | 512 | 0 |
| 1 | 512 | 0 |
| 2 | 620 | 0 |
| 3 | 809 | 0 |
| 4 | 308 | 0 |
| 5 | 223 | 2 |
| 6 | 245 | 2 |
| 7 | 185 | 6 |
| 8 | 173 | 5 |
| 9 | 233 | 2 |
| 10 | 188 | 7 |
| 11 | 132 | 4 |
| 12 | 154 | 2 |
| 13 | 160 | 9 |
| 14 | 161 | 18 |
| 15 | 114 | 18 |
| (ranks above 15) | 2547 | 585 |

## Growth kind against the test (starts; fails = some stage within the horizon fails T)
| Population | Law | Growth kind | Starts | Fail within horizon | Pass throughout | Median share of one-parent births (starts with births) |
| --- | --- | --- | ---: | ---: | ---: | --- |
| P2 | parity | stalled | 0 | 0 | 0 | n/a |
| P2 | parity | bounded | 1 | 1 | 0 | 0.000 |
| P2 | parity | growing | 6 | 6 | 0 | 0.002 |
| P2 | nae | stalled | 0 | 0 | 0 | n/a |
| P2 | nae | bounded | 1 | 1 | 0 | 0.000 |
| P2 | nae | growing | 6 | 6 | 0 | 0.002 |
| P3 | parity | stalled | 744 | 0 | 744 | n/a |
| P3 | parity | bounded | 129 | 8 | 121 | 0.500 |
| P3 | parity | growing | 151 | 25 | 126 | 0.295 |
| P3 | nae | stalled | 744 | 0 | 744 | n/a |
| P3 | nae | bounded | 51 | 7 | 44 | 0.500 |
| P3 | nae | growing | 229 | 26 | 203 | 0.313 |
Stalled kind, P2/parity: by outcome {} (outcome closed with no births = no live knot at the source).
Stalled kind, P2/nae: by outcome {} (outcome closed with no births = no live knot at the source).
Stalled kind, P3/parity: by outcome {'stall': 731, 'closed': 13} (outcome closed with no births = no live knot at the source).
Stalled kind, P3/nae: by outcome {'stall': 731, 'closed': 13} (outcome closed with no births = no live knot at the source).

Starts of bounded kind that fail within the horizon: 17 of 182 bounded histories (P2 and P3, both laws): [('P2', 'parity', 'five_founder_clock', 1), ('P2', 'nae', 'five_founder_clock', 1), ('P3', 'nae', (0, 72), 3), ('P3', 'nae', (0, 165), 3), ('P3', 'nae', (0, 244), 3), ('P3', 'nae', (1, 0), 3), ('P3', 'nae', (1, 37), 3), ('P3', 'nae', (2, 40), 3), ('P3', 'nae', (3, 162), 1), ('P3', 'parity', (0, 72), 3)].

Outcomes of the histories (horizon = alive after the horizon; closed = a closing birth or no live knot; stall; cap = the next step would exceed the knot cap; time = wall-clock budget): P2/nae/cap: 5; P2/nae/horizon: 2; P2/parity/cap: 5; P2/parity/horizon: 2; P3/nae/closed: 13; P3/nae/horizon: 280; P3/nae/stall: 731; P3/parity/closed: 91; P3/parity/horizon: 202; P3/parity/stall: 731

## P2 histories (recorded sources)
| Source | Law | Outcome | Knots at each stage | Growth kind | One-parent births / births | First failing step | Lower / upper removal bound at it |
| --- | --- | --- | --- | --- | --- | ---: | --- |
| archive_start-00 | parity | horizon | [6, 14, 26, 41, 56, 70, 84, 99, 108, 127, 153, 184, 251, 573, 582, 618, 702] | growing | 3/696 | 1 | 0 / 2 (ok) |
| archive_start-00 | nae (history shared with parity) | horizon | [6, 14, 26, 41, 56, 70, 84, 99, 108, 127, 153, 184, 251, 573, 582, 618, 702] | growing | 3/696 | 1 | 0 / 2 (ok) |
| archive_start-04 | parity | cap | [6, 16, 32, 58, 95, 158, 285, 1300, 2081] | growing | 6/2075 | 1 | 0 / 1 (ok) |
| archive_start-04 | nae (history shared with parity) | cap | [6, 16, 32, 58, 95, 158, 285, 1300, 2081] | growing | 6/2075 | 1 | 0 / 1 (ok) |
| archive_start-13 | parity | cap | [7, 22, 49, 105, 220, 500, 1368] | growing | 8/1361 | 1 | 0 / 3 (ok) |
| archive_start-13 | nae (history shared with parity) | cap | [7, 22, 49, 105, 220, 500, 1368] | growing | 8/1361 | 1 | 0 / 3 (ok) |
| five_founder_clock | parity | horizon | [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85] | bounded | 0/80 | 1 | 0 / 2 (ok) |
| five_founder_clock | nae (history shared with parity) | horizon | [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85] | bounded | 0/80 | 1 | 0 / 2 (ok) |
| knots21_two_clocks | parity | cap | [21, 33, 57, 113, 256, 634, 1676, 4662, 13486] | growing | 0/13465 | 2 | 0 / 14 (ok) |
| knots21_two_clocks | nae (history shared with parity) | cap | [21, 33, 57, 113, 256, 634, 1676, 4662, 13486] | growing | 0/13465 | 2 | 0 / 14 (ok) |
| nine_knot_drawn | parity | cap | [9, 24, 54, 117, 259, 597, 1426, 3516, 8911] | growing | 1/8902 | 1 | 0 / 5 (ok) |
| nine_knot_drawn | nae (history shared with parity) | cap | [9, 24, 54, 117, 259, 597, 1426, 3516, 8911] | growing | 1/8902 | 1 | 0 / 5 (ok) |
| seven_knot | parity | cap | [7, 15, 27, 46, 78, 134, 235, 420, 765, 1420, 2683, 5146, 9993, 19614] | growing | 0/19607 | 1 | 0 / 2 (ok) |
| seven_knot | nae (history shared with parity) | cap | [7, 15, 27, 46, 78, 134, 235, 420, 765, 1420, 2683, 5146, 9993, 19614] | growing | 0/19607 | 1 | 0 / 2 (ok) |

## Removal bounds at the first failing stage (P3 starts that fail)
66 failing P3 histories; upper bound computed for 66 (min 1, median 1.0, max 6); lower bound min 0, max 0; comparison {'lower<=upper': 66, 'lower<upper': 66}. First failing step distribution: {1: 4, 2: 2, 3: 60}

## P3: ordinary growth against its rewiring
| Law | Arm (extra meetings) | Starts | Funded (at least one step) | Start or a rewiring fails | First failing step of the start no earlier than the median of its rewirings' | Fail within horizon: start | Fail: at least one rewiring |
| --- | --- | ---: | ---: | ---: | --- | ---: | ---: |
| parity | 0 | 256 | 69 | 69 | 69/69 (100.0%) | 15 | 69 |
| parity | 1 | 256 | 29 | 29 | 29/29 (100.0%) | 7 | 29 |
| parity | 2 | 256 | 69 | 41 | 40/41 (97.6%) | 8 | 41 |
| parity | 3 | 256 | 113 | 51 | 51/51 (100.0%) | 3 | 51 |
| parity | all | 1024 | 280 | 190 | 189/190 (99.5%) | 33 | 190 |
| nae | 0 | 256 | 69 | 69 | 69/69 (100.0%) | 15 | 69 |
| nae | 1 | 256 | 29 | 29 | 29/29 (100.0%) | 7 | 29 |
| nae | 2 | 256 | 69 | 58 | 57/58 (98.3%) | 8 | 58 |
| nae | 3 | 256 | 113 | 98 | 98/98 (100.0%) | 3 | 98 |
| nae | all | 1024 | 280 | 254 | 253/254 (99.6%) | 33 | 254 |
| both | 0 | 512 | 138 | 138 | 138/138 (100.0%) | 30 | 138 |
| both | 1 | 512 | 58 | 58 | 58/58 (100.0%) | 14 | 58 |
| both | 2 | 512 | 138 | 99 | 97/99 (98.0%) | 16 | 99 |
| both | 3 | 512 | 226 | 149 | 149/149 (100.0%) | 6 | 149 |
| both | all | 2048 | 560 | 444 | 442/444 (99.5%) | 66 | 444 |

Primary reading (no failure = +infinity; median = mean of the 4th and 5th smallest of eight): 442/444 (99.5%); lower median: 444/444 (100.0%); no failure coded last stage + 1: 442/444 (99.5%). Prediction P3 holds when the share is at least 3/4.
Starts compared with the median of their rewirings (primary reading): {'start later than median': 421, 'equal': 21, 'start earlier than median': 2}.

Qualifying starts by whether the start passes and how many of its eight rewirings fail (within the horizon): {'start fails; 5 of 8 rewirings fail': 1, 'start fails; 8 of 8 rewirings fail': 65, 'start passes; 1 of 8 rewirings fail': 5, 'start passes; 6 of 8 rewirings fail': 6, 'start passes; 7 of 8 rewirings fail': 2, 'start passes; 8 of 8 rewirings fail': 365}
Median first failing step of the rewirings (inf = at least five of eight rewirings pass throughout): {'inf': 5, 1.0: 2, 1.5: 6, 2.0: 96, 2.5: 26, 3.0: 92, 3.5: 8, 4.0: 100, 4.5: 10, 5.0: 26, 5.5: 2, 6.0: 21, 6.5: 3, 7.0: 41, 7.5: 3, 8.0: 2, 8.5: 1}
Starts whose first failing step is earlier than the rewiring median (the exceptions to P3): [{"law": "nae", "arm": 2, "draw": 180, "start_first_failing_step": 1, "rewirings_first_failing_step": [4, 2, 4, 1, 1, 1, 2, 1], "steps": 12, "n_at": [7, 10, 14, 19, 25, 32, 40, 49, 59, 70, 82, 95, 109]}, {"law": "parity", "arm": 2, "draw": 180, "start_first_failing_step": 1, "rewirings_first_failing_step": [4, 2, 4, 1, 1, 1, 2, 1], "steps": 12, "n_at": [7, 10, 14, 19, 25, 32, 40, 49, 59, 70, 82, 95, 109]}]
Rewirings of funded starts: 4480; with any shortfall: 70; total parents missing: 70; births with a shortfall: 70.

First step funded (starts with at least one parent step): parity arm 0: 69/256; parity arm 1: 29/256; parity arm 2: 69/256; parity arm 3: 113/256; nae arm 0: 69/256; nae arm 1: 29/256; nae arm 2: 69/256; nae arm 3: 113/256

## P4: closed parity parts met
Closed parity parts met (P2 and P3, parity law): 91; checked by the independent signed-operator solver: 91; not checked: 0 (Counter()); admits and fails T: 1; neither: 90; disagreements: 0.
Breakdown (population, T, admits): ('P3', 'fail', True): 1; ('P3', 'pass', False): 90
Closed parts by (knots, distinctions): {(4, 6): 13, (5, 7): 33, (5, 8): 10, (5, 9): 1, (6, 8): 1, (6, 9): 9, (6, 10): 2, (6, 11): 4, (7, 11): 1, (8, 12): 5, (8, 13): 2, (8, 14): 1, (12, 19): 1, (12, 20): 7, (13, 23): 1}
