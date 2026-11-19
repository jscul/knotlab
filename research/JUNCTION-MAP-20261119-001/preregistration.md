# A map that sees loops through first-round junctions: pre-registration

Epic `JUNCTION-MAP-20261119-001` (the coordinator's go-ahead on `BREAK-EDDIES-20261119-001#1`; goal G17), 2026-11-19. Written after
a pilot (disclosed) and the advisor's answer, before the frozen run. The canonical K1–K3 test is unchanged.

## The question and the stop rule

**The map.** Take the growth's stage after s rounds as a start: its junctions are the points, and the live ones are the last
round's. Read that start by the cluster rule, with its one scope cut lifted, so that a first-round group of three sharing two knots
with another block is kept and makes a loop of length two.

**The question.** Does this map predict the round-weights of the break-shape eddies (BREAK-EDDIES)?

**The stop rule.** Stop when it predicts the W of the 36 with W = y^2 (1 + y), or at a start where it cannot.

## Pilot (disclosed): the stop rule's second case is reached

- **The knot-level map with the cut lifted** differs from the growth by round 2 on all 36 starts. It overcounts; its rate is about
  3.3.
- **The junction map, at s = 1 and at s = 2,** equals the growth for one round, then differs at the next on all 36.
- **Merging instead** (the overlapping group of three demoted to an ordinary simplex) differs at round 1.
- **Controls.**
  - On the ring of five with a spare, five five-place knots, and the ring of seven with a spare, the stage at s = 1 is inside the
    rule's scope and the junction map is exact for 8 rounds.
  - At s = 2 and 3 these stages already hold the overlap, and the map differs at the second round. Yet the knot-level rule is exact
    on the original start.
  - Two touching knots and a chain of three are exact at s = 1, 2 and 3.
- **The gate.** Growth from the stage presentation equals the continued growth on 39 of 39 checks (8 rounds; s = 1, 2, 3).
- **The reading.** A group of three sharing two knots with a block is not a loop of length two: on a second lap the growth reaches
  the same junction, where the unrolled map counts a new cluster on every lap. The overlap arises two rounds into ordinary rings too,
  where the knot-level unrolled map handles it correctly from the start. So a later stage is not a valid start for the rule.

## Prior work in the program

`python3 -B scripts/track.py objects "junction map stage presentation first-round groups of three loop of length two" --until 2026-11-19 --exclude JUNCTION-MAP-20261119-001`

- `BREAK-EDDIES-20261119-001`: the same starts, their W, and the stage reading (stagelib).
- `CLUSTER-ALL-20261119-001` and `RING-PAIR-20261119-001`: the rule and the cover model.
- `NAE-GROWTH-20261119-001`: the stage presentations of A108. `MEET-ONCE-20261119-001`: a related object (presentations whose
  junctions meet once), the same words.

## Predictions (frozen), on fresh starts

The population: BREAK-EDDIES' other 80 rational starts, the referee's two six-knot eddies, the five catalogue entries, rings of 9 to
13 knots with a spare, and two controls; s = 1, 2, 3.

| # | Prediction | Fails when |
| --- | --- | --- |
| G | the stage presentation grown 8 rounds equals the continued growth | any differs |
| J1 | where the stage holds the overlap, the junction map equals the growth at round s + 1 and differs at round s + 2 | any other pattern |
| J2 | where the stage is inside the rule's scope and free of known breaks, the junction map equals the growth for every round compared (up to 8) | any differs |
| J3 | the knot-level cut-lifted map differs by round 2 on every rational break-shape start | one does not |

## Runs and stop rule

`job.py` through the shared runner (94 cases); `merge.py` scores.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2), before the freeze.
- **The answer is unreliable.** The advisor had no tools, yet it describes reading and running files that do not exist: `eddies.py`,
  `pilot_junction_map2.py` and a scratch folder `/tmp/jm_adv/`, which is absent. Its two checkable claims are false:
  - the W = y^2 (1 + y) starts do approach the plastic number (three-round mean ratios 1.324 to 1.327 at round 34);
  - the stage presentation does equal the continued growth (39 of 39).
- **Its one usable point** is to gate the stage presentation before comparing any map with it, which is gate G.
- **Its suggestion,** that the loop of length two is in the stage a ring of four knots (A, k0, B, k1, joined by two-knot places), is
  recorded as a direction, not tested.
