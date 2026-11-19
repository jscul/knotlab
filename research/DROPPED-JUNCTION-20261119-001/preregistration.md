# Parity's eddies over the dropped junction: pre-registration

Epic `DROPPED-JUNCTION-20261119-001` (the coordinator's go-ahead on `STATES-GROWTH-20261119-001#3`; goals G1 and G17),
2026-11-19. Written after a pilot (disclosed) and the advisor's answer, before the frozen run. The canonical K1–K3 test is unchanged.

## The question

Under parity, the states fix only the completed system G*: the presentation, plus the implied junction "out" holding every loose
distinction. So any point of G* can be the dropped one. Grow every choice, and stop at the set of rates.

The states-only candidate rule is to drop the point of largest degree. As the advisor notes, that is the same as taking the
presentation with the fewest places, since a presentation that drops v has 2L − deg(v) places.

## Pilot (disclosed)

| Ring | Original choice (drop out) | Every other choice |
| --- | --- | --- |
| Ring of five with one spare | 1.1347 | 2 a round, or closes (5, 3, 3, 1) |
| Five five-place knots | the golden ratio | closes |
| Bare ring | 5 a round | 2 a round |

In all three the original is the unique point of largest degree. The advisor reads the pattern locally. The dropped knot's lines
become the only loose ones: one on each ring neighbour and the rest on out. Two or three loose lines on the hub then give 2 a round
or a closing.

## Classes

From 30 rounds or 60,000 junctions, by LOOP-CATALOGUE's rule (`job_iso.classify`):
- closed or stall;
- dimension k, when the k-th differences at some lag of at most 12 vanish on the last 16 rounds;
- exponential, when the count is not quasi-polynomial and still rising, or passes the junction cap rising by 10% a round.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| D1 | on every eddy (the catalogue's five, the census's 13 rings, rings of 9 to 13 with a spare), the original choice is the only exponential one | any other choice is exponential, or the original is not |
| D2 | on each of them, the original is the unique point of largest degree. The advisor notes this is forced by counting on rings, so it is a check, not a test | one is not |
| D3 | (risky, the test of the rule) on 300 random growing five-knot census starts, where the original is not the unique point of largest degree, dropping the unique largest point gives a different growth class in at least one start, so the largest-point rule is not the cheapest growth | none differs |

Readouts: how often the original is the unique largest point among the 300; how often any other choice changes the class.

## Prior work in the program

`python3 -B scripts/track.py objects "parity completed system dropped junction cycle matroid Whitney eddy" --until 2026-11-19 --exclude DROPPED-JUNCTION-20261119-001`

- `STATES-GROWTH-20261119-001`: the completed system and Whitney's theorem, the same object.
- `LOOP-CATALOGUE-20261119-001`: the eddies.
- `BOND-METRIC-20261118-001` (bond distance on parity bases), `UNIQUE-TABLE-20261119-001` and `JUNCTION-MAP-20261119-001`: related
  objects, the same words.

## Runs and stop rule

`job.py` through the shared runner (33 cases); `merge.py` scores.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md);
`modelUsage` names claude-fable-5-2), before the freeze. The answer stayed within its text.
- **The rule's restatement.** "Fewest places" is the same rule as "drop the largest point". When G* is three-connected its points
  are the non-separating cocircuits of the cycle matroid (Tutte), which are states-only.
- **D2.** It is forced on rings, so it is kept only as a check.
- **D3.** The real test needs starts where a knot ties with out or beats it. They are among the 300, and D3 is stratified on them.
- **Its local conjecture.** The class after a drop depends only on the dropped knot's lines; recorded as a direction.
