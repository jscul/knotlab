# What a knot on three additions predicts about the fourth

The three-distinction knot predicts how often the fourth binds to a pair from the three. Two older patterns can produce exactly the same visible knot and still allow different outcomes at the next addition. Both results concern the same growth rule after erasing the original knots at eight distinctions.

## What the fourth can do

The grower saw the current allowed states. The observer saw only the three additions since erasure and the new fourth. The census covers all 22,475 eleven-distinction contexts reached from the 13 starting classes at eight, counted separately by starting class. All the contexts admitted a fourth addition that kept the number of full allowed states at twelve. The result includes 917,768 literal fourth choices summed over the contexts. The rates below give the two original six-distinction starts equal weight and use each growth path's probability, conditional on the visible triple. [Design](preregistration.md)

| What the three allow | Reached contexts | Different sets of possible four-distinction outcomes | Different probability laws | Fourth forms a knot with at least one pair from the three | Three determine the fourth's value |
| --- | ---: | ---: | ---: | ---: | ---: |
| Six states, a knot | 14,309 | 6 | 371 | 98.17% | 3.63% |
| Eight states, free | 8,166 | 10 | 501 | 73.26% | 18.45% |

The last column asks whether every allowed assignment of the three values fixes a unique value of the fourth. A pair forming a knot with the fourth is a different property. The counts of sets and laws in the table also hold when the observer forgets which of the four came last. All comparisons allow renaming distinctions and swapping their values. [Exact results](../../artifacts/FOURTH-FROM-THREE-20261117-001/FOURTH-FROM-THREE-20261117-001-E001_prediction/results.json)

## Why identical knots can have different futures

Take two different eight-distinction starting classes. Each admits a history in which the same three new columns appear on the twelve rows, even counting repetitions of each visible assignment. In the first, zero of 38 legal fourth choices allow the three to determine the fourth. In the second, two of 40 choices do. The resulting six-row table can be recognized even after forgetting which distinction came last. For a matched pair of free triples, the corresponding difference is whether the four can obey a single parity law. It occurs in zero of 42 choices in one context and two of 42 in the other. Replaying the histories with the original constraint enumerator verifies every move. [Replayed examples](../../artifacts/FOURTH-FROM-THREE-20261117-001/FOURTH-FROM-THREE-20261117-001-E001_prediction/witnesses.json)

The knotted example has a short explanation. Swap values so the visible triple excludes 000 and 111. Its six assignments come in three complementary pairs. Since the rule preserves simultaneous reversal of all values, a fourth determined by the three has only four possible value patterns up to reversing its own values. Three copy a visible distinction. The remaining one takes the minority value of the three on each row. It can be forced by requiring each pair together with the fourth to avoid three equal values. The pair whose two values agree forces the fourth to take the opposite value.

The growth rule forbids copies of any existing distinction, including its reverse. The first older pattern has already used the minority pattern. The second leaves it available. That one yes-or-no fact settles whether a determined fourth is possible in every one of the 14,309 knotted contexts. This gives the rules-within-rules intuition a concrete instance under the supplied law. The visible knot identifies a candidate for a later rule, and the larger pattern decides whether it can be realized. Predicting the full next relation from the triple alone fails even at the level of possibility. [Independent census](../../artifacts/FOURTH-FROM-THREE-20261117-001/FOURTH-FROM-THREE-20261117-001-E001_prediction/checks.json)

## Reproduction

From the repository root, the primary enumeration, independent check and direct replays can be run as follows.

```bash
k=FOURTH-FROM-THREE-20261117-001
f="experiments/$k/${k}-E001_prediction"
.venv/bin/python -B "$f/measure.py" --output /tmp/fourth-from-three-results.json
python3 -B "$f/verify.py" --compare /tmp/fourth-from-three-results.json
.venv/bin/python -B "$f/witnesses.py" --results /tmp/fourth-from-three-results.json
```
