# Late hearing from afar under the local taking rules, and under laws in which knots hold back part of what they are owed

Epic `HOLD-BACK-20261126-001`, at the coordinator's go-ahead under the owner's standing rule, after
[`TWO-RECEPTIONS-20261126-001`](../TWO-RECEPTIONS-20261126-001/decision.md). A check by the thread, not a registered
study; computed; referee pending. Program: [`hold.py`](hold.py) (the readings of that study's census).


> **Refereed (R1, [report](referee-R1/report.md)): confirmed with fixes, two Blocks.** The two laws are not one of each
> of the advisor's classes (NET-OWING is not a constant shortfall of one; joins are given two to four distinctions, not
> two), and late hearing does not need a fixed number: a ceiling read from the demand gives the cap's allocations and
> hearings on the histories read. The counts stand. See [the decision's notice](decision.md).
## A. The local taking rules

The referee of the two-receptions study found that under the ordinary count with a local taking rule a change at a far
member after round 1 reaches a join of the receiver's own in round 2, with no knot short; that study's census, with
changes after round 3 only, heard none (0 of 4,143). Here the same 100 receivers (seed 20261126) and five senders,
joined by a meeting through two link knots, under the ordinary count with each local take (MET with the oldest or the
newest candidate, MET-SOLE, STEPS1-SOLE, STEPS2-SOLE), with changes after rounds 1, 2 and 3 at up to five linked and
two unlinked far members. A hearing is late when it comes after round 2d = 6.

**Expected** (written before the run, after one trial pair: nine changes, none heard): hearings after rounds 1 and 2
in some pairs, all by round 6; none late. A late hearing ends A with a positive; a clean census ends it without one.

## B. Laws in which knots hold back part of what they are owed (G18)

**The forms**, chosen with the advisor ([question](advisor_question.md), [answer](advisor_answer.md)), each in place of
the ordinary count's f = max(D, 3 − p, 1) and kept above its floor, max(…, 3 − p, 1), reading only what a birth knows:

- **INHERIT**: a new knot takes no more fresh distinctions than it was given, f = min(D, p). On these starts (no takes)
  a join is given two and an offshoot one, so it caps joins at two; it is short only where it is owed more than it was
  given. The advisor's cap-like class.
- **NET-OWING**: what a new knot was given pays part of what it is owed, f = D − p + 1. A join owed two is given one
  fresh distinction and is short by one; offshoots get the ordinary count. The advisor's class of a constant shortfall.

The advisor's other two forms (one per parent; keep one back) are the same as these two on starts with no takes, or
are the made ration ONE-FEWER of an earlier study; they are not run. Both forms are choices, registered as a scaffold
(A284). The knot law is not-all-equal.

**Read:** B1, the census of A (100 receivers, five senders, changes after rounds 1, 2, 3) under the two forms, the
ordinary count (the negative control) and the cap of three; B2, the 28 far ends that stay linked to the cap's switch
kind (LINKED-UNDER-CAP), against it, under the two forms and the cap of three (the positive control: heard at rounds
13, 17 and 23), 24 rounds. The advisor's jam check: a hearing counts only where both growths go on making knots after
it. **Survives the change of form** means a receiver hears a far change made after both exist, late, under a form of
each class; **belongs to one form** means it is heard under one form or the cap only.

**Expected** (written before the run, after a trial of two of the 28 far ends: the cap's positive control heard at 13,
17, 23; under both forms the two patterns come apart by round 2 or 3 and nothing is heard): under both forms no late
hearing in B2 (the patterns part at once); in B1 late hearings only under NET-OWING and only where the receiver's own
knots are held waiting (as under JOIN-FEWER, which NET-OWING equals on these starts), and none under INHERIT; so late
hearing does not survive the change of form.

### What was found: A

[`tally.py`](tally.py) on `takes_runs.jsonl.gz`: 1,588 of 2,500 pairs read; **912 not run** (21 jobs stopped by their
25-minute clock or memory cap; the takes with the oldest or newest candidate grow until the engine's guard and are
slow), not negatives.

| law | pairs read | short knots made after the start | changes after round 1 / 2 / 3 heard | heard after round 6 |
|---|---|---|---|---|
| ordinary count + MET, oldest candidate | 329 | 0 | 0 of 951 / 0 of 971 / 0 of 69 | 0 |
| ordinary count + MET, newest candidate | 317 | 0 | 99 of 852 / 3 of 852 / 0 of 325 | 0 |
| ordinary count + MET-SOLE | 314 | 0 | 0 of 787 / 0 of 713 / 0 of 566 | 0 |
| ordinary count + STEPS1-SOLE, STEPS2-SOLE | 314 each | 0 | 0 of 787 / 0 of 766 / 0 of 608 | 0 |

- **A clean census, in what was read: no late hearing under any local take.** Only the newest-candidate take carries
  a far change at all, and only one made after round 1 (99 of 852) or round 2 (3 of 852), first heard in rounds 2 to
  4; none made after round 3. No knot made after the start is short. The referee's witnesses (round 2) are of this
  kind: the take passes an early change across, and nothing arrives late.

## What was found: B

[`hold_table.md`](hold_table.md) (`hold_runs.jsonl.gz`, the census, 101 receivers with the two controls, 505 pairs per
law, all read) and `linked_runs.jsonl.gz` (the 28 linked pairs).

| law | B1: pairs with a short knot made after the start | B1: linked after round 3 | B1: far changes heard (of) | B1: heard after round 6 | B2: the 28 linked pairs, linked after round 3; heard (of) |
|---|---|---|---|---|---|
| INHERIT | 493 of 505 | 4 | 0 of 2,860 | 0 | 0; 0 of 165 |
| NET-OWING | 505 of 505 | 0 | 0 of 2,924 | 0 | 0; 0 of 168 |
| the ordinary count (negative control) | 0 | 231 | 0 of 3,437 | 0 | — |
| the cap of three (positive control) | 399 | 62 | 6 of 3,088 | 6 (rounds 9 and 11) | 28; 124 of 252, all late (rounds 13 to 23) |

- **Neither form gives a late hearing from afar, nor any hearing at all**: 0 of 5,784 far changes in the census and 0
  of 333 in the linked pairs. Both make knots short (as the advisor said: INHERIT where a knot is owed more than it was
  given, NET-OWING at every join), and both part the two patterns almost at once (4 and 0 census pairs still linked
  after round 3; none of the 28 linked pairs).
- **The controls behave.** The ordinary count keeps many pairs linked and hears nothing; the cap of three hears late, in
  the census (the switch kind and its four-knot twin, rounds 9 and 11, from seven or eight sharings, growth going on in
  both runs: the advisor's jam check passed in 6 of 6) and in all 28 linked pairs.
- **So late hearing from afar does not survive the change of form; it does not appear under either form.** What the cap
  does that these forms do not is to keep the two patterns linked while making the receiver's partners short: the cap
  binds only where the owing exceeds a number (here three), while INHERIT binds a join at two and NET-OWING at every join
  owed two, which is every join in these starts, so the link between the patterns breaks at once.

## Expectations, and how they fared

- *A: early hearings after rounds 1 and 2, none late.* Holds: 102 early hearings, all under the newest-candidate take,
  none late (in the 1,588 pairs read).
- *B2: under both forms no late hearing.* Holds (0 of 333).
- *B1: late hearings only under NET-OWING, at receivers held waiting; none under INHERIT.* The second half holds; the
  first fails (none under NET-OWING either: the two patterns come apart before anything can travel).
- *Late hearing does not survive the change of form.* Holds, more strongly than expected: it appears under neither form.

## What this does not say

- Two forms, chosen as one of each of the advisor's classes; the others (one per parent, keep one back) differ only
  with takes or at offshoots owed three or more, and were not run. Not-all-equal only.
- 101 receivers, five senders, one join, d = 3, 12 rounds (24 for the linked pairs).
- A form that binds only above a number the knot reads from itself (as the cap binds above three) was not among these;
  it is what the result points to.
