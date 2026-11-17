# SLOW-LOOP-20261117-001, referee R1: soundness, identity, charging and the comparator

2026-11-17. Fresh code in this folder (`referee_*`). The referee's oracle (`referee_oracle.py`) enumerates all 2^n states
itself and is written from the definitions only. The study's code was called only as the thing under test:
`slow_loop.planted` / `planted_embed` (generators), `initial_state`, `_handle`, `run_slow`, `run_fast`, `reduce_pattern`,
and the C entry points `fl_run`, `sl_probe`, `fl_get` (through the study's ctypes wrapper, built into the scratchpad,
never into the study's folders). Every Python run used `-B`, a memory cap (`ulimit -v`) and at most 8 processes.

| Task | Verdict |
| --- | --- |
| 1 Soundness | **Matches**: no violation in any check |
| 2 Identity until the first move | **Matches** |
| 3 Charging (A91) | **Differs** (in size): `work` leaves out the rebuild's sorting, about 0.5 to 1 times the charged total for GO |
| 4 Comparator | **Matches** within noise |

## 1. Soundness by brute force: Matches

**1a/1b, probes and rebuild** (`referee_task1_soundness.py`, `.json`; 90 s on 8 cores).
- **Instances.** 8,000 planted instances with n from 10 to 20, 1,600 per kind:
  - `rand` at densities 1.5, 2.1, 3 and 4;
  - `block` with blocks of 3 to 5 at densities 2.0, 2.5 and 3.5;
  - `local` windows 2 to 4 ("w10 scaled") and 5 to 8 ("w40 scaled") at densities 2.5 and 4;
  - `embed` with local share 0.25 or 0.5, coupling 0.1 or 0.2, window 2 or 3.
  
  82 tiny `embed` instances were skipped (generator, see below).
- **Rounds.** Up to 10 rounds per instance. In each round, sl_probe runs in modes 0 (guided, after a 5 to 200-flip epoch), 1
  (random) and 2 (static) on fresh handles of the current reduced, signed pattern. The draws:
  - slow budget unlimited or 2,000;
  - probe budget pb of 10^7 (half the draws), 4,000, 50 or 5;
  - beta 0, 0.5 or 1, and J 1 to 8;
  - abort 0 or 2.

  Then the round's finds go through `reduce_pattern`.
- **Checked on the original allowed set A:**
  - every tie written: **945,168**;
  - every shadow knot written: **716,604**;
  - after every rebuild (**19,741**), each distinction's (root, parity), and that the reduced pattern lifted by
    x_v = y_root(v) ^ parity(v) is A one for one (same set, same size);
  - every original and shadow knot through the classes. **714,810** were dropped, each one always holding ("binding" or
    "contra" images: 0). **1,795,947** were kept, and the referee's canonical images equal the reduced knots exactly, with
    no duplicates.
- **Outcome.** 0 violations; 0 contradictions from sl_probe or sl_reduce. Probing reached the true tie classes (the
  pairs of constant parity on A) on 7,904 of 7,918 instances.
- **Negative controls** (`referee_task1_control_*.json`; the same code with one change):
  - every tie applied with the wrong parity: caught on 355 of the 385 instances with finds;
  - one sign of every shadow flipped: caught on 362 of 385.

  The rest had finds of the other kind only.

**1c, the full run_slow** (`referee_task1c_runslow.py`, `.json`; 192 s).
- **Instances and policies.** 1,479 instances of the same kinds (21 skipped). The policies: GO as frozen, RNDO, GO with
  beta 0.5, ST, and an extreme one (epoch 0.2n, rho 20, beta 1, J 4, pb 10^5).
- **Fast loops.**
  - **The cell's Novelty+ (0.75, 0.1).** At n ≤ 20 it solves within the first 100-flip epoch, so GO moved in only 7 of
    2,958 such runs.
  - **Weak ones, to make the slow loop move:** Novelty+ (0, 0), a random walk (probSAT cb 0), and an anti-greedy probSAT
    (cb −2).
- **Outcome.** 59,160 runs, 21,292 with at least one rebuild, 307,764 moves.
  - Every one of the 58,984 solved states satisfies every original knot.
  - 0 contradictions.
  - In all 59,160, the final classes, the 132,567 shadow knots and the lifted final pattern equal A one for one.
  - The 176 unsolved runs are Novelty+ (0, 0) cycling to the cap.

**1d, at the study's size** (extension; `referee_task1d_atsize.py`, `.json`; 5 s). Oracle: CaDiCaL 1.9.5 via pysat, a
third party, not the study's code.
- **Runs.** 90 full runs: GO, GO with shadows and the extreme policy, on 10 test instances each of `local` w10 800,
  `local` w40 800 and `block` 800, with 2,349 rebuilds.
- **Checked exactly:**
  - all 29,544 final ties (both violating states refuted, 59,088 UNSAT calls);
  - all 21,872 shadow knots.
- **Sampled lifts.** 1,197 original states project to allowed states of the reduced pattern, and 1,704 reduced states
  lift to allowed states.
- **Outcome.** 0 violations; every reported state checks. `embed` 800 was tried and stopped after about 10 minutes: the
  solver is slow under assumptions on its uniform part.

**1e, the stored runs' own flags** (`referee_task1e_stored_flags.py`, `.json`). Matches the note:
- 0 contradictions and 0 solved-but-unverified in 17,500 test, 1,000 stress and 2,500 post hoc runs;
- 4 unsolved runs, all on `embed` 800 seed 7,100,044 (NOV, G, Gx, GO);
- every CDCL model checks.

**Side finding (not soundness).** `planted_embed`'s draw has no retry guard, unlike `planted`'s 10,000 tries. When a
sub-pattern's hidden values are all equal it never returns, and its memory grows: one worker reached 14 GB before I
stopped it. This happens only at tiny sizes (a 5-distinction local part); at n ≥ 800 the chance is about 2^−199.

## 2. Identity until the first move: Matches

`referee_task2_identity.py`, `.json` (21 s).
- **(a) Stored runs.** Every slow-arm run with no rebuild has exactly NOV's flips, solved flag and fast work, for the
  same instance and run index. That is 4,752 runs, 0 mismatches:
  - test: G 1,190, GO 528, Gx 935, RND 706, ST 575;
  - stress: G, GO and ST, 100 each;
  - post hoc: RNDO 518.
- **(b) Fresh runs.** 1,750 runs: 7 cells (`local` w10/w40 3200, `embed` and `block` 3200, `local` w10 800, `rand` 800,
  `embed` 800), arms G, GO, RND, RNDO and Gx, 10 test instances, 5 runs each.
  - Each run of `run_slow` was stopped at its first rebuild by wrapping `reduce_pattern`. The driver's state read back
    there (x at every distinction, last-flip times, fast RNG state, step counter t, flips, fast work) equals Novelty+
    alone capped at the same flips, in **1,391 of 1,391**.
  - The 359 runs that never moved equal NOV's whole run.
  - The first move comes after one epoch for GO, RND and RNDO (n flips), and later for G (median 25,600 flips on the
    primary cell).

## 3. Charging (A91): Differs, in size

`referee_task3_charging.py`, `.json`. The data part takes 0.2 s. The instrumented reruns take 9 s: GO, 10 test instances
× 5 runs on `local` w10 3200, w40 3200, `embed` 3200 and `local` w10 800. **All 200 reruns reproduce the stored runs bit
for bit.**

**By reading, what does real work and whether `work` charges it:**

| Operation | Charged | Uncharged real work |
| --- | --- | --- |
| `fl_new` (handle, occurrence lists) | 3m | O(n) prefix sums, copies |
| `fl_run` per flip (bm on 3 members, flip) | deg read | O(1) knot draw and visit count; O(previous epoch's visits) reset per epoch |
| `sl_probe` mode 0 target read | nvis + nord | **qsort, O(nord log nord)** |
| mode 1 draws, mode 2 scan | 1 per draw; 0 | mode 2 skips probed knots, O(m) per pass |
| `propagate`, `tie_probe`, `shadow_triple`, `is_knot`, shadow choice | 3 per knot read + ns; scan; 6 | trail reset (bounded by the charged work) |
| `sl_reduce` | 3m + 3 per worklist pop + 1 per moved incidence + n0 + 3m, on all original knots and shadows every time | uf_find chains (amortized), O(n0 + m) init, reading the input ties |
| `run_slow` after a find: `fl_get` | 0 | O(n + m) copies |
| `probed_keys = np.union1d(...)` | 0 | **sort of the probed-key set, which grows over the run** |
| `reduce_pattern`: `np.unique(sig_keys)`, `idx.sort()`, `np.unique(ties.root)` | 0 | **O(m log m) + O(n0 log n0) sorts** |
| `build`: `np.isin(sig_keys, probed_keys)` | 0 | **O((m + P) log(m + P))** |
| idx map, majority vote (2 × bincount, where), xo | n0 | O(n0), O(m) passes |
| final map back and check | 0 | the same as NOV's check |

So `work` charges the rebuild O(m0 + n0) where its real cost is O(m log m + P log P), and charges the guided qsort
linearly.

**Measured for GO on the primary cell** (per run, means over the 50 reruns):
- **Charged work.** 3.27·10^6 in total: fast 0.89, probes 0.84, rebuild 1.54 (·10^6), over 10.5 rebuilds.
- **Uncharged sorting.** 1.89·10^6 element·log2 operations: `np.unique` 1.02, `np.isin` 0.69, `union1d` 0.06, guided
  qsort 0.11 (·10^6). That is 1.2 times `work_rebuild` and 0.58 times the charged total.
- **The C rebuild is charged fairly.** `sl_reduce` and `fl_new` cost 5.7 ns per charged incidence; the fast loop costs
  5.3 ns.
- **The Python side is not charged.** It takes 11 to 17 ms of 18 to 26 ms of rebuild CPU, about 2 to 3.3·10^6
  fast-incidence equivalents. That is 1.1 to 2.1 times `work_rebuild`, depending on machine load.
- **Rebuild CPU per charged incidence** is 17 to 64 ns across cells, against 5 to 6 ns for the fast loop.

**R with the uncharged part added**, two ways:
- **sort operations at one unit each** (deterministic; a lower estimate);
- **rebuild CPU at the cell's pooled fast-loop rate** (from the stored runs; an upper estimate that includes interpreter
  overhead).

| GO, cell | R_W (reported) | + sort ops | + rebuild CPU | + all uncharged CPU | R_CPU |
| --- | ---: | ---: | ---: | ---: | ---: |
| `local` w10 3200 | 0.150 | 0.24 | 0.28 | 0.30 | 0.33 |
| `local` w40 3200 | 0.235 | 0.46 | 0.59 | 0.60 | 0.61 |
| `embed` 3200 | 0.671 | 1.09 | 1.30 | 1.35 | 1.33 |
| `local` w10 800 | 0.384 | 0.57 | 1.29 | 1.45 | 1.63 |

**What this changes:**
- **GO's charged wins on both local 3200 cells survive.** The study also states them in CPU.
- **GO's "work win" on `embed` 3200 does not survive** any correction (1.09 to 1.30).
- **GO's "work win" on `local` w10 800** survives only at sort cost (0.57), not at CPU cost (1.29).
- **G and RND get worse.** By rebuild CPU, G on the primary cell goes from 0.84 to 2.1 and RND from 1.07 to 2.8, because
  they make many small rebuilds, each sorting all m0 knots. This only strengthens the frozen reading 4.
- **G's attention read is undercharged too.** G's probe CPU per charged incidence is 21 to 33 ns, against 5 to 7 for RND
  and GO, because of the qsort and the scan of visited knots. G's selection cost (P12) is therefore understated, not
  overstated.

**On the note's wording.** The Limitations line "Charged work does not depend on this" is not accurate. The Python side
does real O(m log m) work (sorting signatures and searching the probed set) that `work` does not count; it is not only
interpreter overhead.

## 4. The comparator: Matches

`referee_task4_comparator.py`, `.json` (35 s). The engine is the WHERE-NEXT referee's own unsigned-NAE Novelty+, copied
unchanged as `referee_sls_wherenext_copy.c`: its own RNG, and exact score ties broken uniformly at random. It ran at the
re-tuned settings, 5 runs on each of the first 20 test instances (seeds 7,100,000 to 7,100,019). Every final state was
checked.

| Cell (setting) | Referee median flips | Study NOV median flips | Ratio [99% bootstrap] | Spearman per instance |
| --- | ---: | ---: | --- | ---: |
| `local` w10 3200 (0.75, 0.1) | 452,989 | 415,326 | 1.09 [0.70, 1.90] | 0.80 |
| `rand` 3200 (0.65, 0.05) | 69,718 | 76,164 | 0.92 [0.76, 1.25] | 0.49 |

0 unsolved runs and 0 failed state checks.
