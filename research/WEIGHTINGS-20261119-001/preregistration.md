# Pre-registration: is two dimensions typical of the growth or of the weighting?

Epic `WEIGHTINGS-20261119-001`, ticket `WEIGHTINGS-20261119-001B`, 19 November 2026, by Claude, on the coordinator's go-ahead.
Goal G17. It challenges `A106` (the weighting of first-knot arrangements), under the owner's standing rule that every random
process is a weighting and the question is what is typical under each.

## The question

The identification line proved that, in its class, the cheapest parity growth is the clusters of the relayed extended map of joins.
The class is (S0) no stall, (S3) no round-1 group of three, (S4) no two live knots with two common neighbours, and (S6′) at least
two loose distinctions. A start with at most one loose distinction closes at round 1, which is DOUBLE-IDENT's edge case.

The growth class is read off the map piece by piece:
- a finished piece closes if it is alone, and relays (dimension 2) otherwise;
- a tree core with R chains has dimension R;
- a bare single cycle has dimension 1;
- any other cycle grows exponentially.

Under SCALE-SHARE's weighting, two dimensions take over inside the class and three never occurs (`SCALE-THEOREM-20261119-001`). In
the theorem's terms, a chain needs a knot with open places left after its joins, and that weighting leaves few. The question is
whether "two is typical" belongs to the growth or to that weighting. The theorem reads the starts; nothing is grown except the
regrowth check.

## The weightings (frozen before any sample was classified)

Each draws a connected start of n knots. Every shared distinction lies in exactly two knots.
- **tree.** A uniform random labelled tree (Prüfer code), every knot at its bare size max(3, shared + round-1 demand), with no
  surplus. Bare sizes never stall. This is the weighting where stalls do not dominate.
- **tree-s25, tree-s50, tree-s100.** The same tree, with each knot given one surplus open distinction independently with
  probability 25%, 50% or 100%. This is one knob running from the bare tree towards crowded open places (the advisor's suggestion).
- **tree+.** The same bare tree plus r extra lines between uniformly chosen non-adjacent pairs, with r Poisson of mean 1, at bare
  sizes. It adds cycles of every length.
- **grow.** Knots are added one at a time (A106's "a growth process that adds knots one at a time").
  - Each knot has k places, k uniform in {3, 4, 5}.
  - Each new knot shares one distinction with an existing knot chosen in proportion to its open places. With probability 1/3 it
    shares one more with a second existing knot, chosen the same way, if both have an open place left.
  - Places are fixed, so stalls can occur. If no existing knot has an open place, the start is redrawn.
- **config.** A configuration model (A106's "random pairing of places"; the advisor's suggestion).
  - Each knot has k places, k uniform in {3, 4, 5}.
  - The places are joined by a uniformly random partial matching, so every partial matching is equally likely and the number of
    lines is weighted by its count of matchings.
  - The draw is conditioned on no line joining two places of one knot, and on a connected start.
  - It weights a description by its place labellings, where SCALE-SHARE counted each description once.

## Population and method

- **Sizes.** n = 5, 6, 7, 8, 10, 12, 16, 20, as SCALE-SHARE.
- **Samples.** 2,000 independent samples per weighting and size, seeded by the case id: 7 × 8 × 2,000 = 112,000 in all.
- **The reader.** SCALE-THEOREM's: DOUBLE-IDENT's `machine_check.classify` and `dims.predict`, loaded by path, unchanged.
  - Each sample gets its fine class: stall; out by (S3) or by (S4); none; one loose; or in.
  - Outside stalls and "out", it gets its growth class, and for dimension 2 its mechanism: two chains, relay, or both.
- **The regrowth.** At n = 8, 12 and 20, per weighting, the growth is regrown for every in-class sample predicted three-or-more or
  exponential (up to 50) and for the first 30 other in-class growers. Each is compared round by round to round 6 with the relayed
  cover (DOUBLE-IDENT's model), in each junction's parents and fresh count. This follows the advisor's trap: a random 30 would miss
  the rare classes.
- **Recorded too.**
  - The largest knot (bare trees can exceed five places).
  - The numbers of lines and of knot pairs.
  - For tree, the leaves beside a knot of degree 2.
  - For tree+, the number of extra lines.
- **The run.** Through the shared runner (`runs/weightings`).

## Smoke tests (disclosed)

- Three samples per weighting at n = 5 and 20 were drawn and classified, to check that the code runs. The output was not read
  beyond success.
- Four cases at 60 samples each, and every case at 15 samples, ran through `job.run` and `merge.main` with seeds different from the
  run's ("-smoke"). Only timings and the absence of errors were read.

## The trees, in the theorem's terms (derived before the freeze)

On a bare tree, (S0), (S3), (S4) and (S6′) hold automatically.
- Bare sizes never stall.
- A tree has no two knots with two common neighbours.
- Three knots pairwise two apart in a tree have one common neighbour, so no valid set of three exists.
- Every leaf keeps at least two open distinctions.

A leaf beside a knot of degree 2 keeps one pendant point with one ray. No other knot of a bare tree has a pendant point. The map of
joins has one piece per parity class of the tree that holds a live knot. Only a star's centre is dead (all its neighbours are
leaves), so a star has one piece, with no ray, and closes.

So, outside stars, the dimension is the larger, over the two parity classes, of the number of ray-leaves in it, where a class with
none counts 2 by relay. Dimension three or more needs three ray-leaves in one parity class. At n = 7, the only tree that has them is the three-armed
spider with arms of two: 7 · 120 = 840 of 7^5 = 16,807 labelled trees. This is the advisor's count, checked here.

## Predictions (frozen; scored by `merge.py`)

"Three-plus" is dimension three or more. "In-class growers" are the in-class samples that do not close.

| # | Prediction | Falsified by |
| --- | --- | --- |
| W1 | (the advisor's, exact in expectation) tree, three-plus count of 2,000: 0 at n = 5 and 6; 70 to 130 at n = 7 (expected 99.95 = 2,000 · 840/16,807); 31 to 73 at n = 8 (expected 51.3 = 2,000 · 6,720/262,144); and more at 7 than at 8 | any of these failing |
| W2 | (the advisor's; sampler check) tree, the mean number of leaves beside a knot of degree 2 is within 5% of (n−1)(1−2/n)^(n−3) at every size | a size outside |
| W3 | (derived) tree, tree-s25, tree-s50 and tree-s100: every sample is in the class | one sample outside |
| W4 | (derived) the same four: no sample grows exponentially | one that does |
| W5 | (risky; the advisor's, low confidence) tree, three-plus is more than 10% of all samples at n = 16 and more than 20% at n = 20 | either failing |
| W6 | (the advisor's) tree+, exponential is at least 10% of in-class growers at every n ≥ 8; and the samples with no extra line are all in the class with no exponential growth | either failing |
| W7 | (the advisor's) grow, exponential is more than half of in-class growers at every n ≥ 10 with at least 20 of them; three-plus is under 2% of in-class growers at every size | either failing |
| W8 | (mine) at n = 20, the three-plus share of all samples does not rise with surplus: tree ≥ tree-s25 ≥ tree-s50 ≥ tree-s100 | an inversion |
| W9 | (mine, uncertain) config behaves like SCALE-SHARE: stalls above 40% at every size; at every size with at least 20 in-class growers, dimension 2 is at least 70% and three-plus under 2% of them | any failing |
| W10 | (the theorem; the stop rule) every regrown sample agrees round by round to round 6 | one that differs |
| W11 | (sampler check) grow, the share with a cycle-free knot graph is at least (2/3)^(n−1) minus three standard errors at every size (a second line can fail to form, never form unasked) | a size below |

## What counts as common, and what would follow

**Common** is fixed now. Three-plus, or exponential growth, is common in the class at a weighting and size when it is at least 10%
of that weighting's in-class growers, with at least 20 in-class growers at that size.

- **Common under some weighting.** "Two is typical" then belongs to the weighting, not the growth, and is narrowed to the
  weightings where it holds. The report names them and says so plainly.
  - If the bare tree makes three-plus common, the cause is the open places a bare tree leaves at its leaves. That is the theorem's
    mechanism: a chain needs a knot with open places left after its joins.
  - If tree+ or grow make exponential growth common, the cause is cycles inside the class.
- **Common under none.** "Two is typical" is then robust across these seven weightings, at least for starts in the class, and the
  report says so.
- **W10 failing** stops the study at that weighting and size. The theorem would then be wrong there, which is a correction.

**Readouts** (no prediction):
- per weighting and size, the share of all samples in each fine class, with the ejection reasons ((S3) or (S4));
- the in-class growth classes as shares of all samples and of in-class growers;
- the dimension-2 mechanism (two chains, relay, both), so that a two from a relay is not read as SCALE-SHARE's two;
- the shares restricted to starts whose knots have at most five places;
- tree+ split by its number of extra lines.

## Prior work in the program

`python3 -B scripts/track.py objects "weighting random starts trees surplus configuration model growth dimension typical proved class" --until 2026-11-19 --exclude WEIGHTINGS-20261119-001`

- `SCALE-THEOREM-20261119-001` and `SCALE-SHARE-20261119-001`: SCALE-SHARE's weighting, the object compared with.
- `CHAIN-IDENT-20261119-001`: on bare trees, rays come from leaves whose neighbour has degree 2 (the derivation above).
- `RELAY-IDENT-20261119-001`: the dimension rule on trees, with a finished piece counting two.
- `TOUCH-CENSUS-20261118-001`: "two typical, three and four rare", which rests on `A106`.

## Advisor

`claude -p --model claude-fable-5-2 --tools ""` ([question](advisor/question_1.md), [answer](advisor/answer_1_fable.md)), before the
freeze, on which weightings are honest contrasts.
- **It found none of the original three clean.**
  - tree favours two at these sizes, because the ray-leaf mean is only 1.4 to 3.2.
  - tree+'s exponential share is set by its Poisson parameter, and (S4) ejects its cycles of four.
  - grow is dominated by cycles.
- **Adopted from it.**
  - tree-sP and config.
  - Shares of all samples next to in-class shares, with ejection reasons.
  - The two sources of "two", tabulated separately.
  - The stratified regrowth.
  - The largest knot recorded.
  - Its predictions W1, W2, W5, W6 and W7.
- **Checked here.** Its reading of the tree rule ("each parity class is a piece with dimension equal to its ray count, or 2 by relay")
  was checked against CHAIN-IDENT's proof, and its count of 840 against the spider.
