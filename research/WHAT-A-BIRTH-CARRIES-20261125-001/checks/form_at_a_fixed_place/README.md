# The place held fixed, the form changed: a third probe of "more than a count"

Sub-goal B335, 25 November 2026. [The second probe](../reach_further/README.md) ended on what its runs could not say:
whether a part's course responds to what a second part is, as against where and when it arrives, because no test held
the place fixed and changed the form. The owner asked for that test and gave leave to explore. **This is a probe by
the thread, not a frozen study.** Nothing was registered beforehand; each program states at its head what was expected
before its first run, and two of those expectations were wrong.

Programs (run `make_engine.py` first; it writes the engine into this folder): [the starts, the two readings and the classes](form.py) ·
[its driver](drive_form.py) · [single changes at one depth](depth.py) ([driver](drive_depth.py)) ·
[the checks](checks.py) · [how long start knots act](startknots.py) · tallies: [by law](summ_form2.py),
[in full](summ_form.py), [depth](summ_chains.py), [single changes](summ_depth.py), [when pairs are first told apart](late.py),
[what decides the class](features.py).
Outputs: [the mixed family](form_b.jsonl.gz) · [the chains](chains_a.jsonl.gz) · [single changes](depth_a.jsonl.gz) ·
[the family not seen beforehand](unseen.jsonl.gz) · [checks](checks.jsonl.gz).

> **Referee report R1, 26 November 2026** ([the report](../../referee-R1/report.md)): this probe's counts are
> recounted (4 to 23 classes with the bare start counted, 3 to 22 without); four statements are narrowed.
> - "A single knot against anything longer" holds in 10,800 of 10,800 comparisons among chains and fails in 445 of
>   16,560 in the mixed family.
> - Finding 4's "through made knots alone" does not follow from rosters with no start member after round 1: a start
>   knot that has left the roster can still supply a distinction or witness a group.
> - "About half of those": 2,938 of 6,077 for differences first seen in round 2, and 6,521 of 9,852 for rounds 2 to
>   7. What is the same there is a multiset of birth kinds, counts and descent flags, not every fact of round 1.
> - The fate count on the second family is 62 studies of 90 on a common round, not 71.
> The registered study that followed supplied the wider record and the unlinked control
> ([its result](../../../FOLLOWS-THE-FORM-20261125-001A/results.md)).

## What the record already had

Ticket A of this study found that the first pattern's first join receives two fresh distinctions and one more for
each birth the second pattern makes that round, and that courses separate exactly where that count differs. Its
second pattern varied only by which of its members a bar left usable. The study of parts that meet again found that
what crosses is whether the other part is there. No record substitutes one form for another at a fixed place.

## The test

A start is built from a **first seed**, one **link** distinction, and a **second seed** that holds the link on one of
its knots. The first seed and the place of the link are held fixed while the second seed runs over a family of forms.
Each start is grown under one law, and what the first seed's own descent does is read: the knots descended from the
first seed's start knots and from none of the second seed's.

- **Two readings.** Ticket B's course from the first part only, unchanged; and a plainer one written here, *what it
  makes*: its births round by round, each by kind, number of parents, places, fresh distinctions and takes. Two
  second seeds are in one class when the reading is the same through the last round.
- **First seeds**, five: one knot; two knots; a ring of three; a chain of three held at its end; the same chain held
  in the middle.
- **Second seeds.** A mixed family of 50 (one knot, two knots, chains of three held at the end or the middle, rings
  of three, with 0 to 5 loose distinctions a knot), and 62 chains of one to five knots with 2 or 3 loose
  distinctions a knot. Every start knot has three or more places.
- **Laws**: the ordinary count, the cap of three and "just enough for three places", with short knots retiring,
  making offshoots or waiting; each with no taking rule, and with the take of a sole candidate. Not-all-equal,
  9 or 10 rounds. 10,260 runs, and 3,420 more on a family not seen beforehand (below).

## What was found

1. **What the first part makes follows the form of what it is attached to, under every law, the recorded ones with
   no taking rule included.** Among the 50 forms and the bare start, the first seed's own births fall into 4 to 14
   classes with no taking rule and 4 to 23 with the take of a sole candidate, depending on the law and the first
   seed. Ticket B's course gives the same or one or two more. Of the pairs of forms, 59% to 83% are told apart.
2. **What it becomes differs: it ends, idles or grows.** Under the ordinary count with short knots retiring and no
   taking rule, from the first seed of two knots: attached to a single knot of any size its own line grows (4, 4, 4,
   5, 6, 7, 8, 9, 10 births a round); attached to any pair of knots it settles at one birth a round (3, 2, 1, 1, 1,
   ...); attached to a full ring of three it ends by round 3 (2, 1, 0, ...); seven classes in all. Over the five
   first seeds under that law (255 runs), the first seed's line ends in 75, holds steady in 67 and grows in 113.
3. **It is more than one count, and it goes on after the first contact.** Most pairs of forms are told apart in
   round 1, but not all:

   | Taking rule, short knots | Round 1 | Round 2 | Round 3 | Round 4 | Rounds 5 to 7 | Never | Not read further |
   | --- | --- | --- | --- | --- | --- | --- | --- |
   | none, retiring | 9,837 | 1,053 | 43 | 0 | 0 | 7,442 | 0 |
   | none, making offshoots | 10,962 | 1,053 | 43 | 0 | 0 | 6,317 | 0 |
   | none, waiting | 10,611 | 1,659 | 1,292 | 96 | 0 | 4,717 | 0 |
   | sole candidate, retiring | 11,765 | 719 | 7 | 0 | 0 | 5,755 | 129 |
   | sole candidate, making offshoots | 13,123 | 763 | 9 | 0 | 0 | 4,296 | 184 |
   | sole candidate, waiting | 12,352 | 830 | 1,571 | 224 | 490 | 2,646 | 262 |

   (18,375 pairs of forms a row: 1,225 pairs for each of three rations and five first seeds.) Under the cap of three
   a birth receives at most three fresh distinctions, and the classes still number up to 18.
4. **From round 2 the difference travels through knots the growth made.** Where short knots retire or make
   offshoots, a start knot is a member of the roster in round 1 only, in all 3,000 runs counted. So the pairs first
   told apart in rounds 2 and 3 there (1,096 under each with no taking rule, 726 and 772 with the take of a sole
   candidate) reached the first seed's descent through made knots alone.
5. **How deep it sees: the near end in detail, the length further out.** On the chains, pairs that differ in one
   knot's loose count (2 against 3), by how many steps that knot is from the link knot, and pairs that differ by one
   more knot at the far end, told apart over the five first seeds:

   | Law | Depth 0 | Depth 1 | Depth 2 | Depth 3 | Depth 4 | 1 knot v 2 | 2 v 3 | 3 v 4 | 4 v 5 |
   | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
   | no take, ordinary count, retiring | 56/155 | 0/150 | 0/140 | 0/120 | 0/80 | 20/20 | 8/40 | 0/80 | 0/160 |
   | no take, cap of three, retiring | 87/155 | 60/150 | 0/140 | 0/120 | 0/80 | 20/20 | 8/40 | 0/80 | 0/160 |
   | no take, cap of three, waiting | 89/155 | 74/150 | 4/140 | 0/120 | 4/80 | 20/20 | 8/40 | 0/80 | 4/160 |
   | sole candidate, ordinary count, waiting | 99/155 | 64/150 | 4/140 | 0/120 | 0/80 | 20/20 | 36/40 | 64/80 | 80/160 |
   | sole candidate, cap of three, waiting | 87/155 | 40/150 | 12/140 | 15/120 | 9/80 | 20/20 | 24/40 | 56/80 | 98/160 |

   (Five of the eighteen laws; the others are in the output.) With no taking rule the first part sees the link knot,
   whether it has a neighbour, and under the cap of three that neighbour's count. With the take of a sole candidate
   it tells a chain of four knots from one of five in up to three fifths of the pairs. It does not read the whole
   form: the 62 chains fall into far fewer classes than 62.
6. **Which lines it draws depends on the first seed.** Two first seeds do not sort the forms the same way: under the
   ordinary count with retiring, the one-knot and two-knot first seeds both tell 733 pairs apart, one only 243, and
   neither 249. One line is drawn from every first seed under every law: a single knot against anything longer.

## Repeated once on first seeds and forms not seen

Before anything above was written up, a second family of 37 second seeds (larger single knots and pairs, other
chains and rings, a knot with three arms held at its centre or at an arm) and five new first seeds were fixed in the
program with three predictions, and run once under the same eighteen laws ([output](unseen.jsonl.gz)).

| Prediction, written first | Outcome |
| --- | --- |
| For every law and first seed, what the first seed's descent makes falls into three or more classes among the forms | **Fails in one study of 90**: one first seed (a ring of three) under the ordinary count with offshoots and no taking rule gives two. The other 89 give 3 to 30. |
| Under each of the four rows with short knots retiring or making offshoots, some pairs of forms are first told apart in round 2 or later | Holds: 900, 864, 433 and 200 pairs, all in round 2. |
| In at least half of the studies the first seed's line has two or more of the fates "ends", "steady", "grows" | Holds: 71 of 90. |

With no taking rule 69% to 81% of the pairs of forms are told apart, with the take of a sole candidate 81% to 85%.

## What it says

Hold the place fixed and change the form, and what a part makes changes with it: in kind (it ends, idles or grows),
in many classes, by more than one count, and partly through knots the growth made. That is the thing the two earlier
probes could not show. It is shown here **on starts built by hand**: the second seed is part of the start and the two
seeds are joined from the first round, so the meeting is supplied. What remains for the owner's fold is the same thing
between two parts that the growth made and that meet through a knot the growth made. The earlier probes found such
meetings, and there the second parts had the same form near the first part, so nothing could follow it.

## How it was checked

- **Two readings.** The plainer one gives the class counts above; ticket B's course, read on the same runs, gives
  the same count or up to two more in every study.
- **Renumbering**: on three studies (150 runs), every start with its distinctions renamed and its places and knots
  shuffled, three seeds each: what the first seed makes is the same in 450 of 450.
- **The knot test** on every knot of every round of those 150 runs: 103,934 verdicts, none failing, none untested.
- **Every start knot has three or more places.** A first run that included 16 second seeds with a knot of two places
  was discarded and the family rebuilt.

## Expected before the runs, and what happened

- "The course separates forms by a count at the first contact": held.
- "Whether it goes on separating them is not known; under laws with no taking rule perhaps not at all": wrong. With no
  taking rule 1,096 to 3,047 pairs a row are first told apart after round 1.
- "Where short knots wait, a change at every depth is seen, later for deeper knots; under the other laws only depth 0
  or 1": half right. With no taking rule nothing past depth 1 is seen to speak of, waiting or not; with the take of a
  sole candidate, the cap of three and waiting, changes at every depth to 4 are seen in some pairs, and not later for
  deeper knots.

## Not run, and limits

- **A probe.** No pre-registration, no referee, one growth engine (ticket B's, with the second probe's recorded
  changes); the thread wrote the starts, the plainer reading and the checks.
- **Built starts**, five first seeds, two families of second seeds. Nothing is sampled, and no weighting is claimed.
- **The meeting is supplied.** The two seeds share a start distinction.
- **Not run**: the fourth check study passed its time limit; the taking rule that reaches further (it passed 280
  seconds on its first trial); parity; more than 10 rounds. Under the take of a sole candidate with the ordinary
  count some runs are stopped by the engine's guard, and classes are counted at the last round every form reached
  (3 to 6 there, 9 or 10 elsewhere).
- **"Ends, idles, grows"** is read from the last three rounds of nine.
- Nothing here is about living things, minds or physics.

## Report as sent (2026-11-25, about 23:05 UTC)

**The gap is bridged on starts built by hand. Hold the place fixed, change the form of what a part is attached to, and what the part makes changes with it: its own line ends, idles or grows. This happens under the laws we already had, with no taking rule added. It is not yet shown between two parts the growth itself made.** This was a third probe of my own, not a registered study.

The test: one first seed, one link distinction, and a second seed that I swap through a family of forms while the first seed and the place of the link stay the same. Then I read what the first seed's own descent makes.

- **What a part makes follows the form of what it is attached to.** Among 50 forms, the first seed's own births fall into 4 to 14 classes with no taking rule and 4 to 23 with the take of a sole candidate. Between 59% and 83% of pairs of forms are told apart.
- **What it becomes differs in kind.** Example, under the ordinary count with short knots retiring and nothing added, from a first seed of two knots: attached to a single knot its line grows (4, 4, 4, 5, 6, 7, 8, 9, 10 births a round); attached to any pair of knots it settles at one birth a round; attached to a full ring of three it ends by round 3.
- **It is more than one count, and it goes on after the first contact.** Most pairs are told apart in round 1, but 1,096 to 3,047 pairs in each row of the table are first told apart in rounds 2 to 4 with no taking rule, and as late as round 7 with the take of a sole candidate.
- **The later differences travel through made knots.** Where short knots retire or make offshoots, start knots act in round 1 only, so anything first told apart after that reached the first seed's descent through knots the growth made.
- **It sees the near end in detail and the length further out, not the whole form.** With no taking rule it sees the link knot, whether that has a neighbour, and sometimes the neighbour's count. With the take of a sole candidate it tells a chain of four knots from one of five in up to three fifths of the pairs.
- **Which forms it tells apart depends on the first seed.** Two first seeds do not sort the forms the same way. One line is drawn from every first seed under every law: a single knot against anything longer.

I then fixed a second family of 37 forms and five new first seeds in the program, with three predictions, and ran it once. Two held. One failed in one study of 90: I predicted three or more classes everywhere and one first seed under one law gives two.

Checks: renumbering changes nothing (450 of 450); the knot test passes on every knot of the 150 runs checked (103,934 verdicts). Two of the three things I expected before the first runs were wrong, and the README says which.

The limit that matters: the meeting here is supplied. The two seeds share a start distinction, so this is a part responding to the form of what the start attached it to. The two earlier probes found meetings the growth made, and there the second parts had the same form near the first part, so there was nothing to follow.

| Scope | Verdict | Why |
| --- | --- | --- |
| This attempt — the third probe of sub-goal B335: the place fixed, the form changed | **Status:** Partially successful | On built starts a part's making follows the form of what it is attached to, in kind, by more than a count, partly through made knots. Not shown between parts the growth made. |
| Local direction — form-following on built starts | Continue | The result is a probe's; a registered study with an independent engine would make it one of the record's. |
| Broader exploration — the owner's fold of emergence | Known alternatives | The same between two made parts meeting through a made knot; the third property; the copier study. |
| Long-term goal — G15 Learning: a point in a learned knot pattern, with G18 Comparing growth laws | Capability gained | What a part makes is shown to follow the form of what it is attached to, in kind and by more than one count, where the record had one count or one bit. |

**Next step:** Continue — selected: #1

| # | Direction | Payoff | Concreteness | First step → stop when | Status |
| --- | --- | --- | --- | --- | --- |
| 1 | A registered study of form-following on built starts | 3/3 — it would put "what a part makes follows what it meets" in the record, refereed | 3/3 — the starts, readings, families and predictions exist | Freeze the families, laws and predictions; an engine written from the frozen text by a helper; referee → the class counts and the late pairs reproduced, or a counterexample | Selected · awaiting go-ahead |
| 2 | The same between two parts the growth made, meeting through a made knot | 3/3 — it is the fold's own setting | 1/3 — the made meetings found so far have second parts of one form | Search the census runs for two starts whose made first parts are alike through a round and whose made second parts differ → one such pair with courses that differ, or none | Alternative · deferred |
| 3 | What decides whether the first part ends, idles or grows | 2/3 — a rule there would say what a part "reads" | 2/3 — the 255 runs of one law are in hand; the rule is not | Tabulate fate against the form within two steps of the link → a rule that fits every run, or the smallest exception | Alternative · deferred |

Direction 1 moves G15 and is ready to freeze; its main uncertainty is whether an engine written by someone else reproduces the plainer reading. It needs a helper, which is why it waits for your word. Direction 2 is the real remaining gap and I do not yet have a way in. Direction 3 is cheap and would turn the example into a statement.

**GO**, on your word, for direction 1. What the probe taught: the dependence on form was there under the recorded laws all along, and the earlier studies missed it because they varied whether a second part was present, never what it was. The registered study would say whether that survives an independent engine and a referee; it stops at the class counts reproduced or at the first counterexample.

**Corrections:** none to earlier claims. Two expectations written before the runs failed, and one prediction failed in one study of 90; those are results.
**Goals:** no checkpoint row (no study closed). B335 carries the three probes.
**Assumptions:** one scaffold entered, A258 (starts built from two seeds joined by one link distinction). The study of parts that meet again said that in no case did a part's course depend on what the other part is; that stands for its own class and is no longer the whole picture.
**Scaffolds:** added: the built starts (A258). Swapped: the first seed (ten), the family of second seeds (three), the ration (three), the treatment of short knots (three), with and without the take of a sole candidate. What survived: what the first seed's descent makes differs with the form of the second seed. What did not: which forms are told apart, which changes with the first seed and the law.
**Basket:** directions 1 and 2 are recorded on B335; direction 3 is in this report only.

> **Correction, 25 November 2026, later the same day (narrowing; raised by the advisor's review of the registered
> study).** "Ends" above counts births descended from the first seed and from none of the second. A birth with a
> parent of each descent leaves that count. With no taking rule on the mixed family, every line that reads as ended
> (372 runs, the example of the full ring of three among them) is **taken up**: births with a first-seed ancestor go
> on, each also of the second seed. Lines with no births at all occur with the take of a sole candidate (370 runs on
> that family) and on the second family (109 runs with no taking rule). The registered study splits the two:
> [its definitions](../../../FOLLOWS-THE-FORM-20261125-001/definitions.md), FF 7. Also from that review: a pair first
> told apart in round 2 can be one round-1 count held in a knot of both descents, so "through made knots alone" says
> little; about half of those pairs still differ when every round-1 birth with a first-seed ancestor is the same.
