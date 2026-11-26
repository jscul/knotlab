# A made pattern that, on meeting a second pattern, leaves two of the second? Result

Ticket `MADE-COPIER-20261125-001A` of the copier study (lead B327; assumptions A244 and A248; goals G15 with G17 and
G18), 2026-11-25. Computed by an engine written from the frozen text by a helper that had not seen the drafter's
prototype, then checked by a second helper that recounted the raw results and reran the claimed cases with readings of
its own. Evidence class of everything here: **computed, bounded, referee pending.**
[Pre-registration](preregistration.md) · [claim](../MADE-COPIER-20261125-001/claim.md) ·
[definitions](../MADE-COPIER-20261125-001/definitions.md) · [the owner's arm](../MADE-COPIER-20261125-001/owner_arm.md) ·
[code and its recorded readings](../../experiments/MADE-COPIER-20261125-001A/MADE-COPIER-20261125-001A-E001_made_copier/deviations.md)

**No copier was found, in any of the three readings of "two of it", for any registered class of second patterns, base
law and stated choice rule. Under not-all-equal no made distinction is ever tied to another, so the values reading
cannot hold there from these starts. Under the ration of COPY-LAW(t) (the name the study of parts that meet again gave a ration and a
treatment; it is not a law of copying) every knot made after the start's own offshoots holds at most one loose distinction, so the part that copies itself
stops and no part of its kind is made again. Under parity a value of every second pattern can be tied at two loose places
made by the first pattern, but only in histories of takes that were picked, and under one stated rule it happens once:
for one second pattern, numbered one way, and it is gone when the start is renamed. Under the two rations where parts
like the second pattern are made again, two of one second pattern appear in one case under the taking rule of the claim,
and that case is there with that second pattern and not with the first pattern alone, is no copier for any other
pattern of the class, and is gone when the start is renamed. So this ticket reaches neither arm of the owner's stop: there
is no copier with a class it works for, and no reason that no made pattern can under parity.**

The words used: a **law** is the rule the growth follows; the **first pattern** X (the candidate copier) and the
**second pattern** Y are parts the growth or the start supplies; **two of it** is read three ways (two parts the same as
Y; two renamings of Y's knots among the made knots; two usable loose made distinctions tied to one place of Y). The
laws are named as in the study of parts that meet again (`PARTS-MEET-AGAIN-20261124-001`, "the earlier study" below): COPY-LAW(t)
and FBP(t) give a birth just enough fresh distinctions for three places, FBP counting by parents; CAP-3(t) caps them at
three; t says what a short knot does (retires, makes offshoots, or waits); MET lets a birth also take a shared
distinction held by a knot its parent meets, STEPS-1 one held one parent step back; OLDEST and NEWEST take the smallest
or largest name, IN-TURN goes by the order of births, BY-COUNT by the parent's number of places as a position among the
candidates sorted by name. The starts are named in the study's data file; this note says what each is when it uses it:

| Name in the data file | What it is |
| --- | --- |
| made-h (h = 2 to 6) | two start knots sharing one distinction, the second holding h loose distinctions; their round-1 offshoots are X (two knots) and Y (h knots); made-2 is the control with Y the same as X |
| Y present from round 0, of kind one-2, one-3, two-22, two-23, two-33, three-222 | the three-knot start's two founders (X) with their dead knot, and a second dead knot sharing one distinction e with the first and meeting Y's members: one member holding two; one holding three; two holding two each (the control); two and three; three and three; three holding two each |

> **Referee report R1, 26 November 2026: confirmed with fixes, no block**
> ([the report](../MADE-COPIER-20261125-001/referee-R1/report.md)). No registered class passed the copier test. The
> values case failed all four renumberings; the main form case failed two of three; a form case under the take by
> parent steps survived 28 added numberings under each knot law and failed for the class. Three of the arguments
> this ticket leans on are narrowed in the report (no tie from two holders needs the knot law; "a knot holding barred
> distinctions has no children" needs its start conditions; a changed take need not show in the first pattern's next
> round).

## Verdicts

Thirty-four predictions and the owner's reading were frozen. Twenty-four hold, two fail, eight are reported with no
prediction, and the owner's reading is only supported. The two failures are replications of the prototype's counts in the owner's arm, and both trace to one
reading of which round a confirmation is read at (next section). No verdict about a copier depends on them.

| # | Verdict | What was found |
| --- | --- | --- |
| P0 (gate) | Holds | Runs grown through the study's wrapper equal those of the earlier study's engine in 384 of 384. Tie classes equal those of every assignment on 600 drawn structures under both knot laws; sameness and renamings of Y's knots equal brute force (571 pairs, 411 cases); 105 sets of knots placed by hand are each found exactly once. 29 of 29 unit tests pass. Rerun by the checker: identical. |
| P1 (check of an argument) | Holds | In 216 runs under COPY-LAW(t) with the three taking rules, every birth receives one fresh distinction (none when implied under parity), except offshoots of start knots and, under the rule that takes two parent steps back, offshoots of knots whose parents are all start knots. |
| P2 (check of an argument) | Holds | Under not-all-equal no tie class holds a made distinction, in every run and history read: 1,728 runs A at every round, the other runs at their last round and 80,032 drawn or listed histories (counts per run in the engine's summary). The 60 starts with a third pattern have no tie at round 0. |
| P3 | Holds | No part the same as the two-knot part after round 3 under any taking rule (576 runs); with no taking rule, the counts of the data file in 18 of 18 runs under each knot law. |
| P4 (the owner's step 2) | Holds | Every record check passes: 3,659 parity structures and 14,459 parts; 80,811 listed and 3,690 drawn not-all-equal structures; the piece of the seven-knot pattern with its three tied distinctions; the counterexample to "any start". |
| P5 (check) | Holds | 24 parts the same as a member of a class with a member made after round s, all Y's own round-1 offshoots of a start knot; no renaming of Y's knots among the made knots in 576 runs (in none of 1,728). |
| P6 | Holds | Exactly one of 1,728 runs (checker's rerun: the same one): the start with Y present from round 0, three members holding two each, under COPY-LAW(CANCEL-OFFSHOOT) with MET(NEWEST) and parity. Two made distinctions descended from X only are tied to a loose place of one of Y's members at round 6. |
| P7a, P7b, P7c | Hold | That case survives holding and demand before the takes; is lost under the other three rules; is lost under each of the four renamings. |
| P7d | Reported | Lost under the other eight base laws, the other taking rule, the order of births reversed and the other knot law. |
| P8a | Holds | The 33 registered take lists replay exactly: the listed two, at the listed round, every knot passing. |
| P8b | Reported | Every choice of takes, drawn under the take-by-take weighting where there are more than 60,000 histories: histories with two of a place of Y made by X are found under COPY-LAW(CANCEL-OFFSHOOT) for all 11 starts (18 to 249 of 20,000 each), and in none under the other five base laws. No history stopped at the guard. |
| P9 | Reported | Pooled over the 11 starts under that base law (take-by-take weighting, 220,000 histories): two tied to a place of Y, made by X, in 1,158; by Y only, 8,938; to a place of X, made by X, 5,198; by Y only, 94. Recounted by the checker for three starts: identical. |
| P10 | Holds | Under not-all-equal no knot fails. Under parity every failing knot is a join (34 failing verdicts in the main runs, 31 in 28 of the 1,158 drawn histories with two, 19 in 8 runs of the swaps; the last kinds found by the checker's rerun, the result file keeps only their count); the two methods never disagree; every counted case passes. |
| P11 | Holds | C(r, b) holds for none of the 48 pairs of rule and base law: one member of one class before the renamings, none after. |
| P12 | Holds | CF(r, b) holds for none. The one case under the claim's taking rule is in the next section. |
| P13 | Holds | Parts the same as Y are made for made-3 to made-6 and for one-2, one-3 and three-222; two-23 and two-33 are dropped. The census counts differ from the prototype's for three members (next section). |
| P14 (check) | Holds | With no taking rule on the two-knot start both readings count exactly the numbers of the earlier study's engine at every round 2 to 7 under the three treatments; each structure placed by hand is found, one more. |
| P16 (check) | Holds, with nothing to check | No case made by X only meets condition 2 of the copier. |
| P17 | Reported | X's course differs with what Y is in 164 of 864 pairs of runs (made starts) and 203 of 1,440 (starts with Y present from round 0), as disclosed; on the parts by descent 132 and 474. |
| P18 | Reported | Under MET, X's course always differs from X alone; under STEPS-1 in 144 of 288, 72 of 144 and 0 of 432. |
| P19 | Reported | The second pattern hands on its own value in 9 parity runs, the same with X barred; Y returns in 30 runs, 80 with X barred. |
| P20 | Holds | With one member holding two instead of three, all three takes of round 3 by X's births take Y's fresh distinction, and after round 6 X's three usable loose made distinctions are tied to three different start distinctions. |
| PO1 (check) | Holds | In 1,728 runs and 478 pairs no relation among X's distinctions changes and no birth without a parent in X takes a usable loose distinction of X. Under not-all-equal the relation is read over at most 12 distinctions (708 of 864 runs had a round read so). |
| PO2 | Holds | Under the rations FLOOR0 and ONE-FEWER, births descended from Y only change the relation on X's distinctions in 68 runs, and in each a knot fails at that round. |
| **PO3 (replication)** | **Fails** | Y's course with X barred is confirmed through a meeting in 359 runs; 357 disclosed. Every other count is reproduced. |
| **PO4 (replication)** | **Fails** | Of Y's, the first take after the course difference in 64; 62 disclosed. The same two runs. |
| PO5, PO6 | Hold | Reading (ii) in exactly the 3 listed runs, its reverse in exactly the 9 listed. |
| PO7 | Holds | With Y the same as X, X and Y end in the same round in all 144 runs of each naming; takes in one direction only exactly where listed. |
| PO8 (check) | Holds | Where every history is read, the counts of the two patterns' states are unchanged when they are exchanged; drawn counts are reported and some differ. |
| PO9, PO10 | Reported | Reading (iii) in 70 runs, its reverse in 8; reading (iv) as disclosed (in the owner's section). |
| POA (the owner's) | Only supported | (i): no copier at all. Readings (ii) to (iv) are reported and called support for nothing. |

The checker's recount differs from the engine's in no number. It differs in four descriptions, given where they arise.

## The two failures and the three disagreements

**PO3 and PO4: at which round a confirmation is read.** The two runs are the start with one second-pattern member
holding two, under (CAP-3, CANCEL-OFFSHOOT, RELEASE) with MET(NEWEST), one under each knot law. Run A stops at the fold
engine's guard in round 5, so the last round every run of the reading reached is round 4. Y's course in the run with the
two patterns kept from joining equals its course with X barred through round 4, and differs from it at round 5 by a
take. The definitions say both that "every comparison is made at" that last round (D 7.1, the owner's arm) and that
"comparisons are through the last round every run of the comparison reached" (D 4.9). The engine followed the first and
reads "through a meeting"; the prototype's count follows the second. The replay listing supports this account (the
checker compared the listed courses round by round). The registered verdict stays **fails**: these are replications, and
a miss is a finding about the engines and an ambiguity in the text, not about the claim.

**The census of the form classes: which run a class member's "Y after round s" comes from.** Here made-4 15 runs,
made-5 7, made-6 34; disclosed 13, 6, 11. All the extra runs are under the cap of three, where the offshoots of a start
knot with five or six loose distinctions receive three fresh distinctions each, so the member's own Y has members
holding three. Taking each member from its own run under the same law gives the engine's numbers; taking it from its run
under COPY-LAW(t) with the same treatment and rule gives exactly the disclosure. The checker counted both with its own
readings and got both sets of numbers. The frozen text does not say which; the same-law reading fits the claim's "one
law, the same for every member of the class". The same members are made and dropped either way, so P13 holds either way.

**Every choice under the cap of three: the guard.** The prototype saw the guard of the earlier study's engine stop 4,867, 5,000 and
5,000 of its drawn histories of made-4, made-5 and made-6 under (CAP-3, CANCEL-OFFSHOOT, RELEASE); the engine saw none
in 20,000 each. The checker read the prototype's code: to list a round's candidate takes it grows the round once on a
copy with every take set to the oldest candidate, and a guard stop there ends the history. Run on the registered
generator, that probe of round s + 4 meets the pairs guard (21,000 to 97,000 joinable pairs, all births having taken one
distinction), while the history's own round s + 4 does not. The definitions count a history as stopped when its own round
stops (D 2.7), so the engine is right, and those three designs are read through round s + 4 here, with no history having
two. The prototype read them only through round s + 3. Not settled: whether any of the remaining drawn rounds meets the
guard (the engine counts none; the checker sampled 2,000 for made-4).

**A fourth difference, found by the checker.** The prototype seeded its draws with the law's name written with
"MET(OLDEST)"; the definitions register the name written "MET(every choice)". With the prototype's seed the checker
reproduces the registered take lists of made-4 at its 84th, 187th and 211th histories; with the registered seed, none.
So the disclosed counts of drawn histories are of other histories than the registered generator draws. The engine uses
the registered seed. Nothing registered depends on it: P8b and P9 are reported, and P8a replays the lists by their takes.

## The cases with two of Y

**Values, under a stated rule (P6).** On the start with three second-pattern members holding two each, under
COPY-LAW(CANCEL-OFFSHOOT) with MET(NEWEST) and parity, two usable loose distinctions made by births descended from X
only are tied to a loose place of one of Y's members at round 6 (that place has one holder after round 0 and seven at
round 6). Both are later taken by different births and stay tied through round 8. With Y's members barred after round 0,
two others are tied to a different place of Y, one Y's member shares with Y's dead knot, so the case does not need Y's
births. With X barred, the second pattern hands on nothing of its own. Every knot passes.

- Who made the two: births descended from X only.
- What fixed the takes: a stated rule whose case is lost under each renaming of the start, under each other rule and
  under each other base law. NEWEST picks by name, so the start's numbering decides.
- Where X and its link come from: X is a start pattern, joined to Y through a start distinction.
- **Supplied.** Only the births that carry the value are made.

**Form, under the claim's taking rule (P12).** On made-4 (Y four knots holding two each) under FBP(CANCEL-OFFSHOOT), the
ration with the fresh count by parents, with MET(BY-COUNT), under each knot law: two parts the same as Y, every member
descended from X only, at round 5 and at no other round. X and Y are one part at rounds 2 and 3. The checker reran it
with its own readings:

- X alone (X's start knot with the shared distinction barred) makes no part the same as Y at any round, and its course
  differs from X's in the run with Y from round 2.
- With Y's members barred after round 1, X's births make the same two at round 5 and X's course is the same: the case
  needs Y's knots, not Y's births.
- With made-3, made-5 or made-6 as the second pattern, those runs hold at most 0, 1 and 1 parts the same as made-4's Y,
  and none of them gets two of its own: a copier for no other member of the class.
- It survives the renaming that draws a permutation of the labels, and is lost when the names are reversed or X's labels
  are put after Y's. **Supplied**: the start, the rule BY-COUNT (which counts by the parent's places but indexes the
  candidates sorted by name) and the numbering.

**Form, under the second taking rule (reported).** On the same start and base law, STEPS-1 with NEWEST and with BY-COUNT
each leave two parts the same as Y made by X only. In the registered numbering X alone makes the same two, X's course is
the same as in X alone, and X and Y are never one part: these are X's own course, with nothing met. One of them passes
the three registered renamings; the next section is about it.

**The control with Y the same as X.** Two parts the same as Y appear on made-2 and on the same start with the names of X
and Y exchanged, under one base law with STEPS-1(BY-COUNT); X alone makes them too.

## What this shows and does not show

- **Supplied in every case**: the starts and the classes, built by hand; the stated choice rules, all four of which use
  the start's names; the naming convention and its four renamings; the take lists, which are picked histories; the base
  laws, the taking rules and their bounds; the take-by-take weighting and its seeds; the bounds of six rounds (eight for
  the two-users reading), 500 knots and the guard of the earlier study's engine. Every verdict here is about these scaffolds as much as
  about the growth; the swaps say which survive (the previous section, and the run of swaps: no case beyond the made-4 ones and the
  controls under the renamings, the order of births reversed, demand before the takes or holding).
- **"No copier" is bounded** by one first pattern (the two-knot part, made or present from round 0), the registered
  classes of four and five second patterns, four stated rules, two taking rules under the claim and six rounds. It is no
  argument that no made pattern can leave two of what it meets, and under parity the question is not decided.
- **What is settled by argument**, and checked on finitely many runs: under COPY-LAW(t) no part with a member holding two
  is made after the start's own offshoots (the ration's doing, saying nothing about copying); under not-all-equal, from a
  start with no tie, no made distinction is ever tied, whatever the takes.
- **Under parity the knot law allows a value of each second pattern at two loose places made by X**, under one base law
  and in picked histories (18 to 249 of 20,000 drawn under the take-by-take weighting, a weighting that is not uniform
  over histories). Under the other five base laws none was found: in full where there are at most 60,000 histories, and
  otherwise only in 20,000 drawn, which is a sample, not every choice.
- **The form arm has no every-choice control**: its negative says that four stated rules and their swaps leave no two of
  a class, not that the law forbids it.
- **What a second pattern changes**, under the registered laws: no place and no relation among the first pattern's
  distinctions (an argument, checked in every run over at most 12 distinctions under not-all-equal); it changes the first
  pattern's course, in 652 of 1,728 runs.

## Added after the freeze: a wider family of numberings

Not registered; added on the thread's instruction because passing three renamings does not show that the takes are
not fixed by names. The one case that passes the registered renamings, made-4 under FBP(CANCEL-OFFSHOOT) with
STEPS-1(NEWEST), was run under 28 numberings of its start under each knot law: each of the 7 shifts of the order of
its 7 distinctions, with the names given in that order or reversed, with the two start knots in either order. These are
28 different named starts. The case passes all 28 under each knot law (engine and checker agree).

The checker found a qualification the engine's summary lacks. In 8 of the 28 (the registered numbering among them) X and
Y are never one part and X's course is X alone's. In the other 20, the reversed names among them, X and Y are one part
at round 2, X's course differs from X alone's from round 3, and the two parts appear at round 5, a round before X alone
makes them. So "X's own course" describes 8 of the numberings, not all. It is no copier in any of them: in the run with Y,
Y's own births make 32 parts of Y's form by round 6, the runs with made-5 or made-6 as the second pattern hold 42 and 50
parts the same as made-4's Y, and no other member of the class gets two of its own. Passing every numbering here says
that this ration and rule make parts of this form from any start knot's offshoots. It says nothing about meeting.

## The owner's inkling, kept apart

His words (24 November 2026), recorded as assumption A248: "it's actually impossible to generalize a 'copier' for all logic
structures. It might be the case that some logic models are able to over-write the instructions of the copier and break
out." These readings are reported apart from the evidence for the claim, as the frozen claim requires, and none is
called support for his second sentence, whose object is a copier.

- **(i)** No first pattern, law and stated rule is a copier for any member of a registered class: no copier at all. That
  only supports his first sentence, since the classes are finite and "all logic structures" is not. The case of the last
  section has two made by X under a rule that survives the registered renamings; it fails as a copier because the other
  members do not get two of their own and their runs hold parts of its form, not because of the names.
- **(ii)** In 3 runs the first pattern has ended while the second still makes births, and had not ended by the same
  round with the second barred; the reverse in 9 (as disclosed). In one of the three the run is cut off at round 5 by
  the guard.
- **(iii)** In 70 runs the first pattern's course differs with whether the second is there while the second's does not
  differ with the first; the reverse in 8.
- **(iv)** A third pattern named before the second removes the one values case, which returns when the third is barred;
  named after, the case is gone too, and with the third barred the two are tied to a place of the third. It follows the
  names, as the case does. Under the registered take lists a third pattern removes nothing where the list still applies
  (154 of 180 runs).
- Under the registered laws a second pattern changes no place and no relation among the first pattern's distinctions,
  only its course. Only under the rations FLOOR0 and ONE-FEWER did births descended from Y only change that relation (68
  runs), and in every one a knot fails the knot test at that round.

## The knot test

Every knot was tested under the run's own knot law as registered (by the engine's count, 896,939 verdicts under parity
and 849,181 under not-all-equal in the three main runs, besides the replayed lists and the drawn histories with two). Under
not-all-equal none fails. Under parity every failing knot is a join, and both methods agree. Every case
counted in this note passes. Start knots fail only under the rations FLOOR0 and ONE-FEWER, which can give a birth nothing.

## Deviations and limits

- **Readings recorded by the engine's author: 51.** Two decide registered numbers without changing a verdict about a
  copier: which round a confirmation is read at (PO3, PO4 fail under it) and which run a class member's reference comes
  from (P13's counts). Two were recorded after a first pass of the run they affect and before it was redone: a repair
  of the controls placed by hand (P14 first failed, then held under the definitions' own wording), and leaving a round
  unread where its roster meets the guard, as the frozen bounds say (8 runs of the swaps, all at round 6, none at a law
  with a case). The code for ties under not-all-equal was made faster three times while runs went on, with the same
  partition checked on several hundred structures. The deviations file is not under version control, so the dates of
  its earlier entries cannot be checked.
- **Not kept in the result files**: the kinds of failing knots in the run of swaps (found by the checker's rerun: all
  joins); every drawn history (the counts are kept, and the checker's recount of three starts agrees); the courses of the
  two PO3 runs past round 4 are in the replay listing only.
- **The checker did not recompute** courses (traces), ties under not-all-equal, or the drawn counts of 8 of the 11
  starts.
- **Everything is finite**: 11 starts and their renamings, 6 rounds, at most 500 knots a run, 20,000 drawn histories a
  design and law.
- **Evidence class**: computed by an engine written from the frozen text; the claimed cases and the counts of runs A
  reproduced by a second set of readings written by the checker; two arguments (the ration's doing; not-all-equal from a
  start with no tie) checked on every run. Scientific referee pending.
