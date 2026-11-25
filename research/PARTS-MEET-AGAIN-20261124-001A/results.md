# Can parts that have come apart become one part again, so that one part's course depends on another? Result

Ticket `PARTS-MEET-AGAIN-20261124-001A` (lead B317; assumptions A223 and A241; goals G15 with G17 and G18), 2026-11-24.
Computed with an engine written from the frozen text by a helper that had not seen the drafter's prototype; scientific
referee pending. One registered run is still going (below). [Pre-registration](preregistration.md) ·
[definitions](../PARTS-MEET-AGAIN-20261124-001/definitions.md) ·
[the owner's request, as given](../PARTS-MEET-AGAIN-20261124-001/owner_request.md) ·
[code and its recorded readings](../../experiments/PARTS-MEET-AGAIN-20261124-001A/PARTS-MEET-AGAIN-20261124-001A-E001_meet_again/deviations.md)

**Under the three recorded laws, no, and the reason can be stated: a birth that takes only what its own parents hold can
never reach a part that shares nothing with it. If a birth may also take a distinction from a knot its parent meets, or
from a knot one or two steps back along its own descent, parts that came apart do become one part again, and the first
then builds differently according to whether the second is there. In some of these cases the knot they come back through
is a knot both descend from, which is the owner's picture. But every such case needs its own ration, each needs a supplied
rule and a supplied choice of which distinction is taken, and what crosses is whether the other part is there, not what
it is. No part has yet built anything from what another part is.**

## Verdicts

Nineteen predictions were frozen. Sixteen hold, two fail, and one holds or fails according to a reading the frozen text
left open. The two failures are both in controls and both trace to wording that did not fix which pair of parts was meant.

| # | Verdict | What was found |
| --- | --- | --- |
| P0 (gate) | Holds | With no taking rule the engine equals the ring study's engine knot for knot in 840 runs (6,720 rounds), and the other thread's rule-R and rule-Q engines in 3,256 runs (16,149 rounds). Its three knot tests agree with brute force on 600 drawn structures, and its test for large knots agrees with the direct test on 135,314 knots. |
| P1 (a check of the argument) | Holds | Under rule Q, rule R as a treatment of a short knot, and the law that carries one distinction down a whole descent: no two parts that share nothing are ever one part again, and no birth has a parent in each. 504 runs, and so far 1.94 million histories with every choice tried (about 34.6 million pairs of parts). |
| P2 (a check) | Holds | Under those laws a part's course never differs with the other part stopped: 1,396 pairs under not-all-equal and 1,168 under parity. |
| P3 | Holds | Under rules Q and R from round 1 the ring never returns and no two-knot part copies itself. |
| P4 | Holds | Why: the would-be parts stay joined (24 of 24 runs). |
| P5 | Holds | With rule Q or R switched on only after the copies exist: 355, 387, 438 and 438 pairs that came apart, none one part again. |
| P6 (a check) | Holds | Joining by the record of descent alone never rejoins parts that came apart (444 pairs); a law under which any two members join lets nothing come apart. |
| P7 | Holds | The record-free law on the three-knot start does exactly what the advisor predicted by hand: everything retires in round 2 with six knots. |
| P8 | Holds | The smallest case, round by round as disclosed (below). |
| P9, P10 | Hold | Its swaps, and a second case through a knot the growth made, as disclosed. |
| P11 | Depends on a reading | The cheapest laws are as predicted if the supplier of the choice is taken as a label: one step above the parent under "just enough for three places", and a knot the parent meets under the cap of three. If the supplier is compared like the other costs, three more laws are also cheapest. The frozen text did not say which. |
| P12 | Holds | No case for parts that came apart survives a change of its ration; one case for the two-knot start's own halves survives every swap. |
| P13 | Holds | The choice of which distinction is taken is necessary: change it for the first part alone and the dependence appears or goes. |
| P14 | Open, reported | The course never differed with what the other part is: 16 pairs under six laws. |
| P15 | **Fails in one clause** | The birth placed by hand joins two copies. Where short knots retire the first copy's course is unchanged, and on the ring the ring's course does not depend on the part it gave off, as predicted. Where short knots wait, the first copy's course differs at round 5; the frozen text said round 3, which is the round for another choice of which part is "the first". |
| P16 | **Fails in one clause** | With knots that hold, parts that still share something become one part again a round later and no course differs, as predicted. But "under rule Q with holding nothing comes apart" is false: where every member is short, holding keeps nothing and parts come apart as under release. |
| P17 | Open, reported | Births with a parent in each part: below. |
| P18 | Holds | Knots fail only where predicted (below). |

## The reason the recorded laws cannot

Rule R lets a short knot take a distinction it already shares; rule Q lets an offshoot also take one its parent shares. In
both, everything a new knot takes is held by one of its own parents. Whatever a parent holds is already met by
everything the parent meets. So taking it can make the new knot meet only what its parent already met: it can rejoin
what is still joined, and nothing else. The argument is written out in the pre-registration as one induction, for parts
that share nothing even through a third part, under any release rule. It is an argument for the referee. The runs bear it
out on every pair tested, including every choice of which distinction is taken on the small starts.

The third recorded item, the move of assumption A225, is a birth placed by hand, not a law. As a law it is rule R or
rule Q. Placed by hand between two parts that share nothing, it does join them; that is the control of P15, and its
verdict is "supplied".

On the two objects themselves, rules Q and R from round 1 undo them: the ring never returns and nothing copies itself,
because the parts that would have come apart stay joined.

## The laws that reach further

A law outside that argument has a birth take a distinction that none of its parents holds. Seven such laws were run, with
four ways of choosing which distinction is taken. Each has a cost in what it looks at.

| Law | Looks at, in holder steps | Looks at, in steps of the record of descent | Parts that came apart become one part again, and the first's course differs? |
| --- | --- | --- | --- |
| Joined by the record alone | 0 | 2 or 3 | No (and by argument never) |
| Any two members join | 0 | 0, but it looks at the whole roster | Nothing ever comes apart |
| Rule Q, rule R | 1 | 0 | No (the argument above) |
| One distinction carried down a whole descent | 1 | 1 | Nothing comes apart; one distinction reaches 246 holders |
| From a knot the parent meets | 2 | 0 | Yes, under the cap of three, on the ring of five |
| From one step above the parent | 2 | 1 | Yes, under "just enough for three places", on the two-knot start |
| From two steps above the parent | 3 | 2 | Yes, under both rations, on every start |
| From the nearest ancestor with members in two parts | any | any, and it looks at the parts | Yes, but mostly because its own rule looks for the other part |

- **The cheapest law that works needs no record of descent.** An offshoot also takes a distinction held by a knot its parent
  meets. It looks two holder steps out and at nothing written.
- **How the choice is made is part of every law.** Oldest and newest use the start's numbering; "in turn" uses the order of
  births; "by count" uses the number of places the parent has, which is in the structure. None is made by the growth.
- **What it costs in holders.** Within eight rounds the most-held distinction reached 128 holders under rule Q, 182 under
  the record-free law and 114 with two steps above the parent, against 2 under the earlier laws.

## What the cases are

Over the registered runs, under both knot laws together, 302 pairs of parts that came apart show the first part's course
differing with the second stopped.

- **216 are through a meeting made by births**: 180 through a knot the growth made, 36 through a start knot.
- **80 are supplied**: the law is the control whose rule looks for the other part.
- **6 are unconfirmed.**

Of the 216:

- **In 62 a knot that both parts descend from is among the knots that link them**, an ancestral common knot. It is always a
  start knot. In 6 it is the only link: on the three-knot start with a short knot making offshoots and the law that takes
  from two steps above the parent, a part of one knot and a part of four are one part again at round 7 through the start
  knot both descend from, and the first builds differently at round 8. An ancestral common knot that the growth itself
  made appears only under the control law.
- **In 72 a birth is then made with a parent in each part.** These are under the ring's law with the law that takes from
  two steps above, on all three ring starts, and under three other combinations. In the rest the meeting only makes knots
  short.
- **In none does the course depend on what the other part is.**

**The smallest case** has 20 knots: the three-knot start, "just enough for three places" with a short knot retiring, and
the law that takes the oldest distinction from two steps above the parent.

1. Round 1: the two members join, and each makes an offshoot.
2. Round 2: the join is short and retires. Each offshoot makes two offshoots: two two-knot parts that share nothing.
3. Round 3: each part's offshoots take a distinction that its founder shares with the start's dead knot. That knot now meets
   all four, so the two parts are one part again.
4. Round 4: the four are each asked for three joins and hold one, so they retire. With the second part stopped, or removed,
   the first part makes a join of three parents instead.

Every knot passes the knot test under both knot laws through round 8. The knot the parts come back through is the start's
dead knot, which neither part descends from. With the start renumbered, the same case goes through the retired join of
round 1, a knot the growth made.

## What is the scaffolds'

Every case with a confirmed mark was rerun with each supplied rule swapped (80 cases: 33 for parts that came apart, 47 for
the two halves of the two-knot start, which were never one part).

- **The ration.** All 33 cases for parts that came apart vanish when "just enough for three places" is swapped for the cap
  of three on the same start, or the cap for the other. For the smallest case the reason is known: under the cap its copies
  never come apart, so there is nothing to rejoin. Cases exist under each ration, on different starts.
- **Exactly two steps, or up to two.** Every case of the law that takes from exactly two steps above vanishes when it may
  also take from one step above.
- **Holding** removes 24 of the 33; the start's names reversed 12; reading the demand before the takes 9; the order of
  births reversed 5; counting fresh distinctions by parents 4. The knot law removes none.
- **One case survives every swap**, and it is not a reunion: the record-free law, choosing by count, with a short knot
  making offshoots, joins the two halves of the two-knot start through the distinction its two start knots share.

So nothing here is yet a property of the model. Each case is a property of one base law together with one taking rule and
one way of choosing.

## Supplied or made

- **Rules R and Q, and the A225 move:** no reader at all, by an argument.
- **The laws that reach further:** in 216 of 302 marks the dependence goes through a meeting that births made, under a
  stated law with nothing placed by hand after the start. In that sense the meeting is made by the growth. The law, its
  way of choosing, the base law's ration and treatment, and the start are supplied.
- **What crosses is one bit**: whether the other part is there. It crosses by crowding, the meeting leaving knots with
  more asked of them than they hold, or by a joint birth. "Reads" in the owner's fuller sense, a part whose course depends
  on what another part is, was not found.

## The knot test

Every knot of every run was tested at every round under the run's own knot law: 517,822 verdicts in the main runs, 1.84
million in the comparison runs and 231 million in the enumeration so far, with no disagreement between methods and none
left untested. Under not-all-equal no knot fails outside the law that carries a distinction down a descent. Under
parity knots fail only at joins of ten or twelve parents under two of the laws, at joins of three parents in comparison
runs of one law, and, under the two rations that can give a join nothing, where that happens.

## Deviations and limits

- **One registered run is not finished.** The run that tries every choice under rules Q and R with the swaps has done 285 of
  its 360 enumerations, with nothing against P1. Seventy-three more are expected within the day and two, on the ring of
  five under one ration, need forty hours or more (long-running check `PARTSMEET-RUN2`, stress test pending). They test an
  argument that has held in everything run. This note will be updated when they end.
- **Three places where the frozen text was unclear** (the thread's and the drafter's wording): how the supplier of the
  choice is compared in the cost of a law (P11); which two parts are meant "after round 2" where a short knot waits and
  there are three (P15); and a statement about holding that cannot be true where every member is short (P16). Four smaller
  ones are in the code's recorded readings.
- **The engine's author recorded 44 readings**, repaired three faults of its own before the affected runs were redone, and
  reported two slips: one read-only look at the repository's state, and stopping one of its own scratch programs by name
  instead of by number. Neither touched the study.
- **Agreement with the drafter's prototype.** The two programs agree on all 302 marks and their verdicts, on the ways and
  demand lines, on the 116 marks for the two-knot start's halves, on the counts per law, and on the 80 swap cases except
  how one swap is counted. They differ in the number of pairs tested (7,089 against 7,039), in one knot whose size depends
  on a reading, and in the two failed clauses above.
- **Everything is finite:** six starts, eight rounds, at most about 1,500 knots a run.
- **Evidence class:** exact computation by an engine written from the frozen text, with a second independent program
  agreeing; one argument (that taking only what a parent holds cannot rejoin parts that share nothing).
- **Scaffolds:** every taking rule, every way of choosing, the late start, the birth placed by hand, the base laws and the
  starts. All were swapped; the summary above says what survived.

## Correction of 25 November 2026: "by count" also uses the names

**Not a block** (logged in the program's corrections log, `docs/CORRECTIONS.md`). The sentence above, that "by count"
"uses the number of places the parent has, which is in the structure", and the definitions' "It uses the structure only",
say more than the rule does. The count is in the structure. It is then used as a position in the list of candidates
sorted by name, "counting from the oldest at zero", and for a join it is the count of the first parent by name. So all
four ways of choosing use the supplied names, and none uses the structure only. No verdict changes: reversing the
start's names was a registered swap and was run on every case, the "by count" cases among them, and "None is made by the
growth" already covered all four. The frozen definitions keep their text. Found independently by the advisor reviewing
the design of the study that follows this one, and by the survey for the Intuitions guide's chapter on time.

## Correction of 25 November 2026: not every history tried every choice

**Narrowing** (logged in the program's corrections log, `docs/CORRECTIONS.md`). The verdict on P1 above says "so far 1.94
million histories with every choice tried". The frozen text allowed an enumeration of more than 100,000 histories to be
replaced by 100,000 taken at random under a fixed seed, and that happened in 17 of the 285 enumerations done so far. So
every choice was tried in 268 enumerations (239,866 histories), and 1,700,000 histories, 88% of the total, were taken at
random, 100,000 in each of the other 17. Nothing was found against the argument in either kind, and the argument does
not rest on the enumeration; but for those 17 the runs show what a sample shows, not that no choice does it. The same
holds for the decision note's "in every choice of distinction tried so far" and for "285 of 360 parts done" wherever
this record says "trying every choice". Found by the independent fact-check of the Intuitions guide's chapter on folds
of emergence.

## Update of 25 November 2026: the enumeration at 358 of 360 parts

The registered run that goes through the possibilities for which distinction each birth takes, under rules Q and R with
the swaps, has now done 358 of its 360 parts: 3,571,746 histories, with every possibility tried in 326 parts (371,746
histories) and, where the frozen text's cap applied, 100,000 histories taken at random under a fixed seed in each of
the other 32. In none are two parts that share nothing one part again, and in none does a birth have a parent in each.
The last two parts are still running and are expected to need about forty hours; this note will be followed by one
more when they end. The counts above replace "285 of 360" and "1.94 million" in the verdict on P1, in "One registered
run is not finished" and in the correction of the same day.

## Update of 25 November 2026: the last two parts stopped, the enumeration left unfinished at 358 of 360

The last two parts of the registered enumeration were stopped on 25 November 2026 at the owner's word, and the run is
recorded as unfinished at 358 of its 360 parts. Both parts are on Ring(5, 3) under COPY-LAW(OFFSHOOT) with rule Q on
from round 1 and the swap ONE-FEWER, one under each knot law. Each was to take 100,000 histories at random under the
fixed seed. When they were stopped, after about eight hours, they stood as follows.

| Knot law | Histories taken, of 100,000 | Pairs of parts that share nothing | Of these, one part again | Births with a parent in each | Knot verdicts |
| --- | --- | --- | --- | --- | --- |
| Parity | 59,000 | 8,274 | 0 | 0 | 11,960,662 |
| Not-all-equal | 2,000 | 258 | 0 | 0 | 404,051 |

Nothing in either is against the argument, as far as each went. These partial counts are not among the 358 parts or
the 3,571,746 histories of the note above. They are the last progress lines of `run2_long_progress.jsonl`, and
`summary.md` quotes them under "Not finished when this summary was written".

At the rates seen, the parity part needed about six more hours and the not-all-equal part about sixteen days. The
note above gave "about forty hours" for both, which was wrong for each.

The argument of the pre-registration ("Settled by construction") covers these two parts as it covers the others; what
is missing is its check on them. The verdict on P1 stands as "holds" on 358 parts, with these two unfinished.
