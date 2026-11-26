# The ring that returns at one end of a waiting line: does a change pass each time it comes round?

> **Refereed (R1, confirmed with fixes, no Block): the narrowings are in the notice of [the decision](decision.md).**

Direction 1 of [the report at the first checkpoint](report_1.md) of `SHORT-AGAIN-20261126-001`, taken up without a
new word from the owner (his standing rule: a selected direction is run). A check by the thread, not a registered
study; computed; referee pending. Program: [`ring_line.py`](ring_line.py).

## What is read

**The start.** The seven-knot source (A, the receiver) and the ring of five knots (B) joined at their first knots
through d − 1 link knots, d = 1 to 8, by a meeting (the far table's join) and, as a swap, by a shared distinction.
Beside it, the same source with a stub where the ring was.

**Laws**, a short knot waiting in each: a cap of three (the ring's law: the two added rules under which it
returns); the record's "one fewer than asked" (the ring study's, none at least where three places are given), under
which the bare ring also returns; ONE-FEWER and JOIN-FEWER (the two made rations that carried the far table, one at
least); and the ordinary count. 16 rounds or 3,000 knots.

**The ring's returns** are read as the ring study defines them: a part of B's own knots after round s, with five
members or more, returns at the least t > s at which the members that descend from it include a part the same as it
up to renaming, each member's usable and barred counts kept. A part made of the very same knots (all waited) is not
a return, since a part whose knots all wait is the same after every round.

**Changes.** One more loose distinction at a member of the ring's part each time it returns, at each member in turn,
for its first six returns; where the ring does not return, after rounds 2, 4, …, 12 at the five members of B's own
knots nearest (in sharings) to a knot that is not B's own. Read the first later round in which the source's own
births differ from the growth without the change. **Sent again:** in the growth with the first change that was
heard, a second change the round after it was heard (the five members nearest the line, each), compared with the
growth with the first change only; then a third.

**Also read:** the source's own births with the ring and with the stub, round by round; the rounds in which they
differ; births and short knots by whose knot it is (A's own, B's own, link side, joint).

**Stop** (as the report gave it): the source's own births differ again after each return, three times (a signal that
repeats); or the line passes once and stops (the line is spent by use).

## Seen before the full run

Trial cases, d = 1 and 3, by a meeting, every law (`ring_line.py run`), and the bare ring:

- The bare ring returns every two rounds under all four waiting laws (its five-knot phase at even rounds, its
  ten-knot phase at odd). Joined by a meeting to a stub, it no longer returns under any of them in 12 rounds.
  Joined to the source, it returns under the cap of three at d = 1 (from round 3) and not at d = 2 or 3.
- Under the cap of three the source's own births are **the same with the ring as with a stub** in every round, at
  d = 1 and 3. No change at the returned ring (45 at d = 1) is heard.
- Under JOIN-FEWER at d = 3 the source makes nothing of its own in rounds 2 to 5 with the ring, and 2 to 4 with a
  stub; after that its own births are the same numbers in both, the ring's one round later (8, 16, 21, 37, 54, 91,
  119). No change at the ring after round 2 is heard. Under both one-fewer rations at d = 1, with a stub the source
  makes nothing of its own after round 1 through round 16; with the ring, from round 5.

Found on the way, in the far table's own records (`far.jsonl.gz`): without a change, the two sources and their
line make **no knot at all after round 1**, through round 16, under JOIN-FEWER, ONE-FEWER and BUSY-FEWER with waiting
(every member short in rounds 2 to 16; the 32 to 53 knots at round 16 are the start and its round-1 births). With a
mark at the other source the structure grows again (at d = 4: 4,766 knots at round 11). The note said the structure
"barely grows"; it does not grow at all until something frees it. That is logged as a correction, and the study
in [JAM.md](JAM.md) asks whether hearing from afar is always the end of such a jam.

## Taken from the advisor's review

[Question](advisor_question_2.md), [answer](advisor_answer_2.md) (asked of the Fable model named in the program's
rule; it answered). Taken: a returned part must descend from the earlier part alone, since in a growth that
multiplies a part the same as the ring can turn up by coincidence; a second change is placed at a current member,
never at a knot that has acted. Noted: item 4 below is nearly implied by the jam reading, so it carries little
information by itself; and a hearing in the exploded growth after a first change may come by the growth near the
receiver rather than along the line (not traced here).

## Expected (written before the full run, after the trial cases above)

1. **The ring comes back only under its own law, and not at every distance.** Under the three one-fewer rations no
   part of the ring's own knots of five or more returns at any d, by either join; under the cap of three, at some d
   and not others.
2. **Under the ring's law the source does not feel the ring.** Its own births are the same as with a stub at every
   d by a meeting, and no change at the returned ring is heard at d ≥ 2.
3. **Under the one-fewer rations what passes is one number: when the source starts making knots again.** The
   source makes nothing of its own from round 2 until a round that depends on what is at the other end. Where it
   starts again both with the ring and with a stub, its own births are then the same numbers, shifted.
4. **The line passes once and stops.** No change at the ring after round 2 is heard by the source at d ≥ 2 under
   any law, and nothing is sent again.

If the ring returns under a one-fewer ration and a change at each of three returns is heard, item 4 fails and the
stop's first half is met.

## What was found

All 80 runs were read (8 distances, 5 laws, 2 joins; 8 to 16 rounds each); the table is
[`ring_line_table.md`](ring_line_table.md) ([`tally_ring_line.py`](tally_ring_line.py) on
[`ring_line_runs.jsonl.gz`](ring_line_runs.jsonl.gz)).

**The stop met is the second: the line passes once and stops.** No change set at the ring in round 2 or later is
heard by the source at two steps or more: 0 of 1,855, under every law and both joins. At one step, by a shared
distinction, one change is heard under each one-fewer ration (set after round 2, heard in round 4), and a second
change after it is not.

- **The ring comes back only under its own law.** Under the cap of three it returns by a meeting at d = 1 (11
  returns, from round 3) and by a shared distinction at d = 2 to 8 (11 or 12 returns each). Under the three
  one-fewer rations and the ordinary count it never returns once joined, at any distance, by either join.
- **Where it comes back, nothing it does reaches the source.** None of the 45 changes at the returned ring is heard
  in any of the eight starts where it returns. By a meeting the source's own births are the same as with a stub at
  every distance but two (where the ring does not return, and they differ from round 3).
- **Under the one-fewer rations, by a meeting, what passes is one number.** With the ring at the far end the
  source makes nothing of its own from round 2 to round d + 2 under JOIN-FEWER and to d + 3 under the two others;
  with a stub there, to d + 1 under all three. Then it starts again, and from there its own births are the same
  numbers with the ring as with the stub (21 of 21 starts, three rations, d = 2 to 8), one round later under
  JOIN-FEWER and two under the others. The delay is the ring's: with the ring at its end every knot of the line is
  still short in round 2 (and under the two one-fewer rations in round 3), because the ring's own knots near the
  line are waiting, while with a stub the line's far knot acts in round 2. At d = 1 the source and a stub jam each
  other for good, and the ring frees the source (round 4 or 5).
- **By a shared distinction** the source is never jammed under these rations; its own births differ from those with
  a stub from round 1 or 2 at d = 1 to 5 under every law but the ordinary count's meeting, as the bench found for that
  join (it leaves knots short at once), and are the same at d = 6 to 8.

## Expectations, and how they fared

1. *The ring comes back only under the cap of three, not at every distance.* Holds.
2. *Under the cap the source does not feel the ring.* Holds for the changes (none heard); for the births, at every
   distance but two by a meeting. By a shared distinction they differ at d ≤ 5 from the first rounds: that is the
   join, not the ring.
3. *Under the one-fewer rations one number passes.* Holds by a meeting at every d from 2 to 8.
4. *The line passes once and stops.* Holds. The ring does not come round under the rations that carry, and where
   it comes round, the line does not carry.

## What this does not say

- The ring was joined at one knot, by the two joins of the bench; a ring joined so that its returns reach the line
  in some other way is not excluded.
- "What passes is one number" is read from the source's own births, 13 to 16 rounds, one sender and a stub; it is
  not a statement about every sender (the jam study reads more of them).
- The scaffolds are those of the far table (the made rations, A278; the meeting, the link knots, the change, A277),
  plus the record's one fewer and its cap. Swapped here: the join, five laws, eight distances. The result is about
  this line under these laws.
