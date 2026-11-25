# Changes from version 2 to version 3

For the thread. The advisor's second pass is `study/copier_advisor2/answer.md` ("A2 n" below is its section n); the
thread's thirteen decisions on it are "decision n". Each item of A2 sections 1 to 8 is listed as done, or why not. I
checked every statement of A2 before adopting it, by reading the fold engine or by a scratch run; where I disagree I say
so and give the counterexample. Where removing or demoting met a requirement as well as adding, I took the smaller text
and say so ("smaller").

## Files

Written in the scratch folder under the names below; each will go in the repository under the name in brackets.
Versions 1 and 2 are left in place.

| Scratch file | Repository name |
| --- | --- |
| `claim_v3.md` | `research/MADE-COPIER-20261125-001/claim.md` |
| `definitions_v3.md` | `research/MADE-COPIER-20261125-001/definitions.md` |
| `survey_v3.md` | `research/MADE-COPIER-20261125-001/survey.md` |
| `owner_arm_v3.md` | `research/MADE-COPIER-20261125-001/owner_arm.md` (replaces `arm_owner_inkling.md`) |
| `preregistration_v3.md` | `research/MADE-COPIER-20261125-001A/preregistration.md` |
| `take_lists_v3.json` | `research/MADE-COPIER-20261125-001A/take_lists.json` |
| `starts_v3.json` | `research/MADE-COPIER-20261125-001A/starts.json` |
| `record_structures_v3.json` | `research/MADE-COPIER-20261125-001A/record_structures.json` |

New scratch code: `v3_arm.py`, `v3_checks.py`, `v3_record.py`, `v3_starts.py`; outputs in `out/v3_*.json*`,
`out/record_structures.json`, `out/starts_v3.json`. Links in the texts are relative to the repository names. No header
says "frozen" or "draft"; each text says once that versions 1 and 2 are filed in the advisor folder as sent and says
where a reading changed. Abbreviations (SD, FD, D, P) are defined once in each text.

## A2 section 1: the ten required changes of the first pass

- **Values form of condition 2 undefined.** Done (D 5.1, claim 4): in values the condition is only that the run with Y′
  has two of Y′. **A small disagreement**: A2 and decision 5 say "with condition 3 and X alone standing in for the rest".
  X alone has no place of Y (Y's knots are removed), so it can never have two of Y and adds nothing to condition 2. The
  texts say "condition 3 stands in for the rest (X alone, which has no place of Y, is reported)".
- **Base law unquantified.** Done: C(r, b) and CF(r, b), one base law b fixed for the whole class (D 5.1 says "the same
  for every member"); CF under MET only, STEPS-1 reported (claim 5, P12).
- **Form class mixes the families.** Done: one form class per family (claim 5); made-3's Y and three-222's Y are the same
  pattern, and so are made-2's and two-22's (checked: the census counts them identically).
- **P2 leans on S6 for the three-holder starts.** Done: the tie classes at round 0 of all 60 third-pattern starts were
  computed (each kind of Y with each of the five other kinds of Z, named before and after): e has three holders, and no
  start has a tie or a frozen distinction under either knot law. Registered in run G and P2.
- **P16 gap.** Done with B3 (A2 section 3).
- **P5 wording.** Done: "has as its made members offshoots of start knots"; the second clause is argued in P, "Settled by
  construction" item 5: a member of Y holds two or more loose places, so its image is an offshoot of a start knot (S4),
  whose inputs keep their old holder, the start knot, outside every set of made knots, while every holder of a place of
  a member of Y is one of Y's knots.
- **"Holds one loose distinction" to "at most one".** Done (claim 5, D 6.4, P item 4).
- **X alone compared by names.** Done in the text (D 4.6: the traces renamed by first appearance). The prototype already
  compared renamed traces (`v2_common.renamed_trace_hashes`), so no count changes.
- **The place moving from 16 to 10; B(ii) on start knots.** Agreed with A2 that neither matters. D 4.2 now says once that
  B(ii) is not run in this study, and the mentions in P1, S1 and P's checks item are removed (smaller).

## A2 section 2: the form arm

- **Class sound; follows the engine's census.** Done (claim 5: "a census by the study's engine").
- **Census by descent from X only.** Taken (also decision 11). **A correction while doing it**: version 2's census
  (made-3 276, made-4 204, …) counted pairs of a run and a round and called them runs. Recounted as runs, per family, in
  the runs of that family (P, disclosure): made family (192 runs) made-3 94, made-4 26, made-5 12, made-6 22; family with
  Y present from round 0 (240 runs) one-2 62, one-3 2, three-222 76, two-23 0, two-33 0. By descent from X only: made-3
  92, made-4 26, made-5 12, made-6 22; one-2 4, one-3 0, three-222 6. The class is unchanged. This corrects a draft
  that has not left the thread; if the thread sent version 2's numbers further, it is a Narrowing for
  `docs/CORRECTIONS.md` (the class and the predictions do not change).
- **Counting mode for Y's knots.** Done (D 3.6): the number of distinct connected sets of made knots each carried onto Y's
  knots by a renaming, up to 10,000; used only in the controls of the readings.
- **The part and knots placed by hand.** Defined (D 3.6), as the prototype did it (`v2_reader.py`).
- **No every-choice control for form.** Not added (decision 11); said under "What a result would and would not show":
  the form negative is about four stated rules and their swaps, not about what the law allows.
- **CF decidable.** Agreed; no change needed beyond the quantifier.
- **The made-4 wording and its reverse check.** Done: A2's wording is used ("one case that is there with this Y and not
  in X alone, not a copier for any other member, lost under renaming"), and condition 2's reverse is read from version
  2's runs: with made-3, made-5 and made-6 in Y's place the parts the same as made-4's Y number 0, 1 and 1. Checked
  too: X's course in that case is the same with Y barred and differs from X alone at round 2, so it needs Y's knots, not
  Y's births, as A2 says.

## A2 section 3: the owner's arm

- **Ended.** Done: SD's ended (D 7.2). A2 says to define "goes on" as a member left and a birth in round T; decision 3
  says "makes a birth in the last round read". I used the decision's name with A2's condition (D 7.3: X has not ended
  by round T and some birth of round T has a parent among X and its descendants), because the bare name is wrong in two
  pattern-runs seen: X makes a birth in round T, an implied birth, and has no member after it. Neither is a case of any
  reading.
- **The round.** Done: one T for every comparison of a run, the last round every run of the reading reached (A, B(i),
  B_X, M, M_Y) (D 7.1). This is slightly wider than decision 3's "the last round both runs reached"; one T per run is the
  smaller text and gives the same counts here (T = 6 in 1,606 of 1,728 runs).
- **"Ended by what it met" requires no meeting.** Replaced by reading (ii), "X ended with Y making births, Y still making
  births", which names no cause; "through a meeting" (X not ended by T in M) is reported with it (D 7.6).
- **The bound.** Done: the round of ending in every run (D 7.2). Checked further: in the made-4 case of (ii), with Y
  barred X ends at round 6, one round after T = 5 (run A's next round stops at the fold engine's guard). This is now
  said in P (PO5), in the owner's arm and in the plain sentence.
- **Plainness.** Done (owner's arm A and D).
- **B1 (a), (b).** Agreed. **(c), (d).** Agreed and rewritten (owner's arm B1; claim 6; P item 8), with the sentence of
  decision 4. I checked (c) in the engine: under CANCEL-RETIRE a short member's usable distinctions are barred
  (`pm.py`, the barring step); FILLERS bars too and is not registered; the paired runs bar by construction.
- **"A loose distinction is never eligible".** Agreed (FD 2.2).
- **The FLOOR0 counterexample; PO2 has no run.** Done: run O (P, runs table; D 7.9 defines "changed by births
  descended from Y only"). Seen: of 1,034 runs read, 68 have such a change, all under parity and STEPS-1, and in every
  one some knot fails the knot test at that round; the smallest is the one A2 checked by hand, reproduced.
- **PO1.** Done: "takes"; the whole set; not-all-equal by a solver over the whole set when it has at most 12
  distinctions, otherwise the 12 with the smallest names, reported so.
- **B2.** Done: a proof where every history is read; for drawn histories only the weighting is carried. PO8 is marked a
  check where read in full and a seeded replication under offshoots, and is now registered in run 4 (made-2, both knot
  laws).
- **B3.** Done the smaller way A2 offers: P16 kept only on the parts by descent, said to be true by definition; the
  renamed trace is reported (P17) with the reason it cannot carry the statement at the last round read. "What is
  necessary is a take" is now "seen in the one case".
- **The third-pattern runs.** Agreed with all three points. Reading (iv) is reported with no prediction; the note that a
  three-holder e changes the start beyond adding Z is in the owner's arm, C.5; the made-design construction is dropped:
  Z is defined only on the designs with Y present from round 0 (smaller), so the made-4 form case and the 15 made take
  lists are not read under (iv), and the texts say so.

## A2 section 4: the inkling as registered

- **(i) in two parts.** Done: "no copier at all" and "a copier for some members and not all" (owner's arm A; P, POA).
  Seen: no copier at all.
- **(ii) renamed and never support.** Done (decision 3): "X ended with Y making births, Y still making births", reported
  with its reverse and the controls. A2's reason that the made-4 case is likely the implied closing: **confirmed** by a
  trace: X ends when its join of six parents is implied (no fresh distinction); under not-all-equal the same join receives
  one and X does not end.
- **The plain sentences.** Done, fitted to the version-3 counts. **A small disagreement with the wording "once between
  two patterns of the same kind"**: on the registered naming the control two-22 gives two of the three runs of (ii) (one
  start and law, both knot laws) and none of the reverse; the sentence now says "two of the three are one start of two
  patterns of the same kind". The reverse count is 9 on the registered naming (14 over both namings of e).
- **(iii) one-way and (iv) a third pattern.** Added (D 7.7, 7.8), reported, no prediction (P, PO9 and PO10). Seen: (iii)
  in 70 runs and its reverse in 8, none in the controls; (iv) on the stated-rule case in 5 of 5 with Z named before Y and
  0 of 5 named after; on the take lists in none (with Z there the two remain wherever the list applies). For (iv) under a
  take list I added a translation rule (D 7.8, eight lines): without it a take list, which names distinctions of a run
  without Z, does not define a run with Z.

## A2 section 5: predictions

- **Undecidable as registered.** All fixed. PO2: run O. PO3, PO4, PO6: cut to the registered naming (decision 1, the
  smaller of the two ways; e named first remains only as renaming n2 of the cases), so no e-first run is added. PO7:
  made-2-exchanged added to run 2 as one design. PO5 and PO6: their runs are listed in P itself. P4: run R's structures
  are `record_structures.json`. P3: the counts are in `starts.json`.
- **Pinned too exactly.** P15, PO3, PO4, PO5 and PO6 are marked **replication**: a miss is a finding about the engines,
  not about the claim, replayed birth by birth. **P15 is merged into PO3** (smaller): it was the same reading on the same
  runs; PO3 gives version 2's per-base-law totals (50, 276, 240 of 528) as a consequence of its table. A2's sums (828 and
  550 + 94 + 180 + 4) were over both namings and are replaced: 560 = 370 + 60 + 126 + 4 on the registered naming.
- **P9.** Demoted to reported (c), at the registered 20,000 histories (smaller than repairing it).
- **True by construction.** Marked: P20's first clause follows from P6; P16 on the parts by descent is true by
  definition; PO8 is a check only where every history is read.
- **P20's reason.** Done: two checkable clauses, "smallest in the registered class".
- **Step 2's sentence.** Done (survey, top; P item 6), with the not-all-equal half; the holders of v are reported for all
  35 values cases (one holder after round s in 21, two in 14; 2 to 11 at the round read; at least six distinctions with
  three or more holders in every structure read).
- **His stop.** Agreed, covered.

## A2 section 6: for the implementer

Each item, and where it now is:
- Take lists and their format: `take_lists.json`, format stated in the file (also the holders of v).
- Run R's structures: `record_structures.json` (the drawn structures dumped with the seed and order of
  `sB_record_checks.py`; the hand-built ones; the enumerated labelled structures described in P).
- The lists for two-knot, three-knot and three-knot-larger, and Ring(5, 3): `starts.json`, "fold study starts".
- The record's CAP-3 counts: `starts.json`, "counts for P3" (every round 0 to 8, both base laws, the three starts).
- The e-first starts: not needed as runs (cut); n2 is an exact label map in `starts.json`. made-2 with the names
  exchanged: `starts.json`, design `made-2-exchanged`.
- Controls of the readings: Y and s, the counting mode, the construction placed by hand, 7 rounds (D 3.6; run G).
- Run 4: rounds s + 1 to s + 4; the exact `<design>` and `<law>` strings; a history stopped by the guard is read through
  the rounds before and counted apart; knot tests on every history with two and every replayed list (D 2.7).
- Run 3: 7 rounds; pairs for s = 0 to 4 with no limit on their number, FD 5.8's limits not used (D 4.8), as version 1
  selected them.
- Renamings: exact label maps per design in `starts.json`; n4's exact call in D 4.5; "survives" compares the reading,
  not the names (D 4.5).
- The third pattern: numeric labels in both positions (`starts.json`), only on the designs with Y present from round 0,
  Z barred after round 0, s = 0 (D 7.8).
- Descent of knots made by round s: D 2.6.
- The fourth mark's renaming: by first appearance, on the replacement runs (D 5.3).
- Masked runs for Y: M_Y and M′_Y (D 4.7).
- The meeting round when there is none: D 2.3.
- Solver bounds: PO1 (12 distinctions); the strong form (14 places, D 3.2); not-all-equal ties are exact (D 3.3).
- The naming convention: D 1.2 (FD 2.1, e = 1000).
- One number per thing: 20,000 histories (P9 reported); run 4 rounds s + 1 to s + 4; run 3 and the controls 7 rounds;
  run 2 6 rounds, 8 for the two-users reading on a case.

## A2 section 7: words

All done in the five texts: "ended by what it met", "goes on", "the symmetric control" (now "the control with Y the same
as X" and "a start with a renaming exchanging X and Y"), "exchange-symmetric" (now "unchanged when X and Y are
exchanged"), "reader controls" (now "the controls of the readings"), rules as the subject of "read" (now "use"), "the
fourth mark" (now FD's name with "on the replacement runs"), "specific" and "specificity" (now "condition 2, not of the
others"), "copier" for starts and start patterns (gone), "form" and "values" (admitted in D 0 as labels of the
readings), "crosses" (now "its way is"), "handed down a chain" (now "handed on, birth by birth"), "reaches two loose
places" (now "is tied at"), "planted" (now "placed by hand"), "one bit" (now "one value"), "chains" and "outputs" (gone),
"stated by structure" (gone), "cheap" (gone), "permanent" (now "at every later round"), "share" where counts are given
(now "counts"). Also, from the decisions: no "mirror", "tally", "generation" or "grandparent" (P item 4 now says "two
parent steps away"); names "before" and "after", and "below", "above" and "beside" removed even for positions in the
text; "symmetric" for meeting is now "mutual"; the owner's addition dated as decision 12 says. The words kept as A2
allows: "a third pattern", "descended from X only", "the take-by-take weighting", "present with X from round 0", "met by
a dead knot", "hand on", "every member left waits".

## A2 section 8: the required list, in A2's order

1. The arm's runs and listings registered: done (cut to the registered naming; made-2-exchanged; run O; PO5 and PO6
   listed; PO3 numbers).
2. POA: done ((ii) renamed; (iii), (iv) added; plain sentences; ended, the round, the meeting condition).
3. B1 (c) and (d), and "never what it holds" in the claim and P: done.
4. Values condition 2; the base-law quantifier; the form class by family; the made-4 wording and its reverse check:
   done.
5. B3 and P16: done.
6. Everything in A2 section 6: done (list above).
7. Marks for PO8, P15, PO3 to PO6, P9: done (P15 merged into PO3).
8. Three-holder starts: done (computed, none tied).
9. Step 2 sentence: done.
10. Words: done.

Optional: form in run 4 not added (decision 11; said under "would not show"); the census by descent from X only, the
holders of v, the rounds of ending and P20's clauses all added.

## Removed or demoted, and why

- **P15** merged into PO3: one reading, one row (smaller).
- **P9** demoted to reported: its seen basis was version 1's 3,000 histories with small counts; repairing it would need
  a new prediction on a weighting (smaller).
- **Version 2's PO9** (the third pattern, predicted) demoted to reported reading (iv), PO10, as decision 3 asks.
- **Reading (ii)** demoted from a reading that could "support" the inkling to a reported reading never called support.
- **The arm's counts over two namings of e** replaced by counts on the registered naming (decision 1, the smaller way).
- **The made-design third pattern** of version 2 (D2 7.5: a founder met through two dead knots) removed; Z is defined
  only where Y is present from round 0.
- **B(ii)** mentions removed from P1, S1 and P's checks; D 4.2 says once it is not run.
- **The not-all-equal weighting paragraph** cut to two sentences in P's disclosure and removed from the claim and the
  survey: version 2's decision had already left it out of the study.
- **The version-1 arm note's per-design tables** (three tables, about 90 rows) replaced by one table by family and base
  law (12 rows); its PO10 and PO11 folded into P16 and P17.
- Nothing the owner asked for is removed: his four steps, his stop, his inkling (as reading (i), with (ii) to (iv)
  reported), the paired test (B(i) with B_X, X alone, the masked runs), the knot test under both knot laws, the swaps of
  every scaffold (run 5), and the verdict "supplied or made" (D 5.2).

## Added because nothing smaller met the requirement

`starts.json`, `take_lists.json` (format and holders of v), `record_structures.json`; run O; Y alone (needed by the
reverse of (iii)); D 3.6's counting mode and placing by hand; D 7.8's translation rule for take lists; D 7.9.

## Other findings while revising

- **Under MET, X's course differs from X alone in every run** (864 of 864): X alone has the link barred, and MET's takes
  use it. Under STEPS-1, in 216 of 432 made runs and none with Y present from round 0 (P18). So in reading (iii) the
  clause "differs from X alone" is always met under MET; it is reported so.
- **Who takes from whom on made-2 follows the order of births**, not the start's names: the one-way takes are the same on
  made-2 and made-2-exchanged (owner's arm C.4).
- **The two-22 case of (ii)** ends by retiring: X's five members are short in round 3 and retire.

## What I could not do

- Nothing here is the study's engine; every count is the prototype's, unreviewed, and the predictions marked
  replication are only as good as its code.
- I did not rerun the first test (`v2_run.py`), the swaps or the every-choice runs: version 3 changes their texts, not
  their readings, and their counts are disclosed from version 2 (the census recounted from the same output). Run 4's
  draws remain 5,000 per design and law in the prototype against the registered 20,000.
- PO8's seen value is still version 1's (2,000 draws per law on made-2); not rerun under run 4's laws.
- Version 1's 213 pairs (run 3) were not rerun under the version-3 readings.
- I wrote nothing in the repository and ran no git or tracker command; the files above are for the thread to file.
