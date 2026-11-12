# Steering rules against blind search

Status: Proved (blind baselines exact; runs computed, frozen). Refereed: Confirmed (`referee-R1/report.md`). `check.py`, ticket A of
`research/STEER-LEARN-20261112-001/preregistration.md`, frozen with the code in commit `a2cd50751` before any frozen run. The 1,600 runs are
in `runs.jsonl` (2 hours 47 minutes on 20 processes); `result_summary.json` settles the marks.

## The test

One copy of (2, 0, 4), two settings: F (the drawn engine; 4 laws at rest) and GE (the graded value-free engine; 64). Four learners: B, the
unchanged credit learner; P, persistence targeting; M, make and break; A, two-sided acceptance. Targets the count (`01101001`) and a swap
target g chosen by a frozen rule (F: `0uu01uu1`; GE: `00001111`). 100 seeds each, to the first stop; every world probe and every candidate
check against stored states charged. Pass: median charged probes at most half the blind median and 3 of 4 runs within it. Steering shown:
passes on the count and on g.

## Results

| Setting / rule | Count: found, median charged probes (blind median) | Count: within blind median | g: found, median charged (blind) | g: within | Median candidate checks (count, g) |
| --- | --- | --- | --- | --- | --- |
| F / B | 100, 19 (6) | 13% | 100, 5.5 (11) | 79%, passes | 0, 0 |
| F / P | 99, 19 | 26% | 100, 6 | 81% (median 6 > 5.5) | 0, 0 |
| F / M | 100, 78 | 0% | 100, 22 | 28% | 55.5, 16.5 |
| F / A | 99, 1,759.5 | 0% | 100, 552.5 | 0% | 1,716, 546.5 |
| GE / B | 45, not found in half (22) | 2% | 61, 125.5 (45) | 24% | 0, 0 |
| GE / P | 37, not found in half | 6% | 46, not found in half | 15% | 0, 0 |
| GE / M | 50, not found in half | 0% | 62, 399 | 6% | 158.5, 115.5 |
| GE / A | 36, not found in half | 0% | 58, 4,056 | 0% | 2,118, 1,618 |

Counting world probes only, M and A are no faster than B: on F the count's medians are 21 and 19 world probes, g's 5.5 and 5.5.

**No rule shows steering in either setting.** No rule passes on the count. The one pass is the unchanged learner B on g in F, and every rule
finds g there in about 5.5 to 6 world probes: the learner's own walk reaches g's law faster than blind draws whatever its rule, and reaches
the count's law more slowly. That is a bias of the walk, not of the examples, since B uses none; whether it comes from the dynamics' preference or from the fixed
start (every run begins at the same law) is not separated (referee).

## What it says

Three known steering ideas (WalkSAT's break count, clause weighting, contrastive acceptance), lifted to this learner, do not let its examples
steer it: with every check charged they cost more than blind search, and even counting world probes alone they are no faster than the
unchanged learner. The learner's walk has its own preferences among the laws it can rest at, favouring some targets and disfavouring
others, independent of what it is taught.
