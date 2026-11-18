# Referee report FAR-SIGN-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.**
- **The proofs hold.** L1 to L6 and Proposition 7 check by hand. The referee's own code also reproduces both of Proposition 7's
  fills and the third order.
- **R1 to R6 hold on the referee's own engine,** with fresh seeds and sizes well past the study's:
  - 263 starts, including lines of 34 to n = 56 and lines of 42 to n = 64 (the study stopped at lines of 26, n = 48);
  - the sign is exact, the weak sign, near-pair sign and pair pattern are exact, and F1, T1 and T2 never fail;
  - every treated knot set is in state α or β;
  - L1 and L2 hold on all 3,114,226 treated knot sets.
- **But the headline counts one fact many times (Narrowing, wording).**
  - "None of 147,368 refused fills has the sign" is mostly forced, not tested. Every refused fill that has a treated knot set breaks
    clause (a), and the sign implies clause (a) (proved).
  - The clause-(b) refusals never have a treated knot set at all: 13,325 of 13,325 fresh.
  - So the computed content is two facts:
    - every copy step's treated knot set has the sign (F1);
    - no clause-(b) refusal has the treated shape.
  - R1, R2, R3 and R6 restate these two facts. R3's 1,794 are the copy steps themselves, where L5 forces T1 and T2.
- **The owner's four questions:**
  1. **L1 to L6 and Proposition 7: correct.** One wording point: L5 defines "a base of two orders" only as "complete bipartite
     crossing". By that definition, the base after Proposition 7 (B) is still two orders, although its lattice dimension is 3.
  2. **R1 to R6: confirmed** past the study's sizes.
  3. **"The ablation localises necessity to the middle and near pairs' knots": too strong.** Necessity held only where all three
     pairs had knots. With the middle and near pairs knotted and the far pair not, no copy step occurred at all, so the far pair's
     knot is not ruled out. The pattern does persist past n ≤ 14, in the referee's ablation to n ≤ 20. **Narrowing (wording).**
  4. **The coverage gap is stated fairly, but too weakly.** In every copy step, p is a distinction of the starting line: 3,072 of
     3,072 fresh, never a fill's r or a subdivision's distinction. So the region is never reached, not merely unsampled. The "other
     direction tested there" is forced by L4. **Narrowing (wording).**
- **COPY-CLASS's fold-in (`270dac5e7`, `39cba8eb6`) is faithful.**

## What holds

| Reading | Referee, fresh (263 starts) | Study (165 starts) |
| --- | --- | --- |
| Crossing-making extensions; copy steps | 307,135; 3,072 | 149,162; 1,794 |
| Largest line; largest n | 42; 64 | 26; 48 |
| R0: copy steps with a treated knot set; treated sets with the other orientation of the near knot | 3,072 of 3,072; 0 | 1,794 of 1,794; 0 |
| R1: sign vs SEED (extensions) | 3,072 with the sign; 0 of 304,063 refused | 1,794; 0 of 147,368 |
| R2: F1 (premise ⇒ sign) | 3,072 of 3,072 | 1,794 of 1,794 |
| R3: T1 and T2 under the sign; smaller class ≥ 3 | 3,072 of 3,072; 1,356 | 1,794 of 1,794; 776 |
| R4, R5: pattern, weak sign, near-pair sign (extensions) | each exact | each exact |
| R6: α; β; neither; a fill with both | 3,072; 3,111,154; 0; 0 | 1,794; 1,468,465; 0; 0 |
| R7: copy-class knot sets, copy and refused; closure pictures with both verdicts; marked pictures with both | 3,072 and 105,524; 1 of 34; 0 of 167 | 1,794 and 54,879; 1 of 34; 0 of 138 |
| L1, L2 on treated knot sets | 3,114,226 of 3,114,226 | 1,470,259 |
| Under the sign, both classes chains | 3,072 of 3,072 | not reported |
| Refused: clause (a) fails with a treated knot set; fails without; clause (b), any treated knot set | 233,844; 56,894; **0 of 13,325** | not reported |
| Copy steps whose p is a starting-line distinction | **3,072 of 3,072** | 1,794 of 1,794 not an earlier fill's r |

**The referee's engine** (`referee_sign.py`):
- **Building blocks.** It uses its COPY-CLASS-R1 engine: SEEDK with MID-RULE-R1's `local_fills`, its own crossing graph with r's
  quadrants, and SEED's clauses. SEED is cross-checked against KNOT-SWITCH-R1's `seed_ok`, with 0 disagreements.
- **Readings.** It computes its own roles, its own L1 and L2, the sign, the weak sign, the near-pair sign, F1, T1, T2 (both as L5
  states it and as one whole class), L6's pattern, the states α and β, and a chain test for the classes.
- **Pictures.** It uses COPY-READ-R1's canonical closure class, and a marked picture made of that class plus each split's trace on
  q, a, c and d (relative to p) with a crossed mark.
- **Starts.**
  - Every bracketing of 5, 6, 7 and all 132 of 8, to n = 36.
  - Uniform random lines: 30 of 18 to n = 40, 20 of 26 to n = 48, 12 of 34 to n = 56, and 8 of 42 to n = 64.
  - Fresh seeds throughout.

## 1. The proofs (the owner's question 1)

- **L1.**
  - The three knots pin r as stated:
    - B(p, r, q) forbids p = q ≠ r;
    - B(a, p, r) forbids a = r ≠ p, so where a ≠ p, r = p;
    - B(c, d, r) works likewise.
  - On the P-side state s (s_p = 1): q ∈ P makes the middle knot pin r to 1, and a ∉ P makes the near knot pin it to 1. Otherwise
    only the far knot can pin, which forces s_c ≠ s_d (i) and gives r = s_d.
  - (ii) is the consistency of two pins on one state. Correct.
- **L2.**
  - r lands in the quadrant of its own two sides.
  - If neither split is moved, p is in that quadrant. If both are moved, q is (L1).
  - If one is moved and one is not, the quadrant P(τ) ∖ P(σ) is empty exactly when P(τ) ⊆ P(σ). Then the other three quadrants hold
    p, P(σ) ∖ P(τ) and the outside of P(σ). Correct.
- **L3 and L4.** Correct.
  - The step "an unmoved split separating c from d has d on P" uses both L1 (i) (the moved-kind splits, unmoved only when d ∈ P) and
    L1 (ii).
  - G × M follows, because an unmoved gainer has d ∉ P, so under the sign it is uncrossed, and then it lies in G (L3).
- **L5.** Correct.
  - An uncrossed moved split gains only splits of G, which were uncrossed. No crossed split ends with such a set, because its old
    crossers are crossed. So it has no model.
  - Under T1, a moved crossed split gains G and cannot match M. An unmoved crossed split gains nothing.
  - So the copy step holds exactly when M is the crossers of an unmoved crossed split.
  - On a complete bipartite crossing graph this means "M is one whole class", and that already implies T1.
- **L6.** Correct.
  - Moved and unmoved crossed splits cross: their P-sides hold p, a, c and p, a, d, so the four quadrants hold p, c, d and q.
  - With no three pairwise crossing splits, the moved crossed splits fill one class.
  - The proof says only that the moved ones lie in one class. The unmoved ones lie in the other because each crosses a moved one.
    This step is implicit but immediate.
  - An uncrossed moved split would cross an unmoved crossed one, so T1 holds.
- **The betweenness remark.** Correct.
- **Proposition 7.** Every claim is reproduced by the referee's own code (`referee_sign_P7.json`).
  - The ten states are exactly those its 27 implied knots allow.
  - σ_X crosses σ_0 and σ_2.
  - **(A):** r is fixed on every state; the sign holds; M = {σ_0}; T2 fails; SEED refuses.
  - **(B):** the sign fails; M = {σ_X}; SEED accepts. Of the fill's 29 knot sets (any pairs, irredundant, at most three knots), 18
    have the treated shape and none has the sign.
  - **The third order.**
    - The least cover of the splits by chains of nested sides goes from 2 before (B) to 3 after it.
    - After (B), τ, σ_0 and σ_2 have the pairwise disjoint sides {6, r}, {0, 3} and {2, 5}, which no chain can hold.
    - That is the lattice dimension, read as one chain of cuts per axis.
- **The wording point.**
  - L5 defines "a base of two orders" as crossed splits in two classes with complete bipartite crossing. It does not require the
    classes to be chains.
  - By that definition the base after (B) is still "two orders": its crossed splits are still complete bipartite, K₁,₃. Yet the note
    says (B) "makes a third order".
  - The proofs of L5 and L6 hold for the wider definition, so nothing breaks.
  - The definition should say "two classes", or add "each a chain". Under the sign on SEEDK's runs both classes are chains, 3,072 of
    3,072. **Narrowing (wording).**

## 2. What R1 to R6 test (the owner's question 2)

- **They hold on fresh seeds, past the study's sizes, with no exception** (table above).
- **But they are not independent.** The referee broke the refused extensions down:
  - **233,844 fail clause (a) and have a treated knot set.** By L4, the sign implies clause (a). So none of them can have the sign:
    this is a theorem, not a test.
  - **56,894 fail clause (a) and have no treated knot set.** The sign is not defined on them.
  - **13,325 pass clause (a) and fail (b).** None has a treated knot set, so again the sign is not defined.
- **So "no refused fill has the sign" rests on one computed fact:** no clause-(b) refusal has the treated shape.
- **"Every copy step has the sign" is F1,** since on SEEDK's fills the treated knot sets with a gainer are exactly the copy steps'.
- **R3 is not a separate test.** Its numerator is the copy steps themselves, where L5 forces T1 and T2. R3's content is that no
  refused treated set has the sign, which is the same as R1.
- **R6 states both facts in one line.**
- **R7 (ii)** is implied by R1. The marked picture carries every crossed split's c/d trace, so it contains the sign by construction.
  The note's position table already says that the marks take every split.
- **Fair wording.** "On SEEDK's knot-local fills, two facts hold without exception: every copy step's treated knot set has the sign,
  and no clause-(b) refusal has a treated knot set. With L4 and L5, they make the sign equal to the copy step." The study's 8 of 8
  should be read as two facts, each stated several ways. **Narrowing (wording).**

## 3. The ablation (the owner's question 3)

The referee reran it with its own code, in the study's range (bracketings of 5 and 6, first three bases after the switch,
n ≤ 14) and past it (bracketings of 7 and 8, first eight bases, n ≤ 20). The pattern pq / ap / cd says which of {p, q}, {a, p} and
{c, d} already shared a knot.

| Pattern | Knot sets (range; past) | Copy steps | Copy steps without the sign | Sign sets; refused with the sign |
| --- | --- | --- | --- | --- |
| pq=1 ap=1 cd=1 | 727; 99,718 | 52; 1,106 | 0; 0 | 52; 1,106 — 0 refused |
| **pq=1 ap=1 cd=0** | 253; 84,559 | **0; 0** | — | 0; 0 |
| pq or ap = 0, cd = 1 | 2,490; 627,478 | 932; 47,285 | 688; 35,774 | 244; 11,511 — 0 refused |
| pq or ap = 0, cd = 0 | 832; 579,099 | 89; 17,645 | 89; 17,645 | 0; 0 |

- **Sufficiency is real here, not forced.**
  - With knots on any pairs, many refused treated sets have a gainer: 308 in the range and 80,092 past it fail F1 without being
    copy steps.
  - Yet all 296 and all 12,617 sign sets were copy steps.
  - The study's "SEEDK's bases carry the sign's sufficiency" holds, and holds past n ≤ 14.
  - But the sign never occurred with the far pair unknotted (cd = 0).
- **Necessity.**
  - Copy steps without the sign occur only where the middle or the near pair has no knot.
  - With both knotted, the sign held on every copy step: 52 and 1,106. All of those copy steps also had the far pair knotted.
  - With the middle and near pairs knotted and the far pair not, there were no copy steps at all, among 253 and 84,559 knot sets.
  - So the data cannot tell "the middle and near pairs' knots carry necessity" from "all three pairs' knots do".
- **Fair wording.** "Copy ⇒ sign failed only when the middle or the near pair had no knot, and held on every copy step where all three
  pairs had knots. With the middle and near pairs knotted and the far pair not, no copy step occurred." It is not fair to say "at
  n ≤ 14" only: the pattern persists to n ≤ 20. **Narrowing (wording).**

## 4. The coverage gap (the owner's question 4)

- **True, but understated.**
  - In the referee's 3,072 copy steps, p was always a distinction of the starting line: never a fill's r, and never a subdivision's
    distinction. This holds on lines up to 42 and n up to 64.
  - The region is reached by knot sets: refused treated sets have p from fills 1,396,988 times and from subdivisions 76,617 times.
  - But no copy step lands there. So "copy step ⇒ sign" is untested there because no copy step occurs there, not because sampling
    was thin.
- **A possible lemma.** "On SEEDK, a copy step's shared distinction p lies on the starting line." That is the fair reading of the
  gap.
- **"The other direction is tested there"** is forced. The 623,703 refused treated sets with such a p all fail clause (a), as every
  refused treated set does, and the sign implies clause (a). **Narrowing (wording).**

## 5. COPY-CLASS's fold-in (`270dac5e7`, `39cba8eb6`)

**Faithful.**
- The CORRECTIONS entry states the Block with the right counts.
- It gives the null-comparison lesson.
- It withdraws the G1 capability and corrects the scoring (2 of 4 scored, P4 unscored).
- The note's leftover "Why the far pair" explanation is marked as superseded.

## Fixes for the thread (listed for the owner, not folded in)

1. **The answer and the predictions.**
   - Say that R1's refused side is forced by L4 for every refused fill with a treated knot set, and that clause-(b) refusals have no
     treated knot set (13,325 of 13,325 here).
   - Say that the computed content is F1 together with that shape fact, and that R1, R2, R3 and R6 restate them.
   - **Narrowing (wording).**
2. **L5's "base of two orders".** Say "two classes", or add "each a chain", so that Proposition 7 (B)'s "third order" is consistent
   with the definition. **Narrowing (wording).**
3. **The ablation's sentence.** Use §3's wording: the middle and near pairs' knots are not shown to suffice for necessity apart from
   the far pair's, because that cell had no copy step. Note that the pattern holds to n ≤ 20. **Narrowing (wording).**
4. **The coverage line.** Say "p is a starting-line distinction in every copy step (3,072 of 3,072 here)", and that the converse's
   test there is forced. **Narrowing (wording).**
5. **Direction 1** could start from the two computed facts: F1, and "no clause-(b) refusal has the treated shape". It could also start
   from the line fact for p, which may be the invariant the advisor could not find. **Not a block; a lead.**

## How the work was split

- **The referee:**
  - read the note, the pre-registration, the proof, `signlib.py`, `run.py` and the read-out;
  - checked L1 to L6 and Proposition 7 by hand;
  - wrote `referee_sign.py`, with three parts:
    - S: fresh SEEDK runs and every reading;
    - A: the ablation, in the study's range and past it;
    - P7: Proposition 7's base, both fills, every knot set of each, and the chain covers;
  - read the COPY-CLASS fold-in.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- **`referee_sign.py`.**
- **`referee_sign_S.json`, `referee_sign_A.json` and `referee_sign_P7.json`.**

Reproduce, from `research/FAR-SIGN-20261118-001/referee-R1/`. Each part takes under two minutes on 16 workers.

```sh
../../../.venv/bin/python -B referee_sign.py S > referee_sign_S.json
../../../.venv/bin/python -B referee_sign.py A > referee_sign_A.json
../../../.venv/bin/python -B referee_sign.py P7 > referee_sign_P7.json
```
