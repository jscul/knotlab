# A local reader's view grown on demand

Epic `ON-DEMAND-20261126-001`, at the coordinator's go-ahead on the owner's intuition, after
[`LATE-VIEWS-20261126-001`](../LATE-VIEWS-20261126-001/decision.md). A check by the thread, not a registered study;
computed. The sections down to "Frozen" were committed, after the advisor's review ([question](advisor/question.md),
[answer](advisor/answer.md)), before the frozen runs below.

## The question

The owner wrote: "What if the quantum resolution stuff is actually like when the logic has to settle ... we only need to
compute what is discoverable/discovered. So we can kind of simulate from "life" with a simulated environment ... the
trick here is that we're not actually simulating the full environment from the start, just the parts we need."

Asked as a test: can a local reader's view of a growth be computed from only the part of the start the reader needs,
and does it come out the same whatever further parts are filled in, and in whatever order? And where does the growth law
itself read the whole start, so that no part can be left unread?

## Words

- **A reader** is one live start knot k. **Its view at round t** is the multiset of round-t births that descend from k
  (their ancestry holds k), read by parents and fresh distinctions, and with the parents' readings as well (the two
  readings of the earlier studies, register entry A283).
- **Holder steps.** Two live knots are one holder step apart when some knot (a holder, live or not) is a neighbour of
  both: they share a block. The knots within s holder steps of k are those reached in at most s such steps.
- **On demand.** The growth run on a **region**: a set of live start knots, each holder's block cut to the region, the
  open counts unchanged. A region needs the holders' neighbour sets one start step beyond its knots (the advisor's
  point): the knots are what is computed, the holders what is read to compute them.

## What it rests on

- **Lemma R** (`REDUCE-BLOCKS-20261119-001`, proved): from round 1 on, the growth reads a start only through its live
  knots, their open counts and the maximal blocks. So the roster engine ([`ondemand.py`](ondemand.py), after
  `WALL-READ-20261119-001A`'s, with each birth's ancestry carried) grows any region.
- The engine equals the look-alike study's growth, every round in both readings, on every census start of four knots
  under both knot laws (200 each; [`ondemand.py verify`](ondemand.py)); the five-knot check is running (stress test
  pending).
- **The round.** Rounds are run together, a scaffold the earlier asynchronous study (`LOCAL-ROUND-20261123-001`) shows
  can be replaced by births one at a time from a record of parents. This study does not compose the two.

## Seen before the freeze (exploration, not a test)

1. **Random trees** ([`explore.py`](explore.py); the 'tree' weighting of `WEIGHTINGS-20261119-001B`, 40 knots, five
   starts, one reader each): the least number of holder steps whose knots give the reader's view through round t was t
   or less in every round to 8.
2. **The advisor's hand test** ([`handtest.py`](handtest.py), [`handtest.json`](handtest.json)): a path of two to eight
   knots ending in a triple of knots touching pairwise, two triples sharing a knot, four knots touching pairwise, or a
   triple at both ends, with and without a surplus distinction, every live knot a reader, rounds 1 to 8. The knots within
   t steps fail in 127 of 2,368 (reader, round) cases (and in 19 more where fewer steps happen to work), every one where
   the edge of the region passes through a round-1 group of three or more: a knot one step beyond the edge is a
   candidate of two members of the group, so cutting it gives each of them a one-parent birth where the group had one
   way to grow. The knots within t + 1 steps give the view in all 2,368, under both laws.

So the frozen claim is t + 1 steps.

## The advisor's review, taken

The hand test (above); name what a region reads (the holders); the cap on births per round is a global read, so only
rounds before the full growth's cap are compared and region growths are not capped; the owner's picture is admission
during the growth, so H2 admits further knots in steps and checks each step; the round and the cap are scaffolds
(register entry, below); say that the far part is unread, not undetermined; the exact link for H1 is the dependence cone
of a cellular automaton (one step per round), for H2 confluence, for H3 (b) that a parity consequence has no local
certificate. Not taken: composing the admission with births one at a time (left as a next direction).

## Frozen

Scaffolds: register entry A288.

**Populations** ([`run.py`](run.py)), each start with one reader drawn by the same generator:
1. 60 starts of the 'tree' weighting at 40 knots, `random.Random(20261201)`, rounds 1 to 8.
2. 60 starts of the 'tree+' weighting (a tree plus extra lines, so cycles) at 25 knots, `random.Random(20261202)`, rounds
   1 to 7.
3. 400 starts of the uniform six-knot census sample of the late-view study, drawn by `random.Random(20261203)`, rounds 1
   to 10 (this set holds the starts that stall, several pieces, and groups of three or more that share knots).
The full growth stops before a round of more than 3,000 births; rounds past it are not read.

**Predictions.**
- **H1 (the reach of round t).** Under not-all-equal, for every start that does not stall in round 1, its reader and
  every round t read, the growth on the live knots within t + 1 holder steps of the reader gives the reader's view
  through round t exactly, in both readings. Reported: how often t steps suffice.
- **H2 (any admission).** Every region holding those knots gives the same view through round t: three regions per start
  (those knots, each further live knot added with probability one half), and those knots, then half of the rest, then
  all, admitted in three steps, each step checked.
- **H3 (where the law reads the whole start).** (a) For a start that stalls in round 1, reported: the fewest holder steps
  whose knots stall too, or none when the short knot lies beyond the reader's piece; a reader computing only its region
  would grow where the start does not, so on demand needs one check of the whole start before round 1. (b) Under
  parity, predicted: every reader whose region growth differs from the full growth (within t + 1 steps) sees it at a
  round where the region growth closes with an implied birth and the full growth does not; under not-all-equal, never.
- **Reported, not predicted:** the births a region makes that the full growth does not (provisional births at the edge
  of what is computed, named by descent), and the share of the full growth's births the view rests on.

**Stop.** One start, reader and round under not-all-equal where the knots within t + 1 holder steps, or a region holding
them, give a different view; or none.

**What it cannot show, said before the runs.** A reader's view through round t depends on the start only within t + 1
holder steps: the far part is unread, not undetermined, and a deterministic local law can always be run lazily. This
is the opposite of a link at a distance: a change beyond the reach cannot reach the reader before round t + 1, and the
earlier studies found no far change heard late and nothing in the model beyond the classical bound with free settings.
Parity's implied birth reads the whole presentation (the literature's implied clause), and the earlier studies found no
reader hears a far change through it with free settings.
