# Is hearing from afar the end of a jam?

> **Refereed (R1, confirmed with fixes, no Block): the narrowings are in the notice of [the decision](decision.md).**

Directions 2 and 3 of [the report at the first checkpoint](report_1.md) of `SHORT-AGAIN-20261126-001`, read
together: why the source hears along a line and the ring does not, and whether the made rations matter at all.
A check by the thread, not a registered study; computed; referee pending. Program: [`jam.py`](jam.py).

## Why

In the far table's own records the two seven-knot sources and their line make no knot after round 1 under
JOIN-FEWER, ONE-FEWER and BUSY-FEWER with waiting: every member is short in every round from 2 to 16, and so waits.
The ring study calls a roster in that state **jammed**: it has members and the round makes no birth. With a mark at
the other source, one knot can pay; it acts and leaves the roster, what its neighbours owe falls, they act in turn,
and the receiver's own knots make knots again, later the further the mark. So what the far table heard may be
nothing about what the other is, only the end of a jam. If so, the ring, the two-knot part and the small starts do
not hear along a line because they are never jammed: under these rations they multiply.

## The rule under test

Say that a pattern's own knots are **jammed in a round** when the pattern still has members and every one of them
is short and waits (the record's word, said of a pattern's own knots rather than of the whole roster).

**The rule.** Under waiting, a change two or more steps from a pattern's site reaches its own knots (their births
first differ) only in a round in which its own knots are jammed in the growth without the change or in the growth
with it.

It is stated from the far table and the trial cases below, and tested here on starts it was not stated from.

## What is read

- **Receivers and senders:** the census's 44 sited starts of one to three knots (`census.py`, `sited`) and the
  bench's three patterns (the ring, the two-knot part, the source; the ring and the two-knot part multiply under
  the one-fewer rations), every ordered pair, and a stub as sender for each: 2,256 pairs.
- **The join:** by a meeting through two link knots (d = 3), the far table's join; other distances and the shared
  distinction on a sample (below).
- **Laws**, a short knot waiting: JOIN-FEWER and ONE-FEWER (made, rations.py); the record's "one fewer than asked"
  and its cap of three (direction 3: does a ration of the record's own carry as the made ones did?); "just enough
  for three places" (FLOOR1); the ordinary count. And JOIN-FEWER with a short knot retiring, the control: a knot that
  retires leaves, so nothing stays jammed. 12 rounds or 1,500 knots.
- **Changes:** one more loose distinction at each start knot of the sender and at each link knot (as the far
  table), and, of the other sign, one of its usable loose distinctions barred there. A change's distance is its number of steps from the receiver's site: k for the k-th link knot, d plus its
  sharings from the sender's site for a start knot of the sender.
- **Read:** for the growth without a change and with each: the receiver's own members and own short members in
  each round, its own births; for each change, the first round its own births differ, and whether its own knots
  are jammed in that round with and without the change.

## Seen before the full run (six pairs, d = 3, every law)

- Source to source: under JOIN-FEWER the receiver's own knots are jammed from round 2 to 12; seven of the sender's
  start knots and the second link knot are heard, rounds 5 to 8, each in a round in which the receiver is jammed
  without the change and not with it. ONE-FEWER and the record's one fewer agree with each other (two of the
  sender's knots, the second link knot). Cap of three and the ordinary count: never jammed, nothing heard from two
  steps or more. FLOOR1: jammed from round 2 to 12, and **nothing heard**.
- Ring to source, two-knot part to two-knot part, two small starts: never jammed, nothing heard from afar.
- A one-knot start receiving from the source: under JOIN-FEWER not jammed and nothing heard; under both one-fewer
  rations jammed, and it hears the same three changes the source does.

## Taken from the advisor's review

[Question](advisor_question_2.md), [answer](advisor_answer_2.md). The advisor's view, to be checked, not a result:
the rule is not forced by the round's rules and the test is not empty. A far change can travel only by turning some
knot short or not short, and only knots that wait carry anything from one round to the next; but the last knot of
such a chain need not be the receiver's own. Two ways it can fail: a **partial jam** (one own knot waits while
another of the receiver's knots grows), and a **mixed neighbour** (an own knot that is not short shares a group with
a knot of both descents whose shortness the change turns, so the own knot makes an offshoot in place of a join).
Taken into the design:

- **The denominator.** A receiver jammed in every round of the baseline makes nothing, so any change that frees it
  is heard "in a jam" by definition. The table separates receivers jammed in every round from 2 on, jammed in some
  rounds only, and never jammed, and counts the far changes in each; the rule has content only in the last two.
- **A weaker rule beside it**: a far change is heard only in a round in which some own knot of the receiver waits,
  in one of the two growths (the advisor's "a waiting own knot"; not called jammed).
- **The other sign.** Every change tried so far adds a loose distinction. Each is now also tried with one usable
  loose distinction barred there instead, to see whether a jam can be sent as well as ended.
- **A stub as sender** for every receiver: whether hearing depends on what the sender is at all.
- **The shortfall** (what a short knot owes less what it holds) of every short knot, each round: the advisor's
  reading of why FLOOR1 jams without thawing is that under the one-fewer rations every shortfall is one, so one
  neighbour leaving frees a knot, while under FLOOR1 shortfalls of two or more occur.
- **Other distances and the other join**, on a sample of 400 ordered pairs drawn with seed 20261126 (`jam.py`,
  `sample`): d = 2 and d = 5 by a meeting, d = 3 by a shared distinction.
- **Receivers that multiply** reach the knot bound in fewer rounds; the rounds read are given beside them.

Not taken: the per-knot form of the rule (every own birth that differs has a parent, or a group partner of a
parent, that waited the round before), which needs every birth traced; and the advisor's structural check of
whether a line can carry a second change, which the ring-line study reads by running it.

Seen in three trial pairs after these changes (source to source, source with a stub as sender, a one-knot start
receiving from the source; d = 3): barring a loose distinction ends a jam as adding one does (a knot left with
none leaves the roster, and what its neighbours owe falls); with a stub as sender, one more loose distinction at
the stub **starts** a jam in the source that the bare stub would have ended (heard at round 5, jammed with the
change and not without); the source's shortfalls are all one under the one-fewer rations and two to four under
FLOOR1, as the advisor said, but the one-knot start has shortfall one under FLOOR1 and still hears nothing.

## Expected (written before the full run, after the trial pairs above)

1. **The rule holds without exception.** Every change at distance two or more that a receiver's own knots hear is
   heard in a round in which they are jammed in one of the two growths. One exception at distance three or more
   refutes it. Where it fails, the weaker rule (a waiting own knot) holds.
2. **A change heard from afar ends a jam far more often than it starts one.** Starting one is seen only where the
   sender would otherwise have ended the receiver's jam (a stub, or a start that stays small).
3. **Being jammed is not enough.** Under FLOOR1 receivers are jammed and hear nothing from afar; under the
   one-fewer rations most receivers that are jammed hear something from afar (more than half).
4. **The made rations are not needed, the cap is no carrier** (direction 3). The record's one fewer gives the same
   pairs hearing from afar as ONE-FEWER (they differ only where a knot is given three places and asked for one);
   under the cap of three no receiver is jammed after round 2 and nothing is heard from three steps or more. So the
   lever is "one fewer than asked" with waiting, not a ration made for the purpose.
5. **The control.** With retiring no receiver is jammed in two rounds running, and nothing is heard from three
   steps or more.
6. **Who hears.** Receivers that multiply under a ration (the ring and the two-knot part under the one-fewer
   rations) are never jammed and hear nothing from afar from any sender.

## What was found

All 2,256 pairs were read at three steps by a meeting (15,792 cases), and the sample of 400 at two and at five steps
and at three by a shared distinction (2,800 cases each), 10 to 12 rounds each; none was stopped by the clock. Tables:
[`jam_table.md`](jam_table.md) ([`tally_jam.py`](tally_jam.py)) and [`jam_by_distance.md`](jam_by_distance.md)
([`tally_jam_by_distance.py`](tally_jam_by_distance.py)), on `jam_*.jsonl.gz`.

**By a meeting, under one fewer than asked with waiting, the rule as stated fails and its weaker form holds.**

| d (pairs) | law | changes heard from three steps or more (of) | in a round with none of the receiver's own knots jammed | with none of its own knots waiting |
|---|---|---|---|---|
| 3 (2,256) | the record's one fewer | 696 of 13,207 | 348 | **0** |
| 3 (2,256) | ONE-FEWER | 672 of 13,207 | 420 | **0** |
| 3 (2,256) | JOIN-FEWER | 43 of 13,207 | 0 | **0** |
| 5 (sample) | the record's one fewer / ONE-FEWER / JOIN-FEWER | 406 / 401 / 34 of 3,939 | 221 / 267 / 0 | **0 / 0 / 0** |
| 2 (sample) | the record's one fewer / ONE-FEWER / JOIN-FEWER | 44 / 29 / 2 of 1,539 | 35 / 23 / 0 | **1 / 0 / 0** |

- So the whole pattern need not be jammed: a far change gets in through **own knots that wait**, in 2,326 of the
  2,327 far hearings under these rations by a meeting. Under all three, every short knot falls short by exactly one
  (480,000 of 480,000 at d = 3).
- The weaker rule is not empty, but it is weak: in every pair some own knot of the receiver waits in some round
  after the first. What it adds is that the hearing comes in such a round.
- **Ending and starting.** Of the far hearings at d = 3 under the one-fewer rations, the change ends the receiver's
  waiting in 193 and 198, starts it in 186 and 205, and both growths wait in 293 and 293; at d = 5 ending is the
  larger share (174 and 183 against 40). Barring a loose distinction is heard as often as adding one (392 against
  280 at d = 3), since a knot left with none leaves the roster and what its neighbours owe falls.

**Who hears is a matter of the receiver.** At d = 3 the same eight receivers hear from three steps or more under
both one-fewer rations, each from 47 of the 48 senders (the stub included); the other 39 hear from none. They are the
source, the one-knot start and six starts of two or three knots, every one with its site holding three loose
distinctions; but 13 other receivers whose site holds three do not hear, so this is not yet a rule. Under JOIN-FEWER
only the source hears (from 23 senders). The ring and the two-knot part hear nothing from three steps or more by a
meeting at any distance read (at d = 5 they hear a link knot two steps away, 12 cases).

**Direction 3: the record's own ration carries as the made one does.** The record's "one fewer than asked" and the
made ONE-FEWER give the same eight receivers, and differ in 40 of the 704 changes heard from three steps or more at
d = 3 by one or the other (32 heard only under the record's, 8 only under the made one). The made rations of A278 are therefore not needed for this; the
record's ration, itself a swap of the ring study's added rules (A224), does it. Under "just enough for three places"
(FLOOR1) receivers wait in every pair and nothing is heard from three steps or more (816 changes at two steps); some
of its short knots fall short by two to six (about one in ten), as the advisor said. Under the ordinary count and with
retiring, nothing is heard from two steps or more. **Under the cap of three, one receiver hears from three steps or
more, by another way** (next section).

**By a shared distinction, everything is different.** Under every law of the sample, the ordinary count and retiring
included, 27 to 42 receivers hear from three steps or more, every one by round 7, and the weaker rule fails in 58 to
145 far hearings per law (`jam_by_distance.md`). A shared distinction leaves knots short at once (the bench found
it); what reaches a receiver then is early and goes by no waiting knot. So the rule is about the meeting: a scaffold
(the joins of `TWO-PATTERNS-20261126-001`), swapped here, and the result changes with it.

## The one receiver that hears under the cap: it switches its way of growing

Under the cap of three with waiting, 77 changes three or four steps away are heard at d = 3, all by one receiver:
the three-knot start g7:122 (three knots each sharing with the other two, holding one, two and two loose
distinctions), sited at its knot with one. None of its own knots waits before it hears. It was read again under a
swap of each scaffold ([`switch.py`](switch.py), [`switch_table.md`](switch_table.md) by
[`tally_switch.py`](tally_switch.py); 120 swaps of 48 senders, 16 rounds or 3,000 knots, all read).

- **Two ways of growing.** With nothing at the other end that changes it, the receiver's own knots make 3, 4, 5, …
  knots in rounds 1, 2, 3, … (two more than the round) and none is ever short. From some round on, with some senders,
  they make many more instead (13, 16, 31, 36, 52, 62 at d = 3), and own knots are short every other round.
- **The round grows two per step, and the sender decides.** By a meeting under the cap of three, the receiver leaves
  the first way at round 2d + 1 with 18 of the 48 senders, at 2d + 3 with 2, and never (through round 16) with 28:
  rounds 5, 7, 9, 11, 13 at d = 2 to 6, the same 18, 2 and 28 senders at every distance. The 18 are exactly the
  senders whose site holds two loose distinctions; every sender whose site holds three, and the stub, leave it alone;
  of the nine whose site holds one, two (both of three mutually sharing knots) switch it two rounds later. Changes at
  the sender's start knots and at the link knots switch it on or off: heard from three steps or more 11, 77, 145, 213
  and 281 times at d = 2 to 6, the latest first in round 15.
- **How it gets in.** Not by waiting. The receiver's site keeps joining knots of the link side, which are owed three
  joins and hold three. In the round the switch comes, those partners are owed four, and the cap gives them three:
  they are short, the joins with the receiver's site are cancelled, and the site makes offshoots of its own instead
  (the advisor's "mixed neighbour" route, with knots of the link side). What the sender is decides whether the link
  side's knots beside the receiver come to be owed four, and when.
- **Swaps.** What a short knot does (waits, retires, makes offshoots): the same counts in all three. A cap of four:
  the receiver leaves the first way at round 3d + 2 (rounds 8, 11, 14 at d = 2 to 4; after round 16 at d = 5 and 6),
  with 5 senders of the 18; changes are still heard from three steps or more at every d (20 to 62). The receiver's
  other site (its knot with two loose distinctions): it leaves the first way in round 2 with every sender, and hears
  nothing from three steps. A shared distinction for the meeting: it leaves the first way in round 1 with every
  sender. The ordinary count (no cap): nothing heard from two steps or more (the jam table).

So under a cap, by a meeting, this one receiver hears what is at the far end of the line late and from afar: whether
the sender's site holds two loose distinctions, at round 2d + 1 under a cap of three and 3d + 2 under a cap of four,
at every distance tried (2 to 6), under every treatment of a short knot. This meets the stop of the two studies before
this line ("a mark first heard by own knots after round 6") and this epic's ("heard at every distance tried, under a
law that uses no names"), in a different way from the first checkpoint: the receiver is growing, not stuck. What does
the work is the cap: it is about the cap of the ring study (A224, a scaffold), the meeting, and one receiver of 47.

## Expectations, and how they fared

1. *The rule holds without exception.* Fails as stated: at d = 3 the receiver's own knots are not all short in 768
   of the 1,411 far hearings under the one-fewer rations. Its weaker form (some own knot waits) holds by a meeting
   under these rations: no exception at d = 3 or 5, one in 75 at d = 2. Under the cap of three every far hearing is
   an exception to both (another way in), and by a shared distinction both fail under every law.
2. *A change from afar ends a jam far more often than it starts one.* Holds for the whole pattern (414 and 548
   against 123 and 176, distance two included); for waiting own knots, ending and starting are about equal at d = 3
   (193 against 186) and ending leads at d = 5 (174 against 40).
3. *Being jammed is not enough.* Holds: under FLOOR1, 144 jammed receivers and nothing heard from three steps; under
   the one-fewer rations every jammed receiver hears something from two steps or more (144 of 144, 192 of 192).
4. *The made rations are not needed; the cap is no carrier.* The first half holds (the record's one fewer gives the
   same eight receivers; 40 of 704 far changes differ). The second fails: under the cap of three one receiver hears
   from every distance tried, by the cap's own way.
5. *The control.* Holds: with retiring nothing is heard from two steps or more by a meeting.
6. *Who hears.* Holds by a meeting: the ring and the two-knot part hear nothing from three steps or more.

## What this does not say

- **Twelve rounds or 1,500 knots** (16 or 3,000 for the switch). A receiver that would hear later is counted as not
  hearing.
- **Who hears has no rule yet.** Eight receivers of 47 under the one-fewer rations, one under the cap; a site with
  three loose distinctions is common to the eight but not enough.
- **What is heard is little.** Under the one-fewer rations, that a waiting own knot is freed or held, and when;
  under the cap, one property of the sender's site knot. Neither is a description of the sender as a whole.
- **Scaffolds:** the meeting (by a shared distinction the result changes), the link knots, the change (one loose
  distinction added or barred), the stub, the strict reading of own knots (A277); the one-fewer rations (made, A278,
  and the record's); the cap (A224). Swapped: seven laws, two joins, three distances, both signs of change, 47
  receivers and 48 senders, and for the switch the cap's value, the treatment and the site.
