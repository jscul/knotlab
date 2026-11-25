# The thread's third count

Study `DESCENT-HELD-20261125-001`, 25 November 2026. The confirming run's census counts are what a correction to an
earlier study rests on, so the thread counted them once more with a program that shares nothing with the drafter's
prototype or the confirming run's program.

- **What it uses.** The round of the study of births one at a time (`lr_core.own_round` of
  `LOCAL-ROUND-20261123-001A`, the engine the least-record study's own runs were checked against) and the census of
  `COPYING-PARTS-20261123-001A`, both imported unchanged. [The script](recount.py) · [its output](recount.json).
- **What it counts.** For each of the 3,380 census starts of up to five knots and each of seven laws that round can
  express: grow 8 rounds, or to the first round after which the structure has more than 3,000 knots, or to the first
  round that changes nothing; the start is counted when some new knot has two parents at different parent steps.
- **What it found.** The same numbers as the note and the confirming run, with the same splits by size of start and by
  greatest difference between a child and a parent:

| Law | Counted | Four-knot / five-knot starts | Greatest difference 2 / 3 |
| --- | --- | --- | --- |
| RATION-3 with waiting (the least-record study's law) | 510 | 21 / 489 | 501 / 9 |
| FLOOR1 with waiting | 223 | 11 / 212 | 222 / 1 |
| FLOOR1 with offshoots | 0 | | |
| FLOOR1 with retiring | 0 | | |
| RATION-3 with waiting, HOLD | 48 | 2 / 46 | 48 / 0 |
| FLOOR1 with offshoots, HOLD | 462 | 12 / 450 | 417 / 45 |
| FLOOR1 with retiring, HOLD | 369 | 7 / 362 | 304 / 65 |

- **The three witnesses**, grown three rounds with the same round: under RATION-3 with waiting, the start
  `[[0,1,2],[0,3,5],[1,3,4,6],[2,4,7,8]]` makes new knot 12 in round 3 from parents at parent steps 0 and 1; under
  FLOOR1 with offshoots and HOLD, `[[0,4,5],[1,2,6],[1,3,7,8],[0,2,3]]` makes new knot 9 in round 3 from parents at 0
  and 2; under FLOOR1 with retiring and HOLD, `[[0,4,5],[1,2,6],[1,3,7],[0,2,3,8,9]]` makes new knot 5 in round 2 from
  parents at 0 and 1. Each is as the note writes it.

**Limits.** The count is over all 3,380 starts; the note's figures are over the 3,348 whose start knots pass the knot
test under parity. The two agree because none of the 32 starts set aside is counted. The round used here has the
closing exception of parity built in and runs no knot test. The other seven laws of the confirming run (CAP-3 with
waiting, with and without fillers and with HOLD; ONE-FEWER and RATION-4 with waiting; ORD with waiting or stalling)
were not counted here and rest on two programs.
