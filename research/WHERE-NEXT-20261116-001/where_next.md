# A learned agent that chooses where to act, with memory: it wins where it trained and loses beyond

Epic `WHERE-NEXT-20261116-001`, ticket `WHERE-NEXT-20261116-001A` (`FOLD-TRANSFER-20261114-001#2`; goals G15, G16), 2026-11-16.
Evidence: **computed** (finite experiments on planted instances, every run kept), frozen before the learned arms were trained
([pre-registration](preregistration.md), freeze commit `a341054e5`; [advisor review](advisor_review.md)). **Referee pending.**
The canonical K1–K3 test is unchanged; the knot law used here, not-all-equal on three distinctions, passes it (gate G0).

## The question, and the answer

The owner's idea (2026-11-16) is an agent that reads the context at one logical knot, turns from knot to knot and acts on their
loops, remembers the steps it has taken, and treats choosing a knot as activating it. This study tested that idea on planted
knot patterns of the not-all-equal law. At each step the agent attends to one violated knot and flips one of its three
distinctions. It then chooses which violated knot to attend to next, either one its flip just violated or one drawn from the
rest. In its full version (L3) it remembers when it last visited each knot, when it last flipped each distinction and how
often, and it carries a small recurrent state. It was trained by evolution strategies on patterns of 200 to 800 distinctions.
It was then tested against six tuned hand-written rules on unseen patterns of up to 12,800 distinctions, and on a second
meeting pattern it never saw. The hand-written rules were tuned on the training instances and re-tuned at every test size.

**The answer has three parts.**

1. **At the sizes it trained on, the agent beats every hand-written rule.** It takes 0.45 times the flips of the best re-tuned
   rule at n = 200 and 0.60 times at n = 800. The best rule is always Novelty+.
2. **The gain is memory.** The same agent without memory needs 2.7 to 3.3 times as many flips (M = 0.36, 0.31 and 0.37 at
   n = 200, 800 and 3200). Learning where to go next, without memory, adds little: L2 against L1 is 0.75 to 0.95 on `rand`.
3. **What it learned does not carry over.**
   - At 4 times its largest training size (n = 3200, the primary cell) it ties Novelty+: R = 1.07 [0.90, 1.21]. That is a clean
     loss by the frozen rule, at the margin.
   - At 16 times (n = 12800) it takes 2.4 times Novelty+'s flips, and its memory no longer helps (M = 0.96).
   - On the local meeting pattern it never trained on, it is 2.6 to 55 times worse than Novelty+. There its memory hurts
     (M = 2.8 at n = 800 and 4.7 at n = 3200).
   - In CPU per instance it never wins: it costs 4 to 8 times more per flip, so the break-even count N* is infinite in every cell.

The decision is a **clean loss** on the primary cell and on both secondary cells. Memory **helps** on the primary cell. G-learn
passed: L1's validation median at n = 800 was 0.85 times probSAT's on the same instances.

## Results

Median flips to a satisfying state over unseen instances (100 per cell; 50 at n = 12800), all arms on the same instances from
the same initial states. R is L3 against the best re-tuned hand-written rule, with the paired bootstrap interval in brackets
(95% on the primary cell, 98.3% on the others). Every arm solved every instance within the cap, except where the solved
column says otherwise.

| Cell | L3 (agent, memory) | L2 (no memory) | L1 (what only) | L2w (where only) | Best rule (re-tuned) | R (L3 / best) | M (L3 / L2) | L3 solved |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- | ---: |
| `rand` n = 200 | 782 | 2,190 | 2,938 | 4,042 | Novelty+ 1,738 | 0.45 [0.33, 0.62] | 0.36 [0.23, 0.51] | 100% |
| `rand` n = 800 | 9,060 | 29,692 | 35,092 | 37,879 | Novelty+ 15,073 | 0.60 [0.44, 0.84] | 0.31 [0.24, 0.43] | 100% |
| **`rand` n = 3200** | 77,116 | 208,525 | 220,382 | 291,924 | Novelty+ 72,276 | **1.07 [0.90, 1.21]** | 0.37 [0.31, 0.44] | 100% |
| `rand` n = 12800 | 975,317 | 1,015,842 | 1,147,644 | 1,881,064 | Novelty+ 401,581 | 2.43 [1.73, 4.29] | 0.96 [0.71, 1.73] | 100% |
| `local` n = 200 | 4,217 | 5,116 | 4,266 | 3,512 | Novelty+ 1,592 | 2.65 [0.94, 5.56] | 0.82 [0.30, 1.92] | 100% |
| `local` n = 800 | 741,703 | 261,258 | 230,798 | 174,930 | Novelty+ 39,578 | 18.7 [11.5, 35.2] | 2.84 [1.57, 5.86] | 99% |
| `local` n = 3200 | 32,878,164 | 7,003,615 | 6,855,156 | 3,962,552 | Novelty+ 596,670 | 55.1 [31.2, 95.2] | 4.69 [2.42, 8.43] | 91% |

At `rand` n = 3200 the other re-tuned rules took 227,058 (sticky), 240,107 (greedy-where), 243,494 (probSAT), 294,174 (WalkSAT)
and 418,468 (focused Metropolis, training-tuned) flips. So the memoryless learned arms reached probSAT's level, and only the
memory arm reached Novelty+'s, the one hand-written rule that also remembers. Every cell's full table, with training-tuned and
re-tuned parameters, CPU, incidences per flip and the where diagnostics, is in
[`summary.json`](../../artifacts/WHERE-NEXT-20261116-001A/WHERE-NEXT-20261116-001A-E001_where_next/summary.json).

**Where.** The where-choice was really tested: the agents saw 2.8 to 4.2 distinct candidate knots per step (the frozen reading
rule needed more than 2).
- The memoryless learned agents learned to avoid the knots their own last flip had just violated. They took one in 3 to 8% of
  the steps where one was available. The hand-written sticky rule takes one in 60 to 80%, and was tuned to.
- The memory agent took one in 33 to 37%.
- Learning where with probSAT's what held fixed (L2w) left `rand` flips unchanged against probSAT itself (291,924 against
  277,236 at n = 3200). It cut `local` flips by 37% (3.96 million against 6.25 million), still 6.6 times Novelty+'s.
- So the learned where helped a little only on the meeting pattern it never trained on.

**Cost.**
- *Per flip.* L3 costs about 1.4 to 2.2 µs of CPU, against 0.15 to 0.26 µs for probSAT and 0.19 to 0.39 µs for Novelty+
  (7.7 times probSAT at `rand` n = 3200). It reads about 120 to 220 incidences per flip against probSAT's 29 to 52, because it scores its
  where-candidates.
- *Training.* Both seeds of L3 took 10,953 CPU seconds; all eight trainings took about 46,000.
- *Marginal cost.* Even at n = 800, where L3 takes 0.60 times Novelty+'s flips, its median CPU per instance is 4.7 times
  Novelty+'s (0.016 s against 0.0034 s). It has no per-instance saving to set against its training in any cell.

**Plain exact search.** CaDiCaL on the CNF encoding solved all 60 instances it was given. Its median time was 0.018 s at
n = 200, 0.99 s at n = 400 and 5.6 s at n = 600 (most 34 s), where every local rule takes milliseconds. Local search beats
exact search here by about three orders of magnitude, which is well known for satisfiable random instances. It says nothing for
or against learning.

**Scaling.** Fitted slopes of log median flips against log n over `rand` n = 800 to 12800: Novelty+ 1.18, sticky 1.17 to 1.25,
probSAT 1.25 to 1.37, L1 1.26, L2 1.27, L3 1.69. The agent's flips grow faster with size than every rule's, so the publication
hold does not apply.

## Predictions

| # | Prediction (probability) | Outcome |
| --- | --- | --- |
| G | Engine gate | **Passed** (all six checks, `check.py`) |
| G-learn | L1 within 1.15 times probSAT at n = 800 (80%) | **Passed**: 0.85 (29,664 against 34,907 at the median) |
| P2 | R in [0.7, 1.1] at n = 200 (70%) | **Failed, the other way**: R = 0.45, a larger win than predicted |
| P3 | No flips win on `rand` at 3200 and 12800 (70%) | **Held**: 1.07 and 2.43 |
| P4 | A flips win on `local` at 3200 (30%) | **Failed**: R = 55 |
| P5 | Memory helps on some headline cell (45%) | **Held**: M = 0.37 at `rand` n = 3200 |
| P6 | L3 at least 5 times probSAT's CPU per flip at `rand` n = 3200 (90%) | **Held**: 7.7 times |
| P8 | CaDiCaL at least 10 s and 100 times the best local rule at n = 600 (75%) | **Failed** on the first part (5.6 s); the second holds (over 1,000 times) |
| P9 | R at 12800 at most 1.2 times R at 200 (55%) | **Failed**: 2.43 against 0.45 |
| P10 | No marginal-cost win on the primary cell (90%) | **Held**: CPU per instance 0.130 s against 0.016 s; N* infinite |

## What the study supplied and what was learned

Supplied by hand:
- the knot law, the planted instances and the two meeting patterns;
- the step (attend to a violated knot, flip one of its distinctions);
- the candidate set (up to three knots just violated plus three drawn from the rest);
- every feature the agent reads, the memory features included (ages clipped at 1,000 steps, ranks, counts decayed over 50 steps,
  the recurrent input);
- the network's form, the training method, its curriculum and its budget.

Learned: the 326 weights, that is, how to weigh those reads when choosing a knot and a distinction.

The memory the agent used is the kind Novelty+ uses: each distinction's age within the knot being acted on, and recent flip
counts. Learning found a better use of it than the 1997–99 hand-written rule at the sizes it saw. Learning found no use of the
where-choice that a tuned hand-written rule lacks, except a modest gain on `local`.

## Why the memory did not carry over (not tested)

The working hypothesis is that the memory features are counted in steps. Ages are clipped at 1,000 steps and counts decay over
50 steps. As n grows, the walk takes more steps to come back to a region, so the same reading means something else: most ages
read "long ago", and recent counts read near zero. Novelty+'s rule reads only which of the knot's three distinctions was flipped
most recently, a comparison with no scale. Its re-tuned noise stayed between 0.6 and 0.7 at every size, and its advantage over
re-tuned probSAT grew with size (1.7, 2.4 and 3.4 times fewer flips at n = 200, 800 and 3200). On `local`, where each distinction is in about 12 knots rather than 6.3, the same step counts again mean
something else. Two tests would separate the hypothesis from "learned memory does not transfer":
- retrain L3 with scale-free memory only (ranks, and ages divided by n);
- train on mixed sizes.
Neither was run.

## Limitations

- Planted instances only, of two families, one density each; `local` doubles the density as well as changing the meeting pattern.
- One architecture (326 weights), one training method and budget, two seeds per arm. A larger model or another trainer could
  differ.
- CPU times are thread CPU on a shared machine that was heavily loaded during training (load average up to 55 on 24 cores); flips
  and incidences do not depend on the machine.
- Deviations from the frozen text, all made before any learned arm was scored:
  - the tuning grids were widened where an optimum sat at an edge, which can only strengthen the hand-written side;
  - the n = 12800 re-tuning took its two rules (Novelty+, sticky) from the n = 3200 re-tuning scores rather than the pilot's
    test results;
  - one training (L1, seed 0) hung after it had finished, because a worker of its inner pool ignored the shared runner's stop
    signal, and the thread killed that worker; its weights and accounting were written afterwards and are complete;
  - the stress cell was launched without the runner's foreground smoke test, on job code already smoke-tested in the pilot.

## Where to start again

- Weights, logs and accounting: `artifacts/.../training/runs/<arm>_s<seed>/`. Selection: `policies.json`.
- Tuning: `tuning/tuning.json`. Re-tuning: `retuned_all.json`.
- Every test run: `test/results.jsonl` and `stress/results.jsonl`. CaDiCaL: `cadical/`.
- Code: `nae_engine.c` (one engine for every arm), `engine.py`, `train_es.py`, `test_job.py` and `analyze.py` in
  `experiments/WHERE-NEXT-20261116-001A/WHERE-NEXT-20261116-001A-E001_where_next/`.
- To rerun the gate: `.venv/bin/python -B experiments/.../check.py`.
- To rebuild the summary:
  `.venv/bin/python -B experiments/.../analyze.py test --runs artifacts/.../test artifacts/.../stress --policies artifacts/.../policies.json --cadical artifacts/.../cadical --out summary.json`.
