# Changes from version 3 to version 4

The advisor's third pass (`study/copier_advisor3/answer.md`, "A3 n.m") says "Freeze" with sentence-level fixes. All five
texts change; the three data files do not (no fix needs them). Checks were made with the prototype on its existing
runs (`v4_check.py`, the version-3 arm runs recomputed with the new definition of T; reading `out/v2_main.jsonl` for the
census); nothing new is registered.

## Section 1

- **1.1** Applied: P2 (run O apart, its tie classes reported), P10 ("in runs 1 to 5", "Run O's knots are PO2's"), run 6
  ("of runs 1 to 5"). For P2's "its tie classes are reported" to be true, run O's row now reads them ("under
  not-all-equal, every tie class containing a made distinction (reported)"); that is the one addition the fix needs.
- **1.2** Applied in D 5.1 and claim 4, for form and, by the same words, built structure ("fewer than two of Y′ (any
  descent)" after every round read; "two of Y′ made by X at some round read"). It agrees with the disclosed made-4
  check, which counted parts of any descent.
- **1.3** Applied in the owner's arm, A (i), with "as the second pattern" for "in Y's stead" (A3 6); claim 6 and POA
  point to it. Checked: its last clause is the reverse direction of condition 2's first half, the one a member-by-member
  reading needs; it is the check disclosed for made-4 (0, 1, 1 parts), and it excludes the two STEPS-1 made-4 cases,
  which are X's own course. "No copier at all" still stands.
- **1.4** Applied in P item 10 and the owner's arm B3. Checked: condition 2 gives fewer than two parts the same as Y′
  with Y and two with Y′, so those counts differ by definition; nothing in it bounds the parts the same as Y in the run
  with Y′, as A3 says. P16 is unchanged.
- **1.5** Verified by the prototype: `{f1, a, b}`, `{a, b, v}`, `{v, c, d}`, `{c, d, f2}` has at most two holders, ties
  f1, v and f2 under parity (f1 and f2 its only loose distinctions), every knot passes both parity methods, and there is
  no tie under not-all-equal. The corrected sentence is used in P item 6 and at the top of the survey, with "has any
  other loose distinction" for A3's "keeps any other loose distinction" ("keeps" is HOLD's word), and the four knots as
  the example.
- **1.6** Applied. Checked: `v3_arm.py` read no values reading, so made-2-exchanged was never read for values.
- **1.7** Applied in D 4.5. `starts.json` already lists n1, n3, n4 for the made designs and n1 to n4 for the others.
- **1.8** Applied in D 7.1 and D 7.8. Checked against the 1,728 arm runs: with X alone and Y alone in T, T is unchanged
  in every run (Y alone stops before round 6 in 56 runs, each already with that T or less), and reading (iii) and its
  reverse stay 70 and 8; reading (iv)'s runs with Z and with Z barred reach the same round in all 164 cases read.
- **1.9** Applied to run 3's row. `starts.json` lists no renamings for the pair starts.
- **1.10** Applied to run G (the procedure the engine's own, the one round under COPY-LAW(CANCEL-OFFSHOOT) with
  MET(OLDEST), parity). Checked: nothing disclosed depends on these draws; the prototype's tie check (`t_ties.py`) used
  other draws (seed 7, 400 structures), as the survey says.
- **1.11** Applied. Checked: in each of the 122 runs with T < 6, a run of the reading stopped at round T at the bound
  of 500 knots (14 runs) or at the fold engine's guard (108); none ended its growth early. Version 3's "none stopped by the guard"
  meant that no run raised the guard's exception, and was wrong as written.
- **1.12** Applied to P3 and to the disclosure's version-1 sentence. Checked on version 1's 315 runs: no such part
  after any round t ≥ 3 under any taking rule, and STEPS-2's are at round 2.
- **1.13** Applied, and it **corrects my version-3 numbers**: the census counted the runs of all of a family's designs
  (its control included) under both knot laws, 480 and 576 runs, not the 192 and 240 written. Restated under parity
  (made family 240 runs: made-3 47, made-4 13, made-5 6, made-6 11; by descent from X only 46, 13, 6, 11; other family 288
  runs: one-2 31, one-3 1, three-222 38, two-23 0, two-33 0; by X only 2, 0, 3), with the check that every form reading
  is the same under not-all-equal, run by run (528 of 528 pairs). The class and P13 are unchanged. This version-3 draft
  had not left the thread.

## Sections 3 to 6

- **Section 3.** Condition 2 in values in A3's plainer words (D 5.1, claim 4); "under one law, under both knot laws" for
  the two-22 runs (owner's arm C.4 and D).
- **Section 4.** All five replacement sentences, checked: 70 and 8 runs, 66 of them on made-4 to made-6 under
  offshoots; "two rounds later" (X ends at round 4 with Y there and round 6 with Y barred); "cut off at round 5" (run A's
  next round stops at the guard); "nine"; "under one law and both knot laws"; Under MET, the comparison with X alone
  always differs (864 of 864). Three small changes, each to keep a sentence true or within the word rules:
  - "as seen": "for what your second sentence describes to act on" in place of "for what you called 'over-write' or
    'break out' to act on", so that those words stay inside his quotation only;
  - "as seen": "where a fixed rule leaves two of one pattern of the class", since the every-choice histories leave two in
    every design and were not renamed;
  - "(iii)": "a second pattern of more members than the first and short knots making offshoots" (all 66 are under the
    treatment in which short knots make offshoots; the other 4, on two-33, are too, with two members). The C.3 "Read"
    line, which read as universal in the same way, now says "in 66 runs".
- **Section 5.** Both additions made (claim 5; P's expected-result bullet).
- **Section 6.** Every replacement made: "is not decided"; "have the same number in the order of that parent's
  offshoots"; "as the second pattern", "with X for Y"; "by their order in the start's list", "named before Y and named
  after Y"; "the shared distinction e" (and "0 or e" where version 3 wrote "the barred link"); "two parts" for "halves";
  "leaving two parts the same as a second pattern", "can leave two of what it meets under parity"; "the form given here";
  "restricts each met set to", "the restricted remainder of a mixed part"; "far away" dropped; "of more members"; "is
  barred" (the plain sentences); B1's heading and the plain sentence now say "changed". "Over-write" and "break out" now
  appear only inside his quotation: D 0, claim 6 and the owner's arm say "the words of his inkling" or "his second
  sentence" instead. Kept: "hypergraph-rewriting system", the literature's name in "In standard terms".

## Not applied

Nothing in A3 is left out. The departures from its exact words are the five listed above (1.5's "has", the three in
section 4, and run O's added reading for 1.1), each for the reason given.

## Files

`claim_v4.md`, `definitions_v4.md`, `preregistration_v4.md`, `owner_arm_v4.md`, `survey_v4.md`, `changes_v4.md`;
`take_lists_v3.json`, `starts_v3.json` and `record_structures_v3.json` stay as they are. Check script `v4_check.py`,
output `out/v4_check_all.jsonl`.
