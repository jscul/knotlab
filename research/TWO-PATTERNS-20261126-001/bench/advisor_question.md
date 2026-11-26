You are reviewing, cold, a research note before it is committed. Be adversarial: find claims in "The answer" that
say more than the table and the notes under it support, readings whose definition makes a result trivial or
artefactual, and anything that should be checked before this is reported. You cannot see the program; judge from
the note alone. Answer in at most 500 words as a numbered list, each item with the change you would make. Do not
praise. Background: knots hold distinctions; a member is a knot with a loose distinction (held by it alone); two
members are joinable when some knot shares a distinction with both; groups are sets of joinable members; a member
owed more joins than it has loose distinctions is short and its groups are cancelled; a kept group makes a join
(a new knot); a member gives every loose distinction it has to a join or to an offshoot of its own; a new knot
receives fresh distinctions by the ration (the ordinary count: as many as the joins it will be owed).

# A bench for two patterns joined in one start

First direction of `TWO-PATTERNS-20261126-001`, at the owner's word ([request](../owner_request.md)). A check by the
thread, not a registered study; computed on the cases named; referee pending. This file was begun before the first
full run; the section "Expected" was written then, after one case had been seen while the program was being tried
(the ring joined to the copier at one step under a cap of three with waiting).

## The answer

Three lasting patterns of the record, joined two at a time in one start, one to three steps apart, under 36 laws
that use no names: 1,296 cases, 1,277 read, each for up to 12 rounds or 3,000 knots.

- **Joined so that each can afford it (a meeting), under the ordinary count, a pattern's own knots carry on as if
  the other were a stub.** No knot is ever short (0 of 54 cases). Its own births are the same as with a stub in
  every reading (36 of 36), and no mark in the other is ever heard by its own knots (0 of 168). Everything the two
  have to do with each other is in their **joint descent**, the knots that come from both: it hears a mark at every
  start knot of the other but one kind (156 of 168), at the round the influence-cone study gives, one step a round.
- **With a meeting, under a cap of three or "just enough for three places", the two come apart within five rounds** (the last kept
  join between a pattern's own knots and any other is in round 5 with waiting, 3 or 1 otherwise). With waiting
  under "just enough" they stay joined but locked: no join is kept after round 1, and retiring the other by hand
  sets the waiting knots free.
- **Joined by a shared distinction, with nothing supplied for it, knots are short at once and each pattern's own
  births do depend on what is at the other end** (25 to 31 of 36 readings differ from with a stub), and marks are
  heard by a pattern's own knots (up to 36 of 168, under a cap of three with waiting). Every such mark is first
  heard by round 3.
- **Nothing of what the other is arrives late.** In no reading, under any of the laws, is a mark first heard by a
  pattern's own knots after round 6 (the latest is round 6, under the one take that takes), and by the joint
  descent after round 7. So the stop asked for is not met: no pattern here keeps hearing the other.
- **One pair keeps making something together without end, in the rounds read.** Two two-knot parts that share a
  distinction make two joint knots in every round through round 12, with no knot ever short: 2, 4, 6, … 24 joint
  births, 208 knots in all, the same under the ordinary count and under a cap of three (where the cap never
  binds) and under all three treatments. Retire one after round 8 and the other's own births change in round 9.
  This is the other's presence going on mattering, not what it is: a steady line, not a signal.

So on these patterns the roadmap's fifth level is not reached, and the bench says where the two halves of it sit:
what the other *is* gets across early or never, and what lasts is only that the other *is there*.


## What is joined and what is read

Three patterns of the record ([`bench.py`](bench.py), `STARS`): the **ring** of five knots that returns under a cap
of three with waiting; the **copier**, two knots that become two such pairs every two rounds under "just enough for
three places"; and the **source**, the generator study's seven knots, which keeps releasing families under the
ordinary count. Each has one knot named as its site (its first knot).

Two patterns A and B are **joined at n steps**, in one of two ways. By a **meeting**, the generator study's way
and the main one here: two knots meet through one spent knot of three places, and each of the two receives one more
loose distinction, so that it can afford the one join the meeting asks of it. Or by a **shared distinction**, the
form study's way: the two knots hold one new distinction in common and nothing else is added. At one step the two
sites are joined; at two steps a link knot sits between them, joined to each; at three steps, two link knots. A
**stub** is the least knot that can stand where a pattern stood: one knot holding the far end of the join. A
**mark** at a knot is one more loose distinction there. (The second way was the only one when this note was begun.
The second trial case, two sources at one step under the ordinary count, showed that a shared distinction leaves
knots short in the first round under every ration, since nothing is supplied for the joins it asks; the meeting was
added then, before the full run.)

A knot is **A's own** when every one of its start ancestors is a knot of A, and **of B's descent** when any is a
knot of B. Knots are named by how they were made, so that an own knot of A has the same name whatever A is joined
to. For each case, and for each of the two patterns in it, the bench reads:

1. **Joined.** In each round, the groups that hold an own knot of the pattern together with a knot that is not its
   own, and how many of them are kept (make a join). (Counted also: the groups with a knot of the other's descent.
   Beyond one step there are none, since an own knot's partners are children of an own parent; the two patterns
   then deal with each other only through knots that descend from the link.)
2. **Against a stub.** The first round in which the pattern's own births (name, fresh count, places) differ from
   the same pattern joined to a stub at the same steps.
3. **The other retired by hand.** After rounds 2, 4, 6 and 8 every member of the other's descent is retired (its
   loose distinctions barred) and the growth goes on; the first later round in which the pattern's own births
   differ from the whole growth, or none. Under a law that takes nothing this can only be the loss of a kept
   group, so it says the patterns were still making joint knots after that round; it does not say that what the
   other is matters.
4. **A mark in the other.** For each start knot of the other, one more loose distinction there: the first round
   the pattern's own births differ, or none; and the first round the **joint descent** differs (the knots with a
   start knot of each pattern among their ancestors). This is the reading that asks whether what the other is
   gets across, to the pattern's own knots or to what the two make together, and from how deep.
5. **Against the bare pattern.** Through how many rounds the pattern's own members and births, as counts, are those
   of the pattern grown with nothing joined.

Laws: the ration (a cap of three; just enough for three places; the ordinary count), the treatment of a short knot
(waits, retires, makes offshoots), and the take (none, or one of the engine's three takes of a sole candidate,
which use no names). 36 laws, 6 pairs, 3 distances, 2 ways of joining: 1,296 cases, 12 rounds or 8,000 knots. The
972 cases with a take are read without the marks.

## Expected (written before the first full run)

Items 1 to 6 were written with the shared distinction as the only join. Item 1 had already failed on the second
trial case when the meeting was added (the two sources came apart by round 3, their joining groups cancelled); it
is kept as written, and item 7 restates it for the meeting, after the trial case had shown its first two clauses.

1. **Ordinary count.** No knot is ever short. The patterns stay joined in every round read, with kept groups in
   every round, so retiring the other after any round changes the own births. A mark changes the own births, and
   later for a knot further in (the influence-cone study's rule: one step a round).
2. **Cap of three, and just enough for three, with retiring or offshoots.** Joined in the first rounds only: no
   group joins the patterns after round 5 in any case. Retiring the other after round 4 or later changes nothing.
3. **Waiting.** In at least one case the patterns are still joined at round 8 and retiring the other after round
   8 changes the own births. I hold this weakly.
4. **Takes of a sole candidate.** They take in few cases. Where no birth takes, every reading equals the one with
   nothing taken.
5. **Against the bare pattern.** At one step the own counts leave the bare pattern's within two rounds, since the
   site holds one more distinction. No expectation at two and three steps.
6. **The stop.** A pair one of which still changes the other's course late, under a law that uses no names and
   under a swap of ration, would be: a mark deep in the other heard after round 6, under two of the three rations.
   I expect this only under the ordinary count, which would not meet the swap.
7. **The meeting, under the ordinary count** (written after the trial case two sources at one step, which showed
   kept joining groups in every round, the own births the same as with a stub, and no mark heard by the own knots
   in 9 rounds). In every case: no knot short; joined and kept in every round; the own births the same as with a
   stub; no mark heard by a pattern's own knots; every mark heard by the joint descent, later for a knot further
   in. With a cap of three or just enough for three, the meeting changes nothing in items 2 and 3.

## What was found

The whole table is [`bench_table.md`](bench_table.md) ([`tally_bench.py`](tally_bench.py) on
[`bench_runs.jsonl.gz`](bench_runs.jsonl.gz) and [`bench_take_marks.jsonl.gz`](bench_take_marks.jsonl.gz)). A
reading is one pattern in one case; there are 36 for each join, ration and treatment. With nothing taken:

| join | ration | short knot | cases with a short knot | readings still joined at the last round | latest kept join | differ from with a stub | other retired after round 8 changes own births | marks heard by own knots (latest first round) | by the joint descent (latest) |
|---|---|---|---|---|---|---|---|---|---|
| a meeting | ordinary count | any | 0 of 18 | 24 | round 9 | 0 | 2 of 36 | 0 of 168 | 156 of 168 (5) |
| a meeting | cap of three | waits | 18 of 18 | 0 | 5 | 13 | 0 of 36 | 1 of 168 (3) | 49 of 168 (6) |
| a meeting | cap of three | retires, or offshoots | 18 of 18 | 0 | 3 | 7 | 0 of 36 | 0 of 168 | 4 of 168 (3) |
| a meeting | just enough for three | waits | 18 of 18 | 24 | 1 | 0 | 4 of 36 | 0 of 168 | 4 of 168 (3) |
| a meeting | just enough for three | retires, or offshoots | 18 of 18 | 0 | 1 | 0 | 0 of 36 | 0 of 168 | 0 of 168 |
| a shared distinction | ordinary count | waits (14 of 18 cases read) | 12 of 14 | 10 | 12 | 25 of 28 | 8 of 26 | 16 of 119 (2) | 44 of 119 (4) |
| a shared distinction | ordinary count | retires, or offshoots | 16 of 18 | 10 | 12 | 25 | 8 of 36 | 8 of 168 (1) | 36 of 168 (3) |
| a shared distinction | cap of three | waits | 17 of 18 | 12 | 12 | 31 | 8 of 36 | 36 of 168 (3) | 34 of 168 (5) |
| a shared distinction | cap of three | retires, or offshoots | 17 of 18 | 6 | 12 | 25 | 6 of 36 | 10 of 168 (2) | 20 of 168 (2) |
| a shared distinction | just enough for three | waits | 18 of 18 | 18 | 2 | 27 | 3 of 36 | 23 of 168 (3) | 19 of 168 (3) |
| a shared distinction | just enough for three | retires, or offshoots | 18 of 18 | 0 | 1 | 25 | 0 of 36 | 8 of 168 (1) | 7 of 168 (1) |

Where two treatments share a row their counts are equal. Notes on the columns:

- **Still joined, under the ordinary count with a meeting.** The ring's and the source's own knots have a kept join
  with a knot not their own in every round read (24 readings). The two-knot part's own knots have one through
  round 3 only (12 readings): its own knots then go on alone.
- **The other retired after round 8.** With a meeting under the ordinary count this changes the own births only at
  one step, as it must (beyond one step an own knot is never in a group with a knot of the other's descent), and
  there in every reading read past round 8 (2; at the earlier rounds 12 of 12, 8 of 8 and 8 of 8). It says the two
  are still making joint knots, nothing more.
- **Marks, under the ordinary count with a meeting.** The joint descent first hears a mark in round n, n + 1 or
  n + 2 for patterns n steps apart, by how far in the marked knot is. The 12 it does not hear are all at the
  two-knot part's far knot. A mark at a start knot with no loose distinction (the source's second knot) wakes
  that knot as a short member; those are the only readings in which the three treatments differ under the
  ordinary count.
- **Against the bare pattern.** With a meeting at one step, a pattern's own members and births, as counts, are the
  bare pattern's past round 3 in 64 of 108 readings and leave them after round 1 in 44. With a shared distinction at
  one step they differ from round 1 in 90 of 108.

**The takes.** Two of the engine's three takes of a sole candidate (from one, and from two, parent steps above)
never took: 0 births in 648 cases, and every reading equals the one with nothing taken. The third (from a knot the
parent meets) took in 294 of the 309 cases read and changed a reading in 261. Run again with the marks (300 of 324
cases read): under the ordinary count with a meeting a pattern's own knots hear 5 of 168 marks, all in round 1;
with a shared distinction under a cap of three with waiting they hear 41 of 168, the latest first in round 6.
Its table is in `bench_table.md`.

**The stop, in two readings.** *What the other is, late:* a mark first heard by a pattern's own knots after round
6, under two rations: none, in 1,277 + 300 cases; none under one ration either. *That the other is there, late:*
the other retired after round 8 still changes the own births in 49 readings, 18 of them under two rations or
more (a pattern joined to itself counted once). Eleven of the 18 are the two-knot part joined by a shared
distinction to another two-knot part or to the ring, under the ordinary count and a cap of three; between two
two-knot parts the cap never binds (no knot is short), so there the swap of ration is the same growth twice. The
other seven are all with waiting.

## Expectations, and how they fared

1. *Ordinary count (written for the shared distinction).* Failed. Knots are short in 44 of the 50 cases read; the
   patterns are still joined at the last round in 10 of 36 readings only; a mark is heard by own knots in 8 to 16
   readings, by round 2, not later for a knot further in.
2. *Cap of three and just enough, retiring or offshoots: apart after round 5, and retiring the other after round 4
   changes nothing.* Holds for the meeting (latest kept join in round 3) and for "just enough" with either join.
   Fails for the shared distinction under a cap of three: kept joins through round 12 and 6 readings changed by
   retiring after round 8, the two-knot part's steady line.
3. *Waiting: some case still joined at round 8 where retiring the other then changes the own births.* Holds (4, 8,
   8 and 3 readings), but for a reason I had not seen: under "just enough" the knots are locked, not dealing.
4. *The takes take in few cases.* Two never take, and their readings equal nothing taken in all 648 cases, as
   said. The third takes in nearly every case, which I had wrong.
5. *At one step the own counts leave the bare pattern's within two rounds.* In 44 of 108 readings with a meeting,
   90 of 108 with a shared distinction.
6. *The stop would be met only under the ordinary count.* It is not met at all in its strong reading.
7. *The meeting under the ordinary count.* No knot short: holds. Own births the same as with a stub, and no mark
   heard by own knots: hold. Joined and kept in every round: holds for the ring and the source, fails for the
   two-knot part (through round 3). Every mark heard by the joint descent, later further in: 156 of 168, at one
   step a round.

## What this does not say

- **Three patterns, their first knot as site, twelve rounds.** Nothing about other patterns, other sites, or what
  happens after 3,000 knots. "No mark heard after round 6" is in the rounds read (6 to 12).
- **The joins are scaffolds**, both of them, and they give opposite answers on whether a pattern's own knots feel
  the other. The meeting is the generator study's; the shared distinction is the form study's. The stub, the mark
  (one more loose distinction), the rations other than the ordinary count and the treatments are supplied too.
- **Own knots are a strict reading.** A pattern's own knots are those with nothing else among their ancestors. Under
  the ordinary count the influence-cone study counts every knot with an ancestor in the receiver; those are heard
  here as the joint descent.
- **Not run:** 19 of the 1,296 cases and 24 of the 324 of the take's second pass, all under the ordinary count with
  a shared distinction, stopped by the three-minute clock (waiting or short members pile up and one round's roster
  takes minutes). They are not negatives.
- **The steady line is counted, not understood.** Twelve rounds, 208 knots. Whether it goes on, and whether
  anything can be made to ride on it, is not known.

## Runs

`drive_bench.py` ran 1,296 cases sixteen at a time, each its own run under a memory cap of 8 GB with no swap and a
stop at three minutes; then the 324 cases of the one take that took, again with the marks (`take-marks`). A first
launch at a bound of 8,000 knots was stopped by hand after 123 cases, since the cases under the ordinary count
were costing half a minute each ([`bench_first_launch.jsonl.gz`](bench_first_launch.jsonl.gz)): its 246 readings
agree with the final run on every round both read. A second launch was discarded: it ran while the comparison
with a stub was being corrected (the second pattern's knots had been named by their place in the start, so that
it always seemed to differ from itself with a stub), and so mixed two versions of the program.

To run one case: `PROBE_ROOT=<repository> python3 -B bench.py '{"A":"copier","B":"copier","steps":1,"join":"share","ration":"ORD","treatment":"CANCEL-WAIT","take":null}'`.
