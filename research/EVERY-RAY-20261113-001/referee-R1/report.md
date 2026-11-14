# Referee report EVERY-RAY-R1 (lean, Codex-assisted, fresh code)

**Verdict: Confirmed with fixes.**

**The registered per-depth result stands.** For each sufficiently large depth, some path has a short bond. That holds in 204 of the
296 first-ray growers, and 201 of the 204 are now independently certified bounded without a carried port.

**The Answer reads it as one infinite path, which is false in general.**
- **The counterexample.** Codex found a sampled family whose per-depth minimum is bounded at 3 to 4 while every single infinite path's
  bond grows without bound.
- **What is certified.** Explicit uncarried lassos are certified in 188 families. In 13 more none was found.

**Four sentences are false (Block on each sentence; none touches P1 to P3 or the per-depth minima).**
- The single-path reading.
- "The other 4 are carried-only": in fact 3 have no uncarried bond and 1 was unresolved.
- The description of the bounds.
- The pre-registration's "equivalent calls give L_path = L_ray".

**"No correction" is not quite right.** REACH-CENSUS's Answer "another ray seldom contradicts first-ray growth" needs narrowing now
(see section 6).

**How the work was split.** The background referee thread owns the verdict.
- **Codex.** The Codex command-line tool, at the owner's choice of model and effort, recomputed from fresh code. It opened none of
  the study's or the thread's Python, only the data folders. It took about 17 minutes at up to 3 processes, and wrote only in
  `codex/`, starting with `codex/codex_report.md`.
- **The referee.**
  - Ran the objects searches.
  - Judged A80 and REACH-CENSUS's wording.
  - Classified the fixes.
  - Kept the three largest evidence files on disk; their hashes are in `large_file_hashes.json`.
- **Advisor.** The advisor model was not consulted.

## 1. Prior work (the objects gate)

**The objects gate reports that the pre-registration has no `## Prior work in the program` section.** It was frozen at 13:08 UTC on
2026-11-13, before the gate was introduced at 17:36 UTC, so this is a process note, not a fault.

**My own searches** ("least bond over all descending paths of copies", "members-anywhere bond side branches nested") return
PROVED-RATE, TRUE-BOND and BONDS-AND-COUNT. The note's literature line already names BRANCH-DEPTH, TRUE-BOND and TRUE-RATE as
fixed-target studies, and the minimum over descending paths as new. **Not a block.**

## 2. The uncarried figure and the quantifier (point 2; Codex)

**Per depth.** Codex wrote an exact capped-cost DP (costs above a cap are discarded, which is exact for the bounded decision since
costs never fall) and checked every residue.
- **The certificates.** 200 of the 200 uncarried bounded families are certified, and so is the one uncarried-unresolved family:
  201 of 204. The other 3 have a port-map invariant that forbids an empty top-port set on any path.
- **Against the records.** 12,180 comparisons against the 30 recorded depths, with no disagreement.
- **The bounds.** Per-depth uncarried bounds are 3 (26), 4 (169) and 5 (6).

**One infinite path.**
- **Lassos.** Codex found 188 explicit uncarried lassos, with an entry, a prefix and a repeated call word, including 37 of the 50
  mixed cases. 185 are bounded at every depth and 3 eventually.
- **The gaps.** In 13 families no lasso was found; finite automata exclude an eventual bound of 7 in 12 of them.
- **The counterexample.** In the sampled family `[[3,2,[["K",[1,3,4]],["SELF",[2,0,4]],["SELF",[0,3,4]]]]]`, the per-depth minimum
  is 3 to 4 (via `1^(s−2)01`). Yet every single infinite call word has a bond growing without bound, since each copy adds one
  constraint whose ancestry height grows along any fixed word. Codex gives the symbolic argument and checks all 62 words through
  depth 5.

**What follows.** "Some descending path whose bond stays at three to nine members at every depth ... that path" (the Answer) and "only
a mixed path does" assert one infinite witness. Replace them with: "for each sufficiently large depth, some finite path, possibly
depending on the depth, has a short bond". Where a lasso is certified (188), the single-path statement holds. **Block** (the
sentence as written).

## 3. The labels and bounds (Codex)

**The carried-only labels.**
- **"The other 4 only through a carried port".** The frozen split of the 204 is 200 uncarried bounded, 3 with no uncarried bond, and
  1 unresolved. So the uncarried band has 27 unknowns: 200/296 to 227/296, Wilson 62.0% to 81.1%.
- **B's "20 only through a carried port".** That is 15, plus 5 unresolved.
- **The verdict.** **Block** (labels as published).

**The bounds.** "Certified bounds 3 to 9, mostly 3 (100) or 4 (63)" does not match the records. The plain `uniform_cost_bound` values
run from 2 to 14 (97 at 3), and 14 is a loose certificate. Keep plain, uncarried, single-lasso and observed bounds apart. **Block**
(the sentence).

**Equivalent calls.** The pre-registration says symmetry-equivalent calls give L_path = L_ray, "no new content". That is false: one of
the four has L_path(3) = 3 against L_first(3) = 4, and all four are bounded over paths. The frozen denominator can stay as a declared
estimand without that justification. **Block** (the justification).

## 4. The DP, bands, gate chronology and code versions (points 1, 3 and 4; Codex)

**Shared and repeated arguments (point 1).** 18 more several-definition families, outside G-brute's panel, were checked by direct
enumeration. That is 71 complete depth cells, 1,564 paths and 20.6 million assignments, with no disagreement. A synthetic family with
a repeated argument inside one SELF triple also agrees. **Not a block.**

**Bands (point 3).** The 26 unresolved G families stay out of the numerators and enter the band: 68.9% to 77.7%, with a Wilson
envelope of 63.4% to 82.1%. P1 is undecided, as reported. P3's 22.8% upper end is the envelope for 33 to 34 of 200. **Not a block.**

**G-reg (point 3).** The clarification was frozen after the gate results and before the class shares. All 486 single-entry families
pass, and the 9 mismatches all have two or three entries, with class and λ equal. That is not a post hoc loosening. **Not a block.**

**Code versions (point 4).** No resolved-against-resolved conflict appears wherever rows overlap.
- **The limit of that.** B's and B_resume's keys are disjoint, and the 29 phase-2 overlaps ran the same DP version. So equivalence of
  the patch is not tested by these data, only uncontradicted.
- **The verdict.** **Narrowing.**

## 5. The BRANCH-DEPTH cross-check (Codex; my brief's inequality was wrong)

**My brief's suggestion.** I suggested that BRANCH-DEPTH's linear growth would forbid boundedness over paths (L_true ≤ L_path).
Codex shows that this is not generally valid. BRANCH-DEPTH fixes a first-branch target with members anywhere. EVERY-RAY minimises over
targets with members on the path. Neither feasible set contains the other.
- **The counterexample.** In the family above, L_true(s) = ⌊s/3⌋ + 3 for the fixed target while L_path = 3.

**What could be checked.** Only 2 of the 477 one-definition sample families match BRANCH-DEPTH's inventory exactly, both B and
unresolved. There is no contradiction, but the cross-check covers little. **Not a block.**

## 6. A80 and "no correction" (the referee)

**The ray-qualified statements stand.** PROVED-RATE's and BOND-DEPTH's growth statements were stated along the first ray and were
narrowed in place. They need nothing new.

**But REACH-CENSUS's rewritten Answer needs a correction.** It says "another ray seldom contradicts first-ray growth" and that on the
last-call ray a short bond contradicts it in only 31 of 645 growers.
- **Why it misleads now.** Over all paths, per depth, a short uncarried bond contradicts first-ray growth in 68.9% to 77.7% of
  inequivalent-call growers.
- **The fix.** The sentence should name the last-call ray and cite EVERY-RAY's per-depth result. The Reading's "first-ray lengthening
  is the majority ... where a genuine bond exists" should do the same.
- **The verdict.** **Narrowing** for REACH-CENSUS. A80's status, overturned for growth, is right.

## 7. Wording (Codex)

**"Grow along every path".** This is the per-depth minimum growing, a sample statement within the depths certified, so give it as
such. It is not the same as each single path growing; in the counterexample above the reverse inequality fails.

**Prevalence.** Qualify "about seven in ten", "usually" and the decline with the number of calls as statements about this frozen
sample. **Narrowing.**

## Fixes for the thread

1. **Restate the Answer per depth.** Use "for each sufficiently large depth, some finite path has a short bond". Claim one infinite
   path only where a lasso is certified (188), and cite the counterexample family. **Block** (the sentence).
2. **Correct the carried-only labels.** Of the 204: 3 have no uncarried bond and 1 was unresolved (now certified). The uncarried band
   has 27 unknowns. In B, 15 are carried-only and 5 unresolved. **Block** (the labels).
3. **Correct the bounds sentence** to the recorded fields. **Block** (the sentence).
4. **Withdraw the pre-registration's "equivalent calls give L_path = L_ray"** as a justification. Keep the estimand as declared.
   **Block** (the justification).
5. **Narrow REACH-CENSUS's "another ray seldom contradicts first-ray growth"** to the last-call ray, and cite the per-depth result
   over paths. So EVERY-RAY's "no correction" should become one Narrowing against REACH-CENSUS. **Narrowing.**
6. **Code-version equivalence** is untested by the data. Say so. **Narrowing.**
7. **Sample and depth qualifiers** on the prevalence statements and on "grow along every path". **Narrowing.**
8. **The missing prior-work section** predates the gate. The literature line covers the program's relatives. **Not a block.**

## Files

- **`codex/`.** Codex's brief, report and evidence: `lasso_certify.py`, `min_path_certify.py`, `lasso_automaton.py`,
  `direct_brute.py`, `branch_reading_check.py`, `validate_referee.py`, `family_certificates.json` and the summaries.
  `direct_brute_results.json` is committed gzipped. The two other result files over 5 MB stay on disk, with their hashes in
  `large_file_hashes.json`.
