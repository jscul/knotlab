# When do separately born chains combine? Pre-registration

Epic `PLUS-ONE-20261118-001` (the coordinator's go-ahead on `TOUCH-CENSUS-20261118-001#2`; G17), 2026-11-18. The canonical K1–K3
test is unchanged.

## The question

In the arrangement census the rule "the dimension is the largest class of chains born together" missed 147 of the 11,658 settled
growing arrangements with a birth (145 at the census's close on 26,241, 147 on 26,341), each time by exactly one. Which chains
combine, and does one rule predict every case?

## The rule (found on a pilot of 12 exceptions and 8 matches, then 200 census arrangements; frozen here)

Births and classes as in `TOUCH-CENSUS-20261118-001`. Two classes of one round are **linked** when their partners share a neighbour
(or are neighbours). **The dimension (junctions by round) is the largest, over rounds and linked components, of the sum of the class
sizes in a component**; 0 if there is no birth. The advisor's reading: class and link are one relation on births (partners equal or
candidates of each other), each birth adds one chain direction, related chains join into one product. Exponential rings and
birthless growth are outside the rule.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| F | (fitting, not a test) on the census's 11,658 arrangements: report matches, false positives (linked, dimension = largest class), unlinked exceptions, and the shapes of linked components (class sizes; clique or path) | — |
| P1 | On 400 random six-knot arrangements (sizes 3 to 5), among the settled polynomial arrangements with a birth: dimension = linked sum, with no false positive | any miss |
| P2 | (the advisor's) if a linked component with a non-largest class of size 2 or more, or of three or more classes, appears anywhere, its dimension is the sum; a path of three classes (A–B, B–C, not A–C) gives 2, not 3 | a counterexample appears |

The advisor's constructed cases (a linked 2 + 2, three mutually linked single classes) are not built here; P2 is scored on whatever
shapes the census and the sample contain.

**Exploration disclosed.** The pilot's 20 arrangements and one census shard of 200 (all 200 matched) were read before this freeze.

## Runs

`job.py` through the shared runner: 59 census shards of 200 and 400 six-knot samples; `merge.py` scores. A few minutes to an hour.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md); `modelUsage`
names claude-fable-5-2), before the freeze: it found three forms fitting the pilot (sum, largest + links − 1, largest + 1), favoured
the sum with a mechanical reading, asked that the census run be labelled fitting, and proposed P1 and P2.
