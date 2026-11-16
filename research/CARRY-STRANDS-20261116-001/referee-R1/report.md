# Referee report CARRY-STRANDS-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.** Theorems 1 to 3 hold, including the two points the owner asked about: Theorem 2's
step-count bound, and the exact match of the keep law with black pebbling with sliding. Every recorded value reproduces exactly in
fresh code. The freeze preceded the run, and the post-run read-out fix is disclosed. The fixes:
- **Q5 fails.** Its "not evaluable" part is evaluable and fails: T₃ = T₂ = 13 at d = 4, ℓ = 16. So 2 of 7 predictions held, not 3.
- **"Keeping saves no phase for any distinction forced before the narrowest phase"** is true of the median only.
- **The freeze time** in the decision note is wrong.

**What holds.**
- **Theorem 1** (spend-only phases = ⌈σ/w⌉). Lemma 1 is the register bound applied within a phase, and Lemma 2 (the shift) is exact.
  Both directions check (§1).
- **Theorem 2** (spend-only rounds ≥ max σ). The step count 2^s − 1 and the telescoping through Lemma 2's lower half are right (§2).
- **Theorem 3** (keep law = black pebbling with sliding, F free). The two match move for move (§3). The ladder and layered-circuit
  constructions are right.
- **The freeze.** It preceded the run: commit 4df1a101e at 22:43:14 UTC, run created at 22:43:26 UTC. The four frozen code files
  other than `summarize.py` match their contract hashes, and the state cap of 4,000,000 was frozen.

**What needs fixing.**
- **The freeze time.** The decision note says the pre-registration was "frozen in commit 4df1a101e (22:39 UTC)". The commit is at
  22:43:14 UTC, 12 seconds before the run was created, not four minutes. The order is right, and 22:39 is presumably when the file
  was written. **Not a block** (a wrong time).
- **Q5 fails.** Q5's frozen rule needs all three parts. Its third part, T₃ < T₂ at d = 4, ℓ = 16, hit the frozen state cap, but it
  can be evaluated without the search, and it fails: T₃ = T₂ = 13 (§5). The tally becomes 2 held (Q3b, Q4) and 5 failed.
  **Narrowing**, a correction for docs/CORRECTIONS.md.
- **"Keeping saves no phase for any distinction forced before the narrowest phase"** (the answer, the final report, Q1b's row
  "before: 0 at every n"). The median is 0 at every n, but 9 of the study's own 105 random samples have a positive before-fraction,
  up to 0.041. Witness: rand-n1024-s3, distinction 89 (σ = 3, forcing-law phase 3, narrowest phase 4) is forced by the keep law at
  w = 2 in phase 1, below ⌈3/2⌉ = 2. **Narrowing** (wording): say "for the median sample".

**How the work was split.**
- **The referee.** Read the proof, the note, the pre-registration, the post-run diff of `summarize.py` and the run's timestamps.
- **One Claude helper.** Recomputed Theorems 1–3, the structured families and the random readings, with fresh code (`NOTES.md`).
- **Codex** was not used. **The advisor** was not consulted.

## 1. Theorem 1

**Lemma 1, the (⇐) direction.** Evaluating a tree of number s ≤ w larger child first carries at most s distinctions. This is the
Ershov–Sethi–Ullman order, and F-leaves are free.

**Lemma 1, the (⇒) direction.**
- In a spend-only run each carried copy is produced by one step and spent by at most one, so the production history of v is a
  derivation tree whose nodes are distinct steps.
- Evaluating it without recomputation needs at least its Strahler number of registers, which is at least σ_F(v).

**Lemma 2.** Replacing new leaves by trees of number at most k raises a tree's number by at most k, since combine is monotone and
combine(i + k, j + k) = combine(i, j) + k. Cutting a least tree at its maximal subtrees of number at most k lowers every number above
k by exactly k. The referee checked the three cases: both children above k; one above and one cut; and both equal to k.

**The phase-by-phase induction is right.** The spend-only phase adds exactly the distinctions with σ_F ≤ w (Lemma 1), so Lemma 2
applies with k = w.

**Not a block.**

## 2. Theorem 2 (the owner's first point)

**The bound holds in the stated cost model.**
- **The count.** In a derivation tree over F of number s, with F-leaves 0:
  - an atom over two F members is a beginning, with number 1;
  - a step with one F demander is a follow, a unary node;
  - a step with two non-F children is an open use, a binary node.
  Contracting the F-leaves leaves a tree whose leaves are the beginnings, with number 1, so its Strahler number s needs at least
  2^(s−1) beginnings. A tree with L leaves has exactly L − 1 binary nodes, so there are at least 2^(s−1) − 1 open uses.
- **The steps.** The run's own production tree has number at least σ_F(v), and its nodes are distinct steps. So reaching v takes at
  least 2^(σ_F(v)) − 1 steps, L_t ≥ 2^(s_t) − 1, and the phase costs ⌈log₂(1 + L_t)⌉ ≥ s_t rounds.
- **The telescoping.** Lemma 2's lower half needs only that every added distinction has σ_F ≤ s_t, not that all of them are added.
  So σ_(F_t)(v) ≤ σ_(F_(t+1))(v) + s_t, and summing gives max σ ≤ Σ s_t ≤ T_w.
- **The upper bound.** T₁ ≤ σ·⌈log₂(n + 1)⌉, since there are at most n + 1 states at w = 1.

**Labels.** "Local and elementary, inside this cost model" is fair. The bound is not a lower bound for other ways of evaluating, as
the proof says. It applies to the spend-only law only: the keep law beats it on ladders (T₂ keep = 9 against σ = 129 at k = 128),
as the note shows.

**Not a block.**

## 3. Theorem 3 (the owner's second point)

**The keep law is the black pebble game with sliding, F free, move for move.**

| Keep-law step | Game move |
| --- | --- |
| begin over two F members | placement (both demanders free) |
| follow (x, b → c), b ∈ F, keeping x | placement |
| follow, spending x | slide from x to c |
| open use, keeping both | placement |
| open use, keeping one | slide from the other |
| open use, keeping neither | slide one, then remove the other |
| release | removal |

Conversely, every game move is one of these steps. States are sets, so carried distinctions are pebbles, and "carried in some
reachable state" is "pebbled at some point". **Holds exactly.**

**The advisor's warning applies to a copying law and is avoided by the design.** The helper's recomputation includes a copying
variant (§5).

**The constructions.**
- **Ladder with 2 carried in one phase.** The run {y₀} → {y₀, z₀} → {x₁} → {x₁, y₁} → {y₁, z₁} → {x₂} … never carries more than 2.
- **Layered circuit of width W with 2W** (hold one layer, derive the next, release).

Both are right. Both are standard pebbling arguments in kind: two pebbles slide up a ladder, and layer-by-layer pebbling uses twice
the width. "Local" is a generous label. **Not a block.**

## 4. The freeze, the run and the read-out fix

**The order.**
- The pre-registration commit 4df1a101e is dated 2026-11-16 14:43:14 −0800 (22:43:14 UTC).
- The runner's `job.json` was created at 22:43:26.648 UTC and finished at 22:45:50.
- So the run followed the freeze by 12 seconds.
- The note's "(22:39 UTC)" is not the commit time; the coordinator's "four-minute gap" comes from it.
- The pre-registration discloses what was seen before it: gates, and smoke cases with unregistered seeds, whose timings and state
  counts were read but not their phases. That is fair.

**The code hashes.** `strands.py`, `gates.py` and `job.py` match the contract's sha256 values. `summarize.py` does not: the contract
has c369d339…, and the file now has 1df1ceae…, because of the disclosed fix. The frozen version is in git at 4df1a101e, and its
hash is the contract's c369d339….

**The fix** (the diff from 4df1a101e to affe49efa).
- **Before.** The frozen read-out evaluated Q5 as `a4["w2"] < a4["w1"] and a6["w2"] < a6["w1"] and a4["w3"] < a4["w2"]`. It raised a
  KeyError, because the capped w = 3 law was left out of the values.
- **After.** The fix reports each part, marks the capped part "not evaluable (state cap)", and sets `holds` to whether every
  evaluable part holds. No other read-out changed.
- **Judgement.** The disclosure is fair. But turning "not evaluable" into "held" is a reading choice the frozen rule did not make.
  The part was in fact evaluable by other means, and it fails (§5), so Q5 failed.

## 5. The measurements, recomputed (helper; `NOTES.md`)

**The code.** Fresh: the w-carry laws by search, σ, the pebble game, a search-free tree DP, and the structured and random families.
The study's code was read, not run, by the helper. The referee ran it only as the thing under test, for Q5 below.

| Check | Size | Result |
| --- | --- | --- |
| Theorems 1–3 | every pattern on n = 4 (65,536), 40,000 random at n = 5–12, 1,400 at the jump to n = 64 (σ ≤ 6); Theorem 3 against a separate pebble-game search | 0 failures |
| Structured families: ladders k = 8, 32, 128, pyramids h = 4–12, subdivided trees | all 75 recorded (case, law) entries | identical, including L_t and state counts |
| Random at the jump: the study's 120 instances rebuilt from the seed protocol | all n | identical, so the table's medians reproduce exactly |
| Random at the jump: fresh samples | n ≤ 2048 | Mann–Whitney p > 0.08; at 4096 the study's 10 samples run high (σ p = 0.02), and 30 fresh ones give a P₂(keep) = ⌈P₁/2⌉ share of 0.97 against 0.70, so Q1's failure at 4096 looks like small-sample noise |
| Narrow circuits (Q3b) | all 30 study instances and 77 uncapped fresh ones | one phase with 2W carried |

**Q5's third part.**
- **The helper's two methods.** For d = 4, ℓ = 16, spend-only, w = 3:
  - **The tree DP:** P = 2 and L = [115, 35], so T₃ = 7 + 6 = 13 = T₂. The DP agreed with the search in all 155,321 comparisons.
  - **A counting argument with no search.** The pattern is a tree, so every law produces every node of the unique derivation. The
    phase-1 targets need 115 steps (7 rounds), and the top then needs 35 (6 rounds).
- **The referee's check with the study's own code** (`strands.carried_phases`, `referee_own_q5_study_code.py` and `.txt`):
  - at d = 4, T₃ = T₂ at ℓ = 4 (9 and 9) and at ℓ = 8 (11 and 11);
  - at d = 3, ℓ = 16 its phase-1 step count at w = 3 is the same 115.
- **So** the prediction's third part fails at every ℓ tried. Spend-only w = 3 does not beat w = 2 on this family.

**The copying law (minor).** A natural copying law (spend-only plus a copy step) falls short of pebbling with sliding by at most one
pebble on 468 patterns where it falls short. The advisor's "up to two" was never attained. Smallest witness (n = 7, w = 2): atoms
(0, 4 → 2), (4, 0 → 5), (5, 2 → 6), (6, 5 → 3), (3, 6 → 1), held {0, 4}. This does not affect the study, which uses the keep law.

## 6. Known versus new

- **Theorem 1:** known-with-delta (Ershov; Nakata; Sethi–Ullman). Fair.
- **Theorem 2:** local and elementary. Fair.
- **Theorem 3:** known-with-delta (Cook 1974; Gilbert–Lengauer–Tarjan). Fair.
- **The constructions:** generous, as said above.
- **The note.** It says plainly that the braid picture "explains nothing the classical statement does not", and that what is new is
  measured. Accurate.

## Fixes for the thread (listed for the owner, not folded in)

1. **The freeze time.** Correct "(22:39 UTC)" to the commit time, 22:43:14 UTC, 12 s before the run. **Not a block.**
2. **Q5 fails.** T₃ = T₂ = 13 at d = 4, ℓ = 16, by a tree DP, a counting argument, and the study's own code at ℓ = 4 and 8. Report
   "2 held (Q3b, Q4), 5 failed". The Q5 row should read "failed: T₃ = T₂". **Narrowing**, for docs/CORRECTIONS.md.
3. **"Saves no phase for any distinction forced before the narrowest phase" → "for the median sample".** 9 of 105 samples are
   positive, up to 0.041; witness rand-n1024-s3, distinction 89. This applies to the answer, the final report and Q1b's row.
   **Narrowing** (wording).
4. **Optional.** Note that Q1's failure at n = 4096 rests on 10 samples; 30 fresh ones give 0.97.

## Files

- `NOTES.md`: the helper's notes.
- `referee_*.py` and `referee_*.json`: the checks and their outputs.
