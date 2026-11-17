# Referee report AGENT-LOOP-R1 (fresh code, no Codex)

**Verdict: Confirmed with fixes. No Block.**
- **What holds.** Every number and both frozen verdicts recompute: memory "no difference shown", loop reading 4 on local and 5 on
  block. Every reported state checks, and the first cells were untouched before the freeze.
- **The main fix: the memory test had almost no power, and the note does not say so.** Two positive controls, run in the study's
  own regime, show it.
  - **On `local` w30** wiping the agent's memory every 100 flips changes nothing (1.00 to 1.02).
  - **On `block`** memory matters only over the last few hundred to two thousand flips. The rebuilds are 3,500 to 6,400 flips
    apart, so a perfect carry could gain at most 0 to 13%.
  - **A deliberately scrambled carry** is called "no difference" on the first block cell, as this carry rule was.

  So "carried = restarted" is the frozen verdict, correctly computed, but it is not evidence that this carry rule is harmless or
  preserves useful memory.
- **Two smaller Narrowings** concern the line summary's "the loop neither creates nor multiplies" the agent's lead, and "four
  studies found the same boundary".

## What holds

- **Order and code.**
  - **Times.** The freeze, `cf3982921`, is at 11:02:44 UTC; the test job was created at 11:02:53 and ran to 11:37.
  - **Code.** Its `job.py` sha256 (`f1dcc39b…`) is the committed file, and no study code changed between the freeze and the close.
- **The first cells were untouched.**
  - **Calibration.** The calibration and dry run (`calibration/`) used only `local` w10, `local` w20, `block` w20 and `rand` 2.1,
    on seeds 9,600,000+.
  - **Earlier studies.** No earlier study in the workspace ran `local` w30 or `block` w40. SLOW-LOOP and EARN-BUDGET ran `local`
    w40 and their own block window.
  - **What calibration changed.** The block family, the per-flip budget and the slow-loop-alone arm came from calibration on other
    cells. The block family was chosen after calibration showed the agent ahead on block, as disclosed.
- **Seeds and initial states.** The test seeds are 9,100,000 to 9,100,049, disjoint from calibration and from Dr's training. The
  agent's engine, its handle and Novelty+ draw identical initial states: 150 of 150 checked, against the note's 5.
- **The planted state** appears only in the generators (and in gate A2). It is not read by `agent_loop.py`, `job.py`, the agent's
  engine or its handle.
- **Gates.** Rerun today, `check.py` passes A1 to A4 (FAILS: 0), with the frozen counts.
- **Every reported state checks.**
  - **The stored flags.** All 21,633 solved runs of 24,000 carry `verified = true`.
  - **The referee's rerun** (`referee_verify.py`, `.json`). Every arm under the loop (GN, GNf, GNco, and DrC, DrR, DrCf and DrRf
    for both seeds) was rerun on instances 0 to 9 of all six cells: 3,300 runs.
    - Each reproduces its stored flips, work and outcome exactly.
    - Each final state satisfies every original knot by the referee's own test.
    - Every merged class holds in the planted state, as a proved tie must.
- **The headline, recomputed with the referee's own code** (`referee_R_agent.py`, `.json`).
  - **The statistic.** Per instance, the geometric mean of five runs; per cell and arm, the median; ratios of medians with 99%
    paired bootstraps; R against the better of NOV and NOV8; the 10% capped rule; tests per Dr seed.
  - **Every table value in the note recomputes,** for example:
    - M1 on `block` w40 in flips: 0.99 [0.90, 1.08] and 0.89 [0.82, 1.03];
    - M3 on `block` w40 in flips: 0.65 [0.54, 0.71] and 0.56 [0.47, 0.67];
    - M2 on `local` w30 in work: 0.18 and 0.15;
    - M4 in work on `rand`: 0.69 and 0.71;
    - the co-flip targets: 1.36 to 1.59 in work;
    - the slow loop alone: 0 of 1,500 solved, with median remainders of 106, 203 and 124 classes on `local`.
  - **Room.** 0.54 and 0.75 to 0.76 on `local` w30; 0.88 to 0.92 on block.
  - **Capped shares.** NOV8 is capped in 74%, 99.6% and 71% of runs; no R is a bound.
- **Seed agreement in every verdict.** Every test on every cell has both seeds on the same side of its line; no "seeds disagree"
  occurs. The family rule (first cell, plus one second cell) gives exactly the frozen verdicts.
  - *Memory:* "no difference shown" on both families, in both measures.
  - *Loop:* 4 on `local` (M2 in both measures), 5 on `block` (M3 in flips).
- **The two budgets (A95).** The referee reread every M2 and M3 test under the other budget (`referee_budget_swap.py`, `.json`).
  - **Only one verdict changes.** On `local`, M3 in flips would hold under EARN-BUDGET's rule, at 0.54 to 0.57. That is the
    agent buying about five times the proofs per flip, the exact problem calibration found and the per-flip budget removes.
  - **Every other verdict is the same under either budget.**
  - So A95 does its work in one place only, as designed and disclosed, and the local loop reading rests on it.
- **The carry rule (A94) is implemented as stated.**
  - **Identity.** On an unchanged pattern, carrying the agent's state through the rule every 1,000 flips reproduces the stored Dr
    runs exactly: 40 of 40 instance-seed pairs on `block` w40 and on `local` w30 (`referee_carry_identity.py`, `.json`).
  - **Mapping.** Values come from the slow loop's vote; ages are the latest of a class; counts are decayed sums; the random stream,
    step and recurrent state are kept.
- **The `rand` identity is a driver check, not a memory control.** Carried and restarted runs are identical in 1,000 of 1,000 (both
    budgets). But no rebuild happened in any of them (0 rebuilds), so the carry path never ran on `rand`.
- **M4 in work.**
  - **The `rand` and block passes are dilution.** The slow work is the same for both fast loops: 1.37·10^6 and 1.38·10^6 on
    `rand`, and 2.29·10^6 and 2.27·10^6 on `block` w40. That cost is bounded (each knot probed once) and spread over the agent's
    larger fast work.
  - **On `local` w10 and w20 the pass has another cause.** There the agent buys 2.6 to 2.7 times Novelty+'s probing, and the pass (0.61 to
    0.71) comes from the loop removing most of the search, the part where the agent's per-flip premium sits.
  - **Either way it is not a better use of the reshaped pattern.** M3 in flips is 0.98 to 1.00 there.
- **Prior work.**
  - `objects-gate` asks for the epics `RULER-LEVEL-20261114-001` and `WHERE-NEXT-20261116-001`, as the note's deviations say.
  - A search for learned local search with memory carried through variable substitution found nothing. It found learned SLS
    heuristics (Yolcu and Póczos 2019; Interian et al. 2023) and inprocessing by equivalent-literal substitution. The
    note's "not, as far as this program found, measured in the SAT literature" stands as worded.

## 1. The memory test had almost no power, and the limit is not stated (Narrowing)

The study's "room" (the share of flips after the first change, 0.54 to 0.92) measures how much search is left after a change. It
does not measure whether the agent's memory matters over the stretch a restart wipes.

The referee measured that directly (`referee_memory_power.py`, `.json`; 3,000 cases, 15,000 runs). The study's own driver ran
under the per-flip budget, with two wrappers:
- **wipe every K:** the memory is also wiped every K flips between rebuilds, exactly as the study's restart path wipes it at a
  rebuild;
- **scramble at every rebuild:** the carried ages and counts are permuted among the new distinctions and knots, a deliberately
  wrong carry.

The agent alone was also run with memory wiped or scrambled every K flips on the unchanged pattern. The reference arms reproduce
the stored DrRf, DrCf and Dr runs exactly in all 50 instances of every cell and seed.

| Cell (rebuild spacing, per-flip budget) | Wiped every 100 | every 500 | every 2,000 | Agent alone, wiped every 5,000 | Scrambled carry at every rebuild | Study's M1 |
| --- | --- | --- | --- | --- | --- | --- |
| `local` w30 (about 2,000 flips) | 1.00 [0.98, 1.02], 1.02 [1.00, 1.05] | 1.00, 1.00 | 1.01, 1.01 | — | 0.99, 1.00 | 1.00, 0.99 |
| `block` w40 (about 5,700 to 6,400) | 1.67 [1.45, 1.85], 1.71 [1.51, 2.04] | 1.27, 1.25 | 1.13 [1.00, 1.28], 1.00 | 0.99, 0.99 | 1.01 [0.95, 1.10], 1.13 [0.95, 1.27] | 0.99, 0.89 |
| `block` w20 (about 3,500 to 4,200) | 1.60, 1.92 | 1.24, 1.32 | 1.03 [0.94, 1.19], 1.05 [0.96, 1.20] | 1.01, 0.93 | 1.15 [1.04, 1.31], 1.06 [0.95, 1.13] | 0.92, 0.93 |

Values are against the unwiped or unscrambled arm, for Dr seeds 0 and 1, with 99% intervals.

- **On `local` w30 the agent's memory has no measurable value in this regime.** Under the loop, wiping it every 100 flips costs
  nothing. So no carry rule, good or bad, could have shown a difference there; M1 was untestable on local, not merely null.
- **On block, memory matters only at short range.**
  - Wiping every 100 flips costs 1.6 to 1.9 times, every 500 flips 1.24 to 1.32, every 2,000 flips 1.00 to 1.13 (intervals
    reaching 1), and every 5,000 flips nothing.
  - The study's rebuilds are 3,500 to 6,400 flips apart. So a restart at a rebuild loses only memory the agent would soon have
    rebuilt, and a perfect carry could gain at most what a wipe at that spacing costs: 0 to 13%.
  - The frozen "carry helps" bar (≤ 0.9 with the upper end below 1) was out of reach for any carry rule.
- **A wrong carry is not detected either.** Scrambling the carried memory at every rebuild gives 1.01 and 1.13 on the first block
  cell; neither seed passes "carry hurts" (≥ 1.11, lower end above 1). Only one seed passes on `block` w20. By the frozen rule a
  scrambling carry rule would also read "no difference shown" on the block family.

**What stands and what does not.**
- **What stands.** "No difference shown" is the frozen verdict, correctly computed. "The metacognition picture, in this specific
  form, is not supported" stands only as "not testable at these rebuild spacings".
- **What does not hold, wherever it appears:**
  - "the carried memory did no harm, so the carry rule does not put the agent off its training";
  - "memory ... can be carried through a change of the pattern without harm, but here without use";
  - the G15 row's "survives a change of the pattern without harm and without use";
  - A94's history "so the rule does no harm";
  - direction #1's "this study shows the carry rule is safe to train with".

  The test could not tell this carry rule from a scrambled one on the first block cell.

**For direction #1.** Its stop rule ("carry/restart stays within 0.9 to 1.1") would be met almost by construction, unless the
rebuilds come closer together than the agent's memory range (a few hundred to 2,000 flips) or the trained agent's memory reaches
further.
- **A power check first.** Make the wipe-every-K control above the first step: show that wiping at the planned spacing costs at
  least about 1.2 before reading carry against restart.

## 2. The line summary: "neither creates nor multiplies" and "four studies, one boundary" (Narrowing, wording)

**"The loop neither creates it nor multiplies it"** (what the line established, item 5) is stronger than the cells.
- **On the first block cell the interaction held.** The frozen interaction test in flips held for both seeds on `block` w40:
  0.82 [0.71, 0.96] and 0.80 [0.67, 0.99]. There the loop cut the agent's flips to 0.83 to 0.85, and did not help Novelty+
  (GNf/NOV 1.04).
- **It was not replicated on `block` w20.** There the loop helped both: it halved the agent's flips (M2 holds, 0.42 to 0.47) and
  helped Novelty+ more (M4 1.22 to 1.34).
- **A fair wording.** "The agent's lead exists without the loop (alone, 0.42 to 0.79 of Novelty+'s flips). The loop's added help
  is small on the first block cell (an interaction of 0.80 to 0.82 there, not replicated) and larger for Novelty+ on the second."

**"Four studies found the same boundary, that proofs pay where propagation finds structure"** (what I would do next) counts studies
that tested different things.
- **SLOW-LOOP and EARN-BUDGET located the boundary** with proved moves.
- **SPEC-MERGE showed that one design of unproved moves did not cross it.** It left untried the corner the referee found:
  precision 0.98 on `rand` 3.0, where proofs found nothing, with smaller rounds checked per merge. That is the decision's own
  direction #3.
- **AGENT-LOOP showed that a second fast loop does not change it** on local patterns, under the same slow loop.
- **The common scope.** All four use planted not-all-equal patterns at n ≤ 12,800.
- **A fair wording.** "Two studies located the boundary, one showed one unproved design does not cross it (one corner untried),
  and one showed a learned fast loop does not move it." "A further variant is unlikely to move it" is a judgement and may stay as
  one.

## 3. Smaller points (Not a block)

- **M4 in work on `local`.** "M4 in work measures that dilution" fits `rand` and block. On `local` w10 and w20 the pass comes from
  the loop removing the search where the agent's per-flip premium sits (above). The conclusion, no better use of the reshaped
  pattern, is the same.
- **The `rand` identity.** C4 ("carried and restarted memory coincide in every run") is true, but it is a driver check: no rebuild
  occurred on `rand`, so the carry rule never ran. The note's "So the carry rule ..." does not rest on it, but A3 and C4 should be
  described as such.
- **CPU.** M3 in CPU is 1.9 to 2.6 times under EARN-BUDGET's rule and 2.9 to 3.8 times under the per-flip budget. The note's "1.9
  to 3.8" spans both budgets.
- **Words.** No spatial word is used for the program's objects.

## Fixes for the thread (listed for the owner, not folded in)

1. **State that the memory test had almost no power, with the controls above.**
   - **The no-harm claims.** Withdraw "the carry rule does no harm" and "safe to train with" (the note, the line summary item 4,
     the G15 row, A94's history, direction #1's rating).
   - **The verdict's reading.** Keep "no difference shown" as the frozen verdict, read as "not testable at these rebuild spacings"
     on block, and "untestable" on local.
   - **Direction #1.** Add the wipe-every-K power check as its first step. **Narrowing.**
2. **The line summary.**
   - Replace "the loop neither creates nor multiplies it" with the block w40 interaction (0.80 to 0.82, not replicated) and the
     w20 result.
   - Restate "four studies found the same boundary" as what each study tested, with SPEC-MERGE's untried corner.
   - **Narrowing** (wording).
3. **Small points.** M4 in work on `local` is explained by removed search, not dilution; describe A3 and C4 as driver checks; give
   the CPU range per budget. **Not a block.**

## How the work was split

- **The referee:**
  - read the pre-registration, both drafts, the note, the decision, A94, A95 and the code (`agent_loop.py`, `job.py`,
    `analyze.py` and the agent's `handle.py`);
  - recomputed every test, verdict, room, R and capped share from the raw results;
  - reread M2 and M3 under the swapped budgets;
  - ran the memory power controls with wrappers on the study's driver;
  - reran 3,300 loop runs and checked their states and merges;
  - checked the freeze, the calibration cells and the initial states;
  - reran the gates and the objects gate;
  - searched for prior work.
- **Helpers:** no Claude helper was used. **Codex** was not used. **The advisor** was not consulted.

## Files

- `referee_R_agent.py` and `.json`: the recomputation.
- `referee_budget_swap.py` and `.json`: M2 and M3 under the other budget.
- `referee_memory_power.py`, `referee_memory_power_runs.jsonl` and `referee_memory_power.json`: the power controls.
- `referee_verify.py` and `.json`: 3,300 loop runs rerun and checked.
- `referee_carry_identity.py` and `.json`: the carry rule on an unchanged pattern.
