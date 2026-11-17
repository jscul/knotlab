# Memory that counts no steps carries the navigating agent to parity at larger sizes, not to a win

Epic `SCALE-MEMORY-20261116-001`, ticket `SCALE-MEMORY-20261116-001A` (`WHERE-NEXT-20261116-001#1`; goals G15, G16), 2026-11-17.
Evidence: **computed** (finite experiments on planted instances, every run kept), frozen before any new arm was trained
([pre-registration](preregistration.md), freeze commit `40cf4237c`, 2026-11-17 00:02 UTC; [advisor review](advisor_review.md)).
**Stress test pending**: the n = 51200 cell (registered `SCALE-MEMORY-P1`) is still running and will be folded in. **Refereed**
(SCALE-MEMORY-R1, confirmed with fixes, no Block; [report](referee-R1/report.md); the 51200 cell not refereed). The canonical K1–K3
test is unchanged.

**Corrected 2026-11-17 after the referee** (logged in `docs/CORRECTIONS.md`):
- *Narrowing.* L3m is **inconclusive**, not a clean loss: its seeds read 0.86 and 2.06, on opposite sides of 0.9, so the frozen
  seed-agreement clause fails.
- *Narrowing (wording).* At 12,800 the frozen comparator, Novelty+ (0.7, 0.05) from WHERE-NEXT, was 10 to 15% weaker than the best
  Novelty+ there, (0.7, 0.01) or (0.7, 0); an independent engine gives 1.10 times [1.04, 1.19]. So the frozen 0.82 for L3sm
  flatters it, and the five-run 0.92 to 0.94 is the better reading. At 3,200 the frozen comparator, (0.7, 0.01), was already the
  best.
- *Not a block.* The script that wrote `posthoc_summary.json` is now committed (`posthoc_analyze.py`). Its statistic is the median
  over instances of each instance's geometric mean over five runs; on pooled medians of all 500 runs the referee gets 0.85 to
  0.97.

## The answer

`WHERE-NEXT-20261116-001`'s agent attends to a violated not-all-equal knot, flips one of its distinctions and chooses the next
knot. With memory it beat every hand-written rule at its training sizes, by about 1.3 to 1.4 times fewer flips (the referee's
estimate), and lost at 4 and 16 times those sizes. Its memory read ages in steps, which saturate as the pattern grows.

**Does size-relative memory carry the win to 3,200 and 12,800 distinctions? It carries the agent to parity with the best
hand-written rule, Novelty+, not to a win.**

| Agent (memory reads, largest training size) | n = 3,200: frozen R | n = 3,200: five runs | n = 12,800: frozen R | n = 12,800: five runs |
| --- | --- | --- | --- | --- |
| L3, step-counted, 800 (WHERE-NEXT) | 1.36 [1.12, 1.63] | 1.03 (seed 1) | 14.5 [10.5, 22.2] (seeds 84 and 2.5) | 2.67 (seed 1) |
| L3s, scale-free, 800 | **0.94 [0.79, 1.11]** | **0.88 [0.81, 0.97]** | 0.86 [0.75, 0.97] | 1.01 [0.96, 1.07] |
| L3sm, scale-free, 3,200 | 0.94 [0.80, 1.10] | 0.95 [0.85, 1.02] | **0.82 [0.73, 0.91]** (comparator 10–15% weak here) | **0.94 [0.89, 1.00]** |
| L3m, step-counted, 3,200 | 0.95 [0.81, 1.16] | — | 1.33 [1.12, 1.56] (seeds 0.86 and 2.06) | — |
| L3c, step-counted, schedule control | 1.16 [0.97, 1.42] | — | 2.68 [2.19, 4.04] | — |

How to read the table:
- R is the agent's flips over the best re-tuned rule's, both seeds combined.
- The frozen columns use single runs per instance and 99% intervals; the bold entry is each arm's primary cell.
- The five-run columns are the post hoc check: five fresh runs per instance against the best of three Novelty+ settings,
  including walk probability 0, which the frozen grids lacked.

What the table shows:
- With step-counted memory the agent collapses at 12,800, and one of its two seeds is 84 times worse than Novelty+.
- With scale-free memory, both seeds of both arms stay between 0.76 and 0.99 of Novelty+'s flips in the frozen runs at 3,200 and
  12,800, and at 0.88 to 1.01 in the five-run check.
- The learned margin seen at the training sizes (R about 0.66 to 0.71 at n = 800 for every memory arm) is mostly gone by 4 to 16
  times those sizes.

**By the frozen rule:**
- *L3s and L3sm*: **inconclusive** on their primary cells. L3sm's 0.82 [0.73, 0.91] misses the flips-win line (at most 0.8, upper
  end below 0.9) narrowly.
- *L3m*: **inconclusive** (corrected: its seeds, 0.86 and 2.06, disagree around 0.9). *The control L3c*: **clean loss**.
- *The memoryless L2m*: **learner failure**. It failed the learner gate at 2.1 to 2.3 times Novelty+, as a memoryless policy was
  likely to.
- *Cost*: no arm saves CPU. At 12,800 the scale-free agent takes 0.60 s per instance against Novelty+'s 0.12 s, about 5.5 times
  the computing per flip.

**The diagnosis (frozen):**
- *The reads were an obstacle* (P2 held). S = L3s / L3 = 0.059 [0.038, 0.082] at 12,800. Against L3's better seed alone it is
  about 0.34.
- *For step-counted reads, training at 3,200 also helps* (P3 and P3c held). T = L3m / L3 = 0.092, and C = L3m / L3c = 0.50
  [0.34, 0.62], so the gain comes from the size and not from the longer schedule. But L3m's two seeds disagree (0.86 and 2.06).
- *Once the reads are scale-free, training at 3,200 adds nothing measurable*: L3sm / L3s = 0.95 [0.85, 1.07].
- *Memory still pays at 12,800*: K = L3m / L2m = 0.52.
- *The local pattern is still lost.* On the meeting pattern never trained on (`local`, 3,200) every arm loses, by 4.7 to 29
  times, and the memoryless arm loses least: memory still hurts there.

## How much the three limits weaken this reading

The coordinator and the thread agreed on three limits before the results were final.

1. **The scale-free arms kept the 50-step recent counts.** The WHERE-NEXT referee found these read about 0 from 3,200 on, so at
   large n they carry no information rather than wrong information. *Effect:* they cannot explain the parity. A fully scale-free
   memory could do better than measured, so this limit weakens the "no win at scale" reading somewhat, and the "parity, no
   collapse" reading not at all.
2. **No read is normalized by degree.** A distinction is in about 12 knots on `local` and 6.3 on `rand`, so the counts mean
   something else there. *Effect:* the `local` losses cannot yet be laid on the idea. This limit weakens the negative reading on
   `local` a great deal and leaves `rand` untouched.
3. **Single runs per instance.** *Effect:* the post hoc five-run check moved L3sm at 12,800 from 0.82 to 0.94 against the best
   Novelty+, and L3s from 0.86 to 1.01, the same direction as the WHERE-NEXT referee's correction. Parity is robust to it; any
   claim of a margin at scale is not supported.

## Results in full

Median flips per seed, on unseen instances, every arm from the same initial state per instance. The rules' runs at 800, 3,200,
`local` 3,200 and instances 0–49 of 12,800 are WHERE-NEXT's, reused after gate G6 confirmed that this engine reproduces WHERE-NEXT's
run for run.

| Cell | Novelty+ (re-tuned) | L3s s0 / s1 | L3sm s0 / s1 | L3m s0 / s1 | L3c s0 / s1 | L2m s0 / s1 | L3 s0 / s1 |
| --- | ---: | --- | --- | --- | --- | --- | --- |
| `rand` 800 | 15,073 | 9,736 / 10,286 | 10,591 / 10,884 | 10,176 / 10,768 | 10,802 / 10,364 | 31,670 / 33,430 | 10,792 / 9,060 |
| `rand` 3,200 | 72,276 | 68,078 / 67,499 | 64,752 / 71,428 | 59,447 / 78,633 | 84,985 / 82,463 | 214,834 / 191,738 | 124,848 / 77,116 |
| `rand` 12,800 | 416,258 | 371,878 / 346,795 | 315,248 / 366,252 | 358,866 / 858,724 | 1,912,108 / 648,216 | 1,043,468 / 1,079,176 | 35,007,896 / 1,045,659 |
| `local` 3,200 | 596,670 | 10.4 M / 28.1 M | 6.1 M / 10.3 M | 1.9 M / 25.3 M | 18.5 M / 9.3 M | 2.7 M / 2.9 M | 7.1 M / 32.9 M |

Gates: G passed (G0–G5 and G6, run-for-run identity with WHERE-NEXT's engine on 108 runs). G-learn passed for L3s (0.71, 0.88 of
Novelty+ at n = 800), L3m (0.75, 0.87 at 3,200), L3sm (0.76, 0.78) and L3c (1.08, 0.84), and failed for L2m (2.28, 2.12). G-train
passed for L3m and L3sm (both seeds) and failed for L2m seed 1. Every arm's numbers, intervals and ratios are in
[`summary_pilot.json`](../../artifacts/SCALE-MEMORY-20261116-001A/SCALE-MEMORY-20261116-001A-E001_scale_memory/summary_pilot.json),
the five-run check in [`posthoc_summary.json`](../../artifacts/SCALE-MEMORY-20261116-001A/SCALE-MEMORY-20261116-001A-E001_scale_memory/posthoc_summary.json).

## Predictions

| # | Prediction (probability) | Outcome |
| --- | --- | --- |
| P1 | Scale-free reads keep the training-size gain: L3s / L3 at 800 at most 1.1 (60%) | **Held**: 1.01 |
| P2 | S = L3s / L3 at 12,800 at most 0.7, upper end below 1 (40%) | **Held**: 0.059 [0.038, 0.082] |
| P3 | T = L3m / L3 at 12,800 at most 0.7, upper end below 1 (55%) | **Held**: 0.092 (L3m's seeds disagree) |
| P3c | C = L3m / L3c at 12,800 at most 0.8, upper end below 1 (50%) | **Held**: 0.50 [0.34, 0.62] |
| P4 | L3sm wins in flips at 12,800: R at most 0.8, upper end below 0.9 (30%) | **Failed narrowly**: 0.82 [0.73, 0.91]; five runs: 0.94 |
| P5 | L3sm at 51,200: R at most 1.0 (25%) | **Pending** (stress cell running) |
| P6 | K = L3m / L2m at 12,800 at most 0.8 (50%) | **Held**: 0.52, but L2m failed its learner gate |
| P7 | Every new arm still loses on `local` 3,200 (80%) | **Held**: R from 4.7 to 29 |
| P8 | No real win (90%) | **Held**: CPU per instance about 5 times Novelty+'s |

## What was supplied and what was learned

Supplied by hand: everything WHERE-NEXT supplied (the knot law, the instances, the step, the candidate set, the features, the
network, the trainer), plus the change of reads (ages relative to the knot's and the candidates' oldest, the violated fraction)
and the schedules. Learned: the weights. The scale-free reads are a hand-made change, guided by Novelty+'s rule and by the
referee's saturation table; learning then used them about as well as Novelty+ uses its own.

## For the owner's second stage (sub-goal B191)

A slow loop that changes knot structures would put the fast loop on meeting patterns it never trained on. This study says the
fast loop now holds its own across a sixteen-fold range of size on one meeting pattern, but still loses badly on another
(`local`), where memory hurts and the counts are not yet normalized by degree. So the fast loop is not yet a safe inner loop for a
structure-changing slow loop: the slow loop would be judged by an agent that cannot read structures unlike its training ones. The
step before B191 is a fast loop that carries over across meeting patterns. Its reads would count no steps and be normalized by
degree, and it would train on a mixture of meeting patterns and be tested on a held-out one. Failing that, B191 could use Novelty+
as its fast loop.

## Limitations

- Planted instances of two families only; the three limits above.
- Two seeds per arm, and the seed noise is large for step-counted memory (L3's seeds differ 33 times at 12,800). The arm-level
  intervals do not carry seed variance, which is why the decision also asked for seed agreement.
- The 51,200 cell is pending: its collapsed arms (L3 seed 0, L3c seed 0) run toward the 2·10^9 cap at about 15 minutes per run.
  The first instance read 0.80 to 0.87 of Novelty+ for L3sm and 0.86 to 1.77 for L3s; a single instance decides nothing.
- Deviations from the frozen text:
  - a first training launch was stopped after seconds to fix a pool hang, and relaunched; no result of it was read;
  - the post hoc five-run check is not part of the frozen protocol;
  - the L3c control's G-train is not part of its gates, and was not read.

## Where to start again

- Weights and logs: `artifacts/SCALE-MEMORY-20261116-001A/.../training/runs/`. Gates: `gates.json`. Policies: `policies.json`.
- Re-tuning at 51,200: `retune51200/`, merged in `retuned.json`.
- Tests: `test/`, with WHERE-NEXT's `test/` and `stress/` reused. Five-run check: `posthoc/`.
- Code: `nae_engine.c` (flag 16), `train_es.py`, `train_job.py`, `test_job.py` (phase `scale`), `posthoc_job.py` and
  `analyze_scale.py`, all in `experiments/SCALE-MEMORY-20261116-001A/SCALE-MEMORY-20261116-001A-E001_scale_memory/`.
- To rebuild the summary:
  `.venv/bin/python -B experiments/.../analyze_scale.py summary --where artifacts/WHERE-NEXT-20261116-001A/WHERE-NEXT-20261116-001A-E001_where_next --runs artifacts/.../test --out summary.json`.
