# A slow loop that earns its budget is safe everywhere and wins on new local patterns, but it ramps too slowly to take most of the gain

Epic `EARN-BUDGET-20261117-001`, ticket `EARN-BUDGET-20261117-001A` (`SLOW-LOOP-20261117-001#1`; sub-goal B191; goals G15, G16),
2026-11-17. Evidence: **computed** on finite experiments with planted instances, every run kept. Frozen before any policy was tuned,
comparator re-tuned or test instance run ([pre-registration](preregistration.md), freeze commit `fd9e95c8d`;
[advisor review](advisor_review.md), "freeze with changes", all taken). One deviation came before the test: the charge was
corrected after SLOW-LOOP's referee (below). **Referee pending.** The stress cell (n = 12,800) has finished and is folded in below.
The canonical K1–K3 test is unchanged.

**Stress cell at n = 12,800 (folded in 2026-11-17):** `local` w20 and `heavy`, 20 fresh instances, five runs. NOV and PS were
re-tuned at 12,800; the slow arms kept their 800-tuned policies.
- **On `local` w20** the earned budget's win grows with size, to 0.18 [0.13, 0.21] (CPU 0.22) from 0.75 at 3,200:
  - Erb, tuned without a local pattern, now wins too, at 0.48 [0.34, 0.56];
  - the fixed batched budget is at 0.29, E/Gb = 0.63 [0.62, 0.66];
  - one pass of static probing does best, at 0.11 [0.08, 0.15], so E/ST = 1.60 [1.28, 1.86].
- **On `heavy`** E stays at parity (1.03), and static probing loses (1.31).
- **What this changes.** SLOW-LOOP's obstruction, a budget tuned without a local pattern staying lazy, holds at 3,200 but not at
  12,800. There the gain is large enough that even the cautious rule earns its way up. Part 3 below is therefore scoped to 3,200.

## The question, and the answer

SLOW-LOOP found three things:
- an eager structure-changing slow loop, tuned on `local` window 10, pays several-fold on local patterns;
- the same loop costs 1.5 to 2 times on random and block patterns;
- a fixed budget tuned on the random and block patterns stays lazy everywhere.

Here the slow loop **earns** its budget:
- the moves (tie merges found by bounded propagation refutations) are kept and applied in batches;
- after each rebuild, q is the share of the pattern's classes merged per unit of relative slow cost;
- the budget doubles when q ≥ θ and halves otherwise.

This is productivity-driven scheduling of inprocessing, the principle CDCL solvers use, moved to a local-search fast loop. The rule
was tuned on `rand`, `block` and `local` w10 at n = 800 (E), and on `rand` and `block` alone (Erb). It was tested on fresh
instances of ten patterns at n = 3,200, two of them never run before the freeze.

**The answer has four parts.**

1. **The earned budget wins on new local patterns and costs almost nothing where there is nothing to find.**
   - **The wins.** E's charged work is 0.56 [0.51, 0.68] of the best fast rule on the primary pattern (`local` window 15,
     density 3.5, never run before the freeze), 0.75 [0.61, 0.87] on `local` w20 and 0.56 [0.43, 0.81] on `local` w10. All three
     are charged wins, CPU 0.61, 0.76 and 0.72.
   - **Where nothing is found.** On `rand` 2.1, `rand` 3.0 and the heavy-tailed pattern it costs 3% (R_W 1.03, CPU 1.11 to 1.23),
     and 4% on `block`.
   - **Against the comparators.** It beats the best fixed batched budget tuned on the same patterns (E/Gb 0.68 to 0.86 on the three
     winning cells, never worse elsewhere) and static probing on the primary (0.08).
2. **But it leaves most of the gain on the table.**
   - **The per-cell oracle.** Tuned on each cell's own instances, the best fixed batched budget is the most eager one (3 times the
     search's work) on the four local patterns at density 3.5 and 4.0. It reaches 0.16 to 0.18 on windows 15, 20 and 10, and 0.38
     on window 40; on `local` w10 at density 3.0 it is lazy, at parity. E's regret E/GbO is 3.4 to 4.1 on the local cells where it
     won, and 2.7 on `local` w40.
   - **Against SLOW-LOOP's loops.** E is 1.6 to 2.3 times SLOW-LOOP's eager GO there, and SLOW-LOOP's fixed grid tuned on the same
     mixture (Gm) does better on the local cells (0.46 to 0.52), but loses 17 to 28% on `rand` and `block`.
   - **Why: the ramp.** The budget starts at 3% of the search's work and doubles at most once per rebuild. A rebuild waits until
     the moves found reach 3% of the classes. On `local` w40, where ties are rare but each cascades, E never collected a batch,
     never rebuilt and stayed at its floor in all 250 runs (R 1.03). On `local` w20 it reached the top budget in 18 of 250 runs.
3. **At 3,200, a rule tuned without a local pattern does not carry over.** Erb, tuned on `rand` and `block` alone, is at parity
   everywhere (0.81 [0.65, 1.05] on `local` w10), and so is ErbL with the lazy tie rule. SLOW-LOOP's obstruction stands for the
   earned budget at this size, because the tuning patterns set how slowly it ramps. At 12,800 Erb wins on `local` w20 (0.48; stress
   cell above).
4. **At the tuning size, earning was invisible.**
   - **At n = 800.** Under the corrected charge, E and the best fixed batched budget scored almost alike (−0.070 and −0.073 in mean
     log ratio).
   - **At 3,200.** The per-cell oracles are the eager ones. The gain from changing the structure grows with size: on `local` w10,
     SLOW-LOOP measured Novelty+'s work growing about as n^1.9 from 800 to 3,200, while a pass of probes grows about as n. So a
     schedule tuned at 800 learns to be cautious where caution no longer pays.

**By the frozen rule this is reading 2: it works, but earning is not shown to matter.**
- **What held.** E wins on the unseen primary and on one more structured held-out pattern (`local` w20), loses nowhere
  structure-poor, beats the fixed batched budget somewhere and is worse nowhere, and beats static probing on the primary.
- **What failed.** The one condition that failed is E/GO ≤ 1.5 on `local` w10 (1.65 [1.49, 1.80]).

**What a win here does and does not show** (as frozen):
- **It shows** that a slow loop judging its own changes by how much they shrink the pattern can be tuned on a few patterns and
  carried, safely, to others: about 3% overhead where nothing is found, and real but partial gains where knots meet densely within
  short runs.
- **It does not show** anything about satisfiability in general. The moves are known inference (failed-literal probing with
  equivalent-literal substitution), and the scheduling principle is CDCL inprocessing's. CaDiCaL solves every instance of the three
  local patterns not in SLOW-LOOP in at most 0.06 s of wall time, below every local-search arm.

## Results

Charged work W under the corrected charge (below): the median over 50 fresh instances of each instance's five-run geometric mean.
R is W over the better of re-tuned Novelty+ and probSAT, re-chosen in each of 10,000 paired bootstrap resamples (99% intervals).
Novelty+ was the better rule in every cell.

| Cell | F (W) | E | Erb | Gb | GbO (per-cell oracle) | Gm | ST | GO | E verdict |
| --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- |
| **`local` w15, density 3.5** (primary, never run) | 2.95·10^7 | **0.56 [0.51, 0.68]** | 0.88 | 0.82 | 0.16 | 0.52 | 7.0 (at least; 18% censored) | 0.34 | charged win |
| `local` w20 (seen in calibration) | 2.23·10^7 | **0.75 [0.61, 0.87]** | 0.98 | 0.87 | 0.18 | 0.48 | 0.41 | 0.32 | charged win |
| `local` w40 (SLOW-LOOP's pattern) | 2.64·10^7 | 1.03 [1.03, 1.03] | 1.01 | 1.03 | 0.38 | 0.80 | 1.45 | 0.63 | parity |
| `local` w10, density 3.0 (seen in calibration) | 1.98·10^6 | 1.03 [1.03, 1.05] | 1.01 | 1.03 | 1.03 | 1.15 | 3.19 | 2.43 | parity |
| `embed` (no role) | 5.95·10^6 | 0.86 [0.75, 1.04] | 1.05 | 0.89 | 0.82 | 0.96 | 1.19 | 1.39 | parity |
| `local` w10 (tuning pattern) | 1.94·10^7 | **0.56 [0.43, 0.81]** | 0.81 | 0.78 | 0.16 | 0.46 | 0.61 | 0.34 | charged win |
| `rand` 2.1 (tuning pattern) | 2.03·10^6 | 1.03 [1.03, 1.03] | 1.01 | 1.03 | 1.03 | 1.17 | 1.04 | 1.72 | parity |
| `rand` 3.0 (never run) | 6.15·10^5 | 1.03 [1.03, 1.03] | 1.01 | 1.03 | 1.03 | 1.00 | 1.22 | 1.85 | parity |
| `heavy` (seen in calibration) | 5.75·10^5 | 1.03 [1.02, 1.03] | 1.01 | 1.03 | 1.03 | 1.00 | 1.38 | 1.77 | parity |
| `block` (tuning pattern) | 2.82·10^6 | 1.04 [1.03, 1.06] | 1.01 | 1.04 | 1.04 | 1.28 | 1.84 | 4.76 | parity |

- **CPU** (R_CPU, the whole run): E 0.61 [0.51, 0.78], 0.76 [0.62, 0.88] and 0.72 [0.50, 0.89] on its three wins, and 1.10 to 1.23
  on the structure-poor cells.
- **The oracle GbO** has CPU 0.19 to 0.20 on the local cells.
- **Arms.**
  - ErbL equals Erb within 1% except on `local` w10 (Erb/ErbL 0.89 [0.78, 1.02]).
  - G (SLOW-LOOP's lazy fixed policy) is 1.10 to 1.24 everywhere under the corrected charge.
- **Soundness.** No run reported a contradiction or a state that failed on the original knots (27,500 runs).
- **Censoring.** 47 runs stopped at the cap, 46 of them ST's on the primary, where a single pass of static probing merged the
  pattern to about 1,100 classes and Novelty+ then stalled in 18% of runs. ST's figure there is a lower bound.

**Between arms** (W, 99%):

| Cell | E/Gb | E/GbO | E/Gm | E/ST | E/GO | Erb/E |
| --- | --- | --- | --- | --- | --- | --- |
| `local` w15 d3.5 | 0.68 [0.62, 0.74] | 3.38 [3.13, 3.59] | 1.07 [0.96, 1.20] | 0.08 [0.04, 0.19] | 1.65 [1.49, 1.80] | 1.59 [1.41, 1.92] |
| `local` w20 | 0.86 [0.81, 0.91] | 4.08 [3.62, 4.37] | 1.56 [1.38, 1.70] | 1.84 [1.59, 2.04] | 2.33 [2.10, 2.55] | 1.31 [1.14, 1.45] |
| `local` w10 | 0.71 [0.65, 0.79] | 3.41 [3.27, 3.57] | 1.21 [1.12, 1.34] | 0.91 [0.89, 0.95] | 1.62 [1.47, 1.71] | 1.44 [1.24, 1.62] |
| `local` w40 | 1.00 [1.00, 1.00] | 2.70 [1.92, 3.45] | 1.28 [0.96, 1.73] | 0.71 [0.44, 1.14] | 1.63 [1.16, 2.19] | 0.98 [0.98, 0.98] |
| `rand` 2.1 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.88 [0.84, 0.93] | 0.99 [0.99, 1.00] | 0.60 [0.58, 0.62] | 0.98 [0.98, 0.98] |
| `block` | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.81 [0.72, 0.89] | 0.56 [0.53, 0.63] | 0.22 [0.19, 0.25] | 0.98 [0.96, 0.98] |

**How far the budget rose** (E, 250 runs per cell): it reached its top (3) in 194 runs on the primary and 209 on `local` w10, in 18
on `local` w20, and in none on `local` w40 and `embed`. Its median number of doublings was 9, 4, 8, 0 and 1. On every
structure-poor cell it never left its floor.

**CDCL** (CaDiCaL 1.9.5, 20 instances of each new local pattern): every instance solved within 0.06 s of wall time (median CPU 0.04
to 0.05 s).

## Predictions

| # | Prediction (probability) | Outcome |
| --- | --- | --- |
| G | Gates G0–G10 | **Passed** (`gates/check_output_charge_v2.txt`; the first run is in `gates/check_output.txt`) |
| P1 | E charged win on the primary (`local` w15 d3.5) (60%) | **Held**: 0.56 [0.51, 0.68] |
| P2 | E charged win on `local` w20 (85%) | **Held**: 0.75 [0.61, 0.87] |
| P3 | E charged win on `local` w40 (65%) | **Failed**: 1.03; it never rebuilt |
| P4 | E charged win on `local` w10 d3.0 (35%) | **Failed**: 1.03 |
| P5 | E costs at most 10% on every structure-poor cell (85%) | **Held**: 1.03 on all three |
| P6 | Earning matters, jointly (E/Gb ≤ 0.9 somewhere, upper end below 1.1 everywhere) (50%) | **Held**: 0.68 to 0.86 on three cells, never above 1.00 |
| P7 | Erb charged win on `local` w10 (70%) | **Failed**: 0.81 [0.65, 1.05] |
| P8 | E within 1.5 times GO on `local` w10 (60%) | **Failed**: 1.62 [1.47, 1.71] |
| P9 | Small regret: E/GbO ≤ 1.25 on every structured held-out cell (50%) | **Failed**: 2.7 to 4.1 |
| P10 | CDCL solves every new-pattern instance in under 1 s (95%) | **Held**: at most 0.06 s |
| P11 | Soundness in every run (99%) | **Held** |
| P12 | E charged win on `block` (30%) | **Failed**: 1.04 |

Six of twelve held. The failures share one cause, the slow ramp: P3, P8 and P9 measure how much of the eager gain E captured, and P7
asks for eagerness learned without a local pattern.

**Decision (frozen rule).** Reading 2, **it works, but earning is not shown to matter**: every condition of reading 1 held except
E/GO ≤ 1.5 on `local` w10.

## What the study supplied and what was learned

**Supplied:**
- the moves and their refutations;
- the earned-budget rule (doubling and halving on q) and batched rebuilds;
- the grids, the tuning patterns and the eager tie rule;
- random targets.

**Learned (tuned):** E's four parameters (θ = 0.01, ρ from 0.03 to 3, a batch of 3% of the classes), Erb's and Gb's.

**What it says about the owner's picture.** A slow loop that monitors the yield of its own changes, and not the search's attention,
can be made safe: it never costs more than about 3% where nothing can be found, and it wins on locally structured patterns it never
saw. But doubling from a cautious floor is too slow to reach the eagerness that pays, and the caution was learned at a size where
eagerness did not yet pay. The open problem is to price a batch of moves before paying for the rebuild, so that a few rare,
cascading ties (as on window 40) can justify eagerness at once.

## Deviations from the frozen text

All were made before any test instance ran:
- **The charge was corrected** (charge v2) after SLOW-LOOP's referee found that charged work omitted the rebuild's Python-side
  sorting and set operations (`docs/CORRECTIONS.md`).
  - **What is charged.** Every sort or set merge of k items is charged k ⌈log₂(k + 1)⌉, the guided order's sort included.
  - **What was rerun.** The policy tuning and the first half of the per-cell oracle were rerun under v2. The v1 runs and choices
    are kept (`policy/`, `oracle_a/`, `policies_v1charge.json`).
  - **What it changed.** Under v1 the tuning had chosen E with ρ_max 3, rb 0.01 and Gb with ρ 0.3; under v2, E with rb 0.03 and Gb
    with ρ 0.03.
  - **Gates.** G9 checks identity with SLOW-LOOP under v1. G10 checks that v2 only adds the sorting where no budget is counted in
    it.
- **R1t.** The tuning cells' share of the comparator re-tuning ran ahead, so that policy tuning could start; it is deterministic
  and gives R1's results.
- **The per-cell oracle** ran in two parts, as R1's cells finished.
- **`planted_embed`** was guarded against an all-equal part (no instance changes).
- **Comparator edges.** Settings on a grid edge were reported, and the grid was not widened (as frozen):
  - Novelty+ on `heavy` sat at the corner (noise 0.5, walk probability 0.1) and on `block` at walk probability 0.1. A stronger
    Novelty+ may exist there, which only flatters the slow arms on two cells where none of them wins;
  - probSAT sat at cb 3.0 on `rand` 3.0, where it is the weaker rule.

## Limitations

- **The instances.** Planted instances only, one density per pattern, n = 3,200, with two patterns at 12,800.
- **The rules tried.** One earning rule (factor 2, one q per rebuild), random targets and tie probes only.
- **The fast loop** was not re-tuned on the changed pattern.
- **The charge** is still a model of the cost: one unit per sort operation. Whole-run CPU, which counts everything, agrees on every
  verdict.
- **Not compared:** clause weighting (SLOW-LOOP#2), and a learned fast loop (SLOW-LOOP#3).
- **CPU** is thread CPU on a machine shared with MEET-TRANSFER (load average 13 to 22 on 24 cores).

## Where to start again

- **Code** (in `experiments/EARN-BUDGET-20261117-001A/EARN-BUDGET-20261117-001A-E001_earn_budget/`):
  - `slow_engine.c` and `slow_loop.py`: SLOW-LOOP's, with the earned budget, batching, charge v2 and the heavy family;
  - `job.py`, `choose.py` and `analyze.py`;
  - the gates: `.venv/bin/python -B experiments/.../check.py`.
- **Runs** (in `artifacts/EARN-BUDGET-20261117-001A/EARN-BUDGET-20261117-001A-E001_earn_budget/`):
  - `retune/`, `retune_tune/`, `policy_v2/`, `oracle_a_v2/`, `oracle_b/`, `retune12800/`, `test/` and `stress/`;
  - the choices `retuned.json`, `policies.json`, `oracle_policies.json` and `retuned12800.json`;
  - the summary `summary.json`.
- **To rebuild the summary:**
  `.venv/bin/python -B experiments/.../analyze.py artifacts/.../test artifacts/.../summary.json --stress artifacts/.../stress`.
