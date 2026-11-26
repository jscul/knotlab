# When a local reader's view settles, from the start alone: what stands

Epic `SETTLE-BOUND-20261126-001` (the coordinator's go-ahead on the selected direction of `LOOK-ALIKE-20261126-001`;
goals G17 with G1; register entry A283 bears on it), closed 26 November 2026. A check by the thread, not registered:
computed; referee pending. [The note, with the frozen bound, the expectations and the results](README.md)

## What stands

> **Referee R1, confirmed with fixes, no Block, folded in** ([report](referee-R1/report.md)).

1. **The frozen offsets fail.** The bound frozen on starts of up to four knots, a view settling by M + 5 rounds without
   parents and M + 7 with them (M the larger of the largest set of live start knots sharing a neighbour and the largest
   fresh count of a round-1 birth), fails, through each run's last saved round and with dimensions from the completed
   run, on 41 of 1,556 five-knot starts and 6 of 387 of a seeded sample of 1,000 six-knot starts under not-all-equal,
   and on 11 of 1,078 and 2 of 283 under parity (11 of 1,064 and 2 of 282 if each start rule must pass K1–K3), by up to
   three rounds. M alone cannot fix the settling round: two five-knot starts with M = 3 and identical first-round
   readings settle at 3 and 9.
2. **The late starts settle three rounds after the last fall.** For all 47 late starts under not-all-equal the view
   settles exactly 3 rounds after the last strict fall in the count of births (5 with parents). In 34 of them a single
   join takes every loose distinction and the counts then follow a lone three-place knot's tail (under parity the
   growth closes at that join); the other 13 never narrow to one.
3. **The pair rule** with each start's bound as its cut misses only pairs that include a late start; that pairs whose
   views both settle by the cut are predicted holds by construction, so it is not a test.

**Not established.** A prediction of the last fall from the start alone; starts of seven knots or more.

## Position and next directions

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the settling round bounded by the start's largest block | **Status:** Refuted (the stop met at a miss) | The frozen offsets fail on 41 of 1,556 five-knot and 6 of 387 six-knot starts under not-all-equal, 11 and 2 under parity |
| Local direction — a bound from the start alone | Continue, narrowly | The late starts narrow to one knot first; the round of that merge is the candidate |
| Broader exploration — what a local reader keeps of a start | Searching | The pair rule holds wherever views settle by the cut |
| Long-term goal — G17 Typical and rare meeting patterns, with G1 | Obstruction learned | The settling round is not a function of the largest block; for late starts it follows the last fall in births |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The round of the last merge as the settling bound | 2/3 — a bound from the start's meeting pattern | 3/3 — replay recovers parent identities | Compute from the map of joins the round at which every live member lies in one cluster; compare with settling on the 47 late starts → a bound, or none | Selected · started (`LAST-MERGE-20261126-001`) |
| 2 | Late views from the start alone | 3/3 — "logically small" made static | 2/3 — the late kinds look like chain tips and block bursts | Predict each late view from endless chains and blocks → every view, or a miss | Alternative · deferred |
| 3 | Rings of one proved rate | 2/3 | 3/3 | The look-alike referee's ring pairs, extended | Alternative · deferred |

1. Cheap; it needs a specified event and offset (the referee's note).
2. Still the stronger question.
3. Unchanged from the look-alike study.

**Corrections:** the referee's narrowings, logged (no Block).
**Goals:** checkpoint row added (G17, G1; obstruction learned); no goal changed.
**Assumptions:** none added; the bound was a prediction, now refuted, not an assumption.
**Scaffolds:** the readings (A283), the settling definition and its least round 3, the census weighting and the seeded
sample. Swapped: the knot law (parity), four, five and six knots. The bound fitted the small starts and failed at five knots
and in the six-knot sample under both laws.
**Advisor:** not consulted before the freeze, again a slip against the standing practice; the referee is the check.
