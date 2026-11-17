# Referee R1: the post hoc comparator and the relative-age read

Referee R1 (Claude), 2026-11-16, for SCALE-MEMORY-20261116-001.

**The engine.** `referee_sls.c` is copied from WHERE-NEXT's referee-R1, with two additions; the search
rules are unchanged:
- logging of the relative-age read;
- a CPU-time guard of 240 s per run, which no run reached.

**The instances.** They come from the study's `planted`, which is identical in both studies' `engine.py`.
Each was checked independently: three distinct distinctions per knot, and the hidden state satisfies every
knot. Every solution was verified.

**The runs.** All seeds are the referee's own, on 8 workers.

## 1. The post hoc comparator

**Verdict: Matches.** The frozen comparator was weaker than the best Novelty+ at n = 12800, by about 10%
on the study's statistic and 12% pooled, rather than 13%. The interval excludes 1.

Script: `referee_comparator.py`. Output: `referee_comparator.json`. Wall time 46 s.

Setup:
- The 100 test instances (seeds 3,000,000 to 3,000,099).
- 5 runs per instance at n = 3200 (cap 2e8) and 3 at n = 12800 (cap 2e9).
- *Geo-stat*: the median over instances of each instance's geometric mean over its runs, with a 95%
  bootstrap over instances.

| n | (p, wp) | Geo-stat [95%] | Pooled median | Study's post hoc | Referee / study |
| --- | --- | ---: | ---: | ---: | ---: |
| 3200 | (0.7, 0) | 72,434 [66,848, 76,688] | 74,926 | 71,960 | 1.007 |
| 3200 | (0.7, 0.01) | 72,293 [70,182, 82,380] | 75,458 | 74,046 | 0.976 |
| 3200 | (0.7, 0.05) | 82,162 [74,927, 96,455] | 85,882 | 87,876 | 0.935 |
| 12800 | (0.7, 0) | 361,874 [347,361, 383,652] | 356,716 | 363,539 | 0.995 |
| 12800 | (0.7, 0.01) | 373,847 [359,658, 393,513] | 371,474 | 367,547 | 1.017 |
| 12800 | (0.7, 0.05) | 398,899 [378,300, 430,765] | 401,236 | 416,884 | 0.957 |

How much weaker (0.7, 0.05) is than the others, with paired bootstraps:

| Comparison | Statistic | n = 12800 | n = 3200 |
| --- | --- | --- | --- |
| (0.7, 0.05) / best of the other two, re-chosen per resample | geo | 1.10 [1.04, 1.19] | 1.14 [1.07, 1.30] |
| (0.7, 0.05) / (0.7, 0) | pooled | 1.12 [1.07, 1.19] | 1.15 [1.08, 1.22] |
| (0.7, 0.05) / (0.7, 0.01) | geo | 1.07 [1.00, 1.15] | 1.14 [1.04, 1.27] |

The frozen single-run value at n = 12800, 416,258, is 1.15 times the referee's best geo-stat.

A caution on plain Novelty. At wp = 0 (no walk), 1 of 500 runs at n = 3200 hit the 2e8 cap: instance
3,000,009, run 1. Its median is unaffected, but the rule has no completeness guarantee. The WHERE-NEXT
referee also saw one capped run, at (0.675, 0). (0.7, 0.01) is as fast and safe.

## 2. Is the relative-age read scale-free?

**Verdict: Yes, nearly.** The clipped log age is not.

Script: `referee_relage.py`. Output: `referee_relage.json`. Wall time 2 s.

Setup:
- 20 test instances per n, one run each, Novelty+ at (0.7, 0.01). WHERE-NEXT's re-tuned settings per cell
  give the same picture.
- The read is the relative age a_j / max(a_1, a_2, a_3), taken for the three distinctions of the attended
  knot at every step. A never-flipped distinction has age t + 1.

| n | 200 | 800 | 3200 | 12800 |
| --- | ---: | ---: | ---: | ---: |
| Median relative age | 0.32 | 0.26 | 0.25 | 0.24 |
| First quartile | 0.042 | 0.028 | 0.025 | 0.024 |
| Fraction exactly 1 | 0.359 | 0.344 | 0.343 | 0.341 |
| Steps with a tied oldest member | 5.5% | 2.4% | 2.0% | 1.6% |
| Fraction below 0.001 | 0.3% | 2.3% | 3.8% | 4.7% |
| KS distance to n = 3200 (binned) | 0.061 | 0.018 | 0 | 0.009 |
| Clipped log age: above 1,000 or never | 9.7% | 23.6% | 45.1% | 63.4% |
| Clipped log age: median | 0.58 | 0.76 | 0.95 | 1.00 |

Reading:
- From n = 800 to 12800 the relative read's distribution hardly moves: KS distance at most 0.018.
- n = 200 differs slightly, because short runs leave more members never flipped, which tie at 1.
- One residual drift remains. A member flipped one step ago reads 1/max, and max grows with n, so the mass
  below 0.001 grows from 0.3% to 4.7%. That compresses "very recent" toward 0; it does not change its
  meaning.
