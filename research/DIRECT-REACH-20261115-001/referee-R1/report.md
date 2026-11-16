# Referee report DIRECT-REACH-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.** Theorems W and D and Lemma 0 hold, the three pieces of code the owner was least sure
of are right, and Corollaries W and D and the life counts reproduce. One headline count is wrong: only one of the 100 constant
descriptions is shown to change at s = 5. The other "change" is an effect of the bottom level at depth 9.

**What holds.**
- **Theorem W, Lemma 0 and the bookkeeping in `window_tree.py`**, including the r < r₀ cases and the upward message. The referee
  read the proof and the code line by line. A fresh block DP and a fresh SAT oracle agree on every cell (§1).
- **Corollary W exactly.** 10 constant-2 with L = 2, 32 constant-3 with L = 3 exactly, and 43 half-rate with no tie at any depth, at
  every depth and every s. That includes the two top-2 exceptions.
- **Theorem D, the composite words and the inverse automaton** (`chain_ties.Extended`), checked to level 20. All 41 descents' claims
  hold to level 20 in the explicit union of blocks, and to level 13 in the whole pattern.
- **The finite-reader check** (`automatic_life.py`). All 540 machines pass an independent checker and the explicit depth-18 pattern;
  139 of 146 descriptions have one.
- **The certificates.** 20 of 20 archived certificates match their committed hashes.
- **5b906d33a1e9 really leaves 3 at s = 5.** There is no tie and no three-member bond at N = 9, 10, 11.

**What needs fixing.**
- **"2 of 100 constant descriptions change at s = 5" is 1 of 100.** For d50c90fa37ed, L₉(3, 5) = 3 is the depth-9 cell one level
  above the bottom (r = N − 3 − s = 1). At N = 10, 11, 12 every level-3 address is tied to all of level 8, so L_N(3, 5) = 2.
  **Narrowing.**
- **Every deeper read-out at depth 9 sits at r = 1:** s = 5 from top level 3, and s = 6 from top level 2. One of them is now known to
  be a boundary effect, so P2's "stay at 3" and "exceed 4" are depth-9 readings at r = 1, not evidence about larger depths.
  **Narrowing.**
- **D1's sentence.** "Tied to an anchor" does not give "one tie class" when there are several anchors. Both cases where it matters
  hold when checked directly. **Not a block** (wording).
- **"Frozen" predictions.** The wording needs the history stated: P1 and P2 were fixed in substance before any code, P3 was rewritten
  later, and the file's own time is off. **Narrowing** (wording).

**How the work was split.**
- **The referee.** Read the proof and the three files, recomputed the read-out counts from `readout_D.json` and scanned the full
  every-depth sequences in `window_tree_census.json`. The referee also confirmed d50c90fa37ed's tie at N = 10 and 11 with a separate
  20-line builder (pysat Minisat22).
- **One Claude helper.** Wrote the oracles: a pattern builder, SAT oracles (CaDiCaL and Glucose), a block DP, an inversion, explicit
  blocks and a product-automaton checker. Study functions were called only as the thing under test.
  - Its notes, with every place it read or called study code: `NOTES.md`.
- **Codex** was not used. **The advisor** was not consulted for this study.
- **Process slip.** Machine load was 30 to 50, so three of the helper's foreground runs took 12 to 15 minutes. They were not
  registered as LONG_RUNNING rows. All have finished, and nothing is pending.

## 1. Theorem W and `window_tree.py` (the owner's item a)

**The reading.**
- **Blocks.** Two blocks meet only parent to child, sharing the child's orbit, and a knot placed at v lies in its orbit's block. So
  the decomposition is a tree, and the dynamic programming is exact.
- **The feasible sets.** F_(r+1) = Φ(F_r) with F_(r+1) ⊆ F_r, so F stops changing at the first repeat, r₀.
- **The bookkeeping.**
  - `level_states` carries the upward message: the parent's message, its block, and every sibling's subtree at the right remaining
    depth.
  - `pair_joints` covers both the descendant case and two orbits split at a common ancestor b < k.
  - `every_depth_pairs` uses the stable F for every step whose remaining depth is at least r₀, and applies the last r₀ − r steps
    with F_(r₀−1), …, F_r for r < r₀, computing N − k < r₀ directly.

  Every index checks.
- **The verdict strings** in `window_tree_census.py` list s only up to 8, but the referee scanned the full stored sequences, which
  cover the prefix and a period. No exception is hidden beyond s = 8.

**The fresh checks** (helper, `referee_check_W_sat.py`, `referee_check_W_blocks.py`, `referee_W_verdicts.py`):

| Check | Size | Result |
| --- | --- | --- |
| Builder against the census `pattern()` | 146 descriptions, N = 1, 4, 7 | equal, knot for knot |
| SAT: tie, two-orbit three-member bond, life | k = 3: all 85, N = 4..12, every s (3,825 cells); k = 2: 16 sampled (880); N = 13, 14: 51 cells | 0 mismatches |
| r < r₀ cells (only 867ee877d22b and c99d95ae7866 have r₀ = 1) | every r = 0 cell at k = 2 and 3, and at N = 13, 14 | 0 mismatches |
| Fresh block DP: types against explicit addresses | to level 9 | 0 failures |
| Every-depth predictions against the census | k = 2, 3, s ≤ 60 (30,840 cells) | 0 mismatches |
| Exact per-depth DP | N ≤ 20 (27,540 cells) | 0 mismatches |

**Not a block.**

## 2. Theorem D and `chain_ties.py` (the owner's item b)

**The reading.**
- **The inverse automaton is right.** The inverse of q reads q's output a, returns b = a ⊕ sw[q] and moves to the inverse of q's
  section on b.
- **The composite words are right.** The composite m_j · m_i⁻¹ is listed as `maps[j] + reversed inverses of maps[i]`, applied right
  to left.

**The fresh checks** (helper, `referee_check_D.py`):
- **Composite images.** 116,400 images on random addresses at levels 1–20, against letter-by-letter inversion: 0 wrong.
- **Blocks.** The type evolution's blocks equal explicit blocks at all 740 levels (k₀ to 20) of the 41 descents.
- **The per-level claims.** The D1 and D2 claims hold at all 740 levels in the explicit union of blocks, and the kind found matches
  the study's verdict sequence every time.
- **The whole pattern.** 412 witnesses hold in P₁₃ by SAT.

**A wording gap in D1.**
- **The gap.** "Some address of S_(k+1) is tied to *an* anchor address" does not give "one tie class meets level k₀ and every deeper
  level" when S_(k₀) has anchors in different classes. Nor does it give "for k₀ ≤ 3 the same from level 3".
- **Where it matters.** Only the two descents starting at level 2: 5d9c7de076fa and b4ba185b9c0f.
- **What holds there.**
  - All anchors are tied together at every level to 17.
  - Some S₃ address is tied to some S_(3+s) address in the explicit union (levels 4–17), and in P₁₂ by SAT.
- **So** their L = 2 from level 3 stands.
- **Fix.** Add "with the anchors in one tie class" to the hypothesis, or cite the direct level-3 check. **Not a block.**

## 3. Finite-reader states and `automatic_life.py` (the owner's item c)

**The fresh check** (helper, `referee_check_machines.py`).
- **The checker.** An independently written product check over all words at once.
- **The machines.** 540 in all: 139 from `automatic_search.json` and 401 in the chain files. All pass, and all satisfy every knot of
  P₁₈ explicitly.
- **Negative controls.** On 2,920 mutants and random machines, the two checkers agree on every one.

**The count.** 139 of 146 descriptions have a machine, all with at most 5 states. The 7 without have growing orbits.

**Not a block.**

## 4. The depth-9 read-out

The referee recomputed the read-out counts from `readout_D.json`. P1: 33 of 34. P2: 58 of 60 and 42 of 42, from the cells where
the top-2 control agrees (31, 60 and 42). Top 3 at s = 5: 33 + 1 constant-2 and 65 + 1 constant-3. They are as reported.

**d50c90fa37ed (constant 2, "2 → 3 at s = 5").**
- **At N = 9** the study is right: no level-3 address is tied to level 8, and {7, 255, 256} is a three-member bond (heap ids).
- **At N = 10, 11, 12** every level-3 address is tied to every address of levels 4 to N − 2.
  - Witness: heap ids 7 (level 3) and 255 (level 8) are forced unequal at N = 10 and 11, and free at N = 9 (the referee's own
    builder; the helper's backbone and Glucose agree to N = 12).
- **So** L_N(3, 5) = 2 at N ≥ 10, and the depth-9 value 3 comes from the bottom level (r = 1).
- **P1's exception** ("the one constant-2 without a tie class through levels 3 to 8") is likewise true at depth 9 only.
- **Its top-2 profile** [2, 2, 2, 2, 2, 3] is the same r = 1 cell.

**5b906d33a1e9 (constant 3, "3 → more than 3").**
- No tie from level 3 at N = 9, 10, 11.
- An exhaustive search of every {level-3, level-8, any} set (2.1, 4.2 and 8.4 million sets) finds no three-member bond.
- **So** L ≥ 4 at r = 1, 2, 3. The change is real as far as checked.
- **The other constant-3 above 3 from top 2.** fbb5c3cad5db is also above 3 at s = 5 from level 2, at N = 9 and 10.

**The scope of the read-out.**
- Every s = 5 cell from top 3 and every s = 6 cell from top 2 at depth 9 has r = 1.
- The least bond is not monotone in N (`LEVEL-REACH-20261114-001`'s referee), and d50c90fa37ed now shows a value at r = 1 that is
  higher than at every deeper N checked.
- The deeper read-out (§6 of the conclusions table, P2) should therefore say "at depth 9, one level above the bottom".
- The half-rate "> 4 by s = 5" is not supported beyond depth 9 by anything proved. BLOCK-REACH's Theorem F gives only
  1 + ⌈s/r⌉ with r = 2 or 3.

**Narrowing.**

## 5. Predictions

- **Fixed in substance before any code.** The design question committed on 2026-11-14 (96cb9a7cc, "before any code or result")
  states P1 (at least half), P2 (70%; [3, 3, 4, 4] reaches 5 by s = 6) and P3 (at least a third of the 88 decided at 900 s). The
  advisor's answer in the same commit revises P1 to one class meeting levels 3..8, and P2 to "L ≥ 5 at s = 6 from top 2" with the
  control agreeing. The final P1 and P2 are these revisions.
- **P3 was rewritten before its run.** The new version, at least 2 of 6 pilot descriptions, is not the 11-14 text and not the
  advisor's "a fifth". The rewrite is legitimate before the pilot, but it is not disclosed as a change.
- **The file itself** was written after population D had finished, with 5 of 146 rows seen, as it says.
  - It says "Written 2026-11-16 19:30 UTC", but its last modification was 19:19:04 UTC.
  - `readout_D.py` was written at 19:20:55 UTC. So the file did precede the read-out.
- **Judgement.** "Frozen" is fair for P1 and P2 only with the history attached. Suggested wording: "fixed in substance before any
  code (11-14 design, 96cb9a7cc); written to this file after the run and before the read-out, with 5 rows seen; P3 rewritten for the
  pilot before it ran". Also fix the time. **Narrowing** (wording).

## 6. Certificates (the coordinator's request)

- **The sample.** 20 random entries of `certificate_hashes.json.gz`, 2 from each of 10 archives of the new
  `codex/certificate_archives/` (seed 20261116).
- **The check.** Extracted with the index, then sha256 recomputed for each CNF and LRAT. All 20 match the committed digests and the
  records' `proof_sha256`.
- **The list.** In `NOTES.md` and `referee_certs.json`.
- **Not done.** The LRAT proofs were not replayed.

**Not a block.**

## Fixes for the thread (listed for the owner, not folded in)

1. **"2 of 100 change at s = 5" → 1 of 100.**
   - Reword the Answer, the conclusions table row 6 and the intuition and goals text.
   - State that d50c90fa37ed's depth-9 value at s = 5 is a bottom-level effect: L_N(3, 5) = 2 at N = 10, 11, 12.
   - **Narrowing**, a correction for docs/CORRECTIONS.md.
2. **Mark the deeper read-out as depth 9 at r = 1.** This covers s = 5 from top 3, s = 6 from top 2, P2 and the half-rate "exceed 4".
   **Narrowing.**
3. **P1's exception holds at depth 9 only.** At depth 10, one class of d50c90fa37ed meets levels 3..8. **Not a block.**
4. **D1's hypothesis.** "With the anchors in one tie class", or cite the direct level-3 check for the two k₀ = 2 descents. **Not a
   block.**
5. **Predictions wording and time stamp**, as in §5. **Narrowing.**

## Files

The helper's oracles and outputs are in this folder, `referee_*.py` and `referee_*.json`, with its `NOTES.md`. The referee's own
d50c90fa37ed check is `referee_own_d50_tie.py`, with its output in `referee_own_d50_tie.txt`.
