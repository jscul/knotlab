# Changes in version 2, item by item

The advisor's cold review (`study/copier_advisor/answer.md`, verdict "freeze after listed changes") and the thread's
twelve decisions on it. For every item and sub-point: what was done, or why not. Each of the advisor's factual
statements was checked before it was adopted; the checks are named. "D2" is `definitions_v2.md`, "P2" is
`preregistration_v2.md`, "C2" is `claim_v2.md`, "S2v" is `survey_v2.md`. The four version-1 files are unchanged.

## 1. S1 to S6

- **S1 right under parity with IMPLIED when a knot fails, and with several births on one shared distinction.** Adopted;
  checked (the relation on X's distinctions never changed in 144 runs under FLOOR1 and 144 under CAP-3, failing knots
  included). Stated with what it excludes: LITERAL, FLOOR0, ONE-FEWER, comparisons across B(ii) (P2 S1; D2 6.1; S2v 2.1).
- **S2 exact statement** (tied exactly when one fresh distinction and inputs all tied equal; then tied unequal to each
  input). Adopted after checking the two directions by argument (S2v 2.1). **The knot-test condition dropped**; "from a
  start with no tie, no made distinction is ever tied" by induction with S1. **"The exceptions are exactly … failing
  knots" removed** (a failing knot ties nothing unless its inputs are all tied equal).
- **The Fano counterexample to "any start".** Checked exactly as the advisor gives it: the start (Fano pattern less one
  knot, with {l, a, b} and {x, b, c}) ties {a, b, c, l, x}; the join of the two added knots takes l and x and its fresh
  distinction is tied to them (the two added knots fail the knot test). My first construction, with an extra loose place
  on each added knot, does not tie anything; the advisor's three-place knots are needed. Adopted in C2 5, P2 S2, S2v 2.1.
- **The registered starts are tie-free by S6, so P3 is a true check.** Adopted (P2 P2, renumbered).
- **S3, four precisions.** All adopted (sum over the field of two elements in the span, zero included; a passing maker
  never holds v; the same-round clause needs v's maker to have one fresh distinction and is not needed for values; "two
  or more fresh hands nothing on" relies on IMPLIED).
- **S4: shorter proof; holds in every case listed; exceptions only offshoots of start knots; STEPS-2 one generation
  later; HOLD; state by maker; S4 does not close the designs present from round 0 under STEPS-1 at round 1; FLOOR1 never
  gives more than two.** All adopted. Checked computationally (`v2_checks1.py`): under RELEASE and HOLD, MET, STEPS-1 and
  STEPS-2, every choice rule, three treatments, both knot laws, 21 starts and designs, the only births with two fresh
  distinctions were offshoots of start knots and, under STEPS-2, offshoots of knots whose parents are all start knots.
- **S5, S6 are record checks only.** Adopted; registered as the record check (P4) for the owner's step 2.
- **S7 false for a two-place IMPLIED knot.** Checked: such knots occur (e.g. under STEPS-1 on the three-knot start),
  pass the test, and have both places tied. Fixed ("with three or more places").

## 2. The claim

- **C quantified over the rules after the fact.** Fixed: C(r) stated once per rule, fixed before the runs (C2 5).
- **"One made X" while X is a start pattern on the designs present from round 0; the made class had two members.**
  Fixed: C split by whether X is made; the made class widened to four second patterns not the same as X (made-3 to
  made-6), which was cheap.
- **Register C as predicted to fail.** Done (P11).
- **The first "cannot hold" is about the ration.** Reworded by maker, as the ration's doing: "no part with a member
  holding two is made at all, copied or not" (C2 5, P2 S4).
- **The second is honest for "tied" only, from a tie-free start.** Reworded; the plain sentence changed (C2 5, P2).
- **The law does not match the fold result's P11.** Accepted. Both rations are primary under MET (the thread's
  decision 1), stated where the law is fixed (C2 1, D2 1.3).
- **Form as an arm of its own under MET with CAP-3(t) and the fresh count by parents**, with: a reader control (done:
  the readings reproduce the record's N(t) with no taking rule and find a planted part and planted knots, P14); a census
  (done: two members holding two and three, and three and three, are never made under the arm's laws and are dropped,
  P13); at least two second patterns not the same with the same X, rule and numbering (made-3 to made-6; one-2, one-3,
  three-222); B(i), B_X, the replacement run, item 3's check (P16); the share of cases in which X's course differs with
  Y at all (P15). **Swaps on the arm's negatives**: run (6,336 runs, disclosed), so the clauses that needed them stay.

## 3. The necessary condition

- **Specificity restored in D2 5.1; copies descended from X only; the fourth mark read on the roster's parts by descent
  as well as on the trace; redefined on the replacement runs; registered as a check (P16) and a reported reading (P17);
  to the owner a necessary condition not yet seen, not a reason.** All done. The argument is in P2 (Settled, 9) and in
  `arm_owner_inkling.md` B3.
- **Finding to add, from the new runs**: read on the replacement runs, the fourth mark holds in 367 of 2,304 pairs (X's renamed trace
  differs with what Y is in 164 of 864 made-X pairs and 203 of 1,440 start-X pairs), unlike the fold study's 16 pairs.
  So it is not what fails here; "not yet seen" is true only of a case that is also a copier.

## 4. Not-all-equal and values

- **(a) required; the plain sentence overstates.** Done: "no made distinction is ever tied to another", from a tie-free
  start (C2 5, P2).
- **(b) left out, stated as a limit and a direction with the two reasons.** Done (P2, "The not-all-equal share, left
  out"); both numbers checked by hand (1/2 to 1/3; 2/3 against 3/4).
- **Under parity a share means nothing new.** Agreed; not used.

## 5. The paired test for values

- **"Fewer than two with Y barred" dropped as a condition; B(i) reported as "needs Y's births or not", by tie class.**
  Done (D2 4.2). On the advisor's third reason, a small disagreement about the cause: in the disclosed case barring Y
  moves the place from 16 to 10 not because names move (barring renames nothing) but because Y's join, which took 16 and
  so made it eligible, is not made with Y barred; NEWEST then picks the largest eligible distinction, 10. The point stands:
  per place, B(i) is confounded by the choice.
- **The right tests: at least one of the two from X; the replacement run; renaming the start; B_X.** Done; renaming is
  required before "under a stated rule" (D2 4.5, C2 4). Run on every positive: the values case is lost under all four
  renamings.
- **B(ii) not needed for values; undefined on the designs present from round 0.** Dropped for values. A minor
  disagreement on "undefined": FD 5.1 defines B(ii) through fresh and taken distinctions, so it is undefined for start
  knots in FD's text; the fold engine's reading 15 extended it to start knots. Not material, since it is dropped.
- **"v tied to no place of X after round s"** added (D2 3.3).
- **Usable and loose at the same round read; report whether both are later taken by different births.** Done (D2 3.3);
  in the case, both are later taken by different births and stay tied through round 8.
- **Under RELEASE with offshoots the two are made in the same round.** True of the case (both in round 6); stated as a
  remark, not a definition.

## 6. Definitions

- **The meeting round** defined (D2 2.2), with whether readings fall before, at or after it.
- **Y's knots** (members and every knot a member meets); the search's signature backtracking and bound (two disjoint,
  or 10,000 knot sets: "bound hit"); **disjoint** = no common knot, shared places reported; **run G's brute force** with a
  stated pattern and stated candidates (P2 Runs, G). Done.
- **"Containing", mixed descents, "at some round" against "at the last round".** Done (D2 3).
- **Origins**: "from both" for different parents; a third part's knot as a parent included; "made by X" stated for each
  reading (at least one in values; every member from X only in form and for Y's knots). Done (D2 2.5).
- **The replaced second pattern**: undefined on the pairs (stated: C not tested there, D2 4.7); the dead knot changes
  with Y on the designs present from round 0 (stated, D2 4.4); the answering place of Y′ is any, by tie class. Done.
- **"The same stated choice rule"**: all four read names (BY-COUNT indexes from the oldest); replacement renumbers (e is
  17 and 12, checked); the rule is the same text on the registered naming; the naming is supplied; a positive must
  survive every registered renaming. Done (D2 1.6, 4.4, 4.5).
- **Every choice**: depth-first count stopping past 60,000; the drawing order, the call (`randrange` over the candidates
  sorted by name), single candidates make a call, the design and law strings, the seeds. Done (D2 2.6). The count uses
  a lower bound (the product of a node's candidate counts) to stop early; exact for deciding "more than 60,000".
- **The five counts** are counts, not shares; "of neither", "made by X" and the round defined. Done in P2's run 4 (the
  version-2 table is to be recomputed with the version-2 reading; the version-1 table is kept as disclosed with its
  reading).
- **The set V** dropped. **"The smallest pattern it fails on"** ordered by members, then places, with its
  birth-by-birth reason (P20). **The knot-test filter** kept; cases from runs with a failing knot reported, marked.

## 7. Predictions

- **True by construction** marked as checks: P1 (S4, excluding the fresh count by parents and B(ii)), P2 (S2), P5 (S4
  under COPY-LAW), the parity clause of P10 (offshoots never fail), P14, P16.
- **P0 is nearly empty.** Said plainly in P2 ("What the gate cannot test") and in P0's text.
- **Replications only, and expected failures on an independent engine**: P6 and P7 stated by structure, names in a
  replay listing; P7 split (P7a survives two swaps, P7b lost under the other rules, P7c lost under renaming, P7d
  reported); P8 split into the replay of registered take lists (P8a, decidable) and a reported reading (P8b), two
  members holding three each left open; P2's CAP-3 part separated (P3). The exact "3 of 180" is no longer registered.
- **Undecidable clauses removed**: P4's and P5's "under any swap" now decided by run 5 on the form arm; C for a made X is
  tested on four members; the "why" of step 4 is P20, decided by its birth-by-birth listing.
- **P11 predicted to fail** (a). Done.
- **Missing, added**: the record check (P4); X alone (run 2; P18); the smallest failing pattern's reason (P20); the
  statement that values under parity reach neither arm of the stop, with what is then reported (P2, "What a result would
  and would not show").

## 8. Supplied or made

Three questions with exclusive answers; "made" only when all three are the growth's (D2 5.2, C2 7). The advisor's
one-sentence verdict on the disclosed case adopted (P2).

## 9. Scope and honesty

- What a positive for C would and would not show, and what the expected result shows and does not: adopted (P2).
- The plain sentence: the advisor's, with one added sentence for the form arm (P2).
- **Blurring law and pattern**: C's rule picked for the pattern (fixed: C(r)); F1 and the owner's index (removed; F1 is
  a control: "the knot law allows it; the choice decides it"); COPY-LAW glossed at each first use; "the base law under
  which the two-knot part copies itself" said only of COPY-LAW with no taking rule; "aimed at" and "points at" removed
  ("more often, under the named weighting").

## 10. Words

All of the advisor's item 10 applied (D2 0): no "bearer" or "bears"; no noun "build" ("Y's knots"; "a renaming of Y's
knots among the made knots"); "form" only in the owner's words ("two parts the same as Y"); "descended from X only /
from Y only / from both / from neither", and "joint birth" in FD's sense only; "the take-by-take weighting"; "history"
defined once; "hand on" kept; "the second pattern handing on its own value" and, for form, "returns"; "present with X
from round 0" and "met by a dead knot" for "beside" and "hung on" (designs renamed `ystart-…`); "copier" in the owner's
sense only, with the line re-reading the record's heading. One addition: "goes on" and "ended by what it met" for the
owner's arm, built from SD's "ended".

## 11. The eight open questions

1. Kept C for values, fixed and predicted to fail; form added as its own arm. Done.
2. S4 in every case and under HOLD; STEPS-2 one generation later. Done and checked.
3. S2 not tight; fixed. Done.
4. The tie is the input; replacement and renaming are the tests; B(i) reported; B(ii) not used. Done.
5. Usable and loose at one round; chains apart; "two users" reported. Done.
6. The designs present from round 0 are a separate arm with X supplied by the start; STEPS-2 primary for the arm of
   parts that came apart, cost stated. Done (D2 1.4, 4.7).
7. F1 a control with replayable histories. Done (take lists in `take_lists_v2.json`).
8. Words: item 10.

## 12. Verdict: the required changes in order

1. Law reconciled with P11; the form arm registered with its class, controls and prediction. Done.
2. Both "cannot hold" statements and the plain sentence reworded. Done.
3. The values test revised. Done.
4. C(r) per rule, made X apart from start X, predicted to fail. Done.
5. The corrected necessary condition, specificity in D2 5.1, the fourth mark on replacement runs. Done.
6. Predictions restructured. Done.
7. Definitions completed. Done.
8. Verdicts as three questions. Done.
9. Words. Done.
10. What P0 does not test. Done.

Optional, all taken (the thread's decision 11): S4 extended to STEPS-2 and HOLD; the "two users" reading; X alone; the
set V dropped; the fix to S7; the registered record check. The not-all-equal share left out as a stated limit and
direction (decision 10).

## The thread's decision 12: the owner's arm folded in

`arm_owner_inkling.md` is folded into D2 section 7 and P2 (its runs in run 2, its predictions PO1 onwards), under the
same word rules (designs renamed; "beside" removed). Its counts were made on the version-1 designs and laws; they are
recomputed on the version-2 designs (made-2 to made-6, the designs present from round 0, the three base laws) and
disclosed in P2.

## What I could not do, or did differently

- **The arm of parts that came apart under the version-2 readings** was not rerun; its version-1 results (213 pairs: no
  made distinction of X tied to a place of Y, no two parts the same as Y) are kept as disclosed, and run 3 is registered.
- **The every-choice control** was drawn at 5,000 histories per design and law in the prototype, not the registered
  20,000; the take lists of its cases are registered for replay.
- **The not-all-equal knot tests in the every-choice control** were not run (parity only), as before.
- **Disagreements**, both minor and stated above: the cause of the place moving under B(i) (item 5), and "undefined"
  for B(ii) on start knots (item 5). I found no error in the advisor's checks of S1 to S7.
