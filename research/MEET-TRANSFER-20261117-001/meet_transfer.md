# Memory read per knot carries the navigating agent to meeting patterns it never saw

Epic `MEET-TRANSFER-20261117-001`, ticket `MEET-TRANSFER-20261117-001A` (`SCALE-MEMORY-20261116-001#1`; goals G15, G16; the
prerequisite for sub-goal B191), 2026-11-17. Evidence: **computed** (finite experiments on planted instances, five runs per instance,
every run kept), frozen before any arm was trained or any comparator tuned ([pre-registration](preregistration.md), freeze commit
`19c8b1ed1`, 2026-11-17 04:48 UTC; [advisor review](advisor_review.md)). **Referee pending.** The canonical K1–K3 test is unchanged.

## The answer

The navigating agent attends to a violated not-all-equal knot, flips one of its distinctions and chooses the next knot, with
memory of its earlier steps. In SCALE-MEMORY it held parity with Novelty+ across sizes on `rand`, but lost 4.7 to 29 times on
`local`, a pattern whose knots overlap only within a short run of distinctions. In this study its reads are changed so that
**nothing it reads counts steps or knots**:
- break and make are read as fractions of the distinction's own knots;
- ages are read relative to the knot's oldest distinction;
- the 50-step counts are dropped.

The new agent was trained on a mixture of meeting patterns and tested against a carefully tuned comparator: the best of three
Novelty+ settings, probSAT and WalkSAT, each tuned in two stages, with five runs per instance.

**It now carries over to meeting patterns it never trained on, and in flips it beats the best rule on most of them:**

| Cell | Role | D (4 seeds) | Dr (`rand` only, 2 seeds) | Dl (oracle, trained on `local`) | L3sm (SCALE-MEMORY) |
| --- | --- | --- | --- | --- | --- |
| `local` window 10, n = 3,200 | **primary**, held out | **0.83 [0.63, 1.09]** | 0.77 [0.57, 1.07] | 0.48 | 24.7 |
| `local` window 10, n = 800 | held out | **0.66 [0.60, 0.81]** | 0.70 | 0.46 | 8.6 |
| `local` window 40, n = 800 | untouched | 0.75 [0.62, 1.04] (seeds 0.31 to 2.99) | 0.44 [0.36, 0.62] | 0.37 | 3.4 |
| `local` window 160, n = 800 | untouched | 0.95 [0.89, 1.00] | 1.21 | 0.92 | 1.02 |
| `heavy`, n = 800 | untouched | 0.81 [0.76, 0.88] | 1.00 | 0.78 | 1.09 |
| `heavy`, n = 3,200 | untouched | **0.72 [0.67, 0.77]** | 0.91 | 0.68 | 1.13 |
| `block`, n = 3,200 | training pattern, 4× size | **0.61 [0.54, 0.67]** | 0.67 | 0.61 | 0.71 |
| `rand` 4.0, n = 3,200 | training pattern, 4× size | 0.89 [0.86, 0.95] | 1.15 | 0.88 | 1.02 |
| `rand` 2.1, n = 3,200 | training pattern, 4× size | 1.60 [1.40, 1.87] (seeds 0.83 to 3.86) | 1.07 | 1.30 | 0.84 |

How to read the table:
- Each entry is R, the arm's flips over the best tuned rule's (99% intervals).
- Bold marks a flips win by the frozen tiers: R ≤ 0.8, upper end below 0.9, every seed ≤ 0.8. The primary cell, at 0.83 [0.63, 1.09],
  is inconclusive by those tiers.
- The best rule was Novelty+ in every cell, at a noise of 0.3 to 0.8 depending on the pattern.

What the table shows:
- The agent went from 25 times worse than the best rule on the held-out `local` pattern to 0.83 times its flips at n = 3,200 and
  0.66 at 800.
- On a degree spread no training pattern has (`heavy`) it takes 0.72 to 0.81 times the flips.
- On the untouched wider windows it is at 0.75 and 0.95, though one of its four seeds fails on window 40.
- **It loses on the plainest pattern, `rand` 2.1 at 3,200 (1.60).** Training on the mixture traded some `rand` 2.1 performance for
  the rest. The learner gate passed there only narrowly (1.147 against 1.15), and one seed is 3.9 times worse.

**What carries it is the reads, not the mixture of training patterns.**
- *The reads.* Dr has the same reads but was trained on `rand` 2.1 alone, and on `local` it does as well as D: 0.77 against 0.83,
  X = D / Dr = 1.09 [0.82, 1.32]. Against the old reads, Dr / L3sm = Z = 0.031 at `local` 3,200.
- *The mixture.* Mixed training helps on the patterns near the training mixture (X = 0.78 to 0.91 on `rand` 4.0, `block`, `heavy` and
  window 160). It hurts on `rand` 2.1 (1.50) and window 40 (1.71).
- *Memory* now helps everywhere instead of hurting on `local`. The memoryless Dn needs 12 times as many flips there (K = D / Dn =
  0.081). Dn failed its learner gate, as memoryless policies did before.
- *The oracle.* Dl, trained on `local` as well, does about 1.75 times better than D there (O = 1.75 [1.52, 2.07]). Transfer
  recovers most of the gap but not all of it.

**It still costs more computing.** Per instance, the agent takes 1.5 to 9 times Novelty+'s CPU (3.1 times at the primary cell),
because it scores its where-candidates and runs two small networks per step. So every flips win here is a mechanism win, not a real
win. No cell has a CPU win (P7).

**The inner-loop bar for B191** (R at most 2 with the upper end below 2.5, a solved fraction no lower than the best rule's, a
95th-percentile ratio at most 3, every seed's R at most 2):
- *D* meets it on the primary cell and on three of the four untouched cells (window 160, `heavy` at both sizes). It fails on window
  40, where one seed of four reads 2.99.
- *By the frozen rule that is "usable on the primary only"*: the learned fast loop is not yet licensed for B191, because of seed
  variance.
- *Dr*, the `rand`-trained arm with the same reads, meets the bar on the primary and on every untouched cell (0.44 to 1.21). That is
  read after the fact, since the frozen rule names D.

## Predictions

| # | Prediction (probability) | Outcome |
| --- | --- | --- |
| G | Engine gate, including run-for-run identity with SCALE-MEMORY's engine | **Passed** |
| G-learn | Each arm within 1.15 times the better reference rule on every training pattern | **D passed** (1.147 on `rand` 2.1, borderline), **Dl, Dr passed**, **Dn failed** (learner failure) |
| P1 | D usable as an inner loop on `local` 3,200 (30%) | **Held**: R 0.83, 95th-percentile ratio 0.35 |
| P1o | Dl usable there (50%) | **Held**: 0.48 |
| P2 | X = D / Dr at most 0.5 at `local` 3,200 (50%) | **Failed**: 1.09; the reads, not the mixture, do the work |
| P3 | Y = D / L3sm at most 0.5 (55%) | **Held**: 0.034 |
| P5 | D at most 1.1 on all three training patterns at 3,200 (45%) | **Failed**: `rand` 2.1 at 1.60 |
| P6 | K = D / Dn at most 0.9 at `local` 3,200 (35%) | **Held**: 0.081 |
| P7 | No CPU win anywhere (92%) | **Held**: 1.5 to 9 times the CPU |
| P8 | Z = Dr / L3sm at most 0.7 at `local` 3,200 (40%) | **Held**: 0.031 |
| P9 | D usable on both untouched windows (35%) | **Failed**: one seed at 2.99 on window 40 |
| P10 | D within 1.5 times on `heavy` at 800 and 3,200 (50%) | **Held**: 0.81 and 0.72 |

## What was supplied and what was learned

Supplied by hand:
- the knot law, the families and the step;
- the candidate set;
- the reads, including their normalizations, which are the change that made the difference;
- the network, the trainer and the training mixture.

Learned: the weights. The finding is therefore partly about representation. When the agent reads its local context as fractions
of each distinction's own knots, and its history as relative ages, what it learns on random patterns carries to banded,
clustered and heavy-tailed ones.

## Limits

- *Planted instances only*, of six families at two sizes.
- *The recurrent state decays at a fixed rate per step*, so it still counts steps implicitly.
- *Seed variance is large for D* (window 40, `rand` 2.1). Four seeds expose it, and a design that selects seeds by validation on
  more patterns might remove it.
- *CPU times are thread CPU on a shared machine.* Flips and incidences are machine-independent.
- *Deviation before any learned arm was tested:* the comparator screen was extended at its grid edges (only strengthening the rules).
  The SCALE-MEMORY 51,200 cell was paused from 06:12 to 09:20 UTC to free cores; it belongs to that study.

## Where to start again

- *Weights and logs:* `artifacts/MEET-TRANSFER-20261117-001A/.../training/runs/`. Gates: `gates.json` (per seed and arm level).
  Policies: `policies.json`.
- *Comparator tuning:* `screen/`, `screen_edge/`, `screen.json`, `confirm/`, `retuned.json`, `confirm_detail.json`.
- *Test:* `test/` (12,350 cases, five runs each). Summary: `summary.json`.
- *Code:* `nae_engine.c` (flag 32), `engine.py` (the `block` and `heavy` families), `train_mixed.py`, `train_job.py`, `test_job.py`,
  `analyze_meet.py` and `check.py`.
