# A census of small starts joined two at a time

Third direction of `TWO-PATTERNS-20261126-001`, at the owner's word ([request](../owner_request.md)). A check by the
thread, not a registered study; computed; referee pending. It puts [the bench](../bench/README.md)'s readings to
every pair of small starts, where the bench read three patterns chosen by hand.

## The answer

990 pairs of small starts, 17,820 cases, 17,809 read (11 stopped by the clock), each for up to 10 rounds; all but
four to round 7 or further.

- **No pair hears late.** Of the 101,994 marks read, a start's own knots first hear 6,706 in round 1, 3,988 in
  round 2, 1,550 in round 3, 193 in round 4, 49 in round 5 and 4 in round 6, and never hear the other 89,504 in the
  rounds read. The joint descent first hears 24,874, 14,237, 3,207, 296 and 26 in rounds 1 to 5, and none later.
  The census ends without the pair that would have met the stop.
- **Why, under the ordinary count: after the start no knot is made short.** With a meeting, no knot is short in
  any of the 990 pairs, own births are the same as with a stub in every reading (0 of 1,980 differ), and own knots
  hear no mark (0 of 5,670), as on the bench. With a shared distinction and retiring or offshoots, the last round
  with a short knot is round 1 in 624 cases and there is none in the other 366; marks are heard by own knots in
  round 1 or never. Only with waiting do short knots last (start knots that wait: to round 7 or later in 30
  cases), and only there is a mark first heard as late as round 6. A change reaches a knot of a start's own only
  through a cancelled group, a cancelled group needs a short knot, and the ordinary count gives every new knot
  what it is owed.
- **Under a cap of three and "just enough for three" knots are short in round after round, and still nothing is
  first heard after round 5.** A meeting no longer shields a start (936 of 990 pairs have a short knot under a cap
  of three; own births differ from with a stub in 1,167 to 1,203 of 1,980 readings).
- **Slow joint growth is the common case, not the two-knot part's peculiarity.** Call a case slow when knots of
  both are still being made in the last round, a join between own knots and others is still kept then, and the
  knots of both made a round are constant or rise by a fixed step over the last four rounds. Under the ordinary
  count 469 of the 990 pairs are slow with a meeting and 481 with a shared distinction; under a cap of three, 150
  and 541. Small starts mostly do not multiply under the ordinary count; the bench's ring and source do.

So the search finds what the bench found, on every pair of small starts: what the other is crosses in the first
rounds or not at all, and what goes on is the making of joint knots.

## What is searched

The small starts are the census starts of one to three knots of the study of parts that copy themselves: a
connected graph on the knots, one shared distinction for each pair of knots it joins, zero to three loose
distinctions on each knot, at least three places on every knot and one loose distinction somewhere, each start
once up to the graph's symmetries: 1, 3 and 19 starts. Each is taken with one knot named as its site, once for each
class of knots under the symmetries that keep the loose counts: 44 **sited starts**, 990 pairs (a sited start with
itself included). Every pair counts once: that is the weighting of every count below.

Each pair is joined at one step, by a meeting and by a shared distinction, and grown under nine laws with nothing
taken (the ordinary count, a cap of three, just enough for three places; a short knot waits, retires, or makes
offshoots), for up to 10 rounds, with no further round once a round leaves more than 1,500 knots: 17,820 cases.
For each of the two starts in a case ([`census.py`](census.py), on the bench's program): the last round with a
kept join between its own knots and any other; the first round its own births differ from with a stub in the
other's place; and, for a mark at each start knot of the other, the first round its own knots hear it and the
first round the joint descent does.

## Expected (written before the full run; one pair had been run, the two-knot start with itself)

1. **No pair has a mark first heard by a start's own knots after round 6.** The bench found none in 1,577 cases.
   I hold this fairly firmly; one such pair would be the stop.
2. **With a meeting under the ordinary count, own births differ from with a stub in some pairs,** unlike the bench's
   three patterns: census starts need not hold what their own joins ask, so a knot can be short in the first
   round. I expect it in fewer than a quarter of the pairs.
3. **Slow joint growth is not peculiar to the two-knot start.** Call a case slow when its knots of both are still
   being made in the last round read, a join between own knots and others is still kept then, and the knots of
   both made a round grow by the same step over the last four rounds (the two-knot pair: 2 more each round). I
   expect it under the ordinary count with a shared distinction in more than one pair and fewer than a tenth.
4. **Under "just enough for three" no pair has a kept join between own knots and others after round 3.**

## What was found

The whole table is [`census_table.md`](census_table.md) ([`tally_census.py`](tally_census.py) on
[`census_runs.jsonl.gz`](census_runs.jsonl.gz)). Every pair counts once. Readings are two a case (1,980 for 990
cases); marks are 5,670 for each join, ration and treatment.

| join | ration | short knot | cases with a short knot | own births differ from with a stub | marks heard by own knots (latest first round) | by the joint descent (latest) | readings with a join kept in the last round | slow cases |
|---|---|---|---|---|---|---|---|---|
| a meeting | ordinary count | any | 0 of 990 | 0 | 0 | 4,140 (2) | 814 | 469 |
| a meeting | cap of three | waits | 936 | 1,203 | 705 (5) | 2,007 (3) | 214 | 150 |
| a meeting | cap of three | retires, or offshoots | 936 | 1,167 | 300 (5) | 675 (3) | 214 | 150 |
| a meeting | just enough for three | waits | 990 | 676 | 136 (3) | 639 (4) | 0 | 0 |
| a meeting | just enough for three | retires, or offshoots | 990 | 128 | 0 | 0 | 0 | 0 |
| a shared distinction | ordinary count | waits (979 cases read) | 613 | 1,877 of 1,958 | 1,042 of 5,604 (6) | 4,127 (4) | 651 | 323 |
| a shared distinction | ordinary count | retires | 624 | 1,897 | 744 (1) | 4,104 (2) | 675 | 472 |
| a shared distinction | ordinary count | offshoots | 624 | 1,721 | 744 (1) | 4,104 (2) | 675 | 472 |
| a shared distinction | cap of three | waits | 815 | 1,933 | 2,116 (5) | 3,270 (5) | 503 | 324 |
| a shared distinction | cap of three | retires | 815 | 1,911 | 1,843 (3) | 3,364 (3) | 726 | 517 |
| a shared distinction | cap of three | offshoots | 815 | 1,764 | 1,843 (3) | 3,364 (3) | 726 | 517 |
| a shared distinction | just enough for three | waits | 990 | 1,911 | 1,097 (5) | 1,908 (4) | 38 | 24 |
| a shared distinction | just enough for three | retires | 990 | 1,903 | 810 (2) | 1,063 (2) | 50 | 48 |
| a shared distinction | just enough for three | offshoots | 990 | 1,736 | 810 (2) | 920 (2) | 50 | 20 |

## Expectations, and how they fared

1. *No mark first heard by own knots after round 6.* Holds: none, in 17,805 cases read to round 7 or further. The
   latest is round 6, four marks, all under the ordinary count with a shared distinction and waiting.
2. *With a meeting under the ordinary count, own births differ from with a stub in some pairs.* Failed: in none of
   990. I had thought a census start could be short of what its own joins ask; with one to three knots joined
   through each other none is, so the meeting shields every one of them.
3. *Slow joint growth in more than one pair and fewer than a tenth, under the ordinary count with a shared
   distinction.* Failed on the high side: 481 of 990 pairs.
4. *Under "just enough for three" no kept join between own knots and others after round 3.* Failed: 14 cases have
   their last in round 4 and 138 have one in round 10, all with a shared distinction.

## What this does not say

- **Starts of one to three knots, one step apart, ten rounds, nothing taken.** Larger starts, joins further
  apart, later rounds and the take that takes were not run. A census start of four knots or more can be short of
  what its own joins ask, and the shielding by a meeting then need not hold.
- **"Never heard" is in the rounds read.** 89,504 marks were not heard by own knots within 7 to 10 rounds.
- **The sentence about the ordinary count is read off the engine's rule and counted, not proved here.** That a new
  knot is never short under the ordinary count is how the ration is defined; that nothing else can make a change
  cross is the argument of the third step of
  [`FAMILIES-THAT-MEET-20261126-001`](../../FAMILIES-THAT-MEET-20261126-001/third_step/README.md), not refereed.
- **Not run:** 11 cases, each the ordinary count with a shared distinction and waiting, stopped by the clock.
- **Slow is a reading of four rounds.** A case called slow may multiply later, and "other" holds growths that
  rise and fall.

## Runs

`drive_census.py`, 990 pairs, each pair its own run of 18 cases under a memory cap of 8 GB with no swap. A first
launch with a ten-minute stop and the cases in their plain order was stopped by hand after 389 pairs: the case
with the ordinary count, a shared distinction and waiting can take minutes at a few hundred knots, and a pair
stuck there lost the eight cases after it. The 389 finished pairs were kept; the other 601 were run with that
case last and a stop at 150 seconds, twenty at a time, in about a quarter of an hour.
