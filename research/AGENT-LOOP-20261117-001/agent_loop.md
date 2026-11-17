# The learned agent under the proof-based slow loop: carrying its memory across the loop's changes showed no difference, in a test that could not have shown one; the loop helps it where proofs find structure, and there any search then finishes equally

Epic `AGENT-LOOP-20261117-001`, ticket `AGENT-LOOP-20261117-001A` (sub-goal B191, `SPEC-MERGE-20261117-001#1`, the coordinator's
go-ahead; goals G15, G16), 2026-11-17.
- **Evidence:** **computed** on finite experiments with planted instances, every run kept.
- **Frozen** before any test instance ran ([pre-registration](preregistration.md), freeze commit `cf3982921`). The advisor reviewed
  the design and said "freeze with changes", all taken ([advisor review](advisor_review.md)).
- **Refereed: confirmed with fixes, no Block** ([report](referee-R1/report.md)).

**Corrected 2026-11-17 after the referee** (logged in `docs/CORRECTIONS.md`; both frozen verdicts stand and recompute):
- *Narrowing (the main one): the memory test had almost no power.* "Room", the share of flips after the first change, measures
  how much search is left after a change. It does not measure whether the agent's memory matters over the stretch a restart wipes.
  The referee measured that in this study's own regime (15,000 runs, the per-flip budget), wiping the agent's memory every K flips
  between rebuilds:
  - **On `local` w30,** wiping it every 100 flips changes nothing (1.00 to 1.02), and scrambling the carried memory at every rebuild
    changes nothing (0.99 to 1.00). M1 was untestable on local, not merely null.
  - **On block,** wiping every 100 flips costs 1.6 to 1.9 times, every 500 flips 1.24 to 1.32, every 2,000 flips 1.00 to 1.13, and
    every 5,000 nothing. The rebuilds were 3,500 to 6,400 flips apart, so a perfect carry could have gained at most about 0 to 13%,
    and the frozen "helps" bar was out of reach for any carry rule.
  - **A deliberately scrambled carry** gives 1.01 and 1.13 on the first block cell, so it too would read "no difference shown".

  So "no difference shown" stands as the frozen verdict, read as **not testable at these rebuild spacings** (block) and
  **untestable** (local). "The carry rule does no harm" and "safe to train with" do not follow, and are withdrawn below and in the
  decision, the goals, A94 and the intuition entry.
- *Narrowing (wording), in the decision's line summary.*
  - "The loop neither creates nor multiplies the agent's lead" was too strong. On the first block cell the frozen interaction in
    flips held for both seeds (0.82 [0.71, 0.96], 0.80 [0.67, 0.99]); it was not replicated on `block` w20.
  - "Four studies found the same boundary" counted studies that tested different things. Two located the boundary with proved
    moves; one showed that one unproved design does not cross it, leaving a corner untried; this one showed a learned fast loop
    does not move it.
- *Not a block.*
  - **M4 in work on local.** "Dilution" fits `rand` and block. On `local` w10 and w20 the agent buys 2.6 to 2.7 times the probing,
    and the pass comes from the loop removing the search, where the agent's per-flip premium sits.
  - **The `rand` identity** (C4, gate A3) is a driver check. No rebuild happened in any `rand` run, so the carry path never ran
    there.
  - **CPU.** M3 in CPU is 1.9 to 2.6 times under EARN-BUDGET's rule and 2.9 to 3.8 times under the per-flip budget.
- **These moves keep the allowed states.** Every merge is a proved tie. Every state reported in the 24,000 test runs was mapped
  back and checked on the original knots, and the 21,633 solved runs all satisfied them.
- **The canonical K1–K3 test** is unchanged.

## The question, and the answer

This study tested the owner's picture as one system:
- **The fast loop** is the learned navigating agent Dr of `MEET-TRANSFER-20261117-001` (both seeds). It attends to a violated knot,
  flips one of its distinctions and remembers its steps. It was trained on `rand` 2.1 only.
- **The slow loop** is EARN-BUDGET's eager, batched, proof-based loop. It probes knots by bounded propagation, merges the ties it
  proves, and rebuilds the pattern.
- **Memory across a change.** At every rebuild the agent's whole memory (values, recurrent state, ages, visit counts) was carried
  across by SIGNED-NAV's carry rule, or restarted from the mapped values.

The comparisons were the agent alone, Novelty+ under the same loop, and the slow loop alone. Flips are read under a per-flip proof
budget, the same for every fast loop. Charged work is read under EARN-BUDGET's rule, under which every fast loop spends the same
share of its work on proofs.

**The answer has three parts.**

1. **Memory: carrying it across the changes showed no difference** (the frozen memory verdict, "no difference shown", on both
   families and in both measures), **but the test could not have shown one** (corrected after the referee).
   - **Where it was tested.** It was read only where there was room: on `local` w30, 54% to 76% of the restarted runs' flips came
     after the first change, and on `block` 88% to 92%.
   - **The ratios.** Carried over restarted memory was 0.99 to 1.01 on the local cells. On `block` it was 0.89 to 0.99 in flips
     and 0.95 to 1.02 in work, with every interval reaching 1.
   - **What it shows: little.** In this regime the agent's memory does not matter on local patterns at all, and on block patterns
     it matters only over the last few hundred to 2,000 flips, while the rebuilds were 3,500 to 6,400 flips apart. A scrambled
     carry would have read the same. So the result says neither that this carry rule is harmless nor that it keeps useful memory
     (withdrawn after the referee: "the carried memory did no harm, so the carry rule does not put the agent off its training").
2. **The loop: on local patterns it helps the agent enormously, but then the agent does no better than Novelty+** (loop reading 4).
   - **Against the agent alone.** Under the loop the agent needed 0.02 to 0.06 of its flips and 0.07 to 0.18 of its charged work.
   - **Against Novelty+ under the same loop.** At the same proofs per flip, the agent needed 0.98 to 1.00 of Novelty+'s flips. It
     cost 1.44 to 1.75 times its charged work, and 1.9 to 2.6 times its CPU under EARN-BUDGET's rule (2.9 to 3.8 under the per-flip
     budget).
   - **Why: the slow loop does nearly all the work there.** Alone, it shrinks the 3,200 distinctions to 106 to 203 classes and
     then stops, solving none of 750 runs. Its work up to that point (4.3 to 5.8·10^6) is about what Novelty+ under the loop
     spends in total (3.3 to 5.9·10^6). Whatever fast loop finishes the small remainder, it finishes it in about the same number of
     flips.
3. **On block patterns the agent is the better searcher, but the loop adds little to it** (loop reading 5).
   - **Against Novelty+ under the same loop.** In flips the agent needed 0.51 to 0.65 of Novelty+'s, on both cells and both seeds.
   - **The agent's own lead.** That lead is the agent's own: alone, it already needs 0.42 to 0.79 of the better Novelty+'s flips.
   - **What the loop adds.** On the first cell (`block` w40) the loop cut the agent's flips only to 0.83 to 0.85, short of the
     frozen 0.8, and it raised its charged work to 1.69 to 1.85. On `block` w20 it cut them to 0.42 to 0.47, but the family verdict
     needs the first cell.
   - **What wins where.** The cheapest in charged work on both block cells is Novelty+ alone.

**The interaction (M4), beside the verdicts.** It asks whether the loop helps the agent more than it helps Novelty+. In flips it held on
`block` w40 (0.80 and 0.82) but not on `block` w20 (1.22 and 1.34), so it is not replicated. On local patterns the loop helps
Novelty+ more (2.0 to 2.9).
- **In work the frozen test passes on four cells,** but the control shows what it measures. On `rand`, where nothing is proved,
  it passes too (0.69 and 0.71).
- **Why it passes there.** The probing is bounded by the knots there are to probe, since each is probed once. Its cost is therefore
  close to fixed (about 1.4·10^6 on `rand`), and spread over the agent's four to five times larger fast work it is a smaller share.
- **So M4 in work measures that dilution on `rand` and block,** not a better use of the reshaped pattern. On `local` w10 and w20 the
  pass has another cause (found by the referee): there the agent buys 2.6 to 2.7 times the probing, and the loop removes most of
  the search, where the agent's per-flip premium sits. M3 in flips is 0.98 to 1.00 there.

**The co-flip targets (secondary) never paid.** Probing the pairs that Novelty+ keeps moving together, instead of random knots, cost
1.36 to 1.59 times the work on the local and block cells (2.26 on `rand`). On local patterns it also needed 1.37 to 1.57 times the
flips.

**What it means for the owner's picture.** Here the fast and slow loops each do real work where they are strong: the slow loop on
patterns where propagation proves ties, the agent on patterns where search stays hard. But they do not combine into more than their
parts except on one cell, not replicated (M4 in flips on `block` w40). The metacognition picture, in the specific form "memory
survives a change of structure usefully", was **not testable at these rebuild spacings**: the agent's memory matters only over a
shorter stretch than the loop leaves between changes (corrected after the referee). The agent was never trained with changes in
its episodes. Testing the picture needs changes closer together than the agent's memory range, or an agent whose memory reaches
further, with a power check first (direction #1 of the line summary in the [decision](decision.md)).

**In standard terms.** A learned local-search policy with history features, interleaved with inprocessing (failed-literal probing
and equivalent-literal substitution). Its internal state is mapped through each substitution. On planted not-all-equal patterns:
- inprocessing does most of the work on locally structured instances;
- the policy's memory transfer under substitution is neutral;
- the learned policy's advantage is its own and does not grow under inprocessing.

None of this bears on satisfiability in general. CaDiCaL solves these local patterns in about 0.05 s, and no `rand` cell won, so no
publication-hold question arose.

## Results

Per instance, the geometric mean of five runs; per cell, the median over 50 fresh instances. A ratio is the ratio of cell medians,
with a 99% paired bootstrap interval. The two values are Dr's seeds 0 and 1. The first cell of each family (never run before the
freeze) is listed first.

**Memory (M1)**: carried over restarted memory. Flips are under the per-flip budget (DrCf/DrRf), work under EARN-BUDGET's rule
(DrC/DrR).

| Cell | Room (EARN-BUDGET's rule; per-flip) | Flips | Work | Verdict |
| --- | --- | --- | --- | --- |
| `local` w30 | 0.54; 0.75–0.76 | 1.00 [0.98, 1.01], 0.99 [0.97, 1.03] | 1.00 [0.96, 1.05], 1.01 [0.96, 1.04] | no difference |
| `local` w10 | 0.11–0.12; 0.51 | 0.99, 1.00 | no room | no difference (flips) |
| `local` w20 | 0.29; 0.63 | 0.99, 1.01 | no room | no difference (flips) |
| `block` w40 | 0.91–0.92; 0.91 | 0.99 [0.89, 1.08], 0.89 [0.81, 1.03] | 0.95 [0.89, 1.06], 0.99 [0.92, 1.05] | no difference |
| `block` w20 | 0.88–0.89; 0.89–0.90 | 0.92 [0.83, 1.04], 0.93 [0.88, 1.05] | 0.98, 1.02 | no difference |
| `rand` 2.1 | 0 | identical in 500 of 500 runs | identical | no room (control) |

On the block cells the agent made a median 4 to 7 rebuilds, with 3,750 to 9,900 flips after the first rebuild per rebuild.

**Loop**: M2 is the loop over the agent alone (DrCf/Dr in flips, DrC/Dr in work); M3 is the agent under the loop over Novelty+
under the same loop (DrCf/GNf in flips, DrC/GN in work).

| Cell | M2 flips | M2 work | M3 flips | M3 work |
| --- | --- | --- | --- | --- |
| `local` w30 | 0.06, 0.05 | 0.18 [0.15, 0.23], 0.15 [0.12, 0.19] | 1.00 [0.97, 1.02], 0.98 [0.96, 1.01] | 1.75, 1.74 |
| `local` w10 | 0.02, 0.02 | 0.07, 0.07 | 0.99, 0.98 | 1.45, 1.44 |
| `local` w20 | 0.03, 0.03 | 0.09, 0.09 | 0.98, 0.99 | 1.61, 1.60 |
| `block` w40 | 0.85 [0.79, 0.94], 0.83 [0.75, 0.99] | 1.69, 1.85 | 0.65 [0.54, 0.71], 0.56 [0.47, 0.67] | 1.33, 1.29 |
| `block` w20 | 0.47, 0.42 | 1.23, 1.22 | 0.57, 0.51 | 1.21, 1.19 |
| `rand` 2.1 | 1.00, 1.00 | 1.14, 1.18 | 1.15, 0.90 | 3.45, 2.77 |

- **Family verdicts.**
  - **M2:** holds on local in both measures. On block it fails in both, since in flips the first cell gives 0.83 to 0.85.
  - **M3:** holds on block in flips only, and fails on local in both measures.
- **The frozen verdicts.**
  - **Memory:** "no difference shown" on local and block, in flips and in work.
  - **Loop:** reading 4 on local (the loop helps the agent, but the agent under the loop does not beat Novelty+ under the loop).
    Reading 5 on block (the agent under the loop beats Novelty+ under the loop in flips, but the loop does not help the agent).

**Against Novelty+ alone** (R against F, the better of (0.7, 0.01) and (0.8, 0.01)):

| Arm | `local` w30 flips | work | CPU | `block` w40 flips | work | CPU |
| --- | --- | --- | --- | --- | --- | --- |
| GN (Novelty+ under the loop) | 0.02 | 0.17 [0.14, 0.22] | 0.19 | 1.08 | 4.50 | 4.80 |
| Dr alone | 0.34, 0.41 | 1.65, 2.02 | 2.84, 3.35 | 0.79, 0.70 | 3.54, 3.13 | 6.78, 5.72 |
| DrC (agent under the loop) | 0.01, 0.01 | 0.30 [0.24, 0.38], 0.30 | 0.50 [0.40, 0.63], 0.50 | 0.67, 0.60 | 6.00, 5.80 | 12.6, 12.0 |
| GNco (co-flip targets) | 0.03 | 0.27 | 0.57 | 1.04 | 6.12 | 17.7 |

- **The agent under the loop** is a charged win over Novelty+ alone on every local cell: work 0.20 to 0.30, CPU 0.33 to 0.50.
- **Novelty+ under the loop** is a larger win (work 0.13 to 0.17, CPU 0.16 to 0.20).
- **On block w40 the loop costs** both fast loops 4 to 6 times Novelty+ alone's work.

**The slow loop alone (SL)** solved none of its 1,500 runs. It stopped with 106 to 203 classes on the local cells, 2,495 to 3,070
on the block cells, and 3,200 (nothing proved) on `rand`.

**Capped runs.**
- **Novelty+ (0.8, 0.01)** hit the cap in 74% of runs on `local` w30, 99.6% on both block cells and 71% on `rand`. F is then
  Novelty+ (0.7, 0.01), whose capped share is at most 1.6% (`block` w20). No R is a bound.
- **No other arm** was capped.

**Soundness.**
- **Every solved run** (21,633 of 24,000) satisfies every original knot. The unsolved ones are the 1,500 runs of the slow loop
  alone and the capped Novelty+ runs.
- **On `rand`,** where nothing is proved, carried and restarted memory gave identical runs in 500 of 500. This is a driver check:
  no rebuild happened there, so the carry path never ran.

## Predictions

| # | Prediction (probability) | Outcome |
| --- | --- | --- |
| C1 | Check: M2 holds on local in flips and work (95%) | **Held** |
| C2 | Check: local has no room under EARN-BUDGET's rule (95%) | **Failed**: `local` w30 had room 0.54, so its work reading of memory was made (no difference) |
| C3 | Check: the slow loop alone solves no local or block run (95%) | **Held**: 0 of 1,250 |
| C4 | Check: on `rand`, carried and restarted memory coincide in every run (97%) | **Held**: 500 of 500 (a driver check: no rebuild ran) |
| C5 | Check: every reported state satisfies the original knots (99.9%) | **Held** |
| P1 | On block, M2 holds in flips but not in work (65%) | **Failed**: in flips the first cell gives 0.83 to 0.85 |
| P2 | M3 holds on local in flips (7%) | Did not hold (0.98 to 1.00) |
| P3 | M3 holds on block in flips (65%) | **Held** |
| P4 | M3 holds in work on either family (5%) | Did not hold |
| P5 | Memory in flips on block: "no difference shown" (50%) | **Held** |
| P6 | `local` w30 has room under the per-flip budget (70%) | **Held**: 0.75 to 0.76 |
| P7 | M4 holds in work on local (40%) | Did not hold: the first cell gives 1.06 [0.82, 1.39] for seed 0 |
| P8 | DrC is a charged win against F on `local` w30 (80%) | **Held**: work 0.30, CPU 0.50 |
| P9 | M4 holds in flips on either family (5%) | Did not hold: on block it is not replicated |
| P10 | Co-flip targets pay on some local or block cell (10%) | Did not hold (1.36 to 1.59) |
| — | Loop reading 4 on local (88%); on block, reading 2 (50%), 4 (30%), 6 (10%) | Local **4**, as predicted; block **5**, in the 10% left |

- **The scored predictions.** Of the four above 50%, three held (P1 failed). P5, at 50%, held. The five at 40% or below did not
  happen.
- **The checks.** C2 failed: the wider window left more search after the first change than calibration had shown at windows 10
  and 20.

## Deviations

- **The prior-work searches** in the pre-registration ran with the cut-off `--until 2026-11-18`, the day after the freeze; it
  should have been the freeze date (the lesson of `MEET-TRANSFER-20261117-001`'s correction). Rerun with `--until 2026-11-17`,
  both searches return the same records. The objects gate also asks for the epics `RULER-LEVEL-20261114-001` and
  `WHERE-NEXT-20261116-001` to be named, which the frozen text named only as records (`/1`). Neither studies memory across a
  change.
- **The run took 35 minutes** (11:02 to 11:37 UTC) on 6 workers, within the estimate. Most of it was Novelty+ (0.8, 0.01) at the
  cap.

Nothing else differs from the frozen text.

## Limitations

- **The instances.** Planted not-all-equal patterns only, at n = 3,200, with two structured families (local and block) and one
  random cell.
- **The block family** was chosen after calibration had shown the agent ahead there. Its first cell is a new window of a
  calibrated family, a weak reading of "a pattern untouched before the freeze".
- **The agent and the carry rule.** One agent, never trained with changes in its episodes, and one carry rule. A learner trained
  through rebuilds might use carried memory. This study does not test that.
- **The power of the memory test** (found by the referee). At these rebuild spacings the agent's memory hardly matters between
  changes, so M1 could not tell a good carry from a scrambled one.
- **The slow loop.** One slow loop (EARN-BUDGET's eager batched loop, tie merges only), at one setting.
- **CPU.** Thread CPU on a shared runner.

## Where to start again

- **Code** (in `experiments/AGENT-LOOP-20261117-001A/AGENT-LOOP-20261117-001A-E001_agent_loop/`):
  - `agent_loop.py`: the driver. It runs the agent through SIGNED-NAV's handle with carry or restart, Novelty+ with random or
    co-flip targets, or no fast loop, under either budget;
  - `agent/`: SIGNED-NAV's engine and handle, unchanged;
  - `slow_engine.c`, `slow_loop.py` and `spec_merge.py`: copied from SPEC-MERGE;
  - `job.py` and `analyze.py`;
  - the gates: `.venv/bin/python -B experiments/.../check.py`.
- **Runs** (in `artifacts/AGENT-LOOP-20261117-001A/AGENT-LOOP-20261117-001A-E001_agent_loop/`):
  - `test/`;
  - `summary.json` and `analysis_output.txt`;
  - `gates/` and `calibration/`.
- **To rebuild:** `.venv/bin/python -B experiments/.../analyze.py artifacts/.../test artifacts/.../summary.json`.
