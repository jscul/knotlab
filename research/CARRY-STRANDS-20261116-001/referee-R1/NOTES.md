# Referee R1 helper notes: CARRY-STRANDS-20261116-001 recomputed with fresh code

16 November 2026. Claude helper for the referee, with no Codex and no advisor.

**Oracle code.** All oracle code is new: `referee_carry.py` has the laws, the pebble game, the generators, k* and the
spend-only tree DP. Strahler numbers come from the referee's earlier `research/SEQUENTIAL-WALL-20261116-001/referee-R1/referee_core.py`
(Knuth's generalized Dijkstra, plus the exhaustive set method for n ≤ 8, and the two must agree).

**Study code.** I read `strands.py`, `gates.py`, `job.py`, `summarize.py` and `contract.json` of
`experiments/CARRY-STRANDS-20261116-001A/…_carried/`, and `atoms.py` and `job.py` of `SEQUENTIAL-WALL-20261116-001A`, for
definitions and the sampling protocol. **I ran none of it.** I compared against the study's recorded outputs
(`artifacts/…/run/results.jsonl` and `summary.json`), read as data.

**Instances.** The "study instances" below are rebuilt by my own code from the protocol: the sha256 seeds, then the same draw order.
Matching them sample by sample tests the laws, not the sampler. The "fresh" instances use my own sampler and seeds.

## Task 1: Theorems 1–3 on small patterns. Verdict: **Matches**, with one aside on the copying variant

Scripts: `referee_task1_theorems.py`, `referee_task1b_larger.py` and `referee_dp_vs_bfs.py`, with the same-named JSON files.

**What is checked on every pattern, for w = 1, 2, 3:**
- every law ends in the closure;
- **Theorem 1:** the spend-only phase of v is ⌈σ(v)/w⌉ for every forced v;
- **Theorem 2:**
  - T_w(spend) ≥ max σ;
  - in each spend-only phase, the BFS distance to each newly forced v is at least 2^{σ_F(v)} − 1, with σ_F taken over the phase's
    start;
  - each phase's rounds are at least the largest σ_F it forces;
  - T₁ ≤ σ_max·⌈log₂(n+1)⌉;
- **Theorem 3:** the keep law's one-phase reach from F = H equals the reach of my separate pebble-game search, and the iterated
  pebble phases equal the keep law's whole phase vector. The pebble search uses bitmask configurations and scans the atoms directly:
  placement, a slide from a demander, and removal.

**Sizes and results.**
- **Every pattern on n = 4:** all 2¹² subsets of the 12 atoms, times all 16 held sets, which is 65,536 cases in 2.9 s. 0 failures.
  This set is weak: σ ≤ 1, and keep and spend never differ.
- **Random patterns, n = 5…12:** 40,000 patterns: 3,000 per n at mixed densities and 2,000 per n at the jump. 24 s on 4 workers.
  0 failures. σ_max reaches 4, and keep differs from spend in 332 cases.
- **At the jump, n = 16…64, plus sparse n = 20 and 30:** 1,400 patterns in 81 s. 0 failures. σ_max reaches 6, and keep differs from
  spend in 458 cases.
- **Structured:** 21 small cases (ladders, pyramids, subdivided trees, a zipper and the gates' G8 shape). 0 failures.
- **Contrast check:** the keep law breaks the 2^{σ_F} − 1 distance bound 1,216 times. So the bound is specific to spend-only, and
  the test can fail.

**A second method for spend-only distances.** The DP (`spend_min_steps`) gives the least number of internal nodes of a derivation
tree over F with Strahler number ≤ w. It equals the BFS's first distance in all 155,321 distinction-phase comparisons, over 14,763
pattern-and-w cases. I use it below where the BFS is too large.

**The copying variant (the advisor's warning).**
- **The law:** spend-only multisets, plus a copy step x → x, x when a slot is free.
- **Measured:** copy reach(w) ⊆ pebble reach(w) always. Copy reach(w) falls short of pebble reach(w) in 142 random patterns
  (n ≤ 12), in 323 more at n ≤ 64 (342 pattern-and-w pairs) and in 3 structured ones, including the zipper. Copy reach(w + 1) ⊇
  pebble reach(w) in every case: **the gap is +1 and never +2**.
- **Why the gap is at most one:** each pebble move is simulated with at most one extra slot. Placement over two pebbled demanders
  becomes copy, copy, open use. A slide with the other demander pebbled becomes copy, then open use.
- **Smallest witness found (n = 7, w = 2):** atoms (0,4→2), (4,0→5), (5,2→6), (6,5→3), (3,6→1), H = {0, 4}. Pebbling reaches 1;
  copying with 2 does not, and copying with 3 does.
- **The zipper:** p_{i+1} = (p_i, q_i), q_{i+1} = (p_{i+1}, q_i). Pebbling with 2 reaches every length; copying needs 3.
- **What this means for the proof:** "up to two" is not attained by this copying law. It is not wrong as an upper bound, but one
  is the measured and provable gap. This is a wording point for Theorem 3's status line.

## Task 2: structured families. Verdict: **Matches** on every stated number. **Differs** on Q5's third part, which the study called not evaluable and is evaluable and false

Scripts: `referee_task2_structured.py` and `referee_task2_compare.py`, with their JSON files and the log. Runtime 55 s, peak 590 MB.

**Ladders k = 8, 32, 128.**

| Reading | k = 8 | k = 32 | k = 128 |
| --- | --- | --- | --- |
| σ(top) | 9 | 33 | 129 |
| T₁ | 16 | 64 | 256 |
| T₂ spend | 13 | 49 | 193 |
| T₂ keep, in 1 phase | 5 | 7 | 9 |

**Pyramids h = 4…12, w ≤ 4** (w ≤ 3 for h > 10). P_w = ⌈h/w⌉ for both laws, and T_w = h for every w and both laws.

**Subdivided trees.** d = 4, ℓ = 16: T₁ 21 and T₂ 13 (both laws). d = 6, ℓ = 16: T₁ 31 and T₂ 19.

**Against the study's run.** All 75 (case, law) entries the study recorded are identical: P, T, the list of L_t and the state counts.

**Q5's third part.** The prediction was T₃(spend) < T₂(spend) at d = 4, ℓ = 16. The study recorded it as capped and "not evaluable".
It is evaluable, and **T₃ = T₂ = 13**.
- **The DP:** P = 2 and L = [115, 35], so T₃ = ⌈log₂ 116⌉ + ⌈log₂ 36⌉ = 7 + 6 = 13.
- **A counting check that does not depend on the DP.** The pattern is a tree, with each unforced distinction demanded by one atom
  and a demander of one atom. So every carry law must produce every node of the unique derivation tree.
  - With w = 3, phase 1 forces σ ≤ 3, which includes the level-2 chain ends. Each has 4·16 + 2 + 2·16 + 1 + 16 = 115 internal
    nodes, so L₁ ≥ 115 and phase 1 costs 7 rounds.
  - Phase 2 must force the top. Its tree over F₂ has 2 + 2·16 + 1 = 35 nodes, so phase 2 costs 6 rounds.
  - So T₃ ≥ 13 = T₂.
- **BFS checks of the pieces.** The BFS gives the same L₁ = 115 on d = 3, ℓ = 16 at w = 3. The BFS also gives T₃ = T₂ on d = 4 with
  ℓ = 4 (9 = 9) and with ℓ = 8 (11 = 11). On those three trees, keep equals spend at w = 3.
- **So Q5 fails.** The tally becomes 2 of 7 held (Q3b and Q4) and 5 failed.
- **Elsewhere carrying three does cut the rounds:** d = 3, ℓ = 16 gives T₃ 8 against T₂ 12; d = 6, ℓ = 16 gives 15 against 19 (by
  DP); d = 6, ℓ = 4 gives 12 against 13 (by DP).

## Task 3: random atom patterns at the jump. Verdict: **Matches** (exactly, per sample). One wording claim **Differs**

Scripts: `referee_task3_random.py`, `referee_task3_analyze.py` and `referee_task3_before_witness.py`, with the
`referee_task3_random_n*.json` files, `referee_task3_summary.json` and `referee_task3_before_witness.json`.

**Runtimes** (4 workers): about 1 s for n = 64 and 256, 12 s for n = 1024, 33 s for n = 2048, and 208 s plus 188 s for n = 4096.
Peak memory was 730 MB.

**The study's own instances.** I rebuilt all 120 (20 each at n = 64…1024, 10 each at 2048 and 4096). My code reproduces every
reading exactly in 120 of 120:
- k*, the forced count, σ_max and R;
- P, T, the list of L_t and the state counts for w = 1, w = 2 spend and w = 2 keep;
- the phase sizes;
- the three keep-gain fractions;
- w = 3 at n = 64.

The medians therefore equal `summary.json` at every n, and the decision note's table (n = 64, 256, 1024, 4096) is right as printed.
Theorem 1, Theorem 2 and the DP-against-BFS check also hold on all of these samples.

**Fresh instances.** 20 per n, and 30 at n = 4096. Medians:

| n | σ | R | T₁ | T₂ spend | T₂ keep | P₂ keep | gain after | T₂/T₁ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 64 | 4 | 11.5 | 10 | 8 | 7 | 2 | 0.17 | 0.81 |
| 256 | 5 | 18.5 | 14 | 11 | 11 | 3 | 0.067 | 0.76 |
| 1024 | 6 | 31.5 | 23 | 16.5 | 16 | 3 | 0.063 | 0.75 |
| 4096 | 8 | 55 | 30 | 22 | 21 | 4 | 0.078 | 0.705 |

**Fresh against the study's samples** (two-sided Mann–Whitney).
- Every p > 0.08 at n ≤ 2048.
- At n = 4096 the study's 10 samples run high: σ p = 0.019, T₁ p = 0.015, T₂ spend p = 0.05. That is within noise across about 56
  tests.
- T₂ ≤ T₁ holds in every sample, and the T₂/T₁ trend (0.81 → 0.70) is reproduced.

**Q1 at 4096.** The share with P₂(keep) = ⌈P₁/2⌉ is 29 of 30 = 0.97 in fresh samples, against the study's 7 of 10 (Fisher
p = 0.04). The frozen Q1 verdict ("failed") stands on the frozen sample, but the failure at 4096 looks like a 10-sample fluctuation,
not a trend.

**DIFFERS: "keeping saves no phase for any distinction forced before the narrowest phase".** This is in the decision note, the final
report and the Q1b row ("before: 0 at every n"). It holds for the median only.
- **The study's own samples:** 9 of 105 have a positive before-fraction, up to 0.041.
- **Fresh samples:** 13 of 132, up to 0.115.
- **The narrowest phase is counted as "before"** in `job.py`. Even reading "before" strictly, three study samples have such
  distinctions: rand-n1024-s3 (5), rand-n2048-s6 (13) and rand-n4096-s2 (3).
- **Witness:** the study's instance rand-n1024-s3, distinction 89. σ(89) = 3 and its forcing-law phase is 3; the narrowest phase is
  4, with phase sizes 51, 54, 50, 49, 195, …. The keep law with w = 2 forces 89 in phase 1, below ⌈3/2⌉ = 2.
- **Suggested wording:** "in the median sample, none; in about one sample in ten, a few percent."

## Task 4: narrow layered circuits. Verdict: **Matches**

Script: `referee_task4_narrow.py` and its JSON. Runtime 260 s, peak 860 MB.

- **The study's instances:** 30, rebuilt (W = 2 at d = 4, 8, 16; W = 3 at d = 4, 6, 8; 5 each). P_{2W}(keep) ≤ 1 in 30 of 30
  (P = 0 when no gate is true). P, the state counts and σ_max equal the study's recorded values in 30 of 30.
- **Fresh circuits:** W = 2 at d = 4…64 and W = 3 at d = 4…16, 10 each. Every uncapped sample (77 of 90) takes at most one phase
  with 2W carried, and the forced set equals the true gates.
  - 13 deep samples hit my 1.5M-state cap: W = 2 at d = 64, and W = 3 at d = 12 and 16.
  - The least w giving one phase was at most 3 for W = 2 and at most 4 for W = 3.
