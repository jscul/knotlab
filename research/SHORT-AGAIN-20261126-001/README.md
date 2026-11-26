# A ration under which knots are short now and then: does a pattern then hear another from afar?

> **Refereed (R1, confirmed with fixes, no Block): the narrowings are in the notice of [the decision](decision.md).**

Epic `SHORT-AGAIN-20261126-001`, at the owner's word ([request](owner_request.md)). A check by the thread, not a
registered study; computed; referee pending. Every ration here is made by hand for the purpose: a scaffold.

## Why

The two studies before this one found that what one pattern is reaches another pattern's own knots in the first
rounds or never. Under the ordinary count no new knot is ever short, and a change reaches an own knot only through
a join cancelled by a short knot. Under a cap, or "just enough for three places", knots are short all the time and
the joins between the two patterns stop. The ration wanted is in between: the two stay joined, and knots are
short now and then, by what is around them.

## The design

**Rations** ([`rations.py`](rations.py)). Each reads only what the engine's rations read: join or offshoot, the
number p of distinctions given, the demand D (the joins the knot will be owed next round), and for an offshoot its
parent's owing. Each gives at least enough for three places and one fresh distinction.

| ration | a new knot receives | the advisor's forecast |
|---|---|---|
| the ordinary count | what it is owed | the baseline: own knots never hear |
| ODD-FEWER | one fewer when its demand is odd | the one listed candidate not expected to fail |
| BUSY-FEWER | a join one fewer when its demand exceeds its number of parents | "run second": short only at a join with demand three or more, offshoots never |
| ONE-FEWER (the ring study's) | one fewer, always | the cap's regime: the joins stop |
| JOIN-FEWER | a join one fewer, always | short whatever the other is: constant, so nothing to hear |
| THIRD-FEWER | one fewer when its demand leaves 2 on division by 3 | joins owed two are short: the chain cuts itself |

**Receivers and senders.** Four small starts of the census whose own knots, under the ordinary count, keep a join
with knots not their own through every round read, with every one of the 44 partners, and which grow slowly
(`reach.py list`): three mutually sharing knots with loose counts 1, 1, 2, and three knots in a row with loose
counts 1, 3, 3; 1, 2, 3; and 1, 2, 2, each sited at its first knot. Every ordered pair, the receiver A and the
sender B: 16.

**Distance.** A and B are joined by a meeting through a chain of d − 1 link knots, d = 1 to 8.

**Changes on the sender's side**, each grown beside the unchanged start under the same law: one more loose
distinction at each start knot of B; at each link knot (the advisor's placement control: hearing should follow the
change's distance from A, not d); two more at B's site; one fewer at B's site.

**Read** each round, to 16 rounds or 3,000 knots: the first round A's own births differ (A hears); the first round
the joint descent's births differ; the first round the cancelled groups holding one of A's own knots differ (the
advisor's second reading: the only way in, so it should not come after the first); A's own kept joins with others;
the short knots; A alone under the same law; and, under the ordinary count, every new knot's demand.

**Taken from the advisor's review** ([question](advisor_question.md), [answer](advisor_answer.md)): the forecasts
above; the demand table under the ordinary count first; the receiver alone under each ration; the baseline; the
placement control and the second reading; two more kinds of change; "not heard by round 16" reported as not heard
in the rounds read, never as a round; and the kill rule: if A's own kept joins stop under both ODD-FEWER and
BUSY-FEWER, the treatment of a short knot is what to redesign, not the ration. Not taken: the lag behind the
joint descent's front is read as the difference of two first rounds, not from the front itself.

## Expected (written before the full run, after one trial case: receiver 1, 1, 2, sender 1, 3, 3 at four steps)

1. **Ordinary count.** A's own knots hear no change, at any distance, in any pair.
2. **ONE-FEWER, JOIN-FEWER, THIRD-FEWER.** The last kept join between A's own knots and others is by round 3 in
   every case, as forecast.
3. **ODD-FEWER and BUSY-FEWER keep A's own knots joining** to the last round read in most cases. The trial case
   showed it; it is the half I did not have before.
4. **But they hear only what is next to them.** In the trial case A's own knots heard the change at the link knot
   beside A, in round 2, and nothing further out. I expect that in every pair: no change two or more steps from
   A's site is heard by A's own knots under either ration. If one is, at a round that grows with its distance,
   that is the stop.

## What was found: distance

All 2,304 cases were read, 10 to 16 rounds each (1,336 to round 16); the table is
[`reach_table.md`](reach_table.md) ([`tally_reach.py`](tally_reach.py) on [`reach_runs.jsonl.gz`](reach_runs.jsonl.gz)).
A change's distance is the number of steps from A's site to the knot changed. Treatments that share a row gave the
same counts.

| ration | short knot | A's own knots still joining others in the last round | rounds with a short knot (median) | changes heard by A's own knots at distance 1 | 2 | 3 | 4 or more |
|---|---|---|---|---|---|---|---|
| the ordinary count | any | 128 of 128 | 0 | 4 of 160 | 0 of 176 | 0 of 160 | 0 of 592 |
| ODD-FEWER | any | 128 of 128 | 1 | 132 of 160 | 0 | 0 | 0 |
| BUSY-FEWER | any | 128 of 128 | 1 | 148 of 160 | 0 | 0 | 0 |
| ONE-FEWER | waits | 0 of 128 | 11 | 48 of 160 | 4 of 176 | 0 | 0 |
| ONE-FEWER | retires, or offshoots | 0 of 128 | 13, 10 | 13 of 160 | 0 | 0 | 0 |
| JOIN-FEWER | waits | 0 of 128 | 11 | 46 of 160 | 4 of 176 | 0 | 0 |
| JOIN-FEWER | retires, or offshoots | 0 of 128 | 13, 10 | 13 of 160 | 0 | 0 | 0 |
| THIRD-FEWER | waits | 0 of 128 | 12 | 130 of 160 | 38 of 176 | 0 | 0 |
| THIRD-FEWER | retires, or offshoots | 0 of 128 | 8, 10 | 121 of 160 | 0 | 0 | 0 |

- **No change three or more steps away is heard under any ration (0 of 752 for each law), and none is first heard
  after round 3.** The stop is not met.
- **The candidates split in two, with nothing between.** ODD-FEWER and BUSY-FEWER keep A's own knots joining
  others in every case and to the last round, which no ration of the earlier studies did while making anything
  short; but they make almost nothing short (in half the cases a knot is short in one round or none; under
  ODD-FEWER with waiting 56 cases have a start knot that stays short and waits). The other three make knots short
  in most rounds and A's own knots stop joining others in every case, as the advisor forecast.
- **Why there is nothing between: to a ration, every knot the two make together looks the same.** Under the
  ordinary count every one of the 11,136 new knots of the joint descent, and every one of the 13,440 on the link's
  side, is a join of two parents owed two joins. A ration reads only whether a knot is a join, how many
  distinctions it was given, and what it is owed. So a ration leaves all of those knots short or none of them.
  A's and B's own knots do vary (joins of two owed one to four, joins of three, offshoots owed nothing to two),
  and that is where ODD-FEWER and BUSY-FEWER find their few short knots (5 in 100).
- **The ordinary count's four** are the same change, one loose distinction fewer at the site of one sender, next
  to A: the start knot itself is left short of the join it is asked for. No new knot is short.
- **The second reading.** Where A's own knots hear a change, the cancelled groups holding an own knot differ in
  the same round or earlier, except in 15 changes (all at one step, with waiting, under the three rations that
  cut the joins): there the own births differ in round 3 and the cancelled groups only in round 6. So a cancelled
  group is not the only way in: a new knot's fresh count reads its demand, and its demand counts siblings that
  are not its own.
- **The receiver alone** goes on making knots under every ration (128 of 128 each).

## What was found: a mark at a made knot

The reach table left one thing untried: the joint descent is uniform because a mark at a *start* knot re-makes it
whole. So a mark was set at a *made* knot instead ([`made_mark.py`](made_mark.py),
[`made_mark.jsonl.gz`](made_mark.jsonl.gz)): every receiver and sender at distances 2 and 4, grown to round 6;
then each knot made in round 6 that is not A's own, in turn, given one more loose distinction by hand; then on to
round 16 beside the unmarked growth. Its children are then owed one more than their neighbours: one irregular
place. 288 studies, 4,896 marks.

| ration | marks heard by A's own knots, the marked knot 1 sharing from an own knot | 2 | 3 | 4 or more |
|---|---|---|---|---|
| the ordinary count | 0 of 96 | 0 of 96 | 0 of 96 | 0 of 936 |
| ODD-FEWER | 96 of 96, each first in round 8 | 0 of 96 | 0 of 96 | 0 of 1,544 |
| BUSY-FEWER | 96 of 96, each first in round 8 | 0 of 96 | 0 of 96 | 0 of 1,552 |

So the stop's first half is met and its second is not. Under either made ration a change made in round 6 is
heard by A's own knots two rounds later, which no law of the earlier studies allowed after the start; but only
from the knot beside them, in every one of 96 cases, and from two sharings away in none.

## Why one step and no more where short knots do not wait: a reading

By the engine's rule a member that is not short spends every loose distinction it has: one on each kept join, one
on an offshoot for each that is left (the record calls this the release rule). So when a short knot cancels a
join, its partner makes an offshoot in the join's place and has exactly as many children as before. The partner's
other children are owed what they would have been owed. What has changed is one child, an offshoot of one parent
where a join of two would have been, and that child's own descent after it. **A cancelled join changes what one
child is, never how many there are, so the change is handed down that child's line and not across.** A pattern's
own knots hear it exactly when one of them is the partner: one step.

This is read from the rule, not proved, and it fits the counts where short knots retire or make offshoots: none
heard beyond one step under any ration, in the reach table, at a made knot, and on the two sources below. Where
short knots **wait** it is not the whole story, as the next section shows: a waiting knot later joins whatever
still waits, and that does pass a change across.

## What was found: the bench and the census under the made rations

[`made_table.md`](made_table.md) ([`tally_made.py`](tally_made.py); the bench's 540 cases, 537 read, with the
marks; the census's 990 pairs under ODD-FEWER and BUSY-FEWER, 11,880 cases, all read).

- **The census.** No mark is first heard by a start's own knots after round 6 except two, in round 7 (BUSY-FEWER,
  a shared distinction, waiting). ODD-FEWER leaves a knot short in half the rounds or more in most cases with
  waiting (915 of 990 by a meeting), and marks are heard by own knots far more often than under any earlier law
  (2,097 and 3,593 of 5,670), but early: the latest first hearing is round 6.
- **The bench.** 26 marks are first heard after round 6, and every one is in the same pair: **two seven-knot
  sources joined by a meeting, with waiting**, under BUSY-FEWER (4), ONE-FEWER (8) and JOIN-FEWER (14), at one,
  two and three steps. Under JOIN-FEWER every mark in the other source is heard, at rounds 4 to 6 at one step, 5
  to 7 at two, 6 to 8 at three.

## The two sources: heard from afar, one step a round

> **Correction, logged in [the corrections](../../docs/CORRECTIONS.md).** Without the change these structures make
> no knot after round 1: every member is short and waits in rounds 2 to 16, under JOIN-FEWER and ONE-FEWER with
> waiting at every distance, and under BUSY-FEWER at d = 1 and 2, the only distances at which it carried (the ring
> study's word for this is "jammed"). The 32 to 53 knots at round 16 are the start and its first round. A change
> lets one knot pay; the jam then ends one knot a round along the line, and the structure grows without bound (4,766
> knots at round 11 at d = 4). A stub in place of the other source ends it too (from round 5 at d = 3). So what the
> receiver hears is that the jam has ended, and when, not what the other source is. The counts below stand. [The jam
> study](JAM.md) tests whether hearing from afar is always the end of a jam, and [the ring line](RING_LINE.md) finds
> that the line passes once and stops.

[`far.py`](far.py), [`far.jsonl.gz`](far.jsonl.gz): the two sources joined by a meeting through a chain of up to
seven link knots, with the reach table's changes, to 16 rounds; 96 cases, all read.

| ration, short knots wait | marks at the other source's seven start knots heard by a source's own knots, at distance d = 1 … 8 | a mark at the k-th link knot is first heard in round |
|---|---|---|
| the ordinary count | none at any d | never |
| JOIN-FEWER | 7 of 7 at every d, first in rounds d + 3 to d + 5 (rounds 11 to 13 at d = 8) | k + 3, for every k and d |
| ONE-FEWER (the ring study's) | 2 of 7 at every d, in round d + 5 | k + 3, for every k and d |
| BUSY-FEWER | 7 of 7 at d = 1 and 2, none from d = 3 | the second link knot only |
| ODD-FEWER, THIRD-FEWER | 2 of 7 at d = 1, none beyond | the first (and under THIRD-FEWER the second) only |

With retiring in place of waiting, under every one of these rations: none heard at any distance, except the
knot next to the source under ODD-FEWER and THIRD-FEWER.

- **This meets the stop.** Under a ration that uses no names, a change in the other pattern is first heard by a
  pattern's own knots at a round that grows by one with each step between them, at every distance tried up to
  eight, as late as round 13. The placement control holds: a change on a link knot is heard by its own distance
  from the receiver, whatever the distance of the sender. Two more loose distinctions at the sender's site are
  heard to d = 6 under JOIN-FEWER, one fewer at every d under both. The second reading agrees: in all 98 and 52
  hearings the cancelled groups holding an own knot differ in the same round or earlier.
- **What carries it is a line of waiting knots, and almost nothing grows.** At round 16 these structures hold 32
  to 53 knots; a knot is short in 15 of the 16 rounds; no join between a source's own knots and others is kept in
  the last round. Each join is given one fewer than it is owed, is short, and waits; its partners spend what
  they hold on offshoots; and it acts when what it is owed has fallen to what it holds. That happens to one knot
  after another along the chain, and a change at one end shifts when the next can act. It is nearer a fuse than
  a conversation: I have not seen it pass twice.
- **Only the source hears, and only a source is heard** ([`receivers.json`](receivers.json), three steps apart,
  JOIN-FEWER and ONE-FEWER with waiting). As receiver, the source hears a change on either link knot whatever the
  sender is; the ring, the two-knot part and two small starts hear the link knot beside them or nothing. As
  sender, a source's seven marks are all heard by a source; a ring's five, a two-knot part's two and a small
  start's three are not (0, one exception under ONE-FEWER).

## Expectations, and how they fared

1. *Ordinary count: A's own knots hear no change.* Holds but for one kind: one loose distinction fewer at the site
   of one sender next to A (4 of 1,088), where the start knot itself is left short.
2. *ONE-FEWER, JOIN-FEWER, THIRD-FEWER: the last kept join by round 3.* Holds on the small starts (none still
   joining in the last round, 0 of 128 each).
3. *ODD-FEWER and BUSY-FEWER keep A's own knots joining.* Holds: 128 of 128 each.
4. *But they hear only what is next to them, and the stop is not met.* Right about those two rations on the small
   starts and at a made knot, and wrong about the stop. It is met by the rations I had written off in item 2: the
   joins do stop under them, and with waiting a change travels all the same, through the knots that wait.

## What this does not say

- **One pair of patterns.** Hearing from afar is seen with a source at both ends, and with a source receiving from
  link knots. Why the source and not the ring is not known.
- **A scaffold, and a growth that barely grows.** JOIN-FEWER is made by hand; ONE-FEWER is the record's, but under
  it only two of seven marks are heard. Under both the structure is nearly at rest. This is not two lasting,
  growing patterns exchanging anything.
- **Once.** Nothing here shows a second change passing along the same line.
- **Sixteen rounds, distance eight, one site each, a meeting as the join.** By a shared distinction the bench's
  latest first hearing under JOIN-FEWER with waiting is round 5.
- **The reading of "why" is a reading.** The fuse is described from the counts (knots, short rounds, kept joins),
  not traced knot by knot.

## After the first checkpoint

Three checks and one link, run by the thread that took the line over ([decision](decision.md)):

- [**The ring at one end of the line**](RING_LINE.md) (direction 1): the line passes once and stops. Joined through
  the line, the ring no longer comes round under the rations that carry; where it does come round (the cap of
  three), nothing it does reaches the source. What passes under one fewer is one number: when the source starts
  making knots again (one or two rounds later with the ring than with a stub).
- [**Is hearing from afar the end of a jam?**](JAM.md) (directions 2 and 3, 2,256 pairs and three samples): not of
  the whole pattern. By a meeting under one fewer than asked, a far change gets in through own knots that wait (one
  exception in 2,327 far hearings, at d = 2). The record's own "one fewer" does what the made ration did. Under the
  cap of three one receiver hears from afar another way: it switches its way of growing at round 2d + 1 when the far
  end's site holds two loose distinctions, at every distance tried.
- [**A second change**](AGAIN.md) is heard in 120 of 376 pairs under one fewer; a third could not be read.
- **The link** ([`peel.py`](peel.py), `peel.json`): the end of the two sources' jam follows the literature's threshold
  peeling (bootstrap percolation): every short knot falls short by one, and a knot acts the round after its first
  group partner acts: in 80 of 128 marked cases for every member, and in 2,280 of 2,624 members in all; each of the
  other 344 acts exactly one round late.
