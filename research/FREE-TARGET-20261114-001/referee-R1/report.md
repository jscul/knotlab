# Referee report FREE-TARGET-R1 (the proof as the main object; Codex-assisted, fresh code)

**Verdict: Confirmed with fixes.**

**The headline survives.** In 43 of the 66 every-path growers, every bond from a top port to any copy at depth s, with members
anywhere, grows at least linearly. That is proved per family by a finite certificate.
- **The proof is sound.** The gap argument holds, and the 8×8 port relations are exactly what it needs.
- **The relations reproduce.** All 161 relations and the 66 semigroup decisions reproduce independently.
- **A direct attempt to break it finds nothing.** 70 exact minima on the 10 smallest certified families, by plain satisfiability,
  all lie at or above the bound and at or below L_path.

**One Block, on claim (iii) as justified.** "Single chains have L_any = L_ray by construction" is false.
- **Why.** The ray bond keeps its members on the prefix down to the target, while the free bond may also use members *below* it.
  Codex gives a counted family where L_any(2) ≤ 4 and no prefix bond exists at depth 2.
- **What survives.** The chains' growth through inf_{d≥s} L_ray(d) ≤ L_any(s), with an existence caveat.

**Narrowings.**
- The constant for the 7 families whose main is a wrapper.
- The several-definition scope.
- "None of the 66 has a bond ...": the search ran on 57.
- The weight sentence.

**How the work was split.** The background referee thread owns the verdict.
- **The referee.**
  - Worked through the gap argument and its premises independently.
  - Recounted the chain census.
  - Classified the fixes.
- **Codex.** The Codex command-line tool, at the owner's choice of model and effort, did the following in about 34 minutes, at up to 3
  processes (one brief fourth-process overlap, disclosed):
  - a direct exact computation with no relation code;
  - a fresh rectangularity computation;
  - an audit of the gap argument;
  - the chain recount.
- **Isolation.** It opened none of the study's Python and wrote only in `codex/`, starting with `codex/codex_report.md`.
- **Advisor.** The advisor model was not consulted for this referee pass. The study's own advisor review is noted below.

## 1. The objects gate

`prior-work line: ok`. The pre-registration lists three searches. It names BRANCH-DEPTH (a fixed target with members anywhere),
TRUE-BOND, TRUE-RATE, BONDS-AND-COUNT and EVERY-RAY as relatives, and states that none reads the minimum over target copies with
members anywhere.

## 2. The gap argument (the referee, then Codex's audit)

**Setting.** Take a path C_0, …, C_s to a target copy. For a stretch from C_j to C_{j+r}, there are three parts:
- **T**, everything outside subtree(C_j), with C_j's ports as interface 1;
- **M**, the own distinctions of C_j, …, C_{j+r−1} and all their side subtrees;
- **B**, subtree(C_{j+r}) below its ports (interface 2).

**Why it works.**
- **What T and B share.** Copies share distinctions only through call arguments. So T and B meet only through M's solutions'
  projection onto (interface 1, interface 2), which is the composed product of the R_i.
- **The pass-through case.** A distinction passed straight through the stretch would sit in both interfaces and force equality,
  which is never rectangular for a complement-closed relation with both values.
- **The split.** If that projection is A × B′, then any set W with no member in M has allowed states equal to a product of an upper
  part and a lower part. A constrained W then has a constrained part, so it is not a bond unless it lies on one side.
- **The count.** A bond holding a top port and an own distinction at depth s therefore needs a member in each of the ⌊s/r⌋ disjoint
  M's. Neither endpoint lies in any M, which gives 2 + ⌊s/r⌋.
- **The other premises.** G is the exact limit projection, by compactness. The 8×8 relations composed are exactly the stretch
  projection, and no finer identity tracking is needed, because identity carried through shows up as equality.

**Codex's audit agrees,** and it adds two precise limits.

**The wrapper families (Narrowing).** In the 7 certified families whose main is a wrapper (main ≠ S, depth counted from the entries),
only s − 1 S-steps lie between the top and depth s. So the proved bound is 2 + ⌊(s − 1)/r⌋.
- **Can it be repaired? No.** In all 7, the main-to-entry relation followed by every length-(r − 1) product is not uniformly
  rectangular.
- **The general lemma.** Codex also built a three-definition control, outside the 66, where the unshifted bound fails: a 3-member
  bond to depth 4 against a claimed 4. So the general unshifted lemma is false.
- **What it changes.** The rate 1/r is unchanged, and the direct checks found no violation in the 7 themselves. Conclusion 2 should
  give 2 + ⌊s/r⌋ for the 36 with main = S and 2 + ⌊(s − 1)/r⌋ for the 7.

**What the argument covers in several-definition families.** "Copy at depth s" means a copy of the ray definition S along its calls.
- **The count.** Nine of the 43 have several definitions, and four contain another self-holding definition.
- **Why they are covered.** In those four, the other definition has no own distinctions even after inlining, so it adds no target.
  Its constraints still enter through G. The argument therefore covers every eligible deep target here.
- **The limit.** It does **not** extend automatically to another recursive definition with its own distinctions. Bonds that end in
  such a definition's copies are outside the R_i products. That matters for CENSUS-FORGET's 657 single-call families. **Narrowing**
  (the scope statement).

## 3. A direct attempt to break the bound (Codex)

**The method.** For the 10 smallest certified families (7 with r ≥ 4, including both wrapper kinds), Codex built every copy to depth
s + h with G below. It then searched supports of increasing size anywhere in that tree, against every depth-s own distinction, using
satisfiability and exhaustive checks of every one-forgotten subset, with no relation code.
- **The results.** 70 exact minima across 92 attempted points (33 complete h = 1/h = 2 pairs). Every exact value equals L_path,
  satisfies the lower bound (shifted for the wrappers) and agrees between cutoffs.
- **What the finite search cannot show.** Deeper members than the cutoff are not excluded. The infinite lower bound rests on the
  proof in section 2.

## 4. Rectangularity (Codex)

A standard-library enumerator, fresh, reproduces all 161 R_i, every product-set orbit, all 43 least r (2: 9, 3: 14, 4: 6, 5: 9, 6: 5)
and all 23 recurring non-rectangular words. It follows the sequence to repetition, with no length cap. Controls pass. **Not a block.**

## 5. Claim (iii), the chains

**The label.** It is honestly marked "added at the close".

**The count.** It is not "one definition, one SELF call".
- **The literal class** gives 4,035 distinct families and 4,478 draws, which I recounted from the census.
- **The reported 5,190 and 5,633** reproduce only when finite helper definitions and wrappers are allowed, with S and main each having
  one SELF occurrence (Codex). State the filter. The percentages are sample weights: 5,633/223,261 = 2.52% and 5,633/13,279 = 42.4%.

**"L_any = L_ray by construction" is false.** L_ray keeps its members on the prefix down to the target; L_any may use members below
it.
- **Codex's counterexample.** In a counted family that reduces to the chain NAE(a, b, c), NAE(b, c, d), …, the set {a, b, d, e} is a
  bond to depth 2 that uses e below the target. No prefix bond exists at depth 2.
- **What holds instead.** A bond's deepest member at depth d ≥ s makes it a prefix bond at depth d, so
  inf_{d≥s} L_ray(d) ≤ L_any(s) ≤ L_ray(s).
- **What survives.** Karp's uniform lower bound on L_ray therefore transfers, and the chains' linear lower growth stands wherever a
  bond exists.
- **The existence caveat.** 15 counted rows have depths with no ray bond, 12 of them beyond depth 20.
- **The verdict.** **Block** (the "by construction" sentence). The conclusion survives with the inequality and the caveat.

**Prior work.** A single chain as a ruler is the program's earlier result: LOGIC-AXIS, and the chains of RANDOM-FATES-B. Say that
(iii) transfers it, not that it is new.

## 6. Wording and the unresolved (points 3, 4 and 7)

**"None of the 66 has a bond of at most 5 members ...".** The bounded search ran on 57 families. It skipped 9 with main ≠ S: the 7
certified wrappers and 2 unresolved. Say "no bounded certificate was produced; the eventually-periodic test ran on 57". Keep
"boundedness along depth-dependent paths is not tested", which is EVERY-RAY-R1's counterexample shape. **Narrowing.**

**"About 3% of all nested weight".** It combines the chain draws with the 43/300 sample share applied to another stratum, against the
frozen no-extrapolation rule. Remove it from the conclusions, and report 43 of 66 and 43 of 300 as counts of certified growers.
**Narrowing.**

**"Counts depth".** With the shifted constant and existence from L_path, the 43 do have a proved linear lower bound and an upper bound
from L_path. Keep it as a lower bound, with no exact rate. **Not a block.**

**Wilson.** The upper end for 43/300 rounds to 18.8%, not 18.7%. **Not a block.**

## Fixes for the thread

1. **Claim (iii).** Replace "L_any = L_ray by construction" with inf_{d≥s} L_ray(d) ≤ L_any(s) ≤ L_ray(s).
   - State the counting filter: one SELF call in S and main, with helpers and wrappers allowed.
   - Note the 15 rows with absent depths.
   - Cite LOGIC-AXIS and RANDOM-FATES-B.

   **Block** (the sentence; the conclusion survives with the inequality).
2. **The bound.** Give 2 + ⌊(s − 1)/r⌋ for the 7 wrapper families, and drop any general unshifted statement. **Narrowing.**
3. **The target in several-definition families.** State that it is a copy of S, and that coverage holds here because the other
   self-holding definitions have no own distinctions. This scope carries over to CENSUS-FORGET. **Narrowing.**
4. **The bounded search.** Write "no bounded certificate; tested on 57". **Narrowing.**
5. **The weight sentence.** Remove "about 3% of all nested weight". **Narrowing.**
6. **Wilson.** Correct the rounding to 18.8%. **Not a block.**

## Files

`codex/`: Codex's brief, report and evidence. That covers `direct_bonds.py`, `validate_direct_search.py`, `relations_audit.py` and
`chain_census_audit.py`, the notes `gap_audit.md` and `chain_wording_audit.md`, and the JSON and JSONL results.
