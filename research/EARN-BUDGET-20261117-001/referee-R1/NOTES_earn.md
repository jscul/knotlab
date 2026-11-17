# EARN-BUDGET-20261117-001, referee R1 follow-up: charge v2 and the comparator at the grid edge

2026-11-17. Fresh code in this folder (`referee_earn_*`).
- **The study's code**, called only as the thing under test and never edited: `slow_loop.planted`, `run_slow` (policy E
  from `policies.json`, the cell's Novelty+ from `retuned.json`), `_sortcost`, `sig_keys` and the C entry points. Wrapped
  from outside for timing.
- **Build and run discipline.** The study's library was built into my scratchpad, and every run used `-B`, so nothing was
  written into the study's folder; its `__pycache__` was already there. Each run was under 4 minutes, with at most 8
  processes.
- **Seeds.** As in `job.py`: test seeds are 8,100,000 + i and tuning seeds 8,500,000 + i. The hand-off said 7.1M; those
  are SLOW-LOOP's seeds.

| Task | Verdict |
| --- | --- |
| 1 Does charge v2 count all the rebuild's work? | **Yes**, to within a few percent; R moves by at most 6% |
| 2 Would a widened grid make Novelty+ materially better on the primary? | **No** |

## 1. Charge v2: Matches

`referee_earn_task1_charging.py`, `.json`. The reruns took 5 s.
- **Runs.** E on the first 10 test instances of `local35-w15-3200` (the primary) and of `local-w20-3200`, runs 0 and 1:
  20 runs per cell.
- **Reproduction.** All 40 reruns equal the stored test runs in flips, work, every work part, rebuilds, ties, final
  classes and knots, doublings and epochs.

**What v2 adds** (rerun means per run, primary / w20):

| | primary | w20 |
| --- | ---: | ---: |
| `work_rebuild` | 4.11·10^6 | 2.00·10^6 |
| of which SLOW-LOOP's charge (sl_reduce + n0 + 3m) | 1.22·10^6 | 0.64·10^6 |
| of which v2's additions | 2.89·10^6 (70%) | 1.36·10^6 (68%) |
| sort operations performed (n log2 n; unique, isin, union1d, and the `idx.sort()` after unique) | 2.45·10^6 | 1.18·10^6 |
| v2's sort charges (k ceil(log2(k+1))) | 2.67·10^6 | 1.26·10^6 |

**What is left uncharged:**
- **Net sort operations.** 0.8% / 1.6% of `work_rebuild`, and 0.2% / 0.2% of the total.
- **The one sort v2 does not charge** is `idx.sort()` after `np.unique` in `reduce_pattern`: 15% of `work_rebuild`, and 3.3% /
  1.6% of the total. The dedup sort is charged on all m0 + shadows knots rather than the kept ones, which more than covers
  it.
- **Python glue,** measured as the rebuild's Python-side CPU in fast-loop equivalents minus v2's additions: 25% / 27% of
  `work_rebuild`, and 5.6% / 2.8% of the total. This includes interpreter overhead.
- **Other linear passes** (fancy indexing, the keep mask, `sig_keys`) are of the same order as v2's linear terms.

**CPU per charged incidence** (ns):

| | Stored, 250 runs per cell, pooled (median of runs) | Reruns, C parts |
| --- | --- | --- |
| fast | 5.4 (5.2) / 5.0 (5.0) | 5.7 / 5.0 (fl_run) |
| slow | 5.7 (5.6) / 5.5 (5.4) | 8.0 / 9.4 (includes the ctypes call cost of 90 to 113 calls) |
| rebuild | 5.8 (5.6) / 5.4 (5.7) | C part over the v1 charge: 5.9 / 5.5; Python part over v2's additions: 7.7 / 7.0 |

Under v1 the rebuild cost 17 to 64 ns per charged incidence. Under v2 it costs what the fast loop does.

**R against Novelty+** (the better rule in both cells). Stored runs, 50 instances × 5, my own paired bootstrap, 99%:

| E, cell | R_W | + uncharged `idx.sort` | + rebuild CPU over its charge | + all uncharged CPU (driver loop too) | R_CPU |
| --- | --- | ---: | --- | --- | ---: |
| `local35-w15-3200` | 0.557 [0.51, 0.68] | 0.576 | 0.563 [0.51, 0.69] | 0.589 [0.54, 0.73] | 0.610 |
| `local-w20-3200` | 0.747 [0.60, 0.87] | 0.759 | 0.747 [0.60, 0.88] | 0.781 [0.64, 0.93] | 0.760 |

R_W reproduces the note's 0.56 [0.51, 0.68] and 0.75 [0.61, 0.87]. Under every correction both cells stay charged wins.

## 2. The comparator at the grid edge: no material gain

`referee_earn_task2_grid_edge.py` and `referee_earn_task2b_runnersup.py`, with their `.json`. Tuning took 199 s on 8
cores and the tests 18 s. The engine is the WHERE-NEXT referee's own Novelty+, copied as `referee_earn_sls_work.c` with
one change: a counter of charged work in the studies' incidence units.

**Where the edge is.** The study's own grid already has noise 0.85 and 0.9, and walk probabilities up to 0.1. Those
settings score far worse (20.9 and up, against 16.82 for (0.8, 0)). (0.8, 0.0) is flagged only because wp = 0 is the
grid's lower end, and wp cannot go below 0. So the only room left is finer noise steps.

**Tuning** (the 15 settings asked for, plus noise 0.775 and 0.825; 20 tuning instances × 2 runs, cap 2·10^7; `choose.py`'s
score, mean log work):

| Setting | Score | Unsolved of 40 |
| --- | ---: | ---: |
| **(0.8, 0)** | **16.747** | 0 |
| (0.75, 0.005) | 16.759 | 0 |
| (0.775, 0.005) | 16.798 | 0 |
| (0.775, 0.01) | 16.842 | 0 |
| (0.75, 0.01) | 16.874 | 0 |
| (0.775, 0) | 16.881 | 0 |
| (0.75, 0) | 16.968 | 0 |
| (0.8, 0.005), (0.8, 0.01) | 17.07, 17.09 | 0 |
| noise 0.7 | 17.22 to 17.43 | 0 |
| noise 0.825 | 17.44 to 17.80 | 0 |
| noise 0.85 | 20.97 to 21.66 | 19 to 23 |
| noise 0.9 | 26.1 | 40 |

My engine picks the study's (0.8, 0). The next settings are within 0.012 to 0.13 in mean log work (about 1 to 14%), and all
of them are worse.

**Test** (20 test instances × 3 runs, cap 2·10^8). The median work of (0.8, 0) is 2.36·10^7. Each runner-up's paired ratio
against (0.8, 0), with 99% intervals:

| Setting | Ratio |
| --- | --- |
| (0.75, 0.005) | 1.00 [0.58, 1.70] |
| (0.775, 0.005) | 1.08 [0.62, 1.71] |
| (0.775, 0) | 1.01 [0.64, 1.67] |

- **Calibration.** My (0.8, 0) against the study's stored NOV arm on the same 20 instances: 0.85 [0.55, 1.36].
- **Checks.** No unsolved test run and no failed state check.
- **Resolution.** The test intervals are too wide to resolve 10% alone. The 40-run tuning score is the sharper evidence,
  and it shows nothing better.

**Effect on E's R.** None is expected, since no better setting exists in reach. Suppose a better comparator setting did
cut Novelty+'s work by 10%. E's fast loop is 70% of its work, so on the primary R_E = 0.557 would become:
- **0.576**, if E's fast loop gained equally;
- **0.619**, if it gained nothing.

Either way the upper end stays near 0.70 to 0.75, still a charged win.
