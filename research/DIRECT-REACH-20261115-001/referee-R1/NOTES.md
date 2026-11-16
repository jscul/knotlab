# Referee R1 — DIRECT-REACH-20261115-001, fresh-code recheck

2026-11-16. Every oracle here is my own code, written from the textual definitions (report, proof, the census's key format).
Python: the workspace `.venv` (numpy, pysat CaDiCaL 1.9.5 and Glucose 4). No Codex. The machine ran at load 30 to 50 throughout,
so the runtimes below are slow. Scratch was deleted after use.

## Summary

| Item | Verdict | One line |
| --- | --- | --- |
| (a) Theorem W bookkeeping | **Matches** | 3,825 + 880 SAT cells to N = 12 (plus 51 at N = 13 and 14), 30,840 every-depth predictions and 27,540 exact-DP cells to N = 20, r₀ and periods, with 0 mismatches |
| (b) Extended, composites, descents | **Matches** (one wording gap in D1) | 116,400 composite images to level 20, 740 blocks to level 20, 740 per-level claims, 412 witnesses in P₁₃, with 0 wrong |
| (c) finite-reader check | **Matches** | 540 machines pass my product check, P₁₈ and the study's checker; 139 of 146 have one, all with ≤ 5 states |
| (d) the two s = 5 changes | **Differs (interpretation)** for d50c90fa37ed; **Matches** for 5b906d33a1e9 | d50's "2 → 3 at s = 5" is the r = N − 3 − s = 1 cell at depth 9. At N = 10, 11, 12, level 3 is tied to all of level 8, so L = 2 again |
| (e) certificates | **Matches** | 20 of 20 from 10 archives: CNF and LRAT sha256 match the committed hashes |

## Where I read or called the study's code

- **Read only** (for definitions and data formats): `exploratory/window_types.py`, `window_tree.py`, `window_tree_census.py`,
  `gate_window_tree.py`, `automatic_life.py`, `automatic_search.py`; `chain_ties.py`, `chain_bounded3.py`, `gate_chain.py`,
  `crosscheck_window_tree.py` and the header of `separation.py`; the census's `pattern.py` and `input_addr.py` (address and action
  conventions); the Codex `REPORT.md` (first half); the archives' `INDEX.md`.
- **Called only as the thing under test**, compared against my oracle:
  - `pattern.pattern` and `window_types.population_D`, in `referee_check_builder.py`;
  - `chain_ties.Extended`, `initial_type`, `next_type`, `window_knots` and `window_types.Description` (only to build Extended's
    input), in `referee_check_D.py` (b1, b2);
  - `automatic_life.check_all_levels`, in `referee_check_machines.py`.
- **Data read as claims**: `window_tree_census.json`, `automatic_search.json`, `chain_ties_constant-2.json`,
  `chain_bounded3_constant-3.json`, `readout_D.json`, `certificate_hashes.json.gz`, and the census records (for the keys).
- None of the oracles imports study code: `referee_pattern.py` (builder, SAT oracle, orbits), `referee_blocks.py` (block DP), the
  product checker in `referee_check_machines.py`, and the inversion and explicit blocks in `referee_check_D.py`.

**Builder gate** (`referee_check_builder.py` → `referee_builder.json`, 1 s). My population equals `population_D()` (146: 34 / 66 /
46), and my P_N equals the census `pattern()` knot for knot on all 146 at N = 1, 4 and 7.

## (a) Theorem W: blocks of orbits — Matches

**SAT oracle** (`referee_check_W_sat.py`, results in `referee_W_sat_k3_b1..b6.json`, `referee_W_sat_k2_sample.json` and
`referee_W_sat_k3_N13.json`). For every cell (N, s) it computes three things on the explicit P_N with my builder:
- tie(N, k, s): an exact backbone. For each level-k address u, sampled models propose partners and SAT decides each one, under the
  assumption u = 0, using complement symmetry.
- b3(N, k, s): exact. The orbits come from my own union-find over the images. For every pair (O_u at level k, O_v at level k + s),
  every three-member set meeting both orbits is checked. A set is skipped when one of its pairs is tied (decided by SAT). Otherwise
  every pattern not seen in the models is decided by SAT, and a set with fewer than 8 patterns whose pairs are all free is a bond.
- life(N): satisfiability of P_N.

The models come from fresh CaDiCaL runs on randomly relabelled variables with random phases. A persistent solver with new phases
returned the same model again (2 of 8 patterns covered), so I did not use it. Every model is checked knot by knot.

| Run | Descriptions | Depths | Cells | Mismatches with window_tree_census.json | Time |
| --- | ---: | --- | ---: | ---: | --- |
| k = 3, all small-orbit ones | 85 (10 c2, 32 c3, 43 half-rate) | N = 4..12, every s ≤ N − 3 | 3,825 | 0 | 2,635 s over 6 batches (each ≤ 380 s) |
| k = 2, sample (seed 2026) | 16, including c99d95ae7866, 39079b659d07 and 867ee877d22b | N = 3..12 | 880 | 0 | 849 s |
| k = 3, deeper | 0195d32248c7, 10e63af5c86c, 867ee877d22b, c99d95ae7866 at N = 13; c99d95ae7866 also at N = 14 | 13, 14 | 51 | 0 | 846 s + 440 s |

- **Life:** P_N is satisfiable in all 765 depth-wise checks (85 × N = 4..12).
- **Cells with r = N − k − s < r₀.** Only two descriptions have r₀ ≥ 1: 867ee877d22b (constant 2) and c99d95ae7866 (constant 3),
  both with r₀ = 1. Their r = 0 cells are covered at k = 3 (9 each) and at k = 2 (10 each), and all agree. That includes
  867ee877d22b's r = 0 alternation of b3, [0, 1, 0, 1, …] (b3 = 0 for every r ≥ 1), and c99d95ae7866's tie at s = 1 from level 2.
- **SAT cell values:**

  | Profile | (tie, b3) = (1, ·) | (0, 1) | (0, 0) |
  | --- | --- | --- | --- |
  | constant 2 | every cell | none | none |
  | constant 3 | none | every cell | none |
  | half-rate | none | exactly the s = 1 cells | every other cell |

**My own block DP** (`referee_blocks.py`, `referee_check_W_blocks.py` → `referee_W_blocks.json`, 127 s; and
`referee_W_verdicts.py` → `referee_W_verdicts.json`). Written from the proof's statement.

What the DP computes:
- **Types:** for each element and each word, the index of the image and the word's section. Child orbits are forward closures under
  the maps; each orbit is relabelled breadth-first from its first child.
- **F_r** by remaining depth.
- **Up messages:** what everything outside an orbit's subtree allows.
- **Joints:** an orbit below another one, or two orbits split at a common ancestor b < k.
- **An exact per-depth DP** that assumes no periodicity.
- **My every-depth prediction.** After F becomes constant, the level-k pair states are advanced with the constant F and stop at the
  first repeat. For r < r₀, the last r₀ − r steps use F_{r₀−1} … F_r, and N − k < r₀ is computed directly.

Results:
- **Same 85 small-orbit descriptions.** The other 61 exceed orbit size 4. There are 2 to 45 types; orbit sizes are {1, 2} (75) or
  {1, 2, 4} (10).
- **Types against explicit addresses, to level 9:**
  - the orbit partition of every level;
  - every image;
  - every section, tested on a random 6-letter suffix;
  - every block's knots, against knots placed at the orbit's explicit addresses.

  **0 failures.**
- **r₀ and periods:** r₀ equals the census's for all 85 at k = 2 and k = 3 (83 have 0, 2 have 1). Periods are equal, and
  alive_every_depth is true for all.
- **Every-depth prediction against the census's stored sequences:** k = 2, 3, every s ≤ 60, r = 0..r₀ + 2. 30,840 cells, 0
  mismatches. The census values beyond its stored prefix come from its stated period.
- **Exact DP, every N ≤ 20 and every s:** 27,540 cells, equal to both the census and my prediction.
- **Corollary W reproduced exactly at every s and every r:**
  - constant 2: 10 of 10 have a tie at every s;
  - constant 3: 32 of 32 have no tie and a two-orbit three-member bond at every s;
  - half-rate: 43 of 43 have no tie, and a two-orbit bond only at s = 1;
  - from level 2, the only changes are c99d95ae7866 (a tie at s = 1, then (0, 1)) and 39079b659d07 (no two-orbit bond at any s).

**N = 13 and 14** (`referee_W_sat_k3_N13.json`, `referee_W_sat_k3_N13_c99d.json`). 51 cells, all equal to the census, life included. Among them are the r = 0 cells of both r₀ = 1 descriptions: 867ee877d22b at N = 13, s = 10 gives (1, 1), as the census's r = 0 alternation predicts, and c99d95ae7866 at N = 13 and 14.

## (b) Theorem D: Extended, composite words, descents — Matches (one wording gap)

`referee_check_D.py` → `referee_D.json` and `referee_D_part2..4.json`, merged into `referee_D_all.json`. That is 41 descents (13
D1, 28 D2; 12 with growing orbits), 1,900 s in total. Settings: LMAX = 20, KMAX = 20, NP = 13.

- **(b1) Composite images.** I inverted m_i level by level, letter by letter with my forward action (one letter per position must
  match), then applied m_j. I compared that with `Extended.image(comp[(j, i)], x)` on 4 random addresses per level, levels 1..20,
  for every composite of every descent's description. **116,400 images, 0 wrong.** Long addresses also exercise the sections
  Extended carries.
- **(b2) Blocks.** The type evolution's `window_knots` equals my explicit block (every address v of level k, every placement, my
  action) at every level k₀..20 of every descent. **740 levels, 0 different.**
- **(b3) Per-level claims in my explicit union of blocks** (levels k₀..k, incremental SAT), for every level up to deep level 21:
  - D1: some anchor is tied to some element of S_{k+1};
  - D2: either such a tie, or a constrained {x, x′, y} whose top pair has two machines with different parities, or a constrained
    {x, y, y′} whose deep pair has that property (my own machine evaluation at the explicit addresses).

  **740 of 740 levels hold.** The kind found (in the order tie, then top-top-deep, then top-deep-deep) equals the study's
  `verdicts` sequence at every level.
- **(b4) Witnesses in the whole pattern.** Every witness of (b3) with its deep address at level ≤ 13 holds in P₁₃ by SAT: ties
  forced, triples constrained, one-level pair free. **412 claims, 0 false.**
- **Wording gap in D1** (`referee_check_D_level3.py` → `referee_D_level3.json`, 19 s).
  - The problem: D1's hypothesis, "at every level some element of S_{k+1} tied to *an* anchor", does not by itself give "one tie
    class meets every level" when S_{k₀} has several anchors in different classes. Nor does it give "for k₀ ≤ 3, the same from
    level 3".
  - Where it matters: the two k₀ = 2 descents (5d9c7de076fa, b4ba185b9c0f, both with growing orbits).
  - What holds there:
    - all four anchors are tied to S_{k+1} at every level, through level 17;
    - some element of S_3 is tied to some element of S_{3+s} in the explicit union for every deep level 4..17;
    - the same holds in P₁₂ by SAT for levels 4..12.

    So their L = 2 from level 3 stands. The proof's sentence needs "the anchors in one tie class", or the direct level-3 check.

## (c) Finite-reader states — Matches

`referee_check_machines.py` → `referee_machines.json`, 732 s.

**My all-level check** is a joint product over all used words at once, unlike the study's per-placement product. A configuration
holds, for every word:
- its section;
- the machine's state on the word's image;
- which images are still equal.

It is evaluated on every placement at every configuration, and a breadth-first search explores the reachable configurations.

| Check | Count | Result |
| --- | ---: | --- |
| Machines checked: `automatic_search.json` (139) and every machines list of the two chain JSONs (401) | 540 | all pass my product check, my explicit check of every knot of P₁₈ (numpy, my builder), and the study's `check_all_levels` |
| Negative controls: 80% one-step mutants of the valid machines, 20% random | 2,920 | my checker and the study's agree on every one; the 630 that pass my check also satisfy P₁₂ explicitly |

- **Counts:** 139 of 146 have a machine in `automatic_search.json`, all with ≤ 5 states (2: 102; 3: 33; 4: 1; 5: 3).
- **The 7 without:** 28611064056c, 2c17384e1472, 58fc613a8ccc, 6931977afc9f, a1aaf3bc3d4a, cb4a81a75966 and fbb5c3cad5db. All 7
  have growing orbits, so nothing proves them alive at every depth.
- **Descents:** every one of the 41 has its machines.

## (d) The two constant descriptions that change at s = 5 (top level 3, depth 9)

`referee_check_s5.py` → `referee_s5.json` (477 s), and `referee_check_d50_depth.py` → `referee_d50_depth.json` (267 s).

- **5b906d33a1e9 (3 → more than 3): Matches, and the change is genuine through r = 3.**
  - No level-3 address is tied to any deeper address at N = 9, 10 or 11.
  - An exhaustive search found no three-member bond meeting levels 3 and 8. It covered every {x at level 3, y at level 8, z any other
    address}: 2,091,008 sets at N = 9, 4,188,160 at N = 10 and 8,382,464 at N = 11. Sets seen with all 8 patterns in 1,024 checked
    models are excluded; the rest were decided by SAT.
  - So L_N(3, 5) ≥ 4 at N = 9, 10, 11 (r = 1, 2, 3).
- **d50c90fa37ed (2 → 3): the depth-9 computation Matches, but the reading as a change in s Differs.**
  - At N = 9: no level-3 address is tied to any level-8 address (exact backbone; also none to level 9), and three-member bonds
    meeting levels 3 and 8 exist (for example heap ids {7, 255, 256}). So L₉(3, 5) = 3, as reported.
  - At N = 10, 11, 12: **every level-3 address is tied to every address of levels 4..N − 2**, and to none of level N − 1.

    | N | Level-3 ties, by deep level (count = 8 × level size) |
    | --- | --- |
    | 9 | levels 4..7 |
    | 10 | levels 4..8 (8: 2,048) |
    | 11 | levels 4..9 |
    | 12 | levels 4..10 (10: 8,192) |

  - A second solver (Glucose 4, on my clauses) agrees: level3[0] ~ level8[0] is forced at N = 10, 11, 12 and free at N = 9.
  - **Witness:** at N = 10, s = 5, heap ids 7 and 255 are tied (sign 1), so L₁₀(3, 5) = 2.
  - So d50's L_N(3, s) = 2 whenever r = N − 3 − s ≥ 2 (checked to N = 12, s ≤ 7). It is 3 at r = 1.
  - The depth-9 cell s = 5 from top 3 is an r = 1 cell. The census cells s = 1..4 at depth 9 had r = 5..2.
  - The report's "two leave their constant at s = 5" and "2 of 100 change at the fifth" therefore hold for 5b906d33a1e9 but not for
    d50c90fa37ed, whose change is the bottom boundary (r = 1), not s. The same cell reading also explains its top-2 profile
    [2, 2, 2, 2, 2, 3] (s = 6 from level 2 is again r = 1). P1's lone exception, "the one constant-2 without a tie class through
    levels 3 to 8", is true at depth 9 only: at depth 10 one class holds levels 3..8.
  - Caution for the read-out: every top-3 s = 5 and top-2 s = 6 cell at depth 9 has r = 1.
- **Extra: fbb5c3cad5db** (`referee_check_fbb5.py` → `referee_fbb5.json`, 10 s). This is the other constant-3 description that the
  read-out has above 3 from top 2 at s = 5 and 6. From level 2 at s = 5 there is no tie and no three-member bond meeting levels 2 and
  7, by an exhaustive search at N = 9 (r = 2) and N = 10 (r = 3). So it is genuinely above 3 there.

## (e) Certificates — Matches

`referee_check_certs.py` → `referee_certs.json` (run with `python -I`; extracted copies deleted, `scratch_certs/` removed).

20 entries of `artifacts/DIRECT-REACH-20261115-001A/…/certificate_hashes.json.gz` were drawn at random (seed 20261116), 2 from each
of 10 archives of at most 300 MB raw. They were located with `index.tsv.gz` and only those members were extracted from the
`.tar.zst`. The labels were 10 "reported bond or tie", 6 "tie candidate forbidden pair" and 4 "census internal SAT
query/exhaustion".

For **all 20**:
- sha256 of the raw `<digest>.cnf` = the digest;
- sha256 of the raw `<digest>.lrat` = the committed second hash;
- the record's `proof_sha256` = the same hash.

| Archive (case prefix) | Digests checked |
| --- | --- |
| 484889bb9e59 | b8d66fd2af4f…, 683baffffa16… |
| 52950ab1474d | b854b6f5fa9b…, 00ec3e95f12b… |
| d3f2cb823c04 | e1ccca9d4741…, a73a677e4240… |
| 7e50a5aac6a8 | d5f56a257a2f…, 757c1c45c85a… |
| 6bd9132ff089 | 6061f7f6a587…, fccd339fbe9f… |
| a1aaf3bc3d4a | b11326a5aa17…, e6272d9aebbd… |
| d45686a6d506 | b454679ba26e…, 7f7563e42f82… |
| 6931977afc9f | 10e83e1e51aa…, 5f647f81ddcc… |
| b8c4b784e098 | a52ecd3f843f…, 7ef11bf9dae8… |
| 0195d32248c7 | 663556d1d983…, 75d98d272e62… |

Full digests are in `referee_certs.json`. I did not replay the LRAT proofs.

## Runtime notes and limits

- Runs over about 10 minutes, at load 30 to 50:
  - the k = 2 SAT sample took 849 s;
  - the machine check took 732 s;
  - the first descent run was stopped by its 900 s timeout after 23 of 41 descents, and the other 18 were run in three parts of
    312 to 398 s.

  Peak memory stayed well under 8 GB.
- **SAT depth:** to N = 12 for all 85; N = 13 for 4 and N = 14 for c99d95ae7866. The block DP is exact per depth to N = 20, and is my own every-depth
  argument beyond that.
- **Not checked:** the LRAT proofs themselves, the U pilot, and Theorem D's lower bounds (none are claimed).
