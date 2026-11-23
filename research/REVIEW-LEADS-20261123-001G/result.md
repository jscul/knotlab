# Does repeated release need a failing pattern? Result

Ticket `REVIEW-LEADS-20261123-001G` (follow-up to ticket A, B310; G17 with G1), 2026-11-23. Computed; scientific
referee pending. [Pre-registration](preregistration.md) · [full tables and commands](results_draft.md) ·
[deviations](../../experiments/REVIEW-LEADS-20261123-001G/REVIEW-LEADS-20261123-001G-E001_release_and_test/deviations.md)

**No. In the two populations where release has been proved or excluded, every start that has any birth fails the
operator test at its first parent step, whether or not it is a source. The test tracks whether a start grows there,
not whether it keeps releasing.** The reading fixed before the run said: if at least 90% of growing starts that are
not proved sources fail, no argument is attempted. All of them fail.

## What happened

Fail / pass within twelve parent steps, the same under both laws:

| Recorded verdict | Stalled at once | Bounded | Growing |
| --- | --- | --- | --- |
| Edits of the seven-knot source, proved sources (16) | — | — | 16 / 0 |
| Edits, proved not sources (33) | 0 / 19 | 3 / 0 | 11 / 0 |
| Edits, undecided (4) | — | — | 4 / 0 |
| Supplied draws, proved sources (5) | — | — | 5 / 0 |
| Supplied draws, proved not (14) | — | 9 / 0 | 5 / 0 |
| Supplied draws, unresolved (173) | — | 11 / 0 | 162 / 0 |

- All 226 starts with a birth fail, at parent step 1. All 19 that stall at once pass.
- The first failing stage has a median of 15 knots for the proved sources among the edits and 17 for the growing edits
  proved not to be sources. Among the supplied draws the sources' median is 33 and the others' 29.
- The birth that breaks the test always has two or more parents (0 of 226 with one). Every proved source breaks at a
  two-parent birth.
- Of the 34 edits that fail, 21 fail on a sub-pattern made only of knots the unedited source also has.

## Predictions

| # | Verdict | Evidence |
| --- | --- | --- |
| G | Passed | Ticket A's first failing steps reproduced; the recorded counts (16, 33, 4; 5 of 192) recovered exactly, and both populations regenerated from the earlier study's own generators |
| P1 | Held | 21 of 21 proved sources fail |
| P2 | Held | Median 15 knots against 17 |
| P3 | Failed | 182 of 182 growing starts that are not proved sources fail; the bar was at most half |

The thread regrew eight starts drawn at random from the supplied draws and ran the planarity routine directly: each
passes at step 0 and fails at step 1.

## What this is about

About two recorded populations whose starts were supplied with enough loose distinctions to fund their first joins,
and the neighbours of one built source. The independent sources are five, by tree: the 16 edits are one family and one
draw sits in both arms. No verdict was recomputed. A limit of 240 seconds per growth stopped 32 histories, all after
they had failed.

**Verdict.** The question ticket A left is answered. Every recorded source fails the test because every recorded
source has well-funded births with several parents at its first step, and so does every other start supplied that
way. Set beside ticket A, where 247 of 280 sparsely supplied draws per law pass for twelve steps, what separates
passing from failing is how the first births are funded and grouped, not what the start goes on to produce. No
argument tying sources to the test is attempted.
