# Knots within reach, and the growing end: summary of KNOTS-WITHIN-REACH-20261125-001A-E001

Computed by an engine written from the frozen texts (SD, FD, KD, the claim and the pre-registration) by a helper that had not seen the drafter's prototype; the fold study's engine imported unchanged. Every count is a finite count of what a supplied law makes from a supplied start, read exactly in integers; nothing here is a claim about physical space. Readings taken where the texts leave a choice: `deviations.md` of the experiment folder. Raw records (the counts themselves): the `.jsonl.gz` files beside this summary.

## Run 0: controls and checks

| Control or check | Result |
| --- | --- |
| unit tests of the readings (30) | passed |
| control 1 R_400: H = 2r + 1 from every knot (400), r <= 64 | passed |
| control 1 R_400: POWER(1) from every knot | passed |
| control 1 R_400: gate j = 1 on [4, 64] | passed |
| control 2 T_12: H = 3*2^r - 2 on [0, 12] from the root | passed |
| control 2 T_12: S reads LINREC(1) root 2, 2 fitted, 10 verified | passed |
| control 2 T_12: every knot meets three but the leaves (meets one) | passed |
| control 3 W_99: H = 6r^2 + 6r + 1 from 16 knots, r <= 32 | passed |
| control 3 W_99: gate j = 2 on [4, 32] | passed |
| control 4 L8: 65 rounds reached, b(t) = C(t + 2, 2) | passed |
| control 4 L8: H from the start knot = C(r + 3, 3), POWER(3) on [0, 65] | passed |
| control 4 L8: births of degree 2 from round 1 | passed |
| control 5 comb: H = C(r + 2, 2) from the first spine knot, r <= 63 | passed |
| control 5 comb: H = r + 1 from every far leg end | passed |
| control 5 comb: the gate fails (192 knots examined) | passed |
| control 6 T_12 nae: kappa = product formula on 18429 leaf pairs from 3 sources (exact count) | passed |
| control 6 T_12 nae: |kappa| strictly smaller when hs larger; no discordant comparison | passed |
| control 7 T_12 nae: two leaf pairs at hs 4 have equal kappa; the order test counts them tied | passed |
| control 8 Ring(11,2) L0: made-knot counts as KD 8.8 on [0, min(t, l)], then n(t + r + 1) (132 of 132) | passed |
| control 8 Ring(11,2) L0: made knots | reads as registered on [0, min(t, l)] from every made knot and exactly from every start knot; the registered formula lacks the upper end r <= t, and beyond it the count is n(t + r + 1) (half of the made knots of each ring): 66 of 132 as registered |
| control 8 Ring(11,2) L0: start-knot counts as KD 8.8 (11 start knots) | passed |
| control 8 Ring(15,2) L0: made-knot counts as KD 8.8 on [0, min(t, l)], then n(t + r + 1) (240 of 240) | passed |
| control 8 Ring(15,2) L0: made knots | reads as registered on [0, min(t, l)] from every made knot and exactly from every start knot; the registered formula lacks the upper end r <= t, and beyond it the count is n(t + r + 1) (half of the made knots of each ring): 120 of 240 as registered |
| control 8 Ring(15,2) L0: start-knot counts as KD 8.8 (15 start knots) | passed |
| control 8 Ring(21,2) L0: made-knot counts as KD 8.8 on [0, min(t, l)], then n(t + r + 1) (462 of 462) | passed |
| control 8 Ring(21,2) L0: made knots | reads as registered on [0, min(t, l)] from every made knot and exactly from every start knot; the registered formula lacks the upper end r <= t, and beyond it the count is n(t + r + 1) (half of the made knots of each ring): 231 of 462 as registered |
| control 8 Ring(21,2) L0: start-knot counts as KD 8.8 (21 start knots) | passed |
| control 8 Ring(33,2) L0: made-knot counts as KD 8.8 on [0, min(t, l)], then n(t + r + 1) (1122 of 1122) | passed |
| control 8 Ring(33,2) L0: made knots | reads as registered on [0, min(t, l)] from every made knot and exactly from every start knot; the registered formula lacks the upper end r <= t, and beyond it the count is n(t + r + 1) (half of the made knots of each ring): 561 of 1122 as registered |
| control 8 Ring(33,2) L0: start-knot counts as KD 8.8 (33 start knots) | passed |
| control 8 Ring(5,2) L0: made-knot counts as KD 8.8 on [0, min(t, l)], then n(t + r + 1) (30 of 30) | passed |
| control 8 Ring(5,2) L0: made knots | reads as registered on [0, min(t, l)] from every made knot and exactly from every start knot; the registered formula lacks the upper end r <= t, and beyond it the count is n(t + r + 1) (half of the made knots of each ring): 15 of 30 as registered |
| control 8 Ring(5,2) L0: start-knot counts as KD 8.8 (5 start knots) | passed |
| control 8 Ring(7,2) L0: made-knot counts as KD 8.8 on [0, min(t, l)], then n(t + r + 1) (56 of 56) | passed |
| control 8 Ring(7,2) L0: made knots | reads as registered on [0, min(t, l)] from every made knot and exactly from every start knot; the registered formula lacks the upper end r <= t, and beyond it the count is n(t + r + 1) (half of the made knots of each ring): 28 of 56 as registered |
| control 8 Ring(7,2) L0: start-knot counts as KD 8.8 (7 start knots) | passed |
| control 8 Ring(9,2) L0: made-knot counts as KD 8.8 on [0, min(t, l)], then n(t + r + 1) (90 of 90) | passed |
| control 8 Ring(9,2) L0: made knots | reads as registered on [0, min(t, l)] from every made knot and exactly from every start knot; the registered formula lacks the upper end r <= t, and beyond it the count is n(t + r + 1) (half of the made knots of each ring): 45 of 90 as registered |
| control 8 Ring(9,2) L0: start-knot counts as KD 8.8 (9 start knots) | passed |
| check E (KD 1.6) on 136 named-start runs | passed |
| check F (KD 2.6) on 87 named-start runs (start knots and 8 made knots each) | passed |
| check I: Z, gamma Z, N(a != b) by contraction = enumeration (1930 stages, 8079 pairs) | passed |
| check N (Lemma N) by enumeration on 8079 member pairs, every loose distinction of each | passed |
| check R (KD 2.8) on 136 named-start runs | passed |
| the 64 scratch starts reproduce five_knot_order.json's marks (59 five-knot) | passed |
| graph forms of the parity test = Gaussian elimination (27763 knots, 249 failing) | passed |
| run 4b probe (Ring(5,3) under T1, 3 rounds, one numbering) | 100001 histories in 255 s, not finished (over 10^5); at least 20409 s for its 80 numberings; all cases at least 13857 s on one process; run 4b not run, Settled 3 "argued, unchecked" |

## Predictions

| Prediction | Verdict | The numbers behind it |
| --- | --- | --- |
| P1 | holds | L6, births of degree 1: census share 0.798 (labelled 0.805; without the 64: 0.799); 180 of 219 small, 199 of 250 five-knot (prefix 250); parity derived 0.690 |
| P2 | fails | starts with births of degree >= 2, LINREC root > 1 or RATIO x >= 1.25 under L1, L6, L7, L10, L11: {'L1': 9, 'L6': 9, 'L7': 9, 'L10': 0, 'L11': 13} |
| P3 | fails | L9: 19 starts with births of degree 2 (census:19, census:164, census:172, census:178, census:179, census:214); births of degree 1: census share 0.666 (labelled 0.646; without the 64: 0.669) |
| P4 | holds | L6 runs to round 100: 449; same parts at 36/40 and 96/100 with a constant gain of the largest part over each span: 449 (1.000, unweighted runs); runs with more parts at 100 than at 40: 0; gains (36-40, 96-100): {(1, 1): 361, (0, 0): 70, (2, 2): 17, (3, 3): 1} |
| P5 | holds | runs passing the gate with the scaling condition at j >= 2: 0; decided 196 of 235 (both 21, gate only 0, no gate 175, undecided 39) |
| P6 (reading A: each knot within a factor 2 on [4, n-1]) | fails | n=5: gate both j=1 [264: [8, 132], 528: [11, 264]]; (A) made [79, 79] start [5, 5]; (B) made gate False start gate False; n=7: gate both j=1 [264: [8, 132], 528: [11, 264]]; (A) made [85, 85] start [7, 7]; (B) made gate False start gate False; n=9: gate both j=1 [264: [4, 132], 528: [4, 264]]; (A) made [91, 91] start [0, 9]; (B) made gate False start gate False; n=11: gate both j=1 [264: [5, 132], 528: [5, 264]]; (A) made [97, 97] start [0, 11]; (B) made gate False start gate False; n=15: gate both j=1 [264: [7, 132], 528: [7, 264]]; (A) made [109, 109] start [0, 15]; (B) made gate False start gate False; n=21: gate both j=1 [264: [10, 132], 528: [10, 264]]; (A) made [125, 127] start [0, 21]; (B) made gate False start gate False; n=33: gate both j=1 [264: [16, 132], 528: [16, 264]]; (A) made [123, 128] start [0, 33]; (B) made gate False start gate False |
| P6 (reading B: the full gate, z >= 8a, on [4, n-1]) | fails | gate and scaling at 264/528 with j = 1 for every n: True; see the reading A row for the per-n numbers |
| P7 | fails | L6 and L7 runs of run 2 holding the gate at T: 10, j: {1: 10} (at 2T: 70, j: {2: 54, 1: 16}) |
| P9 (L6, L7 of run 2, as registered) | holds | readings of P from every member counted from: {'POWER(1)': 1700, 'UNDECIDED': 283, 'ALL WITHIN r': 169}; POWER(j >= 2): 0 |
| P9 (with L1 grown on run 2's starts, supplement added after the freeze) | holds | readings: {'POWER(1)': 2433, 'UNDECIDED': 421, 'ALL WITHIN r': 270}; POWER(j >= 2): 0 |
| P10 | holds | T1-T8 runs held by hubs: 0 (of 7552 runs; 3976 reach round 100); knot ratio 100/50: min 1.12 max 2.01; rise of the greatest holder steps 50 to 100: min 0 max 50 |
| P11 | holds | parity, rounds 1 to 10: tied pairs of loose distinctions at two knots both passing K1-K3: 434, in 221 runs; holder steps between the two knots: {2: 291, 3: 70, 4: 19, 5: 9, 7: 13, 1: 24, 6: 5, 9: 1, 10: 1, 8: 1} |
| P12 | holds | L0: 7 knots, 17 distinctions, census:157 after round 1, S = 0; L1: 7 knots, 17 distinctions, census:157 after round 1, S = 0; L6: 7 knots, 17 distinctions, census:157 after round 1, S = 0 |
| P13 | holds | L0: sum S = 434145 (member shuffle mean 1524.6, z 146.5; pair shuffle z 142.5); L1: sum S = 230767 (member shuffle mean 6872.9, z 181.3; pair shuffle z 179.6); L6: sum S = 245891 (member shuffle mean 9522.1, z 193.0; pair shuffle z 196.2) |
| P14 | holds | L3, rounds 1 to 3 of the three- and four-knot starts: 1224 comparisons in stratum (i), 0 untied in delta |
| P15 | undecided (a clause is tested on no stage) | L0: L-W fails on 1916 of 3641 stages testing it; betweenness fails on 16639 of 61925 triples (1697 of 3641 stages) [fails as predicted]; L1: L-W fails on 1933 of 5431 stages testing it; betweenness fails on 10996 of 69679 triples (1724 of 7392 stages) [fails as predicted]; L6: L-W fails on 1669 of 6260 stages testing it; betweenness fails on 7047 of 57824 triples (1212 of 7337 stages) [fails as predicted]; L3: L-W fails on 0 of 0 stages testing it; betweenness fails on 6776 of 26196 triples (971 of 6704 stages) [untested] |

## The claim's questions

1. **The verdict of H and the degree of b(t)** (per law, run 1, on the 219 small starts and the first 250 five-knot starts; every knot counted from is in run1.jsonl.gz with its counts): births by reading {'L0': {'degree 1': 217, 'degree 0': 84, 'degree 2': 19, 'ended': 145, 'degree 3': 4}, 'L1': {'degree 1': 386, 'degree 0': 54, 'degree 2': 9, 'ended': 20}, 'L6': {'degree 1': 379, 'degree 0': 70, 'degree 2': 9, 'ended': 11}, 'L7': {'degree 1': 406, 'degree 0': 54, 'degree 2': 9}, 'L8': {'ended': 195, 'degree 2': 24}, 'L9': {'degree 1': 329, 'degree 0': 106, 'degree 2': 19, 'ended': 11, 'degree 3': 4}, 'L2': {'ended': 469}, 'L3': {'LINREC root 1.41': 440, 'degree 0': 14, 'ended': 15}, 'L10': {'degree 1': 441, 'degree 0': 17, 'ended': 11}, 'L11': {'degree 1': 367, 'degree 0': 78, 'degree 2': 9, 'ended': 11, 'degree 3': 4}, 'L4': {'LINREC root 1.62': 455, 'degree 0': 14}, 'L5': {'RATIO': 417, 'degree 0': 14, 'ended': 38}}. H by class and reading: summary.json, run1.H_verdicts.
2. **Run 2, gate and scaling:** both 21 (all with j = 1: the seven bare rings at 264 and 528, three-knot-larger, Ring(5, 2), Ring(7, 2), Ring(9, 2) under L0, L6, L7 at 66 and 132, census starts 1110 and 3151 under L6; every one with constant births); gate only 0; no gate 175; undecided 39 (least kept range below 32, or T past the knot bound or guard). No run gives the same power of 2 or more from every knot examined on a range that lengthens with the rounds.
3. **Laws with a taking rule (T1 to T10):** {'not held': 4232, 'ended': 4264}; held by hubs in no run, under no step.
4. **Parity, Lambda_t:** yes; 1602 stages have a rule on fewer distinctions than their loose ones; the smallest: ('census:60', 'T2', 'takes:1', 1, 2, 1, 4, 6).
5. **Not-all-equal, per law:** L0: against delta, explained by loose counts census:17 r1 (7 knots, S = 0); not loose counts census:157 r1 (7 knots, S = 0); not loose or shared-place counts census:480 r1 (10 knots, S = 15); against ws (not loose counts) census:157 r1 (7 knots, S = 0); against hs (not loose counts) census:157 r1 (7 knots, S = 0); L-W fails on 1916 of 3641 stages testing it (smallest census:157); betweenness fails on 16639 of 61925 triples; L1: against delta, explained by loose counts census:133 r1 (6 knots, S = -1); not loose counts census:157 r1 (7 knots, S = 0); not loose or shared-place counts census:1409 r1 (9 knots, S = -1); against ws (not loose counts) census:157 r1 (7 knots, S = 0); against hs (not loose counts) census:157 r1 (7 knots, S = 0); L-W fails on 1933 of 5431 stages testing it (smallest census:157); betweenness fails on 10996 of 69679 triples; L3: against delta, explained by loose counts none; not loose counts none; not loose or shared-place counts none; against ws (not loose counts) none; against hs (not loose counts) none; L-W fails on 0 of 0 stages testing it (smallest None); betweenness fails on 6776 of 26196 triples; L6: against delta, explained by loose counts census:17 r1 (7 knots, S = 0); not loose counts census:157 r1 (7 knots, S = 0); not loose or shared-place counts census:480 r1 (10 knots, S = 15); against ws (not loose counts) census:157 r1 (7 knots, S = 0); against hs (not loose counts) census:157 r1 (7 knots, S = 0); L-W fails on 1669 of 6260 stages testing it (smallest census:157); betweenness fails on 7047 of 57824 triples; L7: against delta, explained by loose counts census:17 r1 (7 knots, S = 0); not loose counts census:157 r1 (7 knots, S = 0); not loose or shared-place counts census:480 r1 (10 knots, S = 15); against ws (not loose counts) census:157 r1 (7 knots, S = 0); against hs (not loose counts) census:157 r1 (7 knots, S = 0); L-W fails on 2441 of 5728 stages testing it (smallest census:157); betweenness fails on 6883 of 50355 triples.

## Run 2: the gate

Answers over the 235 registered runs: {'no gate': 175, 'undecided': 39, 'both': 21}. Checks over run 2: E failed on 0 runs, R on 0, F on 0 knots (of 414 readings).

Does any run give the same power of 2 or more from every knot examined on a range that lengthens with the rounds? **No** under the registered thresholds (0 runs). Under the swapped thresholds (z >= 4a, C/c <= 3, 1.5): {'undecided': 68, 'both j=2': 111, 'both j=1': 37, 'no gate': 16, 'gate only': 3}.
Gates that hold at 2T but not at T (answer "no gate" by the registered rule): 67.

| Start | Law | Answer | Gate at T | Gate at 2T | P at T (labels) |
| --- | --- | --- | --- | --- | --- |
| Ring(5,3) | L0 (T=66) | undecided | not reached | not reached | {} |
| Ring(5,3) | L6 (T=66) | no gate | no gate (best j=2: 127 of 133) | j=2 on [6, 66], 133 of 133; spread 2.38 (start 1.09, made 2.29) | {'POWER(1)': 8} |
| Ring(5,3) | L7 (T=66) | no gate | no gate (best j=2: 101 of 133) | not reached | {'POWER(1)': 6, 'UNDECIDED': 2} |
| Ring(7,3) | L0 (T=66) | undecided | not reached | not reached | {} |
| Ring(7,3) | L6 (T=66) | no gate | no gate (best j=2: 125 of 135) | not reached | {'POWER(1)': 7, 'UNDECIDED': 1} |
| Ring(7,3) | L7 (T=66) | no gate | no gate (best j=2: 79 of 135) | not reached | {'UNDECIDED': 2, 'POWER(1)': 6} |
| D2(5,3) | L0 (T=66) | undecided | not reached | not reached | {} |
| D2(5,3) | L6 (T=66) | no gate | no gate (best j=2: 129 of 138) | j=2 on [7, 66], 138 of 138; spread 2.23 (start 1.45, made 2.18) | {'POWER(1)': 8} |
| D2(5,3) | L7 (T=66) | no gate | no gate (best j=2: 117 of 138) | not reached | {'POWER(1)': 7, 'UNDECIDED': 1} |
| two-knot | L0 (T=66) | no gate | no gate (best j=2: 89 of 130) | no gate (best j=2: 105 of 130) | {'POWER(1)': 7, 'UNDECIDED': 1} |
| two-knot | L6 (T=66) | no gate | no gate (best j=2: 87 of 130) | no gate (best j=2: 105 of 130) | {'POWER(1)': 7, 'UNDECIDED': 1} |
| two-knot | L7 (T=66) | no gate | no gate (best j=2: 80 of 130) | no gate (best j=2: 100 of 130) | {'POWER(1)': 6, 'UNDECIDED': 2} |
| three-knot | L0 (T=66) | no gate | no gate (best j=2: 61 of 131) | no gate (best j=2: 76 of 131) | {'POWER(1)': 8} |
| three-knot | L6 (T=66) | no gate | no gate (best j=2: 65 of 131) | no gate (best j=2: 75 of 131) | {'UNDECIDED': 1, 'POWER(1)': 7} |
| three-knot | L7 (T=66) | no gate | no gate (best j=2: 62 of 131) | no gate (best j=2: 77 of 131) | {'POWER(1)': 8} |
| three-knot-larger | L0 (T=66) | both | j=1 on [4, 33], 82 of 82; spread 2.32 (start 1.29, made 2.19) | j=1 on [4, 66], 82 of 82; spread 2.34 (start 1.29, made 1.97) | {'ALL WITHIN r': 5} |
| three-knot-larger | L6 (T=66) | both | j=1 on [4, 33], 82 of 82; spread 2.32 (start 1.29, made 2.07) | j=1 on [4, 66], 82 of 82; spread 2.34 (start 1.29, made 2.09) | {'ALL WITHIN r': 5} |
| three-knot-larger | L7 (T=66) | both | j=1 on [4, 33], 82 of 82; spread 2.32 (start 1.29, made 2.19) | j=1 on [4, 66], 82 of 82; spread 2.34 (start 1.29, made 1.96) | {'ALL WITHIN r': 5} |
| generator7 | L0 (T=66) | undecided | not reached | not reached | {} |
| generator7 | L6 (T=66) | no gate | no gate (best j=2: 115 of 135) | no gate (best j=2: 130 of 135) | {'POWER(1)': 8} |
| generator7 | L7 (T=66) | no gate | no gate (best j=2: 89 of 135) | not reached | {'POWER(1)': 6, 'UNDECIDED': 2} |
| one-knot | L0 (T=66) | no gate | no gate (best j=2: 58 of 129) | no gate (best j=2: 73 of 129) | {'POWER(1)': 7, 'UNDECIDED': 1} |
| one-knot | L6 (T=66) | no gate | no gate (best j=2: 62 of 129) | no gate (best j=2: 80 of 129) | {'POWER(1)': 5, 'UNDECIDED': 3} |
| one-knot | L7 (T=66) | no gate | no gate (best j=2: 59 of 129) | no gate (best j=2: 77 of 129) | {'POWER(1)': 7, 'UNDECIDED': 1} |
| two-share | L0 (T=66) | no gate | no gate (best j=2: 80 of 130) | no gate (best j=2: 101 of 130) | {'POWER(1)': 7, 'UNDECIDED': 1} |
| two-share | L6 (T=66) | no gate | no gate (best j=2: 82 of 130) | no gate (best j=2: 103 of 130) | {'POWER(1)': 7, 'UNDECIDED': 1} |
| two-share | L7 (T=66) | no gate | no gate (best j=2: 86 of 130) | no gate (best j=2: 106 of 130) | {'POWER(1)': 7, 'UNDECIDED': 1} |
| Ring(5,2) | L0 (T=66) | both | j=1 on [4, 33], 84 of 84; spread 2.14 (start 1.21, made 2.07) | j=1 on [6, 66], 84 of 84; spread 2.13 (start 1.15, made 2.10) | {'ALL WITHIN r': 5} |
| Ring(5,2) | L6 (T=66) | both | j=1 on [4, 33], 84 of 84; spread 2.14 (start 1.21, made 2.07) | j=1 on [4, 66], 84 of 84; spread 2.17 (start 1.23, made 2.10) | {'ALL WITHIN r': 5} |
| Ring(5,2) | L7 (T=66) | both | j=1 on [4, 33], 84 of 84; spread 2.14 (start 1.21, made 2.07) | j=1 on [6, 66], 84 of 84; spread 2.13 (start 1.15, made 2.10) | {'ALL WITHIN r': 5} |
| Ring(9,2) | L0 (T=66) | both | j=1 on [4, 33], 100 of 100; spread 2.05 (start 1.11, made 1.99) | j=1 on [4, 66], 100 of 100; spread 2.08 (start 1.12, made 2.05) | {'ALL WITHIN r': 8} |
| Ring(9,2) | L6 (T=66) | both | j=1 on [4, 33], 100 of 100; spread 2.05 (start 1.11, made 1.99) | j=1 on [4, 66], 100 of 100; spread 2.08 (start 1.12, made 2.05) | {'ALL WITHIN r': 8} |
| Ring(9,2) | L7 (T=66) | both | j=1 on [4, 33], 100 of 100; spread 2.05 (start 1.11, made 1.99) | j=1 on [4, 66], 100 of 100; spread 2.08 (start 1.12, made 2.02) | {'ALL WITHIN r': 8} |
| Ring(15,2) | L0 (T=66) | no gate | no gate (best j=1: 27 of 124) | j=1 on [7, 66], 124 of 124; spread 2.04 (start 1.06, made 1.98) | {'UNDECIDED': 8} |
| Ring(15,2) | L6 (T=66) | no gate | no gate (best j=1: 37 of 124) | j=1 on [7, 66], 124 of 124; spread 2.04 (start 1.06, made 2.01) | {'UNDECIDED': 8} |
| Ring(15,2) | L7 (T=66) | no gate | no gate (best j=1: 32 of 124) | j=1 on [7, 66], 124 of 124; spread 2.04 (start 1.06, made 2.01) | {'UNDECIDED': 8} |
| Ring(21,2) | L0 (T=66) | no gate | no gate (best j=2: 21 of 148) | no gate (best j=1: 45 of 148) | {'POWER(1)': 8} |
| Ring(21,2) | L6 (T=66) | no gate | no gate (best j=2: 21 of 148) | no gate (best j=1: 46 of 148) | {'POWER(1)': 8} |
| Ring(21,2) | L7 (T=66) | no gate | no gate (best j=2: 21 of 148) | no gate (best j=1: 50 of 148) | {'POWER(1)': 8} |
| Ring(33,2) | L0 (T=66) | no gate | no gate (best j=2: 97 of 161) | no gate (best j=1: 37 of 161) | {'POWER(1)': 8} |
| Ring(33,2) | L6 (T=66) | no gate | no gate (best j=2: 92 of 161) | no gate (best j=1: 39 of 161) | {'POWER(1)': 8} |
| Ring(33,2) | L7 (T=66) | no gate | no gate (best j=2: 97 of 161) | no gate (best j=1: 37 of 161) | {'POWER(1)': 8} |
| Ring(9,3) | L0 (T=66) | undecided | not reached | not reached | {} |
| Ring(9,3) | L6 (T=66) | no gate | no gate (best j=2: 105 of 137) | not reached | {'POWER(1)': 7, 'UNDECIDED': 1} |
| Ring(9,3) | L7 (T=66) | no gate | no gate (best j=2: 76 of 137) | not reached | {'POWER(1)': 8} |
| Ring(7,2) | L0 (T=66) | both | j=1 on [4, 33], 92 of 92; spread 2.08 (start 1.14, made 2.02) | j=1 on [4, 66], 92 of 92; spread 2.11 (start 1.16, made 2.08) | {'ALL WITHIN r': 7} |
| Ring(7,2) | L6 (T=66) | both | j=1 on [4, 33], 92 of 92; spread 2.08 (start 1.14, made 2.02) | j=1 on [4, 66], 92 of 92; spread 2.11 (start 1.16, made 2.08) | {'ALL WITHIN r': 7} |
| Ring(7,2) | L7 (T=66) | both | j=1 on [4, 33], 92 of 92; spread 2.08 (start 1.14, made 2.02) | j=1 on [4, 66], 92 of 92; spread 2.11 (start 1.16, made 2.08) | {'ALL WITHIN r': 7} |
| Ring(11,2) | L0 (T=66) | no gate | no gate (best j=1: 39 of 108) | j=1 on [5, 66], 108 of 108; spread 2.06 (start 1.09, made 2.03) | {'ALL WITHIN r': 8} |
| Ring(11,2) | L6 (T=66) | no gate | no gate (best j=1: 42 of 108) | j=1 on [5, 66], 108 of 108; spread 2.06 (start 1.09, made 2.03) | {'ALL WITHIN r': 8} |
| Ring(11,2) | L7 (T=66) | no gate | no gate (best j=1: 42 of 108) | j=1 on [5, 66], 108 of 108; spread 2.06 (start 1.09, made 2.03) | {'ALL WITHIN r': 8} |
| Ring(5,2) | L0 (T=264) | both | j=1 on [8, 132], 84 of 84; spread 2.11 (start 1.12, made 2.09) | j=1 on [11, 264], 84 of 84; spread 2.08 (start 1.09, made 2.08) | {'ALL WITHIN r': 5} |
| Ring(7,2) | L0 (T=264) | both | j=1 on [8, 132], 92 of 92; spread 2.11 (start 1.12, made 2.09) | j=1 on [11, 264], 92 of 92; spread 2.08 (start 1.09, made 2.08) | {'ALL WITHIN r': 7} |
| Ring(9,2) | L0 (T=264) | both | j=1 on [4, 132], 100 of 100; spread 2.10 (start 1.13, made 2.06) | j=1 on [4, 264], 100 of 100; spread 2.10 (start 1.13, made 2.08) | {'ALL WITHIN r': 8} |
| Ring(11,2) | L0 (T=264) | both | j=1 on [5, 132], 108 of 108; spread 2.08 (start 1.10, made 2.06) | j=1 on [5, 264], 108 of 108; spread 2.08 (start 1.10, made 2.07) | {'ALL WITHIN r': 8} |
| Ring(15,2) | L0 (T=264) | both | j=1 on [7, 132], 124 of 124; spread 2.05 (start 1.07, made 2.01) | j=1 on [7, 264], 124 of 124; spread 2.06 (start 1.07, made 2.02) | {'UNDECIDED': 8} |
| Ring(21,2) | L0 (T=264) | both | j=1 on [10, 132], 148 of 148; spread 2.03 (start 1.04, made 1.99) | j=1 on [10, 264], 148 of 148; spread 2.04 (start 1.05, made 2.00) | {'POWER(1)': 8} |
| Ring(33,2) | L0 (T=264) | both | j=1 on [16, 132], 161 of 161; spread 2.02 (start 1.02, made 2.00) | j=1 on [16, 264], 161 of 161; spread 2.02 (start 1.03, made 2.02) | {'POWER(1)': 8} |
| census:2640 | L0 (T=66) | undecided | least kept range 1 | least kept range 1 | {'ALL WITHIN r': 3} |
| census:2640 | L6 (T=66) | no gate | no gate (best j=2: 52 of 133) | no gate (best j=2: 81 of 133) | {'UNDECIDED': 2, 'POWER(1)': 6} |
| census:2640 | L7 (T=66) | no gate | no gate (best j=2: 92 of 133) | j=2 on [7, 66], 133 of 133; spread 2.24 (start 1.32, made 2.24) | {'POWER(1)': 7, 'UNDECIDED': 1} |
| census:465 | L0 (T=66) | no gate | no gate (best j=2: 61 of 133) | no gate (best j=2: 75 of 133) | {'POWER(1)': 7, 'UNDECIDED': 1} |
| census:465 | L6 (T=66) | no gate | no gate (best j=2: 65 of 133) | no gate (best j=2: 81 of 133) | {'POWER(1)': 7, 'UNDECIDED': 1} |
| census:465 | L7 (T=66) | no gate | no gate (best j=2: 64 of 133) | no gate (best j=2: 84 of 133) | {'POWER(1)': 7, 'UNDECIDED': 1} |
| census:1194 | L0 (T=66) | no gate | no gate (best j=2: 45 of 133) | no gate (best j=2: 76 of 133) | {'POWER(1)': 6, 'UNDECIDED': 2} |
| census:1194 | L6 (T=66) | no gate | no gate (best j=2: 128 of 133) | j=2 on [7, 66], 133 of 133; spread 2.24 (start 1.08, made 2.24) | {'POWER(1)': 7, 'UNDECIDED': 1} |
| census:1194 | L7 (T=66) | no gate | no gate (best j=2: 127 of 133) | j=2 on [6, 66], 133 of 133; spread 2.30 (start 1.18, made 2.26) | {'POWER(1)': 8} |
| census:2006 | L0 (T=66) | undecided | least kept range 1 | least kept range 1 | {'ALL WITHIN r': 3} |
| census:2006 | L6 (T=66) | no gate | no gate (best j=2: 66 of 133) | no gate (best j=2: 81 of 133) | {'POWER(1)': 8} |
| census:2006 | L7 (T=66) | no gate | no gate (best j=2: 96 of 133) | j=2 on [7, 66], 133 of 133; spread 2.24 (start 1.09, made 2.24) | {'UNDECIDED': 2, 'POWER(1)': 6} |
| census:2694 | L0 (T=66) | undecided | not reached | not reached | {} |
| census:2694 | L6 (T=66) | no gate | no gate (best j=2: 126 of 133) | j=2 on [6, 66], 133 of 133; spread 2.29 (start 1.18, made 2.29) | {'POWER(1)': 8} |
| census:2694 | L7 (T=66) | no gate | no gate (best j=2: 123 of 133) | j=2 on [7, 66], 133 of 133; spread 2.38 (start 1.21, made 2.24) | {'POWER(1)': 7, 'UNDECIDED': 1} |
| census:2522 | L0 (T=66) | undecided | least kept range 2 | least kept range 2 | {'ALL WITHIN r': 4} |
| census:2522 | L6 (T=66) | no gate | no gate (best j=2: 96 of 133) | no gate (best j=2: 117 of 133) | {'POWER(1)': 7, 'UNDECIDED': 1} |
| census:2522 | L7 (T=66) | no gate | no gate (best j=2: 127 of 133) | j=2 on [6, 66], 133 of 133; spread 2.29 (start 1.31, made 2.29) | {'POWER(1)': 7, 'UNDECIDED': 1} |
| census:3122 | L0 (T=66) | no gate | no gate (best j=2: 52 of 133) | no gate (best j=2: 84 of 133) | {'UNDECIDED': 1, 'POWER(1)': 7} |
| census:3122 | L6 (T=66) | no gate | no gate (best j=2: 53 of 133) | no gate (best j=2: 88 of 133) | {'POWER(1)': 8} |
| census:3122 | L7 (T=66) | no gate | no gate (best j=2: 57 of 133) | no gate (best j=2: 83 of 133) | {'POWER(1)': 8} |
| census:663 | L0 (T=66) | undecided | least kept range 2 | least kept range 2 | {'ALL WITHIN r': 5} |
| census:663 | L6 (T=66) | no gate | no gate (best j=2: 93 of 133) | j=2 on [7, 66], 133 of 133; spread 2.24 (start 1.24, made 2.24) | {'POWER(1)': 7, 'UNDECIDED': 1} |
| census:663 | L7 (T=66) | no gate | no gate (best j=2: 118 of 133) | not reached | {'POWER(1)': 7, 'UNDECIDED': 1} |
| census:2408 | L0 (T=66) | no gate | no gate (best j=2: 45 of 133) | no gate (best j=2: 75 of 133) | {'POWER(1)': 8} |
| census:2408 | L6 (T=66) | no gate | no gate (best j=2: 122 of 133) | j=2 on [6, 66], 133 of 133; spread 2.29 (start 1.29, made 2.29) | {'POWER(1)': 7, 'UNDECIDED': 1} |
| census:2408 | L7 (T=66) | no gate | no gate (best j=2: 115 of 133) | j=2 on [6, 66], 133 of 133; spread 2.35 (start 1.26, made 2.29) | {'UNDECIDED': 1, 'POWER(1)': 7} |
| census:2700 | L0 (T=66) | undecided | least kept range 1 | least kept range 1 | {'ALL WITHIN r': 3} |
| census:2700 | L6 (T=66) | no gate | no gate (best j=2: 89 of 133) | no gate (best j=2: 110 of 133) | {'POWER(1)': 8} |
| census:2700 | L7 (T=66) | no gate | no gate (best j=2: 122 of 133) | j=2 on [7, 66], 133 of 133; spread 2.24 (start 1.21, made 2.24) | {'UNDECIDED': 2, 'POWER(1)': 6} |
| census:2258 | L0 (T=66) | no gate | no gate (best j=1: 52 of 133) | j=1 on [6, 66], 133 of 133; spread 3.58 (start 1.78, made 2.24) | {'ALL WITHIN r': 8} |
| census:2258 | L6 (T=66) | no gate | no gate (best j=2: 128 of 133) | j=2 on [6, 66], 133 of 133; spread 2.37 (start 1.22, made 2.29) | {'POWER(1)': 5, 'UNDECIDED': 3} |
| census:2258 | L7 (T=66) | no gate | no gate (best j=2: 120 of 133) | j=2 on [7, 66], 133 of 133; spread 2.55 (start 1.13, made 2.24) | {'POWER(1)': 8} |
| census:3264 | L0 (T=66) | no gate | no gate (best j=2: 64 of 133) | no gate (best j=2: 69 of 133) | {'POWER(1)': 8} |
| census:3264 | L6 (T=66) | no gate | no gate (best j=2: 128 of 133) | j=2 on [6, 66], 133 of 133; spread 2.50 (start 1.28, made 2.29) | {'POWER(1)': 7, 'UNDECIDED': 1} |
| census:3264 | L7 (T=66) | no gate | no gate (best j=2: 125 of 133) | j=2 on [6, 66], 133 of 133; spread 2.78 (start 1.19, made 2.29) | {'POWER(1)': 7, 'UNDECIDED': 1} |
| census:2084 | L0 (T=66) | no gate | no gate (best j=2: 63 of 133) | no gate (best j=2: 80 of 133) | {'POWER(1)': 6, 'UNDECIDED': 2} |
| census:2084 | L6 (T=66) | no gate | no gate (best j=2: 66 of 133) | no gate (best j=2: 85 of 133) | {'POWER(1)': 8} |
| census:2084 | L7 (T=66) | no gate | no gate (best j=2: 64 of 133) | no gate (best j=2: 81 of 133) | {'POWER(1)': 6, 'UNDECIDED': 2} |
| census:1964 | L0 (T=66) | undecided | not reached | not reached | {} |
| census:1964 | L6 (T=66) | no gate | no gate (best j=2: 127 of 133) | j=2 on [6, 66], 133 of 133; spread 2.64 (start 1.13, made 2.29) | {'POWER(1)': 8} |
| census:1964 | L7 (T=66) | no gate | no gate (best j=2: 122 of 133) | not reached | {'POWER(1)': 6, 'UNDECIDED': 2} |
| census:1850 | L0 (T=66) | undecided | least kept range 1 | least kept range 1 | {'ALL WITHIN r': 4} |
| census:1850 | L6 (T=66) | no gate | no gate (best j=2: 119 of 133) | j=2 on [6, 66], 133 of 133; spread 2.29 (start 1.29, made 2.29) | {'POWER(1)': 8} |
| census:1850 | L7 (T=66) | no gate | no gate (best j=2: 121 of 133) | not reached | {'POWER(1)': 6, 'UNDECIDED': 2} |
| census:2339 | L0 (T=66) | no gate | no gate (best j=2: 63 of 133) | no gate (best j=2: 80 of 133) | {'UNDECIDED': 3, 'POWER(1)': 5} |
| census:2339 | L6 (T=66) | no gate | no gate (best j=2: 63 of 133) | no gate (best j=2: 79 of 133) | {'POWER(1)': 7, 'UNDECIDED': 1} |
| census:2339 | L7 (T=66) | no gate | no gate (best j=2: 63 of 133) | no gate (best j=2: 79 of 133) | {'POWER(1)': 8} |
| census:2695 | L0 (T=66) | no gate | no gate (best j=2: 130 of 133) | not reached | {'UNDECIDED': 8} |
| census:2695 | L6 (T=66) | no gate | no gate (best j=2: 122 of 133) | j=2 on [6, 66], 133 of 133; spread 2.29 (start 1.19, made 2.29) | {'UNDECIDED': 1, 'POWER(1)': 7} |
| census:2695 | L7 (T=66) | no gate | no gate (best j=2: 127 of 133) | j=2 on [6, 66], 133 of 133; spread 2.51 (start 1.21, made 2.34) | {'POWER(1)': 7, 'UNDECIDED': 1} |
| census:3087 | L0 (T=66) | no gate | no gate (best j=1: 116 of 120) | j=1 on [5, 66], 120 of 120; spread 2.78 (start 1.35, made 2.78) | {'ALL WITHIN r': 8} |
| census:3087 | L6 (T=66) | no gate | no gate (best j=2: 118 of 133) | j=2 on [6, 66], 133 of 133; spread 2.23 (start 1.27, made 2.23) | {'UNDECIDED': 1, 'POWER(1)': 7} |
| census:3087 | L7 (T=66) | no gate | no gate (best j=2: 122 of 133) | j=2 on [7, 66], 133 of 133; spread 2.24 (start 1.18, made 2.24) | {'POWER(1)': 6, 'UNDECIDED': 2} |
| census:3066 | L0 (T=66) | undecided | least kept range 1 | least kept range 1 | {'ALL WITHIN r': 4} |
| census:3066 | L6 (T=66) | undecided | least kept range 1 | least kept range 1 | {} |
| census:3066 | L7 (T=66) | no gate | no gate (best j=2: 128 of 133) | j=2 on [7, 66], 133 of 133; spread 2.24 (start 1.04, made 2.24) | {'POWER(1)': 8} |
| census:925 | L0 (T=66) | undecided | least kept range 1 | least kept range 1 | {'ALL WITHIN r': 5} |
| census:925 | L6 (T=66) | no gate | no gate (best j=2: 111 of 133) | j=2 on [7, 66], 133 of 133; spread 2.24 (start 1.46, made 2.24) | {'POWER(1)': 8} |
| census:925 | L7 (T=66) | no gate | no gate (best j=2: 121 of 133) | j=2 on [7, 66], 133 of 133; spread 2.38 (start 1.19, made 2.24) | {'POWER(1)': 7, 'UNDECIDED': 1} |
| census:3241 | L0 (T=66) | no gate | no gate (best j=1: 42 of 43) | j=1 on [7, 66], 75 of 75; spread 2.17 (start 1.33, made 2.13) | {'ALL WITHIN r': 2} |
| census:3241 | L6 (T=66) | no gate | no gate (best j=1: 42 of 43) | j=1 on [7, 66], 75 of 75; spread 2.17 (start 1.33, made 2.13) | {'ALL WITHIN r': 2} |
| census:3241 | L7 (T=66) | no gate | no gate (best j=1: 42 of 43) | j=1 on [7, 66], 75 of 75; spread 2.17 (start 1.33, made 2.13) | {'ALL WITHIN r': 2} |
| census:1186 | L0 (T=66) | no gate | no gate (best j=1: 125 of 133) | j=1 on [6, 66], 133 of 133; spread 3.40 (start 1.70, made 2.42) | {'ALL WITHIN r': 8} |
| census:1186 | L6 (T=66) | no gate | no gate (best j=2: 120 of 133) | j=2 on [6, 66], 133 of 133; spread 2.37 (start 1.21, made 2.29) | {'POWER(1)': 8} |
| census:1186 | L7 (T=66) | no gate | no gate (best j=2: 126 of 133) | j=2 on [6, 66], 133 of 133; spread 2.53 (start 1.16, made 2.19) | {'POWER(1)': 5, 'UNDECIDED': 3} |
| census:2576 | L0 (T=66) | no gate | no gate (best j=1: 55 of 133) | j=1 on [6, 66], 133 of 133; spread 3.74 (start 1.86, made 2.48) | {'ALL WITHIN r': 8} |
| census:2576 | L6 (T=66) | no gate | no gate (best j=2: 130 of 133) | not reached | {'UNDECIDED': 6, 'POWER(1)': 2} |
| census:2576 | L7 (T=66) | no gate | no gate (best j=2: 123 of 133) | not reached | {'POWER(1)': 5, 'UNDECIDED': 3} |
| census:1884 | L0 (T=66) | no gate | no gate (best j=2: 56 of 133) | no gate (best j=2: 84 of 133) | {'POWER(1)': 8} |
| census:1884 | L6 (T=66) | no gate | no gate (best j=2: 53 of 133) | no gate (best j=2: 84 of 133) | {'POWER(1)': 8} |
| census:1884 | L7 (T=66) | no gate | no gate (best j=2: 50 of 133) | no gate (best j=2: 81 of 133) | {'POWER(1)': 8} |
| census:677 | L0 (T=66) | no gate | no gate (best j=2: 43 of 133) | no gate (best j=2: 70 of 133) | {'POWER(1)': 6, 'UNDECIDED': 2} |
| census:677 | L6 (T=66) | no gate | no gate (best j=2: 57 of 133) | no gate (best j=2: 64 of 133) | {'POWER(1)': 6, 'ALL WITHIN r': 2} |
| census:677 | L7 (T=66) | no gate | no gate (best j=2: 66 of 133) | no gate (best j=2: 112 of 133) | {'POWER(1)': 6, 'ALL WITHIN r': 1, 'UNDECIDED': 1} |
| census:1143 | L0 (T=66) | undecided | least kept range 2 | least kept range 2 | {'ALL WITHIN r': 5} |
| census:1143 | L6 (T=66) | no gate | no gate (best j=2: 85 of 133) | no gate (best j=2: 112 of 133) | {'ALL WITHIN r': 2, 'POWER(1)': 5, 'UNDECIDED': 1} |
| census:1143 | L7 (T=66) | no gate | no gate (best j=2: 115 of 133) | no gate (best j=2: 127 of 133) | {'POWER(1)': 7, 'UNDECIDED': 1} |
| census:234 | L0 (T=66) | undecided | least kept range 1 | least kept range 1 | {'ALL WITHIN r': 5} |
| census:234 | L6 (T=66) | no gate | no gate (best j=2: 103 of 133) | j=2 on [7, 66], 133 of 133; spread 2.24 (start 1.31, made 2.24) | {'POWER(1)': 8} |
| census:234 | L7 (T=66) | no gate | no gate (best j=2: 122 of 133) | not reached | {'POWER(1)': 8} |
| census:1400 | L0 (T=66) | no gate | no gate (best j=2: 57 of 132) | no gate (best j=2: 64 of 133) | {'UNDECIDED': 2, 'POWER(1)': 6} |
| census:1400 | L6 (T=66) | no gate | no gate (best j=2: 123 of 133) | j=2 on [6, 66], 133 of 133; spread 2.96 (start 1.24, made 2.25) | {'POWER(1)': 8} |
| census:1400 | L7 (T=66) | no gate | no gate (best j=2: 125 of 133) | not reached | {'POWER(1)': 8} |
| census:1213 | L0 (T=66) | undecided | least kept range 2 | least kept range 2 | {'ALL WITHIN r': 4} |
| census:1213 | L6 (T=66) | no gate | no gate (best j=2: 118 of 133) | j=2 on [6, 66], 133 of 133; spread 2.24 (start 1.25, made 2.24) | {'POWER(1)': 8} |
| census:1213 | L7 (T=66) | no gate | no gate (best j=2: 120 of 133) | j=2 on [6, 66], 133 of 133; spread 2.48 (start 1.22, made 2.29) | {'POWER(1)': 6, 'UNDECIDED': 2} |
| census:886 | L0 (T=66) | undecided | least kept range 1 | least kept range 1 | {'ALL WITHIN r': 3} |
| census:886 | L6 (T=66) | no gate | no gate (best j=2: 67 of 133) | no gate (best j=2: 81 of 133) | {'POWER(1)': 8} |
| census:886 | L7 (T=66) | no gate | no gate (best j=2: 86 of 133) | no gate (best j=2: 105 of 133) | {'UNDECIDED': 3, 'POWER(1)': 5} |
| census:3067 | L0 (T=66) | no gate | no gate (best j=2: 64 of 133) | no gate (best j=2: 82 of 133) | {'UNDECIDED': 3, 'POWER(1)': 5} |
| census:3067 | L6 (T=66) | no gate | no gate (best j=2: 62 of 133) | no gate (best j=2: 82 of 133) | {'POWER(1)': 8} |
| census:3067 | L7 (T=66) | no gate | no gate (best j=2: 67 of 133) | no gate (best j=2: 76 of 133) | {'POWER(1)': 7, 'UNDECIDED': 1} |
| census:2022 | L0 (T=66) | undecided | least kept range 1 | least kept range 1 | {'ALL WITHIN r': 3} |
| census:2022 | L6 (T=66) | no gate | no gate (best j=2: 56 of 133) | no gate (best j=2: 77 of 133) | {'UNDECIDED': 2, 'POWER(1)': 6} |
| census:2022 | L7 (T=66) | no gate | no gate (best j=2: 101 of 133) | j=2 on [7, 66], 133 of 133; spread 2.46 (start 1.35, made 2.46) | {'POWER(1)': 6, 'UNDECIDED': 2} |
| census:3051 | L0 (T=66) | no gate | no gate (best j=2: 54 of 133) | no gate (best j=2: 82 of 133) | {'UNDECIDED': 1, 'POWER(1)': 7} |
| census:3051 | L6 (T=66) | no gate | no gate (best j=2: 56 of 133) | no gate (best j=2: 83 of 133) | {'POWER(1)': 7, 'UNDECIDED': 1} |
| census:3051 | L7 (T=66) | no gate | no gate (best j=2: 55 of 133) | no gate (best j=2: 85 of 133) | {'POWER(1)': 8} |
| census:872 | L0 (T=66) | undecided | least kept range 2 | least kept range 2 | {'ALL WITHIN r': 5} |
| census:872 | L6 (T=66) | no gate | no gate (best j=2: 130 of 133) | j=2 on [6, 66], 133 of 133; spread 3.82 (start 1.33, made 3.82) | {'UNDECIDED': 3, 'POWER(1)': 5} |
| census:872 | L7 (T=66) | no gate | no gate (best j=2: 125 of 133) | not reached | {'POWER(1)': 7, 'UNDECIDED': 1} |
| census:804 | L0 (T=66) | undecided | least kept range 2 | least kept range 2 | {'ALL WITHIN r': 5} |
| census:804 | L6 (T=66) | no gate | no gate (best j=2: 66 of 133) | no gate (best j=2: 95 of 133) | {'POWER(1)': 8} |
| census:804 | L7 (T=66) | no gate | no gate (best j=2: 96 of 133) | j=2 on [7, 66], 133 of 133; spread 2.24 (start 1.43, made 2.24) | {'POWER(1)': 7, 'UNDECIDED': 1} |
| census:3249 | L0 (T=66) | no gate | no gate (best j=2: 44 of 133) | no gate (best j=2: 87 of 133) | {'POWER(1)': 7, 'UNDECIDED': 1} |
| census:3249 | L6 (T=66) | no gate | no gate (best j=2: 89 of 133) | no gate (best j=2: 113 of 133) | {'POWER(1)': 7, 'UNDECIDED': 1} |
| census:3249 | L7 (T=66) | no gate | no gate (best j=2: 103 of 133) | j=2 on [6, 66], 133 of 133; spread 2.29 (start 1.33, made 2.29) | {'POWER(1)': 6, 'UNDECIDED': 2} |
| census:3229 | L0 (T=66) | undecided | least kept range 1 | least kept range 1 | {'ALL WITHIN r': 4} |
| census:3229 | L6 (T=66) | no gate | no gate (best j=2: 50 of 133) | no gate (best j=2: 85 of 133) | {'POWER(1)': 8} |
| census:3229 | L7 (T=66) | no gate | no gate (best j=2: 125 of 133) | j=2 on [7, 66], 133 of 133; spread 2.18 (start 1.21, made 2.18) | {'POWER(1)': 8} |
| census:1614 | L0 (T=66) | undecided | least kept range 2 | least kept range 2 | {'ALL WITHIN r': 5} |
| census:1614 | L6 (T=66) | no gate | no gate (best j=2: 83 of 133) | no gate (best j=2: 120 of 133) | {'POWER(1)': 7, 'ALL WITHIN r': 1} |
| census:1614 | L7 (T=66) | no gate | no gate (best j=2: 113 of 133) | no gate (best j=2: 131 of 133) | {'POWER(1)': 6, 'UNDECIDED': 2} |
| census:1610 | L0 (T=66) | no gate | no gate (best j=2: 52 of 133) | no gate (best j=2: 84 of 133) | {'POWER(1)': 8} |
| census:1610 | L6 (T=66) | no gate | no gate (best j=2: 50 of 133) | no gate (best j=2: 87 of 133) | {'POWER(1)': 7, 'UNDECIDED': 1} |
| census:1610 | L7 (T=66) | no gate | no gate (best j=2: 51 of 133) | no gate (best j=2: 82 of 133) | {'POWER(1)': 8} |
| census:2236 | L0 (T=66) | undecided | not reached | not reached | {} |
| census:2236 | L6 (T=66) | no gate | no gate (best j=2: 125 of 133) | j=2 on [7, 66], 133 of 133; spread 2.57 (start 1.11, made 2.26) | {'POWER(1)': 8} |
| census:2236 | L7 (T=66) | no gate | no gate (best j=2: 120 of 133) | not reached | {'UNDECIDED': 2, 'POWER(1)': 6} |
| census:3254 | L0 (T=66) | no gate | no gate (best j=2: 123 of 133) | no gate (best j=2: 113 of 133) | {'UNDECIDED': 8} |
| census:3254 | L6 (T=66) | no gate | no gate (best j=2: 112 of 133) | j=2 on [6, 66], 133 of 133; spread 2.29 (start 1.18, made 2.29) | {'POWER(1)': 7, 'UNDECIDED': 1} |
| census:3254 | L7 (T=66) | no gate | no gate (best j=2: 118 of 133) | j=2 on [7, 66], 133 of 133; spread 2.24 (start 1.10, made 2.24) | {'POWER(1)': 6, 'UNDECIDED': 2} |
| census:668 | L0 (T=66) | no gate | no gate (best j=2: 76 of 133) | no gate (best j=2: 101 of 133) | {'POWER(1)': 8} |
| census:668 | L6 (T=66) | no gate | no gate (best j=2: 82 of 133) | no gate (best j=2: 93 of 133) | {'POWER(1)': 8} |
| census:668 | L7 (T=66) | no gate | no gate (best j=2: 79 of 133) | no gate (best j=2: 99 of 133) | {'POWER(1)': 8} |
| census:353 | L0 (T=66) | undecided | least kept range 2 | least kept range 2 | {'ALL WITHIN r': 5} |
| census:353 | L6 (T=66) | no gate | no gate (best j=2: 79 of 133) | no gate (best j=2: 105 of 133) | {'POWER(1)': 6, 'UNDECIDED': 2} |
| census:353 | L7 (T=66) | no gate | no gate (best j=2: 94 of 133) | no gate (best j=2: 126 of 133) | {'POWER(1)': 7, 'UNDECIDED': 1} |
| census:572 | L0 (T=66) | undecided | least kept range 2 | least kept range 2 | {'ALL WITHIN r': 4} |
| census:572 | L6 (T=66) | no gate | no gate (best j=2: 52 of 133) | no gate (best j=2: 70 of 133) | {'UNDECIDED': 1, 'POWER(1)': 7} |
| census:572 | L7 (T=66) | no gate | no gate (best j=2: 79 of 133) | no gate (best j=2: 110 of 133) | {'POWER(1)': 6, 'UNDECIDED': 2} |
| census:1541 | L0 (T=66) | undecided | least kept range 2 | least kept range 2 | {'ALL WITHIN r': 5} |
| census:1541 | L6 (T=66) | no gate | no gate (best j=2: 109 of 133) | no gate (best j=2: 123 of 133) | {'POWER(1)': 4, 'UNDECIDED': 4} |
| census:1541 | L7 (T=66) | no gate | no gate (best j=2: 124 of 133) | j=2 on [6, 66], 133 of 133; spread 3.89 (start 1.22, made 3.89) | {'POWER(1)': 5, 'UNDECIDED': 3} |
| census:1110 | L0 (T=66) | undecided | least kept range 2 | least kept range 2 | {'ALL WITHIN r': 4} |
| census:1110 | L6 (T=66) | both | j=1 on [4, 33], 84 of 84; spread 2.32 (start 1.41, made 1.98) | j=1 on [4, 66], 84 of 84; spread 2.34 (start 1.41, made 1.98) | {'ALL WITHIN r': 5} |
| census:1110 | L7 (T=66) | no gate | no gate (best j=2: 71 of 133) | no gate (best j=2: 103 of 133) | {'POWER(1)': 5, 'UNDECIDED': 2, 'ALL WITHIN r': 1} |
| census:1082 | L0 (T=66) | undecided | least kept range 2 | least kept range 2 | {'ALL WITHIN r': 4} |
| census:1082 | L6 (T=66) | no gate | no gate (best j=2: 82 of 133) | no gate (best j=2: 114 of 133) | {'POWER(1)': 7, 'UNDECIDED': 1} |
| census:1082 | L7 (T=66) | no gate | no gate (best j=2: 124 of 133) | j=2 on [7, 66], 133 of 133; spread 2.24 (start 1.25, made 2.24) | {'POWER(1)': 8} |
| census:2351 | L0 (T=66) | undecided | least kept range 2 | least kept range 2 | {'ALL WITHIN r': 4} |
| census:2351 | L6 (T=66) | no gate | no gate (best j=2: 76 of 133) | no gate (best j=2: 105 of 133) | {'POWER(1)': 8} |
| census:2351 | L7 (T=66) | no gate | no gate (best j=2: 121 of 133) | j=2 on [7, 66], 133 of 133; spread 2.24 (start 1.27, made 2.24) | {'POWER(1)': 8} |
| census:2537 | L0 (T=66) | undecided | least kept range 2 | least kept range 2 | {'ALL WITHIN r': 5} |
| census:2537 | L6 (T=66) | no gate | no gate (best j=2: 125 of 133) | j=2 on [6, 66], 133 of 133; spread 2.35 (start 1.20, made 2.29) | {'POWER(1)': 7, 'UNDECIDED': 1} |
| census:2537 | L7 (T=66) | no gate | no gate (best j=2: 120 of 133) | not reached | {'UNDECIDED': 3, 'POWER(1)': 5} |
| census:3151 | L0 (T=66) | undecided | least kept range 1 | least kept range 1 | {'ALL WITHIN r': 3} |
| census:3151 | L6 (T=66) | both | j=1 on [4, 33], 84 of 84; spread 2.20 (start 1.33, made 1.96) | j=1 on [4, 66], 84 of 84; spread 2.21 (start 1.33, made 1.98) | {'ALL WITHIN r': 5} |
| census:3151 | L7 (T=66) | no gate | no gate (best j=2: 57 of 133) | no gate (best j=2: 81 of 133) | {'POWER(1)': 6, 'UNDECIDED': 2} |
| census:19 | L0 (T=66) | no gate | no gate (best j=2: 27 of 131) | not reached | {'UNDECIDED': 8} |
| census:19 | L6 (T=66) | no gate | no gate (best j=2: 32 of 131) | not reached | {'UNDECIDED': 8} |
| census:19 | L7 (T=66) | no gate | no gate (best j=2: 30 of 131) | not reached | {'UNDECIDED': 8} |
| census:164 | L0 (T=66) | no gate | no gate (best j=2: 31 of 132) | not reached | {'UNDECIDED': 8} |
| census:164 | L6 (T=66) | no gate | no gate (best j=2: 31 of 132) | not reached | {'UNDECIDED': 8} |
| census:164 | L7 (T=66) | no gate | no gate (best j=2: 35 of 132) | not reached | {'UNDECIDED': 8} |
| census:172 | L0 (T=66) | no gate | no gate (best j=2: 37 of 132) | not reached | {'UNDECIDED': 8} |
| census:172 | L6 (T=66) | no gate | no gate (best j=2: 33 of 132) | not reached | {'UNDECIDED': 8} |
| census:172 | L7 (T=66) | no gate | no gate (best j=2: 41 of 132) | not reached | {'UNDECIDED': 8} |
| census:178 | L0 (T=66) | undecided | not reached | not reached | {} |
| census:178 | L6 (T=66) | no gate | no gate (best j=2: 123 of 132) | j=2 on [7, 66], 132 of 132; spread 2.24 (start 1.07, made 2.24) | {'POWER(1)': 6, 'UNDECIDED': 2} |
| census:178 | L7 (T=66) | no gate | no gate (best j=2: 117 of 132) | j=2 on [7, 66], 132 of 132; spread 2.38 (start 1.11, made 2.24) | {'UNDECIDED': 3, 'POWER(1)': 5} |
| census:179 | L0 (T=66) | undecided | not reached | not reached | {} |
| census:179 | L6 (T=66) | no gate | no gate (best j=2: 123 of 132) | j=2 on [7, 66], 132 of 132; spread 2.24 (start 1.08, made 2.24) | {'POWER(1)': 7, 'UNDECIDED': 1} |
| census:179 | L7 (T=66) | no gate | no gate (best j=2: 123 of 132) | j=2 on [7, 66], 132 of 132; spread 2.38 (start 1.10, made 2.24) | {'POWER(1)': 7, 'UNDECIDED': 1} |
| census:214 | L0 (T=66) | no gate | no gate (best j=2: 35 of 132) | not reached | {'UNDECIDED': 8} |
| census:214 | L6 (T=66) | no gate | no gate (best j=2: 36 of 132) | not reached | {'UNDECIDED': 8} |
| census:214 | L7 (T=66) | no gate | no gate (best j=2: 35 of 132) | not reached | {'UNDECIDED': 8} |
| census:219 | L0 (T=66) | undecided | not reached | not reached | {} |
| census:219 | L6 (T=66) | no gate | no gate (best j=2: 121 of 132) | j=2 on [6, 66], 132 of 132; spread 2.29 (start 1.07, made 2.29) | {'POWER(1)': 7, 'UNDECIDED': 1} |
| census:219 | L7 (T=66) | no gate | no gate (best j=2: 126 of 132) | j=2 on [7, 66], 132 of 132; spread 2.38 (start 1.06, made 2.29) | {'POWER(1)': 7, 'UNDECIDED': 1} |
| census:177 | L0 (T=66) | undecided | not reached | not reached | {} |
| census:177 | L6 (T=66) | no gate | no gate (best j=2: 121 of 132) | j=2 on [7, 66], 132 of 132; spread 2.24 (start 1.08, made 2.24) | {'POWER(1)': 8} |
| census:177 | L7 (T=66) | no gate | no gate (best j=2: 116 of 132) | j=2 on [6, 66], 132 of 132; spread 2.37 (start 1.16, made 2.29) | {'POWER(1)': 8} |
| census:218 | L0 (T=66) | undecided | not reached | not reached | {} |
| census:218 | L6 (T=66) | no gate | no gate (best j=2: 124 of 132) | j=2 on [6, 66], 132 of 132; spread 2.23 (start 1.02, made 2.23) | {'POWER(1)': 7, 'UNDECIDED': 1} |
| census:218 | L7 (T=66) | no gate | no gate (best j=2: 121 of 132) | j=2 on [7, 66], 132 of 132; spread 2.36 (start 1.10, made 2.24) | {'POWER(1)': 8} |

## Run 2: the roster count and the swaps

P beside the gate (members counted from, at T and 2T; L6, L7 and the L1 supplement): {'POWER(1)': 1700, 'UNDECIDED': 283, 'ALL WITHIN r': 169}; with L1: {'POWER(1)': 2433, 'UNDECIDED': 421, 'ALL WITHIN r': 270}.
Swaps of run 2: {"swap HOLD L3": {"undecided": 17}, "swap HOLD L6": {"undecided": 4, "no gate": 9, "both": 4}, "swap bounds L7": {"undecided": 17}, "swap bounds L6": {"undecided": 17}, "swap bounds L0": {"undecided": 17}, "gate under thresholds (at T)": {"holds j=2": 143, "holds j=1": 37, "no gate": 42}, "gate under parent steps (at T)": {"no gate": 206, "holds j=1": 16}, "gate under retired not stepped (at T)": {"no gate": 48, "holds j=1": 2}}.

## Run 1: the screen and the start-by-start table

Cut to a prefix fixed before the run (deviations 29): the 219 three- and four-knot starts under all 12 laws and the first 250 five-knot starts of the registered order under 11 laws; the other 750 five-knot starts are not run. Shares use KD 7.5's estimators with 3,157/250.

| Law | Births per round, by reading (starts, unweighted) | Census shares (degree 0, 1, 2, ended) |
| --- | --- | --- |
| L0 | {'degree 1': 217, 'degree 0': 84, 'degree 2': 19, 'ended': 145, 'degree 3': 4} | 0.183, 0.364, 0.047, 0.398 |
| L1 | {'degree 1': 386, 'degree 0': 54, 'degree 2': 9, 'ended': 20} | 0.109, 0.810, 0.020, 0.061 |
| L2 | {'ended': 469} | 0.000, 0.000, 0.000, 1.000 |
| L3 | {'LINREC root 1.41': 440, 'degree 0': 14, 'ended': 15} | 0.025, 0.000, 0.000, 0.049 |
| L4 | {'LINREC root 1.62': 455, 'degree 0': 14} | 0.025, 0.000, 0.000, 0.000 |
| L5 | {'RATIO': 417, 'degree 0': 14, 'ended': 38} | 0.025, 0.000, 0.000, 0.115 |
| L6 | {'degree 1': 379, 'degree 0': 70, 'degree 2': 9, 'ended': 11} | 0.148, 0.798, 0.020, 0.034 |
| L7 | {'degree 1': 406, 'degree 0': 54, 'degree 2': 9} | 0.109, 0.871, 0.020, 0.000 |
| L8 | {'ended': 195, 'degree 2': 24} | 0.000, 0.000, 0.110, 0.890 |
| L9 | {'degree 1': 329, 'degree 0': 106, 'degree 2': 19, 'ended': 11, 'degree 3': 4} | 0.245, 0.666, 0.047, 0.034 |
| L10 | {'degree 1': 441, 'degree 0': 17, 'ended': 11} | 0.029, 0.937, 0.000, 0.034 |
| L11 | {'degree 1': 367, 'degree 0': 78, 'degree 2': 9, 'ended': 11, 'degree 3': 4} | 0.171, 0.767, 0.020, 0.034 |

Under parity (derived, Settled 4; the 32 starts failing the knot test at round 0 left out): {'L0': {'degree 1': 107, 'ended': 250, 'degree 0': 84, 'degree 2': 19, 'degree 3': 4}, 'L1': {'degree 1': 317, 'ended': 84, 'degree 0': 54, 'degree 2': 9}, 'L6': {'degree 1': 310, 'ended': 75, 'degree 0': 70, 'degree 2': 9}, 'L7': {'degree 1': 337, 'ended': 64, 'degree 0': 54, 'degree 2': 9}, 'L8': {'ended': 199, 'degree 2': 17}, 'L9': {'degree 1': 219, 'degree 0': 106, 'ended': 116, 'degree 2': 19, 'degree 3': 4}, 'L2': {'ended': 464}, 'L3': {'LINREC root 1.41': 423, 'degree 0': 14, 'ended': 27}, 'L10': {'degree 1': 396, 'ended': 51, 'degree 0': 17}, 'L11': {'degree 1': 277, 'ended': 96, 'degree 0': 78, 'degree 2': 9, 'degree 3': 4}, 'L4': {'LINREC root 1.62': 438, 'degree 0': 14, 'ended': 12}, 'L5': {'RATIO': 400, 'degree 0': 14, 'ended': 50}}.

The start-by-start table (births under L0 -> under the law; L9, L10, L11 separate the cap from the treatment):

- L6: {'degree 0 -> degree 0': 54, 'degree 0 -> degree 1': 30, 'degree 1 -> degree 1': 217, 'degree 2 -> degree 1': 10, 'degree 2 -> degree 2': 9, 'degree 3 -> degree 1': 4, 'ended -> degree 0': 16, 'ended -> degree 1': 118, 'ended -> ended': 11}
- L7: {'degree 0 -> degree 0': 54, 'degree 0 -> degree 1': 30, 'degree 1 -> degree 1': 217, 'degree 2 -> degree 1': 10, 'degree 2 -> degree 2': 9, 'degree 3 -> degree 1': 4, 'ended -> degree 1': 145}
- L1: {'degree 0 -> degree 0': 54, 'degree 0 -> degree 1': 30, 'degree 1 -> degree 1': 217, 'degree 2 -> degree 1': 10, 'degree 2 -> degree 2': 9, 'degree 3 -> degree 1': 4, 'ended -> degree 1': 125, 'ended -> ended': 20}
- L9: {'degree 0 -> degree 0': 84, 'degree 1 -> degree 1': 217, 'degree 2 -> degree 2': 19, 'degree 3 -> degree 3': 4, 'ended -> degree 0': 22, 'ended -> degree 1': 112, 'ended -> ended': 11}
- L10: {'degree 0 -> degree 0': 17, 'degree 0 -> degree 1': 67, 'degree 1 -> degree 1': 217, 'degree 2 -> degree 1': 19, 'degree 3 -> degree 1': 4, 'ended -> degree 1': 134, 'ended -> ended': 11}
- L11: {'degree 0 -> degree 0': 59, 'degree 0 -> degree 1': 25, 'degree 1 -> degree 1': 217, 'degree 2 -> degree 1': 10, 'degree 2 -> degree 2': 9, 'degree 3 -> degree 3': 4, 'ended -> degree 0': 19, 'ended -> degree 1': 115, 'ended -> ended': 11}

The screen (the same j from every start knot and 16 made knots at the last round, no scaling): {'L0': {'no j': 210, 'holds j=1': 84, 'holds j=2': 14, 'undecided (range)': 161}, 'L1': {'no j': 177, 'holds j=2': 204, 'holds j=1': 54, 'undecided (range)': 34}, 'L6': {'no j': 260, 'holds j=2': 128, 'holds j=1': 70, 'undecided (range)': 11}, 'L7': {'no j': 196, 'holds j=2': 219, 'holds j=1': 54}, 'L8': {'undecided (range)': 201, 'no j': 18}, 'L9': {'no j': 320, 'holds j=1': 105, 'holds j=2': 17, 'undecided (range)': 27}, 'L2': {'undecided (range)': 469}, 'L3': {'undecided (range)': 455, 'holds j=1': 14}, 'L10': {'no j': 223, 'holds j=2': 218, 'holds j=1': 17, 'undecided (range)': 11}, 'L11': {'no j': 295, 'holds j=1': 78, 'holds j=2': 81, 'undecided (range)': 15}, 'L4': {'undecided (range)': 455, 'holds j=1': 14}, 'L5': {'undecided (range)': 455, 'holds j=1': 14}}.
Runs whose screen gives the same power 1 from every knot examined with births not constant: 0.
H from the knots counted from, by class and reading: see summary.json (run1.H_verdicts).
Check E failed on 0 runs; parent steps change H on 5291 runs (only through the start's own meetings, Lemma E).

## Run 4: laws with a taking rule

Claim 3 by law and knot law (runs): {'T1 parity': {'not held': 352, 'ended': 120}, 'T3 parity': {'not held': 371, 'ended': 101}, 'T4 parity': {'ended': 364, 'not held': 108}, 'T5 parity': {'ended': 304, 'not held': 168}, 'T2 parity': {'ended': 451, 'not held': 21}, 'T6 parity': {'ended': 471, 'not held': 1}, 'T7 parity': {'ended': 141, 'not held': 331}, 'T9 parity': {'ended': 158, 'not held': 78}, 'T10 parity': {'ended': 197, 'not held': 39}, 'T8 parity': {'ended': 472}, 'T3 nae': {'not held': 468, 'ended': 4}, 'T5 nae': {'ended': 274, 'not held': 198}, 'T6 nae': {'ended': 388, 'not held': 84}, 'T1 nae': {'not held': 436, 'ended': 36}, 'T7 nae': {'not held': 368, 'ended': 104}, 'T2 nae': {'not held': 234, 'ended': 238}, 'T4 nae': {'not held': 468, 'ended': 4}, 'T9 nae': {'not held': 89, 'ended': 147}, 'T10 nae': {'not held': 50, 'ended': 186}, 'T8 nae': {'not held': 368, 'ended': 104}}.
Held by hubs: 0 runs. Claim 4 (parity): stages by rank of Lambda_t {'0': 23280, '1': 6199, '2': 112, '3': 6, '4': 1, '5': 1}; stages with a rule on fewer distinctions than all loose ones: 1602; the smallest: [('census:60', 'T2', 'takes:1', 1, 2, 1, 4, 6), ('census:60', 'T6', 'takes:2', 1, 2, 1, 4, 6)] (start, law, seed, round, least number of distinctions in one rule, rank, loose distinctions, knots).
Check P: {'stages': 29599, 'small_stages': 5649, 'bad': 0}. Knot test (every knot after round 25 and 100 later knots): {'parity': {'tested': 327600, 'fails': 204, 'untested': 0, 'disagree': 0}, 'nae': {'tested': 451393, 'fails': 70, 'untested': 0, 'disagree': 0}}; failing knots are listed in summary.json (run4.knot_test_fails): joins of many parents under CARRY among them.
Holder-number distribution at round 100 (all runs reaching it): {'1': 42647, '2': 987187, '3': 190283, '4': 83638, '5': 37434, '6': 17139, '7': 8092, '8': 3930, '9': 1824, '10': 933, '11': 465, '12': 202, '13': 121, '14': 40, '15': 18, '16': 12, '17': 6, '18': 4, '19': 4, '102': 46, '103': 28, '104': 28, '105': 36, '106': 28, '107': 16, '298': 2, '299': 16, '301': 44, '302': 18}.
Run 4c (OLDEST and NEWEST under KD 7.3's numberings; T1-T8 with 10 numberings since no run is held by hubs, T9 and T10 with all 4n): 13072 runs in 612 groups; groups whose claim-3 verdict changes with the numbering: {'T9': 19, 'T10': 3, 'T1-T8 OLDEST': 33, 'T1-T8 NEWEST': 52} (numberings changing it: {'T9': 1193, 'T10': 177, 'T1-T8 OLDEST': 140, 'T1-T8 NEWEST': 186}); held by hubs under any numbering: 0.

## Run 5: the growing end (not-all-equal)

| Law | Stages computed / not run (cap) | Strata (i, ii, iii, iv, v, vi) | |kappa| vs delta (i-1; i-2; i-3: conc, disc, tied) | |gamma| vs delta (i-1) | Smallest stage: not loose counts; not loose or shared-place counts |
| --- | --- | --- | --- | --- | --- |
| L0 | 4678 / 740 | 74327, 10472, 0, 0, 0, 0 | [350955, 307331, 451452]; [113036, 3410, 216783]; [85601, 1680, 197353] | [546221, 112076, 451441] | census:157 r1 (7 knots, 17 distinctions, S = 0); census:480 r1 (10 knots, 24 distinctions, S = 15) |
| L1 | 8896 / 982 | 72652, 172669, 1777, 50404, 0, 22850 | [236312, 21501, 215783]; [135131, 6666, 133291]; [66802, 2095, 90108] | [244281, 13514, 215801] | census:157 r1 (7 knots, 17 distinctions, S = 0); census:1409 r1 (9 knots, 23 distinctions, S = -1) |
| L3 | 9864 / 190 | 19843, 172149, 210, 51634, 0, 0 | [0, 0, 23819]; [0, 0, 22461]; [0, 0, 22433] | [0, 0, 23819] | none; none |
| L6 | 9510 / 574 | 75873, 105724, 0, 19854, 0, 0 | [249410, 16605, 185727]; [149738, 3468, 117497]; [65521, 430, 83646] | [255952, 10061, 185729] | census:157 r1 (7 knots, 17 distinctions, S = 0); census:480 r1 (10 knots, 24 distinctions, S = 15) |
| L7 | 8694 / 1653 | 76300, 216531, 0, 19824, 0, 0 | [226267, 18885, 226038]; [132420, 7588, 146681]; [60872, 4258, 94643] | [229828, 15322, 226040] | census:157 r1 (7 knots, 17 distinctions, S = 0); census:480 r1 (10 knots, 24 distinctions, S = 15) |

- L0: against ws [[350955, 307331, 451452], [113036, 3410, 216783], [85601, 1680, 197353]], against hs [[374096, 304699, 430943], [132868, 2554, 197807], [104657, 1396, 178581]] (|kappa|, i-1/i-2/i-3); rho vs delta [[77033, 581258, 451447], [876, 115571, 216782], [247, 87034, 197353]]; S: {'gamma': {'S': 434145, 'member shuffle mean': 1524.6, 'z member': 146.5, 'z pair': 142.5, 'stages': 4087, 'exact': 3401}, 'kappa': {'S': 43624, 'member shuffle mean': 2718.7, 'z member': 9.4, 'z pair': 14.3, 'stages': 4087, 'exact': 3401}}; L-W {'tests': 3641, 'fails': 1916, 'fails_strict': 1915}; betweenness {'triples': 61925, 'failing': 16639, 'stages_tested': 3641, 'stages_failing': 1697}; history weighting on 224 stages of at most 20 distinctions: discordant under the stage weighting {'i-1': 20, 'i-2': 17, 'i-3': 0}, under the history weighting {'i-1': 23, 'i-2': 17, 'i-3': 0}, history only {'i-1': 3, 'i-2': 0, 'i-3': 0}, stage only {'i-1': 0, 'i-2': 0, 'i-3': 0}; checks on those stages {'stages': 540, 'Z_bad': 0, 'I_bad': 0, 'N_bad': 0, 'pairs': 1129}; knot test {'tested': 36057, 'fails': 0, 'untested': 0, 'direct_compared': 35996, 'disagree': 0}; sign of kappa at each ws {'1': {'-': 37280, '+': 434, '0': 4}, '2': {'-': 13892, '+': 14850, '0': 1}, '3': {'-': 2779, '+': 4145}, '4': {'-': 255, '+': 381}, '5': {'-': 21, '+': 11}}; shares of stages with a discordance (census, labelled) {'kappa|delta|i-2': (0.069, 0.0822), 'kappa|delta|i-1': (0.4012, 0.4422), 'kappa|delta|i-3': (0.0357, 0.0458)}.
- L1: against ws [[234133, 19948, 219515], [134547, 6552, 133989], [66720, 2072, 90213]], against hs [[236050, 19631, 217915], [134533, 6461, 134094], [66564, 2044, 90397]] (|kappa|, i-1/i-2/i-3); rho vs delta [[14752, 243074, 215770], [5862, 135939, 133287], [1855, 67045, 90105]]; S: {'gamma': {'S': 230767, 'member shuffle mean': 6872.9, 'z member': 181.3, 'z pair': 179.6, 'stages': 8282, 'exact': 7206}, 'kappa': {'S': 214811, 'member shuffle mean': 10313.3, 'z member': 171.7, 'z pair': 167.2, 'stages': 8282, 'exact': 7206}}; L-W {'tests': 5431, 'fails': 1933, 'fails_strict': 1932}; betweenness {'triples': 69679, 'failing': 10996, 'stages_tested': 7392, 'stages_failing': 1724}; history weighting on 359 stages of at most 20 distinctions: discordant under the stage weighting {'i-1': 65, 'i-2': 17, 'i-3': 0}, under the history weighting {'i-1': 68, 'i-2': 17, 'i-3': 0}, history only {'i-1': 3, 'i-2': 0, 'i-3': 0}, stage only {'i-1': 0, 'i-2': 0, 'i-3': 0}; checks on those stages {'stages': 723, 'Z_bad': 0, 'I_bad': 0, 'N_bad': 0, 'pairs': 2953}; knot test {'tested': 78746, 'fails': 0, 'untested': 0, 'direct_compared': 78746, 'disagree': 0}; sign of kappa at each ws {'1': {'-': 47570, '+': 517, '0': 20}, '2': {'-': 17860, '+': 1464, '0': 1}, '3': {'-': 3306, '+': 723}, '4': {'-': 311, '+': 238}, '5': {'-': 23, '+': 13}}; shares of stages with a discordance (census, labelled) {'kappa|delta|i-2': (0.0734, 0.0844), 'kappa|delta|i-1': (0.1751, 0.2011), 'kappa|delta|i-3': (0.0453, 0.0493)}.
- L3: against ws [[0, 0, 23819], [0, 0, 22461], [0, 0, 22433]], against hs [[0, 0, 23819], [0, 0, 22461], [0, 0, 22433]] (|kappa|, i-1/i-2/i-3); rho vs delta [[0, 0, 23819], [0, 0, 22461], [0, 0, 22433]]; S: {'gamma': {'S': 0, 'member shuffle mean': 0.0, 'z member': 0, 'z pair': 0, 'stages': 9028, 'exact': 8927}, 'kappa': {'S': 0, 'member shuffle mean': 0.0, 'z member': 0, 'z pair': 0, 'stages': 9028, 'exact': 8927}}; L-W {}; betweenness {'triples': 26196, 'failing': 6776, 'stages_tested': 6704, 'stages_failing': 971}; history weighting on 210 stages of at most 20 distinctions: discordant under the stage weighting {'i-1': 0, 'i-2': 0, 'i-3': 0}, under the history weighting {'i-1': 0, 'i-2': 0, 'i-3': 0}, history only {'i-1': 0, 'i-2': 0, 'i-3': 0}, stage only {'i-1': 0, 'i-2': 0, 'i-3': 0}; checks on those stages {'stages': 999, 'Z_bad': 0, 'I_bad': 0, 'N_bad': 0, 'pairs': 2989}; knot test {'tested': 83447, 'fails': 0, 'untested': 0, 'direct_compared': 83447, 'disagree': 0}; sign of kappa at each ws {'1': {'-': 17889, '0': 2}}; shares of stages with a discordance (census, labelled) {}.
- L6: against ws [[249240, 16580, 185922], [149684, 3440, 117579], [65517, 422, 83658]], against hs [[249785, 15510, 186447], [149973, 2862, 117868], [65736, 304, 83557]] (|kappa|, i-1/i-2/i-3); rho vs delta [[8678, 257341, 185723], [2027, 151180, 117496], [52, 65899, 83646]]; S: {'gamma': {'S': 245891, 'member shuffle mean': 9522.1, 'z member': 193.0, 'z pair': 196.2, 'stages': 8568, 'exact': 8260}, 'kappa': {'S': 232805, 'member shuffle mean': 13723.4, 'z member': 185.1, 'z pair': 185.7, 'stages': 8568, 'exact': 8260}}; L-W {'tests': 6260, 'fails': 1669, 'fails_strict': 1668}; betweenness {'triples': 57824, 'failing': 7047, 'stages_tested': 7337, 'stages_failing': 1212}; history weighting on 417 stages of at most 20 distinctions: discordant under the stage weighting {'i-1': 20, 'i-2': 17, 'i-3': 0}, under the history weighting {'i-1': 23, 'i-2': 17, 'i-3': 0}, history only {'i-1': 3, 'i-2': 0, 'i-3': 0}, stage only {'i-1': 0, 'i-2': 0, 'i-3': 0}; checks on those stages {'stages': 847, 'Z_bad': 0, 'I_bad': 0, 'N_bad': 0, 'pairs': 2013}; knot test {'tested': 76489, 'fails': 0, 'untested': 0, 'direct_compared': 76489, 'disagree': 0}; sign of kappa at each ws {'1': {'-': 47116, '+': 12, '0': 2}, '2': {'-': 19693, '+': 1553, '0': 2}, '3': {'-': 5039, '+': 925}, '4': {'-': 499, '+': 391}, '5': {'-': 29, '+': 53}, '6': {'+': 4}}; shares of stages with a discordance (census, labelled) {'kappa|delta|i-2': (0.113, 0.1335), 'kappa|delta|i-1': (0.0807, 0.0831), 'kappa|delta|i-3': (0.0128, 0.0164)}.
- L7: against ws [[226095, 18860, 226235], [132366, 7560, 146763], [60868, 4250, 94655]], against hs [[226684, 17912, 226594], [132683, 7046, 146960], [61099, 4144, 94530]] (|kappa|, i-1/i-2/i-3); rho vs delta [[11494, 233662, 226034], [6329, 133680, 146680], [3925, 61205, 94643]]; S: {'gamma': {'S': 214506, 'member shuffle mean': 13586.5, 'z member': 176.4, 'z pair': 176.8, 'stages': 7992, 'exact': 7581}, 'kappa': {'S': 207382, 'member shuffle mean': 23423.5, 'z member': 170.1, 'z pair': 170.9, 'stages': 7992, 'exact': 7581}}; L-W {'tests': 5728, 'fails': 2441, 'fails_strict': 2440}; betweenness {'triples': 50355, 'failing': 6883, 'stages_tested': 6804, 'stages_failing': 1188}; history weighting on 242 stages of at most 20 distinctions: discordant under the stage weighting {'i-1': 20, 'i-2': 17, 'i-3': 0}, under the history weighting {'i-1': 23, 'i-2': 17, 'i-3': 0}, history only {'i-1': 3, 'i-2': 0, 'i-3': 0}, stage only {'i-1': 0, 'i-2': 0, 'i-3': 0}; checks on those stages {'stages': 616, 'Z_bad': 0, 'I_bad': 0, 'N_bad': 0, 'pairs': 1577}; knot test {'tested': 87073, 'fails': 0, 'untested': 0, 'direct_compared': 87073, 'disagree': 0}; sign of kappa at each ws {'1': {'-': 51945, '+': 12, '0': 2}, '2': {'-': 17350, '+': 1553, '0': 2}, '3': {'-': 3267, '+': 905}, '4': {'-': 349, '+': 332}, '5': {'-': 25, '+': 32}, '6': {'+': 1}}; shares of stages with a discordance (census, labelled) {'kappa|delta|i-1': (0.0743, 0.0765), 'kappa|delta|i-2': (0.1358, 0.1598), 'kappa|delta|i-3': (0.0844, 0.0873)}.

Swaps on the three- and four-knot starts:
- swap horizon 10, L6: stages {'computed': 762, 'not run (stage cap)': 106}; strata {'i': 5731, 'ii': 6296, 'iii': 0, 'iv': 851, 'v': 0, 'vi': 0}; |kappa| vs delta {'i-1': [19460, 969, 12684], 'i-2': [13176, 147, 8371], 'i-3': [5710, 3, 5617]}; discordant stages by level {'i-1': 150, 'i-2': 66, 'i-3': 2}.
- swap horizon 10, L7: stages {'computed': 722, 'not run (stage cap)': 154}; strata {'i': 5620, 'ii': 9866, 'iii': 0, 'iv': 851, 'v': 0, 'vi': 0}; |kappa| vs delta {'i-1': [17679, 1181, 14260], 'i-2': [10982, 353, 8989], 'i-3': [5001, 183, 5661]}; discordant stages by level {'i-1': 185, 'i-2': 110, 'i-3': 31}.
- swap horizon 10, L0: stages {'computed': 587, 'not run (stage cap)': 121}; strata {'i': 6438, 'ii': 2247, 'iii': 0, 'iv': 0, 'v': 0, 'vi': 0}; |kappa| vs delta {'i-1': [28246, 14181, 28786], 'i-2': [11891, 155, 15545], 'i-3': [8318, 28, 13476]}; discordant stages by level {'i-1': 204, 'i-2': 35, 'i-3': 5}.
- swap horizon 10, L1: stages {'computed': 729, 'not run (stage cap)': 133}; strata {'i': 5632, 'ii': 9806, 'iii': 20, 'iv': 1386, 'v': 0, 'vi': 259}; |kappa| vs delta {'i-1': [19913, 1421, 14585], 'i-2': [12575, 341, 9650], 'i-3': [5517, 129, 5990]}; discordant stages by level {'i-1': 187, 'i-2': 73, 'i-3': 23}.
- swap horizon 10, L3: stages {'computed': 804, 'not run (stage cap)': 64}; strata {'i': 1485, 'ii': 15303, 'iii': 0, 'iv': 3587, 'v': 0, 'vi': 0}; |kappa| vs delta {'i-1': [0, 0, 1742], 'i-2': [0, 0, 1639], 'i-3': [0, 0, 1637]}; discordant stages by level {}.
- swap cap 40/60, L6: stages {'computed': 58, 'not run (stage cap)': 48}; strata {'i': 1275, 'ii': 2129, 'iii': 0, 'iv': 70, 'v': 0, 'vi': 0}; |kappa| vs delta {'i-1': [12742, 1213, 5656], 'i-2': [8464, 63, 4029], 'i-3': [4315, 0, 2502]}; discordant stages by level {'i-1': 38, 'i-2': 22}.
- swap cap 40/60, L7: stages {'not run (stage cap)': 96, 'computed': 58}; strata {'i': 1229, 'ii': 2708, 'iii': 0, 'iv': 0, 'v': 0, 'vi': 0}; |kappa| vs delta {'i-1': [11923, 1203, 5650], 'i-2': [7278, 74, 3661], 'i-3': [3823, 0, 2356]}; discordant stages by level {'i-1': 36, 'i-2': 25}.
- swap cap 40/60, L0: stages {'computed': 49, 'not run (stage cap)': 72}; strata {'i': 1586, 'ii': 445, 'iii': 0, 'iv': 0, 'v': 0, 'vi': 0}; |kappa| vs delta {'i-1': [27150, 5420, 17856], 'i-2': [7817, 55, 6504], 'i-3': [5109, 0, 4544]}; discordant stages by level {'i-1': 29, 'i-2': 3}.
- swap cap 40/60, L1: stages {'not run (stage cap)': 85, 'computed': 48}; strata {'i': 1181, 'ii': 2501, 'iii': 0, 'iv': 35, 'v': 0, 'vi': 0}; |kappa| vs delta {'i-1': [12742, 1378, 6401], 'i-2': [7527, 102, 4084], 'i-3': [3881, 18, 2344]}; discordant stages by level {'i-1': 28, 'i-2': 16, 'i-3': 5}.
- swap cap 40/60, L3: stages {'computed': 37, 'not run (stage cap)': 27}; strata {'i': 128, 'ii': 4019, 'iii': 0, 'iv': 333, 'v': 0, 'vi': 0}; |kappa| vs delta {'i-1': [0, 0, 299], 'i-2': [0, 0, 299], 'i-3': [0, 0, 299]}; discordant stages by level {}.

## Run 3: the knot test of runs 1 and 2

Cut to a prefix fixed before the run (deviations 33): run 2's 235 registered runs and run 1's runs of the first 100 three- and four-knot starts.
- nae: 247186 of 247186 knots tested passed; a failing share above 1.2e-05 is excluded at 95% ; untested knots are not tested and rest on the argued statement. Runs: 1435; runs with a failing knot: 0; methods disagreeing: 0.
- parity: 216017 of 216017 knots tested passed; a failing share above 1.4e-05 is excluded at 95% ; untested knots are not tested and rest on the argued statement. Runs: 1435; runs with a failing knot: 0; methods disagreeing: 0.

## Differences from the numbers disclosed in the pre-registration

- **Known 1, L8 from one knot:** POWER(3) on [0, 65], not [0, 64]: the run stops after round 65 with 50,116 knots (the knot bound read as the fold engine's, deviations 2); the verdict is the same.
- **Known 2, Ring(33, 2):** the gate, its ranges [16, 132] and [16, 264], 161 knots, spreads 2.02 and 2.02 and start knots 1.02 and 1.03 replicate; the made knots' own spread is 2.00 at 264 rounds and 2.02 at 528 (disclosed 2.02). "On [4, 32] the made knots alone read j = 2 (spread within 2)" does not hold for every made knot examined: 23 of 128 at 66 rounds, 11 of 128 at 132, 5 of 128 at 264 and 528 lie outside a factor 2, all made knots of early rounds whose count reaches the start after t holder steps (KD 8.8's missing upper end); listing `listing_run2_bare_ring_made_knots.json`. The start knot's own C/c on [4, 32], 2.41, replicates. Two-share under L0: no gate at 66 or 132, as disclosed; its start knots alone read j = 2 on their own wider ranges [4, 66] and [4, 132].
- **Known 3:** the table on the 64 starts at 40 rounds and its start-by-start statements replicate exactly (`check_known3.json`; its "census 3103 and 3192" are positions in the 3,376, file indices 3107 and 3196). The registered run 1 (100 rounds, the 219 small starts and a prefix of 250 five-knot starts) is a different set.
- **Known 6, the growing end:** the disclosed census (208 small starts and 8 named starts, rounds 1 to 3, an elimination-width cap) is not run 5's set. On run 5's 219 small starts, rounds 1 to 3: under L0 14,146 discordant comparisons under |kappa| against delta, 146 of 10,240 untied at equal loose counts (1.4 percent; disclosed 17,448 and 201 of 13,896, 1.4 percent); under |gamma| 4,224 of 40,206 untied (10.5 percent; disclosed 9.2). L1: 1,227 under |kappa|, 717 under |gamma|, 329 at equal counts (disclosed 1,570, 963, 443); L6: 923, 516, 133 (disclosed 1,051, 606, 165). Strata (i) 5,898, 4,839, 4,731, 1,131 and (ii) 1,996, 9,227, 5,680, 10,157 for L0, L1, L6, L3 (disclosed 6,872, 5,473, 5,092, 1,102 and 2,342, 11,880, 6,684, 10,153). L3's 1,224 comparisons, all tied in delta, replicate exactly (P14).
- **Known 7:** replicates exactly (census start 157 after round 1: 38,178 allowed states, kappa -1/2121, -1/707, 19/19089, S = 0; census start 133 under L1: |kappa| 1/27 at delta 2 against 4/243 at delta 1).
- **Known 10, taking rules at 100 rounds:** not reproduced by the registered seeds. Ring(5, 3) under T2 (MET on CAP-3(RETIRE)): under parity both seeds stop (rounds 47 and 72, 77 and 81 knots); under not-all-equal 296, 421, 671 and 66, 91, 141 knots at rounds 25, 50, 100 (disclosed 514, 1,575, 3,389, greatest holder steps 8, 14, 17; mine 7, 9, 11). Ring(7, 3) under T4: 218, 393, 743 knots, steps 10, 13, 22 (seed 1, not-all-equal; disclosed 228, 378, 678, 9, 14, 21). Three-knot under T4, seed 1, not-all-equal: 125, 250, 500 knots, steps 23, 48, 98 (as disclosed). The drafter's seeds and knot law for these runs are not stated; the verdicts (not held by hubs) agree.
- **Known 11:** 3,376 starts, 32 failing the parity knot test at round 0 (3 of four knots, 29 of five) replicate; the small starts of degree 2 or more under L0 replicate (run2_small_recomputed.json).
- **Known 12:** the golden-ratio eddy (Ring(5, 3) under L0) does not pass 50,000 knots after round 17: the registered guard (more than 200,000 joinable pairs in the demand roster) stops it after round 15 at 20,895 knots (deviations 27); its run 2 answer is "undecided" either way.

## Sizes run against sizes registered, and wall times

- Run 0: as registered; the run 4b probe over its cap (run 4b not run; Settled 3 "argued, unchecked").
- Run 2: as registered (235 runs, 470 gates) with the swaps and the P9 supplement; 12 min on 4 processes.
- Run 5: as registered (3,376 starts x 5 laws) with both swaps on the small starts; 21 min and 4 min.
- Run 1: cut (deviations 29) to the 219 small starts and the first 250 of the 1,000 five-knot starts; 36 min.
- Run 4: as registered (8,496 runs and 944 base-law runs); 11 min and 6 min.
- Run 3: cut (deviations 33) to run 2's 235 runs and run 1's runs of the first 100 small starts (1,435 of 2,863 runs); the direct comparison on sampled knots of at most 6 places (deviations 31); 18 min on 4 processes, stopped and resumed on 6 processes for 17 min more (deviations 34).
- Run 4b: not run (the probe). Run 4c: run with 10 numberings for T1-T8 (no run held by hubs) and all 4n for T9, T10; 2 min on 2 processes.

## Readings and texts found short

Every reading taken is a numbered item of `deviations.md` in the experiment folder, written before the run it affects. Frozen texts found short: KD 8.8 lacks the upper end r <= t for made knots (item 17); P6's clause on [4, n - 1] fails by arithmetic for small n under either reading (reported under both); P9 names L1, which run 2 does not run (supplement, items 20 and 25); KD 5.8 gives no stratum to pairs in different parts of a roster not past its start (a sixth stratum, item 21); the member shuffle's "every permutation" with several parts (item 16).

