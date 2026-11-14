# Referee report CENSUS-FORGET-R1 (Codex-assisted, fresh code)

**Verdict: Confirmed with fixes, with two Blocks.** The shares barely move, but two statements must change.

**What reproduces.** The forgetting computations reproduce on a fresh 127-family sample, and so does every headline fraction.

**Block 1: "every bond to any copy at depth s" is false for 188 of the 538 single-call non-chains.**
- **Why.** In 153 of them another recursive definition has its own distinctions, so its copies are deep targets that the S-call
  certificate does not cover. In 2 more (and in 6 of the 153) such a definition delays S, reaching S copies through steps the
  certificate never tests.
- **The proof.** Five certified census families have a least bond of exactly 3 at every tested depth up to 11. One has an explicit
  bond of 3 at every depth.

**The corrected share.** Restricted to families the proof covers, it is 7,063 draws: 53.2% of first-ray growth and 3.16% of all
nested draws, against the published 54.6% and 3.25%.

**Block 2.** The chains' "L_any = L_ray by construction" repeats FREE-TARGET's false sentence. The inequality replaces it.

**How the work was split.** The background referee thread owns the verdict.
- **The referee.**
  - Stated the scope question from FREE-TARGET-R1.
  - Checked that FREE-TARGET's own 66 contain none of the families with an uncovered target type or a delayed S (0 of 66), so its
    43 are unaffected.
  - Classified the fixes.
- **Codex.** The Codex command-line tool, at the owner's choice of model and effort, recomputed from fresh code in about 9 minutes.
  It reused only FREE-TARGET-R1's referee code, opened none of the study's Python, and wrote only in `codex/`, starting with
  `codex/codex_report.md`.
- **Advisor.** The advisor model was not consulted.

## 1. The objects gate

It reports `missing epic FORGET-RULE-20261114-001`: the prior-work section names an epic the gate cannot find at the
pre-registration's date. It is a process note. **Not a block.**

## 2. The 657 single-call non-chains: what the certificate covers (Codex, the referee)

FREE-TARGET-R1 found that the gap argument covers targets that are copies of S reached through S's calls, and that it does not
automatically cover copies of another recursive definition with its own distinctions. In the census that case is common.

| Of the single-call non-chains | All 657 | Certified 538 |
| --- | ---: | ---: |
| another reachable recursive definition has own distinctions | 183 | 153 |
| no other recursive definition with own distinctions | 474 | 385 |

**The counterexamples (Codex, direct satisfiability with no relation code).** Five certified census families all have main = S and
fresh r of 3 or 5. At depths 1 to 11, at both cutoffs, Codex took every depth-s own distinction as a target and every explicit copy
as a possible member, and found a least bond of 3 every time: 100 exact minima, global by a second solver.
- **The bound they break.** The claimed bound is 4 at s = 6 (and at s = 10 for the r = 5 family).
- **The mechanism, in `f25a8e17968d`.** Its rules are T(a, b, c) = T(a, c, b), NAE(c, b, t), NAE(a, b, c), and
  S(a, b, c) = T(a, u, b), S(b, v, u). The other recursive definition T keeps the pair {u, main.b} at every depth, so
  {main.b, u, t_s} is a bond to T's own distinction at every depth.

**Delayed S.**
- **What it is.** In `e8ce853eb78a`, another recursive definition has no own distinctions, but it calls S after any number of its own
  SELF steps. So S copies at depth s are reached through steps that are not R_i stretches.
- **The evidence.** Codex found 12 global minima of 3 at s = 1 to 6, against a required 4 at s = 5.
- **How many.** Eight certified non-chains have a delayed S: 6 already among the 153, and 2 more.

**FREE-TARGET is unaffected.** None of its 66 families is among these 186 certified families with an uncovered target type or a
delayed S (referee check), which agrees with FREE-TARGET-R1.

**What the certificate covers.** It covers depth-s targets in copies of S whose ancestry after main consists of S calls, with
2 + ⌊(s − 1)/r⌋ for wrappers. The subgroup it covers for any copy has no other-type own targets and no delayed S: **384 of the 538**
single-call certified families and **1,046 of the 1,080** c ≥ 2 families.

**Block** (the "any copy" claim for the 188 outside that subgroup). It does not classify them as bounded; five are proved bounded.

## 3. Fresh verdicts (Codex)

**The sample.** 120 stratified families (c ≥ 2, the 657, chains; certified, non-forgetting, capped) plus 7 targeted ones, 127 in all.
They cover every recorded r from 1 to 12.
- **What reproduces.** All 127 fixed points, 318 R_i (each by 64 direct SAT queries) and 103 completed verdicts, least r values and
  product-set orbits. **Not a block.**
- **The capped cases.** All 24 sampled capped families have a verified non-rectangular lasso, so they are non-forgetting. "12,772
  exact decisions" should separate the 66 capped. **Narrowing.**

## 4. The chains (Codex)

**The count.** 5,190 families and 5,633 draws need finite helpers and wrappers allowed (S and main each with one SELF occurrence).
The literal one-definition count is 4,035 families and 4,478 draws. State the filter. **Narrowing.**

**"L_any = L_ray by construction"** is false, as FREE-TARGET-R1 showed: a free bond can use members below the target. The
replacement, inf_{d≥s} L_ray(d) ≤ L_any(s) ≤ L_ray(s), carries the linear lower bound wherever a bond exists. 15 counted chains have
missing depths, 12 of them beyond depth 20. **Block** (the sentence). The conclusion survives with the inequality.

## 5. Shares and wording (Codex)

**The arithmetic reproduces.** 7,251/13,279 (54.6%), 1,618/7,646, 1,080/6,989 (15.5%), 538/657 (81.9%), 3.25%, the Wilson
intervals, and outside EVERY-RAY's sample, 1,036/6,686 (15.5%). P1 holds as frozen. These are description-weight fractions of the
census draws.

**The corrected headline.** 54.6% and 3.25% include the 188 uncovered families. The conservative covered subtotal is
5,633 + 384 + 1,046 = 7,063 draws: 53.2% [52.3, 54.0] of first-ray growth and 3.16% [3.09, 3.24] of all nested draws. **Block**
(part of the "any copy" fix above).

**"Undecided, almost all certified non-forgetting"** is correctly worded. There are 6,028 draws, 5,962 non-forgetting and 66 capped,
and a recurring non-rectangular product does not certify a bounded bond. **Not a block.**

**"The limit-only growers never forget".** Write "none certified: 203 non-forgetting and 21 capped", and do not imply that they are
bounded. **Narrowing.**

## Fixes for the thread

1. **Restrict "every bond to any copy at depth s".** It applies only to families with no other recursive definition with own
   distinctions and no delayed S. That is 384 single-call and 1,046 c ≥ 2 certified families.
   - Report the covered share as 7,063 draws (53.2% of first-ray growth, 3.16% of all nested).
   - Cite the five bounded counterexamples and the delayed-S family.

   **Block** (the claim as stated).
2. **The chains.** Replace "L_any = L_ray by construction" with the inequality, state the counting filter, and note the 15 chains
   with missing depths. **Block** (the sentence). The conclusion survives.
3. **The 66 capped.** Separate them from exact decisions; the sampled capped are all non-forgetting. **Narrowing.**
4. **The limit-only growers.** Write "none certified (203 non-forgetting, 21 capped)", not "never forget". **Narrowing.**
5. **The wrappers.** Use 2 + ⌊(s − 1)/r⌋ for the 661 wrapper certificates, as in FREE-TARGET. **Narrowing.**
6. **The prior-work line's missing epic.** Fix it. **Not a block.**

## Files

`codex/`: Codex's brief, report and evidence. That covers `target_inventory.py` and `target_inventory.json` (every family's scope),
`direct_other_targets.py` with its JSONL, `validate_other_targets.py`, `sample_audit.py`, `chain_share_audit.py`, and the
summaries.
