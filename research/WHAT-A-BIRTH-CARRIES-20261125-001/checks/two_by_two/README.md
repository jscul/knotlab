# More than a count? A probe of a part that meets two others

Sub-goal B335, 25 November 2026, after the study `WHAT-A-BIRTH-CARRIES-20261125-001` closed. The owner asked for
direction 1 of [its decision](../../decision.md): a class in which a count cannot be the whole difference. **This is a
probe by the thread, not a frozen study.** Nothing was registered beforehand; each program states at its head what was
expected before its first run. The growth, the links and the course are read with
[ticket B's program](../../../../experiments/WHAT-A-BIRTH-CARRIES-20261125-001B/WHAT-A-BIRTH-CARRIES-20261125-001B-E001_link_through_a_made_knot/),
unchanged; one count is repeated without its course reading.

Programs (run from this folder): [the four runs](tbt.py) · [its driver](drive.py) · [the scan for second parts that are not alike](scan.py) ·
[first meetings by round](two_births.py) · [the descent of later meetings](lineage.py) · [the recount](recount.py) ·
drivers [1](drive_scan.py), [2](drive_laws.py), [3](drive_later.py), [4](drive_births.py), [5](drive_lineage.py).
Outputs: [ring starts, four runs](main.jsonl.gz) · [census starts, four runs](census_small.jsonl.gz) ·
[the control](planted.jsonl.gz) · [scan, census](scan_small.jsonl.gz) · [scan, laws](scan_laws.jsonl.gz) ·
[scan, later rounds](scan_later.jsonl.gz) · [first meetings](births_explore.jsonl.gz) · [descent](lineage.jsonl.gz).

## The question

Ticket B found one made part's course changing with another through a knot the growth made, by one count at one birth.
A count cannot be the whole difference where a first part X meets **two** second parts, Y1 and Y2, and its course
either differs with **which** of the two is barred, or takes two values at two births to tell the four cases apart
(neither barred, Y1, Y2, both). So for every part that meets two or more others only through made knots, all wholly
apart after the round at which the parts are chosen, the four runs are grown and the course from X only compared.

## What was read

- **Laws without names**: the take of a sole candidate with ten rations (the three recorded ones, the owing ration,
  its plain form and its other listed forms) and short knots retiring, making offshoots or waiting; two more with the
  fourth listed treatment. Not-all-equal; the four runs on the ring starts under parity as well.
- **Starts**: ticket B's five ring starts, and the 219 census starts of three and four knots.
- **Rounds**: parts chosen after rounds 1 to 4 and read to round 7; for the later readings, chosen after rounds 2 to 6
  and read to round 9 or to 6,000 knots.

## What was found

1. **One count, and it takes as many values as there are second parts.** Under the owing ration and under its plain
   form, with short knots making offshoots, the course from X only is the same whichever one of the two second parts
   is barred, differs from the course with neither barred, and differs again with both barred: on all 2,040 triples of
   the ring starts (both knot laws) and on 3,051 of the 4,251 triples of the census starts read (the other 1,200 show
   no difference at all). One value at one birth separates the cases on every one of them. Recounted without the course reading, on 28 parts with three or more second parts
   (three starts): barring any none, one, two or three of three second parts gives four different courses, the same
   for every choice of which. In the case printed, one knot of X's descent in round 6 has 8, 7, 6 or 5 places, and
   round 7 has 17, 16, 15 or 14 knots from X only.
2. **Never which.** Wherever the course responds, the second parts are alike: a renaming of the structure after the
   round of choosing maps one onto the other and fixes every member of X. That is so for all 6,525 pairs of second
   parts on the 196 census starts run (1,619 first parts, with two to seven second parts each), for all 510 pairs on
   the ring starts under each of the three owing rations without a cap (342 under the cap of four), and for the 126
   pairs found two rounds later. Barring either of two alike parts gives the same run up to renaming, so "which" has
   no test there.
3. **Where the second parts are not alike, the first part does not respond.** With short knots waiting, the first
   part is the part of the waiting members (10 to 14 members) and its second parts are two-member parts in different
   positions around it: 200 pairs not alike on the ring starts under each of seven of the ten rations (the other three
   give no part with two second parts). On the 60 tested with four runs under each, 420 in all, the course from X
   only is the same in all four runs.
4. **Every second part arrives at one birth.** For parts chosen after rounds 2 to 6 on 224 starts (1,120 runs), every
   first meeting of two parts falls in the very next round: 8,838 after round 4 and 5,890 after round 6, counted from
   each side, all only through made knots; 12 after round 5; 78 after round 2, those through start knots; none after
   round 3. No two parts first meet in any later round read. So no second part reaches a first part at a second birth.
5. **Later meetings stay inside one descent.** On 98 starts the parts of the roster after round 6 meet in round 7:
   26,214 meetings counted from each side, and in every one both parts descend from the same single part of the
   roster after round 4. No part of another descent reaches a part's descent at its second meeting.
6. **The control.** Under the rule that looks at parts (81 runs), the course from X only differs with which second
   part is barred on 1,602 triples, and is the same for both on 1,875, of which 1,516 have second parts that are not
   exchanged by any renaming. So the four runs can show a difference by which. Ticket B's reading m calls every one of
   them "handed in one value". **A planted case that needs two values was not built**, so the stop written for B335
   is met only in its first half.

## What it says

In this class, what reaches a made part from other made parts is one number at one birth: how many of the other
branches of the knot it descends from made their join. The parts that meet through made knots are branches of one
knot. They are alike, they all meet in the round after they separate, and parts that do not meet then do not meet
later. Both things the direction asked for need something this class does not hold: parts of different descent that
come to meet, or the same parts meeting at two births. The take of a sole candidate reaches only a knot the parent
meets, which is why. So the finding is about the listed laws, and it names what a law would have to do: let parts
that do not descend from one knot come to meet, without names.

## Not run, and limits

- **A probe.** No pre-registration, no referee. One program (ticket B's) reads the course; the recount uses a weaker
  signature (knots from X only, by round and number of places). The scan's test of likeness is the thread's own.
- **Not run**: 23 of the 219 census starts in the scan (over 120 seconds each); in the first sweep with four runs,
  the census starts after the first 71 (stopped at thirty minutes) and 16 of those 71; two of the five ring starts
  two rounds later; 20 starts stopped by the knot bound before round 8 in the reading of later meetings. None of
  these is a negative.
- **Tested with four runs**: at most 12 pairs that are not alike in each run, 420 of 1,400.
- **Too short to read** in the count of first meetings: 9, 20 and 49 of the 224 runs for parts chosen after rounds 4,
  5 and 6 (stopped by the knot bound). A first meeting is looked for through at least two rounds past the next one.
- **Not examined**: 1,200 triples of the census sweep under the owing ration show no difference at all; why those
  first parts do not respond.
- **"As many values as second parts"** is counted to three second parts barred; parts with four to seven were not
  barred beyond three.
- **No knot test** was run on the barred runs of this probe.
- **Finite**: rounds to 7 or 9, starts of three and four knots and five rings.
- Nothing here is about living things, minds or physics.
