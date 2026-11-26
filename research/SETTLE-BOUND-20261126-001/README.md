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

## What was found

Four runs, each to round 24 or 30,000 knots ([`bound.py`](bound.py)): all 3,157 five-knot starts and the 1,000 sampled
six-knot starts, each under not-all-equal and under parity ([`grown_g5_nae.jsonl.gz`](grown_g5_nae.jsonl.gz),
[`grown_g5_par.jsonl.gz`](grown_g5_par.jsonl.gz), [`grown_g6_nae.jsonl.gz`](grown_g6_nae.jsonl.gz),
[`grown_g6_par.jsonl.gz`](grown_g6_par.jsonl.gz); tallies in `test_*.json`). Settling is the look-alike study's
(degree at most D − 1, least round tried 3, the dimension from the completed run).

| run | starts of a dimension | settle within the bound | past it | pairs the rule with the bound as cut predicts / misses (sig0; sig1) |
|---|---|---|---|---|
| five knots, not-all-equal | 1,556 | 1,515 | 41 | 566,713 / 25,782; 566,585 / 25,910 |
| five knots, parity | 1,078 | 1,067 | 11 | 225,849 / 1,693; 225,848 / 1,694 |
| six knots (held out), not-all-equal | 387 | 381 | 6 | 28,909 / 606; 28,742 / 674 (99 too short to test) |
| six knots (held out), parity | 283 | 281 | 2 | 13,723 / 36; 13,630 / 36 (93 too short) |

**The bound fails.** The settling round exceeds M + 5 (and M + 7 with parents) in 41 five-knot starts and 6 of the
held-out six-knot starts under not-all-equal, by up to 2 and 3 rounds (the worst: M = 4, settling at 12 and 14). The
seven five-knot starts that broke the look-alike study's bound are within this one (M = 10, settling at 14 and 16):
what breaks it now are starts with small blocks (M of 3 or 4).

**What the late starts do.** In 30 of the 41 five-knot misses and 4 of the 6 six-knot ones, the counts rise, then fall
to a single birth a round, and the growth then goes on as a lone knot does (1, 1, 2, 3, …); the view settles a few
rounds after that narrowing, and the narrowing can come late although no block is large (for example 8, 9, 8, 8, 7, 4,
1, 1, 2, 3, … from five knots with M = 3). The other misses settle late without narrowing to one. Neither the
largest block nor the round of the last fall in the counts bounds the settling round tightly (the settling round
lies 1 to 12 rounds after the last fall).

**The pair rule.** With each start's bound as its cut, every pair that the rule misses, in all four runs, includes a
start that settles past its bound (51,692 of 51,692 pair-reading misses at five knots under not-all-equal, 1,280 of
1,280 at six). Where both views settle by the cut, the rule predicts every pair.

**Parity.** Under parity fewer starts are of a dimension (1,078 of the five-knot starts, against 1,556): parity can
close a growth with a birth that takes every loose distinction, and the lone knot's tail closes. The seven bursting
five-knot starts close at round 12 under parity, and so do the 30 five-knot misses that narrow to one; the 11
five-knot misses under parity are the 11 that settle late without narrowing (2 at six knots).

## Expectations, and how they fared

1. *Five knots: the bound holds.* **Failed** (41 starts; 11 under parity).
2. *Six knots, held out: the bound holds.* **Failed** (6 of 387; 2 of 283 under parity).
3. *Parity: the same.* **Failed** likewise; fewer starts are of a dimension under parity.
4. *Rates:* no prediction.

The stop is met at the first miss: a start of a dimension whose view settles past M + 5. The largest block is not
what delays settling in these starts; a narrowing of the whole growth to one knot is, in most of them.

**Link (intuition-links), offered and not checked.** The narrowing is the literature's coarsening or giant merge seen
in the growth's own counts (the record's MERGE-BURST already followed one start into a single block of 781 knots): the
parts of a growth join until one join holds everything, and the growth then starts over from that one knot. What a
local reader sees settles only after that, so the settling round would be bounded by the round of the last merge, which
is a property of the start's whole meeting pattern, not of its largest block. Cheapest test: compute, from the map of
joins, the round at which every live member lies in one cluster, and compare with the settling round on the 41.
