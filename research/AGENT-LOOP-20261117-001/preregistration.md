# Does the owner's whole picture work as a mechanism: a learned agent with memory acting on knots while a proof-based slow loop reshapes the pattern?: pre-registration

Epic `AGENT-LOOP-20261117-001` (`SPEC-MERGE-20261117-001#1`, the coordinator's go-ahead of 2026-11-17; sub-goal B191; goals G15,
G16). **Frozen** before any test instance ran. The commit time of this file is the only authority for the freeze.

**What ran before the freeze:**
- the gates (A1–A4);
- a calibration and a dry run of the whole pipeline, on calibration instances (seeds 9,600,000 and up) of the four cells already
  run in the program (disclosed below).

The two first cells, `local` window 30 and `block` window 40, were not run at all.

**Records:**
- **Code** by the thread (Claude), in `experiments/AGENT-LOOP-20261117-001A/AGENT-LOOP-20261117-001A-E001_agent_loop/`:
  - SPEC-MERGE's engine and driver, copied;
  - SIGNED-NAV's signed-knot agent engine and handle, copied unchanged into `agent/` (from commit `0c631cb87`);
  - a new driver, `agent_loop.py`.
- **The drafts,** kept for audit:
  - the first draft, written before the calibration, is [draft1_before_calibration.md](draft1_before_calibration.md) (SHA-256
    `bd4f1353…`);
  - the second draft, as the advisor saw it, is [advisor_prompt_draft2.txt](advisor_prompt_draft2.txt) (`a689e6aa…`).
- **The canonical K1–K3 test** is unchanged.
- **The advisor** reviewed the second draft and said "freeze with changes" ([advisor note](advisor_review.md)).

## The question

This is the first test of the owner's whole picture in one system. The pieces:
- **The fast loop** is the learned navigating agent, which attends to a violated knot, flips one of its distinctions and remembers
  its steps. It is Dr of `MEET-TRANSFER-20261117-001` (unrefereed), both seeds. Dr was trained on `rand` 2.1 only, never on a
  local or block pattern.
- **The slow loop** reshapes the knot pattern under the agent. It is EARN-BUDGET's eager batched proof-based loop:
  - after each epoch of n′ flips it spends a budget on tie probes (bounded refutations by propagation);
  - it rebuilds the pattern on the proven ties when they reach 0.3% of the classes.
- **Memory across a change.** At each rebuild the agent's whole state (values, recurrent state, ages, visit counts) is carried
  across the change by SIGNED-NAV's carry rule, or restarted from the mapped values with fresh memory.

**The frozen primary is the mechanism question, read in flips and in charged work separately:**
1. **Memory (M1).** Does carried memory beat restarting?
2. **The loop (M2).** Does the agent with the slow loop beat the agent alone?
3. **The agent under the loop (M3).** Does it beat Novelty+ under the same slow loop?

Beside them:
- **M4** asks whether the loop helps the agent more than it helps Novelty+ (the interaction). Only M4 can say that the agent
  "uses the reshaped pattern better", since M3 also counts the agent's advantage before any change.
- **The slow loop alone (SL)** shows whether a fast loop is needed at all.

**Stated up front:**
- The agent costs 4 to 14 times Novelty+'s CPU per flip (SPEC-MERGE's context arm), so a win in charged time over Novelty+ under
  the same loop is unlikely. CPU is reported, and no verdict rests on it except P8.
- These moves keep the allowed states: every merge is a proved tie. The carry is a mapping of the agent's memory through the
  substitution, not a statement about the knots.

The secondary question takes SPEC-MERGE's one positive signal, the co-flip evidence, as the target for proofs: probe the pairs the
search keeps moving together instead of random knots, with Novelty+ as the fast loop, under EARN-BUDGET's rule.

## Two problems found in calibration, and the changes

The first draft froze M1 to M3 on the local cells, with EARN-BUDGET's budget rule. Calibration showed two problems.
1. **No room for memory on local patterns.** There the slow loop reduces the pattern to about 100 to 300 classes within two
   rebuilds. Only 12% to 30% of the agent's flips come after the first change, and carried and restarted memory agree to 1%.
   - **Change:** a second family, `block`, was added, where the slow loop proves little and about 90% of the flips come after the
     first change.
   - **Change:** M1 is read only where there is room (below).

   The block family was chosen after the calibration had shown the agent ahead of Novelty+ there in flips (Dr alone, and Dr
   under the loop). Its first cell (window 40) is a new window of a calibrated family. That is a weak reading of "a pattern
   untouched before the freeze", and the report says so.
2. **The budget rule favours the costlier fast loop.** EARN-BUDGET's slow budget is 3 times the epoch's own fast work. The agent
   charges about 240 incidences per flip, Novelty+ about 50, so the agent buys about 5 times the proofs per flip. Under this rule
   the agent "beat" Novelty+ by about half in flips on local patterns purely through more proofs.
   - **Change:** a per-flip budget, 3 × 50 incidences per flip of the epoch, the same for every fast loop.
   - **Change:** each measure is read under the budget that makes it fair (below).

## In standard terms

A learned local-search policy with history features (a recurrent state, ages and visit counts), interleaved with inprocessing
(failed-literal probing and equivalent-literal substitution). The policy's internal state is mapped through each variable
substitution. Memory transfer under problem reformulation is not, as far as this program found, measured in the SAT literature.

**What each outcome would show.**
- **If M1 holds,** an agent's memory survives a change of structure usefully. That is the owner's metacognition picture in its
  most specific form.
- **If M1 shows that carry hurts,** the carried memory may be harmful. One possible cause is the carry rule's merged ages and
  counts, which lie outside what the agent saw in training.
- **If M2 holds,** the slow loop's structure changes help a learned agent as they help Novelty+.
- **If M3 holds,** the agent under the loop beats Novelty+ under the loop, whether or not the loop is the reason.
- **If M4 holds,** the agent uses the reshaped pattern better than Novelty+ does.
- **None of them** would say anything about satisfiability in general. CaDiCaL solves these local patterns in about 0.05 s.

## Prior work in the program

Objects index, searched 2026-11-17:

`python3 -B scripts/track.py objects "learned agent with memory as the fast loop under a structure-changing slow loop" --until 2026-11-18 --exclude AGENT-LOOP-20261117-001`
`python3 -B scripts/track.py objects "memory carried across a change of the knot pattern" --until 2026-11-18 --exclude AGENT-LOOP-20261117-001`

Neither search returned a study of a learned agent under a structure-changing loop, or of memory carried across a change of the
pattern. The nearest records:
- `SLOW-LOOP-20261117-001/1` and `/2`, and `EARN-BUDGET-20261117-001/1`: the slow loop with Novelty+;
- `WHERE-NEXT-20261116-001/1` and `RULER-LEVEL-20261114-001/1`: unrelated to memory.

The study builds on:
- `SLOW-LOOP-20261117-001`, `EARN-BUDGET-20261117-001` and `SPEC-MERGE-20261117-001`: the slow loop;
- `MEET-TRANSFER-20261117-001`: the agent Dr;
- `SIGNED-NAV-20261117-001`: the signed engine and the carry rule.

## Cells and arms

Planted unsigned not-all-equal patterns at n = 3,200, 50 fresh instances per cell (seeds 9,100,000 to 9,100,049), five runs each.
Every arm runs from the same five initial states per instance. Both engines draw the initial state from the run seed with the same
generator; this was checked on 5 seeds.

| Cell | Family | Role | Flip cap |
| --- | --- | --- | --- |
| `local` window 30, density 4.0 | local | **first cell**: never run in the program before the freeze | 2·10^8 |
| `local` w10, density 4.0 | local | second | 2·10^8 |
| `local` w20, density 4.0 | local | second | 2·10^8 |
| `block` w40, density 2.5 | block | **first cell**: never run in the program before the freeze | 2·10^7 |
| `block` w20, density 2.5 | block | second (run in SLOW-LOOP and EARN-BUDGET on other instances) | 2·10^7 |
| `rand` 2.1 | control | the slow loop proves nothing, so carried and restarted memory must coincide | 2·10^7 |

The block cap is 2·10^7 because Novelty+ (0.8, 0.01) never solved a calibration block run within 2·10^8. The slowest other block
arm needed about 2.3·10^5 flips.

| Arm | What it is |
| --- | --- |
| NOV, NOV8 | Novelty+ (0.7, 0.01) and (0.8, 0.01) alone; F is the better of the two, re-chosen per resample |
| GN | Novelty+ (0.7, 0.01) under the slow loop, EARN-BUDGET's rule (budget 3 × the epoch's own fast work), random probe targets |
| GNf | the same under the per-flip budget (3 × 50 incidences per flip of the epoch) |
| GNco | GN with co-flip probe targets (secondary) |
| SL | the slow loop alone, with no fast loop. Each round has the budget of an epoch at the per-flip unit (3 × 50 × n′ incidences). It solves only if the pattern collapses to no knots, and it stops when nothing is left to probe |
| Dr0, Dr1 | Dr alone, each seed |
| DrC0, DrC1 | Dr under the slow loop, EARN-BUDGET's rule, memory carried |
| DrR0, DrR1 | the same with memory restarted from the mapped values, with a fresh random stream |
| DrCf0, DrCf1, DrRf0, DrRf1 | the same two under the per-flip budget |

## Measures and statistic

- **Flips, charged work (v2) and CPU,** each a separate statistic.
  - **The statistic** is the one SLOW-LOOP, EARN-BUDGET and SPEC-MERGE used. Per instance, the geometric mean of five runs; per cell
    and arm, the median over instances. A ratio between arms is the ratio of those cell medians. Its 99% interval is a paired
    bootstrap over instances (10,000 resamples).
  - **CPU** is the run's thread CPU time, measured in the worker around the whole run, probes and rebuilds included.
- **The agent's charged work** is its engine's incidence count, reads included.
- **The slow loop's charge** counts:
  - the probes, and the sweep that finds the last unprobed knots (SL);
  - the stability counts (co-flip);
  - the rebuilds with their sorting;
  - the carry's mapping and the new handles.
- **R** is against F.
- **Capped runs** enter at the cap. A ratio is reported as a bound, and no test holds on it, when either arm (for R: the arm, or
  both NOV and NOV8) has more than 10% capped runs on the cell.
- **Room** on a cell, for a budget, is the median share of the restarted runs' flips made after the first rebuild. The report
  also gives the median number of rebuilds and the flips after the first rebuild per rebuild, since restarting wipes memory at
  every rebuild.

**Each measure is read under the budget that makes it fair:**
- **In flips, the per-flip budget** (DrCf, DrRf, GNf), so every fast loop gets the same proofs per flip.
- **In charged work, EARN-BUDGET's rule** (DrC, DrR, GN), so every fast loop spends the same share of its work on proofs. Under
  the per-flip budget the agent pays about 240 + 150 incidences per flip against Novelty+'s 50 + 150, so M3 in work would fail
  by construction.

The other budget's ratios are reported as context.

## The mechanism tests (frozen)

Each test is computed for each seed of Dr:
- **On a cell,** a test "holds" only when both seeds pass. It reads "seeds disagree" when one does, "fails" when neither does,
  "no room" (M1, either seed short of room) or "bound".
- **On a family,** a test holds when it holds on the family's first cell and on at least one of its second cells. The first
  cell's own verdict is the headline, and the second cells are replication.

| Test | In flips (per-flip budget) | In work (EARN-BUDGET's rule) | Passes when |
| --- | --- | --- | --- |
| M1, carry helps | DrCf/DrRf | DrC/DrR | ≤ 0.9 with the upper end below 1; read only if the cell has room ≥ 0.5 under that budget for both seeds |
| M1, carry hurts | DrCf/DrRf | DrC/DrR | ≥ 1.11 with the lower end above 1; the same room condition |
| M2 | DrCf/Dr | DrC/Dr | ≤ 0.8 with the upper end below 0.9 |
| M3 | DrCf/GNf | DrC/GN | ≤ 0.9 with the upper end below 1 |
| M4 | (DrCf/Dr) ÷ (GNf/NOV) | (DrC/Dr) ÷ (GN/NOV) | ≤ 0.9 with the upper end below 1 |

## Decision rule (frozen): two verdicts

**Memory (first),** per family and measure, from M1:
- "carry helps";
- "carry hurts";
- "no difference shown";
- "no room";
- "bound".

In flips, a "helps" or "hurts" is marked **budget-dependent** if M1 under the other budget (DrC/DrR in flips, context) passes the
opposite way on the first cell.

**Loop (second),** per family, from the measures in which M2 and M3 hold on the family. Applied in order:
1. **Every part pays in charged work:** both hold in work.
2. **Every part pays in flips only:** both hold in flips.
3. **Both hold, in different measures.**
4. **The loop helps the agent, but the agent under the loop does not beat Novelty+ under the loop:** M2 only.
5. **The agent under the loop beats Novelty+ under the loop, but the loop does not help the agent:** M3 only.
6. **No mechanism gain:** neither.

M4, the slow loop alone and the co-flip targets are reported beside the verdicts. The co-flip targets pay on a cell if GNco/GN
≤ 0.9 with the upper end below 1, in work.

## Gates (run before the freeze)

| # | Gate | Fails when |
| --- | --- | --- |
| A1 | With no slow budget, the agent driver reproduces Dr alone run for run (flips and work), and the Novelty+ driver reproduces Novelty+ alone (24 runs) | any differs |
| A2 | 144 runs at n = 800 (`local` w10 and w20, `block`, `rand`): agent carry and restart under both budgets, Novelty+ with random and co-flip targets and under the per-flip budget, the agent with co-flip targets, and the slow loop alone. Each solves (the slow loop alone excepted), every reported state satisfies every original knot, and every proved tie holds in the planted state | any fails |
| A3 | On `rand`, where nothing is proved, carried and restarted memory give identical runs (6 instances) | any differs |
| A4 | The first epoch under the slow loop equals Dr alone capped there | any differs |

All passed (`gates/check_output.txt`): 55,870 merged distinctions checked against the planted state.

## Calibration and dry run (disclosed)

Both were on calibration instances (seeds 9,600,000 to 9,600,003) of `local` w10 and w20, `block` w20 and `rand`, four
instances each, all arms. The values are ratios of medians of five-run geometric means, for the two seeds; the full output is in
`calibration/`.

| Cell | Room (EARN-BUDGET's rule; per-flip) | M1 flips; work | M2 flips; work | M3 flips; work | SL solves |
| --- | --- | --- | --- | --- | --- |
| `local` w10 | 0.12; 0.51 | 0.99–1.01; no room | 0.02–0.03; 0.06–0.08 | 0.99; 1.38–1.40 | 0 of 20 |
| `local` w20 | 0.30; 0.63–0.64 | 0.99–1.01; no room | 0.02–0.03; 0.06–0.11 | 0.99–1.00; 1.60–1.61 | 0 of 20 |
| `block` w20 | 0.87–0.89; 0.89–0.91 | 0.90–0.91; 1.05 | 0.41–0.46; 1.12–1.30 | 0.52–0.58; 1.14–1.22 | 0 of 20 |
| `rand` | 0; 0 | 1.00; 1.00 | 1.00; 1.13–1.18 | 0.86–1.22; 2.65–3.63 | 0 of 20 |

In flips under EARN-BUDGET's rule (context), M1 on `block` w20 was 1.09–1.10, the opposite side of 1 from the per-flip budget's
0.90–0.91.

The calibration fixed the design changes above. It informed the predictions below, which is why they are sharper than the first
draft's. It did not touch the two first cells.

## Predictions (frozen)

**Checks** (near-certain from the gates or the calibration; not scored):

| # | Check | Probability | Fails when |
| --- | --- | --- | --- |
| C1 | M2 holds on local, in flips and in work | 95% | otherwise |
| C2 | Local has no room under EARN-BUDGET's rule | 95% | room ≥ 0.5 on `local` w30 |
| C3 | The slow loop alone solves no run on the local and block cells | 95% | any solves |
| C4 | On `rand`, DrC and DrR coincide in every run | 97% | any run differs |
| C5 | Every reported state satisfies the original knots | 99.9% | any fails |

**Predictions** (scored):

| # | Prediction | Probability | Fails when |
| --- | --- | --- | --- |
| P1 | On block, M2 holds in flips but not in work | 65% | otherwise |
| P2 | M3 holds on local in flips | 7% | it holds |
| P3 | M3 holds on block in flips | 65% | otherwise |
| P4 | M3 holds in work on either family | 5% | it holds |
| P5 | Memory in flips on block: "no difference shown" (carry helps 30%, hurts 10%, other 10%) | 50% | another verdict |
| P6 | `local` w30 has room ≥ 0.5 under the per-flip budget, both seeds | 70% | otherwise |
| P7 | M4 holds in work on local | 40% | otherwise |
| P8 | DrC (both seeds) is a charged win against F on `local` w30: work ≤ 0.8 (upper end < 0.9) and CPU upper end < 1 | 80% | otherwise |
| P9 | M4 holds in flips on either family | 5% | it holds |
| P10 | Co-flip targets pay on some local or block cell, in work | 10% | they pay |

**Loop verdicts.**
- **Local:** reading 4 about 88%, reading 3 about 5%, others 7%.
- **Block:** reading 2 about 50% (P1 with P3), reading 4 about 30%, reading 6 about 10%, others 10%.

**Publication hold.** As before. Planted patterns, local search and propagation give no general method, and the thread tells the
coordinator before committing if anything on `rand` wins.

## Runs and stop rule

On the shared runner, 6 workers, MemoryMax 16G: 6 cells × 16 arms × 50 instances × 5 runs (4,800 cases), estimated 30 to 60 min
from the dry run's pace (256 cases in 3.3 min on 4 workers). The study stops at the decision rule. Nothing is added after the
results are seen. After this study the line stops for a stock-take with the owner, whatever the outcome.
