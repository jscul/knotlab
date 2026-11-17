# DECIDE-SMALL-20261117-001: predictions

Frozen at the commit that adds this file, after the advisor's check (`advisor/design_answer.md`), before any draw of the new seed was
made. Seen before:
- KEEP-REACH's sample, its mutations and the census, with their verdicts;
- a smoke of `decide.py` on already-seen keys (40 of KEEP-REACH's sample, and five third-class descriptions), whose verdicts matched.

The advisor's view is given beside each prediction.

- **P1 (completeness).** Every distinct pattern of the sample is decided by the five tests or the second tier. Prediction: 40%. The
  advisor gives 30–35%, and expects one to three undecided patterns, at least one cap-limited.
- **P2 (distinct fraction).** Distinct patterns are 10–30% of the kept descriptions. The advisor gives 10–25%. KEEP-REACH's
  population gave 24%, and the census 23%.
- **P3 (T1's share).** 50–80% of distinct patterns grow by T1. The advisor agrees: KEEP-REACH's population gave 42% and the census
  77%.
- **P4 (the late tests).** T3, T4 and T5 together decide at most 2% of the distinct patterns. The advisor gives about 65%; KEEP-REACH's
  population gave 2.7%.
- **P5 (consistency).** No pattern of the full-test subsample gets both a growing and a bounded verdict. Prediction: 95%.
- **P6 (deduplication).** No merge at depth 12 splits at depth 14. Prediction: 90%.
- **P7 (ground truth).** Every decided reading of the 50 ground-truth patterns fits its verdict. Prediction: 95%.
