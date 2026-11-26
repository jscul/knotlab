# How much of a change arrives

Epic `HOW-MUCH-ARRIVES-20261126-001`, at the coordinator's go-ahead on the first direction of the report that
delivered Chapter 11 of the guide ([the request](owner_request.md)). A check by the thread, not a registered study;
computed; referee pending. This file was begun before the full run: the sections "The design" and "Expected" were
written then, after the pilot below, and reviewed by the advisor before anything else was run.

## Why

The owner's lamp has two halves. A lamp twice as far away is seen later, and it delivers a quarter of the power.
Lesson 11.4 of the guide found the first half in the growth: a change spreads at most one step of the map of joins a
round ([Codex's study of how many rounds a change needs](../INFLUENCE-CONE-20261120-001/decision.md), proved, referee
pending). The second half was untested, because the record counts whether and when a change shows and never how much
of it arrives. This study counts it.

## Prior work in the program

`track.py objects` was searched for the share of births that differ after one change, the spread of a disturbance,
damage spreading, and a mark that changes a growth's rate, until 26 November 2026, excluding this epic.

- `INFLUENCE-CONE-20261120-001` (rows 1 to 4): the earliest round at which a change of loose count or of what is
  met can show, sharp; whether, not how much.
- `TWO-PATTERNS-20261126-001` and its referee: under the ordinary count, through a meeting, a pattern's own births
  equal those beside a stub; a mark on one of two two-knot parts gives a whole new table of what they make together;
  moving one loose distinction to the other knot changed 46 of 55 index pairs of that table.
- `SHORT-AGAIN-20261126-001`, `SWITCH-RECEIVERS-20261126-001`, `SECOND-SWITCH-20261126-001`,
  `LINKED-UNDER-CAP-20261126-001`: where a change is heard between patterns from more than one step, it is the end of
  a jam under a ration of one fewer, or a switch of one receiver kind under a cap; whether and when, not how much.
- `LATTICE-NET-20261108-001` (the process line, on a supplied board of rule-60 rings): influence spreads by the
  powers of a Laurent polynomial over GF(2), so cancellation thins it; a board, not the growth.
- `DOUBLE-IDENT-20261119-001`: the growth reads a start only through each knot's live neighbours and each live
  knot's open count.

No record measures how many of a round's births a change alters.

## The pilot (seen before this design was written)

Three starts under the ordinary count, 12 rounds, a mark (one more loose distinction) at each start knot; and four
starts with one loose distinction moved from one start knot to another. Seen:

- two three-place knots sharing a distinction (dimension two): a mark alters 1, 3, 1, 1, 2, 3, …, 9 births in
  rounds 1 to 12, of 5, 6, 5, 6, 8, …, 22; moving a distinction alters all but one each round;
- a bare ring of five (dimension one) and the golden-ratio ring of five: a mark or a move alters every birth from
  round 4 to 8 on, because the changed start grows a different kind of growth (a bare ring with one leftover grows
  one more knot each round; the eddy with one more leftover grows faster than the golden ratio).

## The design (revised once with the advisor, before the full run)

The first draft of this design was sent to the advisor ([question](advisor_question.md),
[answer](advisor_answer.md)). Taken from the answer, before anything below was run in full:

- **Two ancestry-free readings beside the hereditary one** (its point 1). Births named by their parents' names are
  hereditary: once a new birth appears, all of its descendants are new by name, so damage counted by name can hardly
  stay bounded. Each birth is therefore also read by **sig0**, its kind, number of parents, fresh distinctions and
  places, and by **sig1**, sig0 with the sorted sig0 of its parents; the damage is counted in all three readings.
  Only the ancestry-free readings can show a lamp.
- **Damage both ways** (seen while testing the program, before the full run): a change can remove births as well as
  add them, so the damage is c + c⁻, the births of G′ unmatched in G and of G unmatched in G′, against n + n′.
- **A pulse** (its point 2): a mark is a source, since the added distinction is never lost. A pulse marks a knot made
  in round s and, after round s + 1, bars the loose distinctions of the knots made that round that hold the added
  distinction, so the change is struck after one round.
- **Shells** (its point 3): for a change at one knot, each birth is placed by its distance from that knot in holder
  steps, in the structure after its round, and the damage is counted shell by shell.
- **Pairs** (its point 6): two made marks at once in round 2, on two touching knots and chain3, against each alone:
  less than the sum is cancellation, the sum is additivity, more is interaction.
- **Setting B read so that it can weaken** (its point 4): the fraction of far changes that show at all, and the
  share in the first round they show, each as a function of d.
- **Verdicts over the whole series** (its point 5), not four rounds, so a generator's phase cannot pass for a bound.
- Not taken: the advisor's richer signature (the map of joins within one or two steps around a birth); sig1 is its
  one-step form by parents, and the shells give the reading by distance.

**The measure.** A growth G and the same growth G′ with one change. In each round t each birth is read by name (kind,
parents' names, number among equal births of the round, from the start knots' names, as on the two-pattern bench,
with its fresh distinctions and places), by sig0 and by sig1. The **damage** in a reading is c(t) + c⁻(t), the
births of G′ with no match in G that round and of G with none in G′ (differences of multisets), and its **share** is
the damage over n(t) + n′(t), the births of both. A birth of round t is a cluster of t + 1 members of the map of
joins (lesson 8.1), so the round's births are the knots at about t steps from the start, and n(t) is the count the
lamp's sphere stands for. The **descent** is the births of G′ with a changed knot among their ancestors.

**Verdicts,** in each reading, over the rounds read (at least eight), with h the middle round of the series:

- **dies out:** no damage from round h on;
- **takes over:** the damage is at least 0.95 of n + n′ in each of the last four rounds;
- **weakens** (the lamp): the damage at the last round is at most its value at h while n + n′ grew by half or more;
- **bounded** and **grows,** where n + n′ did not grow (a bare ring): damage at the last round at most, or above,
  its value at h;
- **holds:** every other case: the damage grows with the round's count and stays below it.

**Setting A, the model: the ordinary count,** not-all-equal, nothing taken; no knot is ever short there. Starts of
known kind, each grown to round 16 or 20,000 knots:

| start | knots | kind of growth (births per round) |
|---|---|---|
| ring5-bare | five knots in a ring, two loose each | dimension one: 5 a round |
| ring7-bare | seven knots in a ring, two loose each | dimension one: 7 a round |
| two-touching | two three-place knots sharing one distinction | dimension two: 4, 6, 8, … |
| chain3 | three three-place knots in a row | dimension two: 4, 6, 8, … |
| ring5-eddy | five knots in a ring, three loose each | golden ratio: 10, 15, 25, 40, … |
| generator7 | the generator study's seven knots | releases packets (lesson 8.7) |

Changes (`amount.py`): a **mark** at each start knot; a **move** of one loose distinction from one start knot to
another, every ordered pair; a **made** mark at each knot made in round s, s = 2 and 4 (at most the first 40 made);
a **pulse** at the same knots; and **pairs** of made marks in round 2 on two touching knots and chain3. 181 jobs.

**Setting B, supplied (scaffolds, named; `between.py`).** The two settings in which the record hears a change
between patterns, with the earlier studies' starts, joins and laws imported unchanged:

- **B1.** Two seven-knot generators joined by a meeting through d − 1 link knots, d = 1 to 8, under the record's
  "one fewer than asked" with short knots waiting (the jam of `SHORT-AGAIN-20261126-001`; a ration of the record,
  not the made ones of A278). Changes: a mark at each start knot of the far generator. Read in the near generator's
  own births.
- **B2.** The switch receiver of `SWITCH-RECEIVERS-20261126-001` joined by a meeting through d − 1 link knots,
  d = 2 to 5, under the cap of three with waiting (assumption A224), to a far site holding two loose distinctions,
  one holding three, and a stub. Read in the receiver's own births, each far end against each other.
- **B0.** Both under the ordinary count, the control: a pattern's own births are known not to differ there, in any
  reading.

## Expected

Written before the full run, after the pilot of the first draft (marks and moves on four starts, named reading) and
one made-mark case on two touching knots seen while testing the program (there a made mark removed a growing part
of the growth, about one birth more each round).

1. **By name, nothing weakens:** the hereditary reading grows wherever damage appears (nearly forced, as the advisor
   says).
2. **Ancestry-free, a change at a start does not weaken:** marks and moves at a start knot change the kind of growth
   on the rings and the eddy (takes over or holds) and hold on two touching knots, chain3 and the generator.
3. **Ancestry-free, a made mark does not weaken either:** it adds or removes an endless chain or a relay, whose births
   grow with the rounds as the round's count does, so the damage holds in dimension two, holds or grows on the bare
   rings, and holds on the eddy and the generator.
4. **A pulse dies out in most cases** (a majority of the pulses on each start), and where it does not, it holds; it
   never weakens.
5. **Pairs add:** in most pairs the ancestry-free damage of both marks at once equals the sum of each alone at the
   last round read; no pair cancels to less than either alone.
6. **Shells:** a made mark's ancestry-free damage sits in a few shells at the front of the growth (at most three
   shells wide in the last round read), not spread over all shells: a beam, not a glow.
7. **Setting B:** under the ordinary count (B0) no damage in any reading. In B1 the fraction of far marks that show
   is the same at every d (as in the record: under one fewer, two of seven, or all seven) and the share in their
   first round does not fall with d. In B2 the far site with two against three shows at every d, at round 2d + 1,
   with the same first-round share.

**Headline.** No weakening in any setting or reading: the growth has no conserved amount that a change spreads more
thinly with the steps. **Stop:** a case that weakens in an ancestry-free reading of setting A (the lamp's second half
in the model), or every setting read with none.
