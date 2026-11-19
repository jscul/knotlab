# Parity's eddies over the dropped junction

Epic `DROPPED-JUNCTION-20261119-001`, 19 November 2026, by Claude, on the coordinator's go-ahead (taking
`STATES-GROWTH-20261119-001#3`). Goals G1 and G17. **Referee pending.**

**Record.**
- Pre-registration: [preregistration.md](preregistration.md), frozen in commit `9dac43633` at 11:45 UTC after a pilot (disclosed).
- The run went through the shared runner (`DROPPED-JUNCTION-B1`, `runs/dropped-junction`, 33 cases, 323 starts), all ok by
  11:48 UTC.
- Code: [droplib.py, job.py, merge.py](../../experiments/DROPPED-JUNCTION-20261119-001B/DROPPED-JUNCTION-20261119-001B-E001_dropped/).
- Results: [results.json](../../artifacts/DROPPED-JUNCTION-20261119-001B/DROPPED-JUNCTION-20261119-001B-E001_dropped/results.json).

**Words.** Under parity, a presentation in which every distinction lies in at most two junctions has a **completed system** G*: the
presentation plus the implied junction "out" holding every loose distinction. The allowed states fix only G*'s cycle matroid, so
any point of G* can be the **dropped** one, the junction whose lines are the loose distinctions. The **original** choice drops out.

## The answer

**In the owner's terms.**
- **Under parity, a loop's self-feeding is not in the allowed states.** On all 23 eddies tested, only the original choice of
  dropped junction grows exponentially. These are the catalogue's five minimal ones, the census's 13 rings, and the rings of 9 to 13
  with a spare. With the same allowed states and another junction counted as the implied one, the loop only circulates, stalls or
  closes.
- **Why.** Dropping a ring knot makes its few lines the only loose ones, on its two ring neighbours and on the former implied
  junction, which now holds every other distinction. Two loose lines on that hub give 2 junctions a round, and three close the
  growth (the advisor's reading of the pilot).
- **No states-only rule recovers it in general.** The natural one is to drop the point of largest degree, which is the same as
  taking the presentation with the fewest places.
  - On the eddies it is the original choice, but on rings that is forced by counting.
  - On 300 random growing five-knot census starts, the original is the unique largest point in only 129.
  - Where it is not, the rule's pick grows differently in 14 starts.
  - Any other choice changes the growth class in 221 of the 300.
- **So the parity side of A108 is total.** Under not-all-equal the states fix the knots almost everywhere small (STATES-GROWTH,
  MANY-VALUED). Under parity even the eddies depend on which junction counts as the implied one, a choice the states do not record.

## Predictions and verdicts

| # | Prediction | Verdict | Reading |
| --- | --- | --- | --- |
| D1 | on every eddy only the original choice is exponential | **held** | 23 of 23 |
| D2 | on every eddy the original is the unique largest point (forced on rings; a check) | **held** | 23 of 23 |
| D3 | (risky) where the original is not the unique largest point, the largest-point rule changes the class somewhere | **held** | 14 of 171 |

3 of 3 held. Readouts on the 300:
- under the original choice: two-dimensional 193, closed 67, one-dimensional 40;
- under the other 1,500 choices: two-dimensional 799, stall 307, one-dimensional 206, closed 188, exponential none.

## Known results, and what this adds

- **Known, cited once.** Whitney's 2-isomorphism theorem (1933); Tutte's characterisation of the points of a three-connected graph
  as the non-separating cocircuits of its cycle matroid.
- **What this adds.** For the cheapest growth under parity, which junction counts as the implied one decides whether a loop feeds
  itself. Same-state presentations of every eddy lose it. The fewest-places rule, the natural states-only choice, departs from the
  cheapest growth in a measured share of starts.

## Limitations

- Only the dropped-junction choices were tried, not the twists at two-point cuts, which give further presentations of the same
  states.
- 30 rounds or 60,000 junctions; classes by LOOP-CATALOGUE's rule. The samples are five-knot census starts.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2), before the freeze. The answer stayed within its text.
- **The rule and the scope.** It restated the rule as fewest places. It pointed out that D2 is forced on rings, and that the real
  test needs starts where a knot ties with out or beats it (D3).
- **Its local reading.** It read the pilot locally (the dropped knot's lines decide), which is recorded as a direction.

## Position

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: parity's eddies over the dropped junction | **Status:** Successful (3 of 3 held) | Only the original choice feeds itself on all 23 eddies; the fewest-places rule departs from the cheapest growth |
| Local direction: A108 under parity | Confirmed | The growth's class depends on the dropped junction, invisible in the states |
| Broader exploration: the growth and the canonical reading | Known alternatives | Not-all-equal: the states fix the knots almost everywhere; parity: never |
| Long-term goal: G1 | Obstruction learned | Under parity distance (the states) cannot carry the growth's eddies |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The transfer between kinds of junction (`JUNCTION-MAP-20261119-001#1`), once BREAK-EDDIES' verdict is in | 3/3 | 2/3 | as there | Selected · awaiting the verdict |
| 2 | The advisor's local reading: the class after a drop depends only on the dropped knot's lines (test with six-place ring knots and knots with no loose line) | 2/3 | 3/3 | grow the dropped choices on rings with one six-place knot → stop at a rule from the dropped star alone | Alternative · deferred |
| 3 | How often non-minimal supports occur at scale (`MANY-VALUED-20261119-001#3`) | 2/3 | 3/3 | as there | Alternative · deferred |

## Final report as sent (2026-11-19 11:50 UTC)

**Outcome:** Under parity, a loop's self-feeding is not in the allowed states. On all 23 eddies tested, only the original presentation feeds itself. These are the catalogue's five, the census's 13 rings, and the rings of 9 to 13 with a spare. The same states, read with a different junction counted as the implied one, only circulate, stall or close. 3 of 3 frozen predictions held. Closed, referee pending.

- **Why.** Count a ring knot as the implied junction instead, and its few lines become the only loose ones. They sit on its two ring neighbours and on the old implied junction, which now holds everything else. Two loose lines there give 2 junctions a round; three close the growth.
- **No states-only rule recovers it.** The natural rule is "drop the largest junction", the same as "fewest places". It picks the original on the rings, but that is forced by counting. On 300 random growing five-knot starts, the original is the largest in only 129. Where it isn't, the rule grows differently in 14. Any other choice changes the growth class in 221 of the 300.
- **The two laws side by side.** Under not-all-equal the states fix the knots almost everywhere small, so distance carries the growth (the last two studies). Under parity even the eddies need a choice the states don't record.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt: parity's eddies over the dropped junction | **Status:** Successful (3 of 3 held) | Only the original choice feeds itself on all 23 eddies; the fewest-places rule departs from the cheapest growth |
| Local direction: A108 under parity | Confirmed | The growth's class depends on the dropped junction, invisible in the states |
| Broader exploration: the growth and the canonical reading | Known alternatives | Not-all-equal: the states fix the knots almost everywhere; parity: never |
| Long-term goal: G1 | Obstruction learned | Under parity, distance (the states) can't carry the growth's eddies |

**Next step:** Research directions — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | The transfer between kinds of junction, once BREAK-EDDIES' verdict is in | 3/3 | 2/3 | as in JUNCTION-MAP | Selected · awaiting the verdict |
| 2 | The advisor's local reading: the class after a drop depends only on the dropped knot's lines | 2/3 | 3/3 | rings with a six-place knot → stop at a rule from the dropped star alone | Alternative · deferred |
| 3 | How often non-minimal supports occur at scale | 2/3 | 3/3 | as in MANY-VALUED | Alternative · deferred |

**Corrections:** none. **Goals:** G1 and G17 checkpoint (obstruction learned). **Assumptions:** A108 history line (the parity side is total). **Basket:** `STATES-GROWTH-20261119-001#3` taken. **Advisor:** Fable 5.2, before the freeze; its answer stayed within its text. It restated the rule as fewest places, flagged that D2 is forced on rings, and said the real test needs starts where a knot ties with or beats the implied junction (D3, held).

**Referee hand-off.** The decision note is `research/DROPPED-JUNCTION-20261119-001/dropped_junction.md`; the prior-work line is in the pre-registration (objects-gate passes). Please check `droplib.rechoice` (the completed system and each dropped choice) and one non-original choice on a ring by hand.

The BREAK-EDDIES verdict hasn't arrived, so I'm holding the transfer study until it does.
