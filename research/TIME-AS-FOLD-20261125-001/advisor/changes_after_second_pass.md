# Version 3 against the advisor's second review

One line per item of `study/timefold_advisor2/answer.md`: **applied as worded**, **applied with this change**, or **not
applied**, with why. Files: `claim_v3.md`, `definitions_v3.md` (TD), `preregistration_v3.md` (PR), `survey_v3.md` (it
changes: words, and its findings brought to the new rule for verdicts), `v3_data/` (`starts.json` unchanged;
`rules.json`, `compare.json` and the new `numberings_5b.json`). No growth run was made for version 3. Two reanalyses
read the prototype's existing output (`v2/k12_verdicts_b2.py`, `v2/out/k13_shift_distinct.json`), and one check read
the census rows (copies under the laws of the count). The draw of run 5b's list (`v3/gen_5b.py`) is not a growth run.

## 1. Blockers

- **B1** (ladder knot bound): applied as worded. TD 1.7 now says 6,000.
- **B2** (rule for "decided"): applied with one addition. B2's text says when C-iii fails and when C holds, but not when
  C-iii holds. TD 4.6 adds: "it holds when, for every r, X's trace differs within two periods of the bar, through a meeting
  (a difference seen is decided as seen)". The run 4 second pass is applied as worded. The prototype's paired test was
  re-scored under the new rule from its saved output (`v2/k12_verdicts_b2.py`):
  - C: failed in all 12,901 tests (9,775 by clause 1, 3,126 by an own knot after the lag), held in none, undecided in none.
  - C-iii: held in 44, failed in 12,825, undecided in 32. The 32 are all unconfirmed differences under STEPS-2 with FLOOR1.
  - The v2 count of 44,931 undecided comparisons is removed.
- **B3** ("ruled out by the treatment"): applied as worded in the claim §5 and PR item 3. P5 is marked (t) for that case
  only. From the saved output: 3,403 of the 3,443 tests under (CANCEL-OFFSHOOT, not-all-equal) make no joint knot after the
  bar. In the other 40 (STEPS-2 and STEPS-3 for offshoots of joins) X still makes own knots in every round after each bar.
- **B4** (the count with a lag): applied as worded: clause 2's e, TD 5.3's (number − e)/c, and clause 1's four periods
  from t_j to t_{j+4}. The claim also says that the own knots number c·r + e.
- **B5** ("each clock form"): applied as worded in run 4. The PR's disclosure now states the prototype's own grouping
  exactly: the same four periods from its first qualifying j and the same parity of that round. This differs slightly
  from run 4's "the same periods".
- **B6** (limit and `compare.json`): applied as worded (TD 1.7, PR header, Runs, Predictions, Resources, and
  `compare.json`'s "about"). The changes for numbers from runs cut short:
  - The PR now says the prototype's limits were wall time (60 seconds a census run, 600 seconds for all the tests of one
    run), and that its counts are over the runs it finished.
  - The undecided counts leave the exact comparison.
  - The two-knot rows of `v2/k9_numberings_cases.py` (cut at 600 seconds) and the convention swap (cut by hand) are
    marked "not compared".
- **B7** (P4): applied as worded.
- **B8** ("Neither survives"): applied as worded in claim §8 and PR question 3. P16's numbering clause is marked (b).
  Survey §5.6 is changed the same way.
- **B9** (L1 heading): applied as worded.
- **B10** (copies against SD line 87): applied as worded in TD 2.7, PR item 2(d) and (e), and P2. Checked on the census
  rows (main group and demand taken before the takes): under the laws of the count no series has a tick with two or more
  qualifying parts, and the bound counting copies is never exceeded.
- **B11** (run 5b; TD 6.3): applied as worded, with the list written as data (section "Coordinator" below).
- **B12** (run 8): applied as worded in the PR's run 8 and the claim §6.
- **B13** (a law's verdict): applied as worded in the PR's stop rule.
- **Smaller, TD 8** ("m′ = 4 periods"): applied as worded ("four periods").
- **Smaller, P11**: applied. P11 is marked (b), and its text says it was seen at 8 rounds on the primary laws.

## 2. The fourteen required changes

- Rows 1, 2, 3, 7, 9, 11, 13 and 14: their remaining defects are B2, B3, B4, item 2(a) for Q (section 7), B5, B11, the
  marks of P11 and P16, and section 10. All are applied as above and below.
- Rows 4, 5, 6, 8, 10 and 12: no change needed.

## 3. Disagreements

- The count rests on the fresh count by distinct inputs; under the swap L1 is "seen, not argued", like L2: applied as
  worded (claim §7, PR, survey §5.2).
- L2, round 1: nothing to apply. The PR's item 7 now gives the advisor's reason: groups and shortness are fixed before the
  takes, and the parts have the same members.
- Three members for each k, for STEPS-k only: applied (TD 1.4, PR item 6). The cost sentence is corrected as worded: no
  "one more parent step", only the new component. `rules.json` now gives STEPS-k for offshoots of joins and of offshoots
  record steps k, not k + 1.
- "Kinds of birth treated differently": applied as worded (TD 1.4, the claim §2, `rules.json`'s key
  `kinds_of_birth_treated_differently`).
- The quotation of the stop, "gone under the other numbering", "exactly k" needs k ≥ 2, and no third masked run: nothing
  to apply.

## 4. The numberings

- Sound as a refutation, not as a confirmation: applied (PR "What a result would and would not show", and question 3's
  answer).
- What passing the 4n shows and does not show: kept as the advisor's reasoning behind B11. Not copied into the files.
- How many of the 4n differ up to the start's own symmetries: applied and computed (`v2/out/k13_shift_distinct.json`;
  TD 5.4 registers the report).
  - All 4n differ on every named start of more than six distinctions and on every one of the 227.
  - The two-knot start's 20 shifts are 10 named starts, and its 240 numberings are 30 named starts, each from 8
    numberings. This agrees with the advisor's "no symmetry of a start fixes a numbering".
- A case must pass all to answer "the growth"; one failing is "under a supplied numbering", with the condition on names:
  applied (TD 6.3, PR).
- "80 of 240" as "one third, each numbering weighted once", with the condition on names beside it: applied (claim §8,
  PR, P6, the plain statement, survey §5.6).
- "44 of 112" as "fails under at least one registered numbering; passes 44 of the 112 run": applied (claim §8, PR, P15).
- The paragraph on the sister study: not applied here, as the coordinator asked. Two survey-result lines in the PR's
  prior work still name its epic ID as a search returned it, without comment.

## 5. Undecided comparisons

- Verdicts per test, failures decided as seen, r = 1 first, a second pass only for tests with no failure: applied (TD
  4.6, run 4).
- No change to which pairs are tested, and no pruning: applied (none made).
- The result gives tests, failed, held and undecided per law: applied (PR "Engine and stop rule"). `compare.json` has
  the prototype's table under "verdicts_td46".
- "Or none is" becomes "or none is among the decided": applied with this change. The words "or none is" are in the PR's
  own stop rule (b), not in the filed stop, which has no such words. The PR's rule (b) now reads "or none is among the
  decided". Beside the unchanged quotation of the filed stop (claim, "The question"; PR, "The question") the reading is
  stated: a law with undecided tests gives "none among n decided, m undecided", never "none". `owner_request.md` is not
  touched.

## 6. The claim

- C tests "makes a pattern of its own" only as c own knots per tick: applied (claim §6, "would not show"; PR).
- Clause 1 is weak: applied (claim §6), with the two-knot case's 6 own knots a period as the example.
- "At each of three returns" where a result is stated: applied (claim §5's C-iii heading and §8, PR, survey, the plain
  statement).
- The expected end reaches neither part of the filed stop: applied (claim §7, last bullet; PR).

## 7. The reason arm

- The exact hypotheses of the count: applied as "the laws of the count" (claim §7, PR item 2).
- "Under Q the candidate is the place g took from q": applied as worded. PR item 2(a) now gives the MET/STEPS-1/UP-TO-k
  argument and the Q sentence separately, since g's own take under Q is a place of q.
- "For STEPS-k the bound is the number of acting knots with no ancestor k parent steps above them": applied as worded
  (claim §7, PR item 2, P2). The PR's statement that the 1,440 births under STEPS-2 that gain one are all of that kind
  rests on the argument. They were not checked birth by birth, and the PR says so.
- The two replacement sentences (the head and the last sentence of the tension bullet): applied as worded (claim §7).

## 8. The three corrections

- D for k = 1, and 112 and 80: nothing to apply. The advisor's counts agree with the files.
- "An offshoot": applied (PR reading 8, with the advisor's hand check of knot [0,3,5]).

## 9. The plain sentence

- Sentence 1: applied as worded.
- Sentence 2: applied with one change: "a part's number of loose distinctions does not rise" became "once the start knots
  have acted a part's number of loose distinctions does not rise". An offshoot of a start knot receives two, and the
  count's bound is the number of start knots acting, not zero.
- Sentence 4: applied as worded.
- Sentence 6: applied as worded, with its opening filled as "Under a law that takes from an ancestor two parent steps
  above,", to keep "look … back" out.
- Sentence 7: applied with one change. The case under STEPS-2 for offshoots of joins with COPY-LAW(CANCEL-WAIT) is not
  ruled out by the treatment, since waiting does not force a birth every round. There C fails at clause 1 because X's own
  knots grow (7, 15, 32, 74). The sentence reads "either the treatment rules a count out or the reading part's births
  grow each period, so there is no fixed ratio".
- Sentences 3, 5 and 8 are kept, with section 4's "one third, each weighted once" and section 6's "at each of three
  returns" in sentence 5.

## 10. Words

Every row was searched for in all four files and `rules.json`, and applied.
- "open" → "undecided": the claim §7, the PR mark (c), TD 0 ("nothing left undecided"). The heading is now "Questions for
  the advisor, with its answers".
- "rules ceasing out" → "rules out 'makes no further own knot'" (PR, survey).
- "comes back" → "the start's roster returns" (claim §7, PR ladder, P4, P7, survey).
- "read names" → "use names" (TD 1.5, 5.4).
- "runs read 18 rounds" → "runs are grown through 18 rounds" (TD 1.7, 4.6). The same change was made to "both runs are
  read through", "rounds read" and, beyond the table, "series read with/without" → "taken with/without", per TD 0's rule
  that studies "use", "look at" or "check".
- "unread" → "unfinished"; runs "stopped" → "cut short". The quotation of the filed stop keeps "stopped", and SD's own
  sense is kept where named.
- "the way" → "which of the three (ended, all members wait, closed)" (TD 5.2, PR Words, survey). TD 0 keeps FD 5.5's
  "way" as FD's.
- "one way" and "the one-way case" → "X reads Y and Y's series is unchanged with X barred". The literature's "one-way
  entrainment" became "the entrainment of one oscillator by another".
- "the fold study", "fold engine", "fold guard" → "the study of parts that meet again", "its engine", "its guard".
  `rules.json`'s arms "fold rule(s)" became "rule(s) of the study of parts that meet again". The scratch file name
  `v2/k10_rotations.py` is kept as a file name.
- "L1's class" → "the laws of the count".
- "classes of birth distinguished" → "kinds of birth treated differently".
- "rotations" → "shifts of the order of distinctions"; the key in `compare.json` is "shifts".
- "full horizon" → "full number of rounds".
- "inside the first 2k rounds" → "within".
- "most survive" → "28 of 30 pass". Checked: 28 of the 30 STEPS-2 laws and starts pass all four; the two on Ring(5,4)
  with BY-COUNT pass 2.
- "look … back" in the owner sentence → as in section 9.

## 11. Verdict

- Freeze: the fixes of sections 1, 9 and 10 and the replacement sentences of section 7 are applied as above.

## Coordinator's items not in the answer

- **Run 5b's list** (`v3_data/numberings_5b.json`, `v3/gen_5b.py`):
  - 200 numberings for each registered start of more than six distinctions: the 11 named ones and all 227, 238 starts,
    3.5 MB.
  - Each numbering is a pair of orders. Each order sorts its items by the SHA-256 digest of
    "<seed>|<start>|<draw>|d or k|<item>". The seed is "TIME-AS-FOLD-20261125-001A run 5b, drawn 2026-11-24".
  - A draw equal to one of the start's 4n shifts, or to an earlier kept draw, is refused; none was refused.
  - Each numbering is weighted once. Redrawing gives the same file byte for byte (checked twice).
  - The PR states the procedure in full.
- **`compare.json`'s role**: restated as the advisor words it (its "about" and the PR's header and predictions).
