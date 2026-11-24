## Row G
| Check | Result |
| --- | --- |
| R and the ordinary mode against the recorded driver, 280 funded draws, parity | ordinary mode 280/280, R-O 280/280, R-N 280/280 identical; payments 0+0, short knots 0+0; rounds also matched against the recorded operator 2528 (R-O) |
| R and the ordinary mode against the recorded driver, 280 funded draws, nae | ordinary mode 280/280, R-O 280/280, R-N 280/280 identical; payments 0+0, short knots 0+0; rounds also matched against the recorded operator 3360 (R-O) |
| R against the recorded driver on the seven recorded sources (test (b)) | 28/28 R histories identical (digest of full holdings, knots per stage, outcome, first failing step); payments, short knots and elimination disagreements: 0 |
| Elimination against the shortcut, every parity birth of the 1,024 ordinary histories | 25257 births, 0 disagreements; closings met 78 |
| Elimination against enumeration, stages of at most 20 distinctions in rounds 1-2 of R (O, parity) on all 1,024 draws | 5635 births on 1196 stages, 5635 agree, 76 implied |
| The two closings of test (d) at 00, ordinary growth | C_binary: shortcut [True], elimination [True], enumeration [True]; C_ternary: shortcut [True], elimination [True], enumeration [True] |
| Rounds of test (c) also run by the recorded code (R, both laws, both conventions) | groups 41967, lookaheads 41583, whole rounds with no short knot 39033 (fresh counts equal 38015, differ by the replaced closing test 1018); every one equal |
| C search against Python search on ends and lookaheads beyond the recorded code's reach (gate f) | 41428/41428 equal |
| Next-round cap shortcut against full computation (gate f) | 28/28 agree; 22 of 50 shortcut histories not verified (size) |

## Test (b): the seven recorded sources
| Source | Law | Rule | Outcome | Knots per stage (last) | Rounds | First failing step | Kind | Most holders | Payments |
| --- | --- | --- | --- | ---: | ---: | ---: | --- | ---: | ---: |
| archive_start-00 | nae | R-N | horizon | 702 | 16 | 1 | growing | 2 | 0 |
| archive_start-00 | nae | R-O | horizon | 702 | 16 | 1 | growing | 2 | 0 |
| archive_start-00 | nae | ordinary (recorded driver) | horizon | 702 | 16 | 1 | growing | 2 | 0 |
| archive_start-00 | parity | R-N | horizon | 702 | 16 | 1 | growing | 2 | 0 |
| archive_start-00 | parity | R-O | horizon | 702 | 16 | 1 | growing | 2 | 0 |
| archive_start-00 | parity | ordinary (recorded driver) | horizon | 702 | 16 | 1 | growing | 2 | 0 |
| archive_start-04 | nae | R-N | cap | 2081 | 8 | 1 | growing | 2 | 0 |
| archive_start-04 | nae | R-O | cap | 2081 | 8 | 1 | growing | 2 | 0 |
| archive_start-04 | nae | ordinary (recorded driver) | cap | 2081 | 8 | 1 | growing | 2 | 0 |
| archive_start-04 | parity | R-N | cap | 2081 | 8 | 1 | growing | 2 | 0 |
| archive_start-04 | parity | R-O | cap | 2081 | 8 | 1 | growing | 2 | 0 |
| archive_start-04 | parity | ordinary (recorded driver) | cap | 2081 | 8 | 1 | growing | 2 | 0 |
| archive_start-13 | nae | R-N | cap | 1368 | 6 | 1 | growing | 2 | 0 |
| archive_start-13 | nae | R-O | cap | 1368 | 6 | 1 | growing | 2 | 0 |
| archive_start-13 | nae | ordinary (recorded driver) | cap | 1368 | 6 | 1 | growing | 2 | 0 |
| archive_start-13 | parity | R-N | cap | 1368 | 6 | 1 | growing | 2 | 0 |
| archive_start-13 | parity | R-O | cap | 1368 | 6 | 1 | growing | 2 | 0 |
| archive_start-13 | parity | ordinary (recorded driver) | cap | 1368 | 6 | 1 | growing | 2 | 0 |
| five_founder_clock | nae | R-N | horizon | 85 | 16 | 1 | bounded | 2 | 0 |
| five_founder_clock | nae | R-O | horizon | 85 | 16 | 1 | bounded | 2 | 0 |
| five_founder_clock | nae | ordinary (recorded driver) | horizon | 85 | 16 | 1 | bounded | 2 | 0 |
| five_founder_clock | parity | R-N | horizon | 85 | 16 | 1 | bounded | 2 | 0 |
| five_founder_clock | parity | R-O | horizon | 85 | 16 | 1 | bounded | 2 | 0 |
| five_founder_clock | parity | ordinary (recorded driver) | horizon | 85 | 16 | 1 | bounded | 2 | 0 |
| knots21_two_clocks | nae | R-N | cap | 13486 | 8 | 2 | growing | 2 | 0 |
| knots21_two_clocks | nae | R-O | cap | 13486 | 8 | 2 | growing | 2 | 0 |
| knots21_two_clocks | nae | ordinary (recorded driver) | cap | 13486 | 8 | 2 | growing | 2 | 0 |
| knots21_two_clocks | parity | R-N | cap | 13486 | 8 | 2 | growing | 2 | 0 |
| knots21_two_clocks | parity | R-O | cap | 13486 | 8 | 2 | growing | 2 | 0 |
| knots21_two_clocks | parity | ordinary (recorded driver) | cap | 13486 | 8 | 2 | growing | 2 | 0 |
| nine_knot_drawn | nae | R-N | cap | 8911 | 8 | 1 | growing | 2 | 0 |
| nine_knot_drawn | nae | R-O | cap | 8911 | 8 | 1 | growing | 2 | 0 |
| nine_knot_drawn | nae | ordinary (recorded driver) | cap | 8911 | 8 | 1 | growing | 2 | 0 |
| nine_knot_drawn | parity | R-N | cap | 8911 | 8 | 1 | growing | 2 | 0 |
| nine_knot_drawn | parity | R-O | cap | 8911 | 8 | 1 | growing | 2 | 0 |
| nine_knot_drawn | parity | ordinary (recorded driver) | cap | 8911 | 8 | 1 | growing | 2 | 0 |
| seven_knot | nae | R-N | cap | 19614 | 13 | 1 | growing | 2 | 0 |
| seven_knot | nae | R-O | cap | 19614 | 13 | 1 | growing | 2 | 0 |
| seven_knot | nae | ordinary (recorded driver) | cap | 19614 | 13 | 1 | growing | 2 | 0 |
| seven_knot | parity | R-N | cap | 19614 | 13 | 1 | growing | 2 | 0 |
| seven_knot | parity | R-O | cap | 19614 | 13 | 1 | growing | 2 | 0 |
| seven_knot | parity | ordinary (recorded driver) | cap | 19614 | 13 | 1 | growing | 2 | 0 |

## Test (c): the 1,024 draws per law under R
Population: the 744 draws per law that make no birth at round 1 under ordinary growth (731 stall, 13 have no live knot). The other 280 per law are funded; under R they are identical to ordinary growth (row G).

| Law | Convention | Residual stall at round 1 | No live knot | Residual stall later | Closed | Alive at 12 rounds | Cap (5,000 knots) | Kind (recorded fn): stalled / bounded / growing | Kind by births: stalled / bounded / growing |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| nae | N | 85 | 13 | 0 | 0 | 625 | 21 | 98 / 171 / 475 | 98 / 171 / 475 |
| nae | O | 102 | 13 | 0 | 0 | 605 | 24 | 115 / 160 / 469 | 115 / 160 / 469 |
| parity | N | 85 | 13 | 0 | 21 | 604 | 21 | 98 / 191 / 455 | 98 / 191 / 455 |
| parity | O | 102 | 13 | 0 | 17 | 588 | 24 | 115 / 176 / 453 | 115 / 176 / 453 |

Largest number of holders of a distinction within the horizon (744 draws per law):

| Law | Convention | 2 | 3 | 4 | 5 | 6+ | Largest | Draws with 4 or more |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| nae | N | 98 | 549 | 97 | 0 | 0 | 4 | 97 |
| nae | O | 115 | 521 | 108 | 0 | 0 | 4 | 108 |
| parity | N | 98 | 549 | 97 | 0 | 0 | 4 | 97 |
| parity | O | 115 | 521 | 108 | 0 | 0 | 4 | 108 |

First failing step of the operator test (stage index; none = passes at every stage reached):

| Law | Convention | none | 0 | 1 | 2 | 3 | 4+ | Under ordinary growth (same draws): none / fails |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| nae | N | 152 | 0 | 215 | 299 | 77 | 1 | 744 / 0 |
| nae | O | 162 | 0 | 196 | 301 | 83 | 2 | 744 / 0 |
| parity | N | 152 | 0 | 215 | 299 | 77 | 1 | 744 / 0 |
| parity | O | 162 | 0 | 196 | 301 | 83 | 2 | 744 / 0 |

Rounds and births with a payment by a shared distinction (744 draws per law):

| Law | Convention | Rounds | Rounds with a payment | Births | Births with a shared distinction | Payments | Short knots | Implied births (no fresh) | Births with fresh counts as lower bounds |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| nae | N | 7688 | 646 | 145218 | 1593 | 1926 | 1480 | 0 | 28080 |
| nae | O | 7468 | 629 | 147138 | 1518 | 1820 | 1418 | 0 | 35267 |
| parity | N | 7504 | 646 | 144279 | 1593 | 1926 | 1480 | 21 | 28080 |
| parity | O | 7319 | 629 | 146365 | 1518 | 1820 | 1418 | 17 | 35267 |

Rounds with a payment after round 1: nae-N 0, nae-O 0, parity-N 0, parity-O 0

Do the two conventions give the same numbers of births per round?

| Law | Draws (of 744) with the same births per round | Different | Different and both alive through round 2 | Same outcome |
| --- | ---: | ---: | ---: | ---: |
| parity | 266 | 478 | 453 | 664 |
| nae | 273 | 471 | 446 | 696 |

Examples (parity): arm 0 draw 1: O [7, 8, 10, 11, 11], N [7, 9, 10, 12, 13]; arm 0 draw 3: O [7, 6, 4, 1, 1], N [7, 9, 13, 18, 23]; arm 0 draw 4: O [9, 11, 11, 9, 7], N [9, 11, 10, 9, 7]
Examples (nae): arm 0 draw 1: O [7, 8, 10, 11, 11], N [7, 9, 10, 12, 13]; arm 0 draw 3: O [7, 6, 4, 1, 1], N [7, 9, 13, 18, 23]; arm 0 draw 4: O [9, 11, 11, 9, 7], N [9, 11, 10, 9, 7]

Funded draws in the test (c) runs: 1120 of 1120 histories (both laws, both conventions) equal ordinary growth in knots per stage, outcome and first failing step.

Residual stalls at round 1: knots left short, by number of unpaid births (744 draws per law):
- nae-N: 85 draws; unpaid births per draw {1: 54, 2: 18, 3: 1, 4: 3, 5: 4, 6: 3, 9: 1, 11: 1}
- nae-O: 102 draws; unpaid births per draw {1: 66, 2: 20, 3: 4, 4: 2, 5: 5, 6: 3, 9: 1, 11: 1}
- parity-N: 85 draws; unpaid births per draw {1: 54, 2: 18, 3: 1, 4: 3, 5: 4, 6: 3, 9: 1, 11: 1}
- parity-O: 102 draws; unpaid births per draw {1: 66, 2: 20, 3: 4, 4: 2, 5: 5, 6: 3, 9: 1, 11: 1}

## Test (c): every allowed choice, rounds 1 and 2
| Law | Draws | No live knot | No short knot at round 1 | Short | Every choice stalls at round 1 | Some choice pays | Choices at round 1 (sum; largest) | Of those: the convention O stalls but a choice pays / N |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| parity | 1024 | 13 | 280 | 731 | 80 | 651 | 389759; 46656 | 22 / 5 |
| nae | 1024 | 13 | 280 | 731 | 80 | 651 | 389759; 46656 | 22 / 5 |
Draws where every choice stalls at round 1 (the same under both laws), by cause: {'owes more than it holds in all': 80}.

parity: on the 651 draws where some choice pays, round-2 births depend on the choice in 492; some round-1 choice leaves a short knot at round 2 in 1 (every round-2 choice stalls after some round-1 choice in 0); largest number of holders after two rounds over all choices (histories): {2: 280, 3: 117730, 4: 272218}; the conventions' round-2 births are among the enumerated ones in 1275 of 1275.

nae: on the 651 draws where some choice pays, round-2 births depend on the choice in 492; some round-1 choice leaves a short knot at round 2 in 0 (every round-2 choice stalls after some round-1 choice in 0); largest number of holders after two rounds over all choices (histories): {2: 280, 3: 117637, 4: 272122}; the conventions' round-2 births are among the enumerated ones in 1275 of 1275.

## Test (d): the stalling set-ups
| Set-up | Law | Rule | Outcome pairs 00, 01, 10, 11 | Alice own / far | Bob own / far | Signed | Largest | Prepared words |
| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: |
| S_cycle_five | parity | ordinary | 00, 00, 00, 11 | yes / yes | yes / yes | 2 | 2 | 256 |
| S_cycle_five | parity | R_O | 11, 11, 11, 11 | no / no | no / no | - | - | 256 |
| S_cycle_five | parity | R_N | 11, 11, 11, 11 | no / no | no / no | - | - | 256 |
| S_cycle_five | parity | R, every choice | 00: 16 choices -> ['(1, 1)'], 01: 4 choices -> ['(1, 1)'], 10: 4 choices -> ['(1, 1)'], 11: 1 choices -> ['(1, 1)'] | | | | | |
| S_cycle_five | nae | ordinary | 00, 00, 00, 11 | yes / yes | yes / yes | 2 | 2 | 3086 |
| S_cycle_five | nae | R_O | 11, 11, 11, 11 | no / no | no / no | - | - | 3086 |
| S_cycle_five | nae | R_N | 11, 11, 11, 11 | no / no | no / no | - | - | 3086 |
| S_cycle_five | nae | R, every choice | 00: 16 choices -> ['(1, 1)'], 01: 4 choices -> ['(1, 1)'], 10: 4 choices -> ['(1, 1)'], 11: 1 choices -> ['(1, 1)'] | | | | | |
| C_binary | parity | ordinary | 10, 01, 00, 01 | yes / yes | yes / no | 0 | 4 | 8 |
| C_binary | parity | R_O | 10, 01, 00, 01 | yes / yes | yes / no | 0 | 4 | 8 |
| C_binary | parity | R_N | 10, 01, 00, 01 | yes / yes | yes / no | 0 | 4 | 8 |
| C_binary | parity | R, every choice | 00: 1 choices -> ['(1, 0)'], 01: 1 choices -> ['(0, 1)'], 10: 1 choices -> ['(0, 0)'], 11: 1 choices -> ['(0, 1)'] | | | | | |
| C_binary | nae | ordinary | 00, 01, 00, 01 | no / no | yes / no | 2 | 2 | 34 |
| C_binary | nae | R_O | 00, 01, 00, 01 | no / no | yes / no | 2 | 2 | 34 |
| C_binary | nae | R_N | 00, 01, 00, 01 | no / no | yes / no | 2 | 2 | 34 |
| C_binary | nae | R, every choice | 00: 1 choices -> ['(0, 0)'], 01: 1 choices -> ['(0, 1)'], 10: 1 choices -> ['(0, 0)'], 11: 1 choices -> ['(0, 1)'] | | | | | |
| C_ternary | parity | ordinary | 10, 01, 00, 01 | yes / yes | yes / no | 0 | 4 | 32 |
| C_ternary | parity | R_O | 10, 01, 00, 01 | yes / yes | yes / no | 0 | 4 | 32 |
| C_ternary | parity | R_N | 10, 01, 00, 01 | yes / yes | yes / no | 0 | 4 | 32 |
| C_ternary | parity | R, every choice | 00: 1 choices -> ['(1, 0)'], 01: 1 choices -> ['(0, 1)'], 10: 1 choices -> ['(0, 0)'], 11: 1 choices -> ['(0, 1)'] | | | | | |
| C_ternary | nae | ordinary | 00, 01, 00, 01 | no / no | yes / no | 2 | 2 | 428 |
| C_ternary | nae | R_O | 00, 01, 00, 01 | no / no | yes / no | 2 | 2 | 428 |
| C_ternary | nae | R_N | 00, 01, 00, 01 | no / no | yes / no | 2 | 2 | 428 |
| C_ternary | nae | R, every choice | 00: 1 choices -> ['(0, 0)'], 01: 1 choices -> ['(0, 1)'], 10: 1 choices -> ['(0, 0)'], 11: 1 choices -> ['(0, 1)'] | | | | | |

## Test (e): pace
Largest distance of a changed birth by round t (over the 200 pairs), and the pairs judged:

| Law | Rule | t=1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | Pairs with a residual stall | Pairs with a stall | Pairs above 3t+3 (no residual stall) | Pairs with a changed birth at t=1 beyond 6 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| parity | ordinary | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 0 | 39 | 0 | 0 |
| parity | RO | 2 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 1 | 0 | 0 | 0 |
| parity | RN | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 0 | 0 | 0 | 0 |
| nae | ordinary | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 0 | 39 | 0 | 0 |
| nae | RO | 2 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 3 | 1 | 0 | 0 | 0 |
| nae | RN | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 2 | 0 | 0 | 0 | 0 |

Largest start distance from the edited knot over the 200 draws: {1: 32, 2: 78, 3: 69, 4: 19, 5: 2}.
Ordinary growth, parity: 39 pairs stall (the edited start, at round 1); in them the largest distance of a changed birth at round 1 is {2: 15, 3: 10, 1: 14}, equal to the start's largest distance from the edited knot in 37.
Ordinary growth, nae: 39 pairs stall (the edited start, at round 1); in them the largest distance of a changed birth at round 1 is {2: 15, 3: 10, 1: 14}, equal to the start's largest distance from the edited knot in 37.
R-O, parity: rounds 4170, rounds with a payment 38; births 42966, with a shared distinction 63.
R-N, parity: rounds 4133, rounds with a payment 39; births 42073, with a shared distinction 67.
R-O, nae: rounds 4788, rounds with a payment 38; births 46514, with a shared distinction 63.
R-N, nae: rounds 4800, rounds with a payment 39; births 45886, with a shared distinction 67.

## Test (a): extension by enumeration (stages of at most 22 distinctions)
| Source | Histories | Rounds | Births | Births with a shared distinction | Births with no fresh distinction | Allowed words checked | Words that fail to extend | Projection cross-checks (equal) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| test (c), conventions | 3662 | 7287 | 28856 | 6182 | 184 | 141910112 | 0 | 4410 (4410) |
| test (d), R | 48 | 48 | 144 | 16 | 4 | 83336 | 0 | 40 (40) |
| test (e), R | 1598 | 3503 | 12913 | 260 | 119 | 66098818 | 0 | 2364 (2364) |
| test (c), every choice | (per choice) | 761642 | 6116567 | 4127550 | 303 | 18486067068 | 0 | - (-) |
| all | | 772480 | 6158480 | 4134008 | 610 | 18694159334 | 0 | 6814 (6814) |

