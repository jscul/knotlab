# Three new distinctions carry a small trace of the starting knots

After the knots were hidden at eight distinctions, the same anonymous rule added three more. An observer given only the allowed states of those three could identify the starting arrangement with **50.05258%** accuracy, with the two starts equally likely. This is an exact finite difference, equivalent to about five extra correct guesses per 10,000 observations over chance.

Both starts had the same twelve allowed states at six distinctions. In one start a single distinction belonged to all four original knots. In the other, each distinction was absent from at least one knot. Their different probabilities of reaching the same anonymous eight-distinction tables were established by the [earlier erasure test](../ERASE-SEPARATELY-20261117-001/erasure.md). The present experiment reuses those exact probabilities.

## What the new distinctions show

The only anonymous outcomes for the new triple were six allowed assignments or all eight. In the six-state outcome, one complementary pair of assignments is missing. All four assignments are possible on each pair of distinctions. This makes the six-state relation a ternary knot under K1–K3, even when an observer sees only the three additions. The test concerns the relation that remains after the eight old distinctions are hidden. Those eight were available to growth throughout.

| Growth rule | Six states when one distinction belonged to all four knots | Six states from the other start | Optimal recognition |
| --- | ---: | ---: | ---: |
| Fewest states with up to three signed knots | 61.60953% | 61.50438% | **50.05258%** |
| Choose three unused columns uniformly | 60.59853% | 60.53430% | **50.03211%** |

Either start can produce either outcome. Seeing six states favors the start in which all four original knots met at one distinction. Seeing eight favors the other. The six-state probabilities differ by 0.10516 percentage points under the knot rule. With equal priors the gain in guessing accuracy is half that difference.

The random comparison keeps the twelve inherited rows. It chooses among distinctions that are still available, excluding every old distinction and its complement. Different starts can leave different choices available. That alone gives about three extra correct guesses per 10,000. The knot rule gives about two more correct guesses per 10,000 than this comparison. The difference shows that a trace can be read from distinctions added after erasure. Its size gives little power to identify the starting knots from any single triple.

## How the readout was isolated

For each of the 13 anonymous eight-distinction input classes, we computed one conditional distribution on the possible triples. The start probabilities entered only when mixing those 13 distributions at the end. Growth had no access to the start, the erased knots or the ages of any distinctions. It used the [frozen rule and scoring procedure](preregistration.md). An evaluator tracked which three distinctions to project onto, then discarded the old distinctions, the order of the additions, the names of the two values at each distinction and the number of full rows realizing each projected assignment.

Each move uses one to three ternary constraints on two current distinctions and the fresh one. Each constraint forbids a complementary pair of assignments. Every old row must still extend, and the new distinction must be constrained and distinct from all old ones even under an independent exchange of values. The rule chooses uniformly among distinct extensions that have the fewest rows. At every reachable parent, a move with twelve resulting rows was available. Across the 13 inputs there were 963,984 literal three-step histories, counting each history within its own input class. Each history received the product of its step probabilities.

The resulting optimal recognition probabilities are exactly 126353290235602541/252441121454676000 under knot growth and 20253/40480 under uniform selection of unused columns. [Primary results](../../artifacts/FRESH-THREE-20261117-001/FRESH-THREE-20261117-001-E001_projection/results.json) · [Independent check and comparison](../../artifacts/FRESH-THREE-20261117-001/FRESH-THREE-20261117-001-E001_projection/checks.json)

## Checks and reproduction

The primary enumeration took 0.99 seconds on the research host. It kept the six complementary row pairs, tried each possible new column and required that up to three compatible constraints force it on all six pairs. A second program independently generated the literal extensions using the preceding study's rule, following all three additions for every cut class under a different coordinate order and value recoding. Every class's exact probabilities agreed. Both programs found total probability one and no stalls.

The verifier also exhausted all 256 labelled ternary relations. Among the complement-closed relations with full projections on every pair, four have six states and are equivalent by value renaming. One has eight states. The six-state representative passed K1–K3 in `knotlab check`. The eight-state relation fails K1 because it is unrestricted. For the uniform comparison, the verifier tried all 2,024 three-element choices from the 24 unused columns at each eight-distinction cut.

From the repository root, reproduce both calculations with these commands.

```bash
ticket=FRESH-THREE-20261117-001
family=experiments/$ticket/${ticket}-E001_projection
.venv/bin/python -B "$family/measure.py" --output /tmp/fresh-three-results.json
.venv/bin/python -B "$family/verify.py" /tmp/fresh-three-results.json
```
