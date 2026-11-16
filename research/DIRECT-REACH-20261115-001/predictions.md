# DIRECT-REACH-20261115-001: predictions

Written 2026-11-16 19:30 UTC, from the advisor's revision of 2026-11-14 (`advisor_design_answer.md`, "Predictions"). The earlier
session agreed these wordings with the advisor but did not write them to a file before it stopped. The population D run had finished
(2026-11-15 06:14 UTC) and this session had seen 5 of its 146 rows (three constant-3 and two constant-2, all agreeing with the census)
before writing this file; no aggregate had been read. Population U had not been run. Treat P1 and P2 as frozen after the run but
before the read-out, and P3 as frozen before its run.

- **P1 (tie chains).** Of the 34 descriptions with L = 2 at s = 1..4, at least half have one tie class at N = 9 that meets every level
  3..8 (one linked chain, not separate ties per s).
- **P2 (direct against half-rate, from top level 2).** Only where the top-2 control agrees with the top-3 profile at s = 1..4:
  at s = 5 and 6 from top 2, at least 70% of the constant-3 descriptions stay at L ≤ 3; and the [3, 3, 4, 4] descriptions have
  L ≥ 5 at s = 6 from top 2 (a size-4 threshold answering no). A phase shift such as [3, 4, 4, 5, 5, 6] counts as half-rate.
  Constant 3 through s = 6 says "direct as far as read", not bounded.
- **P3 (undecided bounded).** In the pilot of 6 undecided bounded descriptions (the first 6 of population U by case id), at least 2
  have every census-undecided s decided with a 900 s budget per s. If fewer than 2 do, U is recorded as not cheaply decidable and the
  remaining 82 are not run.

Settled by construction and not counted as findings (advisor): L = 2 at N = 9 gives L = 2 at every larger N where the pattern lives;
L ≥ 2 always; any s reached by one spanning tie class.
