# What the states remember after the knots are hidden

The two starts had the same twelve allowed states at six distinctions. In one start, a single distinction belonged to all four knots. In the other, each distinction was absent from at least one knot. The rule could read those knots until the step that brought the count to seven or to eight. From that point on, growth and observation had access only to the current allowed states.

With the two values of every distinction independently renamable after erasure, the timing changed what survived. Hiding the knots at seven left both starts equally likely under every later observation. Keeping them for one more step left enough information for an observer to identify the start on 65.84% of trials at nine and 61.28% at ten. The percentages describe exact probabilities, with both starts equally likely.

| Erasure | Recognition at erasure | At nine distinctions | At ten distinctions |
| --- | ---: | ---: | ---: |
| Seven, independent value names | 1/2 | 1/2 | 1/2 |
| Eight, independent value names | 26/35 | 613/931 | 55292726989/90222390720 |
| Seven, shared binary values | 7/8 | 106108757/154492800 | 33894403534703/51985282272000 |

The shared-value seven-cut scores at nine and ten are 68.68% and 65.20%. Claude's KNOT-CAP K4 separately registered erasure at eight with shared binary values. Its scope and this calculation are recorded in the [plan](preregistration.md).

## What carries the difference

At seven, the two starts give the same two fully anonymous tables, each with probability one half. A rule that sees only the table has the same input law from either start. Applying that rule, even with fresh random choices, preserves equality at every later step.

At eight, while the knots are still visible to the preceding growth, the two starts produce different probabilities for the anonymous tables. The two distributions together occupy 13 classes at the cut, 85 at nine and 445 at ten. All the outcomes we enumerated have exactly twelve allowed rows. A reader can still tell the starts apart using just the counts of how often two rows disagree on one distinction, two distinctions, and so on. This simpler reader succeeds 60.32% of the time at nine and 54.19% at ten. Even a statistic that forgets which particular rows or distinctions disagreed carries some information.

The eight-cut finding is statistical. At ten, 326 of the 445 table classes can arise from either start. Weighting by their actual probabilities, about 4.78% of outcomes rule out the other start altogether. The optimal reader also uses the different probabilities within the shared classes. The result establishes transmission through two more additions under the specified rule.

## What the rule can read

Each cut uses the same two starts and the same preceding growth. Each step before erasure gives equal weight to each distinct, irredundant, cheapest set of up to three locally attached knots. There are four first moves per start. The four branches have five, five, seven and seven second choices. A two-step history therefore inherits its branch probability.

After erasure the rule reads only a relation on the current distinctions. It forms conservative extensions by up to three ternary knots, keeps the extensions having the fewest allowed rows and gives every distinct such extension equal weight. No old row can disappear. The new distinction must be constrained and distinct from every existing one. Once the step is taken, every distinction can be renamed, including the one just added. No marks record the first six, the cutoff, or the most recent addition.

In the shared-value comparison the rule uses the three ordinary betweennesses. For the fully anonymous comparison it admits every independent exchange of the values of those knots. This gives four ternary constraints, each forbidding a complementary pair of assignments. An old distinction and its complement both count as copies for this rule. Renaming the old or fresh values bijects the legal extensions, preserves their cost, and preserves every transition probability. This is one explicit anonymous continuation. Other anonymous rules can have different eight-cut rates. Every such rule preserves the seven-cut equality.

## Reproduction and validation

The computation followed the [frozen exploratory contract](../../experiments/ERASE-SEPARATELY-20261117-001/ERASE-SEPARATELY-20261117-001-E001_erasure/contract.json). All transition probabilities use exact fractions. Every enumerated layer has probability one from each start, with zero stalls. The earlier code and all four cut scores were checked before reading the endpoints. The full enumeration took 13.27 seconds on the research host.

A separate verifier recomputed the scores from the [saved state tables and probabilities](../../artifacts/ERASE-SEPARATELY-20261117-001/ERASE-SEPARATELY-20261117-001-E001_erasure/results.json). It tested class uniqueness by permuting the complementary pairs of rows and comparing their column multisets. To check the signed transitions by another method, it tried every possible new column on each of the six complementary row pairs. It accepted a column when at most three compatible knots could force it on all twelve rows. This found 546 minimizing extensions across the 13 eight-distinction input classes and 3,536 across the 85 nine-distinction input classes. The resulting histogram distributions agreed exactly at both endpoints. All four allowed forms of a single knot also passed K1–K3 in `knotlab check`. [Verification results](../../artifacts/ERASE-SEPARATELY-20261117-001/ERASE-SEPARATELY-20261117-001-E001_erasure/checks.json)

From the repository root, these commands rerun the enumeration and its independent checks.

```bash
ticket=ERASE-SEPARATELY-20261117-001
family=experiments/$ticket/${ticket}-E001_erasure
.venv/bin/python -B "$family/enumerate_erasure.py" --output /tmp/erase-separately-results.json
python3 -B "$family/check_scores.py" /tmp/erase-separately-results.json
```
