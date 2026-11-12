# Referee job LIFE-JUMPS-R1: the brief

The coordinator handed this job over on 2026-11-12 (14:44 UTC). It comes from the random-meeting-patterns thread:
`LIFE-JUMPS-20261112-001`, in commit 404324a1f, pre-registered in 68f4ef038. The census imports RANDOM-FATES' frozen `fates.py`.

## Claims under review

All are computed and frozen. J1 to J6 held on 689 of the 690 growths; the last U300 growth was still running.

| # | Claim |
| --- | --- |
| J1 | Uniform knots: share ≤ 0.05 forty knots before the end in 95 to 100% of runs, and ≥ 0.5 at the last base in 93 to 95%. |
| J1b | Ten knots before the end, the median share is 0.28 at U100 and 0.20 at U300. |
| J2 | In X0.3, X0.35, Og0.3 and Ol0.3, among endings after at least 200 knots, a class of at least 10 with share ≥ 0.05 exists at half-life in 61 to 75%. |
| J3 | The share ratio k20 / k1 is about 1.00 in those four, against 0.015 to 0.034 for U. |
| J4 | At X(0.3), the share after 300 and after 1,000 knots predicts an end before 6,000 with AUC 0.82 and 0.84 (the hazard: 0.77 and 0.85). |
| J5 | At X(0.2), the largest class at 6,000 knots is at most 15 in 96% of the 78 runs that reach 6,000. |
| J6 | The largest class's median arrival index is below half the distinctions in 100% of endings. |

**Proved by definition.** The largest class never shrinks. A knot with a new distinction ties it exactly when its pair is tied
equal. The closing hazard is the end's chance per closing.

**Deviations, disclosed.** Two extra units ran with the frozen task and the same seeds. `summary_fixed.py` adds `json default=`.

## The coordinator's questions

- **(i)** Which claims are forced by a never-shrinking largest class or by survivorship? Especially J4 and J6: do the oldest
  distinctions sit in the largest class just because they have had more knots, and does censoring at 6,000 inflate the AUC?
- **(iii)** Do the deviations change any verdict?
- **(iv)** What is rediscovery, given the known results on giant components and 2-colouring and XOR-type thresholds?

(Question ii belongs to MISSING-KNOTS.)
