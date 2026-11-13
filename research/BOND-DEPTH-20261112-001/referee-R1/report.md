# Referee report BOND-DEPTH-R1 (lean, Codex-assisted)

**Verdict: Confirmed with fixes: two Block, two Narrowing, two Not a block.**

**The finite-depth values are right.** That covers L(s) to depth 30, the validation and the merge.

**The classification built on them is not.**
- **"Growing" cannot happen by construction.** The repeat detector normalises by the minimum cost over all states, and that minimum
  is 1 at every level.
- **"Bounded" includes 10 families whose ray bonds vanish.**
- **The undetermined families are mostly bounded or linear.** On samples they settle into bounded values or linear rates, so the
  frozen P1 is unresolved, not failed.

**How the work was split.** The background referee thread owns the verdict.
- **Codex.** The Codex command-line tool, at the owner's choice of model and effort, did the recomputation and critique from a brief
  of repository material only (`codex/brief_codex.md`). It took about 6 minutes, wrote only in `codex/` (starting with
  `codex/codex_report.md`), and changed nothing else.
- **The referee.** It checked the detector independently, by instrumenting the study's own `run_family` (`ref_mn.py`). It also
  rechecked Codex's counts from the merged records.
- **Advisor.** The advisor model was not consulted.

## 1. The repeat detector (caught by both)

`mn = min(layer.values())` is taken over every state, including states that can never close a bond.
- **Why it is 1.** A single top port costs 1. Empty middle selections carry a cost-1 state forward forever, and costs never fall
  below 1.
- **Checked.** The instrumented run shows mn = 1 at every level in rising, flat and bounded families alike (`result_mn.json`).
  Codex's independent replays show the same through 40 levels.
- **The consequence.** The gain of any repeat is 0, so "growing" is unreachable. "Growing exactly 0" and "no family was shown to
  grow" are facts about the detector, not the families.

**A repeat is still sound.** The transition is deterministic and the closing costs are fixed, so L(s + p) = L(s) thereafter.
- **What a repeat certifies.** It certifies a finite bound only when the recurring closing values are finite.
- **The exceptions.** In 10 of the 204 "bounded" families the ray bond vanishes from some depth on: 256, 370, 493, 547, 555, 761,
  764, 909, 954 and 1289. For example, family 256 reads 3, 4, then none. I confirmed this from the merged records.
- **The true limits.** The 194 finite tails are constant 3 (167), constant 2 (17), constant 4 (3), and periodic between 2 and 3 (7),
  per Codex. The reported 173/30/1 were observed minima, not the limits.

**Why it misses.** The detector can miss periodic L(s). States that cannot close keep their relative costs changing, so the whole
vector never repeats even when L does.

## 2. The undetermined families (Codex)

Codex removed states that cannot complete a minimal bond or reach an accepting closing, then checked samples of the 20 smallest
families each, with certificates and a replay to depth 512.
- **20 "rising".** All are eventually linear plus periodic: rate 1 in 13, rate 1/2 in 6, rate 2 in 1.
- **20 "flat".** All are bounded at every depth: 3 in 19 and 2 in one.

**"Rising steadily in 240" is wrong as worded.** 240 is the count with L(30) > L(1).
- **What the records show.** Only 214 rise between depths 20 and 30, which I confirmed from the records. 26 are constant over 20 to
  30.
- **What Codex proved.** The five smallest of those 26 are eventually constant at 4.
- **So the 240 are not all linear.**

## 3. P1

P1 ("at least half bounded") is reported as failed. The census certified 194 to 204 families bounded and left 447 undetermined.
- **Why it is not a failure.** Undetermined is not "not bounded", and the samples suggest most flat families are bounded. P1 is
  therefore unresolved, not failed.
- **The possible range.** With Codex's new certificates, the bounded count lies between 219 and 632 of 664.

## 4. What else holds

- **Validation.** Codex independently matched 24 of 24 cells (8 families at depths 1 to 3) by exhaustive support search, and the
  chains give 4 to 9 = steps + 2. The original 120 of 120 record lacks per-case values, so only this subset was reproduced.
- **The helpers.** There are 831 raw rows: 653 finished families and 11 unfinished ones (485, 751, 840, 869, 933, 1113, 1186, 1222,
  1296, 1315 and 1329). The 150 duplicated indices agree in every scientific field; only `seconds` and `helper` differ. Merging by
  index changed nothing.
  - **The summary script.** `summarize()` neither deduplicates nor handles the unfinished rows, so the merge procedure should be kept
    as code.
- **Settled by construction.**
  - Ray bonds bound the true least bond from above, so a finite ray bound transfers and a rise is only an upper bound.
  - Endpoint minimisation takes some top port and some own distinction at each depth, not a fixed one.
- **"No class in between".** The finite graph gives eventually affine behaviour for each length residue, possibly with different
  rates, or absent, by residue. It does not give one common rate. Codex gives a four-state example.

## Fixes for the thread

1. **Repair or retire the growth detector, and restate Conclusions 2 and 3.**
   - "Growing" is unreachable, since mn ≡ 1.
   - Normalise only over states that can still close a bond, or certify rates as Codex did.
   - Drop the 10 families with vanishing ray bonds from "bounded".
   - Report the recurring tail values (167 at 3, 17 at 2, 3 at 4, 7 periodic) instead of the observed minima.

   **Block** (the classification as published).
2. **P1 is unresolved, not failed.** The certification target was not reached, and the bounded share is between about a third and
   all of the families. **Block** (the headline verdict).
3. **"Rising steadily in 240".** Say 240 rise from the first depth to the last and 214 between 20 and 30. On a sample of 20, rates
   of 1, 1/2 and 2 are certified. At least five of the 26 that are late constant settle at 4. **Narrowing.**
4. **The common-rate claim.** Qualify it by length residue. **Narrowing.**
5. **The helpers.** Keep the merge and summary as code, and note that the records' metadata differ. **Not a block.**
6. **Validation.** Note that 24 of the 120 cells were reproduced independently. **Not a block.**

## Files

- **`codex/`.** Codex's brief and report, `independent_dp.py`, `independent_validation.py`, `verify_results.py`,
  `audit_records.py`, and their JSON.
- **Referee.** `ref_mn.py` and `result_mn.json`.
