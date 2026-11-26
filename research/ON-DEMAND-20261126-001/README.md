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

**Deviation, recorded before the rerun.** The first run of the tree-plus-lines set was stopped by its 6 GB cap at its
fifteenth start (a region growth without a cap). It is rerun from the start with the same seed and draws, each start in
a child process with 3 GB of address space and 300 seconds, and every region growth capped like the full growth: a
region growth that stops at the cap before round t is not read at t, and a start over either limit is not read. Its
first 14 starts reproduce the first run exactly (checked on three). The tree and six-knot sets, which finished, are
not rerun.

## What was found

Three runs ([`results_tree40.jsonl`](results_tree40.jsonl), [`results_treeplus25.jsonl`](results_treeplus25.jsonl),
[`results_census6.jsonl`](results_census6.jsonl); the stopped first run kept as
[`results_treeplus25_first_run.jsonl`](results_treeplus25_first_run.jsonl)), scored by [`score.py`](score.py)
([`score.json`](score.json)).

| population | starts read | (reader, round) cases | H1: within t + 1 steps, not-all-equal | within t steps | H2 regions and steps | stalls in round 1 |
|---|---|---|---|---|---|---|
| 'tree', 40 knots | 60 | 411 | 411 agree | 411 agree | 327 agree | none |
| 'tree+', 25 knots | 58 (2 not read: memory, time) | 365 | 365 agree | 352 agree, 13 differ | 329 agree | none |
| six-knot census sample | 148 (of 400) | 1,480 | 1,480 agree | 1,466 agree, 14 differ | 888 agree | 252 |

**H1 holds: the stop is "none".** Under not-all-equal, in all 2,256 (reader, round) cases, the growth run on the live
knots within t + 1 steps of the map gives the reader's view through round t exactly, in both readings. The knots within
t steps suffice in 2,229; the 27 that need one step more are all in the two sets with cycles or groups of three or more,
none in the trees, as the hand test found.

**H2 holds.** Every region holding those knots gave the same view (1,544 regions and admission steps under
not-all-equal): admitting more of the start, in any of the orders drawn, never changed a round already read.

**H3 holds.** (a) Of the 252 starts that stall in round 1, the reader's own region stalls within 1 step of the map in
194, within 2 in 55 and within 3 in 1; in 2 the short knot lies in another piece of the start, which no region grown
from the reader ever reaches. So on demand needs one check of the whole start before round 1, and only then. (b) Under
parity, 53 (reader, round) cases differ, all in the six-knot set, and in every one the region's growth closes on an
implied birth (one birth holding every live knot of the region) that the full growth does not make; under
not-all-equal none differ. Nine further regions of H2 differ under parity; how they end was not recorded.

**What a reader rests on (reported).** At the last round read, the reader's view rests on a median of 28% of the full
growth's births in the trees (least 5%), 34% in the starts with cycles (least 10%), and nearly all of them in the six-knot
starts, which are too small to leave anything out. The growth on the knots within t + 1 steps makes some births the full
growth does not, at the edge of what it computes (2.9% of its births in the trees, 4.0% with cycles, 3 of 74,219 in the
six-knot starts): provisional births, which the full growth replaces once the knots beyond the edge are admitted, and
which the reader's view never contains.

**What it says.** In the growth of Chapter 8 under not-all-equal, a reader's view through round t depends on the start
only within t + 1 steps of the map from it, so the view can be computed on demand from that part alone, filled in in any
order, after one check of the whole start that no knot is short. Parity's implied birth is the one rule that reads the
whole presentation at a later round.

**What it does not show.** The far part is unread, not undetermined: a deterministic local law can always be run
lazily, and nothing is settled by being read. The bound of one step of the map a round is the opposite of a link at a
distance: nothing beyond the reach can change the reader's view before the round it reaches. The earlier studies found
no far change heard late and nothing beyond the classical bound with free settings, and this adds nothing to either.
Admission was tested with rounds run together, not with births made one at a time; the readers are start knots; the
starts have up to 40 knots.

**Stress test pending.** The engine's check against the growth on all 3,157 five-knot census starts under both laws
(four-knot: all agree) was 2,026 starts in, all agreeing, when this was written.

**Link (intuition-links), offered as an intuition.** The exact link for H1 is the dependence cone of a cellular
automaton: with one step per round, the state at a site after t rounds depends only on the sites within t steps; here
the reach is one step more, because a group of three or more is read whole at its edge. H2 is confluence (Newman's
lemma, for a growth with a finite round structure). For H3 (b), a parity consequence has no local certificate: the
literature's contrast between unit propagation and Gaussian elimination, of which Tseitin's parity on a cycle is the
smallest case. The owner's "quantum resolution" is, on this reading, not where the far part settles: the far part is
settled by the law whether read or not. The one place where a reader's own birth waits on the whole start is parity's
implied birth, a consequence of the whole presentation, which the earlier studies found no reader can use to hear a far
change.
