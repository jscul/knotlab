# When a local reader's view settles, from the start alone

Epic `SETTLE-BOUND-20261126-001`, at the coordinator's go-ahead on the selected direction of
[`LOOK-ALIKE-20261126-001`](../LOOK-ALIKE-20261126-001/decision.md). A check by the thread, not a registered study;
computed; referee pending. The sections "The bound" and "Expected" were committed before the test runs below.

## Why

The look-alike study found that a local reader's view of a grown start (each kind of birth, read by its kind,
parents, fresh distinctions and places, counted per round) settles into polynomials in the round, and that the
settled views decide which starts look alike. Its frozen settling bound (round 12, or 14 with parents) missed seven
five-knot starts in which a block of ten live knots bursts through the binomial numbers until round 11. This study
puts a bound on the settling round that comes from the start itself.

## What it rests on

`REDUCE-BLOCKS-20261119-001` (refereed): the growth reads a start only through its live knots, their open counts and
the sets of them that share a neighbour, and after round 1 a knot's only neighbours are its parents. So a set of live
knots that share a neighbour, or the children of one knot, can all join one another: such a block of m knots makes
the binomial numbers of m in successive rounds and ends in one join of all m. A knot's children number its fresh
distinctions, so the children of a round-1 birth with f fresh distinctions are a block of f.

## The bound (frozen)

For a start X, let **M(X)** be the larger of: the largest number of live start knots that share a distinction with
one knot (Lemma R's live-neighbour sets), and the largest number of fresh distinctions that a birth of round 1
receives (round 1 is computed from the start, the one round the bound reads). Fitted on all 181 starts of a fixed
dimension of up to four knots (the look-alike study's phase 1), the settling round K satisfies

- **K ≤ M + 5** in the reading without parents (sig0), and
- **K ≤ M + 7** in the reading with them (sig1),

with equality reached in both. The bound is to hold for every start of a fixed dimension.

**The pair rule with this cut.** For two starts of one dimension, compute each one's view from its counts through
round M + 5 (sig0) or M + 7 (sig1), whichever reading, and its fitted polynomials after; the first round from which
the two agree up to the count, so computed, is to equal the observed one, for every pair whose cut leaves at least two
rounds read to check against.

## Expected (written before the test runs)

1. **Five knots** (all 3,157; their counts and settling rounds were seen in the look-alike study, and the seven late
   starts suggested the bound, so this is not a held-out test): the bound holds for every start of a dimension under
   not-all-equal, and the pair rule with the new cut predicts every pair, including the 6,993 that include one of the
   seven late starts.
2. **Six knots, held out** (a sample of 1,000 of the 82,656 census starts, Python's `random.Random(20261126)`, uniform
   over the census list, each start once up to its symmetries): the bound holds for every start of a dimension, and the
   pair rule with the new cut predicts every pair.
3. **The knot law swapped** (parity, the scaffold the look-alike study did not swap): on the five-knot starts and the
   six-knot sample, the same bound holds and the pair rule predicts every pair; where parity closes a growth that
   not-all-equal continues, the start leaves the population of that law.
4. **Rates** stay outside: no prediction.

**Stop.** A start of a dimension whose view settles later than M + 5 or M + 7, or a pair the rule with the new cut
misses, in either knot law; or none.
