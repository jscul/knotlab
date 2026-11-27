# Reading a growth straight off its start: the graded order, tested where groups share a knot

Epic `GRADED-ORDER-20261126-001`, under G17 with G1, at the coordinator's pick (the advisor's direction 2, the
late-views study's direction 2). Design and predictions frozen before any fresh start is grown; [the code](graded.py).
Results go in a section of their own after the run.

## The question

The late-views study (`LATE-VIEWS-20261126-001`) read a local reader's whole view of a growth, round by round, off the
start's finite map for 705 of 706 accepted six-knot starts. Its frozen reading failed where two round-1 group cells
share a knot. A reading found afterwards, the **graded order** (`late.GeneralPiece`): the valid sets of the map ordered
by inclusion, a birth's parents the valid sets it covers and its fresh distinctions the valid sets covering it plus one
per chain at it, fixed 40 of the 42 misses. It is post hoc and untested, and it still misses two starts: census entry
6408 (six knots) and the hand-built eight-knot start (four eight-place knots meeting pairwise, each with a three-place
knot hanging from it).

## The quick check by hand (the advisor's, done first; done before the advisor's review below)

**The graded order does not fix the eight-knot start**, so as coded it fails with size. Worked through:
- The four large knots form one round-1 group cell G = {0, 1, 2, 3}; each small knot k joins the three large knots it
  does not hang from through a block B_k (for small knot 4, B_4 = {1, 2, 3, 4}).
- Round 2: the reading and the growth agree that the set G ∪ {4} is a birth with four parents (G and the three pairs
  {4, j}). The reading gives it 3 fresh distinctions (one valid superset G ∪ {4, k} for each other small knot k); the
  growth gives it 6.
- Round 3: the reading makes one birth G ∪ {4, 5} with four parents; the growth makes two, each with three parents:
  G ∪ {4}, G ∪ {5}, and one of {4, 2, 5} or {4, 3, 5}. The blocks B_4 = {1, 2, 3, 4} and B_5 = {0, 2, 3, 5} meet G in
  the common knots 2 and 3, and the growth makes one birth for each route from 4 to 5 through a common knot.
- **The exception, stated.** A **route cycle**: two distinct blocks, outside every group cell, that meet one group cell
  in two or more common knots (or two group cells that share two knots). The map's count of cycles treats the cycle
  B_4–2–B_5–3–B_4 (blocks and knots in turn) as filled, since it is the sum of two cycles each running through the
  cell; the growth does not fill it.
- **Post hoc check on every start already grown** (the late-views sets and fitting data, both laws): the route-cycle
  condition holds for exactly the misses (2 of 2 under each law: 6408 and the eight-knot start) and for none of the
  5,360 start-and-law cases the graded order gets right. This was seen before the freeze; the frozen test below is on fresh starts.

## The advisor's review before the freeze ([question](advisor_question_1.md), [answer](advisor_answer_1.md))

- **The route cycle is two failures under one name.** Its block clause is "two kept blocks share two knots", the proved
  class's own hypothesis (`REDUCE-BLOCKS`, corollary 2), which the cell hides; its cell clause (two cells sharing two
  knots) is a different failure, where the reading gives a cell no valid set and makes one birth for two at round 1.
- **A static form of the exception, computable without growing (adopted):** a **split pair**, a valid set of rank two
  or more with two parents that share no parent in the graded order (the order is not lower semimodular there, in the
  literature's words; Stanley, *Enumerative Combinatorics* I, chapter 3). The growth joins only births that pairwise
  share a parent, so two parents with no common parent enter two joins. Checked post hoc on every start already grown:
  the split-pair flag holds for exactly the misses (2 of 2 under each law) and for none of the 5,360 start-and-law
  cases the reading gets right.
- **A start where the graded order should fail with no route cycle** (adopted as a replay): eight knots, places
  5, 7, 6, 4, 7, 6, 4, 5, pairs 0–7, 1–7, 2–7, 4–7, 5–7, 0–1, 1–2, 1–3, 2–3, 0–4, 4–5, 4–6, 5–6; two cells {0, 1, 2, 3}
  and {0, 4, 5, 6} sharing knot 0. Its map is a tree by the count, the route-cycle flag is false and the split-pair
  flag is true; the advisor predicts a difference at round 1.
- **The first sample repeated one start many times** (repeats were removed by labels only); the sample is now drawn
  again with repeats removed up to renaming (a Weisfeiler–Lehman hash of the knot multigraph with places and
  multiplicities). Knots of the `tree+` weighting can have more than five places (bare sizes: open equals the round-1
  demand, so many of its starts have no pendant point and no chain).

## Design (frozen)

**The reading under test.** `late.GeneralPiece` unchanged, through `late.predict(..., general=True)`. Two static flags,
computed without growing (`graded.py`): **split pair** and **cells sharing two knots**; the first flag of this study,
the route cycle, is kept for comparison.

**Population (fresh, drawn by structure before any growth; every count below is up to renaming).** Seven-knot starts:
- **Primary**: the `tree+` weighting of `WEIGHTINGS-20261119-001B` (a uniform random tree of knots plus a Poisson(1)
  number of extra shared pairs, bare sizes), seed 20261127, 40,000 draws, up to 40 a bucket by stratum and route
  cycle: 83 starts ([fresh7_treeplus.jsonl](fresh7_treeplus.jsonl)): 41 with neither flag (15 with chains), 39 with a
  split pair, 3 with cells sharing two knots (one also a split pair).
- **Second weighting**: the `grow` weighting (the late-views study's seven-knot weighting), seed 20261127, 200,000 draws,
  up to 60 a bucket: 93 starts ([fresh7_grow.jsonl](fresh7_grow.jsonl)): 86 with neither flag, 7 with a split pair (6
  of them, with cells sharing a knot, have no route cycle, so the two flags disagree on them), 1 with cells sharing two
  knots.
- **Replays**: census entry 6408 and the hand-built eight-knot start (known misses), and the advisor's eight-knot start.
- Each grown to round 24 under parity and under not-all-equal with the look-alike study's growth (its 30,000-knot cap
  kept), compared in both readings with `score.compare`; the rounds read are reported for every start, and a start
  stopped by the cap is counted apart. The reading takes 0.01 s on the start with the most pendant points (10).

**Prior work in the program.** Searched, `--until 2026-11-26 --exclude GRADED-ORDER-20261126-001`:

`python3 -B scripts/track.py objects "graded order of valid sets reading growth from the start" --until 2026-11-26 --exclude GRADED-ORDER-20261126-001`
`python3 -B scripts/track.py objects "group cells sharing a knot" --until 2026-11-26 --exclude GRADED-ORDER-20261126-001`
`python3 -B scripts/track.py objects "seven-knot starts grown by ordinary growth weighting" --until 2026-11-26 --exclude GRADED-ORDER-20261126-001`

- `LATE-VIEWS-20261126-001` — the same object: this study tests its post hoc reading on fresh starts.
- `EXPLOSIVE-20261119-001` — a relative, and a warning: the filled map predicts where groups of three do not overlap;
  every explosive start within seven places had groups of three sharing a point and a block. A fresh start of that kind
  that explodes would be a miss of a different cause, recorded as such. Its direction 2 is the same open item as the
  order lemma below.
- `ROUND-FREE-20261119-001`, `COUNT-BALLS-20261118-001`, `INFLUENCE-CONE-20261120-001`, `GENERATORS-20261120-001` —
  unrelated objects on related populations.

## Predictions (frozen)

| # | Prediction | Fails when |
| --- | --- | --- |
| F1 | Every fresh start with neither flag agrees in every round read, both readings, both laws (85%) | any such start differs (a new exception) |
| F2 | Every fresh start with a split pair and no cells sharing two knots differs, first at round 1 or 2 (85%) | such a start agrees |
| F3 | Every start with cells sharing two knots differs at round 1 (85%) | otherwise |
| F4 | The six `grow` starts on which the flags disagree (split pair, no route cycle) differ (75%): the split pair, not the route cycle, is the exception | they agree |
| F5 | The replays: 6408 and the hand-built start differ at round 2 (a check of the code); the advisor's start differs, first at round 1 (80%) | otherwise |

**What a result will mean (frozen).** If F1 to F4 hold, the statement to prove is: *in the late-views predictor's class,
a start whose graded order has no split pair and no two group cells sharing two knots has as its births exactly the
valid sets of its graded order, each with the sets it covers as parents and the sets covering it, plus one per chain,
as fresh distinctions, with the relay and closing of `late.py` and the fresh count's floor max(D, 3 − p, 1).* A proof
needs Lemma R (`REDUCE-BLOCKS`, in hand) and one lemma about the order: any two parents of a valid set share a parent,
and every set of births that pairwise share a parent and lies in no one parent's children is the parent set of exactly
one valid set. Finding the class where that lemma holds is the open part. If F1 fails, the failing start gives the next
exception. Pieces with a cycle stay outside the reading.

## Scaffolds

The weightings (`tree+` primary, `grow` second), the seed, the bucket sizes and the 24-round horizon; entered in the
register with the results. The reading is the record's, unchanged.
