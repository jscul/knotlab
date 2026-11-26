# FOLLOWS-THE-FORM-20261125-001A-E001: summary

An independent reading on the shared growth engine (ticket B's `eng.py`, unchanged), written from the frozen texts alone. Every prediction is judged by its "Fails when" entry. Readings chosen where the texts leave a choice are numbered in `deviations.md` of the experiment folder. No weighting is named.

## Predictions

| # | verdict | numbers |
| --- | --- | --- |
| G | **holds** | three starts as written; 400 sampled runs: 209/209 with no taking rule identical to the fold engine at every round; 191/191 with the take, 85436 births, 9547 takes, every take as the rule says |
| PR1 | **holds** | 270 of 270 studies with R* and classes equal |
| PR2 | **holds** | 0 differing cells of 62 |
| PR3 | **holds** | 0 differing cells of 162 |
| PR5 | **holds** | 0 differing cells of 158 |
| PR4 | **holds** | 9000 runs; 0 with a start knot a member after round 1 |
| CU | **holds** | 90 of 90 studies with every form in the bare start's class |
| S1 | **holds** | 90 of 90 studies |
| S2 | **holds** | 90 of 90 studies; fewest 2 |
| S3 | **holds** | cells: 20/20 |
| PN2 | **holds** | 87 of 90 studies (needs 81) |
| PN3 | **holds** | by row: {"none, CANCEL-RETIRE": 422, "none, CANCEL-OFFSHOOT": 445, "none, CANCEL-WAIT": 5415, "sole, CANCEL-RETIRE": 765, "sole, CANCEL-OFFSHOOT": 1309, "sole, CANCEL-WAIT": 4816} (needs 50 in each row with retiring or offshoots) |
| PN4 | **holds** | percent by row: {"none, CANCEL-RETIRE": 58.92, "none, CANCEL-OFFSHOOT": 58.55, "none, CANCEL-WAIT": 80.24, "sole, CANCEL-RETIRE": 71.91, "sole, CANCEL-OFFSHOOT": 74.35, "sole, CANCEL-WAIT": 87.07} |
| PN5 | **fails** | 37 of 90 studies (needs 40); fates not read in 4 |
| PN6 | **holds** | 87 of 90 studies (needs 60) |
| PN7 | **holds** | not a function of the held knot in 90 (needs 81); not of it with the births by round in 41 (needs 25); not of the births by round alone in 87; of 90 |
| PD1 | **holds** | highest: depth 2 10.0%, depth 3 0.0%, depth 4 0.0%, 3 against 4 knots 20.0%, 4 against 5 knots 0.0% |
| PD2 | **holds** | sole, ORD, CANCEL-RETIRE 32/160 (20.0%), sole, ORD, CANCEL-OFFSHOOT 32/160 (20.0%), sole, ORD, CANCEL-WAIT 48/160 (30.0%), sole, CAP-3, CANCEL-WAIT 126/160 (78.8%) |
| C1 | **holds** | 900 of 900 renumbered runs make the same |
| C2 | **holds** | cut to half (deviations 35): not-all-equal 99 of 100 runs tested, 113640 verdicts, 0 failing; parity 50 of 50 runs, 62347 verdicts, 0 failing knots in 0 runs (reported); not run: job 941 (R2|nae|fresh|L|None|ORD|CANCEL-WAIT|ring:3,1,3,1@0|True). Outside the half, reported apart: not-all-equal 80 runs, 100244 verdicts, 0 failing; parity 34 runs, 0 failing |

First failing case of each failed prediction:

- **PN5**: `"fewer than 40 studies"`

Claim parts as the pre-registration judges them: claim C1 (by PN2 and PN4 with CU): holds; claim C2 (by PN3): holds; claim C3 (by PN7): holds; claim C4 (by PN5): fails; claim C5 (by PD1 and PD2): holds.

## Checks reported with the verdicts

- PN5 reading applied to R1 (disclosed: 58 of 90 on mixed, 62 of 90 on second): {"mixed": 58, "second": 62, "chains": 52}
- R4 against R2: runs whose record differs (parity against not-all-equal, same starts and laws): [28, 5490]
- R4: entries of the wider record with f = 0 (implied births of the first): 22
- studies of R4 whose classes differ from the same study of R2: 0

## Wall time

From `logs/walltime.log` (timing parts and readings are listed in `deviations.md`, entries 28 to 35):

```
R0 start 2026-11-25T23:31:46Z
R0 pids 2420321 2420322 2420323 2420324 2420325 2420326 2420327 2420328
R0 end 2026-11-25T23:31:56Z wall 10.393047258 s rc 0
R1 start 2026-11-25T23:32:14Z
R1 pids 2420746 2420747 2420748 2420749 2420750 2420751 2420752 2420753
R1 end 2026-11-25T23:35:28Z wall 193.690078414 s rc 0
R2 start 2026-11-25T23:37:37Z
R2 pids 2422273 2422274 2422275 2422276 2422277 2422278 2422279 2422280
R2 end 2026-11-25T23:40:01Z wall 144.557045978 s rc 0
R2u start 2026-11-25T23:40:23Z
R2u pids 2422779 2422780 2422781 2422782 2422783 2422784 2422785 2422786
R2u end 2026-11-25T23:41:18Z wall 55.208771573 s rc 0
R3 start 2026-11-25T23:41:45Z
R3 pids 2423009 2423010 2423011 2423012 2423013 2423014 2423015 2423016
R3 end 2026-11-25T23:42:54Z wall 69.511477399 s rc 0
R4 start 2026-11-25T23:43:19Z
R4 pids 2423315 2423316 2423317 2423318 2423319 2423320 2423321 2423322
R4 end 2026-11-25T23:45:45Z wall 146.656567407 s rc 0
R5 start 2026-11-25T23:50:47Z
R5 pids 2424403 2424404 2424405 2424406 2424407 2424408 2424409 2424410
R5 chunk 3 (pid 2424406) stopped 2026-11-26T00:04:55Z, deviations 35
R5rest start 2026-11-26T00:05:03Z
R5rest 0 pid 2431314
R5rest 1 pid 2431315
R5rest 2 pid 2431316
R5rest 3 pid 2431317
R5rest 4 pid 2431318
R5rest 5 pid 2431319
R5rest 6 pid 2431320
R5rest 1 (pid 2431315) finished 2026-11-26T00:12:01Z
R5 chunk 0 (pid 2424403) stopped at the deadline, job 941 unfinished 2026-11-26T00:33:04Z
R5 end 2026-11-26T00:33:04Z wall 2536.616025005 s rc 1
```

## R2, held out (`fresh`, first seeds K to O, not-all-equal)

**First told apart**, pairs of forms (26550 a row):

| row | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | never | not read further |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| none, CANCEL-RETIRE | 15051 | 591 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10908 | 0 |
| none, CANCEL-OFFSHOOT | 14961 | 583 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 11006 | 0 |
| none, CANCEL-WAIT | 15208 | 4168 | 1212 | 182 | 414 | 120 | 0 | 0 | 0 | 5218 | 28 |
| sole, CANCEL-RETIRE | 18083 | 979 | 24 | 0 | 5 | 0 | 0 | 0 | 0 | 6828 | 631 |
| sole, CANCEL-OFFSHOOT | 18324 | 1413 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 6136 | 675 |
| sole, CANCEL-WAIT | 18241 | 3492 | 1068 | 209 | 158 | 124 | 16 | 1 | 1 | 2755 | 485 |

**After the first round:**

| row | pairs | told apart at R* | first told apart in round 2 or later | of those, the wider record of round 1 the same | in round 3 or later with the wider records the same through round 2 |
| --- | --- | --- | --- | --- | --- |
| none, CANCEL-RETIRE | 26550 | 15642 | 591 | 422 | 0 |
| none, CANCEL-OFFSHOOT | 26550 | 15544 | 583 | 445 | 0 |
| none, CANCEL-WAIT | 26550 | 21304 | 6096 | 5415 | 1291 |
| sole, CANCEL-RETIRE | 26550 | 19091 | 1008 | 765 | 0 |
| sole, CANCEL-OFFSHOOT | 26550 | 19739 | 1415 | 1309 | 0 |
| sole, CANCEL-WAIT | 26550 | 23117 | 5069 | 4816 | 1370 |

**Fates on the window** (forms):

| row | grows | steady | shrinks | other | ends, taken up | ends, no births | not read |
| --- | --- | --- | --- | --- | --- | --- | --- |
| none, CANCEL-RETIRE | 734 | 45 | 0 | 0 | 61 | 60 | 0 |
| none, CANCEL-OFFSHOOT | 801 | 38 | 0 | 0 | 61 | 0 | 0 |
| none, CANCEL-WAIT | 738 | 38 | 0 | 0 | 60 | 64 | 0 |
| sole, CANCEL-RETIRE | 477 | 0 | 71 | 30 | 44 | 218 | 60 |
| sole, CANCEL-OFFSHOOT | 714 | 0 | 22 | 32 | 12 | 0 | 120 |
| sole, CANCEL-WAIT | 537 | 5 | 21 | 46 | 32 | 199 | 60 |

**The count profile** (studies in which the class is a function of it): the held knot 0; the second seed's births by round 3; both 49; of 90 studies.

**R\*** by row: none, CANCEL-RETIRE: {"9": 15}; none, CANCEL-OFFSHOOT: {"9": 15}; none, CANCEL-WAIT: {"9": 12, "6": 1, "7": 2}; sole, CANCEL-RETIRE: {"9": 10, "4": 2, "3": 1, "5": 1, "6": 1}; sole, CANCEL-OFFSHOOT: {"9": 10, "4": 3, "3": 2}; sole, CANCEL-WAIT: {"9": 10, "4": 4, "3": 1}

**Classes among the forms** (studies by number of classes): {"2": 3, "3": 14, "4": 5, "5": 13, "6": 4, "7": 7, "8": 8, "9": 4, "10": 1, "11": 3, "12": 4, "13": 2, "14": 5, "15": 1, "16": 2, "17": 1, "18": 3, "21": 1, "22": 2, "25": 1, "27": 1, "32": 3, "33": 1, "36": 1}. **By the wider record**: {"2": 3, "3": 6, "4": 3, "5": 3, "6": 6, "7": 3, "8": 3, "9": 3, "10": 6, "11": 4, "12": 1, "13": 2, "14": 4, "15": 3, "16": 2, "17": 2, "18": 1, "19": 5, "20": 2, "21": 1, "23": 1, "24": 3, "25": 1, "26": 1, "27": 4, "31": 2, "33": 1, "37": 2, "40": 1, "43": 2, "44": 1, "46": 3, "47": 1, "49": 2, "50": 1, "52": 1}. Wider record against own descent: {"equal": 21, "more": 69}.

Bare start a class of its own: [90, 90] studies.

## R4, the knot law swapped (`fresh`, K to O, parity)

**First told apart**, pairs of forms (26550 a row):

| row | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | never | not read further |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| none, CANCEL-RETIRE | 15051 | 591 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 10908 | 0 |
| none, CANCEL-OFFSHOOT | 14961 | 583 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 11006 | 0 |
| none, CANCEL-WAIT | 15208 | 4168 | 1212 | 182 | 414 | 120 | 0 | 0 | 0 | 5218 | 28 |
| sole, CANCEL-RETIRE | 18083 | 979 | 24 | 0 | 5 | 0 | 0 | 0 | 0 | 6828 | 631 |
| sole, CANCEL-OFFSHOOT | 18324 | 1413 | 2 | 0 | 0 | 0 | 0 | 0 | 0 | 6136 | 675 |
| sole, CANCEL-WAIT | 18241 | 3492 | 1068 | 209 | 158 | 124 | 16 | 1 | 1 | 2755 | 485 |

**After the first round:**

| row | pairs | told apart at R* | first told apart in round 2 or later | of those, the wider record of round 1 the same | in round 3 or later with the wider records the same through round 2 |
| --- | --- | --- | --- | --- | --- |
| none, CANCEL-RETIRE | 26550 | 15642 | 591 | 422 | 0 |
| none, CANCEL-OFFSHOOT | 26550 | 15544 | 583 | 445 | 0 |
| none, CANCEL-WAIT | 26550 | 21304 | 6096 | 5415 | 1291 |
| sole, CANCEL-RETIRE | 26550 | 19091 | 1008 | 765 | 0 |
| sole, CANCEL-OFFSHOOT | 26550 | 19739 | 1415 | 1309 | 0 |
| sole, CANCEL-WAIT | 26550 | 23117 | 5069 | 4816 | 1370 |

**Fates on the window** (forms):

| row | grows | steady | shrinks | other | ends, taken up | ends, no births | not read |
| --- | --- | --- | --- | --- | --- | --- | --- |
| none, CANCEL-RETIRE | 734 | 45 | 0 | 0 | 61 | 60 | 0 |
| none, CANCEL-OFFSHOOT | 801 | 38 | 0 | 0 | 61 | 0 | 0 |
| none, CANCEL-WAIT | 738 | 38 | 0 | 0 | 60 | 64 | 0 |
| sole, CANCEL-RETIRE | 477 | 0 | 71 | 30 | 42 | 220 | 60 |
| sole, CANCEL-OFFSHOOT | 714 | 0 | 22 | 32 | 12 | 0 | 120 |
| sole, CANCEL-WAIT | 537 | 5 | 21 | 46 | 28 | 203 | 60 |

**The count profile** (studies in which the class is a function of it): the held knot 0; the second seed's births by round 3; both 49; of 90 studies.

**R\*** by row: none, CANCEL-RETIRE: {"9": 15}; none, CANCEL-OFFSHOOT: {"9": 15}; none, CANCEL-WAIT: {"9": 12, "6": 1, "7": 2}; sole, CANCEL-RETIRE: {"9": 10, "4": 2, "3": 1, "5": 1, "6": 1}; sole, CANCEL-OFFSHOOT: {"9": 10, "4": 3, "3": 2}; sole, CANCEL-WAIT: {"9": 10, "4": 4, "3": 1}

**Classes among the forms** (studies by number of classes): {"2": 3, "3": 14, "4": 5, "5": 13, "6": 4, "7": 7, "8": 8, "9": 4, "10": 1, "11": 3, "12": 4, "13": 2, "14": 5, "15": 1, "16": 2, "17": 1, "18": 3, "21": 1, "22": 2, "25": 1, "27": 1, "32": 3, "33": 1, "36": 1}. **By the wider record**: {"2": 3, "3": 6, "4": 3, "5": 3, "6": 6, "7": 3, "8": 3, "9": 3, "10": 6, "11": 2, "12": 3, "13": 2, "14": 3, "15": 4, "16": 1, "17": 3, "18": 1, "19": 5, "20": 2, "21": 1, "23": 1, "24": 3, "25": 1, "26": 1, "27": 4, "31": 2, "33": 1, "37": 2, "40": 1, "43": 2, "44": 1, "46": 1, "47": 3, "49": 2, "50": 1, "52": 1}. Wider record against own descent: {"equal": 21, "more": 69}.

Bare start a class of its own: [90, 90] studies.

## R2u, the unlinked control

**Unlinked control, fresh**: studies 90; studies in which every form is in the bare start's class 90. R\* by row: none, CANCEL-RETIRE: {"9": 15}; none, CANCEL-OFFSHOOT: {"9": 15}; none, CANCEL-WAIT: {"9": 15}; sole, CANCEL-RETIRE: {"9": 10, "3": 5}; sole, CANCEL-OFFSHOOT: {"9": 10, "3": 5}; sole, CANCEL-WAIT: {"9": 10, "3": 5}.

## R3, depth on the chains (first seeds K to O together; told apart / pairs)

| law | depth 0 | 1 against 2 knots | depth 1 | 2 against 3 knots | depth 2 | 3 against 4 knots | depth 3 | 4 against 5 knots | depth 4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| none, FLOOR1, CANCEL-RETIRE | 0/155 | 20/20 | 0/150 | 0/40 | 0/140 | 0/80 | 0/120 | 0/160 | 0/80 |
| none, FLOOR1, CANCEL-OFFSHOOT | 0/155 | 20/20 | 0/150 | 0/40 | 0/140 | 0/80 | 0/120 | 0/160 | 0/80 |
| none, FLOOR1, CANCEL-WAIT | 60/155 | 20/20 | 0/150 | 8/40 | 0/140 | 16/80 | 0/120 | 0/160 | 0/80 |
| none, CAP-3, CANCEL-RETIRE | 0/155 | 20/20 | 0/150 | 0/40 | 0/140 | 0/80 | 0/120 | 0/160 | 0/80 |
| none, CAP-3, CANCEL-OFFSHOOT | 0/155 | 20/20 | 0/150 | 0/40 | 0/140 | 0/80 | 0/120 | 0/160 | 0/80 |
| none, CAP-3, CANCEL-WAIT | 58/155 | 20/20 | 0/150 | 14/40 | 14/140 | 0/80 | 0/120 | 0/160 | 0/80 |
| none, ORD, CANCEL-RETIRE | 0/155 | 20/20 | 0/150 | 0/40 | 0/140 | 0/80 | 0/120 | 0/160 | 0/80 |
| none, ORD, CANCEL-OFFSHOOT | 0/155 | 20/20 | 0/150 | 0/40 | 0/140 | 0/80 | 0/120 | 0/160 | 0/80 |
| none, ORD, CANCEL-WAIT | 58/155 | 20/20 | 0/150 | 4/40 | 0/140 | 0/80 | 0/120 | 0/160 | 0/80 |
| sole, FLOOR1, CANCEL-RETIRE | 0/155 | 20/20 | 0/150 | 0/40 | 0/140 | 0/80 | 0/120 | 0/160 | 0/80 |
| sole, FLOOR1, CANCEL-OFFSHOOT | 0/155 | 20/20 | 0/150 | 0/40 | 0/140 | 16/80 | 0/120 | 0/160 | 0/80 |
| sole, FLOOR1, CANCEL-WAIT | 30/155 | 20/20 | 0/150 | 12/40 | 0/140 | 32/80 | 0/120 | 16/160 | 0/80 |
| sole, CAP-3, CANCEL-RETIRE | 35/155 | 20/20 | 24/150 | 20/40 | 6/140 | 32/80 | 0/120 | 64/160 | 0/80 |
| sole, CAP-3, CANCEL-OFFSHOOT | 13/155 | 20/20 | 14/150 | 12/40 | 0/140 | 56/80 | 0/120 | 32/160 | 0/80 |
| sole, CAP-3, CANCEL-WAIT | 106/155 | 20/20 | 43/150 | 24/40 | 26/140 | 64/80 | 26/120 | 126/160 | 13/80 |
| sole, ORD, CANCEL-RETIRE | 69/155 | 20/20 | 62/150 | 24/40 | 4/140 | 48/80 | 0/120 | 32/160 | 0/80 |
| sole, ORD, CANCEL-OFFSHOOT | 71/155 | 20/20 | 74/150 | 32/40 | 4/140 | 80/80 | 0/120 | 32/160 | 0/80 |
| sole, ORD, CANCEL-WAIT | 98/155 | 20/20 | 62/150 | 36/40 | 4/140 | 80/80 | 0/120 | 48/160 | 0/80 |

R\* by row (R3): none, CANCEL-RETIRE: {"10": 15}; none, CANCEL-OFFSHOOT: {"10": 15}; none, CANCEL-WAIT: {"10": 15}; sole, CANCEL-RETIRE: {"10": 10, "5": 4, "4": 1}; sole, CANCEL-OFFSHOOT: {"10": 10, "5": 4, "4": 1}; sole, CANCEL-WAIT: {"10": 10, "5": 2, "4": 3}

## R\* by row, every run set

- R1, `chains`: none, CANCEL-RETIRE: {"10": 15}; none, CANCEL-OFFSHOOT: {"10": 15}; none, CANCEL-WAIT: {"10": 15}; sole, CANCEL-RETIRE: {"10": 10, "5": 2, "4": 3}; sole, CANCEL-OFFSHOOT: {"10": 10, "5": 2, "4": 3}; sole, CANCEL-WAIT: {"10": 10, "5": 1, "4": 4}
- R1, `mixed`: none, CANCEL-RETIRE: {"9": 15}; none, CANCEL-OFFSHOOT: {"9": 15}; none, CANCEL-WAIT: {"9": 15}; sole, CANCEL-RETIRE: {"9": 10, "4": 1, "3": 2, "6": 1, "5": 1}; sole, CANCEL-OFFSHOOT: {"9": 10, "4": 1, "3": 2, "5": 2}; sole, CANCEL-WAIT: {"9": 10, "4": 2, "3": 2, "5": 1}
- R1, `second`: none, CANCEL-RETIRE: {"9": 15}; none, CANCEL-OFFSHOOT: {"9": 15}; none, CANCEL-WAIT: {"9": 13, "7": 1, "6": 1}; sole, CANCEL-RETIRE: {"9": 10, "4": 3, "3": 1, "2": 1}; sole, CANCEL-OFFSHOOT: {"9": 10, "4": 1, "2": 2, "3": 2}; sole, CANCEL-WAIT: {"9": 10, "4": 1, "3": 3, "2": 1}
- R2, `fresh`: none, CANCEL-RETIRE: {"9": 15}; none, CANCEL-OFFSHOOT: {"9": 15}; none, CANCEL-WAIT: {"9": 12, "6": 1, "7": 2}; sole, CANCEL-RETIRE: {"9": 10, "4": 2, "3": 1, "5": 1, "6": 1}; sole, CANCEL-OFFSHOOT: {"9": 10, "4": 3, "3": 2}; sole, CANCEL-WAIT: {"9": 10, "4": 4, "3": 1}
- R2u, `fresh`: none, CANCEL-RETIRE: {"9": 15}; none, CANCEL-OFFSHOOT: {"9": 15}; none, CANCEL-WAIT: {"9": 15}; sole, CANCEL-RETIRE: {"9": 10, "3": 5}; sole, CANCEL-OFFSHOOT: {"9": 10, "3": 5}; sole, CANCEL-WAIT: {"9": 10, "3": 5}
- R3, `chains`: none, CANCEL-RETIRE: {"10": 15}; none, CANCEL-OFFSHOOT: {"10": 15}; none, CANCEL-WAIT: {"10": 15}; sole, CANCEL-RETIRE: {"10": 10, "5": 4, "4": 1}; sole, CANCEL-OFFSHOOT: {"10": 10, "5": 4, "4": 1}; sole, CANCEL-WAIT: {"10": 10, "5": 2, "4": 3}
- R4, `fresh`: none, CANCEL-RETIRE: {"9": 15}; none, CANCEL-OFFSHOOT: {"9": 15}; none, CANCEL-WAIT: {"9": 12, "6": 1, "7": 2}; sole, CANCEL-RETIRE: {"9": 10, "4": 2, "3": 1, "5": 1, "6": 1}; sole, CANCEL-OFFSHOOT: {"9": 10, "4": 3, "3": 2}; sole, CANCEL-WAIT: {"9": 10, "4": 4, "3": 1}

## Classes by the wider record (reported, no prediction)

- R1, `chains`: wider record against own descent {"equal": 15, "more": 75}; classes among the forms {"2": 26, "3": 28, "4": 11, "5": 8, "6": 1, "7": 7, "8": 3, "9": 3, "15": 3}; by the wider record {"2": 9, "3": 8, "4": 7, "5": 5, "6": 8, "7": 1, "8": 4, "9": 4, "10": 5, "11": 1, "12": 1, "13": 1, "16": 1, "17": 1, "21": 2, "23": 1, "25": 3, "30": 1, "32": 1, "33": 2, "34": 1, "36": 3, "37": 1, "39": 1, "41": 3, "48": 6, "58": 3, "59": 3, "61": 3}
- R1, `mixed`: wider record against own descent {"equal": 10, "more": 80}; classes among the forms {"3": 14, "4": 14, "5": 16, "6": 5, "7": 7, "8": 7, "9": 4, "10": 4, "11": 4, "13": 2, "15": 4, "17": 3, "18": 1, "19": 1, "20": 2, "21": 1, "22": 1}; by the wider record {"3": 4, "4": 5, "5": 3, "6": 4, "7": 7, "8": 5, "9": 4, "10": 3, "11": 4, "12": 6, "13": 2, "14": 2, "15": 7, "16": 1, "17": 1, "18": 1, "19": 1, "20": 1, "21": 2, "22": 1, "23": 1, "24": 3, "25": 2, "28": 1, "29": 1, "32": 1, "33": 2, "34": 1, "35": 4, "36": 3, "37": 4, "40": 3}
- R1, `second`: wider record against own descent {"more": 76, "equal": 14}; classes among the forms {"2": 1, "3": 5, "4": 12, "5": 12, "6": 9, "7": 8, "8": 3, "9": 8, "10": 5, "11": 2, "12": 4, "13": 3, "14": 2, "15": 4, "16": 3, "18": 1, "19": 1, "22": 2, "26": 1, "27": 1, "28": 2, "30": 1}; by the wider record {"3": 2, "4": 2, "5": 8, "6": 3, "7": 2, "8": 1, "9": 7, "10": 8, "11": 8, "12": 3, "13": 2, "14": 3, "15": 6, "16": 5, "17": 2, "19": 3, "20": 1, "23": 3, "24": 2, "25": 1, "26": 1, "27": 2, "29": 2, "31": 6, "32": 2, "35": 2, "36": 1, "37": 2}
- R2, `fresh`: wider record against own descent {"equal": 21, "more": 69}; classes among the forms {"2": 3, "3": 14, "4": 5, "5": 13, "6": 4, "7": 7, "8": 8, "9": 4, "10": 1, "11": 3, "12": 4, "13": 2, "14": 5, "15": 1, "16": 2, "17": 1, "18": 3, "21": 1, "22": 2, "25": 1, "27": 1, "32": 3, "33": 1, "36": 1}; by the wider record {"2": 3, "3": 6, "4": 3, "5": 3, "6": 6, "7": 3, "8": 3, "9": 3, "10": 6, "11": 4, "12": 1, "13": 2, "14": 4, "15": 3, "16": 2, "17": 2, "18": 1, "19": 5, "20": 2, "21": 1, "23": 1, "24": 3, "25": 1, "26": 1, "27": 4, "31": 2, "33": 1, "37": 2, "40": 1, "43": 2, "44": 1, "46": 3, "47": 1, "49": 2, "50": 1, "52": 1}
- R4, `fresh`: wider record against own descent {"equal": 21, "more": 69}; classes among the forms {"2": 3, "3": 14, "4": 5, "5": 13, "6": 4, "7": 7, "8": 8, "9": 4, "10": 1, "11": 3, "12": 4, "13": 2, "14": 5, "15": 1, "16": 2, "17": 1, "18": 3, "21": 1, "22": 2, "25": 1, "27": 1, "32": 3, "33": 1, "36": 1}; by the wider record {"2": 3, "3": 6, "4": 3, "5": 3, "6": 6, "7": 3, "8": 3, "9": 3, "10": 6, "11": 2, "12": 3, "13": 2, "14": 3, "15": 4, "16": 1, "17": 3, "18": 1, "19": 5, "20": 2, "21": 1, "23": 1, "24": 3, "25": 1, "26": 1, "27": 4, "31": 2, "33": 1, "37": 2, "40": 1, "43": 2, "44": 1, "46": 1, "47": 3, "49": 2, "50": 1, "52": 1}

## Start knots in the roster (PR4 and reported)

- R1 chains retiring or offshoots: a start knot a member after round 1: 0
- R1 chains retiring or offshoots: runs: 3780
- R1 chains waiting: a start knot a member after round 1: 528
- R1 chains waiting: runs: 1890
- R1 mixed retiring or offshoots: a start knot a member after round 1: 0
- R1 mixed retiring or offshoots: runs: 3060
- R1 mixed waiting: a start knot a member after round 1: 858
- R1 mixed waiting: runs: 1530
- R1 second retiring or offshoots: a start knot a member after round 1: 0
- R1 second retiring or offshoots: runs: 2280
- R1 second waiting: a start knot a member after round 1: 744
- R1 second waiting: runs: 1140
- R2 fresh retiring or offshoots: a start knot a member after round 1: 0
- R2 fresh retiring or offshoots: runs: 3660
- R2 fresh waiting: a start knot a member after round 1: 1506
- R2 fresh waiting: runs: 1830
- R2u fresh retiring or offshoots: a start knot a member after round 1: 0
- R2u fresh retiring or offshoots: runs: 3660
- R2u fresh waiting: a start knot a member after round 1: 0
- R2u fresh waiting: runs: 1830
- R3 chains retiring or offshoots: a start knot a member after round 1: 0
- R3 chains retiring or offshoots: runs: 3780
- R3 chains waiting: a start knot a member after round 1: 732
- R3 chains waiting: runs: 1890
- R4 fresh retiring or offshoots: a start knot a member after round 1: 0
- R4 fresh retiring or offshoots: runs: 3660
- R4 fresh waiting: a start knot a member after round 1: 1506
- R4 fresh waiting: runs: 1830

