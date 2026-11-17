<!-- The first draft of the pre-registration, written before the calibration and dry run and never frozen; kept for audit. The frozen text is preregistration.md. -->

# Does the owner's whole picture work as a mechanism: a learned agent with memory acting on knots while a proof-based slow loop reshapes the pattern?: pre-registration

Epic `AGENT-LOOP-20261117-001` (`SPEC-MERGE-20261117-001#1`, the coordinator's go-ahead of 2026-11-17; sub-goal B191; goals G15,
G16). **Frozen** before any test instance ran. The commit time of this file is the only authority for the freeze. Before it, only
the gates (A1–A4) and one smoke run on a calibration instance (seed 9,600,000) ran.
- **Code** by the thread (Claude), in `experiments/AGENT-LOOP-20261117-001A/AGENT-LOOP-20261117-001A-E001_agent_loop/`:
  - SPEC-MERGE's engine and driver, copied;
  - SIGNED-NAV's signed-knot agent engine and handle, copied unchanged into `agent/` (from commit `0c631cb87`);
  - a new driver, `agent_loop.py`.
- **The canonical K1–K3 test** is unchanged.
- **The advisor** reviewed a draft ([advisor note](advisor_review.md)).

## The question

This is the first test of the owner's whole picture in one system. The pieces:
- **The fast loop** is the learned navigating agent, which attends to a violated knot, flips one of its distinctions and remembers
  its steps. It is Dr of `MEET-TRANSFER-20261117-001` (unrefereed), both seeds.
- **The slow loop** reshapes the knot pattern under the agent. It is EARN-BUDGET's eager batched proof-based loop:
  - after each epoch it spends 3 times the epoch's fast work on tie probes;
  - it rebuilds when the proven ties reach 0.3% of the classes.
- **Memory across a change.** At each rebuild the agent's memory is carried across the change by SIGNED-NAV's carry rule, or
  restarted.

**The primary question is the mechanism, in flips and in charged work, each read separately:**
1. **M1.** Does carried memory beat restarting?
2. **M2.** Does the agent with the slow loop beat the agent alone?
3. **M3.** Does it beat Novelty+ under the same slow loop?

**Stated up front:** the agent costs 4 to 14 times Novelty+'s CPU per flip (SPEC-MERGE's context arm), so a win in charged time
over Novelty+ under the same loop is unlikely. CPU is reported, and no verdict rests on it except the context line P4.

The secondary question takes SPEC-MERGE's one positive signal, the co-flip evidence, as the target for proofs: probe the pairs the
search keeps moving together instead of random knots, with Novelty+ as the fast loop.

## In standard terms

A learned local-search policy with history features (a recurrent state, ages and visit counts), interleaved with inprocessing
(failed-literal probing and equivalent-literal substitution). The policy's internal state is mapped through each variable
substitution. Memory transfer under problem reformulation is not, as far as this program found, measured in the SAT literature.

**What each outcome would show.**
- **If M2 holds,** the slow loop's structure changes help a learned agent as they help Novelty+.
- **If M1 holds,** an agent's memory survives a change of structure usefully. That is the owner's metacognition picture in its
  most specific form.
- **If M3 holds in flips,** the agent uses the reshaped pattern better than Novelty+ does.
- **None of them** would say anything about satisfiability in general. CaDiCaL solves these local patterns in about 0.05 s.

## Prior work in the program

Objects index, searched 2026-11-17:

`python3 -B scripts/track.py objects "learned agent with memory as the fast loop under a structure-changing slow loop" --until 2026-11-18 --exclude AGENT-LOOP-20261117-001`
`python3 -B scripts/track.py objects "memory carried across a change of the knot pattern" --until 2026-11-18 --exclude AGENT-LOOP-20261117-001`

The study builds on `SLOW-LOOP-20261117-001`, `EARN-BUDGET-20261117-001` and `SPEC-MERGE-20261117-001` (the slow loop),
`MEET-TRANSFER-20261117-001` (the agent Dr) and `SIGNED-NAV-20261117-001` (the signed engine and the carry rule).

## Cells and arms

Planted unsigned not-all-equal patterns at n = 3,200, 50 fresh instances per cell (seeds 9,100,000 and up), five runs each. Every
arm runs from the same five initial states per instance; both engines draw the initial state from the run seed the same way (gate
A1).

| Cell | Role | Flip cap |
| --- | --- | --- |
| `local` window 30, density 4.0 | **primary**: never run in the program before the freeze | 2·10^8 |
| `local` w10, density 4.0 | where the slow loop pays most | 2·10^8 |
| `local` w20, density 4.0 | between | 2·10^8 |
| `rand` 2.1 | control: the slow loop proves nothing, so carried and restarted memory must coincide | 2·10^7 |

| Arm | What it is |
| --- | --- |
| NOV, NOV8 | Novelty+ (0.7, 0.01) and (0.8, 0.01) alone; F is the better of the two, re-chosen per resample |
| GN | Novelty+ (0.7, 0.01) under the slow loop, random probe targets (the comparator for M3) |
| GNco | the same with co-flip probe targets (secondary) |
| Dr0, Dr1 | Dr alone, each seed |
| DrC0, DrC1 | Dr under the slow loop, memory carried |
| DrR0, DrR1 | Dr under the slow loop, memory restarted from the mapped values with a fresh random stream |

## Measures

- **Flips, charged work (v2) and CPU,** each a separate statistic: per instance the geometric mean of five runs, per cell the
  median.
- **The agent's charged work** is its engine's incidence count, reads included.
- **The slow loop's charge** counts the probes, the stability counts (for co-flip), the rebuilds with their sorting, the carry's
  mapping and the new handles.
- **R** is against F, and ratios between arms are paired, with 99% bootstrap intervals over instances.

## The mechanism tests (frozen)

Each test is per seed of Dr, and a claim needs **both seeds** (seed agreement):

| Test | Ratio | Holds when |
| --- | --- | --- |
| M1, carry helps | DrC/DrR | ≤ 0.9 with the upper end below 1 |
| M1, carry hurts | DrC/DrR | the lower end above 1 |
| M2 | DrC/Dr | ≤ 0.8 with the upper end below 0.9 |
| M3 | DrC/GN | ≤ 0.9 with the upper end below 1 |

Each test is read in flips and in charged work separately.

## Decision rule (frozen)

Applied in order. "Holds" means on the primary and on at least one other local cell.

1. **The whole picture works as a mechanism:** M2 and M3 hold, in flips and in charged work.
2. **The agent beats Novelty+ under the loop in flips only:** M2 holds in both measures, M3 in flips but not in work.
3. **The loop helps the agent, but the agent adds nothing:** M2 holds in both measures, M3 does not.
4. **No mechanism gain:** M2 fails.

Beside the rule: memory matters if M1 (carry helps) holds in flips, both seeds, on some local cell; and the co-flip targets pay if
GNco/GN ≤ 0.9 with the upper end below 1.

## Gates (run before the freeze)

| # | Gate | Fails when |
| --- | --- | --- |
| A1 | With no slow budget, the agent driver reproduces Dr alone run for run (flips and work), and the Novelty+ driver reproduces Novelty+ alone (24 runs) | any differs |
| A2 | 80 runs at n = 800 (`local` w10 and w20, `block`, `rand`; agent carry, agent restart, Novelty+ with random and co-flip targets, agent with co-flip targets): each solves, its state satisfies every original knot, and every proved tie holds in the planted state | any fails |
| A3 | On `rand`, where nothing is proved, carried and restarted memory give identical runs (6 instances) | any differs |
| A4 | The first epoch under the slow loop equals Dr alone capped there | any differs |

All passed (`gates/check_output.txt`): 31,046 merged distinctions checked against the planted state.

## Calibration (disclosed)

One `local` w10 instance at n = 800, one run, Dr seed 0:
- **Dr alone** took 11,125 flips and 2.7·10^6 charged incidences;
- **Dr under the slow loop:** 813 flips with carried memory and 825 with restarted, at about 0.96·10^6;
- **Novelty+:** 31,230 flips alone and 1,544 under the loop (0.69·10^6).

## Predictions (frozen)

| # | Prediction | Probability | Fails when |
| --- | --- | --- | --- |
| P1 | M2 holds on the primary, both seeds, in flips and in work | 80% | otherwise |
| P2a | M3 holds on the primary in flips | 35% | otherwise |
| P2b | M3 holds on the primary in charged work | 10% | otherwise |
| P3 | M1, carry helps in flips on some local cell, both seeds | 25% | nowhere |
| P4 | DrC (either seed) is a charged win against F on the primary: work ≤ 0.8 (upper end < 0.9) and CPU upper end < 1 | 55% | otherwise |
| P5 | DrC's CPU is at most GN's on the primary | 10% | above |
| P6 | Co-flip targets pay: GNco/GN ≤ 0.9 (upper end < 1) on some local cell, in work | 40% | nowhere |
| P7 | On `rand`, DrC and DrR coincide in every run | 90% | any run differs |
| P8 | Every reported state satisfies the original knots | 99.9% | any fails |

**Publication hold.** As before. Planted patterns, local search and propagation give no general method, and the thread tells the
coordinator before committing if anything on `rand` wins.

## Runs and stop rule

On the shared runner, 4 workers: 4 cells × 10 arms × 50 instances × 5 runs, estimated 40 to 90 min. The study stops at the decision
rule. Nothing is added after the results are seen. After this study the line stops for a stock-take with the owner, whatever the
outcome.
