# Referee report TRUE-BOND-R1 (lean, Codex-assisted, fresh code)

**Verdict: Confirmed with fixes: one Block, two Narrowing, three Not a block.**

**The method and every recomputed value hold.**
- **The objects are right.** The main run uses the fixed-point side table, which is the true bond with members at any depth.
- **The cap hides nothing,** and the uniform truncation is the right finite object for the gate.
- **Fresh SAT agrees.** All 48 values at h ≥ 2 match on 8 small families, including 911's shortening.

**The Block: one sentence of Conclusion 3 is contradicted by its own data.**
- **What the note says.** The four families whose deficit grows (269, 302, 642, 908) are described as having a lowered rate that
  keeps growing.
- **What the data show.** Their true least bond is flat at 3 through depth 7, while the ray bond rises to 6.

**The Narrowing on selection.** The families read deep enough are mostly ones without shortening, so "growth survives" rests on 2
and 9 shortened families.

**How the work was split.** The background referee thread owns the verdict.
- **Codex.** The Codex command-line tool, at the owner's choice of model and effort, recomputed from fresh code. It was barred from
  the study's own folder, and its log shows the folder was not opened. It used 2 processes and under 200 MB in about 8 minutes, and
  wrote only in `codex/`, starting with `codex/codex_report.md`.
- **The referee.**
  - Read the study's code to see which object the main run computes.
  - Checked the selection and the four families from the result rows.
  - Verified Codex's Block finding.
- **Advisor.** The advisor model was not consulted.

## 1. The objects (the referee and Codex)

**The main run computes the true bond.** It calls `generic_fixed_point(L_ray(s) − 2)`, the least-cost side table closed over all
heights. That is the spec's L(s), with members at any depth.
- **Why that is right.** Every bond has finite member depth, and identical summaries act identically in every parent.
- **Where the truncation matters.** The "uniform-depth truncation" the owner settled on (side tables of height D − j at C_j, with
  D = s + h) is used only for the finite gate. There it is the right object to compare with brute force at the same truncation.

**The cap hides nothing.** A bond of size at most L_ray(s) holds a top port and an own distinction of C_s. Its side members
therefore number at most L_ray(s) − 2.

**L ≤ L_ray holds by construction.** A ray bond is a bond of the same infinite relation, so "never lengthens" is a consistency
check, not a finding.

## 2. Fresh recomputation (Codex)

**The method.** Direct satisfiability on truncations to depth s + h, with members anywhere, on the seven smallest study families
and 911, for s = 1, 2, 3 and h = 1, 2, 3.
- **The match.** All 72 minima were found, and all 48 at h ≥ 2 equal the recorded L.
- **Family 112.** It shows why depth matters: at s = 2 it falls from 4 (h = 1) to 3 (h = 2), using a side member at depth 4.
- **Family 911.** At s = 2 it gives 3 against L_ray = 4, with the witness spelled out.
- **What this does not show.** It checks small cases. It does not prove depth-free lower bounds for answers of size 4.

## 3. The four families with growing deficits (Codex caught this; the referee verified it)

| Family | L, depths 1–7 | L_ray, depths 1–7 | Status |
| --- | --- | --- | --- |
| 269, 302, 642, 908 | 3, 3, 3, 3, 3, 3, 3 | 3, 4, 4, 5, 5, 6, 6 | timeout after depth 7 |

**What the note says.** Conclusion 3 calls these "a side branch lowers the rate, from one member per level to one per two, without
stopping the growth". The Answer says "in a few it lowers the rate of growth".
- **What the data show.** The true least bond does not grow at all in the depths read, while the ray bond doubles. These four are
  the strongest evidence in the run *against* "growth survives".
- **Why the headline missed them.** They stopped at depth 7, so they are outside both the 37 and the 75.
- **The verdict.** **Block** (the sentence as published).

## 4. Selection (the referee and Codex)

| Group | Families | Shortened somewhere |
| --- | ---: | ---: |
| reached depth 12 | 37 | 2 (5%) |
| reached depth 8 or more | 75 | 9 (12%) |
| reached 6 to 11 | 77 | 20 (26%) |
| reached 5 or less | 112 | 40 (36%) |

**The 37 are smaller families.** Their median is 94 ray-graph nodes against 282.

**Shortening makes the computation harder,** so the families read deep are mostly ones where side branches change nothing.
- **What the headlines rest on.** "37 of 37 grow" and "75 of 75 grow" are informative only for the 2 and 9 shortened families among
  them (273 and 1332, then 230, 296, 332, 382, 660, 1128 and 1287).
- **What those show.** All of them grow, but mostly by one member over six to eight levels.
- **The 35 and 66 others.** They have L = L_ray at every depth read, so their growth is the ray's growth, already proved.
- **P3.** It is undecided on its registered denominator, not held.

## 5. The rest

- **The roster.** The 226 families appear once each, and the statuses add up.
- **The two errors.** Families 248 and 1288 hit `SystemError: error return without exception set` in the bond search, at depths 3
  and 6. The rows do not show the cause.
- **P1 failed honestly.** At least 62 of 226 are shortened, against a registered limit of 20%.
- **The Reading.** "No route skips a level ..., so the reach still lengthens" does not follow. Passing through successive levels
  does not force more chosen members, and the four flat families show exactly that.

## Fixes for the thread

1. **Replace the growing-deficit sentence.**
   - Families 269, 302, 642 and 908 have a true least bond flat at 3 through depth 7, while the ray bond reaches 6. Say so.
   - Remove "in a few it lowers the rate of growth" from the Answer.
   - Note that these are the strongest evidence against "growth survives".

   **Block** (contradicted by the data).
2. **Restrict "growth survives".**
   - Say that the families read deep are mostly unshortened: 2 of the 37 and 9 of the 75 are shortened. Those 2 and 9 grow, by
     about one member over six to eight levels.
   - Say that P3 is undecided on its registered denominator.
   - Drop "not an artefact ... in every family where this could be checked" as a general reading.

   **Narrowing.**
3. **The Reading's route argument.** Withdraw "no route skips a level, so the reach still lengthens". **Narrowing.**
4. **Note that L ≤ L_ray is by construction.** **Not a block.**
5. **Report the two SystemError failures** as unexplained. **Not a block.**
6. **The gate.** Keep it as stated. The fresh SAT check agrees on 48 of 48 values at h ≥ 2. **Not a block.**

## Files

`codex/`: Codex's brief and report, `recompute_sat.py`, `verify_recomputation.py`, `audit_claims.py` and their JSON.
