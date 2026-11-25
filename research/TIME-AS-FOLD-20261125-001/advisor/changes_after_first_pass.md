# Version 2 against the advisor's cold review

Every item of sections 1 to 14 of the review (`study/timefold_advisor/answer.md`), in its order, with what version 2 does.
"Done" names where; "checked" says how the drafter tested the advisor's argument before adopting it (the advisor ran
nothing); a disagreement gives its counterexample. Files: `claim_v2.md`, `definitions_v2.md` (TD), `preregistration_v2.md`
(PR), `survey_v2.md`, `v2_data/starts.json`, `v2_data/rules.json`, `v2_data/compare.json`. Scripts: `v2/tf2.py` and
`v2/k*.py`, outputs in `v2/out/`. Where removing met a requirement as well as adding, the smaller text was kept; those
places are marked **(smaller)**.

## 1. The claim

| Item | Verdict |
| --- | --- |
| C implies C-ii once "knots made" is a count; "a positive for C would not show that the pattern holds the number of ticks" is wrong | Done: claim §5 (the count is recoverable from X's own knots, so X is a counting pattern) and §6 (what a positive would show, corrected). |
| C-ii's three counts are ad hoc | Done **(smaller)**: the three counts are removed; the one count is X's own knots (claim §3, TD 3.4, 5.3). |
| C is the stop, merged with C-ii; C-iii beside it | Done: claim §5. The stop's wording is said to be the thread's (claim, "The question"). |
| Count only births with no parent among Y's part and its descendants | Done: own knots (TD 3.4); joint knots reported apart. Checked: in the two-knot cases X makes no joint knot (4 own knots a round and 0 joint in the near case, 3 and 0 in the C-iii case), so the change leaves them as they were and closes the route the advisor names. |
| Allow a stated lag | Done: up to two periods (claim §5 clause 2, TD 5.2), reported for each r. |
| Require rounds read after the bar | Done: two periods read after the lag, run A making own knots there; 18 rounds; otherwise undecided (TD 4.6, 5.2). |
| The claim as the advisor states it | Adopted, with "own knots" for "knots with no parent among Y's", and the numbering clause defined (TD 5.4). |
| The supplied-rounds limit and the conditional waiting test | Done: claim §6; PR run 8, conditional on a candidate. Not run: no candidate exists. |
| "Ruled out by the treatment" under CANCEL-OFFSHOOT, not-all-equal, no FILLERS | Done: claim §5, PR settled 3. Checked on the prototype: 2,043 rounds of that treatment, no member without a birth and no birth that is not a member. |

## 2. The law

| Item | Verdict |
| --- | --- |
| L1 and L2 with all four choices; "cheapest with a confirmed case under each ration" | Done: claim §2. Checked against FD 3.3's vector: MET (2, 0, no, the choice) is no costlier than STEPS-1 (2, 1, no, the choice) in any component. |
| The four-component extras need verdicts, not primary rank | Done: claim §2; they are in the census (PR table) and each gets a verdict there. |
| The primary verdict is known before the freeze; cheapest for meeting, not returning; the informative arm is the second | Done: claim §2, PR "Known before the freeze". |
| L1's negative rests on the fresh count by distinct inputs; swap fresh by parents over the whole census | Done and run: the census's group "fbp" (8,736 runs). Checked: under that swap 107,803 of 110,291 births under STEPS-1 gain a usable loose distinction. L1's verdict survives the swap (no clock giving parts off at four ticks), but its reason does not (the bound is exceeded in 2 runs, and a series gives parts off at two ticks in 6), and the class does not (Q has such a clock in 10 runs). |

## 3. Settled by construction

| Item | Verdict |
| --- | --- |
| (a) P2's argument garbled; the candidate is any other place of g's parent | Done: PR settled 2(a), the advisor's argument. Checked by hand (it needs only two places of the parent, of which g holds one) and on the prototype (under not-all-equal an offshoot of a made knot that did not take would gain a usable loose distinction, and none does under STEPS-1, MET, Q or UP-TO-2 in 10 rounds on the twelve starts; the next row). |
| (a) "No part with a member holding two or three is made after round 1" is false | Agreed and removed. Checked: the advisor's counterexample exists, though not on the twelve registered starts (where it held in all 10,359 knots of the first draft). Found on the ring study's start with atlas index 17, loose counts (0, 1, 1, 2), stars [[0,1,2],[0,3,5],[1,3,4,6],[2,4,7,8]]: under COPY-LAW(CANCEL-WAIT) a start knot waits and makes an offshoot holding two in round 2. Recorded in PR "Known before the freeze", item 8. |
| (a) Use the count argument | Done: PR settled 2, claim §7, with its class and its scaffold. Checked by hand (the step from rises to ticks needs that each start knot acts in one round under release, which bounds the ticks by the rounds in which start knots act) and on the prototype: no birth outside start knots' offshoots gains a usable loose distinction (0 of 8,004, 5,568, 4,924, 8,294 births under STEPS-1, MET, Q, UP-TO-2, not-all-equal; 0 under parity); no run of the class in the census exceeds the bound, and none of its series gives parts off at any tick. Outside the class it fails as it should: under STEPS-2, 1,440 of 12,677 births gain one. |
| (b) Only round 1 can be argued; name the second mechanism | Done: PR settled 7, claim §7. **Partial disagreement, checked**: the advisor's premise "a round's births equal the control's" holds for parents and loose inputs only. On Ring(5,3) every choice: the control's joins receive 3 fresh and offshoots 2; under MET joins receive 2 and offshoots 3. On Ring(7,3) and Ring(9,3) every MET birth receives 3, and in round 2 14 and 18 members are short against the control's 7 and 9. The union-of-parts conclusion still holds after round 1 (parts after round 1: [10], [14], [18] in both). The fresh-count difference is the advisor's own "a taker's fresh count changes", already in round 1. |
| (c) Qualify by RELEASE and the treatment; HOLD, FILLERS, IMPLIED exceptions | Done: PR settled 3 and TD 5.2 (the way: ended, all members wait, closed). |
| Settled 4 wrong: a knot can descend from both X and Y | Agreed. Done: PR settled 4 (corrected), TD 4.1 (X's descendants never barred; how many are in the barred part is reported). On the prototype's paired test, see section 8 below for how often it happens. |
| (d) What D argues and what it does not | Done: PR settled 5 and P7, in the advisor's terms; the false parts named with their counts (BY-COUNT 22 runs, NEWEST 4). |

## 4. The reason arm

| Item | Verdict |
| --- | --- |
| (a) extends to the class | Done: PR settled 2, claim §7, with MET's offshoot clause alone added to the class (it satisfies the class's condition; checked in the census: none of its series gives parts off). |
| No argument under CAP-3 | Stated: claim §7 ("Under L2: seen, not argued"). |
| The reason arm is about offshoot-taking laws; join-taking laws are the open case | Done: claim §7, survey §5.5. Checked: under MET's join clause alone a clock giving parts off at four ticks in 184 of 288 runs under FLOOR1 and 64 of 384 under the cap of three. |
| The tension in two forms, not an impossibility | Done: claim §7. |

## 5. D

| Item | Verdict |
| --- | --- |
| "Exactly k" not honest; restate; two parts; the first 2k rounds are no evidence | Done: claim §7 (the advisor's sentence, with the reason for round 2k + 1 added, and a third clause for k = 1 below), PR settled 5 and P7. Checked over k = 1 to 8 (448 runs, 4 stopped by the guard): the universal clause holds in every run that finished. "Exactly k" needs a further limit the advisor did not name: for k = 1 the ring never comes back under any choice (56 runs; the parts given off take from round k + 1 = 2, the round of the first return). For k ≥ 2 it holds in all 96 finished runs under OLDEST and all 96 under IN-TURN; NEWEST: 94 of 98, a later return after a gap in 4; BY-COUNT: 76 of 98, fewer in 22. The first draft's counts (and the advisor's "22" and "4") stand; its "all 210 runs" under OLDEST and IN-TURN counted k = 1 wrongly as "exactly k" and is corrected. The words "depth", "window" and "shallower" are gone. |

## 6. The second arm

| Item | Verdict |
| --- | --- |
| STEPS-k for offshoots of offshoots is fitted; register as a fitted control | Done: TD 1.4, `rules.json` ("fitted control, added by hand after the census"). |
| MET's join clause alone is a fair candidate, also chosen after the census | Done: same places. |
| Register the whole family beforehand | Done: `rules.json` (22 entries: the control, 5 fold rules, the ladder STEPS-1 to STEPS-8, MET's two clauses alone, STEPS-k for offshoots of joins and of offshoots for k = 1, 2, 3). **Disagreement, by construction**: "STEPS-k applied to offshoots of start knots" takes nothing (a start knot has no ancestor), so of the advisor's seven combinations per k only three are distinct (offshoots of joins, of offshoots, of both = STEPS-k); PR settled 6. MET with neither clause is the control. The sub-family registered is k = 1, 2, 3 for the parent-kind rules, stated as a sub-family. |
| A cost component "kinds of birth told apart" | Done as "classes of birth distinguished" (1, 2 or 3; TD 1.4, `rules.json`): "told" is one of the decided words not used. |
| A positive under a fitted rule is "the law supplied what spares the clock"; needs a start outside the ring family and every numbering | Done: PR "What a result would and would not show". |
| Run 4 names two undefined rules | Done **(smaller)**: "offshoot-of-offshoot MET" is dropped (it was never defined and nothing needs it); STEPS-1 in run 4 is FD's STEPS-1. |

## 7. The near case

| Item | Verdict |
| --- | --- |
| "X reads Y and Y does not read X" not sound; with X barred Y's period is 1 round | Agreed and checked: with the part of four barred at round 4, the one-member part returns at every round 4 to 18 (`v2/out/k1_checks.txt`, (F)). Removed. |
| A one-member part's return is the endless chain | Agreed: TD 2.5, claim §3. The near case is no case under v2 **(demoted)**. |
| The meeting goes through a start distinction OLDEST selects by name | Agreed and checked: over all 240 numberings of the two-knot start (5,760 runs), the near case passes the test in 112, exactly those in which the shared start distinction is the least-named place of at least one start knot. |
| IN-TURN equals OLDEST wherever a parent makes one offshoot | Checked: under MET's join clause alone the two give the same series in all 168 comparisons of the census, so that rule has three choices (TD 1.4); under STEPS-1 they differ in 32 of 166, so the two choices are not one there. |
| The honest sentence | Adopted with one **disagreement, checked**: "the case is gone under the other numbering" is not what the numberings show. It is gone under 128 of the 240 and present under 112; the sentence now says so (claim §8). |
| Every numbering first; ALL-CHOICES bounded and labelled "history picked" | Done for the two-knot start (every numbering run before any choice of take was enumerated; TD 5.4 labels a picked history). ALL-CHOICES was not run. Also found by running every numbering: the C-iii case with three-member parts (reading each other) passes in 80 of the 240, those in which the shared distinction is the least-named place of the start knot listed second. |

## 8. The paired test

| Item | Verdict |
| --- | --- |
| It tests dependence on Y being there in each of three periods | Done: TD 4.7. |
| X's descendants inside the barred part | Done: never barred (TD 4.1); counted. On the prototype's paired test (12,901 tests on 3,086 runs) it occurred in no test: the route is real by construction but did not arise. |
| Round-wide triggers | Kept as a reported "way" (TD 5.2, 6.2). |
| A comparison cut short is undecided | Done: TD 4.6. It matters: 44,931 of 79,687 comparisons in the prototype are undecided, most under the laws that keep the copier (9,218 of 14,328 under MET's join clause alone with FLOOR1), so "no C-iii found" there mostly means "not read". |
| The one-period limit is too short; two periods; report the lag per r | Done: TD 5.2 and C-iii's "within two periods"; lags recorded per r. |
| The parts given off earlier are not barred | Kept as stated; B′(r) separates the latest tick's parts. Not added: a bar on every earlier part given off (it would bar most of the roster under the copier). |
| Add B′(r) | Done: TD 4.2; run. It separates the two readings: under STEPS-2 for offshoots of offshoots with the cap of three, 24 tests in 8 runs change X's course under B′(r) at all three bars and not under B(r) (X reads the parts given off, not the clock); in the one-way case under STEPS-2 for offshoots of joins with CANCEL-WAIT both change it. |
| A third masked-run class | **Not added (smaller)**: it is not a few lines (it needs a mask on common-knot status and on eligibility, both inside the take step). A difference the mask does not reproduce is reported as "unconfirmed" with the two kinds it could be named (TD 4.4). In the prototype there are 144 such differences, all under STEPS-2 (96) and STEPS-3 for offshoots of joins (48) with FLOOR1. |
| Define the mask for knots descended from both | Done: TD 4.4 (such a knot is on both sides and joinable with no member of either). |

## 9. The definitions

| Item | Verdict |
| --- | --- |
| "Past its start" filters wrongly under taking; report both | Done: TD 2.2; every census count both ways (PR table). Checked: under L1 the filter turns 46 runs with a clock into 0. |
| "The same" does not carry a direct meeting | Done: said, and every return reports its direct meetings (TD 2.3). |
| "Has a member made after round s"; t_r against s | Done: TD 2.3; the claim uses t_j, the definitions s, with the relation stated. |
| Least-name convention; record every qualifying part; bar all | Done: TD 2.3 (every qualifying part recorded), 4.3 (Ball(r)), the swap to the greatest name registered (PR run 1). Run in part (`v2/k8_convention.py`, stopped after 2,338 runs: the control on every start, every law on six ring starts under not-all-equal): the greatest-name convention changes the series of two or more members in 7 runs and the verdict on a clock giving parts off in none. |
| Require equal periods | Done: TD 2.6. |
| Mixed parts given off | Done: TD 2.7 (counted, labelled "mixed"). |
| X's origin not exhaustive | Done: three yes/no facts (TD 3.3). |
| One set of births for each use | Done: own knots for the ratio, the count and ceasing; FD's trace for C-iii (TD 3.4). |
| Add "knots made"; read in B(r) at run A's rounds | Done: TD 5.3. |
| "Ceases" vacuous for r = 3 at 12 rounds; 18 rounds | Done: 18 rounds; undecided otherwise. |
| Renaming: knot order too; define "survives"; BY-COUNT's tie order uses names | Done: TD 5.4 (numbering = order of distinctions and of knots; "survives"); TD 1.5 (every choice depends on the numbering). Registered: every numbering of a start of at most six distinctions (the two-knot start, 240), and for larger starts the 4n numberings made of the n rotations of the order of distinctions, each as given or reversed, with the knots as given or reversed. "Every numbering on the small starts" was not adopted beyond six distinctions: the three-knot start has 8, and 8! × 3! = 241,920 numberings per law. The rotation family puts each distinction once in the least-named place, which is what OLDEST and BY-COUNT read first; whether it is enough is put to the advisor (PR, open question 3). |
| MET(IN-TURN) on joins is OLDEST | Done and checked (section 7 above). |
| STEPS-k ranges disagree | Done: one statement (the ladder k = 1 to 8; the family k = 1, 2, 3; STEPS-1 and STEPS-2 as fold rules), TD 1. |
| The fold guard is cited, not given | Done: its text in TD 1.7. |
| The stop is misquoted; the filed stop has no "the reader" | **Disagreement, checked**: the filed stop does contain "with the reader and the law's choice said plainly to be supplied or made" (`tickets/TIME-AS-FOLD-20261125-001.json`, its objective; `docs/RESEARCH_GOALS.md` line 2690). The quotation is kept, exact. The thread's claim C drops "the reader", and the survey says why (§0). |

## 10. The predictions

| Item | Verdict |
| --- | --- |
| Mark what is true by construction, what replicates the prototype, what was seen for r = 0 only | Done: marks (t), (p), (r0), (b), (c) in PR. |
| P5 and P6 not decidable at 12 rounds; P6's "exactly" is (b); P8 seen only for r = 0 | Done: 18 rounds; P6 restated as a structural clause; the r = 0 reading replaced by r = 1, 2, 3. |
| Over-pinned P9, P6, P3, P0 | Done: every prediction is a structural clause plus exact numbers in `compare.json`, compared and replayed on disagreement (PR, "Predictions"). P0's altered copies are checked by brute force (G3). |
| The advisor expects P6's "exactly", a clause of P9 and P11 to fail | Noted. P6's "exactly" is gone. |
| Missing: the gate on taking rules | Done: G2; run on the prototype (1,134 runs, 9,862 rounds, 0 mismatches; trivially, the same engine). |
| Missing: the 227 | Done: G1 and run 2; regenerated from the ring study's public code, count reproduced exactly (227 of 86,032 after 316 set aside). |
| Missing: scaffold swaps on the census | Done: fresh by parents and demand before the takes run on the census; "past its start" read both ways; the convention swap registered (not run). |
| Missing: the knot test for k > 4 and at every round of comparison runs under parity | Done: TD 7, PR run 7. Run: k = 1 to 8 (2,855,335 verdicts) and the near case's 18 comparison runs at every round under both knot laws (13,118), none failing. Not run on the census's comparison runs. |
| Missing: masked runs are not growths under the law | Done: TD 4.4, PR P14. |
| Missing: a prediction for the reverse test | Done: P10 (the test with X barred). |

## 11. Scope and honesty

| Item | Verdict |
| --- | --- |
| What a positive would and would not show | Done: claim §6, PR. |
| The expected result and what it does not show | Done: PR. |
| The plain sentence for the owner | Adopted, corrected by the checks: "it rests on the numbering" became "it appears under 80 of the 240 numberings of its start and not the others" (PR). |
| Blurring: "keeps time with", "falls out of step", "yet" | Removed. |
| "The least demanding fold in the owner's sense"; "the owner's stop", "the owner's word" | Removed; only the question is attributed to the owner (claim, "The question"). |
| The one-member part called a clock | Removed (TD 2.5). |
| "In most combinations", "few and mostly" without counts | Removed; counts are given (survey §5, PR). |

## 12. Words

| Row | Verdict |
| --- | --- |
| series of returns | Done everywhere. |
| the second part; at a fixed ratio (the thread's) | Kept, attributed. |
| ceases | Dropped as a term: "makes no further own knot" with the way (TD 5.2). The quotation of the filed stop keeps "cease", as quoted. |
| Y barred after its r-th tick | Done. |
| the test with X barred | Done. |
| MET's join clause alone; STEPS-k for offshoots of offshoots (added by hand after the census) | Done. |
| line; dormant | Not used (TD 0); P14's "dormant" is gone. |
| depth, window, shallower | Removed: "the ladder under STEPS-k", "the first 2k rounds". |

## 13. The nine open questions

All nine answers are applied as in the items above (1: section 2; 2 and 3: section 1; 4: section 6; 5: section 5; 6:
section 7; 7: section 9, the convention; 8: section 10, the 227, with A238's weighting named; 9: section 12).

## 14. The fourteen required changes

| # | Done where |
| --- | --- |
| 1 | 18 rounds; undecided comparisons (TD 4.6). |
| 2 | X's descendants never barred; own and joint knots (TD 3.4, 4.1). |
| 3 | Claim §5, §6. |
| 4 | TD 2.2, 2.5; PR table. |
| 5 | TD 4.5; claim §8; P10. |
| 6 | Census group "fbp"; claim §7 and PR settled 2. |
| 7 | PR settled 2, 3, 4. |
| 8 | Claim §7; P7. |
| 9 | TD 1.4; `rules.json`; the undefined rule dropped. |
| 10 | TD 4.2, 5.2. |
| 11 | TD 5.4; every numbering of the two-knot start run. |
| 12 | G2; TD 7; PR run 7. |
| 13 | PR predictions; the quotation kept exact (a disagreement, section 9); the attributions to the owner fixed. |
| 14 | Section 12. |

Optional: the conditional waiting test is registered (run 8), not run (no candidate); the 227 are run under L2 (1,815
runs, 1 unread; no clock giving parts off); a third masked-run class is not added (section 8); a bar on every copy is
added (Ball(r)) and run.
