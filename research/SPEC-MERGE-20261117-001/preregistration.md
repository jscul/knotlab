# Do speculative merges chosen from a fast search's own co-flip evidence, undone when they do not help, cut the charged work where provable moves find nothing?: pre-registration

Epic `SPEC-MERGE-20261117-001` (sub-goal B191; the coordinator's go-ahead of 2026-11-17 for direction A gated by D; goals G15,
G16). **Frozen** before the gate, any tuning or any test instance ran. The commit time of this file is the only authority for the
freeze. Before it, only the gates (S1–S5) and a calibration ran (below, disclosed). Code by the thread (Claude) in
`experiments/SPEC-MERGE-20261117-001A/SPEC-MERGE-20261117-001A-E001_spec_merge/`. It is EARN-BUDGET's engine, copied, with a
per-distinction flip counter and a pair probe, and a new driver `spec_merge.py`. The canonical K1–K3 test is unchanged. The advisor
reviewed a draft and said "freeze with changes"; the changes are in ([advisor note](advisor_review.md)).

## The question

SLOW-LOOP and EARN-BUDGET changed the knot pattern only with moves a refutation proves, tie merges and shadow knots, which keep the
allowed states. Those moves pay where knots meet within short runs, and find nothing on random patterns. The owner's picture is of
mutations of the knot structure that improve results. This study tests mutations that are not proofs:
- **The evidence.** After each epoch of the fast loop (Novelty+), the slow loop counts, for every co-knotted pair of distinctions,
  how many epochs in a row both have flipped while their relative value x_p ⊕ x_q stayed the same. A high count marks a pair the
  search keeps moving together.
- **The move.** When the search is stuck (no new least violated count for some epochs), the slow loop merges the most stable pairs
  at their current relative value, without proof.
- **The undo.** If the search, on the coarser pattern, does not get below where it was stuck, the merges are undone.

**These merges do not keep the allowed states.** A wrong merge can remove every allowed state, and the undo is the only defence.
Every state the loop reports is mapped back and checked on the original knots. A state of the coarser pattern always maps to a
solution of the original (merging only fixes relative values), and the check is made anyway.

The study asks two questions:
- **D, the gate.** Does the co-flip evidence pick pairs that are tied provably (on `local` w10) or in the planted state (on random
  patterns) more often than random co-knotted pairs?
- **A.** Do speculative merges on that evidence cut the charged work, on random patterns (the primary, since provable moves found
  nothing there) and on a local pattern for contrast, against Novelty+, against the same schedule merging random pairs, and
  against SLOW-LOOP's proof-based loop?

## In standard terms, and the known neighbours

Speculative variable identification (equivalence guessing) during stochastic local search, with undo. The two nearest known
methods:
- **Multilevel refinement for SAT** (Walshaw 2002). It coarsens the formula by merging variables, chosen by a matching on the
  clause graph before any search, solves the coarsest level and refines with local search while uncoarsening.
- **Backbone-guided local search** (Zhang 2004). It estimates pseudo-backbones from the assignments of local minima and biases the
  search's variable and value choices.

Also related is decimation guided by survey propagation (Braunstein, Mézard and Zecchina 2005), which fixes variables by estimated
marginals and is near-perfect only close to the solution cluster.

**What differs here:**
- the merges fix **relative values of pairs**, not values of variables;
- they are chosen from the fast loop's own **co-flip history during** the search, not from the clause graph before it, and not
  from the values of local minima;
- they **change the structure the search runs on**, not its choice probabilities;
- they are **undone** when the search does not improve after them.

The knot framing adds that the move is the owner's "mutation": a change to which distinctions are one, kept only if it helps.

**What a win would and would not show.**
- **On random patterns,** a charged win would be a structure-changing slow loop that helps where every provable move found
  nothing. It would hold for planted patterns near the threshold at these sizes, and say nothing about hard SAT in general.
- **On local patterns,** a win mainly re-finds what proofs find, more cheaply or not; Gpr reads which.

## Prior work in the program

Objects index, searched 2026-11-17:

`python3 -B scripts/track.py objects "speculative merges of distinctions from a search's co-flip evidence with undo" --until 2026-11-18 --exclude SPEC-MERGE-20261117-001`
`python3 -B scripts/track.py objects "multilevel coarsening backbone-guided local search equivalence guessing" --until 2026-11-18 --exclude SPEC-MERGE-20261117-001`
`python3 -B scripts/track.py objects "planted not-all-equal random patterns near the threshold Novelty+" --until 2026-11-18 --exclude SPEC-MERGE-20261117-001`

Hits, each named:
- `SLOW-LOOP-20261117-001` and `EARN-BUDGET-20261117-001`: the same slow loop with proof-based moves. This study reuses their
  engine and charge, and its Gpr is EARN-BUDGET's per-cell oracle. Their finding, that attention counts are no better than
  random targets, is why the evidence here is co-flip stability instead.
- `WHERE-NEXT-20261116-001`: the same planted patterns and comparator (Novelty+); its CaDiCaL context row is not reused.
- `COMMON-FOLD-20261112-001`: a relative; ties forced by conditioning and propagation, measured on grown bases, with no search.
- `JOINT-RECORDS-20261116-001`, `SEARCH-AUDIT-20261112-001` and `SHIFT-LOCK-20261112-001`: unrelated objects, matched on
  "records", "search" and "ties".

## Calibration before the freeze (disclosed)

Seeds 9,500,000 and up, disjoint from every seed below; Novelty+ (0.7, 0.01); n = 3,200.
- **Gate D, one instance per family.** At 8 and 16 epochs, the 32 most stable pairs agreed with the planted relative values in
  0.88 and 0.94 of cases on `rand`, against 0.62 and 0.75 for random co-knotted pairs. On `local` w10, 0.72 to 0.78 of them were
  tied by a pair probe, against 0.22.
- **A first version** merged a round every two epochs regardless of progress, at 5% of n per round. On `rand` almost every round
  contradicted itself, the precision was 0.53, and nothing was solved within 3·10^6 flips.
- **A second version** acted only when stuck, but kept rounds that had been followed by any improvement. Wrong merges stayed in
  place (precision 0.65 to 0.73 on `rand`), and runs went unsolved.
- **The frozen acting rule** undoes a round unless the search gets below its pre-round best. At five instances per family:
  - the default setting A0 (epochs of 4n flips, stability ≥ 8, 2% of n per round, patience 2) cost 1.26 on `rand`, where it never
    merged, and 1.06 on `local`;
  - an eager setting (2n, ≥ 4, 10%, 1) cost 1.52 on `rand` (precision about 0.7) and 0.53 on `local` (precision 0.99), where the
    same schedule with random pairs cost 6.0 and left one run unsolved.

These shaped the grid and the stats charge (4 reads per pair per update, 2 per distinction). They enter no verdict.

## Cells, seeds and arms

Planted unsigned not-all-equal patterns, SLOW-LOOP's generators:

| Cell | Role | Instances | Flip cap |
| --- | --- | --- | --- |
| `rand` 2.1, n = 3,200 | **primary** | 50 | 2·10^7 |
| `rand` 3.0, n = 3,200 | another density | 50 | 2·10^7 |
| `rand` 2.1, n = 12,800 | four times the size | 20 | 10^8 |
| `local` w10 at density 4.0, n = 3,200 | contrast: structure provable | 50 | 10^8 |

Seeds: gate 8,700,000 and up (30 instances per gate cell); tuning 8,800,000 and up; test 8,900,000 and up. Five runs per instance,
the same five initial states for every arm.

| Arm | What it is |
| --- | --- |
| NOV | Novelty+ (0.7, 0.01), the coordinator's comparator |
| NOVt | Novelty+ at EARN-BUDGET's re-tuned settings for the family at 3,200: (0.7, 0.005) on `rand` 2.1, (0.6, 0.02) on `rand` 3.0, (0.8, 0.01) on `local` w10 |
| F | the better of NOV and NOVt, re-chosen per resample |
| A0 | speculative merges at the default setting (epochs 4n, stability ≥ 8, 2% of n′ per round, patience 2, warm-up 2): the minimal A |
| Arand0 | A0's schedule merging as many pairs drawn uniformly among the co-knotted pairs that both flipped in the last epoch, at their current relative values (activity-matched, so it merges where the search works, without the evidence) |
| AE, AErand | a fixed eager setting (epochs 2n, stability ≥ 4, 10% of n′ per round, patience 1) and its activity-matched random control, in every cell: merging is tested on `rand` whatever the tuning picks |
| A | speculative merges tuned on `rand` 2.1 at 3,200 over 25 settings: epochs {2n, 8n} × stability {4, 8} × round size {0.5%, 2%, 10%} × patience {1, 3}, and A0's setting |
| Arand | A's schedule with random pairs |
| Aloc, Arandloc | the same, tuned on `local` w10 at 3,200 |
| Gpr | the proof-based reference: EARN-BUDGET's eager batched slow loop, a slow budget 3 times the fast work, tie probes, rebuilds at 0.3% of the classes |
| Dr0, Dr1 | context only: MEET-TRANSFER's learned fast loop Dr (both seeds, unrefereed), alone, in its own engine, from the same initial states. It reads unsigned knots, so the slow loop cannot run on it; no verdict uses it |

**Which arms run (frozen).**
- NOV, NOVt, A0, Arand0, AE, AErand, Gpr, Dr0 and Dr1 run in every case.
- A and Arand run only if gate D passes on `rand`.
- Aloc and Arandloc run only if it passes on `local`.

So if D fails, the minimal A still runs, as the coordinator asked.

In every speculative arm the fast loop is Novelty+ (0.7, 0.01) and the slow loop acts only when the search is stuck. A round once
kept is never undone later, so a kept wrong merge can censor a run; the diagnostics count, for every round, whether all its merges
agreed with the planted state and whether it was kept. Tuning
score: the mean over 8 tuning instances × 3 runs of log(the setting's charged work) − log(NOV's from the same initial state), with
an unsolved run at log(work) + log(1 + least violated count); ties go to the first setting in grid order.

## Measures

- **Charged work** under EARN-BUDGET's corrected charge (v2) counts:
  - the fast loop, with one extra unit per flip for the flip counter;
  - the stability counts: 4 per pair and 2 per distinction per update;
  - the selection of a round, as a sort;
  - every rebuild, its sorting included.
- **Whole-run thread CPU** is reported beside it, and a charged win needs both.
- **Statistics.** As in EARN-BUDGET: per instance the geometric mean of five runs, per cell the median, R against F with a 99%
  paired bootstrap, and the censoring bounds.
- **Ratios:** A/Arand, A0/Arand0, AE/AErand and Aloc/Arandloc (the evidence), and A/Gpr, AE/Gpr and Aloc/Gpr (speculative
  against proved). R against NOV alone is also reported, since NOV is the speculative arms' fast loop.
- **Diagnostics:** merges, undos, active merges at the end, and the precision of the merges against the planted state. The
  precision is computed after the run; the loop never reads the planted state.

## Gate D (frozen)

The gate cells are `rand` 2.1 and `local` w10 at n = 3,200, 30 instances each. On each gate instance, Novelty+ (0.7, 0.01) runs
alone in epochs of n flips. An instance solved before a checkpoint is left out of that checkpoint, and the counts are reported.
After the last checkpoint the run continues to a solution, and every checkpoint's pairs are also read against the solution that
run found (reported; on `rand` 2.1, near the threshold, many solutions exist, so planted agreement can understate a merge's
harm or harmlessness). "At some checkpoint" is a maximum over three, at 99%. At epochs 4, 8 and 16, the k = 1% of n most stable
co-knotted pairs (stability ≥ 1) are compared with k uniformly drawn co-knotted pairs.
- **D on `rand`** passes if, at some checkpoint, the mean over instances of (their agreement with the planted relative values −
  the random pairs') is at least 0.10, with the 99% bootstrap lower end above 0.
- **D on `local`** passes if, at some checkpoint, the share tied by a pair probe is at least 1.5 times the random pairs' share,
  with the lower end of the difference above 0.

## Decision rule (frozen)

Applied in order; the first that holds is the verdict.
- **Arms and wins.** "A speculative arm" is any of A0, AE and A; "a win" is a charged win.
- **The evidence matters** when the winning arm over its activity-matched random control is ≤ 0.9, with the upper end below 1.

0. **Untested.** No speculative arm made a merge in the median run on `rand` 2.1 at 3,200. Merging was not tested there; the
   other cells are still read.
1. **Speculative merges pay on random patterns.** A speculative arm wins on `rand` 2.1 at 3,200, and the evidence matters there.
   **The publication hold applies at once.** The thread stops and messages the coordinator, with the SHA-256 of the raw test
   outputs, before committing any result.
2. **Restructuring pays on random patterns, but not because of the evidence.** A speculative arm wins on `rand` 2.1 at 3,200, and
   the evidence does not matter. The publication hold also applies.
3. **A win only elsewhere on random patterns.** A speculative arm wins on `rand` 3.0 or at 12,800, but not on `rand` 2.1 at 3,200.
   The publication hold applies, and the reading is partial.
4. **They pay only where structure is provable.** No win on any `rand` cell, but one on `local` w10 (A0, AE, A or Aloc). Gpr reads
   whether speculative merging beats proof there.
5. **No win anywhere.**

## Gates (run before the freeze)

| # | Gate | Fails when |
| --- | --- | --- |
| S1 | 240 small instances (n = 10–16) and 36 at n = 800, the three patterns, both selection rules, very eager settings: every reported state satisfies every original knot; at n = 800 at least 1,000 speculative merges are made (783,040 were, with 17,182 undos) | any fails |
| S2 | With merging off, the speculative driver reproduces Novelty+ alone run for run (60 runs) | any differs |
| S3 | The stability counts equal a direct recount on 50 random sequences | any differs |
| S4 | Every tie the pair probe reports holds in every allowed state (brute force), and a wrong-parity mutant is caught on all | any fails |
| S5 | The engine reproduces EARN-BUDGET's run for run for Novelty+ (24 runs) | any differs |

## Predictions (frozen)

| # | Prediction | Probability | Fails when |
| --- | --- | --- | --- |
| P1 | D passes on `rand` | 80% | otherwise |
| P2 | D passes on `local` | 90% | otherwise |
| P3 | No speculative arm has a charged win on `rand` 2.1 at 3,200 | 95% | one does |
| P4 | A (or A0 if A does not run) costs at most 10% on `rand` 2.1 at 3,200 (R_W ≤ 1.1) | 15% | above |
| P5 | Some speculative arm (A0, AE, A or Aloc) has a charged win on `local` w10 | 60% | none does |
| P6 | The evidence matters on `local` w10: the best speculative arm over its random-pair control ≤ 0.9 (upper end below 1) | 85% | otherwise |
| P7 | Speculative merging beats proof on `local` w10: (best speculative arm)/Gpr ≤ 1 | 10% | above |
| P8 | On `rand` 2.1 at 3,200, AE's merges are wrong often: its median precision is below 0.8 (no merges counts as a failure) | 45% | at least 0.8, or no merges |
| P9 | Every reported state satisfies the original knots | 99.9% | any fails |

**Publication hold.** If any speculative arm wins on any random cell (rules 1 to 3), the thread stops and tells the coordinator,
with a hash of the raw outputs, before committing any result.

## Runs and stop rule

On the shared runner, at most 4 workers while MEET-TRANSFER runs:
- the gate: 60 cases;
- the policy tuning: 2 × 8 × 25 cases at 3,200;
- the test: 4 cells × up to 13 arms × 50 (20) instances × 5 runs.

Estimates: gate and tuning about 15 min, the test about an hour. Nothing is added after the test results are seen.
