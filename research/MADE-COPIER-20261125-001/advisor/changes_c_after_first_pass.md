# Ticket C, version 2: the advisor's items, one line each

Files: `c_claim_v2.md`, `c_definitions_v2.md`, `c_preregistration_v2.md`, `starts_c_v2.json` (changed: the labelled
weights over the starts read under parity, the registered not-all-equal samples and the order of running added),
`cases_c_v2.json` (changed: the masked counts and the reading at any round added to the two values comparisons). Version
1 files are left in place. New scratch scripts: `c/c2_read.py`, `c/c2_posctl.py`, `c/c2_posctl_sum.py`,
`c/c2_rename_exact.py`, `c/c2_checks.py`, `c/c2_strata.py`.

## The owner's limit of 25 November 2026 (no run longer than about an hour)

- **The registered design**: every run sized from costs measured at the registered bounds (`c/c2_time.py`: parity MET
  0.121 s a growth, STEPS-1 0.421; not-all-equal MET 0.449, STEPS-1 about 3.1; the holder weighting 0.108 and 0.316;
  HOLD 0.087 and 0.859; STEPS-2 0.396; not-all-equal HOLD with MET 0.482) to finish within about 50 minutes on 6
  processes; eleven runs, about 7 hours in all. R1 is split by taking rule and knot law (R1a to R1d). Every run reads a
  prefix of one uniform permutation of the census (`random.Random('C|order')`), so a run cut for time leaves a sample
  under the census weighting. Version 1's every-start-twice under both rules, and its 300 + 300 five-knot samples under
  not-all-equal, are replaced (DC 1.5; PC "Runs"). Each zero bound is given for the size registered (PC "Runs", the
  table of bounds); the power sentence is unchanged. Four runs listed as "would need the owner's exception", not
  registered: not-all-equal STEPS-1 at every start (about 10 hours), parity STEPS-1 at every start twice (2.7 hours),
  not-all-equal MET at every start (1.5 hours), R7 at every start of three and four knots (days).
- **The knot test** moves to the last round read for every growth and continuation (Settled 7 says why that finds every
  failure), D 8's every round kept as a swap on the small starts: a change from D 8 for time.
- **R0b, R3, R6 and R7** are sized from the scratch's other runs and marked estimated.
- **The labelled weighting's bound** for a prefix is through max w / w̄ (DC 4.5), about 4.7/(K N).
- **My scratch**: each rerun timed on a prefix first; the timing runs themselves were cut at 5 to 10 minutes, and two
  that passed their budget on a long growth were stopped by their numbers.

## Section 17, required, in order

1. **The rate rule** (section 5): applied with this change. The masked continuations (FD 5.6) are added at confirmation
   as a fourth kind (`|BM|`), not at the first stage, at a cost of a third more continuations per case that passes at
   100 (the engine's `pm.Mask` in the continuation's context; checked in scratch). The case is renamed: a confirmed case
   is "a case met more often with Y"; "needs the meeting" is kept only for one with none of 1,000 with Y barred and none
   of 1,000 masked. The Y-barred control is said to be empty for from both, and so is the masked one (no birth has a
   parent among X's descendants and one among Y's), which the advisor did not say. A stopped continuation is read
   through its last round and counts as not meeting an event not met by then; stopped counts are reported, and rates
   over unstopped ones. The event of each rate is stated (q₁ after the meeting; q₁ at any round, reported; the controls
   at any round after s), with the lean toward the negative said and kept. The masked control was run in scratch on the
   four values cases: it removes the two that had passed (DC 4.3–4.4; PC, "Known").
2. **C-S1 as its own lemma** (section 3): applied as worded. Lemma C-S1 in PC, Settled 1, with the state named (DC 1.6),
   the demand point said ((e)), the reason corrected ("a loose distinction has one holder"; the knot laws' symmetry only
   for ties and the knot test), implied births, joins of three or more parents, both weightings, pairs and seeds. The
   guard checked in the fold engine and ticket A's engine (see the report; PC, "Known", and Settled 1 (g)): every count
   the guard compares is a function of the state, and the two counted in name order (cliques, joinable pairs) pass their
   limits exactly when their totals do. The wording "argued for every law of the family; checked exactly on small starts
   through round 3 and by sample at 8 rounds" is used; "cannot recur" and "no longer threatens a result" are gone. R7
   and R8 widened as section 3's last list says: five renamings (shift of the order of distinctions, knots alone,
   distinctions alone, reversed, permuted), the holder weighting, HOLD and STEPS-1 on four-knot starts, the class with
   the birth record and barred marks, the four coverage counts. Rerun in scratch: 243 checks on the first 12 three-knot
   starts and 84 on the first 8 four-knot starts (the holder weighting, STEPS-1, HOLD), all equal under all five
   renamings; the 192 single-history checks of version 1 are said, and the 120 of version 2.
3. **Values** (section 7): applied as worded. "Values, both from X" (both from X only) is claimed; values with one from
   both and both from both are reported apart; ticket A's reading has its own verdict (claim §5, PC9: not confirmed, the
   masked control meeting it as often or more); the post-hoc choice is disclosed at the head of "Known".
4. **Y's form not X's form** (section 7): applied as worded (DC 3.2, form, D 5.1's condition 3). None of the 92 scratch
   form cases had Y's form the same as X's.
5. **The error family, the index overlap, the stage-2 level, the power sentence** (sections 5, 8): applied as worded,
   with one addition: the reported readings form their own family m′. The K′ = 300 swap has its own seed kinds (`BN3`,
   `BY3`, `BX3`); confirmation uses i = 100 to 1,099; stage 2 has its own family m₂; the power sentence is in DC 4.4.
6. **The C-S3 gap and PC6** (section 4): applied as worded, and checked in scratch: under COPY-LAW(CANCEL-WAIT) 196 and
   195 of 219 growths had an older member, 20 and 25 an offshoot of a start knot holding two; under the other two
   treatments none (PC, "Known"). PC6 is "by argument" for four laws and "check" for two.
7. **Zero bounds** (section 6): applied as worded: strata, the labelled weights over the 3,344 starts read (256,561,
   largest 120), no bound on a share of met pairs, 7.4/M for all laws at once, the honest sentence registered, and the
   scratch bounds restated by stratum (PC, "Known", "Zero, bounded, by stratum"). The scratch's labelled sample is given
   "about", since two starts sampled twice were grown once.
8. **Knot test** (section 10): applied as worded: every rate over all growths and over growths with no failing knot
   (named as the conditioned weighting); cases in such growths marked and not counted toward CC-1 or CC-2; every scratch
   failure classified (298 knots in 298 growths, all joins failing in their own round: 151 of two parents that took a
   distinction, 145 of three to twelve parents with no take, 2 implied); PC14 no longer says "every law"; Settled 7 says
   why the last round suffices for continuations.
9. **CC-2 made definite** (section 8): applied as worded: at least 3 of 100 fresh growths of the start each holding a
   confirmed (F, G) case, stage 2's own family, the rate with its exact interval, no named percentage; "not of the
   others" as rates per met pair with a one-sided test, with a floor of 20 met pairs below which a G′ is "not read" (my
   addition, so that low power is not read as "not for others"; section 8's A248 point).
10. **Words** (section 14): applied as worded, item by item below.
11. **Predictions and a positive control** (section 13): predictions applied as worded (PC1 loosened to 10%, PC2 to 20%,
    PC5 "none confirmed", PC10 → PC12 "summed over the laws", PC12 → PC14 "some growths", PC3b → PC9 without "under no
    other law", PC9 → PC11 one statistic per law and renaming with an exact test, PC3 marked seen only where run, PC6
    split, PC13 → PC15 marked not seen under STEPS-1 (310 rounds had more than eight pairs), PC8 for from both, the
    scale sentence). **Positive control: not applied as asked, with the evidence.** Ticket A's made designs under
    sampled takes were run in scratch (183 of 210 design-and-law cells, parity, 100 continuations of each of four
    kinds): the claimed readings were met after the meeting in 2 cells at 1 of 100, ticket A's values reading in 2 (5
    and 1 of 100), and no cell passes at 100; so they give no positive control for the form reading. Registered instead
    (R0b): a machinery control (Y's own values on made-4 and made-5 under COPY-LAW(CANCEL-OFFSHOOT) with STEPS-1, 78 and
    86 of 100 against 0 with Y barred), which tests the continuations, seeds, readings and test but not a copier, and
    negative controls (the designs' cells; the 92 MET form cases). This still ties ticket A to ticket C: under sampled
    takes A's designs give no case met more often with Y.
12. **The soup sentence and the named later ticket** (section 2): applied as worded (claim §1, C-S6; PC question and
    stop rule). The later ticket is not designed.
13. **The definition gaps** (section 12): applied as worded: the state (DC 1.6), continuations through round 8 and how a
    stopped one counts (DC 4.1), Y's own from Y only with a member made after s (DC 4.2), the holder weighting's call
    (DC 1.4), seeds with exact tokens, the order of suffixes and places for stage 2 and R8 (DC 1.4, 5.2; PC R8), R8's
    own seeds, the labelled weighting by knot numberings only (DC 1.2), stage 2 and m (DC 4.4, 5.2), "seed" for
    "generator string" (ticket A's D 9 word).

## Section 17, optional

- **HOLD and STEPS-2 on the five-knot sample**: taken, on the first 300 five-knot starts of the order under parity, once
  each (DC 1.3, PC R5).
- **q₁ at any round, reported**: taken (DC 3.3, 4.3; PC17).
- **Ticket A's designs under sampled takes**: taken as R0b and run in scratch (item 11 above).

## Sections 1 to 16, item by item

- §1 scale: applied (claim §1 "The scale"; PC "What a result would and would not show").
- §1 "need": applied (PC, "What the study can say and cannot").
- §1 what follows a hit: applied (PC, "What follows a case").
- §1 many separate origins and a copier of whatever it meets: applied in part: the first is §2's later ticket; the
  second is said in "A candidate seen again would show … not a copier for a registered class".
- §1 "a case is one sample; a copier is a rate": applied as worded (claim §1).
- §2 all items: applied as worded (claim §1; C-S6; PC stop rule).
- §3 rations, treatments, MET and STEPS-1, demand, the birth record, implied births, joins, T1 and T2, pairs, seeds:
  applied as worded in Lemma C-S1 (a) to (h); "Markov process on structures" repaired to "on finite states … with their
  bars, retirements and record of parents" (PC, "In standard terms").
- §3 the draft's reason wrong: applied (c).
- §3 the citation is a hole: applied (the lemma, and why DB 7 does not suffice).
- §3 the guard: checked (see the report); applied in (g).
- §3 status, thinness, allowed wording, R7 and R8 additions: applied as worded.
- §4 C-S2 right, with the check of ties: applied, and checked: no tie at round 0 under not-all-equal in any of the 3,376
  starts. **One sentence corrected against the engine**: "every ration gives a one-parent birth at least two fresh
  distinctions" is not right under the fresh count by distinct inputs when the one-parent birth takes a distinction (p =
  2: FLOOR1 gives one); the conclusion holds because such a birth has three places. Written: "every birth at least one,
  a birth with a single input at least two, so every knot made has at least three places".
- §4 C-S3 gap: applied (item 6). §4 C-S6: applied.
- §5 all items: applied (items 1 and 5); the masked control's emptiness for from both added.
- §6 all items: applied (item 7).
- §7 form, values, ticket A's reading, wholly apart, "X always made", DC 6 against claim §7: applied as worded; "wholly
  apart" removed no pair under STEPS-1 in scratch (0 of 20,169) and 20 of 507 under HOLD; cases reported by s; DC 6 and
  claim §7 now say the same ("made" only with both X and Y made patterns and a meeting through made knots).
- §8 all items: applied (item 9).
- §9 the family and the swaps: applied; the post-hoc STEPS-1 and the strict values reading disclosed; the cheap repair
  taken (optional item).
- §10 all items: applied (item 8). "I cannot check the frozen predictions of tickets A and B": no change asked.
- §11 cost: applied as worded (the sentence in PC, "Runs"; 8 rounds kept; the order of running registered, DC 1.5).
- §12 all items: applied (item 13).
- §13 all items: applied (item 11).
- §14 "a case": kept. "a case that needs the meeting": replaced by "a case met more often with Y", "needs" kept only for
  none of 1,000 in both controls without the meeting. "discovery / confirmation": replaced by "passes at 100" /
  "confirmed". "a candidate found": replaced by "a candidate seen again". "a case with no measured rate": replaced by "a
  one-history case", with its numbers. "values by X": replaced by "values, both from X". W1, W2, T1, T2: replaced by the
  census, labelled, take-by-take and holder weightings (letters remain only inside the scratch's literal seeds, quoted
  as code). "the null pairs": replaced by "the unmet pairs". "the continuations of a pair; a sampled growth": kept.
  "hit" and "soup": only in his quotation and as 'his "hit", read' and 'his "primordial soup", read'. "draws": removed.
  "one component frozen": now "barred". "the meeting hands Y's value": now "a birth descended from X hands Y's value on"
  (D 3.4). "the growth holds two patterns": now "the roster had two parts or more". "nearly every round": now "1% of the
  rounds read under MET and 35% under STEPS-1, under parity on the starts of three and four knots and the take-by-take
  weighting". "would be a template replicator": now "the nearest term in that literature". "Control" is defined in DC 0
  in its three phrases.
- §15 the eight answers: followed.
- §16 the four sentences for the owner: adjusted to the registered numbers and the masked result, at the end of the
  report and in PC; the five over-statements removed: "CC-1 fails everywhere" → "not found; bounded"; "cannot recur",
  "no longer threatens a result" → the allowed wording; "Every MET form case is the law's own" → "none was shown to be
  met more often with Y" (claim: "were met with Y barred as often … none passed at 100"); "X does not leave two of it
  more often…" → said of the two cases only; "every start of up to five knots read" → "under parity".
