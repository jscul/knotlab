# Construction addendum, written before any joint start is grown

Experiment `REVIEW-LEADS-20261123-001D-E001`. Frozen text of this file is hashed in `artifacts/REVIEW-LEADS-20261123-001D/REVIEW-LEADS-20261123-001D-E001_shared_supply/construction_addendum.sha256` before `gate.py` stage 2 or `grow.py` writes a single birth of a joint start. It supplements, and changes no definition in, `research/REVIEW-LEADS-20261123-001D/preregistration.md`.

**Disclosure.** Before this file was written one ordinary growth of the repaired S1-type merge (both ring originals, shortage repair) was run in a scratch script outside the experiment folder to size the horizon: births per parent step 22, 36, 59, 101, 176, 320, 595 through step 7. No other joint start was grown and no outcome of any serial rule was read before this file was hashed.

## 1. Which sources can be placed in a joint start inside the frozen horizon

The horizon is 400 births or 12 completed parent steps. Gate 1 (`gate.py 1`, `gate1.json`) measures the ordinary growth of each recorded source alone. Only the clock of the scarcity study, the eight-knot ring with one marked spare, has a recorded tick inside the horizon (parent steps 6 and 10). The seven-knot source, the nine-knot drawn source and the two clocks of the 21-knot structure first tick at parent steps 15 to 31, after the cumulative ordinary births have passed 400 at step 7, 5 and 5 respectively. Those four are left out of the joint starts and recorded in `deviations.md`. Every joint start below therefore joins two copies of the scarcity clock, each copy taken at the cut where the donor is a knot of the recorded history.

Gate 1 as run (`gate1.json`):

| source alone | ordinary growth: tick made at step | guarded rule: tick made at birth number | recompute rule, `unrestricted`: first tick | recompute rule: second tick |
| --- | --- | --- | --- | --- |
| R0 | tick 6: 6, tick 10: 10 | tick 6: 56, tick 10: 128 | made (20 births, 1797 states) | budget (20001 states) |
| R5 | tick 6: 1, tick 10: 5 | tick 6: 1, tick 10: 73 | made (1 births, 2 states) | exhausted (193 states) |
| R9 | tick 10: 1 | tick 10: 1 | made (1 births, 2 states) | none recorded after the stage |

Under the `joins_first` pool the first tick is reproduced alone for R5, R9 and not for R0 (exhausted at 745 states).

Births at the recorded cuts (5, 6, 9, 10) agree with the scarcity receipt for the bare ring and both attachments. Other sources: clock_21_knot: cumulative ordinary births pass 400 at step 5, first recorded tick at step 31, 47; nine_knot: cumulative ordinary births pass 400 at step 5, first recorded tick at step 17; seven_knot: cumulative ordinary births pass 400 at step 7, first recorded tick at step 15.

## 2. The construction

A source is a presentation: the original ring, or the ring after 5 or 9 complete ordinary parent steps (the warm stages that the scarcity study already uses). Its donor is a knot that pays into its tick: an original (the ring knot opposite the marked one, or the marked one that holds the spare) or the first parent of a tick (knot 57 of the 63-knot stage for tick 6, knot 126 of the 135-knot stage for tick 10). The joint start is the disjoint union of the two presentations with the two donors made one knot. The merged knot holds both supports (every shared distinction and every loose distinction of both), less the shortfall s: s = 1 removes one loose distinction of the second source's part. A knot's holdings are never changed afterwards.

Why the stage cuts: under ordinary growth every live knot pays all its loose distinctions in the single parent step after its birth (each leftover loose distinction pays one unary birth). Two sources that share one knot therefore always ask it in the same parent step of the joint growth. Two donors can differ only in recorded time: the step of the source's own recorded history at which its tick first draws on the donor (donor birth depth + 1). A pair is called **same-step** when these recorded steps are equal and **staggered** when they differ. A pair that differs in the step of the joint growth does not exist for a shared knot (stated, not tested).

Merging two live knots that each have live neighbours changes the proposals: the merged knot is a common witness of its neighbours on both sides, so the four cross pairs between them are new proposals. With both donors original ring knots this is S1 below: the unfunded merge stalls at step 1 with the shortages listed. S1 is run with those exact shortages repaired (extra loose slots at the four neighbours, as the scarcity study's attachment does at a host's neighbours), reported as a second version of the definition. A donor whose neighbours on one side are all spent (a stage knot) creates no cross pair; S2, T1, T2 and T3 need no repair.

## 3. The sources

| source | stage | donor (id in stage) | recorded first ask | loose at donor | demand on donor (plan births through it) | roles through donor needed for tick 6 / tick 10 |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| R0 | 0 | 4 | step 1 | 2 | 2 | tick 6: 2, tick 10: 2 |
| R0m | 0 | 0 | step 1 | 3 | 3 | tick 6: 3, tick 10: 3 |
| R5 | 5 | 57 | step 6 | 3 | 3 | tick 6: 1, tick 10: 1 |
| R9 | 9 | 126 | step 10 | 4 | 4 | tick 10: 1 |

## 4. The joint starts

| start | class | X + Y | knots | donor | donor loose s=0 / s=1 | demand X + Y | recorded first asks | step-1 plan s=0 | step-1 plan s=1 |
| --- | --- | --- | ---: | ---: | --- | --- | --- | --- | --- |
| S1 | same-step | R0 + R0 | 15 | 4 | 4 / 3 | 2 + 2 | 1 / 1 | extend, 22 births | stall, shortages [[4, 1]] |
| S2 | same-step | R5 + R5 | 125 | 57 | 6 / 5 | 3 + 3 | 6 / 6 | extend, 30 births | stall, shortages [[57, 1]] |
| T1 | staggered | R0 + R5 | 70 | 4 | 5 / 4 | 2 + 3 | 1 / 6 | extend, 24 births | stall, shortages [[4, 1]] |
| T2 | staggered | R5 + R9 | 197 | 57 | 7 / 6 | 3 + 4 | 6 / 10 | extend, 39 births | stall, shortages [[57, 1]] |
| T3 | staggered | R0m + R5 | 70 | 0 | 6 / 5 | 3 + 3 | 1 / 6 | extend, 24 births | extend, 23 births |

### S1: same-step (recorded first asks 1 and 1), original donors

X = R0, Y = R0. The donor is joint knot 4, arity 8, shared with knots [3, 5, 11, 12] through 4 distinctions, loose 4 (s = 0) or 3 (s = 1).
Unfunded merge: step-1 status `stall`, shortages (knot, missing) [[3, 2], [5, 2], [11, 2], [12, 2]]. Repair used: extra loose slots {3: 2, 5: 2, 11: 2, 12: 2}.
At s = 0 the first step is funded with 22 births; 4 of them take a loose distinction of the donor (2 from X's side, 2 from Y's, 0 cross, 0 unary). Proposals not in either source's alone plan: [[3, 11], [3, 12], [5, 11], [5, 12]]; alone proposals missing from the joint plan: 0.
At s = 1 the first step stalls with shortages [[4, 1]].
Lawfulness (`certify_source`, both laws): every star's projected relation equals its full relation (fixtures.certify_source); the knotlab K1-K3 checker is run on the relation of every arity up to 5, larger arities use the same expected relation; the same for not-all-equal; also at s = 1.

Every knot (id, origin X/Y/D, recorded birth depth, arity, loose, shared with):

```
  0 X d0  arity 5  loose 3  shared [1, 7]
  1 X d0  arity 4  loose 2  shared [0, 2]
  2 X d0  arity 4  loose 2  shared [1, 3]
  3 X d0  arity 6  loose 4  shared [2, 4]
  4 D d0  arity 8  loose 4  shared [3, 5, 11, 12]
  5 X d0  arity 6  loose 4  shared [4, 6]
  6 X d0  arity 4  loose 2  shared [5, 7]
  7 X d0  arity 4  loose 2  shared [0, 6]
  8 Y d0  arity 5  loose 3  shared [9, 14]
  9 Y d0  arity 4  loose 2  shared [8, 10]
 10 Y d0  arity 4  loose 2  shared [9, 11]
 11 Y d0  arity 6  loose 4  shared [4, 10]
 12 Y d0  arity 6  loose 4  shared [4, 13]
 13 Y d0  arity 4  loose 2  shared [12, 14]
 14 Y d0  arity 4  loose 2  shared [8, 13]
```

### S2: same-step (recorded first asks 6 and 6), first parents of tick 6

X = R5, Y = R5. The donor is joint knot 57, arity 10, shared with knots [43, 44, 106, 107] through 4 distinctions, loose 6 (s = 0) or 5 (s = 1).
At s = 0 the first step is funded with 30 births; 6 of them take a loose distinction of the donor (3 from X's side, 3 from Y's, 0 cross, 0 unary). Proposals not in either source's alone plan: []; alone proposals missing from the joint plan: 0.
At s = 1 the first step stalls with shortages [[57, 1]].
Lawfulness (`certify_source`, both laws): every star's projected relation equals its full relation (fixtures.certify_source); the knotlab K1-K3 checker is run on the relation of every arity up to 5, larger arities use the same expected relation; the same for not-all-equal; also at s = 1.

Every knot (id, origin X/Y/D, recorded birth depth, arity, loose, shared with):

```
  0 X d0  arity 5  loose 0  shared [1, 7, 8, 9, 16]
  1 X d0  arity 4  loose 0  shared [0, 2, 10, 11]
  2 X d0  arity 4  loose 0  shared [1, 3, 8, 12]
  3 X d0  arity 4  loose 0  shared [2, 4, 10, 13]
  4 X d0  arity 4  loose 0  shared [3, 5, 12, 14]
  5 X d0  arity 4  loose 0  shared [4, 6, 13, 15]
  6 X d0  arity 4  loose 0  shared [5, 7, 9, 14]
  7 X d0  arity 4  loose 0  shared [0, 6, 11, 15]
  8 X d1  arity 5  loose 0  shared [0, 2, 17, 18, 19]
  9 X d1  arity 5  loose 0  shared [0, 6, 17, 20, 21]
 10 X d0  arity 4  loose 0  shared [1, 3, 22, 23]
 11 X d0  arity 4  loose 0  shared [1, 7, 22, 24]
 12 X d1  arity 4  loose 0  shared [2, 4, 18, 25]
 13 X d0  arity 4  loose 0  shared [3, 5, 23, 26]
 14 X d1  arity 4  loose 0  shared [4, 6, 20, 25]
 15 X d0  arity 4  loose 0  shared [5, 7, 24, 26]
 16 X d1  arity 3  loose 0  shared [0, 19, 21]
 17 X d2  arity 5  loose 0  shared [8, 9, 27, 28, 29]
 18 X d2  arity 5  loose 0  shared [8, 12, 28, 30, 31]
 19 X d2  arity 4  loose 0  shared [8, 16, 27, 30]
 20 X d2  arity 5  loose 0  shared [9, 14, 29, 32, 33]
 21 X d2  arity 4  loose 0  shared [9, 16, 27, 32]
 22 X d0  arity 4  loose 0  shared [10, 11, 34, 35]
 23 X d0  arity 4  loose 0  shared [10, 13, 34, 36]
 24 X d0  arity 4  loose 0  shared [11, 15, 35, 37]
 25 X d2  arity 4  loose 0  shared [12, 14, 31, 33]
 26 X d0  arity 4  loose 0  shared [13, 15, 36, 37]
 27 X d3  arity 5  loose 0  shared [17, 19, 21, 38, 39]
 28 X d3  arity 5  loose 0  shared [17, 18, 38, 40, 41]
 29 X d3  arity 5  loose 0  shared [17, 20, 39, 40, 42]
 30 X d3  arity 4  loose 0  shared [18, 19, 38, 43]
 31 X d3  arity 5  loose 0  shared [18, 25, 41, 43, 44]
 32 X d3  arity 4  loose 0  shared [20, 21, 39, 45]
 33 X d3  arity 5  loose 0  shared [20, 25, 42, 44, 45]
 34 X d0  arity 4  loose 0  shared [22, 23, 46, 47]
 35 X d0  arity 4  loose 0  shared [22, 24, 46, 48]
 36 X d0  arity 4  loose 0  shared [23, 26, 47, 49]
 37 X d0  arity 4  loose 0  shared [24, 26, 48, 49]
 38 X d4  arity 5  loose 0  shared [27, 28, 30, 50, 51]
 39 X d4  arity 5  loose 0  shared [27, 29, 32, 50, 52]
 40 X d4  arity 5  loose 0  shared [28, 29, 50, 53, 54]
 41 X d4  arity 5  loose 0  shared [28, 31, 51, 53, 55]
 42 X d4  arity 5  loose 0  shared [29, 33, 52, 54, 56]
 43 X d4  arity 4  loose 0  shared [30, 31, 51, 57]
 44 X d4  arity 6  loose 0  shared [31, 33, 55, 56, 57, 58]
 45 X d4  arity 4  loose 0  shared [32, 33, 52, 58]
 46 X d0  arity 4  loose 0  shared [34, 35, 59, 60]
 47 X d0  arity 4  loose 0  shared [34, 36, 59, 61]
 48 X d0  arity 4  loose 0  shared [35, 37, 60, 62]
 49 X d0  arity 4  loose 0  shared [36, 37, 61, 62]
 50 X d5  arity 5  loose 2  shared [38, 39, 40]
 51 X d5  arity 5  loose 2  shared [38, 41, 43]
 52 X d5  arity 5  loose 2  shared [39, 42, 45]
 53 X d5  arity 5  loose 3  shared [40, 41]
 54 X d5  arity 5  loose 3  shared [40, 42]
 55 X d5  arity 6  loose 4  shared [41, 44]
 56 X d5  arity 6  loose 4  shared [42, 44]
 57 D d5  arity 10 loose 6  shared [43, 44, 106, 107]
 58 X d5  arity 5  loose 3  shared [44, 45]
 59 X d0  arity 4  loose 2  shared [46, 47]
 60 X d0  arity 4  loose 2  shared [46, 48]
 61 X d0  arity 4  loose 2  shared [47, 49]
 62 X d0  arity 4  loose 2  shared [48, 49]
 63 Y d0  arity 5  loose 0  shared [64, 70, 71, 72, 79]
 64 Y d0  arity 4  loose 0  shared [63, 65, 73, 74]
 65 Y d0  arity 4  loose 0  shared [64, 66, 71, 75]
 66 Y d0  arity 4  loose 0  shared [65, 67, 73, 76]
 67 Y d0  arity 4  loose 0  shared [66, 68, 75, 77]
 68 Y d0  arity 4  loose 0  shared [67, 69, 76, 78]
 69 Y d0  arity 4  loose 0  shared [68, 70, 72, 77]
 70 Y d0  arity 4  loose 0  shared [63, 69, 74, 78]
 71 Y d1  arity 5  loose 0  shared [63, 65, 80, 81, 82]
 72 Y d1  arity 5  loose 0  shared [63, 69, 80, 83, 84]
 73 Y d0  arity 4  loose 0  shared [64, 66, 85, 86]
 74 Y d0  arity 4  loose 0  shared [64, 70, 85, 87]
 75 Y d1  arity 4  loose 0  shared [65, 67, 81, 88]
 76 Y d0  arity 4  loose 0  shared [66, 68, 86, 89]
 77 Y d1  arity 4  loose 0  shared [67, 69, 83, 88]
 78 Y d0  arity 4  loose 0  shared [68, 70, 87, 89]
 79 Y d1  arity 3  loose 0  shared [63, 82, 84]
 80 Y d2  arity 5  loose 0  shared [71, 72, 90, 91, 92]
 81 Y d2  arity 5  loose 0  shared [71, 75, 91, 93, 94]
 82 Y d2  arity 4  loose 0  shared [71, 79, 90, 93]
 83 Y d2  arity 5  loose 0  shared [72, 77, 92, 95, 96]
 84 Y d2  arity 4  loose 0  shared [72, 79, 90, 95]
 85 Y d0  arity 4  loose 0  shared [73, 74, 97, 98]
 86 Y d0  arity 4  loose 0  shared [73, 76, 97, 99]
 87 Y d0  arity 4  loose 0  shared [74, 78, 98, 100]
 88 Y d2  arity 4  loose 0  shared [75, 77, 94, 96]
 89 Y d0  arity 4  loose 0  shared [76, 78, 99, 100]
 90 Y d3  arity 5  loose 0  shared [80, 82, 84, 101, 102]
 91 Y d3  arity 5  loose 0  shared [80, 81, 101, 103, 104]
 92 Y d3  arity 5  loose 0  shared [80, 83, 102, 103, 105]
 93 Y d3  arity 4  loose 0  shared [81, 82, 101, 106]
 94 Y d3  arity 5  loose 0  shared [81, 88, 104, 106, 107]
 95 Y d3  arity 4  loose 0  shared [83, 84, 102, 108]
 96 Y d3  arity 5  loose 0  shared [83, 88, 105, 107, 108]
 97 Y d0  arity 4  loose 0  shared [85, 86, 109, 110]
 98 Y d0  arity 4  loose 0  shared [85, 87, 109, 111]
 99 Y d0  arity 4  loose 0  shared [86, 89, 110, 112]
100 Y d0  arity 4  loose 0  shared [87, 89, 111, 112]
101 Y d4  arity 5  loose 0  shared [90, 91, 93, 113, 114]
102 Y d4  arity 5  loose 0  shared [90, 92, 95, 113, 115]
103 Y d4  arity 5  loose 0  shared [91, 92, 113, 116, 117]
104 Y d4  arity 5  loose 0  shared [91, 94, 114, 116, 118]
105 Y d4  arity 5  loose 0  shared [92, 96, 115, 117, 119]
106 Y d4  arity 4  loose 0  shared [57, 93, 94, 114]
107 Y d4  arity 6  loose 0  shared [57, 94, 96, 118, 119, 120]
108 Y d4  arity 4  loose 0  shared [95, 96, 115, 120]
109 Y d0  arity 4  loose 0  shared [97, 98, 121, 122]
110 Y d0  arity 4  loose 0  shared [97, 99, 121, 123]
111 Y d0  arity 4  loose 0  shared [98, 100, 122, 124]
112 Y d0  arity 4  loose 0  shared [99, 100, 123, 124]
113 Y d5  arity 5  loose 2  shared [101, 102, 103]
114 Y d5  arity 5  loose 2  shared [101, 104, 106]
115 Y d5  arity 5  loose 2  shared [102, 105, 108]
116 Y d5  arity 5  loose 3  shared [103, 104]
117 Y d5  arity 5  loose 3  shared [103, 105]
118 Y d5  arity 6  loose 4  shared [104, 107]
119 Y d5  arity 6  loose 4  shared [105, 107]
120 Y d5  arity 5  loose 3  shared [107, 108]
121 Y d0  arity 4  loose 2  shared [109, 110]
122 Y d0  arity 4  loose 2  shared [109, 111]
123 Y d0  arity 4  loose 2  shared [110, 112]
124 Y d0  arity 4  loose 2  shared [111, 112]
```

### T1: staggered (recorded first asks 1 and 6)

X = R0, Y = R5. The donor is joint knot 4, arity 9, shared with knots [3, 5, 51, 52] through 4 distinctions, loose 5 (s = 0) or 4 (s = 1).
At s = 0 the first step is funded with 24 births; 5 of them take a loose distinction of the donor (2 from X's side, 3 from Y's, 0 cross, 0 unary). Proposals not in either source's alone plan: []; alone proposals missing from the joint plan: 0.
At s = 1 the first step stalls with shortages [[4, 1]].
Lawfulness (`certify_source`, both laws): every star's projected relation equals its full relation (fixtures.certify_source); the knotlab K1-K3 checker is run on the relation of every arity up to 5, larger arities use the same expected relation; the same for not-all-equal; also at s = 1.

Every knot (id, origin X/Y/D, recorded birth depth, arity, loose, shared with):

```
  0 X d0  arity 5  loose 3  shared [1, 7]
  1 X d0  arity 4  loose 2  shared [0, 2]
  2 X d0  arity 4  loose 2  shared [1, 3]
  3 X d0  arity 4  loose 2  shared [2, 4]
  4 D d0  arity 9  loose 5  shared [3, 5, 51, 52]
  5 X d0  arity 4  loose 2  shared [4, 6]
  6 X d0  arity 4  loose 2  shared [5, 7]
  7 X d0  arity 4  loose 2  shared [0, 6]
  8 Y d0  arity 5  loose 0  shared [9, 15, 16, 17, 24]
  9 Y d0  arity 4  loose 0  shared [8, 10, 18, 19]
 10 Y d0  arity 4  loose 0  shared [9, 11, 16, 20]
 11 Y d0  arity 4  loose 0  shared [10, 12, 18, 21]
 12 Y d0  arity 4  loose 0  shared [11, 13, 20, 22]
 13 Y d0  arity 4  loose 0  shared [12, 14, 21, 23]
 14 Y d0  arity 4  loose 0  shared [13, 15, 17, 22]
 15 Y d0  arity 4  loose 0  shared [8, 14, 19, 23]
 16 Y d1  arity 5  loose 0  shared [8, 10, 25, 26, 27]
 17 Y d1  arity 5  loose 0  shared [8, 14, 25, 28, 29]
 18 Y d0  arity 4  loose 0  shared [9, 11, 30, 31]
 19 Y d0  arity 4  loose 0  shared [9, 15, 30, 32]
 20 Y d1  arity 4  loose 0  shared [10, 12, 26, 33]
 21 Y d0  arity 4  loose 0  shared [11, 13, 31, 34]
 22 Y d1  arity 4  loose 0  shared [12, 14, 28, 33]
 23 Y d0  arity 4  loose 0  shared [13, 15, 32, 34]
 24 Y d1  arity 3  loose 0  shared [8, 27, 29]
 25 Y d2  arity 5  loose 0  shared [16, 17, 35, 36, 37]
 26 Y d2  arity 5  loose 0  shared [16, 20, 36, 38, 39]
 27 Y d2  arity 4  loose 0  shared [16, 24, 35, 38]
 28 Y d2  arity 5  loose 0  shared [17, 22, 37, 40, 41]
 29 Y d2  arity 4  loose 0  shared [17, 24, 35, 40]
 30 Y d0  arity 4  loose 0  shared [18, 19, 42, 43]
 31 Y d0  arity 4  loose 0  shared [18, 21, 42, 44]
 32 Y d0  arity 4  loose 0  shared [19, 23, 43, 45]
 33 Y d2  arity 4  loose 0  shared [20, 22, 39, 41]
 34 Y d0  arity 4  loose 0  shared [21, 23, 44, 45]
 35 Y d3  arity 5  loose 0  shared [25, 27, 29, 46, 47]
 36 Y d3  arity 5  loose 0  shared [25, 26, 46, 48, 49]
 37 Y d3  arity 5  loose 0  shared [25, 28, 47, 48, 50]
 38 Y d3  arity 4  loose 0  shared [26, 27, 46, 51]
 39 Y d3  arity 5  loose 0  shared [26, 33, 49, 51, 52]
 40 Y d3  arity 4  loose 0  shared [28, 29, 47, 53]
 41 Y d3  arity 5  loose 0  shared [28, 33, 50, 52, 53]
 42 Y d0  arity 4  loose 0  shared [30, 31, 54, 55]
 43 Y d0  arity 4  loose 0  shared [30, 32, 54, 56]
 44 Y d0  arity 4  loose 0  shared [31, 34, 55, 57]
 45 Y d0  arity 4  loose 0  shared [32, 34, 56, 57]
 46 Y d4  arity 5  loose 0  shared [35, 36, 38, 58, 59]
 47 Y d4  arity 5  loose 0  shared [35, 37, 40, 58, 60]
 48 Y d4  arity 5  loose 0  shared [36, 37, 58, 61, 62]
 49 Y d4  arity 5  loose 0  shared [36, 39, 59, 61, 63]
 50 Y d4  arity 5  loose 0  shared [37, 41, 60, 62, 64]
 51 Y d4  arity 4  loose 0  shared [4, 38, 39, 59]
 52 Y d4  arity 6  loose 0  shared [4, 39, 41, 63, 64, 65]
 53 Y d4  arity 4  loose 0  shared [40, 41, 60, 65]
 54 Y d0  arity 4  loose 0  shared [42, 43, 66, 67]
 55 Y d0  arity 4  loose 0  shared [42, 44, 66, 68]
 56 Y d0  arity 4  loose 0  shared [43, 45, 67, 69]
 57 Y d0  arity 4  loose 0  shared [44, 45, 68, 69]
 58 Y d5  arity 5  loose 2  shared [46, 47, 48]
 59 Y d5  arity 5  loose 2  shared [46, 49, 51]
 60 Y d5  arity 5  loose 2  shared [47, 50, 53]
 61 Y d5  arity 5  loose 3  shared [48, 49]
 62 Y d5  arity 5  loose 3  shared [48, 50]
 63 Y d5  arity 6  loose 4  shared [49, 52]
 64 Y d5  arity 6  loose 4  shared [50, 52]
 65 Y d5  arity 5  loose 3  shared [52, 53]
 66 Y d0  arity 4  loose 2  shared [54, 55]
 67 Y d0  arity 4  loose 2  shared [54, 56]
 68 Y d0  arity 4  loose 2  shared [55, 57]
 69 Y d0  arity 4  loose 2  shared [56, 57]
```

### T2: staggered (recorded first asks 6 and 10)

X = R5, Y = R9. The donor is joint knot 57, arity 11, shared with knots [43, 44, 167, 169] through 4 distinctions, loose 7 (s = 0) or 6 (s = 1).
At s = 0 the first step is funded with 39 births; 7 of them take a loose distinction of the donor (3 from X's side, 4 from Y's, 0 cross, 0 unary). Proposals not in either source's alone plan: []; alone proposals missing from the joint plan: 0.
At s = 1 the first step stalls with shortages [[57, 1]].
Lawfulness (`certify_source`, both laws): every star's projected relation equals its full relation (fixtures.certify_source); the knotlab K1-K3 checker is run on the relation of every arity up to 5, larger arities use the same expected relation; the same for not-all-equal; also at s = 1.

Every knot (id, origin X/Y/D, recorded birth depth, arity, loose, shared with):

```
  0 X d0  arity 5  loose 0  shared [1, 7, 8, 9, 16]
  1 X d0  arity 4  loose 0  shared [0, 2, 10, 11]
  2 X d0  arity 4  loose 0  shared [1, 3, 8, 12]
  3 X d0  arity 4  loose 0  shared [2, 4, 10, 13]
  4 X d0  arity 4  loose 0  shared [3, 5, 12, 14]
  5 X d0  arity 4  loose 0  shared [4, 6, 13, 15]
  6 X d0  arity 4  loose 0  shared [5, 7, 9, 14]
  7 X d0  arity 4  loose 0  shared [0, 6, 11, 15]
  8 X d1  arity 5  loose 0  shared [0, 2, 17, 18, 19]
  9 X d1  arity 5  loose 0  shared [0, 6, 17, 20, 21]
 10 X d0  arity 4  loose 0  shared [1, 3, 22, 23]
 11 X d0  arity 4  loose 0  shared [1, 7, 22, 24]
 12 X d1  arity 4  loose 0  shared [2, 4, 18, 25]
 13 X d0  arity 4  loose 0  shared [3, 5, 23, 26]
 14 X d1  arity 4  loose 0  shared [4, 6, 20, 25]
 15 X d0  arity 4  loose 0  shared [5, 7, 24, 26]
 16 X d1  arity 3  loose 0  shared [0, 19, 21]
 17 X d2  arity 5  loose 0  shared [8, 9, 27, 28, 29]
 18 X d2  arity 5  loose 0  shared [8, 12, 28, 30, 31]
 19 X d2  arity 4  loose 0  shared [8, 16, 27, 30]
 20 X d2  arity 5  loose 0  shared [9, 14, 29, 32, 33]
 21 X d2  arity 4  loose 0  shared [9, 16, 27, 32]
 22 X d0  arity 4  loose 0  shared [10, 11, 34, 35]
 23 X d0  arity 4  loose 0  shared [10, 13, 34, 36]
 24 X d0  arity 4  loose 0  shared [11, 15, 35, 37]
 25 X d2  arity 4  loose 0  shared [12, 14, 31, 33]
 26 X d0  arity 4  loose 0  shared [13, 15, 36, 37]
 27 X d3  arity 5  loose 0  shared [17, 19, 21, 38, 39]
 28 X d3  arity 5  loose 0  shared [17, 18, 38, 40, 41]
 29 X d3  arity 5  loose 0  shared [17, 20, 39, 40, 42]
 30 X d3  arity 4  loose 0  shared [18, 19, 38, 43]
 31 X d3  arity 5  loose 0  shared [18, 25, 41, 43, 44]
 32 X d3  arity 4  loose 0  shared [20, 21, 39, 45]
 33 X d3  arity 5  loose 0  shared [20, 25, 42, 44, 45]
 34 X d0  arity 4  loose 0  shared [22, 23, 46, 47]
 35 X d0  arity 4  loose 0  shared [22, 24, 46, 48]
 36 X d0  arity 4  loose 0  shared [23, 26, 47, 49]
 37 X d0  arity 4  loose 0  shared [24, 26, 48, 49]
 38 X d4  arity 5  loose 0  shared [27, 28, 30, 50, 51]
 39 X d4  arity 5  loose 0  shared [27, 29, 32, 50, 52]
 40 X d4  arity 5  loose 0  shared [28, 29, 50, 53, 54]
 41 X d4  arity 5  loose 0  shared [28, 31, 51, 53, 55]
 42 X d4  arity 5  loose 0  shared [29, 33, 52, 54, 56]
 43 X d4  arity 4  loose 0  shared [30, 31, 51, 57]
 44 X d4  arity 6  loose 0  shared [31, 33, 55, 56, 57, 58]
 45 X d4  arity 4  loose 0  shared [32, 33, 52, 58]
 46 X d0  arity 4  loose 0  shared [34, 35, 59, 60]
 47 X d0  arity 4  loose 0  shared [34, 36, 59, 61]
 48 X d0  arity 4  loose 0  shared [35, 37, 60, 62]
 49 X d0  arity 4  loose 0  shared [36, 37, 61, 62]
 50 X d5  arity 5  loose 2  shared [38, 39, 40]
 51 X d5  arity 5  loose 2  shared [38, 41, 43]
 52 X d5  arity 5  loose 2  shared [39, 42, 45]
 53 X d5  arity 5  loose 3  shared [40, 41]
 54 X d5  arity 5  loose 3  shared [40, 42]
 55 X d5  arity 6  loose 4  shared [41, 44]
 56 X d5  arity 6  loose 4  shared [42, 44]
 57 D d5  arity 11 loose 7  shared [43, 44, 167, 169]
 58 X d5  arity 5  loose 3  shared [44, 45]
 59 X d0  arity 4  loose 2  shared [46, 47]
 60 X d0  arity 4  loose 2  shared [46, 48]
 61 X d0  arity 4  loose 2  shared [47, 49]
 62 X d0  arity 4  loose 2  shared [48, 49]
 63 Y d0  arity 5  loose 0  shared [64, 70, 71, 72, 79]
 64 Y d0  arity 4  loose 0  shared [63, 65, 73, 74]
 65 Y d0  arity 4  loose 0  shared [64, 66, 71, 75]
 66 Y d0  arity 4  loose 0  shared [65, 67, 73, 76]
 67 Y d0  arity 4  loose 0  shared [66, 68, 75, 77]
 68 Y d0  arity 4  loose 0  shared [67, 69, 76, 78]
 69 Y d0  arity 4  loose 0  shared [68, 70, 72, 77]
 70 Y d0  arity 4  loose 0  shared [63, 69, 74, 78]
 71 Y d1  arity 5  loose 0  shared [63, 65, 80, 81, 82]
 72 Y d1  arity 5  loose 0  shared [63, 69, 80, 83, 84]
 73 Y d0  arity 4  loose 0  shared [64, 66, 85, 86]
 74 Y d0  arity 4  loose 0  shared [64, 70, 85, 87]
 75 Y d1  arity 4  loose 0  shared [65, 67, 81, 88]
 76 Y d0  arity 4  loose 0  shared [66, 68, 86, 89]
 77 Y d1  arity 4  loose 0  shared [67, 69, 83, 88]
 78 Y d0  arity 4  loose 0  shared [68, 70, 87, 89]
 79 Y d1  arity 3  loose 0  shared [63, 82, 84]
 80 Y d2  arity 5  loose 0  shared [71, 72, 90, 91, 92]
 81 Y d2  arity 5  loose 0  shared [71, 75, 91, 93, 94]
 82 Y d2  arity 4  loose 0  shared [71, 79, 90, 93]
 83 Y d2  arity 5  loose 0  shared [72, 77, 92, 95, 96]
 84 Y d2  arity 4  loose 0  shared [72, 79, 90, 95]
 85 Y d0  arity 4  loose 0  shared [73, 74, 97, 98]
 86 Y d0  arity 4  loose 0  shared [73, 76, 97, 99]
 87 Y d0  arity 4  loose 0  shared [74, 78, 98, 100]
 88 Y d2  arity 4  loose 0  shared [75, 77, 94, 96]
 89 Y d0  arity 4  loose 0  shared [76, 78, 99, 100]
 90 Y d3  arity 5  loose 0  shared [80, 82, 84, 101, 102]
 91 Y d3  arity 5  loose 0  shared [80, 81, 101, 103, 104]
 92 Y d3  arity 5  loose 0  shared [80, 83, 102, 103, 105]
 93 Y d3  arity 4  loose 0  shared [81, 82, 101, 106]
 94 Y d3  arity 5  loose 0  shared [81, 88, 104, 106, 107]
 95 Y d3  arity 4  loose 0  shared [83, 84, 102, 108]
 96 Y d3  arity 5  loose 0  shared [83, 88, 105, 107, 108]
 97 Y d0  arity 4  loose 0  shared [85, 86, 109, 110]
 98 Y d0  arity 4  loose 0  shared [85, 87, 109, 111]
 99 Y d0  arity 4  loose 0  shared [86, 89, 110, 112]
100 Y d0  arity 4  loose 0  shared [87, 89, 111, 112]
101 Y d4  arity 5  loose 0  shared [90, 91, 93, 113, 114]
102 Y d4  arity 5  loose 0  shared [90, 92, 95, 113, 115]
103 Y d4  arity 5  loose 0  shared [91, 92, 113, 116, 117]
104 Y d4  arity 5  loose 0  shared [91, 94, 114, 116, 118]
105 Y d4  arity 5  loose 0  shared [92, 96, 115, 117, 119]
106 Y d4  arity 4  loose 0  shared [93, 94, 114, 120]
107 Y d4  arity 6  loose 0  shared [94, 96, 118, 119, 120, 121]
108 Y d4  arity 4  loose 0  shared [95, 96, 115, 121]
109 Y d0  arity 4  loose 0  shared [97, 98, 122, 123]
110 Y d0  arity 4  loose 0  shared [97, 99, 122, 124]
111 Y d0  arity 4  loose 0  shared [98, 100, 123, 125]
112 Y d0  arity 4  loose 0  shared [99, 100, 124, 125]
113 Y d5  arity 5  loose 0  shared [101, 102, 103, 126, 127]
114 Y d5  arity 5  loose 0  shared [101, 104, 106, 126, 128]
115 Y d5  arity 5  loose 0  shared [102, 105, 108, 127, 129]
116 Y d5  arity 5  loose 0  shared [103, 104, 126, 130, 131]
117 Y d5  arity 5  loose 0  shared [103, 105, 127, 130, 132]
118 Y d5  arity 6  loose 0  shared [104, 107, 128, 131, 133, 134]
119 Y d5  arity 6  loose 0  shared [105, 107, 129, 132, 133, 135]
120 Y d5  arity 5  loose 0  shared [106, 107, 128, 135, 136]
121 Y d5  arity 5  loose 0  shared [107, 108, 129, 134, 136]
122 Y d0  arity 4  loose 0  shared [109, 110, 137, 138]
123 Y d0  arity 4  loose 0  shared [109, 111, 137, 139]
124 Y d0  arity 4  loose 0  shared [110, 112, 138, 140]
125 Y d0  arity 4  loose 0  shared [111, 112, 139, 140]
126 Y d6  arity 5  loose 0  shared [113, 114, 116, 141, 142]
127 Y d6  arity 5  loose 0  shared [113, 115, 117, 141, 143]
128 Y d6  arity 6  loose 0  shared [114, 118, 120, 142, 144, 145]
129 Y d6  arity 6  loose 0  shared [115, 119, 121, 143, 146, 147]
130 Y d6  arity 5  loose 0  shared [116, 117, 141, 148, 149]
131 Y d6  arity 6  loose 0  shared [116, 118, 142, 148, 150, 151]
132 Y d6  arity 6  loose 0  shared [117, 119, 143, 149, 152, 153]
133 Y d6  arity 6  loose 0  shared [118, 119, 144, 146, 150, 152]
134 Y d6  arity 5  loose 0  shared [118, 121, 145, 146, 151]
135 Y d6  arity 5  loose 0  shared [119, 120, 144, 147, 153]
136 Y d6  arity 4  loose 0  shared [120, 121, 145, 147]
137 Y d0  arity 4  loose 0  shared [122, 123, 154, 155]
138 Y d0  arity 4  loose 0  shared [122, 124, 154, 156]
139 Y d0  arity 4  loose 0  shared [123, 125, 155, 157]
140 Y d0  arity 4  loose 0  shared [124, 125, 156, 157]
141 Y d7  arity 5  loose 0  shared [126, 127, 130, 158, 159]
142 Y d7  arity 6  loose 0  shared [126, 128, 131, 158, 160, 161]
143 Y d7  arity 6  loose 0  shared [127, 129, 132, 159, 162, 163]
144 Y d7  arity 6  loose 0  shared [128, 133, 135, 160, 164, 165]
145 Y d7  arity 5  loose 0  shared [128, 134, 136, 161, 164]
146 Y d7  arity 6  loose 0  shared [129, 133, 134, 162, 164, 166]
147 Y d7  arity 5  loose 0  shared [129, 135, 136, 163, 164]
148 Y d7  arity 6  loose 0  shared [130, 131, 158, 167, 168, 169]
149 Y d7  arity 6  loose 0  shared [130, 132, 159, 167, 170, 171]
150 Y d7  arity 6  loose 0  shared [131, 133, 160, 166, 168, 172]
151 Y d7  arity 5  loose 0  shared [131, 134, 161, 166, 169]
152 Y d7  arity 6  loose 0  shared [132, 133, 162, 165, 170, 172]
153 Y d7  arity 5  loose 0  shared [132, 135, 163, 165, 171]
154 Y d0  arity 4  loose 0  shared [137, 138, 173, 174]
155 Y d0  arity 4  loose 0  shared [137, 139, 173, 175]
156 Y d0  arity 4  loose 0  shared [138, 140, 174, 176]
157 Y d0  arity 4  loose 0  shared [139, 140, 175, 176]
158 Y d8  arity 6  loose 0  shared [141, 142, 148, 177, 178, 179]
159 Y d8  arity 6  loose 0  shared [141, 143, 149, 177, 180, 181]
160 Y d8  arity 6  loose 0  shared [142, 144, 150, 178, 182, 183]
161 Y d8  arity 5  loose 0  shared [142, 145, 151, 179, 182]
162 Y d8  arity 6  loose 0  shared [143, 146, 152, 180, 184, 185]
163 Y d8  arity 5  loose 0  shared [143, 147, 153, 181, 184]
164 Y d8  arity 6  loose 0  shared [144, 145, 146, 147, 182, 184]
165 Y d8  arity 6  loose 0  shared [144, 152, 153, 183, 184, 186]
166 Y d8  arity 6  loose 0  shared [146, 150, 151, 182, 185, 187]
167 Y d8  arity 7  loose 0  shared [57, 148, 149, 177, 188, 189, 190]
168 Y d8  arity 6  loose 0  shared [148, 150, 178, 187, 188, 191]
169 Y d8  arity 5  loose 0  shared [57, 148, 151, 179, 187]
170 Y d8  arity 6  loose 0  shared [149, 152, 180, 186, 189, 192]
171 Y d8  arity 5  loose 0  shared [149, 153, 181, 186, 190]
172 Y d8  arity 6  loose 0  shared [150, 152, 183, 185, 191, 192]
173 Y d0  arity 4  loose 0  shared [154, 155, 193, 194]
174 Y d0  arity 4  loose 0  shared [154, 156, 193, 195]
175 Y d0  arity 4  loose 0  shared [155, 157, 194, 196]
176 Y d0  arity 4  loose 0  shared [156, 157, 195, 196]
177 Y d9  arity 7  loose 4  shared [158, 159, 167]
178 Y d9  arity 6  loose 3  shared [158, 160, 168]
179 Y d9  arity 5  loose 2  shared [158, 161, 169]
180 Y d9  arity 6  loose 3  shared [159, 162, 170]
181 Y d9  arity 5  loose 2  shared [159, 163, 171]
182 Y d9  arity 6  loose 2  shared [160, 161, 164, 166]
183 Y d9  arity 6  loose 3  shared [160, 165, 172]
184 Y d9  arity 6  loose 2  shared [162, 163, 164, 165]
185 Y d9  arity 6  loose 3  shared [162, 166, 172]
186 Y d9  arity 6  loose 3  shared [165, 170, 171]
187 Y d9  arity 6  loose 3  shared [166, 168, 169]
188 Y d9  arity 7  loose 5  shared [167, 168]
189 Y d9  arity 7  loose 5  shared [167, 170]
190 Y d9  arity 6  loose 4  shared [167, 171]
191 Y d9  arity 6  loose 4  shared [168, 172]
192 Y d9  arity 6  loose 4  shared [170, 172]
193 Y d0  arity 4  loose 2  shared [173, 174]
194 Y d0  arity 4  loose 2  shared [173, 175]
195 Y d0  arity 4  loose 2  shared [174, 176]
196 Y d0  arity 4  loose 2  shared [175, 176]
```

### T3: staggered (recorded first asks 1 and 6), marked original with the spare

X = R0m, Y = R5. The donor is joint knot 0, arity 10, shared with knots [1, 7, 51, 52] through 4 distinctions, loose 6 (s = 0) or 5 (s = 1).
At s = 0 the first step is funded with 24 births; 6 of them take a loose distinction of the donor (2 from X's side, 3 from Y's, 0 cross, 1 unary). Proposals not in either source's alone plan: []; alone proposals missing from the joint plan: 0.
At s = 1 the first step is still funded, with 23 births: 5 take a loose distinction of the donor (2 from X's side, 3 from Y's, 0 unary). The one missing distinction removes the unary birth of the donor from the plan.
Lawfulness (`certify_source`, both laws): every star's projected relation equals its full relation (fixtures.certify_source); the knotlab K1-K3 checker is run on the relation of every arity up to 5, larger arities use the same expected relation; the same for not-all-equal; also at s = 1.

Every knot (id, origin X/Y/D, recorded birth depth, arity, loose, shared with):

```
  0 D d0  arity 10 loose 6  shared [1, 7, 51, 52]
  1 X d0  arity 4  loose 2  shared [0, 2]
  2 X d0  arity 4  loose 2  shared [1, 3]
  3 X d0  arity 4  loose 2  shared [2, 4]
  4 X d0  arity 4  loose 2  shared [3, 5]
  5 X d0  arity 4  loose 2  shared [4, 6]
  6 X d0  arity 4  loose 2  shared [5, 7]
  7 X d0  arity 4  loose 2  shared [0, 6]
  8 Y d0  arity 5  loose 0  shared [9, 15, 16, 17, 24]
  9 Y d0  arity 4  loose 0  shared [8, 10, 18, 19]
 10 Y d0  arity 4  loose 0  shared [9, 11, 16, 20]
 11 Y d0  arity 4  loose 0  shared [10, 12, 18, 21]
 12 Y d0  arity 4  loose 0  shared [11, 13, 20, 22]
 13 Y d0  arity 4  loose 0  shared [12, 14, 21, 23]
 14 Y d0  arity 4  loose 0  shared [13, 15, 17, 22]
 15 Y d0  arity 4  loose 0  shared [8, 14, 19, 23]
 16 Y d1  arity 5  loose 0  shared [8, 10, 25, 26, 27]
 17 Y d1  arity 5  loose 0  shared [8, 14, 25, 28, 29]
 18 Y d0  arity 4  loose 0  shared [9, 11, 30, 31]
 19 Y d0  arity 4  loose 0  shared [9, 15, 30, 32]
 20 Y d1  arity 4  loose 0  shared [10, 12, 26, 33]
 21 Y d0  arity 4  loose 0  shared [11, 13, 31, 34]
 22 Y d1  arity 4  loose 0  shared [12, 14, 28, 33]
 23 Y d0  arity 4  loose 0  shared [13, 15, 32, 34]
 24 Y d1  arity 3  loose 0  shared [8, 27, 29]
 25 Y d2  arity 5  loose 0  shared [16, 17, 35, 36, 37]
 26 Y d2  arity 5  loose 0  shared [16, 20, 36, 38, 39]
 27 Y d2  arity 4  loose 0  shared [16, 24, 35, 38]
 28 Y d2  arity 5  loose 0  shared [17, 22, 37, 40, 41]
 29 Y d2  arity 4  loose 0  shared [17, 24, 35, 40]
 30 Y d0  arity 4  loose 0  shared [18, 19, 42, 43]
 31 Y d0  arity 4  loose 0  shared [18, 21, 42, 44]
 32 Y d0  arity 4  loose 0  shared [19, 23, 43, 45]
 33 Y d2  arity 4  loose 0  shared [20, 22, 39, 41]
 34 Y d0  arity 4  loose 0  shared [21, 23, 44, 45]
 35 Y d3  arity 5  loose 0  shared [25, 27, 29, 46, 47]
 36 Y d3  arity 5  loose 0  shared [25, 26, 46, 48, 49]
 37 Y d3  arity 5  loose 0  shared [25, 28, 47, 48, 50]
 38 Y d3  arity 4  loose 0  shared [26, 27, 46, 51]
 39 Y d3  arity 5  loose 0  shared [26, 33, 49, 51, 52]
 40 Y d3  arity 4  loose 0  shared [28, 29, 47, 53]
 41 Y d3  arity 5  loose 0  shared [28, 33, 50, 52, 53]
 42 Y d0  arity 4  loose 0  shared [30, 31, 54, 55]
 43 Y d0  arity 4  loose 0  shared [30, 32, 54, 56]
 44 Y d0  arity 4  loose 0  shared [31, 34, 55, 57]
 45 Y d0  arity 4  loose 0  shared [32, 34, 56, 57]
 46 Y d4  arity 5  loose 0  shared [35, 36, 38, 58, 59]
 47 Y d4  arity 5  loose 0  shared [35, 37, 40, 58, 60]
 48 Y d4  arity 5  loose 0  shared [36, 37, 58, 61, 62]
 49 Y d4  arity 5  loose 0  shared [36, 39, 59, 61, 63]
 50 Y d4  arity 5  loose 0  shared [37, 41, 60, 62, 64]
 51 Y d4  arity 4  loose 0  shared [0, 38, 39, 59]
 52 Y d4  arity 6  loose 0  shared [0, 39, 41, 63, 64, 65]
 53 Y d4  arity 4  loose 0  shared [40, 41, 60, 65]
 54 Y d0  arity 4  loose 0  shared [42, 43, 66, 67]
 55 Y d0  arity 4  loose 0  shared [42, 44, 66, 68]
 56 Y d0  arity 4  loose 0  shared [43, 45, 67, 69]
 57 Y d0  arity 4  loose 0  shared [44, 45, 68, 69]
 58 Y d5  arity 5  loose 2  shared [46, 47, 48]
 59 Y d5  arity 5  loose 2  shared [46, 49, 51]
 60 Y d5  arity 5  loose 2  shared [47, 50, 53]
 61 Y d5  arity 5  loose 3  shared [48, 49]
 62 Y d5  arity 5  loose 3  shared [48, 50]
 63 Y d5  arity 6  loose 4  shared [49, 52]
 64 Y d5  arity 6  loose 4  shared [50, 52]
 65 Y d5  arity 5  loose 3  shared [52, 53]
 66 Y d0  arity 4  loose 2  shared [54, 55]
 67 Y d0  arity 4  loose 2  shared [54, 56]
 68 Y d0  arity 4  loose 2  shared [55, 57]
 69 Y d0  arity 4  loose 2  shared [56, 57]
```

## 5. Fixed before any growth

**Pairs.** Same-step: S2 (and S1 with its repair). Staggered: T1, T2, T3, in each of which the first member (X) asks earlier in recorded time. The earlier asker for P2 is X.

**Registered ticks.** The recorded ticks of the scarcity study at tick ages 6 and 10, restricted to ages after the stage. A tick is made when a physical birth realizes its whole ancestry by parent sets (the role map of `raw.py`, `ordinary_roles` and `realizations`).

**Ordinary growth** (gate 2): `engine.ordinary_layer`, whole parent steps, through the latest registered tick age of the start or until 100,000 cumulative births, whichever comes first (a tick age not reached is reported as not reached by the gate), checked against the archived `literal_turn` on the first three steps of every start.

**Guarded serial rule**: write the ordinary plan of the least unfinished parent step one birth at a time; the births that are roles of a registered tick go first inside a step; a step whose plan is unfunded stalls as a whole and nothing after it is written; stop at 400 births or 12 completed parent steps.

**Recompute-after-every-birth rule**: the proposals of `raw.py` (`facts`, `pool`, `apply`) with the child's fresh count read from the current demand, implemented count-level in `engine.py` and compared with the archived functions at every state of random walks (gate 1: 360 states per ring and pool policy, plus 60 per policy under not-all-equal, all equal). Pool policy `unrestricted` is primary; `joins_first` is reported separately and only for sources whose first tick the alone gate reproduces under it. A birth is **contested** when the shared donor has more enabled multi-parent proposals than loose distinctions. Every enabled multi-parent proposal through the donor is a branch at a contested birth; the contested births exist at the start and are resolved before any other birth, until none is contested. A **leaf** is a state with no contested birth. Branches are enumerated exactly with equal states merged (the numbers of choice sequences are exact); sampling by seed 2026112304 is used only if more than 20,000 distinct leaves occur. At each leaf the outcome of every registered tick is (a) `made` if a depth-first search (20,000 states) over births that are roles of the tick's ancestry finds a firing completion (run for the first registered tick of each source only, because gate 1 does not reproduce a second tick under this rule: from the original ring the search is undecided at 20,000 states, from the 63-knot stage it is exhausted at 193 states with no firing order); otherwise (b) `lost` if, after a fair continuation at the donor (every enabled multi-parent proposal through it written in ascending order, then offered unary births, until the donor holds no loose distinction), a parent that the tick requires holds no loose distinction (the certificate names the parent and the birth that spent its last one) or a larger common child excludes a required pair; otherwise `open`. For a second tick only (b) is applied.

**Reading of the predictions.** P1: no registered tick of either source has a loss certificate in any branch at s = 0, under each rule. P2: at s = 1 on T1, T2, T3 the earlier asker X has no lost tick in any branch, under each rule; the failing clause (a branch in which the later asker keeps ticking and X loses) is reported as well. P3: at s = 1 on S1 and S2 both a branch in which X loses and Y does not and a branch in which Y loses and X does not occur. Where a stalled step writes nothing, the outcome is `stalled`, not a loss certificate, and is reported as such.

