## Gate row G

| Part | Result |
| --- | --- |
| G1 rule, 3 places | K1 True, K2 False, K3 True, knot False (command line agrees) |
| G1 rule, 4 places | K1 True, K2 False, K3 True, knot False (command line agrees) |
| G1 control parity, 3 places | K1 True, K2 True, K3 True, knot True |
| G1 control parity, 4 places | K1 True, K2 True, K3 True, knot True |
| G1 control nae, 3 places | K1 True, K2 True, K3 True, knot True |
| G1 control nae, 4 places | K1 True, K2 True, K3 True, knot True |
| G2 parity alone from the quiet start | 64 of 64 six-bit patterns, signal counts [0, 1, 2, 3, 4, 5, 6] |
| G2 nae alone from the quiet start | 64 of 64 six-bit patterns, signal counts [0, 1, 2, 3, 4, 5, 6] |
| G3 rule from the quiet start | histories 1, patterns [[0, 0, 0, 0, 0, 0]], carried count by stage [[0], [10], [0], [10]]..., engine count at depth 4 1 |

## Five-founder clock, all arms

| Arm | lawful valued starts | used | survivors at step 0 / 30 | histories per start: min / median / max | starts with exactly one history | signal fractions over the histories of a start |
| --- | --- | --- | --- | --- | --- | --- |
| rule | 4,009 | 4,009 (all) | 4,009 / 4,009 | 1 / 1.924e27 / 4.611e27 | 16 | 16 starts: 0/6; 3993 starts: 0/6,1/6,2/6,3/6,4/6,5/6,6/6 |
| parity | 8,192 | 1,024 (drawn) | 1,024 / 1,024 | 3.401e44 / 1.360e45 / 5.441e45 | 0 | 1024 starts: 0/6,1/6,2/6,3/6,4/6,5/6,6/6 |
| nae | 179,878 | 1,024 (drawn) | 1,024 / 1,024 | 6.406e80 / 5.495e81 / 2.617e82 | 0 | 1024 starts: 0/6,1/6,2/6,3/6,4/6,5/6,6/6 |

## Clock, rule arm, by carried count of the start, with the hand null

| C0 | starts | with one history | histories min .. max | fractions with a history | mean share of a start's histories at signal count 0,1,...,6 |
| --- | --- | --- | --- | --- | --- |
| 0 | 8 | 8 | 1 .. 1 | 8: 0/6 | 1.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000 |
| 2 | 302 | 0 | 2.596e16 .. 1.373e17 | 302: 0/6,1/6,2/6,3/6,4/6,5/6,6/6 | 0.0507, 0.2014, 0.3240, 0.2698, 0.1226, 0.0289, 0.0028 |
| 4 | 1623 | 0 | 9.858e25 .. 4.611e27 | 1623: 0/6,1/6,2/6,3/6,4/6,5/6,6/6 | 0.0020, 0.0224, 0.1019, 0.2453, 0.3288, 0.2322, 0.0673 |
| 6 | 1723 | 0 | 9.858e25 .. 4.611e27 | 1723: 0/6,1/6,2/6,3/6,4/6,5/6,6/6 | 0.0020, 0.0224, 0.1020, 0.2454, 0.3288, 0.2321, 0.0673 |
| 8 | 345 | 0 | 2.596e16 .. 1.373e17 | 345: 0/6,1/6,2/6,3/6,4/6,5/6,6/6 | 0.0509, 0.2019, 0.3242, 0.2694, 0.1221, 0.0287, 0.0027 |
| 10 | 8 | 8 | 1 .. 1 | 8: 0/6 | 1.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 0.0000 |

Hand null against the run: {"C0_0_or_10": {"starts": 16, "unique_and_fraction_zero": 16}, "C0_1_or_9": {"starts": 0, "histories_equal_2^30": 0, "signal_histogram_equals_hand_walk": 0, "all_seven_fractions": 0}, "C0_2_to_8": {"starts": 3993, "at_least_two_histories": 3993, "all_seven_fractions": 3993}}

## Carried count by stage on the clock

- rule: stage 0 [0, 2, 4, 6, 8, 10]; stage 1 [0, 2, 4, 6, 8, 10]; stage 2 [0, 2, 4, 6, 8, 10]; stage 29 [0, 2, 4, 6, 8, 10]; stage 30 [0, 2, 4, 6, 8, 10]; universal alternation C0, 10-C0 (rule): True; carried vectors with no lawful next step: 0 of 243
- parity: stage 0 [2, 4, 6, 8, 10]; stage 1 [0, 2, 4, 6, 8, 10]; stage 2 [0, 2, 4, 6, 8, 10]; stage 29 [0, 2, 4, 6, 8, 10]; stage 30 [0, 2, 4, 6, 8, 10]; universal alternation C0, 10-C0 (rule): None; carried vectors with no lawful next step: 0 of 243
- nae: stage 0 [1, 2, 3, 4, 5, 6, 7, 8, 9]; stage 1 [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]; stage 2 [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]; stage 29 [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]; stage 30 [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]; universal alternation C0, 10-C0 (rule): None; carried vectors with no lawful next step: 0 of 243

## seven-knot source

7 founders, 25 distinctions (9 shared), loose per founder [3, 0, 3, 3, 3, 2, 2], founder arities [6, 3, 5, 5, 7, 4, 4]; horizon 6 parent steps; knots by step [7, 15, 27, 46, 78, 134, 235, 420]; stalls None; both laws give the same births True.

Arities met: founders {'3': 1, '4': 2, '5': 2, '6': 1, '7': 1}, newborns {'5': 13, '6': 35, '7': 87, '8': 78, '9': 15}.

| Arm | lawful valued starts | used | survivors by step (drawn) | lawful starts with no survivor at the horizon | to the horizon: no history / one / two or more (drawn) | counted through | histories per start at the deepest counted step: min / median / max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| rule | 92,312 | 1,024 | [1024, 1024, 1024, 1024, 1024, 1024, 1024] | 0 | 0 / 0 / 1024 | 2 | 2.052e8 / 1.384e10 / 5.886e10 |
| parity | 262,144 | 1,024 | [1024, 1024, 1024, 1024, 1024, 1024, 1024] | 0 | 0 / 0 / 1024 | 2 | 2.048e9 / 1.106e11 / 6.636e11 |
| nae | 16,316,976 | 1,024 | [1024, 1024, 1024, 1024, 1024, 1024, 1024] | 0 | 0 / 0 / 1024 | 2 | 3.200e14 / 2.034e16 / 1.112e17 |

- rule: all lawful starts surviving by step [92312, 92312, 92312, 92312, 92312, 92312, 92312]; uniqueness over all lawful starts {'False': 92312}; prefix removal at step 2 {'space': 81920, 'dead_vectors': 0, 'examples': []}; counting stopped at depth 3 (state cap), distinct vectors finished 0 of 345; carried count values reached by stage {'1': (2, 24), '2': (0, 42), '0': (2, 14)}
- parity: all lawful starts surviving by step [262144, 262144, 262144, 262144, 262144, 262144, 262144]; uniqueness over all lawful starts None; prefix removal at step 2 {'space': 81920, 'dead_vectors': 0, 'examples': []}; counting stopped at depth 3 (state cap), distinct vectors finished 0 of 482; carried count values reached by stage {'1': (0, 24), '2': (0, 42), '0': (2, 14)}
- nae: all lawful starts surviving by step [16316976, 16316976, 16316976, 16316976, 16316976, 16316976, 16316976]; uniqueness over all lawful starts None; prefix removal at step 2 {'space': 81920, 'dead_vectors': 0, 'examples': []}; counting stopped at depth 3 (state cap), distinct vectors finished 0 of 582; carried count values reached by stage {'1': (0, 25), '2': (0, 42), '0': (2, 13)}

## nine-knot source

9 founders, 39 distinctions (10 shared), loose per founder [5, 2, 4, 3, 3, 4, 3, 3, 2], founder arities [8, 3, 7, 5, 5, 7, 5, 5, 4]; horizon 4 parent steps; knots by step [9, 24, 54, 117, 259, 597]; stalls None; both laws give the same births True.

Arities met: founders {'3': 1, '4': 1, '5': 4, '7': 2, '8': 1}, newborns {'4': 2, '5': 2, '6': 20, '7': 42, '8': 50, '9': 74, '10': 44, '11': 14, '12': 2}.

| Arm | lawful valued starts | used | survivors by step (drawn) | lawful starts with no survivor at the horizon | to the horizon: no history / one / two or more (drawn) | counted through | histories per start at the deepest counted step: min / median / max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| rule | 449,885,231 | 1,024 | [1024, 1024, 1024, 1024, 1024] | 0 | 0 / 0 / 1024 | 1 | 2,645,248 / 7.920e8 / 1.000e10 |
| parity | 1,073,741,824 | 1,024 | [1024, 1024, 1024, 1024, 1024] | 0 | 0 / 0 / 1024 | 1 | 2.184e7 / 9.137e9 / 1.521e11 |
| nae | 267,940,964,814 | 1,024 | [1024, 1024, 1024, 1024, 1024] | 0 | 0 / 0 / 1024 | 1 | 3.741e11 / 7.756e13 / 8.906e14 |

- rule: all lawful starts surviving by step [449885231, 449885231, 449885231, 449885231, 449885231]; uniqueness over all lawful starts {'False': 449885231}; prefix removal at step 2 {'space': 41990400000, 'skipped': 'space too large to enumerate'}; counting stopped at depth 2 (state cap), distinct vectors finished 1 of 966; carried count values reached by stage {'1': (8, 60), '0': (6, 22)}
- parity: all lawful starts surviving by step [1073741824, 1073741824, 1073741824, 1073741824, 1073741824]; uniqueness over all lawful starts None; prefix removal at step 2 {'space': 41990400000, 'skipped': 'space too large to enumerate'}; counting stopped at depth 2 (state cap), distinct vectors finished 0 of 1004; carried count values reached by stage {'1': (0, 62), '0': (4, 22)}
- nae: all lawful starts surviving by step [267940964814, 267940964814, 267940964814, 267940964814, 267940964814]; uniqueness over all lawful starts None; prefix removal at step 2 {'space': 41990400000, 'skipped': 'space too large to enumerate'}; counting stopped at depth 2 (state cap), distinct vectors finished 0 of 990; carried count values reached by stage {'1': (0, 63), '0': (6, 22)}

