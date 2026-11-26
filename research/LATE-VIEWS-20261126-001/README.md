# The late views of a growth from its start alone

Epic `LATE-VIEWS-20261126-001`, at the coordinator's go-ahead on the selected direction of
[`LAST-MERGE-20261126-001`](../LAST-MERGE-20261126-001/decision.md). A check by the thread, not a registered study;
computed; refereed (R1: confirmed with fixes, no Block; folded in below). The sections down to "Frozen" were committed, after the advisor's review before the freeze
([question](advisor_question_freeze.md), [answer](advisor_answer_freeze.md)), before any grown file of the held-out
sets below was opened; the sets were grown meanwhile.

## Prior work in the program

Added after the referee (R1, item 7). Earlier work already had the pieces this study assembles: the cluster-count study
(`CLUSTER-ALL-20261119-001`, [preregistration](../CLUSTER-ALL-20261119-001/preregistration.md)) required a group of
three or more to enter all at once and adjusted the relay for its size, and its record documented a failure with two
groups sharing one knot and a two-knot block ([note](../CLUSTER-ALL-20261119-001/cluster_all.md)); the reduction lemma
(`REDUCE-BLOCKS-20261119-001`, corollary 2) supplies distinct maximal blocks with the identification's hypotheses; the
chain identification's Theorem 2 already sums the untyped binomials over the core. What this study adds: those rules
predict the counts by kind of birth and by the parents' kinds, every round, and the settling cuts, including the attempted
extension to a block meeting a cell; and it locates where the one-or-all rule fails at six knots. The freeze is commit
`f97fd78ae5`, the results `3ceb22a8ec` (identical prediction bytes and predictor logic); no separate deviations file
accompanies the freeze.

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
grown. [Corrected after the referee:] for round one the map must also keep each live start knot's original number of places: of 290
pairs of accepted uniform starts with the same maximal blocks and loose counts, 284 differ in their first reading with
parents.

Two readings go past the identification as first proved; both were found by exploring the census of up to four knots
([Corrected after the referee:] the first is already proved, by the reduction lemma's corollary 2, and the second follows the cluster-count study's one-or-all rule):
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
to the predicted counts). [Corrected after the referee:] the terms of each kind are summed before its last departure from its eventual
polynomial is located, since their departures can cancel (for two three-place knots sharing one distinction the
two-parent births with two fresh distinctions give 2x²/(1 − x)², whose terms depart by +2, −4 and +2 at round two); the
largest set of a kind gives only a bound. The literature's
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
growths fails on all 470 that close. The predictor can fail. [Corrected after the referee:] the fitting runs are read through their saved
rounds (the archive of one to four knots ends at round 20; at five knots 22 accepted records per law hit the knot cap in
rounds 19 or 21), and the 470 are the parity closures among starts the not-all-equal predictor accepts (of the 478 parity
closures, eight have an excluded cycle).

**The six-knot census by structure alone** ([`strata_census6.json`](strata_census6.json), [`strata.py`](strata.py)):
of 82,656 starts, 50,845 stall in round 1 by their demand, 1,473 have a piece with a cycle, and 30,338 are accepted
(95.4% of those that do not stall): 2,053 in the proved class, 4,264 with repeated blocks only, 20,232 with group cells,
3,733 with a block meeting a group cell, 56 with one loose distinction. Rare strata: two group cells sharing no knot (92),
group cells sharing a knot (42); none of the 30,338 accepted starts has two cells sharing at least two knots
([Corrected after the referee:] 1,151 starts that do not stall but are excluded have such an overlap).

## Frozen

**The held-out sets**, each grown to round 24 under not-all-equal and under parity with the look-alike study's growth,
unchanged (scaffolds: register entry A286):
1. **Uniform.** 2,000 six-knot census starts, `random.Random(20261128).sample` over the census outside the 3,000 sampled
   before ([`sample.py`](sample.py)).
2. **Stratified.** 199 six-knot starts, up to 40 in each of five rare strata, `random.Random(20261130)`, outside all
   5,000 ([`stratified.jsonl`](stratified.jsonl)).
3. **Built by hand.** 17 starts with group cells of four to seven knots ([`handbuilt.py`](handbuilt.py)). [Corrected after the referee:]
13 of the 17 are census identities, nine of them in the fitting data; of the four outside the census, three are accepted
and two agree.
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

## What was found

> **Referee R1, confirmed with fixes, no Block, folded in** ([report](referee-R1/report.md)). Narrowed: the existing
> proofs cover 125 of the 706 uniform starts, not 39; the round-1 reading needs each start knot's places; the misses are
> 40 starts with cells sharing a knot (from round one) and two with a block meeting a four-knot cell (from round two);
> the settling cut needs each kind's terms summed first; 13 of the 17 hand-built starts are census identities; the
> horizon set reached round 40 on 95 before the referee's replay; prior work credited (Not a block). Sentences are
> corrected where marked.

The grown sets ([`held_out_nae.jsonl.gz`](held_out_nae.jsonl.gz), [`held_out_parity.jsonl.gz`](held_out_parity.jsonl.gz),
`grown_*.jsonl.gz`) were opened after the freeze and scored by [`score.py`](score.py) ([`score.json`](score.json)).

| set | accepted | proved class: agree | a new reading: agree | not accepted |
|---|---|---|---|---|
| uniform, six knots | 706 | 39 of 39 | 666 of 667 | 1,253 stall; 41 a piece with a cycle |
| stratified, six knots | 199 | none in it | 159 of 199 | none |
| built by hand | 16 | none in it | 15 of 16 | 1 a piece with a cycle |
| 'grow' weighting, seven knots | 70 | 40 of 40 | 30 of 30 | 929 stall; 1 a piece with a cycle |
| horizon, to round 40 | 100 | 9 of 9 | 91 of 91 | none |

Each row holds under not-all-equal and under parity alike: the same starts agree and differ. [Corrected after the referee:] these
denominators count structural starts; requiring every start to pass K1–K3 removes one agreeing parity start from each of
the uniform and seven-knot sets (704 of 705 and 69 of 69). Of the 747 uniform starts that grow, 705 agree in both
readings; 41 accepted starts per law hit the knot cap, 26 of them before round 24.

**The stop is met: 42 accepted starts differ.** By the stratum each was drawn for:
- **Group cells sharing a knot: 39 of 39 differ**, from round 1 ([Corrected after the referee:] by membership, 40 of 40 tested starts with
cells sharing a knot differ, the fortieth drawn for another stratum; their total births agree every round, their kinds do
not). Two cells G1 and G2 meet in one knot k; a knot a of
  G1 and a knot b of G2 are candidates through k, so {a, b} is a round-1 pair, and in round 2 one birth holds both cells
  with three parents, G1, G2 and the pair. The frozen rule underpredicts the pair by one fresh distinction ([Corrected after the referee:] 0 for 1 on 12 starts, 1 for 2 on 17,
  2 for 3 on 11) and gives the union two parents.
- **A block meeting a group cell of four: 2 differ**, from round 2 (census entry 6408 of the uniform set, and the
  hand-built start of four knots touching pairwise with a knot hanging from each; [Corrected after the referee:] the third miss first
  listed here, census entry 30324, has two cells of three sharing a knot and belongs above).
- [Corrected after the referee:] by membership in the supplement, two cells sharing no knot agree 40 of 40, a cell of four or more with chains
  99 of 99, and of the 65 with a block meeting a cell with chains 21 miss (all of them with cells sharing a knot).

**The rest of the predictions.**
- **P2.** The grown dimension equals the predicted one for every accepted start of a dimension; the settling round is as
  predicted for all but the starts that differ (uniform 697 of 698 in each reading under not-all-equal; seven knots 70 of
  70; horizon 100 of 100).
- **P3** holds: all 100 match their saved views. [Corrected after the referee:] the growths reached round 40 on 95, round 35 on two and
  round 34 on three; the referee's replay supplied the missing 28 rounds and confirms 100 of 100 through round 40.
- **P4** holds: without the relay 217 of the 706 uniform starts differ, without the group cells 581, and the
  not-all-equal reading on the parity growths 173 ([Corrected after the referee:] on the 705 starts the full predictor gets right they
  introduce 216, 580 and 172 errors).
- Every start read as stalling by its round-1 demand stalls at round 1 (1,253 uniform, 929 seven-knot).

**Post hoc, not a test** ([`posthoc.py`](posthoc.py), [`posthoc.json`](posthoc.json)). Read the valid sets as a graded
collection ordered by inclusion: a birth's parents are all its valid subsets of size one less, and its fresh
distinctions all its valid supersets of size one more, plus one per chain at it (`late.GeneralPiece`). In the proved
class this is the identification itself. It agrees with 40 of the 42 misses and with every start that agreed before, in
every set and the fitting data; the two left (census entry 6408 and the hand-built start, a cell of four with blocks
meeting it) are not explained. Found on the misses, it needs held-out starts of its own.

**What it says.** For 705 of the 706 accepted starts of the uniform six-knot sample, and every accepted seven-knot start
of a second weighting, a local reader's whole view, every round in both readings, and the round at which it settles are
read off the start's finite map without growing it. [Corrected after the referee:] 39 of the 706 satisfy the identification directly and
86 more after repeated or contained blocks are removed (the reduction lemma's corollary 2); of the remaining 581 with
cells, 580 agree. The one-or-all reading of groups, after the cluster-count study, fails where two cells share a knot,
42 starts in the six-knot census.

**Link (intuition-links), offered and not checked as a theorem.** The post hoc reading makes the growth the literature's
Hasse diagram of a graded partially ordered set (Stanley, *Enumerative Combinatorics* I, chapter 3): the valid sets
ordered by inclusion, ranked by size less one; a birth's round is its rank, its parents are the sets it covers, and its
fresh distinctions count the sets that cover it. A group cell is then a set that enters the order whole, one rank above
its knots, and two cells that share a knot are covered together by their union. Cheapest test: the revised reading on
fresh starts where cells share a knot.
