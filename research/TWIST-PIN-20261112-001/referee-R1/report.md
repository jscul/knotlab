# Referee report TWIST-PIN-R1: twisted pins

**Verdict: Confirmed with fixes.** Every count I can compare reproduces. Living does not depend on the cycle's length in the range,
and the advisor's living condition is exact on every single cycle. The claim that cycle length does not matter at all is wrong, by the
record's own data: in the exception block, the tie between the spare distinctions 4 and 5 appears on cycles of 2 and 3 knots and is
absent on the cycle of 6. T3, read as a full description of twisted pins, does not cover that block, and frozen prediction P2 failed in
that cell without being reported. A short rule replaces the quotient on one cycle and predicts every cell exactly, the exception
included.

Referee: the background referee thread, 2026-11-12. My code (`ref_twist.py`, built on the referee's `ref_subst.py`) imports none of
`twist_lib.py`, `subst_lib.py` or `check.py`; the author's result files were read only to compare. Validation: V2. The advisor model
was not consulted for this job.

## 1. What reproduces

| Item | Record | Referee |
| --- | --- | --- |
| The binding's form: at most one place per knot where three copies' values are not all the same | holds on 87 blocks | holds on 87 blocks, by brute force |
| Blocks whose symmetries move a distinction they cannot spare; non-identity classes | 18; 60 (block, class) pairs | 18; 60 |
| Chain of 4 knots, and balanced cells | the same as untwisted | the same |
| Twist on the cycle: living at cycles of 2, 3 and 6 knots | 37 live and 23 end at every length (after the run) | 37 and 23 at every length; two cycles of 3 too |
| The advisor's condition on one cycle: lives iff some state t has t∘h within k moves of t | 60 of 60 frozen; 180 of 180 after the run | 60 of 60; 180 of 180 |
| P4: the necessary and sufficient conditions | never violated | never violated |
| Rings with every middle member twisted by an involution | balanced on 6 (43 of 43), never on 7 | the same, 43 of 43 |
| Measured ties inside a copy equal to the quotient's | 389 of 390 frozen; 156 of 159 after the run | 276 of 277 frozen; 205 of 208 on the cycle |

My cell designs differ from the record's in one respect: for the two cycles I use the same class on both, where the record uses pairs.
Each design's exceptions are the same block and the same symmetry.

## 2. The exception, explained, and the cycle-length effect on ties

- **The block.** Knots (0,1,2), (0,1,3), (0,1,4), (2,3,4) and (2,3,5), with h exchanging 2 and 3.
- **Its spare distinctions.** 2, 3, 4 and 5 are spare, so N = {0, 1}, and h is N-balanced.
- **The move distances.** Of its 20 states, those with 4 = 5 are 0 or 2 moves from their image under h. Those with 4 ≠ 5 are exactly
  4 moves from it. (A move changes a set of places that meets every knot of the block at most once.)
- **The rule (the referee's, for one twisted cycle of k knots).** The copy that carries the twist takes exactly the states t of the
  block with t∘h within k moves of t. Proof: shift the twist onto one knot of the cycle (T1, T2). The cycle's copies then walk
  t = a_0, a_1, …, a_(k−1), t∘h. Two consecutive copies, with any pendant copy, are allowed together exactly when they differ on a set
  meeting every knot at most once, by the binding's form; take the pendant equal to one of them. A walk may stay in place.
- **The rule checked.** It predicts the copy's whole tie relation in all 111 living single-cycle cells with the twist on the cycle.
- **What it gives for the exception.** On cycles of 2 and 3 knots, only states with 4 = 5 occur, so 4 and 5 are tied in every copy.
  From 4 knots on, every state occurs and the tie is gone. The record's own after-run file shows the same: on the closed chain of 6,
  distinctions 4 and 5 are tied only to themselves.
- **Why the quotient misses it.** The N-quotient reads only the distinctions the block cannot spare, so it predicts no tie at any
  length. The full folded block (2 and 3 identified) forces 4 = 5 at every length. Each is right at some lengths and wrong at others.
- **The advisor's remark before the freeze was right.** It said length can matter only if some knot holds two or more spare
  distinctions; here (2,3,4) and (2,3,5) each hold three. What the run missed is that the effect shows in the ties, not in living.

## 3. The coordinator's points

**Is the cycle-length answer after-run and descriptive, and worded so?**
- The proof and the evidence table label it so: "the length part descriptive, after the run".
- The answer's headline ("cycle length does not matter"), the "In the owner's words" paragraph ("it never depends on how long the
  loop is") and the Position table ("no effect") carry no label. They are also too strong: living is the same at 2, 3 and 6 knots,
  but ties are not.
- "69 N-balanced cells end" in the proof is an after-run count (the frozen run has 33) and should say so.

**Are the exceptions explained, or folded into "quotient = measured"?**
- They are flagged as "beyond the quotient" and left unexplained. All of them (1 of 390 frozen, 3 of 159 after) are one block and one
  symmetry, on cycles of 2 and 3 knots and on two cycles of 3.
- The move rule above explains them.
- The record's sentence "on every cycle it ties the spare distinctions 4 and 5" is false for the cycle of 6.

**Is T3 contradicted by the exception block?**
- **T3's first clause holds.** It is a necessary condition: on N, the pinned values are constant on H-orbits.
- **Its bolded reading fails.** "A twisted pin is ordinary pinning with the block folded by H", read as a description of what the
  copies take, is contradicted: neither quotient gives the copy's ties at every length.
- **The same goes for "pins vary exactly where a holonomy moves a pinned distinction off its own tie class".** An N-balanced
  holonomy here creates a new tie inside a copy, through spare distinctions.
- **And P2 failed as frozen.** P2 ("N-balanced cells: no new tie inside a copy") fails in that one frozen cell, two knots sharing two.
  The frozen summary shows it (52 of the 53 living N-balanced cells unchanged), but the note's comparison with the pre-registration
  does not list P2.

## 4. Fixes for the thread

1. **Length.** Narrow "cycle length does not matter" (answer, owner's words, Position table) to "living does not depend on the cycle's
   length in the range". Add that the ties can: in one block a tie appears on cycles of 2 and 3 knots and is gone at 6. Label the
   length finding after-run and descriptive wherever it is stated. **Narrowing** (Overreading).
2. **T3.** Restate T3 as a necessary condition on the pinned layer, not as a full description of twisted pins. Give the exact rule for
   one cycle: the copy's states are those within k moves of their twist image. It contains the advisor's living condition and explains
   the exception. **Narrowing.**
3. **P2.** Report P2 as failed in one frozen cell, with the reason (spare distinctions folded by an N-balanced holonomy). Correct "on
   every cycle it ties 4 and 5" to "on cycles of 2 and 3 knots". **Not a block** (an unreported failed prediction, which changes no
   conclusion once fix 1 is made).
4. "69 N-balanced cells end" is an after-run count. **Not a block** (labelling).

## Files

`brief.md`; `ref_twist.py` → `result_twist.json` (the binding's form, 600 cells with both placements, the rings).
