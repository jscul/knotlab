# Changes from the second to the third versions, item by item of the advisor's last pass

`study/descent_advisor2/answer.md`, sections 1 to 7. "Applied" means applied as worded. Files: `note_v3.md`,
`definitions_v3.md` (DH), `preregistration_v3.md` (PR), `survey_v3.md`, `history_lines_v3.md`, `v3_data/`.

## Section 7, the twelve required items, in order

1. **Correct the hand case.** Applied; the advisor is right birth by birth. Scratch: under the barred forms the two-knot start
   under (FLOOR1, CANCEL-OFFSHOOT) gives 4 new knots, then 6 (2 joins, 4 offshoots); NEXT3-BARRED's round 2 has s = 2; the
   usable form gives 4, then 10. Written out in PR's hand case H1 and in `hand_cases.json`.
2. **HOLD gate and the two witnesses.** Applied. The HOLD gate reproduces the least-record study's sixteen holding runs
   (births by round equal on 16 of 16, no birth with parents at different parent steps) **only with that study's stopping
   reading** (a run ends at the first round that changes nothing); with the first versions' reading (end at the first round with
   no birth) two runs under FLOOR1 retiring with HOLD stop early. The definitions now take that study's reading (DH 1.1), with
   the other as a swap; it changes one census count (below). Witnesses W1 (census start 133, waiting) and W2 (census start 64,
   holding, no knot waits), in PR and the history lines.
3. **Replace P6 and "(c) exactly" with the general rule.** Applied as worded (δ, e). Scratch: the general rule gives exactly the
   wrong places on 16 runs; no parent of a retired knot retired in them, so the case of two retired holders is not exercised.
4. **The knot test's hypothesis and P10.** **Applied with a change.** The advisor's counterexample is real (FLOOR0, the cycle of
   three with one loose place each, parity: the closing knot fails) but misdiagnosed: the failure comes from the closing birth,
   not from F_B = 0. Scratch: the same knot fails under FLOOR1 and ORD, where F_B = 1, whenever DH2's step 5 gives a closing
   birth fresh distinctions (all three count forms). A birth that takes every loose distinction has its taken places forced
   even by the other knots, so any fresh place it gets is forced too. So the registered closing reading is changed to the
   former swap: under parity a closing birth receives nothing (DH 3.2 step 5), and DH2's reading becomes the swap, reported as
   failing the knot test. The hypothesis is then: every birth that is not a closing birth receives a fresh distinction (true
   where F_B ≥ 1). P10 is a check under parity with these hypotheses, through every round (after the base law's closing round
   the barred forms carry barred loose places, so no birth takes every loose distinction); under not-all-equal it is a
   replication, as the knot-test argument there is not made.
5. **The restart lemma.** Applied: "up to renaming with marks kept"; the error-count form; the three ways a structure carries two
   records; "necessary, not sufficient" with "under the laws named"; the complete-round extension limited to structures after a
   complete round. The 515, resolved from scratch: **prefix** in the engine's order (as run); sources: **the 220 kept and all 223
   give the same 515**; split: **4** are structures after a complete round 1, **511** only within round 1; with any
   parent-closed subset in place of a prefix, 1,234. "Allowed start" is in DH 10 with its swap.
6. **"By argument 1 no reached structure meets (a)" and "no knot can check (b′)".** Applied as worded, with one addition: under
   the new closing reading a structure closed by a closing birth under parity meets (a) (the cycle of three closes to four
   three-place knots of count 0); it grows no further, and H1 now has a hypothesis (d), no closing birth that would need s > 0.
7. **Extend P11; (b) against (b′).** Applied: the greatest-difference split (501/9, 502/8, 502/8, 222/1), fives (501, 502, 502,
   222; counted from the record as parent steps in fives), 155/351/400, 1,474, the six-knot 493/493/493/184, the joint stratum,
   and which starts are counted under not-all-equal (all 3,380; the counts are the same, none of the 32 set aside is counted).
   **One number differs from the advisor's and the coordinator's text:** FLOOR1 retiring with HOLD counts 369 under the
   least-record study's stopping reading, 368 under the first versions' (scratch, `v3_hold.py`); the third versions say 369
   with the other in a note.
8. **P8.** Applied: its hypotheses; the three-stage comparison (equal names; the exact test on at most 300 knots; the signature,
   labelled). Scratch: equal names in 57 of 57 tests. The hand-in clause carries "(a), (c) and (d) through round 1" and is
   called deliberate for the barred forms; "6 × 11" replaced by "6 starts × 7 RELEASE bases × 3 forms = 126" (scratch: the rule
   wrong at every old parent place from the new knot's side, right from the parent's side, 126 of 126).
9. **The search's coverage.** Applied: 40 knots (the run that finished used 40; the first launch at 60 was stopped), 148 of 173
   in the 26 finished cases, biased upward, a signature match in 68 of 68 tests, FILLERS and closing as following from the
   definition, labelled scratch and unchecked.
10. **Ten against eleven.** Resolved: **ten** lone-knot cases (ORD 3, CAP-3 2, RATION-3 1, RATION-4 1, FLOOR1, FLOOR0,
    ONE-FEWER 1 each). The "11" and "44 items" of the second pre-registration were the drafter's miscount; part 3 has 40 items.
11. **The owner sentences, the corrected sentence and the P9 wording.** Applied as written, with "369" in place of "368" (item
    7) and the advisor's additions to sentence 3 and 5.
12. **The period formula's hypotheses; P9.** Applied: q common to the members and their parent steps agreeing counted in threes
    (DH 6.4 defines q through the renaming found); P9 a replication with the hypotheses checked.

## Optional items

- The error-count form of the lemma: applied (note). The joint stratum: applied (PR P11). The word list: applied (below).
  "Allowed start" in DH 10: applied. The note on the step 5 swap: applied, and now the swap is the old reading (item 4).

## Sections 1 to 6, the other points

- **1.** "Recovers the parents on every structure reached" read as every structure of the listed runs, each stamped from its
  own start: applied (note). "Without a stamp, no claim pooled over the census can hold at any d": applied, with "admitting
  structures within round 1" (the 4 after a complete round 1 are the only ones in a complete-round population).
- **2.** A join's parents in one piece: applied. (c) automatic for the place-count forms: applied. The H3 additions (grows on
  where the base law closes; shortness on usable places, checked on members holding barred places): applied (PR part 0 (f)).
- **3.** "Not of that law on other starts": applied. P9 stays "Fails", its stated limit met off the registered runs: applied.
  P1 is a RELEASE statement: applied. The greatest-difference caveat, the witnesses, the numbers in place of "many": applied.
- **4.** 0c's wording, part 3 computed on each run's own record, M2's denominators from part 1: applied. "Nothing to cut":
  agreed; the run is re-timed at about 25 minutes on 6 processes.
- **5.** The third sense of "recovers" replaced; "nothing but the ration uses it; no birth depends on the comparison": applied,
  and "a knot can compare" removed (no knot does). "Reads": the bar in DH 0.6 is kept and every use for a rule replaced by
  "uses" (import of modules is "without changing them"). "Value" kept for the stamp ("the numbers a", "keep their count in
  threes"). "Holds" in new senses replaced ("carries two records", "contains every start knot"). "Made a knot of fewer than
  three places" removed. "'Made' is closed by argument 1" reworded ("ruled out by argument 1"). No "most" or "many" without a
  number. The step 3 swap stated as cyclic; q defined; "one round past" defined (through R and again through R + 1); subset or
  prefix stated (DH 5.5).
- **6.** The owner sentences: applied, with the report's first bullet in the advisor's wording.

## Found wrong in the advisor's answer

- **Section 2, the knot test**: "true where F_B ≥ 1" is not enough at a closing birth: under DH2's step 5 the closing knot fails
  the parity test with F_B = 1 as well (scratch, `v3_checks.py`, the cycle of three, FLOOR1 and ORD, all three forms). The fix
  is the closing reading, as in item 4.
- **Section 3, the corrected sentence and the P9 wording**: right, with 369 for FLOOR1 retiring with HOLD under the least-record
  study's own stopping reading (item 7). Nothing else found wrong; the advisor's two counterexamples and its correction of the
  hand case were checked in scratch and stand.
