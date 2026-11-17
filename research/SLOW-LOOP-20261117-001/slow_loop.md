# A slow loop that changes the knot pattern pays on local patterns when it is eager, the eagerness does not carry over from patterns with nothing to find, and the search's attention does not help it choose

Epic `SLOW-LOOP-20261117-001`, ticket `SLOW-LOOP-20261117-001A` (sub-goal B191, the owner's second stage; goals G15, G16),
2026-11-17. Evidence: **computed** on finite experiments with planted instances, every run kept. Frozen before any policy was tuned,
comparator re-tuned or test instance run ([pre-registration](preregistration.md), freeze commit `8898f7117`;
[advisor review](advisor_review.md), "freeze with changes", all taken but one). **Referee pending.** The canonical K1–K3 test is
unchanged. The knot law (not-all-equal on three distinctions) and its signed form both pass it (gate G0).

## The question, and the answer

The owner's picture is a fast search on the knot structure and a slower loop that reshapes the structure, "a kind of
metacognition", with braids and untangles as ways of creating structure. The study reads it (assumption A90) as follows:
- **The loops.** Between epochs of a fast local search (re-tuned Novelty+), a slow loop changes the knot pattern at the knots the
  search attended to most.
- **The moves.** Each move keeps the allowed states, and each is found by a bounded refutation by propagation:
  - **tie merge**: two distinctions tied in every allowed state become one;
  - **shadow knot**: a signed three-place knot that every allowed state satisfies is added.

Every probe and rebuild is charged, in incidences read (A91) and in CPU.

**The answer has four parts.**

1. **Changing the pattern pays, a lot, where the pattern has local structure, but only when the slow loop is eager.**
   - **The eager policy.** GO, tuned on `local` window 10, spends as much on probes as on search. At n = 3,200 it cuts charged work
     to 0.15 [0.12, 0.19] of the best fast rule alone on `local` window 10, and to 0.23 [0.19, 0.30] on `local` window 40. GO never
     saw window 40. Both are charged wins, CPU included (0.33 and 0.61).
   - **One size up.** At n = 12,800 the cut on `local` window 10 is 0.12 [0.05, 0.16] (stress cell).
   - **Against static probing.** GO's work is 0.29 and 0.18 times that of tuned static probing, the preprocessing precedent.
   - **The cost elsewhere.** The same eager policy costs 1.5 to 2.1 times as much on the random and block patterns, where probes
     find nothing or little that helps.
2. **A policy tuned where nothing pays transfers as doing almost nothing.**
   - **G's setting.** G was tuned on `rand` and `block` at n = 800. The tuning picked the laziest setting of the grid: slow budget
     3% of the fast work, no shadow knots. The advisor predicted this, and the pre-registration declared how to read it.
   - **G's results.** G is at parity in every cell, from 0.84 [0.65, 1.07] on the primary cell to 1.09. It never loses more than
     about 4% where it finds nothing.
   - **The frozen verdict.** By the frozen decision rule this is reading 4, "no charged win for G anywhere". The cost of not
     having tuned on the pattern is T = G/GO = 5.6 [4.8, 6.3] on the primary cell.
3. **The search's attention is not a useful guide to where the pattern should change.**
   - **Per probed knot.** The knots the search attended to most yield ties no more often than random knots. On average they yield
     slightly less often (0.71 against 0.87 moves per target on the primary cell at G's budget). A one-epoch diagnostic gives the
     same picture: ties found at 51% of the most attended knots against 59% of random ones on `local` window 10, and 0.2% against
     1.0% on window 40.
   - **At the eager policy.** In a post hoc check (not frozen), random targets did as well as attention or better: GO/RNDO is 1.18
     [1.08, 1.24] on the primary cell and 0.97 to 1.13 elsewhere.
   - **Reading the counts costs.** At G's small budget, the counts' cost takes most of the slow budget.
   - **The frozen P6 and P12.** P6 ("G/RND ≤ 0.9 somewhere") held only by its letter. On the primary cell, G/RND = 0.78 [0.66,
     0.89] because RND found more ties and paid for more rebuilds that did not pay off, not because G chose better. The frozen
     attention measure (P12) failed.
4. **Shadow knots turned no cell into a win.** Switching them on changed G's work by −18% to +10% across cells; the only clear
   help was on `local` w10 at 800, where G/Gx = 1.22 [1.10, 1.45] but both stay at parity with the fast loop. A very large number
   of them (13,000 in a calibration run) kept Novelty+ from solving at all.

**Known mathematics, and what the knot framing adds.**
- **Known.** Both moves are known inference: failed-literal probing with equivalent-literal substitution (tie merges), and learned
  implied clauses (shadow knots). The eager slow loop is inprocessing for local search.
- **Expected.** That it pays on patterns of bounded bandwidth, and is waste on random ones, is what that literature would predict.
- **CDCL.** CaDiCaL solves every `local` instance at 3,200 in a median 0.06 s of CPU. That is below every local-search arm
  except GO on window 10 (0.037 s). At 800 the fastest local-search arms are below it. It needs a median of 88 s on `rand` 3,200,
  where Novelty+ takes 0.014 s.
- **What the framing adds.** The moves stated as changes to a knot pattern that keep its allowed states (tie classes; shadows
  that pass K1–K3), and one specific test of the owner's metacognition picture: the search's own attention as the signal for
  where to change the structure. That signal failed here. The scheduling that worked is plain eagerness, a budget proportional
  to the search's work, interleaved with it. That interleaving is what beat static probing.

## Results

Charged work W: the median over 50 unseen instances of each instance's geometric mean over five runs. R is W over the better of
re-tuned Novelty+ and probSAT, re-chosen in each of 10,000 paired bootstrap resamples (99% intervals). Novelty+ was the better rule
in every cell. RNDO is post hoc (not frozen). Every reported state checked on the original knots. Every run solved its instance
except four on one `embed` 800 instance, which stopped at the cap with one knot violated: NOV, G and Gx from the same initial
state, and GO. No arm has more than 5% of its runs censored, so no figure is a bound.

| Cell | F (W) | G | Gx | RND | ST | GO | RNDO (post hoc) | G verdict | GO verdict |
| --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- |
| **`local` w10, 3,200** (primary) | 2.17·10^7 | 0.84 [0.65, 1.07] | 0.83 [0.64, 1.07] | 1.07 [0.80, 1.33] | 0.52 [0.39, 0.65] | **0.15 [0.12, 0.19]** | 0.13 [0.10, 0.16] | parity | charged win |
| `local` w40, 3,200 | 3.46·10^7 | 0.91 [0.77, 1.25] | 0.91 [0.74, 1.34] | 0.81 [0.60, 1.17] | 1.27 [0.92, 1.81] | **0.23 [0.19, 0.30]** | 0.23 [0.18, 0.30] | parity | charged win |
| `embed`, 3,200 | 6.74·10^6 | 0.98 [0.78, 1.18] | 0.91 [0.72, 1.16] | 1.13 [0.95, 1.38] | 0.90 [0.74, 1.09] | 0.67 [0.54, 0.82] | 0.60 [0.49, 0.72] | parity | work win |
| `rand`, 3,200 | 2.10·10^6 | 1.04 [1.04, 1.04] | 1.04 [1.04, 1.04] | 1.03 [1.03, 1.03] | 1.04 [1.03, 1.04] | 1.64 [1.57, 1.68] | 1.64 [1.57, 1.70] | parity | loss |
| `block`, 3,200 | 3.23·10^6 | 1.03 [0.94, 1.16] | 1.11 [1.02, 1.21] | 1.76 [1.43, 1.93] | 1.60 [1.42, 1.80] | 1.88 [1.63, 2.13] | 1.94 [1.68, 2.17] | parity | loss |
| `local` w10, 800 | 1.47·10^6 | 1.09 [0.95, 1.42] | 0.89 [0.73, 1.16] | 1.52 [1.24, 2.04] | 1.90 [1.65, 2.51] | 0.38 [0.34, 0.50] | 0.38 [0.33, 0.50] | parity | work win |
| `local` w40, 800 | 4.65·10^5 | 1.02 [0.95, 1.03] | 1.12 [0.93, 1.40] | 1.01 [0.85, 1.21] | 3.96 [2.99, 5.06] | 2.05 [1.54, 2.57] | 2.00 [1.58, 2.57] | parity | loss |
| `embed`, 800 | 3.87·10^5 | 1.09 [0.90, 1.39] | 1.05 [0.85, 1.21] | 1.52 [1.13, 1.83] | 3.21 [2.47, 3.75] | 1.51 [1.14, 1.77] | 1.51 [1.09, 1.75] | parity | loss |
| `rand`, 800 | 3.21·10^5 | 1.04 [1.04, 1.04] | 1.05 [1.04, 1.06] | 1.03 [1.03, 1.03] | 1.06 [1.04, 1.09] | 1.78 [1.68, 1.84] | 1.84 [1.72, 1.93] | parity | loss |
| `block`, 800 | 4.82·10^5 | 0.99 [0.89, 1.17] | 1.08 [0.93, 1.31] | 1.29 [1.00, 1.61] | 2.28 [1.78, 2.87] | 2.14 [1.60, 2.73] | 2.17 [1.71, 2.61] | parity | loss |

**CPU** (R_CPU, the whole run in thread CPU, Python included):
- **GO:** 0.33 [0.26, 0.43] and 0.61 [0.48, 0.81] on the two local cells at 3,200, 1.33 on `embed` 3,200, and 1.63 on `local` w10
  800, where its work win is not a CPU win.
- **ST:** 0.64 on the primary cell.
- **G:** 1.1 to 3.5 everywhere.
- **Where the CPU goes.** For GO on the primary cell the median split is 0.005 s fast loop, 0.005 s probes and 0.025 s rebuild.
  The rebuild is written partly in Python, so the CPU figures overstate the slow loop's cost.

**What the eager loop does to the pattern.** On the primary cell GO's runs merged a median of 741 ties into 624 classes, from 3,200
distinctions, and solved with 0.04 times the flips. On `local` w40 they ended at 181 classes. Tuned static probing (one pass,
aborting after 5% of knots without a find) found 8,996 ties on the primary cell and left 253 classes. On window 40 it found 84 and
left 3,168.

**Between arms** (W, 99%):

| Cell | G/ST | G/RND | G/Gx | T = G/GO | GO/ST | GO/RNDO (post hoc) |
| --- | --- | --- | --- | --- | --- | --- |
| `local` w10, 3,200 | 1.61 [1.35, 1.81] | 0.78 [0.66, 0.89] | 1.00 [0.86, 1.15] | 5.59 [4.84, 6.31] | 0.29 [0.27, 0.31] | 1.18 [1.08, 1.24] |
| `local` w40, 3,200 | 0.72 [0.56, 1.02] | 1.13 [0.87, 1.54] | 1.00 [0.73, 1.27] | 3.89 [3.29, 4.96] | 0.18 [0.15, 0.23] | 1.04 [0.93, 1.14] |
| `embed`, 3,200 | 1.09 [0.92, 1.26] | 0.87 [0.72, 1.00] | 1.08 [0.81, 1.29] | 1.46 [1.21, 1.78] | 0.75 [0.65, 0.81] | 1.13 [0.99, 1.23] |
| `rand`, 3,200 | 1.00 [1.00, 1.01] | 1.01 [1.01, 1.01] | 1.00 [1.00, 1.00] | 0.64 [0.62, 0.66] | 1.58 [1.52, 1.62] | 1.00 [0.98, 1.01] |
| `block`, 3,200 | 0.64 [0.59, 0.72] | 0.59 [0.55, 0.73] | 0.93 [0.85, 1.03] | 0.55 [0.50, 0.64] | 1.17 [1.01, 1.27] | 0.97 [0.86, 1.09] |

**The attention signal, per probed knot** (median over instances of moves found per target probed, five runs pooled):

| Cell | G (attention, lazy) | RND (random, lazy) | GO (attention, eager) | RNDO (random, eager; post hoc) |
| --- | ---: | ---: | ---: | ---: |
| `local` w10, 3,200 | 0.71 | 0.87 | 0.86 | 0.91 |
| `local` w40, 3,200 | 0.004 | 0.008 | 0.014 | 0.011 |
| `block`, 3,200 | 0.09 | 0.14 | 0.10 | 0.09 |
| `embed`, 3,200 | 0.27 | 0.24 | 0.05 | 0.04 |

The frozen measure divides moves found by probe incidences rather than by targets. On it G found 0.06 to 0.43 times RND's in every
cell with finds (P12 failed). Most of that gap is the cost of reading the attention counts. G's slow work per target is 2 to 80
times RND's, because each epoch it reads the knots visited and sorts them, and at a budget of 3% little is left for probes. Per
target, the two are close.
The one-epoch diagnostic (`attention_diag.json`, post hoc) probes the 3% most attended knots and as many random ones on the
unchanged pattern. It found ties at:

| Cell | Most attended knots | Random knots |
| --- | ---: | ---: |
| `local` w10, 3,200 | 51% | 59% |
| `local` w40, 3,200 | 0.2% | 1.0% |
| `block`, 3,200 | 10% | 12% |
| `embed`, 3,200 | 22% | 21% |

The knots' members meet about as many knots in both groups (13.1 against 13.2 on `local` w10). The attended knots are more often
still violated at the end of the epoch: 8–10% against 3–5% in three cells, and equally often (8%) on window 40. Being attended to
does not make a knot's distinctions more likely to be tied.

**What predicts whether the eager loop pays** (post hoc reading of the frozen GO runs, not frozen). How often its probes find
something does not predict it, but how fast the pattern shrinks nearly does:

| Cell | GO verdict | Moves per target | Share of distinctions merged | Classes merged per 10^6 slow incidences |
| --- | --- | ---: | ---: | ---: |
| `local` w10, 3,200 | charged win | 0.86 | 81% | 1,099 |
| `local` w40, 3,200 | charged win | 0.013 | 94% | 519 |
| `embed`, 3,200 | work win | 0.05 | 23% | 295 |
| `local` w10, 800 | work win | 0.79 | 74% | 1,473 |
| `block`, 3,200 | loss | 0.10 | 19% | 157 |
| `block`, 800 | loss | 0.10 | 15% | 169 |
| `embed`, 800 | loss | 0.04 | 19% | 456 |
| `local` w40, 800 | loss | 0.005 | 0.4% | 8 |
| `rand`, 800 and 3,200 | loss | 0 | 0% | 0 |

On window 40 a tie is rare, but each one cascades through the dense knots around it. On `block` ties are common but stay inside
their blocks. The one exception to the shrink rate is `embed` at 800, where the search alone is already cheap.

**CDCL (CaDiCaL 1.9.5, one run per instance).** The 60 s interrupt did not stop pysat's CaDiCaL, so every run went to its answer
and every instance was solved. "Within 60 s" is read from the wall time.
- **`local`, both windows and sizes:** all within 0.12 s; median CPU 0.06 s at 3,200 (about 4,000 propagations).
- **`rand` 3,200:** 3 of 20 within 60 s; median 88 s, at most 237 s (about 1.8·10^8 propagations), against Novelty+'s 0.014 s.
- **`block` 3,200:** 18 of 20; median 38 s.
- **`embed` 3,200:** 39 of 50; median 46 s, at most 391 s.
- **At 800:** `rand` median 5.1 s, `block` 0.05 s, `embed` 2.7 s.

**Stress cell, one size up** (n = 12,800, 20 instances, five runs, the 3,200 settings):
- `local` w10: G 0.75 [0.32, 1.06], ST 0.36 [0.15, 0.51] and GO 0.12 [0.05, 0.16], the last two charged wins (CPU 0.46 and 0.28).
- `rand`: G 1.04, ST 1.02, GO 1.49 [1.41, 1.55].

The eager loop's gain on `local` w10 grows with size (0.38, 0.15, 0.12 at 800, 3,200, 12,800), and its overhead on `rand` shrinks
(1.78, 1.64, 1.49).

## Predictions

| # | Prediction (probability) | Outcome |
| --- | --- | --- |
| G | Gates G0–G7 | **Passed** (`gates/check_output.txt`): 16,481 moves checked by brute force, the wrong-parity mutant caught on 118 of 118, run-for-run identity with SCALE-MEMORY's engine |
| P1 | G charged win on the primary cell (80%) | **Failed**: 0.84 [0.65, 1.07], parity |
| P2 | G costs at most 15% on `rand` 3,200 (85%) | **Held**: 1.04 [1.04, 1.04] |
| P3 | No win for G on `block` 3,200 (90%) | **Held**: 1.03 |
| P4 | G work win or better on `local` w40 3,200 (25%) | **Failed**: 0.91 [0.77, 1.25] |
| P5 | ST at least as good as G on the primary cell, G/ST ≥ 0.9 (75%) | **Held**: 1.61 |
| P6 | G/RND ≤ 0.9 with upper end below 1 in some 3,200 cell (15%) | **Held by its letter**: 0.78 [0.66, 0.89] on the primary cell. The cause is RND's extra rebuilds, not better targets (above) |
| P7 | T = G/GO on the primary cell within [0.8, 1.25] (35%) | **Failed**: 5.59 |
| P8 | Shadow knots change G by less than 10% in every cell (25%) | **Failed**: G/Gx 1.22 on `local` w10 800 |
| P9 | CDCL solves all 50 primary-cell instances within 60 s, at a median CPU below G's (90%) | **Held**: 50 of 50, 0.057 s against 0.27 s |
| P10 | CDCL solves fewer than half of `rand` 3,200 within 60 s (90%) | **Held**: 3 of 20 (by wall time; see above) |
| P11 | Soundness in every run (99%) | **Held**: 0 contradictions and 0 failed checks in 17,500 test runs, 1,000 stress runs and 2,500 post hoc runs |
| P12 | On `embed` 3,200 G finds at least as many moves per unit of probe work as RND (25%) | **Failed**: 116 against 585 per 10^6 incidences |
| P13 | G work win or better on `embed` 3,200 (25%) | **Failed**: 0.98 |

Seven of thirteen held. The failures on G (P1, P4, P7, P13) all come from one fact: tuning on patterns with nothing to find made G
lazy. The advisor named that risk before the freeze.

**Decision (frozen rule).** Reading 4, **no charged win for G anywhere**: these moves, scheduled by a policy tuned on the random
and block patterns, do not pay at charged cost. This is a verdict on this reading of the owner's idea (A90) and this tuning, not on
the idea. The oracle-tuned eager loop does pay on both local patterns, but the frozen rule asks the transferred policy to carry it,
and it does not.

## What the study supplied and what was learned

**Supplied by hand:**
- the knot law, the planted instances and the five meeting patterns;
- the fast loop (Novelty+, re-tuned per cell);
- the two moves and their refutation by propagation, with its budget;
- the target rule (most attended first) and the rebuild;
- the policy grid and the tuning patterns.

**Learned (tuned):** four parameters of the slow loop (epoch length, slow budget, shadow-knot share, backoff), and one of static
probing's eight settings.

**What was learned about the owner's picture:**
- Changing the structure can cut the fast loop's charged work several-fold, and the cut grows with size on local patterns.
- What decides whether it pays is how much structure the pattern has, and the slow loop was told nothing about that: a fixed
  budget tuned on structure-poor patterns stays lazy everywhere.
- The fast loop's attention, the natural "metacognitive" signal, carries no information about where moves can be found. It only
  marks where the search is currently stuck.

## Deviations from the frozen text

All were made before any slow arm was scored, except where noted:
- **The re-tuning grids were extended** one step beyond an edge where the best setting sat on it (S1b). Novelty+ got noise 0.85
  and 0.9 and walk probability 0.1 in the five 3,200 cells and `local` w10 800; probSAT got cb 0.6 and 0.8 in the two `local`
  3,200 cells. Only the primary cell's Novelty+ setting changed, from (0.8, 0.05) to (0.75, 0.1), a 1.7% better score. This can
  only strengthen the comparator.
- **The analysis script.** Two of its frozen measures were missing from the committed script because one edit had not applied: R
  against Novelty+ alone, the censoring bounds and the CPU split. They were restored before the results were read, as the
  pre-registration specifies them. No run had a censored figure, so no bound applies.
- **CDCL.** The 60 s interrupt did not stop CaDiCaL, so CDCL ran to its answer on every instance. P9 and P10 are read from wall
  times.
- **Post hoc, not frozen** (decided after the policy tuning gave G the laziest setting, and before the test was complete):
  - RNDO, GO's policy with random targets, on every cell;
  - static probing tuned on `local` w10 at 800 (STO). It came out the same setting as ST, so it was not rerun;
  - the one-epoch attention diagnostic.

  None of these enters a frozen verdict.

## Limitations

- **The instances.** Planted instances only, five meeting patterns, one density each.
- **The fast loop.** It was not re-tuned on the changed pattern; the slow arms keep the cell's Novelty+ setting. This can only
  understate them.
- **The rebuild.** It is partly in Python, which inflates the slow arms' CPU (for GO on the primary cell, 70% of its CPU is
  rebuild). Charged work does not depend on this.
- **G's laziness.** It is partly the cost of reading the attention counts (a scan and sort of the knots visited each epoch). A
  cheaper read, kept up incrementally by the fast loop, would leave more of a small budget for probes. At the eager budget the
  read is cheap relative to the probes, and attention still did not help.
- **Not compared:** a clause-weighting search (PAWS or SAPS), the closest precedent that also follows where a search stays
  violated; re-tuning of the policy per cell; moves that keep only satisfiability.
- **The learned agent** was not used as the fast loop, because its engine reads unsigned knots only.
- **CPU times** are thread CPU on a shared machine with a load average of 25 to 35 on 24 cores. Work does not depend on the machine.

## Where to start again

- **Code** (in `experiments/SLOW-LOOP-20261117-001A/SLOW-LOOP-20261117-001A-E001_slow_loop/`):
  - `slow_engine.c`: the signed-knot fast loop, the probes and the tie cascade;
  - `slow_loop.py`: the driver, the rebuild and the generators;
  - `job.py`: every stage;
  - `choose.py`, `analyze.py`, `posthoc_analyze.py` and `attention_diag.py`.
- **Gates:** `.venv/bin/python -B experiments/.../check.py`.
- **Runs** (in `artifacts/SLOW-LOOP-20261117-001A/SLOW-LOOP-20261117-001A-E001_slow_loop/`):
  - `retune/`, `retune2/`, `policy/`, `test/`, `stress/`, `posthoc_tune/` and `posthoc/`, each with `results.jsonl`;
  - the choices `retuned.json`, `policies.json` and `posthoc_policies.json`;
  - the summaries `summary.json`, `posthoc_summary.json` and `attention_diag.json`.
- **Job versions.** Each run records the SHA-256 of the `job.py` that made it, and they differ only by added stages:
  - S1 ran the frozen version (`a46b5c49…`, commit `8898f7117`);
  - S1b to S4 ran `712741b8…` (commit `ad355d474`);
  - the post hoc tuning ran `766be51f…`, whose post hoc stage still listed STO;
  - the post hoc check ran the committed version (`137ccd40…`).
- **To rebuild the summary:**
  `.venv/bin/python -B experiments/.../analyze.py artifacts/.../test artifacts/.../summary.json --stress artifacts/.../stress`.
