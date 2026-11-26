# The origin of class facts under ordinary parity growth

On every finite stage reached by a funded complete round of ordinary even-parity growth, every class fact given by a parity has a representative on the starting distinctions. This holds for both readings of a small change in the study. The proof needs a four-distinction change to be shortest through at least one of its distinctions. On a thirteen-knot start, a displayed change has least sizes 2, 4, 4 and 2 through its four respective distinctions.

## The three premises

1. Each proposed group takes one loose distinction per parent. Each remaining loose distinction goes to a unary birth. Funding therefore uses every loose distinction exactly once, with distinct parents within each birth.
2. Two live knots sharing a neighbour form a candidate pair. Every candidate pair belongs to a chosen larger group or is taken as a pair by the group rule. On a funded round its joint birth exists. The witness here is a knot of the presentation.
3. A birth receives zero fresh distinctions only when its input parity follows from the older laws. In a sum of older laws giving only loose distinctions, the coefficients at the two holders of every shared distinction agree. They are constant on each connected part. Consequently such a sum is the union of all loose distinctions of the selected parts. A birth's parents are in one part and its inputs are nonempty. Its input parity is implied exactly when it takes all of that part's loose distinctions. Premise 1 then makes it the sole birth there, and each parent had one loose distinction. Its subsequent demand is zero, since it has no sibling there. [Ordinary group and grant rules](../../ORDINARY-DYNAMICS-20261120-001/end_operator.md) · [Earlier component criterion for an implied parity](../../ERASURE-AND-CLOSING-SIGNS-20261121-001B/closing_law.md)

## Removing the oldest changed birth

Over the two-element field, an allowed change uses an even number of distinctions at every knot. Join the loose distinctions in the calculation to one bookkeeping holder, U. Evenness there already follows by adding all the knot laws. Ignore all starting distinctions and retain only changes fixing them. Every remaining shared distinction was born at one knot and taken by a child exactly one round later. Every remaining loose distinction belongs to the newest round. An older closed part can have ceased growing earlier.

Take any such change, and in its earliest round take a birth *w* that it meets. If *w* is older than the newest round, the change uses an even number of distinctions there, all going to children. Pair them in any order. Each pair goes to two distinct children by premise 1. Each child received a fresh distinction. Indeed, a zero-fresh child would have been its part's only birth by premise 3. If the children are newest, take one loose distinction at each, completing a four-distinction change through U. Otherwise their common parent *w* gives them a common child by premise 2, completing a four-distinction change through that child. Adding the change cancels the pair at *w* and introduces nothing in its round or earlier. Repeat until only newest births remain. At each of these the remaining even set of loose distinctions splits into pairs. This also covers a closed part with no loose distinctions.

The generators must qualify in the **full** stage to be small changes there. Each pair has size two and a single distinction changes some knot's parity. For a four-distinction generator, take its lower distinction from *w* in round *s* to its child *v* in round *s* + 1, where *s* ≥ 1. Premise 1 excludes a second distinction with the same holders. No third ordinary holder can meet both *w* and *v*. Their possible neighbouring rounds are respectively {*s* − 1, *s* + 1} and {*s*, *s* + 2}, and U meets only newest knots. A starting holder cannot meet *v*, which is in round two or later. Thus no change of at most three distinctions contains the lower distinction. The generator of size four is a least change through it. All ties enter the shortest-change reading. Both sizes also qualify under the up-to-five reading.

## What the representatives say

The fixed-start changes therefore lie in the span of small changes. Two allowed states with the same starting values differ by a fixed-start change. Adding its small generators one at a time stays in the allowed states by even parity. Both states give the same value for every class fact. Every allowed starting state extends at every ordinary round. Each positive-grant birth has a private fresh distinction that can satisfy its parity for any inputs, and the zero-grant equations follow from the old laws.

For a parity *f*, the induced function on the allowed starting states is linear. Extend it to a linear form *g* on all starting distinctions. Then *f* + *g* vanishes on every grown allowed state and is a sum of grown knot laws. Two such representatives *g* and *g′* agree on every allowed starting state because each one extends. Hence *g* + *g′* is a sum of start laws. Being invariant under the starting small changes and being readable by one starting knot are properties of the function, independent of its representative. Support, size and disjointness can depend on the representative. Any parity equation among the grown parities gives a sum of start laws on their representatives. The factorization as a function applies to all class facts. The linear-sum statement applies to parities.

## Independent checks

The replay rebuilt funding, implication and group demand from the definitions. At each stage binary elimination on all knot laws restricted to fresh distinctions gave the dimension of fixed-start changes. A second calculation enumerated every pair and every four-distinction cycle visiting four different holders, counting U as one holder. It retained just the pairs and the four-changes with the round pattern in the proof for the reported rank. For each fresh distinction, deleting it in the full stage and finding a shortest return gave its least change size, including any route through the starting knots. The six archived ranks agreed. The first 19 archived births of the three-knot example matched by round, parent count, fresh count and implication. The selections below are individual constructions. [Code](argument.py) · [Stage-by-stage results and witnesses](argument.json)

| Ordinary start | Last tested round | Distinctions then | Fixed-start dimension | Rank of the proof's changes |
| --- | ---: | ---: | ---: | ---: |
| Thirteen knots in a ring, two loose distinctions apiece | 24 | 663 | 312 | 312 |
| Sixty-one knots in a ring, two loose distinctions apiece | 8 | 1,159 | 488 | 488 |
| Three knots, each pair sharing two distinctions, two loose apiece | 12 | 1,176 | 764 | 764 |
| One three-place starting knot, which closes in round three | 3 | 12 | 3 | 3 |

All three premises and the rank equality held at every one of the 47 reached stages, covering 1,207 births. At round two of the thirteen-knot ring, the change on distinctions 65, 39, 40 and 67 has least full-stage sizes 2, 4, 4 and 2 in that order. All 52 four-changes from the proof on this stage admit a shorter change through some member. In the study note, replace “each of which is a shortest change through its distinctions” with “each of which is a shortest change through at least one of its distinctions”. This clarification preserves the proof. [Study wording](../README.md#the-argument-the-advisors-sketch-to-be-tested) · [Exact witness](argument.json)

To test the role of common-neighbour coverage, take the same single three-place starting knot, grow its ordinary first round, then give each loose distinction its own unary birth with two fresh distinctions throughout. At round three all old states still extend. The dimension fixing the start is 21 and the pairs and four-changes have rank 18. Distinction 3, fresh in the first round, has least change size six. It is a class fact under changes of at most five, although changing distinctions 3, 9, 21, 25, 11 and 4 flips it with every starting value fixed. This change of rule gives an example in which the conclusion about up-to-five changes genuinely fails. [Changed-rule witness](argument.json)

The argument concerns finite complete stages, free loose distinctions, even parity and the two specified move families. No census of all larger starts, infinite-stage limit or other law was run here.

From the repository root, each command uses one process capped at two GiB. The two-round pilot includes the complete three-round changed-rule control.

```sh
.venv/bin/python -B research/BUILT-BINDING-20261126-001/referee-R1/argument.py --pilot
.venv/bin/python -B research/BUILT-BINDING-20261126-001/referee-R1/argument.py
```
