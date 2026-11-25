# Changes from the second version, item by item (the advisor's second look, `reach_advisor2/answer.md`)

"Applied" = applied as worded; otherwise the change or the reason is given. KD = `definitions_v3.md`, PR =
`preregistration_v3.md`, claim = `claim_v3.md`.

## The scratch check that comes first

- The amended gate on Ring(33, 2) and on the comb — **run** (PR, Known 2): Ring(33, 2) gives **no gate at 66 or 132 rounds**
  and **the same power 1 from every knot examined at 264 rounds on [16, 132] and at 528 on [16, 264]** (161 knots, spread
  2.02, start knots 1.02 and 1.03), scaling holding; the comb gives no gate (as required). The ring does give the same j
  from every knot examined, so the final versions were written. The advisor's hand figures for made knots are right (2.562
  and 2.063); its start-knot figure at r = 32 is close (1.063 against its 1.05), but its start-knot formula r² + 1.5r + 1 is
  wrong: the start knot reads 2r² + 2r + 1 to r = (n − 1)/2 = 16, then rises by n + 1 a step to 33² at r = 32. Consequence,
  **against the advisor's section 1**: "with j = 2 on [4, n − 1] listed before it" fails for the start knots, whose own
  C_u/c_u on [4, 32] is 2.41 > 2; only the made knots read j = 2 there. P6 and claim 2 say so, and the bare rings are run at
  264 and 528 rounds (cheap), since j = 1 needs a ≥ 16 and z ≥ 128.

## Section 8, required, in order

1. The gate per knot, the spread in bands with start knots apart, the canonical range, P6 and claim 2 — **applied** (KD 4.1–4.3, P6, claim 2), with P6 corrected as above.
2. Run 1 a screen; the full gate in run 2 with the census sample; P5 — **applied** (PR runs 1 and 2; P5 marked (a) on two named starts where the amended gate was run, (c) elsewhere).
3. Class (c) off by one; rule of three per class and "of that class" — **applied** (KD 2.3 uses ⌊s_min/2⌋ − 2 ≤ s ≤ ⌊s_min/2⌋ with T = 66; KD 4.4).
4. The growing end — **applied**: "never: growth ended" (KD 5.5); three nested strata and headline levels (KD 5.8, 5.9); |κ| primary, "how strongly related, either sign" (claim §1, KD 5.2, 5.6); the member shuffle as the reference, the pair shuffle kept as descriptive (KD 5.7); the statement on loose counts in the advisor's words (PR, Known 6; its figures checked against my data: 17,448 − 201 = 17,247; 13,695 + 201 = 13,896; 59,100 = 53,662 + 5,438).
5. The table — **applied and run**: "the law CAP-3(RETIRE), cap and treatment together" (claim 1); the separating arm L9–L11 run on the same 64 starts (PR, Known 3); P1 to P4 as shares on births per round. **Its result partly refutes the second version's reading**: without a cap, retiring alone gives births of degree 1 in 49 of 64 starts (all 49 also degree 1 under the cap of three); the cap stops births rising faster (degree 2 in 2 of 64 without a cap, in none with caps of 2, 3 or 4).
6. RATIO floor 1.25, ENDED with stalled and jammed, j from 0 to 3, verdicts for P, KD 2.1 without "always" — **applied** (KD 3.5, 3.6, 3.2, 2.2, 2.1).
7. Run 4 — **applied**: claim 4 at rounds 1 to 10 and 25; KD 6.2 amended; 100 later knots per run (class `later-knots`); the two take seeds named `takes:1`, `takes:2`; run 4 timed on 20 runs in scratch (0.03 s mean), which replaces the second version's 2 s estimate.
8. The helper's undefined items — **applied**: the bare rings' law (L0); the knots examined and the range of each hand-built control (KD 8; R_40 replaced by R_400 and T_9 by T_12, because R_40 cannot reach z = 32 and T_9 has too few terms for LINREC's fit and 8 verified terms); exact seed spellings (KD 2.4); the guard's limits as numbers (KD 7.4); the labelled and history weightings stated (KD 7.5, 5.2); the 4n numberings stated (KD 7.3); a count-based stage cap and a 60 s process-time limit per stage (KD 7.6).
9. Run 3 cut and reconciled; run 4c conditional; run 1 re-timed — **applied** (PR runs table; run 3 about 11 min; run 1 re-timed with the counts at 15.9 s per start for its 11 laws, so run 1 is about 58 min and a cut leaves a prefix).
10. P16 cut; P9's strictness; replications; the estimator — **applied** (old P16 now a registered question; old P9, now P10, uses "rise by at most 2" with both ratios reported; P12–P15 marked replication; KD 7.5's estimators).
11. Words and owner sentences — **applied** (section 6 words below; section 7 sentences in the report).

## Optional

- The m-phase form — **taken**: it adds nothing to a run's time (the same counts, read again) (KD 3.2).
- The class near 3·s_min/4 beside the gate — **taken** as class (d), in run 2 only, read on its own kept range from the same grown structures; it adds counts but no growth (KD 2.3).
- γ divided by the two members' own all-equal shares — **not taken**: it needs one more contraction per member per stage, and the coordinator's instruction limited optional items to those adding nothing.
- Run 5 limited to the laws with predictions — **taken**: L0, L1, L3, L6, L7.

## Other points of sections 1 to 7

- §1 question 1 ("where the number of parts is fixed", strike "always") — **applied** (KD 2.1, claim §1).
- §1 question 2 (no class near 3·s_min/4 in the gate) — **applied** (class (d) beside only).
- §1 question 4 (one knot: C/c ≤ 2 admits exponents within a third of j) — **applied** (KD 3.4).
- §1 waiting laws with small s_min — **applied** (KD 2.5: the number of runs with s_min below 32 is reported).
- §1 LINREC ambiguity and order — **applied** (KD 3.3: 8 verified terms beyond the 2k fitted; least k first).
- §2 question 5 (ρ fails at one step by sign) — **applied** (KD 5.6: sign counts beside the ρ swap).
- §2 start 157 has S = 0 — **applied** (PR Known 7, P12).
- §2 under L0, δ = ws — **applied** (KD 5.5).
- §3 run 4b probe in run 0, capped at 10 minutes, "argued, unchecked" otherwise — **applied**.
- §3 even rings — **applied**: nothing is said of even n.
- §3 T9, T10 never pooled with uniform takes — **applied** (KD 7.1).
- §4 the wording beyond the data ("each of which gains one member", "most; some", "POWER(2) of H", "the law sets the 2") — **applied**; counts given (PR Known 3).
- §4 refutations — **applied** in P2, P3, P4, P7, with one change: the advisor's "the same pattern under (ORD, CANCEL-RETIRE), which would make it the treatment" is already partly met by the arm I ran (49 of 64 of degree 1 without a cap), so P3 registers what separates them instead: degree 2 appears under L9 and not under any cap.
- §5 run 2 enlarged with the first 50 five-knot starts and the small starts of degree 2 under L0 — **applied with a change**: "degree 2 or more" (9 starts: degree 2 at 19, 164, 172, 178, 179, 214, 219 and degree 3 at 177, 218), recorded in run2_small_starts.json.
- §5 run 1's 28 minutes omitted the counts — **re-timed**: my first timing did include the counts from 21 knots per run; the new timing with 16 made knots and the guard multiplied by ten is 15.9 s per start for 11 laws, so run 1 is about 58 minutes with the separating laws added.
- §6 P10's evidence outside the registered stages — **applied** (claim 4 now at rounds 1 to 10 and 25).
- §6 the parent-step swap null outside the start by Lemma E — **applied** (KD 1.6, scaffold table).
- §6 Lemma F's induction — **applied** (KD 2.6).
- §6 words — **applied**: "rank" and "least number of distinctions in one rule" for Λ_t; "more strongly related" and "less" for the order; "rate" removed from KD 0 (it no longer names anything); "linear space" with the literature's name marked (binary linear code); "slice" marked as the literature's; "grid" and "square" only in the drawn weave control; "most" and "some" replaced by counts or "at least one".
- §7 owner sentences — **applied** with the added sentence adjusted to the separating arm (report).

## Files

`claim_v3.md`, `definitions_v3.md`, `preregistration_v3.md` (opening ready for the line "Frozen on 2026-11-25 (UTC) ..."; headers say neither "draft" nor "frozen"; links written for research/KNOTS-WITHIN-REACH-20261125-001/ and research/KNOTS-WITHIN-REACH-20261125-001A/); `survey_v3.md` (from v2: no private paths, links to the final names, one blur removed); `v3_data/`: census_starts.json, named_starts.json (with R_400, T_12, the comb), five_knot_order.json, run2_small_starts.json. Earlier versions are left in place.
