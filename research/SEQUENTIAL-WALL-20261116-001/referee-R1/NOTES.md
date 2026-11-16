# Referee R1 recomputation: SEQUENTIAL-WALL-20261116-001

Written 16 November 2026 by an independent referee helper (Claude). All oracle code is new and lives in this folder
(`referee_core.py` plus one script per task). I read the study's `atoms.py`, `job.py`, `summarize.py`, the opening of
`gates.py`, `contract.json` and `proof.md` only to fix the definitions and the sampling protocol: m = 3n ordered distinct
triples, held set = a prefix of a uniform order, k* = least k with 2·closure ≥ n, k = round(αn), "largest Strahler number"
= the maximum over true last-layer outputs (layered) or over all true gates (unlayered), and the median taken over samples
with a true output. No oracle imports or copies study code. The one exception is `referee_cross_study_code.py`, which runs the
study's `atoms.py` as the thing under test on my instances (with `-B`, so no bytecode is written). For the statistical
comparisons I read the study's per-sample records from `artifacts/.../run/results.jsonl` as data. Seeds are my own
(`SeedSequence([773x, ...])`). Every run used `.venv/bin/python -B`; no run took over 5 minutes. Memory was not measured but stayed small (n ≤ 2^18).

Methods that differ from the study's on purpose:
- k* by binary search, which is valid because the closure grows with k; the study used one incremental closure.
- Triples drawn by rejection sampling.
- Forced set computed three ways: worklist counters, synchronous rounds, and phases.
- σ computed exactly two ways. (1) Set-valued enumeration: T_h(v) is the set of Strahler numbers of derivation trees of
  height ≤ h, iterated to h = n. A tree that has the least Strahler number, and the fewest nodes among those, repeats no
  label on a root-to-leaf path, so its height is at most n − 1. (2) Knuth's 1977 generalized Dijkstra for superior
  functions. Relaxation from ∞ is a third check.
- Fringe computed as an exact integer by Knuth's algorithm with x + y, instead of log-floats.

## Task 1: Theorem 1 by brute force. Verdict: Matches

Script `referee_task1_theorem1.py`, output `referee_task1_theorem1.json`, 24 s in total.

| Set | Cases | Distinctions | Largest σ | Mismatches |
| --- | --- | --- | --- | --- |
| exhaustive, n = 4: all 2^12 atom sets × 2^4 held sets | 65,536 | 262,144 | 1 | 0 |
| random, n = 5..12, m from n/2 to 4n, 1..n−1 held | 30,000 | 254,841 | 3 | 0 |
| stress, n = 8..12, m from 2n to 6n, 2–3 held | 20,000 | 199,535 | 3 | 0 |
| pyramids, h = 1..6 | 6 | 83 | 6 | 0 |

In every case all of these agree:
- the phase from the literal pure-Python forcing law;
- σ from set enumeration, from Knuth's algorithm and from relaxation;
- the vectorized phase law (10,502 cases);
- P = max finite σ;
- the forced set, computed as closure, rounds and phases; on 2,234 cases it was also checked against brute force over all
  states.

Re-running the enumeration to height 2n changed nothing (1,000 of 1,000 cases). The proof's unsupported-cycle example
((h, c → d), (h, d → c)) gives σ = ∞ by enumeration, while (1, 1) satisfies the min-equations, as the proof says.
The limitation is that σ ≤ 3 in the random sets at n ≤ 12, so deeper nesting is covered only by the pyramids and by Task 2,
where Knuth's σ equals the phase at k* and k* − 1 on all 142 samples, up to σ = 13.

## Task 2: Rounds and phases at the jump. Verdict: Matches, within sampling noise

Script `referee_task2_random.py`, outputs `referee_task2_n{10,12,14,16}.json`. Runtimes: 0.4 s, 2 s, 13 s and 78 s for
40, 40, 30 and 20 samples. As an extra size I also ran 2^18 with 12 samples (289 s). The read-out is
`referee_task2_analyze.py`, written to `referee_task2_summary.json`; the p-values come from Mann–Whitney tests of my
samples against the study's samples.

Medians, mine against the study's:

| log₂ n | k*/n | R* | P* | R at k*−1 | P at k*−1 | log₂ fringe at k* |
| --- | --- | --- | --- | --- | --- | --- |
| 10 | 0.1055 / 0.1021 | 32 / 34 | 6 / 6 | 12.5 / 11.5 | 3 / 3 | 10.66 / 10.80 |
| 12 | 0.1021 / 0.1023 | 52.5 / 55 | 7 / 8 | 23.5 / 21 | 4 / 4 | 12.90 / 13.18 |
| 14 | 0.1005 / 0.1002 | 86 / 86 | 9 / 9 | 46 / 38.5 | 5 / 5 | 15.17 / 15.20 |
| 16 | 0.0991 / 0.0980 | 142 / 128 | 10 / 10 | 72 / 63.5 | 6 / 6 | 17.79 / 17.36 |
| 18 (extra) | 0.0983 / 0.0984 | 197.5 / 176 | 11 / 11 | 123.5 / 107 | 7 / 6 | 18.95 / 19.02 |

Of the 74 testable Mann–Whitney comparisons (6 have the same constant on both sides), two give p < 0.05, about what chance predicts: P at α = 0.06, n = 2^12, p = 0.017 with both medians 2; and R at α = 0.4, p = 0.047 with both medians 7. At n = 2^12:
- α = 0.03: R = 2, P = 1, the same as the study;
- α = 0.2: R = 12, P = 4, the same as the study;
- α = 0.06 and 0.4 also agree.

The closure at k* − 1 and at k* (0.21n and 0.934n) agrees with the study at every size.

Slopes of median R* (log₂ against log₂ n) and of median P* (against log₂ n), with bootstrap 95% intervals:

| Range | Mine, R* | Study's data, R* | Mine, P* | Study's data, P* |
| --- | --- | --- | --- | --- |
| 2^10..2^16 | 0.358 [0.315, 0.376] | 0.319 [0.289, 0.343] | 0.70 [0.55, 0.78] | 0.65 [0.48, 0.73] |
| 2^14..2^18 | 0.300 [0.257, 0.353] | 0.258 [0.202, 0.360] | 0.50 | 0.50 |
| 2^10..2^18 | 0.334 [0.308, 0.349] | 0.298 [0.272, 0.337] | 0.65 | 0.60 |
| study as reported | | 0.302 over 2^14..2^20 [0.269, 0.356] | | 0.57 over 2^10..2^20 [0.49, 0.65] |

My exponents, about 0.30 to 0.36, are consistent with the reported 0.30, and the intervals overlap. Phases grow by 0.5 to
0.7 per doubling, consistent with 0.57.

A caveat that is not a discrepancy: on the study's own data, the R* slope over 2^14..2^18 is 0.258, below P2a's window
[0.29, 0.37]. Its 0.302 over 2^14..2^20 rests on the 8-sample point at 2^20. "Held" for P2a is therefore not robust to
dropping the last size, although my 2^10..2^18 slope (0.334) does sit inside the window.

## Task 3: Fringe. Verdict: Matches

The fringe is computed in the same runs as Task 2, as an exact integer, at every size up to 2^18. σ ≤ log₂ fringe holds
for every forced distinction at k* and k* − 1 in all 142 samples. My median of the largest log₂ fringe at k* is 10.66,
12.90, 15.17, 17.79 and 18.95, against the study's 10.80, 13.18, 15.20, 17.36 and 19.02, with all p > 0.29. The study's
float `log2_fringe` agrees with my exact fringe on 5 instances at k* with n = 2^12 and on 3,000 small patterns (see the
cross-check below).

## Task 4: Circuits. Verdict: Matches, within sampling noise

Scripts `referee_task4_circuits.py` (10 samples per family, 10 s) and `referee_task4_more.py` (100 samples, 46 s), with
outputs of the same names.

- **Encoding.** On every input of 120 random layered circuits (width 2–5, depth 1–4) and 120 unlayered circuits (2–6
  inputs, 1–10 gates), 5,020 evaluations in all, the closure equals the circuit's value at every gate, with 0 mismatches.
  On 4,316 of these the forced set also equals the brute-force set of distinctions that are 1 in every allowed state.
- **σ against phase.** σ equals the phase at every distinction of every circuit, and native rounds reproduce the
  circuit's values.

Median largest σ among true outputs. Only 10-sample medians are comparable with the study's 10-sample values: the 100-sample
figure is a far more precise estimate, so a gap of one between it and a 10-sample median is not a discrepancy. P(10-median)
is how often a 10-sample median drawn from my 100 samples equals the study's value.

| Family | Mine, 10 samples | Mine, 100 samples | Study, 10 samples | P(10-median = study's) | Mann–Whitney p |
| --- | --- | --- | --- | --- | --- |
| w1024, d = 8 | 4 | 4 | 4 | 1.00 | 0.34 |
| w1024, d = 16 | 5 | 5 | 5 | 1.00 | 0.37 |
| w1024, d = 32 | 7 | 6 (52 at 6, 45 at 7) | 7 | 0.31 | 0.47 |
| w1024, d = 64 | 8 | 9 | 9 | 0.48 | 0.41 |
| w256, d = 8 / 16 / 32 / 64 | 4 / 5 / 6.5 / 8 | 4 / 5 / 6 / 8 | 4 / 5 / 6 / 9 | 0.12 at d = 64 | > 0.35 |
| unlayered, G = 1,024 | 3 | 2 (68 at 2, 32 at 3) | 2 | 0.81 | 0.90 |
| unlayered, G = 4,096 | 3 | 3 | 3 | 1.00 | 0.87 |
| unlayered, G = 16,384 | 4 | not run | 4 | not run | not run |

The 10-sample medians move by one between seeds; the distributions are the same.

## Task 5: The dual law. Verdict: Matches

Scripts `referee_task5_dual.py` (18 s) and `referee_task5_pdual_more.py` (60 s). I implemented the dual law from the
proof's text alone.

On 30,000 random acyclic patterns (n = 5..12, m from n/2 to 4n, 0..n/2 held; 254,807 distinctions, 171,075 of them
unforced):
- (a) Every distinction is forced or found unforced, never both: 0 failures. On 7,519 patterns the unforced set also equals
  the complement of the brute-force forced set.
- (b) The dual phase equals the least generalized Strahler number, computed by a DP in topological order, at every
  distinction: 0 failures. Dual phases reach 5.
- P_dual equals the largest dual phase plus one.
- The mutant without the +1 disagrees on 24,718 patterns, so the test has power.

The ladder (k = 2, 8, 32) and the pyramid (h = 4, 8, 16) have nothing unforced and P_dual = 0, while their P equals k + 1
and h.

Bonus, layered w = 1024 (median P_dual against the study's): 5 against 5 at d = 16 (60 samples); 7 against 6 at d = 32 (60
samples, 24 at 6 and 34 at 7, Mann–Whitney p = 0.076); 9 against 8.5 at d = 64 (40 samples). The medians of min(P, P_dual)
are 5, 6 and 8, exactly the study's. The forced and unforced sets partition every circuit. The d = 32 gap is sampling
noise, not a definitional difference: the study's `dual_phases` gives the same per-distinction dual phases and P_dual as my
law on these same 10 circuits.

## Cross-check: the study's code under test

Script `referee_cross_study_code.py`, 5 s. The study's `untangling_phases`, `rank`, `log2_fringe` and `dual_phases` agree
with my oracle at every distinction on:
- 3,000 small acyclic patterns;
- 5 random patterns at k* with n = 2^12;
- 10 layered circuits with w = 1024 and d = 32.

## Summary

Nothing differs beyond sampling noise:
- Theorem 1 holds on 115,542 brute-force cases with 0 failures.
- The random-pattern medians, the slopes, the fringe, the circuit Strahler numbers and the dual law all reproduce.
- The only caveat is the fragility of P2a's slope window, noted under Task 2.
