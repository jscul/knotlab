# Does a slow loop that earns its budget from how fast its moves shrink the knot pattern keep the eager loop's gain and lose its cost, on fresh instances and new meeting patterns?: pre-registration

Epic `EARN-BUDGET-20261117-001` (`SLOW-LOOP-20261117-001#1`, the coordinator's go-ahead of 2026-11-17; sub-goal B191; goals G15,
G16). **Frozen** before any policy was tuned, any comparator re-tuned or any test instance run. The commit time of this file is the
only authority for the freeze. Before it, only the gates and a calibration ran (below, disclosed). Code by the thread (Claude) in
`experiments/EARN-BUDGET-20261117-001A/EARN-BUDGET-20261117-001A-E001_earn_budget/`. It is SLOW-LOOP's engine and driver, copied,
with two additions: the earned budget and batched rebuilds. Gate G9 checks that the driver reproduces SLOW-LOOP's run for run on
SLOW-LOOP's policies. The canonical K1–K3 test is unchanged. The advisor reviewed a draft and said "freeze with changes", and the changes are in
([advisor note](advisor_review.md)).

## The question

`SLOW-LOOP-20261117-001` found that a slow loop which changes the knot pattern between epochs of re-tuned Novelty+, using tie
merges and shadow knots, pays only when eager:
- **The eager policy** (GO), tuned on `local` window 10, cut charged work to 0.15 and 0.23 on two local patterns at n = 3,200.
- **The cost.** It cost 1.5 to 2.1 times on random and block patterns.
- **The tuned policy.** A fixed budget tuned on the random and block patterns (G) stayed lazy and at parity everywhere.

A post hoc reading of those runs suggested that how fast the moves shrink the pattern nearly separates the cells where eagerness
pays. Here the slow loop sets its own budget from that rate:
- after a rebuild, q is the share of the pattern's classes it merged per unit of relative slow cost;
- the next budget doubles when q ≥ θ and halves otherwise.

Does this keep the gain where structure exists and lose the cost where it does not? The test is on fresh instances. Two meeting
patterns are new to the program and were never run before the freeze: `local` window 15 at density 3.5, the primary, and `rand`
at density 3.0. Three more were seen only in this study's calibration (below).

## In standard terms, and what is already known

This is **productivity-driven scheduling of inprocessing**, the principle CDCL solvers already use:
- **Lingeling and CaDiCaL** (Biere, 2010 onward) limit each inprocessing technique's effort relative to the search's own effort.
  They preempt and resume preprocessing between restarts, with its time bounded relative to search time (Biere, POS 2014). CaDiCaL
  runs rounds at growing conflict intervals, with efforts relative to search "ticks" (Biere et al., SAT Competition 2020 system
  descriptions). Lingeling's scheduler also adjusts how often a technique runs by how productive it was. The advisor recalls
  per-technique penalties that rise after unproductive rounds and fall after productive ones, essentially doubling and halving
  on yield. That was not checked against Lingeling's source before the freeze, and the closest documented statements are the
  two above. Kissat schedules the same way.
- **The rules.** The inprocessing framework of Järvisalo, Heule and Biere (2012) states which rules keep satisfiability and
  equivalence.
- **What this study adds.** The earned budget is that principle moved to a local-search fast loop. Its productivity measure is the
  share of distinctions merged by tie merges per unit of relative slow cost. Its update is doubling and halving.

Nothing in the rule is new to SAT solving. What is new to the program is whether it removes SLOW-LOOP's obstruction, namely that a
budget tuned elsewhere does not carry over, on meeting patterns the rule never saw.

**What a win would and would not show.**
- **A win would show** that a slow loop judging its own changes by how much they shrink the pattern can be tuned on a few patterns
  and carried to others. It would be eager where knots meet densely within short runs and lazy where they do not, for local search
  on these planted not-all-equal families. This is the owner's metacognition in one narrow sense: the slow loop monitoring its own
  yield.
- **Two caveats.**
  - **Batching** is a second change, and in calibration it alone moved `block` from a loss to a gain. So only a win over the fixed
    batched budget (Gb, and the per-cell oracle GbO) is evidence that monitoring its own yield matters; a win over Novelty+ is not.
  - **The calibration** ran on three of the test patterns (`local` w20, `local` w10 at density 3.0, `heavy`), and batching and its
    grid were chosen from it. Those cells are labelled "seen in calibration", and the primary is a pattern nothing touched.
- **It would not show anything about satisfiability in general.** The moves are known inference. CaDiCaL solves the local patterns
  in about 0.06 s, below every local-search arm in SLOW-LOOP but one, and needs 88 s on the random pattern where Novelty+ takes
  0.014 s. So a win does not make local search with structure changes competitive with CDCL where structure exists, and it does
  nothing where structure is absent. It would not show that the search's own attention is a useful signal either: SLOW-LOOP found
  it is not, so the targets here are drawn at random.

## Prior work in the program

Objects index, searched 2026-11-17:

`python3 -B scripts/track.py objects "slow loop that earns its budget from how fast its moves shrink the knot pattern" --until 2026-11-18 --exclude EARN-BUDGET-20261117-001`
`python3 -B scripts/track.py objects "productivity-driven inprocessing schedule for local search" --until 2026-11-18 --exclude EARN-BUDGET-20261117-001`
`python3 -B scripts/track.py objects "planted not-all-equal patterns local window heavy-tailed degrees" --until 2026-11-18 --exclude EARN-BUDGET-20261117-001`

- `SLOW-LOOP-20261117-001`: the same object with fixed budgets; this study continues it. It reuses its engine, its moves and its
  two fixed policies (G and GO, frozen there), and uses fresh instances throughout.
- `WHERE-NEXT-20261116-001` and `SCALE-MEMORY-20261116-001`: the learned fast loop on the same patterns. Their lesson of five runs
  against a widely re-tuned Novelty+ is kept.
- `SEQUENTIAL-WALL-20261116-001`: a relative. It counts rounds of propagation on atom patterns, and propagation is the probe
  here, but it measures no search cost. `GROW-FACE-20261110-001`: unrelated, matched on "grow" and "budget".
- `MEET-TRANSFER-20261117-001` (running) uses the heavy-tailed and `local` window 40 patterns for the learned fast loop. Its runs
  and files are not touched.

## Calibration before the freeze (disclosed)

These runs used seeds 9,400,000 and up, disjoint from every seed below: four instances at n = 3,200, one run each, Novelty+ (0.7,
0.05), random targets, ρ_min = 0.03, ρ_max = 1.
- **Without batching,** the earned budget hardly rose: its top was 0.03 to 0.09 even on `local` window 10. Each rebuild costs
  about ten reads per knot whatever it merges, so at a small budget a rebuild merging a few classes never paid for itself.
- **With batching,** the pattern is rebuilt only once the moves found since the last rebuild reach 1% of the classes. Charged work
  against Novelty+ for θ = 0.03, 0.1, 0.3 and 1 was:
  - `local` w10: 0.15, 0.28, 0.32, 0.35;
  - `local` w20: 0.21, 0.28, 0.40, 0.41;
  - `local` w10 at density 3.0: 0.75 at every θ;
  - `block`: 0.69 to 0.85;
  - `rand` and the heavy-tailed pattern: 1.03.
- **Batching also helps a fixed budget,** so a fixed batched budget (Gb) is a required control.

## Families and cells

All planted, unsigned not-all-equal patterns, from SLOW-LOOP's generators (the heavy-tailed one is MEET-TRANSFER's, copied).
Fresh instances throughout:
- policy tuning: seeds 8,000,000 and up at n = 800;
- comparator re-tuning: 8,500,000 and up;
- test: 8,100,000 and up;
- stress: 8,200,000 and up.

Every arm runs from the same five initial states per instance (`run_seed("test", cell, seed, rep)`).

| Cell (n = 3,200, 50 instances, cap 2·10^8 flips) | Role |
| --- | --- |
| `local` window 15, density 3.5 | **primary**: structured, never run before the freeze |
| `rand` density 3.0 | structure-poor, never run before the freeze |
| `local` window 40, density 4.0 | structured, held out from tuning (SLOW-LOOP's pattern; the earned rule was designed after its results) |
| `local` window 20, density 4.0 | structured, seen in calibration |
| `local` window 10, density 3.0 | structured in part, seen in calibration (0.75 there) |
| `heavy`, density 3.0 | structure-poor, seen in calibration |
| `embed` | mixed (local structure on a quarter), reported, no role in the rule |
| `local` window 10, `rand` 2.1, `block` 2.5 | tuning patterns at 4 times the tuning size; `block` is partly structured once rebuilds are batched (calibration 0.69–0.85), so it is not counted as structure-poor |

## Arms

All local-search arms run five times per instance. Unless stated, a slow arm draws its targets uniformly among unprobed knots,
since SLOW-LOOP found the attention counts no better and costly to read. Tie probes only (no shadow knots), with a probe budget of
4,000 and epochs of n′ flips.

| Arm | What it is |
| --- | --- |
| NOV | Novelty+ re-tuned per cell: noise 0.5–0.9 (8 values) × walk probability 0–0.1 (6 values), 48 settings |
| PS | probSAT (poly, eps 1) re-tuned per cell: cb 0.6–3.0, 10 settings |
| F | the better of NOV and PS by the cell figure, re-chosen in every bootstrap resample |
| **E** | the earned budget, **tuned on `rand`, `block` and `local` w10 at n = 800** over 90 settings: θ ∈ {0.01, 0.03, 0.1, 0.3, 1}, ρ_max ∈ {0.3, 1, 3}, ρ_min ∈ {0.01, 0.03}, batching threshold rb ∈ {0.003, 0.01, 0.03} of the classes |
| **Erb** | the same rule tuned on **`rand` and `block` alone**, with no local pattern. This is SLOW-LOOP's obstruction put to the earned budget. `block` is partly structured once rebuilds are batched, so "no structure at all" would overstate it |
| ErbL | Erb with the opposite tie rule (the most lazy setting within 0.01 of the best): how much of Erb's result the eager tie rule supplies |
| Gb | a fixed batched budget, tuned like E over ρ ∈ {0.03, 0.1, 0.3, 1, 3} × rb ∈ {0.003, 0.01, 0.03}: the control for earning, since batching alone helps |
| GbO | the per-cell oracle: the same 15 fixed batched settings tuned on each test cell's own tuning instances at n = 3,200. E/GbO is the regret that earning is meant to close |
| Gm | SLOW-LOOP's fixed unbatched grid (48 settings, attention targets), tuned like E: the best fixed budget without either change |
| ST | SLOW-LOOP's static probing grid (8 settings), tuned like E: the preprocessing precedent |
| G, GO | SLOW-LOOP's two frozen policies (lazy, tuned on `rand` and `block`; eager, tuned on `local` w10), as references |
| CDCL | CaDiCaL 1.9.5 on 20 instances of each of the three local patterns not in SLOW-LOOP, for context (its interrupt does not fire; read from wall time) |

In every slow arm the fast loop is the cell's re-tuned NOV setting.

**Tuning.**
- **The score** on a pattern is the mean over 8 instances × 3 runs of log(the setting's charged work) − log(NOV's charged work from
  the same initial state). An unsolved run scores log of its work at the cap plus log(1 + least violated count).
- **What is minimized.** E, Gb, Gm and ST minimize the mean over the three tuning patterns; Erb minimizes the mean over `rand` and
  `block`.
- **Tie rule** (declared because Erb's patterns cannot tell a high θ from a higher one): for E, Erb and Gb, among settings within
  0.01 of the best score, the most eager is taken. That is the first in grid order: smallest θ, then largest ρ_max, largest ρ_min,
  smallest rb; for Gb, largest ρ, then smallest rb. Gm and ST take the least score.
- **The comparators** NOV and PS are re-tuned per cell on 8 tuning instances × 3 runs by mean log charged work, cap 2·10^7. A best
  setting on a grid edge is reported, and the grid is not widened after the freeze.

## Measures

As in SLOW-LOOP (A91):
- **charged work W**, incidences read by both loops, with probes and rebuilds counted; CPU beside it;
- **the statistics:** the per-instance geometric mean of five runs, the cell median, R against F with a 99% paired bootstrap over
  instances (10,000 resamples), and the censoring bounds;
- **ratios between arms** the same way: E/Gb (earning against a fixed batched budget), E/GbO (regret against the per-cell
  oracle), E/Gm, E/ST, E/GO, E/G, Erb/E, Erb/ErbL (the tie rule's share), Gb/Gm;
- **diagnostics:** the earned budget's highest value (ρ_top), its doublings, classes left, ties, rebuilds.

## Verdicts and decision rule (frozen)

The verdict for each arm in each cell is SLOW-LOOP's:
- **charged win:** R_W ≤ 0.8 with its upper end below 0.9, and R_CPU's upper end below 1;
- **work win:** the W condition without the CPU one;
- **loss:** R_W's lower end above 1.1;
- **parity or inconclusive:** otherwise.

Definitions:
- **A win** is a charged win; a work win does not count.
- **The structured held-out cells** are `local` w15 at density 3.5 (the primary), `local` w40, `local` w20 and `local` w10 at
  density 3.0.
- **The structure-poor cells** are `rand` 2.1, `rand` 3.0 and `heavy`.
- **Order.** The readings are applied in order, and the first that holds is the verdict.

1. **The earned budget works.** All of the following hold:
   - E wins on the primary and on at least one more structured held-out cell;
   - E has no loss on a structure-poor cell;
   - E/Gb ≤ 0.9 (upper end below 1) in some cell, structured or not, and E/Gb's upper end is below 1.1 in every cell;
   - E/ST's upper end is below 1 in some cell where E wins;
   - E/GO ≤ 1.5 on `local` w10.
2. **It works, but earning is not shown to matter.** E wins on the primary and one more structured held-out cell, with no loss on
   a structure-poor cell, but one of reading 1's comparisons fails. The note says which.
3. **Partial.** E wins on some structured held-out cell, but not as 1 or 2 require.
4. **No win** on any structured held-out cell.

Beside the rule:
- whether Erb, tuned without a local pattern, has a charged win on `local` w10 3,200 (SLOW-LOOP's obstruction removed or not), and
  whether ErbL does too (if not, the tie rule supplied it);
- E/GbO, the regret against a fixed budget tuned on each cell itself.

## Gates (run before the freeze)

G0–G7 are SLOW-LOOP's, with G1, G4 and G7 also run on the earned budget with batched rebuilds:
- G1 is brute-force soundness and the one-for-one map on 240 small instances;
- G4 is the wrong-parity mutant;
- G7 checks every move against the planted state at 800 and 3,200.

Two gates are added:
- **G8:** the earned budget rises above 0.12 on `local` w10 at 3,200 and stays at its floor on `rand`;
- **G9:** this driver reproduces SLOW-LOOP's run for run (flips, work, moves) for G, GO and ST on 12 instances.

## Predictions (frozen)

| # | Prediction | Probability | Fails when |
| --- | --- | --- | --- |
| P1 | E charged win on the primary cell (`local` w15 at density 3.5, never run) | 60% | otherwise |
| P2 | E charged win on `local` w20 (seen in calibration) | 85% | otherwise |
| P3 | E charged win on `local` w40 | 65% | otherwise |
| P4 | E charged win on `local` w10 at density 3.0 | 35% | otherwise |
| P5 | E costs at most 10% on every structure-poor cell (R_W ≤ 1.1 on `rand` 2.1, `rand` 3.0 and `heavy`) | 85% | above on one |
| P6 | Earning matters, jointly: E/Gb ≤ 0.9 (upper end below 1) somewhere and E/Gb's upper end below 1.1 everywhere | 50% | otherwise |
| P7 | Erb charged win on `local` w10 3,200 (SLOW-LOOP's obstruction removed; read beside ErbL) | 70% | otherwise |
| P8 | E within 1.5 times GO on `local` w10 3,200 (E/GO ≤ 1.5) | 60% | above |
| P9 | Small regret: E/GbO ≤ 1.25 on every structured held-out cell | 50% | above on one |
| P10 | CDCL solves every instance of the three new local patterns in under 1 s of wall time | 95% | some instance takes longer |
| P11 | Soundness in every run | 99% | any contradiction or failed check |
| P12 | E charged win on `block` 3,200 | 30% | otherwise |

**Publication hold.** As before: planted patterns, local search and probing by propagation give no general method. The thread tells
the owner before committing if a slow arm's work on `rand` or `heavy` grows with n clearly more slowly than F's.

## Runs and stop rule

On the shared runner, with at most 5 workers to share the machine with MEET-TRANSFER:
1. **R1, re-tuning:** 13 cells × 58 settings × 8 instances × 3 runs.
2. **P1, policy tuning:** 3 patterns × (90 + 15 + 48 + 8 settings) × 8 instances × 3 runs.
3. **O1, the per-cell oracle:** 10 cells × 15 settings × 8 instances × 3 runs at n = 3,200.
4. **T1, the test:** 10 cells × 11 arms × 50 instances × 5 runs, and CDCL.
5. **T2, a stress cell,** registered and in the background: `local` w20 and `heavy` at n = 12,800, 20 instances, five runs, NOV,
   PS, E, Erb, Gb and ST.
   - **R2.** NOV and PS are re-tuned at 12,800 over the 3,200 choice and its grid neighbours, on 8 instances × 3 runs (the
     advisor asked for a re-tune; the full grid at 12,800 would cost about six CPU-hours).
   - **The slow arms** keep their 3,200 policies and use the re-tuned NOV setting.

Estimates: R1 30–50 min, P1 15–30 min, T1 about an hour, T2 30–60 min, with estimates here running about twice too low. The study
stops at the decision rule. No arm, cell or setting is added after the test results are seen, except T2.

## Not done, with the reason

- **Attention targets for the earned arms.** SLOW-LOOP found them no better than random and costly to read. Gm keeps them, as
  SLOW-LOOP's policy did.
- **Shadow knots.** They turned no SLOW-LOOP cell into a win, so they are off in the new arms.
- **A clause-weighting comparator** (SLOW-LOOP#2) is a separate direction.
- **The learned agent as the fast loop** is SLOW-LOOP#3, under B191.
