# When do separately born chains combine?

Epic `PLUS-ONE-20261118-001`, 18 November 2026, by Claude, on the coordinator's go-ahead for `TOUCH-CENSUS-20261118-001#2`. Goal
G17. **Referee pending.**

**Record.** Pre-registration [preregistration.md](preregistration.md) (frozen in commit `7497a7e52`); code
[linked.py, job.py, merge.py](../../experiments/PLUS-ONE-20261118-001B/PLUS-ONE-20261118-001B-E001_linked/); results
[results.json](../../artifacts/PLUS-ONE-20261118-001B/PLUS-ONE-20261118-001B-E001_linked/results.json); run `runs/plus-one`
(459 cases, all ok, 22:43 UTC). `merge.py` had one scorer fix after the run (a dictionary key printed as text); no number changed.

## The answer

**In the owner's terms.**
- **Chains born apart combine when their partners touch, mostly.** Two chains born in the same round grow as one product, adding
  their dimensions, when the junctions they are each asked to join with share a neighbour. With that one link the rule predicts the
  dimension (junctions by round) in 11,649 of the 11,658 census arrangements that grow with a birth, never overshooting.
- **It is not the whole rule.** Ten arrangements (9 in the census, 1 of the 149 six-knot samples that grow with a birth) combine two
  chains whose partners do not share a neighbour. All ten have the same shape: two births in round 1 from two start knots that
  share a distinction. The obvious repair, linking births whose parents are neighbours, is wrong: it overshoots in 889 census
  arrangements (checked after the read-out). So the frozen test P1 failed, by one arrangement, and the right second link is open.
- **No larger shapes occurred.** Every linked component was two classes (1 + 1, or 1 + 2), always pairwise linked; no 2 + 2, no
  three classes, no path. The advisor's sharper predictions could not be tested.

| Part | Arrangements | Rule matches | Overshoots | Misses (unlinked, dimension one more) |
| --- | --- | --- | --- | --- |
| census (fitting) | 11,658 | 11,649 | 0 | 9 |
| six knots (test, P1) | 149 settled with a birth (of 400 sampled) | 148 | 0 | 1 |

The six-knot sample: 237 stall at once, 14 close, 15 grow one-, 132 two- and 2 three-dimensionally (two-dimensional 89% of those
that grow).

## Predictions and verdicts

| # | Prediction | Verdict |
| --- | --- | --- |
| F | (fitting) report matches, overshoots, unlinked misses and shapes | 11,649 matches, 0 overshoots, 9 unlinked misses; shapes 1 + 1 (218) and 1 + 2 (4), all cliques |
| P1 | six knots: dimension = linked sum, no overshoot | **failed** (148 of 149; no overshoot; the miss is the census's unlinked shape) |
| P2 | larger components add, a path of three gives 2 | not tested (no such shape occurred) |

## Limitations

- "Dimension" counts junctions by round. The six-knot sample is 400 random arrangements, not uniform over distinct ones.
- The second kind of link is not found.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2), before the freeze. It found three forms fitting the pilot, favoured the sum with a reading
(class and link one relation on births), asked that the census be labelled fitting, warned that links across what the test sees
would undercount (they did, in a different way: the ten misses link through the births' parents, not across rounds), and proposed
P1 and P2.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: when do separately born chains combine? | **Status:** Partially successful | Linked partners add dimensions in 99.9% of growing arrangements, with no overshoot; ten cases combine through a link not yet found |
| Local direction: an exact chain rule | Continue | One shape remains, all ten alike |
| Broader exploration: what sets the cheapest growth's dimension | Known alternatives | Chains born together, rings winding a cone (`RING-GROWTH-20261118-001`) |
| Long-term goal: G17 Typical and rare meeting patterns | Capability gained | A rule that predicts the dimension of almost every small arrangement from its first births |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The second link: the ten arrangements where two round-1 births from start knots sharing a distinction combine | 1/3 — closes the rule | 3/3 — ten cases, one shape | compare their partners' descendants with the 889 overshoots of the naive repair → stop at a link that separates them, or a proof none local does | Selected · awaiting go-ahead |
| 2 | Serial growth read from distances (`FRESH-COUNT-20261118-001#1`) | 2/3 — tests A104 | 2/3 | as before | Alternative · deferred |
| 3 | The general ring formula (`RING-GROWTH-20261118-001#2`) | 2/3 | 2/3 | as before | Alternative · deferred |

**Corrections:** none. **Goals:** G17 checkpoint (capability gained). **Assumptions:** none new. **Basket:** B196,
`FRESH-COUNT-20261118-001#1`, `RING-GROWTH-20261118-001#2`, B202; none taken.

## Final report as sent (2026-11-18 22:47 UTC)

**Outcome:** Separately born chains combine when the junctions they are each asked to join share a neighbour, almost always. With that one link, the dimension (junctions by round) is predicted in 11,649 of 11,658 census arrangements that grow with a birth, and in 148 of 149 six-knot samples, with no overshoot anywhere. The frozen test failed by one arrangement. Closed, partially successful, referee pending.

- **The ten misses** (9 in the census, 1 in the six-knot sample) all have one shape. Two round-1 births come from start knots that share a distinction, and their partners do not share a neighbour.
- **The obvious repair fails.** Linking births whose parents are neighbours overshoots in 889 census arrangements (checked after the read-out). So the right second link is open.
- **No larger shapes appeared.** Every linked pair was 1 + 1 or 1 + 2. The advisor's sharper predictions (2 + 2, three classes, a path) could not be tested.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: when do separately born chains combine? | **Status:** Partially successful | Linked partners add dimensions in 99.9% of growing arrangements, with no overshoot; ten cases combine through a link not yet found |
| Local direction: an exact chain rule | Continue | One shape remains, all ten alike |
| Broader exploration: what sets the cheapest growth's dimension | Known alternatives | Chains born together; rings winding a cone (`RING-GROWTH-20261118-001`) |
| Long-term goal: G17 Typical and rare meeting patterns | Capability gained | A rule that predicts the dimension of almost every small arrangement from its first births |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The second link: the ten arrangements where two round-1 births from start knots sharing a distinction combine | 1/3 — closes the rule | 3/3 — ten cases, one shape | compare their partners' descendants with the 889 overshoots of the naive repair → stop at a link that separates them, or a proof none local does | Selected · awaiting go-ahead |
| 2 | Serial growth read from distances (`FRESH-COUNT-20261118-001#1`) | 2/3 — tests A104 | 2/3 | as before | Alternative · deferred |
| 3 | The general ring formula (`RING-GROWTH-20261118-001#2`) | 2/3 | 2/3 | as before | Alternative · deferred |

**Corrections:** none. **Goals:** G17 checkpoint (capability gained). **Assumptions:** none new. **Basket:** B196, `FRESH-COUNT-20261118-001#1`, `RING-GROWTH-20261118-001#2`, B202; none taken. **Advisor:** Fable 5.2, before the freeze. It shaped the rule and the predictions.

Referee hand-off: the decision note is `research/PLUS-ONE-20261118-001/plus_one.md`.
