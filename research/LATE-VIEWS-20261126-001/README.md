# The late views of a growth from its start alone

Epic `LATE-VIEWS-20261126-001`, at the coordinator's go-ahead on the selected direction of
[`LAST-MERGE-20261126-001`](../LAST-MERGE-20261126-001/decision.md). A check by the thread, not a registered study;
computed. The sections down to "Frozen" were committed, after the advisor's review before the freeze
([question](advisor_question_freeze.md), [answer](advisor_answer_freeze.md)), before any grown file of the held-out
sets below was opened; the sets were grown meanwhile.

## Where it starts

The look-alike study found that a local reader's view of a grown start (each kind of birth, read by its number of
parents and fresh distinctions, `sig0`, or with its parents' kinds as well, `sig1`, counted per round) becomes polynomial
in the round, and that these views decide which starts look alike; the last-fall study found that a late start's view
settles three rounds after the last fall in births. Both read the view off the grown counts. This study reads it off the
start.

**Exploration (not a test).** Neither the late constant counts nor the slope is a function of the number of leftover
distinctions after round 1 (starts with two leftovers show (offshoots, slope) = (2, 1) in 211 cases and (4, 2) in 26).

## What it rests on

- **The identification** (`RING-IDENT`, `CHAIN-IDENT`, `RELAY-IDENT`, `DOUBLE-IDENT`, all proved and refereed): in a class of
  starts, the births of round t are the connected sets of t + 1 points of an extended map X⁺ (the live knots; s = open − d
  pendant points per live knot, d its number of round-1 groups; 0, 1 or 2 endless chains on each pendant point as open is
  at least 3, 2 or 1; a block N(w) ∩ live for every knot w), a birth's parents are its points whose removal leaves it
  connected and holding a knot, and its fresh distinctions are its outside neighbours. A piece with no chain relays under
  not-all-equal (`NAE-GROWTH-20261118-001`): the set of all its points takes one fresh distinction and a point with two
  chains hangs from it; under parity it closes when it is the start's only piece.
- **Lemma R** (`REDUCE-BLOCKS-20261119-001`, proved): the growth reads only the down-closure of the blocks.
- **Round 1** read from the start alone: the groups are the maximal cliques of three or more knots of the candidate graph
  (two live knots are candidates when some knot is a neighbour of both) that no block holds, and the candidate pairs inside
  none of them (`WALL-READ-20261119-001A`'s roster rule). Computed in [`late.py`](late.py) without the engine, it equals
  the engine's groups on every census start of one to six knots (86,036).

## The predictor ([`late.py`](late.py))

The finite part of each piece (its live knots and pendant points: its core) is listed once. A connected set of the
extended map is a connected set C of the core holding a knot, a set E of the chains leaving C, and a length of at least
one along each chain in E. Its kind depends only on (C, E), and in the reading with parents also on which chains have
length exactly one, so the number of round-t births of each kind is a finite sum of binomial coefficients in t. Nothing is
grown.

Two readings go past the proved class; both were found by exploring the census of up to four knots:
1. **Repeated blocks.** Blocks are read as their distinct maximal sets (Lemma R). This takes in starts with two live knots
   that have two common neighbours.
2. **Group cells.** Each round-1 group of g ≥ 3 live knots is a cell: a set is valid when it holds one knot of the cell or
   none, or all of it; its size is its number of points less g − 2 for each whole cell (a group is born in round 1); its
   parents are its valid subsets of size one less (one point removed, or a whole cell cut to one of its knots); its fresh
   distinctions are its ways to grow by one (an outside point, the rest of a cell it meets once, one step along a chain).
   Blocks inside a cell are dropped, and a block meeting a cell in m ≥ 2 knots is read as m − 1 filled cycles.

Any other cycle puts the piece outside the predictor (a ring: reported as not predicted, not as a miss).

**The settling round from the start.** Each kind's count is a sum of binomial coefficients, and its polynomial part
continues them below the sizes at which they start, so the count equals its polynomial from the round after its last
departure. The predicted settling round K is the least K ≥ max(D, 3) with every count equal to its polynomial part from
round K − D + 1 on, D being the largest number of chains a set takes (the look-alike study's settling definition, applied
to the predicted counts). In the advisor's words, it is set per kind by the largest set of that kind; the literature's
fact behind it is that a rational series with denominator a power of 1 − x is polynomial past the degree of its
numerator (Stanley, *Enumerative Combinatorics* I, section 4.3).

**Known mathematics.** Counting connected subsets of a finite graph by size is the literature's enumeration of animals
or connected induced subgraphs (for subtrees of trees, Székely and Wang, *Advances in Applied Mathematics* 34, 2005); the
binomial is the count of compositions of the chains' lengths. What this adds: the growth's births are those sets once the
blocks are reduced and each round-1 group is read as one cell, so a local reader's view is a finite sum over the start's
core.

## Seen before the freeze (the fitting data)

Every round to 24, both readings, every census start up to its symmetries ([`fitting/`](fitting), from `late.py check`):

| starts | knot law | accepted | agree in every round | settling round as predicted | not accepted |
|---|---|---|---|---|---|
| 1 to 4 knots | not-all-equal | 181 of a dimension | 181 | 181 of 181 (both readings) | 42 stall |
| 5 knots | not-all-equal | 1,554 (1,547 of a dimension, 7 unread) | 1,554 | 1,547 of 1,547 | 1,587 stall; 16 a piece with a cycle |
| 5 knots | parity | 1,547 (463 closing) | 1,547 | 1,077 of 1,077 | 1,587 stall; 16 a piece with a cycle; 7 one loose |

At five knots under not-all-equal the accepted starts are 210 in the proved class, 351 with repeated blocks only, 783
with group cells, 203 with a block meeting a group cell in two knots, and 7 with one loose distinction. So 1,344 of the
1,554 agreements rest on a reading the proved theorems do not cover.

**Negative controls (five knots, not-all-equal).** With the relay removed, 698 starts differ; with the group cells
removed, 986 differ (every start of dimension three or four has a cell); the not-all-equal predictor applied to the parity
growths fails on all 470 that close. The predictor can fail.

**The six-knot census by structure alone** ([`strata_census6.json`](strata_census6.json), [`strata.py`](strata.py)):
of 82,656 starts, 50,845 stall in round 1 by their demand, 1,473 have a piece with a cycle, and 30,338 are accepted
(95.4% of those that do not stall): 2,053 in the proved class, 4,264 with repeated blocks only, 20,232 with group cells,
3,733 with a block meeting a group cell, 56 with one loose distinction. Rare strata: two group cells sharing no knot (92),
group cells sharing a knot (42); none has two cells sharing two knots.

## Frozen

**The held-out sets**, each grown to round 24 under not-all-equal and under parity with the look-alike study's growth,
unchanged (scaffolds: register entry A286):
1. **Uniform.** 2,000 six-knot census starts, `random.Random(20261128).sample` over the census outside the 3,000 sampled
   before ([`sample.py`](sample.py)).
2. **Stratified.** 199 six-knot starts, up to 40 in each of five rare strata, `random.Random(20261130)`, outside all
   5,000 ([`stratified.jsonl`](stratified.jsonl)).
3. **Built by hand.** 17 starts outside the census with group cells of four to seven knots ([`handbuilt.py`](handbuilt.py)).
4. **A second weighting.** 1,000 seven-knot starts of the 'grow' weighting of `WEIGHTINGS-20261119-001B`,
   `random.Random(20261129)` ([`sample_grow.py`](sample_grow.py)).
5. **A longer horizon.** 100 starts of the uniform set accepted with predicted dimension at most two,
   `random.Random(20261131)`, grown to round 40 under not-all-equal ([`horizon.jsonl`](horizon.jsonl)).

**Pre-registered.** Every prediction, made from the starts alone, is in [`predictions.jsonl.gz`](predictions.jsonl.gz)
([`predict_all.py`](predict_all.py)); the sha256 of its uncompressed content is
`d6aefb73dc32220c61166efc94e568c0a6906f48a7ccf7eb508d72c1ab3f699d`. Accepted: 706 of the uniform set under each law,
all 199 stratified, 16 of 17 built by hand, 70 of the seven-knot set, all 100 for the horizon.

**Predictions.**
- **P1.** Every accepted start agrees with its grown view in every round read, in both readings, under both laws.
  Reported in two parts: starts in the proved class (a check of the code: the theorems predict them) and starts that need
  a new reading (the test of the two readings).
- **P2.** For every accepted start of a dimension, the grown dimension equals the predicted one, and the settling round
  equals the predicted K in each reading whenever K is at most the last round read less two. P2 follows from P1 except
  where a fit through the rounds read coincides with the counts and fails later; it is reported, not counted as a second
  test.
- **P3.** On the horizon set, P1 holds through round 40.
- **P4.** Each of the three negative controls fails on some accepted start of the uniform set.
- **Reported, not predicted:** coverage (falling coverage is no failure, and high coverage no support), the starts
  read as stalling against their growth, and the strata of any miss.

**Stop.** One accepted start whose grown view differs from its prediction in any round read, in either reading, under
either law, in any set; or none. A miss in the proved class would be a fault in the code or in the identification; a
miss elsewhere, in a stratum, narrows the two readings to the strata where they held.
