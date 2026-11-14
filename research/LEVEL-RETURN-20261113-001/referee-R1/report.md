# Referee report LEVEL-RETURN-R1 (Codex-assisted, fresh code)

**Verdict: Confirmed with fixes, with one Block on the evidence for "certified".**

**The mathematics holds, and one part is stronger than claimed.**
- **R2 is proved at every level,** by an independent product automaton, and it handles the identity word and dropped knots
  correctly.
- **R4's "exactly two knots" is now proved for every even level ≥ 4**, not only computed to 14.
- **Rigidity is freshly certified at levels 6, 8, 10 and 12,** and the implication from rigidity to death is valid.
- **The sampled high-level verdicts are freshly recertified.** That is 12 of the 13 dead and all 13 alive cells of the seven at
  levels 13 to 16, and 30 of 34 cells overall, with no disagreement.

**The Block.**
- **What is missing.** The registered runs keep no CNFs, proofs or models, and none of the proof hashes that the pre-registration
  promised.
- **What follows.** "294 dead with LRAT refutations checked" cannot be replayed, so the owner's point (b) cannot be answered on the
  original proofs.
- **What it does not touch.** The verdicts themselves; they are recertified where sampled.

**How the work was split.** The background referee thread owns the verdict.
- **The referee.**
  - Checked the objects gate and the rigidity-to-death logic.
  - Classified the fixes.
  - Kept the 387 MB of fresh certificates on disk with their hashes (`large_file_hashes.json`).
- **Codex.** The Codex command-line tool, at the owner's choice of model and effort, recomputed from fresh code in about 33 minutes.
  It used the earlier ADDR-KNOTS referee's independent RUP checker.
- **Isolation.** It opened none of the study's Python or C. It wrote only in `codex/`, starting with `codex/codex_report.md`, apart
  from one disclosed deviation: early proof traces went to /tmp.
- **Advisor.** The advisor model was not consulted.

## 1. The objects gate

`prior-work line: ok`.

## 2. The refutations (point b; Codex)

**No original proofs to check.**
- **What the registered directories hold.** Records only, with no CNFs, LRAT/DRUP proofs or models. The 294 dead rows carry pattern
  hashes, not proof hashes, although the pre-registration promised to retain proof SHA-256 values.
- **What that means.** There is no original CNF to compare and no original proof to check independently.
- **The verdict.** **Block** (the "certified" evidence claim as stated). Retain or regenerate the certificates, and record their
  hashes.

**Fresh recertification instead.** The rebuilt CNF has both NAE clauses per distinct-image knot and a complement-symmetry unit.
Proofs were checked by hint-free RUP with the earlier referee's `check_rup_fast`, which uses no solver code.

| The seven, levels 13 to 16 | Registered | Freshly certified |
| --- | --- | --- |
| alive cells | 13 | 13 (models checked against every knot) |
| dead cells | 13 | 12 (#2 at 14: a 2.5-million-step proof timed out at 600 s) |
| undecided cells | 2 | rebuilt, not solved |

Six more cases in five other patterns give 4 dead and 1 alive certified, plus 1 over budget. There is no decided disagreement
anywhere. Controls pass: the Fano pattern is refuted, and non-RUP, truncated, malformed and out-of-bounds proofs are rejected.

## 3. R2, all levels (point a; Codex)

**Direct checks.** Parity is a state of #2 at every odd level from 3 to 21, and first XOR last is a state of #3 at every even level
from 2 to 22.

**An independent all-level argument.** It is a product automaton over three things: the three residual map words, the state's
memories, and three bits recording whether each pair of images has differed. It also tracks the length's parity.
- **The search.** It exhausts the reachable configurations (39, 19 and 27 per placement for #2) and finds no violation.
- **The interpretation.** It is proved by induction on the input prefix.

**The identity word and dropped knots are handled correctly.** Both rules are essential: at input `010`, #2's placement [1,9,10] has
images 101, 101, 000 and is correctly dropped. Replacing the identity by map 0 produces a false counterexample, which the argument
detects. **Not a block.**

## 4. R4, "exactly two knots" (point c; Codex)

**Proved for every even n ≥ 4.** The product automaton shows that the retained violating inputs are exactly the language (00)+1(0|1)
for placement [0,8,10], and none for the other two placements.
- **The images.** For x = 0^(n−2)1b they are 0^(n−2)1b, 00 1^(n−4) 0 (1+b) and 0 1^(n−3) 0 b. These are pairwise distinct, so they
  form exactly two knots.
- **Level 16.** The reduced pattern keeps parity and its complement as states at every even level, which settles existence at level
  16, where the registered SAT run timed out.

The study's "computed to 14" can become "proved". **Not a block** (an upgrade).

## 5. R5, rigidity (Codex)

**Fresh certificates at 6, 8, 10 and 12.** Codex fixed X_0 = 0, blocked the parity assignment, and refuted with DRUP checked by the
independent checker (53, 654, 6,487 and 47,750 steps). Level 4 is a checked non-rigid control.

**The implication is valid.** A part's states include the whole's, so if the reduced pattern is rigid, the whole has at most parity
and its complement. Both violate the two knots, so the whole is dead.

**Uniform rigidity is open.** With t_x = s_x ⊕ parity(x), each retained knot gives t_a = t_b ⇒ t_c = t_a, and a finite induction
forcing t to be constant has not been shown. **Narrowing:** keep "rigidity at every even level is open".

## 6. Wording (point d; Codex)

1. **"No state of this automatic kind exists for the other five".** Write "none was found among the feature automata tried (up to
   424 states)". **Narrowing.**
2. **The unqualified reading.** "The only states are parity and its complement" and "forces ... at every odd level" go beyond the
   evidence.
   - #2 has other states at levels 3 and 5 (for example `01101000` at 3).
   - Its odd-level rigidity records run from 7 to 13, and level 15 is undecided.
   - Conclusion 4 needs R5's lower bound of level 4: #3 has non-complementary states at level 2.

   **Narrowing.**
3. **The totals.** 775 cases, 420 alive, 294 dead and 61 undecided recount correctly from the records. R1's high-level cells are
   13 alive, 13 dead and 2 undecided, as stated. **Not a block.**

## Fixes for the thread

1. **Retain the CNFs and proofs, or regenerate them, with their hashes** as the pre-registration promised. Until then, say that the
   294 refutations were checked at run time and are not archived, and that 12 of 13 sampled high-level ones were independently
   recertified. **Block** (the evidence claim).
2. **R4.** Upgrade "exactly two knots, computed to 14" to proved for every even n ≥ 4, citing the product argument. **Not a block.**
3. **The feature-automaton sentence.** Narrow it to the automata tried. **Narrowing.**
4. **The rigidity wording.** State the lower bounds and the odd-level range, and give the counterexamples at levels 3 and 5. Keep
   uniform rigidity open. **Narrowing.**

## Files

`codex/`: Codex's report and evidence. That covers `automata/` (the uniform proof and explicit automata), `rigidity/` (CNFs, proofs
and results), `certificates/` (fresh certificates and models), `rigidity_argument.md`, `wording_results.json` and the summaries.
Files over 2 MB stay on disk (`.gitignore`), with their hashes in `large_file_hashes.json`.
